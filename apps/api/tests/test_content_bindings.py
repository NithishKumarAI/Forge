import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.config import REPO_ROOT, Settings, settings
from app.models import (AppSetting, ArenaAttempt, ArenaProblem, ArenaTopicBinding, ContentRevision,
                        CourseExerciseBinding, Curriculum, Exercise, LearnerTopicState, LessonSectionProgress,
                        MasteryEvidenceEvent, Topic, TopicContentBinding, Track)
from app.schemas.content_registry import LegacyBindingsManifest
from app.services.active_curriculum import activate_curriculum
from app.services.arena import resolve_arena_topic, sync_problem_bank
from app.services.content_paths import ContentPathError, safe_path
from app.services.content_registry import (RegistryError, bound_lessons, load_manifest, load_snapshot,
                                          register_legacy_lessons)
from app.services.course import (CourseError, current_course_exercise_ids, lesson_choices, load_lesson_for_topic,
                                 mark_section, progress, search_course, sync_course_pack)
from app.services.curriculum import seed_default_curriculum
from app.services.practice import start_practice


def setup_both(session):
    new = seed_default_curriculum(session, settings.curriculum_v2_path)
    activate_curriculum(session, new)
    sync_course_pack(session)
    return new


def topic_for(session, curriculum_id, key):
    track, topic = key.split("/")
    return session.exec(select(Topic).join(Track).where(Track.curriculum_id==curriculum_id,Track.slug==track,Topic.slug==topic)).one()


def test_registers_all_53_legacy_lessons_and_scoped_exercises(session):
    new = setup_both(session)
    lessons = session.exec(select(ContentRevision).where(ContentRevision.content_type=="lesson_bundle")).all()
    assert len(lessons) == 53
    assert {row.approval_status for row in lessons} == {"legacy_baseline"}
    for row in lessons:
        snapshot = load_snapshot(row)
        assert json.loads(row.provenance_json)["legacy_content_hash"] == snapshot["lesson"]["content_hash"]
    bindings = session.exec(select(TopicContentBinding)).all()
    assert len(bindings) == 100
    associations = session.exec(select(CourseExerciseBinding)).all()
    assert len(associations) == 700
    for row in associations:
        exercise = session.get(Exercise,row.exercise_id)
        topic = session.get(Topic,row.topic_id)
        track = session.get(Track,topic.track_id)
        assert (exercise.topic_id,exercise.track_id,exercise.curriculum_id) == (topic.id,track.id,track.curriculum_id)
    topic = topic_for(session,new.id,"python/control-flow")
    _, items = start_practice(session,topic,None)
    assert len(items)==3 and {item.id for item in items}.issubset(current_course_exercise_ids(session,topic.id))


def test_multi_lesson_order_and_new_reading_do_not_inherit_progress(session):
    new = setup_both(session)
    topic = topic_for(session,new.id,"python/advanced-working-python")
    choices = lesson_choices(session,topic)
    assert [row["content_key"].split("/")[-1] for row in choices] == ["iterators","generators","decorators","type-hints"]
    primary = load_lesson_for_topic(session,topic)
    secondary = load_lesson_for_topic(session,topic,choices[1]["content_revision_id"])
    old = LessonSectionProgress(topic_id=topic.id,section_slug=secondary.sections[0].slug,completed=True)
    session.add(old);session.commit()
    assert progress(session,topic,secondary)["completed_sections"]==0
    before = session.get(LearnerTopicState,topic.id).model_dump()
    mark_section(session,topic,primary.sections[0].slug,True,choices[0]["content_revision_id"])
    assert progress(session,topic,primary)["completed_sections"]==1
    assert progress(session,topic,secondary)["completed_sections"]==0
    assert session.get(LearnerTopicState,topic.id).model_dump()==before
    assert session.get(LessonSectionProgress,(topic.id,old.section_slug)).completed


def test_duplicate_section_slugs_are_revision_scoped(session):
    setup_both(session)
    curriculum = Curriculum(name="Explicit custom",version=1,description="",source_type="custom",status="confirmed")
    session.add(curriculum);session.flush()
    track=Track(curriculum_id=curriculum.id,name="Python",slug="python")
    session.add(track);session.flush()
    topic=Topic(track_id=track.id,name="Explicit pair",slug="pair")
    session.add(topic);session.flush()
    revisions=[]
    for order,key in enumerate(["debugging","functions"]):
        revision=session.exec(select(ContentRevision).where(ContentRevision.content_key==f"ai-engineer/v1/python/{key}")).one()
        revisions.append(revision)
        session.add(TopicContentBinding(curriculum_id=curriculum.id,topic_id=topic.id,content_revision_id=revision.id,order_index=order,coverage_note="Explicit synthetic binding"))
    session.commit()
    a,b=[load_lesson_for_topic(session,topic,revision.id) for revision in revisions]
    common={section.slug for section in a.sections}&{section.slug for section in b.sections}
    assert common
    slug=sorted(common)[0]
    mark_section(session,topic,slug,True,revisions[0].id)
    assert progress(session,topic,a)["completed_sections"]==1
    assert progress(session,topic,b)["completed_sections"]==0


