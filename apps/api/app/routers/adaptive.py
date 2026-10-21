from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    Curriculum, Exercise, LearningSession, PracticeSessionExercise,
    ReviewEvent, ReviewState, Topic, Track, TransferCheck,
)
from ..schemas.adaptive import AdaptiveSubmission, PlannerSettingsUpdate
from ..schemas.practice import CodeSubmission, MCQSubmission, ShortAnswerSubmission
from ..services.active_curriculum import get_active_curriculum
from ..services.mastery import mastery_breakdown, recalculate_topic
from ..services.planner import planner_settings, set_plan_status, today_plan, update_planner_settings
from ..services.readiness import curriculum_readiness, track_readiness
from ..services.review import apply_review
from ..services.course import current_course_exercise_ids


router = APIRouter(prefix="/api", tags=["adaptive"])


def _topic(session: Session, topic_id: int) -> Topic:
    topic = session.get(Topic, topic_id)
    if not topic: raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/topics/{topic_id}/mastery")
def get_mastery(topic_id: int, session: Session = Depends(get_session)) -> dict:
    _topic(session, topic_id)
    return mastery_breakdown(session, topic_id)


@router.post("/topics/{topic_id}/recalculate")
def recalculate(topic_id: int, session: Session = Depends(get_session)) -> dict:
    _topic(session, topic_id); return recalculate_topic(session, topic_id)


@router.get("/tracks/{track_id}/readiness")
def get_track_readiness(track_id: int, session: Session = Depends(get_session)) -> dict:
    track = session.get(Track, track_id)
    if not track: raise HTTPException(status_code=404, detail="Track not found")
    return track_readiness(session, track)


@router.get("/curricula/{curriculum_id}/readiness")
def get_curriculum_readiness(curriculum_id: int, session: Session = Depends(get_session)) -> dict:
    curriculum = session.get(Curriculum, curriculum_id)
    if not curriculum: raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum_readiness(session, curriculum)


def _review_queue(session: Session, now: datetime) -> list[dict]:
    curriculum = get_active_curriculum(session)
    if not curriculum: return []
    rows = session.exec(select(ReviewState).join(Topic).join(Track).where(Track.curriculum_id == curriculum.id).order_by(ReviewState.due_at)).all()
    result = []
    for row in rows:
        topic = session.get(Topic, row.topic_id); track = session.get(Track, topic.track_id)
        result.append({"topic_id": topic.id, "topic_name": topic.name, "track_name": track.name, "due_at": row.due_at})
    return result


@router.get("/reviews/due")
def reviews_due(session: Session = Depends(get_session)) -> list[dict]:
    now = datetime.now(timezone.utc); return [item for item in _review_queue(session, now) if item["due_at"].replace(tzinfo=timezone.utc) <= now]


@router.get("/reviews/upcoming")
def reviews_upcoming(session: Session = Depends(get_session)) -> dict:
    now = datetime.now(timezone.utc); rows = _review_queue(session, now)
    tomorrow = sum(1 for item in rows if now < item["due_at"].replace(tzinfo=timezone.utc) <= now + timedelta(days=1))
    week = sum(1 for item in rows if now < item["due_at"].replace(tzinfo=timezone.utc) <= now + timedelta(days=7))
    curriculum = get_active_curriculum(session)
    recent = [] if not curriculum else session.exec(select(ReviewEvent).join(Topic).join(Track).where(Track.curriculum_id == curriculum.id).order_by(ReviewEvent.reviewed_at.desc()).limit(5)).all()
    return {"tomorrow": tomorrow, "next_7_days": week, "items": [item for item in rows if item["due_at"].replace(tzinfo=timezone.utc) > now][:10], "recently_reviewed": [{"topic_id": item.topic_id, "topic_name": session.get(Topic, item.topic_id).name, "score": item.score, "at": item.reviewed_at} for item in recent]}


@router.get("/planner/today")
def planner_today(session: Session = Depends(get_session)) -> dict: return today_plan(session)


@router.post("/planner/items/{item_id}/skip")
def planner_skip(item_id: int, session: Session = Depends(get_session)) -> dict:
    try: set_plan_status(session, item_id, "skipped")
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "skipped"}


@router.post("/planner/items/{item_id}/complete")
def planner_complete(item_id: int, session: Session = Depends(get_session)) -> dict:
    try: set_plan_status(session, item_id, "completed")
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "completed"}


@router.get("/planner/settings")
def get_planner_settings(session: Session = Depends(get_session)) -> dict: return planner_settings(session)


@router.put("/planner/settings")
def put_planner_settings(update: PlannerSettingsUpdate, session: Session = Depends(get_session)) -> dict:
    try: return update_planner_settings(session, update.model_dump(exclude_unset=True))
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
