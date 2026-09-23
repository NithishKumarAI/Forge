from datetime import date, datetime, timezone

from sqlmodel import Session, select

from ..models import AppSetting, DailyPlanItem, LearnerTopicState, Mistake, ReviewState, Topic, TopicPrerequisite, Track
from .active_curriculum import get_active_curriculum
from .mastery import transfer_eligible


DEFAULT_SETTINGS = {"daily_study_target": "150", "dsa_daily_minimum": "30", "max_review_topics": "10", "desired_retention": "0.90"}


def planner_settings(session: Session) -> dict:
    values = {}
    for key, default in DEFAULT_SETTINGS.items():
        setting = session.get(AppSetting, key)
        values[key] = setting.value if setting else default
    return {"daily_study_target": int(values["daily_study_target"]), "dsa_daily_minimum": int(values["dsa_daily_minimum"]), "max_review_topics": int(values["max_review_topics"]), "desired_retention": float(values["desired_retention"])}


def update_planner_settings(session: Session, values: dict) -> dict:
    limits = {"daily_study_target": (30, 480), "dsa_daily_minimum": (0, 120), "max_review_topics": (1, 30), "desired_retention": (0.70, 0.97)}
    for key, value in values.items():
        if value is None: continue
        low, high = limits[key]
        if not low <= value <= high: raise ValueError(f"{key} must be between {low} and {high}")
        setting = session.get(AppSetting, key) or AppSetting(key=key, value=str(value))
        setting.value = str(value); session.add(setting)
    session.commit()
    return planner_settings(session)


def _add(session: Session, curriculum_id: int, day: str, topic: Topic, kind: str, reason: str, minutes: int, order: int) -> DailyPlanItem:
    item = DailyPlanItem(plan_date=day, curriculum_id=curriculum_id, topic_id=topic.id, item_type=kind, reason=reason, estimated_minutes=minutes, order_index=order)
    session.add(item); return item


def today_plan(session: Session, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc); day = now.date().isoformat()
    curriculum = get_active_curriculum(session)
    if not curriculum: return {"date": day, "target_minutes": 0, "planned_minutes": 0, "items": []}
    existing = session.exec(select(DailyPlanItem).where(DailyPlanItem.plan_date == day, DailyPlanItem.curriculum_id == curriculum.id).order_by(DailyPlanItem.order_index)).all()
    settings = planner_settings(session)
    if not existing:
        tracks = session.exec(select(Track).where(Track.curriculum_id == curriculum.id)).all()
        topics = session.exec(select(Topic).join(Track).where(Track.curriculum_id == curriculum.id)).all()
        topic_ids = {topic.id for topic in topics}; order = 0; used = set(); minutes = 0
        due = session.exec(select(ReviewState).where(ReviewState.due_at <= now).order_by(ReviewState.due_at)).all()
        for review in [item for item in due if item.topic_id in topic_ids][:settings["max_review_topics"]]:
            topic = session.get(Topic, review.topic_id); _add(session, curriculum.id, day, topic, "review", "Due for review today.", 10, order); order += 1; minutes += 10; used.add(topic.id)
        mistakes = session.exec(select(Mistake).where(Mistake.topic_id.in_(topic_ids), Mistake.occurrence_count >= 2).order_by(Mistake.occurrence_count.desc())).all()
        for mistake in mistakes[:2]:
            if mistake.topic_id in used: continue
            topic = session.get(Topic, mistake.topic_id); _add(session, curriculum.id, day, topic, "practice", f"Recurring {mistake.description.lower()} ×{mistake.occurrence_count}.", min(35, topic.estimated_minutes), order); order += 1; minutes += min(35, topic.estimated_minutes); used.add(topic.id)
        dsa_tracks = [track for track in tracks if "dsa" in track.slug.lower() or "algorithm" in track.name.lower()]
        if settings["dsa_daily_minimum"] > 0 and dsa_tracks:
            dsa_topics = [topic for topic in topics if topic.track_id in {track.id for track in dsa_tracks} and (session.get(LearnerTopicState, topic.id) or LearnerTopicState(topic_id=topic.id)).mastery_score < 70]
            if dsa_topics:
                topic = sorted(dsa_topics, key=lambda item: (-(item.priority), (session.get(LearnerTopicState, item.id) or LearnerTopicState(topic_id=item.id)).mastery_score))[0]
                if topic.id not in used: _add(session, curriculum.id, day, topic, "practice", f"DSA daily minimum: {settings['dsa_daily_minimum']} minutes; topic is below strong.", settings["dsa_daily_minimum"], order); order += 1; minutes += settings["dsa_daily_minimum"]; used.add(topic.id)
        candidates = []
        for topic in topics:
            if topic.id in used: continue
            state = session.get(LearnerTopicState, topic.id) or LearnerTopicState(topic_id=topic.id)
            if state.status == "interview_ready": continue
            prereqs = session.exec(select(TopicPrerequisite).where(TopicPrerequisite.topic_id == topic.id)).all()
            blocked = any((session.get(LearnerTopicState, link.prerequisite_topic_id) or LearnerTopicState(topic_id=link.prerequisite_topic_id)).mastery_score < 60 for link in prereqs)
            if transfer_eligible(session, topic.id): score, kind, reason = 85, "transfer", "Ready for transfer verification after strong mixed practice evidence."
            elif topic.priority >= 70 and state.mastery_score < 70: score, kind, reason = 75 + (70-state.mastery_score), "practice", f"High-priority interview topic; mastery {state.mastery_score}%."
            elif blocked: score, kind, reason = 35, "learn", "Prerequisites are not ready yet; study a prerequisite first."
            else: score, kind, reason = 50-state.mastery_score/2, "practice", f"Developing topic; mastery {state.mastery_score}% and confidence {state.confidence}."
            candidates.append((score, topic, kind, reason))
        for _, topic, kind, reason in sorted(candidates, key=lambda item: (-item[0], -item[1].priority, item[1].order_index)):
            if minutes >= settings["daily_study_target"]: break
            duration = 25 if kind == "transfer" else min(45, topic.estimated_minutes)
            _add(session, curriculum.id, day, topic, kind, reason, duration, order); order += 1; minutes += duration
        session.commit()
        existing = session.exec(select(DailyPlanItem).where(DailyPlanItem.plan_date == day, DailyPlanItem.curriculum_id == curriculum.id).order_by(DailyPlanItem.order_index)).all()
    rows = []
    for item in existing:
        topic = session.get(Topic, item.topic_id) if item.topic_id else None; track = session.get(Track, topic.track_id) if topic else None
        action = "/review" if item.item_type == "review" else f"/topics/{topic.id}/transfer" if item.item_type == "transfer" else f"/topics/{topic.id}"
        rows.append({"id": item.id, "topic_id": item.topic_id, "topic_name": topic.name if topic else None, "track_name": track.name if track else None, "item_type": item.item_type, "reason": item.reason, "estimated_minutes": item.estimated_minutes, "order_index": item.order_index, "status": item.status, "action_path": action})
    return {"date": day, "target_minutes": settings["daily_study_target"], "planned_minutes": sum(item.estimated_minutes for item in existing if item.status == "planned"), "items": rows}


def set_plan_status(session: Session, item_id: int, status: str) -> None:
    item = session.get(DailyPlanItem, item_id)
    if not item: raise ValueError("Plan item not found")
    item.status = status; session.add(item); session.commit()
