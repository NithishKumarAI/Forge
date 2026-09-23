from sqlmodel import Session, select

from ..config import settings
from ..models import ChatMessage, Curriculum, LearnerTopicState, LearningSession, Topic, Track
from ..providers import LLMProvider
from ..schemas.ai import TutorTurn
from .catalog import topic_to_dict
from .usage import record_usage


TUTOR_POLICY = """You are Forge, an excellent practical technical tutor.
Teach one manageable concept at a time using concise plain language before terminology.
Use small runnable examples and relate ideas to backend or AI engineering when useful.
After a meaningful concept, ask exactly one short understanding-check question and wait.
When an answer is correct, confirm briefly, add essential nuance, and continue. If partial, identify the missing point and guide. If wrong, explain the misconception simply and ask another short check.
Teach only enough for working and interview fluency unless the learner asks to go deeper.
Never claim mastery from conversation, never manipulate scores, and acknowledge factual uncertainty.
Format technical content cleanly in Markdown and keep each response reasonably short."""


def _topic_context(session: Session, topic: Topic) -> str:
    track = session.get(Track, topic.track_id)
    curriculum = session.get(Curriculum, track.curriculum_id) if track else None
    state = session.get(LearnerTopicState, topic.id) or LearnerTopicState(topic_id=topic.id)
    data = topic_to_dict(session, topic)
    prerequisites = ", ".join(item["name"] for item in data["prerequisites"]) or "None"
    return f"""Curriculum: {curriculum.name if curriculum else 'Unknown'}
Track: {track.name if track else 'Unknown'}
Topic: {topic.name}
Description: {topic.description}
Target level: {topic.target_level}
Estimated minutes: {topic.estimated_minutes}
Prerequisites: {prerequisites}
Learner state: mastery={state.mastery_score}, status={state.status}, attempts={state.attempts}"""


def _recent_messages(session: Session, session_id: int, limit: int = 10) -> str:
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    ).all()
    messages.reverse()
    return "\n".join(f"{message.role}: {message.content}" for message in messages)


def start_tutor_session(
    session: Session, provider: LLMProvider, topic: Topic
) -> tuple[LearningSession, TutorTurn]:
    learning_session = LearningSession(topic_id=topic.id, mode="learn")
    session.add(learning_session)
    session.commit()
    session.refresh(learning_session)
    turn, result = provider.generate_structured(
        system_instruction=TUTOR_POLICY,
        prompt=(
            f"{_topic_context(session, topic)}\n\n"
            "Begin the lesson. Teach the first essential concept, give a tiny example, "
            "and ask one short understanding-check question."
        ),
        thinking_level=settings.gemini_tutor_thinking,
        response_model=TutorTurn,
    )
    session.add(
        ChatMessage(
            session_id=learning_session.id,
            topic_id=topic.id,
            role="assistant",
            content=turn.message_markdown,
            chat_type="tutor",
        )
    )
    session.commit()
    record_usage(
        session,
        provider,
        result,
        purpose="tutor_start",
        thinking_level=settings.gemini_tutor_thinking,
    )
    return learning_session, turn


def continue_tutor_session(
    session: Session,
    provider: LLMProvider,
    learning_session: LearningSession,
    message: str,
) -> TutorTurn:
    if learning_session.mode != "learn" or learning_session.topic_id is None:
        raise ValueError("This is not a tutor learning session")
    topic = session.get(Topic, learning_session.topic_id)
    if topic is None:
        raise ValueError("Session topic no longer exists")
    session.add(
        ChatMessage(
            session_id=learning_session.id,
            topic_id=topic.id,
            role="user",
            content=message,
            chat_type="tutor",
        )
    )
    session.commit()
    history = _recent_messages(session, learning_session.id)
    turn, result = provider.generate_structured(
        system_instruction=TUTOR_POLICY,
        prompt=f"{_topic_context(session, topic)}\n\nRecent conversation:\n{history}",
        thinking_level=settings.gemini_tutor_thinking,
        response_model=TutorTurn,
    )
    session.add(
        ChatMessage(
            session_id=learning_session.id,
            topic_id=topic.id,
            role="assistant",
            content=turn.message_markdown,
            chat_type="tutor",
        )
    )
    session.commit()
    record_usage(
        session,
        provider,
        result,
        purpose="tutor_followup",
        thinking_level=settings.gemini_tutor_thinking,
    )
    return turn


def get_session_messages(session: Session, session_id: int) -> list[ChatMessage]:
    return list(
        session.exec(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.chat_type == "tutor",
            )
            .order_by(ChatMessage.created_at)
        ).all()
    )

