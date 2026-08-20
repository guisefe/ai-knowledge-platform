# RAG Spec

## Objective

Answer questions using indexed documents as grounded context.

## Endpoint

POST /api/v1/rag/query

## Rules

- empty questions return 422;
- top_k must have a maximum limit;
- answer must include sources;
- if context is insufficient, the system must say it does not have enough information;
- the system must not invent sources;
- LLM calls must go through the LLM provider abstraction.

## Contract Tests

- valid query returns answer and sources;
- empty query returns 422;
- top_k above maximum returns 422;
- no context returns a grounded fallback answer.
