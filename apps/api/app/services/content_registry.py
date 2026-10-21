"""Immutable legacy content. Digest = SHA-256 of UTF-8 sorted, compact JSON (no newline).

Lesson snapshots contain BOTH original lesson and exercises, including legacy hashes.
Arena snapshots preserve all raw provenance fields even if the public schema omits them.
Registration is not editorial approval. A changed (key, revision) requires a new revision.
"""
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from sqlmodel import Session, select

from ..config import settings
from ..models import ContentRevision, Curriculum, Topic, TopicContentBinding, TopicPrerequisite, Track
from ..schemas.arena import CodingProblem
from ..schemas.content_registry import LegacyBindingsManifest, LegacyExercise
from ..schemas.course import StaticLesson
from .content_paths import safe_path, reject_links, validate_relative_path


class RegistryError(ValueError):
    pass


def canonical_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _validate_payload(content_type: str, payload: dict) -> None:
    if content_type == "lesson_bundle":
        StaticLesson.model_validate(payload["lesson"])
        keys = []
        for item in payload["exercises"]:
            LegacyExercise.model_validate(item)
            keys.append(item["key"])
        if not keys or len(keys) != len(set(keys)):
            raise RegistryError("Lesson bundle must contain unique exercise identities")
    elif content_type == "arena_problem":
        CodingProblem.model_validate(payload["problem"])
    elif content_type == "assessment_bundle":
        from ..schemas.assessment import AssessmentBundle
        AssessmentBundle.model_validate(payload["assessment"])
    else:
        raise RegistryError(f"Unsupported content type: {content_type}")


