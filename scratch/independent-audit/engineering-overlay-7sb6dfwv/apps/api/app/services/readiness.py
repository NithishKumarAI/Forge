from sqlmodel import Session, select

from ..models import Curriculum, LearnerTopicState, Topic, Track


def _priority_weight(priority: int) -> float:
    return 1.5 if priority >= 70 else 0.7 if priority < 40 else 1.0


def track_readiness(session: Session, track: Track) -> dict:
    topics = session.exec(select(Topic).where(Topic.track_id == track.id)).all()
    weighted = [(session.get(LearnerTopicState, topic.id).mastery_score if session.get(LearnerTopicState, topic.id) else 0, _priority_weight(topic.priority)) for topic in topics]
    total = sum(weight for _, weight in weighted)
    score = round(sum(score * weight for score, weight in weighted) / total) if total else 0
    ready = sum(1 for topic in topics if (state := session.get(LearnerTopicState, topic.id)) and state.status == "interview_ready")
    strong = sum(1 for topic in topics if (state := session.get(LearnerTopicState, topic.id)) and state.status in {"strong", "interview_ready"})
    return {"track_id": track.id, "readiness": score, "ready_topics": ready, "strong_or_ready_topics": strong, "total_topics": len(topics)}


def curriculum_readiness(session: Session, curriculum: Curriculum) -> dict:
    tracks = session.exec(select(Track).where(Track.curriculum_id == curriculum.id)).all()
    summaries = [(track_readiness(session, track), _priority_weight(track.priority)) for track in tracks]
    total_weight = sum(weight for _, weight in summaries)
    score = round(sum(item["readiness"] * weight for item, weight in summaries) / total_weight) if total_weight else 0
    topics = session.exec(select(Topic).join(Track).where(Track.curriculum_id == curriculum.id)).all()
    ready = sum(1 for topic in topics if (state := session.get(LearnerTopicState, topic.id)) and state.status == "interview_ready")
    strong = sum(1 for topic in topics if (state := session.get(LearnerTopicState, topic.id)) and state.status in {"strong", "interview_ready"})
    gaps = sum(1 for topic in topics if topic.priority >= 70 and ((state := session.get(LearnerTopicState, topic.id)) is None or state.mastery_score < 70))
    return {"curriculum_id": curriculum.id, "readiness": score, "ready_topics": ready, "strong_or_ready_topics": strong, "total_topics": len(topics), "high_priority_gaps": gaps, "track_readiness": [item for item, _ in summaries], "disclaimer": "Forge curriculum readiness score; not a hiring probability."}
