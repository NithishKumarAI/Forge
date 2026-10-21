from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class ProblemExample(BaseModel):
    input: str
    output: str
    explanation: str = ""

class CodingProblem(BaseModel):
    model_config = ConfigDict(extra="allow")
    key: str = Field(pattern=r"^[a-z0-9-]+$")
    title: str
    track: Literal["python","sql","dsa"]
    topic_tags: list[str] = Field(min_length=1)
    difficulty: Literal["easy","medium"]
    interview_frequency: Literal["low","medium","high"]
    estimated_minutes: int = Field(ge=5,le=60)
    statement_markdown: str
    constraints: list[str]
    examples: list[ProblemExample]
    starter_code: str | None = None
    starter_query: str | None = None
    hints: list[str]
    explanation: str
    reference_solution: str
    complexity: str
    validation: dict
    source_type: Literal["original", "adapted"] = "original"
    source_project: str | None = None
    source_exercise: str | None = None
    license: str | None = None
    adapted: bool = False
    publication_contract: dict | None = None
    negative_solutions: list[str] = []
    version: str
    mapped_topic: str

    @model_validator(mode="after")
    def track_payload(self):
        if self.track=="sql" and not self.starter_query: self.starter_query="SELECT "
        if self.track!="sql" and not self.starter_code: raise ValueError("Python problems need starter_code")
        if self.track in {"python","dsa"}:
            self.validation.setdefault("judge_mode","function")
            mode=self.validation["judge_mode"]
            if mode not in {"function","stdin_stdout"}: raise ValueError("judge_mode must be function or stdin_stdout")
            if mode=="function" and not self.validation.get("function_name"): raise ValueError("Function judge requires function_name")
            for test in self.validation.get("sample_tests",[])+self.validation.get("hidden_tests",[]):
                if not test.get("name"): raise ValueError("Every Python test needs a name")
                if mode=="function" and "expected" not in test and "expected_typed" not in test and not test.get("expected_exception"): raise ValueError("Function tests need expected, expected_typed, or expected_exception")
                if mode=="stdin_stdout" and ("stdin" not in test or "expected_stdout" not in test): raise ValueError("stdin_stdout tests need stdin and expected_stdout")
        return self

class ArenaAttemptRequest(BaseModel):
    content_revision_id: int | None = None
    source: str = Field(min_length=1,max_length=30000)
    passed: bool
    score: float = Field(ge=0,le=100)
    runtime_ms: int | None = Field(default=None,ge=0)
    result: dict = {}
