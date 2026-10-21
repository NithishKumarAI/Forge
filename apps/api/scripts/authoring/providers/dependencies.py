import os
from functools import lru_cache
from .gemini import GeminiProvider
@lru_cache
def get_llm_provider():
    key=os.environ.get("GEMINI_API_KEY","").strip()
    return GeminiProvider(key,os.environ.get("GEMINI_MODEL","gemini-3.8-flash")) if key else None
