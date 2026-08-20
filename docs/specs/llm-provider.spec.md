# LLM Provider Spec

## Objective

Allow the application to generate text without depending directly on a specific LLM vendor.

## Interface

class LLMProvider:
    async def generate(self, request: LLMRequest) -> LLMResponse:
        ...

## Providers

### V1

- mock
- ollama

### Future

- openai
- azure_openai
- anthropic
- gemini
- semantic_kernel_adapter

## Rules

- tests must use mock provider;
- local development must use Ollama provider by default;
- provider must be selected by environment configuration;
- provider errors must be handled and logged;
- services must depend on the interface, not on concrete providers.

## Contract Tests

- mock provider returns deterministic response;
- provider factory returns provider configured in environment;
- unsupported provider raises clear configuration error.
