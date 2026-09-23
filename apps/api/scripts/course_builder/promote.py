from pathlib import Path
from .validate import validate_lesson

def promote(track:str,topic:str)->Path:
    root=Path(__file__).resolve().parents[4]; folder=root/"content"/"ai-engineer"/"v1"/track/topic; candidate=folder/"lesson.candidate.json"; accepted=folder/"lesson.json"
    if not candidate.exists(): raise FileNotFoundError("No candidate lesson exists")
    validate_lesson(candidate,root/"data"/"course-coverage"/f"{track}.json")
    exercise_candidate=folder/"exercises.candidate.json"
    if not exercise_candidate.exists(): raise FileNotFoundError("No candidate exercise bank exists")
    candidate.replace(accepted); exercise_candidate.replace(folder/"exercises.json"); return accepted
def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("--track",default="python"); p.add_argument("--topic",required=True); a=p.parse_args(); print(promote(a.track,a.topic))
if __name__=="__main__": main()
