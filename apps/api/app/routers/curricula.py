from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import Curriculum
from ..providers import LLMProvider, ProviderError
from ..providers.dependencies import get_llm_provider
from ..schemas.ai import (
    CurriculumDraftRequest,
    CurriculumGenerationRequest,
    CurriculumProposal,
)
from ..schemas.api import CurriculumRead
from ..services.active_curriculum import activate_curriculum, get_active_curriculum
from ..services.catalog import curriculum_to_dict
from ..services.curriculum_generation import generate_curriculum_proposal
from ..services.custom_curriculum import (
    CurriculumMutationError,
    confirm_draft,
    create_draft,
    proposal_from_curriculum,
    update_draft,
)


router = APIRouter(prefix="/api/curricula", tags=["curricula"])


def _provider_or_503(provider: LLMProvider | None) -> LLMProvider:
    if provider is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini isn't configured yet. Add GEMINI_API_KEY to apps/api/.env.",
        )
    return provider


@router.get("/active", response_model=CurriculumRead)
def active_curriculum(session: Session = Depends(get_session)) -> dict:
    curriculum = get_active_curriculum(session)
    if curriculum is None:
        raise HTTPException(status_code=404, detail="No confirmed curriculum is available")
    return curriculum_to_dict(session, curriculum)


@router.post("/generate-preview", response_model=CurriculumProposal)
def generate_preview(
    request: CurriculumGenerationRequest,
    session: Session = Depends(get_session),
    provider: LLMProvider | None = Depends(get_llm_provider),
) -> CurriculumProposal:
    try:
        return generate_curriculum_proposal(session, _provider_or_503(provider), request)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/drafts", response_model=CurriculumRead, status_code=201)
def save_draft(
    request: CurriculumDraftRequest, session: Session = Depends(get_session)
) -> dict:
    curriculum = create_draft(session, request)
    return curriculum_to_dict(session, curriculum)


@router.get("/{curriculum_id}/proposal", response_model=CurriculumProposal)
def get_proposal(
    curriculum_id: int, session: Session = Depends(get_session)
) -> CurriculumProposal:
    curriculum = session.get(Curriculum, curriculum_id)
    if curriculum is None:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return proposal_from_curriculum(session, curriculum)


@router.put("/{curriculum_id}/draft", response_model=CurriculumRead)
def edit_draft(
    curriculum_id: int,
    request: CurriculumDraftRequest,
    session: Session = Depends(get_session),
) -> dict:
    curriculum = session.get(Curriculum, curriculum_id)
    if curriculum is None:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    try:
        curriculum = update_draft(session, curriculum, request)
    except CurriculumMutationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return curriculum_to_dict(session, curriculum)


@router.post("/{curriculum_id}/confirm", response_model=CurriculumRead)
def confirm_curriculum(
    curriculum_id: int, session: Session = Depends(get_session)
) -> dict:
    curriculum = session.get(Curriculum, curriculum_id)
    if curriculum is None:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    try:
        curriculum = confirm_draft(session, curriculum)
    except CurriculumMutationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return curriculum_to_dict(session, curriculum)


@router.post("/{curriculum_id}/activate", response_model=CurriculumRead)
def activate(
    curriculum_id: int, session: Session = Depends(get_session)
) -> dict:
    curriculum = session.get(Curriculum, curriculum_id)
    if curriculum is None:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    try:
        activate_curriculum(session, curriculum)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return curriculum_to_dict(session, curriculum)

