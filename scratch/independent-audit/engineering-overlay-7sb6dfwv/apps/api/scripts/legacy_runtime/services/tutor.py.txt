from sqlmodel import Session, select

from ..config import settings
from ..models import ChatMessage, Curriculum, LearnerTopicState, LearningSession, Topic, Track, TutorSessionState
from ..providers import LLMProvider
from ..schemas.ai import TutorTurn
from .catalog import topic_to_dict
from .usage import record_usage
from .course import CourseError, load_lesson_for_topic, progress


TUTOR_POLICY = """You are Forge, a professor over an authoritative static lesson.
The supplied Forge lesson is authoritative. Teach from it and never modify the syllabus.
Do not introduce factual material outside the supplied course content as if it were part of the lesson.
If a question is unsupported by the supplied course corpus, say so clearly.
You may simplify, rephrase, use analogies, and add a tiny original example consistent with the lesson.
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


def _lesson_context(session: Session, topic: Topic, section_slug: str | None = None) -> tuple[object, object]:
    lesson=load_lesson_for_topic(session,topic); state=progress(session,topic,lesson)
    slug=section_slug or state["current_section_slug"]
    section=next((s for s in lesson.sections if s.slug==slug),None)
    if section is None: raise CourseError("Lesson section not found")
    outline="\n".join(f"{s.order_index+1}. {s.title} ({s.slug})" for s in lesson.sections)
    return lesson, section, f"Authoritative outline:\n{outline}\n\nCurrent section JSON:\n{section.model_dump_json()}\nLearning objectives: {lesson.learning_objectives}"


def start_tutor_session(
    session: Session, provider: LLMProvider, topic: Topic, section_slug: str | None = None
) -> tuple[LearningSession, TutorTurn]:
    lesson, section, lesson_context = _lesson_context(session,topic,section_slug)
    learning_session = LearningSession(topic_id=topic.id, mode="tutor")
    session.add(learning_session)
    session.flush(); session.add(TutorSessionState(session_id=learning_session.id,lesson_version=lesson.version,section_slug=section.slug)); session.commit()
    session.refresh(learning_session)
    turn, result = provider.generate_structured(
        system_instruction=TUTOR_POLICY,
        prompt=(
            f"{_topic_context(session, topic)}\n\n{lesson_context}\n\n"
            "Teach this current section, give a tiny example, "
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
    if learning_session.mode != "tutor" or learning_session.topic_id is None:
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
    tutor_state=session.get(TutorSessionState,learning_session.id)
    _,_,lesson_context=_lesson_context(session,topic,tutor_state.section_slug if tutor_state else None)
    turn, result = provider.generate_structured(
        system_instruction=TUTOR_POLICY,
        prompt=f"{_topic_context(session, topic)}\n\n{lesson_context}\n\nRecent conversation:\n{history}",
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
