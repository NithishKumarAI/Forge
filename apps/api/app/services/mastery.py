import json
from datetime import datetime, timedelta, timezone

from fsrs import Card, Rating, Scheduler
from sqlmodel import Session, select

from ..models import (
    AppSetting, Attempt, Exercise, ExerciseAttemptDetail, LearnerTopicState,
    LearningSession, MasteryEvidenceEvent, Mistake, ReviewState,
)


EVIDENCE_WEIGHTS = {"multiple_choice": 0.60, "short_answer": 0.80, "numeric":0.80, "sql_code":1.0, "python_code": 1.0, "python_debug": 1.0}
HINT_MULTIPLIERS = {0: 1.0, 1: 0.90, 2: 0.78}
MIN_RECALL_GAP = timedelta(hours=24)


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _hint_multiplier(count: int) -> float:
    return HINT_MULTIPLIERS.get(count, 0.65)


def _setting_float(session: Session, key: str, default: float) -> float:
    row = session.get(AppSetting, key)
    try:
        return float(row.value) if row else default
    except ValueError:
        return default


def record_attempt_evidence(
    session: Session, attempt: Attempt, detail: ExerciseAttemptDetail, exercise: Exercise,
    *, event_type: str = "practice", assisted: bool = False, metadata: dict | None = None,
) -> MasteryEvidenceEvent | None:
    if detail.evaluation_status != "complete":
        return None
    existing = session.exec(select(MasteryEvidenceEvent).where(
        MasteryEvidenceEvent.source_attempt_id == attempt.id,
        MasteryEvidenceEvent.event_type == event_type,
    )).first()
    if existing:
        return existing
    base = EVIDENCE_WEIGHTS.get(exercise.exercise_type, 0.6)
    weight = base * _hint_multiplier(detail.hints_used_count)
    event = MasteryEvidenceEvent(
        topic_id=attempt.topic_id, event_type=event_type, source_attempt_id=attempt.id,
        score=attempt.score, evidence_weight=weight, assisted=assisted,
        metadata_json=json.dumps({"exercise_type": exercise.exercise_type, "hints_used": detail.hints_used_count, **(metadata or {})}),
        created_at=attempt.created_at,
    )
    session.add(event)
    if attempt.score < 70:
        _record_mistake(session, attempt, detail, exercise, metadata or {})
    session.flush()
    return event


def _record_mistake(session: Session, attempt: Attempt, detail: ExerciseAttemptDetail, exercise: Exercise, metadata: dict) -> None:
    summary = json.loads(detail.execution_summary_json or "{}")
    if exercise.exercise_type == "multiple_choice":
        category, description = "concept_misunderstanding", f"Incorrect concept choice in {exercise.title}"
    elif exercise.exercise_type == "short_answer":
        misconception = metadata.get("misconception")
        category, description = ("short_answer_misconception", misconception) if misconception else ("missing_concept", f"Missing rubric concepts in {exercise.title}")
    elif summary.get("status") == "runtime_error":
        category, description = "exception_handling", f"Runtime or syntax error in {exercise.title}"
    else:
        names = " ".join(item.get("name", "") for item in summary.get("tests", []) if not item.get("passed")).lower()
        category = "boundary_case" if any(word in names for word in ("empty", "boundary", "edge", "negative", "zero")) else "incorrect_output"
        description = f"Failed {category.replace('_', ' ')} tests in {exercise.title}"
    mistake = session.exec(select(Mistake).where(Mistake.topic_id == attempt.topic_id, Mistake.category == category, Mistake.description == description)).first()
    if mistake:
        mistake.occurrence_count += 1
        mistake.last_seen_at = attempt.created_at
    else:
        mistake = Mistake(topic_id=attempt.topic_id, category=category, description=description, last_seen_at=attempt.created_at)
    session.add(mistake)


def backfill_topic_evidence(session: Session, topic_id: int) -> int:
    attempts = session.exec(select(Attempt).where(Attempt.topic_id == topic_id).order_by(Attempt.created_at)).all()
    created = 0
    for attempt in attempts:
        detail = session.get(ExerciseAttemptDetail, attempt.id)
        if not detail:
            continue
        exercise = session.get(Exercise, detail.exercise_id)
        learning_session = session.get(LearningSession, detail.session_id)
        event_type = "transfer" if learning_session and learning_session.mode == "transfer" else "recall" if learning_session and learning_session.mode == "review" else "practice"
        if exercise and record_attempt_evidence(session, attempt, detail, exercise, event_type=event_type):
            created += 1
    session.commit()
    return created


def backfill_existing_attempts(session: Session) -> None:
    topic_ids = set(session.exec(select(Attempt.topic_id)).all())
    for topic_id in topic_ids:
        recalculate_topic(session, topic_id)


