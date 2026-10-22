from typing import Any, Literal
from pydantic import BaseModel, Field

LearningStage = Literal[
    "not_started",
    "learning",
    "practising",
    "ready_to_advance",
    "retained",
    "review_due"
]

ExerciseProgressionStage = Literal[
    "first_steps",
    "beginner",
    "developing",
    "intermediate",
    "challenging"
]

class WorkedExample(BaseModel):
    title: str
    code: str
    explanation: str

class TracingStep(BaseModel):
    step_number: int
    line_or_expression: str
    state_description: str
    result_or_value: str

class CommonMistake(BaseModel):
    mistake_description: str
    wrong_code: str
    explanation: str
    correct_code: str

class ConceptTeachingContent(BaseModel):
    summary: str
    why_it_matters: str
    intuition: str
    analogy: str
    syntax_guide: str
    worked_example_title: str
    worked_example_code: str
    worked_example_explanation: str
    tracing_steps: list[TracingStep] = Field(default_factory=list)
    common_mistakes: list[CommonMistake] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)

class TeachingRef(BaseModel):
    source_type: str
    content_key: str
    section_slug: str

class ConceptStepSummary(BaseModel):
    key: str
    subject_key: str
    topic_slug: str
    title: str
    stage: ExerciseProgressionStage
    order_index: int
    objective: str
    prerequisite_keys: list[str] = []
    progress_state: LearningStage = "not_started"
    prerequisites_met: bool = True
    is_current: bool = False
    action_path: str = ""
    action_label: str = "Start"

class ConceptStepDetail(ConceptStepSummary):
    teaching_ref: TeachingRef | None = None
    worked_example: WorkedExample | None = None
    teaching_content: ConceptTeachingContent | None = None
    guided_practice_refs: list[str] = []
    independent_practice_refs: list[str] = []
    availability_status: str = "available"
    review_eligible: bool = True

class LearningRecommendation(BaseModel):
    kind: Literal[
        "resume",
        "review",
        "prerequisite",
        "next_concept",
        "practice",
        "secondary_subject"
    ]
    subject_key: str
    subject_name: str
    concept_key: str
    concept_title: str
    stage: str
    objective: str
    progress_state: LearningStage
    progress_summary: str
    reason: str
    action_path: str
    action_label: str
    priority_tier: int = Field(ge=1, le=6)
    is_primary: bool = False

class SubjectProgressSummary(BaseModel):
    subject_key: str
    subject_name: str
    description: str = ""
    icon: str = "book"
    total_concepts: int = 0
    completed_concepts: int = 0
    in_progress_concepts: int = 0
    current_concept_title: str | None = None
    current_concept_key: str | None = None
    progress_state: LearningStage = "not_started"
    action_path: str = ""

class LearningPathDashboardResponse(BaseModel):
    primary_recommendation: LearningRecommendation | None = None
    secondary_recommendations: list[LearningRecommendation] = Field(default_factory=list)
    active_subject: str = "python"
    subjects: list[SubjectProgressSummary] = Field(default_factory=list)
    content_availability: dict[str, Any] = Field(default_factory=dict)
    recent_mistakes: list[dict[str, Any]] = Field(default_factory=list)
    reviews_due_count: int = 0
    active_curriculum: dict[str, Any] | None = None

class ArenaStageDetail(BaseModel):
    key: str
    name: str
    description: str
    order_index: int
    badge_color: str
    problems: list[dict[str, Any]] = Field(default_factory=list)
    solved_count: int = 0
    total_count: int = 0

class BeginnerExerciseRead(BaseModel):
    key: str
    track: Literal["python", "sql", "dsa"]
    stage: str
    title: str
    concept_key: str
    concept_title: str | None = None
    instructions: str
    starter_code: str | None = None
    starter_query: str | None = None
    setup_sql: str | None = None
    examples: list[dict[str, Any]] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    solved: bool = False

class BeginnerExerciseSubmitRequest(BaseModel):
    source: str = Field(min_length=1, max_length=10000)

class BeginnerExerciseSubmitResponse(BaseModel):
    exercise_key: str
    passed: bool
    score: float = Field(ge=0, le=100)
    output: str = ""
    errors: str = ""
    feedback: str = ""
    solution: str | None = None
    explanation: str | None = None
