"""Independent exhaustive static census; flags are evidence, not human approval."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def census(output):
    lessons=[];exercises=[];examples=[];findings=[]
    for path in sorted((ROOT/'content/ai-engineer/v1').glob('*/*/lesson.json')):
        lesson=json.loads(path.read_text(encoding='utf-8'));exercise_path=path.with_name('exercises.json')
        items=json.loads(exercise_path.read_text(encoding='utf-8'));flags=[]
        record={'file':path.relative_to(ROOT).as_posix(),'track':lesson['track_slug'],'topic':lesson['topic_slug'],'title':lesson['title'],
                'version':lesson['version'],'objectives':lesson['learning_objectives'],'prerequisites':lesson['prerequisites'],
                'sections':len(lesson['sections']),'examples':sum(len(s['examples']) for s in lesson['sections']),'exercises':len(items),'sources':lesson['sources'],'flags':flags}
        for section in lesson['sections']:
            if 'count as clean transfer evidence' in section['markdown']:
                flags.append('arena_transfer_claim')
                findings.append({'file':record['file'],'key':section['slug'],'defect':'arena_transfer_claim','existing':section['markdown'],
                    'expected':'Approved Arena evidence is a distinct arena/practice source. A clean transfer requires the dedicated eligible unseen transfer route; legacy Arena awards no new approved credit.'})
            for index,example in enumerate(section['examples']):
                examples.append({'file':record['file'],'section':section['slug'],'index':index,**example})
            codes=[e['code'] for e in section['examples']]
            for other in lesson['sections']:
                if other['order_index']<section['order_index'] and any(code in [e['code'] for e in other['examples']] for code in codes):
                    flags.append('repeated_worked_example');break
        for item in items:
            content=item['content'];item_flags=[]
            answer=content.get('reference_answer','')
            if answer.startswith(('A strong answer records','Handle the boundary explicitly','Answers may vary. The implementation must','A complete answer defines the mechanism')):
                item_flags.append('generic_reference_answer')
            if item['prompt_markdown'].startswith(('Which answer best demonstrates sound use of','Which interview explanation of')):
                item_flags.append('generic_objective_question')
            if 'the sample but fails on an empty input or a tie' in item['prompt_markdown']:
                item_flags.append('missing_program_contract')
            if item['exercise_type']=='multiple_choice':
                if not 0<=content['correct_index']<len(content['choices']):item_flags.append('invalid_choice_index')
                if len(set(content['choices']))!=len(content['choices']):item_flags.append('duplicate_choices')
            row={'file':exercise_path.relative_to(ROOT).as_posix(),'lesson':record['file'],'key':item['key'],'kind':item['exercise_type'],'prompt':item['prompt_markdown'],
                 'reference_answer':answer,'choices':content.get('choices'),'correct_index':content.get('correct_index'),'explanation':content.get('explanation'),
                 'hints':item.get('hints',[]),'difficulty':item['difficulty'],'flags':item_flags}
            exercises.append(row)
            for flag in item_flags:findings.append({'file':row['file'],'key':item['key'],'defect':flag,'existing':answer if flag=='generic_reference_answer' else item['prompt_markdown'],
                'expected':'A topic-specific, fully specified task with a concrete worked answer, tested boundaries and an explanation tied to its actual inputs.'})
            flags.extend(item_flags)
        record['flags']=dict(Counter(flags));lessons.append(record)
    lesson_ids={(r['track'],r['topic']) for r in lessons}
    for row in lessons:row['missing_local_prerequisites']=[p for p in row['prerequisites'] if (row['track'],p) not in lesson_ids]
    problems=[]
    for path in sorted((ROOT/'content/problem-bank').glob('*/*.json')):
        value=json.loads(path.read_text(encoding='utf-8'));contract=value['validation']
        problems.append({'file':path.relative_to(ROOT).as_posix(),'key':value['key'],'revision':value['version'],'track':value['track'],
            'sample_count':len(contract.get('sample_tests',[])),'hidden_count':len(contract.get('hidden_tests',contract.get('hidden_datasets',[]))),
            'source_type':value.get('source_type'),'source_project':value.get('source_project'),'adapted':value.get('adapted'),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    result={'method':'Complete static scan, exact code/output worker execution performed separately. Flags are not a human factual or licensing certification.',
        'totals':{'lessons':len(lessons),'exercises':len(exercises),'examples':len(examples),'problem_files':len(problems),
                  'exercise_kinds':dict(Counter(r['kind'] for r in exercises)),'example_languages':dict(Counter(r['language'] for r in examples)),
                  'finding_categories':dict(Counter(r['defect'] for r in findings))},
        'lessons':lessons,'exercises':exercises,'examples':examples,'problems':problems,'findings':findings}
    output.mkdir(parents=True,exist_ok=True);(output/'content-census.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result['totals']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);census(parser.parse_args().output)
