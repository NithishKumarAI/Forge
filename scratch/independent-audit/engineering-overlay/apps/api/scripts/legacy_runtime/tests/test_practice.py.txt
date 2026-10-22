from copy import deepcopy
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import Session, select

from app.models import Attempt, Exercise, LearnerTopicState, ModelUsageEvent, Topic
from app.database import get_session
from app.main import create_app
from app.providers import LLMProvider, LLMResult, LLMUsage, ProviderError
from app.providers.dependencies import get_llm_provider
from app.providers.gemini import GeminiProvider
from app.schemas.practice import (
    CodeSubmission, ExercisePackProposal, ExerciseProposal, ExecutionResult,
    ExecutionTestResult, MCQSubmission, ShortAnswerSubmission,
)
from app.services.practice import (
    PracticeError, generate_exercises, mark_reference_validation, practice_history, public_exercise,
    reveal_hint, start_practice, submit_code, submit_mcq, submit_short_answer,
)


def exercise_pack(count: int = 3) -> ExercisePackProposal:
    examples = [
        {
            "key": "concept-check", "exercise_type": "multiple_choice",
            "title": "Choose the correct idea", "prompt_markdown": "Which option explains this Python concept?",
            "difficulty": "intro", "hints": ["Think about the function call."],
            "content": {"choices": ["Correct concept", "Wrong concept"], "correct_index": 0, "explanation": "The first choice is correct."},
        },
        {
            "key": "scenario", "exercise_type": "short_answer",
            "title": "Explain a scenario", "prompt_markdown": "Explain when you would use this Python concept.",
            "difficulty": "working", "hints": ["Describe an actual use case."],
            "content": {"rubric": [{"concept": "correct use case", "weight": 1.0}], "reference_answer": "Use it in this case.", "minimum_pass_score": 70},
        },
        {
            "key": "implementation", "exercise_type": "python_code",
            "title": "Implement add", "prompt_markdown": "Implement add(a, b) for two integers.",
            "difficulty": "working", "hints": ["Return a value.", "Use the addition operator."],
            "content": {
                "starter_code": "def add(a, b):\n    pass", "function_name": "add",
                "sample_tests": [{"name": "positives", "args": [2, 3], "expected": 5}],
                "hidden_tests": [{"name": "negative", "args": [-1, 1], "expected": 0}],
                "reference_solution": "def add(a, b):\n    return a + b", "time_limit_ms": 5000,
            },
        },
    ]
    return ExercisePackProposal.model_validate({"exercises": examples[:count]})


class FakePracticeProvider(LLMProvider):
    provider_name = "fake"
    model = "fake-practice"

    def __init__(self, fail: bool = False) -> None:
        self.calls = 0
        self.fail = fail

    def generate_text(self, *, system_instruction: str, prompt: str, thinking_level: str) -> LLMResult:
        raise AssertionError("Practice should not call plain text generation")

    def generate_structured(self, *, system_instruction: str, prompt: str, thinking_level: str, response_model: type):
        self.calls += 1
        if self.fail:
            raise ProviderError("Gemini rate limit reached. Existing cached practice remains available. Try generation again later.")
        value = exercise_pack(3) if response_model is ExercisePackProposal else response_model(
            score=85, passed=True, concepts_present=["correct use case"], concepts_missing=[],
            misconception=None, feedback_markdown="Good explanation.",
        )
        return value, LLMResult(text=value.model_dump_json(), model=self.model, usage=LLMUsage(input_tokens=100, output_tokens=40, thought_tokens=5, cached_tokens=0))


def first_topic(session: Session) -> Topic:
    return session.exec(select(Topic).order_by(Topic.id)).first()


def test_start_generates_pack_and_reuses_cache(session: Session) -> None:
    provider = FakePracticeProvider()
    topic = first_topic(session)
    first, exercises = start_practice(session, topic, provider)
    assert first.mode == "practice"
    assert len(exercises) == 3
    assert provider.calls == 1
    second, reused = start_practice(session, topic, provider)
    assert second.id != first.id
    assert [item.id for item in reused] == [item.id for item in exercises]
    assert provider.calls == 1
    assert session.exec(select(Attempt)).all() == []  # Opening and Run create no evidence.
    event = session.exec(select(ModelUsageEvent)).one()
    assert event.purpose == "exercise_generation"


def test_malformed_exercises_rejected() -> None:
    payload = exercise_pack().model_dump()
    payload["exercises"][0]["content"]["correct_index"] = 99
    with pytest.raises(ValidationError, match="correct_index"):
        ExercisePackProposal.model_validate(payload)
    payload = exercise_pack().model_dump()
    payload["exercises"][2]["content"]["hidden_tests"] = []
    with pytest.raises(ValidationError, match="sample and submission tests"):
        ExercisePackProposal.model_validate(payload)


