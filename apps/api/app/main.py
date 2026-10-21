from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

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
from .services.active_curriculum import activate_curriculum
from .models import AppSetting, Curriculum


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        fresh = session.exec(select(Curriculum.id)).first() is None and session.get(AppSetting, "active_curriculum_id") is None
        seed_default_curriculum(session, settings.curriculum_path)
        new_default=seed_default_curriculum(session, settings.curriculum_v2_path)
        # Only a first install receives the default selection. Upgrades never copy scores,
        # recalculate evidence, or replace the learner's explicit curriculum choice.
        if fresh:
            activate_curriculum(session, new_default)
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

    assets_dir = settings.frontend_dist_path / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    def serve_root():
        index_file = settings.frontend_dist_path / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
        return {"app": settings.app_name, "message": "Frontend build not found. Run 'npm run build' in apps/web."}

    @app.get("/{full_path:path}", include_in_schema=False)
    def catch_all_spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        if full_path == "health":
            raise HTTPException(status_code=404, detail="Not found")

        file_path = settings.frontend_dist_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        index_file = settings.frontend_dist_path / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend build not found")

    return app


app = create_app()
