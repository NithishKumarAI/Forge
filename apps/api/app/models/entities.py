from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import CheckConstraint, Column, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Curriculum(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name", "version", name="uq_curriculum_name_version"),)

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = ""
    source_type: str = Field(index=True)
    status: str = Field(index=True)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    confirmed_at: datetime | None = None
    tracks: list["Track"] = Relationship(back_populates="curriculum")


class Track(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("curriculum_id", "slug", name="uq_track_curriculum_slug"),)

    id: int | None = Field(default=None, primary_key=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", index=True)
    name: str
    slug: str = Field(index=True)
    description: str = ""
    order_index: int = Field(default=0, index=True)
    priority: int = Field(default=50, ge=0, le=100, index=True)
    curriculum: Curriculum | None = Relationship(back_populates="tracks")
    topics: list["Topic"] = Relationship(back_populates="track")


class Topic(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("track_id", "slug", name="uq_topic_track_slug"),)

    id: int | None = Field(default=None, primary_key=True)
    track_id: int = Field(foreign_key="track.id", index=True)
    name: str
    slug: str = Field(index=True)
    description: str = ""
    order_index: int = Field(default=0, index=True)
    priority: int = Field(default=50, ge=0, le=100, index=True)
    target_level: str = "working"
    estimated_minutes: int = Field(default=45, ge=1)
    track: Track | None = Relationship(back_populates="topics")
    learner_state: Optional["LearnerTopicState"] = Relationship(back_populates="topic")


class TopicPrerequisite(SQLModel, table=True):
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    prerequisite_topic_id: int = Field(foreign_key="topic.id", primary_key=True)


class LearnerTopicState(SQLModel, table=True):
    __table_args__ = (CheckConstraint("mastery_score >= 0 AND mastery_score <= 100"),)

    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    mastery_score: int = Field(default=0, ge=0, le=100, index=True)
    confidence: str = "unknown"
    status: str = Field(default="not_started", index=True)
    attempts: int = Field(default=0, ge=0)
    last_studied_at: datetime | None = None
    last_tested_at: datetime | None = None
    next_review_at: datetime | None = Field(default=None, index=True)
    topic: Topic | None = Relationship(back_populates="learner_state")


class LearningSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int | None = Field(default=None, foreign_key="topic.id", index=True)
    mode: str = Field(index=True)
    started_at: datetime = Field(default_factory=utc_now, index=True)
    ended_at: datetime | None = None


class Attempt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    attempt_type: str = Field(index=True)
    score: float = Field(ge=0, le=100)
    used_hint: bool = False
    passed: bool = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)


class Mistake(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("topic_id", "category", "description", name="uq_mistake"),)

    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    category: str = Field(index=True)
    description: str = Field(sa_column=Column(Text, nullable=False))
    occurrence_count: int = Field(default=1, ge=1)
    last_seen_at: datetime = Field(default_factory=utc_now, index=True)


class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: int | None = Field(default=None, foreign_key="learningsession.id", index=True)
    topic_id: int | None = Field(default=None, foreign_key="topic.id", index=True)
    role: str = Field(index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    chat_type: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ReviewState(SQLModel, table=True):
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    due_at: datetime = Field(index=True)
    state_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))


class AppSetting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field(sa_column=Column(Text, nullable=False))


class CurriculumGenerationMetadata(SQLModel, table=True):
    curriculum_id: int = Field(foreign_key="curriculum.id", primary_key=True)
    goal: str = Field(default="", sa_column=Column(Text, nullable=False))
    source_requirements: str = Field(default="", sa_column=Column(Text, nullable=False))
    topic_flags_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))


class ModelUsageEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    provider: str = Field(index=True)
    model: str = Field(index=True)
    purpose: str = Field(index=True)
    thinking_level: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    thought_tokens: int = Field(default=0, ge=0)
    cached_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=utc_now, index=True)


class Exercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", index=True)
    track_id: int = Field(foreign_key="track.id", index=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    exercise_type: str = Field(index=True)
    title: str
    prompt_markdown: str = Field(sa_column=Column(Text, nullable=False))
    difficulty: str = Field(index=True)
    source: str = "gemini"
    generator_model: str | None = None
    generator_version: str | None = None
    created_at: datetime = Field(default_factory=utc_now, index=True)
    is_active: bool = Field(default=True, index=True)
    validation_status: str = Field(default="valid", index=True)
    content_json: str = Field(sa_column=Column(Text, nullable=False))


class PracticeSessionExercise(SQLModel, table=True):
    session_id: int = Field(foreign_key="learningsession.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)
    order_index: int


class ExerciseAttemptDetail(SQLModel, table=True):
    attempt_id: int = Field(foreign_key="attempt.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", index=True)
    session_id: int = Field(foreign_key="learningsession.id", index=True)
    answer: str = Field(sa_column=Column(Text, nullable=False))
    hints_used_count: int = Field(default=0, ge=0)
    execution_summary_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    feedback: str = Field(default="", sa_column=Column(Text, nullable=False))
    grading_source: str
    evaluation_status: str = "complete"


class PracticeHintUse(SQLModel, table=True):
    session_id: int = Field(foreign_key="learningsession.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)
    count: int = Field(default=0, ge=0)


class MasteryEvidenceEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    event_type: str = Field(index=True)
    source_attempt_id: int | None = Field(default=None, foreign_key="attempt.id", index=True)
    score: float = Field(ge=0, le=100)
    evidence_weight: float = Field(gt=0)
    assisted: bool = False
    metadata_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class TransferCheck(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id", index=True)
    session_id: int = Field(foreign_key="learningsession.id", unique=True, index=True)
    attempt_id: int | None = Field(default=None, foreign_key="attempt.id")
    score: float | None = Field(default=None, ge=0, le=100)
    passed: bool = False
    assisted: bool = False
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ReviewEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    session_id: int | None = Field(default=None, foreign_key="learningsession.id", index=True)
    attempt_id: int | None = Field(default=None, foreign_key="attempt.id", index=True)
    score: float = Field(ge=0, le=100)
    fsrs_rating: int = Field(ge=1, le=4)
    reviewed_at: datetime = Field(default_factory=utc_now, index=True)
    previous_due_at: datetime | None = None
    next_due_at: datetime = Field(index=True)
    metadata_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))


class DailyPlanItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plan_date: str = Field(index=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", index=True)
    topic_id: int | None = Field(default=None, foreign_key="topic.id", index=True)
    item_type: str = Field(index=True)
    reason: str = Field(sa_column=Column(Text, nullable=False))
    estimated_minutes: int = Field(ge=1)
    order_index: int = 0
    status: str = Field(default="planned", index=True)


class InterviewSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", index=True)
    mode: str = Field(index=True)
    status: str = Field(default="active", index=True)
    started_at: datetime = Field(default_factory=utc_now, index=True)
    completed_at: datetime | None = None
    overall_score: float | None = Field(default=None, ge=0, le=100)
    duration_seconds: int | None = Field(default=None, ge=0)
    metadata_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))


class InterviewQuestion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="interviewsession.id", index=True)
    section: str = Field(index=True)
    competency: str = Field(index=True)
    question_type: str = Field(index=True)
    prompt_markdown: str = Field(sa_column=Column(Text, nullable=False))
    topic_id: int | None = Field(default=None, foreign_key="topic.id", index=True)
    exercise_id: int | None = Field(default=None, foreign_key="exercise.id", index=True)
    learning_session_id: int | None = Field(default=None, foreign_key="learningsession.id", index=True)
    follow_up_of_id: int | None = Field(default=None, foreign_key="interviewquestion.id", index=True)
    rubric_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    expected_concepts_json: str = Field(default="[]", sa_column=Column(Text, nullable=False))
    difficulty: str = "medium"
    suggested_seconds: int = Field(default=180, ge=30)
    blueprint_slot: int = Field(default=0, ge=0, index=True)
    order_index: int = Field(default=0, ge=0, index=True)
    generated_by: str = "gemini"
    started_at: datetime = Field(default_factory=utc_now, index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)


class InterviewResponse(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="interviewquestion.id", unique=True, index=True)
    response_text: str | None = Field(default=None, sa_column=Column(Text))
    attempt_id: int | None = Field(default=None, foreign_key="attempt.id", index=True)
    score: float = Field(ge=0, le=100)
    evaluation_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    answered_at: datetime = Field(default_factory=utc_now, index=True)
    duration_seconds: int | None = Field(default=None, ge=0)


class InterviewReport(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="interviewsession.id", unique=True, index=True)
    report_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class CourseLesson(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("topic_id", "content_version", name="uq_course_lesson_version"),)
    id: int | None = Field(default=None, primary_key=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", index=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    content_version: str = Field(index=True)
    title: str
    source_path: str
    content_hash: str = Field(index=True)
    active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utc_now)


class LessonSectionProgress(SQLModel, table=True):
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    section_slug: str = Field(primary_key=True)
    completed: bool = False
    first_viewed_at: datetime = Field(default_factory=utc_now)
    last_viewed_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class TutorSessionState(SQLModel, table=True):
    session_id: int = Field(foreign_key="learningsession.id", primary_key=True)
    lesson_version: str
    section_slug: str


