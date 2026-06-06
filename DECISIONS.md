# Decision Ledger

Last updated: `2026-06-06`

## Accepted Decisions

### 2026-06-04 - Frontend redesign stays frontend-only

- Status: `Accepted`
- Decision: keep the home dashboard redesign frontend-only and avoid backend/schema changes for that slice.
- Why: reduce risk and preserve shipping speed.

### 2026-06-05 - Use additive database migration waves

- Status: `Accepted`
- Decision: evolve the backend schema through Waves `A-E` instead of rewriting mutable state tables in place.
- Why: safer rollout, easier validation, lower migration risk.
- Details: [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)

### 2026-06-05 - Campaign-scoped state becomes the source of truth

- Status: `Accepted`
- Decision: use `campaign_skill_states` for live skill progression and `badge_unlocks` for campaign-scoped badge ownership.
- Why: the old global mutable state model was not safe for campaign scoping.

### 2026-06-05 - Reward claim gates XP banking

- Status: `Accepted`
- Decision: quest and weekly XP are only banked after explicit reward claim.
- Why: clearer game loop and better UX feedback.

### 2026-06-06 - Documentation is split into canonical and historical layers

- Status: `Accepted`
- Decision: keep root entrypoints minimal, move source-of-truth docs under `docs/current/`, and move logs/history under `docs/history/`.
- Why: improve session startup quality and reduce context noise.
- ADR: [docs/current/decisions/ADR-001-documentation-layout-and-context-loading.md](docs/current/decisions/ADR-001-documentation-layout-and-context-loading.md)

### 2026-06-06 - Codex session guidance is maintained as prompt playbooks

- Status: `Accepted`
- Decision: keep both generic and repo-first Codex playbooks.
- Why: the generic guides are reusable across repositories, while the repo-first guides preserve this project's exact workflow and documentation expectations.
