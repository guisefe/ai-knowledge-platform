# ADR-004: PostgreSQL and pgvector as Initial Vector Store

## Status

Accepted

## Context

The platform needs to store relational data and document embeddings.

Using a dedicated vector database from the beginning would add operational complexity.

## Decision

The first version will use PostgreSQL with pgvector for both relational data and vector search.

## Consequences

Positive:

- simpler infrastructure;
- one database for metadata and vectors;
- easier Docker Compose setup;
- strong fit for portfolio and MVP development.

Negative:

- specialized vector databases may scale better for large datasets;
- future Qdrant or Weaviate support may require a VectorStore abstraction.
