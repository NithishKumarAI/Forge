import json
import logging

from sqlalchemy import text
from sqlmodel import Session, select

from ..models import (ContentRevision, ContentSectionProgress, CourseExerciseBinding, CourseLesson,
                      Exercise, LessonSectionProgress, Topic, TopicContentBinding, Track, utc_now)
from ..schemas.course import StaticLesson
from .active_curriculum import get_active_curriculum
from .content_registry import bind_legacy_lessons, bound_lessons, canonical_json, load_snapshot, register_legacy_lessons

logger = logging.getLogger(__name__)


class CourseError(ValueError):
    pass


def _selected(session: Session, topic: Topic, lesson_id: int | None = None):
    rows = bound_lessons(session, topic)
    if lesson_id is not None:
        binding = session.get(TopicContentBinding, (topic.id, lesson_id))
        if binding:
            return binding, session.get(ContentRevision, lesson_id)
    if not rows:
        raise CourseError("This topic has no explicitly bound legacy static lesson; coverage is unavailable.")
    if lesson_id is None:
        return rows[0]
    found = next((row for row in rows if row[1].id == lesson_id), None)
    if found is None:
        raise CourseError("This lesson revision is not bound to this topic/curriculum.")
    return found


def load_lesson_for_topic(session: Session, topic: Topic, lesson_id: int | None = None) -> StaticLesson:
    _, revision = _selected(session, topic, lesson_id)
    lesson = StaticLesson.model_validate(load_snapshot(revision)["lesson"])
    lesson._registry_id = revision.id
    return lesson


def lesson_choices(session: Session, topic: Topic) -> list[dict]:
    return [{"content_revision_id": revision.id, "content_key": revision.content_key,
             "sha256": revision.sha256,
             "provenance": json.loads(revision.provenance_json),
             "revision": revision.revision, "title": load_snapshot(revision)["lesson"]["title"],
             "order_index": order, "coverage_note": binding.coverage_note,
             "approval_status": "published" if revision.approval_status == "candidate" else revision.approval_status}
            for order, (binding, revision) in enumerate(bound_lessons(session, topic))]


def progress(session: Session, topic: Topic, lesson: StaticLesson) -> dict:
    binding, revision = _selected(session, topic, lesson._registry_id)
    rows = {r.section_slug: r for r in session.exec(select(ContentSectionProgress).where(
        ContentSectionProgress.topic_id == topic.id, ContentSectionProgress.content_revision_id == revision.id))}
    if binding.legacy_progress_compatible:
        for row in session.exec(select(LessonSectionProgress).where(LessonSectionProgress.topic_id == topic.id)):
            rows.setdefault(row.section_slug, row)
    completed = [s.slug for s in lesson.sections if s.slug in rows and rows[s.slug].completed]
    viewed = [s for s in lesson.sections if s.slug in rows]
    return {"completed_sections": len(completed), "total_sections": len(lesson.sections),
            "percent": round(100 * len(completed) / len(lesson.sections)),
            "current_section_slug": viewed[-1].slug if viewed else lesson.sections[0].slug,
            "completed_section_slugs": completed, "content_revision_id": revision.id}


def mark_section(session: Session, topic: Topic, slug: str, complete: bool = False,
                 lesson_id: int | None = None) -> dict:
    lesson = load_lesson_for_topic(session, topic, lesson_id)
    binding, revision = _selected(session, topic, lesson._registry_id)
    if slug not in {s.slug for s in lesson.sections}:
        raise CourseError("Lesson section not found")
    row = session.get(ContentSectionProgress, (topic.id, revision.id, slug))
    now = utc_now()
    if row is None:
        legacy = session.get(LessonSectionProgress, (topic.id, slug)) if binding.legacy_progress_compatible else None
        row = ContentSectionProgress(topic_id=topic.id, content_revision_id=revision.id, section_slug=slug,
                                     first_viewed_at=legacy.first_viewed_at if legacy else now,
                                     completed=legacy.completed if legacy else False,
                                     completed_at=legacy.completed_at if legacy else None)
    row.last_viewed_at = now
    if complete:
        row.completed, row.completed_at = True, now
    session.add(row)
    session.commit()
    return progress(session, topic, lesson)


def _sync_exercise(session: Session, binding: TopicContentBinding, revision: ContentRevision, lesson: dict, item: dict) -> None:
    identity = (binding.topic_id, revision.id, item["key"])
    if session.get(CourseExerciseBinding, identity):
        return
    topic = session.get(Topic, binding.topic_id)
    content = {"key": item["key"], "hints": item.get("hints", []), "content": item["content"]}
    fields = {"curriculum_id": binding.curriculum_id, "track_id": topic.track_id, "topic_id": topic.id,
              "exercise_type": item["exercise_type"], "title": item["title"],
              "prompt_markdown": item["prompt_markdown"], "difficulty": item.get("difficulty", "working"), "source": "course_pack"}
    legacy_key = f"course-pack:{lesson['version']}:{item['key']}"
    candidates = session.exec(select(Exercise).where(Exercise.topic_id == topic.id,
                                                     Exercise.generator_version == legacy_key).order_by(Exercise.id)).all()
    exercise = None
    for candidate in candidates:
        try:
            same_content = json.loads(candidate.content_json) == content
        except (ValueError, TypeError):
            same_content = False
        if (all(getattr(candidate, key) == value for key, value in fields.items())
                and same_content
                and not session.exec(select(CourseExerciseBinding).where(CourseExerciseBinding.exercise_id == candidate.id)).first()):
            exercise = candidate
            break
    if exercise is None:
        exercise = Exercise(**fields, generator_version=f"registry:{revision.content_key}:{revision.revision}:{item['key']}",
                            validation_status="valid", content_json=canonical_json(content).decode())
        session.add(exercise)
        session.flush()
    session.add(CourseExerciseBinding(topic_id=topic.id, content_revision_id=revision.id,
                                     exercise_key=item["key"], exercise_id=exercise.id))


