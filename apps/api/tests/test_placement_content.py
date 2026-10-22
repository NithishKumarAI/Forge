"""Candidate checks do not approve or publish educational content."""
import json
import pytest
from fractions import Fraction
from scripts.content_checks.subject_accuracy import arithmetic,check_subject_accuracy
from scripts.placement_batch import ROOT
from app.schemas.assessment import AssessmentItem
from app.schemas.publication import Candidate
from app.services.content_registry import digest


def test_review_batch_has_nine_subjects_exact_candidate_reports_and_no_human_review():
    subjects=set()
    paths=list((ROOT/'candidates').glob('*.json'));assert len(paths)==18
    for path in paths:
        candidate=Candidate.model_validate_json(path.read_text(encoding='utf-8'))
        report=json.loads((ROOT/'validation'/(path.stem+'.validation.json')).read_text(encoding='utf-8'))
        assert report['candidate_sha256']==digest(candidate.model_dump(mode='json'))
        assert report['approved'] is False and report['editorial_status']=='awaiting_human_review'
        if candidate.content_type=='assessment_bundle':
            for item in candidate.payload['assessment']['items']:
                selected=AssessmentItem.model_validate(item);subjects.add(selected.subject)
                if selected.kind=='single_choice':assert set(selected.contract['choices'])=={'a','b'}
                check_subject_accuracy(selected)
    assert len(subjects)==9
    assert not list(ROOT.glob('*.human-review.json'))


def test_arithmetic_proof_is_exact_and_never_evaluates_code():
    assert arithmetic({'op':'divide','args':['1','3']})==Fraction(1,3)
    with pytest.raises((ValueError,TypeError)):arithmetic("__import__('os')")
    with pytest.raises(ValueError):arithmetic({'op':'eval','args':['1','2']})


def test_wrong_math_answer_and_off_by_one_sequence_proofs_are_rejected():
    from tests.assessment_fixtures import item
    selected=item(kind='numeric');selected.contract.update(answer='4',exact_derivation={'op':'add','args':['1','2']})
    with pytest.raises(ValueError,match='contradicts'):check_subject_accuracy(selected)

    selected.contract.pop('exact_derivation');selected.contract.update(answer='17',sequence_proof={'start':2,'step':3,'position':5})
    with pytest.raises(ValueError,match='contradicts'):check_subject_accuracy(selected)


def test_choice_id_cannot_reveal_answer_before_submission():
    from tests.assessment_fixtures import item
    value=item().model_dump();value['contract']={'choices':{'correct':'One','wrong':'Two'},'correct':['correct']}
    with pytest.raises(ValueError,match='encode correctness'):AssessmentItem.model_validate(value)


def test_full_inventory_retains_all_scope_identities_and_truthful_depths():
    from app.config import REPO_ROOT
    value=json.loads((REPO_ROOT/'data/placement-foundations-coverage.json').read_text(encoding='utf-8'))
    scope=json.loads((REPO_ROOT/'data/placement-foundations-scope.json').read_text(encoding='utf-8'))
    assert {r['topic_key'] for r in value['topics']}=={t['key'] for t in scope['topics']}
    assert len(value['topics'])==157 and value['totals']['candidate_lessons']==9
    assert all(r['publication_status']=='unpublished' and not any(r['published_pool_depth'].values()) for r in value['topics'])


def test_exact_batch_can_publish_only_with_synthetic_reviews_in_isolated_database(session):
    from app import models as m
    from sqlmodel import select
    from app.services import editions
    from tests.test_editions import confirm
    from tests.test_content_publication import approved_package
    from app.services.content_registry import database_graph
    from app.services.content_publication import publish_release
    from app.services.editions import availability
    curriculum=confirm(session,editions.create_placement_draft(session))
    entries=[]
    for path in sorted((ROOT/'candidates').glob('*.json')):
        candidate=Candidate.model_validate_json(path.read_text(encoding='utf-8'))
        content=candidate.payload.get('lesson')
        item=candidate.payload.get('assessment',{}).get('items',[{}])[0]
        subject=content['track_slug'] if content else item['subject']
        topic=content['topic_slug'] if content else item['topic']
        package=approved_package(session,candidate,'SYNTHETIC-ONLY')
        package['entries'][0]['targets']=[{'source_type':'custom','curriculum_id':curriculum.id,'curriculum_name':curriculum.name,
            'curriculum_version':curriculum.version,'graph_sha256':digest(database_graph(session,curriculum)),
            'topic':subject+'/'+topic,'order_index':0}]
        entries.extend(package['entries'])
    publish_release(session,{'format_version':1,'release_id':'synthetic-batch-test','entries':entries})
    topics=session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==curriculum.id)).all()
    assert sum(availability(session,t)['approved_lesson_count'] for t in topics)==9
    assert not session.exec(select(m.MasteryEvidenceEvent)).all()
