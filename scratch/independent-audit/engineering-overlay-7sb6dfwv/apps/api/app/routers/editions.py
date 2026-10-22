from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..models import Curriculum, Topic
from ..schemas.editions import EditionConfirmation, EditionOverviewRead, EditionIndexRead
from ..services import editions
from ..services.custom_curriculum import confirm_draft

router = APIRouter(prefix="/api/editions", tags=["editions"])


def _call(function, *args, **kwargs):
    try: return function(*args, **kwargs)
    except ValueError as error: raise HTTPException(409, str(error)) from error


def _curriculum(session, curriculum_id):
    curriculum = session.get(Curriculum, curriculum_id)
    if curriculum is None: raise HTTPException(404, "Curriculum not found")
    return curriculum


@router.get("", response_model=EditionIndexRead)
def index(session: Session = Depends(get_session)):
    return editions.index(session)


@router.get("/topics/{topic_id}")
def topic_metadata(topic_id: int, session: Session = Depends(get_session)):
    topic = session.get(Topic, topic_id)
    if topic is None: raise HTTPException(404, "Topic not found")
    return _call(editions.topic_metadata, session, topic)


@router.get("/curricula/{curriculum_id}/review", response_model=EditionOverviewRead)
def review(curriculum_id: int, session: Session = Depends(get_session)):
    _curriculum(session, curriculum_id)
    return _call(editions.overview, session, curriculum_id=curriculum_id)


@router.post("/curricula/{curriculum_id}/confirm", response_model=EditionOverviewRead)
def confirm(curriculum_id: int, request: EditionConfirmation, session: Session = Depends(get_session)):
    curriculum = _curriculum(session, curriculum_id)
    _call(editions.overview, session, curriculum_id=curriculum_id)
    _call(confirm_draft, session, curriculum, edition_review=request)
    return editions.overview(session, curriculum_id=curriculum_id)


@router.post("/curricula/{curriculum_id}/activate", response_model=EditionOverviewRead)
def activate(curriculum_id: int, session: Session = Depends(get_session)):
    _call(editions.activate_edition_curriculum, session, _curriculum(session, curriculum_id))
    return editions.overview(session, curriculum_id=curriculum_id)


@router.get("/{edition_key}", response_model=EditionOverviewRead)
def overview(edition_key: str, curriculum_id: int | None = None, session: Session = Depends(get_session)):
    return _call(editions.overview, session, edition_key, curriculum_id)


@router.post("/{edition_key}/select", response_model=EditionIndexRead)
def select(edition_key: str, session: Session = Depends(get_session)):
    return _call(editions.select_edition, session, edition_key)


@router.post("/placement-foundations/draft", response_model=EditionOverviewRead)
def create_draft(session: Session = Depends(get_session)):
    curriculum = _call(editions.create_placement_draft, session)
    return editions.overview(session, curriculum_id=curriculum.id)
