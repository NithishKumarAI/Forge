import argparse,json
from pathlib import Path
from app.config import settings
from app.providers.dependencies import get_llm_provider
from app.schemas.arena import CodingProblem
POLICY="""Create one original Forge interview problem. Do not copy external problem statements. Use only easy or common-medium difficulty. Include deterministic validation, progressive hints, a correct reference solution, explanation, and complexity. Python/DSA must use standard-library code. SQL initially supports SELECT and PostgreSQL-compatible fixtures. Return the requested structure."""
def main():
    p=argparse.ArgumentParser();p.add_argument("--track",choices=["python","sql","dsa"],required=True);p.add_argument("--topic",required=True);p.add_argument("--difficulty",choices=["easy","medium"],required=True);p.add_argument("--key",required=True);p.add_argument("--dry-run",action="store_true");a=p.parse_args();summary=vars(a)
    if a.dry_run:print(json.dumps(summary));return
    provider=get_llm_provider()
    if not provider:raise SystemExit("Gemini is not configured; no candidate was written.")
    root=Path(__file__).resolve().parents[4]/"content"/"problem-bank";existing=[json.loads(x.read_text())["title"] for x in root.glob("*/*.json")]
    problem,_=provider.generate_structured(system_instruction=POLICY,prompt=json.dumps({**summary,"existing_titles":existing}),thinking_level="medium",response_model=CodingProblem)
    if problem.key!=a.key or problem.track!=a.track or problem.difficulty!=a.difficulty:raise SystemExit("Generated problem changed fixed build parameters")
    target=root/a.track/f"{a.key}.candidate.json";target.write_text(problem.model_dump_json(indent=2),encoding="utf-8");print(target)
if __name__=="__main__":main()
