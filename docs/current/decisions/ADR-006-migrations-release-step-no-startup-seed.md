# ADR-006: Migrations — Separate Release Step, No Auto-Migrate/Seed In on_startup In Production

## Status

**Superseded (2026-06-11)** — owner dropped the public-SaaS direction (see
[`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md)). For a single shared server with few users, the
current startup migrate/seed is acceptable; decoupling migrations into a release step is no longer
pursued. Retained for history.

## Date

2026-06-11

## Context

Today, `on_startup` ([backend/app/main.py:443](../../../backend/app/main.py)) calls
`run_database_bootstrap()` and then `seed_database()` on **every** container start.
`run_database_bootstrap` ([backend/app/database.py:49](../../../backend/app/database.py)) runs
`command.upgrade(head)` at startup. With a single instance this is fine, but:

- If the SaaS ever scales to multiple instances, they would **race to run migrations** on startup,
  which can corrupt schema state.
- `seed_database` running on every start is wasteful and risky in production (even though it is
  idempotent) — production data should come from real users, not the seed.

The migration filenames already follow `YYYYMMDD_NN` with `upgrade()`/`downgrade()` (23 migrations
through `20260611_23`), so the migration mechanics are sound; what is missing is separating "run
migrations" from "start the app".

## Decision

- Run migrations as a **separate release step** — a release command / job that runs
  `alembic upgrade head` **once** before the app starts. Remove auto-migrate from `on_startup`.
- **Do not seed in production.** Seeding remains a dev/demo concern; production schema is migrated,
  production data is created by real users.
- "True zero-downtime migrations" (additive-only, no large table locks) is deferred until there is
  real traffic — not needed at the target scale.

## Consequences

Positive:

- Safe when scaling to multiple instances (no migration race).
- No seed/demo data leaking into production.
- Migrations become an explicit, observable deploy step.

Tradeoffs:

- The deploy pipeline must include the release step (the PaaS supports release commands).
- Local dev must run migrations explicitly (or keep the dev-only startup path behind the
  `ENVIRONMENT` flag from ADR-005).
