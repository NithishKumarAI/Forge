from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..services.content_paths import validate_relative_path


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LegacyExercise(BaseModel):
    """Existing static format, distinct from the runtime AI proposal schema.

    Legacy rubrics may be strings or weighted objects. Registration preserves them;
    it does not certify answers, rewrite rubrics, or change their grading policy.
    """
    key: str = Field(min_length=1)
    exercise_type: Literal["multiple_choice", "short_answer", "python_code", "python_debug"]
    title: str = Field(min_length=1)
    prompt_markdown: str = Field(min_length=1)
    difficulty: str = Field(min_length=1)
    hints: list[str] = []
    content: dict

    @model_validator(mode="after")
    def structured_content(self):
        if self.exercise_type == "multiple_choice":
            choices, index = self.content.get("choices"), self.content.get("correct_index")
            if not isinstance(choices, list) or not isinstance(index, int) or not 0 <= index < len(choices):
                raise ValueError("Invalid legacy MCQ choice contract")
        elif self.exercise_type == "short_answer":
            if not isinstance(self.content.get("rubric"), list) or not self.content.get("reference_answer"):
                raise ValueError("Missing legacy short-answer reference/rubric")
        elif not self.content.get("function_name") or not self.content.get("reference_solution"):
            raise ValueError("Missing legacy code contract")
        return self


class LessonReference(StrictModel):
    content_key: str
    revision: str = Field(min_length=1)
    legacy_progress_compatible: bool = False

    _safe_key = field_validator("content_key")(validate_relative_path)


class TopicBindingSpec(StrictModel):
    topic: str
    lessons: list[LessonReference] = Field(min_length=1)
    coverage_note: str = Field(min_length=1)

    _safe_topic = field_validator("topic")(validate_relative_path)

    @model_validator(mode="after")
    def unambiguous(self):
        keys = [(item.content_key, item.revision) for item in self.lessons]
        if len(keys) != len(set(keys)):
            raise ValueError("A topic cannot bind the same lesson revision twice")
        if any(item.legacy_progress_compatible for item in self.lessons[1:]):
            raise ValueError("Only the original primary lesson may use legacy progress")
        return self


class ArenaBindingSpec(StrictModel):
    problem_key: str = Field(pattern=r"^[a-z0-9-]+$")
    revision: str = Field(min_length=1)
    topic: str | None
    rationale: str = Field(min_length=1)

    @field_validator("topic")
    @classmethod
    def safe_topic(cls, value):
        return validate_relative_path(value) if value is not None else None


class CurriculumBindingSpec(StrictModel):
    name: str
    version: int = Field(ge=1)
    source_type: Literal["default"] = "default"
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    topics: list[TopicBindingSpec]
    unmapped_topics: dict[str, str]
    arena: list[ArenaBindingSpec]

    @model_validator(mode="after")
    def unambiguous(self):
        topics = [item.topic for item in self.topics]
        problems = [item.problem_key for item in self.arena]
        if len(topics) != len(set(topics)) or len(problems) != len(set(problems)):
            raise ValueError("Duplicate/ambiguous topic or Arena binding")
        if set(topics).intersection(self.unmapped_topics):
            raise ValueError("Topic cannot be both bound and unmapped")
        return self


class LegacyBindingsManifest(StrictModel):
    format_version: Literal[1]
    curricula: list[CurriculumBindingSpec]

    @model_validator(mode="after")
    def unique_curricula(self):
        identities = [(item.name, item.version, item.source_type) for item in self.curricula]
        if len(identities) != len(set(identities)):
            raise ValueError("Ambiguous curriculum identity")
        return self
