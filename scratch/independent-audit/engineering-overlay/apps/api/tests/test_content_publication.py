"""Review identities below are synthetic TEST FIXTURES, never shipped approvals."""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
import httpx
import pytest
from sqlalchemy import text
from sqlmodel import Session, create_engine, select
from app import models as m
from app.config import settings
from app.migrations import run_migrations
from app.schemas.arena import CodingProblem, ArenaAttemptRequest
from app.schemas.publication import Candidate, HumanReview, QUALITY_CHECKS
from app.services.content_registry import digest, database_graph, load_snapshot, canonical_json
from app.services.content_publication import (publish_release, active_release, transition_release,
    write_immutable, verify_release_snapshots)
from app.services.course import load_lesson_for_topic, mark_section, current_course_exercise_ids
from app.services.arena import sync_problem_bank, load_problem, problem_revision, record_attempt, public_problem
from scripts.content_checks.bundle import validate_candidate
from scripts.content_checks.examples import check_python, check_sql
from scripts.content_checks.provenance import inventory
from scripts.course_builder.fetch import fetch_url

ROOT = Path(__file__).resolve().parents[3]
TWO_SUM = ROOT / "data/content-approvals/candidates/two-sum-1.0.1.json"


def lesson_candidate():
    lesson = json.loads((ROOT / "content/ai-engineer/v1/python/syntax-data-types/lesson.json").read_text())
    lesson.update(topic_slug="phase2-example", version="2.0.0", prerequisites=[])
    lesson["sections"] = lesson["sections"][:2]
    for index, section in enumerate(lesson["sections"]):
        section["examples"] = [{"language": "python", "code": "print(1 + 1)", "expected_output": "2", "explanation": "One plus one produces the integer two."}]
    lesson["content_hash"] = digest({k: v for k, v in lesson.items() if k not in {"content_hash", "generated_at"}})
    exercises = [
        {"key": "sum-choice", "exercise_type": "multiple_choice", "title": "Addition", "difficulty": "easy", "prompt_markdown": "What does 1 + 1 produce?", "hints": ["Add two integers."],
         "content": {"choices": ["2", "3"], "correct_index": 0, "answer_text": "2", "assumptions": "Python integer arithmetic", "explanation": "One plus one equals two."}},
        {"key": "sum-explain", "exercise_type": "short_answer", "title": "Explain", "difficulty": "medium", "prompt_markdown": "Explain the addition result.", "hints": [],
         "content": {"reference_answer": "Adding one integer to another integer returns their integer sum.", "rubric": ["Integer operands", "Sum of two"]}},
    ]
    return Candidate(content_key="ai-engineer/v1/python/phase2-example", revision="2.0.0", content_type="lesson_bundle",
        payload={"lesson": lesson, "exercises": exercises},
        provenance={"origin": "original", "author": "TEST ONLY author", "sources": [
            {"source_id": s["source_id"], "url": s["url"], "usage": "factual_reference", "status": "resolved"} for s in lesson["sources"]]},
        coverage={"key": "test-coverage", "version": "1", "competencies": [{"id": "addition", "status": "covered",
            "lesson_refs": ["section/" + lesson["sections"][0]["slug"]], "assessment_refs": ["exercise/sum-choice"]}]},
        example_checks=[{"section_slug": s["slug"], "example_index": 0, "mode": "python", "expected_stdout": "2"} for s in lesson["sections"]])


def approved_package(session, candidate=None, release_id="test-release", topic="backend-engineering/testing"):
    candidate = candidate or lesson_candidate()
    candidate = Candidate.model_validate(candidate)
    report = validate_candidate(candidate)
    review = HumanReview(candidate_sha256=report["candidate_sha256"], validation_sha256=digest(report),
        reviewer="TEST ONLY independent human fixture", reviewed_at=datetime.now(timezone.utc), outcome="approved",
        human_attestation=True, checklist={k: True for k in QUALITY_CHECKS}, notes="Synthetic test approval; never a real editorial claim.")
    curriculum = session.exec(select(m.Curriculum).where(m.Curriculum.version == 1, m.Curriculum.source_type == "default")).one()
    targets = [{"curriculum_name": curriculum.name, "curriculum_version": curriculum.version,
        "graph_sha256": digest(database_graph(session, curriculum)), "topic": topic, "order_index": 0}]
    return {"format_version": 1, "release_id": release_id, "entries": [{"candidate": candidate.model_dump(mode="json"), "validation": report,
        "review": review.model_dump(mode="json"), "targets": targets}]}


