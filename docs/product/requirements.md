# Product Requirements

## Functional requirements

### FR-001: Idempotent document ingestion

The system must accept an authorized UTF-8 text or Markdown document and calculate its SHA-256 checksum before processing.

Acceptance criteria:

- unsupported media types are rejected;
- the original file metadata and checksum are stored;
- uploading identical content to the same logical document does not create a duplicate version;
- the same public content may exist in different ownership scopes;
- processing status and failure reason are visible.

### FR-002: Document versioning

The system must preserve document history when content changes.

Acceptance criteria:

- versions are numbered within a logical document;
- checksum and storage location belong to a specific version;
- one version is explicitly active;
- previous versions remain available for audit;
- deleted or inactive versions are excluded from current retrieval.

### FR-003: Deterministic processing

The system must extract text, create chunks, generate embeddings, and store them with source provenance.

Acceptance criteria:

- repeating the same processing configuration produces the same chunk boundaries;
- each chunk references its document version and source location;
- successful processing changes the version status to `indexed`;
- failures change the status to `failed` and preserve an actionable reason;
- retries do not duplicate chunks.

### FR-004: Scoped retrieval

The system must retrieve evidence only from documents the caller is allowed to access.

Acceptance criteria:

- ownership scope is applied inside the retrieval query;
- deleted and inactive versions are excluded;
- `top_k` has a configured maximum;
- results include document, version, chunk, location, and score;
- cross-owner retrieval is covered by integration tests.

### FR-005: Evidence-based answers

The system must answer a question only when retrieved passages provide sufficient support.

Acceptance criteria:

- a supported answer includes citations to stored chunks;
- citations identify the exact document version;
- unsupported questions return `insufficient_evidence`;
- the model cannot invent a citation identifier;
- the response includes a request identifier.

### FR-006: Versioned evaluation

The system must evaluate retrieval and answer behavior against a curated dataset.

Acceptance criteria:

- the dataset includes supported, ambiguous, conflicting, and unsupported questions;
- reports record dataset and retrieval configuration;
- evaluation can run without modifying production data;
- regressions are visible in pull requests.

## Non-functional requirements

### NFR-001: Testability

Domain behavior and API contracts must be testable without calling a real LLM. PostgreSQL-specific behavior must be tested against PostgreSQL with pgvector.

### NFR-002: Security

Uploaded documents are untrusted input. Access control must be applied before evidence is exposed, secrets must not appear in logs, and document content must not grant tools or permissions.

### NFR-003: Observability

Ingestion, retrieval, and generation operations must share a correlation identifier and expose stage latency, outcome, provider configuration, and failure reason without logging sensitive content by default.

### NFR-004: Reproducibility

A clean environment must install the project, apply all migrations, run deterministic tests, and reproduce an evaluation report from versioned configuration.

### NFR-005: Focused extensibility

Provider abstractions are allowed at external boundaries expected to change. New internal interfaces or layers require a concrete second implementation, testing need, or documented architectural constraint.

## Deferred capabilities

Text-to-SQL, autonomous agents, PDF parsing, user interfaces, and multiple vector databases are not part of the RAG MVP.
