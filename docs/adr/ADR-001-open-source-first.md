# ADR-001: Open Source First

## Status

Accepted

## Context

The project should be useful for portfolio, learning, experimentation, and local development without requiring paid APIs.

Using proprietary LLMs from the beginning would increase cost, reduce reproducibility, and create vendor lock-in.

## Decision

The first version will run using open-source and local-first technologies.

The initial stack includes:

- FastAPI;
- PostgreSQL;
- pgvector;
- Redis;
- RQ;
- Ollama-compatible LLM provider;
- local embedding models;
- Docker Compose;
- GitHub Codespaces.

## Consequences

Positive:

- no paid API required;
- easier local development;
- lower cost;
- better reproducibility;
- stronger vendor-neutral architecture.

Negative:

- local models may produce lower quality responses than premium APIs;
- Codespaces resources may limit model execution;
- future cloud providers will require adapters.