def target_topic(session, slug="testing", track="backend-engineering"):
    return session.exec(select(m.Topic).join(m.Track).where(m.Track.slug == track, m.Topic.slug == slug)).first()


def test_exact_candidate_and_invalid_exercises_not_accepted_fallback(tmp_path):
    candidate = lesson_candidate()
    assert validate_candidate(candidate)["editorial_status"] == "awaiting_human_review"
    (tmp_path / "exercises.json").write_text(json.dumps(candidate.payload["exercises"]))
    candidate.payload["exercises"][0]["content"]["correct_index"] = 99
    (tmp_path / "exercises.candidate.json").write_text(json.dumps(candidate.payload["exercises"]))
    with pytest.raises(ValueError, match="MCQ"):
        validate_candidate(candidate)


def test_first_publication_exact_bytes_progress_and_idempotency(session):
    topic = target_topic(session)
    with pytest.raises(ValueError): load_lesson_for_topic(session, topic)
    package = approved_package(session)
    release = publish_release(session, package)
    assert active_release(session) == release.release_id
    lesson = load_lesson_for_topic(session, topic)
    rev = session.get(m.ContentRevision, lesson._registry_id)
    assert load_snapshot(rev) == package["entries"][0]["candidate"]["payload"]
    assert rev.approval_status == "candidate"  # immutable row is never rewritten to approved
    assert len(current_course_exercise_ids(session, topic.id)) == 2
    from app.services.course import lesson_choices
    assert lesson_choices(session, topic)[0]["provenance"] == package["entries"][0]["candidate"]["provenance"]
    assert mark_section(session, topic, lesson.sections[0].slug, True)["completed_sections"] == 1
    before = {table: session.exec(text(f"SELECT COUNT(*) FROM {table}")).scalar() for table in ("contentrevision", "contentreleaseentry", "contentreleaseevent", "exercise")}
    publish_release(session, package)
    assert before == {table: session.exec(text(f"SELECT COUNT(*) FROM {table}")).scalar() for table in before}
    for table in ("contentrevision", "contentvalidationreport", "contentreviewrecord", "approvedcontentrelease", "contentreleaseentry", "contentreleaseevent"):
        with pytest.raises(Exception, match="immutable|append-only"):
            session.exec(text(f"DELETE FROM {table}"))
        session.rollback()


@pytest.mark.parametrize("change", ["unreviewed", "stale_content", "stale_report", "semantic", "rejected", "partial"])
def test_publication_rejects_missing_stale_or_unreviewed_approval(session, change):
    package = approved_package(session)
    entry = package["entries"][0]
    if change == "unreviewed": entry["review"] = {}
    if change == "stale_content": entry["candidate"]["payload"]["exercises"][0]["title"] = "Changed"
    if change == "stale_report": entry["validation"]["execution"] = []
    if change == "semantic": entry["review"]["checklist"]["semantic_answers"] = False
    if change == "rejected": entry["review"]["outcome"] = "rejected"
    if change == "partial":
        entry["validation"]["coverage"][0]["status"] = "partially_covered"
        entry["review"]["validation_sha256"] = digest(entry["validation"])
    with pytest.raises((ValueError, KeyError)):
        publish_release(session, package)
    assert not session.exec(select(m.ApprovedContentRelease)).all()
    assert active_release(session) is None


def test_publication_failure_rolls_back_all_visibility(session, monkeypatch):
    package = approved_package(session)
    from app.services import course
    monkeypatch.setattr(course, "rebuild_search_index", lambda *a, **k: (_ for _ in ()).throw(OSError("disk fault")))
    with pytest.raises(OSError, match="disk fault"):
        publish_release(session, package)
    for model in (m.ContentRevision, m.ContentReviewRecord, m.ContentValidationReport, m.ContentReleaseEntry, m.ApprovedContentRelease):
        assert not session.exec(select(model)).all()
    assert active_release(session) is None


