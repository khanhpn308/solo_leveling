# IELTS Quest Dashboard Tasks

## Session Resume State

Last updated: 2026-06-06

## Current Project State

- The frontend home dashboard redesign is complete, reviewer-accepted, and frontend-only.
- Phase 1 UX smoothing for the daily loop is now implemented on the frontend, including the weekly touchpoint polish slice.
- Reward claim flow is now implemented across backend and frontend for main quests, daily quests, and weekly missions.
- No Docker Compose changes were required for these slices.
- The new home shell now includes:
  - compact top bar with level/rank, avatar status modal trigger, suggestion inbox dropdown, and host date/time
  - roadmap phase hero with overall roadmap start/end
  - bottom stat cards
  - burger navigation with Quest submenu, Certificate, and Boss
  - quest overlay with Main / Daily / Weekly / Archive tabs
  - certificate overlay wired to the existing test-records API
  - boss overlay with current boss first
  - avatar picker placeholder only
  - real suggestion inbox actions via existing backend suggestion endpoints
  - weekly mission touchpoint polish with clickable weekly support surface, normalized mission progress/state feedback, and weekly progress pulse/toast updates
  - reward-claim loop with burger-button red dot, per-mission `CLAIM` buttons, backend claim state for quest/weekly rewards, and XP banking only after claim
- Validation recorded for the completed redesign:
  - `python -m py_compile backend/app/*.py backend/alembic/versions/20260605_04_reward_claim_flow.py`: passed
  - `npm.cmd run build`: passed
  - `npm.cmd run test:dashboard-data`: passed
  - `5 tests, 0 failures`
- Validation recorded for the original redesign slice:
  - `npm.cmd run build`: passed
  - `npm.cmd run test:dashboard-data`: passed
  - `5 tests, 0 failures`
  - `reviewer-gpt55`: `ACCEPT`
- No browser screenshot or visual walkthrough was captured.

## Completed

- Replaced the home dashboard with a compact game-status style shell inspired by the Solo Leveling direction in the repo brief.
- Added the top bar cluster for level/rank, avatar status, suggestion inbox, and host time.
- Added roadmap phase hero treatment with roadmap start/end context.
- Added bottom stat cards for quick study-state visibility.
- Added burger navigation with a Quest submenu plus Certificate and Boss entry points.
- Added quest overlay tabs for Main, Daily, Weekly, and Archive.
- Added weekly mission touchpoint polish so the weekly support panel opens the Weekly tab and the weekly card shows normalized progress, state, and reward feedback.
- Added reward-claim gating so quest and weekly XP are only banked after explicit `CLAIM` actions.
- Added burger-button notification dot for pending unclaimed rewards across main, daily, and weekly surfaces.
- Added backend migration and API support for quest and weekly reward claims.
- Wired the certificate overlay to the existing test-records API.
- Added a boss overlay that surfaces the current boss first.
- Kept the avatar picker as placeholder-only UI.
- Kept the redesign aligned with the existing backend and data model.

## In Progress

- Browser visual walkthrough / screenshot verification remains pending.
- Follow-up documentation task remains open: add a status-semantics note for the database schema if we want the meaning of `status`, `quest_role`, `scope`, and similar enum-like fields written down separately from the raw schema snapshot.
- Wave D still has 2 explicit follow-up items left:
  - add typed-source writes for future weakness-suggestion generators if those code paths are introduced
  - add automated backend tests for Wave D behavior

## Database Migration Plan Tracker

Last updated: 2026-06-05

Purpose:
- Track the approved migration sequence for low-risk database hardening around campaign scope, typed tracker links, and future-safe skill/badge state.

Status legend:
- `Done` = already implemented
- `Not done` = planned but not implemented yet

### Chosen migration direction

- `Done` Review current schema snapshot in `docs/DATABASE_SCHEMA.md` and compare it against `backend/app/models.py`.
- `Done` Choose additive migration strategy instead of rewriting current `skills` / `badges` semantics in place.
- `Done` Choose typed nullable FK columns for tracker/source links instead of relying only on `tracker_type + tracker_entry_id` and `source_type + source_ref_id`.
- `Done` Get final user approval for the migration plan before editing schema/code.

### Wave A - Add nullable scope and typed-link columns

#### Wave A.0 - Prep and safety checks

- `Done` Confirm the new migration revision name and `down_revision` from the latest Alembic head.
- `Done` Reuse the repo's additive migration style: `ensure_column()`, `ensure_index()`, and inspector-based existence checks.
- `Done` Keep every new column nullable in Wave A to avoid blocking upgrade on existing rows.
- `Done` Do not drop, rename, or repurpose any existing column in Wave A.

