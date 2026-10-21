"""Historical interview reads never fabricate continuation or rewrite saved model values."""
import json
import pytest
from app import models as m
from app.services import interview

def test_unknown_historical_mode_keeps_questions_answers_rubric_and_report(session):
    row=m.InterviewSession(curriculum_id=1,mode='retired-custom-mode',status='saved',metadata_json='{"model":"historical"}')
    session.add(row);session.flush()
    q=m.InterviewQuestion(session_id=row.id,section='project',competency='Old project',question_type='project',prompt_markdown='Explain the saved project',rubric_json='{"old_weight":1}',generated_by='gemini')
    session.add(q);session.flush()
    response=m.InterviewResponse(question_id=q.id,response_text='My original project explanation',score=63,evaluation_json='{"model_feedback":"Original assessment"}')
    session.add(response);session.add(m.InterviewReport(session_id=row.id,report_json='{"overall_score":63,"legacy":true}'));session.commit()
    session.refresh(row);session.refresh(q);session.refresh(response);before=(row.model_dump(),q.model_dump(),response.model_dump())
    read=interview.interview_read(session,row)
    assert read['read_only'] and read['questions'][0]['rubric_json']=='{"old_weight":1}'
    assert read['responses'][0]['saved_answer']=='My original project explanation'
    assert interview.report_for(session,row.id)=={'overall_score':63,'legacy':True}
    with pytest.raises(ValueError):interview.transition(session,row,'resume')
    assert (row.model_dump(),q.model_dump(),response.model_dump())==before
