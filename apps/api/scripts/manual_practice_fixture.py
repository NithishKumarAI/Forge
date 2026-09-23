"""Seed a disposable Practice pack for browser smoke tests without calling Gemini.

Run only with FORGE_DATABASE_URL pointing to a forge-practice-smoke.db file.
"""

import json

from sqlmodel import Session, select

from app import models  # noqa: F401 -- register tables
from app.config import settings
from app.database import create_db_and_tables, engine
from app.models import Exercise, Topic, Track
from app.services.curriculum import seed_default_curriculum


if not settings.database_url.endswith("forge-practice-smoke.db"):
    raise SystemExit("Set FORGE_DATABASE_URL to a disposable forge-practice-smoke.db first")

create_db_and_tables()
with Session(engine) as session:
    seed_default_curriculum(session, settings.curriculum_path)
    track = session.exec(select(Track).where(Track.slug == "python-programming")).first()
    if track is None:
        track = session.exec(select(Track).where(Track.name.contains("Python"))).first()
    if track is None:
        raise SystemExit("No Python track found")
    topic = session.exec(select(Topic).where(Topic.track_id == track.id).order_by(Topic.id)).first()
    if topic is None:
        raise SystemExit("No Python topic found")
    existing = session.exec(select(Exercise).where(Exercise.topic_id == topic.id)).first()
    if existing is None:
        examples = [
            ("multiple_choice", "Choose Python addition", "Which expression adds two numbers in Python?", {
                "choices": ["a + b", "a & b", "a == b"], "correct_index": 0,
                "explanation": "The + operator adds numbers.",
            }, ["Think of the arithmetic operator."]),
            ("short_answer", "Explain a small function", "Why is returning a value useful in a Python function?", {
                "rubric": [{"concept": "caller can use result", "weight": 1.0}],
                "reference_answer": "The caller can use the returned result.", "minimum_pass_score": 70,
            }, ["Think about what the caller receives."]),
            ("python_code", "Implement add", "Write add(a, b) to return their sum.", {
                "starter_code": "def add(a, b):\n    pass", "function_name": "add",
                "sample_tests": [{"name": "positives", "args": [2, 3], "kwargs": {}, "expected": 5}],
                "hidden_tests": [{"name": "negative", "args": [-1, 1], "kwargs": {}, "expected": 0}],
                "reference_solution": "def add(a, b):\n    return a + b", "time_limit_ms": 5000,
            }, ["Return the sum.", "Use the addition operator."]),
        ]
        for index, (kind, title, prompt, content, hints) in enumerate(examples):
            session.add(Exercise(
                curriculum_id=track.curriculum_id, track_id=track.id, topic_id=topic.id,
                exercise_type=kind, title=title, prompt_markdown=prompt, difficulty="intro",
                source="manual_smoke_fixture", validation_status="pending" if kind == "python_code" else "valid",
                content_json=json.dumps({"key": f"smoke-{index}", "hints": hints, "content": content}),
            ))
        session.commit()
    print(f"Practice smoke topic: {topic.id} — {track.name} / {topic.name}")
