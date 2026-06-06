# IELTS Quest Dashboard

Local IELTS Academic self-study dashboard with a game-style progression loop.

## What This Project Is

This repo tracks an 18-month IELTS study campaign starting on `2026-06-04`.
The stack is:

- Frontend: React + Vite
- Backend: FastAPI
- Database: MySQL
- Runtime: Docker Compose

The product direction is a game-inspired study dashboard with:

- campaign roadmap phases
- main / daily / weekly quests
- reward-claim XP banking
- skill ranks from `F` to `S`
- badges and boss battles
- check-ins, trackers, and study history

The current UI copy is English-first.

## Quick Start

Run the full app:

```bash
docker compose up --build
```

Local URLs:

- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`
- MySQL host: `localhost`
- MySQL port: `3307`

## Context Load Order

For a new engineering session, read files in this order:

1. [AGENTS.md](AGENTS.md)
2. [README.md](README.md)
3. [TASKS.md](TASKS.md)
4. [DECISIONS.md](DECISIONS.md)
5. [docs/current/CONTEXT_INDEX.md](docs/current/CONTEXT_INDEX.md)

Then load only the specific canonical or history docs needed for the task.

## Docs Map

Root entrypoints:

- [AGENTS.md](AGENTS.md): agent rules and official context load order
- [TASKS.md](TASKS.md): active tracker only
- [DECISIONS.md](DECISIONS.md): short decision ledger
- [README.md](README.md): project overview and startup info

Canonical docs:

- [docs/current/CONTEXT_INDEX.md](docs/current/CONTEXT_INDEX.md)
- [docs/current/PROJECT_CONTEXT.md](docs/current/PROJECT_CONTEXT.md)
- [docs/current/BUSINESS_RULES.md](docs/current/BUSINESS_RULES.md)
- [docs/current/DATABASE_SCHEMA.md](docs/current/DATABASE_SCHEMA.md)
- [docs/current/SCHEMA_SEMANTICS.md](docs/current/SCHEMA_SEMANTICS.md)
- [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md)
- [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md)
- [docs/current/prompt-en.md](docs/current/prompt-en.md)
- [docs/current/prompt-vi.md](docs/current/prompt-vi.md)

History and validation:

- [docs/history/changelogs.md](docs/history/changelogs.md)
- [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md)
- [docs/history/AGENT_NOTES.md](docs/history/AGENT_NOTES.md)
- [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)
- [docs/history/FRONTEND_PLAN.md](docs/history/FRONTEND_PLAN.md)

## Current Technical State

- Frontend dashboard redesign is complete.
- Reward-claim flow is implemented.
- Database migration Waves `A` through `E` are complete.
- Campaign-scoped skill state now lives in `campaign_skill_states`.
- Campaign-scoped badge ownership now lives in `badge_unlocks`.
- Constraint hardening is complete for the current migration plan.

## Main Open Work

- browser visual walkthrough and screenshots
- automated backend tests for post-migration behavior
- future cleanup of deferred legacy database fields

## Working With Codex

Use these guides for session workflow and prompt quality:

- [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md): generic English playbook for Codex across repos
- [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md): generic Vietnamese playbook for Codex across repos
- [docs/current/prompt-en.md](docs/current/prompt-en.md): canonical English Codex session playbook and prompt library
- [docs/current/prompt-vi.md](docs/current/prompt-vi.md): Vietnamese operator version of the same workflow

See [TASKS.md](TASKS.md) for the current tracker.
