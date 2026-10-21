"""Portable publication contracts. These are development artifacts, never model approvals."""
from datetime import datetime
from typing import Literal
from pydantic import Field, StrictBool, field_validator, model_validator
from .content_registry import StrictModel
from ..services.content_paths import validate_relative_path

POLICY_VERSION = "forge-content-checks/1"
QUALITY_CHECKS = (
    "objective", "accurate_explanation", "terminology", "worked_example",
    "reasoning_steps", "common_mistakes", "progressive_practice", "worked_answers",
    "progressive_hints", "revision_summary", "provenance", "independent_technical_review",
    "semantic_answers", "coverage", "statement_judge_agreement",
)


class Candidate(StrictModel):
    format_version: Literal[1] = 1
    content_key: str
    revision: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
    content_type: Literal["lesson_bundle", "arena_problem"]
    payload: dict
    provenance: dict
    coverage: dict
    example_checks: list[dict] = []
    problem_contract: dict | None = None
    negative_solutions: list[str] = []
    known_content: list[str] = []
    prerequisite_keys: list[str] = []

    _safe = field_validator("content_key")(validate_relative_path)


class HumanReview(StrictModel):
    candidate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reviewer: str = Field(min_length=3)
    reviewed_at: datetime
    outcome: Literal["approved", "rejected"]
    human_attestation: Literal[True]
    checklist: dict[str, StrictBool]
    notes: str = Field(min_length=20)

    @field_validator("reviewer")
    @classmethod
    def meaningful_identity(cls, value):
        value = value.strip()
        if len(value) < 3:
            raise ValueError("A meaningful reviewer identity is required")
        return value

    @model_validator(mode="after")
    def complete(self):
        if self.reviewed_at.tzinfo is None:
            raise ValueError("Review timestamp must include a timezone")
        if self.outcome == "approved" and any(self.checklist.get(key) is not True for key in QUALITY_CHECKS):
            raise ValueError("Every technical, semantic, coverage and teaching review item is required")
        return self


class ReleaseTarget(StrictModel):
    curriculum_name: str
    curriculum_version: int
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    topic: str
    order_index: int = Field(default=0, ge=0)
    _safe = field_validator("topic")(validate_relative_path)


class ReleasePackage(StrictModel):
    format_version: Literal[1] = 1
    release_id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{0,99}$")
    entries: list[dict] = Field(min_length=1)
