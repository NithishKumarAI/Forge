from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .practice import ExerciseProposal, ExecutionResult


QuestionType = Literal[
    "technical_short_answer", "scenario", "project", "behavioral",
    "system_design", "python_code", "python_debug",
]


class RubricDimension(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    weight: float = Field(gt=0, le=1)
    criteria: str = Field(min_length=5, max_length=500)


class InterviewQuestionProposal(BaseModel):
    question: str = Field(min_length=10, max_length=5000)
    question_type: QuestionType
    competency: str = Field(min_length=2, max_length=160)
    difficulty: Literal["easy", "medium", "medium_deep"]
    rubric: list[RubricDimension] = Field(min_length=1, max_length=8)
    expected_concepts: list[str] = Field(min_length=1, max_length=20)
    follow_up_allowed: bool = True
    coding_exercise: ExerciseProposal | None = None

    @model_validator(mode="after")
    def validate_question(self) -> "InterviewQuestionProposal":
        if abs(sum(item.weight for item in self.rubric) - 1) > 0.01:
            raise ValueError("rubric weights must total 1")
        coding = self.question_type in {"python_code", "python_debug"}
        if coding != (self.coding_exercise is not None):
            raise ValueError("coding question types require exactly one coding_exercise")
        if self.coding_exercise:
            if self.coding_exercise.exercise_type != self.question_type:
                raise ValueError("coding exercise type must match question type")
            if self.coding_exercise.hints:
                raise ValueError("interview coding exercises cannot contain hints")
        return self


class InterviewEvaluation(BaseModel):
    dimension_scores: dict[str, int] = Field(min_length=1, max_length=10)
    strengths: list[str] = Field(default_factory=list, max_length=8)
    missing_concepts: list[str] = Field(default_factory=list, max_length=10)
    misconceptions: list[str] = Field(default_factory=list, max_length=8)
    feedback: str = Field(min_length=1, max_length=3000)
    follow_up_needed: bool = False
    follow_up_reason: str | None = Field(default=None, max_length=500)
    recommended_follow_up: str | None = Field(default=None, max_length=1500)

    @field_validator("dimension_scores")
    @classmethod
    def valid_scores(cls, values: dict[str, int]) -> dict[str, int]:
        if any(not 0 <= score <= 100 for score in values.values()):
            raise ValueError("dimension scores must be between 0 and 100")
        return values

    @model_validator(mode="after")
    def valid_follow_up(self) -> "InterviewEvaluation":
        if self.follow_up_needed and not self.recommended_follow_up:
            raise ValueError("a requested follow-up must include the question")
        return self


class InterviewReportNarrative(BaseModel):
    summary: str = Field(min_length=10, max_length=3000)
    communication_feedback: list[str] = Field(default_factory=list, max_length=8)

    @field_validator("summary")
    @classmethod
    def no_employment_prediction(cls, value: str) -> str:
        lowered = value.lower()
        if "hiring probability" in lowered or "chance of getting hired" in lowered:
            raise ValueError("report cannot predict employment outcomes")
        return value


class InterviewStartRequest(BaseModel):
    mode: str = Field(min_length=2, max_length=60)


class InterviewAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=20_000)
    duration_seconds: int | None = Field(default=None, ge=0, le=86_400)


class InterviewCodingRequest(BaseModel):
    source: str = Field(min_length=1, max_length=20_000)
    execution: ExecutionResult
    duration_seconds: int | None = Field(default=None, ge=0, le=86_400)


class BudgetSettingsUpdate(BaseModel):
    monthly_gemini_budget: float | None = Field(default=None, ge=0.01, le=10_000)
    pause_nonessential_ai: bool | None = None
