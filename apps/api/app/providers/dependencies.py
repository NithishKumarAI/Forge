from functools import lru_cache

from ..config import settings
from .base import LLMProvider
from .gemini import GeminiProvider


@lru_cache
def get_llm_provider() -> LLMProvider | None:
    if not settings.gemini_api_key:
        return None
    return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
