from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from ..config import settings
from ..models import AppSetting, ModelUsageEvent
from ..providers import LLMProvider, LLMResult


def estimate_cost(result: LLMResult) -> float:
    usage = result.usage
    non_cached_input = max(0, usage.input_tokens - usage.cached_tokens)
    cost = (
        non_cached_input * settings.gemini_input_price_per_million
        + usage.cached_tokens * settings.gemini_cached_input_price_per_million
        + (usage.output_tokens + usage.thought_tokens)
        * settings.gemini_output_price_per_million
    ) / 1_000_000
    return round(cost, 8)


def record_usage(
    session: Session,
    provider: LLMProvider,
    result: LLMResult,
    *,
    purpose: str,
    thinking_level: str,
) -> ModelUsageEvent:
    event = ModelUsageEvent(
        provider=provider.provider_name,
        model=result.model,
        purpose=purpose,
        thinking_level=thinking_level,
        input_tokens=result.usage.input_tokens,
        output_tokens=result.usage.output_tokens,
        thought_tokens=result.usage.thought_tokens,
        cached_tokens=result.usage.cached_tokens,
        estimated_cost_usd=estimate_cost(result),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def budget_settings(session: Session) -> dict:
    budget = session.get(AppSetting, "monthly_gemini_budget")
    pause = session.get(AppSetting, "pause_nonessential_ai")
    try: amount = max(0.01, float(budget.value)) if budget else 10.0
    except ValueError: amount = 10.0
    return {"monthly_gemini_budget": amount, "pause_nonessential_ai": bool(pause and pause.value.lower() == "true")}


def update_budget_settings(session: Session, *, monthly_gemini_budget: float | None = None, pause_nonessential_ai: bool | None = None) -> dict:
    if monthly_gemini_budget is not None:
        row = session.get(AppSetting, "monthly_gemini_budget") or AppSetting(key="monthly_gemini_budget", value="10")
        row.value = str(monthly_gemini_budget); session.add(row)
    if pause_nonessential_ai is not None:
        row = session.get(AppSetting, "pause_nonessential_ai") or AppSetting(key="pause_nonessential_ai", value="false")
        row.value = str(pause_nonessential_ai).lower(); session.add(row)
    session.commit(); return budget_settings(session)


def budget_summary(session: Session, estimated_cost: float) -> dict:
    configured = budget_settings(session); budget = configured["monthly_gemini_budget"]
    percent = round(estimated_cost / budget * 100, 1) if budget else 0
    if percent >= 100: level, message = "reached", "Estimated Forge API budget reached."
    elif percent >= 90: level, message = "almost", "API budget almost reached."
    elif percent >= 75: level, message = "approaching", "Approaching monthly Forge API budget."
    else: level, message = "normal", "Normal"
    return {**configured, "used_percent": percent, "level": level, "message": message, "disclaimer": "Forge's estimate is not Google billing."}


def nonessential_ai_allowed(session: Session) -> bool:
    usage = monthly_usage(session)
    budget = usage["budget"]
    return not (budget["pause_nonessential_ai"] and budget["used_percent"] >= 100)


def monthly_usage(session: Session) -> dict[str, int | float | dict]:
    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    events = session.exec(
        select(ModelUsageEvent).where(ModelUsageEvent.created_at >= month_start)
    ).all()
    summary = {
        "calls": len(events),
        "input_tokens": sum(event.input_tokens for event in events),
        "output_tokens": sum(event.output_tokens for event in events),
        "thought_tokens": sum(event.thought_tokens for event in events),
        "cached_tokens": sum(event.cached_tokens for event in events),
        "estimated_cost_usd": round(
            sum(event.estimated_cost_usd or 0 for event in events), 6
        ),
    }
    summary["budget"] = budget_summary(session, summary["estimated_cost_usd"])
    return summary
