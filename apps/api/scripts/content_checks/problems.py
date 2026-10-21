"""Structured contracts render the displayed statement/examples for new revisions."""
import ast
from .examples import check_python, check_sql


def decode(item):
    kind, value = item["type"], item.get("value")
    if kind == "list": return [decode(x) for x in value]
    if kind == "tuple": return tuple(decode(x) for x in value)
    if kind == "dict": return {decode(x["key"]): decode(x["value"]) for x in value}
    return None if kind == "NoneType" else value


def render_statement(contract):
    parameters = ", ".join(f"`{p['name']}: {p['annotation']}`" for p in contract["parameters"])
    return (f"Implement `{contract['function_name']}` with parameters {parameters}.\n\n"
        f"Return a `{contract['return_type']}` (`{contract['return_annotation']}`). {contract['behavior']}\n\n"
        f"No solution: {contract['no_solution']}\n\nExceptions: {contract['exception_behavior']}")


def rendered_example(test):
    expected = decode(test["expected_typed"]) if "expected_typed" in test else test.get("expected")
    return {"input": ", ".join([*(repr(x) for x in test.get("args", [])), *(f"{k}={v!r}" for k, v in test.get("kwargs", {}).items())]),
            "output": "raises " + test["expected_exception"] if test.get("expected_exception") else repr(expected)}


def check_problem(problem, contract=None, negatives=(), *, require_contract=False):
    validation = problem.validation
    if problem.track == "sql":
        if not problem.reference_solution.lstrip().lower().startswith(("select", "with")):
            raise ValueError("Arena SQL contracts support SELECT/CTE queries only")
        check_sql({"arena_problem": problem.model_dump(mode="json")})
        if require_contract:
            # General SQL prose needs explicit human statement/judge review.
            if not contract or contract.get("manual_statement_review_required") is not True:
                raise ValueError("SQL problem requires explicit manual statement review")
            if not negatives:
                raise ValueError("SQL publication requires deliberately incorrect implementations")
            for source in negatives:
                wrong = problem.model_dump(mode="json")
                wrong["reference_solution"] = source
                try:
                    check_sql({"arena_problem": wrong})
                except ValueError:
                    continue
                raise ValueError("SQL judge accepted a deliberately incorrect implementation")
        return {"statement": "requires_review", "reference": "executed"}
    source = problem.reference_solution
    ast.parse(source)
    tests = validation.get("sample_tests", []) + validation.get("hidden_tests", [])
    if not tests or len({t["name"] for t in tests}) != len(tests):
        raise ValueError("Reference tests must have unique identities")
    for test in tests:
        request = {**test, "code": source}
        if validation.get("judge_mode", "function") == "function":
            request["function_name"] = validation["function_name"]
        check_python(request, test)
    if not contract:
        if require_contract:
            raise ValueError("New Python/DSA publication requires a structured statement/judge contract")
        return {"statement": "requires_review", "reference": "executed"}
    if validation.get("judge_mode", "function") != "function":
        raise ValueError("Structured stdin/stdout publication is awaiting a reviewed formatter")
    if contract["function_name"] != validation["function_name"]:
        raise ValueError("Function name differs from judge")
    for code in (source, problem.starter_code):
        functions = [n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef) and n.name == contract["function_name"]]
        if len(functions) != 1:
            raise ValueError("Missing/ambiguous declared function")
        function = functions[0]
        parameters = [{"name": a.arg, "annotation": ast.unparse(a.annotation) if a.annotation else ""} for a in function.args.args]
        if parameters != contract["parameters"] or function.args.vararg or function.args.kwarg or function.args.kwonlyargs or function.args.posonlyargs:
            raise ValueError("Parameter contract differs from starter/reference")
        if not function.returns or ast.unparse(function.returns) != contract["return_annotation"]:
            raise ValueError("Return annotation differs from structured contract")
    if problem.statement_markdown != render_statement(contract) or problem.constraints != contract["constraints"]:
        raise ValueError("Displayed statement/constraints differ from authoritative structured contract")
    by_name = {t["name"]: t for t in tests}
    linked = contract["example_test_names"]
    if len(linked) != len(problem.examples) or len(linked) != len(set(linked)):
        raise ValueError("Displayed examples require unique fixture links")
    for example, name in zip(problem.examples, linked):
        if name not in by_name or example.model_dump(include={"input", "output"}) != rendered_example(by_name[name]):
            raise ValueError("Displayed example contradicts typed judge fixture")
    required = {"normal", "edge", "boundary", "no_solution"}
    if not required <= {tag for t in tests for tag in t.get("case_tags", [])}:
        raise ValueError("Normal, edge, boundary and no-solution fixtures are required")
    for test in tests:
        if not test.get("expected_exception"):
            expected = decode(test["expected_typed"]) if "expected_typed" in test else test.get("expected")
            if type(expected).__name__ != contract["return_type"]:
                raise ValueError("Hidden/visible fixture return type contradicts contract")
        for bound in contract.get("bounds", []):
            param = next(i for i, p in enumerate(contract["parameters"]) if p["name"] == bound["parameter"])
            value = test.get("args", [])[param]
            values = value if bound["kind"] == "list_int" else [value]
            if bound["kind"] == "list_int" and not bound["min_length"] <= len(value) <= bound["max_length"]:
                raise ValueError("Test violates declared length bounds")
            if any(type(x) is not int or not bound["min"] <= x <= bound["max"] for x in values):
                raise ValueError("Test violates declared numeric bounds")
    if require_contract and not negatives:
        raise ValueError("At least one deliberately incorrect implementation is required")
    for wrong in negatives:
        failures = 0
        for test in tests:
            try: check_python({**test, "code": wrong, "function_name": validation["function_name"]}, test)
            except ValueError: failures += 1
        if not failures:
            raise ValueError("Judge failed to reject a deliberately incorrect implementation")
    return {"statement": "rendered_from_contract", "reference": "executed", "tests": len(tests), "negative_solutions": len(negatives)}