#### Wave A.1 - Add campaign-scope columns

- `Done` Add `checkins.campaign_id int null fk campaigns.id`.
- `Done` Add `test_records.campaign_id int null fk campaigns.id`.
- `Done` Add `skill_rank_suggestions.campaign_id int null fk campaigns.id`.
- `Done` Add `skill_rank_history.campaign_id int null fk campaigns.id`.
- `Done` Add `weakness_suggestions.campaign_id int null fk campaigns.id`.
- `Done` Create indexes:
  - `ix_checkins_campaign_id`
  - `ix_test_records_campaign_id`
  - `ix_skill_rank_suggestions_campaign_id`
  - `ix_skill_rank_history_campaign_id`
  - `ix_weakness_suggestions_campaign_id`

#### Wave A.2 - Add quest daily-slot and typed tracker link columns

- `Done` Add `quests.daily_slot_code varchar(20) null`.
- `Done` Add `quests.error_log_id int null fk error_logs.id`.
- `Done` Add `quests.writing_entry_id int null fk writing_entries.id`.
- `Done` Add `quests.speaking_entry_id int null fk speaking_entries.id`.
- `Done` Add `quests.mock_test_id int null fk mock_tests.id`.
- `Done` Create indexes:
  - `ix_quests_daily_slot_code`
  - `ix_quests_error_log_id`
  - `ix_quests_writing_entry_id`
  - `ix_quests_speaking_entry_id`
  - `ix_quests_mock_test_id`

#### Wave A.3 - Add weakness suggestion typed source link columns

- `Done` Add `weakness_suggestions.source_test_record_id int null fk test_records.id`.
- `Done` Add `weakness_suggestions.source_mock_test_id int null fk mock_tests.id`.
- `Done` Add `weakness_suggestions.source_error_log_id int null fk error_logs.id`.
- `Done` Add `weakness_suggestions.source_quest_id int null fk quests.id`.
- `Done` Create indexes:
  - `ix_weakness_suggestions_source_test_record_id`
  - `ix_weakness_suggestions_source_mock_test_id`
  - `ix_weakness_suggestions_source_error_log_id`
  - `ix_weakness_suggestions_source_quest_id`

#### Wave A.4 - Backfill only the low-risk values inside Wave A

- `Done` Backfill `quests.daily_slot_code = quest_role` where `session_type = 'Daily Quest'` and `quest_role in ('core', 'support', 'mini')`.
- `Done` Backfill typed quest tracker FK columns from `tracker_type + tracker_entry_id` only for exact known mappings:
  - `error_log -> error_log_id`
  - `writing_entry -> writing_entry_id`
  - `speaking_entry -> speaking_entry_id`
  - `mock_test -> mock_test_id`
- `Done` Backfill typed weakness source FK columns from `source_type + source_ref_id` only for exact known mappings:
  - `test_record -> source_test_record_id`
  - `mock_test -> source_mock_test_id`
  - `error_log -> source_error_log_id`
- `Done` Leave ambiguous rows untouched instead of guessing.
- `Done` Do not backfill `campaign_id` fields in Wave A migration; keep that work in Wave C.

#### Wave A.5 - ORM / schema preparation required when implementation starts

- `Done` Add new nullable fields to SQLAlchemy models:
  - `CheckIn.campaign_id`
  - `TestRecord.campaign_id`
  - `SkillRankSuggestion.campaign_id`
  - `SkillRankHistory.campaign_id`
  - `WeaknessSuggestion.campaign_id`
  - `Quest.daily_slot_code`
  - `Quest.error_log_id`
  - `Quest.writing_entry_id`
  - `Quest.speaking_entry_id`
  - `Quest.mock_test_id`
  - `WeaknessSuggestion.source_test_record_id`
  - `WeaknessSuggestion.source_mock_test_id`
  - `WeaknessSuggestion.source_error_log_id`
  - `WeaknessSuggestion.source_quest_id`
- `Done` Expose only the fields needed for safe runtime compatibility in Pydantic schemas; do not remove legacy fields in this wave.
- `Done` Keep service logic behavior compatible while adding the new fields and dev-reset FK safety updates.

#### Wave A.6 - Validation checklist for implementation

