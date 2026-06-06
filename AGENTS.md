# Repository Agent Guide

## Purpose

This file is the root agent entrypoint for `IELTS Quest Dashboard`.

Use it to:

- understand the project quickly
- load context in the correct order
- follow repository-specific workflow and documentation rules

## Project Summary

- Product: local gamified IELTS Academic dashboard
- User goal: reach IELTS `7.0-7.5` over an 18-month campaign
- Stack: React + Vite, FastAPI, MySQL, Docker Compose
- Theme direction: game-style progression dashboard

## Session Context Load Order

Read these first, in order:

1. [AGENTS.md](AGENTS.md)
2. [README.md](README.md)
3. [TASKS.md](TASKS.md)
4. [DECISIONS.md](DECISIONS.md)
5. [docs/current/CONTEXT_INDEX.md](docs/current/CONTEXT_INDEX.md)

After that, read only the task-specific canonical docs or history docs that matter.

## Canonical vs History

Canonical docs live under `docs/current/`.
They are the source of truth for current project understanding.

History docs live under `docs/history/`.
They are for:

- implementation logs
- validation snapshots
- migration history
- superseded planning notes

Do not treat history files as the primary source of current product truth unless the canonical docs point you there.

## Root File Roles

- [README.md](README.md): project overview, startup, docs map
- [TASKS.md](TASKS.md): active tracker only
- [DECISIONS.md](DECISIONS.md): concise decision ledger
- [AGENTS.md](AGENTS.md): agent workflow and documentation rules

## Current Canonical Docs

- [docs/current/CONTEXT_INDEX.md](docs/current/CONTEXT_INDEX.md)
- [docs/current/PROJECT_CONTEXT.md](docs/current/PROJECT_CONTEXT.md)
- [docs/current/BUSINESS_RULES.md](docs/current/BUSINESS_RULES.md)
- [docs/current/DATABASE_SCHEMA.md](docs/current/DATABASE_SCHEMA.md)
- [docs/current/SCHEMA_SEMANTICS.md](docs/current/SCHEMA_SEMANTICS.md)
- [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md)
- [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md)
- [docs/current/prompt-en.md](docs/current/prompt-en.md)
- [docs/current/prompt-vi.md](docs/current/prompt-vi.md)
- [docs/current/decisions/ADR-001-documentation-layout-and-context-loading.md](docs/current/decisions/ADR-001-documentation-layout-and-context-loading.md)

## History Docs

- [docs/history/changelogs.md](docs/history/changelogs.md)
- [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md)
- [docs/history/AGENT_NOTES.md](docs/history/AGENT_NOTES.md)
- [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)
- [docs/history/FRONTEND_PLAN.md](docs/history/FRONTEND_PLAN.md)

## Engineering Rules

- Keep the app runnable with Docker Compose.
- Do not remove existing features unless explicitly requested.
- Prefer additive, low-risk changes for schema and API evolution.
- Keep documentation in English.
- Keep public API response shapes stable unless the user approves a contract change.

## Documentation Rules

- Update [docs/history/changelogs.md](docs/history/changelogs.md) after each implementation task.
- Changelog entries must be **newest first**.
- Update [TASKS.md](TASKS.md) immediately when a tracked task changes status.
- Update [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md) after meaningful validation.
- Update [docs/history/AGENT_NOTES.md](docs/history/AGENT_NOTES.md) with short factual notes only.
- Record enduring architecture or workflow decisions in [DECISIONS.md](DECISIONS.md) and, when needed, an ADR under `docs/current/decisions/`.

## Validation Expectations

When code changes are made:

- run syntax checks when possible
- run focused smoke tests when possible
- explain any skipped validation clearly

## Current Open Work Themes

- browser visual verification
- automated backend tests for post-migration behavior
- deferred cleanup of legacy database fields

See [TASKS.md](TASKS.md) for exact active items.
