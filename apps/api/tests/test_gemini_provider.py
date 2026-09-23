from types import SimpleNamespace

from app.providers.gemini import _usage_from_interaction


def test_interactions_usage_fields_are_mapped() -> None:
    interaction = SimpleNamespace(
        usage=SimpleNamespace(
            total_input_tokens=120,
            total_output_tokens=50,
            total_thought_tokens=15,
            total_cached_tokens=8,
        )
    )
    usage = _usage_from_interaction(interaction)
    assert usage.input_tokens == 120
    assert usage.output_tokens == 50
    assert usage.thought_tokens == 15
    assert usage.cached_tokens == 8
