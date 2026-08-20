# Documents Spec

## Objective

Allow authenticated users to upload, list, inspect, and delete documents.

## Endpoints

POST /api/v1/documents
GET /api/v1/documents
GET /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}

## Supported Statuses

uploaded
processing
indexed
failed
deleted

## Rules

- document must belong to an authenticated user or organization;
- unsupported files must be rejected;
- deleted documents must not appear in retrieval;
- parser failures must set status to failed;
- uploaded documents must be processed asynchronously.

## Contract Tests

- upload supported file returns 201;
- upload unsupported file returns 415;
- list documents returns only current user's documents;
- get missing document returns 404;
- delete document returns 204.
