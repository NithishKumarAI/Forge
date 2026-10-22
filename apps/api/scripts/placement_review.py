"""Render exact candidate solutions for a genuine human reviewer; never approve."""
import json
from scripts.placement_batch import ROOT
from app.schemas.publication import Candidate,QUALITY_CHECKS
from app.services.content_registry import digest


def packets():
    directory=ROOT/"review";directory.mkdir(exist_ok=True)
    for lesson_path in sorted((ROOT/"candidates").glob("*.lesson.json")):
        key=lesson_path.name.removesuffix(".lesson.json")
        lines=["# Human review packet: "+key,"", "UNPUBLISHED. Agent-authored material. No human approval is present. The checked references are factual references; no publisher text or illustrations are redistributed.","",
               "Review the exact JSON and validation reports. If any candidate changes, validation/review digests must be regenerated; an old approval cannot cover new bytes.",""]
        for suffix in ["lesson","assessment"]:
            path=ROOT/"candidates"/(key+"."+suffix+".json");value=json.loads(path.read_text(encoding="utf-8"));report=ROOT/"validation"/(path.stem+".validation.json")
            lines += ["## "+suffix,"",f"Candidate: `{path.relative_to(ROOT)}`",f"Candidate SHA-256: `{digest(Candidate.model_validate(value).model_dump(mode='json'))}`",f"Validation: `{report.relative_to(ROOT)}`","",
                      "Provenance and factual references:","```json",json.dumps(value["provenance"],indent=2),"```",""]
            if suffix=="lesson":
                for section in value["payload"]["lesson"]["sections"]:lines += ["### "+section["title"],"",section["markdown"],""]
            else:
                for item in value["payload"]["assessment"]["items"]:
                    lines += ["### "+item["key"]+" ("+", ".join(item["purposes"])+")","",item["prompt"],"",item["explanation"],"", "Exact scoring contract / worked solution / fixtures:","```json",json.dumps(item["contract"],indent=2,ensure_ascii=False),"```",""]
        lines += ["## Known uncertainties and reviewer decisions","",
                  "- Proposed coverage is an author claim, not a completed human review. Check every learning outcome against teaching and independent evidence.",
                  "- Verify source relevance, original expression, factual accuracy, beginner sequencing and legitimate alternative answers.",
                  "- Verify transfer families require actual independent application rather than a superficial rewording. Revise/reject if inadequate; never approve by count.",
                  "- Confirm the restricted Python subset/PGlite contracts assess the intended competency. Reflection must stay unscored.",
                  "- No title-based historical mapping is authorized. Remaining Level 1–3 topics are not covered by this packet.","", "## Reviewer checklist (all unchecked)",""]
        lines += ["- [ ] "+name.replace("_"," ") for name in QUALITY_CHECKS]
        lines += ["", "## Authorized human actions", "",
                  "1. Read both exact candidates, all worked answers/fixtures, validation reports and references. Edit/revalidate if any check is unsatisfied.",
                  "2. Copy `review-checklist.template.json`; only personally completed checks may become true. Use the existing `scripts.content_checks.publish review` command with your actual name and `--i-am-the-human-reviewer`, separately for each candidate.",
                  "3. Explicitly review/confirm the Placement Foundations graph in Forge (confirmation does not approve content). Export its actual curriculum ID and graph digest for release targets. No graph or reviewer identity is guessed here.",
                  "4. Use `scripts.content_checks.publish package` for each reviewed candidate/target and combine entries into one canonical complete overlay. Run the existing publish CLI only after checking the exact package and destination DB. Preserve previous approved entries when constructing an overlay.",
                  "See `data/content-approvals/README.md` for exact CLI arguments and backup/restore safeguards. No review or publication command was run by this agent.",""]
        (directory/(key+".md")).write_text("\n".join(lines),encoding="utf-8")
    print("9 review packets prepared; no human review or publication")


if __name__=="__main__":packets()