def _validate_identity(key: str, revision: str, content_type: str, payload: dict) -> None:
    if content_type == "assessment_bundle":
        from ..schemas.assessment import AssessmentBundle
        from ..schemas.editions import SUBJECT_KEYS
        bundle=AssessmentBundle.model_validate(payload["assessment"])
        if key != bundle.key or revision != bundle.version or any(
            item.subject not in SUBJECT_KEYS or item.level>3 or key != f"assessment/placement-foundations/{item.subject}/{item.topic}"
            for item in bundle.items):
            raise RegistryError("Assessment namespace differs from immutable subject/topic identity")
        validate_relative_path(key)
        return
    if content_type == "lesson_bundle":
        content = payload["lesson"]
        expected = f"ai-engineer/v1/{content['track_slug']}/{content['topic_slug']}"
        if key.startswith("forge/"):
            import re
            from ..schemas.editions import SUBJECT_KEYS
            if (content["curriculum_key"] != "placement-foundations" or content["track_slug"] not in SUBJECT_KEYS
                    or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", content["topic_slug"])):
                raise RegistryError("Invalid Forge lesson subject/topic namespace")
            expected = f"forge/placement-foundations/{content['track_slug']}/{content['topic_slug']}"
    else:
        content = payload["problem"]
        expected = f"arena/{content['key']}"
    if key != expected or revision != content["version"]:
        raise RegistryError("Registry identity differs from the content's declared key/revision")


def load_snapshot(revision: ContentRevision) -> dict:
    expected_path = f"sha256/{revision.sha256[:2]}/{revision.sha256}.json"
    if revision.snapshot_path != expected_path or len(revision.sha256) != 64 or any(c not in "0123456789abcdef" for c in revision.sha256):
        raise RegistryError("Invalid content-addressed snapshot identity")
    path = safe_path(settings.content_snapshot_path, revision.snapshot_path)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != revision.sha256:
        raise RegistryError(f"Snapshot digest mismatch for {revision.content_key}@{revision.revision}")
    payload = json.loads(data)
    if canonical_json(payload) != data:
        raise RegistryError("Snapshot is not in the documented canonical format")
    _validate_payload(revision.content_type, payload)
    _validate_identity(revision.content_key, revision.revision, revision.content_type, payload)
    return payload


def register_revision(session: Session, *, key: str, revision: str, content_type: str,
                      source_path: str, payload: dict, provenance: dict, registration_status: str = "legacy_baseline") -> ContentRevision:
    validate_relative_path(key)
    validate_relative_path(source_path)
    _validate_payload(content_type, payload)
    _validate_identity(key, revision, content_type, payload)
    sha256 = digest(payload)
    existing = session.exec(select(ContentRevision).where(ContentRevision.content_key == key, ContentRevision.revision == revision)).one_or_none()
    if existing:
        if (existing.sha256, existing.content_type, existing.source_path) != (sha256, content_type, source_path):
            raise RegistryError(f"Immutable content changed without a new revision: {key}@{revision}")
        load_snapshot(existing)
        return existing
    relative = f"sha256/{sha256[:2]}/{sha256}.json"
    target = safe_path(settings.content_snapshot_path, relative, must_exist=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    reject_links(target)
    temporary = target.with_name(f".{uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(canonical_json(payload))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            # Windows rename is atomic and refuses an existing destination. POSIX
            # rename replaces it, so use an exclusive hard link on that platform.
            if os.name == "nt":
                temporary.rename(target)
            else:
                os.link(temporary, target)
        except FileExistsError:
            if target.read_bytes() != canonical_json(payload):
                raise RegistryError("Existing content-addressed file has invalid bytes")
    finally:
        temporary.unlink(missing_ok=True)
    row = ContentRevision(content_key=key, revision=revision, content_type=content_type,
                          source_path=source_path, snapshot_path=relative, sha256=sha256,
                          provenance_json=canonical_json(provenance).decode(), approval_status=registration_status)
    session.add(row)
    session.flush()
    load_snapshot(row)
    return row


def register_legacy_lessons(session: Session) -> dict[tuple[str, str], ContentRevision]:
    root = settings.course_content_path
    manifest_path = safe_path(root, "manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    names = manifest["compiled_topics"]
    if len(names) != len(set(names)):
        raise RegistryError("Duplicate compiled topic identity")
    actual = {path.parent.relative_to(root).as_posix() for path in root.glob("*/*/lesson.json")}
    if set(names) != actual:
        raise RegistryError("Course manifest and accepted lesson files differ")
    result = {}
    for name in sorted(names):
        lesson_path = safe_path(root, f"{name}/lesson.json")
        exercise_path = safe_path(root, f"{name}/exercises.json")
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        if name != f"{lesson['track_slug']}/{lesson['topic_slug']}":
            raise RegistryError("Lesson file path and declared identity differ")
        payload = {"lesson": lesson, "exercises": json.loads(exercise_path.read_text(encoding="utf-8"))}
        key = f"ai-engineer/v1/{name}"
        row = register_revision(session, key=key, revision=lesson["version"], content_type="lesson_bundle",
                                source_path=f"{name}/lesson.json", payload=payload,
                                provenance={"sources": lesson["sources"], "legacy_content_hash": lesson["content_hash"],
                                            "lesson_file_sha256": hashlib.sha256(lesson_path.read_bytes()).hexdigest(),
                                            "exercise_file_sha256": hashlib.sha256(exercise_path.read_bytes()).hexdigest(),
                                            "status_reason": "Imported legacy baseline; no editorial approval asserted"})
        result[key, row.revision] = row
    return result


def load_manifest() -> LegacyBindingsManifest:
    reject_links(settings.content_bindings_path)
    return LegacyBindingsManifest.model_validate_json(settings.content_bindings_path.read_text(encoding="utf-8"))


def source_graph(payload: dict) -> dict:
    """Normalize only seeder defaults; hash the exact confirmed graph including prerequisites."""
    tracks = []
    for index, track in enumerate(payload["tracks"], 1):
        topics = []
        for order, topic in enumerate(track["topics"], 1):
            topics.append({"slug": topic["slug"], "name": topic["name"],
                           "description": topic.get("description", f"Understand and apply {topic['name'].lower()}."),
                           "order_index": order, "priority": topic.get("priority", track.get("priority", 50)),
                           "target_level": topic.get("target_level", "working"), "estimated_minutes": topic.get("estimated_minutes", 45),
                           "prerequisites": sorted(topic.get("prerequisites", []))})
        tracks.append({"slug": track["slug"], "name": track["name"], "description": track["description"],
                       "order_index": index, "priority": track.get("priority", 50), "topics": topics})
    return {"name": payload["name"], "version": payload["version"], "description": payload["description"], "tracks": tracks}


def database_graph(session: Session, curriculum: Curriculum) -> dict:
    tracks = session.exec(select(Track).where(Track.curriculum_id == curriculum.id).order_by(Track.order_index)).all()
    pairs = session.exec(select(Topic, Track).join(Track).where(Track.curriculum_id == curriculum.id)).all()
    keys = {topic.id: f"{track.slug}/{topic.slug}" for topic, track in pairs}
    prerequisites = {}
    for link in session.exec(select(TopicPrerequisite).where(TopicPrerequisite.topic_id.in_(keys))):
        prerequisites.setdefault(link.topic_id, []).append(keys.get(link.prerequisite_topic_id, "INVALID-EXTERNAL-PREREQUISITE"))
    output = []
    for track in tracks:
        topics = sorted((topic for topic, parent in pairs if parent.id == track.id), key=lambda t: t.order_index)
        output.append({**{field: getattr(track, field) for field in ("slug", "name", "description", "order_index", "priority")},
                       "topics": [{**{field: getattr(topic, field) for field in ("slug", "name", "description", "order_index", "priority", "target_level", "estimated_minutes")},
                                   "prerequisites": sorted(prerequisites.get(topic.id, []))} for topic in topics]})
    return {"name": curriculum.name, "version": curriculum.version, "description": curriculum.description, "tracks": output}


def matched_curricula(session: Session, manifest: LegacyBindingsManifest):
    result = []
    for spec in manifest.curricula:
        curriculum = session.exec(select(Curriculum).where(Curriculum.name == spec.name, Curriculum.version == spec.version,
                                                          Curriculum.source_type == spec.source_type, Curriculum.status == "confirmed")).one_or_none()
        if curriculum is None:
            continue
        if digest(database_graph(session, curriculum)) != spec.graph_sha256:
            raise RegistryError(f"Confirmed curriculum graph differs from reviewed binding identity: {spec.name} v{spec.version}")
        topics = {f"{track.slug}/{topic.slug}": topic for topic, track in session.exec(select(Topic, Track).join(Track).where(Track.curriculum_id == curriculum.id))}
        if {item.topic for item in spec.topics} | set(spec.unmapped_topics) != set(topics):
            raise RegistryError("Binding manifest must explicitly account for every confirmed topic")
        result.append((spec, curriculum, topics))
    return result


def bind_legacy_lessons(session: Session, registered: dict) -> int:
    count = 0
    for spec, curriculum, topics in matched_curricula(session, load_manifest()):
        for item in spec.topics:
            topic = topics[item.topic]
            for order, reference in enumerate(item.lessons):
                revision = registered.get((reference.content_key, reference.revision))
                if revision is None:
                    raise RegistryError(f"Binding references missing content: {reference.content_key}@{reference.revision}")
                expected = {"curriculum_id": curriculum.id, "order_index": order,
                            "legacy_progress_compatible": reference.legacy_progress_compatible, "coverage_note": item.coverage_note}
                existing = session.get(TopicContentBinding, (topic.id, revision.id))
                if existing and any(getattr(existing, key) != value for key, value in expected.items()):
                    raise RegistryError("An existing content binding changed; use an explicit versioned migration")
                if not existing:
                    if session.exec(select(TopicContentBinding).where(TopicContentBinding.topic_id == topic.id, TopicContentBinding.order_index == order)).first():
                        raise RegistryError("Ambiguous lesson order for this topic")
                    session.add(TopicContentBinding(topic_id=topic.id, content_revision_id=revision.id, **expected))
                count += 1
    session.flush()
    return count


def bound_lessons(session: Session, topic: Topic) -> list[tuple[TopicContentBinding, ContentRevision]]:
    track = session.get(Track, topic.track_id)
    rows = session.exec(select(TopicContentBinding, ContentRevision).join(ContentRevision)
                        .where(TopicContentBinding.topic_id == topic.id, TopicContentBinding.curriculum_id == track.curriculum_id)
                        .order_by(TopicContentBinding.order_index)).all()
    from .content_publication import release_entries
    released = [(entry, rev) for entry, rev in release_entries(session, curriculum_id=track.curriculum_id)
                if entry.topic_id == topic.id and rev.content_type == "lesson_bundle"]
    if released:
        return [(session.get(TopicContentBinding, (topic.id, rev.id)), rev) for _, rev in released]
    return [(binding, rev) for binding, rev in rows if rev.approval_status == "legacy_baseline"]
