import json
from pathlib import Path

from sqlmodel import Session, select

from ..models import AppSetting, Curriculum, LearnerTopicState, Topic, TopicPrerequisite, Track


def seed_default_curriculum(session: Session, curriculum_path: Path) -> Curriculum:
    payload = json.loads(curriculum_path.read_text(encoding="utf-8"))
    existing = session.exec(
        select(Curriculum).where(
            Curriculum.name == payload["name"], Curriculum.version == payload["version"]
        )
    ).first()
    if existing:
        if session.get(AppSetting, "active_curriculum_id") is None:
            session.add(AppSetting(key="active_curriculum_id", value=str(existing.id)))
            session.commit()
        return existing

    curriculum = Curriculum(
        name=payload["name"],
        description=payload["description"],
        source_type="default",
        status="confirmed",
        version=payload["version"],
        confirmed_at=payload.get("confirmed_at"),
    )
    session.add(curriculum)
    session.flush()

    topics_by_key: dict[str, Topic] = {}
    prerequisites: list[tuple[str, str]] = []
    for track_index, track_data in enumerate(payload["tracks"], start=1):
        track = Track(
            curriculum_id=curriculum.id,
            name=track_data["name"],
            slug=track_data["slug"],
            description=track_data["description"],
            order_index=track_index,
            priority=track_data.get("priority", 50),
        )
        session.add(track)
        session.flush()
        for topic_index, topic_data in enumerate(track_data["topics"], start=1):
            topic = Topic(
                track_id=track.id,
                name=topic_data["name"],
                slug=topic_data["slug"],
                description=topic_data.get(
                    "description", f"Understand and apply {topic_data['name'].lower()}."
                ),
                order_index=topic_index,
                priority=topic_data.get("priority", track.priority),
                target_level=topic_data.get("target_level", "working"),
                estimated_minutes=topic_data.get("estimated_minutes", 45),
            )
            session.add(topic)
            session.flush()
            key = f"{track.slug}/{topic.slug}"
            topics_by_key[key] = topic
            session.add(LearnerTopicState(topic_id=topic.id))
            for prerequisite in topic_data.get("prerequisites", []):
                prerequisites.append((key, prerequisite))

    for topic_key, prerequisite_key in prerequisites:
        topic = topics_by_key.get(topic_key)
        prerequisite = topics_by_key.get(prerequisite_key)
        if topic is None or prerequisite is None:
            raise ValueError(f"Unknown prerequisite link: {prerequisite_key} -> {topic_key}")
        session.add(
            TopicPrerequisite(
                topic_id=topic.id, prerequisite_topic_id=prerequisite.id
            )
        )

    session.commit()
    session.refresh(curriculum)
    if session.get(AppSetting, "active_curriculum_id") is None:
        session.add(AppSetting(key="active_curriculum_id", value=str(curriculum.id)))
        session.commit()
    return curriculum
