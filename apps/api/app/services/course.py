import hashlib
import json
import sqlite3
from pathlib import Path

from sqlalchemy import text
from sqlmodel import Session, select

from ..config import settings
from ..models import CourseLesson, Exercise, LessonSectionProgress, Topic, Track, utc_now
from ..schemas.course import StaticLesson


class CourseError(ValueError): pass


def lesson_path(track_slug: str, topic_slug: str) -> Path:
    if track_slug == "python" and topic_slug == "foundations":
        topic_slug = "syntax-data-types"
    return settings.course_content_path / track_slug / topic_slug / "lesson.json"


def load_lesson_for_topic(session: Session, topic: Topic) -> StaticLesson:
    track = session.get(Track, topic.track_id)
    path = lesson_path(track.slug, topic.slug)
    if not path.exists():
        raise CourseError("This topic does not have an accepted static lesson yet.")
    return StaticLesson.model_validate_json(path.read_text(encoding="utf-8"))


def progress(session: Session, topic: Topic, lesson: StaticLesson) -> dict:
    rows = {r.section_slug: r for r in session.exec(select(LessonSectionProgress).where(LessonSectionProgress.topic_id == topic.id))}
    completed = sum(bool(rows.get(s.slug) and rows[s.slug].completed) for s in lesson.sections)
    viewed = [s for s in lesson.sections if s.slug in rows]
    current = viewed[-1].slug if viewed else lesson.sections[0].slug
    return {"completed_sections": completed, "total_sections": len(lesson.sections), "percent": round(100*completed/len(lesson.sections)), "current_section_slug": current}


def mark_section(session: Session, topic: Topic, slug: str, complete: bool = False) -> dict:
    lesson = load_lesson_for_topic(session, topic)
    if slug not in {s.slug for s in lesson.sections}: raise CourseError("Lesson section not found")
    row = session.get(LessonSectionProgress, (topic.id, slug))
    now = utc_now()
    if row is None: row = LessonSectionProgress(topic_id=topic.id, section_slug=slug, first_viewed_at=now)
    row.last_viewed_at = now
    if complete: row.completed, row.completed_at = True, now
    session.add(row); session.commit()
    return progress(session, topic, lesson)


def sync_course_pack(session: Session) -> int:
    count = 0
    for path in settings.course_content_path.glob("*/*/lesson.json"):
        lesson = StaticLesson.model_validate_json(path.read_text(encoding="utf-8"))
        track = session.exec(select(Track).where(Track.slug == lesson.track_slug)).first()
        topic = session.exec(select(Topic).where(Topic.track_id == track.id, Topic.slug == lesson.topic_slug)).first() if track else None
        if not topic: continue
        existing = session.exec(select(CourseLesson).where(CourseLesson.topic_id == topic.id, CourseLesson.content_version == lesson.version)).first()
        if not existing:
            session.add(CourseLesson(curriculum_id=track.curriculum_id, topic_id=topic.id, content_version=lesson.version, title=lesson.title, source_path=str(path.relative_to(settings.course_content_path)), content_hash=lesson.content_hash))
        exercises_path = path.with_name("exercises.json")
        if exercises_path.exists():
            for item in json.loads(exercises_path.read_text(encoding="utf-8")):
                key = f"course-pack:{lesson.version}:{item['key']}"
                exists = session.exec(select(Exercise).where(Exercise.topic_id == topic.id, Exercise.generator_version == key)).first()
                if not exists:
                    session.add(Exercise(curriculum_id=track.curriculum_id, track_id=track.id, topic_id=topic.id, exercise_type=item["exercise_type"], title=item["title"], prompt_markdown=item["prompt_markdown"], difficulty=item.get("difficulty", "medium"), source="course_pack", generator_version=key, validation_status="valid", content_json=json.dumps({"key": item["key"], "hints": item.get("hints", []), "content": item["content"]})))
        count += 1
    # V2 deliberately reuses the accepted V1 foundations lesson without duplicating its canonical file.
    from .active_curriculum import get_active_curriculum
    active=get_active_curriculum(session)
    track=session.exec(select(Track).where(Track.curriculum_id==active.id,Track.slug=="python")).first() if active else None
    topic=session.exec(select(Topic).where(Topic.track_id==track.id,Topic.slug=="foundations")).first() if track else None
    alias_path=settings.course_content_path/"python"/"syntax-data-types"/"lesson.json"
    if topic and alias_path.exists():
        lesson=StaticLesson.model_validate_json(alias_path.read_text(encoding="utf-8"))
        if not session.exec(select(CourseLesson).where(CourseLesson.topic_id==topic.id,CourseLesson.content_version==lesson.version)).first():session.add(CourseLesson(curriculum_id=track.curriculum_id,topic_id=topic.id,content_version=lesson.version,title=lesson.title,source_path="python/syntax-data-types/lesson.json",content_hash=lesson.content_hash))
        for item in json.loads(alias_path.with_name("exercises.json").read_text(encoding="utf-8")):
            key=f"course-pack:{lesson.version}:{item['key']}"
            if not session.exec(select(Exercise).where(Exercise.topic_id==topic.id,Exercise.generator_version==key)).first():session.add(Exercise(curriculum_id=track.curriculum_id,track_id=track.id,topic_id=topic.id,exercise_type=item["exercise_type"],title=item["title"],prompt_markdown=item["prompt_markdown"],difficulty=item.get("difficulty","medium"),source="course_pack",generator_version=key,validation_status="valid",content_json=json.dumps({"key":item["key"],"hints":item.get("hints",[]),"content":item["content"]})))
    session.commit(); rebuild_search_index(session)
    return count


def rebuild_search_index(session: Session) -> None:
    session.exec(text("CREATE VIRTUAL TABLE IF NOT EXISTS course_content_fts USING fts5(topic_id UNINDEXED, track_slug, topic_slug, section_slug UNINDEXED, title, body, key_points)"))
    session.exec(text("DELETE FROM course_content_fts"))
    for path in settings.course_content_path.glob("*/*/lesson.json"):
        lesson = StaticLesson.model_validate_json(path.read_text(encoding="utf-8")); track = session.exec(select(Track).where(Track.slug == lesson.track_slug)).first()
        topic = session.exec(select(Topic).where(Topic.track_id == track.id, Topic.slug == lesson.topic_slug)).first() if track else None
        if topic:
            for sec in lesson.sections:
                session.exec(text("INSERT INTO course_content_fts VALUES (:tid,:tr,:to,:slug,:title,:body,:keys)"), params={"tid": topic.id,"tr":lesson.track_slug,"to":lesson.topic_slug,"slug":sec.slug,"title":sec.title,"body":sec.markdown,"keys":" ".join(sec.key_points)})
    session.commit()


def search_course(session: Session, query: str, topic_id: int | None = None) -> list[dict]:
    cleaned = " ".join(word for word in query.replace('"',' ').split() if word.isalnum())
    if not cleaned: return []
    try:
        rows = session.exec(text("SELECT topic_id,track_slug,topic_slug,section_slug,title,body,key_points FROM course_content_fts WHERE course_content_fts MATCH :q ORDER BY CASE WHEN topic_id=:tid THEN 0 ELSE 1 END, rank LIMIT 5"), params={"q": cleaned, "tid": topic_id or -1}).all()
    except Exception:
        return []
    return [dict(zip(["topic_id","track_slug","topic_slug","section_slug","title","markdown","key_points"], row)) for row in rows]
