from pydantic import ValidationError
from sqlmodel import Session

from ..config import settings
from ..providers import InvalidStructuredResponse, LLMProvider, ProviderError
from ..schemas.ai import CurriculumGenerationRequest, CurriculumProposal
from .usage import record_usage


CURRICULUM_POLICY = """You design compact, practical interview-preparation curricula.
Optimize for practical competence, interview readiness, minimal sufficient depth, and logical prerequisites.
Include only requested topics and genuinely necessary prerequisites. Never expand into unrelated technologies.
Use unique lowercase kebab-case keys for every track and every topic across the whole curriculum.
Prerequisites must reference topic keys exactly. Keep prerequisite chains shallow and acyclic.
Mark genuinely AI-added prerequisite topics with added_as_prerequisite=true; requested topics are false.
Aim for 2-8 tracks and 3-15 topics per track unless the user's scope clearly requires otherwise."""


def generate_curriculum_proposal(
    session: Session, provider: LLMProvider, request: CurriculumGenerationRequest
) -> CurriculumProposal:
    prompt = (
        f"User requirements:\n{request.requirements}\n\n"
        f"Preferred curriculum name: {request.name or 'Choose a concise name'}\n"
        f"Learning goal: {request.goal or 'Infer a practical interview-ready goal'}"
    )
    for attempt in range(2):
        try:
            proposal, result = provider.generate_structured(
                system_instruction=CURRICULUM_POLICY,
                prompt=prompt,
                thinking_level=settings.gemini_curriculum_thinking,
                response_model=CurriculumProposal,
            )
            record_usage(
                session,
                provider,
                result,
                purpose="curriculum_generation" if attempt == 0 else "curriculum_repair",
                thinking_level=settings.gemini_curriculum_thinking,
            )
            return proposal
        except InvalidStructuredResponse as exc:
            if attempt == 1:
                raise ProviderError(
                    "Curriculum generation returned an invalid structure. Please retry."
                ) from exc
            prompt += (
                "\n\nRepair the proposed curriculum. It failed validation with these errors:\n"
                f"{str(exc)[:1800]}\nReturn a complete corrected curriculum."
            )
    raise ProviderError("Curriculum generation returned an invalid structure. Please retry.")

