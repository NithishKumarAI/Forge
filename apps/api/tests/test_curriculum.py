from pathlib import Path

from sqlmodel import Session, select

from app.models import Curriculum, LearnerTopicState, Topic, Track
from app.services.curriculum import seed_default_curriculum


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_default_curriculum_is_seeded_once(session: Session) -> None:
    curriculum_path = REPO_ROOT / "data" / "default-ai-engineer-curriculum.json"
    first = seed_default_curriculum(session, curriculum_path)
    second = seed_default_curriculum(session, curriculum_path)

    assert first.id == second.id
    assert len(session.exec(select(Curriculum)).all()) == 1
    assert len(session.exec(select(Track)).all()) == 10
    assert len(session.exec(select(Topic)).all()) == 160
    states = session.exec(select(LearnerTopicState)).all()
    assert len(states) == 160
    assert all(state.mastery_score == 0 and state.status == "not_started" for state in states)