- `Done` Run `python -m py_compile` for backend app files plus the new Alembic revision.
- `Done` Run Alembic upgrade on the current local DB and verify it reaches `head` with the host-side MySQL URL override.
- `Done` Verify no existing API breaks due to added nullable fields.
- `Done` Spot-check with SQL or API data that:
  - new columns exist
  - exact tracker/source mappings were copied where expected
  - ambiguous legacy rows remain null rather than incorrectly mapped
- `Done` Record the implementation result in `TEST_REPORT.md` and `changelogs.md`.

### Wave B - Add new additive state tables

#### Wave B.0 - Freeze Wave B scope

- `Done` Keep `skills` as the current definition + global state table in this wave.
- `Done` Keep `badges` as the current definition + global unlock-state table in this wave.
- `Done` Do not change public API payloads for `/api/skills` or `/api/badges` in this wave.
- `Done` Do not backfill any row into the new tables in this wave.
- `Done` Do not cut service read/write logic over to the new tables in this wave.

#### Wave B.1 - Add `campaign_skill_states`

- `Done` Create table `campaign_skill_states` with columns:
  - `id`
  - `campaign_id`
  - `skill_id`
  - `xp`
  - `rank`
  - `confirmed_rank`
  - `level`
  - `streak`
  - `last_practiced`
  - `weak_point`
  - `user_weakness_note`
  - `last_system_suggestion_at`
  - `created_at`
  - `updated_at`
- `Done` Add foreign key `campaign_skill_states.campaign_id -> campaigns.id`.
- `Done` Add foreign key `campaign_skill_states.skill_id -> skills.id`.
- `Done` Add unique key `(campaign_id, skill_id)` named `uq_campaign_skill_states_campaign_skill`.
- `Done` Add index `(campaign_id, confirmed_rank)` for campaign-scoped rank filtering.
- `Done` Add index on `skill_id` for reverse lookups from a skill definition.
- `Done` Add SQLAlchemy model `CampaignSkillState`.
- `Done` Add relationships:
  - `Campaign.skill_states`
  - `Skill.campaign_states`
  - `CampaignSkillState.campaign`
  - `CampaignSkillState.skill`

#### Wave B.2 - Add `badge_unlocks`

- `Done` Create table `badge_unlocks` with columns:
  - `id`
  - `player_id`
  - `campaign_id`
  - `badge_id`
  - `source_boss_battle_id`
  - `unlocked_at`
- `Done` Add foreign key `badge_unlocks.player_id -> players.id`.
- `Done` Add foreign key `badge_unlocks.campaign_id -> campaigns.id`.
- `Done` Add foreign key `badge_unlocks.badge_id -> badges.id`.
- `Done` Add foreign key `badge_unlocks.source_boss_battle_id -> boss_battles.id`.
- `Done` Add unique key `(campaign_id, badge_id)` named `uq_badge_unlocks_campaign_badge`.
- `Done` Add index on `player_id`.
- `Done` Add index on `badge_id`.
- `Done` Add index on `source_boss_battle_id`.
- `Done` Add SQLAlchemy model `BadgeUnlock`.
- `Done` Add relationships:
  - `Player.badge_unlocks`
  - `Campaign.badge_unlocks`
  - `Badge.unlocks`
  - `BadgeUnlock.player`
  - `BadgeUnlock.campaign`
  - `BadgeUnlock.badge`
- `Done` Optionally add:
  - `BossBattle.badge_unlocks`
  - `BadgeUnlock.source_boss_battle`

#### Wave B.3 - Write the Alembic revision

- `Done` Create a new Alembic revision after `20260605_05`.
- `Done` Create `campaign_skill_states` in the migration.
- `Done` Create `badge_unlocks` in the migration.
- `Done` Create all named unique constraints and supporting indexes in the migration.
- `Done` Do not add any `INSERT`, `UPDATE`, or backfill SQL to this revision.
- `Done` Implement a real `downgrade()` that drops the new tables in reverse dependency order.

#### Wave B.4 - Backend compatibility touchpoints

- `Done` Register the two new SQLAlchemy models in `backend/app/models.py`.
- `Done` Keep `schemas.py` unchanged in this wave.
- `Done` Keep `services.py` skill/badge recompute logic unchanged in this wave.
- `Done` Keep `seed.py` unchanged with respect to populating the new tables in this wave.
- `Done` Update `/api/dev/reset` delete order so `badge_unlocks` and `campaign_skill_states` are deleted before parent tables.
- `Done` Translate remaining backend user-facing Vietnamese seed/business strings to English, including backend seed-fed source data such as `material.md`, while keeping legacy description-matching logic compatible for already-seeded rows.

#### Wave B.5 - Validation checklist for implementation

