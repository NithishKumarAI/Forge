import pytest
from pydantic import ValidationError
from sqlmodel import Session

from app.models import Curriculum
from app.schemas.ai import CurriculumDraftRequest, CurriculumProposal
from app.services.active_curriculum import activate_curriculum, get_active_curriculum
from app.services.custom_curriculum import (
    CurriculumMutationError,
    confirm_draft,
    create_draft,
    update_draft,
)
from app.services.dashboard import build_dashboard
from tests.fakes import valid_proposal


def _payload() -> dict:
    return valid_proposal().model_dump()


def test_curriculum_proposal_validation() -> None:
    proposal = valid_proposal()
    assert proposal.tracks[0].topics[1].prerequisites == ["python-functions"]


def test_duplicate_topic_rejected() -> None:
    payload = _payload()
    duplicate = payload["tracks"][0]["topics"][0].copy()
    payload["tracks"][0]["topics"].append(duplicate)
    with pytest.raises(ValidationError, match="topic keys must be unique"):
        CurriculumProposal.model_validate(payload)


def test_dangling_prerequisite_rejected() -> None:
    payload = _payload()
    payload["tracks"][0]["topics"][1]["prerequisites"] = ["missing"]
    with pytest.raises(ValidationError, match="unknown prerequisites"):
        CurriculumProposal.model_validate(payload)


def test_cyclic_prerequisite_rejected() -> None:
    payload = _payload()
    payload["tracks"][0]["topics"][0]["prerequisites"] = ["fastapi"]
    with pytest.raises(ValidationError, match="contains a cycle"):
        CurriculumProposal.model_validate(payload)


def test_draft_creation_confirmation_and_immutability(session: Session) -> None:
    request = CurriculumDraftRequest(
        proposal=valid_proposal(), source_requirements="Python and FastAPI"
    )
    draft = create_draft(session, request)
    assert draft.status == "draft"
    edited_request = CurriculumDraftRequest(
        proposal=valid_proposal("Edited Backend Starter"),
        source_requirements="Python and FastAPI",
    )
    draft = update_draft(session, draft, edited_request)
    assert draft.name == "Edited Backend Starter"
    confirmed = confirm_draft(session, draft)
    assert confirmed.status == "confirmed"
    assert confirmed.confirmed_at is not None
    with pytest.raises(CurriculumMutationError, match="cannot be structurally edited"):
        update_draft(session, confirmed, edited_request)


def test_only_confirmed_curriculum_can_be_active(session: Session) -> None:
    draft = create_draft(
        session, CurriculumDraftRequest(proposal=valid_proposal(), source_requirements="")
    )
    with pytest.raises(ValueError, match="Only a confirmed"):
        activate_curriculum(session, draft)
    confirm_draft(session, draft)
    activate_curriculum(session, draft)
    assert get_active_curriculum(session).id == draft.id


def test_dashboard_respects_active_curriculum(session: Session) -> None:
    draft = create_draft(
        session,
        CurriculumDraftRequest(proposal=valid_proposal("Custom Active"), source_requirements=""),
    )
    confirm_draft(session, draft)
    activate_curriculum(session, draft)
    dashboard = build_dashboard(session)
    assert dashboard["active_curriculum"]["id"] == draft.id
    assert len(dashboard["tracks"]) == 1
    assert all(topic["track_name"] == "Foundations" for topic in dashboard["recommendations"])