def test_old_new_revisions_arena_history_and_revocation(session):
    sync_problem_bank(session)
    old = problem_revision(session, "dsa-two-sum-indices")
    result = record_attempt(session, "dsa-two-sum-indices", ArenaAttemptRequest(source="def two_sum(nums, target): return [0,0]", passed=False, score=0, content_revision_id=old.id))
    attempt_id = result["attempt_id"]
    historical = session.get(m.ArenaAttempt, attempt_id).model_dump()
    evidence = [e.model_dump() for e in session.exec(select(m.MasteryEvidenceEvent))]
    package = approved_package(session, json.loads(TWO_SUM.read_text()), "two-sum-test", "dsa/hash-maps")
    publish_release(session, package)
    new = problem_revision(session, "dsa-two-sum-indices")
    assert new.id != old.id and new.revision == "1.0.1"
    assert not public_problem(session, session.get(m.ArenaProblem, "dsa-two-sum-indices"))["solved"]
    assert load_problem("dsa-two-sum-indices", session=session, revision_id=old.id).version == "1.0.0"
    assert session.get(m.ArenaProblem, "dsa-two-sum-indices").version == "1.0.0"
    assert session.get(m.ArenaTopicBinding, (1, "dsa-two-sum-indices")).content_revision_id == old.id
    assert session.get(m.ArenaAttemptContent, attempt_id).content_revision_id == old.id
    assert session.get(m.ArenaAttempt, attempt_id).model_dump() == historical
    assert [e.model_dump() for e in session.exec(select(m.MasteryEvidenceEvent))] == evidence
    with pytest.raises(ValueError, match="release changed"):
        record_attempt(session, "dsa-two-sum-indices", ArenaAttemptRequest(source="# stale", passed=False, score=0, content_revision_id=old.id))
    with pytest.raises(ValueError, match="exact content_revision_id"):
        record_attempt(session, "dsa-two-sum-indices", ArenaAttemptRequest(source="# missing identity", passed=False, score=0))
    transition_release(session, "two-sum-test", "revoked", "TEST reviewer", "Rollback test")
    assert problem_revision(session, "dsa-two-sum-indices").id == old.id
    assert load_snapshot(new)["problem"]["version"] == "1.0.1"
    publish_release(session, package)  # repeat must not undo revocation
    assert active_release(session) is None


def test_new_lesson_revision_retains_old_revision_and_progress(session):
    first = approved_package(session)
    publish_release(session, first)
    topic = target_topic(session)
    old = load_lesson_for_topic(session, topic)
    candidate = lesson_candidate()
    candidate.revision = candidate.payload["lesson"]["version"] = "2.0.1"
    candidate.payload["lesson"]["content_hash"] = digest({k: v for k, v in candidate.payload["lesson"].items() if k not in {"content_hash", "generated_at"}})
    second = approved_package(session, candidate, "second-release")
    publish_release(session, second)
    assert load_lesson_for_topic(session, topic).version == "2.0.1"
    assert load_lesson_for_topic(session, topic, old._registry_id).version == "2.0.0"
    from app.services.course import lesson_choices
    assert lesson_choices(session, topic)[0]["order_index"] == 0
    changed = copy.deepcopy(second)
    changed["entries"][0]["candidate"]["payload"]["lesson"]["title"] = "Changed"
    with pytest.raises(ValueError, match="immutable"):
        publish_release(session, changed)
    candidate.provenance["note"] = "Changed attribution with identical lesson bytes"
    changed_provenance = approved_package(session, candidate, "changed-provenance")
    with pytest.raises(ValueError, match="provenance changed"):
        publish_release(session, changed_provenance)
    assert active_release(session) == "second-release"


def test_fresh_install_archive_reconstructs_verified_snapshots(session, tmp_path, monkeypatch):
    package = approved_package(session)
    archive = write_immutable(tmp_path / "tracked-release.json", package)
    engine = create_engine("sqlite://")
    run_migrations(engine)
    from app.services.curriculum import seed_default_curriculum
    monkeypatch.setattr(settings, "content_snapshot_path", tmp_path / "fresh-snapshots")
    with Session(engine) as fresh:
        seed_default_curriculum(fresh, ROOT / "data/default-ai-engineer-curriculum.json")
        publish_release(fresh, json.loads(archive.read_text(encoding="utf-8")), archive_path=archive)
        verify_release_snapshots(fresh)
        assert load_lesson_for_topic(fresh, target_topic(fresh)).version == "2.0.0"
    engine.dispose()