def practice_metrics(session: Session, topic_id: int) -> dict:
    events = session.exec(select(MasteryEvidenceEvent).where(
        MasteryEvidenceEvent.topic_id == topic_id,
        MasteryEvidenceEvent.event_type.in_(["practice","arena"]),
    ).order_by(MasteryEvidenceEvent.created_at.desc(), MasteryEvidenceEvent.id.desc())).all()
    # Ambiguous old Arena rows are preserved, never promoted by guessing linkage.
    events=[item for item in events if item.event_type!="arena" or _qualified_arena(session,item)][:8]
    base_weight = sum(EVIDENCE_WEIGHTS.get(json.loads(item.metadata_json).get("exercise_type"), 0.6) for item in events)
    score = round(sum(item.score * item.evidence_weight for item in events) / base_weight, 1) if base_weight else None
    types = {json.loads(item.metadata_json).get("exercise_type") for item in events}
    return {"score": score, "count": len(events), "types": sorted(item for item in types if item), "events": events}


def _qualified_arena(session,event):
    from ..models import EvidenceCredit,AssessmentSelection
    credit=session.exec(select(EvidenceCredit).where(EvidenceCredit.event_id==event.id)).one_or_none()
    selected=session.get(AssessmentSelection,credit.selection_id) if credit else None
    return bool(selected and selected.status=="complete" and selected.approval=="approved" and not selected.assisted
        and selected.arena_attempt_id and selected.attempt_id==event.source_attempt_id
        and selected.policy_version=="forge-evidence/2" and json.loads(selected.result_json).get("passed") is True
        and json.loads(selected.result_json).get("verification")=="backend_bounded_worker")


def projection_comparison(session,topic_id):
    """Read-only replay preview. Never backfill or rewrite history/cache here."""
    all_events=session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.topic_id==topic_id)
        .order_by(MasteryEvidenceEvent.created_at.desc(),MasteryEvidenceEvent.id.desc())).all()
    legacy=[e for e in all_events if e.event_type=="practice"][:8]
    denominator=sum(EVIDENCE_WEIGHTS.get(json.loads(e.metadata_json).get("exercise_type"),.6) for e in legacy)
    old=round(sum(e.score*e.evidence_weight for e in legacy)/denominator,1) if denominator else None
    proposed=practice_metrics(session,topic_id)
    return {"old_policy":"legacy/unversioned","new_policy":"forge-evidence/2","old_practice_score":old,"new_practice_score":proposed["score"],
        "excluded_ambiguous_arena_events":sum(e.event_type=="arena" and not _qualified_arena(session,e) for e in all_events)}


def transfer_eligible(session: Session, topic_id: int) -> bool:
    metrics = practice_metrics(session, topic_id)
    from ..models import Topic,Track
    track=session.get(Track,session.get(Topic,topic_id).track_id)
    coding=track.slug in {"python","sql-postgresql","sql-cs","dsa"}
    independent=any(json.loads(e.metadata_json).get("verified") is True and not e.assisted
        and json.loads(e.metadata_json).get("exercise_type") in {"python_code","python_debug","sql_code"} for e in metrics["events"])
    return bool(metrics["score"] is not None and metrics["score"] >= 70 and metrics["count"] >= 2
        and (independent if coding else len(metrics["types"]) >= 1))


def _ensure_review_state(session: Session, topic_id: int, now: datetime) -> ReviewState:
    state = session.get(ReviewState, topic_id)
    if state:
        return state
    scheduler = Scheduler(desired_retention=_setting_float(session, "desired_retention", 0.90), learning_steps=(), relearning_steps=(), enable_fuzzing=False)
    card, _ = scheduler.review_card(Card(), Rating.Good, review_datetime=now)
    minimum_due = now + MIN_RECALL_GAP
    if card.due < minimum_due:
        card.due = minimum_due
    state = ReviewState(topic_id=topic_id, due_at=card.due, state_json=json.dumps({"fsrs_schema_version": 1, "card": json.loads(card.to_json())}))
    session.add(state)
    return state


