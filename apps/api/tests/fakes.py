from pydantic import BaseModel

from app.providers import LLMProvider, LLMResult, LLMUsage
from app.schemas.ai import CurriculumProposal, TopicProposal, TrackProposal, TutorTurn


def valid_proposal(name: str = "Backend Starter") -> CurriculumProposal:
    return CurriculumProposal(
        name=name,
        description="A compact backend interview curriculum.",
        goal="Build practical backend interview fluency.",
        tracks=[
            TrackProposal(
                key="foundations",
                name="Foundations",
                description="Core prerequisites.",
                priority=100,
                topics=[
                    TopicProposal(
                        key="python-functions",
                        name="Python functions",
                        description="Use and explain Python functions.",
                        priority=100,
                        target_level="working",
                        estimated_minutes=40,
                        prerequisites=[],
                        added_as_prerequisite=True,
                    ),
                    TopicProposal(
                        key="fastapi",
                        name="FastAPI",
                        description="Build typed HTTP APIs.",
                        priority=95,
                        target_level="interview_ready",
                        estimated_minutes=60,
                        prerequisites=["python-functions"],
                        added_as_prerequisite=False,
                    ),
                ],
            )
        ],
    )


class FakeLLMProvider(LLMProvider):
    provider_name = "fake"
    model = "fake-model"

    def __init__(self) -> None:
        self.calls = 0

    def _result(self, text: str) -> LLMResult:
        self.calls += 1
        return LLMResult(
            text=text,
            model=self.model,
            usage=LLMUsage(
                input_tokens=100,
                output_tokens=40,
                thought_tokens=10,
                cached_tokens=5,
            ),
        )

    def generate_text(
        self, *, system_instruction: str, prompt: str, thinking_level: str
    ) -> LLMResult:
        return self._result("Because blocking I/O pauses the event-loop thread. Use an async client.")

    def generate_structured(
        self,
        *,
        system_instruction: str,
        prompt: str,
        thinking_level: str,
        response_model: type[BaseModel],
    ) -> tuple[BaseModel, LLMResult]:
        if response_model is CurriculumProposal:
            value = valid_proposal()
        elif response_model is TutorTurn:
            value = TutorTurn(
                message_markdown="`await` lets other tasks run while work is paused. What happens while a coroutine awaits I/O?",
                turn_type="check",
                question="What happens while a coroutine awaits I/O?",
                concepts_covered=["await", "event loop"],
                suggested_next_action="Answer the check question.",
            )
        else:
            raise AssertionError(f"Unexpected response model: {response_model}")
        result = self._result(value.model_dump_json())
        return value, result