def test_python_output_types_exceptions_and_capabilities():
    with pytest.raises(ValueError, match="stdout mismatch"):
        check_python({"code": "print(2)"}, {"expected_stdout": "3"})
    with pytest.raises(ValueError, match="typed return mismatch"):
        check_python({"code": "def f(): return (0, 1)", "function_name": "f"}, {"expected": [0, 1]})
    with pytest.raises(ValueError, match="Reference raised"):
        check_python({"code": "raise ValueError('wrong')"}, {"expected_stdout": ""})
    with pytest.raises(ValueError, match="EOFError"):
        check_python({"code": "print(input())"}, {"expected_stdout": ""})
    for code in ("import socket", "open('forge.db')", "import os", "print((1).__class__)",
                 "import re; re.sys.modules['os'].stat('forge.db')", "import string; print(string.Formatter())", "while True: pass"):
        with pytest.raises(ValueError): check_python({"code": code}, {"expected_stdout": ""})


def test_sql_rows_columns_duplicates_nulls_order_and_alternate_datasets():
    fixture = {"query": "SELECT x FROM t ORDER BY x NULLS LAST", "setup_sql": "CREATE TABLE t(x int); INSERT INTO t VALUES (1),(1),(NULL)",
        "expected_columns": ["x"], "expected_rows": [[1], [1], [None]], "order_sensitive": True,
        "alternate_datasets": [{"setup_sql": "CREATE TABLE t(x int); INSERT INTO t VALUES (2),(NULL)", "expected_rows": [[2], [None]]}]}
    check_sql(fixture)
    for field, wrong in (("expected_columns", ["wrong"]), ("expected_rows", [[1], [None]]), ("expected_rows", [[None], [1], [1]])):
        with pytest.raises(ValueError, match="SQL example mismatch"):
            check_sql({**fixture, field: wrong})


def test_two_sum_full_contract_and_negative_specification(tmp_path):
    from scripts.problem_builder.validate import validate_problem
    candidate = Candidate.model_validate_json(TWO_SUM.read_text())
    report = validate_candidate(candidate)
    assert report["execution"]["tests"] == 10 and report["execution"]["negative_solutions"] == 2
    raw = candidate.payload["problem"]
    path = tmp_path / "two-sum.json"
    path.write_text(json.dumps(raw))
    assert validate_problem(path).version == "1.0.1"
    for change in ("reference", "display", "parameter", "constraint", "hidden"):
        wrong = copy.deepcopy(raw)
        if change == "reference": wrong["reference_solution"] = wrong["negative_solutions"][0]
        if change == "display": wrong["examples"][0]["output"] = "(0, 1)"
        if change == "parameter": wrong["starter_code"] = wrong["starter_code"].replace("target: int", "total: int")
        if change == "constraint": wrong["constraints"] = ["Unspecified"]
        if change == "hidden": wrong["validation"]["hidden_tests"][0]["expected"] = [0, 0]
        path.write_text(json.dumps(wrong))
        with pytest.raises(ValueError): validate_problem(path)


def test_provenance_round_trip_and_license_policy(session):
    raw = json.loads((ROOT / "content/problem-bank/python/python-bob.json").read_text())
    serialized = CodingProblem.model_validate(raw).model_dump()
    assert all(serialized[k] == raw[k] for k in ("source_project", "source_exercise", "license", "adapted"))
    sync_problem_bank(session)
    public = public_problem(session, session.get(m.ArenaProblem, "python-bob"))
    assert public["source_type"] == "adapted" and public["declared_source_type"] == "original"
    assert public["provenance"]["legacy_metadata"]["license"] == "MIT"
    report = inventory(ROOT / "content/problem-bank")
    assert len(report["problems"]) == 110
    assert sum(p["classification"] == "adapted" for p in report["problems"]) == 9
    candidate = lesson_candidate()
    candidate.provenance["sources"][0].update(usage="redistributed", license="MIT")
    with pytest.raises(ValueError, match="license/notice"):
        validate_candidate(candidate)
    candidate = Candidate.model_validate_json(TWO_SUM.read_text())
    candidate.payload["problem"].update(adapted=True, source_project="exercism")
    with pytest.raises(ValueError, match="Adapted"):
        validate_candidate(candidate)


