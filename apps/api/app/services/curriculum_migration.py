import json
from pathlib import Path
from sqlmodel import Session,select
from ..models import Curriculum,Topic,TopicMigrationMap,Track

def _topics(session,curriculum_id):
    rows=session.exec(select(Topic,Track).join(Track,Topic.track_id==Track.id).where(Track.curriculum_id==curriculum_id)).all()
    return {f"{track.slug}/{topic.slug}":topic for topic,track in rows}

def migrate_default_v2(session:Session,old:Curriculum,new:Curriculum,path:Path)->int:
    """Record legacy lineage only. Selection and evidence never migrate implicitly.

    Not invoked during startup. Previously copied scores/selection are preserved as
    historical data; this helper must not copy them again on an upgraded database.
    """
    payload=json.loads(path.read_text(encoding="utf-8"));old_topics=_topics(session,old.id);new_topics=_topics(session,new.id);count=0
    for old_key,new_key in payload["mappings"].items():
        old_topic,new_topic=old_topics.get(old_key),new_topics.get(new_key)
        if not old_topic or not new_topic:continue
        if session.get(TopicMigrationMap,(old_topic.id,new_topic.id)):continue
        session.add(TopicMigrationMap(old_topic_id=old_topic.id,new_topic_id=new_topic.id,mapping_key=f"{old_key}->{new_key}"));count+=1
    session.commit();return count