def test_mcq_grading_hint_history_and_mastery(session: Session) -> None:
    topic = first_topic(session)
    before = session.get(LearnerTopicState, topic.id).model_dump()
    practice_session, exercises = start_practice(session, topic, FakePracticeProvider())
    mcq = exercises[0]
    hint = reveal_hint(session, mcq, practice_session.id)
    assert hint["hints_used_count"] == 1
    attempt = submit_mcq(session, mcq, MCQSubmission(session_id=practice_session.id, selected_index=0))
    assert attempt["score"] == 100
    assert attempt["passed"] is True
    assert attempt["hints_used_count"] == 1
    assert practice_history(session, topic.id)["attempt_count"] == 1
    after = session.get(LearnerTopicState, topic.id)
    assert after.mastery_score > before["mastery_score"]
    assert after.mastery_score < 80


def test_short_answer_uses_fake_provider_and_records_usage(session: Session) -> None:
    topic = first_topic(session)
    provider = FakePracticeProvider()
    practice_session, exercises = start_practice(session, topic, provider)
    answer = submit_short_answer(session, exercises[1], ShortAnswerSubmission(session_id=practice_session.id, answer="A correct use case."), provider)
    assert answer["score"] == 85
    assert answer["grading_source"] == "gemini_rubric"
    assert [item.purpose for item in session.exec(select(ModelUsageEvent)).all()] == ["exercise_generation", "short_answer_evaluation"]


def test_short_answer_pending_without_provider(session: Session) -> None:
    topic = first_topic(session)
    practice_session, exercises = start_practice(session, topic, FakePracticeProvider())
    answer = submit_short_answer(session, exercises[1], ShortAnswerSubmission(session_id=practice_session.id, answer="An answer."), None)
    assert answer["evaluation_status"] == "pending"
    assert answer["score"] is None


def test_code_solution_protected_and_submit_saved(session: Session) -> None:
    topic = first_topic(session)
    practice_session, exercises = start_practice(session, topic, FakePracticeProvider())
    coding = exercises[2]
    public = public_exercise(coding)
    assert "reference_solution" not in str(public)
    assert "hidden_tests" not in str(public)
    coding.validation_status = "valid"
    session.add(coding)
    session.commit()
    result = submit_code(session, coding, CodeSubmission(
        session_id=practice_session.id,
        source="def add(a, b):\n    return a + b",
        execution=ExecutionResult(status="passed", stdout="", stderr="", duration_ms=50, tests=[
            ExecutionTestResult(name="positives", passed=True),
            ExecutionTestResult(name="negative", passed=True),
        ]),
    ))
    assert result["score"] == 100
    assert result["grading_source"] == "client_pyodide"
    assert practice_history(session, topic.id)["attempt_count"] == 1


def test_cached_practice_works_without_provider_and_failure_clean(session: Session) -> None:
    topic = first_topic(session)
    with pytest.raises(ProviderError, match="no cached practice"):
        start_practice(session, topic, None)
    start_practice(session, topic, FakePracticeProvider())
    _, cached = start_practice(session, topic, None)
    assert len(cached) == 3
    other = session.exec(select(Topic).where(Topic.id != topic.id)).first()
    with pytest.raises(ProviderError, match="rate limit"):
        start_practice(session, other, FakePracticeProvider(fail=True))


def test_partial_cache_survives_provider_rate_limit(session: Session) -> None:
    topic = first_topic(session)
    _, exercises = start_practice(session, topic, FakePracticeProvider())
    exercises[2].is_active = False
    session.add(exercises[2])
    session.commit()
    _, cached = start_practice(session, topic, FakePracticeProvider(fail=True))
    assert len(cached) == 2


def test_practice_routes_protect_answers_and_run_is_unscored(session: Session) -> None:
    topic = first_topic(session)
    practice_session, exercises = start_practice(session, topic, FakePracticeProvider())
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_llm_provider] = lambda: None
    client = TestClient(app)
    mcq = client.get(f"/api/practice/exercises/{exercises[0].id}")
    assert mcq.status_code == 200
    assert "correct_index" not in mcq.text
    short = client.get(f"/api/practice/exercises/{exercises[1].id}")
    assert "reference_answer" not in short.text
    coding = client.get(f"/api/practice/exercises/{exercises[2].id}")
    assert "reference_solution" not in coding.text
    assert "hidden_tests" not in coding.text
    assert client.get(f"/api/practice/sessions/{practice_session.id}").status_code == 200
    assert client.get(f"/api/practice/exercises/{exercises[2].id}/submission-tests").status_code == 200
    assert session.exec(select(Attempt)).all() == []  # Browser Run and reading tests are unscored.


def test_failed_reference_is_retired(session: Session) -> None:
    topic = first_topic(session)
    _, exercises = start_practice(session, topic, FakePracticeProvider())
    coding = exercises[2]
    mark_reference_validation(session, coding, False)
    assert coding.validation_status == "invalid"
    assert coding.is_active is False
    _, cached = start_practice(session, topic, None)
    assert coding.id not in [item.id for item in cached]


def test_gemini_rate_limit_is_clear_and_not_retried() -> None:
    class RateLimit(Exception):
        status_code = 429

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        raise RateLimit()

    provider = GeminiProvider.__new__(GeminiProvider)
    provider._client = SimpleNamespace(interactions=SimpleNamespace(create=create))
    with pytest.raises(ProviderError, match="rate limit reached"):
        provider._create(model="fake")
    assert len(calls) == 1
