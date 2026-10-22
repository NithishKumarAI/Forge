import os
from types import SimpleNamespace
settings=SimpleNamespace(gemini_api_key=os.environ.get("GEMINI_API_KEY",""),gemini_model=os.environ.get("GEMINI_MODEL","gemini-3.8-flash"))
