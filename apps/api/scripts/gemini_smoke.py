"""Optional one-call Gemini smoke test. Run manually; never used by pytest."""

from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from app.config import settings  # noqa: E402
from app.providers import GeminiProvider  # noqa: E402


def main() -> int:
    if not settings.gemini_api_key:
        print("GEMINI_API_KEY is not configured in apps/api/.env")
        return 1
    provider = GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    result = provider.generate_text(
        system_instruction="Reply briefly and plainly.",
        prompt="In one sentence, say that the Forge Gemini connection works.",
        thinking_level="low",
    )
    print("success: true")
    print(f"model: {result.model}")
    print(f"reply: {result.text}")
    print(
        "tokens: "
        f"input={result.usage.input_tokens}, output={result.usage.output_tokens}, "
        f"thinking={result.usage.thought_tokens}, cached={result.usage.cached_tokens}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
