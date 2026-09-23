import json
from datetime import datetime

from pydantic import ValidationError
from sqlmodel import Session, select

from ..config import settings
from ..models import (
    Attempt, ChatMessage, Curriculum, Exercise, ExerciseAttemptDetail,
    LearnerTopicState, LearningSession, Mistake, PracticeHintUse,
    PracticeSessionExercise, Topic, TopicPrerequisite, Track,
)
from ..providers import InvalidStructuredResponse, LLMProvider, ProviderError
from ..schemas.practice import (
    AttemptRead, CodeSubmission, ExercisePackProposal, ExerciseProposal,
    MCQSubmission, PublicExercise, ShortAnswerEvaluation, ShortAnswerSubmission,
)
from .usage import nonessential_ai_allowed, record_usage


EXERCISE_POLICY = """Create compact entry-level AI/backend/Python interview practice.
Generate diverse exercises testing understanding and application, not trivia.
Use standard-library Python only, no network, packages, OS manipulation, or long computation.
For coding/debugging, require one named function with JSON-serializable args, kwargs and expected results.
Provide 2-3 progressive hints without revealing final code. Keep each task small.
The reference solution must pass every supplied sample and hidden test.
Use multiple choice, short answer, and Python coding/debugging according to the topic."""

ANSWER_POLICY = """Grade a short technical answer only against the fixed rubric and reference concepts.
Be fair to equivalent wording. Give concise, actionable feedback. Do not alter the exercise,
rubric, curriculum, or learner mastery. Return the requested structured evaluation."""


class PracticeError(ValueError):
    pass


def _content(exercise: Exercise) -> dict:
    return json.loads(exercise.content_json)


def public_exercise(exercise: Exercise) -> dict:
    stored = _content(exercise)
    content = stored["content"]
    kind = exercise.exercise_type
    if kind == "multiple_choice":
        exposed = {"choices": content["choices"]}
    elif kind == "short_answer":
        exposed = {}
    else:
        exposed = {
            "starter_code": content.get("starter_code") or content.get("broken_code"),
            "function_name": content["function_name"],
            "sample_tests": content["sample_tests"],
            "time_limit_ms": content["time_limit_ms"],
        }
    return {
        "id": exercise.id,
        "topic_id": exercise.topic_id,
        "exercise_type": kind,
        "title": exercise.title,
        "prompt_markdown": exercise.prompt_markdown,
        "difficulty": exercise.difficulty,
        "hints_available": len(stored["hints"]),
        "validation_status": exercise.validation_status,
        "content": exposed,
    }


def _topic_context(session: Session, topic: Topic) -> str:
    track = session.get(Track, topic.track_id)
    curriculum = session.get(Curriculum, track.curriculum_id)
    state = session.get(LearnerTopicState, topic.id)
    prerequisites = []
    for link in session.exec(select(TopicPrerequisite).where(TopicPrerequisite.topic_id == topic.id)):
        prerequisite = session.get(Topic, link.prerequisite_topic_id)
        if prerequisite:
            prerequisites.append(prerequisite.name)
    mistakes = session.exec(
        select(Mistake).where(Mistake.topic_id == topic.id).order_by(Mistake.last_seen_at.desc()).limit(3)
    ).all()
    prior = session.exec(
        select(Exercise).where(Exercise.topic_id == topic.id).order_by(Exercise.created_at.desc()).limit(12)
    ).all()
    return (
        f"Curriculum: {curriculum.name}\nTrack: {track.name}\nTopic: {topic.name}\n"
        f"Description: {topic.description}\nTarget level: {topic.target_level}\n"
        f"Prerequisites: {', '.join(prerequisites) or 'none'}\n"
        f"Learner state: mastery={state.mastery_score if state else 0}, "
        f"status={state.status if state else 'not_started'}\n"
        f"Recent mistakes: {', '.join(m.description for m in mistakes) or 'none'}\n"
        f"Previous exercise IDs/types: {', '.join(f'{e.id}:{e.exercise_type}' for e in prior) or 'none'}"
    )


