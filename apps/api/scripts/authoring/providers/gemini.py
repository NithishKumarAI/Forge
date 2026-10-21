import time
from typing import Any

import httpx
from pydantic import ValidationError

from .base import (
    InvalidStructuredResponse,
    LLMProvider,
    LLMResult,
    LLMUsage,
    ProviderError,
    StructuredModel,
)


def _integer(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _usage_from_interaction(interaction: Any) -> LLMUsage:
    usage = getattr(interaction, "usage", None)
    if usage is None:
        return LLMUsage()
    return LLMUsage(
        input_tokens=_integer(
            getattr(usage, "total_input_tokens", None)
            or getattr(usage, "input_tokens", None)
            or getattr(usage, "prompt_token_count", None)
        ),
        output_tokens=_integer(
            getattr(usage, "total_output_tokens", None)
            or getattr(usage, "output_tokens", None)
            or getattr(usage, "candidates_token_count", None)
        ),
        thought_tokens=_integer(
            getattr(usage, "total_thought_tokens", None)
            or getattr(usage, "thought_tokens", None)
            or getattr(usage, "thoughts_token_count", None)
        ),
        cached_tokens=_integer(
            getattr(usage, "total_cached_tokens", None)
            or getattr(usage, "cached_tokens", None)
            or getattr(usage, "cached_content_token_count", None)
        ),
    )


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required")
        from google import genai

        self.model = model
        self._client = genai.Client(api_key=api_key)

    def _create(self, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                return self._client.interactions.create(timeout=60, **kwargs)
            except Exception as exc:  # SDK transports use several exception types.
                last_error = exc
                status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
                if status == 400:
                    raise ProviderError("Gemini request was invalid. Check the configured model and request settings. [provider_category=invalid_request status=400]") from exc
                if status == 401:
                    raise ProviderError("Gemini authentication failed. Check the API key. [provider_category=authentication status=401]") from exc
                if status == 403:
                    raise ProviderError("Gemini access is restricted for this project. Check permissions or billing. [provider_category=permission status=403]") from exc
                if status == 404:
                    raise ProviderError("The configured Gemini model or endpoint is unavailable. [provider_category=not_found status=404]") from exc
                if status == 429:
                    raise ProviderError(
                        "Gemini API rate limit reached (or quota exhausted). Cached learning material remains available. Try again shortly. [provider_category=rate_limit status=429]"
                    ) from exc
                transient = isinstance(exc, (TimeoutError, httpx.TransportError)) or (
                    isinstance(status, int) and status >= 500
                )
                if not transient or attempt == 1:
                    break
                time.sleep(0.35)
        raise ProviderError("Gemini is temporarily unavailable. Try again.") from last_error

    def generate_text(
        self, *, system_instruction: str, prompt: str, thinking_level: str
    ) -> LLMResult:
        interaction = self._create(
            model=self.model,
            system_instruction=system_instruction,
            input=prompt,
            generation_config={"thinking_level": thinking_level},
        )
        text = (getattr(interaction, "output_text", None) or "").strip()
        if not text:
            raise ProviderError("Gemini returned an empty response. Please retry.")
        return LLMResult(text=text, model=self.model, usage=_usage_from_interaction(interaction))

    def generate_structured(
        self,
        *,
        system_instruction: str,
        prompt: str,
        thinking_level: str,
        response_model: type[StructuredModel],
    ) -> tuple[StructuredModel, LLMResult]:
        interaction = self._create(
            model=self.model,
            system_instruction=system_instruction,
            input=prompt,
            generation_config={"thinking_level": thinking_level},
            response_format=[
                {
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": response_model.model_json_schema(),
                }
            ],
        )
        text = (getattr(interaction, "output_text", None) or "").strip()
        try:
            parsed = response_model.model_validate_json(text)
        except (ValidationError, ValueError) as exc:
            raise InvalidStructuredResponse(str(exc)) from exc
        return parsed, LLMResult(
            text=text, model=self.model, usage=_usage_from_interaction(interaction)
        )
