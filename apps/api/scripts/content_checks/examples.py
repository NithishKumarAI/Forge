"""Bounded development execution only. SQL uses fresh PGlite, never Forge SQLite."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

WORKER = Path(__file__).with_name("python_worker.py")
SQL_WORKER = Path(__file__).resolve().parents[4] / "apps/web/scripts/validate-content-sql.mjs"


def typed(value):
    if type(value) in (list, tuple):
        return {"type": type(value).__name__, "value": [typed(x) for x in value]}
    if type(value) is dict:
        return {"type": "dict", "value": [{"key": typed(k), "value": typed(v)} for k, v in value.items()]}
    return {"type": type(value).__name__, "value": value}


def run_python(request):
    ast.parse(request["code"])
    # No inherited secrets, Python path, database configuration or working directory.
    env = {k: os.environ[k] for k in ("SystemRoot", "WINDIR") if k in os.environ}
    with tempfile.TemporaryDirectory(prefix="forge-content-") as directory:
        try:
            result = subprocess.run([sys.executable, "-I", "-S", str(WORKER)], input=json.dumps(request),
                text=True, capture_output=True, timeout=5, cwd=directory, env=env)
        except subprocess.TimeoutExpired as error:
            raise ValueError("Python content execution timed out") from error
    if result.returncode:
        raise ValueError("Python content execution failed: " + (result.stdout or result.stderr)[:1000])
    return json.loads(result.stdout)


def check_python(request, expected):
    actual = run_python(request)
    if actual["exception"] != expected.get("expected_exception"):
        raise ValueError(f"Reference raised {actual['exception']}; expected {expected.get('expected_exception')}")
    if actual["exception"] is not None:
        return
    if "expected_stdout" in expected:
        rules = expected.get("stdout_normalization", {})
        def normalized(value):
            if rules.get("trim_trailing_whitespace", True):
                value = "\n".join(line.rstrip() for line in value.splitlines())
            if rules.get("ignore_final_newline", True):
                value = value.rstrip("\n")
            return value
        if normalized(actual["stdout"]) != normalized(expected["expected_stdout"]):
            raise ValueError("Python example stdout mismatch")
    if "expected" in expected or "expected_typed" in expected:
        target = expected.get("expected_typed", typed(expected.get("expected")))
        if not equal_typed(actual["returned"], target):
            raise ValueError(f"Reference failed: typed return mismatch: {actual['returned']} != {target}")


def equal_typed(actual, expected):
    if actual["type"] != expected["type"]:
        return False
    kind, left, right = actual["type"], actual.get("value"), expected.get("value")
    if kind in {"list", "tuple"}:
        return len(left) == len(right) and all(equal_typed(a, b) for a, b in zip(left, right))
    if kind == "dict":
        return len(left) == len(right) and all(any(equal_typed(a["key"], b["key"]) and equal_typed(a["value"], b["value"]) for b in right) for a in left)
    return type(left) is type(right) and left == right


def check_sql(fixture):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("SQL PGlite validation unavailable")
    try:
        result = subprocess.run([node, "--max-old-space-size=256", str(SQL_WORKER)], input=json.dumps(fixture), capture_output=True, text=True, timeout=120 if isinstance(fixture, list) else 25)
    except subprocess.TimeoutExpired as error:
        raise ValueError("SQL example timed out") from error
    if result.returncode:
        raise ValueError("SQL example mismatch/invalid fixture: " + (result.stderr or result.stdout)[:1500])


def check_lesson_examples(candidate):
    checks = {(x["section_slug"], x["example_index"]): x for x in candidate.example_checks}
    if len(checks) != len(candidate.example_checks):
        raise ValueError("Duplicate example fixture identity")
    visited, results = set(), []
    for section in candidate.payload["lesson"]["sections"]:
        for index, example in enumerate(section.get("examples", [])):
            key = section["slug"], index
            check = checks.get(key)
            if not check:
                raise ValueError("Every example must be executable or explicitly contextual")
            visited.add(key)
            mode = check["mode"]
            if mode == "context":
                if not check.get("reason"):
                    raise ValueError("Contextual examples need an explicit review reason")
                results.append({"section": key[0], "index": index, "status": "requires_review", "reason": check["reason"]})
                continue
            if mode == "python" and example["language"].lower() == "python":
                if example.get("expected_output") is None or check.get("expected_stdout") != example["expected_output"]:
                    raise ValueError("Python documented output and fixture differ")
                check_python({**check, "code": example["code"]}, check)
            elif mode == "sql" and example["language"].lower() == "sql":
                if json.loads(example["expected_output"]) != {"columns": check["expected_columns"], "rows": check["expected_rows"]}:
                    raise ValueError("SQL displayed output and fixture differ")
                check_sql({**check, "query": example["code"]})
            else:
                raise ValueError("Example language/mode mismatch")
            results.append({"section": key[0], "index": index, "status": "executed"})
    if set(checks) != visited:
        raise ValueError("Dangling example fixture reference")
    return results
