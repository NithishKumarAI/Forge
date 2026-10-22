"""Optional exact author-supplied proofs, never an editorial approval."""
from fractions import Fraction


def arithmetic(tree, depth=0):
    if depth > 12:
        raise ValueError("Arithmetic proof is too deep")
    if isinstance(tree, str) and len(tree) <= 40:
        return Fraction(tree)
    if not isinstance(tree, dict) or set(tree) != {"op", "args"} or len(tree["args"]) != 2:
        raise ValueError("Expected a bounded binary arithmetic proof")
    a, b = [arithmetic(child, depth + 1) for child in tree["args"]]
    operations = {"add": lambda: a+b, "subtract": lambda: a-b,
                  "multiply": lambda: a*b, "divide": lambda: a/b}
    if tree["op"] not in operations:
        raise ValueError("Unknown arithmetic proof operation")
    result = operations[tree["op"]]()
    if max(result.numerator.bit_length(), result.denominator.bit_length()) > 256:
        raise ValueError("Arithmetic proof exceeds supported bounds")
    return result


def check_subject_accuracy(item):
    contract = item.contract
    if "exact_derivation" in contract:
        if item.kind != "numeric" or arithmetic(contract["exact_derivation"]) != Fraction(contract["answer"]):
            raise ValueError("Exact mathematical derivation contradicts answer")
        return "exact_rational_derivation_checked"
    if "sequence_proof" in contract:
        proof = contract["sequence_proof"]
        if set(proof) != {"start", "step", "position"} or any(type(v) is not int for v in proof.values()) or not 1 <= proof["position"] <= 100:
            raise ValueError("Explicit bounded sequence rule required")
        terms = [proof["start"]]
        for _ in range(1, proof["position"]):
            terms.append(terms[-1] + proof["step"])
        if item.kind != "numeric" or Fraction(str(terms[-1])) != Fraction(contract["answer"]):
            raise ValueError("Enumerated sequence contradicts answer")
        return "explicit_sequence_enumerated"
    return "human_semantic_review_required"
