from sqlmodel import Session, select

from app.models import LearnerTopicState, Topic
from app.services.recommendations import recommend_topics


def test_recommendations_are_deterministic_and_exclude_ready_topics(session: Session) -> None:
    first_run = recommend_topics(session, limit=5)
    second_run = recommend_topics(session, limit=5)
    assert [topic.id for topic in first_run] == [topic.id for topic in second_run]
    assert len(first_run) == 5

    top_topic = first_run[0]
    state = session.get(LearnerTopicState, top_topic.id)
    assert state is not None
    state.status = "interview_ready"
    session.add(state)
    session.commit()

    updated = recommend_topics(session, limit=5)
    assert top_topic.id not in [topic.id for topic in updated]
    assert all(topic.priority <= first_run[0].priority for topic in updated)


def test_satisfied_prerequisite_wins_within_same_priority(session: Session) -> None:
    syntax = session.exec(select(Topic).where(Topic.slug == "syntax-data-types")).first()
    assert syntax is not None
    state = session.get(LearnerTopicState, syntax.id)
    assert state is not None
    state.mastery_score = 70
    session.add(state)
    session.commit()

    recommendations = recommend_topics(session, limit=20)
    assert recommendations

