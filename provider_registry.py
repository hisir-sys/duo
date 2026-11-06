"""Provider connection registry for DuoAI Studio.

All providers use official APIs. Gemini, Mistral, Groq, OpenRouter and
Cerebras expose OpenAI-compatible endpoints; Claude uses the Anthropic SDK.
"""
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ProviderSpec:
    key_name: str
    env_name: str
    default_model: str
    models: tuple[str, ...]
    base_url: str | None = None
    kind: str = "openai"
    headers: tuple[tuple[str, str], ...] = ()


PROVIDERS: Mapping[str, ProviderSpec] = {
    "claude": ProviderSpec(
        "claude", "ANTHROPIC_API_KEY", "claude-sonnet-5-5",
        ("claude-sonnet-5-5", "claude-opus-5-5", "claude-haiku-5-5"),
        kind="anthropic",
    ),
    "chatgpt": ProviderSpec(
        "openai", "OPENAI_API_KEY", "gpt-4o",
        ("gpt-4o", "gpt-4o-mini", "o3"),
    ),
    "gemini": ProviderSpec(
        "gemini", "GEMINI_API_KEY", "gemini-2.5-flash",
        ("gemini-2.5-flash", "gemini-2.5-pro"),
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
    "mistral": ProviderSpec(
        "mistral", "MISTRAL_API_KEY", "mistral-small-latest",
        ("mistral-small-latest", "mistral-large-latest", "codestral-latest"),
        "https://api.mistral.ai/v1",
    ),
    "groq": ProviderSpec(
        "groq", "GROQ_API_KEY", "llama-3.3-70b-versatile",
        ("llama-3.3-70b-versatile", "openai/gpt-oss-120b"),
        "https://api.groq.com/openai/v1",
    ),
    "openrouter": ProviderSpec(
        "openrouter", "OPENROUTER_API_KEY", "openrouter/free",
        ("openrouter/free",),
        "https://openrouter.ai/api/v1",
        headers=(("X-Title", "DuoAI Studio"),),
    ),
    "cerebras": ProviderSpec(
        "cerebras", "CEREBRAS_API_KEY", "llama3.1-8b",
        ("llama3.1-8b", "llama-3.3-70b"),
        "https://api.cerebras.ai/v1",
    ),
}


def get_spec(provider: str) -> ProviderSpec:
    try:
        return PROVIDERS[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported AI provider: {provider}") from exc


def create_client(provider: str, api_key: str, *, timeout: int = 120, max_retries: int = 2):
    """Create an SDK client without making a network request."""
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("A non-empty API key is required.")
    spec = get_spec(provider)
    if spec.kind == "anthropic":
        import anthropic
        return anthropic.Anthropic(
            api_key=api_key.strip(), timeout=timeout, max_retries=max_retries
        )

    from openai import OpenAI
    options = {
        "api_key": api_key.strip(),
        "timeout": timeout,
        "max_retries": max_retries,
    }
    if spec.base_url:
        options["base_url"] = spec.base_url
    if spec.headers:
        options["default_headers"] = dict(spec.headers)
    return OpenAI(**options)


def list_models(provider: str, client, *, fallback: bool = True) -> list[str]:
    """List models from the provider; use known defaults only when allowed."""
    spec = get_spec(provider)
    try:
        response = client.models.list()
        models = [item.id for item in response.data if getattr(item, "id", None)]
        if provider == "chatgpt":
            models = [
                model for model in models
                if model.startswith(("gpt", "o"))
                and "audio" not in model and "realtime" not in model
            ]
        if models:
            return sorted(set(models))
    except Exception:
        if not fallback:
            raise
    if fallback:
        return list(spec.models)
    return []
