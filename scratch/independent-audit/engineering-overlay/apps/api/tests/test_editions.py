"""All reviews here are synthetic fixtures, never real curriculum/content approvals."""
import copy
import json
from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, select, create_engine
from sqlalchemy import text
from app import models as m
from app.database import get_session
from app.migrations import run_migrations
from app.services import editions as e
from app.services.custom_curriculum import create_draft, update_draft, confirm_draft, proposal_from_curriculum
from app.services.active_curriculum import get_active_curriculum, activate_curriculum
from app.services.content_registry import digest, _validate_identity, load_snapshot
from app.services.content_publication import _resolve_target, publish_release
from app.schemas.editions import SUBJECT_KEYS, PlacementScope, EditionConfirmation
from app.schemas.publication import ReleaseTarget
from app.schemas.ai import CurriculumDraftRequest
from tests.test_content_publication import lesson_candidate, approved_package

ROOT = Path(__file__).resolve().parents[3]


def review_request(session, curriculum):
    overview = e.overview(session, curriculum_id=curriculum.id)
    return EditionConfirmation(graph_sha256=overview["binding"]["graph_sha256"],scope_sha256=overview["scope_sha256"],
        reviewer="TEST ONLY curriculum reviewer",scope_reviewed=True,missing_content_acknowledged=True)


def confirm(session, curriculum):
    return confirm_draft(session,curriculum,edition_review=review_request(session,curriculum))


def test_scope_nine_subjects_levels_unique_graph_and_outcomes():
    scope = e.scope()
    assert len(scope.topics) == 157 and len(scope.proposal().tracks) == 9
    assert len({t.key for t in scope.topics}) == 157
    assert {(t.subject_key,t.level) for t in scope.topics} == {(s,n) for s in SUBJECT_KEYS for n in (1,2,3)}
    assert all(t.learning_outcomes and t.coverage_requirements and t.content_key.startswith("forge/placement-foundations/") for t in scope.topics)
    for mode in ("missing_level", "duplicate", "dangling", "cycle"):
        bad=scope.model_dump(mode="json")
        if mode=="missing_level":bad["topics"]=[t for t in bad["topics"] if not(t["subject_key"]=="python" and t["level"]==3)]
        if mode=="duplicate":bad["topics"][1]["key"]=bad["topics"][0]["key"]
        if mode=="dangling":bad["topics"][0]["prerequisites"]=["missing-topic"]
        if mode=="cycle":bad["topics"][0]["prerequisites"]=[bad["topics"][1]["key"]];bad["topics"][1]["prerequisites"]=[bad["topics"][0]["key"]]
        with pytest.raises(ValueError):PlacementScope.model_validate(bad)


def test_editions_independent_preview_reads_and_preference_do_not_activate(session):
    from app.services.curriculum import seed_default_curriculum
    second=seed_default_curriculum(session,ROOT/"data/default-interview-curriculum-v2.json")
    activate_curriculum(session,second)
    before=session.get(m.AppSetting,"active_curriculum_id").value
    for _ in range(2):
        data=e.overview(session)
        assert data["binding"] is None and all(t["availability"]["lesson_status"]=="planned" for s in data["subjects"] for t in s["topics"])
    assert not session.exec(select(m.EditionCurriculumBinding)).all()
    assert e.index(session)["selected_edition_key"] is None
    e.select_edition(session,"placement-foundations")
    assert session.get(m.AppSetting,"active_curriculum_id").value == before
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
    with pytest.raises(ValueError):e.select_edition(session,"advanced-engineering")
    assert e.overview(session,"advanced-engineering")["subjects"] == []
    assert second.version == 2 and not session.get(m.EditionCurriculumBinding,second.id)


