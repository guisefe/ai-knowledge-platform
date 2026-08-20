import pytest

from app.domain.llm.factory import UnsupportedLLMProviderError, get_llm_provider
from app.domain.llm.mock import MockLLMProvider
from app.domain.llm.schemas import LLMRequest


def test_factory_returns_mock_provider() -> None:
    provider = get_llm_provider("mock")

    assert isinstance(provider, MockLLMProvider)


def test_factory_rejects_unsupported_provider() -> None:
    with pytest.raises(UnsupportedLLMProviderError):
        get_llm_provider("unknown")


@pytest.mark.asyncio
async def test_mock_provider_returns_deterministic_response() -> None:
    provider = MockLLMProvider()

    response = await provider.generate(
        LLMRequest(
            prompt="Explain RAG in one sentence.",
            model="mock-model",
            temperature=0.2,
        )
    )

    assert response.provider == "mock"
    assert response.model == "mock-model"
    assert response.text == "Mock response for prompt: Explain RAG in one sentence."
    assert response.latency_ms >= 0
    assert response.metadata["mock"] is True
