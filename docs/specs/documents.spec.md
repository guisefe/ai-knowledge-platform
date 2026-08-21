# Documents Spec

## Objective

Store logical documents and immutable content versions so ingestion is idempotent and every retrieved passage has traceable provenance.

## Target endpoints

- `POST /api/v1/documents`
- `POST /api/v1/documents/{document_id}/versions`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `DELETE /api/v1/documents/{document_id}`

## Lifecycle

A document is the logical identity visible to the user. A document version owns the checksum, storage location, processing status, and failure reason.

Supported version statuses:

- `uploaded`;
- `processing`;
- `indexed`;
- `failed`;
- `deleted`.

## Rules

- access is scoped to the authenticated owner or organization;
- the first upload creates document version 1;
- changed content creates the next version;
- identical content does not create another version;
- only one version is active for current retrieval;
- previous versions remain available for audit;
- deleted documents and versions never appear in current retrieval;
- retries do not duplicate chunks;
- processing failures preserve an actionable reason.

## Contract and integration tests

- supported upload returns `201`;
- unsupported media type returns `415`;
- identical upload returns the existing version;
- changed content increments the version number;
- list and get operations never expose another owner's documents;
- deletion removes the document from current retrieval;
- migrations and ownership constraints are validated against PostgreSQL.
