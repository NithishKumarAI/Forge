from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..config import settings
from ..database import get_session
from ..schemas.ai import AIStatusRead
from ..schemas.interview import BudgetSettingsUpdate
from ..services.usage import budget_settings, monthly_usage, update_budget_settings


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status", response_model=AIStatusRead)
def ai_status(session: Session = Depends(get_session)) -> dict:
    return {
        "configured": bool(settings.gemini_api_key),
        "provider": "gemini",
        "model": settings.gemini_model,
        "this_month": monthly_usage(session),
    }


@router.get("/settings")
def ai_settings(session: Session = Depends(get_session)) -> dict:
    return budget_settings(session)


@router.put("/settings")
def put_ai_settings(update: BudgetSettingsUpdate, session: Session = Depends(get_session)) -> dict:
    return update_budget_settings(session, **update.model_dump())
