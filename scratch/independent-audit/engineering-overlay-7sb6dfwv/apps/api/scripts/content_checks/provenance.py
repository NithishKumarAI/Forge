"""Conservative publication policy; historical claims are preserved, not certified."""
import json
from pathlib import Path
from urllib.parse import urlparse
from app.services.content_registry import digest


from app.services.content_policy import check_provenance

def inventory(root: Path):
    output = []
    for path in sorted(root.glob("*/*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        adapted = bool(raw.get("adapted") or raw.get("source_project") or raw.get("source_type") == "adapted")
        conflict = bool(adapted and raw.get("source_type") == "original")
        reason = "No pinned per-item upstream revision/notice chain" if adapted else "Legacy originality claim; independent review not recorded"
        if raw["key"] == "python-celsius-to-fahrenheit":
            reason = "Historical attribution document claimed adaptation; JSON does not. Resolve origin before new publication."
        output.append({"key": raw["key"], "revision": raw["version"], "sha256": digest({"problem": raw}),
            "path": path.relative_to(root).as_posix(), "classification": "adapted" if adapted else "declared_original",
            "declared_metadata": {k: raw[k] for k in ("source_type", "source_project", "source_exercise", "license", "adapted") if k in raw},
            "metadata_conflict": conflict, "status": "unresolved" if adapted or raw["key"] == "python-celsius-to-fahrenheit" else "requires_review",
            "new_publication_allowed": False, "reason": reason,
            "upstream_candidate_url": ("https://github.com/exercism/problem-specifications/tree/main/exercises/" + raw["source_exercise"]) if adapted and raw.get("source_exercise") else None,
            "upstream_reference_status": "unverified; repository-level MIT license checked separately; per-item commit unknown" if adapted else "not_applicable"})
    return {"format_version": 1, "problems": output}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(inventory(Path(__file__).resolve().parents[4] / "content/problem-bank"), indent=2) + "\n", encoding="utf-8")
