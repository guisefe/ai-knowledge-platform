# Documents Spec

## Objective

Store logical documents and immutable content versions so ingestion is idempotent and every retrieved passage has traceable provenance.

## Implemented document identity endpoints

- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `DELETE /api/v1/documents/{document_id}`

The content ingestion milestone adds:

- `POST /api/v1/documents/{document_id}/versions`

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
- owner identity is derived from the access token and never accepted from the payload;
- lists are paginated, deterministically ordered, and exclude soft-deleted documents;
- foreign and nonexistent document identifiers return the same `404` contract;
- repeated deletion by the owner is idempotent;
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