def recalculate_topic(session: Session, topic_id: int, *, now: datetime | None = None, commit: bool = True) -> dict:
    now = _utc(now or datetime.now(timezone.utc))
    # Historical attempts are not reinterpreted/backfilled merely by browsing or recalculation.
    metrics = practice_metrics(session, topic_id)
    events = session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.topic_id == topic_id).order_by(MasteryEvidenceEvent.created_at)).all()
    transfers = [item for item in events if item.event_type == "transfer"]
    recalls = [item for item in events if item.event_type == "recall"]
    from ..models import EvidencePolicyRecord,Topic,Track
    policy=session.get(EvidencePolicyRecord,topic_id)
    track=session.get(Track,session.get(Topic,topic_id).track_id)
    if policy and track.slug in {"python","sql-postgresql","sql-cs","dsa"}:
        def independent_code(event):
            metadata=json.loads(event.metadata_json)
            return metadata.get("verified") is True and metadata.get("exercise_type") in {"python_code","python_debug","sql_code"}
        transfers=[e for e in transfers if independent_code(e)]
        recalls=[e for e in recalls if independent_code(e)]
    clean_transfer = next((item for item in reversed(transfers) if item.score >= 75 and not item.assisted), None)
    valid_recalls = [item for item in recalls if clean_transfer and _utc(item.created_at) - _utc(clean_transfer.created_at) >= MIN_RECALL_GAP]
    latest_recall = valid_recalls[-1] if valid_recalls else None
    practice_score = metrics["score"]
    mastery = min(79, round(practice_score)) if practice_score is not None else 0
    cap = 79
    if clean_transfer:
        mastery = max(80, min(89, round(0.65 * (practice_score or 0) + 0.35 * clean_transfer.score)))
        cap = 89
    if latest_recall:
        if latest_recall.score >= 75 and not latest_recall.assisted:
            mastery = max(90, min(100, round(0.4 * (practice_score or 0) + 0.3 * clean_transfer.score + 0.3 * latest_recall.score)))
            cap = 100
        else:
            mastery = min(89, round(0.45 * (practice_score or 0) + 0.25 * clean_transfer.score + 0.30 * latest_recall.score))
            cap = 89
    if not events:
        status = "not_started"
    elif mastery < 40:
        status = "learning"
    elif mastery < 70:
        status = "working"
    elif mastery < 90:
        status = "strong" if clean_transfer else "working"
    else:
        status = "interview_ready"
    if not metrics["count"]:
        confidence = "unknown"
    elif metrics["count"] <= 2:
        confidence = "low"
    elif clean_transfer and latest_recall and latest_recall.score >= 75 and not latest_recall.assisted and len(metrics["types"]) >= 2:
        confidence = "high"
    else:
        confidence = "medium" if len(metrics["types"]) >= 2 else "low"
    state = session.get(LearnerTopicState, topic_id) or LearnerTopicState(topic_id=topic_id)
    state.mastery_score, state.status, state.confidence, state.attempts = mastery, status, confidence, metrics["count"]
    state.last_tested_at = max((_utc(item.created_at) for item in events), default=state.last_tested_at)
    if (practice_score or 0) >= 60 or clean_transfer:
        review = _ensure_review_state(session, topic_id, now)
        if clean_transfer:
            minimum_due = _utc(clean_transfer.created_at) + MIN_RECALL_GAP
            if _utc(review.due_at) < minimum_due:
                wrapper = json.loads(review.state_json)
                card = Card.from_json(json.dumps(wrapper["card"]))
                card.due = minimum_due
                review.due_at = minimum_due
                review.state_json = json.dumps({"fsrs_schema_version": 1, "card": json.loads(card.to_json())})
                session.add(review)
        state.next_review_at = review.due_at
    session.add(state)
    if commit:session.commit()
    else:session.flush()
    return mastery_breakdown(session, topic_id, cap=cap)


def mastery_breakdown(session: Session, topic_id: int, cap: int | None = None) -> dict:
    metrics = practice_metrics(session, topic_id)
    state = session.get(LearnerTopicState, topic_id) or LearnerTopicState(topic_id=topic_id)
    events = session.exec(select(MasteryEvidenceEvent).where(MasteryEvidenceEvent.topic_id == topic_id).order_by(MasteryEvidenceEvent.created_at)).all()
    from ..models import EvidencePolicyRecord,Topic,Track
    if session.get(EvidencePolicyRecord,topic_id) and session.get(Track,session.get(Topic,topic_id).track_id).slug in {"python","sql-postgresql","sql-cs","dsa"}:
        events=[event for event in events if event.event_type not in {"transfer","recall"} or
            (json.loads(event.metadata_json).get("verified") is True and
             json.loads(event.metadata_json).get("exercise_type") in {"python_code","python_debug","sql_code"})]
    transfer = next((item for item in reversed(events) if item.event_type == "transfer"), None)
    recall = next((item for item in reversed(events) if item.event_type == "recall"), None)
    clean=next((item for item in reversed(events) if item.event_type=="transfer" and item.score>=75 and not item.assisted),None)
    mistakes = session.exec(select(Mistake).where(Mistake.topic_id == topic_id).order_by(Mistake.occurrence_count.desc())).all()
    inferred_cap = cap or (100 if state.status == "interview_ready" else 89 if clean else 79)
    return {
        "topic_id": topic_id, "mastery_score": state.mastery_score, "status": state.status, "confidence": state.confidence,
        "practice_score": metrics["score"], "practice_attempts": metrics["count"], "evidence_types": metrics["types"],
        "transfer_eligible": transfer_eligible(session, topic_id),
        "transfer": None if not transfer else {"score": transfer.score, "passed": transfer.score >= 75 and not transfer.assisted, "assisted": transfer.assisted, "at": transfer.created_at},
        "delayed_recall": None if not recall else {"score": recall.score, "passed": bool(recall.score >= 75 and not recall.assisted and clean and _utc(recall.created_at)-_utc(clean.created_at)>=MIN_RECALL_GAP), "at": recall.created_at},
        "current_cap": inferred_cap,
        "cap_reason": "Complete a clean transfer check to progress beyond 79." if inferred_cap == 79 else "Pass delayed recall after at least 24 hours to progress beyond 89." if inferred_cap == 89 else "Transfer and delayed recall gates completed.",
        "mistakes": [{"category": item.category, "description": item.description, "occurrence_count": item.occurrence_count, "last_seen_at": item.last_seen_at} for item in mistakes],
        "next_review_at": state.next_review_at,
    }