- `Done` Run `python -m py_compile` for touched backend files and the new Alembic revision.
- `Done` Run Alembic upgrade on an empty or resettable DB and confirm the revision reaches `head`.
- `Done` Run Alembic upgrade on the current local DB and confirm both new tables are created.
- `Done` Verify via `information_schema` or SQL inspection that:
  - both new tables exist
  - expected foreign keys exist
  - expected unique constraints exist
  - expected indexes exist
- `Done` Verify both new tables are still empty immediately after Wave B migration.
- `Done` Verify `/api/skills` response shape is unchanged.
- `Done` Verify `/api/badges` response shape is unchanged.
- `Done` Verify `/api/dev/reset` no longer fails because of the new child tables.
- `Done` Verify newly seeded roadmap, quest, mission, badge, and study-material text is English-only after reset.

#### Wave B.6 - Tracking and documentation after coding

- `Done` Update `TASKS.md` statuses for each `Wave B.*` item after implementation.
- `Done` Record the implementation summary in `AGENT_NOTES.md`.
- `Done` Record the validation result in `TEST_REPORT.md`.
- `Done` Add a full Wave B entry to `changelogs.md`.

### Wave C - Backfill existing data

#### Wave C.0 - Data-only migration guardrails

- `Done` Create a new data-only Alembic revision after `20260605_06`: `20260605_07_wave_c_backfill_existing_state.py`.
- `Done` Keep Wave C schema-neutral:
  - no new columns
  - no new tables
  - no new constraints
- `Done` Keep Wave C idempotent by:
  - only filling nullable target fields
  - only inserting missing rows into additive tables
  - never overwriting already-populated typed link fields

#### Wave C.1 - Backfill existing daily-slot and typed-link columns

- `Done` Backfill `quests.daily_slot_code = quest_role` for all daily quest rows with `quest_role in ('core', 'support', 'mini')`.
- `Done` Backfill quest typed tracker FK columns from `tracker_type + tracker_entry_id` only when:
  - the typed FK is still null
  - the referenced row actually exists
- `Done` Backfill weakness typed source FK columns from `source_type + source_ref_id` only when:
  - the typed FK is still null
  - the referenced row actually exists
- `Done` Leave ambiguous or non-existent legacy typed-link mappings untouched.

#### Wave C.2 - Backfill campaign scope on existing rows

- `Done` Backfill `checkins.campaign_id` by campaign date windows where a unique campaign match exists.
- `Done` Backfill `test_records.campaign_id` by:
  - player + test date window first
  - player's sole campaign fallback second
- `Done` Backfill `skill_rank_suggestions.campaign_id` from linked `test_records`.
- `Done` Backfill `skill_rank_history.campaign_id` from linked `test_records`.
- `Done` Backfill `weakness_suggestions.campaign_id` from linked evidence in priority order:
  - `test_records`
  - `mock_tests`
  - `error_logs`
  - `quests`
  - single active campaign fallback for `last_practiced` / `quest_pattern`

#### Wave C.3 - Seed additive campaign-scoped state tables

- `Done` Seed `campaign_skill_states` from the active campaign and current global `skills` state.
- `Done` Insert only missing `(campaign_id, skill_id)` rows into `campaign_skill_states`.
- `Done` Seed `badge_unlocks` from:
  - cleared `boss_battles` first
  - existing unlocked badge state second
- `Done` Keep `badge_unlocks` insert-only and non-destructive when no qualifying rows exist.

#### Wave C.4 - Validation and acceptance

- `Done` Run `python -m py_compile` for the new Wave C Alembic revision.
- `Done` Run Alembic upgrade on the current local DB and confirm revision `20260605_07` reaches `head`.
- `Done` Verify post-backfill DB facts:
  - `test_records.campaign_id` no longer null on current seeded rows
  - `skill_rank_suggestions.campaign_id` no longer null on current seeded rows
  - seeded daily quests now have `daily_slot_code`
  - `campaign_skill_states` now contains one row per current skill for the active campaign
  - `badge_unlocks` remains empty on the current DB because no source rows qualify yet
- `Done` Verify read-only API smoke checks:
  - `/api/test-records`
  - `/api/rank-suggestions`
  - `/api/quests/today`
  - `/api/weekly-mission/current`
- `Done` Current local unresolved-row audit after Wave C:
  - `checkins.campaign_id`: `0` null rows
  - `test_records.campaign_id`: `0` null rows
  - `skill_rank_suggestions.campaign_id`: `0` null rows
  - `skill_rank_history.campaign_id`: `0` null rows
  - `weakness_suggestions.campaign_id`: `0` null rows
  - daily quest `daily_slot_code`: `0` null rows

