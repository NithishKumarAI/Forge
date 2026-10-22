import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest
from sqlalchemy import inspect
from sqlmodel import Session, create_engine

from app.migrations import MigrationError, run_migrations
from app.migrations import runner, v001_legacy_schema, v002_content_bindings
from app.services.database_backup import (BackupError, create_database_backup, restore_database_backup,
                                          verify_database_backup)


def legacy_database(path: Path):
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        v001_legacy_schema.apply(connection)
    return engine


def test_fresh_and_repeat_initialization(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path/'fresh.db').as_posix()}")
    assert run_migrations(engine)["applied"] == [1, 2, 3, 4, 5, 6]
    assert run_migrations(engine) == {"schema_version": 6, "applied": [], "backup_path": None}
    assert {"contentrevision", "topiccontentbinding", "arenatopicbinding", "schemamigration"}.issubset(inspect(engine).get_table_names())
    engine.dispose()


def test_copied_unversioned_database_backup_upgrade_restore(tmp_path):
    original = tmp_path / "legacy.db"
    engine = legacy_database(original)
    with engine.begin() as connection:
        connection.exec_driver_sql("INSERT INTO appsetting VALUES ('preserve','original payload')")
    engine.dispose()
    verified = create_database_backup(original, tmp_path / "source-backups")
    copy = restore_database_backup(verified, tmp_path / "copy.db")
    copy_engine = create_engine(f"sqlite:///{copy.as_posix()}")
    result = run_migrations(copy_engine)
    metadata = verify_database_backup(Path(result["backup_path"]))
    assert metadata["schema_version"] == 0 and metadata["table_counts"]["appsetting"] == 1
    assert run_migrations(copy_engine)["applied"] == []
    restored = restore_database_backup(Path(result["backup_path"]), tmp_path / "restored.db")
    with sqlite3.connect(restored) as connection:
        assert connection.execute("SELECT * FROM appsetting").fetchall() == [("preserve", "original payload")]
        assert not connection.execute("SELECT name FROM sqlite_master WHERE name='schemamigration'").fetchall()
    with pytest.raises(BackupError, match="already exist"):
        restore_database_backup(verified, original)
    copy_engine.dispose()


def test_failed_migration_rolls_back_ddl_and_ledger(tmp_path, monkeypatch):
    engine = legacy_database(tmp_path / "legacy.db")
    before = set(inspect(engine).get_table_names())
    original = v002_content_bindings.apply

    def interrupted(connection):
        connection.exec_driver_sql("CREATE TABLE interrupted_migration(id INTEGER)")
        raise RuntimeError("simulated interruption")

    monkeypatch.setattr(v002_content_bindings, "apply", interrupted)
    with pytest.raises(RuntimeError, match="interruption"):
        run_migrations(engine)
    assert set(inspect(engine).get_table_names()) == before
    monkeypatch.setattr(v002_content_bindings, "apply", original)
    assert run_migrations(engine)["applied"] == [1, 2, 3, 4, 5, 6]
    engine.dispose()


def test_modified_applied_migration_detected(tmp_path, monkeypatch):
    engine = create_engine("sqlite://")
    run_migrations(engine)
    read = Path.read_text

    def changed(path, *args, **kwargs):
        value = read(path, *args, **kwargs)
        return value + "\n# modified applied migration\n" if path.name == "v002_content_bindings.py" else value

    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(MigrationError, match="checksum"):
        run_migrations(engine)


def test_newer_schema_rejected():
    engine = create_engine("sqlite://")
    run_migrations(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("UPDATE schemamigration SET version=99 WHERE version=2")
    with pytest.raises(MigrationError, match="newer"):
        run_migrations(engine)


@pytest.mark.parametrize("mode", ["partial_legacy", "changed_legacy", "missing_trigger", "changed_check"])
def test_incompatible_schema_fails_visibly(tmp_path, mode):
    engine = create_engine("sqlite://")
    if mode == "partial_legacy":
        with engine.begin() as connection:
            connection.exec_driver_sql("CREATE TABLE curriculum(id INTEGER PRIMARY KEY)")
    elif mode == "changed_check":
        with engine.begin() as connection:
            for table in json.loads(v001_legacy_schema.SCHEMA.read_text()):
                connection.exec_driver_sql(table["sql"].replace("CHECK (mastery_score >= 0 AND mastery_score <= 100)", "CHECK (1=1)"))
                for statement in table["indexes"]:
                    connection.exec_driver_sql(statement)
    else:
        run_migrations(engine)
        with engine.begin() as connection:
            if mode == "changed_legacy":
                connection.exec_driver_sql("ALTER TABLE attempt ADD COLUMN unexpected TEXT")
            else:
                connection.exec_driver_sql("DROP TRIGGER contentrevision_immutable_update")
    with pytest.raises(MigrationError, match="Incompatible|integrity triggers"):
        run_migrations(engine)


@pytest.mark.parametrize("failure", ["space", "write"])
def test_backup_failure_leaves_original_unmodified(tmp_path, monkeypatch, failure):
    from app.services import database_backup
    path = tmp_path / "legacy.db"
    engine = legacy_database(path)
    before = path.read_bytes()
    if failure == "space":
        monkeypatch.setattr(database_backup.shutil, "disk_usage", lambda _: SimpleNamespace(free=0))
    else:
        monkeypatch.setattr(database_backup, "_copy", lambda *args: (_ for _ in ()).throw(OSError("write failure")))
    with pytest.raises(BackupError):
        run_migrations(engine)
    assert path.read_bytes() == before
    assert "schemamigration" not in inspect(engine).get_table_names()
    engine.dispose()


def test_backup_includes_committed_wal_and_detects_corruption(tmp_path):
    source = tmp_path / "wal.db"
    with sqlite3.connect(source) as connection:
        assert connection.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        connection.execute("CREATE TABLE history(id INTEGER PRIMARY KEY, answer TEXT)")
        connection.execute("INSERT INTO history VALUES (7,'committed in WAL')")
        connection.commit()
        backup = create_database_backup(source, tmp_path / "backups")
        with sqlite3.connect(backup) as copied:
            assert copied.execute("SELECT * FROM history").fetchall() == [(7, "committed in WAL")]
        assert verify_database_backup(backup)["table_counts"]["history"] == 1
    with backup.open("ab") as handle:
        handle.write(b"changed")
    with pytest.raises(BackupError, match="SHA-256"):
        verify_database_backup(backup)
