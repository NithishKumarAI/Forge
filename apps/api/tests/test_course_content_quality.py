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