def generate_exercises(
    session: Session, topic: Topic, provider: LLMProvider, needed: int,
    *, purpose: str = "exercise_generation",
) -> list[Exercise]:
    if purpose in {"exercise_generation", "review_generation"} and not nonessential_ai_allowed(session):
        raise ProviderError("Estimated Forge API budget reached. Cached learning material remains available; adjust the optional budget pause in Settings to generate fresh material.")
    track = session.get(Track, topic.track_id)
    prompt = (
        f"{_topic_context(session, topic)}\n\nGenerate exactly {needed} new exercises "
        "for a practical working/interview difficulty. Prefer variety: concept check, "
        "applied scenario, then implementation/debugging where appropriate. "
        "For Python/DSA topics, include coding. For other topics, prioritize reasoning."
    )
    for attempt in range(2):
        try:
            pack, result = provider.generate_structured(
                system_instruction=EXERCISE_POLICY,
                prompt=prompt,
                thinking_level=settings.gemini_exercise_thinking,
                response_model=ExercisePackProposal,
            )
            if len(pack.exercises) < needed:
                raise InvalidStructuredResponse(f"Expected {needed} exercises, got {len(pack.exercises)}")
            created = []
            for proposal in pack.exercises[:needed]:
                exercise = Exercise(
                    curriculum_id=track.curriculum_id,
                    track_id=track.id,
                    topic_id=topic.id,
                    exercise_type=proposal.exercise_type,
                    title=proposal.title,
                    prompt_markdown=proposal.prompt_markdown,
                    difficulty=proposal.difficulty,
                    source="gemini",
                    generator_model=result.model,
                    generator_version="phase3-v1",
                    validation_status="pending" if proposal.exercise_type.startswith("python_") else "valid",
                    content_json=json.dumps({"key": proposal.key, "hints": proposal.hints, "content": proposal.content.model_dump()}),
                )
                session.add(exercise)
                created.append(exercise)
            session.commit()
            record_usage(
                session, provider, result,
                purpose=f"{purpose}_repair" if attempt else purpose,
                thinking_level=settings.gemini_exercise_thinking,
            )
            return created
        except InvalidStructuredResponse as exc:
            if attempt:
                raise ProviderError("Exercise generation returned an invalid structure. Please retry.") from exc
            prompt += f"\n\nRepair the complete pack. Validation errors: {str(exc)[:1200]}"
    raise ProviderError("Exercise generation returned an invalid structure. Please retry.")


def _attempted_success_ids(session: Session, topic_id: int) -> set[int]:
    rows = session.exec(
        select(ExerciseAttemptDetail.exercise_id)
        .join(Attempt, Attempt.id == ExerciseAttemptDetail.attempt_id)
        .where(Attempt.topic_id == topic_id, Attempt.passed == True)  # noqa: E712
    ).all()
    return set(rows)


def start_practice(
    session: Session, topic: Topic, provider: LLMProvider | None
) -> tuple[LearningSession, list[Exercise]]:
    successful = _attempted_success_ids(session, topic.id)
    available = session.exec(
        select(Exercise)
        .where(Exercise.topic_id == topic.id, Exercise.is_active == True)  # noqa: E712
        .order_by(Exercise.created_at.desc(), Exercise.id.desc())
    ).all()
    unused = [exercise for exercise in available if exercise.id not in successful]
    unused.sort(key=lambda exercise: (exercise.source != "course_pack", -exercise.id))
    chosen = unused[:3]
    if len(chosen) < 3 and provider is not None:
        try:
            chosen.extend(generate_exercises(session, topic, provider, 3 - len(chosen)))
        except ProviderError:
            if not chosen:
                raise
    if not chosen:
        raise ProviderError(
            "There is no cached practice or validated static practice for this topic. Gemini fallback is unavailable."
        )
    chosen.sort(key=lambda exercise: exercise.id)
    practice_session = LearningSession(topic_id=topic.id, mode="practice")
    session.add(practice_session)
    session.flush()
    for index, exercise in enumerate(chosen):
        session.add(
            PracticeSessionExercise(
                session_id=practice_session.id, exercise_id=exercise.id, order_index=index
            )
        )
    session.commit()
    session.refresh(practice_session)
    return practice_session, chosen


def session_exercises(session: Session, practice_session: LearningSession) -> list[Exercise]:
    if practice_session.mode != "practice":
        raise PracticeError("Not a practice session")
    links = session.exec(
        select(PracticeSessionExercise)
        .where(PracticeSessionExercise.session_id == practice_session.id)
        .order_by(PracticeSessionExercise.order_index)
    ).all()
    return [exercise for link in links if (exercise := session.get(Exercise, link.exercise_id))]


def ensure_in_session(session: Session, session_id: int, exercise: Exercise, modes: tuple[str, ...] = ("practice",)) -> LearningSession:
    practice_session = session.get(LearningSession, session_id)
    if practice_session is None or practice_session.mode not in modes or practice_session.topic_id != exercise.topic_id:
        raise PracticeError("Exercise is not in this practice session")
    if session.get(PracticeSessionExercise, (session_id, exercise.id)) is None:
        raise PracticeError("Exercise is not in this practice session")
    return practice_session


