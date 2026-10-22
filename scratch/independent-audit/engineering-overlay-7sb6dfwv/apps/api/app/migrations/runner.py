"""Numbered, frozen SQLite schema upgrades; never infer upgrades from current ORM metadata."""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import re
from pathlib import Path
import sqlite3

from sqlalchemy.engine import Engine

from ..config import settings
from ..services.database_backup import create_database_backup
from . import v001_legacy_schema, v002_content_bindings, v003_content_publication, v004_editions, v005_assessment, v006_study_release


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    module: object

    @property
    def checksum(self) -> str:
        # Normalize Git CRLF/LF only. Definitions AND frozen DDL belong to the checksum.
        definition = Path(self.module.__file__).read_text(encoding="utf-8")
        schema = self.module.SCHEMA.read_text(encoding="utf-8")
        return hashlib.sha256((definition + "\n" + schema).encode("utf-8")).hexdigest()


MIGRATIONS = (
    Migration(1, "legacy_schema", v001_legacy_schema),
    Migration(2, "content_bindings", v002_content_bindings),
    Migration(3, "content_publication", v003_content_publication),
    Migration(4, "editions", v004_editions),
    Migration(5, "assessment", v005_assessment),
    Migration(6, "study_release", v006_study_release),
)


def _signature(execute, name: str) -> tuple:
    quoted = '"' + name.replace('"', '""') + '"'
    columns = tuple((r[1], r[2].upper(), r[3], r[4], r[5]) for r in execute(f"PRAGMA table_info({quoted})"))
    foreign_keys = tuple(sorted(tuple(r[2:]) for r in execute(f"PRAGMA foreign_key_list({quoted})")))
    unique = []
    for row in execute(f"PRAGMA index_list({quoted})"):
        if row[2]:
            index = '"' + row[1].replace('"', '""') + '"'
            unique.append(tuple(r[2] for r in execute(f"PRAGMA index_info({index})")))
    table_sql = execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='" + name.replace("'", "''") + "'")
    table_sql = list(table_sql)
    # The legacy CHECK expressions are flat comparisons; include them as integrity
    # constraints, not just column/foreign-key shape.
    checks = tuple(sorted(re.sub(r"\s+", "", expression).lower() for expression in
                          re.findall(r"CHECK\s*\(([^()]*)\)", table_sql[0][0] if table_sql else "", re.IGNORECASE)))
    return columns, foreign_keys, tuple(sorted(unique)), checks


@lru_cache
def _expected(schema_path: Path) -> dict:
    with sqlite3.connect(":memory:") as reference:
        tables = json.loads(schema_path.read_text(encoding="utf-8"))
        for table in tables:
            reference.execute(table["sql"])
            for statement in table["indexes"]:
                reference.execute(statement)
        return {table["name"]: _signature(reference.execute, table["name"]) for table in tables}


def _validate(connection, schema_path: Path, *, omit_ledger: bool = False) -> None:
    for name, expected in _expected(schema_path).items():
        if name == "schemamigration" and omit_ledger:
            continue
        observed = _signature(lambda sql: connection.exec_driver_sql(sql).fetchall(), name)
        if observed != expected:
            raise MigrationError(f"Incompatible SQLite schema for {name}; no drop/recreate repair is permitted")


