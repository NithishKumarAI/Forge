from sqlmodel import Session, select

from ..models import LearnerTopicState, Topic, TopicPrerequisite, Track


def recommend_topics(
    session: Session, limit: int = 4, curriculum_id: int | None = None
) -> list[Topic]:
    statement = select(Topic)
    if curriculum_id is not None:
        statement = statement.join(Track).where(Track.curriculum_id == curriculum_id)
    topics = session.exec(statement).all()
    candidates: list[tuple[int, int, int, Topic]] = []
    for topic in topics:
        state = session.get(LearnerTopicState, topic.id)
        if state is None or state.status == "interview_ready":
            continue
        links = session.exec(
            select(TopicPrerequisite).where(TopicPrerequisite.topic_id == topic.id)
        ).all()
        prerequisites_satisfied = all(
            (prereq_state := session.get(LearnerTopicState, link.prerequisite_topic_id))
            is not None
            and prereq_state.mastery_score >= 60
            for link in links
        )
        candidates.append(
            (-topic.priority, 0 if prerequisites_satisfied else 1, state.mastery_score, topic)
        )
    candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3].order_index, item[3].id))
    return [item[3] for item in candidates[:limit]]
