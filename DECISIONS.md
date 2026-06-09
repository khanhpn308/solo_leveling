# Decision Ledger

Last updated: `2026-06-08`

## Accepted Decisions

### 2026-06-08 - Phase 10 & 11 Architecture Decisions

- Status: `Accepted`
- Decision:
  - **Cross-account resource access → 404** (not 403): do not reveal existence of resources belonging to other accounts.
  - **Frontend routing → react-router-dom**: standard library, supports Phase 12–14 multi-page needs. State-based routing rejected as too limiting.
  - **Token storage → localStorage**: sufficient for MVP. httpOnly cookie deferred — requires backend Set-Cookie support. Risk noted; upgrade task added to deferred backlog.
  - **401 handling → immediate logout** (no silent refresh): simple for MVP. Silent refresh via `/api/auth/refresh` deferred to a future hardening task.
  - **Onboarding gate route → `/onboarding`**: Phase 11 redirects `onboarding_completed=false` here; Phase 12 builds the UI at this path.
- Why: Chosen to minimize implementation complexity for MVP while keeping upgrade paths explicit in the deferred backlog. Each decision has a noted follow-up task.
- Plan: [plans/phase_10_11.md](plans/phase_10_11.md)

### 2026-06-07 - Big Update: Account, Onboarding & Rank Boss System Architecture

- Status: `Accepted`
- Decision:
  - **Account/Auth layer**: Add `accounts`, `account_sessions`, `account_tokens`, `account_security_events`, and `account_preferences` tables above `players` table.
  - **Profile mapping**: 1 account = 1 player = 1 active campaign for MVP, preserving a 1-to-many player-to-campaign model structure for future scalability.
  - **Onboarding flow**: A mandatory step right after registration. Users must complete manual certificate score entry (or skip it, initializing all skill ranks to `F`) and campaign template activation before accessing the dashboard. No internal placement test is implemented in MVP.
  - **Manual certificate entry**: Allows users to input IELTS scores which directly generate skill rank suggestions. Applying these suggestions directly updates the skill's `confirmed_rank` without requiring a Rank Boss exam.
  - **XP-based Rank Promotion**: Triggered when skill XP crosses a rank threshold. It changes `promotion_status` to `boss_required` and sets `pending_rank` to the next rank (only 1 rank jump at a time). To confirm the rank, the user must pass the unlocked Rank Boss Exam (objective questions: Vocabulary, Reading, Listening, Grammar, Collocation) with >= 80% score.
  - **Retry & Time limits**: Rank Boss exams are capped at 2 attempts per day per skill rank transition, with a default 30-minute limit.
  - **Subjective Rank Bosses**: Writing and Speaking Rank Bosses are deferred as out of scope due to subjective grading requirements and are placed in the backlog.
  - **Skill Quota Daily Quests**: Daily quests are generated from template skill quotas (e.g., Vocabulary = 3, Reading = 1) using specific slot codes (e.g., `vocabulary_flashcard`, `reading_scan`), rather than generic roles.
- Why: Minimizes manual setup complexity, establishes a secure multi-user identity layer, maintains a game-like XP/boss progression loop, and ensures future extensibility of the campaign models.

### 2026-06-07 - Skill-Specific Quest XP Routing and Quest Extension

- Status: `Accepted`
- Decision: Use the existing generic Quest system for Vocabulary Daily Quests instead of creating a separate database table. Extend the `Quest`, `QuestTemplate`, and `WeeklyMission` models with track, activity, and target skill fields, and route rewards using separate transaction tables (`skill_xp_transactions` and `player_xp_transactions`).
- Why: Reusing the existing quest system minimizes architectural duplication and database complexity, while transaction-based routing cleanly separates daily skill practice gains from global player milestone progression and ensures reward claim idempotency.

### 2026-06-06 - Map user_id to player_id for Vocabulary Support Skill

- Status: `Accepted`
- Decision: Map `user_id` from vocabulary specifications to `player_id` (foreign key to `players.id`) instead of `campaign_id`.
- Why: Vocabulary represents lifelong study assets that persist across campaigns, whereas skills/badges are campaign-scoped.

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
