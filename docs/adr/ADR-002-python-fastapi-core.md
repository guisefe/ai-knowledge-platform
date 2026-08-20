# ADR-002: Python and FastAPI as Core Backend

## Status

Accepted

## Context

The project combines backend engineering, document processing, embeddings, RAG, Text-to-SQL, and AI provider integrations.

Python has a strong ecosystem for AI, data processing, and API development.

## Decision

The core backend will be built with Python and FastAPI.

## Consequences

Positive:

- strong AI and data ecosystem;
- productive API development;
- OpenAPI documentation by default;
- good integration with Pydantic, SQLAlchemy, and Pytest;
- strong positioning for AI Engineer and Data/AI Engineer roles.

Negative:

- not as enterprise-native as .NET in Microsoft-heavy environments;
- future .NET/Semantic Kernel integration may require an adapter or companion service.
