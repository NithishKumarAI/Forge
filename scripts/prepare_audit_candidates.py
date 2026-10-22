"""Local-only correction drafts. Never approves, publishes or edits historical files."""
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps/api'))
from app.services.content_registry import digest
from app.schemas.publication import QUALITY_CHECKS
from scripts.content_checks.bundle import validate_candidate

DEST=ROOT/'data/content-approvals/independent-audit'


def mcq(key,prompt,choices,index,explanation):
    return {'key':key,'exercise_type':'multiple_choice','title':prompt,'prompt_markdown':prompt,'difficulty':'easy',
        'hints':['Trace each call and distinguish a return value from printed output.'],
        'content':{'choices':choices,'correct_index':index,'answer_text':choices[index],'assumptions':'Python 3; execute exactly the code shown in a fresh namespace.','explanation':explanation}}


def short(key,prompt,answer,rubric):
    return {'key':key,'exercise_type':'short_answer','title':prompt.split('.')[0][:90],'prompt_markdown':prompt,'difficulty':'medium',
        'hints':['Write down inputs, the function body, its return value, and one boundary case.'],
        'content':{'reference_answer':answer,'rubric':rubric,'minimum_pass_score':70}}


def functions():
    lesson=json.loads((ROOT/'content/ai-engineer/v1/python/functions/lesson.json').read_text(encoding='utf-8'))
    lesson.update(version='1.2.0',prerequisites=['syntax-data-types','collections'],
        learning_objectives=['Trace arguments, local names and return values','Use positional, keyword, variadic and default arguments safely','Avoid mutable-default and accidental caller-mutation bugs','Implement and test a fully specified pure normalization function'])
    sections=[
      ('calls-and-return','Calls, parameters and returned values',
       'A function groups instructions behind a name. In def cost(price, quantity=1), price and quantity are parameters. cost(4, 3) supplies arguments 4 and 3. Python binds local parameter names, executes the body, and sends the expression after return back to the caller. print displays text; it does not return that text. Reaching the end without return produces None.',
       'def cost(price, quantity=1):\n    return price * quantity\nprint(cost(4, 3))\nprint(cost(quantity=2, price=5))','12\n10'),
      ('local-names','Local names and shared mutable objects',
       'A parameter is a local name referring to the supplied object. Rebinding that name changes the local reference. Mutating a shared list changes the object the caller also sees. A pure helper reads inputs and returns a result without altering caller-owned objects. Use a new list when the contract promises no mutation.',
       'def extended(values, extra):\n    return values + [extra]\noriginal = [2, 4]\nprint(extended(original, 6))\nprint(original)','[2, 4, 6]\n[2, 4]'),
      ('argument-shapes','Defaults, keyword arguments, *args and **kwargs',
       'Defaults make selected arguments optional. Keyword arguments state parameter names explicitly. A star before a parameter collects remaining positional arguments into a tuple; two stars collect remaining keyword arguments into a dictionary. The function below sums positional amounts and obtains an optional adjustment from named options. Unknown or conflicting arguments should have an explicit API policy in real code.',
       "def adjusted_total(*amounts, **options):\n    return sum(amounts) + options.get('adjustment', 0)\nprint(adjusted_total(3, 5, adjustment=2))",'10'),
      ('safe-defaults','A new list for each call',
       'A default expression is evaluated when def executes, not for every later call. A default list can therefore be shared across calls. Use None as a sentinel and allocate a fresh list inside the function when an omitted argument means a fresh collection. This example makes two independent lists; supplying an existing list deliberately allows mutation and should be documented.',
       "def append_item(item, values=None):\n    if values is None:\n        values = []\n    values.append(item)\n    return values\nprint(append_item('a'))\nprint(append_item('b'))","['a']\n['b']"),
      ('worked-normalization','Worked solution: nonnegative score normalization',
       'Contract: scores is a finite list of nonnegative finite numbers. Return a new list; do not mutate scores. Return [] for an empty list. If the maximum is zero, return zeros of the same length; otherwise divide every score by that maximum. Reject negative values with ValueError. First check the domain, then the empty boundary, then find the maximum, then handle zero before division. For [2, 4], the maximum is 4 and the result is [0.5, 1.0]. The algorithm uses O(n) time and O(n) output space. Finite-number validation is an input precondition for this introductory contract, not silently implemented by type hints.',
       'def normalized_scores(scores):\n    if any(value < 0 for value in scores):\n        raise ValueError("scores must be nonnegative")\n    if not scores:\n        return []\n    maximum = max(scores)\n    if maximum == 0:\n        return [0 for value in scores]\n    return [value / maximum for value in scores]\nvalues = [2, 4]\nprint(normalized_scores(values))\nprint(values)\nprint(normalized_scores([]))\nprint(normalized_scores([0, 0]))','[0.5, 1.0]\n[2, 4]\n[]\n[0, 0]'),
      ('revision','Revision and independent practice',
       'Trace a new call before running it. Check return versus print, the binding of positional and keyword arguments, and whether a list is shared. For normalization, test an empty list, all zeros, unequal positive values, a negative value and unchanged caller input. Writing a reflection or reading this lesson never awards mastery. Scored coding requires a reviewed contract in an approved assessment pool; ordinary legacy Arena is not a clean-transfer shortcut.',
       'def label(value):\n    print(value)\nresult = label("ready")\nprint(result)','ready\nNone')]
    lesson['sections']=[{'slug':slug,'title':title,'order_index':n,'estimated_minutes':8,'learning_objective':lesson['learning_objectives'][min(n,3)],'markdown':text,
        'examples':[{'language':'python','code':code,'expected_output':expected,'explanation':'Execute the complete block independently; trace local names and compare the exact printed lines.'}],
        'key_points':['State the exact input/output contract.','Use explicit boundary cases; reading is not mastery.'],'checkpoint':'Predict every printed line and explain the boundary case.'} for n,(slug,title,text,code,expected) in enumerate(sections)]
    lesson['summary']=['Parameters are local names; arguments supply objects.','return sends a value; print displays text.','Defaults are created at definition time.','A pure function preserves caller-owned state and follows a complete boundary contract.']
    lesson['common_mistakes']=['Forgetting return','Sharing a mutable default unintentionally','Mutating an input despite a pure-function contract','Dividing by a zero maximum or calling max on an empty list']
    lesson['interview_takeaways']=['Trace a call with exact values.','Explain shared mutation and default lifetimes.','Support a claimed contract with boundary tests.']
    exercises=[
      mcq('functions-return-none','What does result contain after def announce(): print("hi") followed by result = announce()?',['"hi"','None','0'],1,'The call prints hi but has no return statement, so result is None.'),
      mcq('functions-keyword-binding','For def cost(price, quantity=1): return price * quantity, what is cost(quantity=3, price=4)?',['7','12','4'],1,'Keyword names bind price=4 and quantity=3, so multiplication returns 12.'),
      mcq('functions-default-list','For def add(x, items=[]): items.append(x); return items, what does print(add(1)); print(add(2)) display?',['[1] then [2]','[1] then [1, 2]','[1, 2] twice'],1,'The same default list is reused. The first print happens before the second mutation, so it prints [1], then [1, 2].'),
      short('functions-trace-scope','Trace: x=10; def double(x): return x*2. Explain double(3) and the outer x afterwards.','double(3) returns 6. Its local parameter x refers to 3. The outer x remains 10 because the call does not assign to the outer name.',['Return value 6','Outer x remains 10','Distinguishes the two bindings']),
      short('functions-fix-return','Fix def square(n): print(n*n) so callers can use square(4)+1. State the final value.','Use def square(n): return n*n. square(4) returns 16, so square(4)+1 is 17. Printing alone returns None, which cannot be added to 1.',['Uses return','Explains None from print-only body','Calculates 17']),
      short('functions-normalize-contract','Implement normalized_scores using the full nonnegative finite-list contract in the worked section. Include empty, zero, negative and no-mutation tests.',sections[4][3]+'\nExpected printed output:\n'+sections[4][4]+'\nA call with [-1] must raise ValueError. Finite numbers are an explicit precondition.',['Empty returns []','All-zero avoids division','Rejects negatives','Returns a new list without input mutation','Divides by maximum']),
      short('functions-explain-sharing','Explain why items=[] is unsafe when an omitted argument should create a fresh list. Give the repair.','The default list is constructed once when def executes, then reused. Use items=None and inside the body if items is None: items=[] before appending. Two omitted-argument calls then receive independent lists.',['Definition-time evaluation','Shared list across calls','None sentinel','New allocation per omitted-argument call'])]
    return lesson,exercises


