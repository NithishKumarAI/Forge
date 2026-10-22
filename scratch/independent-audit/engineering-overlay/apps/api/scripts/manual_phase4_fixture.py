"""Seed a disposable Phase 4 browser-smoke database without calling Gemini.

Run only with FORGE_DATABASE_URL pointing to a forge-phase4-smoke.db file.
"""

import json
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app import models  # noqa: F401 -- register all tables
from app.config import settings
from app.database import create_db_and_tables, engine
from app.models import Exercise, LearningSession, MasteryEvidenceEvent, Mistake, PracticeSessionExercise, ReviewState, Topic, Track, TransferCheck
from app.services.curriculum import seed_default_curriculum
from app.services.mastery import recalculate_topic


if not settings.database_url.endswith("forge-phase4-smoke.db"):
    raise SystemExit("Set FORGE_DATABASE_URL to a disposable forge-phase4-smoke.db first")

create_db_and_tables()
now = datetime.now(timezone.utc)
with Session(engine) as session:
    seed_default_curriculum(session, settings.curriculum_path)
    track = session.exec(select(Track).where(Track.slug == "python")).first()
    topics = session.exec(select(Topic).where(Topic.track_id == track.id).order_by(Topic.id).limit(2)).all()
    transfer_topic, review_topic = topics

    def mcq(topic: Topic, title: str, source: str = "manual_smoke_fixture") -> Exercise:
        existing = session.exec(select(Exercise).where(Exercise.topic_id == topic.id, Exercise.title == title)).first()
        if existing:
            existing.content_json = json.dumps({"key": "phase4-smoke", "hints": [], "content": {"choices": ["a + b", "a & b", "a == b"], "correct_index": 0, "explanation": "The + operator adds numbers."}})
            session.add(existing); session.commit()
            return existing
        row = Exercise(
            curriculum_id=track.curriculum_id, track_id=track.id, topic_id=topic.id,
            exercise_type="multiple_choice", title=title,
            prompt_markdown="Which Python expression adds two numeric values?", difficulty="intro",
            source=source, validation_status="valid",
            content_json=json.dumps({"key": "phase4-smoke", "hints": [], "content": {"choices": ["a + b", "a & b", "a == b"], "correct_index": 0, "explanation": "The + operator adds numbers."}}),
        )
        session.add(row); session.flush(); return row

    if not session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.topic_id == transfer_topic.id)).first():
        for offset, kind, weight in [(3, "multiple_choice", .6), (2, "short_answer", .8), (1, "python_code", 1.0)]:
            session.add(MasteryEvidenceEvent(topic_id=transfer_topic.id, event_type="practice", score=90, evidence_weight=weight, metadata_json=json.dumps({"exercise_type": kind, "hints_used": 0}), created_at=now - timedelta(hours=offset)))
        session.add(Mistake(topic_id=transfer_topic.id, category="boundary_case", description="Missed an empty-input boundary case", occurrence_count=2, last_seen_at=now - timedelta(days=1)))
        session.commit(); recalculate_topic(session, transfer_topic.id, now=now)

    transfer_exercise = mcq(transfer_topic, "Unseen transfer scenario", source="transfer")
    open_check = session.exec(select(TransferCheck).where(TransferCheck.topic_id == transfer_topic.id, TransferCheck.attempt_id == None)).first()  # noqa: E711
    if not open_check:
        learning = LearningSession(topic_id=transfer_topic.id, mode="transfer")
        session.add(learning); session.flush()
        session.add(PracticeSessionExercise(session_id=learning.id, exercise_id=transfer_exercise.id, order_index=0))
        session.add(TransferCheck(topic_id=transfer_topic.id, exercise_id=transfer_exercise.id, session_id=learning.id))
        session.commit()

    if not session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.topic_id == review_topic.id)).first():
        session.add(MasteryEvidenceEvent(topic_id=review_topic.id, event_type="practice", score=80, evidence_weight=.8, metadata_json=json.dumps({"exercise_type": "short_answer", "hints_used": 0}), created_at=now - timedelta(days=2)))
        session.commit(); recalculate_topic(session, review_topic.id, now=now - timedelta(days=2))
    mcq(review_topic, "Recall Python addition")
    review = session.get(ReviewState, review_topic.id)
    review.due_at = now - timedelta(minutes=5)
    session.add(review); session.commit()

    print(f"Transfer topic: {transfer_topic.id} — {transfer_topic.name}")
    print(f"Due review topic: {review_topic.id} — {review_topic.name}")
