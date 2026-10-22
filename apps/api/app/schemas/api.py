from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TopicStateRead(ApiModel):
    mastery_score: int
    confidence: str
    status: str
    attempts: int
    last_studied_at: datetime | None
    last_tested_at: datetime | None
    next_review_at: datetime | None


class PrerequisiteRead(ApiModel):
    id: int
    name: str
    slug: str
    mastery_score: int
    status: str


class TopicRead(ApiModel):
    id: int
    track_id: int
    track_name: str
    name: str
    slug: str
    description: str
    order_index: int
    priority: int
    target_level: str
    estimated_minutes: int
    state: TopicStateRead
    prerequisites: list[PrerequisiteRead] = Field(default_factory=list)
    reason: str | None = None


class TrackSummary(ApiModel):
    id: int
    curriculum_id: int
    name: str
    slug: str
    description: str
    order_index: int
    priority: int
    mastery: int
    topic_count: int


class TrackRead(TrackSummary):
    topics: list[TopicRead]


class CurriculumSummary(ApiModel):
    id: int
    name: str
    description: str
    source_type: str
    status: str
    version: int
    created_at: datetime
    confirmed_at: datetime | None
    track_count: int


class CurriculumRead(CurriculumSummary):
    tracks: list[TrackRead]


class TopicStateUpdate(BaseModel):
    mastery_score: int | None = Field(default=None, ge=0, le=100)
    confidence: str | None = None
    status: str | None = None
    attempts: int | None = Field(default=None, ge=0)


class DashboardRead(BaseModel):
    content_status: dict = Field(default_factory=dict)
    reading_progress: dict = Field(default_factory=dict)
    recent_mistakes: list[dict] = Field(default_factory=list)
    interview_readiness: int
    active_curriculum: dict[str, int | str] | None = None
    tracks: list[TrackSummary]
    recommendations: list[TopicRead]
    readiness: dict = Field(default_factory=dict)
    reviews_due: int = 0
    today_plan: dict = Field(default_factory=dict)


class HealthRead(BaseModel):
    status: str
