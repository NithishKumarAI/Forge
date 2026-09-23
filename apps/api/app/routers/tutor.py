from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import LearningSession, Topic
from ..providers import LLMProvider, ProviderError
from ..providers.dependencies import get_llm_provider
from ..schemas.ai import (
    ChatMessageRead,
    TutorMessageRequest,
    TutorStartResponse,
    TutorTurn,
)
from ..services.tutor import (
    continue_tutor_session,
    get_session_messages,
    start_tutor_session,
)
from ..services.interview import assert_assessment_available


router = APIRouter(prefix="/api/tutor", tags=["tutor"])


def _provider_or_503(provider: LLMProvider | None) -> LLMProvider:
    if provider is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini isn't configured yet. Add GEMINI_API_KEY to apps/api/.env.",
        )
    return provider


@router.post("/topics/{topic_id}/start", response_model=TutorStartResponse)
def start(
    topic_id: int,
    session: Session = Depends(get_session),
    provider: LLMProvider | None = Depends(get_llm_provider),
) -> dict:
    try:
        assert_assessment_available(session)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    try:
        learning_session, turn = start_tutor_session(
            session, _provider_or_503(provider), topic
        )
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"session_id": learning_session.id, "turn": turn}


@router.post("/sessions/{session_id}/message", response_model=TutorTurn)
def message(
    session_id: int,
    request: TutorMessageRequest,
    session: Session = Depends(get_session),
    provider: LLMProvider | None = Depends(get_llm_provider),
) -> TutorTurn:
    try:
        assert_assessment_available(session)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    learning_session = session.get(LearningSession, session_id)
    if learning_session is None:
        raise HTTPException(status_code=404, detail="Learning session not found")
    try:
        return continue_tutor_session(
            session, _provider_or_503(provider), learning_session, request.message
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
def messages(session_id: int, session: Session = Depends(get_session)) -> list[dict]:
    learning_session = session.get(LearningSession, session_id)
    if learning_session is None:
        raise HTTPException(status_code=404, detail="Learning session not found")
    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "chat_type": message.chat_type,
            "created_at": message.created_at,
        }
        for message in get_session_messages(session, session_id)
    ]
