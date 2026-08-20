# AI Knowledge Backend

Open-source, spec-driven backend platform for corporate knowledge retrieval, RAG, and Text-to-SQL.

## Problem

Companies usually have valuable knowledge spread across documents, reports, spreadsheets, databases, policies, and internal tools. This makes information hard to find, hard to audit, and highly dependent on technical teams or key employees.

## Solution

AI Knowledge Backend provides an API-first platform that allows users to query documents and structured data using natural language.

The project starts with an open-source-first architecture using local models, PostgreSQL, pgvector, Redis, and FastAPI, while keeping the LLM layer pluggable for future providers such as OpenAI, Azure OpenAI, Anthropic, Gemini, and enterprise .NET/Semantic Kernel integrations.

## Core Capabilities

- Document ingestion
- Text extraction and chunking
- Local embeddings
- Vector search with PostgreSQL + pgvector
- RAG with source references
- Safe Text-to-SQL
- JWT authentication
- Docker-based development
- Contract-first API design
- LLM provider abstraction

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- pgvector
- Redis
- RQ
- Ollama-compatible provider architecture
- SQLAlchemy
- Alembic
- Pytest
- Ruff
- Mypy
- Docker Compose
- GitHub Codespaces

## Development Approach

This project follows a spec-driven development workflow:

```text
Problem → Requirements → Specs → API Contracts → Tests → Implementation

---

# 2. Criar Product Specs

```bash
cat > docs/product/problem-statement.md <<'EOF'
# Problem Statement

## Context

Organizations usually have valuable knowledge spread across documents, reports, spreadsheets, databases, policies, tickets, internal tools, and undocumented operational routines.

This knowledge is often hard to access because it depends on manual search, technical teams, or key employees who know where information is located.

## Problem

The information exists, but it is not easily accessible, searchable, auditable, or reusable.

This creates several issues:

- employees waste time searching for information;
- answers are inconsistent across teams;
- business users depend on technical teams for SQL queries;
- onboarding is slower;
- documentation becomes underused;
- operational knowledge is lost or concentrated in a few people;
- AI adoption becomes risky without governance and traceability.

## Proposed Solution

Build an open-source-first backend platform that allows users to query documents and structured data using natural language.

The system should combine:

- document ingestion;
- semantic search;
- RAG;
- safe Text-to-SQL;
- local LLM providers;
- provider abstraction;
- audit logs;
- API-first architecture.

## Expected Outcome

The platform should allow companies to transform internal knowledge into a secure, queryable, and extensible AI backend capability.
