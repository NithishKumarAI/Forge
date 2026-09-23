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


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as test_session:
        seed_default_curriculum(
            test_session, REPO_ROOT / "data" / "default-ai-engineer-curriculum.json"
        )
        yield test_session

