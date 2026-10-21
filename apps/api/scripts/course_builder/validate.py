import ast
import json
from pathlib import Path

from app.schemas.course import StaticLesson


QUALITY_TARGETS = {
    # Python (19)
    ("python", "async-await"), ("python", "collections"),
    ("python", "comprehensions"), ("python", "control-flow"),
    ("python", "debugging"), ("python", "decorators"),
    ("python", "exceptions"), ("python", "file-handling"),
    ("python", "functions"), ("python", "generators"),
    ("python", "iterators"), ("python", "modules-packages"),
    ("python", "oop"), ("python", "reading-unfamiliar-code"),
    ("python", "strings"), ("python", "syntax-data-types"),
    ("python", "testing"), ("python", "type-hints"),
    ("python", "virtual-environments"),
    # SQL (14)
    ("sql-postgresql", "aggregation"), ("sql-postgresql", "constraints-design"),
    ("sql-postgresql", "ctes"), ("sql-postgresql", "data-modification"),
    ("sql-postgresql", "database-python"), ("sql-postgresql", "indexes"),
    ("sql-postgresql", "joins"), ("sql-postgresql", "postgresql-practicals"),
    ("sql-postgresql", "query-basics"), ("sql-postgresql", "relational-foundations"),
    ("sql-postgresql", "subqueries"), ("sql-postgresql", "transactions"),
    ("sql-postgresql", "values-expressions"), ("sql-postgresql", "window-functions"),
    # DSA (20)
    ("dsa", "arrays"), ("dsa", "backtracking"),
    ("dsa", "bfs"), ("dsa", "big-o"),
    ("dsa", "binary-search"), ("dsa", "dfs"),
    ("dsa", "dynamic-programming"), ("dsa", "graphs"),
    ("dsa", "hash-maps"), ("dsa", "heaps"),
    ("dsa", "linked-lists"), ("dsa", "queues"),
    ("dsa", "recursion"), ("dsa", "sets"),
    ("dsa", "sliding-window"), ("dsa", "sorting"),
    ("dsa", "stacks"), ("dsa", "strings"),
    ("dsa", "trees"), ("dsa", "two-pointers"),
}

PLACEHOLDER_PHRASES = (
    "this is the ", "section about ", "learn about ", "key point about ",
    "dummy table", "adding some padding", "exercise 1 for",
    "answer is related to", "understand the core concept",
)

DSA_REQUIRED_HEADINGS = (
    "when to recognize this pattern", "core idea", "naive approach",
    "better approach", "python implementation", "step-by-step example",
    "time complexity", "space complexity", "common mistakes", "arena reference",
)


def _lesson_corpus(lesson: StaticLesson) -> str:
    return " ".join([
        lesson.title, lesson.description, *lesson.learning_objectives,
        *lesson.summary, *lesson.interview_takeaways, *lesson.common_mistakes,
        *[
            section.title + " " + section.markdown + " " + " ".join(section.key_points)
            for section in lesson.sections
        ],
    ]).lower()


