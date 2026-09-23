from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..providers import LLMProvider, ProviderError
from ..providers.dependencies import get_llm_provider
from ..schemas.ai import DoubtMessageRequest, DoubtMessageResponse
from ..services.doubt import send_doubt
from ..services.interview import assert_assessment_available


router = APIRouter(prefix="/api/doubt", tags=["doubt"])


@router.post("/message", response_model=DoubtMessageResponse)
def message(
    request: DoubtMessageRequest,
    session: Session = Depends(get_session),
    provider: LLMProvider | None = Depends(get_llm_provider),
) -> dict:
    try:
        assert_assessment_available(session)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if provider is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini isn't configured yet. Add GEMINI_API_KEY to apps/api/.env.",
        )
    try:
        doubt_session, reply = send_doubt(
            session,
            provider,
            session_id=request.session_id,
            topic_id=request.topic_id,
            message=request.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"session_id": doubt_session.id, "reply": reply}
