import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.database import get_session
from app.main import app
from app.models import AppSetting, ArenaAttempt, ArenaProblem, Topic
from app.services.learning_path import (
    check_prerequisites_met,
    derive_step_action,
    evaluate_beginner_exercise,
    get_all_concepts_summary,
    get_arena_stages_detail,
    get_beginner_exercise,
    get_concept_step_progress,
    get_learning_path_dashboard,
    get_subject_progress_summaries,
    load_arena_stages_manifest,
    load_beginner_exercises_manifest,
    load_concept_steps_manifest,
    set_concept_step_progress,
)


def test_concept_steps_manifest_integrity():
    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])
    assert len(concepts) >= 25
    step_keys = {c["key"] for c in concepts}
    assert len(step_keys) == len(concepts), "Duplicate step keys detected"

    # All 9 Placement Foundations subjects must be represented
    subjects = {c["subject_key"] for c in concepts}
    expected_subjects = {
        "python",
        "sql-postgresql",
        "dsa",
        "quantitative-aptitude",
        "logical-reasoning",
        "verbal-english",
        "system-design",
        "ai-fundamentals",
        "interview-communication",
    }
    assert expected_subjects.issubset(subjects), f"Missing subjects: {expected_subjects - subjects}"

    # Verify no dangling prerequisites
    for c in concepts:
        for prereq in c.get("prerequisite_keys", []):
            assert prereq in step_keys, f"Dangling prerequisite {prereq} in step {c['key']}"

    # Topological sort cycle check
    visited = set()
    visiting = set()
    concept_dict = {c["key"]: c for c in concepts}

    def check_cycle(k: str):
        if k in visiting:
            raise AssertionError(f"Prerequisite cycle detected involving {k}")
        if k in visited:
            return
        visiting.add(k)
        for p in concept_dict[k].get("prerequisite_keys", []):
            check_cycle(p)
        visiting.remove(k)
        visited.add(k)

    for k in concept_dict:
        check_cycle(k)


def test_arena_stages_manifest_integrity():
    manifest = load_arena_stages_manifest()
    stages = manifest.get("stages", [])
    mappings = manifest.get("problem_mappings", {})

    assert len(stages) == 5
    stage_keys = [s["key"] for s in stages]
    assert stage_keys == ["first_steps", "beginner", "developing", "intermediate", "challenging"]

    # Exactly 110 original problems (40 Python, 30 SQL, 40 DSA) must be preserved and mapped
    assert len(mappings) == 110

    # Every problem in mapping has a valid stage and concept tag
    for p_key, meta in mappings.items():
        assert meta.get("stage") in stage_keys
        assert meta.get("concept")
        assert "prerequisites" in meta


def test_beginner_exercises_integrity():
    manifest = load_beginner_exercises_manifest()
    exercises = manifest.get("exercises", [])
    assert len(exercises) >= 14
    for ex in exercises:
        assert ex["key"]
        assert ex["track"] in ("python", "sql", "dsa")
        assert ex["stage"] == "first_steps"
        assert ex["title"]
        assert "instructions" in ex
        assert "explanation" in ex
        assert len(ex.get("hints", [])) >= 1


def test_deterministic_recommendations_and_stability(session: Session):
    # Initial dashboard call
    d1 = get_learning_path_dashboard(session, active_subject="python")
    assert d1.primary_recommendation is not None
    assert d1.primary_recommendation.subject_key == "python"
    assert d1.primary_recommendation.concept_key == "step-py-values-1"
    assert d1.primary_recommendation.priority_tier == 4  # next concept
    assert len(d1.secondary_recommendations) <= 3
    assert len(d1.subjects) == 9

    # Re-calling dashboard must be deterministic and identical across refreshes
    d2 = get_learning_path_dashboard(session, active_subject="python")
    assert d2.primary_recommendation.concept_key == d1.primary_recommendation.concept_key
    assert d2.primary_recommendation.priority_tier == d1.primary_recommendation.priority_tier
    assert [r.concept_key for r in d2.secondary_recommendations] == [r.concept_key for r in d1.secondary_recommendations]


def test_recommendation_priority_tier_1_resume_unfinished(session: Session):
    # Set step-py-values-1 to learning
    set_concept_step_progress(session, "step-py-values-1", "learning")

    dashboard = get_learning_path_dashboard(session, active_subject="python")
    primary = dashboard.primary_recommendation
    assert primary is not None
    assert primary.priority_tier == 1  # Resume unfinished work
    assert primary.concept_key == "step-py-values-1"
    assert primary.kind == "resume"
    assert primary.action_label in ("Resume learning", "Resume exercise", "Resume concept")


