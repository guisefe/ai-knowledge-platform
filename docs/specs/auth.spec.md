# Auth Spec

## Objective

Provide secure authentication using email/password and JWT access tokens.

## Endpoints

POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me

## Rules

- email must be unique;
- password must never be stored in plain text;
- invalid credentials return 401;
- invalid tokens return 401;
- protected endpoints require a valid bearer token.

## Contract Tests

- register returns 201 with expected payload;
- duplicate email returns 409;
- login with valid credentials returns token;
- login with invalid credentials returns 401;
- /me without token returns 401.
