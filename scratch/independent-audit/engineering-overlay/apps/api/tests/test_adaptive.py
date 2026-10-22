import json
from datetime import datetime, timedelta, timezone

from fsrs import Card, Rating
from sqlmodel import Session, select

from app.models import (
    AppSetting, Exercise, LearnerTopicState, MasteryEvidenceEvent, Mistake,
    ReviewState, Topic, Track,
)
from app.schemas.practice import MCQSubmission
from app.services.mastery import backfill_topic_evidence, mastery_breakdown, recalculate_topic, transfer_eligible
from app.services.planner import today_plan, update_planner_settings
from app.services.readiness import curriculum_readiness
from app.services.review import apply_review, rating_for_performance
from app.services.active_curriculum import get_active_curriculum


def first_topic(session: Session) -> Topic:
    return session.exec(select(Topic).order_by(Topic.id)).first()


def event(session: Session, topic_id: int, kind: str, score: float, exercise_type: str, when: datetime, assisted: bool = False, hints: int = 0) -> MasteryEvidenceEvent:
    weights = {"multiple_choice": .6, "short_answer": .8, "python_code": 1.0, "python_debug": 1.0}
    multiplier = 1 if hints == 0 else .9 if hints == 1 else .78 if hints == 2 else .65
    row = MasteryEvidenceEvent(topic_id=topic_id, event_type=kind, score=score, evidence_weight=weights[exercise_type] * multiplier, assisted=assisted, metadata_json=json.dumps({"exercise_type": exercise_type, "hints_used": hints,"verified":True}), created_at=when)
    session.add(row); session.commit(); return row


def mixed_practice(session: Session, topic: Topic, now: datetime, score: float = 90) -> None:
    event(session, topic.id, "practice", score, "multiple_choice", now - timedelta(hours=3))
    event(session, topic.id, "practice", score, "short_answer", now - timedelta(hours=2))
    event(session, topic.id, "practice", score, "python_code", now - timedelta(hours=1))


def test_practice_cap_confidence_weights_and_hint_penalty(session: Session) -> None:
    topic = first_topic(session); now = datetime.now(timezone.utc)
    event(session, topic.id, "practice", 100, "multiple_choice", now - timedelta(minutes=3), hints=1)
    hinted = mastery_breakdown(session, topic.id)["practice_score"]
    event(session, topic.id, "practice", 100, "python_code", now - timedelta(minutes=2))
    result = recalculate_topic(session, topic.id, now=now)
    assert hinted == 90
    assert result["mastery_score"] == 79
    assert result["confidence"] == "low"
    assert result["current_cap"] == 79
    assert result["practice_score"] > hinted  # higher-value independent code dominates more.


def test_transfer_gates_and_delayed_recall(session: Session) -> None:
    topic = first_topic(session); now = datetime.now(timezone.utc); mixed_practice(session, topic, now)
    assert transfer_eligible(session, topic.id)
    event(session, topic.id, "transfer", 84, "python_code", now)
    strong = recalculate_topic(session, topic.id, now=now)
    assert strong["status"] == "strong" and strong["mastery_score"] < 90
    event(session, topic.id, "recall", 95, "short_answer", now + timedelta(hours=2))
    same_session = recalculate_topic(session, topic.id, now=now + timedelta(hours=2))
    assert same_session["mastery_score"] < 90
    event(session, topic.id, "recall", 95, "python_code", now + timedelta(hours=25))
    ready = recalculate_topic(session, topic.id, now=now + timedelta(hours=25))
    assert ready["status"] == "interview_ready" and ready["mastery_score"] >= 90
    assert ready["confidence"] == "high"
    event(session, topic.id, "recall", 30, "python_code", now + timedelta(days=3))
    weakened = recalculate_topic(session, topic.id, now=now + timedelta(days=3))
    assert weakened["mastery_score"] < ready["mastery_score"]
    assert weakened["status"] != "interview_ready"


def test_failed_or_assisted_transfer_does_not_promote(session: Session) -> None:
    topic = first_topic(session); now = datetime.now(timezone.utc); mixed_practice(session, topic, now)
    event(session, topic.id, "transfer", 95, "python_code", now, assisted=True)
    result = recalculate_topic(session, topic.id, now=now)
    assert result["mastery_score"] <= 79 and result["status"] != "strong"


def test_fsrs_rating_and_review_state(session: Session) -> None:
    assert rating_for_performance(20) == Rating.Again
    assert rating_for_performance(60) == Rating.Hard
    assert rating_for_performance(80) == Rating.Good
    assert rating_for_performance(95) == Rating.Easy
    assert rating_for_performance(95, assisted=True) == Rating.Good
    topic = first_topic(session); now = datetime.now(timezone.utc)
    review = apply_review(session, topic.id, 82, session_id=None, attempt_id=None, reviewed_at=now)
    assert review.next_due_at.replace(tzinfo=timezone.utc) > now
    assert session.get(ReviewState, topic.id) is not None


def test_review_created_only_after_meaningful_evidence(session: Session) -> None:
    topic = first_topic(session); now = datetime.now(timezone.utc)
    event(session, topic.id, "practice", 30, "multiple_choice", now)
    recalculate_topic(session, topic.id, now=now)
    assert session.get(ReviewState, topic.id) is None
    event(session, topic.id, "practice", 100, "python_code", now)
    recalculate_topic(session, topic.id, now=now)
    assert session.get(ReviewState, topic.id) is not None


def test_planner_prioritizes_due_high_priority_and_dsa_with_reasons(session: Session) -> None:
    from tests.phase5_fixtures import published_scope
    published_scope(session)
    curriculum = get_active_curriculum(session); topics = session.exec(select(Topic).join(Track).where(Track.curriculum_id == curriculum.id)).all(); now = datetime.now(timezone.utc)
    high = next(item for item in topics if session.get(Track,item.track_id).slug=='quantitative-aptitude')
    session.add(ReviewState(topic_id=high.id, due_at=now - timedelta(days=1), state_json=json.dumps({"fsrs_schema_version": 1, "card": json.loads(Card().to_json())})))
    update_planner_settings(session, {"daily_study_target": 120, "dsa_daily_minimum": 30, "max_review_topics": 10, "desired_retention": .9})
    plan = today_plan(session, now=now)
    assert plan["items"][0]["item_type"] == "review"
    assert all(item["reason"] for item in plan["items"])
    assert any(item['subject']=='dsa' for item in plan['items'])
    assert all(item['content_references'] for item in plan['items'])
    assert plan['planned_minutes']<=120


def test_readiness_is_weighted_scoped_and_not_probability(session: Session) -> None:
    curriculum = get_active_curriculum(session); summary = curriculum_readiness(session, curriculum)
    assert summary["curriculum_id"] == curriculum.id
    assert "not a hiring probability" in summary["disclaimer"]
    assert summary["total_topics"] > 0
