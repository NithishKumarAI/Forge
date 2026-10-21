"""Versioned immutable assessment contracts; free text is never objectively scored."""
from decimal import Decimal, InvalidOperation
from typing import Literal
from pydantic import Field, StrictInt, model_validator
from .content_registry import StrictModel


class AssessmentItem(StrictModel):
    key: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    family: str = Field(min_length=3, max_length=120)
    subject: str
    topic: str
    level: int = Field(ge=1, le=5)
    kind: Literal["single_choice", "multi_choice", "numeric", "python", "sql", "reflection"]
    purposes: list[Literal["practice", "transfer", "recall", "interview"]] = Field(min_length=1)
    independent_variant: bool = False
    prompt: str = Field(min_length=10, max_length=12000)
    explanation: str = Field(min_length=10, max_length=12000)
    hints: list[str] = Field(default_factory=list, max_length=3)
    contract: dict

    @model_validator(mode="after")
    def valid_contract(self):
        c = self.contract
        if self.kind in {"single_choice", "multi_choice"}:
            choices = c.get("choices", {})
            correct = c.get("correct", [])
            if (not isinstance(choices, dict) or not 2 <= len(choices) <= 8 or not isinstance(correct,list) or not correct
                    or len(correct) != len(set(correct)) or not set(correct) <= set(choices)
                    or self.kind == "single_choice" and len(correct) != 1):
                raise ValueError("Invalid immutable choice answer identities")
            if any(not isinstance(k,str) or not k.strip() or not isinstance(v,str) or not v.strip() for k,v in choices.items()) or len({v.strip().casefold() for v in choices.values()})!=len(choices):
                raise ValueError("Choice identities/text must be distinct and nonblank")
        elif self.kind == "numeric":
            if any(type(c.get(k)) is not str or len(c[k])>120 for k in ("answer","tolerance")):
                raise ValueError("Numeric answers and tolerances must be exact decimal strings")
            try:
                expected, tolerance = Decimal(c["answer"]), Decimal(c["tolerance"])
            except (KeyError, InvalidOperation, TypeError):
                raise ValueError("Explicit decimal answer/tolerance required")
            if (not expected.is_finite() or not tolerance.is_finite() or tolerance < 0 or abs(expected.adjusted())>1000 or abs(tolerance.adjusted())>1000
                    or c.get("rounding") != "none" or c.get("boundary") != "inclusive"
                    or not isinstance(c.get("unit"), str) or c.get("representation") != "decimal"):
                raise ValueError("Unsupported numeric units/tolerance/rounding policy")
        elif self.kind == "python":
            if not isinstance(c.get("tests"),list) or not 1<=len(c["tests"])<=100 or c.get("mode") not in {"function", "stdin_stdout"}:
                raise ValueError("Python needs complete fixtures and explicit mode")
            for test in c["tests"]:
                if not isinstance(test,dict) or not isinstance(test.get("name"),str) or not test["name"].strip():raise ValueError("Named Python fixture objects required")
                if not isinstance(test.get("args",[]),list) or not isinstance(test.get("kwargs",{}),dict):raise ValueError("Explicit function argument containers required")
                if c["mode"]=="function" and not any(key in test for key in ("expected","expected_typed","expected_exception")):raise ValueError("Typed result or exception required")
                if c["mode"]=="stdin_stdout" and not all(isinstance(test.get(key),str) for key in ("stdin","expected_stdout")):raise ValueError("Explicit stdin/stdout fixture required")
            if c["mode"] == "function" and not c.get("function_name", "").isidentifier():
                raise ValueError("Python function identity required")
            if c["mode"] == "function" and (not isinstance(c.get("parameters"),list) or any(not isinstance(p,str) or not p.isidentifier() for p in c["parameters"]) or len(c["parameters"])!=len(set(c["parameters"]))):
                raise ValueError("Explicit unambiguous function parameters required")
            names = [t.get("name") for t in c["tests"]]
            if None in names or len(names) != len(set(names)):
                raise ValueError("Unique fixture names required")
            if not c.get("starter_code") or not c.get("reference_solution"):
                raise ValueError("Starter and reference required")
        elif self.kind == "sql":
            if not isinstance(c.get("datasets"),list) or not 2<=len(c["datasets"])<=10 or not isinstance(c.get("columns"),list) or not c["columns"] or any(not isinstance(name,str) or not name.strip() for name in c["columns"]) or type(c.get("ordered")) is not bool:
                raise ValueError("SQL needs visible/alternate datasets, columns and ordering")
            if len(c["columns"])!=len(set(c["columns"])):raise ValueError("SQL columns must have distinct identities")
            for dataset in c["datasets"]:
                if not isinstance(dataset,dict) or not isinstance(dataset.get("setup_sql"),str) or not isinstance(dataset.get("expected_rows"),list):raise ValueError("Explicit SQL fixture schema/rows required")
                if any(not isinstance(row,list) or len(row)!=len(c["columns"]) for row in dataset["expected_rows"]):raise ValueError("SQL expected row/column arity mismatch")
            if c.get("public_dataset") is not None and (not isinstance(c["public_dataset"],dict) or set(c["public_dataset"])!={"setup_sql"} or not isinstance(c["public_dataset"]["setup_sql"],str)):
                raise ValueError("Public SQL fixture may contain schema/setup only")
            if not c.get("reference_solution"):
                raise ValueError("SQL reference required")
        elif not c.get("rubric") or not c.get("example"):
            raise ValueError("Reflection needs a prewritten rubric and example")
        if "transfer" in self.purposes and not self.independent_variant:
            raise ValueError("Transfer requires reviewed independent variant classification")
        return self


class AssessmentBundle(StrictModel):
    key: str
    version: str
    items: list[AssessmentItem] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_items(self):
        if len({i.key for i in self.items}) != len(self.items):
            raise ValueError("Duplicate assessment item identity")
        return self


class AssessmentStart(StrictModel):
    topic_id: StrictInt
    purpose: Literal["practice", "transfer", "recall"] = "practice"


class AssessmentSubmission(StrictModel):
    content_sha256: str
    answer: str | list[str] = ""
    unit: str = ""
    source: str = Field(default="", max_length=20000)
