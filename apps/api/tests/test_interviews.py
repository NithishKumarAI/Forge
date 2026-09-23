import json
from datetime import datetime, timezone

import pytest
from pydantic import BaseModel
from sqlmodel import Session, select

from app.models import (
    Exercise, InterviewQuestion, InterviewResponse, InterviewSession, LearnerTopicState,
    MasteryEvidenceEvent,
)
from app.providers import LLMProvider, LLMResult, LLMUsage
from app.schemas.interview import InterviewEvaluation, InterviewQuestionProposal, InterviewReportNarrative
from app.schemas.practice import ExecutionResult, ExecutionTestResult, ExerciseContent, ExerciseProposal, PythonTest
from app.services.interview import (
    BLUEPRINTS, abandon_interview, active_interview, answer_current,
    assert_assessment_available, complete_interview, current_question, history,
    interview_read, modes, resume_interview, save_interview, start_interview,
    submit_current_code,
)
from app.services.usage import budget_summary, update_budget_settings


class FakeInterviewProvider(LLMProvider):
    provider_name = "fake"
    model = "fake-interview"

    def __init__(self, follow_up: bool = False) -> None:
        self.follow_up = follow_up
        self.calls: list[str] = []

    def _result(self, value: BaseModel) -> LLMResult:
        return LLMResult(text=value.model_dump_json(), model=self.model, usage=LLMUsage(input_tokens=20, output_tokens=10))

    def generate_text(self, *, system_instruction: str, prompt: str, thinking_level: str) -> LLMResult:
        raise AssertionError("Interview paths use structured output")

    def generate_structured(self, *, system_instruction: str, prompt: str, thinking_level: str, response_model: type[BaseModel]):
        self.calls.append(response_model.__name__)
        if response_model is InterviewQuestionProposal:
            context = json.loads(prompt[prompt.index("{"):])
            kind = context["allowed_question_types"][0]
            project = context.get("project_profile")
            question = f"Walk me through {project['name']} and one architectural trade-off." if project else f"Explain a practical decision involving {context['fixed_competency']}."
            coding = None
            if kind in {"python_code", "python_debug"}:
                content = ExerciseContent(
                    starter_code="def add(a, b):\n    pass" if kind == "python_code" else None,
                    broken_code="def add(a, b):\n    return a - b" if kind == "python_debug" else None,
                    function_name="add",
                    sample_tests=[PythonTest(name="positive", args=[2, 3], expected=5)],
                    hidden_tests=[PythonTest(name="negative", args=[-1, 1], expected=0)],
                    reference_solution="def add(a, b):\n    return a + b",
                )
                coding = ExerciseProposal(key=f"interview-{len(self.calls)}", exercise_type=kind, title="Implement addition", prompt_markdown="Implement add(a, b) and return the numeric sum.", difficulty="interview", hints=[], content=content)
            value = InterviewQuestionProposal(
                question=question, question_type=kind, competency=context["fixed_competency"],
                difficulty=context["difficulty"], rubric=context["fixed_rubric"][kind],
                expected_concepts=[context["fixed_competency"]], follow_up_allowed=True,
                coding_exercise=coding,
            )
        elif response_model is InterviewEvaluation:
            payload = json.loads(prompt)
            dimensions = {item["name"]: 80 for item in payload["rubric"]}
            value = InterviewEvaluation(
                dimension_scores=dimensions, strengths=["Clear core reasoning"],
                missing_concepts=["Timeout boundaries"], misconceptions=[],
                feedback="The response covered the core idea.", follow_up_needed=self.follow_up,
                follow_up_reason="Clarify operational safeguards" if self.follow_up else None,
                recommended_follow_up="What explicit timeout and retry boundary would you add?" if self.follow_up else None,
            )
        elif response_model is InterviewReportNarrative:
            value = InterviewReportNarrative(summary="A consistent Forge-rubric performance with concrete areas for further practice.", communication_feedback=["State trade-offs explicitly."])
        else:
            raise AssertionError(response_model)
        return value, self._result(value)


def _finish_current(session: Session, interview: InterviewSession, provider: FakeInterviewProvider) -> None:
    question = current_question(session, interview)
    if question.question_type in {"python_code", "python_debug"}:
        exercise = session.get(Exercise, question.exercise_id)
        exercise.validation_status = "valid"; session.add(exercise); session.commit()
        execution = ExecutionResult(status="passed", stdout="", stderr="", duration_ms=2, tests=[
            ExecutionTestResult(name="positive", passed=True),
            ExecutionTestResult(name="negative", passed=True),
        ])
        submit_current_code(session, interview, "def add(a, b):\n    return a + b", execution, 20, provider)
    else:
        answer_current(session, interview, "I would explain the constraints, trade-offs, failure boundary, and verify the result.", 30, provider)


def test_interview_modes_and_blueprints_are_fixed() -> None:
    available = {item["mode"] for item in modes()}
    assert available == {"quick", "full_ai_engineer", "python_backend", "llm_rag", "project_deep_dive", "system_design", "behavioral"}
    assert len(BLUEPRINTS["quick"]["slots"]) == 5
    assert {slot["section"] for slot in BLUEPRINTS["full_ai_engineer"]["slots"]} >= {"python_backend", "llm_rag", "coding", "project", "system_design", "behavioral"}
    assert sum(slot["weight"] for slot in BLUEPRINTS["full_ai_engineer"]["slots"]) == pytest.approx(1)