#### Wave C.5 - Tracking after coding

- `Done` Update `TASKS.md` Wave C status to reflect the implemented backfill migration and local validation.
- `Done` Add a Wave C implementation entry to `changelogs.md`.

### Wave D - Application cutover

#### Wave D.0 - Cutover guardrails

- `Done` Keep Wave D schema-neutral:
  - no new DB columns
  - no new DB tables
  - no new constraints
- `Done` Keep public response shapes unchanged for:
  - `SkillOut`
  - `BadgeOut`
  - `SummaryOut`
  - `QuestOut`
  - `CheckInOut`
  - `SkillRankSuggestionOut`
  - `WeaknessSuggestionOut`
- `Done` Treat `campaign_skill_states` as the source of truth for campaign skill progression.
- `Done` Treat `badge_unlocks` as the source of truth for campaign badge ownership.
- `Done` Treat global state columns on `skills` and `badges` as legacy compatibility fields only.
- `Done` Preserve the current badge rule thresholds/criteria; do not redesign badge rules in Wave D.

#### Wave D.1 - Skill state read/write cutover

- `Done` Add a backend helper that guarantees one `campaign_skill_states` row exists for every `(active_campaign_id, skill_id)` pair before recompute/read operations.
- `Done` Add a serializer/helper that builds `SkillOut` from:
  - static skill definition fields from `Skill`
  - mutable campaign-scoped state from `CampaignSkillState`
- `Done` Change `/api/skills` to return serialized campaign-scoped skill state instead of raw `Skill` ORM rows.
- `Done` Change `/api/summary` to use the same serialized campaign-scoped skill list for `skills`.
- `Done` Rewrite campaign skill recompute so it updates `CampaignSkillState`, not global `Skill`.
- `Done` Scope skill XP recompute to:
  - `Quest.campaign_id == active_campaign.id`
  - `Quest.skill_id == skill.id`
  - `Quest.completed == true`
  - `Quest.reward_claimed == true`
- `Done` Update campaign-scoped skill fields during recompute:
  - `xp`
  - `rank`
  - `level`
  - `last_practiced`
- `Done` Leave `CampaignSkillState.streak` behavior unchanged in Wave D.
- `Done` Rewrite `create_rank_suggestions_for_test()` so `current_rank` comes from the active campaign’s `CampaignSkillState.confirmed_rank`.
- `Done` Rewrite `apply_rank_suggestion()` so it updates `CampaignSkillState.confirmed_rank`.
- `Done` Keep `SkillRankHistory` creation in place and record campaign-scoped old/new rank values.
- `Done` Rewrite weakness-note mutation helpers so they append into `CampaignSkillState.user_weakness_note`.
- `Done` Rewrite weakness-suggestion generation bookkeeping so it updates `CampaignSkillState.last_system_suggestion_at`.
- `Done` Rewrite inactivity checks in weakness-suggestion generation so they read `CampaignSkillState.last_practiced`.
- `Done` Ensure pending weakness-suggestion counting is campaign-scoped.

#### Wave D.2 - Badge read/write cutover

- `Done` Add a backend helper that builds `BadgeOut` from:
  - static badge definition fields from `Badge`
  - unlock state from `BadgeUnlock` for the active campaign
- `Done` Change `/api/badges` to return campaign-scoped badge unlock state via `badge_unlocks + badges`.
- `Done` Change `/api/summary` to use the same serialized badge list for `badges`.
- `Done` Rewrite `recompute_badges()` so it evaluates unlock criteria against the active campaign only:
  - campaign-scoped skill XP from `campaign_skill_states`
  - campaign-scoped completed quest counts
- `Done` When a badge becomes unlocked for the active campaign, create or keep exactly one `BadgeUnlock` row for `(campaign_id, badge_id)`.
- `Done` Keep `BadgeUnlock.unlocked_at` stable once the row exists.
- `Done` Do not rely on `Badge.unlocked` / `Badge.unlocked_at` for reads after Wave D.
- `Done` Do not delete or mutate historical `badge_unlocks` rows from other campaigns during recompute.

#### Wave D.3 - Endpoint scope and compatibility cutover

- `Done` Change `/api/checkins` GET to return active-campaign check-ins only.
- `Done` Keep `/api/checkins` POST backward-compatible, but make upsert resolution campaign-aware:
  - first try `(campaign_id == active_campaign.id, checkin_date == payload.checkin_date)`
  - if not found, fall back to any existing same-date row only to preserve pre-Wave-E uniqueness compatibility
  - if that fallback row belongs to another campaign, return `409` instead of silently reassigning it