class ArenaProblem(SQLModel, table=True):
    key: str = Field(primary_key=True)
    track: str = Field(index=True)
    title: str
    difficulty: str = Field(index=True)
    topic_tags_json: str = Field(default="[]", sa_column=Column(Text, nullable=False))
    source_path: str
    content_hash: str = Field(index=True)
    version: str
    active: bool = Field(default=True, index=True)
    mapped_topic_id: int | None = Field(default=None, foreign_key="topic.id", index=True)


class ArenaAttempt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    problem_key: str = Field(foreign_key="arenaproblem.key", index=True)
    track: str = Field(index=True)
    submitted_source: str = Field(sa_column=Column(Text, nullable=False))
    score: float = Field(ge=0, le=100)
    passed: bool = Field(index=True)
    gave_up: bool = False
    hints_used: int = Field(default=0, ge=0)
    runtime_ms: int | None = Field(default=None, ge=0)
    result_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ArenaHintUse(SQLModel, table=True):
    problem_key: str = Field(foreign_key="arenaproblem.key", primary_key=True)
    count: int = Field(default=0, ge=0)


class TopicMigrationMap(SQLModel, table=True):
    old_topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    new_topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    mapping_key: str = Field(index=True)
    migrated_at: datetime = Field(default_factory=utc_now)


class SchemaMigration(SQLModel, table=True):
    version: int = Field(primary_key=True)
    name: str
    checksum: str
    applied_at: datetime = Field(default_factory=utc_now)


class ContentRevision(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("content_key", "revision", name="uq_content_revision"),)
    id: int | None = Field(default=None, primary_key=True)
    content_key: str = Field(index=True)
    revision: str
    content_type: str = Field(index=True)
    source_path: str
    snapshot_path: str
    sha256: str
    provenance_json: str = Field(sa_column=Column(Text, nullable=False))
    approval_status: str = "legacy_baseline"
    registered_at: datetime = Field(default_factory=utc_now)


class TopicContentBinding(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("topic_id", "order_index", name="uq_topic_content_order"),)
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    content_revision_id: int = Field(foreign_key="contentrevision.id", primary_key=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", index=True)
    order_index: int = Field(ge=0)
    legacy_progress_compatible: bool = False
    coverage_note: str


class ArenaTopicBinding(SQLModel, table=True):
    curriculum_id: int = Field(foreign_key="curriculum.id", primary_key=True)
    problem_key: str = Field(foreign_key="arenaproblem.key", primary_key=True)
    content_revision_id: int = Field(foreign_key="contentrevision.id")
    topic_id: int | None = Field(default=None, foreign_key="topic.id", index=True)
    rationale: str


class CourseExerciseBinding(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("exercise_id", name="uq_registry_exercise"),)
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    content_revision_id: int = Field(foreign_key="contentrevision.id", primary_key=True)
    exercise_key: str = Field(primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", index=True)


class ContentSectionProgress(SQLModel, table=True):
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    content_revision_id: int = Field(foreign_key="contentrevision.id", primary_key=True)
    section_slug: str = Field(primary_key=True)
    completed: bool = False
    first_viewed_at: datetime = Field(default_factory=utc_now)
    last_viewed_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class ContentValidationReport(SQLModel, table=True):
    sha256: str = Field(primary_key=True)
    candidate_sha256: str
    payload_sha256: str
    policy_version: str
    candidate_json: str = Field(sa_column=Column(Text, nullable=False))
    report_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)


class ContentReviewRecord(SQLModel, table=True):
    sha256: str = Field(primary_key=True)
    validation_sha256: str = Field(foreign_key="contentvalidationreport.sha256")
    reviewer: str
    outcome: str
    reviewed_at: datetime
    review_json: str = Field(sa_column=Column(Text, nullable=False))


class ApprovedContentRelease(SQLModel, table=True):
    release_id: str = Field(primary_key=True)
    sha256: str
    package_json: str = Field(sa_column=Column(Text, nullable=False))
    published_at: datetime = Field(default_factory=utc_now)


class ContentReleaseEntry(SQLModel, table=True):
    release_id: str = Field(foreign_key="approvedcontentrelease.release_id", primary_key=True)
    curriculum_id: int = Field(foreign_key="curriculum.id", primary_key=True)
    content_revision_id: int = Field(foreign_key="contentrevision.id", primary_key=True)
    validation_sha256: str = Field(foreign_key="contentvalidationreport.sha256")
    review_sha256: str = Field(foreign_key="contentreviewrecord.sha256")
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    order_index: int = Field(ge=0)


class ContentReleaseEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    release_id: str = Field(foreign_key="approvedcontentrelease.release_id")
    status: str
    actor: str
    reason: str
    created_at: datetime = Field(default_factory=utc_now)


class ArenaAttemptContent(SQLModel, table=True):
    attempt_id: int = Field(foreign_key="arenaattempt.id", primary_key=True)
    content_revision_id: int = Field(foreign_key="contentrevision.id")
