# ADR-001: Local-First Runtime

## Status

Accepted

## Context

The RAG pipeline must be reproducible in development and evaluation without requiring paid APIs. Provider availability, rate limits, and changing hosted models would make deterministic tests and baseline comparisons harder.

Local execution also has constraints: model quality and latency depend on the available hardware, and a Codespace may not have enough resources for useful generation.

## Decision

The first evaluated vertical slice will support a local or deterministic runtime:

- deterministic mock providers for unit and contract tests;
- PostgreSQL with pgvector for persistence and retrieval;
- a local embedding implementation for the first evaluation baseline;
- an Ollama-compatible generation adapter only when generation is required;
- Docker Compose for reproducible backing services.

Redis and a background queue will be introduced only when asynchronous ingestion behavior requires them.

## Consequences

Positive:

- tests do not depend on network access or paid APIs;
- evaluation configuration can be versioned;
- the core pipeline remains usable in a clean development environment;
- provider failures do not block domain and API contract testing.

Negative:

- local model results may not match premium hosted models;
- performance varies with hardware;
- adding a hosted provider later requires a separate adapter and evaluation baseline.

## Revisit when

Revisit this decision when a use case requires quality or throughput that cannot be met locally, or when a hosted provider can be justified by measured cost, latency, and quality.
