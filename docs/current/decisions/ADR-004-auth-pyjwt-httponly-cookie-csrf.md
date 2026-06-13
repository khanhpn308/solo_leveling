# ADR-004: Auth — PyJWT + Fail-Fast Secret + Access Token In httpOnly Cookie + CSRF

## Status

**Superseded (2026-06-11)** — owner dropped the public-SaaS direction (see
[`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md)). For the small-group tool, only **removing the
hardcoded JWT secret** is kept (P0); PyJWT migration, httpOnly-cookie + CSRF are NOT pursued
(localStorage token is acceptable for trusted users). Retained for history.

## Date

2026-06-11

## Context

The current auth is hand-rolled. JWTs are signed with `hmac` manually
([backend/app/auth_utils.py:17](../../../backend/app/auth_utils.py)), and the secret has a
hardcoded fallback: `os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-prod-123456789")`
([auth_utils.py:8](../../../backend/app/auth_utils.py)). On a public SaaS, anyone who knows that
fallback string (it is in the repo) can forge a token for any account, including admins; and if the
production server forgets to set the env var, the whole auth system silently becomes decorative.

The access token is stored in `localStorage` ([backend → frontend/src/api/client.js:3](../../../frontend/src/api/client.js)),
which is readable by JavaScript — any XSS hole harvests tokens. For a single user the risk is small;
for a multi-user public SaaS, one XSS becomes mass token theft. The refresh token is already an
httpOnly cookie with rotation, so a cookie-based architecture is not foreign to the codebase.

## Decision

- **Replace the hand-rolled JWT with PyJWT** (standard library, fewer subtle pitfalls, supports
  audience/issuer and algorithm flexibility). Rewrite create/decode and update the auth tests.
- **Fail-fast secret:** remove the hardcoded fallback; the app **refuses to start** if
  `JWT_SECRET_KEY` is missing, with a clear error. Also sweep other weak defaults (DB password in
  `database.py`, MySQL credentials in compose).
- **Move the access token into an httpOnly cookie** so XSS cannot read it, and add **CSRF
  protection** (cookies are sent automatically, so a CSRF token / strict SameSite is required).
  This changes both frontend (`apiFetch` drops the `Authorization` header) and backend
  (`get_current_account` reads the cookie instead of the Bearer header).

## Consequences

Positive:

- Forged-token account takeover is closed (fail-fast secret + a real signing library).
- XSS can no longer read the access token (httpOnly).
- Aligns with the already-cookie-based refresh flow.

Tradeoffs:

- A cross-cutting change to both FE and BE auth paths.
- CSRF is the part most easily done wrong; it must be implemented and tested carefully.
