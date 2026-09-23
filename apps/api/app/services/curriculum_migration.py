import json
from pathlib import Path
from sqlmodel import Session,select
from ..models import AppSetting,Curriculum,LearnerTopicState,Topic,TopicMigrationMap,Track

def _topics(session,curriculum_id):
    rows=session.exec(select(Topic,Track).join(Track,Topic.track_id==Track.id).where(Track.curriculum_id==curriculum_id)).all()
    return {f"{track.slug}/{topic.slug}":topic for topic,track in rows}

def migrate_default_v2(session:Session,old:Curriculum,new:Curriculum,path:Path)->int:
    payload=json.loads(path.read_text(encoding="utf-8"));old_topics=_topics(session,old.id);new_topics=_topics(session,new.id);count=0
    for old_key,new_key in payload["mappings"].items():
        old_topic,new_topic=old_topics.get(old_key),new_topics.get(new_key)
        if not old_topic or not new_topic:continue
        if session.get(TopicMigrationMap,(old_topic.id,new_topic.id)):continue
        old_state=session.get(LearnerTopicState,old_topic.id);new_state=session.get(LearnerTopicState,new_topic.id)
        if old_state and new_state and new_state.attempts==0:
            new_state.mastery_score,new_state.confidence,new_state.status,new_state.attempts,new_state.last_studied_at,new_state.last_tested_at,new_state.next_review_at=old_state.mastery_score,old_state.confidence,old_state.status,old_state.attempts,old_state.last_studied_at,old_state.last_tested_at,old_state.next_review_at;session.add(new_state)
        session.add(TopicMigrationMap(old_topic_id=old_topic.id,new_topic_id=new_topic.id,mapping_key=f"{old_key}->{new_key}"));count+=1
    active=session.get(AppSetting,"active_curriculum_id")
    if active and active.value==str(old.id):active.value=str(new.id);session.add(active)
    session.commit();return count
