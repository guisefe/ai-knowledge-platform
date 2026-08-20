# ADR-005: RAG Without LangChain in Core

## Status

Accepted

## Context

LangChain and similar frameworks are useful, but using them too early can hide the actual RAG flow and increase framework coupling.

The project should demonstrate understanding of the full pipeline.

## Decision

The first version will implement the RAG flow directly:

parser -> chunker -> embedding provider -> vector store -> retriever -> prompt builder -> LLM provider

LangChain or LlamaIndex may be added later as optional adapters.

## Consequences

Positive:

- clearer architecture;
- stronger technical demonstration;
- lower dependency coupling;
- easier testing of each component.

Negative:

- more code to maintain;
- fewer built-in integrations in the first version.
