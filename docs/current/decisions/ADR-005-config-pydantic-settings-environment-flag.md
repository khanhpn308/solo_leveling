# ADR-005: Config — Pydantic Settings + ENVIRONMENT Flag As Central Switch

## Status

**Superseded (2026-06-11)** — owner dropped the public-SaaS direction (see
[`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md)). A full Pydantic-Settings refactor is no longer
required; the small-group P0 only needs an env var for the JWT secret and a simple way to disable dev
endpoints. Retained for history.

## Date

2026-06-11

## Context

Configuration is currently hardcoded in `docker-compose.yml`: CORS lists both localhost and the old
EC2 IP ([docker-compose.yml:30](../../../docker-compose.yml)), `VITE_API_URL` hardcodes that IP
([docker-compose.yml:48](../../../docker-compose.yml)), and DB/MySQL credentials are written inline.
There is no `.env.example` and no environment flag. Several decided must-fixes depend on a clean
config layer that does not yet exist: fail-fast secret (ADR-004), disabling dev endpoints in prod,
not seeding in prod, and the cookie `Secure` flag all need a central place to branch on environment.

## Decision

Introduce a **Pydantic Settings** class as the single source of configuration truth (centralized,
type-validated, with required variables made explicit), plus:

- An **`ENVIRONMENT`** variable (`development` / `production`) as the central switch for:
  enabling/disabling `/api/dev/*`, fail-fast secret behavior, whether to seed, and the cookie
  `Secure` flag.
- All secrets/hosts via environment variables, documented in a **`.env.example`** that lists every
  required key (no real values). **No secret is hardcoded in the repo.**
- The existing `docker-compose.yml` becomes **dev-only** (keeps reload + volume mounts); a separate
  **production configuration** (a `compose.prod` or the PaaS config) has no reload, no volume mount,
  and does not expose the DB port externally.

## Consequences

Positive:

- A single, validated config surface; required variables fail loudly when missing.
- Cleanly enables the env-gated behaviors of ADR-004 and the dev-endpoint/seed/migration decisions.
- Clear dev/prod separation.

Tradeoffs:

- Slightly more upfront work than scattered `os.getenv` calls.
- Every config consumer must be migrated to read from the Settings object.
