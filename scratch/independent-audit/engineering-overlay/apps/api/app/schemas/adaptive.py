from datetime import datetime
from typing import Any

from pydantic import BaseModel

from .practice import ExecutionResult, PublicExercise


class AdaptiveSubmission(BaseModel):
    selected_index: int | None = None
    answer: str | None = None
    source: str | None = None
    execution: ExecutionResult | None = None
    assisted: bool = False


class TransferSessionRead(BaseModel):
    session_id: int
    topic_id: int
    exercise: PublicExercise


class ReviewQueueItem(BaseModel):
    topic_id: int
    topic_name: str
    track_name: str
    due_at: datetime


class ReviewSessionItem(BaseModel):
    session_id: int
    topic_id: int
    topic_name: str
    exercise: PublicExercise


class PlannerItemRead(BaseModel):
    id: int
    topic_id: int | None
    topic_name: str | None
    track_name: str | None
    item_type: str
    reason: str
    estimated_minutes: int
    order_index: int
    status: str
    action_path: str


class PlannerSettings(BaseModel):
    study_timezone: str = "Asia/Kolkata"
    daily_study_target: int
    dsa_daily_minimum: int
    python_daily_minimum: int
    sql_daily_minimum: int
    max_review_topics: int
    desired_retention: float


class PlannerSettingsUpdate(BaseModel):
    study_timezone: str | None = None
    daily_study_target: int | None = None
    dsa_daily_minimum: int | None = None
    python_daily_minimum: int | None = None
    sql_daily_minimum: int | None = None
    max_review_topics: int | None = None
    desired_retention: float | None = None
