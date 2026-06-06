# Test Report

Newest first.

## 2026-06-06 - Repo-first prompt guides glossary refinement

Status: `Passed`

Checks:

- added glossary section to `prompt-en.md`
- added matching glossary section to `prompt-vi.md`
- covered:
  - platform-level protocol
  - repo operating standard
  - skill
  - harness
  - orchestrator
  - worker

Notes:

- This was a documentation-only refinement.

## 2026-06-06 - Repo-first prompt guides expanded with minimum validation matrix

Status: `Passed`

Checks:

- added task-specific minimum validation guidance to `prompt-en.md`
- added matching Vietnamese guidance to `prompt-vi.md`
- covered:
  - backend
  - migration/database
  - frontend
  - debugging
  - review-only
  - documentation-only
  - session-close-only

Notes:

- This was a documentation-only refinement.
- No application runtime validation was required.

## 2026-06-06 - Repo-first prompt guides expanded with task-specific context loading

Status: `Passed`

Checks:

- extended `prompt-en.md` with task-specific context expansion
- extended `prompt-vi.md` with the same repo-first guidance in Vietnamese
- added stop rules for context loading

Notes:

- This was a documentation-only refinement.
- No application runtime validation was required.

## 2026-06-06 - Generic prompt playbook split validation

Status: `Passed`

Checks:

- added generic Codex playbooks:
  - `docs/current/prompt-generic-en.md`
  - `docs/current/prompt-generic-vi.md`
- kept repo-first guides intact:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- updated canonical doc map to distinguish generic vs repo-first usage
- reran local markdown link scan after the split

Results:

- local markdown links checked: `89`
- broken local links: `0`

## 2026-06-06 - Prompt playbook and library documentation validation

Status: `Passed`

Checks:

- created bilingual prompt guides:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- updated canonical docs map in:
  - `README.md`
  - `AGENTS.md`
  - `docs/current/CONTEXT_INDEX.md`
- updated tracker and decision ledger references
- repo-managed markdown links remain valid after the additions

Notes:

- This was a documentation-only change.
- No application runtime validation was required.

## 2026-06-06 - Repository-wide stale-link scan after documentation reorganization

Status: `Passed`

Checks:

- parsed local markdown links across repo docs
- excluded `node_modules` and `.git`
- resolved relative paths from each source markdown file
- verified target existence for all local markdown links

Results:

- markdown files scanned: `18`
- local markdown links checked: `69`
- broken local links: `0`

Notes:

- This confirms the current documentation move to `docs/current/` and `docs/history/` did not leave stale local markdown links in repo-managed docs.

## 2026-06-06 - Documentation reorganization validation

Status: `Passed`

Checks:

- root entrypoint files rewritten
- canonical docs created under `docs/current/`
- history docs created under `docs/history/`
- changelog reordered newest-first
- task tracker compressed to active state only
- AGENTS load order updated

Notes:

- This was a documentation-only change.
- No application API or database validation was required for this slice.

## 2026-06-06 - Wave E validation snapshot

Status: `Passed`

Highlights:

- `python -m py_compile`: passed
- pre-migration reset safety: passed
- Alembic upgrade to `20260606_08`: passed
- post-migration SQL audits: all target null/duplicate counts `0`
- live HTTP smoke:
  - `/api/health`
  - `/api/checkins`
  - `/api/summary`
  - `/api/weekly-mission/current`
  - `/api/quests/today`
  - `/api/dev/reset`

## 2026-06-05 - Wave D validation snapshot

Status: `Passed`

Highlights:

- syntax checks passed
- live API smoke passed for campaign-scoped skill, badge, summary, suggestion, check-in, and quest flows
- typed quest completion dual-write verified manually

## 2026-06-05 - Wave C validation snapshot

Status: `Passed`

Highlights:

- data-only Alembic upgrade reached `20260605_07`
- backfill left `0` null campaign rows in current local DB for the targeted tables
- seeded daily quests had `0` null `daily_slot_code`

## 2026-06-05 - Wave B validation snapshot

Status: `Passed`

Highlights:

- new additive tables exist
- expected indexes and unique keys exist
- tables remained empty immediately after migration
- reset and English seed sync were verified

## 2026-06-05 - Wave A validation snapshot

Status: `Passed`

Highlights:

- nullable campaign/typed-link columns exist
- backend syntax checks passed
- migration upgrade passed with local MySQL URL override
