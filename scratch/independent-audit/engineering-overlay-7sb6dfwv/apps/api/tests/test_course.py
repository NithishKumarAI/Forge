import json
from pathlib import Path
import pytest
from sqlmodel import select
from app.models import LearnerTopicState, Topic, Track
from app.services.course import load_lesson_for_topic, mark_section, progress, search_course, sync_course_pack
from app.services.practice import start_practice
from scripts.course_builder.extract import extract_main_text
from scripts.course_builder.fetch import robots_allows
from scripts.course_builder.sources import load_manifest
from scripts.course_builder.validate import validate_lesson

ROOT=Path(__file__).resolve().parents[3]

def python_topic(session):
    track=session.exec(select(Track).where(Track.slug=="python")).first()
    return session.exec(select(Topic).where(Topic.track_id==track.id,Topic.slug=="syntax-data-types")).first()

def test_source_manifest_and_extraction():
    manifest=load_manifest(ROOT/"data"/"course-sources.json")
    assert manifest["python"][0]["base_url"].startswith("https://docs.python.org")
    assert "Useful" in extract_main_text("<nav>skip</nav><main><h1>Useful</h1></main>")
    assert not robots_allows("https://example.test/private", "User-agent: *\nDisallow: /private")

def test_static_lesson_schema_coverage_and_python_syntax():
    lesson=validate_lesson(ROOT/"content/ai-engineer/v1/python/syntax-data-types/lesson.json",ROOT/"data/course-coverage/python.json")
    assert any(s.slug=="booleans" for s in lesson.sections)

def test_missing_coverage_and_duplicate_section_rejected():
    source=json.loads((ROOT/"content/ai-engineer/v1/python/syntax-data-types/lesson.json").read_text())
    source["sections"]=source["sections"][:2]; path=ROOT/"apps/api/data/lesson-test-candidate.json"
    try:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(source))
        with pytest.raises(ValueError): validate_lesson(path,ROOT/"data/course-coverage/python.json")
        source=json.loads((ROOT/"content/ai-engineer/v1/python/syntax-data-types/lesson.json").read_text());source["sections"][1]["slug"]=source["sections"][0]["slug"];path.write_text(json.dumps(source))
        with pytest.raises(ValueError): validate_lesson(path,ROOT/"data/course-coverage/python.json")
    finally:
        path.unlink(missing_ok=True)

def test_sync_offline_progress_search_and_static_practice(session):
    topic=python_topic(session); before=session.get(LearnerTopicState,topic.id).mastery_score
    assert sync_course_pack(session)>=1
    lesson=load_lesson_for_topic(session,topic); assert lesson.sections[6].slug=="booleans"
    mark_section(session,topic,lesson.sections[0].slug,True)
    assert progress(session,topic,lesson)["completed_sections"]==1
    assert session.get(LearnerTopicState,topic.id).mastery_score==before
    assert search_course(session,"booleans",topic.id)
    _, exercises=start_practice(session,topic)
    assert len(exercises)==3 and all(e.source=="course_pack" for e in exercises)
