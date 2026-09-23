import json
from datetime import datetime, timezone

from fsrs import Card, Rating, Scheduler
from sqlmodel import Session

from ..models import AppSetting, LearnerTopicState, ReviewEvent, ReviewState


def rating_for_performance(score: float, assisted: bool = False) -> Rating:
    rating = Rating.Again if score < 50 else Rating.Hard if score < 70 else Rating.Good if score < 90 else Rating.Easy
    if assisted and rating == Rating.Easy:
        rating = Rating.Good
    return rating


def _retention(session: Session) -> float:
    setting = session.get(AppSetting, "desired_retention")
    try:
        return min(0.97, max(0.70, float(setting.value))) if setting else 0.90
    except ValueError:
        return 0.90


def apply_review(
    session: Session, topic_id: int, score: float, *, session_id: int | None,
    attempt_id: int | None, assisted: bool = False, reviewed_at: datetime | None = None,
) -> ReviewEvent:
    reviewed_at = reviewed_at or datetime.now(timezone.utc)
    if reviewed_at.tzinfo is None:
        reviewed_at = reviewed_at.replace(tzinfo=timezone.utc)
    state = session.get(ReviewState, topic_id)
    payload = json.loads(state.state_json) if state else {}
    card = Card.from_json(json.dumps(payload["card"])) if payload.get("card") else Card()
    previous_due = state.due_at if state else None
    rating = rating_for_performance(score, assisted)
    scheduler = Scheduler(desired_retention=_retention(session), learning_steps=(), relearning_steps=(), enable_fuzzing=False)
    card, _ = scheduler.review_card(card, rating, review_datetime=reviewed_at)
    if state is None:
        state = ReviewState(topic_id=topic_id, due_at=card.due)
    state.due_at = card.due
    state.state_json = json.dumps({"fsrs_schema_version": 1, "card": json.loads(card.to_json())})
    event = ReviewEvent(
        topic_id=topic_id, session_id=session_id, attempt_id=attempt_id, score=score,
        fsrs_rating=int(rating), reviewed_at=reviewed_at, previous_due_at=previous_due,
        next_due_at=card.due, metadata_json=json.dumps({"assisted": assisted}),
    )
    learner = session.get(LearnerTopicState, topic_id)
    if learner:
        learner.next_review_at = card.due
        session.add(learner)
    session.add(state)
    session.add(event)
    session.commit()
    return event
