from pathlib import Path
from .validate import validate_problem
def promote(track,key):
    root=Path(__file__).resolve().parents[4]/"content"/"problem-bank"/track;candidate=root/f"{key}.candidate.json";validate_problem(candidate);target=root/f"{key}.json";candidate.replace(target);return target
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--track",required=True);p.add_argument("--problem",required=True);a=p.parse_args();print(promote(a.track,a.problem))
if __name__=="__main__":main()
