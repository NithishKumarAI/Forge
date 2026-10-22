"""SYNTHETIC verification database only. Refuses existing/outside-scratch paths."""
import argparse
import copy
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def prepare(database):
    database=database.resolve()
    if not database.is_relative_to(ROOT/'scratch') or database.exists():raise ValueError('Choose a new database under repository scratch; learner DBs are forbidden')
    database.parent.mkdir(parents=True,exist_ok=True)
    os.environ['FORGE_DATABASE_URL']='sqlite:///'+database.as_posix()
    os.environ['FORGE_CONTENT_SNAPSHOT_PATH']=str(database.parent/'snapshots')
    os.environ['FORGE_DATABASE_BACKUP_PATH']=str(database.parent/'backups')
    sys.path.insert(0,str(ROOT/'apps/api'))
    from sqlmodel import Session,create_engine,select
    from app import models as m
    from app.config import settings
    from app.migrations import run_migrations
    from app.services.curriculum import seed_default_curriculum
    from app.services.course import sync_course_pack
    from app.services.arena import sync_problem_bank
    from app.services.editions import create_placement_draft
    from app.services.active_curriculum import activate_curriculum
    from app.services.content_registry import digest,database_graph
    from app.services.content_publication import publish_release
    from app.services import assessment as a
    from app.schemas.assessment import AssessmentSubmission
    from tests.test_editions import confirm
    from tests.test_content_publication import approved_package
    engine=create_engine('sqlite:///'+database.as_posix());run_migrations(engine)
    with Session(engine) as session:
        seed_default_curriculum(session,settings.curriculum_path);seed_default_curriculum(session,settings.curriculum_v2_path)
        sync_course_pack(session);sync_problem_bank(session)
        curriculum=confirm(session,create_placement_draft(session));activate_curriculum(session,curriculum)
        entries=[];answers={};sources={};topics={}
        for path in sorted((ROOT/'data/content-approvals/phase5/candidates').glob('*.json')):
            value=json.loads(path.read_text(encoding='utf-8'))
            if value['content_type']=='assessment_bundle':
                bundle=value['payload']['assessment'];subject=bundle['items'][0]['subject'];topic=bundle['items'][0]['topic']
                value['revision']=bundle['version']='browser-1'
                original=copy.deepcopy(bundle['items'])
                for index in range(6):
                    bundle['items'].append({'key':f'browser-mock-{subject}-{index}','family':f'SYNTHETIC/{subject}/mock-{index}','subject':subject,'topic':topic,'level':1,
                        'kind':'single_choice','purposes':['interview'],'independent_variant':False,'prompt':'SYNTHETIC TEST FIXTURE: choose Alpha to verify persistence and deterministic scoring.',
                        'explanation':'This synthetic item tests application mechanics; it is not educational coverage.','hints':[],
                        'contract':{'choices':{'a':'Alpha','b':'Beta'},'correct':['a']}})
                coding=next((i for i in original if i['kind'] in {'python','sql'}),None)
                if coding:
                    coding=copy.deepcopy(coding);coding.update(key='browser-code-'+subject,family='SYNTHETIC/'+subject+'/coding',purposes=['interview'],independent_variant=False)
                    bundle['items'].append(coding)
                # Coverage must reference every synthetic addition explicitly.
                value['coverage']['competencies']=[{'id':i['key'],'status':'covered','lesson_refs':['explanation/'+i['key']],'assessment_refs':['item/'+i['key']]} for i in bundle['items']]
                for i in bundle['items']:
                    if i['kind'] in {'python','sql'}:sources[i['key']]=i['contract']['reference_solution']
                    elif i['kind']=='numeric':answers[i['key']]=i['contract']['answer']
                    elif i['kind']=='single_choice':answers[i['key']]=i['contract']['correct'][0]
            else:
                lesson=value['payload']['lesson'];subject=lesson['track_slug'];topic=lesson['topic_slug']
            package=approved_package(session,value,'synthetic-browser')
            package['entries'][0]['targets']=[{'source_type':'custom','curriculum_id':curriculum.id,'curriculum_name':curriculum.name,'curriculum_version':curriculum.version,
                'graph_sha256':digest(database_graph(session,curriculum)),'topic':subject+'/'+topic}]
            entries.extend(package['entries'])
            target=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id,m.Track.slug==subject,m.Topic.slug==topic)).one()
            topics[subject]=target.id
        publish_release(session,{'format_version':1,'release_id':'synthetic-browser-verification','entries':entries})
        # Construct a genuine deterministic *synthetic* past-time sequence for the
        # 24-hour browser recall gate. Never mutate/delete an already recorded event.
        past=datetime.now(timezone.utc)-timedelta(hours=73)
        topic=session.get(m.Topic,topics['dsa'])
        for offset in range(2):
            item=a.start(session,topic,now=past+timedelta(minutes=offset))
            a.submit(session,session.get(m.AssessmentSelection,item['id']),AssessmentSubmission(content_sha256=item['content_sha256'],source=sources[item['item_key']]),now=past+timedelta(minutes=offset))
        item=a.start(session,topic,'transfer',now=past+timedelta(minutes=3))
        a.submit(session,session.get(m.AssessmentSelection,item['id']),AssessmentSubmission(content_sha256=item['content_sha256'],source=sources[item['item_key']]),now=past+timedelta(minutes=3))
        session.add(m.ChatMessage(topic_id=topics['python'],role='assistant',chat_type='doubt',content='SYNTHETIC HISTORICAL CHAT: preserve this original message without generation.'))
        legacy=m.InterviewSession(curriculum_id=curriculum.id,mode='unknown-legacy-test-mode',status='completed',overall_score=61,metadata_json='{"model":"historical synthetic fixture"}')
        session.add(legacy);session.flush()
        session.add(m.InterviewReport(session_id=legacy.id,report_json='{"overall_score":61,"unknown_legacy_field":"HISTORICAL_SYNTHETIC_NOT_REWRITTEN"}'));session.commit()
        manifest={'SYNTHETIC_TEST_DATA_ONLY':True,'database':str(database),'curriculum_id':curriculum.id,'topics':topics,'answers':answers,'sources':sources,'legacy_interview_id':legacy.id,
                  'past_recall_fixture':'DSA practice/transfer executed with an explicit past test clock; no historical evidence was rewritten'}
        (database.parent/'fixture.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    engine.dispose();print('Synthetic browser fixture prepared:',database)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--database',required=True,type=Path)
    prepare(parser.parse_args().database)
