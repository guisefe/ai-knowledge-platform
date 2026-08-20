# Text-to-SQL Spec

## Objective

Allow safe natural language querying over structured data.

## Endpoint

POST /api/v1/sql/ask

## Rules

- only SELECT statements are allowed;
- DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE are blocked;
- multiple statements are blocked;
- only registered tables are allowed;
- LIMIT must be enforced;
- generated SQL must be logged;
- unsafe SQL must not be executed.

## Contract Tests

- SELECT query is accepted;
- destructive commands are rejected;
- multiple statements are rejected;
- queries without LIMIT receive enforced limit;
- unknown tables are rejected.
