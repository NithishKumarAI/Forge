"""Seed disposable interview history and budget state for the final V1 browser smoke test."""

import json
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app import models  # noqa: F401
from app.config import settings
from app.database import create_db_and_tables, engine
from app.models import AppSetting, InterviewQuestion, InterviewReport, InterviewSession, ModelUsageEvent, Topic
from app.services.active_curriculum import get_active_curriculum
from app.services.curriculum import seed_default_curriculum
from app.services.interview import _fixed_rubric


if not settings.database_url.endswith("forge-v1-smoke.db"):
    raise SystemExit("Set FORGE_DATABASE_URL to a disposable forge-v1-smoke.db first")

create_db_and_tables()
with Session(engine) as session:
    seed_default_curriculum(session, settings.curriculum_path)
    curriculum = get_active_curriculum(session)
    topic = session.exec(select(Topic).order_by(Topic.priority.desc(), Topic.id)).first()
    completed = session.exec(select(InterviewSession).where(InterviewSession.status == "completed")).first()
    saved = session.exec(select(InterviewSession).where(InterviewSession.status == "saved")).first()
    if not completed:
        completed = InterviewSession(
            curriculum_id=curriculum.id, mode="quick", status="completed",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
            completed_at=datetime.now(timezone.utc) - timedelta(days=2, minutes=-18),
            overall_score=72, duration_seconds=1080,
            metadata_json=json.dumps({"blueprint_version": 1, "fixture": True}),
        )
        session.add(completed); session.flush()
        report = {
            "label": "Forge Interview Score", "overall_score": 72,
            "section_scores": {"python_backend": 74, "llm_rag": 76, "coding": 68, "project": 82, "behavioral": 70},
            "strengths": ["LLM tool-calling fundamentals", "Project architecture explanation"],
            "priority_gaps": ["Timeout boundaries", "SQL indexing trade-offs"],
            "communication_feedback": ["State failure modes before implementation detail."],
            "recommended_topics": [{"topic_id": topic.id, "topic_name": topic.name, "reason": "Review this high-priority curriculum topic before the next mock."}],
            "summary": "A solid baseline with specific reliability and communication gaps to practice.",
            "disclaimer": "Forge Interview Score is not a hiring probability.",
        }
        session.add(InterviewReport(session_id=completed.id, report_json=json.dumps(report)))
        saved = InterviewSession(curriculum_id=curriculum.id, mode="python_backend", status="saved", metadata_json=json.dumps({"blueprint_version": 1, "fixture": True}))
        session.add(saved); session.flush()
        session.add(InterviewQuestion(
            session_id=saved.id, section="backend", competency="FastAPI, HTTP, authentication, async, and external APIs",
            question_type="scenario", prompt_markdown="How would you keep an unreliable external API from hanging a FastAPI request?",
            topic_id=topic.id, rubric_json=json.dumps(_fixed_rubric("scenario", "Backend reliability")),
            expected_concepts_json=json.dumps(["timeout", "bounded retry", "error handling"]), difficulty="medium",
            suggested_seconds=180, blueprint_slot=0, order_index=0, generated_by="manual_fixture",
        ))
        session.add(ModelUsageEvent(provider="fake", model="manual-fixture", purpose="manual_fixture", thinking_level="none", estimated_cost_usd=9.1))
        session.add(AppSetting(key="monthly_gemini_budget", value="10"))
        session.add(AppSetting(key="pause_nonessential_ai", value="false"))
        session.commit()
    print(f"Completed report: /interview/{completed.id}/report")
    print(f"Saved interview: /interview/{saved.id}")