def indexes():
    lesson=json.loads((ROOT/'content/ai-engineer/v1/sql-postgresql/indexes/lesson.json').read_text(encoding='utf-8'))
    lesson['version']='1.2.0'
    lesson['learning_objectives']=['Explain balanced-tree lookup and index maintenance tradeoffs','Choose and inspect composite indexes without universal planner claims','Read plans and distinguish index-only eligibility from zero heap fetches']
    customer="CREATE TABLE customers(id int PRIMARY KEY,email text,signup_date date); INSERT INTO customers VALUES(1,'user@example.com','2026-09-24'); CREATE INDEX idx_customers_email ON customers(email);"
    orders="CREATE TABLE orders(id int PRIMARY KEY,customer_id int,order_date date,total_amount numeric(10,2)); INSERT INTO orders VALUES(5,101,'2026-02-01',120); CREATE INDEX idx_orders_cust_date ON orders(customer_id,order_date);"
    specs=[
      ('btree-fundamentals','B-tree lookup with explicit data','A B-tree organizes keys so an equality lookup navigates a balanced tree. Traversal is logarithmic in indexed entries, but total query cost also includes matches, visibility checks and possible heap access. A small table may still be cheaper to scan. This complete fixture inserts the row before selecting it.',customer,"SELECT id,signup_date::text AS signup_date FROM customers WHERE email='user@example.com';",['id','signup_date'],[[1,'2026-09-24']]),
      ('composite-indexes-and-column-order','Composite key order','An index on (customer_id,order_date) sorts primarily by customer and then date. Equality on the leading key plus a date range directly matches that ordering. Filtering only on a later key is not universally forbidden: the planner may scan the index or use version-dependent strategies, whose cost depends on data. Inspect the actual plan.',orders,"SELECT id,total_amount::int AS total_amount FROM orders WHERE customer_id=101 AND order_date>='2026-01-01';",['id','total_amount'],[[5,120]]),
      ('write-cost-and-index-tradeoffs','Index maintenance and inspection','Indexes consume storage and add maintenance work. Do not equate an insert with a fixed count of physical writes. PostgreSQL uses MVCC and WAL; eligible HOT updates can avoid new index entries, and index cleanup for deleted versions is coordinated with vacuum. In pg_stat_user_indexes, relname is the table name and indexrelname is the index name. Sizes depend on data and environment; no fixed byte count is promised.',orders,"SELECT indexrelname AS index_name FROM pg_stat_user_indexes WHERE indexrelname='idx_orders_cust_date';",['index_name'],[['idx_orders_cust_date']]),
      ('explain-and-query-plans','Inspect a plan instead of inventing it','EXPLAIN shows an estimated plan. EXPLAIN (ANALYZE, BUFFERS) executes the query and reports measured behavior. Never run a mutating EXPLAIN ANALYZE on valuable data without an appropriate disposable transaction. An Index Only Scan still may fetch heap pages for visibility checks unless the relevant pages are marked all-visible. Plans and timings depend on version, statistics, visibility and data, so the example below has no universal exact plan.',customer,"EXPLAIN (ANALYZE, BUFFERS) SELECT email FROM customers WHERE email='user@example.com';",None,None),
      ('revision','Boundary checks and a revision question','Before adding an index, identify the query, expected selectivity, write workload and existing keys. Compare plans and measured work on representative data. Do not infer production latency from a one-row fixture. The following count only checks that the explicitly inserted fixture is present.',customer,'SELECT count(*)::int AS n FROM customers;',['n'],[[1]])]
    lesson['sections']=[];checks=[]
    for n,(slug,title,text,setup,query,columns,rows) in enumerate(specs):
        expected=json.dumps({'columns':columns,'rows':rows}) if columns else 'Plan is environment-dependent; inspect node type, rows and heap fetches rather than a fixed cost or timing.'
        lesson['sections'].append({'slug':slug,'title':title,'order_index':n,'estimated_minutes':8,'learning_objective':lesson['learning_objectives'][min(n,2)],'markdown':text+'\n\nRun this declared setup in a fresh database before the query below:\n```sql\n'+setup.replace('; ',';\n')+'\n```',
            'examples':[{'language':'sql','code':query,'expected_output':expected,'explanation':'Use the complete disposable schema/data declared immediately above. Display casts make deterministic fixture output explicit.'}],
            'key_points':['Planner choices depend on data and version.','Use indexrelname to identify an index.'],'checkpoint':'Explain the input data, result and one limit of the example.'})
        checks.append({'section_slug':slug,'example_index':0,**({'mode':'sql','setup_sql':setup,'expected_columns':columns,'expected_rows':rows,'order_sensitive':True} if columns else {'mode':'context','reason':'EXPLAIN plan/costs depend on data, statistics and engine version; inspect manually, not against invented exact output.'})})
    lesson['summary']=['An index is a tradeoff, not a guarantee of a chosen plan.','Use explicit fixtures and correct catalog columns.','Index Only Scan can still require heap visibility checks.']
    lesson['common_mistakes']=['Inventing rows without inserting data','Filtering a table-name catalog column using an index name','Treating all update paths and physical writes as identical','Treating planner costs or index sizes as portable constants']
    lesson['interview_takeaways']=['State workload and selectivity before proposing an index.','Measure and explain the plan with visibility and write-cost limits.']
    exercises=[mcq('index-catalog-name','Which pg_stat_user_indexes column identifies the index name?',['relname','indexrelname','schemaname'],1,'indexrelname names the index; relname names its table.'),
        mcq('index-only-visibility','Does an Index Only Scan always guarantee zero heap fetches?',['Yes','No'],1,'Visibility checks may still require heap access when pages are not all-visible.'),
        mcq('index-physical-writes','Does adding ten indexes imply exactly eleven physical writes for each insert?',['Yes','No'],1,'Logical index maintenance, buffers and WAL do not imply a fixed physical write count.'),
        short('index-composite-query','For (customer_id,order_date), describe the query pattern that directly uses the leading key and explain the limitation.','Equality on customer_id followed by a range on order_date matches the ordering. Queries omitting the leading key are not universally impossible; inspect plan and cost for the engine version and data.',['Leading equality','Trailing range','Qualifies planner claims']),
        short('index-fix-catalog','Fix a query that filters relname = \'idx_orders_cust_date\' to find that index.','SELECT indexrelname AS index_name FROM pg_stat_user_indexes WHERE indexrelname = \'idx_orders_cust_date\'; relname is the table name.',['Uses indexrelname in projection and filter','Explains table/index difference']),
        short('index-fixture-rows','A sample creates an empty table and then promises a selected row. What must its fixture add?','Insert the exact row before querying, or change the expected result to empty. Declare schema, inserted data, query and ordering together; never invent a row in the answer.',['Explicit inserted data','Correct expected rows','Ordering']),
        short('index-explain-report','What should a worked EXPLAIN example promise instead of a fixed cost or runtime?','Provide complete setup and ask the reader to inspect plan nodes, actual rows and visibility/heap behavior. State engine version and data. Timings and selected plans are observations, not universal expected constants.',['Setup','Measured plan','Version/data context','No invented universal timing'])]
    for item in exercises:
        item['hints']=['Identify the schema, rows and exact catalog fields named in the question.','Separate a logical guarantee from a data-dependent planner or storage observation.']
        if item['exercise_type']=='multiple_choice':item['content']['assumptions']='PostgreSQL; exact catalog-column names and visibility semantics; no universal planner-cost claim.'
    return lesson,exercises,checks


