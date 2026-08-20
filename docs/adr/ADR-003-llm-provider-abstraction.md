# ADR-003: LLM Provider Abstraction

## Status

Accepted

## Context

The application should start with local/open-source models, but later support providers such as OpenAI, Azure OpenAI, Anthropic, Gemini, and enterprise adapters.

Directly coupling services to one provider would make the system harder to test and evolve.

## Decision

All LLM calls must go through an abstract provider interface.

Initial providers:

- MockLLMProvider;
- OllamaLLMProvider.

Future providers:

- OpenAIProvider;
- AzureOpenAIProvider;
- AnthropicProvider;
- GeminiProvider;
- SemanticKernelAdapter.

## Consequences

Positive:

- avoids vendor lock-in;
- improves testability;
- allows future provider switching by configuration;
- keeps business logic independent from infrastructure.

Negative:

- requires additional abstraction code;
- provider-specific features may need careful modeling.
