from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from . import models  # noqa: F401 -- registers SQLModel tables
from .config import settings
from .database import create_db_and_tables, engine
from .routers import router
from .routers.ai import router as ai_router
from .routers.curricula import router as curricula_router
from .routers.doubt import router as doubt_router
from .routers.tutor import router as tutor_router
from .routers.practice import router as practice_router
from .routers.adaptive import router as adaptive_router
from .routers.interviews import router as interviews_router
from .routers.course import router as course_router
from .routers.arena import router as arena_router
from .services.course import sync_course_pack
from .services.arena import sync_problem_bank
from .schemas.api import HealthRead
from .services.curriculum import seed_default_curriculum
from .services.curriculum_migration import migrate_default_v2
from .services.mastery import backfill_existing_attempts


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        old_default=seed_default_curriculum(session, settings.curriculum_path)
        new_default=seed_default_curriculum(session, settings.curriculum_v2_path)
        migrate_default_v2(session,old_default,new_default,settings.curriculum_migration_path)
        backfill_existing_attempts(session)
        sync_course_pack(session)
        sync_problem_bank(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Specific curriculum routes must precede the legacy /{curriculum_id} route.
    app.include_router(curricula_router)
    app.include_router(ai_router)
    app.include_router(tutor_router)
    app.include_router(doubt_router)
    app.include_router(practice_router)
    app.include_router(adaptive_router)
    app.include_router(interviews_router)
    app.include_router(course_router)
    app.include_router(arena_router)
    app.include_router(router)

    @app.get("/health", response_model=HealthRead)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
