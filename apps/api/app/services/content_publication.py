"""Digest-bound human approvals and transactional release overlays.

The local repository/reviewer is the trust boundary. Hashes detect stale artifacts;
they are not signatures proving who operated the local review command.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from sqlmodel import Session, select
from ..models import (ApprovedContentRelease, ContentReleaseEntry, ContentReleaseEvent,
    ContentReviewRecord, ContentValidationReport, ContentRevision, Curriculum, Topic, Track,
    TopicContentBinding, ArenaProblem)
from ..schemas.publication import Candidate, HumanReview, ReleasePackage, ReleaseTarget, POLICY_VERSION
from .content_registry import canonical_json, digest, database_graph, register_revision, load_snapshot


def verified_entry(entry):
    candidate = Candidate.model_validate(entry["candidate"])
    value = candidate.model_dump(mode="json")
    report = entry["validation"]
    review = HumanReview.model_validate(entry["review"])
    if (report["policy_version"] != POLICY_VERSION or report["candidate_sha256"] != digest(value)
            or report["payload_sha256"] != digest(candidate.payload)
            or report["coverage_sha256"] != digest(candidate.coverage)
            or report["provenance"]["sha256"] != digest(candidate.provenance)
            or report.get("structurally_valid") is not True or report.get("executable_checks_passed") is not True):
        raise ValueError("Stale/invalid candidate validation digest or policy")
    if review.candidate_sha256 != digest(value) or review.validation_sha256 != digest(report):
        raise ValueError("Stale review/approval digest")
    if review.outcome != "approved":
        raise ValueError("Candidate is awaiting human approval or was rejected")
    if review.reviewer.strip().casefold() == candidate.provenance["author"].strip().casefold():
        raise ValueError("Independent technical reviewer must differ from the author")
    if review.reviewed_at > datetime.now(timezone.utc):
        raise ValueError("Review timestamp is in the future")
    if not report["coverage"] or any(x["status"] != "covered" for x in report["coverage"]):
        raise ValueError("Partial/missing/requires-review coverage cannot be published")
    # Recheck policy/structure without executing arbitrary code in the backend.
    from ..schemas.arena import CodingProblem
    from .content_registry import _validate_payload, _validate_identity
    _validate_payload(candidate.content_type, candidate.payload)
    _validate_identity(candidate.content_key, candidate.revision, candidate.content_type, candidate.payload)
    from .content_policy import check_provenance, check_coverage
    if check_provenance(candidate) != report["provenance"] or check_coverage(candidate) != report["coverage"]:
        raise ValueError("Validation report contradicts backend coverage/provenance policy")
    if candidate.content_type == "lesson_bundle":
        lesson = candidate.payload["lesson"]
        if lesson["content_hash"] != digest({k: v for k, v in lesson.items() if k not in {"content_hash", "generated_at"}}):
            raise ValueError("Invalid new lesson content hash")
    if candidate.content_type == "arena_problem":
        p = CodingProblem.model_validate(candidate.payload["problem"])
        if p.adapted or p.source_project or p.source_type != "original" or candidate.provenance.get("origin") != "original":
            raise ValueError("New Arena releases are original-only")
    targets = [ReleaseTarget.model_validate(t) for t in entry["targets"]]
    if not targets:
        raise ValueError("A release entry requires explicit curriculum/topic targets")
    return candidate, report, review, targets


def record_validation(session, candidate, report):
    sha = digest(report)
    value = Candidate.model_validate(candidate).model_dump(mode="json")
    if report["candidate_sha256"] != digest(value) or report["payload_sha256"] != digest(value["payload"]):
        raise ValueError("Stale validation digest")
    row = session.get(ContentValidationReport, sha)
    if row is None:
        row = ContentValidationReport(sha256=sha, candidate_sha256=digest(value), payload_sha256=report["payload_sha256"],
            policy_version=report["policy_version"], candidate_json=canonical_json(value).decode(), report_json=canonical_json(report).decode())
        session.add(row)
        session.flush()
    return row


def record_review(session, review):
    review = HumanReview.model_validate(review)
    value = review.model_dump(mode="json")
    sha = digest(value)
    validation = session.get(ContentValidationReport, review.validation_sha256)
    if not validation or validation.candidate_sha256 != review.candidate_sha256:
        raise ValueError("Review requires its recorded validation report")
    row = session.get(ContentReviewRecord, sha)
    if row is None:
        row = ContentReviewRecord(sha256=sha, validation_sha256=review.validation_sha256, reviewer=review.reviewer,
            outcome=review.outcome, reviewed_at=review.reviewed_at, review_json=canonical_json(value).decode())
        session.add(row)
        session.flush()
    return row


def active_release(session):
    event = session.exec(select(ContentReleaseEvent).order_by(ContentReleaseEvent.id.desc())).first()
    return event.release_id if event and event.status in {"published", "activated"} else None


def release_entries(session, *, curriculum_id=None):
    selected = active_release(session)
    if not selected:
        return []
    query = select(ContentReleaseEntry, ContentRevision).join(ContentRevision).where(ContentReleaseEntry.release_id == selected)
    if curriculum_id is not None:
        query = query.where(ContentReleaseEntry.curriculum_id == curriculum_id)
    return list(session.exec(query.order_by(ContentReleaseEntry.order_index)))


def transition_release(session, release_id, status, actor, reason):
    if status not in {"activated", "revoked", "superseded"} or not actor.strip() or not reason.strip():
        raise ValueError("Explicit actor, reason and supported release transition are required")
    if not session.get(ApprovedContentRelease, release_id):
        raise ValueError("Unknown release")
    if status != "activated" and active_release(session) != release_id:
        raise ValueError("Only the selected release can be revoked/superseded")
    try:
        session.add(ContentReleaseEvent(release_id=release_id, status=status, actor=actor, reason=reason))
        from .course import rebuild_search_index
        session.flush()
        rebuild_search_index(session, commit=False)
        session.commit()
    except BaseException:
        session.rollback()
        raise


def _resolve_target(session, target):
    curriculum = session.exec(select(Curriculum).where(Curriculum.name == target.curriculum_name,
        Curriculum.version == target.curriculum_version, Curriculum.status == "confirmed", Curriculum.source_type == "default")).one_or_none()
    if curriculum is None or digest(database_graph(session, curriculum)) != target.graph_sha256:
        raise ValueError("Release target confirmed graph does not match")
    track_slug, topic_slug = target.topic.split("/")
    topic = session.exec(select(Topic).join(Track).where(Track.curriculum_id == curriculum.id,
        Track.slug == track_slug, Topic.slug == topic_slug)).one_or_none()
    if topic is None:
        raise ValueError("Missing release target topic")
    return curriculum, topic


def publish_release(session: Session, package, *, archive_path: Path | None = None):
    """One DB commit exposes the complete overlay. Orphan snapshots are inert.

    CLI supplies an already-created, immutable repository archive as input. The
    archive is not watched/imported by runtime: failed publication cannot activate it.
    """
    package = ReleasePackage.model_validate(package)
    value = package.model_dump(mode="json")
    sha = digest(value)
    try:
        existing = session.get(ApprovedContentRelease, package.release_id)
        if existing:
            if existing.sha256 != sha:
                raise ValueError("Published release identity is immutable")
            verify_release_snapshots(session)
            return existing
        if archive_path is not None and archive_path.read_bytes() != canonical_json(value):
            raise ValueError("Release archive is not the exact canonical package")
        verified = [verified_entry(entry) for entry in package.entries]
        available = set(session.exec(select(ContentRevision.content_key))) | {c.content_key for c, _, _, _ in verified}
        prerequisites = {}
        for candidate, _, _, _ in verified:
            if candidate.content_type == "lesson_bundle":
                required = set(candidate.payload["lesson"]["prerequisites"])
                if (required | set(candidate.known_content)) - available:
                    raise ValueError("Release contains unresolved prerequisite/content references")
                prerequisites[candidate.content_key] = required
        def visit(key, path):
            if key in path:
                raise ValueError("Cyclic lesson prerequisites")
            for parent in prerequisites.get(key, ()):
                visit(parent, path | {key})
        for key in prerequisites:
            visit(key, set())
        identities, slots = set(), set()
        session.add(ApprovedContentRelease(release_id=package.release_id, sha256=sha, package_json=canonical_json(value).decode()))
        session.flush()
        for candidate, report, review, targets in verified:
            identity = candidate.content_key
            if identity in identities:
                raise ValueError("Ambiguous duplicate content identity in release")
            identities.add(identity)
            validation = record_validation(session, candidate, report)
            reviewed = record_review(session, review)
            prior = session.exec(select(ContentRevision).where(ContentRevision.content_key == candidate.content_key,
                ContentRevision.revision == candidate.revision)).one_or_none()
            if prior and canonical_json(json.loads(prior.provenance_json)) != canonical_json(candidate.provenance):
                raise ValueError("Registered provenance changed; use a new content revision")
            revision = register_revision(session, key=candidate.content_key, revision=candidate.revision,
                content_type=candidate.content_type, payload=candidate.payload,
                source_path=f"approved/{digest(candidate.payload)}.json", provenance=candidate.provenance,
                registration_status="candidate")
            if candidate.content_type == "arena_problem":
                raw = candidate.payload["problem"]
                if session.get(ArenaProblem, raw["key"]) is None:
                    session.add(ArenaProblem(key=raw["key"], track=raw["track"], title=raw["title"], difficulty=raw["difficulty"],
                        topic_tags_json=json.dumps(raw["topic_tags"]), source_path=revision.source_path, content_hash=revision.sha256,
                        version=raw["version"]))
                    session.flush()
            for target in targets:
                curriculum, topic = _resolve_target(session, target)
                slot = (curriculum.id, topic.id, target.order_index) if candidate.content_type == "lesson_bundle" else (curriculum.id, identity)
                if slot in slots:
                    raise ValueError("Ambiguous release target/order")
                slots.add(slot)
                session.add(ContentReleaseEntry(release_id=package.release_id, curriculum_id=curriculum.id,
                    topic_id=topic.id, order_index=target.order_index, content_revision_id=revision.id,
                    validation_sha256=validation.sha256, review_sha256=reviewed.sha256))
                if candidate.content_type == "lesson_bundle":
                    binding = session.get(TopicContentBinding, (topic.id, revision.id))
                    if binding is None:
                        orders = session.exec(select(TopicContentBinding.order_index).where(TopicContentBinding.topic_id == topic.id)).all()
                        binding = TopicContentBinding(topic_id=topic.id, content_revision_id=revision.id, curriculum_id=curriculum.id,
                            order_index=max(orders, default=-1) + 1, legacy_progress_compatible=False, coverage_note="Approved release; exact versioned competency references")
                        session.add(binding)
                        session.flush()
                    from .course import _sync_exercise
                    for item in candidate.payload["exercises"]:
                        _sync_exercise(session, binding, revision, candidate.payload["lesson"], item)
        session.flush()
        session.add(ContentReleaseEvent(release_id=package.release_id, status="published",
            actor=verified[0][2].reviewer, reason="Exact validated and human-reviewed release"))
        session.flush()
        from .course import rebuild_search_index
        rebuild_search_index(session, commit=False)
        session.commit()
        return session.get(ApprovedContentRelease, package.release_id)
    except BaseException:
        session.rollback()
        raise


def verify_release_snapshots(session):
    """Verify every historical approved release on startup. Restore via explicit CLI.

    Archives contain all bytes needed on fresh installation; imports are explicit
    so a failed publication's archive can never become active merely on restart.
    """
    for release in session.exec(select(ApprovedContentRelease)):
        package = json.loads(release.package_json)
        if digest(package) != release.sha256:
            raise ValueError("Release package integrity mismatch")
        for entry in package["entries"]:
            candidate, _, _, _ = verified_entry(entry)
            revision = session.exec(select(ContentRevision).where(ContentRevision.content_key == candidate.content_key,
                ContentRevision.revision == candidate.revision)).one()
            if load_snapshot(revision) != candidate.payload:
                raise ValueError("Approved runtime bytes differ from tested bundle")
            if json.loads(revision.provenance_json) != candidate.provenance:
                raise ValueError("Approved runtime provenance differs from reviewed provenance")


def write_immutable(path: Path, value):
    """Atomic non-replacing artifact write using the same policy as registry snapshots."""
    import os
    from uuid import uuid4
    from .content_paths import reject_links
    reject_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_json(value)
    temporary = path.with_name("." + uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            if os.name == "nt": temporary.rename(path)
            else: os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != data:
                raise ValueError("Immutable artifact already exists with different bytes")
    finally:
        temporary.unlink(missing_ok=True)
    return path
