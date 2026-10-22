import json
from datetime import datetime,timedelta,timezone
import pytest
from sqlmodel import select
from app import models as m
from app.schemas.assessment import AssessmentSubmission
from app.services import assessment as a
from app.services.assessment_pool import candidates
from app.services.mastery import mastery_breakdown
from tests.assessment_fixtures import item,publish,topic

def answer(session,row,answer="a",source="",now=None):
    selected=session.get(m.AssessmentSelection,row["id"])
    return a.submit(session,selected,AssessmentSubmission(content_sha256=row["content_sha256"],answer=answer,source=source),now=now)

def test_pool_absence_no_generation_or_rows(session):
    with pytest.raises(ValueError,match="No approved questions"):a.start(session,topic(session))
    assert not session.exec(select(m.AssessmentSelection)).all()

def test_frozen_selection_resume_deduplicate_and_stale_hash(session):
    t=publish(session,[item()]);first=a.start(session,t)
    assert a.start(session,t)["id"]==first["id"] and "correct" not in first["contract"]
    selected=session.get(m.AssessmentSelection,first["id"])
    with pytest.raises(ValueError,match="Stale"):a.submit(session,selected,AssessmentSubmission(content_sha256="0"*64,answer="a"))
    result=answer(session,first);assert result["result"]["score"]==100
    assert answer(session,first)["id"]==first["id"]
    assert len(session.exec(select(m.Attempt)).all())==1
    second=a.start(session,t);answer(session,second)
    assert len(session.exec(select(m.Attempt)).all())==2
    assert len(session.exec(select(m.MasteryEvidenceEvent)).all())==1
    assert session.get(m.LearnerTopicState,t.id).mastery_score==79

def test_reflection_has_no_score_evidence_or_mastery(session):
    t=publish(session,[item(kind="reflection")]);selected=a.start(session,t)
    result=answer(session,selected,"I would explain my reasoning.")
    assert result["status"]=="reflection" and result["result"]["score"] is None
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    assert session.get(m.LearnerTopicState,t.id).mastery_score==0

def test_hint_reveal_and_transfer_exposure_exclusion(session):
    t=publish(session,[item(kind="python",purposes=["practice","transfer"])])
    assert len(candidates(session,t,"transfer"))==1
    selected=a.start(session,t);row=session.get(m.AssessmentSelection,selected["id"])
    assert a.hint(session,row)["index"]==1
    result=a.reveal(session,row);assert result["score"] is None
    assert candidates(session,t,"transfer")==[]
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()

def test_coding_requires_real_execution_and_mcqs_do_not_unlock_transfer(session):
    t=publish(session,[item("a-choice"),item("b-choice")])
    answer(session,a.start(session,t));answer(session,a.start(session,t))
    assert not mastery_breakdown(session,t.id)["transfer_eligible"]
    with pytest.raises(ValueError,match="independent"):a.start(session,t,"transfer")

def test_full_static_practice_transfer_recall_and_weak_recall(session):
    variants=[item("a-code",kind="python"),item("b-code",kind="python"),item("c-transfer",kind="python",purposes=["transfer"]),item("d-recall",kind="python",purposes=["recall"])]
    t=publish(session,variants);now=datetime.now(timezone.utc)
    answer(session,a.start(session,t),source="def solve(x):\n    return x+1",now=now)
    answer(session,a.start(session,t),source="def solve(x):\n    return x+1",now=now)
    assert mastery_breakdown(session,t.id)["transfer_eligible"]
    transfer=a.start(session,t,"transfer");answer(session,transfer,source="def solve(x):\n    return x+1",now=now)
    assert session.get(m.LearnerTopicState,t.id).mastery_score==89
    with pytest.raises(ValueError,match="exhausted"):a.start(session,t,"transfer")
    with pytest.raises(ValueError):a.start(session,t,"recall",now=now+timedelta(hours=23))
    state=session.get(m.ReviewState,t.id);state.due_at=now+timedelta(hours=24);session.add(state);session.commit()
    recall=a.start(session,t,"recall",now=now+timedelta(hours=25));answer(session,recall,source="def solve(x):\n    return x+1",now=now+timedelta(hours=25))
    assert session.get(m.LearnerTopicState,t.id).mastery_score>=90
    state=session.get(m.ReviewState,t.id);state.due_at=now+timedelta(days=3);session.add(state);session.commit()
    recall=a.start(session,t,"recall",now=now+timedelta(days=3));answer(session,recall,source="def solve(x):\n    return 900",now=now+timedelta(days=3))
    assert session.get(m.LearnerTopicState,t.id).mastery_score<90
    assert len(session.exec(select(m.ReviewEvent)).all())==2