def current_course_exercise_ids(session: Session, topic_id: int) -> set[int]:
    revisions = [rev.id for _, rev in bound_lessons(session, session.get(Topic, topic_id))]
    return set(session.exec(select(CourseExerciseBinding.exercise_id).where(
        CourseExerciseBinding.topic_id == topic_id, CourseExerciseBinding.content_revision_id.in_(revisions))))


def sync_course_pack(session: Session) -> int:
    try:
        registered = register_legacy_lessons(session)
        bind_legacy_lessons(session, registered)
        rows = session.exec(select(TopicContentBinding, ContentRevision).join(ContentRevision)
                            .order_by(TopicContentBinding.topic_id, TopicContentBinding.order_index)).all()
        for binding, revision in rows:
            payload = load_snapshot(revision)
            lesson = payload["lesson"]
            # The single-lesson table remains readable; multi-lesson identity lives in bindings.
            if binding.order_index == 0 and not session.exec(select(CourseLesson).where(
                    CourseLesson.topic_id == binding.topic_id, CourseLesson.content_version == revision.revision)).first():
                session.add(CourseLesson(curriculum_id=binding.curriculum_id, topic_id=binding.topic_id,
                                         content_version=revision.revision, title=lesson["title"],
                                         source_path=revision.source_path, content_hash=lesson["content_hash"]))
            for item in payload["exercises"]:
                _sync_exercise(session, binding, revision, lesson, item)
        session.flush()
        rebuild_search_index(session, commit=False)
        session.commit()
        return len(registered)
    except BaseException:
        session.rollback()
        raise


def rebuild_search_index(session: Session, *, commit: bool = True) -> None:
    try:
        session.exec(text("""CREATE VIRTUAL TABLE IF NOT EXISTS course_content_fts_v2 USING fts5(
            curriculum_id UNINDEXED, topic_id UNINDEXED, content_revision_id UNINDEXED,
            content_key UNINDEXED, revision UNINDEXED, track_slug, topic_slug,
            section_slug UNINDEXED, title, body, key_points)"""))
        session.exec(text("DELETE FROM course_content_fts_v2"))
        snapshots = {}
        selected = [pair for topic in session.exec(select(Topic)) for pair in bound_lessons(session, topic)]
        for binding, revision in selected:
            if revision.id not in snapshots:
                snapshots[revision.id] = load_snapshot(revision)["lesson"]
            topic = session.get(Topic, binding.topic_id)
            track = session.get(Track, topic.track_id)
            for section in snapshots[revision.id]["sections"]:
                session.exec(text("""INSERT INTO course_content_fts_v2 VALUES
                    (:cid,:tid,:rid,:key,:rev,:tr,:to,:slug,:title,:body,:points)"""), params={
                    "cid": binding.curriculum_id, "tid": topic.id, "rid": revision.id,
                    "key": revision.content_key, "rev": revision.revision, "tr": track.slug, "to": topic.slug,
                    "slug": section["slug"], "title": section["title"], "body": section["markdown"],
                    "points": " ".join(section["key_points"])})
        if commit:
            session.commit()
    except Exception as error:
        session.rollback()
        logger.exception("Could not rebuild the curriculum-scoped course search index")
        raise CourseError("Course search index rebuild failed; see backend diagnostics") from error


def search_course(session: Session, query: str, topic_id: int | None = None) -> list[dict]:
    words = [word for word in query.split() if word.isalnum()]
    if not words:
        return []
    topic = session.get(Topic, topic_id) if topic_id is not None else None
    if topic_id is not None and topic is None:
        raise CourseError("Search topic not found")
    curriculum_id = session.get(Track, topic.track_id).curriculum_id if topic else getattr(get_active_curriculum(session), "id", None)
    if curriculum_id is None:
        return []
    try:
        rows = session.exec(text("""SELECT topic_id,track_slug,topic_slug,section_slug,title,body,key_points,
            curriculum_id,content_revision_id,content_key,revision FROM course_content_fts_v2
            WHERE course_content_fts_v2 MATCH :q AND curriculum_id=:cid
            ORDER BY CASE WHEN topic_id=:tid THEN 0 ELSE 1 END,rank,topic_id,content_revision_id LIMIT 5"""),
            params={"q": " AND ".join('"' + word + '"' for word in words), "tid": topic_id or -1, "cid": curriculum_id}).all()
    except Exception as error:
        logger.exception("Course search query failed for curriculum %s", curriculum_id)
        raise CourseError("Course search index is unavailable; see backend diagnostics") from error
    result = []
    for row in rows:
        item = dict(zip(["topic_id", "track_slug", "topic_slug", "section_slug", "title", "markdown", "key_points",
                         "curriculum_id", "content_revision_id", "content_key", "revision"], row))
        item["url"] = f"/topics/{item['topic_id']}/learn?lesson_id={item['content_revision_id']}"
        result.append(item)
    return result
