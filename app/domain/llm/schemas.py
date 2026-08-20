from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)


class LLMResponse(BaseModel):
    text: str
    model: str
    provider: str
    latency_ms: int = Field(ge=0)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
