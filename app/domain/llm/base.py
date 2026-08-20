from abc import ABC, abstractmethod

from app.domain.llm.schemas import LLMRequest, LLMResponse


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError
