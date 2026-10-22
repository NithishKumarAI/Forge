"""Negative contract probes use bounded workers and never write attempts/evidence."""
import ast
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'apps/api'))
from app.services.assessment_pool import arena_item
from app.services.assessment_judge import judge


def decoded(value):
    kind=value['type'];raw=value.get('value')
    if kind in {'tuple','list'}:return (tuple if kind=='tuple' else list)(decoded(x) for x in raw)
    if kind=='dict':return {decoded(x['key']):decoded(x['value']) for x in raw}
    return raw


def main():
    results=[]
    for path in sorted((ROOT/'content/problem-bank').glob('*/*.json')):
        p=json.loads(path.read_text(encoding='utf-8'))
        if p['track']=='sql' or p['validation'].get('judge_mode','function')!='function':continue
        item=arena_item(p);first=item.contract['tests'][0]
        expected=decoded(first['expected_typed']) if 'expected_typed' in first else first.get('expected')
        source=f"def {item.contract['function_name']}({', '.join(item.contract['parameters'])}):\n    return {expected!r}"
        result=judge(item,source)
        results.append({'key':p['key'],'file':path.relative_to(ROOT).as_posix(),'probe':'constant first-sample answer','accepted':result.get('status')=='verified' and result['passed']==result['total'],'result':result})
    in_place=[]
    for key,source in {
        'dsa-move-zeroes':'def move_zeroes(nums):\n    return [x for x in nums if x != 0] + [0] * nums.count(0)',
        'dsa-sort-colors':'def sort_colors(nums):\n    return sorted(nums)',
        'dsa-reverse-string':'def reverse_string(chars):\n    return chars[::-1]',
        'dsa-remove-duplicates-sorted':'def remove_duplicates(nums):\n    return sorted(set(nums))',
    }.items():
        path=ROOT/'content/problem-bank/dsa'/(key+'.json');p=json.loads(path.read_text(encoding='utf-8'));result=judge(arena_item(p),source)
        in_place.append({'key':key,'file':path.relative_to(ROOT).as_posix(),'probe':'returns correct values without required input mutation','source':source,'accepted':result.get('status')=='verified' and result['passed']==result['total'],'result':result})
    p=json.loads((ROOT/'content/problem-bank/dsa/dsa-two-sum-indices.json').read_text(encoding='utf-8'))
    source=p['reference_solution'].replace('return [seen[need], i]','return (seen[need], i)')
    if source==p['reference_solution']:
        source='def two_sum(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        if target - value in seen:\n            return (seen[target-value], i)\n        seen[value] = i\n    return ()'
    tuple_result=judge(arena_item(p),source)
    value={'method':'One constant-answer mutant per eligible non-SQL function, plus four input-mutation probes. Not a proof of complete contract correctness.',
           'constant_answer_probes':results,'constant_answers_accepted':sum(r['accepted'] for r in results),'in_place_probes':in_place,
           'two_sum_tuple_statement_probe':{'source':source,'result':tuple_result,'statement_requires_tuple':True},'no_database_access':True}
    (ROOT/'docs/forge-v1/audit-evidence/contract-probes.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'constant_probes':len(results),'constants_accepted':value['constant_answers_accepted'],'in_place_constraint_bypasses':sum(r['accepted'] for r in in_place),'two_sum_tuple':tuple_result}))


if __name__=='__main__':main()
