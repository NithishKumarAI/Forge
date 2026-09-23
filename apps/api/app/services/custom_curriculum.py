import json

from sqlalchemy import func
from sqlmodel import Session, delete, select

from ..models import (
    Curriculum,
    CurriculumGenerationMetadata,
    LearnerTopicState,
    Topic,
    TopicPrerequisite,
    Track,
)
from ..schemas.ai import CurriculumDraftRequest, CurriculumProposal, TopicProposal, TrackProposal
from ..models.entities import utc_now


class CurriculumMutationError(ValueError):
    pass


def _flags(proposal: CurriculumProposal) -> dict[str, bool]:
    return {
        topic.key: topic.added_as_prerequisite
        for track in proposal.tracks
        for topic in track.topics
    }


def _write_structure(
    session: Session, curriculum: Curriculum, request: CurriculumDraftRequest
) -> None:
    proposal = request.proposal
    topics_by_key: dict[str, Topic] = {}
    prerequisite_links: list[tuple[str, str]] = []
    for track_index, track_data in enumerate(proposal.tracks, start=1):
        track = Track(
            curriculum_id=curriculum.id,
            name=track_data.name,
            slug=track_data.key,
            description=track_data.description,
            order_index=track_index,
            priority=track_data.priority,
        )
        session.add(track)
        session.flush()
        for topic_index, topic_data in enumerate(track_data.topics, start=1):
            topic = Topic(
                track_id=track.id,
                name=topic_data.name,
                slug=topic_data.key,
                description=topic_data.description,
                order_index=topic_index,
                priority=topic_data.priority,
                target_level=topic_data.target_level,
                estimated_minutes=topic_data.estimated_minutes,
            )
            session.add(topic)
            session.flush()
            topics_by_key[topic_data.key] = topic
            session.add(LearnerTopicState(topic_id=topic.id))
            prerequisite_links.extend(
                (topic_data.key, prerequisite) for prerequisite in topic_data.prerequisites
            )
    for topic_key, prerequisite_key in prerequisite_links:
        session.add(
            TopicPrerequisite(
                topic_id=topics_by_key[topic_key].id,
                prerequisite_topic_id=topics_by_key[prerequisite_key].id,
            )
        )
    metadata = session.get(CurriculumGenerationMetadata, curriculum.id)
    if metadata is None:
        metadata = CurriculumGenerationMetadata(curriculum_id=curriculum.id)
    metadata.goal = proposal.goal
    metadata.source_requirements = request.source_requirements
    metadata.topic_flags_json = json.dumps(_flags(proposal))
    session.add(metadata)


def create_draft(session: Session, request: CurriculumDraftRequest) -> Curriculum:
    proposal = request.proposal
    latest_version = session.exec(
        select(func.max(Curriculum.version)).where(Curriculum.name == proposal.name)
    ).one()
    curriculum = Curriculum(
        name=proposal.name,
        description=proposal.description,
        source_type="custom",
        status="draft",
        version=(latest_version or 0) + 1,
    )
    session.add(curriculum)
    session.flush()
    _write_structure(session, curriculum, request)
    session.commit()
    session.refresh(curriculum)
    return curriculum


def _delete_structure(session: Session, curriculum_id: int) -> None:
    track_ids = list(
        session.exec(select(Track.id).where(Track.curriculum_id == curriculum_id)).all()
    )
    if not track_ids:
        return
    topic_ids = list(session.exec(select(Topic.id).where(Topic.track_id.in_(track_ids))).all())
    if topic_ids:
        session.exec(
            delete(TopicPrerequisite).where(
                (TopicPrerequisite.topic_id.in_(topic_ids))
                | (TopicPrerequisite.prerequisite_topic_id.in_(topic_ids))
            )
        )
        session.exec(delete(LearnerTopicState).where(LearnerTopicState.topic_id.in_(topic_ids)))
        session.exec(delete(Topic).where(Topic.id.in_(topic_ids)))
    session.exec(delete(Track).where(Track.id.in_(track_ids)))


def update_draft(
    session: Session, curriculum: Curriculum, request: CurriculumDraftRequest
) -> Curriculum:
    if curriculum.status != "draft":
        raise CurriculumMutationError("Confirmed curricula cannot be structurally edited")
    _delete_structure(session, curriculum.id)
    curriculum.name = request.proposal.name
    curriculum.description = request.proposal.description
    session.add(curriculum)
    _write_structure(session, curriculum, request)
    session.commit()
    session.refresh(curriculum)
    return curriculum


def proposal_from_curriculum(session: Session, curriculum: Curriculum) -> CurriculumProposal:
    metadata = session.get(CurriculumGenerationMetadata, curriculum.id)
    flags = json.loads(metadata.topic_flags_json) if metadata else {}
    tracks = session.exec(
        select(Track)
        .where(Track.curriculum_id == curriculum.id)
        .order_by(Track.order_index)
    ).all()
    track_proposals: list[TrackProposal] = []
    for track in tracks:
        topics = session.exec(
            select(Topic).where(Topic.track_id == track.id).order_by(Topic.order_index)
        ).all()
        topic_proposals: list[TopicProposal] = []
        for topic in topics:
            links = session.exec(
                select(TopicPrerequisite).where(TopicPrerequisite.topic_id == topic.id)
            ).all()
            prerequisites = [
                prerequisite.slug
                for link in links
                if (prerequisite := session.get(Topic, link.prerequisite_topic_id)) is not None
            ]
            topic_proposals.append(
                TopicProposal(
                    key=topic.slug,
                    name=topic.name,
                    description=topic.description,
                    priority=topic.priority,
                    target_level=topic.target_level,
                    estimated_minutes=topic.estimated_minutes,
                    prerequisites=prerequisites,
                    added_as_prerequisite=bool(flags.get(topic.slug, False)),
                )
            )
        track_proposals.append(
            TrackProposal(
                key=track.slug,
                name=track.name,
                description=track.description,
                priority=track.priority,
                topics=topic_proposals,
            )
        )
    return CurriculumProposal(
        name=curriculum.name,
        description=curriculum.description,
        goal=metadata.goal if metadata else curriculum.description,
        tracks=track_proposals,
    )


def confirm_draft(session: Session, curriculum: Curriculum) -> Curriculum:
    if curriculum.status != "draft":
        raise CurriculumMutationError("Only a draft curriculum can be confirmed")
    proposal_from_curriculum(session, curriculum)
    curriculum.status = "confirmed"
    curriculum.confirmed_at = utc_now()
    session.add(curriculum)
    session.commit()
    session.refresh(curriculum)
    return curriculum

