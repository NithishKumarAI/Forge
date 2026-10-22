from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, PrivateAttr, model_validator


class SourceReference(BaseModel):
    source_id: str
    title: str
    url: HttpUrl
    retrieved_at: datetime


class CodeExample(BaseModel):
    language: str
    code: str
    expected_output: str | None = None
    explanation: str


class LessonSection(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str
    order_index: int = Field(ge=0)
    estimated_minutes: int = Field(ge=1, le=60)
    learning_objective: str
    markdown: str = Field(min_length=20)
    examples: list[CodeExample] = []
    key_points: list[str] = Field(min_length=1)
    checkpoint: str | None = None


class StaticLesson(BaseModel):
    _registry_id: int | None = PrivateAttr(default=None)
    curriculum_key: str
    track_slug: str
    topic_slug: str
    title: str
    description: str
    version: str
    learning_objectives: list[str] = Field(min_length=1)
    prerequisites: list[str] = []
    sections: list[LessonSection] = Field(min_length=2, max_length=30)
    summary: list[str] = Field(min_length=1)
    interview_takeaways: list[str] = Field(min_length=1)
    common_mistakes: list[str] = Field(min_length=1)
    sources: list[SourceReference] = Field(min_length=1)
    content_hash: str
    generated_at: datetime

    @model_validator(mode="after")
    def sections_are_deterministic(self):
        slugs = [s.slug for s in self.sections]
        if len(slugs) != len(set(slugs)):
            raise ValueError("section slugs must be unique")
        if [s.order_index for s in self.sections] != list(range(len(self.sections))):
            raise ValueError("section order must be contiguous from zero")
        return self


class SectionContextRequest(BaseModel):
    section_slug: str | None = None