def reveal_hint(session: Session, exercise: Exercise, session_id: int) -> dict:
    ensure_in_session(session, session_id, exercise)
    hints = _content(exercise)["hints"]
    use = session.get(PracticeHintUse, (session_id, exercise.id))
    if use is None:
        use = PracticeHintUse(session_id=session_id, exercise_id=exercise.id)
    if use.count >= len(hints):
        raise PracticeError("No more hints are available")
    index = use.count
    use.count += 1
    session.add(use)
    session.commit()
    return {"index": index + 1, "text": hints[index], "hints_used_count": use.count}


def _hint_count(session: Session, session_id: int, exercise_id: int) -> int:
    use = session.get(PracticeHintUse, (session_id, exercise_id))
    return use.count if use else 0


def _save_attempt(
    session: Session, exercise: Exercise, session_id: int, *, answer: str,
    score: float | None, passed: bool | None, feedback: str,
    grading_source: str, evaluation_status: str = "complete",
    execution_summary: dict | None = None,
    evidence_type: str = "practice", assisted: bool = False,
    evidence_metadata: dict | None = None,
) -> dict:
    hints = _hint_count(session, session_id, exercise.id)
    attempt = Attempt(
        topic_id=exercise.topic_id,
        attempt_type=exercise.exercise_type,
        score=score if score is not None else 0,
        passed=passed if passed is not None else False,
        used_hint=hints > 0,
    )
    session.add(attempt)
    session.flush()
    detail = ExerciseAttemptDetail(
        attempt_id=attempt.id,
        exercise_id=exercise.id,
        session_id=session_id,
        answer=answer,
        hints_used_count=hints,
        execution_summary_json=json.dumps(execution_summary or {}),
        feedback=feedback,
        grading_source=grading_source,
        evaluation_status=evaluation_status,
    )
    session.add(detail)
    session.commit()
    if evaluation_status == "complete" and evidence_type != "none":
        from .mastery import record_attempt_evidence, recalculate_topic
        record_attempt_evidence(
            session, attempt, detail, exercise, event_type=evidence_type,
            assisted=assisted, metadata=evidence_metadata,
        )
        session.commit()
        recalculate_topic(session, exercise.topic_id)
    return attempt_to_dict(attempt, detail, exercise)


def attempt_to_dict(attempt: Attempt, detail: ExerciseAttemptDetail, exercise: Exercise) -> dict:
    pending = detail.evaluation_status != "complete"
    return {
        "attempt_id": attempt.id,
        "session_id": detail.session_id,
        "exercise_id": exercise.id,
        "exercise_title": exercise.title,
        "exercise_type": exercise.exercise_type,
        "score": None if pending else attempt.score,
        "passed": None if pending else attempt.passed,
        "hints_used_count": detail.hints_used_count,
        "grading_source": detail.grading_source,
        "evaluation_status": detail.evaluation_status,
        "feedback": detail.feedback,
        "created_at": attempt.created_at,
    }


def submit_mcq(session: Session, exercise: Exercise, request: MCQSubmission, *, evidence_type: str = "practice", assisted: bool = False) -> dict:
    ensure_in_session(session, request.session_id, exercise, ("practice", "transfer", "review", "interview"))
    if exercise.exercise_type != "multiple_choice":
        raise PracticeError("Exercise is not multiple choice")
    content = _content(exercise)["content"]
    if not 0 <= request.selected_index < len(content["choices"]):
        raise PracticeError("Selected choice is out of range")
    passed = request.selected_index == content["correct_index"]
    feedback = (
        ("Correct. " if passed else f"Correct answer: {content['choices'][content['correct_index']]}. ")
        + content["explanation"]
    )
    return _save_attempt(
        session, exercise, request.session_id, answer=str(request.selected_index),
        score=100 if passed else 0, passed=passed, feedback=feedback,
        grading_source="deterministic_mcq", evidence_type=evidence_type, assisted=assisted,
    )


