from pathlib import Path
from collections.abc import Mapping
import os

from dotenv import load_dotenv
from sqlalchemy.engine import make_url


API_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(API_DIR / ".env")


def _path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.absolute()
    result = (base / path).resolve()
    if not result.is_relative_to(REPO_ROOT):
        raise ValueError(f"Relative Forge path escapes the repository: {value}")
    return result


class Settings:
    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        env = os.environ if environ is None else environ
        self.app_name = "Forge API"
        self.database_url = env.get(
            "FORGE_DATABASE_URL",
            f"sqlite:///{(API_DIR / 'data' / 'forge.db').as_posix()}",
        )
        url = make_url(self.database_url)
        if url.drivername.startswith("sqlite") and url.database not in (None, "", ":memory:"):
            # Retain the documented sqlite:///data/forge.db API-relative convention.
            self.database_url = url.set(database=_path(url.database, API_DIR).as_posix()).render_as_string(hide_password=False)
        # All other relative file settings are repository-relative, independent of cwd.
        paths = {
            "curriculum_path": ("FORGE_CURRICULUM_PATH", "data/default-ai-engineer-curriculum.json"),
            "curriculum_v2_path": ("FORGE_CURRICULUM_V2_PATH", "data/default-interview-curriculum-v2.json"),
            "curriculum_migration_path": ("FORGE_CURRICULUM_MIGRATION_PATH", "data/curriculum-migrations/v1-to-v2.json"),
            "projects_path": ("FORGE_PROJECTS_PATH", "data/default-projects.json"),
            "course_content_path": ("FORGE_COURSE_CONTENT_PATH", "content/ai-engineer/v1"),
            "course_sources_path": ("FORGE_COURSE_SOURCES_PATH", "data/course-sources.json"),
            "frontend_dist_path": ("FORGE_FRONTEND_DIST_PATH", "apps/web/dist"),
            "content_bindings_path": ("FORGE_CONTENT_BINDINGS_PATH", "data/content-bindings/legacy-curricula.json"),
            "content_snapshot_path": ("FORGE_CONTENT_SNAPSHOT_PATH", "apps/api/data/content-snapshots"),
            "database_backup_path": ("FORGE_DATABASE_BACKUP_PATH", "apps/api/data/db-backups"),
            "problem_bank_path": ("FORGE_PROBLEM_BANK_PATH", "content/problem-bank"),
        }
        for attribute, (variable, default) in paths.items():
            setattr(self, attribute, _path(env.get(variable, default), REPO_ROOT))
        self.cors_origins = [
            origin.strip()
            for origin in env.get(
                "FORGE_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        ]
        self.gemini_api_key = env.get("GEMINI_API_KEY", "").strip()
        self.gemini_model = env.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
        self.gemini_tutor_thinking = env.get("GEMINI_TUTOR_THINKING", "low").strip()
        self.gemini_doubt_thinking = env.get("GEMINI_DOUBT_THINKING", "low").strip()
        self.gemini_curriculum_thinking = env.get(
            "GEMINI_CURRICULUM_THINKING", "medium"
        ).strip()
        self.gemini_exercise_thinking = env.get("GEMINI_EXERCISE_THINKING", "low").strip()
        self.gemini_answer_evaluation_thinking = env.get(
            "GEMINI_ANSWER_EVALUATION_THINKING", "low"
        ).strip()
        self.gemini_interview_thinking = env.get("GEMINI_INTERVIEW_THINKING", "low").strip()
        self.gemini_interview_evaluation_thinking = env.get(
            "GEMINI_INTERVIEW_EVALUATION_THINKING", "medium"
        ).strip()
        self.gemini_input_price_per_million = float(
            env.get("GEMINI_INPUT_PRICE_PER_MILLION", "0.75")
        )
        self.gemini_output_price_per_million = float(
            env.get("GEMINI_OUTPUT_PRICE_PER_MILLION", "3.75")
        )
        self.gemini_cached_input_price_per_million = float(
            env.get("GEMINI_CACHED_INPUT_PRICE_PER_MILLION", "0.075")
        )


settings = Settings()