def test_recommendation_priority_tier_2_due_review(session: Session):
    # Set step-py-values-1 to review_due
    set_concept_step_progress(session, "step-py-values-1", "review_due")

    dashboard = get_learning_path_dashboard(session, active_subject="python")
    primary = dashboard.primary_recommendation
    assert primary is not None
    assert primary.priority_tier == 2  # Review due
    assert primary.concept_key == "step-py-values-1"
    assert primary.kind == "review"
    assert primary.action_label == "Review now"


def test_progress_update_persists_without_fabricating_mastery(session: Session):
    # Client cannot arbitrarily jump to ready_to_advance without evidence
    with pytest.raises(ValueError, match="Cannot advance concept"):
        set_concept_step_progress(session, "step-py-values-1", "ready_to_advance")

    # Marking learning state persists
    set_concept_step_progress(session, "step-py-values-1", "learning")
    setting = session.get(AppSetting, "lp_step_state:step-py-values-1")
    assert setting is not None
    assert setting.value == "learning"

    concepts = get_all_concepts_summary(session)
    step = next(c for c in concepts if c.key == "step-py-values-1")
    assert step.progress_state == "learning"


def test_beginner_exercise_grading_python_pass(session: Session):
    result = evaluate_beginner_exercise(
        session,
        "py-first-print-message",
        'def say_hello():\n    return "Hello, Forge!"',
    )
    assert result.passed is True
    assert result.score == 100.0
    assert result.solution is not None  # Revealed on pass
    assert "passed" in result.output.lower()

    # Verify exercise now shows as solved
    ex = get_beginner_exercise(session, "py-first-print-message")
    assert ex is not None
    assert ex.solved is True


def test_beginner_exercise_grading_python_fail(session: Session):
    result = evaluate_beginner_exercise(
        session,
        "py-first-add-two",
        'def add_numbers(a, b):\n    return a - b',  # Incorrect subtraction
    )
    assert result.passed is False
    assert result.score < 100.0
    # Reference solution MUST be hidden on failure
    assert result.solution is None


def test_beginner_exercise_grading_sql_pass(session: Session):
    result = evaluate_beginner_exercise(
        session,
        "sql-first-select-constant",
        "SELECT 42 AS answer;",
    )
    assert result.passed is True
    assert result.score == 100.0
    assert result.solution is not None


def test_api_learning_path_endpoints(session: Session):
    try:
        app.dependency_overrides[get_session] = lambda: session
        client = TestClient(app)

        # 1. Dashboard
        resp = client.get("/api/learning-path/dashboard?active_subject=python")
        assert resp.status_code == 200
        data = resp.json()
        assert "primary_recommendation" in data
        assert "secondary_recommendations" in data
        assert "subjects" in data
        assert len(data["subjects"]) == 9
        assert data["content_availability"]["legacy_reference_lessons"] == 53

        # 2. Arena stages
        resp = client.get("/api/learning-path/arena/stages")
        assert resp.status_code == 200
        stages = resp.json()
        assert len(stages) == 5

        # 3. Exercise detail before solve
        resp = client.get("/api/learning-path/exercises/py-first-even-odd")
        assert resp.status_code == 200
        ex = resp.json()
        assert ex["solved"] is False

        # 4. Update concept progress (learning)
        resp = client.post("/api/learning-path/steps/step-py-values-1/progress?state=learning")
        assert resp.status_code == 200
        assert resp.json()["progress_state"] == "learning"

        # 5. Submit exercise with correct function name
        resp = client.post(
            "/api/learning-path/exercises/py-first-even-odd/submit",
            json={"source": "def even_or_odd(n):\n    return 'even' if n % 2 == 0 else 'odd'"},
        )
        assert resp.status_code == 200
        sub_res = resp.json()
        assert sub_res["passed"] is True
        assert sub_res["solution"] is not None
    finally:
        app.dependency_overrides.pop(get_session, None)


# --- REGRESSION TESTS FOR AUDIT HARDENING ---


