# Success Metrics

## Purpose

The project is evaluated as an AI-backed software system, not only as an API that can call a model. Results are reported with the dataset version and complete retrieval configuration so changes can be compared.

The targets below are acceptance gates, not current claims.

## RAG MVP targets

The initial dataset will contain at least 30 human-written questions covering supported, ambiguous, conflicting, and unsupported cases.

| Dimension | Metric | MVP target |
|---|---|---:|
| Retrieval | Recall@5 | >= 0.80 |
| Citations | Citation precision | >= 0.90 |
| Grounding | Supported claims | >= 0.90 |
| Abstention | Unsupported questions correctly refused | 1.00 |
| Isolation | Cross-owner retrieval incidents | 0 |
| Performance | Retrieval p95 on the demo corpus | < 250 ms |

Each report must record:

- dataset version;
- embedding model;
- chunking configuration;
- retrieval parameters;
- corpus size;
- hardware or execution environment;
- execution date.

## Backend quality gates

- a clean environment can install the project from `pyproject.toml`;
- migrations can upgrade an empty database to the latest revision;
- unit and contract tests do not require a real LLM;
- integration tests run against PostgreSQL with pgvector;
- duplicate ingestion is idempotent;
- failed processing preserves an actionable error reason;
- structured logs correlate ingestion, retrieval, and generation operations.

## Regression policy

A change to parsing, chunking, embeddings, ranking, prompting, or model configuration must run the evaluation suite.

A regression may be accepted only when the pull request records the measured impact, the benefit obtained, and why the trade-off is acceptable.
