"""Explicitly synthetic approvals for disposable tests; never real editorial records."""
import json
from sqlmodel import select
from app import models as m
from app.schemas.publication import Candidate
from app.services.editions import create_placement_draft
from app.services.active_curriculum import activate_curriculum
from app.services.content_registry import database_graph,digest
from app.services.content_publication import publish_release
from tests.test_editions import confirm
from tests.test_content_publication import approved_package
from tests.assessment_fixtures import item


def published_scope(session,per_subject=2,purposes=None):
    curriculum=confirm(session,create_placement_draft(session));activate_curriculum(session,curriculum)
    entries=[]
    for track in session.exec(select(m.Track).where(m.Track.curriculum_id==curriculum.id)).all():
        topics=session.exec(select(m.Topic).where(m.Topic.track_id==track.id).order_by(m.Topic.order_index)).all()[:per_subject]
        for topic in topics:
            selected=item('synthetic-'+str(topic.id),purposes=purposes or ['practice','recall','interview'],subject=track.slug,topic=topic.slug)
            key=f'assessment/placement-foundations/{track.slug}/{topic.slug}'
            candidate=Candidate(content_key=key,revision='1',content_type='assessment_bundle',payload={'assessment':{'key':key,'version':'1','items':[selected.model_dump(mode='json')]}},
                provenance={'origin':'original','author':'TEST ONLY','sources':[]},coverage={'key':'synthetic-'+str(topic.id),'version':'1','competencies':[{'id':'test','status':'covered','lesson_refs':['explanation/'+selected.key],'assessment_refs':['item/'+selected.key]}]})
            package=approved_package(session,candidate,'synthetic-only')
            package['entries'][0]['targets']=[{'source_type':'custom','curriculum_id':curriculum.id,'curriculum_name':curriculum.name,'curriculum_version':curriculum.version,
                'graph_sha256':digest(database_graph(session,curriculum)),'topic':track.slug+'/'+topic.slug}]
            entries.extend(package['entries'])
    publish_release(session,{'format_version':1,'release_id':'synthetic-phase5-test','entries':entries})
    return curriculum
