# Deterministic Processing Spec

## Objective

Transform an uploaded UTF-8 text or Markdown document version into an ordered,
reproducible set of chunks with enough provenance to support retrieval, citations,
auditing, and safe retries.

## Scope

The first processing implementation supports:

- `text/plain`;
- `text/markdown`;
- deterministic text normalization;
- deterministic character-based chunk boundaries;
- persisted chunk content and source offsets.

PDF parsing, OCR, semantic chunking, and provider-specific tokenization are deferred.

## Normalized source text

Processing must decode content as UTF-8 and normalize line endings from `CRLF` or
`CR` to `LF`. It must not silently replace invalid bytes.

Markdown is treated as source text in the first implementation. Markdown syntax may
inform safe split boundaries, but the persisted chunk content must remain traceable
to the normalized source without model-generated rewriting or summarization.

## Chunk contract

Each persisted chunk contains:

- a stable identifier;
- the owning document version identifier;
- a zero-based position within that version;
- non-empty chunk content;
- the SHA-256 digest of that exact content;
- zero-based `start_offset` and exclusive `end_offset` character positions in the
  normalized source text;
- its creation timestamp.

Chunk order is defined by `position`, not by creation time or identifier.

## Determinism rules

Given identical normalized text and the same processing configuration, processing
must produce the same:

- number of chunks;
- chunk positions;
- chunk content;
- source offsets;
- content digests.

The processing configuration must include a named strategy version, maximum chunk
size, and overlap. A configuration change is evaluated explicitly and must not
silently alter already indexed document versions.

## Lifecycle and atomicity

- only versions in `uploaded` or `failed` state may start processing;
- processing changes the version status to `processing`;
- the complete chunk set is stored in the same transaction;
- a version changes to `indexed` only after all chunks are persisted successfully;
- a failure rolls back partial chunks, changes the version to `failed`, and stores an
  actionable reason;
- an indexed version becomes active only after successful processing;
- an inactive, failed, or deleted version is never eligible for current retrieval.

## Idempotency

There is at most one chunk for a given document version and position. Retrying the
same version with the same configuration must not create additional chunks.

A retry must either recognize an identical complete chunk set or replace the
version's chunk set atomically. Partial replacement is not allowed.

## Security and observability

- document ownership is checked before stored content is read for processing;
- chunk ownership is always derived through its document version and document;
- raw document and chunk content are not written to logs by default;
- processing logs include a request identifier, document version identifier,
  strategy version, duration, outcome, and sanitized failure reason.

## Contract and integration tests

- identical input and configuration produce identical chunks;
- line-ending normalization is deterministic;
- every chunk has valid ordered offsets into the normalized source;
- chunk content and digest match the persisted source slice;
- duplicate positions for one version are rejected;
- the same position may exist in different versions;
- failed processing leaves no partial chunks and preserves a reason;
- retrying processing does not duplicate chunks;
- successful processing marks the version `indexed` and allows activation;
- processing cannot read another owner's document content.
