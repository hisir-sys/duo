import sys
from types import SimpleNamespace

import pytest

import provider_registry as registry


@pytest.mark.parametrize(
    ("provider", "base_url"),
    [
        ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        ("mistral", "https://api.mistral.ai/v1"),
        ("groq", "https://api.groq.com/openai/v1"),
        ("openrouter", "https://openrouter.ai/api/v1"),
        ("cerebras", "https://api.cerebras.ai/v1"),
    ],
)
def test_openai_compatible_provider_uses_official_endpoint(provider, base_url, monkeypatch):
    captured = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    client = registry.create_client(provider, "test-key")
    assert isinstance(client, FakeOpenAI)
    assert captured["base_url"] == base_url
    assert captured["api_key"] == "test-key"
    assert captured["timeout"] == 120
    assert captured["max_retries"] == 2


def test_openrouter_sets_app_identification_header(monkeypatch):
    captured = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    registry.create_client("openrouter", "test-key")
    assert captured["default_headers"] == {"X-Title": "DuoAI Studio"}


def test_claude_uses_anthropic_sdk(monkeypatch):
    captured = {}

    class FakeAnthropic:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setitem(sys.modules, "anthropic", SimpleNamespace(Anthropic=FakeAnthropic))
    registry.create_client("claude", "test-key")
    assert captured["api_key"] == "test-key"
    assert captured["timeout"] == 120


def test_unknown_provider_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        registry.get_spec("unknown")


def test_empty_api_key_is_rejected():
    with pytest.raises(ValueError, match="API key"):
        registry.create_client("gemini", "  ")


def test_model_listing_uses_provider_defaults_on_non_strict_failure():
    class BrokenModels:
        def list(self):
            raise RuntimeError("offline")

    client = SimpleNamespace(models=BrokenModels())
    assert registry.list_models("gemini", client) == list(
        registry.get_spec("gemini").models
    )


def test_model_listing_can_raise_for_connection_test():
    class BrokenModels:
        def list(self):
            raise RuntimeError("unauthorized")

    client = SimpleNamespace(models=BrokenModels())
    with pytest.raises(RuntimeError, match="unauthorized"):
        registry.list_models("groq", client, fallback=False)


def test_model_listing_returns_provider_models():
    client = SimpleNamespace(
        models=SimpleNamespace(
            list=lambda: SimpleNamespace(data=[
                SimpleNamespace(id="model-z"),
                SimpleNamespace(id="model-a"),
            ])
        )
    )
    assert registry.list_models("mistral", client) == ["model-a", "model-z"]