def _validate_target_quality(lesson: StaticLesson, path: Path, corpus: str, exercise_path: Path | None = None) -> None:
    target = (lesson.track_slug, lesson.topic_slug)
    if target not in QUALITY_TARGETS:
        return

    placeholders = [phrase for phrase in PLACEHOLDER_PHRASES if phrase in corpus]
    if placeholders:
        raise ValueError(f"{path}: placeholder content remains: {', '.join(placeholders)}")
    if not 5 <= len(lesson.sections) <= 8:
        raise ValueError(f"{path}: remediated lessons require 5-8 substantive sections")
    short_sections = [section.slug for section in lesson.sections if len(section.markdown.strip()) < 220]
    if short_sections:
        raise ValueError(f"{path}: sections are too thin: {', '.join(short_sections)}")
    if any(not section.checkpoint or len(section.checkpoint.strip()) < 20 for section in lesson.sections):
        raise ValueError(f"{path}: every section needs a meaningful checkpoint")

    examples = [item for section in lesson.sections for item in section.examples]
    if len(examples) < 2:
        raise ValueError(f"{path}: remediated lessons require at least two runnable examples")
    expected_language = "sql" if lesson.track_slug == "sql-postgresql" else "python"
    if sum(item.language.lower() == expected_language for item in examples) < 2:
        raise ValueError(f"{path}: expected at least two {expected_language} examples")
    if any(len(item.explanation.strip()) < 25 for item in examples):
        raise ValueError(f"{path}: every example needs an explanatory note")

    if lesson.track_slug == "dsa":
        missing = [heading for heading in DSA_REQUIRED_HEADINGS if heading not in corpus]
        if missing:
            raise ValueError(f"{path}: missing DSA teaching blocks: {', '.join(missing)}")
    if target == ("sql-postgresql", "window-functions"):
        required = ("input", "output", "row_number", "rank()", "dense_rank", "lag", "lead", "running total", "rows between")
        missing = [term for term in required if term not in corpus]
        if missing:
            raise ValueError(f"{path}: incomplete window-function coverage: {', '.join(missing)}")
    if target == ("sql-postgresql", "transactions"):
        required = ("atomicity", "consistency", "isolation", "durability", "begin", "commit", "rollback", "concurrency", "retry")
        missing = [term for term in required if term not in corpus]
        if missing:
            raise ValueError(f"{path}: incomplete transaction coverage: {', '.join(missing)}")

    _validate_exercises(exercise_path or path.with_name("exercises.json"))


def _validate_exercises(path: Path) -> None:
    if not path.exists():
        raise ValueError(f"{path}: exercise file is required")
    exercises = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(exercises, list) or not 6 <= len(exercises) <= 8:
        raise ValueError(f"{path}: expected 6-8 exercises")
    keys = [item.get("key") for item in exercises]
    if any(not isinstance(key, str) or not key for key in keys) or len(keys) != len(set(keys)):
        raise ValueError(f"{path}: exercise keys must be non-empty and unique")
    allowed_types = {"multiple_choice", "short_answer", "python_code", "python_debug"}
    if any(item.get("exercise_type") not in allowed_types for item in exercises):
        raise ValueError(f"{path}: unsupported exercise type")
    prompts = [item.get("prompt_markdown", "").strip() for item in exercises]
    if any(len(prompt) < 30 for prompt in prompts):
        raise ValueError(f"{path}: exercise prompts must require substantive reasoning")
    corpus = " ".join(
        str(value) for item in exercises
        for value in (item.get("title", ""), item.get("prompt_markdown", ""), item.get("content", ""))
    ).lower()
    placeholders = [phrase for phrase in PLACEHOLDER_PHRASES if phrase in corpus]
    if placeholders:
        raise ValueError(f"{path}: placeholder exercises remain: {', '.join(placeholders)}")
    counts = {kind: sum(item["exercise_type"] == kind for item in exercises) for kind in allowed_types}
    if counts["multiple_choice"] < 2 or counts["short_answer"] < 3:
        raise ValueError(f"{path}: include at least two MCQs and three applied short answers")

    for item in exercises:
        content = item.get("content")
        if not isinstance(content, dict):
            raise ValueError(f"{path}: {item['key']} needs structured content")
        if item["exercise_type"] == "multiple_choice":
            choices, index = content.get("choices"), content.get("correct_index")
            if not isinstance(choices, list) or not 2 <= len(choices) <= 6:
                raise ValueError(f"{path}: {item['key']} needs 2-6 choices")
            if not isinstance(index, int) or not 0 <= index < len(choices):
                raise ValueError(f"{path}: {item['key']} has an invalid correct_index")
            if len(content.get("explanation", "").strip()) < 20:
                raise ValueError(f"{path}: {item['key']} needs an explanation")
        if item["exercise_type"] == "short_answer":
            rubric = content.get("rubric")
            if not isinstance(rubric, list) or len(rubric) < 2:
                raise ValueError(f"{path}: {item['key']} needs a multi-part rubric")
            if len(content.get("reference_answer", "").strip()) < 50:
                raise ValueError(f"{path}: {item['key']} needs a useful reference answer")
    applied_markers = ("predict", "fix", "write", "implement", "diagnose", "explain")
    if sum(marker in corpus for marker in applied_markers) < 4:
        raise ValueError(f"{path}: exercises need prediction, debugging, writing, and explanation tasks")