def test_deterministic_idempotent_draft_and_explicit_review_activation(session):
    active=get_active_curriculum(session).id
    first=e.create_placement_draft(session)
    assert first.source_type=="custom" and first.status=="draft"
    assert e.create_placement_draft(session).id==first.id
    assert get_active_curriculum(session).id==active
    placements=session.exec(select(m.TopicPlacement)).all()
    assert len(placements)==157
    assert {p.level for p in placements}=={1,2,3}
    with pytest.raises(ValueError):confirm_draft(session,first)
    with pytest.raises(ValueError):activate_curriculum(session,first)
    with pytest.raises(ValueError):
        confirm_draft(session,first,edition_review={**review_request(session,first).model_dump(),"scope_reviewed":False})
    confirm(session,first)
    assert first.status=="confirmed" and get_active_curriculum(session).id==active
    assert e.create_placement_draft(session).id==first.id
    e.activate_edition_curriculum(session,first)
    assert get_active_curriculum(session).id==first.id
    assert session.get(m.AppSetting,e.EDITION_PREFERENCE).value=="placement-foundations"
    with pytest.raises(ValueError):update_draft(session,first,CurriculumDraftRequest(proposal=proposal_from_curriculum(session,first)))
    with pytest.raises(Exception,match="immutable"):
        session.exec(text("UPDATE topic SET name='Changed' WHERE id=:id"),params={"id":placements[0].topic_id});session.commit()
    session.rollback()
    assert not session.exec(select(m.Attempt)).all() and not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_draft_edits_reconcile_only_draft_placements_and_invalidate_stale_review(session):
    curriculum=e.create_placement_draft(session)
    old_review=review_request(session,curriculum)
    proposal=proposal_from_curriculum(session,curriculum)
    proposal.tracks[0].topics[0].name="Working with whole numbers"
    proposal.tracks[0].topics.reverse()
    updated=update_draft(session,curriculum,CurriculumDraftRequest(proposal=proposal))
    assert len(session.exec(select(m.TopicPlacement)).all())==157
    assert all(session.get(m.Topic,p.topic_id) for p in session.exec(select(m.TopicPlacement)))
    with pytest.raises(ValueError,match="changed after review"):
        confirm_draft(session,updated,edition_review=old_review)
    bad=proposal_from_curriculum(session,updated);bad.tracks[0].topics.pop()
    with pytest.raises(ValueError,match="retain all"):
        update_draft(session,updated,CurriculumDraftRequest(proposal=bad))
    assert len(session.exec(select(m.TopicPlacement)).all())==157
    assert session.get(m.EditionCurriculumBinding,updated.id).reviewed_at is None
    confirm(session,updated)


def test_draft_with_activity_is_not_deleted_by_edit(session):
    curriculum=e.create_placement_draft(session)
    placement=session.exec(select(m.TopicPlacement)).first()
    state=session.get(m.LearnerTopicState,placement.topic_id);state.mastery_score=12;session.add(state);session.commit()
    proposal=proposal_from_curriculum(session,curriculum)
    with pytest.raises(ValueError,match="learner activity"):
        update_draft(session,curriculum,CurriculumDraftRequest(proposal=proposal))
    assert session.get(m.LearnerTopicState,placement.topic_id).mastery_score==12


def test_placements_reject_wrong_owner_subject_level_and_duplicates(session):
    curriculum=e.create_placement_draft(session)
    first=session.exec(select(m.TopicPlacement)).first()
    for column,value in (("level",4),("level",1.5),("subject_key","unknown"),("subject_key","python"),("curriculum_id",1)):
        with pytest.raises(Exception,match="Invalid|immutable"):
            session.exec(text(f"UPDATE topicplacement SET {column}=:value WHERE topic_id=:id"),params={"value":value,"id":first.topic_id});session.commit()
        session.rollback()
    legacy=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==1)).first()
    with pytest.raises(Exception,match="same curriculum"):
        session.add(m.TopicPrerequisite(topic_id=first.topic_id,prerequisite_topic_id=legacy.id));session.commit()
    session.rollback()
    with pytest.raises(Exception,match="UNIQUE"):
        session.exec(text("INSERT INTO topicplacement SELECT * FROM topicplacement WHERE topic_id=:id"),params={"id":first.topic_id})
        session.commit()
    session.rollback()


