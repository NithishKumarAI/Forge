from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from pydantic import BaseModel


StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    thought_tokens: int = 0
    cached_tokens: int = 0


@dataclass
class LLMResult:
    text: str
    model: str
    usage: LLMUsage = field(default_factory=LLMUsage)


class ProviderError(RuntimeError):
    """Safe application-level provider error."""


class ProviderNotConfigured(ProviderError):
    pass


class InvalidStructuredResponse(ProviderError):
    pass


class LLMProvider(ABC):
    provider_name: str
    model: str

    @abstractmethod
    def generate_text(
        self, *, system_instruction: str, prompt: str, thinking_level: str
    ) -> LLMResult:
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        *,
        system_instruction: str,
        prompt: str,
        thinking_level: str,
        response_model: type[StructuredModel],
    ) -> tuple[StructuredModel, LLMResult]:
        raise NotImplementedError
