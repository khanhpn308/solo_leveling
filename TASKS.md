# IELTS Quest Dashboard Tasks

Last updated: `2026-06-06`

## Session Resume

- Frontend redesign is complete and accepted.
- Reward-claim flow is complete.
- Backend migration Waves `A-E` are complete.
- Campaign-scoped skill and badge state are live.
- Documentation/context reorganization is now complete.
- Repo-first Codex prompt playbooks now exist in English and Vietnamese.
- Generic Codex prompt playbooks now also exist in English and Vietnamese.

## Current State

- Canonical context now lives under `docs/current/`.
- History and validation logs now live under `docs/history/`.
- Root files are reduced to session entrypoints:
  - `README.md`
  - `AGENTS.md`
  - `TASKS.md`
  - `DECISIONS.md`

## Active Documentation Reorganization Tracker

Status legend:

- `Done`
- `Not done`

### Documentation and Context Restructure

- `Done` Audit the current repo documentation and identify canonical vs historical files.
- `Done` Keep only root entrypoint files for session startup.
- `Done` Create `docs/current/` for canonical low-churn project context.
- `Done` Create `docs/history/` for logs, validation, and historical planning records.
- `Done` Rewrite `README.md` as a concise human/project entrypoint.
- `Done` Rewrite `AGENTS.md` with official session load order and newest-first changelog rule.
- `Done` Compress `TASKS.md` into an active tracker instead of a full historical dump.
- `Done` Rewrite `DECISIONS.md` into a concise decision ledger.
- `Done` Add `docs/current/CONTEXT_INDEX.md`.
- `Done` Add `docs/current/SCHEMA_SEMANTICS.md`.
- `Done` Add an ADR for documentation layout and context loading.
- `Done` Move historical notes, validation, changelog, and migration summary into `docs/history/`.
- `Done` Normalize target documentation to English.
- `Done` Reorder changelog entries so the newest entries are at the top.
- `Done` Add repo-first Codex session playbooks and prompt libraries in English and Vietnamese.
- `Done` Add generic Codex session playbooks in English and Vietnamese alongside the repo-first versions.

## In Progress

- Browser visual walkthrough / screenshot verification remains pending.
- Automated backend tests for Wave D and Wave E behavior remain pending.

## Next Tasks

1. Capture a browser visual review of the current dashboard and overlays.
2. Add automated backend tests for:
   - campaign-scoped skill state
   - badge unlock read path
   - check-in upsert behavior
   - daily-slot invariants
3. Plan deferred legacy cleanup only after backend tests exist.

## Deferred Backlog

- Drop legacy quest tracker fields:
  - `tracker_type`
  - `tracker_entry_id`
- Drop legacy weakness source fields:
  - `source_type`
  - `source_ref_id`
- Drop global mutable state columns from `skills`.
- Drop global unlock-state columns from `badges`.
- Add stricter typed-source / typed-tracker check constraints after legacy-field removal planning.

## Known Risks

- Browser automation is still unavailable in the current environment.
- Manual smoke coverage exists, but automated backend coverage is still thin for the new migration behavior.
- Legacy compatibility fields still exist in the database by design.

## Where To Read More

- Migration summary: [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)
- Latest validation: [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md)
- Latest implementation log: [docs/history/changelogs.md](docs/history/changelogs.md)
- Generic Codex guide (EN): [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md)
- Generic Codex guide (VI): [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md)
- Codex operator guide (EN): [docs/current/prompt-en.md](docs/current/prompt-en.md)
- Codex operator guide (VI): [docs/current/prompt-vi.md](docs/current/prompt-vi.md)