def test_beginner_exercise_sql_incorrect_syntax_and_values(session: Session):
    # 1. Syntax error must fail
    res_syntax = evaluate_beginner_exercise(
        session, "sql-first-select-constant", "SELECT FROM table;"
    )
    assert res_syntax.passed is False
    assert res_syntax.score == 0.0

    # 2. Wrong column alias must fail
    res_col = evaluate_beginner_exercise(
        session, "sql-first-select-constant", "SELECT 42 AS wrong_name;"
    )
    assert res_col.passed is False
    assert res_col.score == 0.0

    # 3. Wrong row value must fail even if starts with SELECT
    res_val = evaluate_beginner_exercise(
        session, "sql-first-select-constant", "SELECT 99 AS answer;"
    )
    assert res_val.passed is False
    assert res_val.score == 0.0
    assert res_val.solution is None

    # 4. SQL with table fixture: wrong condition must fail
    res_fixture_fail = evaluate_beginner_exercise(
        session, "sql-first-where", "SELECT name FROM users WHERE is_active = false;"
    )
    assert res_fixture_fail.passed is False
    assert res_fixture_fail.score == 0.0

    # 5. Correct query must pass
    res_fixture_pass = evaluate_beginner_exercise(
        session, "sql-first-where", "SELECT name FROM users WHERE is_active = true;"
    )
    assert res_fixture_pass.passed is True
    assert res_fixture_pass.score == 100.0


def test_beginner_exercise_python_infinite_loop_and_banned_builtins(session: Session):
    # 1. Infinite loop must be killed within bounded worker timeout and fail
    res_loop = evaluate_beginner_exercise(
        session,
        "py-first-add-two",
        "def add_numbers(a, b):\n    while True:\n        pass",
    )
    assert res_loop.passed is False
    assert res_loop.score == 0.0
    assert res_loop.solution is None

    # 2. Banned builtins like open() must be rejected
    res_banned = evaluate_beginner_exercise(
        session,
        "py-first-add-two",
        "def add_numbers(a, b):\n    open('secret.txt', 'w')\n    return a + b",
    )
    assert res_banned.passed is False
    assert res_banned.score == 0.0


def test_recommendation_urls_are_resolvable(session: Session):
    valid_prefixes = (
        "/arena/exercises/",
        "/arena/problems/",
        "/topics/",
        "/curriculum",
        "/review",
        "/practice",
        "/concepts/",
    )
    subjects = [
        "python",
        "sql-postgresql",
        "dsa",
        "quantitative-aptitude",
        "logical-reasoning",
        "verbal-english",
        "system-design",
        "ai-fundamentals",
        "interview-communication",
    ]
    for sub in subjects:
        dash = get_learning_path_dashboard(session, active_subject=sub)
        if dash.primary_recommendation:
            path = dash.primary_recommendation.action_path
            assert any(path.startswith(prefix) for prefix in valid_prefixes), (
                f"Subject {sub} primary recommendation generated invalid URL: {path}"
            )
            assert not path.startswith("/learn/step-"), f"Broken route generated: {path}"

        for sec in dash.secondary_recommendations:
            path = sec.action_path
            assert any(path.startswith(prefix) for prefix in valid_prefixes), (
                f"Subject {sub} secondary recommendation generated invalid URL: {path}"
            )


def test_unpublished_candidate_lessons_not_claimed_available(session: Session):
    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])

    # Step in quantitative aptitude has no bound lessons and no beginner exercises
    quant_step = next(c for c in concepts if c["subject_key"] == "quantitative-aptitude")
    _, _, has_usable = derive_step_action(session, quant_step, "not_started")
    assert has_usable is False

    try:
        app.dependency_overrides[get_session] = lambda: session
        client = TestClient(app)
        resp = client.get(f"/api/learning-path/steps/{quant_step['key']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["availability_status"] == "candidate_unreviewed"
        assert data["availability_status"] != "available"
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_false_readiness_prevented_without_verified_evidence(session: Session):
    try:
        app.dependency_overrides[get_session] = lambda: session
        client = TestClient(app)

        # 1. API endpoint rejects ready_to_advance when evidence is missing
        resp = client.post("/api/learning-path/steps/step-py-values-1/progress?state=ready_to_advance")
        assert resp.status_code == 400
        assert "Cannot advance concept" in resp.json()["detail"]

        # 2. Service level raises ValueError
        manifest = load_concept_steps_manifest()
        concept = next(c for c in manifest.get("concepts", []) if c["key"] == "step-py-values-1")
        assert get_concept_step_progress(session, concept) == "not_started"

        with pytest.raises(ValueError):
            set_concept_step_progress(session, "step-py-values-1", "ready_to_advance")

        # 3. Supply genuine verified evidence: solve all guided exercises + pass independent problem
        from app.services.arena import sync_problem_bank
        sync_problem_bank(session)

        for g in concept.get("guided_practice_refs", []):
            session.add(AppSetting(key=f"lp_ex_solved:{g}", value="true"))
        for p in concept.get("independent_practice_refs", []):
            session.add(
                ArenaAttempt(
                    problem_key=p,
                    track="python",
                    submitted_source="def solution(): pass",
                    passed=True,
                    score=100.0,
                )
            )
        session.commit()

        # 4. Now evidence-derived state advances to ready_to_advance
        assert get_concept_step_progress(session, concept) == "ready_to_advance"

        # 5. API call succeeds now that evidence is present
        resp = client.post("/api/learning-path/steps/step-py-values-1/progress?state=ready_to_advance")
        assert resp.status_code == 200
        assert resp.json()["progress_state"] == "ready_to_advance"
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_prerequisite_violations_prevent_advancing(session: Session):
    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])
    step_2 = next(c for c in concepts if c["key"] == "step-py-values-2")
    assert "step-py-values-1" in step_2.get("prerequisite_keys", [])

    progress_by_key = {c["key"]: "not_started" for c in concepts}

    # Prerequisites unmet initially
    assert check_prerequisites_met(step_2, progress_by_key) is False

    # When step 2 is active, recommendation engine elevates prerequisite step 1
    progress_by_key["step-py-values-2"] = "learning"
    set_concept_step_progress(session, "step-py-values-2", "learning")

    dashboard = get_learning_path_dashboard(session, active_subject="python")
    # Priority 3 elevates missing prerequisite
    prereq_rec = next((r for r in dashboard.secondary_recommendations if r.kind == "prerequisite"), None)
    if dashboard.primary_recommendation.kind == "prerequisite":
        prereq_rec = dashboard.primary_recommendation
    assert prereq_rec is not None
    assert prereq_rec.concept_key == "step-py-values-1"

    # Once prerequisite is ready_to_advance, check_prerequisites_met succeeds
    progress_by_key["step-py-values-1"] = "ready_to_advance"
    assert check_prerequisites_met(step_2, progress_by_key) is True


