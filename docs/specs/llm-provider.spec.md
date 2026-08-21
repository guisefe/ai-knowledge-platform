# LLM Provider Spec

## Objective

Allow the application to generate text without depending directly on a specific LLM vendor.

## Interface

class LLMProvider:
    async def generate(self, request: LLMRequest) -> LLMResponse:
        ...

## Current baseline

The repository currently implements:

- `mock`, for deterministic unit and contract tests.

No runtime generation provider is part of the implemented application yet.

## First evaluated adapter

An Ollama-compatible adapter may be introduced when the document-to-answer flow requires generation. It must be evaluated as part of the same versioned RAG configuration as retrieval and prompting.

## Deferred adapters

- openai
- azure_openai
- anthropic
- gemini
- semantic_kernel_adapter

## Rules

- tests must use mock provider;
- the application defaults to the mock provider until a generation adapter is implemented;
- provider must be selected by environment configuration;
- provider errors must be handled and logged;
- services must depend on the interface, not on concrete providers.

## Contract Tests

- mock provider returns deterministic response;
- provider factory returns provider configured in environment;
- unsupported provider raises clear configuration error.
