from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ExerciseType = Literal["multiple_choice", "short_answer", "python_code", "python_debug"]


class PythonTest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    args: list[Any] = Field(default_factory=list, max_length=10)
    kwargs: dict[str, Any] = Field(default_factory=dict)
    expected: Any = None
    expected_exception: str | None = None

    @model_validator(mode="after")
    def expected_result(self) -> "PythonTest":
        if self.expected_exception and self.expected is not None:
            raise ValueError("use expected or expected_exception, not both")
        return self


class RubricItem(BaseModel):
    concept: str = Field(min_length=1, max_length=300)
    weight: float = Field(gt=0, le=1)


class ExerciseContent(BaseModel):
    choices: list[str] | None = None
    correct_index: int | None = None
    explanation: str | None = None
    rubric: list[RubricItem] | None = None
    reference_answer: str | None = None
    minimum_pass_score: int = Field(default=70, ge=1, le=100)
    starter_code: str | None = None
    broken_code: str | None = None
    task: str | None = None
    function_name: str | None = None
    sample_tests: list[PythonTest] | None = None
    hidden_tests: list[PythonTest] | None = None
    reference_solution: str | None = None
    time_limit_ms: int = Field(default=5000, ge=500, le=10000)


class ExerciseProposal(BaseModel):
    key: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    exercise_type: ExerciseType
    title: str = Field(min_length=3, max_length=160)
    prompt_markdown: str = Field(min_length=10, max_length=5000)
    difficulty: Literal["intro", "working", "interview"]
    hints: list[str] = Field(default_factory=list, max_length=3)
    content: ExerciseContent

    @model_validator(mode="after")
    def validate_type(self) -> "ExerciseProposal":
        content = self.content
        if any(not hint.strip() for hint in self.hints):
            raise ValueError("hints cannot be blank")
        if self.exercise_type == "multiple_choice":
            if not content.choices or not 2 <= len(content.choices) <= 6:
                raise ValueError("multiple choice requires 2-6 choices")
            if any(not choice.strip() for choice in content.choices):
                raise ValueError("choices cannot be blank")
            if content.correct_index is None or not 0 <= content.correct_index < len(content.choices):
                raise ValueError("correct_index must identify one choice")
            if not content.explanation or not content.explanation.strip():
                raise ValueError("multiple choice explanation is required")
        elif self.exercise_type == "short_answer":
            if not content.rubric or not content.reference_answer or not content.reference_answer.strip():
                raise ValueError("short answer requires rubric and reference answer")
            if abs(sum(item.weight for item in content.rubric) - 1) > 0.01:
                raise ValueError("rubric weights must total 1")
        else:
            initial = content.starter_code if self.exercise_type == "python_code" else content.broken_code
            if not initial or not initial.strip() or len(initial) > 12000:
                raise ValueError("coding exercise requires reasonable starter or broken code")
            if not content.function_name or not content.function_name.isidentifier():
                raise ValueError("coding exercise requires a valid function_name")
            if not content.sample_tests or not content.hidden_tests:
                raise ValueError("coding exercise requires sample and submission tests")
            if not content.reference_solution or not content.reference_solution.strip():
                raise ValueError("coding exercise requires a reference solution")
            if len(content.reference_solution) > 12000:
                raise ValueError("reference solution is too large")
            forbidden = ("import os", "import subprocess", "import socket", "pip install", "micropip")
            if any(term in (initial + content.reference_solution).lower() for term in forbidden):
                raise ValueError("coding exercise requires unsupported or unsafe facilities")
        return self


class ExercisePackProposal(BaseModel):
    exercises: list[ExerciseProposal] = Field(min_length=1, max_length=5)

    @model_validator(mode="after")
    def unique_keys(self) -> "ExercisePackProposal":
        keys = [exercise.key for exercise in self.exercises]
        if len(keys) != len(set(keys)):
            raise ValueError("exercise keys must be unique")
        return self


class PublicExercise(BaseModel):
    id: int
    topic_id: int
    exercise_type: ExerciseType
    title: str
    prompt_markdown: str
    difficulty: str
    hints_available: int
    validation_status: str
    content: dict[str, Any]


class PracticeStartResponse(BaseModel):
    session_id: int
    exercises: list[PublicExercise]


class PracticeSessionRead(BaseModel):
    session_id: int
    topic_id: int
    exercises: list[PublicExercise]


class HintRead(BaseModel):
    index: int
    text: str
    hints_used_count: int


class MCQSubmission(BaseModel):
    session_id: int
    selected_index: int


class ShortAnswerSubmission(BaseModel):
    session_id: int
    answer: str = Field(min_length=1, max_length=8000)


class ExecutionTestResult(BaseModel):
    name: str
    passed: bool
    message: str = ""


class ExecutionResult(BaseModel):
    status: Literal["passed", "failed", "runtime_error", "timeout"]
    stdout: str = Field(default="", max_length=30000)
    stderr: str = Field(default="", max_length=30000)
    tests: list[ExecutionTestResult] = Field(default_factory=list, max_length=100)
    duration_ms: int = Field(ge=0)


class CodeSubmission(BaseModel):
    session_id: int
    source: str = Field(min_length=1, max_length=20000)
    execution: ExecutionResult


class AttemptRead(BaseModel):
    attempt_id: int
    session_id: int
    exercise_id: int
    exercise_title: str
    exercise_type: str
    score: float | None
    passed: bool | None
    hints_used_count: int
    grading_source: str
    evaluation_status: str
    feedback: str
    created_at: datetime


class PracticeHistory(BaseModel):
    attempts: list[AttemptRead]
    attempt_count: int
    recent_average: float | None
    last_practiced_at: datetime | None


class ShortAnswerEvaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    passed: bool
    concepts_present: list[str] = Field(default_factory=list)
    concepts_missing: list[str] = Field(default_factory=list)
    misconception: str | None = None
    feedback_markdown: str = Field(min_length=1, max_length=3000)