def test_source_redirect_dns_robots_and_cache_integrity(tmp_path, monkeypatch):
    from scripts.course_builder import fetch
    monkeypatch.setattr(fetch.socket, "getaddrinfo", lambda *a, **k: [(None, None, None, None, ("93.184.216.34", 443))])
    source = {"id": "test-source", "base_url": "https://example.test/docs/", "allowed_paths": ["/docs/"], "enabled": True}
    requests = []
    def handler(request):
        requests.append(str(request.url))
        if request.url.path == "/docs/start": return httpx.Response(302, headers={"location": "/docs/final"})
        return httpx.Response(200, text="Content")
    with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
        record = fetch_url("https://example.test/docs/start", source, tmp_path, client=client, robots_text="User-agent: *\nAllow: /")
        assert record["final_url"] == "https://example.test/docs/final"
        assert fetch_url(record["url"], source, tmp_path, client=client, robots_text="User-agent: *\nAllow: /") == record
        assert len(requests) == 2
        cache = next(tmp_path.glob("*.json"))
        bad = json.loads(cache.read_text());bad["html"] = "Corrupt";cache.write_text(json.dumps(bad))
        with pytest.raises(ValueError, match="integrity"):
            fetch_url(record["url"], source, tmp_path, client=client, robots_text="User-agent: *\nAllow: /")
    for destination in ("https://other.test/docs/x", "https://example.test/private", "http://example.test/docs/x", "https://127.0.0.1/docs/x", "https://example.test/docs/%2e%2e/private"):
        with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(302, headers={"location": destination}))) as client:
            with pytest.raises(ValueError):
                fetch_url("https://example.test/docs/start", source, tmp_path / "bad", client=client, robots_text="User-agent: *\nAllow: /")
    monkeypatch.setattr(fetch.socket, "getaddrinfo", lambda *a, **k: [(None,None,None,None,("127.0.0.1",443))])
    with pytest.raises(ValueError, match="private"):
        fetch_url("https://example.test/docs/start", source, tmp_path)


def test_phase1_to_phase2_upgrade_preserves_frozen_checksums_and_bindings(tmp_path):
    from app.migrations import runner, v001_legacy_schema, v002_content_bindings
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        v001_legacy_schema.apply(connection)
        ledger = next(t for t in json.loads(v002_content_bindings.SCHEMA.read_text()) if t["name"] == "schemamigration")
        connection.exec_driver_sql(ledger["sql"])
        v002_content_bindings.apply(connection)
        for migration in runner.MIGRATIONS[:2]:
            connection.exec_driver_sql("INSERT INTO schemamigration VALUES (?,?,?,?)", (migration.version,migration.name,migration.checksum,"2026-10-20"))
        before = connection.exec_driver_sql("SELECT * FROM schemamigration").all()
    assert run_migrations(engine)["applied"] == [3, 4, 5, 6]
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT * FROM schemamigration WHERE version<3").all() == before
        assert connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE name='arenatopicbinding_type'").first()
    engine.dispose()


def test_coverage_reports_exact_references_and_unverified_states():
    from scripts.content_checks.coverage import check_coverage
    candidate = lesson_candidate()
    for state in ("covered", "partially_covered", "missing", "requires_review"):
        candidate.coverage["competencies"][0]["status"] = state
        assert check_coverage(candidate)[0]["status"] == state
    candidate.coverage["competencies"][0]["lesson_refs"] = ["section/missing"]
    with pytest.raises(ValueError, match="dangling"):
        check_coverage(candidate)


def test_source_redirect_bounds_robots_and_source_restrictions(tmp_path, monkeypatch):
    from scripts.course_builder import fetch
    monkeypatch.setattr(fetch.socket, "getaddrinfo", lambda *a, **k: [(None,None,None,None,("93.184.216.34",443))])
    source = {"id":"test", "base_url":"https://example.test/docs/", "allowed_paths":["/docs/"], "enabled":True}
    requests = []
    def loop(request):
        requests.append(request.url)
        return httpx.Response(302, headers={"location":"/docs/loop"})
    with httpx.Client(transport=httpx.MockTransport(loop)) as client:
        with pytest.raises(ValueError, match="Redirect count"):
            fetch_url("https://example.test/docs/loop", source, tmp_path, client=client, robots_text="User-agent: *\nAllow: /")
        assert len(requests) == 6
        with pytest.raises(PermissionError, match="robots"):
            fetch_url("https://example.test/docs/loop", source, tmp_path, client=client, robots_text="User-agent: *\nDisallow: /")
        with pytest.raises(PermissionError):
            fetch_url("https://example.test/docs/loop", {**source, "category":"reference_only"}, tmp_path, client=client)


