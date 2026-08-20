# AI Knowledge Backend

[![CI](https://github.com/guisefe/ai-knowledge-plataform/actions/workflows/ci.yml/badge.svg)](https://github.com/guisefe/ai-knowledge-plataform/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791)
![Status](https://img.shields.io/badge/status-active%20development-orange)

AI Knowledge Backend is a spec-driven backend platform for building AI-powered knowledge systems over long-form documents and structured data.

The project explores how Retrieval-Augmented Generation, safe Text-to-SQL, local-first LLM providers, async persistence, migrations, tests, and CI can be combined inside a pragmatic backend architecture.

It is not a chatbot demo. It is a backend engineering project focused on architecture, reproducibility, testability, and useful AI integration.

## Why this project exists

Most AI demos stop at a simple chat interface.

Real systems need more than that. They need authentication, persistence, migrations, deterministic tests, clear boundaries between domain logic and model providers, and a way to retrieve grounded context before asking a model to answer.

AI Knowledge Backend focuses on that backend layer.

The goal is to make documents and structured data queryable through natural language while keeping the system testable, extensible, and provider-agnostic.

## Core capabilities

The project is being designed to support:

- ingestion of long-form documents;
- text parsing and chunking;
- retrieval over indexed document chunks;
- grounded answers with source references;
- pluggable LLM providers;
- local-first model execution;
- safe Text-to-SQL patterns;
- async database access;
- database migrations;
- contract and unit tests.

## Demo corpus

The demo corpus uses classic public-domain literature instead of random synthetic documents.

The goal is to test retrieval and grounded answers over real long-form texts that are culturally recognizable, structurally rich, and meaningful enough to demonstrate reasoning.

Initial corpus:

| Work | Author | Purpose |
|---|---|---|
| The Grand Inquisitor | Fyodor Dostoyevsky | MVP document for questions about freedom, authority, conscience, and moral responsibility |
| Inferno | Dante Alighieri | Planned document for allegory, symbolic structure, moral order, and poetic narrative |
| The Republic | Plato | Planned document for justice, education, political order, and philosophical reasoning |

The first MVP document will be The Grand Inquisitor because it is short enough for an initial implementation, but rich enough to test retrieval over complex ideas.

## Development approach

This project follows a spec-driven development workflow:

    Problem -> Requirements -> Specs -> Tests -> Implementation

Before implementing a feature, the expected behavior is documented through requirements, technical specs, or architecture decision records.

This keeps the project from becoming a random AI prototype and allows it to evolve as a small but coherent backend platform.

## Current status

Implemented:

- product requirements;
- technical specs;
- architecture decision records;
- FastAPI application foundation;
- healthcheck endpoint;
- GitHub Actions CI;
- SQLAlchemy async database foundation;
- Alembic migrations;
- PostgreSQL and pgvector setup;
- initial User model;
- LLM provider abstraction with mock provider.

In progress:

- authentication flow;
- document ingestion;
- chunking service;
- embedding provider abstraction;
- RAG query endpoint.

Planned:

- PostgreSQL and pgvector retrieval;
- local embedding models;
- Ollama provider;
- PDF or long-form text parsing;
- safe Text-to-SQL;
- structured logs and observability.

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Language | Python 3.12 |
| Database | PostgreSQL |
| Vector search | pgvector |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Queue and cache | Redis and RQ |
| LLM provider | Mock first, Ollama planned |
| Testing | Pytest |
| Quality | Ruff and Mypy |
| Environment | Docker Compose and GitHub Codespaces |
| CI | GitHub Actions |

## Architecture principles

### Open-source first

The first version should run without paid APIs or proprietary model providers.

### Provider abstraction

LLM and embedding providers should be replaceable.

The domain should not depend directly on Ollama, OpenAI, Anthropic, Azure OpenAI, or any specific vendor.

### Pragmatic design

The project avoids abstractions that do not solve a real problem.

Abstractions are introduced only where the system is expected to change, such as LLM providers, embedding providers, vector stores, and document parsers.

### Testable by design

Core behavior should be testable without calling real LLMs.

Mock providers keep tests deterministic, fast, and reliable.

### API-first

The backend is designed to be integrated with different clients, including web applications, internal tools, automations, bots, BI platforms, and enterprise systems.

## Project structure

    app/
      api/
      core/
      domain/
        documents/
        embeddings/
        llm/
        rag/
        text_to_sql/
        users/
      infra/
      workers/

    docs/
      product/
      specs/
      adr/
      architecture/
      api/

    tests/
      unit/
      integration/
      contract/

## Running locally

Create an environment file:

    cp .env.example .env

Install dependencies:

    python -m pip install -e ".[dev]"

Run the API:

    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Healthcheck:

    curl http://localhost:8000/api/v1/health

Interactive API docs:

    http://localhost:8000/docs

## Quality checks

    python -m ruff check .
    python -m mypy app
    python -m pytest

## Roadmap

### Sprint 1 — Backend foundation

- [x] FastAPI foundation
- [x] async database session
- [x] Alembic setup
- [x] User model
- [ ] authentication flow

### Sprint 2 — Document ingestion

- [ ] document metadata model
- [ ] upload endpoint
- [ ] text parsing
- [ ] chunking service
- [ ] indexing workflow

### Sprint 3 — RAG MVP

- [x] LLM provider abstraction
- [ ] embedding provider abstraction
- [ ] vector retrieval
- [ ] prompt builder
- [ ] RAG query endpoint

### Sprint 4 — Text-to-SQL

- [ ] schema registry
- [ ] SQL generation prompt
- [ ] SQL validator
- [ ] safe query executor

## What this project demonstrates

This project demonstrates practical backend engineering for AI systems:

- designing AI features around explicit requirements;
- building provider-agnostic LLM architecture;
- using async persistence and database migrations;
- applying RAG without hiding the full pipeline behind a framework;
- preparing safe Text-to-SQL patterns;
- writing contract and unit tests;
- keeping the project reproducible and CI-validated.

## Positioning

This project sits at the intersection of backend engineering, data engineering, applied AI, and enterprise architecture.

The goal is to show how AI can be integrated into backend systems in a way that is practical, testable, extensible, and useful.
