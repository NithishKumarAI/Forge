"""Static scope, explicit draft/review/activation, and registry-derived availability."""
import json
from sqlmodel import Session, select
from ..config import REPO_ROOT
from ..models import (AppSetting, Curriculum, EditionCurriculumBinding, TopicPlacement, Topic, Track,
    ArenaTopicBinding, ContentRevision, TopicPrerequisite, utc_now)
from ..schemas.editions import EditionManifest, PlacementScope, EditionConfirmation
from ..schemas.ai import CurriculumDraftRequest
from .content_registry import digest, canonical_json, database_graph, bound_lessons
from .active_curriculum import get_active_curriculum, activate_curriculum

EDITION_PREFERENCE = "selected_product_edition"


def manifest():
    return EditionManifest.model_validate_json((REPO_ROOT / "data/editions.json").read_text(encoding="utf-8"))


def scope():
    return PlacementScope.model_validate_json((REPO_ROOT / "data/placement-foundations-scope.json").read_text(encoding="utf-8"))


def binding_scope(binding):
    value = PlacementScope.model_validate_json(binding.scope_json)
    if digest(value.model_dump(mode="json")) != binding.scope_sha256:
        raise ValueError("Stored edition scope integrity mismatch")
    return value


def index(session):
    selected = session.get(AppSetting, EDITION_PREFERENCE)
    active = get_active_curriculum(session)
    return {**manifest().model_dump(mode="json"), "selected_edition_key": selected.value if selected else None,
            "active_curriculum_id": active.id if active else None}


def select_edition(session, key):
    edition = next((e for e in manifest().editions if e.key == key), None)
    if edition is None or edition.status == "future":
        raise ValueError("This edition is not available for selection")
    row = session.get(AppSetting, EDITION_PREFERENCE) or AppSetting(key=EDITION_PREFERENCE, value=key)
    row.value = key
    session.add(row)
    session.commit()
    return index(session)


def validate_proposal(proposal, binding):
    spec = binding_scope(binding)
    expected = {s: {t.key for t in spec.topics if t.subject_key == s} for s in manifest().editions[0].subjects}
    actual = {t.key: {p.key for p in t.topics} for t in proposal.tracks}
    if expected != actual:
        raise ValueError("Edition drafts must retain all reviewed scope topics in their defined subjects; create a new scope version to add/remove topics")


def reconcile_placements(session, curriculum):
    binding = session.get(EditionCurriculumBinding, curriculum.id)
    if binding is None:
        return
    if curriculum.status != "draft":
        raise ValueError("Confirmed edition placements cannot be rewritten")
    from .custom_curriculum import proposal_from_curriculum
    validate_proposal(proposal_from_curriculum(session, curriculum), binding)
    topics = {t.key: t for t in binding_scope(binding).topics}
    for topic, track in session.exec(select(Topic, Track).join(Track).where(Track.curriculum_id == curriculum.id)):
        item = topics[topic.slug]
        session.add(TopicPlacement(topic_id=topic.id, curriculum_id=curriculum.id, edition_key=binding.edition_key,
            subject_key=item.subject_key, level=item.level, order_index=topic.order_index - 1))
    binding.graph_sha256 = digest(database_graph(session, curriculum))
    binding.reviewed_by = binding.reviewed_at = None
    session.add(binding)
    session.flush()


def create_placement_draft(session):
    value = scope()
    sha = digest(value.model_dump(mode="json"))
    existing = session.exec(select(EditionCurriculumBinding).where(EditionCurriculumBinding.edition_key == value.edition_key,
        EditionCurriculumBinding.scope_sha256 == sha)).one_or_none()
    if existing:
        return session.get(Curriculum, existing.curriculum_id)
    from .custom_curriculum import create_draft
    proposal = value.proposal()
    definitions = {s.key: s for s in manifest().subjects}
    for track in proposal.tracks:
        track.name, track.description = definitions[track.key].name, definitions[track.key].description
    try:
        curriculum = create_draft(session, CurriculumDraftRequest(proposal=proposal,
            source_requirements="Placement Foundations scope " + value.version), commit=False)
        session.add(EditionCurriculumBinding(curriculum_id=curriculum.id, edition_key=value.edition_key,
            scope_version=value.version, scope_sha256=sha, scope_json=canonical_json(value.model_dump(mode="json")).decode(),
            graph_sha256=digest(database_graph(session, curriculum))))
        session.flush()
        reconcile_placements(session, curriculum)
        session.commit()
        return session.get(Curriculum, curriculum.id)
    except BaseException:
        session.rollback()
        raise


