"""Pure backend publication gates. No execution, fetching or provider imports."""
from urllib.parse import urlparse
from .content_registry import digest


def check_coverage(candidate):
    spec = candidate.coverage
    if not spec.get("key") or not spec.get("version") or not spec.get("competencies"):
        raise ValueError("Versioned coverage specification is required")
    if candidate.content_type == "lesson_bundle":
        lesson = candidate.payload["lesson"]
        lessons = {"section/" + s["slug"] for s in lesson["sections"]}
        assessments = {"exercise/" + e["key"] for e in candidate.payload["exercises"]}
    else:
        problem = candidate.payload["problem"]
        lessons = {"statement", "explanation"}
        assessments = {"test/" + t["name"] for t in problem["validation"].get("sample_tests", []) + problem["validation"].get("hidden_tests", [])}
        if problem["track"] == "sql":
            assessments = {"dataset/visible"} | {"dataset/" + d["name"] for d in problem["validation"]["hidden_datasets"]}
    ids, result = set(), []
    for item in spec["competencies"]:
        key = item["id"]
        if not key or key in ids:
            raise ValueError("Coverage competency identities must be unique")
        ids.add(key)
        teaching, checks = item.get("lesson_refs", []), item.get("assessment_refs", [])
        if not set(teaching) <= lessons or not set(checks) <= assessments:
            raise ValueError("Coverage contains dangling teaching/assessment references")
        status = item.get("status", "requires_review")
        if status not in {"covered", "partially_covered", "missing", "requires_review"}:
            raise ValueError("Invalid coverage status")
        if not teaching or not checks:
            status = "missing"
        result.append({"id": key, "status": status, "lesson_refs": teaching, "assessment_refs": checks})
    return result


def check_provenance(candidate):
    record = candidate.provenance
    if (record.get("origin") not in {"original", "approved_license"}
            or not isinstance(record.get("author"), str) or not record["author"].strip()):
        raise ValueError("Explicit original/approved-license provenance and author are required")
    content = candidate.payload.get("problem", candidate.payload.get("lesson", {}))
    adapted = content.get("adapted") or content.get("source_type") == "adapted" or content.get("source_project")
    if adapted and record["origin"] == "original":
        raise ValueError("Adapted content cannot claim original provenance")
    if candidate.content_type == "arena_problem" and (adapted or record["origin"] != "original"):
        raise ValueError("New Arena releases require original challenges; adapted history remains legacy")
    sources = record.get("sources", [])
    if record["origin"] == "approved_license" and not sources:
        raise ValueError("Missing license sources")
    for source in sources:
        if not source.get("source_id") or urlparse(source.get("url", "")).scheme != "https":
            raise ValueError("Source identity and HTTPS reference are required")
        usage = source.get("usage")
        if usage not in {"factual_reference", "redistributed"}:
            raise ValueError("Separate factual reference from redistribution permission")
        if usage == "redistributed":
            if (source.get("license") not in {"MIT", "PSF-2.0", "PostgreSQL", "CC0-1.0"}
                    or not all(source.get(k) for k in ("upstream_revision", "notice", "permission_evidence"))):
                raise ValueError("Unresolved license/notice/upstream permission blocks publication")
        if source.get("status") != "resolved":
            raise ValueError("Unresolved provenance blocks publication")
    if candidate.content_type == "lesson_bundle":
        declared = {(s["source_id"], s["url"]) for s in content["sources"]}
        if declared != {(s["source_id"], s["url"]) for s in sources}:
            raise ValueError("Lesson and provenance source metadata differ")
    return {"status": "requires_human_review", "sha256": digest(record)}
