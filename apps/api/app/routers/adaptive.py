from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    Curriculum, Exercise, LearningSession, PracticeSessionExercise,
    ReviewEvent, ReviewState, Topic, Track, TransferCheck,
)
from ..providers import LLMProvider, ProviderError
from ..providers.dependencies import get_llm_provider
from ..schemas.adaptive import AdaptiveSubmission, PlannerSettingsUpdate
from ..schemas.practice import CodeSubmission, MCQSubmission, ShortAnswerSubmission
from ..services.active_curriculum import get_active_curriculum
from ..services.mastery import mastery_breakdown, recalculate_topic
from ..services.planner import planner_settings, set_plan_status, today_plan, update_planner_settings
from ..services.practice import generate_exercises, public_exercise, submit_code, submit_mcq, submit_short_answer
from ..services.readiness import curriculum_readiness, track_readiness
from ..services.review import apply_review
from ..services.transfer import start_transfer, transfer_session
from ..services.course import current_course_exercise_ids


router = APIRouter(prefix="/api", tags=["adaptive"])


def _topic(session: Session, topic_id: int) -> Topic:
    topic = session.get(Topic, topic_id)
    if not topic: raise HTTPException(status_code=404, detail="Topic not found")
    return topic


def _adaptive_submit(session: Session, exercise: Exercise, session_id: int, request: AdaptiveSubmission, provider: LLMProvider | None, event_type: str) -> dict:
    if exercise.exercise_type == "multiple_choice":
        if request.selected_index is None: raise HTTPException(status_code=422, detail="selected_index is required")
        return submit_mcq(session, exercise, MCQSubmission(session_id=session_id, selected_index=request.selected_index), evidence_type=event_type, assisted=request.assisted)
    if exercise.exercise_type == "short_answer":
        if not request.answer: raise HTTPException(status_code=422, detail="answer is required")
        return submit_short_answer(session, exercise, ShortAnswerSubmission(session_id=session_id, answer=request.answer), provider, evidence_type=event_type, assisted=request.assisted)
    if not request.source or not request.execution: raise HTTPException(status_code=422, detail="source and execution are required")
    return submit_code(session, exercise, CodeSubmission(session_id=session_id, source=request.source, execution=request.execution), evidence_type=event_type, assisted=request.assisted)


@router.get("/topics/{topic_id}/mastery")
def get_mastery(topic_id: int, session: Session = Depends(get_session)) -> dict:
    _topic(session, topic_id); recalculate_topic(session, topic_id)
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


@router.post("/mastery/topics/{topic_id}/transfer/start")
def transfer_start(topic_id: int, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    try:
        learning_session, exercise = start_transfer(session, _topic(session, topic_id), provider)
        return {"session_id": learning_session.id, "topic_id": topic_id, "exercise": public_exercise(exercise)}
    except ValueError as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/mastery/transfer/{session_id}")
def get_transfer(session_id: int, session: Session = Depends(get_session)) -> dict:
    try: return transfer_session(session, session_id)
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/mastery/transfer/{session_id}/submit")
def submit_transfer(session_id: int, request: AdaptiveSubmission, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    check = session.exec(select(TransferCheck).where(TransferCheck.session_id == session_id)).first()
    if not check: raise HTTPException(status_code=404, detail="Transfer session not found")
    if check.attempt_id: raise HTTPException(status_code=409, detail="Transfer check already submitted")
    exercise = session.get(Exercise, check.exercise_id)
    request.assisted = bool(request.assisted or check.assisted)
    result = _adaptive_submit(session, exercise, session_id, request, provider, "transfer")
    if result["evaluation_status"] == "complete":
        check.attempt_id, check.score = result["attempt_id"], result["score"]
        check.passed = bool(result["score"] >= 75 and not request.assisted)
        check.assisted = request.assisted; session.add(check); session.commit(); recalculate_topic(session, check.topic_id)
    return {**result, "transfer_passed": check.passed, "message": "Transfer verified." if check.passed else "Not yet — Forge will recommend another practice session."}


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


@router.post("/reviews/session/start")
def start_reviews(session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    due = reviews_due(session); maximum = planner_settings(session)["max_review_topics"]; items = []
    for row in due[:maximum]:
        topic = session.get(Topic, row["topic_id"])
        exercises = session.exec(select(Exercise).where(Exercise.topic_id == topic.id, Exercise.is_active == True, Exercise.validation_status == "valid", Exercise.source != "transfer").order_by(Exercise.created_at.desc())).all()  # noqa: E712
        current_static = current_course_exercise_ids(session, topic.id)
        exercises = [item for item in exercises if item.source != "course_pack" or item.id in current_static]
        if not exercises and provider:
            try: exercises = generate_exercises(session, topic, provider, 1, purpose="review_generation")
            except ProviderError: exercises = []
        if not exercises: continue
        learning_session = LearningSession(topic_id=topic.id, mode="review"); session.add(learning_session); session.flush()
        session.add(PracticeSessionExercise(session_id=learning_session.id, exercise_id=exercises[0].id, order_index=0)); session.commit()
        items.append({"session_id": learning_session.id, "topic_id": topic.id, "topic_name": topic.name, "exercise": public_exercise(exercises[0])})
    return {"items": items}


@router.post("/reviews/session/{session_id}/submit")
def submit_review(session_id: int, request: AdaptiveSubmission, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    learning = session.get(LearningSession, session_id)
    if not learning or learning.mode != "review": raise HTTPException(status_code=404, detail="Review session not found")
    link = session.exec(select(PracticeSessionExercise).where(PracticeSessionExercise.session_id == session_id)).first()
    exercise = session.get(Exercise, link.exercise_id)
    result = _adaptive_submit(session, exercise, session_id, request, provider, "recall")
    if result["evaluation_status"] != "complete": return result
    event = apply_review(session, learning.topic_id, result["score"], session_id=session_id, attempt_id=result["attempt_id"], assisted=request.assisted)
    recalculate_topic(session, learning.topic_id)
    return {**result, "fsrs_rating": event.fsrs_rating, "next_due_at": event.next_due_at}


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
