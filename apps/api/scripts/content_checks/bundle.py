"""Validate a complete portable candidate; a passing report is not editorial approval."""
import json
from pathlib import Path
import re
from pydantic import ConfigDict
from app.schemas.publication import Candidate, POLICY_VERSION
from app.schemas.arena import CodingProblem
from app.services.content_registry import _validate_identity, _validate_payload, digest
from .coverage import check_coverage
from .examples import check_lesson_examples
from .provenance import check_provenance
from .problems import check_problem


def validate_candidate(value):
    candidate = Candidate.model_validate(value)
    _validate_payload(candidate.content_type, candidate.payload)
    _validate_identity(candidate.content_key, candidate.revision, candidate.content_type, candidate.payload)
    provenance = check_provenance(candidate)
    coverage = check_coverage(candidate)
    if candidate.content_type == "lesson_bundle":
        lesson = candidate.payload["lesson"]
        from app.schemas.course import StaticLesson
        from app.schemas.content_registry import LegacyExercise
        class NewLesson(StaticLesson):
            model_config = ConfigDict(extra="forbid")
        class NewExercise(LegacyExercise):
            model_config = ConfigDict(extra="forbid")
        NewLesson.model_validate(lesson)
        if lesson["content_hash"] != digest({k: v for k, v in lesson.items() if k not in {"content_hash", "generated_at"}}):
            raise ValueError("New lesson canonical content_hash is invalid")
        if set(lesson["prerequisites"]) - set(candidate.prerequisite_keys):
            raise ValueError("Unresolved lesson prerequisite reference")
        if candidate.content_key in lesson["prerequisites"]:
            raise ValueError("A lesson cannot require itself")
        for item in candidate.payload["exercises"]:
            NewExercise.model_validate(item)
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,99}", item["key"]):
                raise ValueError("Invalid stable exercise identity")
            if item.get("version", candidate.revision) != candidate.revision:
                raise ValueError("Exercise/lesson revision inconsistency")
            if item["exercise_type"] == "multiple_choice":
                content = item["content"]
                choices = content["choices"]
                if len(choices) < 2 or len({str(c).strip().casefold() for c in choices}) != len(choices):
                    raise ValueError("MCQ options must be distinct")
                if type(content["correct_index"]) is not int or not content.get("explanation") or not content.get("assumptions"):
                    raise ValueError("MCQ needs answer explanation and explicit assumptions")
                if content.get("answer_text") != choices[content["correct_index"]]:
                    raise ValueError("MCQ answer text contradicts selected index")
            elif item["exercise_type"] in {"python_code", "python_debug"}:
                # No unexecuted coding answer can silently pass the new publication gate.
                raise ValueError("Course coding items require a supported Arena contract; publish as an Arena revision")
        from scripts.course_builder.validate import extract_arena_problem_references
        from app.schemas.course import StaticLesson
        for reference in extract_arena_problem_references(StaticLesson.model_validate(lesson)):
            if "arena/" + reference not in candidate.known_content:
                raise ValueError("Unresolved Arena reference")
        execution = check_lesson_examples(candidate)
    elif candidate.content_type == "assessment_bundle":
        from app.schemas.assessment import AssessmentBundle
        from app.services.assessment_judge import judge
        bundle=AssessmentBundle.model_validate(candidate.payload["assessment"])
        execution=[]
        for item in bundle.items:
            if item.kind in {"python","sql"}:
                checked=judge(item,item.contract["reference_solution"])
                if checked.get("status")!="verified" or checked.get("passed")!=checked.get("total"):
                    raise ValueError("Assessment reference failed full contract")
                if not item.contract.get("negative_solutions"):
                    raise ValueError("Coding assessment needs negative implementations")
                for source in item.contract["negative_solutions"]:
                    wrong=judge(item,source)
                    if wrong.get("status")!="verified" or wrong.get("passed")==wrong.get("total"):
                        raise ValueError("Negative implementation was accepted or unverified")
            execution.append({"item":item.key,"status":"executed" if item.kind in {"python","sql"} else "requires_human_answer_review"})
    else:
        raw = candidate.payload["problem"]
        if raw.get("publication_contract") != candidate.problem_contract or raw.get("negative_solutions", []) != candidate.negative_solutions:
            raise ValueError("Candidate and delivered problem contract/negative fixtures differ")
        execution = check_problem(CodingProblem.model_validate(candidate.payload["problem"]), candidate.problem_contract,
                                  candidate.negative_solutions, require_contract=True)
    return {"policy_version": POLICY_VERSION, "candidate_sha256": digest(candidate.model_dump(mode="json")),
        "payload_sha256": digest(candidate.payload), "coverage_sha256": digest(candidate.coverage),
        "provenance": provenance, "coverage": coverage, "execution": execution,
        "structurally_valid": True, "executable_checks_passed": True,
        "editorial_status": "awaiting_human_review", "approved": False}


def load_candidate(path: Path):
    return Candidate.model_validate_json(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate_candidate(load_candidate(args.candidate)), indent=2))
