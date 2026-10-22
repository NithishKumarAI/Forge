from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool


API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(API_ROOT))

from app import models  # noqa: E402, F401
from app.services.curriculum import seed_default_curriculum  # noqa: E402
from app.config import settings  # noqa: E402
from app.migrations import run_migrations  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_runtime_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "content_snapshot_path", tmp_path / "snapshots")
    monkeypatch.setattr(settings, "database_backup_path", tmp_path / "backups")

    # No optional model SDK is imported by fixtures or supported runtime flows.
    import socket
    original=socket.socket.connect
    def local_only(sock,address):
        if isinstance(address,tuple) and address[0] not in ("127.0.0.1","localhost","::1"):
            raise AssertionError("External network forbidden in automated tests")
        return original(sock,address)
    monkeypatch.setattr(socket.socket,"connect",local_only)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    run_migrations(engine)
    with Session(engine) as test_session:
        seed_default_curriculum(
            test_session, REPO_ROOT / "data" / "default-ai-engineer-curriculum.json"
        )
        yield test_session
    engine.dispose()

