from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import InterviewSession
from ..providers import LLMProvider, ProviderError
from ..providers.dependencies import get_llm_provider
from ..schemas.interview import InterviewAnswerRequest, InterviewCodingRequest, InterviewStartRequest
from ..services.active_curriculum import get_active_curriculum
from ..services.interview import (
    abandon_interview, answer_current, complete_interview, history, interview_read,
    modes, prepare_next, report_for, resume_interview, save_interview, start_interview,
    submit_current_code,
)


router = APIRouter(prefix="/api/interviews", tags=["interviews"])


def _interview(session: Session, interview_id: int) -> InterviewSession:
    row = session.get(InterviewSession, interview_id)
    if not row:
        raise HTTPException(status_code=404, detail="Interview not found")
    return row


def _provider(provider: LLMProvider | None) -> LLMProvider:
    if not provider:
        raise HTTPException(status_code=503, detail="Gemini is required for scored interview questions and evaluation. Configure GEMINI_API_KEY first.")
    return provider


@router.get("/modes")
def interview_modes() -> list[dict]:
    return modes()


@router.post("/start")
def start(request: InterviewStartRequest, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    try:
        row = start_interview(session, request.mode, _provider(provider))
        return interview_read(session, row)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/history")
def interview_history(session: Session = Depends(get_session)) -> list[dict]:
    curriculum = get_active_curriculum(session)
    return history(session, curriculum.id if curriculum else None)


@router.get("/{interview_id}")
def get_interview(interview_id: int, session: Session = Depends(get_session)) -> dict:
    return interview_read(session, _interview(session, interview_id))


@router.post("/{interview_id}/answer")
def answer(interview_id: int, request: InterviewAnswerRequest, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    try:
        return answer_current(session, _interview(session, interview_id), request.answer, request.duration_seconds, _provider(provider))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{interview_id}/coding-submit")
def coding_submit(interview_id: int, request: InterviewCodingRequest, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    try:
        return submit_current_code(session, _interview(session, interview_id), request.source, request.execution, request.duration_seconds, _provider(provider))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{interview_id}/complete")
def complete(interview_id: int, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    try:
        return complete_interview(session, _interview(session, interview_id), provider)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{interview_id}/next")
def next_question(interview_id: int, session: Session = Depends(get_session), provider: LLMProvider | None = Depends(get_llm_provider)) -> dict:
    try:
        return prepare_next(session, _interview(session, interview_id), _provider(provider))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{interview_id}/save")
def save(interview_id: int, session: Session = Depends(get_session)) -> dict:
    try: save_interview(session, _interview(session, interview_id))
    except ValueError as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "saved"}


@router.post("/{interview_id}/resume")
def resume(interview_id: int, session: Session = Depends(get_session)) -> dict:
    row = _interview(session, interview_id)
    try: resume_interview(session, row)
    except ValueError as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc
    return interview_read(session, row)


@router.post("/{interview_id}/abandon")
def abandon(interview_id: int, session: Session = Depends(get_session)) -> dict:
    try: abandon_interview(session, _interview(session, interview_id))
    except ValueError as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "abandoned"}


@router.get("/{interview_id}/report")
def report(interview_id: int, session: Session = Depends(get_session)) -> dict:
    _interview(session, interview_id)
    try: return report_for(session, interview_id)
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