def record_confirmation(session, curriculum, request):
    binding = session.get(EditionCurriculumBinding, curriculum.id)
    if binding is None:
        return
    if request is None:
        raise ValueError("Review this Placement Foundations draft through its edition review screen before confirmation")
    request = EditionConfirmation.model_validate(request)
    from .custom_curriculum import proposal_from_curriculum
    validate_proposal(proposal_from_curriculum(session, curriculum), binding)
    observed = digest(database_graph(session, curriculum))
    if request.graph_sha256 != observed or request.scope_sha256 != binding.scope_sha256 or observed != binding.graph_sha256:
        raise ValueError("Draft/scope changed after review; reload the review summary")
    if not request.scope_reviewed or not request.missing_content_acknowledged or len(request.reviewer.strip()) < 3:
        raise ValueError("Explicit scope review, missing-content acknowledgment and reviewer identity are required")
    placements = session.exec(select(TopicPlacement).where(TopicPlacement.curriculum_id == curriculum.id)).all()
    expected = {t.key: (t.subject_key, t.level) for t in binding_scope(binding).topics}
    actual = {session.get(Topic, p.topic_id).slug: (p.subject_key, p.level) for p in placements}
    if expected != actual:
        raise ValueError("Draft placements do not match the reviewed scope")
    binding.reviewed_by, binding.reviewed_at = request.reviewer.strip(), utc_now()
    session.add(binding)
    session.flush()


def require_reviewed_curriculum(session, curriculum, graph_sha=None):
    binding = session.get(EditionCurriculumBinding, curriculum.id)
    observed = digest(database_graph(session, curriculum))
    if (curriculum.status != "confirmed" or binding is None or binding.edition_key != "placement-foundations"
            or not binding.reviewed_by or not binding.reviewed_at or binding.graph_sha256 != observed
            or graph_sha is not None and graph_sha != observed):
        raise ValueError("Publication/activation requires an explicitly reviewed confirmed edition curriculum")
    binding_scope(binding)
    return binding


def activate_edition_curriculum(session, curriculum):
    binding = require_reviewed_curriculum(session, curriculum)
    # Activation and preference are explicit; ordinary preview/selection never calls this.
    row = session.get(AppSetting, EDITION_PREFERENCE) or AppSetting(key=EDITION_PREFERENCE, value=binding.edition_key)
    row.value = binding.edition_key
    session.add(row)
    activate_curriculum(session, curriculum)


def availability(session, topic):
    from .course import progress, load_lesson_for_topic, current_course_exercise_ids
    from .content_publication import release_entries
    track = session.get(Track, topic.track_id)
    released = release_entries(session, curriculum_id=track.curriculum_id)
    approved_lessons = {r.id for e, r in released if e.topic_id == topic.id and r.content_type == "lesson_bundle"}
    lessons = bound_lessons(session, topic)
    completed = total = 0
    for _, revision in lessons:
        reading = progress(session, topic, load_lesson_for_topic(session, topic, revision.id))
        completed += reading["completed_sections"]
        total += reading["total_sections"]
    override_keys = {r.content_key.removeprefix("arena/") for _, r in released if r.content_type == "arena_problem"}
    old_arena = {p.problem_key for p in session.exec(select(ArenaTopicBinding).where(
        ArenaTopicBinding.curriculum_id == track.curriculum_id, ArenaTopicBinding.topic_id == topic.id))} - override_keys
    new_arena = {r.content_key for e, r in released if e.topic_id == topic.id and r.content_type == "arena_problem"}
    exercises = current_course_exercise_ids(session, topic.id)
    approved_count = sum(r.id in approved_lessons for _, r in lessons)
    return {"lesson_status": "approved" if approved_count else "legacy" if lessons else "planned",
        "lesson_count": len(lessons), "approved_lesson_count": approved_count, "legacy_lesson_count": len(lessons) - approved_count,
        "practice_available": bool(exercises or old_arena or new_arena),
        "approved_practice_available": bool(new_arena or approved_count and exercises),
        "course_exercise_count": len(exercises), "arena_count": len(old_arena) + len(new_arena),
        "completed_sections": completed, "total_sections": total, "reading_percent": round(100 * completed / total) if total else 0}


