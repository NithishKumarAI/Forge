from datetime import datetime, timezone

from sqlmodel import Session, select

from ..models import ReviewState, Topic, Track
from .active_curriculum import get_active_curriculum
from .catalog import topic_to_dict, track_to_dict
from .recommendations import recommend_topics
from .readiness import curriculum_readiness
from .planner import today_plan
from .mastery import mastery_breakdown


def build_dashboard(session: Session) -> dict:
    curriculum = get_active_curriculum(session)
    if curriculum is None:
        return {
            "interview_readiness": 0,
            "active_curriculum": None,
            "tracks": [],
            "recommendations": [],
        }
    tracks = session.exec(
        select(Track)
        .where(Track.curriculum_id == curriculum.id)
        .order_by(Track.order_index)
    ).all()
    track_summaries = [track_to_dict(session, track, include_topics=False) for track in tracks]
    readiness = curriculum_readiness(session, curriculum)
    recommendations = []
    for topic in recommend_topics(session, curriculum_id=curriculum.id):
        item = topic_to_dict(session, topic)
        breakdown = mastery_breakdown(session, topic.id)
        if breakdown["transfer_eligible"]:
            item["reason"] = "Ready for transfer verification."
        elif breakdown["mistakes"]:
            mistake = breakdown["mistakes"][0]
            item["reason"] = f"Recurring {mistake['description'].lower()} ×{mistake['occurrence_count']}."
        elif topic.priority >= 70:
            item["reason"] = f"High-priority interview topic; mastery {item['state']['mastery_score']}%."
        else:
            item["reason"] = f"Developing topic; mastery {item['state']['mastery_score']}%."
        recommendations.append(item)
    now = datetime.now(timezone.utc)
    topic_ids = session.exec(select(Topic.id).join(Track).where(Track.curriculum_id == curriculum.id)).all()
    due_states = session.exec(select(ReviewState).where(ReviewState.topic_id.in_(topic_ids))).all() if topic_ids else []
    due_count = sum(1 for item in due_states if item.due_at.replace(tzinfo=timezone.utc) <= now)
    return {
        "interview_readiness": readiness["readiness"],
        "readiness": readiness,
        "reviews_due": due_count,
        "today_plan": today_plan(session),
        "active_curriculum": {
            "id": curriculum.id,
            "name": curriculum.name,
            "version": curriculum.version,
        },
        "tracks": track_summaries,
        "recommendations": recommendations,
    }
