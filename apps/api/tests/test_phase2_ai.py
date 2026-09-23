from sqlmodel import Session, select

from app.config import settings
from app.models import ChatMessage, Exercise, LearnerTopicState, LearningSession, ModelUsageEvent, Topic, Track, TransferCheck
from app.routers.ai import ai_status
from app.services.doubt import send_doubt
from app.services.tutor import continue_tutor_session, start_tutor_session
from app.services.usage import monthly_usage
from tests.fakes import FakeLLMProvider


def _first_topic(session: Session) -> Topic:
    return session.exec(select(Topic).order_by(Topic.id)).first()


def test_ai_status_with_no_key(session: Session, monkeypatch) -> None:
    monkeypatch.setattr(settings, "gemini_api_key", "")
    status = ai_status(session)
    assert status["configured"] is False
    assert "key" not in status


def test_tutor_stores_messages_without_changing_mastery(session: Session) -> None:
    provider = FakeLLMProvider()
    topic = _first_topic(session)
    state = session.get(LearnerTopicState, topic.id)
    before = state.model_dump()

    learning_session, first_turn = start_tutor_session(session, provider, topic)
    second_turn = continue_tutor_session(
        session, provider, learning_session, "Other tasks can run."
    )

    messages = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == learning_session.id)
    ).all()
    assert [message.role for message in messages] == ["assistant", "user", "assistant"]
    assert first_turn.question and second_turn.message_markdown
    session.refresh(state)
    assert state.model_dump() == before


def test_doubt_stores_messages_without_changing_mastery(session: Session) -> None:
    provider = FakeLLMProvider()
    topic = _first_topic(session)
    state = session.get(LearnerTopicState, topic.id)
    before = state.model_dump()

    doubt_session, reply = send_doubt(
        session,
        provider,
        session_id=None,
        topic_id=topic.id,
        message="Why is blocking I/O a problem?",
    )
    messages = session.exec(
        select(ChatMessage).where(ChatMessage.session_id == doubt_session.id)
    ).all()
    assert doubt_session.mode == "doubt"
    assert [message.role for message in messages] == ["user", "assistant"]
    assert "blocking I/O" in reply
    session.refresh(state)
    assert state.model_dump() == before


def test_doubt_during_open_transfer_marks_it_assisted(session: Session) -> None:
    topic = _first_topic(session)
    track = session.get(Track, topic.track_id)
    transfer_session = LearningSession(topic_id=topic.id, mode="transfer")
    session.add(transfer_session); session.flush()
    exercise = Exercise(
        curriculum_id=track.curriculum_id, track_id=track.id, topic_id=topic.id,
        exercise_type="multiple_choice", title="Transfer", prompt_markdown="Choose.",
        difficulty="interview", source="transfer", validation_status="valid",
        content_json='{"key":"test","hints":[],"content":{"choices":["A","B"],"correct_index":0,"explanation":"Because."}}',
    )
    session.add(exercise); session.flush()
    check = TransferCheck(topic_id=topic.id, exercise_id=exercise.id, session_id=transfer_session.id)
    session.add(check); session.commit()

    send_doubt(session, FakeLLMProvider(), session_id=None, topic_id=topic.id, message="Can I get help?")

    session.refresh(check)
    assert check.assisted is True


def test_fake_provider_usage_is_recorded(session: Session) -> None:
    provider = FakeLLMProvider()
    topic = _first_topic(session)
    start_tutor_session(session, provider, topic)
    event = session.exec(select(ModelUsageEvent)).one()
    assert event.provider == "fake"
    assert event.input_tokens == 100
    assert event.output_tokens == 40
    assert event.thought_tokens == 10
    assert event.cached_tokens == 5
    summary = monthly_usage(session)
    assert summary["calls"] == 1
    assert summary["input_tokens"] == 100