def test_concept_teaching_content_schema_and_detail_endpoint(session: Session):
    try:
        app.dependency_overrides[get_session] = lambda: session
        client = TestClient(app)

        # GET /api/learning-path/steps/step-py-values-1
        resp = client.get("/api/learning-path/steps/step-py-values-1")
        assert resp.status_code == 200
        data = resp.json()

        assert data["key"] == "step-py-values-1"
        assert data["subject_key"] == "python"
        assert data["title"] == "Values, variables and basic types"
        assert data["action_path"] == "/concepts/step-py-values-1"
        assert data["action_label"] == "Learn concept"

        # Teaching content presence
        tc = data.get("teaching_content")
        assert tc is not None, "Teaching content must be present on concept step"
        assert "summary" in tc and len(tc["summary"]) > 20
        assert "why_it_matters" in tc
        assert "intuition" in tc
        assert "analogy" in tc
        assert "syntax_guide" in tc
        assert "worked_example_title" in tc
        assert "worked_example_code" in tc
        assert "worked_example_explanation" in tc

        # Step-by-step trace
        assert len(tc["tracing_steps"]) >= 3
        for trace in tc["tracing_steps"]:
            assert trace["step_number"] >= 1
            assert trace["line_or_expression"]
            assert trace["state_description"]

        # Common beginner mistakes
        assert len(tc["common_mistakes"]) >= 2
        for mistake in tc["common_mistakes"]:
            assert mistake["mistake_description"]
            assert mistake["wrong_code"]
            assert mistake["correct_code"]

        # Revision notes
        assert len(tc["revision_notes"]) >= 3
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_revision_aware_exercise_fingerprint(session: Session):
    from app.services.learning_path import (
        get_exercise_fingerprint,
        is_beginner_exercise_solved,
    )
    manifest = load_beginner_exercises_manifest()
    ex = manifest["exercises"][0]
    fp = get_exercise_fingerprint(ex)
    assert len(fp) == 16

    # Initially unsolved
    assert is_beginner_exercise_solved(session, ex["key"], ex) is False

    # Submit valid solution
    res = evaluate_beginner_exercise(session, ex["key"], ex["reference_solution"])
    assert res.passed is True
    assert res.score == 100.0

    # Solved setting stored with fingerprint
    assert session.get(AppSetting, f"lp_ex_solved:{ex['key']}:{fp}") is not None
    assert is_beginner_exercise_solved(session, ex["key"], ex) is True

    # If exercise contract changes materially, previous solve does NOT grant credit to altered version
    altered_ex = dict(ex)
    altered_ex["instructions"] = "Altered instructions that change contract."
    altered_fp = get_exercise_fingerprint(altered_ex)
    assert altered_fp != fp
    assert is_beginner_exercise_solved(session, ex["key"], altered_ex) is False