NON_ARENA_KEYS = {
    "python-language-reference",
    "python-official-tutorial",
    "python-stdlib-docs",
    "sql-postgresql",
    "sql-official-docs",
    "sql-tutorial",
    "sql-expressions",
    "python-implementation",
    "python-builtin-sort-and-keys",
    "sql-practicals",
    "sql-types",
}


def get_accepted_problem_keys(bank_dir: Path | None = None) -> set[str]:
    if bank_dir is None:
        root = Path(__file__).resolve().parents[4]
        bank_dir = root / "content" / "problem-bank"
    keys = set()
    if bank_dir.exists():
        for track in ("python", "sql", "dsa"):
            track_dir = bank_dir / track
            if track_dir.exists():
                for f in track_dir.glob("*.json"):
                    keys.add(f.stem)
    return keys


def extract_arena_problem_references(lesson: StaticLesson) -> list[str]:
    import re
    refs = []
    seen = set()
    for section in lesson.sections:
        is_arena_section = "arena" in section.slug.lower() or "arena" in section.title.lower()
        in_arena_block = False

        for line in section.markdown.splitlines():
            line_str = line.strip()
            if "arena practice" in line_str.lower() or "arena reference" in line_str.lower():
                in_arena_block = True
            elif line_str.startswith("##") and "arena" not in line_str.lower():
                in_arena_block = False

            for m in re.finditer(r"`((?:dsa|sql|python)-[a-z0-9-]+)`", line_str):
                cand = m.group(1)
                if cand in NON_ARENA_KEYS:
                    continue
                if in_arena_block or is_arena_section or "arena" in line_str.lower() or "practice" in line_str.lower():
                    if cand not in seen:
                        seen.add(cand)
                        refs.append(cand)

        for kp in section.key_points:
            for m in re.finditer(r"`((?:dsa|sql|python)-[a-z0-9-]+)`", kp):
                cand = m.group(1)
                if cand in NON_ARENA_KEYS:
                    continue
                if is_arena_section or "arena" in kp.lower() or "practice" in kp.lower():
                    if cand not in seen:
                        seen.add(cand)
                        refs.append(cand)

    return refs


def _validate_arena_references(lesson: StaticLesson, path: Path, bank_dir: Path | None = None) -> None:
    accepted = get_accepted_problem_keys(bank_dir)
    if not accepted:
        return
    referenced = extract_arena_problem_references(lesson)
    for key in referenced:
        if key not in accepted:
            raise ValueError(f"{path}: referenced Arena problem '{key}' does not exist in problem bank")


def validate_lesson(path: Path, coverage_path: Path, exercise_path: Path | None = None) -> StaticLesson:
    lesson = StaticLesson.model_validate_json(path.read_text(encoding="utf-8"))
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))[lesson.topic_slug]["required_concepts"]
    corpus = _lesson_corpus(lesson)
    missing = [concept for concept in coverage if concept.lower() not in corpus]
    if missing:
        raise ValueError(f"{path}: missing required concepts: {', '.join(missing)}")
    for section in lesson.sections:
        for item in section.examples:
            if item.language.lower() == "python":
                try:
                    ast.parse(item.code)
                except SyntaxError as exc:
                    raise ValueError(f"{path}: invalid Python in section {section.slug}: {exc}") from exc
    if len(corpus) > 100_000:
        raise ValueError(f"{path}: lesson is too large")
    _validate_target_quality(lesson, path, corpus, exercise_path)
    _validate_arena_references(lesson, path)
    return lesson


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", default="python")
    parser.add_argument("--topic")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    base = root / "content" / "ai-engineer" / "v1" / args.track
    coverage = root / "data" / "course-coverage" / f"{args.track}.json"
    paths = [base / args.topic / "lesson.json"] if args.topic else sorted(base.glob("*/lesson.json"))
    for path in paths:
        validate_lesson(path, coverage)
        print(f"valid: {path}")


if __name__ == "__main__":
    main()
