import json
from pathlib import Path

import pytest

from scripts.problem_builder.validate import validate_problem


def _problem(reference_solution: str, validation: dict) -> dict:
    return {
        "key": "judge-contract", "title": "Judge contract", "track": "python",
        "topic_tags": ["testing"], "difficulty": "easy", "interview_frequency": "high",
        "estimated_minutes": 10, "statement_markdown": "Test the judge.", "constraints": [],
        "examples": [{"input": "x", "output": "y"}], "starter_code": "def solve():\n    pass",
        "hints": [], "explanation": "Contract fixture.", "reference_solution": reference_solution,
        "complexity": "O(1)", "validation": validation, "source_type": "original",
        "version": "1.0.0", "mapped_topic": "python/foundations",
    }


def _validate(tmp_path: Path, payload: dict):
    path = tmp_path / "problem.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return validate_problem(path)


@pytest.mark.parametrize(
    ("literal", "expected"),
    [
        ("5", 5),
        ("None", None),
        ("[1, 'two', False]", [1, "two", False]),
        ("{'items': [1, {'ok': True}]}", {"items": [1, {"ok": True}]}),
    ],
)
def test_function_reference_preserves_exact_nested_types(tmp_path, literal, expected):
    validation = {"judge_mode": "function", "function_name": "solve", "sample_tests": [{"name": "typed", "args": [], "kwargs": {}, "expected": expected}], "hidden_tests": []}
    assert _validate(tmp_path, _problem(f"def solve():\n    return {literal}", validation)).validation["judge_mode"] == "function"


@pytest.mark.parametrize(("literal", "expected"), [("'5'", 5), ("True", 1), ("1", True)])
def test_function_reference_rejects_equal_but_different_python_types(tmp_path, literal, expected):
    validation = {"judge_mode": "function", "function_name": "solve", "sample_tests": [{"name": "strict", "args": [], "kwargs": {}, "expected": expected}], "hidden_tests": []}
    with pytest.raises(ValueError, match="Reference failed"):
        _validate(tmp_path, _problem(f"def solve():\n    return {literal}", validation))


def test_typed_tuple_and_integer_dictionary_keys(tmp_path):
    expected = {"type": "tuple", "value": [{"type": "dict", "value": [{"key": {"type": "int", "value": 404}, "value": {"type": "int", "value": 2}}]}]}
    validation = {"judge_mode": "function", "function_name": "solve", "sample_tests": [{"name": "typed", "expected_typed": expected}], "hidden_tests": []}
    _validate(tmp_path, _problem("def solve():\n    return ({404: 2},)", validation))


def test_expected_exception_contract(tmp_path):
    validation = {"judge_mode": "function", "function_name": "solve", "sample_tests": [{"name": "error", "expected_exception": "ValueError"}], "hidden_tests": []}
    _validate(tmp_path, _problem("def solve():\n    raise ValueError('safe message')", validation))


def test_syntax_error_is_rejected(tmp_path):
    validation = {"judge_mode": "function", "function_name": "solve", "sample_tests": [{"name": "syntax", "expected": None}], "hidden_tests": []}
    with pytest.raises(SyntaxError):
        _validate(tmp_path, _problem("def solve(:\n    pass", validation))


def test_stdin_stdout_reference_and_trailing_whitespace(tmp_path):
    validation = {"judge_mode": "stdin_stdout", "sample_tests": [{"name": "stdio", "stdin": "Ada\n", "expected_stdout": "Hello Ada\n"}], "hidden_tests": []}
    _validate(tmp_path, _problem("name=input()\nprint('Hello', name)  ", validation))


def test_malformed_test_for_mode_is_rejected(tmp_path):
    validation = {"judge_mode": "stdin_stdout", "sample_tests": [{"name": "missing output", "stdin": "x"}], "hidden_tests": []}
    with pytest.raises(ValueError, match="expected_stdout"):
        _validate(tmp_path, _problem("print(input())", validation))
