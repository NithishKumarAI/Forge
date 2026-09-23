from sqlmodel import Session, select

from app.models import LearnerTopicState, Topic, Track
from app.services.dashboard import build_dashboard


def test_dashboard_aggregates_track_mastery(session: Session) -> None:
    python_track = session.exec(select(Track).where(Track.slug == "python")).one()
    python_topics = session.exec(select(Topic).where(Topic.track_id == python_track.id)).all()
    for topic in python_topics:
        state = session.get(LearnerTopicState, topic.id)
        assert state is not None
        state.mastery_score = 50
        session.add(state)
    session.commit()

    dashboard = build_dashboard(session)
    python_summary = next(track for track in dashboard["tracks"] if track["slug"] == "python")
    assert python_summary["mastery"] == 50
    assert dashboard["interview_readiness"] == 5
    assert len(dashboard["tracks"]) == 10
    assert len(dashboard["recommendations"]) == 4

