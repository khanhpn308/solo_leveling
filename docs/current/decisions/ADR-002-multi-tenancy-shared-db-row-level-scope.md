# ADR-002: Multi-Tenancy — Shared DB, Row-Level Scope By account_id

## Status

**Superseded (2026-06-11)** — owner dropped the public-SaaS direction the same day (see
[`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md)). Full multi-tenant isolation across ~123 routes is
no longer pursued; only **basic per-account data scoping** (users don't overwrite each other) is kept
as P0. Retained for decision history.

## Date

2026-06-11

## Context

The product owner decided to take the app to a **public multi-tenant SaaS** (open sign-up).
The current business core is fundamentally single-player: `get_active_player(db)` is
`db.query(Player).first()` ([backend/app/services.py:235](../../../backend/app/services.py)),
returning the first player in the DB regardless of who is authenticated. Many routes resolve the
player/campaign through this path (~123 routes, 137 resolve call sites in `main.py`), so if two
users exist, data leaks across accounts. The auth layer (`Account` / JWT / session) is already
complete, and newer endpoints already scope by `account.id`.

Two structural options were considered:

- **Shared DB with row-level scoping** by `account_id` (one database, every query filtered).
- **Instance-per-customer** (one container + one DB per customer), avoiding the data-layer rewrite.

## Decision

Use a **single shared database with row-level scoping by `account_id`**. Fix the data-access
layer **at the root** rather than auditing 123 routes individually:

- Remove the `get_active_player().first()` variant entirely so no route can fetch the "first"
  player anymore; make every resolve require an authenticated account.
- Standardize all routes onto `get_current_player` / `get_current_campaign`, which already scope
  by `account.id`.
- Let the compiler/runtime surface every caller not yet migrated (a missing account becomes a
  hard failure, not a silent leak).
- Add a strict **cross-account test** (two accounts, sweep every route, assert no leak) that runs
  in CI as the definitive proof of isolation.

Instance-per-customer was rejected: its operational and cost overhead scales linearly with the
number of customers and only makes sense for a few paying customers, which is not the target.

## Consequences

Positive:

- One isolation model for the whole app; a single cross-account test proves correctness.
- "Fix at the root" turns silent leaks into hard failures — safer for a single developer.
- Cheapest infrastructure for the target scale (tens–hundreds of free users).

Tradeoffs:

- A large, cross-cutting change touching ~123 routes — this is the heaviest item in Phase 1 (P1b).
- All tenant data shares one database; a future hard-isolation requirement would need rework.
