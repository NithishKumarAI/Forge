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
    from ..models import Mistake,TopicContentBinding,ContentRevision,ContentSectionProgress
    from .content_publication import release_entries
    approved=[(entry,revision) for entry,revision in release_entries(session,curriculum_id=curriculum.id) if revision.content_type=='lesson_bundle']
    approved_topics={entry.topic_id for entry,_ in approved}
    legacy=session.exec(select(TopicContentBinding,ContentRevision).join(ContentRevision).where(TopicContentBinding.curriculum_id==curriculum.id,ContentRevision.approval_status=='legacy_baseline')).all()
    legacy=[(entry,revision) for entry,revision in legacy if entry.topic_id not in approved_topics]
    available_topics=approved_topics|{entry.topic_id for entry,_ in legacy}
    mistakes=session.exec(select(Mistake).where(Mistake.topic_id.in_(topic_ids)).order_by(Mistake.last_seen_at.desc()).limit(5)).all() if topic_ids else []
    reading=session.exec(select(ContentSectionProgress).where(ContentSectionProgress.topic_id.in_(topic_ids))).all() if topic_ids else []
    return {
        "interview_readiness": readiness["readiness"],
        "readiness": readiness,
        "reviews_due": due_count,
        "today_plan": today_plan(session),
        "content_status":{"approved_lessons":len({r.id for _,r in approved}),"legacy_lessons":len({r.id for _,r in legacy}),"missing_topics":len(topic_ids)-len(available_topics),"total_topics":len(topic_ids)},
        "reading_progress":{"saved_revision_sections":len(reading),"completed_revision_sections":sum(r.completed for r in reading)},
        "recent_mistakes":[{"topic_id":r.topic_id,"topic_name":session.get(Topic,r.topic_id).name,"description":r.description,"occurrence_count":r.occurrence_count} for r in mistakes],
        "active_curriculum": {
            "id": curriculum.id,
            "name": curriculum.name,
            "version": curriculum.version,
        },
        "tracks": track_summaries,
        "recommendations": recommendations,
    }
