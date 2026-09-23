from sqlmodel import Session, select

from ..models import Curriculum, LearnerTopicState, Topic, TopicPrerequisite, Track


def _state_dict(state: LearnerTopicState) -> dict:
    return {
        "mastery_score": state.mastery_score,
        "confidence": state.confidence,
        "status": state.status,
        "attempts": state.attempts,
        "last_studied_at": state.last_studied_at,
        "last_tested_at": state.last_tested_at,
        "next_review_at": state.next_review_at,
    }


def topic_to_dict(session: Session, topic: Topic) -> dict:
    track = session.get(Track, topic.track_id)
    state = session.get(LearnerTopicState, topic.id)
    links = session.exec(
        select(TopicPrerequisite).where(TopicPrerequisite.topic_id == topic.id)
    ).all()
    prerequisites = []
    for link in links:
        prerequisite = session.get(Topic, link.prerequisite_topic_id)
        if prerequisite:
            prerequisite_state = session.get(LearnerTopicState, prerequisite.id)
            prerequisites.append(
                {
                    "id": prerequisite.id,
                    "name": prerequisite.name,
                    "slug": prerequisite.slug,
                    "mastery_score": prerequisite_state.mastery_score
                    if prerequisite_state
                    else 0,
                    "status": prerequisite_state.status
                    if prerequisite_state
                    else "not_started",
                }
            )
    return {
        "id": topic.id,
        "track_id": topic.track_id,
        "track_name": track.name if track else "",
        "name": topic.name,
        "slug": topic.slug,
        "description": topic.description,
        "order_index": topic.order_index,
        "priority": topic.priority,
        "target_level": topic.target_level,
        "estimated_minutes": topic.estimated_minutes,
        "state": _state_dict(state or LearnerTopicState(topic_id=topic.id)),
        "prerequisites": prerequisites,
    }


def track_to_dict(session: Session, track: Track, include_topics: bool = True) -> dict:
    topics = session.exec(
        select(Topic).where(Topic.track_id == track.id).order_by(Topic.order_index)
    ).all()
    weighted = [
        (
            session.get(LearnerTopicState, topic.id).mastery_score
            if session.get(LearnerTopicState, topic.id) else 0,
            1.5 if topic.priority >= 70 else 0.7 if topic.priority < 40 else 1.0,
        )
        for topic in topics
    ]
    result = {
        "id": track.id,
        "curriculum_id": track.curriculum_id,
        "name": track.name,
        "slug": track.slug,
        "description": track.description,
        "order_index": track.order_index,
        "priority": track.priority,
        "mastery": round(sum(score * weight for score, weight in weighted) / sum(weight for _, weight in weighted)) if weighted else 0,
        "topic_count": len(topics),
    }
    if include_topics:
        result["topics"] = [topic_to_dict(session, topic) for topic in topics]
    return result


def curriculum_to_dict(session: Session, curriculum: Curriculum, detailed: bool = True) -> dict:
    tracks = session.exec(
        select(Track)
        .where(Track.curriculum_id == curriculum.id)
        .order_by(Track.order_index)
    ).all()
    result = {
        "id": curriculum.id,
        "name": curriculum.name,
        "description": curriculum.description,
        "source_type": curriculum.source_type,
        "status": curriculum.status,
        "version": curriculum.version,
        "created_at": curriculum.created_at,
        "confirmed_at": curriculum.confirmed_at,
        "track_count": len(tracks),
    }
    if detailed:
        result["tracks"] = [track_to_dict(session, track) for track in tracks]
    return result
