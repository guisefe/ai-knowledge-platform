# Product Requirements

## Functional Requirements

### RF-001: Authentication

The system must allow users to register, log in, and access protected endpoints using JWT.

Acceptance criteria:

- users can register with email and password;
- passwords are stored using a secure hash;
- users can log in and receive an access token;
- protected endpoints reject missing or invalid tokens.

### RF-002: Document Upload

The system must allow authenticated users to upload documents for indexing.

Acceptance criteria:

- accepts supported file types;
- stores document metadata;
- sets initial document status as uploaded;
- returns a document ID;
- dispatches background processing.

### RF-003: Document Processing

The system must extract text, split it into chunks, generate embeddings, and store them in a vector store.

Acceptance criteria:

- document status changes to processing while being indexed;
- document status changes to indexed after successful processing;
- document status changes to failed when processing fails;
- chunks preserve reference to the original document.

### RF-004: RAG Query

The system must answer questions using indexed documents as context.

Acceptance criteria:

- receives a natural language question;
- retrieves semantically relevant chunks;
- builds a grounded prompt;
- generates an answer using the configured LLM provider;
- returns sources used in the answer;
- logs model, provider, latency, and metadata.

### RF-005: Safe Text-to-SQL

The system must generate and execute safe SQL queries from natural language questions.

Acceptance criteria:

- only SELECT statements are allowed;
- destructive commands are blocked;
- multiple statements are blocked;
- only allowed tables can be queried;
- LIMIT is enforced;
- generated SQL is logged.

### RF-006: LLM Provider Abstraction

The system must use an abstract LLM provider interface.

Acceptance criteria:

- application services do not depend directly on Ollama, OpenAI, Anthropic, or Azure OpenAI;
- provider is selected using configuration;
- tests can use a mock provider;
- new providers can be added without changing API routes.

## Non-Functional Requirements

### RNF-001: Open Source First

The first version must run without paid APIs or proprietary model providers.

### RNF-002: Testability

The system must be testable without requiring real LLM calls.

### RNF-003: Observability

The system must provide structured logs and basic runtime metadata.

### RNF-004: Security

The system must validate inputs, protect private endpoints, and block unsafe SQL.

### RNF-005: Extensibility

The system must be designed to support future model providers, vector stores, and enterprise integrations.
