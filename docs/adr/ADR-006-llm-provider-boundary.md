# ADR-006: LLM Provider Boundary

## Status

Accepted

## Context

The document-to-answer flow will eventually require text generation. Tests must remain deterministic and the domain must not depend on a vendor SDK.

An abstraction is justified at this external boundary, but listing integrations before they exist would overstate the implemented scope.

## Decision

Generation calls go through the narrow `LLMProvider` interface.

The current implementation contains only:

- `MockLLMProvider`, used for deterministic tests and contract development.

The first real adapter will be selected when the evaluated RAG flow needs generation. An Ollama-compatible adapter is the local-first candidate, but is not an implemented capability of this ADR.

Additional providers require a measured product need and their own evaluation baseline.

## Consequences

Positive:

- avoids vendor lock-in;
- improves testability;
- leaves room for provider switching by configuration;
- keeps business logic independent from infrastructure.

Negative:

- requires additional abstraction code;
- provider-specific features may need careful modeling.

## Revisit when

Revisit the request and response contract when the first non-mock provider is implemented. Do not generalize the interface for provider-specific features before that concrete need exists.