- `Done` Change `/api/rank-suggestions` GET to return only suggestions for the active campaign.
- `Done` Change `/api/weakness-suggestions` GET to return only suggestions for the active campaign.
- `Done` Ensure rank-suggestion apply/dismiss endpoints reject suggestions outside the active campaign.
- `Done` Ensure weakness-suggestion apply/dismiss endpoints reject suggestions outside the active campaign.
- `Done` Keep `/api/test-records` GET player-wide by design for history views.
- `Done` Keep `/api/test-records` POST writing into the active campaign.

#### Wave D.4 - Quest completion typed-link write cutover

- `Done` Add an optional request body for `/api/quests/{quest_id}/complete` so typed tracker IDs can be written during completion without breaking the current frontend.
- `Done` Keep the endpoint backward-compatible:
  - current no-body `POST` still works
  - new body fields are optional
- `Done` Introduce a `QuestCompletionIn` payload with optional fields:
  - `tracker_type`
  - `tracker_entry_id`
  - `error_log_id`
  - `writing_entry_id`
  - `speaking_entry_id`
  - `mock_test_id`
  - `raw_score`
  - `completion_note`
- `Done` Enforce that at most one typed tracker FK can be provided in a single completion request.
- `Done` If a typed tracker FK is provided, dual-write both:
  - typed FK column
  - legacy `tracker_type + tracker_entry_id`
- `Done` Use canonical typed-to-legacy mappings for:
  - `error_log_id`
  - `writing_entry_id`
  - `speaking_entry_id`
  - `mock_test_id`
- `Done` If only legacy `tracker_type + tracker_entry_id` is provided, fill the typed FK too when the referenced row exists.
- `Done` Keep `raw_score` and `completion_note` behavior unchanged.
- `Done` On `uncomplete`, clear both:
  - legacy tracker fields
  - typed tracker FK fields
- `Done` Keep `QuestOut` response shape unchanged.

#### Wave D.5 - Weakness suggestion typed-source write cutover

- `Done` Keep `WeaknessSuggestionOut` shape unchanged.
- `Done` Update current backend weakness-suggestion creation paths so they prefer writing typed source FK fields at creation time.
- `Done` Preserve legacy `source_type + source_ref_id` semantics during transition for new weakness suggestions.
- `Done` Current implemented write rules:
  - repeated error suggestions -> write `source_error_log_id`
  - quest-pattern suggestions -> write `source_quest_id` when a concrete quest row exists
  - `last_practiced` suggestions -> keep typed source FKs null
- `Not done` Add typed-source writes for any future weakness-suggestion creation paths that do not exist yet in the current backend (for example dedicated test-record-driven or mock-test-driven weakness generators).

#### Wave D.6 - Refresh loop and summary consistency

- `Done` Keep `refresh_progress_state()` as the single high-level recompute entrypoint.
- `Done` Update `refresh_progress_state()` order so it:
  - resolves active player/campaign
  - ensures campaign skill state rows exist
  - syncs quest statuses
  - recomputes weekly missions with campaign-scoped check-ins
  - recomputes campaign skill progress
  - recomputes campaign badge unlocks
  - recomputes player progress
  - commits once at the end
- `Done` Update `recompute_weekly_missions()` so check-ins are filtered by active campaign instead of all `CheckIn` rows globally.
- `Done` Update `recompute_player_progress()` so `checkin_dates` are filtered by active campaign instead of all `CheckIn` rows globally.
- `Done` Keep quest XP, weekly mission XP, and boss XP campaign-scoped.
- `Done` Keep `SummaryOut.player` shape unchanged.

#### Wave D.7 - Validation and acceptance

- `Done` Run `python -m py_compile` for touched backend files.
- `Done` Run live API smoke checks for:
  - `/api/skills`
  - `/api/badges`
  - `/api/summary`
  - `/api/rank-suggestions`
  - `/api/weakness-suggestions`
  - `/api/checkins`
  - `/api/test-records`
  - `/api/quests/today`
- `Done` Verify `POST /api/quests/{id}/complete` still works with no request body.
- `Done` Verify typed tracker dual-write by completing a quest with `error_log_id` and confirming:
  - `tracker_type = 'error_log'`
  - `tracker_entry_id` is populated
  - `error_log_id` is populated