def test_stale_canonical_lesson_hash_and_unresolved_prerequisite(session):
    candidate = lesson_candidate()
    candidate.payload["lesson"]["summary"] = ["Changed after hashing"]
    with pytest.raises(ValueError, match="canonical content_hash"):
        validate_candidate(candidate)
    candidate = lesson_candidate()
    candidate.payload["lesson"]["prerequisites"] = ["ai-engineer/v1/python/missing"]
    candidate.prerequisite_keys = list(candidate.payload["lesson"]["prerequisites"])
    candidate.payload["lesson"]["content_hash"] = digest({k:v for k,v in candidate.payload["lesson"].items() if k not in {"content_hash","generated_at"}})
    package = approved_package(session, candidate)
    with pytest.raises(ValueError, match="unresolved prerequisite"):
        publish_release(session, package)


def test_legacy_promoters_cannot_replace_accepted_files():
    from scripts.course_builder.promote import promote as promote_lesson
    from scripts.problem_builder.promote import promote as promote_problem
    lesson_path = ROOT / "content/ai-engineer/v1/python/syntax-data-types/lesson.json"
    problem_path = ROOT / "content/problem-bank/dsa/dsa-two-sum-indices.json"
    before = lesson_path.read_bytes(), problem_path.read_bytes()
    with pytest.raises(ValueError, match="human review"):
        promote_lesson("python", "syntax-data-types")
    with pytest.raises(ValueError, match="human review"):
        promote_problem("dsa", "dsa-two-sum-indices")
    assert before == (lesson_path.read_bytes(), problem_path.read_bytes())


def test_one_lesson_can_publish_to_multiple_topics_in_same_curriculum(session, tmp_path):
    from scripts.content_checks.publish import publish_package
    package = approved_package(session)
    targets = package["entries"][0]["targets"]
    targets.append({**targets[0], "topic":"backend-engineering/debugging"})
    # This confirmed curriculum has testing and error-handling, not a debugging topic.
    targets[1]["topic"] = "backend-engineering/error-handling"
    archive = write_immutable(tmp_path / "multi-release.json", package)
    publish_package(archive, session)
    assert len(session.exec(select(m.ContentReleaseEntry)).all()) == 2
    assert load_lesson_for_topic(session, target_topic(session, "error-handling")).version == "2.0.0"


def test_typed_dict_comparison_is_order_independent():
    check_python({"code":"def f(): return {'second': 2, 'first': 1}", "function_name":"f"},
                 {"expected":{"first":1,"second":2}})


def test_pinned_transport_preserves_sni_and_host(monkeypatch):
    from scripts.course_builder import fetch
    captured = []
    monkeypatch.setattr(fetch, "public_addresses", lambda host: ["93.184.216.34"])
    def handle(self, request):
        captured.append(request)
        return httpx.Response(200, request=request)
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", handle)
    with fetch.PinnedTransport() as transport:
        transport.handle_request(httpx.Request("GET","https://example.test/docs/x"))
    request = captured[0]
    assert request.url.host == "93.184.216.34"
    assert request.headers["Host"] == "example.test"
    assert request.extensions["sni_hostname"] == "example.test"


def test_fresh_install_cli_restores_tracked_archive(session, tmp_path):
    import os
    import sqlite3
    import subprocess
    import sys
    package = approved_package(session)
    archive = write_immutable(tmp_path / "synthetic-reviewed-release.json", package)
    destination = tmp_path / "fresh.db"
    environment = {**os.environ, "GEMINI_API_KEY":"", "FORGE_DATABASE_URL":"sqlite:///:memory:",
        "FORGE_CONTENT_SNAPSHOT_PATH":str(tmp_path / "restored-snapshots"),
        "FORGE_DATABASE_BACKUP_PATH":str(tmp_path / "restored-backups")}
    result = subprocess.run([sys.executable, "-m", "scripts.content_checks.publish", "restore", "--package", str(archive),
        "--database", str(destination)], cwd=ROOT / "apps/api", env=environment, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    with sqlite3.connect(destination.as_uri() + "?mode=ro", uri=True) as connection:
        assert connection.execute("SELECT count(*) FROM schemamigration").fetchone()[0] == 6
        assert connection.execute("SELECT count(*) FROM contentrevision").fetchone()[0] == 164
        assert connection.execute("SELECT count(*) FROM exercise").fetchone()[0] == 702
        assert connection.execute("SELECT value FROM appsetting WHERE key='active_curriculum_id'").fetchone()[0] == "2"
        assert connection.execute("SELECT count(*) FROM arenaattempt").fetchone()[0] == 0
