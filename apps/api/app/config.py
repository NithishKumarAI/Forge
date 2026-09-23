from pathlib import Path
import os

from dotenv import load_dotenv


API_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(API_DIR / ".env")


class Settings:
    def __init__(self) -> None:
        self.app_name = "Forge API"
        self.database_url = os.getenv(
            "FORGE_DATABASE_URL",
            f"sqlite:///{(API_DIR / 'data' / 'forge.db').as_posix()}",
        )
        self.curriculum_path = Path(
            os.getenv(
                "FORGE_CURRICULUM_PATH",
                str(REPO_ROOT / "data" / "default-ai-engineer-curriculum.json"),
            )
        )
        self.projects_path = Path(
            os.getenv("FORGE_PROJECTS_PATH", str(REPO_ROOT / "data" / "default-projects.json"))
        )
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv(
                "FORGE_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        ]
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
        self.gemini_tutor_thinking = os.getenv("GEMINI_TUTOR_THINKING", "low").strip()
        self.gemini_doubt_thinking = os.getenv("GEMINI_DOUBT_THINKING", "low").strip()
        self.gemini_curriculum_thinking = os.getenv(
            "GEMINI_CURRICULUM_THINKING", "medium"
        ).strip()
        self.gemini_exercise_thinking = os.getenv("GEMINI_EXERCISE_THINKING", "low").strip()
        self.gemini_answer_evaluation_thinking = os.getenv(
            "GEMINI_ANSWER_EVALUATION_THINKING", "low"
        ).strip()
        self.gemini_interview_thinking = os.getenv("GEMINI_INTERVIEW_THINKING", "low").strip()
        self.gemini_interview_evaluation_thinking = os.getenv(
            "GEMINI_INTERVIEW_EVALUATION_THINKING", "medium"
        ).strip()
        self.gemini_input_price_per_million = float(
            os.getenv("GEMINI_INPUT_PRICE_PER_MILLION", "0.75")
        )
        self.gemini_output_price_per_million = float(
            os.getenv("GEMINI_OUTPUT_PRICE_PER_MILLION", "3.75")
        )
        self.gemini_cached_input_price_per_million = float(
            os.getenv("GEMINI_CACHED_INPUT_PRICE_PER_MILLION", "0.075")
        )


settings = Settings()
