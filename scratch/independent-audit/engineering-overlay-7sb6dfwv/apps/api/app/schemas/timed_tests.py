from typing import Literal
from pydantic import Field
from .content_registry import StrictModel
from .assessment import AssessmentSubmission


class TimedStart(StrictModel):
    kind: Literal['subject','level','mixed','coding']
    subject: str | None = None
    level: int | None = Field(default=None,ge=1,le=3,strict=True)


class TimedAnswer(AssessmentSubmission):
    position: int = Field(ge=0,strict=True)