- `Done` Verify `POST /api/quests/{id}/uncomplete` clears both typed and legacy tracker fields.
- `Done` Verify multiple typed tracker IDs in one completion request return `400`.
- `Done` Verify `/api/skills` and `/api/summary.skills` read campaign-scoped state instead of global `skills` fields by forcing a temporary mismatch and confirming the API returns `CampaignSkillState` values.
- `Done` Verify `/api/badges` reads `badge_unlocks` instead of global `badges.unlocked` by forcing a temporary mismatch and confirming the API returns `BadgeUnlock` state.
- `Not done` Add an automated backend test suite for Wave D behavior; validation is manual smoke coverage only in this slice.

### Wave E - Enforce stronger constraints after cutover

#### Wave E.0 - Guardrails and chosen scope

- `Done` Keep Wave E focused on backend + database hardening after the Wave D cutover; do not remove legacy fields in this wave.
- `Done` Treat Wave E as both:
  - a migration/DDL wave
  - a minimal backend-guard wave needed to keep new constraints safe
- `Done` Keep API response shapes unchanged in Wave E.
- `Done` Use fail-fast migration checks for unresolved rows or duplicate future keys; do not auto-resolve ambiguous data during Wave E.
- `Done` Expand Wave E scope slightly beyond the old stub by also hardening:
  - `quests.campaign_id` to `NOT NULL`
  - daily quest creation/update paths so `daily_slot_code` is always populated
  - `/api/checkins` upsert logic so it no longer depends on the pre-Wave-E global same-date fallback

#### Wave E.1 - Backend write-path hardening before DDL

- `Done` Change SQLAlchemy model nullability to match the post-Wave-E target for:
  - `CheckIn.campaign_id`
  - `TestRecord.campaign_id`
  - `SkillRankSuggestion.campaign_id`
  - `SkillRankHistory.campaign_id`
  - `WeaknessSuggestion.campaign_id`
  - `Quest.campaign_id`
- `Done` Keep `Quest.daily_slot_code` nullable at the SQLAlchemy field level, but enforce the runtime invariant that every generated daily quest with role `core` / `support` / `mini` always sets `daily_slot_code`.
- `Done` Update `/api/checkins` POST so upsert resolution becomes strictly `(campaign_id, checkin_date)` based.
- `Done` Remove the old fallback that queried any row by `checkin_date` globally to preserve the pre-Wave-E unique behavior.
- `Done` Keep `/api/checkins` GET campaign-scoped exactly as in Wave D.

#### Wave E.2 - Seed/reset hardening for constraint safety

- `Done` Update daily quest seed/create paths so newly created daily quests always write `daily_slot_code = quest_role`.
- `Done` Update the daily-quest "existing row refresh" path in `seed.py` so old rows also get `daily_slot_code` synchronized when they are touched during reset/seed.
- `Done` Confirm no quest creation path in the current backend can create a daily quest with:
  - `campaign_id = null`
  - `daily_slot_code = null` when `quest_role in ('core', 'support', 'mini')`
- `Done` Keep main quests unchanged; they should continue to have `daily_slot_code = null`.
- `Done` Re-run `/api/dev/reset` during validation because reset/seed must keep passing after the stricter constraints land.

#### Wave E.3 - Alembic preflight and fail-fast checks

- `Done` Create a new Alembic revision after `20260605_07` for Wave E hardening.
- `Done` Add explicit preflight checks in the migration that abort with clear errors if any of these still exist:
  - `checkins.campaign_id is null`
  - `test_records.campaign_id is null`
  - `skill_rank_suggestions.campaign_id is null`
  - `skill_rank_history.campaign_id is null`
  - `weakness_suggestions.campaign_id is null`
  - `quests.campaign_id is null`
  - daily quest rows with `daily_slot_code is null`
- `Done` Add explicit duplicate checks that abort if any future unique key would fail:
  - duplicate `(campaign_id, checkin_date)` in `checkins`
  - duplicate `(campaign_id, quest_date, daily_slot_code)` among daily quests
- `Done` Keep preflight checks read-only except for a narrow safe sync of `daily_slot_code` before the final alter statements.
- `Done` Do not introduce new broad data backfill logic in Wave E; campaign backfills belong to Wave C and are already done.

#### Wave E.4 - Constraint and nullability enforcement

