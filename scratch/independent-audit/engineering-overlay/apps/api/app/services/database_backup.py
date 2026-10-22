"""Consistent SQLite backups. Restore creates a new file; it never replaces a learner DB."""
from datetime import datetime, timezone
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import time
from uuid import uuid4

from .content_paths import reject_links


class BackupError(RuntimeError):
    pass


@contextmanager
def _readonly(path: Path):
    reject_links(path)
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    try:
        yield connection
    finally:
        connection.close()


def database_summary(connection: sqlite3.Connection) -> dict:
    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]
    counts = {name: connection.execute('SELECT COUNT(*) FROM "' + name.replace('"', '""') + '"').fetchone()[0]
              for name in tables}
    version = connection.execute("SELECT COALESCE(MAX(version),0) FROM schemamigration").fetchone()[0] if "schemamigration" in tables else 0
    return {"schema_version": version, "table_counts": counts}


def _integrity(connection: sqlite3.Connection) -> None:
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise BackupError("SQLite integrity verification failed")


def _copy(source: sqlite3.Connection, destination: Path) -> None:
    deadline = time.monotonic() + 30

    def progress(status: int, remaining: int, total: int) -> None:
        if time.monotonic() > deadline:
            raise BackupError("SQLite backup timed out; source was not replaced")

    # The exclusive create prevents an accidental overwrite, including an interrupted restore.
    with destination.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(destination)) as target:
            source.backup(target, pages=128, progress=progress, sleep=0.05)
            _integrity(target)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def create_database_backup(source: Path, backup_root: Path) -> Path:
    source, backup_root = source.absolute(), backup_root.absolute()
    reject_links(source)
    reject_links(backup_root)
    backup_root.mkdir(parents=True, exist_ok=True)
    target = backup_root / f"{source.stem}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid4().hex}.sqlite3"
    try:
        with _readonly(source) as connection:
            size = connection.execute("PRAGMA page_count").fetchone()[0] * connection.execute("PRAGMA page_size").fetchone()[0]
            if shutil.disk_usage(backup_root).free < size * 2 + 1024 * 1024:
                raise BackupError("Insufficient free disk space for a verified SQLite backup")
            _copy(connection, target)
        with _readonly(target) as copied:
            metadata = database_summary(copied)
        metadata.update({"created_at": datetime.now(timezone.utc).isoformat(),
                         "source_name": source.name,
                         "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        with target.with_suffix(".json").open("x", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2)
        verify_database_backup(target)
        return target
    except BaseException as error:
        target.unlink(missing_ok=True)
        target.with_suffix(".json").unlink(missing_ok=True)
        if isinstance(error, (KeyboardInterrupt, SystemExit, BackupError)):
            raise
        raise BackupError("Could not create/verify SQLite backup; migration was not started") from error


def verify_database_backup(backup: Path) -> dict:
    reject_links(backup)
    reject_links(backup.with_suffix(".json"))
    try:
        metadata = json.loads(backup.with_suffix(".json").read_text(encoding="utf-8"))
        if hashlib.sha256(backup.read_bytes()).hexdigest() != metadata["sha256"]:
            raise BackupError("Backup SHA-256 does not match its metadata")
        with _readonly(backup) as connection:
            _integrity(connection)
            if database_summary(connection) != {key: metadata[key] for key in ("schema_version", "table_counts")}:
                raise BackupError("Backup schema/counts differ from its metadata")
        return metadata
    except (OSError, KeyError, ValueError, sqlite3.Error) as error:
        raise BackupError("Backup or metadata is missing, invalid, or unreadable") from error


def restore_database_backup(backup: Path, destination: Path) -> Path:
    """Call explicitly with Forge stopped; inspect the new file before selecting it in config."""
    destination = destination.absolute()
    reject_links(destination)
    if any(Path(str(destination) + suffix).exists() for suffix in ("", "-wal", "-shm", "-journal")):
        raise BackupError("Restore destination/sidecars already exist; choose a new path. Nothing was replaced.")
    metadata = verify_database_backup(backup)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with _readonly(backup) as source:
        size = backup.stat().st_size
        if shutil.disk_usage(destination.parent).free < size * 2 + 1024 * 1024:
            raise BackupError("Insufficient free disk space for restore")
        _copy(source, destination)
    try:
        with _readonly(destination) as restored:
            if database_summary(restored) != {key: metadata[key] for key in ("schema_version", "table_counts")}:
                raise BackupError("Restored database does not match the backup")
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return destination
