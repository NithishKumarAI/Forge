"""Check the actual local FastAPI surface required by the committed frontend."""
import pytest
from pydantic import ValidationError
from app.main import create_app
from app.schemas.timed_tests import TimedStart,TimedAnswer


def test_committed_phase5_frontend_routes_are_registered_locally():
    schema=create_app().openapi()
    expected={
        '/api/planner/today':'get','/api/planner/regenerate':'post','/api/planner/options':'get',
        '/api/planner/items/{item_id}/replace':'post','/api/planner/settings':'get',
        '/api/timed-tests/start':'post','/api/timed-tests/history':'get','/api/timed-tests/{key}':'get',
        '/api/timed-tests/{key}/draft':'post','/api/timed-tests/{key}/answer':'post',
        '/api/timed-tests/{key}/complete':'post','/api/timed-tests/{key}/abandon':'post',
    }
    for path,method in expected.items():assert method in schema['paths'][path]
    operation_ids=[operation['operationId'] for path in schema['paths'].values() for method,operation in path.items() if method in {'get','post','put','patch','delete','options'}]
    assert len(operation_ids)==len(set(operation_ids))
    assert schema['components']['schemas']['TimedAnswer']['additionalProperties'] is False


@pytest.mark.parametrize('value',[True,1.0,'1'])
def test_level_and_question_position_require_actual_json_integers(value):
    with pytest.raises(ValidationError):TimedStart(kind='subject',subject='python',level=value)
    with pytest.raises(ValidationError):TimedAnswer(position=value,content_sha256='a'*64,answer=['a'])
