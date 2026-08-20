from app.core.config import settings
from app.domain.llm.base import LLMProvider
from app.domain.llm.mock import MockLLMProvider


class UnsupportedLLMProviderError(ValueError):
    pass


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    selected_provider = provider_name or settings.LLM_PROVIDER

    if selected_provider == "mock":
        return MockLLMProvider()

    raise UnsupportedLLMProviderError(f"Unsupported LLM provider: {selected_provider}")
