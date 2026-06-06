# ADR-001: Documentation Layout And Context Loading

## Status

Accepted

## Date

2026-06-06

## Context

The repository had accumulated several large mixed-purpose files:

- task tracker mixed with migration history
- changelog mixed with old and new ordering
- validation and notes living at root
- duplicate or overlapping product context spread across root and `docs/`

This made session startup noisy and inconsistent.

## Decision

The repo documentation is split into:

- root entrypoints:
  - `README.md`
  - `AGENTS.md`
  - `TASKS.md`
  - `DECISIONS.md`
- canonical docs:
  - `docs/current/`
- historical logs and validation:
  - `docs/history/`

The official session load order is:

1. `AGENTS.md`
2. `README.md`
3. `TASKS.md`
4. `DECISIONS.md`
5. `docs/current/CONTEXT_INDEX.md`

## Consequences

Positive:

- faster session startup
- lower context noise
- clearer separation between source-of-truth docs and historical logs
- easier maintenance of current product knowledge

Tradeoffs:

- old file paths changed
- historical logs are now intentionally less prominent
- agents must follow the load order instead of reading history first
