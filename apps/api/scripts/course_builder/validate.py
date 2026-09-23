import ast, json
from pathlib import Path
from app.schemas.course import StaticLesson

def validate_lesson(path:Path, coverage_path:Path)->StaticLesson:
    lesson=StaticLesson.model_validate_json(path.read_text(encoding="utf-8")); coverage=json.loads(coverage_path.read_text(encoding="utf-8"))[lesson.topic_slug]["required_concepts"]
    corpus=" ".join([lesson.title,*lesson.learning_objectives,*lesson.summary,*lesson.interview_takeaways,*[s.title+" "+s.markdown+" "+" ".join(s.key_points) for s in lesson.sections]]).lower()
    missing=[c for c in coverage if c.lower() not in corpus]
    if missing: raise ValueError("Missing required concepts: "+", ".join(missing))
    for section in lesson.sections:
        for example in section.examples:
            if example.language.lower()=="python": ast.parse(example.code)
    if len(corpus)>100_000: raise ValueError("Lesson is too large")
    return lesson

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("--track",default="python"); p.add_argument("--topic"); args=p.parse_args()
    root=Path(__file__).resolve().parents[4]; base=root/"content"/"ai-engineer"/"v1"/args.track; coverage=root/"data"/"course-coverage"/f"{args.track}.json"
    paths=[base/args.topic/"lesson.json"] if args.topic else list(base.glob("*/lesson.json"))
    for path in paths: validate_lesson(path,coverage); print(f"valid: {path}")
if __name__=="__main__": main()