def submit_short_answer(
    session: Session, exercise: Exercise, request: ShortAnswerSubmission,
    provider: LLMProvider | None, *, evidence_type: str = "practice", assisted: bool = False,
) -> dict:
    ensure_in_session(session, request.session_id, exercise, ("practice", "transfer", "review"))
    if exercise.exercise_type != "short_answer":
        raise PracticeError("Exercise is not short answer")
    if provider is None:
        return _save_attempt(
            session, exercise, request.session_id, answer=request.answer,
            score=None, passed=None,
            feedback="Answer saved. Evaluation is pending until Gemini is available.",
            grading_source="pending_gemini", evaluation_status="pending",
        )
    content = _content(exercise)["content"]
    prompt = json.dumps({
        "question": exercise.prompt_markdown,
        "learner_answer": request.answer,
        "rubric": content["rubric"],
        "reference_answer": content["reference_answer"],
        "minimum_pass_score": content["minimum_pass_score"],
    })
    try:
        evaluation, result = provider.generate_structured(
            system_instruction=ANSWER_POLICY,
            prompt=prompt,
            thinking_level=settings.gemini_answer_evaluation_thinking,
            response_model=ShortAnswerEvaluation,
        )
    except ProviderError:
        return _save_attempt(
            session, exercise, request.session_id, answer=request.answer,
            score=None, passed=None,
            feedback="Answer saved. Gemini evaluation is temporarily unavailable.",
            grading_source="pending_gemini", evaluation_status="pending",
        )
    record_usage(
        session, provider, result, purpose="short_answer_evaluation",
        thinking_level=settings.gemini_answer_evaluation_thinking,
    )
    return _save_attempt(
        session, exercise, request.session_id, answer=request.answer,
        score=evaluation.score,
        passed=evaluation.score >= content["minimum_pass_score"],
        feedback=evaluation.feedback_markdown,
        grading_source="gemini_rubric",
        evidence_type=evidence_type, assisted=assisted,
        evidence_metadata={"misconception": evaluation.misconception, "concepts_missing": evaluation.concepts_missing},
    )


def submission_tests(exercise: Exercise) -> dict:
    if not exercise.exercise_type.startswith("python_"):
        raise PracticeError("Exercise does not contain Python tests")
    content = _content(exercise)["content"]
    return {
        "function_name": content["function_name"],
        "tests": content["sample_tests"] + content["hidden_tests"],
        "time_limit_ms": content["time_limit_ms"],
    }


def reference_validation_payload(exercise: Exercise) -> dict:
    if exercise.validation_status != "pending":
        raise PracticeError("Reference validation is not pending")
    payload = submission_tests(exercise)
    payload["reference_solution"] = _content(exercise)["content"]["reference_solution"]
    return payload


def mark_reference_validation(session: Session, exercise: Exercise, passed: bool) -> None:
    if exercise.validation_status != "pending":
        raise PracticeError("Reference validation is not pending")
    exercise.validation_status = "valid" if passed else "invalid"
    exercise.is_active = passed
    session.add(exercise)
    session.commit()


def submit_code(session: Session, exercise: Exercise, request: CodeSubmission, *, evidence_type: str = "practice", assisted: bool = False) -> dict:
    ensure_in_session(session, request.session_id, exercise, ("practice", "transfer", "review", "interview"))
    if not exercise.exercise_type.startswith("python_"):
        raise PracticeError("Exercise is not Python code")
    if exercise.validation_status != "valid":
        raise PracticeError("Exercise reference solution has not passed validation")
    expected_tests = submission_tests(exercise)["tests"]
    observed = request.execution.tests
    if len(observed) != len(expected_tests) or [item.name for item in observed] != [item["name"] for item in expected_tests]:
        raise PracticeError("Execution result does not match the submission test set")
    passed_tests = sum(item.passed for item in observed)
    score = round(100 * passed_tests / len(expected_tests), 1)
    passed = request.execution.status == "passed" and passed_tests == len(expected_tests)
    failures = [item.name + (f": {item.message}" if item.message else "") for item in observed if not item.passed]
    feedback = (
        f"{passed_tests}/{len(expected_tests)} tests passed. "
        + ("All tests passed." if not failures else "Failed: " + "; ".join(failures[:5]))
    )
    return _save_attempt(
        session, exercise, request.session_id, answer=request.source,
        score=score, passed=passed, feedback=feedback,
        grading_source="client_pyodide",
        execution_summary=request.execution.model_dump(),
        evidence_type=evidence_type, assisted=assisted,
    )


def practice_history(session: Session, topic_id: int) -> dict:
    attempts = session.exec(
        select(Attempt)
        .where(Attempt.topic_id == topic_id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
    ).all()
    rows = []
    for attempt in attempts:
        detail = session.get(ExerciseAttemptDetail, attempt.id)
        if detail is None:
            continue
        exercise = session.get(Exercise, detail.exercise_id)
        if exercise:
            rows.append(attempt_to_dict(attempt, detail, exercise))
    scored = [row["score"] for row in rows[:10] if row["score"] is not None]
    return {
        "attempts": rows,
        "attempt_count": len(rows),
        "recent_average": round(sum(scored) / len(scored), 1) if scored else None,
        "last_practiced_at": rows[0]["created_at"] if rows else None,
    }
