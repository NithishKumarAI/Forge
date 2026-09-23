import json
from pathlib import Path
import pytest

from scripts.course_builder.validate import validate_lesson
from scripts.problem_builder.validate import validate_problem

ROOT = Path(__file__).resolve().parents[3]
CONTENT_ROOT = ROOT / "content" / "ai-engineer" / "v1"
PROBLEM_BANK = ROOT / "content" / "problem-bank"
COVERAGE_DIR = ROOT / "data" / "course-coverage"


def test_manifest_tracks_and_compiled_topics():
    manifest_path = CONTENT_ROOT / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(manifest["accepted_tracks"]) == {"python", "sql-postgresql", "dsa"}
    assert len(manifest["compiled_topics"]) >= 50


@pytest.mark.parametrize("track", ["python", "sql-postgresql", "dsa"])
def test_all_lessons_valid_against_coverage(track):
    coverage_path = COVERAGE_DIR / f"{track}.json"
    assert coverage_path.exists(), f"Missing coverage specification for {track}"
    lessons = list((CONTENT_ROOT / track).glob("*/lesson.json"))
    assert len(lessons) > 0, f"No lessons found for {track}"

    for lesson_path in lessons:
        lesson = validate_lesson(lesson_path, coverage_path)
        assert lesson.track_slug == track
        assert len(lesson.sections) >= 2
        # Verify accompanying exercises exist
        exercises_path = lesson_path.with_name("exercises.json")
        assert exercises_path.exists(), f"Missing exercises for {lesson_path}"
        exercises = json.loads(exercises_path.read_text(encoding="utf-8"))
        assert len(exercises) >= 4, f"Insufficient exercises in {exercises_path}"


def test_arena_problem_counts_and_validation():
    track_targets = {"python": 40, "sql": 30, "dsa": 40}
    all_titles = set()
    adapted_count = 0

    for track, target in track_targets.items():
        problems = list((PROBLEM_BANK / track).glob("*.json"))
        assert len(problems) >= target, f"Expected at least {target} problems in {track}, got {len(problems)}"

        for p_path in problems:
            problem = validate_problem(p_path)
            assert problem.track == track
            assert problem.title not in all_titles, f"Duplicate problem title: {problem.title}"
            all_titles.add(problem.title)

            # Check adapted Exercism problems
            raw = json.loads(p_path.read_text(encoding="utf-8"))
            if raw.get("adapted"):
                assert raw.get("source_project") == "exercism"
                assert raw.get("license") == "MIT"
                adapted_count += 1

    assert adapted_count >= 5, "Expected at least 5 Exercism-adapted problems with MIT attribution"
