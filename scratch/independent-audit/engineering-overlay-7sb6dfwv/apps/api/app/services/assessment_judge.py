"""Complete submission verification in bounded workers. Browser Run stays Pyodide/PGlite.

This restricted local interpreter is not remote proctoring or a general Python sandbox.
Unsupported capabilities fail closed without independent evidence.
"""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from .scoring_policy import typed, equal_typed

WORKERS = Path(__file__).resolve().parents[1] / "workers"


def _process(command, payload, timeout):
    env={k:os.environ[k] for k in ("SystemRoot","WINDIR") if k in os.environ}
    with tempfile.TemporaryDirectory(prefix="forge-assessment-") as directory:
        result=subprocess.run(command,input=json.dumps(payload,allow_nan=False),text=True,encoding="utf-8",
            capture_output=True,timeout=timeout,cwd=directory,env=env)
    if result.returncode:
        raise ValueError("Worker rejected unsupported code or is unavailable")
    return json.loads(result.stdout)


def judge(item, source):
    if not source.strip(): raise ValueError("Source is required")
    c=item.contract
    try:
        if item.kind=="sql":
            node=shutil.which("node")
            if node is None:return {"status":"unverified","reason":"Local SQL worker runtime unavailable"}
            return _process([node,"--max-old-space-size=256",str(WORKERS/"sql_worker.mjs")],{"source":source,"contract":c},30)
        tree=ast.parse(source)
        if c["mode"]=="function":
            functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==c["function_name"]]
            if len(functions)!=1:raise ValueError("Required function signature missing or ambiguous")
            if c.get("parameters") is not None and ([a.arg for a in functions[0].args.args]!=c["parameters"] or functions[0].args.vararg or functions[0].args.kwarg or functions[0].args.kwonlyargs or functions[0].args.posonlyargs):
                raise ValueError("Function parameters differ from the contract")
        passed=0
        for test in c["tests"]:
            request={"code":source,"args":test.get("args",[]),"kwargs":test.get("kwargs",{}),"stdin":test.get("stdin","")}
            if c["mode"]=="function":request["function_name"]=c["function_name"]
            actual=_process([sys.executable,"-I","-S",str(WORKERS/"python_worker.py")],request,5)
            good=actual["exception"]==test.get("expected_exception")
            if good and actual["exception"] is None:
                if c["mode"]=="stdin_stdout":
                    rules=c.get("stdout_normalization",{})
                    def normalize(text):
                        if rules.get("trim_trailing_whitespace",True):text="\n".join(line.rstrip() for line in text.splitlines())
                        return text.rstrip("\n") if rules.get("ignore_final_newline",True) else text
                    good=normalize(actual["stdout"])==normalize(test["expected_stdout"])
                else:good=equal_typed(actual["returned"],test.get("expected_typed",typed(test.get("expected"))))
            passed+=bool(good)
        return {"status":"verified","passed":passed,"total":len(c["tests"])}
    except SyntaxError:
        return {"status":"verified","passed":0,"total":len(c.get("tests",[])),"reason":"Syntax error"}
    except subprocess.TimeoutExpired:
        if item.kind=="sql":
            return {"status":"unverified","reason":"SQL worker did not finish verification; no mastery credit"}
        return {"status":"verified","passed":0,"total":len(c.get("tests",c.get("datasets",[]))),"reason":"Worker time limit exceeded"}
    except (ValueError, OSError, KeyError, json.JSONDecodeError):
        return {"status":"unverified","reason":"Worker unavailable or unsupported code; no mastery credit"}
