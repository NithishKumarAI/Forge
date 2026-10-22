import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.database import get_session
from app.main import app
from app.models import AppSetting
from app.services.learning_path import (
    evaluate_beginner_exercise,
    get_all_concepts_summary,
    get_arena_stages_detail,
    get_beginner_exercise,
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
    assert primary.action_label == "Resume learning"


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
    set_concept_step_progress(session, "step-py-values-1", "ready_to_advance")

    # Verify persisted in AppSetting
    setting = session.get(AppSetting, "lp_step_state:step-py-values-1")
    assert setting is not None
    assert setting.value == "ready_to_advance"

    # Step progress is reflected in concepts summary
    concepts = get_all_concepts_summary(session)
    step = next(c for c in concepts if c.key == "step-py-values-1")
    assert step.progress_state == "ready_to_advance"


def test_beginner_exercise_grading_python_pass(session: Session):
    result = evaluate_beginner_exercise(
        session,
        "py-first-print-message",
        'def say_hello():\n    return "Hello, Forge!"',
    )
    assert result.passed is True
    assert result.score == 100.0
    assert result.solution is not None  # Revealed on pass
    assert "Passed" in result.output

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

        # 4. Update concept progress
        resp = client.post("/api/learning-path/steps/step-py-values-1/progress?state=practising")
        assert resp.status_code == 200
        assert resp.json()["progress_state"] == "practising"

        # 5. Submit exercise
        resp = client.post(
            "/api/learning-path/exercises/py-first-even-odd/submit",
            json={"source": "def check_even_odd(n):\n    return 'even' if n % 2 == 0 else 'odd'"},
        )
        assert resp.status_code == 200
        sub_res = resp.json()
        assert sub_res["passed"] is True
        assert sub_res["solution"] is not None
    finally:
        app.dependency_overrides.pop(get_session, None)
