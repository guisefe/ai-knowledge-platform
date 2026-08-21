# ADR-003: Document Storage Boundary

## Status

Accepted

## Context

Uploaded source documents must survive API requests, remain traceable to an immutable database version, and avoid coupling domain behavior to a cloud vendor. Development and CI also need a deterministic implementation that works without external credentials.

User-controlled filenames cannot be trusted as storage paths. Uploads may be oversized, incorrectly labelled, invalid UTF-8, interrupted, duplicated, or submitted concurrently.

## Decision

The upload use case depends on a narrow document-storage protocol. The first adapter uses the local filesystem and is explicitly limited to development and single-instance deployments.

The adapter:

- streams content through bounded chunks;
- validates extension, declared media type, UTF-8 content, and configured size;
- calculates SHA-256 during the same pass;
- writes to isolated staging storage;
- uses server-generated keys containing owner ID, document ID, and checksum;
- atomically promotes a staged file only for a newly registered version.

The database document row is locked while a version is registered. This makes concurrent identical uploads converge on one immutable version.

## Consequences

- tests and local development do not require object-storage credentials;
- routes and domain services do not depend on filesystem APIs;
- an S3, Azure Blob Storage, or compatible adapter can replace local storage without changing the HTTP contract;
- horizontal production deployment requires a shared object-storage adapter;
- production ingress must enforce a request-body limit before multipart spooling;
- abandoned staging objects and unreferenced final objects require periodic operational cleanup in a production adapter.
