from decimal import Decimal
import pytest
from app.schemas.assessment import AssessmentItem
from app.services.scoring_policy import objective,typed,equal_typed
from app.services.assessment_judge import judge
from tests.assessment_fixtures import item

@pytest.mark.parametrize("answer,passed",[("a",True),("b",False)])
def test_single_choice_identity(answer,passed):assert objective(item(),answer)==passed

@pytest.mark.parametrize("answer,passed",[(["a","c"],True),(["c","a"],True),(["a"],False),(["b"],False)])
def test_multi_select_exact_set(answer,passed):assert objective(item(kind="multi_choice"),answer)==passed

@pytest.mark.parametrize("mutation",["missing","unknown","duplicate","multi_single"])
def test_invalid_answer_contract(mutation):
    value=item().model_dump();value["contract"]["correct"]={"missing":[],"unknown":["z"],"duplicate":["a","a"],"multi_single":["a","b"]}[mutation]
    with pytest.raises(ValueError):AssessmentItem.model_validate(value)

@pytest.mark.parametrize("answer,unit,passed",[("1.25","m",True),("1.26","m",True),("1.24","m",True),("1.260001","m",False),("1.25","cm",False),("125","m",False)])
def test_decimal_tolerance_inclusive_and_units(answer,unit,passed):assert objective(item(kind="numeric"),answer,unit)==passed

@pytest.mark.parametrize("answer",["1/4","__import__('os')","NaN","Infinity"])
def test_numeric_never_evaluates_expressions(answer):
    with pytest.raises(ValueError):objective(item(kind="numeric"),answer,"m")

@pytest.mark.parametrize("key,value",[("tolerance","-1"),("tolerance","NaN"),("answer","Infinity"),("rounding","guess"),("boundary","exclusive")])
def test_bad_numeric_policy_rejected(key,value):
    value_item=item(kind="numeric").model_dump();value_item["contract"][key]=value
    with pytest.raises(ValueError):AssessmentItem.model_validate(value_item)

@pytest.mark.parametrize("a,b",[([1],(1,)),(True,1),({"x":[False]},{"x":[0]}),([1],[1.0])])
def test_strict_nested_types(a,b):assert not equal_typed(typed(a),typed(b))

def test_python_worker_executes_full_contract_and_rejects_claims():
    selected=item(kind="python")
    assert judge(selected,"def solve(x):\n    return x+1")=={"status":"verified","passed":2,"total":2}
    assert judge(selected,"def solve(x):\n    return True")["passed"]==0
    assert judge(selected,"import os\ndef solve(x):\n    return x+1")["status"]=="unverified"

def test_python_tuple_exception_and_stdio():
    selected=item(kind="python")
    selected.contract["tests"]=[{"name":"nested","args":[1],"expected":[1]}]
    assert judge(selected,"def solve(x):\n    return (x,)")["passed"]==0
    selected.contract["tests"]=[{"name":"exception","args":[1],"expected_exception":"ValueError"}]
    assert judge(selected,"def solve(x):\n    raise ValueError('no')")["passed"]==1
    selected.contract.update(mode="stdin_stdout",tests=[{"name":"stdin","stdin":"2\n","expected_stdout":"3"}])
    assert judge(selected,"print(int(input())+1)")["passed"]==1

def test_sql_worker_preserves_duplicates_null_columns_and_order():
    selected=item(kind="sql")
    assert judge(selected,"SELECT v FROM t")["passed"]==2
    assert judge(selected,"SELECT DISTINCT v FROM t")["passed"]<2
    assert judge(selected,"SELECT v FROM t WHERE v IS NOT NULL")["passed"]==0
    assert judge(selected,"SELECT v AS wrong FROM t")["passed"]==0
    selected.contract["ordered"]=True
    assert judge(selected,"SELECT v FROM t ORDER BY v DESC NULLS FIRST")["passed"]==0


def test_sql_runtime_setup_failure_is_unverified_and_dates_numeric_are_explicit():
    selected=item(kind="sql")
    selected.contract.update(columns=["d","n"],datasets=[
        {"setup_sql":"CREATE TABLE t(d date,n numeric); INSERT INTO t VALUES ('2024-01-02',1.20);",
         "expected_rows":[["2024-01-02T00:00:00.000Z","1.20"]]} for _ in range(2)])
    assert judge(selected,"SELECT d,n FROM t")["passed"]==2
    selected.contract["datasets"][0]["setup_sql"]="INVALID FIXTURE"
    assert judge(selected,"SELECT d,n FROM t")["status"]=="unverified"
