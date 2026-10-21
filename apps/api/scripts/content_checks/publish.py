"""Human-operated development workflow. No LLM integration."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from sqlmodel import Session, create_engine
from app.schemas.publication import Candidate, HumanReview, ReleasePackage, QUALITY_CHECKS
from app.services.content_registry import digest
from app.services.content_publication import publish_release, verified_entry, write_immutable
from .bundle import validate_candidate


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def publish_package(path, session):
    package = ReleasePackage.model_validate(read(path))
    for entry in package.entries:
        verified_entry(entry)
        if validate_candidate(entry["candidate"]) != entry["validation"]:
            raise ValueError("Validation changed; revalidate and obtain a new human review")
    return publish_release(session, package, archive_path=Path(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--candidate", type=Path, required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--candidate", type=Path, required=True)
    validate.add_argument("--output", type=Path, required=True)
    review = sub.add_parser("review")
    for name in ("candidate", "validation", "checklist", "output"):
        review.add_argument("--" + name, type=Path, required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", required=True)
    review.add_argument("--outcome", choices=["approved", "rejected"], required=True)
    review.add_argument("--i-am-the-human-reviewer", action="store_true", required=True)
    package = sub.add_parser("package")
    for name in ("candidate", "validation", "review", "targets", "output"):
        package.add_argument("--" + name, type=Path, required=True)
    package.add_argument("--release-id", required=True)
    transition = sub.add_parser("transition")
    transition.add_argument("--database", type=Path, required=True)
    transition.add_argument("--release-id", required=True)
    transition.add_argument("--status", choices=["activated", "revoked", "superseded"], required=True)
    transition.add_argument("--actor", required=True)
    transition.add_argument("--reason", required=True)
    for action in ("publish", "restore"):
        publish = sub.add_parser(action)
        publish.add_argument("--package", type=Path, required=True)
        publish.add_argument("--database", type=Path, required=True, help="Explicit Forge SQLite file; never inferred")
    args = parser.parse_args()
    if args.action == "inspect":
        print(json.dumps({"candidate": read(args.candidate), "required_human_checks": QUALITY_CHECKS}, indent=2))
    elif args.action == "validate":
        report = validate_candidate(read(args.candidate))
        write_immutable(args.output, report)
        print(f"Validated {report['candidate_sha256']}; report {digest(report)}; awaiting human review")
    elif args.action == "review":
        candidate = Candidate.model_validate(read(args.candidate))
        report = read(args.validation)
        if validate_candidate(candidate) != report:
            raise ValueError("Stale validation; review refused")
        review = HumanReview(candidate_sha256=report["candidate_sha256"], validation_sha256=digest(report),
            reviewer=args.reviewer, reviewed_at=datetime.now(timezone.utc), outcome=args.outcome,
            human_attestation=True, checklist=read(args.checklist), notes=args.notes)
        if args.reviewer.strip().casefold() == candidate.provenance["author"].strip().casefold():
            raise ValueError("Reviewer must be independent of author")
        write_immutable(args.output, review.model_dump(mode="json"))
        print(f"Human review recorded: {args.outcome}")
    elif args.action == "package":
        entry = {"candidate": Candidate.model_validate(read(args.candidate)).model_dump(mode="json"),
            "validation": read(args.validation), "review": read(args.review), "targets": read(args.targets)}
        verified_entry(entry)
        write_immutable(args.output, ReleasePackage(release_id=args.release_id, entries=[entry]).model_dump(mode="json"))
        print("Approved package archived; not yet published")
    elif args.action == "transition":
        from app.services.content_publication import transition_release
        from app.migrations import run_migrations
        engine = create_engine("sqlite:///" + args.database.absolute().as_posix())
        run_migrations(engine)
        with Session(engine) as session:
            transition_release(session, args.release_id, args.status, args.actor, args.reason)
        engine.dispose()
        print(f"Release {args.release_id}: {args.status}")
    else:
        # Validate before opening/migrating any database.
        package = ReleasePackage.model_validate(read(args.package))
        for entry in package.entries:
            verified_entry(entry)
            if validate_candidate(entry["candidate"]) != entry["validation"]:
                raise ValueError("Stale executable validation")
        from app.migrations import run_migrations
        engine = create_engine("sqlite:///" + args.database.absolute().as_posix())
        run_migrations(engine)
        with Session(engine) as session:
            if args.action == "restore":
                from app.config import settings
                from app.services.curriculum import seed_default_curriculum
                from app.services.course import sync_course_pack
                from app.services.arena import sync_problem_bank
                from app.models import Curriculum, AppSetting
                from sqlmodel import select
                fresh = session.exec(select(Curriculum)).first() is None and session.get(AppSetting, "active_curriculum_id") is None
                seed_default_curriculum(session, settings.curriculum_path)
                default = seed_default_curriculum(session, settings.curriculum_v2_path)
                if fresh:
                    from app.services.active_curriculum import activate_curriculum
                    activate_curriculum(session, default)
                sync_course_pack(session)
                sync_problem_bank(session)
            release = publish_release(session, package, archive_path=args.package)
            print(f"Published {release.release_id} @ {release.sha256}")
        engine.dispose()


if __name__ == "__main__":
    main()