def test_quick_start_respects_fixed_competency_and_rubric(session: Session) -> None:
    provider = FakeInterviewProvider()
    interview = start_interview(session, "quick", provider)
    question = current_question(session, interview)
    assert question.competency == BLUEPRINTS["quick"]["slots"][0]["competency"]
    assert question.question_type in BLUEPRINTS["quick"]["slots"][0]["allowed"]
    stored = json.loads(question.rubric_json)
    assert [item["name"] for item in stored] == ["correctness", "completeness", "reasoning", "practicality", "clarity"]
    assert interview_read(session, interview)["current_question"]["prompt_markdown"]


def test_only_one_contextual_follow_up_is_possible(session: Session) -> None:
    provider = FakeInterviewProvider(follow_up=True)
    interview = start_interview(session, "quick", provider)
    answer_current(session, interview, "Async alone is not a deadline; add timeouts and bounded retries.", 20, provider)
    follow_up = current_question(session, interview)
    assert follow_up.follow_up_of_id is not None
    answer_current(session, interview, "Use an explicit client timeout and retry only idempotent calls with backoff.", 15, provider)
    rows = session.exec(select(InterviewQuestion).where(InterviewQuestion.session_id == interview.id, InterviewQuestion.follow_up_of_id != None)).all()  # noqa: E711
    assert len(rows) == 1
    assert current_question(session, interview).follow_up_of_id is None


def test_project_question_is_grounded_in_seeded_profile(session: Session) -> None:
    interview = start_interview(session, "project_deep_dive", FakeInterviewProvider())
    question = current_question(session, interview)
    assert "Robin" in question.prompt_markdown
    assert question.question_type == "project"


def test_behavioral_response_does_not_change_technical_mastery(session: Session) -> None:
    before = {row.topic_id: row.model_dump() for row in session.exec(select(LearnerTopicState)).all()}
    interview = start_interview(session, "behavioral", FakeInterviewProvider())
    answer_current(session, interview, "I described the situation, task, action, result, and what I learned.", 45, FakeInterviewProvider())
    after = {row.topic_id: row.model_dump() for row in session.exec(select(LearnerTopicState)).all()}
    assert before == after
    assert session.exec(select(MasteryEvidenceEvent)).all() == []


def test_coding_reuses_grader_has_no_hints_and_does_not_rewrite_mastery(session: Session) -> None:
    provider = FakeInterviewProvider(); interview = start_interview(session, "quick", provider)
    _finish_current(session, interview, provider); _finish_current(session, interview, provider)
    question = current_question(session, interview)
    assert question.question_type.startswith("python_")
    public = interview_read(session, interview)["current_question"]["exercise"]
    assert public["hints_available"] == 0
    topic_state = session.get(LearnerTopicState, question.topic_id).model_dump()
    _finish_current(session, interview, provider)
    assert session.get(LearnerTopicState, question.topic_id).model_dump() == topic_state
    response = session.exec(select(InterviewResponse).where(InterviewResponse.question_id == question.id)).one()
    assert response.score == 100 and response.attempt_id is not None


def test_complete_report_uses_blueprint_weights_and_links_topics(session: Session) -> None:
    provider = FakeInterviewProvider(); interview = start_interview(session, "quick", provider)
    while current_question(session, interview):
        _finish_current(session, interview, provider)
    report = complete_interview(session, interview, provider)
    assert report["label"] == "Forge Interview Score"
    assert report["overall_score"] == 85  # four 80-point free-form sections plus 100-point coding at 25%.
    assert "not a hiring probability" in report["disclaimer"]
    assert interview.status == "completed"
    assert history(session)[0]["overall_score"] == 85


def test_save_resume_and_abandon_are_consistent(session: Session) -> None:
    interview = start_interview(session, "quick", FakeInterviewProvider())
    save_interview(session, interview); assert interview.status == "saved" and active_interview(session) is None
    resume_interview(session, interview); assert active_interview(session).id == interview.id
    abandon_interview(session, interview); assert interview.status == "abandoned" and active_interview(session) is None
    with pytest.raises(ValueError): resume_interview(session, interview)


def test_tutoring_guard_blocks_only_active_interviews(session: Session) -> None:
    interview = start_interview(session, "quick", FakeInterviewProvider())
    with pytest.raises(ValueError, match="unavailable"):
        assert_assessment_available(session)
    save_interview(session, interview)
    assert_assessment_available(session)


@pytest.mark.parametrize("cost,level", [(7.49, "normal"), (7.5, "approaching"), (9.0, "almost"), (10.0, "reached")])
def test_budget_warning_thresholds_are_estimates(session: Session, cost: float, level: str) -> None:
    update_budget_settings(session, monthly_gemini_budget=10, pause_nonessential_ai=False)
    summary = budget_summary(session, cost)
    assert summary["level"] == level
    assert "not Google billing" in summary["disclaimer"]
