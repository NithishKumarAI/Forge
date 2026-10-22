"""Edition identity and content difficulty are independent of curriculum/mastery versions."""
from typing import Literal
from pydantic import Field, StrictBool, model_validator
from .content_registry import StrictModel
from .ai import CurriculumProposal

SUBJECT_KEYS = ("quantitative-aptitude", "logical-reasoning", "verbal-english", "python",
    "sql-postgresql", "dsa", "system-design", "ai-fundamentals", "interview-communication")


class SubjectDefinition(StrictModel):
    key: str
    name: str
    description: str
    priority: int = Field(ge=1, le=100)
    icon: str


class EditionDefinition(StrictModel):
    key: Literal["placement-foundations", "advanced-engineering"]
    label: str
    name: str
    description: str
    levels: list[int]
    status: Literal["preparing", "future"]
    subjects: list[str]


class EditionManifest(StrictModel):
    format_version: Literal[1]
    subjects: list[SubjectDefinition]
    editions: list[EditionDefinition]

    @model_validator(mode="after")
    def valid_manifest(self):
        if {s.key for s in self.subjects} != set(SUBJECT_KEYS) or len(self.subjects) != 9:
            raise ValueError("Exactly the nine defined subjects are required")
        if {e.key for e in self.editions} != {"placement-foundations", "advanced-engineering"} or len(self.editions) != 2:
            raise ValueError("Edition identities must be unique")
        for edition in self.editions:
            if edition.levels != list(range(1, 4 if edition.key == "placement-foundations" else 6)) or edition.subjects != list(SUBJECT_KEYS):
                raise ValueError("Invalid edition subject/level scope")
            if edition.status != ("preparing" if edition.key == "placement-foundations" else "future"):
                raise ValueError("Advanced Engineering remains unavailable until a future compatible release")
        return self


class ScopeTopic(StrictModel):
    key: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    subject_key: str
    title: str
    description: str
    level: int = Field(ge=1, le=3)
    learning_outcomes: list[str] = Field(min_length=1)
    prerequisites: list[str]
    estimated_minutes: int = Field(ge=10, le=480)
    priority: int = Field(ge=1, le=100)
    coverage_requirements: list[str] = Field(min_length=1)
    assessment_route: Literal["objective", "coding", "reflection"]
    content_key: str


class PlacementScope(StrictModel):
    format_version: Literal[1]
    edition_key: Literal["placement-foundations"]
    version: str
    name: str
    description: str
    goal: str
    availability_policy: Literal["registry_bindings_only"]
    topics: list[ScopeTopic] = Field(min_length=27, max_length=200)

    @model_validator(mode="after")
    def complete_graph(self):
        if {(t.subject_key, t.level) for t in self.topics} != {(s, n) for s in SUBJECT_KEYS for n in (1, 2, 3)}:
            raise ValueError("Every subject must represent Levels 1, 2 and 3")
        if len({t.key for t in self.topics}) != len(self.topics):
            raise ValueError("Global topic keys must be unique")
        for topic in self.topics:
            if not topic.key.startswith(topic.subject_key + "-") or topic.content_key != f"forge/placement-foundations/{topic.subject_key}/{topic.key}":
                raise ValueError("Topic namespace does not match its subject")
        self.proposal()
        return self

    def proposal(self) -> CurriculumProposal:
        return CurriculumProposal(name=self.name, description=self.description, goal=self.goal, tracks=[{
            "key": subject, "name": subject.replace("-", " ").title(),
            "description": f"Build practical foundations in {subject.replace('-', ' ')}.",
            "priority": max(t.priority for t in self.topics if t.subject_key == subject),
            "topics": [{"key": t.key, "name": t.title, "description": t.description, "priority": t.priority,
                "target_level": "working", "estimated_minutes": t.estimated_minutes, "prerequisites": t.prerequisites}
                for t in self.topics if t.subject_key == subject]} for subject in SUBJECT_KEYS])


class EditionConfirmation(StrictModel):
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    scope_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reviewer: str = Field(min_length=3, max_length=120)
    scope_reviewed: StrictBool
    missing_content_acknowledged: StrictBool


class ContentAvailability(StrictModel):
    lesson_status: Literal["approved", "legacy", "planned"]
    lesson_count: int
    approved_lesson_count: int
    legacy_lesson_count: int
    practice_available: bool
    approved_practice_available: bool
    course_exercise_count: int
    assessment_item_count: int = 0
    arena_count: int
    completed_sections: int
    total_sections: int
    reading_percent: int


class EditionTopicRead(ScopeTopic):
    id: int | None
    availability: ContentAvailability


class EditionSubjectRead(SubjectDefinition):
    topics: list[EditionTopicRead]


class EditionBindingRead(StrictModel):
    curriculum_id: int
    name: str
    version: int
    status: Literal["draft", "confirmed"]
    graph_sha256: str
    reviewed_by: str | None
    is_active: bool


class EditionOverviewRead(StrictModel):
    edition: EditionDefinition
    subjects: list[EditionSubjectRead]
    binding: EditionBindingRead | None
    active_curriculum_id: int | None
    scope_version: str | None = None
    scope_sha256: str | None = None


class EditionIndexRead(EditionManifest):
    selected_edition_key: str | None
    active_curriculum_id: int | None
