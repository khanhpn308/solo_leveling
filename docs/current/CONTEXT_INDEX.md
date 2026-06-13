# Context Index

This file is the canonical map for loading project context.

## Default Read Order

Start with:

1. [../../AGENTS.md](../../AGENTS.md)
2. [../../README.md](../../README.md)
3. [../../TASKS.md](../../TASKS.md)
4. [../../DECISIONS.md](../../DECISIONS.md)
5. [CONTEXT_INDEX.md](CONTEXT_INDEX.md)

Then load only what the task needs.

## Canonical Docs

- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)
  - load when you need product/user goals and project boundaries
- [BUSINESS_RULES.md](BUSINESS_RULES.md)
  - load when you need domain logic, gameplay rules, and progression behavior
- [SMALL_GROUP_PLAN.md](SMALL_GROUP_PLAN.md) **(current direction, 2026-06-11)**
  - load when you need the current product direction: small-group internal tool, P0 minimum hygiene, feature-work priority. **This is the active plan.**
- [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) — **SUPERSEDED 2026-06-11**
  - historical public-SaaS roadmap (12-point DoD, phasing). Superseded by SMALL_GROUP_PLAN.md; load only for decision history, NOT as current truth. ADR-002…006 are likewise superseded.
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
  - load when you need the current database model at a structural level
- [SCHEMA_SEMANTICS.md](SCHEMA_SEMANTICS.md)
  - load when you need the exact meaning of enum-like or state-like fields
- [prompt-generic-en.md](prompt-generic-en.md)
  - load when you want a reusable Codex workflow for any repo
- [prompt-generic-vi.md](prompt-generic-vi.md)
  - load when you want the same generic guidance in Vietnamese
- [prompt-en.md](prompt-en.md)
  - load when you need the repo-first Codex session workflow and prompt templates for this project
- [prompt-vi.md](prompt-vi.md)
  - load when the user wants the repo-first workflow guidance in Vietnamese

## Architecture Decisions (ADRs)

Load a specific ADR when you need the rationale behind an architectural choice:

- [decisions/ADR-001-documentation-layout-and-context-loading.md](decisions/ADR-001-documentation-layout-and-context-loading.md)
- [decisions/ADR-002-multi-tenancy-shared-db-row-level-scope.md](decisions/ADR-002-multi-tenancy-shared-db-row-level-scope.md)
- [decisions/ADR-003-deploy-target-managed-paas.md](decisions/ADR-003-deploy-target-managed-paas.md)
- [decisions/ADR-004-auth-pyjwt-httponly-cookie-csrf.md](decisions/ADR-004-auth-pyjwt-httponly-cookie-csrf.md)
- [decisions/ADR-005-config-pydantic-settings-environment-flag.md](decisions/ADR-005-config-pydantic-settings-environment-flag.md)
- [decisions/ADR-006-migrations-release-step-no-startup-seed.md](decisions/ADR-006-migrations-release-step-no-startup-seed.md)

ADR-002 through ADR-006 record the production-readiness decisions; see
[PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for how they fit together.

## History Docs

Load these only when needed:

- [../history/MIGRATION_HISTORY.md](../history/MIGRATION_HISTORY.md)
  - for the Wave A-E backend migration story
- [../history/TEST_REPORT.md](../history/TEST_REPORT.md)
  - for recent validation evidence
- [../history/changelogs.md](../history/changelogs.md)
  - for recent implementation diffs and task logs
- [../history/AGENT_NOTES.md](../history/AGENT_NOTES.md)
  - for short factual build/change notes

## What Not To Do

- Do not load history docs first.
- Do not use `TASKS.md` as a long-term architecture document.
- Do not rely on stale historical plan files when a canonical file exists.
