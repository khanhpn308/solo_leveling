# Small-Group Tool Plan — ielts-quest-dashboard

## Status

**Active (2026-06-11).** Supersedes [`PRODUCTION_ROADMAP.md`](PRODUCTION_ROADMAP.md) and ADR-002…006.
Decided by the owner via grill-me after changing direction away from public SaaS the same day.

---

## Context — why the direction changed

The earlier plan aimed at a **public multi-tenant SaaS** (3–6 month rewrite: ~123 routes made
multi-tenant, email verify, anti-bot, multi-template content). The owner reassessed and chose a
**lighter, realistic target**: this is an **internal tool for a small group of known people**, not a
public product. Priority shifts from production hardening to **finishing/fixing features**.

## Direction (decided)

| Axis | Decision |
|---|---|
| **Audience** | 5–20 known people (friends / learners the owner knows personally) |
| **Hosting** | One shared server, reachable over the internet but the link is only shared with the group |
| **Goal** | Finish features + fix bugs, not production-grade SaaS |
| **SaaS roadmap** | Dropped (PRODUCTION_ROADMAP + ADR-002…006 marked Superseded) |

### Explicitly NOT pursued (dropped from the SaaS plan)
Full multi-tenant isolation across all routes · email verify / forgot-password / email service ·
httpOnly-cookie + CSRF · global anti-bot rate limiting · Pydantic-Settings full refactor · migrations
release step · CI/CD · Sentry/observability stack · multi-template content authoring · PaaS deploy.
These remain available in the superseded docs if the public direction is ever revived.

---

## P0 — Minimum hygiene (still required because the app is on a shared internet-facing server)

Even for a trusted small group, three things are genuinely dangerous and must be fixed. These are the
*cheap* subset salvaged from the old P1a — nothing more.

> **Note:** P0 task details (file:line, acceptance) reuse the verified context in the superseded
> "Production Readiness — Phase 1a" block in [`../../TASKS.md`](../../TASKS.md) — only PR-2 (secret),
> PR-4 (dev gating), and a *basic* version of PR-1's isolation idea are kept.

1. **Stop `/api/dev/*` from being callable by anyone.** `POST /api/dev/reset` (`backend/app/main.py:1510`,
   unauthenticated) wipes the whole DB for everyone. Also `run_migrations` (`:1599`),
   `regenerate-quests` (`:1959`). → Disable them unless explicitly enabled (a simple env flag, e.g.
   `ENABLE_DEV_ENDPOINTS`, default off). No full Pydantic-Settings refactor needed.
2. **Remove the hardcoded JWT secret fallback.** `backend/app/auth_utils.py:8` has
   `"super-secret-key-change-in-prod-123456789"` as default → read `JWT_SECRET_KEY` from env, no weak
   fallback (fail or warn loudly if unset). Don't migrate to PyJWT, don't add CSRF — out of scope.
3. **Basic per-account data scoping (don't overwrite each other).** `get_active_player(db)` =
   `db.query(Player).first()` (`backend/app/services.py:235`) returns the first player regardless of
   who is logged in, and several routes resolve through it (`get_player_or_404` `main.py:429`). With
   >1 user this means people share/overwrite one player's progress. → Route the read/write paths
   through the already-correct account-scoped `get_current_player` / `get_current_campaign`
   (`main.py:270-297`) so each logged-in user gets their own player. **Goal is "right user → right
   data", NOT a hardened cross-account-attack test.** localStorage token stays (acceptable for a
   trusted group).

**P0 done = the group can use it on the shared server without one request wiping the DB, without a
known forgeable secret, and without users clobbering each other's progress.**

---

## Feature work (the actual priority)

Ordered by the owner's choice. Detailed task breakdown lives in the "Implementation Plan:
Small-Group Tool" block in [`../../TASKS.md`](../../TASKS.md) (to be filled when starting each item).

1. **Finish the in-progress mobile / UI work.** Continue `ui_mobile` / `fix_redesign_ui_mobile`
   (most recent commits show this is mid-flight) — complete responsive layout + unfinished UI.
2. **Fix bugs in existing features.** Sweep + fix issues in current features (Quest/XP, Boss, Vocab,
   Collocation, Rank exam, SRS) so they run smoothly, rather than adding new ones.

Not now (owner did not prioritize): real SM-2 SRS, brand-new learning features.

---

## What stays true regardless

- App keeps running via Docker Compose (dev as-is; no separate prod artifacts needed for a shared box).
- Don't remove existing features. Additive, low-risk changes.
- Repo docs in English. Use codegraph before manual Read/Grep.
- Per CLAUDE.md: archive a task only after `Gap check: [x]`.

## Pointers
- Superseded SaaS direction (history): [`PRODUCTION_ROADMAP.md`](PRODUCTION_ROADMAP.md), ADR-002…006.
- Verified current-state code references: the superseded P1a block in [`../../TASKS.md`](../../TASKS.md).
