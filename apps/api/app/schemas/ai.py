from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


KEY_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class TopicProposal(BaseModel):
    key: str = Field(min_length=1, max_length=80, pattern=KEY_PATTERN)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=800)
    priority: int = Field(ge=1, le=100)
    target_level: str = Field(min_length=1, max_length=40)
    estimated_minutes: int = Field(ge=10, le=480)
    prerequisites: list[str] = Field(default_factory=list, max_length=20)
    added_as_prerequisite: bool = False

    @field_validator("name", "description", "target_level")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class TrackProposal(BaseModel):
    key: str = Field(min_length=1, max_length=80, pattern=KEY_PATTERN)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=800)
    priority: int = Field(ge=1, le=100)
    topics: list[TopicProposal] = Field(min_length=1, max_length=80)

    @field_validator("name", "description")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class CurriculumProposal(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=1200)
    goal: str = Field(min_length=1, max_length=1200)
    tracks: list[TrackProposal] = Field(min_length=1, max_length=15)

    @field_validator("name", "description", "goal")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @model_validator(mode="after")
    def validate_graph(self) -> "CurriculumProposal":
        track_keys = [track.key for track in self.tracks]
        if len(track_keys) != len(set(track_keys)):
            raise ValueError("track keys must be unique")

        topics = [topic for track in self.tracks for topic in track.topics]
        if len(topics) > 200:
            raise ValueError("curriculum cannot contain more than 200 topics")
        topic_keys = [topic.key for topic in topics]
        if len(topic_keys) != len(set(topic_keys)):
            raise ValueError("topic keys must be unique across the curriculum")
        known = set(topic_keys)
        graph: dict[str, list[str]] = {}
        for topic in topics:
            if topic.key in topic.prerequisites:
                raise ValueError(f"topic '{topic.key}' cannot depend on itself")
            dangling = [key for key in topic.prerequisites if key not in known]
            if dangling:
                raise ValueError(
                    f"topic '{topic.key}' has unknown prerequisites: {', '.join(dangling)}"
                )
            graph[topic.key] = topic.prerequisites

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(key: str) -> None:
            if key in visiting:
                raise ValueError("curriculum prerequisite graph contains a cycle")
            if key in visited:
                return
            visiting.add(key)
            for prerequisite in graph[key]:
                visit(prerequisite)
            visiting.remove(key)
            visited.add(key)

        for key in graph:
            visit(key)
        return self


class CurriculumGenerationRequest(BaseModel):
    requirements: str = Field(min_length=3, max_length=20_000)
    name: str | None = Field(default=None, max_length=160)
    goal: str | None = Field(default=None, max_length=1200)


class CurriculumDraftRequest(BaseModel):
    proposal: CurriculumProposal
    source_requirements: str = Field(default="", max_length=20_000)


class TutorTurn(BaseModel):
    message_markdown: str = Field(min_length=1, max_length=12_000)
    turn_type: Literal["explain", "check", "feedback", "clarify", "transition", "wrap_up"]
    question: str | None = Field(default=None, max_length=1000)
    concepts_covered: list[str] = Field(default_factory=list, max_length=20)
    suggested_next_action: str | None = Field(default=None, max_length=500)


class TutorStartResponse(BaseModel):
    session_id: int
    turn: TutorTurn


class TutorMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    chat_type: str
    created_at: datetime


class DoubtMessageRequest(BaseModel):
    session_id: int | None = None
    topic_id: int | None = None
    message: str = Field(min_length=1, max_length=8000)


class DoubtMessageResponse(BaseModel):
    session_id: int
    reply: str


class UsageSummary(BaseModel):
    calls: int
    input_tokens: int
    output_tokens: int
    thought_tokens: int
    cached_tokens: int
    estimated_cost_usd: float
    budget: dict


class AIStatusRead(BaseModel):
    configured: bool
    provider: str
    model: str
    this_month: UsageSummary
