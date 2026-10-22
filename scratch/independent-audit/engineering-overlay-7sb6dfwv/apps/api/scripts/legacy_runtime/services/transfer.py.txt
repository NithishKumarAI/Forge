import json

from sqlmodel import Session, select

from ..config import settings
from ..models import Exercise, LearningSession, PracticeSessionExercise, Topic, Track, TransferCheck
from ..providers import InvalidStructuredResponse, LLMProvider, ProviderError
from ..schemas.practice import ExercisePackProposal
from .mastery import transfer_eligible
from .practice import EXERCISE_POLICY, _topic_context, public_exercise
from .usage import record_usage


TRANSFER_POLICY = EXERCISE_POLICY + """
Generate exactly one unseen transfer exercise in a meaningfully different context from prior tasks.
Prefer Python code/debug for Python or DSA and scenario short answer for backend, LLM, RAG, or DevOps.
It must work without hints; still provide an empty hints array. Do not lightly reword prior tasks.
"""


def start_transfer(session: Session, topic: Topic, provider: LLMProvider | None) -> tuple[LearningSession, Exercise]:
    if not transfer_eligible(session, topic.id):
        raise ValueError("More mixed practice evidence is needed before transfer verification.")
    existing_open = session.exec(select(TransferCheck).where(TransferCheck.topic_id == topic.id, TransferCheck.attempt_id == None).order_by(TransferCheck.created_at.desc())).first()  # noqa: E711
    if existing_open:
        existing_exercise = session.get(Exercise, existing_open.exercise_id)
        if existing_exercise and existing_exercise.is_active:
            return session.get(LearningSession, existing_open.session_id), existing_exercise
    if provider is None:
        raise ProviderError("Gemini is required to generate a genuinely unseen transfer check.")
    track = session.get(Track, topic.track_id)
    prior = session.exec(select(Exercise).where(Exercise.topic_id == topic.id).order_by(Exercise.created_at.desc()).limit(12)).all()
    prompt = _topic_context(session, topic) + "\nPrior task summaries:\n" + "\n".join(f"- {item.exercise_type}: {item.title}: {item.prompt_markdown[:240]}" for item in prior)
    prompt += "\nGenerate exactly one distinct transfer exercise. It must not repeat or lightly reword any summary above."
    last_error = None
    for attempt in range(2):
        try:
            pack, result = provider.generate_structured(system_instruction=TRANSFER_POLICY, prompt=prompt, thinking_level=settings.gemini_exercise_thinking, response_model=ExercisePackProposal)
            if len(pack.exercises) != 1:
                raise InvalidStructuredResponse("Transfer generation must return exactly one exercise")
            proposal = pack.exercises[0]
            proposal.hints = []
            exercise = Exercise(
                curriculum_id=track.curriculum_id, track_id=track.id, topic_id=topic.id,
                exercise_type=proposal.exercise_type, title=proposal.title,
                prompt_markdown=proposal.prompt_markdown, difficulty="interview", source="transfer",
                generator_model=result.model, generator_version="phase4-v1",
                validation_status="pending" if proposal.exercise_type.startswith("python_") else "valid",
                content_json=json.dumps({"key": proposal.key, "hints": [], "content": proposal.content.model_dump()}),
            )
            session.add(exercise); session.flush()
            learning_session = LearningSession(topic_id=topic.id, mode="transfer")
            session.add(learning_session); session.flush()
            session.add(PracticeSessionExercise(session_id=learning_session.id, exercise_id=exercise.id, order_index=0))
            session.add(TransferCheck(topic_id=topic.id, exercise_id=exercise.id, session_id=learning_session.id))
            session.commit()
            record_usage(session, provider, result, purpose="transfer_generation" if attempt == 0 else "transfer_generation", thinking_level=settings.gemini_exercise_thinking)
            return learning_session, exercise
        except InvalidStructuredResponse as exc:
            last_error = exc
            prompt += f"\nRepair the complete response: {str(exc)[:1000]}"
    raise ProviderError("Transfer generation returned invalid structured output. Try again later.") from last_error


def transfer_session(session: Session, session_id: int) -> dict:
    check = session.exec(select(TransferCheck).where(TransferCheck.session_id == session_id)).first()
    if not check:
        raise ValueError("Transfer session not found")
    return {"session_id": session_id, "topic_id": check.topic_id, "exercise": public_exercise(session.get(Exercise, check.exercise_id))}
