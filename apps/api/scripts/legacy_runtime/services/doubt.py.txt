from sqlmodel import Session, select

from ..config import settings
from ..models import ChatMessage, Curriculum, LearningSession, Topic, Track, TransferCheck
from ..providers import LLMProvider
from .usage import record_usage
from .course import load_lesson_for_topic, search_course


DOUBT_POLICY = """You are Forge Doubts, a concise grounded technical teaching assistant.
Answer only from CURRENT SECTION plus LOCAL COURSE SEARCH supplied below. If the answer is not supported, say exactly: "This isn't covered in the current Forge course material."
Answer the specific question first. Explain jargon simply and use one tiny example when useful.
Stay aware of the supplied learning context, but do not turn a small doubt into a full lesson.
Never change or claim mastery, curriculum, or recommendations. Acknowledge uncertainty."""


def _context(session: Session, topic_id: int | None, section_slug: str | None, query: str) -> str:
    if topic_id is None:
        return "Context: General technical question"
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise ValueError("Topic not found")
    track = session.get(Track, topic.track_id)
    curriculum = session.get(Curriculum, track.curriculum_id) if track else None
    lesson=load_lesson_for_topic(session,topic)
    section=next((s for s in lesson.sections if s.slug==section_slug),lesson.sections[0])
    neighbors=[s.title for s in lesson.sections if abs(s.order_index-section.order_index)==1]
    retrieved=search_course(session,query,topic_id)
    return (
        f"Curriculum: {curriculum.name if curriculum else 'Unknown'}\n"
        f"Track: {track.name if track else 'Unknown'}\n"
        f"Topic: {topic.name}\nCurrent section: {section.title}\nSection content: {section.markdown}\n"
        f"Key points: {section.key_points}\nNeighbor sections: {neighbors}\nSources: {[str(s.url) for s in lesson.sources]}\n"
        f"Local search results: {retrieved}"
    )


def send_doubt(
    session: Session,
    provider: LLMProvider,
    *,
    session_id: int | None,
    topic_id: int | None,
    message: str,
    section_slug: str | None = None,
) -> tuple[LearningSession, str]:
    doubt_session = session.get(LearningSession, session_id) if session_id else None
    if doubt_session is not None and doubt_session.mode != "doubt":
        raise ValueError("Session is not a doubt conversation")
    if doubt_session is None:
        doubt_session = LearningSession(topic_id=topic_id, mode="doubt")
        session.add(doubt_session)
        session.commit()
        session.refresh(doubt_session)
    effective_topic_id = topic_id if topic_id is not None else doubt_session.topic_id
    if effective_topic_id is not None:
        open_transfer = session.exec(
            select(TransferCheck)
            .where(TransferCheck.topic_id == effective_topic_id, TransferCheck.attempt_id == None)  # noqa: E711
            .order_by(TransferCheck.created_at.desc())
        ).first()
        if open_transfer:
            open_transfer.assisted = True
            session.add(open_transfer)
    session.add(
        ChatMessage(
            session_id=doubt_session.id,
            topic_id=effective_topic_id,
            role="user",
            content=message,
            chat_type="doubt",
        )
    )
    session.commit()
    recent = session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == doubt_session.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    ).all()
    recent.reverse()
    history = "\n".join(f"{item.role}: {item.content}" for item in recent)
    result = provider.generate_text(
        system_instruction=DOUBT_POLICY,
        prompt=f"{_context(session, effective_topic_id, section_slug, message)}\n\nRecent conversation:\n{history}",
        thinking_level=settings.gemini_doubt_thinking,
    )
    session.add(
        ChatMessage(
            session_id=doubt_session.id,
            topic_id=effective_topic_id,
            role="assistant",
            content=result.text,
            chat_type="doubt",
        )
    )
    session.commit()
    record_usage(
        session,
        provider,
        result,
        purpose="doubt",
        thinking_level=settings.gemini_doubt_thinking,
    )
    return doubt_session, result.text