def test_missing_coverage_and_custom_slug_collision_are_explicit(session):
    new=setup_both(session)
    with pytest.raises(CourseError,match="unavailable"):
        load_lesson_for_topic(session,topic_for(session,new.id,"python/standard-library"))
    custom=Curriculum(name="Collision",description="",version=1,source_type="custom",status="confirmed")
    session.add(custom);session.flush()
    track=Track(curriculum_id=custom.id,name="Python",slug="python")
    session.add(track);session.flush()
    topic=Topic(track_id=track.id,name="Foundations",slug="foundations")
    session.add(topic);session.commit()
    sync_course_pack(session)
    with pytest.raises(CourseError,match="unavailable"):
        load_lesson_for_topic(session,topic)
    assert not current_course_exercise_ids(session,topic.id)
    activate_curriculum(session,custom)
    assert search_course(session,"booleans")==[]


def test_snapshot_integrity_and_source_mutation(session,tmp_path,monkeypatch):
    import shutil
    setup_both(session)
    row=session.exec(select(ContentRevision).where(ContentRevision.content_type=="lesson_bundle")).first()
    original=load_snapshot(row)
    copied=tmp_path/'copied-content'
    shutil.copytree(settings.course_content_path,copied)
    monkeypatch.setattr(settings,"course_content_path",copied)
    path=copied/row.source_path
    changed=json.loads(path.read_text());changed["description"]+=" changed without revision"
    path.write_text(json.dumps(changed),encoding="utf-8")
    assert load_snapshot(row)==original
    with pytest.raises(RegistryError,match="without a new revision"):
        sync_course_pack(session)
    row=session.get(ContentRevision,row.id)
    target=settings.content_snapshot_path/row.snapshot_path
    target.write_bytes(b'{}')
    with pytest.raises(RegistryError,match="digest mismatch"):
        load_snapshot(row)


@pytest.mark.parametrize("relative", ["../outside.json","a/../../x","/absolute","C:/absolute","a\\b","a//b","./x"])
def test_unsafe_paths_rejected(tmp_path,relative):
    with pytest.raises(ContentPathError):
        safe_path(tmp_path,relative,must_exist=False)


def test_link_and_invalid_digest_rejected(session,tmp_path,monkeypatch):
    setup_both(session)
    original=Path.is_symlink
    monkeypatch.setattr(Path,"is_symlink",lambda path: path.name=="linked" or original(path))
    with pytest.raises(ContentPathError,match="Symlink"):
        safe_path(tmp_path,"linked/lesson.json",must_exist=False)
    row=session.exec(select(ContentRevision)).first()
    forged=ContentRevision(**{**row.model_dump(),"sha256":"not-a-digest"})
    with pytest.raises(RegistryError,match="identity"):
        load_snapshot(forged)


def test_ambiguous_missing_and_changed_bindings_rejected(session,tmp_path,monkeypatch):
    setup_both(session)
    raw=json.loads(settings.content_bindings_path.read_text())
    duplicate=copy.deepcopy(raw)
    duplicate["curricula"][0]["topics"].append(duplicate["curricula"][0]["topics"][0])
    with pytest.raises(ValueError,match="ambiguous"):
        LegacyBindingsManifest.model_validate(duplicate)
    missing=copy.deepcopy(raw)
    missing["curricula"][0]["topics"][0]["lessons"][0]["content_key"]="ai-engineer/v1/missing/lesson"
    manifest=tmp_path/'bindings.json';manifest.write_text(json.dumps(missing),encoding="utf-8")
    monkeypatch.setattr(settings,"content_bindings_path",manifest)
    with pytest.raises(RegistryError,match="missing content"):
        sync_course_pack(session)


def test_database_enforces_immutable_content_and_binding_ownership(session):
    new=setup_both(session)
    row=session.exec(select(ContentRevision)).first()
    with pytest.raises(IntegrityError,match="immutable"):
        session.exec(text("UPDATE contentrevision SET sha256='changed' WHERE id=:id"),params={"id":row.id})
    session.rollback()
    old=session.exec(select(Curriculum).where(Curriculum.version==1)).one()
    topic=topic_for(session,new.id,"python/foundations")
    with pytest.raises(IntegrityError,match="another curriculum"):
        session.add(TopicContentBinding(curriculum_id=old.id,topic_id=topic.id,content_revision_id=row.id,order_index=99,coverage_note="wrong owner"))
        session.flush()
    session.rollback()