- `Done` Make `checkins.campaign_id` non-null.
- `Done` Make `test_records.campaign_id` non-null.
- `Done` Make `skill_rank_suggestions.campaign_id` non-null.
- `Done` Make `skill_rank_history.campaign_id` non-null.
- `Done` Make `weakness_suggestions.campaign_id` non-null.
- `Done` Make `quests.campaign_id` non-null.
- `Done` Replace unique `uq_checkin_date` with unique `(campaign_id, checkin_date)`, using a named new constraint such as `uq_checkins_campaign_date`.
- `Done` Add unique `(campaign_id, quest_date, daily_slot_code)` on `quests` for daily-slot protection, using a named constraint such as `uq_quests_campaign_date_daily_slot`.
- `Done` Keep `daily_slot_code` nullable for non-daily quests so main quests remain unaffected by the new unique key.

#### Wave E.5 - Downgrade and rollback expectations

- `Done` Implement a real downgrade for Wave E that:
  - drops the new check-in composite unique
  - drops the new daily-slot unique on `quests`
  - restores `uq_checkin_date`
  - changes the newly hardened `campaign_id` columns back to nullable
- `Done` Keep downgrade schema-only; do not attempt to reverse data changes such as `daily_slot_code` syncs.
- `Done` Document clearly that downgrade is for schema rollback only and does not restore pre-Wave-E write behavior in application code.

#### Wave E.6 - Validation and acceptance

- `Done` Run `python -m py_compile` for all touched backend files plus the new Wave E Alembic revision.
- `Done` Run `/api/dev/reset` before applying the Wave E migration to confirm seed logic no longer creates rows that would violate the new constraints.
- `Done` Run Alembic upgrade on the current local DB and confirm the new revision reaches `head`.
- `Done` Verify with SQL or `SHOW CREATE TABLE` that:
  - target `campaign_id` columns are now `NOT NULL`
  - `uq_checkin_date` is gone
  - the new `(campaign_id, checkin_date)` unique exists
  - the new `(campaign_id, quest_date, daily_slot_code)` unique exists
- `Done` Re-run unresolved-row/duplicate audits after migration and confirm all counts are `0`.
- `Done` Run backend smoke checks for:
  - `/api/checkins` GET
  - `/api/checkins` POST create/update
  - `/api/summary`
  - `/api/weekly-mission/current`
  - `/api/quests/today`
  - `/api/dev/reset`
- `Done` Confirm reset-generated daily quests still seed correctly and all have non-null `daily_slot_code` when applicable.
- `Done` Confirm `/api/checkins` no longer depends on global same-date fallback behavior and still works correctly for the active campaign.

#### Wave E.7 - Tracking after coding

- `Done` Update `TASKS.md` statuses for every `Wave E.*` item after implementation.
- `Done` Add a Wave E implementation summary to `AGENT_NOTES.md`.
- `Done` Record SQL audits, migration result, and API smoke results in `TEST_REPORT.md`.
- `Done` Add a full Wave E changelog entry to `changelogs.md`.

### Explicitly deferred

- `Not done` Drop legacy quest tracker fields `tracker_type` / `tracker_entry_id`.
- `Not done` Drop legacy weakness source fields `source_type` / `source_ref_id`.
- `Not done` Drop global state columns from `skills`.
- `Not done` Drop unlock-state columns from `badges`.
- `Not done` Add polymorphic-style check constraints that enforce exactly one typed source/tracker FK is set.

## Known Issues / Risks

- Browser automation is unavailable in this environment, so visual confirmation is still missing.
- The new reward-claim flow changes backend API/schema expectations for quests and weekly missions, so any old client assuming XP arrives on `complete` will now be stale.
- Worktree is dirty and contains unrelated frontend/backend/generated changes from prior work; do not revert user changes.

## Next Candidate Tasks

1. Capture a browser visual review of the home dashboard.
   - Confirm spacing, overlay density, and mobile/laptop responsiveness.

2. Run a browser smoke check specifically for the new reward-claim loop.
   - Verify `Complete -> Claim` on daily/main, weekly claim gating, burger dot visibility, and XP updates after claim.

3. Write a companion schema note for field semantics.
   - Document the business meaning of `status`, `quest_role`, `scope`, `rank`, and other enum-like fields separately from the raw table inventory.

4. Add automated backend tests for Wave D and Wave E.
   - Cover campaign-scoped skill/badge state, check-in upsert behavior, daily-slot invariants, and reset/migration-safe backend expectations.

## Delegation Rule For Next Coding Work

- Do not code directly without user confirmation.
- Assign one small task at a time to `coder-gpt54`.
- After `coder-gpt54` finishes, ask `reviewer-gpt55` to review the diff.
- If `reviewer-gpt55` reports P0/P1 issues, send a focused fix task back to `coder-gpt54`.
- Repeat review after the fix before moving to the next task.