def run_migrations(engine: Engine, *, backup_root: Path | None = None) -> dict:
    if engine.dialect.name != "sqlite":
        raise MigrationError("Forge migrations currently support SQLite only")
    backup_root = backup_root if backup_root is not None else settings.database_backup_path
    backup = None
    applied = []
    with engine.connect() as connection:
        # Explicit BEGIN is essential: sqlite3's legacy transaction mode otherwise autocommits DDL.
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
        connection.commit()
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        try:
            tables = set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").scalars())
            ledger = []
            if "schemamigration" in tables:
                _validate_ledger(connection)
                ledger = connection.exec_driver_sql("SELECT version,name,checksum FROM schemamigration ORDER BY version").all()
                versions = [r[0] for r in ledger]
                if versions and max(versions) > MIGRATIONS[-1].version:
                    raise MigrationError("Database schema is newer than this Forge application")
                if versions != list(range(1, len(ledger) + 1)):
                    raise MigrationError("Migration ledger is not a supported contiguous history")
                for row, migration in zip(ledger, MIGRATIONS):
                    if (row[1], row[2]) != (migration.name, migration.checksum):
                        raise MigrationError(f"Applied migration {row[0]} has a checksum/name mismatch")
            existing = bool(tables - {"schemamigration", "sqlite_sequence"})
            if existing or ledger:
                _validate(connection, v001_legacy_schema.SCHEMA)
            if len(ledger) >= 2:
                _validate(connection, v002_content_bindings.SCHEMA)
                triggers = set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='trigger'").scalars())
                required = {f"{table}_immutable_{op}" for table in (
                    "contentrevision", "topiccontentbinding", "arenatopicbinding", "courseexercisebinding") for op in ("update", "delete")}
                required.update({"topiccontentbinding_owner", "arenatopicbinding_owner", "courseexercisebinding_owner",
                                 "contentsectionprogress_owner_insert", "contentsectionprogress_owner_update",
                                 "topiccontentbinding_type", "arenatopicbinding_type"})
                if not required.issubset(triggers):
                    raise MigrationError("Content schema is missing required integrity triggers")
            elif tables.intersection({"contentrevision", "topiccontentbinding", "arenatopicbinding",
                                      "courseexercisebinding", "contentsectionprogress"}):
                raise MigrationError("Unrecorded/partial content schema; restore a verified backup before retrying")
            pending = MIGRATIONS[len(ledger):]
            if len(ledger) >= 3:
                _validate(connection, v003_content_publication.SCHEMA)
                triggers = set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='trigger'").scalars())
                if not v003_content_publication.TRIGGERS <= triggers:
                    raise MigrationError("Publication schema is missing required integrity triggers")
            elif tables.intersection(v003_content_publication.TABLES):
                raise MigrationError("Unrecorded/partial publication schema")
            if len(ledger) >= 4:
                _validate(connection, v004_editions.SCHEMA)
                triggers = set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='trigger'").scalars())
                if not v004_editions.TRIGGERS <= triggers:
                    raise MigrationError("Edition schema is missing required integrity triggers")
            elif tables.intersection(v004_editions.TABLES):
                raise MigrationError("Unrecorded/partial edition schema")
            if len(ledger) >= 5:
                _validate(connection, v005_assessment.SCHEMA)
                triggers = set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='trigger'").scalars())
                if not v005_assessment.TRIGGERS <= triggers:
                    raise MigrationError("Assessment integrity triggers missing")
            elif tables.intersection(v005_assessment.TABLES):
                raise MigrationError("Unrecorded/partial assessment schema")
            if len(ledger) >= 6:
                _validate(connection, v006_study_release.SCHEMA)
                triggers = set(connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='trigger'").scalars())
                if not v006_study_release.TRIGGERS <= triggers:
                    raise MigrationError("Study release integrity triggers missing")
            elif tables.intersection(v006_study_release.TABLES):
                raise MigrationError("Unrecorded/partial study release schema")
            if pending and existing and engine.url.database not in (None, "", ":memory:"):
                # BEGIN IMMEDIATE quiesces other writers; a separate reader backup includes committed WAL data.
                backup = create_database_backup(Path(engine.url.database), backup_root)
            if pending and "schemamigration" not in tables:
                definition = next(t for t in json.loads(v002_content_bindings.SCHEMA.read_text()) if t["name"] == "schemamigration")
                connection.exec_driver_sql(definition["sql"])
            for migration in pending:
                migration.module.apply(connection)
                connection.exec_driver_sql(
                    "INSERT INTO schemamigration(version,name,checksum,applied_at) VALUES (?,?,?,strftime('%Y-%m-%d %H:%M:%f','now'))",
                    (migration.version, migration.name, migration.checksum),
                )
                applied.append(migration.version)
            _validate(connection, v001_legacy_schema.SCHEMA)
            _validate(connection, v002_content_bindings.SCHEMA)
            _validate(connection, v003_content_publication.SCHEMA)
            _validate(connection, v004_editions.SCHEMA)
            _validate(connection, v005_assessment.SCHEMA)
            _validate(connection, v006_study_release.SCHEMA)
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
    return {"schema_version": MIGRATIONS[-1].version, "applied": applied,
            "backup_path": str(backup) if backup else None}


def _validate_ledger(connection) -> None:
    expected = _expected(v002_content_bindings.SCHEMA)["schemamigration"]
    if _signature(lambda sql: connection.exec_driver_sql(sql).fetchall(), "schemamigration") != expected:
        raise MigrationError("Incompatible schema migration ledger")
