# Auth Spec

## Objective

Provide secure authentication using email/password and JWT access tokens.

## Endpoints

POST /api/v1/auth/register
POST /api/v1/auth/token
GET /api/v1/auth/me

## Rules

- email must be unique;
- email is normalized before persistence and lookup;
- passwords contain between 12 and 128 characters;
- password must never be stored in plain text;
- the token endpoint accepts the email in OAuth2's `username` form field;
- invalid credentials return 401;
- invalid tokens return 401;
- inactive users cannot obtain or use an access token;
- protected endpoints require a valid bearer token.

## Contract Tests

- register returns 201 with expected payload;
- duplicate email returns 409;
- token request with valid credentials returns a bearer token;
- token request with invalid credentials returns 401;
- /me without token returns 401.
