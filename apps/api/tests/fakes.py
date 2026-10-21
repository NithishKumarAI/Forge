from app.schemas.ai import CurriculumProposal, TopicProposal, TrackProposal

def valid_proposal(name: str = "Backend Starter") -> CurriculumProposal:
    return CurriculumProposal(
        name=name,
        description="A compact backend interview curriculum.",
        goal="Build practical backend interview fluency.",
        tracks=[
            TrackProposal(
                key="foundations",
                name="Foundations",
                description="Core prerequisites.",
                priority=100,
                topics=[
                    TopicProposal(
                        key="python-functions",
                        name="Python functions",
                        description="Use and explain Python functions.",
                        priority=100,
                        target_level="working",
                        estimated_minutes=40,
                        prerequisites=[],
                        added_as_prerequisite=True,
                    ),
                    TopicProposal(
                        key="fastapi",
                        name="FastAPI",
                        description="Build typed HTTP APIs.",
                        priority=95,
                        target_level="interview_ready",
                        estimated_minutes=60,
                        prerequisites=["python-functions"],
                        added_as_prerequisite=False,
                    ),
                ],
            )
        ],
    )