def test_unassisted_independent_attempt_qualification(session: Session):
    from app.services.learning_path import is_qualified_independent_attempt
    from app.services.arena import sync_problem_bank
    sync_problem_bank(session)

    # 1. Clean unassisted passing attempt -> Qualifies
    clean_attempt = ArenaAttempt(
        problem_key="python-two-fer",
        track="python",
        submitted_source="def solution(): pass",
        passed=True,
        score=100.0,
        hints_used=0,
        gave_up=False,
    )
    session.add(clean_attempt)
    session.commit()
    assert is_qualified_independent_attempt(session, clean_attempt, "python-two-fer") is True

    # 2. Assisted attempt (hints_used > 0) -> Fails qualification
    assisted_attempt = ArenaAttempt(
        problem_key="python-two-fer",
        track="python",
        submitted_source="def solution(): pass",
        passed=True,
        score=100.0,
        hints_used=1,
        gave_up=False,
    )
    session.add(assisted_attempt)
    session.commit()
    assert is_qualified_independent_attempt(session, assisted_attempt, "python-two-fer") is False

    # 3. Gave up attempt -> Fails qualification
    gave_up_attempt = ArenaAttempt(
        problem_key="python-two-fer",
        track="python",
        submitted_source="# gave up",
        passed=False,
        score=0.0,
        hints_used=0,
        gave_up=True,
    )
    session.add(gave_up_attempt)
    session.commit()
    assert is_qualified_independent_attempt(session, gave_up_attempt, "python-two-fer") is False

    # 4. Partial score (< 100.0) -> Fails qualification
    partial_attempt = ArenaAttempt(
        problem_key="python-two-fer",
        track="python",
        submitted_source="def solution(): pass",
        passed=False,
        score=66.7,
        hints_used=0,
        gave_up=False,
    )
    session.add(partial_attempt)
    session.commit()
    assert is_qualified_independent_attempt(session, partial_attempt, "python-two-fer") is False


def test_prerequisite_blocker_caps_at_practising(session: Session):
    from app.services.arena import sync_problem_bank
    sync_problem_bank(session)

    manifest = load_concept_steps_manifest()
    concepts = manifest.get("concepts", [])
    step_2 = next(c for c in concepts if c["key"] == "step-py-values-2")
    assert "step-py-values-1" in step_2.get("prerequisite_keys", [])

    # Learner solves all guided exercises and independent problem for step 2 ahead of order
    for g in step_2.get("guided_practice_refs", []):
        session.add(AppSetting(key=f"lp_ex_solved:{g}", value="true"))
    for p in step_2.get("independent_practice_refs", []):
        session.add(
            ArenaAttempt(
                problem_key=p,
                track="python",
                submitted_source="def solution(): pass",
                passed=True,
                score=100.0,
                hints_used=0,
                gave_up=False,
            )
        )
    session.commit()

    # Step 1 is NOT completed (prerequisite missing!)
    # State MUST be capped at "practising", NEVER "ready_to_advance"
    state = get_concept_step_progress(session, step_2)
    assert state == "practising", f"Expected 'practising' due to missing prerequisite, got {state}"

    # Client cannot force advancement either
    with pytest.raises(ValueError):
        set_concept_step_progress(session, "step-py-values-2", "ready_to_advance")

    # Complete step 1 prerequisites
    step_1 = next(c for c in concepts if c["key"] == "step-py-values-1")
    for g in step_1.get("guided_practice_refs", []):
        session.add(AppSetting(key=f"lp_ex_solved:{g}", value="true"))
    for p in step_1.get("independent_practice_refs", []):
        session.add(
            ArenaAttempt(
                problem_key=p,
                track="python",
                submitted_source="def solution(): pass",
                passed=True,
                score=100.0,
                hints_used=0,
                gave_up=False,
            )
        )
    session.commit()
    assert get_concept_step_progress(session, step_1) == "ready_to_advance"

    # Now step 2 can advance!
    assert get_concept_step_progress(session, step_2) == "ready_to_advance"


def test_beginner_exercises_35_inventory_coverage():
    manifest = load_beginner_exercises_manifest()
    exercises = manifest.get("exercises", [])
    assert len(exercises) == 35, f"Expected exactly 35 beginner exercises, found {len(exercises)}"

    tracks = [e["track"] for e in exercises]
    assert tracks.count("python") == 18, f"Expected 18 Python exercises, found {tracks.count('python')}"
    assert tracks.count("sql") == 10, f"Expected 10 SQL exercises, found {tracks.count('sql')}"
    assert tracks.count("dsa") == 7, f"Expected 7 DSA exercises, found {tracks.count('dsa')}"

    # Every exercise must have non-empty tests and instructions
    for ex in exercises:
        assert len(ex["instructions"]) > 10
        assert len(ex.get("tests", [])) >= 1
        assert ex.get("reference_solution")
        assert ex.get("hints")
