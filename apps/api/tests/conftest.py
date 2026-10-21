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
from app.providers.gemini import GeminiProvider  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_runtime_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "content_snapshot_path", tmp_path / "snapshots")
    monkeypatch.setattr(settings, "database_backup_path", tmp_path / "backups")

    def forbidden_provider(*args, **kwargs):
        raise AssertionError("Automated tests must inject a fake provider, never construct Gemini")

    monkeypatch.setattr(GeminiProvider, "__init__", forbidden_provider)


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