def write_candidate(lesson,exercises,name,context=False,notes='',checks_override=None):
    for item in exercises:
        if item['exercise_type']=='multiple_choice':
            content=item['content']
            content.setdefault('answer_text',content['choices'][content['correct_index']])
            content.setdefault('assumptions','Python 3 in the stated context; environment-dependent examples need the separately reviewed setup.')
    lesson['generated_at']='2026-10-22T00:00:00Z';lesson['content_hash']=digest({k:v for k,v in lesson.items() if k not in {'content_hash','generated_at'}})
    key='ai-engineer/v1/'+lesson['track_slug']+'/'+lesson['topic_slug']
    checks=[]
    for section in lesson['sections']:
        for index,example in enumerate(section['examples']):
            checks.append({'section_slug':section['slug'],'example_index':index,**({'mode':'context','reason':'Unchanged legacy example requires its declared environment/setup and full independent human fixture review. Independent browser audit records actual runtime behavior; this context declaration is not an execution pass.'} if context else {'mode':'python','expected_stdout':example['expected_output']})})
    if checks_override is not None:checks=checks_override
    candidate={'content_key':key,'revision':lesson['version'],'content_type':'lesson_bundle','payload':{'lesson':lesson,'exercises':exercises},
        'provenance':{'origin':'original','author':'AI-assisted audit correction draft; independent human review pending','sources':[{'source_id':s['source_id'],'url':s['url'],'usage':'factual_reference','status':'resolved'} for s in lesson['sources']]},
        'coverage':{'key':lesson['topic_slug']+'-audit-correction','version':'1','competencies':[{'id':'correction','status':'covered','lesson_refs':['section/'+s['slug'] for s in lesson['sections']],'assessment_refs':['exercise/'+e['key'] for e in exercises]}]},
        'example_checks':checks,'prerequisite_keys':lesson['prerequisites'],'known_content':['arena/'+p.stem for p in (ROOT/'content/problem-bank').glob('*/*.json')]}
    path=DEST/'candidates'/(name+'.json');path.parent.mkdir(parents=True,exist_ok=True)
    report=validate_candidate(candidate);folder=DEST/'validation';folder.mkdir(exist_ok=True)
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=candidate:raise ValueError('Refusing to overwrite a different correction draft')
    else:path.write_text(json.dumps(candidate,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (folder/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return {'name':name,'candidate':path.relative_to(ROOT).as_posix(),'candidate_sha256':report['candidate_sha256'],'validation':(folder/(name+'.json')).relative_to(ROOT).as_posix(),
        'review_state':'NOT REVIEWED','publication_state':'UNPUBLISHED','validation_scope':'structural/context only; example setup/semantic review unresolved' if context else 'all six standalone Python examples executed with exact stdout','notes':notes}


def main():
    pairs=[];lesson,exercises=functions();pairs.append(write_candidate(lesson,exercises,'python-functions-1.2.0',notes='Full replacement of generic Functions prompts and worked answers; no scored transfer pool is claimed.'))
    replacements={
      ('python','exceptions','try-except-blocks'):('Catching bare `except:` or broad `except Exception:` without re-raising is a severe anti-pattern that swallows critical system signals like `KeyboardInterrupt`, memory errors, and subtle programming bugs like typos.','A bare except catches BaseException subclasses, including KeyboardInterrupt and SystemExit. except Exception does not catch those two system signals, but can hide ordinary bugs and MemoryError if used without an appropriate boundary policy. Catch specific expected errors inside operations; at a deliberate error boundary, log and handle Exception according to the API contract.'),
      ('python','type-hints','interview-check'):('*(No. Aside from negligible module load time to evaluate annotation dictionaries, type hints are stripped by the compiler and produce no runtime overhead).*','*(Annotations are not automatically enforced as runtime type checks, but their metadata remains available. Annotation evaluation/storage behavior depends on the Python version and configuration; tools can inspect it. Do not claim that annotations are stripped or universally cost-free.)*'),
      ('python','control-flow','truthiness-and-falsiness'):('All other objects evaluate to truthiness.','Other built-in values are generally truthy, but user-defined objects can provide __bool__ or __len__ and can also be falsy. Check the relevant object contract rather than assuming every remaining object is true.')}
    for (track,topic,slug),(old,new) in replacements.items():
        path=ROOT/'content/ai-engineer/v1'/track/topic/'lesson.json';value=json.loads(path.read_text(encoding='utf-8'));section=next(s for s in value['sections'] if s['slug']==slug)
        assert old in section['markdown'];section['markdown']=section['markdown'].replace(old,new);value['version']='1.2.0'
        pairs.append(write_candidate(value,json.loads(path.with_name('exercises.json').read_text(encoding='utf-8')),track+'-'+topic+'-1.2.0',context=True,notes='Focused factual correction only; inherited examples/exercises still need complete environment, pedagogy and semantic review. Not a completed course replacement.'))
    lesson,exercises,checks=indexes()
    pairs.append(write_candidate(lesson,exercises,'sql-indexes-1.2.0',context=True,checks_override=checks,notes='Corrects missing seed rows, relname/indexrelname confusion and universal planner/write/heap-fetch claims. Four exact PGlite examples; EXPLAIN plan intentionally requires contextual human review.'))
    pairs[-1]['validation_scope']='Four exact SQL fixtures executed; one environment-dependent EXPLAIN example remains contextual, not a machine execution certification.'
    (DEST/'review-checklist.template.json').write_text(json.dumps({k:False for k in QUALITY_CHECKS},indent=2)+'\n',encoding='utf-8')
    (DEST/'review-queue.json').write_text(json.dumps({'approved':False,'publication_performed':False,'candidates':pairs},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'new_correction_candidates':len(pairs),'human_reviews':0,'published':0}))


if __name__=='__main__':main()