def test_real_startup_reuses_scoped_draft_and_preserves_selection(session, monkeypatch):
    import app.main as main
    engine=session.get_bind()
    active=get_active_curriculum(session).id
    draft=e.create_placement_draft(session)
    draft_id=draft.id
    monkeypatch.setattr(main,"engine",engine)
    monkeypatch.setattr(main,"create_db_and_tables",lambda:run_migrations(engine))
    app=main.create_app()
    def sessions():
        with Session(engine) as current:yield current
    app.dependency_overrides[get_session]=sessions
    for _ in range(2):
        with TestClient(app) as client:
            assert client.get('/health').status_code==200
            result=client.post('/api/editions/placement-foundations/draft')
            assert result.status_code==200,result.text
            assert result.json()['binding']['curriculum_id']==draft_id
            assert result.json()['binding']['status']=='draft'
            assert result.json()['active_curriculum_id']==active
    session.expire_all()
    assert len(session.exec(select(m.EditionCurriculumBinding)).all())==1
    assert len(session.exec(select(m.TopicPlacement)).all())==157
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


def test_legacy_availability_and_phase1_progress_are_not_relabelled(session):
    from app.services.course import sync_course_pack,load_lesson_for_topic,mark_section
    from app.services.arena import sync_problem_bank
    sync_course_pack(session);sync_problem_bank(session)
    topic=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==1,m.Track.slug=="python",m.Topic.slug=="syntax-data-types")).first()
    lesson=load_lesson_for_topic(session,topic)
    mark_section(session,topic,lesson.sections[0].slug,True)
    state=session.get(m.LearnerTopicState,topic.id).model_dump()
    before=[r.model_dump() for r in session.exec(select(m.ContentSectionProgress))]
    data=e.topic_metadata(session,topic)
    assert data["placement"] is None and data["availability"]["lesson_status"]=="legacy"
    assert not data["availability"]["approved_practice_available"]
    assert data["availability"]["completed_sections"]==1 and data["availability"]["practice_available"]
    e.overview(session);e.create_placement_draft(session);e.overview(session)
    assert [r.model_dump() for r in session.exec(select(m.ContentSectionProgress))]==before
    assert session.get(m.LearnerTopicState,topic.id).model_dump()==state
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()


@pytest.mark.parametrize("mutation",["subject","topic","edition","traversal"])
def test_new_namespace_is_strict_and_legacy_unchanged(mutation):
    candidate=lesson_candidate();legacy=candidate.content_key
    _validate_identity(legacy,candidate.revision,candidate.content_type,candidate.payload)
    lesson=candidate.payload["lesson"];lesson["curriculum_key"]="placement-foundations"
    key=f"forge/placement-foundations/python/{lesson['topic_slug']}"
    _validate_identity(key,candidate.revision,candidate.content_type,candidate.payload)
    if mutation=="subject":key=key.replace('/python/','/unknown/')
    if mutation=="topic":key+="-other"
    if mutation=="edition":lesson["curriculum_key"]="advanced-engineering"
    if mutation=="traversal":lesson["topic_slug"]="../escape"
    with pytest.raises(ValueError):_validate_identity(key,candidate.revision,candidate.content_type,candidate.payload)


def test_publication_custom_requires_reviewed_confirmed_exact_graph_and_legacy_archives_work(session):
    curriculum=e.create_placement_draft(session)
    item=e.scope().topics[0]
    overview=e.overview(session)
    target={"source_type":"custom","curriculum_id":curriculum.id,"curriculum_name":curriculum.name,"curriculum_version":curriculum.version,
        "graph_sha256":overview["binding"]["graph_sha256"],"topic":item.subject_key+"/"+item.key,"order_index":0}
    with pytest.raises(ValueError):_resolve_target(session,ReleaseTarget.model_validate(target))
    confirm(session,curriculum)
    assert _resolve_target(session,ReleaseTarget.model_validate(target))[0].id==curriculum.id
    with pytest.raises(ValueError):_resolve_target(session,ReleaseTarget.model_validate({**target,"graph_sha256":"0"*64}))
    with pytest.raises(ValueError):_resolve_target(session,ReleaseTarget.model_validate({**target,"curriculum_id":None}))
    # Complete synthetic content review passes the same Phase 2 gates in the new namespace.
    candidate=lesson_candidate();lesson=candidate.payload["lesson"]
    lesson.update(curriculum_key="placement-foundations",track_slug=item.subject_key,topic_slug=item.key)
    candidate.content_key=item.content_key
    lesson["content_hash"]=digest({k:v for k,v in lesson.items() if k not in {"content_hash","generated_at"}})
    package=approved_package(session,candidate,"edition-publication")
    package["entries"][0]["targets"]=[target]
    publish_release(session,package)
    topic=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id,m.Topic.slug==item.key)).one()
    assert e.availability(session,topic)["lesson_status"]=="approved"
    assert e.availability(session,topic)["approved_practice_available"]
    legacy_target=approved_package(session)["entries"][0]["targets"][0]
    assert "source_type" not in legacy_target
    assert _resolve_target(session,ReleaseTarget.model_validate(legacy_target))[0].source_type=="default"