def test_fts_scoping_revision_links_and_diagnosable_failure(session,caplog):
    new=setup_both(session)
    old=session.exec(select(Curriculum).where(Curriculum.version==1)).one()
    for curriculum in [old,new]:
        activate_curriculum(session,curriculum)
        matches=search_course(session,"booleans")
        assert matches and {row["curriculum_id"] for row in matches}=={curriculum.id}
        assert all(f"lesson_id={row['content_revision_id']}" in row["url"] for row in matches)
    session.exec(text("DROP TABLE course_content_fts_v2"));session.commit()
    with pytest.raises(CourseError,match="diagnostics"):
        search_course(session,"booleans")
    assert "Course search query failed" in caplog.text


def test_all_17_arena_misses_resolved_and_repeat_preserves_history(session):
    new=setup_both(session)
    sync_problem_bank(session)
    active=session.exec(select(ArenaTopicBinding).where(ArenaTopicBinding.curriculum_id==new.id)).all()
    assert len(active)==110 and all(row.topic_id for row in active)
    diagnosed=[row for row in active if "dsa/stacks ->" in row.rationale or any(source+" ->" in row.rationale for source in ["sql-cs/subqueries","sql-cs/ctes","sql-cs/group-by"])]
    assert len(diagnosed)==17
    keys={row.key for row in session.exec(select(ArenaProblem))}
    problem_key=sorted(keys)[0]
    attempt=ArenaAttempt(problem_key=problem_key,track="python",submitted_source="historical source",passed=True,score=100)
    event=MasteryEvidenceEvent(topic_id=active[0].topic_id,event_type="arena",score=100,evidence_weight=1,metadata_json='{"historical":true}')
    session.add_all([attempt,event]);session.commit()
    session.refresh(attempt);session.refresh(event)
    before=(attempt.model_dump(),event.model_dump())
    sync_problem_bank(session);sync_course_pack(session)
    session.refresh(attempt);session.refresh(event)
    assert (attempt.model_dump(),event.model_dump())==before
    assert {row.key for row in session.exec(select(ArenaProblem))}==keys
    assert len(session.exec(select(ContentRevision)).all())==163
    assert len(session.exec(select(CourseExerciseBinding)).all())==700
    # Selection uses the current curriculum's binding, not a stale global mapped_topic_id.
    old=session.exec(select(Curriculum).where(Curriculum.version==1)).one()
    activate_curriculum(session,old)
    assert resolve_arena_topic(session,"python-bob") is None
    activate_curriculum(session,new)
    assert resolve_arena_topic(session,"python-bob") is not None


def test_sample_environment_paths_are_cwd_independent(tmp_path,monkeypatch):
    from dotenv import dotenv_values
    sample={key:value for key,value in dotenv_values(REPO_ROOT/'apps/api/.env.example').items() if value is not None}
    for directory in [REPO_ROOT/'apps/api',tmp_path]:
        monkeypatch.chdir(directory)
        value=Settings(sample)
        for attribute in ["curriculum_path","curriculum_v2_path","course_content_path","course_sources_path","curriculum_migration_path","content_bindings_path","problem_bank_path"]:
            path=getattr(value,attribute)
            assert path.exists() and path.is_relative_to(REPO_ROOT)
        assert str(REPO_ROOT/'apps/api/data/forge.db').replace('\\','/') in value.database_url
    absolute=tmp_path/'explicit-root'
    assert Settings({"FORGE_COURSE_CONTENT_PATH":str(absolute)}).course_content_path==absolute
    with pytest.raises(ValueError,match="escapes"):
        Settings({"FORGE_COURSE_CONTENT_PATH":"../outside"})


def test_additive_multi_lesson_api_and_revision_progress(session):
    from app.main import create_app
    from app.database import get_session
    new=setup_both(session)
    topic=topic_for(session,new.id,"python/advanced-working-python")
    app=create_app();app.dependency_overrides[get_session]=lambda:session
    client=TestClient(app)
    data=client.get(f"/api/course/topics/{topic.id}").json()
    assert data["lesson"] and data["progress"] and len(data["lessons"])==4
    secondary=data["lessons"][1]["content_revision_id"]
    selected=client.get(f"/api/course/topics/{topic.id}?lesson_id={secondary}").json()
    slug=selected["lesson"]["sections"][0]["slug"]
    saved=client.post(f"/api/course/topics/{topic.id}/sections/{slug}/complete?lesson_id={secondary}")
    assert saved.json()["completed_sections"]==1
    assert client.get(f"/api/course/topics/{topic.id}").json()["progress"]["completed_sections"]==0
    other=topic_for(session,new.id,"python/strings")
    assert client.get(f"/api/course/topics/{other.id}?lesson_id={secondary}").status_code==404
