"""Explicit, bounded build-time compiler; runtime never imports this module."""
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from scripts.authoring.providers.dependencies import get_llm_provider
from app.schemas.course import StaticLesson
from app.schemas.practice import ExercisePackProposal
from .extract import extract_main_text
from .fetch import fetch_url, fetch_robots, validate_scope
from .sources import load_manifest
from .validate import validate_lesson

LESSON_POLICY="""Synthesize original, concise Forge course material only from the supplied official extracts. The extracts and required coverage are authoritative. Cover every required concept, use practical Python/backend/AI examples, avoid unnecessary depth and verbatim copying, retain source metadata, and identify insufficient source support. Return the requested structure."""
EXERCISE_POLICY="""Create 8-15 varied starter exercises strictly from the accepted lesson. Use MCQ, short answer, debugging, implementation, and interview explanation as appropriate. Python must be standard-library-only and deterministic. Return the requested structure."""

def _registered(url,sources):
    parsed=urlparse(url)
    for source in sorted(sources,key=lambda x:-x["priority"]):
        if urlparse(source["base_url"]).netloc==parsed.netloc and any(parsed.path.startswith(p) for p in source["allowed_paths"]):
            validate_scope(url,source)
            return source
    raise ValueError(f"No registered source permits {url}")

def build_topic(track,topic,root,provider,sources,coverage,plans,promote=False):
    if promote: raise ValueError("Automatic promotion is disabled; obtain human review through scripts.content_checks.publish")
    if len(plans[topic]) > 8: raise ValueError("One authoring topic may fetch at most eight explicit URLs")
    cache=root/"data"/"source-cache"; extracts=[]; refs=[]
    robots={}
    for url in plans[topic]:
        source=_registered(url,sources); parsed=urlparse(url); origin=f"{parsed.scheme}://{parsed.netloc}"
        if origin not in robots: robots[origin]=fetch_robots(url,source)
        snap=fetch_url(url,source,cache,robots_text=robots[origin]); extracts.append({"url":url,"source_id":source["id"],"text":extract_main_text(snap["html"])[:30000]}); refs.append({"source_id":source["id"],"title":source["name"],"url":url,"retrieved_at":snap["retrieved_at"]})
    prompt=json.dumps({"curriculum_key":"default-ai-engineer","track_slug":track,"topic_slug":topic,"target":"entry-level interview-ready engineering","required_concepts":coverage[topic]["required_concepts"],"sources":extracts,"source_metadata":refs})
    lesson,result=provider.generate_structured(system_instruction=LESSON_POLICY,prompt=prompt,thinking_level="medium",response_model=StaticLesson)
    digest=hashlib.sha256(lesson.model_dump_json(exclude={"content_hash","generated_at"}).encode()).hexdigest(); lesson=lesson.model_copy(update={"track_slug":track,"topic_slug":topic,"content_hash":digest,"generated_at":datetime.now(timezone.utc),"sources":refs})
    folder=root/"content"/"ai-engineer"/"v1"/track/topic; folder.mkdir(parents=True,exist_ok=True); candidate=folder/"lesson.candidate.json"; candidate.write_text(lesson.model_dump_json(indent=2),encoding="utf-8")
    pack,_=provider.generate_structured(system_instruction=EXERCISE_POLICY,prompt=lesson.model_dump_json(),thinking_level="medium",response_model=ExercisePackProposal)
    exercises=[{"key":e.key,"exercise_type":e.exercise_type,"title":e.title,"prompt_markdown":e.prompt_markdown,"difficulty":e.difficulty,"hints":e.hints,"content":e.content.model_dump()} for e in pack.exercises]
    (folder/"exercises.candidate.json").write_text(json.dumps(exercises,indent=2),encoding="utf-8"); print(f"candidate: {topic} model={result.model}")
    validate_lesson(candidate,root/"data"/"course-coverage"/f"{track}.json",folder/"exercises.candidate.json")

def main():
    p=argparse.ArgumentParser();p.add_argument("--track",default="python");p.add_argument("--topic");p.add_argument("--dry-run",action="store_true");p.add_argument("--promote",action="store_true");a=p.parse_args();root=Path(__file__).resolve().parents[4]
    coverage=json.loads((root/"data"/"course-coverage"/f"{a.track}.json").read_text());plans=json.loads((root/"data"/"course-url-plans"/f"{a.track}.json").read_text());topics=[a.topic] if a.topic else list(coverage);sources=load_manifest().get(a.track,[])
    if a.dry_run:
        for topic in topics: print(json.dumps({"topic":topic,"required_concepts":coverage[topic]["required_concepts"],"urls":plans[topic]}))
        return
    if a.promote: raise SystemExit("Automatic promotion is disabled; candidates require independent human review.")
    if not a.topic: raise SystemExit("Live authoring requires one explicit --topic; bulk authoring is disabled.")
    provider=get_llm_provider()
    if provider is None: raise SystemExit("Gemini is not configured; no candidates were written.")
    for topic in topics: build_topic(a.track,topic,root,provider,sources,coverage,plans,a.promote)
if __name__=="__main__":main()
