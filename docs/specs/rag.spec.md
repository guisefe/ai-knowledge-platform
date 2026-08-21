# RAG Spec

## Objective

Return answers supported by stored document passages and abstain when the available evidence is insufficient.

## Target endpoint

`POST /api/v1/rag/query`

## Request rules

- an empty question returns `422`;
- `top_k` has a configured maximum;
- retrieval scope is derived from authorization, not accepted blindly from the request;
- inactive, failed, and deleted document versions are excluded.

## Answer contract

An `answered` response includes:

- a concise answer;
- citations to stored chunk identifiers;
- document identifier and version for each citation;
- source location and excerpt;
- retrieval metadata;
- a request identifier.

An unsupported response uses `status: insufficient_evidence`, has no generated answer, and does not invent citations.

## Security rules

- ownership filtering occurs inside the retrieval query;
- retrieved document instructions cannot grant tools, permissions, or additional data access;
- citation identifiers must resolve to chunks returned by retrieval;
- raw document content is not written to logs by default.

## Contract and integration tests

- a supported question returns citations from the authorized corpus;
- an unsupported question returns `insufficient_evidence`;
- an empty question returns `422`;
- `top_k` above the configured maximum returns `422`;
- fabricated citation identifiers are rejected;
- retrieval cannot return another owner's chunks;
- every cited chunk belongs to the reported document version.
