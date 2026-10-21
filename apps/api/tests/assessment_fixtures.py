"""Synthetic reviewed fixtures ONLY. Never ship these as educational approvals."""
from sqlmodel import select
from app import models as m
from app.schemas.assessment import AssessmentItem
from app.schemas.publication import Candidate
from app.services.content_registry import digest
from app.services.content_publication import publish_release
from tests.test_content_publication import approved_package


def topic(session,subject="python",slug="syntax-data-types"):
    return session.exec(select(m.Topic).join(m.Track).where(m.Track.curriculum_id==1,m.Track.slug==subject,m.Topic.slug==slug)).one()


def item(key="test-choice",kind="single_choice",purposes=None,**overrides):
    contracts={
        "single_choice":{"choices":{"a":"One","b":"Two"},"correct":["a"]},
        "multi_choice":{"choices":{"a":"One","b":"Two","c":"Three"},"correct":["a","c"]},
        "numeric":{"answer":"1.25","tolerance":"0.01","unit":"m","rounding":"none","boundary":"inclusive","representation":"decimal"},
        "python":{"mode":"function","function_name":"solve","parameters":["x"],"starter_code":"def solve(x):\n    pass","reference_solution":"def solve(x):\n    return x + 1",
            "tests":[{"name":"normal","args":[1],"expected":2},{"name":"edge","args":[-1],"expected":0}],"sample_tests":[{"name":"normal","args":[1],"expected":2}],"negative_solutions":["def solve(x):\n    return 0"]},
        "reflection":{"rubric":["Explain your reasoning honestly"],"example":"Describe the choice and its practical limits."},
        "sql":{"columns":["v"],"ordered":False,"reference_solution":"SELECT v FROM t", "datasets":[{"setup_sql":"CREATE TABLE t(v int); INSERT INTO t VALUES (1),(1),(NULL);","expected_rows":[[1],[1],[None]]},{"setup_sql":"CREATE TABLE t(v int); INSERT INTO t VALUES (2),(NULL);","expected_rows":[[2],[None]]}],"negative_solutions":["SELECT DISTINCT v FROM t"]},
    }
    return AssessmentItem.model_validate({"key":key,"family":"test-family/"+key,"subject":"python","topic":"syntax-data-types","level":1,
        "kind":kind,"purposes":purposes or ["practice"],"independent_variant":bool(purposes and "transfer" in purposes),
        "prompt":"TEST ONLY: demonstrate the fixed assessment contract.","explanation":"TEST ONLY explanation of the expected contract.","hints":["TEST ONLY progressive hint"],"contract":contracts[kind],**overrides})


def publish(session,items,selected_topic=None,release="test-assessment-release"):
    t=selected_topic or topic(session)
    track=session.get(m.Track,t.track_id)
    items=[i.model_copy(update={"subject":track.slug,"topic":t.slug}) for i in items]
    candidate=Candidate(content_key=f"assessment/placement-foundations/{track.slug}/{t.slug}",revision="1.0.0",content_type="assessment_bundle",
        payload={"assessment":{"key":f"assessment/placement-foundations/{track.slug}/{t.slug}","version":"1.0.0","items":[i.model_dump(mode="json") for i in items]}},
        provenance={"origin":"original","author":"TEST ONLY author","sources":[]},coverage={"key":"test-assessment","version":"1","competencies":[{"id":i.key,"status":"covered","lesson_refs":["explanation/"+i.key],"assessment_refs":["item/"+i.key]} for i in items]})
    package=approved_package(session,candidate,release,track.slug+"/"+t.slug)
    publish_release(session,package)
    return t
