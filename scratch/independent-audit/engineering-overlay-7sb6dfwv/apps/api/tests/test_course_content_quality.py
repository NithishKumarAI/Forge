import json
from pathlib import Path

import pytest

from scripts.course_builder.validate import QUALITY_TARGETS, validate_lesson


REPO_ROOT = Path(__file__).resolve().parents[3]
COURSE_ROOT = REPO_ROOT / "content" / "ai-engineer" / "v1"
COVERAGE_ROOT = REPO_ROOT / "data" / "course-coverage"


@pytest.mark.parametrize("track,topic", sorted(QUALITY_TARGETS))
def test_remediated_lessons_and_exercises_meet_quality_contract(track: str, topic: str):
    lesson = COURSE_ROOT / track / topic / "lesson.json"
    coverage = COVERAGE_ROOT / f"{track}.json"

    validated = validate_lesson(lesson, coverage)

    assert validated.topic_slug == topic
    assert 5 <= len(validated.sections) <= 8


def test_target_quality_rejects_placeholder_prose(tmp_path: Path):
    source_dir = COURSE_ROOT / "python" / "collections"
    payload = json.loads((source_dir / "lesson.json").read_text(encoding="utf-8"))
    payload["sections"][0]["markdown"] += " This is the collections section."
    lesson_path = tmp_path / "lesson.json"
    lesson_path.write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "exercises.json").write_text(
        (source_dir / "exercises.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="placeholder content remains"):
        validate_lesson(lesson_path, COVERAGE_ROOT / "python.json")


def test_validate_lesson_rejects_missing_arena_problem(tmp_path: Path):
    source_dir = COURSE_ROOT / "dsa" / "arrays"
    payload = json.loads((source_dir / "lesson.json").read_text(encoding="utf-8"))
    payload["sections"][4]["markdown"] += "\nPractice with `dsa-fake-problem-xyz` in Forge Arena."
    lesson_path = tmp_path / "lesson.json"
    lesson_path.write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "exercises.json").write_text(
        (source_dir / "exercises.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="referenced Arena problem 'dsa-fake-problem-xyz' does not exist"):
        validate_lesson(lesson_path, COVERAGE_ROOT / "dsa.json")


def test_all_53_lessons_reference_only_existing_arena_problems():
    from scripts.course_builder.validate import extract_arena_problem_references, get_accepted_problem_keys
    from app.schemas.course import StaticLesson

    accepted_keys = get_accepted_problem_keys()
    assert len(accepted_keys) >= 110

    lesson_files = sorted(COURSE_ROOT.glob("*/*/lesson.json"))
    assert len(lesson_files) == 53

    for lf in lesson_files:
        lesson = StaticLesson.model_validate_json(lf.read_text(encoding="utf-8"))
        refs = extract_arena_problem_references(lesson)
        for r in refs:
            assert r in accepted_keys, f"{lf}: referenced Arena problem '{r}' does not exist in accepted bank"

