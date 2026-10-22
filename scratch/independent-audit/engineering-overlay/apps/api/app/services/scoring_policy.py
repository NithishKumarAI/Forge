"""Pure scoring: inclusive Decimal tolerance and exact choice identities."""
from decimal import Decimal, InvalidOperation, localcontext

POLICY_VERSION = "forge-evidence/2"
JUDGE_VERSION = "forge-worker/1"


def objective(item, answer, unit=""):
    c = item.contract
    if item.kind in {"single_choice", "multi_choice"}:
        submitted = [answer] if isinstance(answer, str) else answer
        if len(submitted) != len(set(submitted)) or not set(submitted) <= set(c["choices"]):
            raise ValueError("Choose valid distinct answer identities")
        if item.kind == "single_choice" and len(submitted) != 1:
            raise ValueError("Choose exactly one answer")
        return set(submitted) == set(c["correct"])
    if item.kind == "numeric":
        if not isinstance(answer, str) or len(answer) > 120:
            raise ValueError("Use a decimal numeral, not an expression")
        try:
            value = Decimal(answer)
        except InvalidOperation:
            raise ValueError("Use a decimal numeral, not an expression")
        if not value.is_finite():
            raise ValueError("Finite decimal required")
        if abs(value.adjusted())>1000:raise ValueError("Decimal exponent exceeds supported bounds")
        with localcontext() as context:
            context.prec=4096
            return unit == c["unit"] and abs(value - Decimal(c["answer"])) <= Decimal(c["tolerance"])
    raise ValueError("This item does not have an objective answer")


def typed(value):
    if type(value) in (list, tuple):
        return {"type":type(value).__name__,"value":[typed(x) for x in value]}
    if type(value) is dict:
        return {"type":"dict","value":[{"key":typed(k),"value":typed(v)} for k,v in value.items()]}
    return {"type":type(value).__name__,"value":value}


def equal_typed(a,b):
    if a["type"] != b["type"]: return False
    kind,left,right=a["type"],a.get("value"),b.get("value")
    if kind in {"list","tuple"}:
        return len(left)==len(right) and all(equal_typed(x,y) for x,y in zip(left,right))
    if kind=="dict":
        return len(left)==len(right) and all(any(equal_typed(x["key"],y["key"]) and equal_typed(x["value"],y["value"]) for y in right) for x in left)
    return type(left) is type(right) and left==right
