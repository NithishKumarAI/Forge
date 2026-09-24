import ast,contextlib,io,shutil,subprocess,sys
from pathlib import Path
from app.schemas.arena import CodingProblem

REPO_ROOT=Path(__file__).resolve().parents[4]
SQL_VALIDATOR=REPO_ROOT/"apps"/"web"/"scripts"/"validate-sql-problems.mjs"
WEB_ROOT=REPO_ROOT/"apps"/"web"

def validate_sql_with_pglite(problem_key:str|None=None)->None:
    node=shutil.which("node")
    if not node or not SQL_VALIDATOR.exists():raise RuntimeError("SQL PGlite validation unavailable")
    command=[node,str(SQL_VALIDATOR)]
    if problem_key:command.extend(["--problem",problem_key])
    try:result=subprocess.run(command,cwd=WEB_ROOT,capture_output=True,text=True,check=False)
    except OSError as error:raise RuntimeError("SQL PGlite validation unavailable") from error
    if result.returncode:
        detail=(result.stderr or result.stdout).strip()
        raise ValueError(f"SQL PGlite validation failed{': '+detail if detail else ''}")

def _validate_sql_contract(problem:CodingProblem)->None:
    validation=problem.validation;required={"setup_sql","expected_columns","expected_rows","visible_tables","hidden_datasets","order_sensitive"}
    if not required.issubset(validation):raise ValueError("SQL validation contract is incomplete")
    if not problem.reference_solution.lstrip().lower().startswith(("select","with")):raise ValueError("Initial SQL bank supports SELECT/CTE queries only")

def _typed_value(item):
    kind,value=item["type"],item.get("value")
    if kind=="list":return [_typed_value(entry) for entry in value]
    if kind=="tuple":return tuple(_typed_value(entry) for entry in value)
    if kind=="dict":return {_typed_value(entry["key"]):_typed_value(entry["value"]) for entry in value}
    if kind=="NoneType":return None
    return value

def _strict_equal(actual,expected):
    if type(actual) is not type(expected):return False
    if isinstance(actual,(list,tuple)):return len(actual)==len(expected) and all(_strict_equal(a,e) for a,e in zip(actual,expected))
    if isinstance(actual,dict):
        return len(actual)==len(expected) and all(any(_strict_equal(ak,ek) and _strict_equal(av,ev) for ek,ev in expected.items()) for ak,av in actual.items())
    return actual==expected

def _normalized_stdout(value,rules):
    if rules.get("trim_trailing_whitespace",True):value="\n".join(line.rstrip() for line in value.splitlines())
    if rules.get("ignore_final_newline",True):value=value.rstrip("\n")
    return value

def validate_problem(path:Path,run_sql:bool=True)->CodingProblem:
    problem=CodingProblem.model_validate_json(path.read_text(encoding="utf-8"));validation=problem.validation
    if problem.track in {"python","dsa"}:
        ast.parse(problem.reference_solution);compiled=compile(problem.reference_solution,str(path),"exec");namespace={}
        tests=validation["sample_tests"]+validation["hidden_tests"]
        if not tests:raise ValueError("Python problem requires tests")
        mode=validation.get("judge_mode","function")
        if mode=="function":
            exec(compiled,{"__builtins__":__builtins__},namespace);function=namespace[validation["function_name"]]
            for test in tests:
                expected=_typed_value(test["expected_typed"]) if "expected_typed" in test else test.get("expected")
                try:actual=function(*test.get("args",[]),**test.get("kwargs",{}))
                except Exception as error:
                    if type(error).__name__!=test.get("expected_exception"):raise ValueError(f"Reference raised {type(error).__name__} for {test['name']}") from error
                    continue
                if not _strict_equal(actual,expected):raise ValueError(f"Reference failed {test['name']}: {actual!r} ({type(actual).__name__}) != {expected!r} ({type(expected).__name__})")
        else:
            for test in tests:
                output=io.StringIO();old_stdin=sys.stdin;sys.stdin=io.StringIO(test["stdin"])
                try:
                    with contextlib.redirect_stdout(output):exec(compiled,{"__name__":"__main__"})
                finally:sys.stdin=old_stdin
                if _normalized_stdout(output.getvalue(),test.get("stdout_normalization",{}))!=_normalized_stdout(test["expected_stdout"],test.get("stdout_normalization",{})):raise ValueError(f"Reference stdout failed {test['name']}")
    else:
        _validate_sql_contract(problem)
        if run_sql:validate_sql_with_pglite(problem.key)
    return problem

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--track",choices=["python","sql","dsa"]);p.add_argument("--problem");a=p.parse_args();root=REPO_ROOT/"content"/"problem-bank"
    paths=[root/a.track/f"{a.problem}.json"] if a.problem else list((root/a.track).glob("*.json")) if a.track else list(root.glob("*/*.json"))
    titles=set();sql_keys=[]
    for path in paths:
        problem=validate_problem(path,run_sql=False)
        if problem.title.lower() in titles:raise ValueError(f"Duplicate title: {problem.title}")
        titles.add(problem.title.lower())
        if problem.track=="sql":sql_keys.append(problem.key)
        else:print(f"valid: {problem.key}")
    if sql_keys:
        validate_sql_with_pglite(sql_keys[0] if len(sql_keys)==1 else None)
        for key in sql_keys:print(f"valid: {key} (PGlite)")
if __name__=="__main__":main()