def test_legacy_questions_remain_unverified(session):
    from app.services.course import sync_course_pack
    sync_course_pack(session);t=topic(session)
    row=a.start(session,t)
    assert row["approval"]=="legacy_unverified"
    if row["kind"]=="single_choice":answer(session,row,list(row["contract"]["choices"])[0])
    else:answer(session,row,"Reflection")
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_partial_coding_score_cannot_create_passing_evidence(session):
    selected=item(kind="python")
    selected.contract["tests"]=[{"name":"case-"+str(n),"args":[n],"expected":n+1} for n in range(5)]
    t=publish(session,[selected]);row=a.start(session,t)
    result=answer(session,row,source="def solve(x):\n    return x+1 if x<4 else -1")
    assert result["result"]["score"]==80 and not result["result"]["passed"]
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    assert session.get(m.LearnerTopicState,t.id).mastery_score==0


def test_revealed_recall_needs_a_delay_before_same_variant_can_be_used(session):
    t=publish(session,[item(kind="python",purposes=["recall"])])
    now=datetime.now(timezone.utc)
    session.add(m.ReviewState(topic_id=t.id,due_at=now-timedelta(hours=1)));session.commit()
    row=a.start(session,t,"recall",now=now)
    a.reveal(session,session.get(m.AssessmentSelection,row["id"]))
    with pytest.raises(ValueError):a.start(session,t,"recall",now=now+timedelta(minutes=1))
    delayed=a.start(session,t,"recall",now=now+timedelta(hours=25))
    assert delayed["id"]!=row["id"] and not delayed["assisted"]
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_scoring_failure_rolls_back_attempt_credit_and_projection(session,monkeypatch):
    from app.services import mastery
    t=publish(session,[item()]);row=a.start(session,t)
    def fail(*args,**kwargs):raise RuntimeError("Synthetic projection interruption")
    monkeypatch.setattr(mastery,"recalculate_topic",fail)
    with pytest.raises(RuntimeError,match="interruption"):answer(session,row)
    session.rollback()
    assert session.get(m.AssessmentSelection,row["id"]).status=="open"
    assert not session.exec(select(m.Attempt)).all()
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    assert not session.exec(select(m.EvidenceCredit)).all()
    assert session.get(m.LearnerTopicState,t.id).mastery_score==0


def test_approved_bundle_availability_drives_navigation_without_fake_lessons(session):
    from app.services.editions import topic_metadata
    t=publish(session,[item()]);data=topic_metadata(session,t)["availability"]
    assert data["lesson_count"]==0 and data["lesson_status"]=="planned"
    assert data["assessment_item_count"]==1 and data["approved_practice_available"]
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_historical_generated_exercise_is_never_silently_reapproved(session):
    t=topic(session);track=session.get(m.Track,t.track_id)
    legacy=m.Exercise(curriculum_id=1,track_id=track.id,topic_id=t.id,exercise_type="multiple_choice",title="Old generated exercise",
        prompt_markdown="A saved model-era question",difficulty="working",source="gemini",validation_status="valid",content_json='{"content":{"choices":["A","B"],"correct_index":0},"hints":[]}')
    session.add(legacy);session.commit();session.refresh(legacy);before=legacy.model_dump()
    with pytest.raises(ValueError,match="No approved questions"):a.start(session,t)
    assert session.get(m.Exercise,legacy.id).model_dump()==before
    assert not session.exec(select(m.Attempt)).all() and not session.exec(select(m.MasteryEvidenceEvent)).all()
