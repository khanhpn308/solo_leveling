# Agent Notes

Newest first.

## 2026-06-06 - Repo-first glossary addition

- Added a short glossary to the repo-first prompt guides.
- The glossary now distinguishes platform rules from project workflow standards.

## 2026-06-06 - Repo-first minimum validation matrix

- Expanded the repo-first prompt guides with a minimum validation matrix by task type.
- Added validation baselines for:
  - backend
  - migration/database
  - frontend
  - debugging
  - review-only
  - documentation-only
  - session-close-only

## 2026-06-06 - Repo-first context loading expansion

- Expanded the repo-first prompt guides with task-specific context-loading rules.
- Added separate guidance for:
  - backend
  - migration/database
  - frontend
  - documentation
  - review
  - debugging
- Added stop rules so future sessions do not over-load context.

## 2026-06-06 - Generic prompt playbook split

- Added a generic layer on top of the existing repo-first prompt guides.
- New files:
  - `docs/current/prompt-generic-en.md`
  - `docs/current/prompt-generic-vi.md`
- Repo-first files remain the local source for this project:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- Updated docs maps so future sessions can choose correctly between generic and repo-specific guidance.

## 2026-06-06 - Bilingual Codex prompt playbooks

- Added repo-first Codex operator guides in:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- The English file is the canonical version for repo docs.
- The Vietnamese file mirrors the workflow for direct operator use.
- Updated root/canonical doc references so future sessions can discover the guides from `README.md`, `AGENTS.md`, and `docs/current/CONTEXT_INDEX.md`.

## 2026-06-06 - Repository-wide stale-link scan

- Confirmed the environment can now run a repo-wide stale-link scan.
- Ran an automated markdown-link existence check across repo-managed docs.
- Excluded `node_modules` and `.git`.
- Result:
  - markdown files scanned: `18`
  - local markdown links checked: `69`
  - broken links: `0`

## 2026-06-06 - Documentation and context reorganization

- Reorganized documentation for low-noise context loading.
- Reduced root documentation to four entrypoints:
  - `README.md`
  - `AGENTS.md`
  - `TASKS.md`
  - `DECISIONS.md`
- Created `docs/current/` for canonical project context.
- Created `docs/history/` for implementation history and validation logs.
- Rewrote root entrypoints in English.
- Added:
  - `CONTEXT_INDEX.md`
  - `SCHEMA_SEMANTICS.md`
  - ADR for documentation layout and context loading
- Normalized current documentation to English.
- Reordered changelog to newest-first.

## 2026-06-06 - Wave E constraint hardening

- Completed backend/database hardening after the Wave D cutover.
- Enforced `NOT NULL` campaign scope on the target tables.
- Replaced the old global check-in uniqueness with campaign-scoped uniqueness.
- Added daily-slot uniqueness protection for campaign-scoped daily quests.
- Validation passed on local migration and HTTP smoke.
- Remaining gap:
  - automated backend tests still missing

## 2026-06-05 - Wave D application cutover

- Switched live skill reads/writes to `campaign_skill_states`.
- Switched live badge reads to `badge_unlocks`.
- Scoped suggestions and check-ins to the active campaign.
- Added typed quest completion dual-write behavior.

## 2026-06-05 - Wave C data backfill

- Backfilled campaign scope and typed-link fields.
- Seeded campaign-scoped skill state.
- Seeded badge unlock rows when qualifying source rows existed.

## 2026-06-05 - Wave B additive state tables

- Added `campaign_skill_states`.
- Added `badge_unlocks`.
- Updated backend seed-fed English text.
- Fixed reset order for the new child tables.

## 2026-06-05 - Wave A nullable scope and typed-link columns

- Added campaign-scope columns and typed tracker/source link columns.
- Updated backend write paths to begin filling the new fields.
