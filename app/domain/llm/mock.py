from time import perf_counter

from app.domain.llm.base import LLMProvider
from app.domain.llm.schemas import LLMRequest, LLMResponse


class MockLLMProvider(LLMProvider):
    provider_name = "mock"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start = perf_counter()

        text = f"Mock response for prompt: {request.prompt}"

        latency_ms = int((perf_counter() - start) * 1000)

        return LLMResponse(
            text=text,
            model=request.model,
            provider=self.provider_name,
            latency_ms=latency_ms,
            metadata={"mock": True},
        )