def test_arbitrary_custom_confirmed_curriculum_is_not_authorized(session):
    proposal=e.scope().proposal();proposal.name="Unreviewed custom copy"
    curriculum=create_draft(session,CurriculumDraftRequest(proposal=proposal));confirm_draft(session,curriculum)
    from app.services.content_registry import database_graph
    item=e.scope().topics[0]
    target=ReleaseTarget(source_type="custom",curriculum_id=curriculum.id,curriculum_name=curriculum.name,curriculum_version=curriculum.version,
        graph_sha256=digest(database_graph(session,curriculum)),topic=item.subject_key+"/"+item.key)
    with pytest.raises(ValueError,match="reviewed confirmed"):_resolve_target(session,target)


def test_migration_four_upgrades_three_preserving_ledger_and_backup(tmp_path):
    from app.migrations import runner
    from app.services.database_backup import restore_database_backup,verify_database_backup
    engine=create_engine('sqlite:///'+(tmp_path/'old.db').as_posix())
    with engine.begin() as connection:
        schema=json.loads(runner.v002_content_bindings.SCHEMA.read_text())
        for migration in runner.MIGRATIONS[:3]:
            if migration.version==1:
                migration.module.apply(connection)
                connection.exec_driver_sql(next(t['sql'] for t in schema if t['name']=='schemamigration'))
            else:migration.module.apply(connection)
            connection.exec_driver_sql('INSERT INTO schemamigration VALUES (?,?,?,?)',(migration.version,migration.name,migration.checksum,'2026-10-20'))
        connection.exec_driver_sql("INSERT INTO appsetting VALUES ('preserve','exact payload')")
        before=connection.exec_driver_sql('SELECT * FROM schemamigration').all()
    result=run_migrations(engine)
    assert result['applied']==[4,5,6] and verify_database_backup(Path(result['backup_path']))['schema_version']==3
    assert run_migrations(engine)['applied']==[]
    with engine.connect() as connection:
        assert connection.exec_driver_sql('SELECT * FROM schemamigration WHERE version<4').all()==before
        assert connection.exec_driver_sql("SELECT value FROM appsetting WHERE key='preserve'").scalar()=='exact payload'
    restore_database_backup(Path(result['backup_path']),tmp_path/'restored.db')
    engine.dispose()


def test_http_workflow_and_generic_confirmation_bypass_are_safe(session):
    from app.routers.editions import router
    from app.routers.curricula import router as curricula
    app=FastAPI();app.include_router(router);app.include_router(curricula)
    def sessions():yield session
    app.dependency_overrides[get_session]=sessions
    with TestClient(app) as client:
        assert client.get('/api/editions').json()['selected_edition_key'] is None
        data=client.post('/api/editions/placement-foundations/draft').json();cid=data['binding']['curriculum_id']
        assert client.post('/api/editions/placement-foundations/draft').json()['binding']['curriculum_id']==cid
        assert client.post(f'/api/curricula/{cid}/confirm').status_code==409
        assert client.post(f'/api/editions/curricula/{cid}/activate').status_code==409
        request=review_request(session,session.get(m.Curriculum,cid)).model_dump(mode='json')
        result=client.post(f'/api/editions/curricula/{cid}/confirm',json=request)
        assert result.status_code==200,result.text
        assert not result.json()['binding']['is_active']
        assert client.post(f'/api/editions/curricula/{cid}/activate').json()['binding']['is_active']
        assert client.post('/api/editions/advanced-engineering/select').status_code==409
        assert client.get('/api/editions/advanced-engineering').json()['subjects']==[]
