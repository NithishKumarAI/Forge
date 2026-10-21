from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ..database import get_session
from ..models import Exercise, LearningSession, Topic
from ..providers import LLMProvider, ProviderError
from ..providers.dependencies import get_llm_provider
from ..schemas.practice import (
    AttemptRead, CodeSubmission, HintRead, MCQSubmission, PracticeHistory,
    PracticeSessionRead, PracticeStartResponse, PublicExercise,
    ShortAnswerSubmission,
)
from ..services.practice import (
    PracticeError, mark_reference_validation, practice_history, public_exercise,
    reference_validation_payload, reveal_hint, session_exercises, start_practice,
    submission_tests, submit_code, submit_mcq, submit_short_answer,
)


router = APIRouter(prefix="/api/practice", tags=["practice"])


def _exercise(session: Session, exercise_id: int) -> Exercise:
    exercise = session.get(Exercise, exercise_id)
    if exercise is None or not exercise.is_active:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


def _conflict(exc: PracticeError) -> HTTPException:
    return HTTPException(status_code=409, detail=str(exc))


@router.post("/topics/{topic_id}/start", response_model=PracticeStartResponse)
def start(
    topic_id: int,
    session: Session = Depends(get_session),
    provider: LLMProvider | None = Depends(get_llm_provider),
) -> dict:
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    try:
        practice_session, exercises = start_practice(session, topic, provider)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"session_id": practice_session.id, "exercises": [public_exercise(item) for item in exercises]}


@router.get("/sessions/{session_id}", response_model=PracticeSessionRead)
def get_practice_session(session_id: int, session: Session = Depends(get_session)) -> dict:
    practice_session = session.get(LearningSession, session_id)
    if practice_session is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    try:
        exercises = session_exercises(session, practice_session)
    except PracticeError as exc:
        raise _conflict(exc) from exc
    return {"session_id": session_id, "topic_id": practice_session.topic_id, "exercises": [public_exercise(item) for item in exercises]}


@router.get("/topics/{topic_id}/history", response_model=PracticeHistory)
def history(topic_id: int, session: Session = Depends(get_session)) -> dict:
    if session.get(Topic, topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return practice_history(session, topic_id)


@router.get("/exercises/{exercise_id}", response_model=PublicExercise)
def get_exercise(exercise_id: int, session: Session = Depends(get_session)) -> dict:
    return public_exercise(_exercise(session, exercise_id))


class SessionRequest(BaseModel):
    session_id: int


class ValidationReport(BaseModel):
    passed: bool


@router.post("/exercises/{exercise_id}/hint", response_model=HintRead)
def hint(exercise_id: int, request: SessionRequest, session: Session = Depends(get_session)) -> dict:
    try:
        return reveal_hint(session, _exercise(session, exercise_id), request.session_id)
    except PracticeError as exc:
        raise _conflict(exc) from exc


@router.get("/exercises/{exercise_id}/submission-tests")
def get_submission_tests(exercise_id: int, session: Session = Depends(get_session)) -> dict:
    try:
        return submission_tests(_exercise(session, exercise_id))
    except PracticeError as exc:
        raise _conflict(exc) from exc


@router.get("/exercises/{exercise_id}/reference-validation")
def get_reference_validation(exercise_id: int, session: Session = Depends(get_session)) -> dict:
    try:
        return reference_validation_payload(_exercise(session, exercise_id))
    except PracticeError as exc:
        raise _conflict(exc) from exc


@router.post("/exercises/{exercise_id}/reference-validation")
def report_reference_validation(
    exercise_id: int, report: ValidationReport, session: Session = Depends(get_session)
) -> dict:
    try:
        mark_reference_validation(session, _exercise(session, exercise_id), report.passed)
    except PracticeError as exc:
        raise _conflict(exc) from exc
    return {"validation_status": "valid" if report.passed else "invalid"}


@router.post("/exercises/{exercise_id}/submit/mcq", response_model=AttemptRead)
def mcq(exercise_id: int, request: MCQSubmission, session: Session = Depends(get_session)) -> dict:
    try:
        return submit_mcq(session, _exercise(session, exercise_id), request)
    except PracticeError as exc:
        raise _conflict(exc) from exc


@router.post("/exercises/{exercise_id}/submit/short-answer", response_model=AttemptRead)
def short_answer(
    exercise_id: int, request: ShortAnswerSubmission,
    session: Session = Depends(get_session),
    provider: LLMProvider | None = Depends(get_llm_provider),
) -> dict:
    try:
        return submit_short_answer(session, _exercise(session, exercise_id), request, provider)
    except PracticeError as exc:
        raise _conflict(exc) from exc


@router.post("/exercises/{exercise_id}/submit/code", response_model=AttemptRead)
def code(exercise_id: int, request: CodeSubmission, session: Session = Depends(get_session)) -> dict:
    try:
        return submit_code(session, _exercise(session, exercise_id), request)
    except PracticeError as exc:
        raise _conflict(exc) from exc
