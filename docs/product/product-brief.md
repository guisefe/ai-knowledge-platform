# Product Brief

## Product statement

AI Knowledge Platform turns versioned operational documents into auditable answers. It returns the evidence and document version behind an answer or explicitly abstains when the available sources are insufficient.

## Problem

Operational knowledge often lives in policies, manuals, and procedures that are difficult to search and easy to use out of date.

A conventional RAG response can sound correct while relying on the wrong document, mixing versions, or inventing unsupported details. In operational workflows, a plausible answer without traceable evidence creates risk instead of value.

## Primary user

An operations analyst who needs to make or support a decision using current internal procedures without depending on manual folder searches or informal knowledge.

The analyst does not need to understand embeddings, prompts, or model providers. The analyst needs a concise answer, its source, and a clear refusal when the system cannot support the answer.

## Primary use case: current procedure lookup

Given a question and an authorized document collection, the system:

1. retrieves passages only from the caller's scope;
2. identifies the document version behind each passage;
3. returns a supported answer with citations; or
4. returns `insufficient_evidence`.

Success means the user can verify the answer without trusting the model blindly.

## Secondary use case: controlled document updates

When a procedure changes, the system preserves the previous version, indexes the new content, and makes the active version explicit.

Historical answers remain traceable to the sources that were available when they were produced.

## Integration use case

The capability is exposed through an API so internal portals, copilots, bots, and workflow tools can consume the same evidence contract. Building those clients is outside the MVP.

## Business value

- reduce time spent locating current procedures;
- reduce decisions based on outdated documents;
- make AI-generated answers reviewable;
- expose missing or conflicting documentation;
- provide a reusable backend capability instead of coupling the logic to one user interface.

## Demo strategy

The primary demo dataset represents a fictional organization with versioned policies and procedures. It contains intentional updates, conflicts, and gaps so the system can demonstrate version selection and abstention.

A separate public-domain literature corpus evaluates retrieval over longer and conceptually denser documents.

No real client data or proprietary documents are used.

## MVP boundaries

The MVP includes:

- document identity and version history;
- UTF-8 text and Markdown ingestion;
- deterministic parsing and chunking;
- PostgreSQL and pgvector retrieval;
- ownership-scoped queries;
- cited answers and explicit abstention;
- a versioned evaluation dataset and report.

The MVP excludes:

- PDF parsing;
- Text-to-SQL;
- autonomous agents;
- web or mobile interfaces;
- multiple vector databases;
- a catalog of model-provider integrations.

## Completion criteria

The MVP is complete when one document-to-answer path works end to end, integration tests run against PostgreSQL with pgvector, and the published evaluation report meets the defined quality gates.
