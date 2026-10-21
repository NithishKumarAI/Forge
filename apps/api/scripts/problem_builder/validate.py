import shutil, subprocess
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
    try:result=subprocess.run(command,cwd=WEB_ROOT,capture_output=True,text=True,check=False,timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:raise RuntimeError("SQL PGlite validation unavailable") from error
    if result.returncode:
        detail=(result.stderr or result.stdout).strip()
        raise ValueError(f"SQL PGlite validation failed{': '+detail if detail else ''}")

def _validate_sql_contract(problem:CodingProblem)->None:
    validation=problem.validation;required={"setup_sql","expected_columns","expected_rows","visible_tables","hidden_datasets","order_sensitive"}
    if not required.issubset(validation):raise ValueError("SQL validation contract is incomplete")
    if not problem.reference_solution.lstrip().lower().startswith(("select","with")):raise ValueError("Initial SQL bank supports SELECT/CTE queries only")

def validate_problem(path:Path,run_sql:bool=True)->CodingProblem:
    problem=CodingProblem.model_validate_json(path.read_text(encoding="utf-8"));validation=problem.validation
    if problem.track in {"python","dsa"}:
        from scripts.content_checks.problems import check_problem
        check_problem(problem, problem.publication_contract, problem.negative_solutions)
    else:
        _validate_sql_contract(problem)
        if run_sql:
            from scripts.content_checks.problems import check_problem
            check_problem(problem)
    return problem

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--track",choices=["python","sql","dsa"]);p.add_argument("--problem");a=p.parse_args();root=REPO_ROOT/"content"/"problem-bank"
    paths=[root/a.track/f"{a.problem}.json"] if a.problem else list((root/a.track).glob("*.json")) if a.track else list(root.glob("*/*.json"))
    if not a.problem:
        paths += list((root/"revisions").glob(f"{a.track or '*'}/*/*.json"))
    titles={};sql_problems=[]
    for path in paths:
        problem=validate_problem(path,run_sql=False)
        if problem.title.lower() in titles and titles[problem.title.lower()] != problem.key:raise ValueError(f"Duplicate title: {problem.title}")
        titles[problem.title.lower()]=problem.key
        if problem.track=="sql":sql_problems.append(problem)
        else:print(f"valid: {problem.key}")
    if sql_problems:
        from scripts.content_checks.examples import check_sql
        check_sql([{"arena_problem": problem.model_dump(mode="json")} for problem in sql_problems])
        for problem in sql_problems: print(f"valid: {problem.key} (PGlite exact bundle)")
if __name__=="__main__":main()