def topic_metadata(session, topic):
    placement = session.get(TopicPlacement, topic.id)
    curriculum = session.get(Curriculum, session.get(Track, topic.track_id).curriculum_id)
    return {"placement": placement.model_dump() if placement else None, "curriculum_status": curriculum.status,
            "availability": availability(session, topic)}


def overview(session, key="placement-foundations", curriculum_id=None):
    definition = next((e for e in manifest().editions if e.key == key), None)
    if definition is None: raise ValueError("Unknown edition")
    if key != "placement-foundations":
        return {"edition": definition.model_dump(), "binding": None, "subjects": [], "active_curriculum_id": index(session)["active_curriculum_id"]}
    binding = session.get(EditionCurriculumBinding, curriculum_id) if curriculum_id else session.exec(
        select(EditionCurriculumBinding).where(EditionCurriculumBinding.edition_key == key).order_by(EditionCurriculumBinding.curriculum_id.desc())).first()
    if curriculum_id and (binding is None or binding.edition_key != key): raise ValueError("Curriculum is not bound to this edition")
    spec = binding_scope(binding) if binding else scope()
    curriculum = session.get(Curriculum, binding.curriculum_id) if binding else None
    pairs = session.exec(select(Topic, Track).join(Track).where(Track.curriculum_id == curriculum.id)).all() if curriculum else []
    actual = {topic.slug: topic for topic, _ in pairs}
    tracks = {track.slug: track for _, track in pairs}
    empty = {"lesson_status":"planned", "lesson_count":0, "approved_lesson_count":0, "legacy_lesson_count":0,
        "practice_available":False, "approved_practice_available":False, "course_exercise_count":0,"arena_count":0,
        "completed_sections":0,"total_sections":0,"reading_percent":0}
    subjects = []
    for subject in manifest().subjects:
        topics = []
        for item in spec.topics:
            if item.subject_key != subject.key: continue
            topic = actual.get(item.key)
            topics.append({**item.model_dump(), "id":topic.id if topic else None,
                "title":topic.name if topic else item.title, "description":topic.description if topic else item.description,
                "estimated_minutes":topic.estimated_minutes if topic else item.estimated_minutes,
                "priority":topic.priority if topic else item.priority,
                "availability":availability(session, topic) if topic else dict(empty),
                "prerequisites": [session.get(Topic, p.prerequisite_topic_id).slug for p in session.exec(
                    select(TopicPrerequisite).where(TopicPrerequisite.topic_id==topic.id))] if topic else item.prerequisites})
        if curriculum:
            topics.sort(key=lambda item: actual[item["key"]].order_index)
        track = tracks.get(subject.key)
        subjects.append({**subject.model_dump(), "name":track.name if track else subject.name, "topics":topics})
    active_id = index(session)["active_curriculum_id"]
    return {"edition":definition.model_dump(),"scope_version":spec.version,"scope_sha256":binding.scope_sha256 if binding else digest(spec.model_dump(mode="json")),
        "active_curriculum_id":active_id,"subjects":subjects,"binding":{
            "curriculum_id":curriculum.id,"name":curriculum.name,"version":curriculum.version,"status":curriculum.status,
            "graph_sha256":digest(database_graph(session,curriculum)),"reviewed_by":binding.reviewed_by,
            "is_active":curriculum.id==active_id} if curriculum else None}
