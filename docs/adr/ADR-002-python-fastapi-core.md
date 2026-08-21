# ADR-002: Python and FastAPI as the Core Backend

## Status

Accepted

## Context

The service combines asynchronous HTTP APIs, document processing, vector retrieval, evaluation tooling, and model-provider integrations.

The implementation needs native OpenAPI contracts, strong input validation, asynchronous I/O, and direct access to the Python data and machine-learning ecosystem.

## Decision

The core backend will use Python 3.12 and FastAPI.

Pydantic defines boundary contracts, SQLAlchemy manages asynchronous persistence, and domain services remain independent from FastAPI request objects.

## Consequences

Positive:

- native OpenAPI generation and request validation;
- direct integration with document, embedding, and evaluation libraries;
- asynchronous support for database and provider I/O;
- deterministic API testing with Pytest;
- one language across the backend and evaluation pipeline.

Negative:

- CPU-bound parsing or embedding work must not block API workers;
- Python type guarantees rely on static tooling and disciplined boundaries;
- Microsoft-specific integrations may require adapters or a companion service.

## Revisit when

Revisit this decision if measured CPU workloads require a different runtime, or if a mandatory platform integration cannot be supported cleanly through an adapter.
