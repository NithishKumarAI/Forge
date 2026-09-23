from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Curriculum, LearnerTopicState, Topic, Track
from ..schemas.api import (
    CurriculumRead,
    CurriculumSummary,
    DashboardRead,
    TopicRead,
    TopicStateUpdate,
    TrackRead,
    TrackSummary,
)
from ..services.catalog import curriculum_to_dict, topic_to_dict, track_to_dict
from ..services.dashboard import build_dashboard


router = APIRouter(prefix="/api")
ALLOWED_STATUSES = {"not_started", "learning", "working", "strong", "interview_ready"}
ALLOWED_CONFIDENCE = {"unknown", "low", "medium", "high"}


@router.get("/curricula", response_model=list[CurriculumSummary])
def list_curricula(session: Session = Depends(get_session)) -> list[dict]:
    curricula = session.exec(select(Curriculum).order_by(Curriculum.created_at.desc())).all()
    return [curriculum_to_dict(session, curriculum, detailed=False) for curriculum in curricula]


@router.get("/curricula/{curriculum_id}", response_model=CurriculumRead)
def get_curriculum(curriculum_id: int, session: Session = Depends(get_session)) -> dict:
    curriculum = session.get(Curriculum, curriculum_id)
    if curriculum is None:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum_to_dict(session, curriculum)


@router.get("/tracks", response_model=list[TrackSummary])
def list_tracks(session: Session = Depends(get_session)) -> list[dict]:
    tracks = session.exec(select(Track).order_by(Track.order_index)).all()
    return [track_to_dict(session, track, include_topics=False) for track in tracks]


@router.get("/tracks/{track_id}", response_model=TrackRead)
def get_track(track_id: int, session: Session = Depends(get_session)) -> dict:
    track = session.get(Track, track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return track_to_dict(session, track)


@router.get("/topics", response_model=list[TopicRead])
def list_topics(track_id: int | None = None, session: Session = Depends(get_session)) -> list[dict]:
    statement = select(Topic).order_by(Topic.track_id, Topic.order_index)
    if track_id is not None:
        statement = statement.where(Topic.track_id == track_id)
    topics = session.exec(statement).all()
    return [topic_to_dict(session, topic) for topic in topics]


@router.get("/topics/{topic_id}", response_model=TopicRead)
def get_topic(topic_id: int, session: Session = Depends(get_session)) -> dict:
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic_to_dict(session, topic)


@router.patch("/topics/{topic_id}/state", response_model=TopicRead)
def update_topic_state(
    topic_id: int, update: TopicStateUpdate, session: Session = Depends(get_session)
) -> dict:
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    state = session.get(LearnerTopicState, topic_id)
    if state is None:
        state = LearnerTopicState(topic_id=topic_id)
        session.add(state)
    values = update.model_dump(exclude_unset=True)
    if "status" in values and values["status"] not in ALLOWED_STATUSES:
        raise HTTPException(status_code=422, detail="Unsupported topic status")
    if "confidence" in values and values["confidence"] not in ALLOWED_CONFIDENCE:
        raise HTTPException(status_code=422, detail="Unsupported confidence")
    for key, value in values.items():
        setattr(state, key, value)
    session.commit()
    return topic_to_dict(session, topic)


@router.get("/dashboard", response_model=DashboardRead)
def get_dashboard(session: Session = Depends(get_session)) -> dict:
    return build_dashboard(session)

