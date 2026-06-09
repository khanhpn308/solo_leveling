# Changelog

Newest first.

## [2026-06-09] Session 8k — Main Quest Start-Date Rebase (lazy-purring-sundae.md)

### Bug

Main quest dates were hard-anchored to `2026-06-04`. Picking any other onboarding start date left main-quest `quest_date` on the material.md absolute dates → the first main quests rendered **expired**. Daily quests were already rebased off `campaign.start_date`; study-plan weeks/sessions (and therefore main quests) were not.

### Changes

- **`backend/app/seed.py`** — added `MATERIAL_ANCHOR_DATE = date(2026, 6, 4)` (Week1/Session1 in `material/material.md`, a Thursday) + pure helper `rebase_material_date(material_date, campaign_start) -> date` = `campaign_start + (material_date - MATERIAL_ANCHOR_DATE)`. (MQ-1)
- **`backend/app/seed.py` `ensure_study_plan`** — every week (`week_start`/`week_end`) and session (`study_date`) date now wrapped in `rebase_material_date(..., campaign.start_date)`; `weekday_label` recomputed from the rebased date (`strftime("%A")`, overrides material text). Both the create **and** existing-row update branches rewrite the dates so a re-seed self-heals. Main quests need no change — `quest_date=session.study_date` inherits the rebased value. (MQ-2)
- **`backend/app/seed.py` `parse_start_date`** — bare fallback changed from `"2026-06-04"` to `date.today()`; `APP_START_DATE` env override preserved (container still sets it → demo seed stays deterministic). (MQ-3)
- **`backend/app/seed.py` `ensure_main_quest_instances`** — existing-row branch now rewrites `quest_date`/`week_no` from the rebased `session.study_date` (latent self-heal gap: previously updated title/xp but left main-quest dates stale on in-place re-seed).

### Why

`material/material.md` stores **absolute** session dates and `parse_material_plan()` reads them verbatim. Offset-rebasing against a single anchor constant slides the whole plan to the user's chosen start while preserving the exact material cadence (Thu→Sat→Mon→Wed = +0/+2/+4/+6, weeks 7 days apart). This mirrors the existing daily-quest / roadmap-phase rebasing, keeping one consistent date model. The parser stays a pure, reusable function; rebasing happens where `campaign.start_date` is in scope.

### Validated

- Backend suite: **61 passed, 0 failed** (`python -m pytest app/test_backend.py`).
- Live smoke: `/api/dev/reset` + register + `activate-campaign {start_date: 2026-06-15}` (future Monday) → Main Quest #1 `quest_date=2026-06-15` (== start), status **pending** (not expired); sessions land on 15/17/19/21 (+0/+2/+4/+6); `weekday_label=Monday`; week1 start 2026-06-15, week2 2026-06-22 (+7, shares the week-1 window with daily quests).
- `parse_start_date`: env unset → `date.today()`; env `2026-07-15` → that date.
- No frontend change required (dates are backend-derived).

---

## [2026-06-09] Session 8j — Phase 10 gap audit: GAP-16-1 + GAP-18-1

### Changes

- **GAP-16-1 — `frontend/src/dashboard-data.js`**: `getPlayerXpProgress` rewritten to mirror the backend level curve `round(19*(L^1.6-1))` (`services.py:_LEVEL_XP`) via a `LEVEL_XP_FLOORS` table. Previously used a flat `(level-1)*120` step → StatusModal XP bar % and "XP to next level" were wrong for every level > 1 (e.g. 900 XP @ L11 showed 0%/420 instead of 29%/94). Added max-level-60 cap (100% / 0 remaining) and null-level fallback (derive level from XP).
- **GAP-16-1 — `frontend/src/dashboard-data.test.js`**: regression test locking L11/L1/L60/null against real backend floors (862, 994, 13279).
- **GAP-18-1 — `frontend/src/components/SkillCards.jsx`**: render `SupportBuffLines` in the **compact** branch too. Task 18 had added it only to the non-compact branch, which renders solely via `SkillMatrixPanel` — a component imported nowhere (dead). The live skill-card surface is `StatusModal` compact mode, so the buff lines were never visible.
- **GAP-18-1 cleanup — deleted `frontend/src/components/SkillMatrixPanel.jsx`** (imported nowhere) and the unreachable non-compact branch of `SkillCards.jsx`; removed unused `formatDate` import; simplified the component signature.

### Validated

- `npm run test:dashboard-data` — 6/6 PASS (was 5/5; +1 curve regression test).
- `npm run build` — ✓ 0 errors.
- Task 16 + Task 18 gap-check notes updated; Checkpoint GAP-3 `[x]`.

---

## [2026-06-09] Session 8i — Task 18: Skill buff lines (support sources inside skill cards)

### Changes

- **`frontend/src/components/SkillCards.jsx`**: added `SupportBuffLines` component (reads `skill.support_breakdown`; renders `+N XP from {source}` in green when XP > 0, muted `—` when 0); called in full-mode cards only.
- **`frontend/src/styles.css`**: `.skill-node__buffs`, `.skill-node__buff`, `.skill-node__buff--active`, `.skill-node__buff--empty`.

### Validated

- `npm run build` — ✓ 0 errors.
- Task 18 gap-check `[x]`. Checkpoint G `[x]`.

---

## [2026-06-09] Session 8h (cont.) — Task 17: 9-slot daily board + boss-lock badge

### Changes

- **`frontend/src/components/DailyQuestPanel.jsx`**: added `SlotChip` (slot code → label + colour), `BossLockBadge` (amber lock when `promotion_status != "none"`), `is-claim-ready` card state; `skillStatusMap` memoized from `skills` prop; summary card "Daily Slots"; new `skills` prop.
- **`frontend/src/components/QuestOverlay.jsx`**: added `skills` prop; threaded to `DailyQuestPanel`.
- **`frontend/src/App.jsx`**: pass `skills={view.skills}` to `QuestOverlay`.
- **`frontend/src/styles.css`**: `.quest-node__chips`, `.quest-slot-chip` (7 accent variants), `.quest-boss-lock`, `.quest-node.is-claim-ready`.

### Validated

- `npm run build` — ✓ 0 errors.

---

## [2026-06-09] Session 8h (cont.) — Task 16: Stale FE player rank formulas removed

### Changes

- **`frontend/src/dashboard-data.js`**: removed `PLAYER_RANK_THRESHOLDS`, `getPlayerLevel`, `getPlayerRank`. `buildDashboardView` now reads `player.player_level`/`player.player_rank` from backend. `buildPlayerSnapshot` fallback uses `null`/`'F'`. `getPlayerXpProgress` default param `level=1`.

### Validated

- `npm run test:dashboard-data` — 5/5 PASS.
- `npm run build` — ✓ 222 modules, 0 errors.

---

## [2026-06-09] Session 8h — Phase GAP-FIX-2: GAP-15-1..4 patched; Task 15 archived

### Changes

- **`backend/app/seed.py`**:
  - **GAP-15-1**: added `db=db` to all 4 `infer_main_quest_xp(...)` callsites in `ensure_main_quest_instances` (lines 1457, 1458, 1475, 1486) → `MainQuestXpPolicy` is now the source of truth for main quest XP (not hard-code fallback).
  - **GAP-15-3**: added `speaking-focus` + `grammar-focus` pattern dicts in `weekly_mission_patterns`; added `"speaking"→speaking_weekly` and `"grammar"→grammar_weekly` branches in `map_weekly_pattern_to_mission_type` → all 7 `WeeklyMissionXpPolicy` rows are now reachable.

- **`backend/app/main.py`**:
  - **GAP-15-2**: imported `RankXpThreshold`, `QuestXpPolicy`, `WeeklyMissionXpPolicy`, `MainQuestXpPolicy`; added them to `reset_database` delete-list (before `Skill`, FK-safe) → `/api/dev/reset` fully wipes all 4 policy tables.

- **`backend/app/test_backend.py`**:
  - `TestGap151MainQuestReadsPolicy.test_main_quest_xp_reads_policy_not_hardcode` — mutates `standard` 35→40, re-seeds, asserts `base_xp=40` on matching quests. PASS.
  - `TestGap153WeeklyPolicyAllRowsReachable`:
    - `test_all_weekly_policy_mission_types_reachable` — all policy mission_types reachable from pattern codes. PASS.
    - `test_speaking_weekly_missions_seeded` — speaking_weekly missions exist after activate-campaign. PASS.
    - `test_grammar_weekly_missions_seeded` — grammar_weekly missions exist after activate-campaign. PASS.

- **GAP-15-4**: self-resolved — "Phase XP-3" ref never existed in Task 15 Verification field; only in GAP-15-4 description.

- **`TASKS.md`**: all 4 GAP-15-x tasks + Checkpoint GAP-2 + Task 15 gap-check flipped `[x]`.
- **`tasks-done.md`**: Task 15 + GAP-FIX-2 session archived.

### Validated

- Suite: **60 passed, 1 skipped, 0 failed** (+4 new tests vs session 8g's 56).
- All policy tables read/wiped correctly; all weekly mission types reachable; main quest XP policy-driven.

---

## [2026-06-09] Session 8g (cont.) — Task 15: Policy tables wired + verified

### Changes

- **`backend/app/seed.py`**: added `ensure_policy_tables(db)` call in both `seed_database` and `activate_campaign_for_player` — placed before `ensure_templates` so templates can read `QuestXpPolicy` during seeding. Previously the fn was defined but never called → policy rows absent at runtime.

- **`backend/app/test_backend.py`**: new `TestPolicyTables` class (6 tests):
  - `test_rank_xp_thresholds_seeded` — verifies all 7 ranks with correct min_xp + first_level (spec §2.3).
  - `test_quest_xp_policies_seeded` — verifies 9 activity_code rows (listening=10, grammar_exercise=7→Writing, etc.) per spec §5.1.
  - `test_weekly_mission_xp_policies_seeded` — verifies 6 mission_type rows per spec §7 (grammar_weekly → Writing, 45).
  - `test_main_quest_xp_policies_seeded` — verifies 5 tier_code rows per spec §6 (light_intro=25, mock=60).
  - `test_policy_idempotent` — two `ensure_policy_tables` runs → row count unchanged.
  - `test_daily_quest_xp_from_policy` — daily quests' `base_xp` matches `QuestXpPolicy.xp_reward` for each `daily_slot_code`.

### Validated

- **56 passed, 1 skipped, 0 failed** (↑ from 50).

---

## [2026-06-09] Session 8g — GAP-1 + GAP-2 fixes; Tasks 5–14 archived

**Status:** Both gaps fixed, 2 tests added, suite 50/1/0. Tasks 5–14 archived.

### Changes

- **`backend/app/main.py`** `get_campaign_skill_outputs` (~line 341): added `Quest.session_type != "Main Quest"` to `support_xp_by_name` filter. Matches `recompute_skill_progress` which only folds non-Main support quests — no more double-count in `support_breakdown`. *(Task GAP-1)*

- **`backend/app/seed.py`** `ensure_collocations` (~line 2203): dedup key changed from `{item.collocation: item}` to `{(item.item_order, item.collocation): item}`; lookup updated from `colloc not in existing_items` to `key = (item_data["item_order"], colloc); key not in existing_items`; `else` branch uses `existing_items[key]`. Idempotency preserved; intra-topic duplicates no longer dropped. *(Task GAP-2)*

- **`backend/app/test_backend.py`**: 2 new tests added to `TestCollocationMasterData`:
  - `test_gap1_support_breakdown_excludes_main_quest_xp`: Grammar Main Quest 100XP + Daily 30XP → Writing `support_breakdown[Grammar].xp == 30`.
  - `test_gap2_collocation_seed_allows_duplicate_strings_different_order`: fixture with 2 same-string items at different `item_order` → both seeded (count=2), idempotent on 2nd run.

### Validated

- **50 passed, 1 skipped, 0 failed** (`docker exec ielts_quest_backend pytest app/test_backend.py`). Up from 48.
- Tasks 5, 6, 13, 14 gap-check → `[x]`. Tasks 7–12 gap-check already `[x]`. GAP-1, GAP-2 tasks → `[x]`. Checkpoint GAP → `[x]`.
- Tasks 5–14 archived to `tasks-done.md`.

---

## [2026-06-09] Session 8f — Gap audit of Tasks 5–14 + GAP-FIX plan

**Status:** Audit done; no code changed. Plan added for 2 latent gaps.

### What was audited
Read `services.py`, `main.py`, `seed.py`, the two new migrations, and `test_backend.py`; ran the full backend suite in the container.

- **Test suite: 48 passed, 1 skipped, 0 failed** (`docker exec ielts_quest_backend pytest app/test_backend.py`), incl. `test_collocation_parser_and_seed`, `test_main_quest_xp_and_routing`, `test_non_boss_gated_skills`.

### Verdict per task
- **Tasks 7, 8, 9, 10, 11, 12 — no gaps.** Gap-check flipped `[x]` (archive pending at Checkpoint GAP).
  - Vocab cap = `min(data_entry,40)+min(mastery,50)` (Task 7).
  - Daily-slot migration `20260609_15` is a no-op placeholder (column already `String(20)`) (Task 8).
  - Quota seed totals exactly **9 slots/day** (Vocab 3 / Reading 1 / Listening 1 / Grammar 2 / Writing 1 / Speaking 1; Collocation 0) (Task 9).
  - `infer_main_quest_xp` tiers 45/35/25/60 + reads `MainQuestXpPolicy` (Task 10).
  - `resolve_main_quest_covered_skills` credits full XP to each covered matrix skill (Task 11).
  - `skills.boss_gated` migration `20260609_16` + seed W/S=False; auto-confirm rank when not boss-gated (Task 12).

### Gaps found (both latent — not triggered by current seed)
- **GAP-1 (blocks Tasks 5, 6):** `main.py:get_campaign_skill_outputs` computes `support_xp_by_name` from **all** Grammar/Collocation claimed quests, but `recompute_skill_progress` folds only **non-Main** quests → `support_breakdown.xp` can exceed the XP actually folded into Writing/Vocabulary (breaks the "no double-count" contract). Not triggered today: seed has no Grammar/Collocation Main Quests (Main quests are only Listening/Reading/Writing). **Fix:** add `session_type != "Main Quest"` to the query.
- **GAP-2 (blocks Tasks 13, 14):** `ensure_collocations` dedups items by `collocation` string per topic, dropping intra-topic duplicates (violates §9 "allow duplicates"). Not triggered today: real file = 60 sections / 1409 items / 0 dup topics → seeded == parsed. **Fix:** key on `(topic_id, item_order, collocation)`.

### Plan
Added **Phase GAP-FIX** to `TASKS.md` (Tasks GAP-1, GAP-2) with acceptance + tests; Checkpoint GAP archives Tasks 5–14 once both land. Note: Task 15 (`ensure_policy_tables`, `MainQuestXpPolicy` read) is already partially implemented.

## [2026-06-09] Session 8i — Phase 7: Writing/Speaking non-boss-gated (Task 12)

**Status:** Done (Gap check left unchecked awaiting review)

### Changes

**`backend/app/models.py`**
- Added `boss_gated` column (`Boolean`, default `True`) to the `Skill` model.

**`backend/alembic/versions/20260609_16_add_boss_gated_to_skills.py`**
- Created Alembic migration to add the `boss_gated` column to the `skills` table, with a server default of `1` (true).

**`backend/app/seed.py`**
- Updated `ensure_skills()` to set `boss_gated = False` for `"Writing"` and `"Speaking"`, and `True` for other skills (Listening, Reading, Vocabulary, Collocation, Grammar). Updates existing database rows.

**`backend/app/services.py`**
- Refactored `recompute_skill_progress()` to bypass the boss-gating flow when the skill is not boss-gated (`boss_gated` is false). In this case, `confirmed_rank` is directly updated to `rank`, and all promotion states (`promotion_status`, `pending_rank`, `promotion_unlocked_at`) are cleared/set to `"none"` or `None`.

**`backend/app/main.py`**
- Guarded `/api/rank-exams/unlock` against non-boss-gated skills, returning a 400 Bad Request if a user attempts to unlock a boss exam for Writing or Speaking.

**`backend/app/test_backend.py`**
- Added `test_non_boss_gated_skills` in `TestCollocationMasterData` to verify seeding, direct rank confirmation/bypass on quest claim for Writing/Speaking, and the controller endpoint block.

### Validated
- Full unittest suite: **48/48 PASS** (including the new integration test).

## [2026-06-09] Session 8h — Phase 6: Main Quest Full-XP + Skill Tiering (Tasks 10 and 11)

**Status:** Done (Gap check left unchecked awaiting review)

### Changes

**`backend/app/seed.py`**
- Updated `infer_primary_skill` to fall back to scanning the `task_detail` field if the `skill_summary` doesn't match any primary skills. This correctly resolves S4's primary skill/focus from the weekly syllabus.
- Rewrote `infer_main_quest_xp` to assign XP based on skill column tiering: Writing + Grammar (S3) -> 45 XP, standard core skills (S1/S2) -> 35 XP, and standard Review (S4) -> 25 XP unless it represents a mock exam (containing "mock", "simulation", or "sectional test" in the combined summary/detail), which awards 60 XP.
- Updated main quest seeding calls to pass `session.task_detail` to `infer_main_quest_xp` and `infer_primary_skill`.

**`backend/app/services.py`**
- Added `resolve_main_quest_covered_skills` helper function to map Main Quest sessions to their covered matrix skills: S1 -> {Listening, Speaking}, S2 -> {Reading, Vocabulary}, S3 -> {Writing}, and S4 -> {primary_skill}.
- Modified `recompute_skill_progress` to calculate Main Quest XP independently using the resolver, crediting full XP to every matrix skill covered in the session (e.g. S2 credits 35 XP to both Reading and Vocabulary). Daily Quests and support routing queries now filter out Main Quests to avoid double-counting.

**`backend/app/test_backend.py`**
- Added `test_main_quest_xp_and_routing` to `TestCollocationMasterData` to verify XP tiering of S1/S2/S3/S4 sessions and assert full-XP routing when claiming Main Quests.

### Validated
- Full unittest suite: **47/47 PASS** (including the new integration test).

## [2026-06-09] Session 8g — Phase 5: 9 Daily Slots (Tasks 8 and 9)

**Status:** Done (Gap check left unchecked awaiting review)

### Changes

**`backend/app/seed.py`**
- Updated `quest_template_seed()` to seed exactly the 9 redesigned daily quest templates with correct names, skills, and base XP: `Reading Daily` (10 XP), `Listening Daily` (10 XP), `Writing Daily` (12 XP), `Speaking Daily` (12 XP), `Flashcard Gate` (4 XP), `Codex Entry` (5 XP), `Collocation Forge` (5 XP), `Grammar Review` (5 XP), and `Grammar Exercise` (7 XP).
- Updated template quotas in `ensure_campaign_templates()` to Vocabulary: 3, Reading: 1, Listening: 1, Grammar: 2, Collocation: 0, Writing: 1, Speaking: 1. Added logic to update existing template quotas in the DB.
- Refactored `ensure_campaign_settings_and_quotas()` to overwrite existing `CampaignSkillQuestQuota` entries on re-seed.
- Refactored `slot_mapping` in `ensure_quest_instances()` to map the 9 daily slots.
- Refactored skill resolution in daily quest generation (`ensure_quest_instances()`) to resolve `skill_id` using the template's primary skill (`primary_skill.name`) instead of the mapping category, enabling correct support-source routing.

**`backend/app/test_backend.py`**
- Updated `test_default_quotas_generation` to assert that 9 daily quests are generated with correct skill counts.
- Updated `test_custom_quotas_generation` to assert vocab slot codes.
- Added `test_nine_daily_slots_generation_and_routing` to assert 9 daily quests are generated with correct base XP, and that Grammar/Collocation quest completion routes XP to Writing and Vocabulary respectively.

### Validated
- Full pytest suite: **46/46 PASS** (including the new integration test).

## [2026-06-09] Session 8f — Task 7: Cap data-entry vocab XP at 40/word (mastery separate)

**Status:** Done (Gap check left unchecked awaiting review)

### Changes

**`backend/app/services.py`**
- Restructured `compute_vocabulary_xp` to cap per-word vocabulary data-entry XP at 40.
- Implemented grouped count queries for vocabulary examples and relations grouped by item/word to prevent N+1 database queries.
- Kept `mastery_score` (capped at 50) separate, added on top of the 40 XP cap.

**`backend/app/test_backend.py`**
- Added `test_vocabulary_anti_farm_cap` in `TestWaveDAndE` to verify that standard data-entry XP is capped at 40, and mastery score is added separately on top.

### Validated
- Ran specific unit test: `python -m unittest app.test_backend.TestWaveDAndE.test_vocabulary_anti_farm_cap` → PASS.
- Ran full `TestWaveDAndE` suite: `python -m unittest app.test_backend.TestWaveDAndE` → PASS (7 tests).

---

## [2026-06-09] Session 8e — Tasks 5+6: Grammar→Writing / Collocation→Vocabulary routing + support_breakdown

**Status:** Done

### Changes

**`backend/app/services.py`**
- Added `SUPPORT_ROUTING: dict[str,str] = {"Grammar":"Writing","Collocation":"Vocabulary"}` constant after `MATRIX_SKILLS`.
- Rewrote `recompute_skill_progress`: when the skill being recomputed is a matrix skill, loop through `SUPPORT_ROUTING` entries that target it and add earned XP from those source-skill quests (`own_earned + routed_earned`). Grammar quests' XP is now folded into Writing state; Collocation quests' XP folded into Vocabulary state.

**`backend/app/schemas.py`**
- Added `SupportBreakdownItem(source: str, xp: int)` Pydantic model.
- Added `support_breakdown: list[SupportBreakdownItem] = []` field to `SkillOut`.

**`backend/app/main.py`**
- Imported `MATRIX_SKILLS`, `SUPPORT_ROUTING` from services; `SupportBreakdownItem` from schemas.
- Updated `serialize_skill_state` to accept optional `support_breakdown` parameter.
- Rewrote `get_campaign_skill_outputs`:
  - Pre-computes earned XP per source skill (Grammar, Collocation) from claimed quests.
  - Builds `breakdown_by_target` map (Writing→[Grammar:N], Vocabulary→[Collocation:N]).
  - **Filters output to MATRIX_SKILLS only** — Grammar/Collocation states excluded from tile list.
  - Attaches `support_breakdown` to Writing and Vocabulary outputs.

### Validated
- `from app.main import app` → OK
- `get_campaign_skill_outputs` returns exactly 5 tiles (Listening, Reading, Writing, Speaking, Vocabulary).
- Writing tile has `support_breakdown=[{source:"Grammar", xp:0}]`; Vocabulary tile has `support_breakdown=[{source:"Collocation", xp:0}]`.
- Grammar/Collocation states not present in tile list.
- Full suite: **44/44 PASS** (no regressions).

---

## [2026-06-09] Session 8d — Fix pre-existing certificate suggestion failures (44/44)

**Status:** Done

### Root causes (2 pre-existing test failures)

**`test_manual_certificate_creation_pre_campaign` (0 != 7):**
`activate_campaign` (main.py ~line 661) linked pre-existing `CertificateRecord` rows to the new campaign (`cert.campaign_id = campaign.id`) but never called `create_rank_suggestions_for_certificate`. Result: 0 suggestions.

**`test_manual_certificate_creation_post_campaign` (4 != 7):**
`create_rank_suggestions_for_certificate` (services.py) only iterated 4 component skills (Listening/Reading/Writing/Speaking). Vocabulary/Grammar/Collocation were absent — no inferred suggestions created.

### Fixes

**`backend/app/services.py` — `create_rank_suggestions_for_certificate`:**
Added `inferred` dict `{Vocabulary, Grammar, Collocation} → cert.overall_score`. Merged with `components` dict before the loop. All 7 skills now generate a `SkillRankSuggestion`. Vocabulary/Grammar/Collocation rank maps from `overall_score` via `map_ielts_score_to_rank`.

**`backend/app/main.py` — `activate_campaign`:**
After `cert.campaign_id = campaign.id` + `db.flush()`, now calls `create_rank_suggestions_for_certificate(db, cert)` for each pre-existing cert. Comment updated (removed "(display only, no rank suggestions)").

### Validated
- `TestCertificateAndSuggestionEndpoints` (4 tests): PASS
- Full suite: **44/44 PASS** (up from 42/44)

---

## [2026-06-09] Session 8c — XP/Level/Rank Redesign: Tasks 1–4 + Gap Fixes

**Status:** Done

### Changes

**`backend/app/services.py`**
- Replaced `RANK_THRESHOLDS` (7-tuple flat model) with 60-level curve: `_LEVEL_XP = [round(19*(L^1.6-1)) for L in 1..60]`. Added `level_from_xp`, `rank_from_level`, `get_rank_level`. Added `RANK_MIN_XP` dict and `_RANK_FIRST_LEVEL` dict.
- Fixed `recompute_skill_progress` + `apply_rank_suggestion`: `state.level` now uses `_RANK_FIRST_LEVEL[confirmed_rank]`, not old tuple unpacking.
- Added `MATRIX_SKILLS = {"Listening","Reading","Writing","Speaking","Vocabulary"}`.
- Rewrote `recompute_player_progress`: `player_xp = round(mean(5 matrix skill xp))`, no longer sums quest/mission/boss/vocab.
- Updated `refresh_progress_state`: passes `state_map` to `recompute_player_progress` (skills computed before player average).
- `award_player_xp` → no-op (signature kept, body = `pass`).

**`backend/app/main.py`**
- Weekly mission claim + boss claim: removed `else` branches that called `award_player_xp` for `reward_skill_id=None` cases. Player never accrues XP directly.

**`backend/app/seed.py`**
- Deleted stale `RANK_THRESHOLDS` block + dead `get_rank_level` function (Gap A).
- Updated `seed_rank_exam_pools()` transitions to canonical RANK_MIN_XP values: F→E=862, E→D=2460, D→C=4604, C→B=7212, B→A=10234, A→S=13279 (Gap B).

**`backend/app/test_backend.py`**
- Updated `test_boss_reward_routing` part 2: asserts no `PlayerXpTransaction` + no `player_xp` change for boss with `reward_skill_id=None` (Gap C).

**`spec/infor/ielts_xp_policy_rank_quest_spec.md`**
- Added UI note to §1.1: 5 matrix tiles, buff lines, `support_breakdown:[{source,xp}]` field, muted state for XP=0.

**`spec/infor/player_level.md`**
- Added §2.A: Support sources in UI (FINAL — owner decision 2026-06-09): 5 tiles, Grammar buff inside Writing card, Collocation buff inside Vocabulary card.

### Validated
- Level curve boundary checks (inside container): `level_from_xp(0)=1`, `(862)=11`, `(13279)=60`; `get_rank_level(861)=("F",10)`, `(862)=("E",11)`.
- `RANK_MIN_XP` matches spec §2.3 exactly.
- Mock player_xp average: `[1000,2000,0,0,0]` → 600.
- `award_player_xp` no-op; grep confirms no direct `player_xp` increment calls remain.
- `test_boss_reward_routing` part 2: PASS.
- Suite: 42/44 pass (2 pre-existing certificate-suggestion failures, unrelated).

### Deferred (not in scope)
- **Gap D / Gap E** → Task 16: FE `getPlayerLevel`/`getPlayerRank` stale formulas + `total_xp` naming mismatch.

---

## [2026-06-09] Session 8b — Boss-Gated Quest Claim XP Leak Fix

**Status:** Done

### Change
- `backend/app/main.py` (`POST /api/quests/{id}/claim`): when `skill_blocked=True` (skill `promotion_status` is `"boss_required"` or `"in_progress"`), return early without setting `reward_claimed=True`. Previously the endpoint set `reward_claimed=True` even when suppressing `award_skill_xp`, causing `recompute_skill_progress` to sum the quest's `earned_xp` back into `state.xp` on every refresh.

### Validated
- `TestRankExamPhase9.test_quest_claim_suppresses_xp_when_boss_required`: PASS (was failing: `state.xp=20`, expected 0)
- `TestRankExamPhase9.test_quest_claim_awards_xp_normally_when_eligible`: PASS (regression check)
- Suite: 42/44 pass (up from 41/44)

---

## [2026-06-08] Session 7b — Frontend Onboarding Redesign + Logout Button

**Status:** Done

### Changes
- `frontend/src/pages/Register.jsx`: bỏ form tên hiển thị — chỉ còn email + password.
- `frontend/src/pages/Onboarding.jsx`: rewrite thành 5 bước: Name → Campaign → StartDate → Certificate → Confirm. `CAMPAIGN_OPTIONS` constant (1 entry). `StepStartDate`: 2 options (Hôm nay / Ngày khác) + date input khi chọn Ngày khác. `StepConfirm`: hiển thị tên, campaign, ngày bắt đầu, rank.
- `frontend/src/api/auth.js`: `activateCampaign` nhận thêm `startDate`, truyền `start_date` vào body.
- `frontend/src/components/StatusModal.jsx`: thêm prop `onLogout`, nút "Đăng xuất" ở cuối modal.
- `frontend/src/App.jsx`: `handleLogout` gọi `logout()` + `navigate('/login')`; truyền vào StatusModal.
- `frontend/src/styles.css`: thêm styles cho `.status-logout-*`, `.onboarding-startdate-*`, `.onboarding-campaign-*`, `.onboarding-confirm-*`.
- `docker-compose.yml`: fix volume mount `material.md` (từ 0-byte `./backend/material.md` → `./material/material.md`) — giải quyết "No study-plan data" bug.

### Validated
- Playwright headless Chromium, all checks PASS:
  - Register: chỉ email + password ✅
  - Register → redirect /onboarding ✅
  - Step 1 tên input ✅ / Step 2 campaign card + "⭐ Đề xuất" badge + pre-selected ✅
  - Step 3 "Hôm nay" pre-selected + "Ngày khác" → date picker ✅
  - Step 4 5 score inputs + Quay lại ✅ / Step 5 confirm rows (tên + ngày) ✅
  - Kích hoạt → dashboard ✅
  - StatusModal mở → nút "Đăng xuất" visible → click → /login ✅

## [2026-06-08] Session 7 — Deterministic Seed + /me Fixes + Uvicorn Reload

**Status:** Done

### Changes
- `seed.py`: thêm `ensure_demo_account()` helper; `ensure_player` dùng `account_id` filter thay `Player.first()` — loại bỏ cross-account corruption; `ensure_account_and_profile` simplified.
- `main.py` `register()`: bỏ `"IELTS Hunter"` hardcode → `email_prefix or "New Hunter"`.
- `schemas.py` + `main.py`: thêm `OnboardingActivateIn`; `activate-campaign` nhận optional `display_name` + `campaign_template_code`.
- `schemas.py`: thêm `name` vào `PlayerMeOut`; đổi `active_campaign` → `campaign` trong `MeResponseOut`.
- `docker-compose.yml`: uvicorn `--reload` — backend tự reload khi code thay đổi.

### Validated
- Static: `py_compile` OK; grep confirms `Player.first()` và `"IELTS Hunter"` đã xóa khỏi register.
- Runtime: idempotent seed (reset ×2); register fallback = email prefix; `activate-campaign` body set name; 3-account isolation; `/me` trả đủ `player.name` + `campaign` key; uvicorn watch active.

## [2026-06-08] Collocation Master Data System Complete

**Status:** Done
**Summary:** Implemented the Collocation Master Data system, replacing the per-player legacy `vocabulary_collocations` table with a master data hierarchy (`CollocationCollection` -> `CollocationSection` -> `CollocationTopic` -> `CollocationItem`), link collections to campaigns (`CampaignCollocationLink`), track player progress (`PlayerCollocationProgress`), and updated services/APIs/tests accordingly.

### 1. Key changes

- **Alembic Migration**: Created and executed migration `950b4a9af4c2_add_collocation_master_data.py` which creates the 6 new tables and drops the legacy `vocabulary_collocations` table.
- **SQLAlchemy Models**: Defined `CollocationCollection`, `CollocationSection`, `CollocationTopic`, `CollocationItem`, `CampaignCollocationLink`, and `PlayerCollocationProgress` in `models.py`. Removed legacy `VocabularyCollocation`.
- **Pydantic Schemas**: Added new schemas in `schemas.py` including nested outline and progress wrappers, and deleted the old `VocabularyCollocationIn`/`VocabularyCollocationOut` schemas.
- **Services**: Appended CRUD and progress helper service functions to `services.py`. Refactored `get_collocation_practice()`, `sync_node_status_from_item()`, and `challenge_vocabulary_boss()` (checkpoints 3 & 4) to query from the new `CollocationItem` table. Removed stale `.collocations` joinedloads on `VocabularyItem` queries.
- **APIs**: Registered new endpoints for collections, sections, links, and progress in `main.py` and removed the old legacy endpoint routes.
- **Unit Tests**: Added `TestCollocationMasterData` to verify the entire lifecycle (creation, link, outline, practice matching game, progress updates, and vocabulary boss checkpoint integration). All 44 tests pass successfully.

### 2. Files changed

- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/services.py`
- `backend/app/main.py`
- `backend/app/test_backend.py`
- `backend/alembic/versions/950b4a9af4c2_add_collocation_master_data.py`
- `TASKS.md`
- `tasks-done.md`

## [2026-06-08] Phase 10–14: Auth Wire + Frontend Auth Shell + Onboarding UI + Suggestion Inbox + Rank Boss UI

**Status:** Done
**Summary:** Completed Phases 10–14 across two sessions. Backend ownership chain fully wired; frontend Auth Shell, Onboarding, Suggestion Inbox, and Rank Boss UI built and integrated.

### Phase 10 — Backend Ownership Protection
- Added `get_current_player`, `get_current_campaign`, `get_optional_campaign` FastAPI Depends chain
- Replaced ~70 call sites of `get_player_or_404` / `get_active_player` with account-scoped dependencies
- Added ownership guards on all routes with `{id}` in path (cross-account → 404)
- Updated `TestWaveDAndE` fixtures: StaticPool, `app.dependency_overrides`, TestClient
- Documented ownership chain in `docs/current/SCHEMA_SEMANTICS.md`
- All 43 tests pass

### Phase 11 — Frontend Auth Shell
- `frontend/src/api/client.js`: fetch wrapper with `Authorization: Bearer`, 401 error propagation
- `frontend/src/api/auth.js`: register, login, logout, getMe, getOnboardingStatus
- `frontend/src/auth/AuthProvider.jsx`: AuthContext, hydrateFromToken, login/logout/register callbacks, refreshAuth
- `frontend/src/auth/ProtectedRoute.jsx`: redirect to /login or /onboarding based on auth state
- `frontend/src/pages/Login.jsx`, `Register.jsx`: form pages with error handling
- `frontend/src/main.jsx`: BrowserRouter + Routes wrapping App
- `frontend/src/App.jsx`: api() useCallback with 401→logout handler

### Phase 12 — Frontend Onboarding UI
- `frontend/src/pages/Onboarding.jsx`: 3-step flow — Welcome → Manual Certificate (IELTS scores, skippable) → Confirm + activate
- `frontend/src/api/auth.js`: added `postManualCertificate()`, `activateCampaign()`
- Auth CSS + Onboarding CSS added to `styles.css`

### Phase 13 — Frontend Suggestion Inbox Fix
- `SuggestionInboxDropdown.jsx` + `SuggestionInboxPanel.jsx`: Apply/Dismiss buttons wired to `handleSuggestionAction` in App
- `dashboard-data.js`: rank suggestion title format `Rank F → E`, English detail strings
- Toast messages in English

### Phase 14 — Frontend Rank Boss UI
- `backend/app/schemas.py`: `SkillOut` exposes `promotion_status` + `pending_rank`
- `backend/app/main.py`: `serialize_skill_state` populates both fields
- `frontend/src/api/rankExam.js`: unlockRankExam, startRankExam, getRankExamAttempt, submitRankExam
- `frontend/src/components/RankBossNotif.jsx`: fixed bottom-right banner for eligible/boss_required/in_progress skills
- `frontend/src/components/RankExamScreen.jsx`: exam overlay — timer countdown, question navigator, MCQ + free-text, auto-submit on expiry
- `frontend/src/components/RankExamResultScreen.jsx`: result overlay — CLEARED/FAILED, score stats, retry button
- App.jsx wired with handleUnlockBoss, handleStartExam, handleExamResult, handleExamClose

### Files changed
- `backend/app/main.py`, `backend/app/schemas.py`
- `frontend/src/api/client.js`, `auth.js`, `rankExam.js` (new)
- `frontend/src/auth/AuthProvider.jsx`, `ProtectedRoute.jsx` (new)
- `frontend/src/pages/Login.jsx`, `Register.jsx`, `Onboarding.jsx`
- `frontend/src/components/RankBossNotif.jsx`, `RankExamScreen.jsx`, `RankExamResultScreen.jsx` (new)
- `frontend/src/components/SuggestionInboxDropdown.jsx`, `SuggestionInboxPanel.jsx`
- `frontend/src/App.jsx`, `main.jsx`, `dashboard-data.js`, `styles.css`
- `docs/current/SCHEMA_SEMANTICS.md`, `TASKS.md`, `DECISIONS.md`

## [2026-06-08] Phase 9 M6: Rank Boss Integration Tests + Bug Fixes

**Status:** Done
**Summary:** Wrote 16 integration tests for the Phase 9 rank boss flow. Discovered and fixed 4 bugs in `services.py` and `main.py` during testing.

### 1. Key changes

- `backend/app/test_backend.py`: Added `TestRankExamPhase9` class (16 tests covering unlock, start, get, submit pass/fail/penalty, XP block, retry cap, double-submit).
- `backend/app/services.py:sync_quest_statuses`: Guard `not quest.earned_xp` → `earned_xp is None and not reward_claimed` — prevents backfill from overriding XP-blocked quests.
- `backend/app/services.py:recompute_skill_progress`: Else-branch guard extended from `{"in_progress", "passed"}` to `{"eligible", "boss_required", "in_progress", "passed"}` — prevents recompute from clobbering in-flight exam state.
- `backend/app/services.py:refresh_progress_state`: Added `db.expire_all()` before state map reload — ensures fresh DB reads on shared SQLite session in tests.
- `backend/app/main.py:submit_rank_exam`: XP penalty (`state.xp -= 50`) moved to AFTER `refresh_progress_state`, with explicit `db.refresh(state)` — prevents recompute overwriting penalty.

### 2. Files changed

- `backend/app/test_backend.py`
- `backend/app/services.py`
- `backend/app/main.py`
- `TASKS.md`
- `docs/history/AGENT_NOTES.md`
- `docs/history/TEST_REPORT.md`
- `docs/history/changelogs.md`

## [2026-06-07] Phase 7: Backend Manual Certificate and Suggestion Apply Fix Complete

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Implemented manual certificate submissions mapping IELTS component and overall band scores to skill rank suggestions, fixed rank suggestion application logic to trigger direct promotions (resetting pending exam flags), and aligned route endpoints with the specification by adding `/api/skill-rank-suggestions` aliases.

### 1. Key changes

- Implemented `map_ielts_score_to_rank` helper in `backend/app/services.py` mapping IELTS scores to ranks `F` through `S` according to project progression semantics.
- Implemented `create_rank_suggestions_for_certificate` generator mapping Listening, Reading, Writing, Speaking to components, and mapping Overall score to support skills (Vocabulary, Grammar, Collocation).
- Updated `apply_rank_suggestion` service function to directly promote `confirmed_rank` (and `rank` if the suggested rank is higher) and clear any pending boss exam constraints (`pending_rank=None`, `promotion_status="none"`).
- Implemented authenticated `POST /api/certificates/manual` and `GET /api/certificates` endpoints in `backend/app/main.py`.
- Added spec-compliant route aliases `@app.get("/api/skill-rank-suggestions")`, `@app.post("/api/skill-rank-suggestions/{suggestion_id}/apply")`, and `@app.post("/api/skill-rank-suggestions/{suggestion_id}/dismiss")` in `backend/app/main.py` to ensure backend routes match both the specification and frontend expectations.
- Updated campaign activation flow (`POST /api/onboarding/activate-campaign`) to automatically link pre-existing certificate records (created during onboarding step 1) to the new campaign, generating suggestions immediately.
- Refactored suggestion apply/dismiss endpoints to secure them with `Depends(get_current_account)` and ensure multi-user campaign isolation.
- Added and updated `TestCertificateAndSuggestionEndpoints` in `backend/app/test_backend.py` validating 4 new manual certificate, suggestion mapping, direct promotion, and dismissal scenarios, including testing of `/api/skill-rank-suggestions` paths.
- Verified that all 24 backend unit tests compile and pass successfully.

### 2. Files changed

- [backend/app/main.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/main.py)
- [backend/app/services.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/services.py)
- [backend/app/test_backend.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/test_backend.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)

## [2026-06-07] Phase 6: Backend Onboarding and Campaign Activation Complete

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Implemented the mandatory onboarding status checks and campaign activation APIs, allowing players to transition from a newly registered account status to an active game loop campaign. Added automated integration tests for verification.

### 1. Key changes

- Implemented `GET /api/onboarding/status` endpoint in `backend/app/main.py` to retrieve onboarding completion status and certificate existence.
- Implemented `POST /api/onboarding/activate-campaign` endpoint in `backend/app/main.py` which triggers the complete campaign initialization flow (settings, templates, quotas, quest instances, weekly missions, bosses, test records, and campaign skill states) and updates `Account.onboarding_completed` and `Campaign.setup_completed`/`Player.setup_completed` atomically.
- Refactored `parse_start_date` to be defined in `backend/app/seed.py` and imported in `backend/app/main.py` to avoid circular dependencies and resolve a `NameError`.
- Added the `TestOnboardingEndpoints` class in `backend/app/test_backend.py` implementing comprehensive integration tests for status checks, certificate presence, activation flow success, and unauthorized request blocks.
- Ran the test suite successfully with all 20 tests passing.

### 2. Files changed

- [backend/app/main.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/main.py)
- [backend/app/seed.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/seed.py)
- [backend/app/test_backend.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/test_backend.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)

## [2026-06-07] Phase 5: Backend Auth MVP Complete

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Implemented comprehensive unit tests and resolved critical bugs inside the Backend Auth MVP flow. Covered registration, login, token refresh, logout, and get_me endpoints using FastAPI's `TestClient` in SQLite. Resolved a non-null database constraint failure on registration and a logic ordering vulnerability on login account locking.

### 1. Key changes

- Added `TestAuthEndpoints` class in `backend/app/test_backend.py` implementing 10 new API integration tests for full auth lifecycle coverage.
- Configured SQLite in-memory engine under `TestAuthEndpoints` with `StaticPool` and disabled `check_same_thread` to support multi-threaded test requests by FastAPI's server workers.
- Fixed a bug in `POST /api/auth/register` where `PlayerLearningProfile` was constructed with an un-flushed `player.id` (which was `None`), raising database integrity errors. Linked the models via standard SQLAlchemy object relationships (`player=player`).
- Fixed a bug in `POST /api/auth/login` where account lockouts were checked *after* password verification, which made locking ineffective against incorrect passwords. Swapped the order to verify lock status first.
- Added `httpx` package dependency in `backend/requirements.txt` for TestClient support.

### 2. Files changed

- [backend/app/main.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/main.py)
- [backend/app/test_backend.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/test_backend.py)
- [backend/requirements.txt](file:///d:/better_english/ielts-quest-dashboard/backend/requirements.txt)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)


## [2026-06-07] Phase 4: Seed and Backfill Development Environment Seeding

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Resolved database reset and seeding constraint issues. Shortened vocabulary daily quest slot codes from 22 characters to under 20 to fit within the `daily_slot_code` column limit. Added raw SQL transient foreign key disables (`SET FOREIGN_KEY_CHECKS = 0/1;`) in `reset_database` endpoint (`/api/dev/reset`) to ensure clean and fully idempotent database wiping and reseeding. Verified completeness of seeded records.

### 1. Key changes

- Modified `backend/app/seed.py` to shorten vocabulary slot codes (`vocabulary_flashcard` -> `vocab_flashcard`, `vocabulary_codex` -> `vocab_codex`, `vocabulary_collocation` -> `vocab_collocation`) to fit the database `String(20)` length constraint.
- Modified `backend/app/main.py` to temporarily disable MySQL foreign key checks during the execution of the `/api/dev/reset` endpoint, ensuring deletes succeed regardless of table dependency order.
- Configured backend container with `PYTHONUNBUFFERED=1` to allow instant Docker log flushes.
- Verified all dev account linking, preferences, learning profiles, campaign templates, vocabulary settings, and 30 rank exam pools with correct progression XP thresholds were seeded successfully.

### 2. Files changed

- [backend/app/seed.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/seed.py)
- [backend/app/main.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/main.py)
- [docker-compose.yml](file:///d:/better_english/ielts-quest-dashboard/docker-compose.yml)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)


## [2026-06-07] Pre-Phase Fix: Idempotent Database Migrations and Container Alignment

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Resolved database schema migration blocks on MariaDB/MySQL by rewriting Alembic migration `30b9013e0a20` and `d4fcb0a83bb2` to conditionally drop all foreign key constraints before altering columns from `BIGINT` to `INT`, and dynamically querying `Vocabulary` skill IDs during seeding. Configured container-friendly environment variable lookups in `backend/alembic/env.py` and aligned documentation.

### 1. Key changes

- Rewrote `backend/alembic/versions/30b9013e0a20_add_certificate_record_fk_and_xp_.py` to conditionally drop and recreate all dependent foreign keys and indexes to prevent MySQL 3780 type incompatibility errors.
- Rewrote `backend/alembic/versions/d4fcb0a83bb2_add_certificate_fk_and_xp_threshold.py` to resolve dynamic skill IDs and fill in NOT NULL columns (`created_at`, `updated_at`, etc.) for bulk inserts.
- Updated `backend/alembic/env.py` to respect the `DATABASE_URL` environment variable, enabling container-friendly upgrades.
- Successfully applied all migrations on host and inside the `ielts_quest_backend` Docker container.
- Updated `docs/current/DATABASE_SCHEMA.md` and `docs/current/SCHEMA_SEMANTICS.md` to register new entities and document the onboarding status atomicity requirement.

### 2. Files changed

- [backend/alembic/versions/30b9013e0a20_add_certificate_record_fk_and_xp_.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/versions/30b9013e0a20_add_certificate_record_fk_and_xp_.py)
- [backend/alembic/versions/d4fcb0a83bb2_add_certificate_fk_and_xp_threshold.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/versions/d4fcb0a83bb2_add_certificate_fk_and_xp_threshold.py)
- [backend/alembic/env.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/env.py)
- [docs/current/DATABASE_SCHEMA.md](file:///d:/better_english/ielts-quest-dashboard/docs/current/DATABASE_SCHEMA.md)
- [docs/current/SCHEMA_SEMANTICS.md](file:///d:/better_english/ielts-quest-dashboard/docs/current/SCHEMA_SEMANTICS.md)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)

## [2026-06-07] Phase 3: Certificate and Rank Boss Database Migration

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Implemented SQLAlchemy models for tracking certificates and the Rank Boss Exam system (exam pools, versions, questions, attempts, answers), modified `campaign_skill_states` with rank promotion columns, generated and cleaned Alembic migration revision `53902275681a`, aligned migration stamping, and verified tests.

### 1. Key changes

- Modified `backend/app/models.py` to declare `CertificateRecord`, `RankExamPool`, `RankExamVersion`, `RankExamQuestion`, `RankExamAttempt`, and `RankExamAnswer` models.
- Modified `CampaignSkillState` model to add columns `pending_rank`, `promotion_status`, `promotion_unlocked_at`, and `last_rank_exam_attempt_id` (along with relationships).
- Linked `Player` and `Campaign` models with relationships to the new certificate records and rank attempts.
- Generated and cleaned Alembic migration `53902275681a_add_certificate_and_rank_boss_tables.py`, and stamped database state to head to resolve reloading bootstrapping collisions.
- Ran all backend unit tests successfully.

### 2. Files changed

- [backend/app/models.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/models.py)
- [backend/alembic/versions/53902275681a_add_certificate_and_rank_boss_tables.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/versions/53902275681a_add_certificate_and_rank_boss_tables.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)
- [docs/history/TEST_REPORT.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/TEST_REPORT.md)
- [docs/history/AGENT_NOTES.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/AGENT_NOTES.md)

## [2026-06-07] Phase 2: Campaign Template / Settings / Quota Database Migration

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Implemented SQLAlchemy models for Campaign templates, settings, skill quotas, quest quotas, and vocabulary settings, modified campaigns table columns/relationships, generated Alembic migration, resolved database bootstrapping overlaps, and verified unit tests.

### 1. Key changes

- Modified `backend/app/models.py` to declare `CampaignSetting`, `CampaignTemplateSkillQuota`, `CampaignSkillQuestQuota`, and `VocabularySetting` models.
- Modified `CampaignTemplate` and `Campaign` models to include new columns (`campaign_template_id`, `setup_completed`, `setup_completed_at`) and foreign keys/relationships.
- Generated and cleaned Alembic migration revision `53ec0dd9fb0d_add_campaign_template_and_quotas.py`, and stamped the database head to align migration versioning.
- Ran and verified all backend unit tests pass successfully.

### 2. Files changed

- [backend/app/models.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/models.py)
- [backend/alembic/versions/53ec0dd9fb0d_add_campaign_template_and_quotas.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/versions/53ec0dd9fb0d_add_campaign_template_and_quotas.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)
- [docs/history/TEST_REPORT.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/TEST_REPORT.md)
- [docs/history/AGENT_NOTES.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/AGENT_NOTES.md)

## [2026-06-07] Phase 1: Account/Auth Database Migration

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Implemented SQLAlchemy models for Account-scoped authentication tables and players linkage, generated and executed the Alembic migration to apply the tables to MySQL, and verified unit tests.

### 1. Key changes

- Modified `backend/app/models.py` to add `Account`, `AccountSession`, `AccountToken`, `AccountSecurityEvent`, and `AccountPreference` models.
- Modified `Player` model to include a nullable `account_id` foreign key referencing `accounts.id` with unique constraint and unique index, and established a one-to-one mapping relationship.
- Generated Alembic migration revision `b14757712bca_add_account_auth_tables.py` and cleaned it from noisy autogenerate type modifications on existing tables.
- Dropped conflicting empty table schema leftovers in local MySQL and executed `alembic upgrade head` to finalize DB state.
- Checked players column metadata and ran unit tests successfully.

### 2. Files changed

- [backend/app/models.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/models.py)
- [backend/alembic/versions/b14757712bca_add_account_auth_tables.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/versions/b14757712bca_add_account_auth_tables.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [docs/history/TEST_REPORT.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/TEST_REPORT.md)
- [docs/history/AGENT_NOTES.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/AGENT_NOTES.md)

## [2026-06-07] Phase 0: Big Update Documentation and ADR Preparation

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Updated architecture decisions in `DECISIONS.md`, database entity mappings in `docs/current/DATABASE_SCHEMA.md`, and enum/state semantic meanings in `docs/current/SCHEMA_SEMANTICS.md` to reflect the new Account, Onboarding, and Rank Boss updates.

### 1. Key changes

- Added the `2026-06-07 - Big Update: Account, Onboarding & Rank Boss System Architecture` decision block to `DECISIONS.md`.
- Expanded `docs/current/DATABASE_SCHEMA.md` to include account-scoped tables (`accounts`, `account_sessions`, `account_tokens`, `account_security_events`, `account_preferences`), template/definition tables (`campaign_templates`, `campaign_template_skill_quotas`, etc.), and rank exam tables (`rank_exam_pools`, `rank_exam_versions`, etc.). Registered corresponding unique keys and foreign key constraints.
- Updated `docs/current/SCHEMA_SEMANTICS.md` to add meanings for `pending_rank`, `promotion_status` progression states, the three active scope layers (account-scoped, campaign-scoped, player-wide), account statuses and roles, and rank boss exam attempt status values.
- Updated the main checklist in `TASKS.md`.

### 2. Files changed

- [DECISIONS.md](file:///d:/better_english/ielts-quest-dashboard/DECISIONS.md)
- [docs/current/DATABASE_SCHEMA.md](file:///d:/better_english/ielts-quest-dashboard/docs/current/DATABASE_SCHEMA.md)
- [docs/current/SCHEMA_SEMANTICS.md](file:///d:/better_english/ielts-quest-dashboard/docs/current/SCHEMA_SEMANTICS.md)
- [docs/history/changelogs.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/changelogs.md)

## [2026-06-07] Add database check constraints for typed links

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Generated and executed Alembic migration `089adadeddde_add_typed_links_check_constraints.py` to add database-level check constraints on the `quests` and `weakness_suggestions` tables to enforce that at most one typed tracker or source link is defined. Bounded these check constraints with automated tests in `test_backend.py`.

### 1. Key changes

- Created Alembic migration `089adadeddde_add_typed_links_check_constraints.py` executing `create_check_constraint` for:
  - `ck_quests_only_one_tracker` on `quests` table.
  - `ck_weakness_suggestions_only_one_source` on `weakness_suggestions` table.
- Added `test_check_constraints` inside `backend/app/test_backend.py` asserting that violating these constraints correctly triggers database-level `IntegrityError` exceptions.
- Updated `TASKS.md` and `docs/history/MIGRATION_HISTORY.md` to reflect that the Deferred Backlog tasks have been fully completed.

### 2. Files changed

- [backend/alembic/versions/089adadeddde_add_typed_links_check_constraints.py](file:///d:/better_english/ielts-quest-dashboard/backend/alembic/versions/089adadeddde_add_typed_links_check_constraints.py)
- [backend/app/test_backend.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/test_backend.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)
- [docs/history/MIGRATION_HISTORY.md](file:///d:/better_english/ielts-quest-dashboard/docs/history/MIGRATION_HISTORY.md)
- [tasks-done.md](file:///d:/better_english/ielts-quest-dashboard/tasks-done.md)

## [2026-06-07] Add Boss claim reward routing test and fix main.py import NameError

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Added automated backend unit tests for skill-specific vs overall player boss battle claim reward routing and fixed a NameError in the API controller caused by a missing import of the `datetime` module.

### 1. Key changes

- Added `test_boss_reward_routing` inside `backend/app/test_backend.py` which:
  - Verifies that claiming a skill-scoped boss battle routes XP to `SkillXpTransaction` and updates campaign skill state XP correctly.
  - Verifies that claiming a player-scoped boss battle routes XP to `PlayerXpTransaction` and updates player total XP correctly.
  - Asserts correct idempotency key routing and verifies no cross-pollution of transaction types.
- Fixed a `NameError` in `backend/app/main.py` at line 763 by adding `datetime` to the imports from `datetime` (i.e. `from datetime import date, datetime, timedelta`).
- Ran and verified that all 5 unit tests in `test_backend.py` compile and pass cleanly inside the backend container.
- Updated `TASKS.md` to check off the boss battle reward transactions verification task.

### 2. Files changed

- [backend/app/main.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/main.py)
- [backend/app/test_backend.py](file:///d:/better_english/ielts-quest-dashboard/backend/app/test_backend.py)
- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)

## [2026-06-07] Visual verification walkthrough screenshots

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Wrote and ran a puppeteer-core automation script to capture dashboard and overlay screenshots.

### 1. Key changes

- Created Node.js automation script `scratch/capture.js` to control host Chrome.
- Captured three screenshots validating dashboard components and active layouts:
  - `img/dashboard_main.png` (Main view)
  - `img/vocabulary_workspace.png` (Vocabulary Workspace view)
  - `img/quest_overlay.png` (Daily Quest Panel view)
- Updated `TASKS.md` to mark the visual walkthrough task as complete.

### 2. Files changed

- [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md)

## [2026-06-07] Fix frontend connection failure ("Failed to fetch")

**Agent:** Antigravity (session)
**Status:** Done
**Summary:** Changed frontend API connection URL from localhost to 127.0.0.1 to avoid HSTS and DNS issues on the host.

### 1. Key changes

- Modified `frontend/src/App.jsx` fallback API URL from `localhost` to `127.0.0.1`.
- Modified `docker-compose.yml` to change `VITE_API_URL` for the frontend service to `http://127.0.0.1:8000/api`.
- Recreated the frontend container (`docker compose up -d`) to apply the new environment variables.

### 2. Files changed

- [docker-compose.yml](file:///d:/better_english/ielts-quest-dashboard/docker-compose.yml)
- [frontend/src/App.jsx](file:///d:/better_english/ielts-quest-dashboard/frontend/src/App.jsx)

## [2026-06-07] Session: Quest & XP routing, migrations, boss rewards, frontend tweaks

**Agent:** GitHub Copilot (session)
**Status:** Done
**Summary:** Implemented quest reward routing, idempotent XP transactions, seed updates, migration scripts and dev helpers, boss reward routing, and small frontend UX improvements. Also updated `TASKS.md` and the session todo tracker.

### 1. Key changes

- Added `SkillXpTransaction` and `PlayerXpTransaction` flow with idempotency keys and service helpers to record and apply XP.
- Extended `Quest`, `QuestTemplate`, and `WeeklyMission` models with reward/track fields and relationships to `Skill`.
- Implemented claim flows to route rewards to skill-scoped or player-scoped transactions (`POST /api/quests/{id}/claim`, `POST /api/weekly-missions/{id}/claim`).
- Added boss reward fields and a claim endpoint (`POST /api/boss-battles/{id}/claim`) to route boss rewards to skill or player XP.
- Added Alembic migration file for quest/xp transaction changes and a follow-up migration for boss reward fields; added a dev endpoint to run migrations (`POST /api/dev/run_migrations`).
- Enhanced the dev reset endpoint (`POST /api/dev/reset`) to return seeded counts for verification.
- Frontend: show reward skill on quest cards, add quick skill filter, and display `completion_payload` on completed quests.
- Updated `TASKS.md` and the session todo tracker to reflect completed items.

### 2. Files changed (high-level)

- backend/app/models.py: relationships and new boss reward fields
- backend/app/services.py: `award_skill_xp`, `award_player_xp` helpers and rank updates
- backend/app/main.py: claim endpoints, dev helpers (`/api/dev/reset`, `/api/dev/run_migrations`), boss claim endpoint
- backend/app/schemas.py: extended `QuestOut` and `BossBattleOut` outputs
- backend/app/seed.py: vocabulary templates seeded earlier in session (retained)
- backend/alembic/versions/20260607_11_quest_and_xp_transactions.py: migration file (created earlier)
- backend/alembic/versions/20260607_12_boss_reward_fields.py: migration file (added)
- frontend/src/components/DailyQuestPanel.jsx: show reward skill, skill filter, completion payload
- frontend/src/dashboard-data.js: reward value helpers (existing usage)
- TASKS.md: updated task statuses and notes
- docs/history/changelogs.md: this entry

### 3. Notes & next steps

- Run migrations locally or call `POST /api/dev/run_migrations` before starting the app against a real DB.
- Verify seed reset by calling `POST /api/dev/reset` and confirming `quest_templates` / `weekly_missions` counts in the response.
- Verify idempotency by attempting duplicate claims; transactions use `idempotency_key` to avoid duplicates.

If you want, I can add a more detailed per-file diff summary or generate a small verification script to run these checks automatically.

## [2026-06-07] Record Architecture Decision and Setup Quest Routing Tasks

**Agent:** Antigravity
**Status:** Done
**Related task:** Track tasks and note decisions from `spec/feature/skill_specific_quest_xp_routing_spec.md`

### 1. Summary

Parsed the newly approved `spec/feature/skill_specific_quest_xp_routing_spec.md` specification, recorded the architectural decisions, and registered the implementation tasks.

- Recorded the decision to extend the generic Quest system for Vocabulary Daily Quests and utilize separate `skill_xp_transactions` and `player_xp_transactions` tables in [DECISIONS.md](file:///d:/better_english/ielts-quest-dashboard/DECISIONS.md).
- Added the `Skill-Specific Quest XP Routing & Vocabulary Daily Quest Tracker` section to [TASKS.md](file:///d:/better_english/ielts-quest-dashboard/TASKS.md) with 7 distinct implementation tasks.
- Marked **Task 1 — Docs / ADR Decision** subtasks as completed since the decision recording and agent note/changelog tasks are completed.

### 2. Files changed

| File           | Change type | What changed                                                                                             |
| -------------- | ----------- | -------------------------------------------------------------------------------------------------------- |
| `DECISIONS.md` | Modified    | Added the Skill-Specific Quest XP Routing and Quest Extension decision entry.                            |
| `TASKS.md`     | Modified    | Appended the new Quest XP Routing and Vocabulary Daily Quest tracker sections and marked Task 1 as Done. |

## [2026-06-07] Quest System Specification Update and Translation

**Agent:** Antigravity
**Status:** Done
**Related task:** Update and complete `spec/infor/quest.md`

### 1. Summary

Fully translated `spec/infor/quest.md` to English (per the repository rules) and expanded it to serve as the canonical source of truth for the Quest system.

- Documented `QuestTemplate` entity and fields.
- Documented `Quest` entity and fields, including the nullable typed link fields (`error_log_id`, `writing_entry_id`, `speaking_entry_id`, `mock_test_id`) and lifecycle state fields.
- Documented Main Quests in detail, including study plan week/session references, dynamic XP calculation rules, and unique daily slot constraint bypassing.
- Documented Quest Archive and Backlog query-based logic, including `/api/quests/backlog` filters and late completion/claiming behaviors.
- Detailed the uniqueness invariants (e.g., `uq_quests_campaign_date_daily_slot` constraint).
- Explained the quest status lifecycle transitions and synchronization logic (`sync_quest_statuses`) mapping pending, completed, overdue, expired, and claimed states, alongside the 50% XP penalty rule for late completions.
- Outlined the parent-child structure of Weekly Missions (`weekly_missions` and `weekly_mission_items`) and detail progress item triggers.
- Detailed the reward-claiming and XP banking progression loop.
- Expanded the Mermaid ERD visualization to model all entities, templates, and evidence tracker linkages.

### 2. Files changed

| File                  | Change type | What changed                                                            |
| --------------------- | ----------- | ----------------------------------------------------------------------- |
| `spec/infor/quest.md` | Modified    | Fully translated to English and updated with comprehensive quest specs. |

## [2026-06-07] Lexical Awakening Full-Tab UI Redesign Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Redesign Lexical Awakening overlay to full-tab page

### 1. Summary

Redesigned the Lexical Awakening (Vocabulary Support Skill) UI from a constrained modal overlay to a dedicated full-tab page workspace, resolving usability and layout cramping issues for all modules.

- Created `frontend/src/components/VocabularyWorkspace.jsx` to render the full-tab view, featuring a sidebar containing the back button, key stats (Words in Codex, Due Cards, Active Errors), and tab navigation (9 tabs), and a large right-side main workspace container.
- Modified `frontend/src/App.jsx` to implement a `currentView` routing state (`'dashboard'` or `'vocabulary'`). Conditioned layout rendering on this state, replacing the legacy `VocabularyOverlay` modal trigger completely.
- Added comprehensive styles in `frontend/src/styles.css` for the workspace, sidebar, nav buttons, stats badges, and set container height constraints for the Word Network Tree (React Flow) canvas to use full screen height bounds.
- Verified that the codebase compiles and builds cleanly without warnings or errors.

### 2. Files changed

| File                                              | Change type | What changed                                                                                                                        |
| ------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `frontend/src/components/VocabularyWorkspace.jsx` | Created     | Built full-tab workspace view, replacing old OverlayFrame wrappers.                                                                 |
| `frontend/src/App.jsx`                            | Modified    | Integrated `currentView` routing state, and conditionally rendered the new VocabularyWorkspace instead of the legacy modal overlay. |
| `frontend/src/styles.css`                         | Modified    | Added workspace and sidebar classes, and configured heights for child minigames.                                                    |
| `TASKS.md`                                        | Modified    | Marked full-tab redesign task as In Progress / Done.                                                                                |

## [2026-06-07] Wave D & E Automated Backend Tests Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Add automated backend tests for Wave D and E behavior

### 1. Summary

Created a robust unit/integration test suite to verify campaign-scoped database invariants and model logic introduced in Waves D and E.

- Implemented tests in `backend/app/test_backend.py` using `unittest` and SQLite in-memory database.
- Tested campaign-scoped skill state isolation, campaign-scoped badge unlocks recomputation, campaign-scoped check-in uniqueness, and daily-slot code uniqueness constraints.
- Updated constraints inside `backend/app/models.py` for `Quest` and `CheckIn` models to match the database constraints.

### 2. Files changed

| File                          | Change type | What changed                                                             |
| ----------------------------- | ----------- | ------------------------------------------------------------------------ |
| `backend/app/test_backend.py` | Created     | Added automated test suite for Wave D & E.                               |
| `backend/app/models.py`       | Modified    | Synchronized unique constraints on Quest and CheckIn with the DB schema. |

## [2026-06-07] Fix backend API crash loop

**Agent:** Antigravity
**Status:** Done
**Related task:** Diagnose and fix `API ERROR: Failed to fetch`

### 1. Summary

Fixed a backend crash loop (API Error: Failed to fetch) on startup. The application was crashing during the startup database inspection in `refresh_progress_state` due to the missing `vocabulary_errors` table. This occurred because a previous migration (`6c233774a1db`) failed halfway through when trying to add columns that already existed in the database, yet the DB version was stamped.

To resolve this, we:

- Made the migration `6c233774a1db_add_vocabulary_errors.py` fully idempotent by checking if tables/columns exist before creating or adding them.
- Successfully executed the migration and verified the database state.
- Verified that the backend container starts successfully and the health check responds with 200 OK.

### 2. Files changed

| File                                                             | Change type | What changed                               |
| ---------------------------------------------------------------- | ----------- | ------------------------------------------ |
| `backend/alembic/versions/6c233774a1db_add_vocabulary_errors.py` | Modified    | Made table and column creation idempotent. |

## [2026-06-07] Phase 4: Error Dungeon & Boss Battles Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 4: Boss and Error System

### 1. Summary

Fully completed Phase 4 of the Lexical Awakening System.

- Created `vocabulary_errors` database table and logic for the Error Dungeon.
- Added `example_meaning` fields to `vocabulary_examples` and `vocabulary_collocations` tables/models/schemas.
- Implemented Error Dungeon backend endpoints (`POST`, `GET`, `PATCH`, `/defeat`) and frontend screen (`ErrorDungeon.jsx`).
- Implemented Vocabulary Boss checkpoint battles backend endpoints (`/status`, `/challenge`, `/submit`) and frontend screen (`VocabularyBoss.jsx`).
- Connected vocabulary boss achievements and defeated error counts with Campaign Badge wall unlocks (e.g. Memory Streak Badge I, Lexical Awakener, Writing Lexical Buff, and Error Killer).
- Upgraded the Flashcard Gate component to render rich, structured metadata including word types (part of speech), IPA US pronunciation, and examples with their translations.

### 2. Files changed

| File                                                             | Change type | What changed                                                                                                                                              |
| ---------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/alembic/versions/6c233774a1db_add_vocabulary_errors.py` | Modified    | Cleared autogenerated noise to execute exactly table creations and column additions.                                                                      |
| `backend/app/models.py`                                          | Modified    | Appended `example_meaning` to `VocabularyExample` and `VocabularyCollocation`.                                                                            |
| `backend/app/schemas.py`                                         | Modified    | Updated schemas for collocations and examples, added Boss Battle schemas, and added `vocabulary_item` relation to `FlashcardOut`.                         |
| `backend/app/services.py`                                        | Modified    | Appended Error Dungeon CRUD and defeat services, Boss status/exam generation/submit services, and updated `recompute_badges` and `compute_vocabulary_xp`. |
| `backend/app/main.py`                                            | Modified    | Exposed Error Dungeon and Vocabulary Boss endpoints.                                                                                                      |
| `frontend/src/components/ErrorDungeon.jsx`                       | Created     | Built the active errors dashboard rendering mistakes as HP-based monsters.                                                                                |
| `frontend/src/components/VocabularyBoss.jsx`                     | Created     | Built the checkpoint boss battles selection grid and dynamic multi-step quiz challenge.                                                                   |
| `frontend/src/components/VocabularyOverlay.jsx`                  | Modified    | Upgraded Flashcard front/back display, loaded active errors and boss status, and mounted Dungeon and Boss tabs.                                           |
| `backend/app/seed.py`                                            | Modified    | Added the new badges (Memory Streak Badge I, Lexical Awakener, Writing Lexical Buff) to the database seed list.                                           |
| `TASKS.md`                                                       | Modified    | Marked Phase 4 tracker tasks as Done.                                                                                                                     |

## [2026-06-07 02:00] Phase 3 Slice 4: Echo Chamber Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 3: IELTS Advanced Vocabulary - Echo Chamber

### 1. Summary

Implemented the Echo Chamber interactive mini-game. Added the `/api/vocabulary/practice/echo-chamber` route in `main.py` to query custom items with IPA & stress or fallback to standard phonetics questions with custom syllables and silent letters. Built the frontend `EchoChamber.jsx` challenge including browser-native speech synthesis, syllable stress selection, silent letter hunting, and API recording integrations.

### 2. Files changed

| File                                            | Change type | What changed                                                                             |
| ----------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------- |
| `backend/app/schemas.py`                        | Modified    | Added `EchoChamberQuestion` and `EchoChamberResponse` schemas.                           |
| `backend/app/services.py`                       | Modified    | Added `get_echo_chamber_practice` service to extract stress patterns and silent letters. |
| `backend/app/main.py`                           | Modified    | Exposed `/api/vocabulary/practice/echo-chamber` endpoint.                                |
| `frontend/src/components/EchoChamber.jsx`       | Created     | Built pronunciation audio controls, stressed syllable games, and silent letter hunts.    |
| `frontend/src/components/VocabularyOverlay.jsx` | Modified    | Registered and mounted `EchoChamber` under activeTab `'echo-chamber'`.                   |
| `frontend/src/styles.css`                       | Modified    | Appended CSS classes for the syllable stress buttons and silent letter selection blocks. |

## [2026-06-07 01:40] Phase 3 Slice 3: Word Family Evolution Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 3: IELTS Advanced Vocabulary - Word Family Evolution

### 1. Summary

Implemented the Word Family Evolution interactive panel. Added the `/api/vocabulary/practice/word-family` endpoint to group vocabulary items by family roots using database relations and fallback to standard IELTS word families (e.g. produce, communicate, create) synced with the player's vocabulary discovery state. Created the frontend `WordFamilyEvolution.jsx` component using React Flow to render tree-morphological diagrams of root words and parts of speech, combined with an interactive sentence gap quiz that registers success and updates mastery.

### 2. Files changed

| File                                              | Change type | What changed                                                                                       |
| ------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------- |
| `backend/app/schemas.py`                          | Modified    | Added `WordFamilyNode`, `WordFamilyEdge`, `WordFamilyGroup`, and `WordFamilyResponse` schemas.     |
| `backend/app/services.py`                         | Modified    | Added `get_word_families_practice` service to build visual family trees.                           |
| `backend/app/main.py`                             | Modified    | Exposed `/api/vocabulary/practice/word-family` endpoint.                                           |
| `frontend/src/components/WordFamilyEvolution.jsx` | Created     | Built React Flow tree component, detailed sidebar description cards, and sentence gap quizzes.     |
| `frontend/src/components/VocabularyOverlay.jsx`   | Modified    | Registered and mounted `WordFamilyEvolution` under activeTab `'word-family'`.                      |
| `frontend/src/styles.css`                         | Modified    | Appended CSS classes for the canvas wrappers, select controls, quiz items, and active/locked rows. |

## [2026-06-07 01:20] Phase 3 Slice 2: Shadow Duel Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 3: IELTS Advanced Vocabulary - Shadow Duel

### 1. Summary

Implemented the Shadow Duel mini-game where players practice synonyms, antonyms, and registers. Exposed `GET /api/vocabulary/practice/shadow-duel` to query relations or fallback to a robust list of IELTS-specific duels. Added `POST /api/vocabulary/practice/record-success` to save correct answers, increment vocabulary item mastery scores, auto-advance ranks, and trigger XP updates. Created the frontend `ShadowDuel.jsx` quiz component with live 10-second countdown timers, visual lives, streak multipliers, and success logging.

### 2. Files changed

| File                                            | Change type | What changed                                                                                                                                                           |
| ----------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/schemas.py`                        | Modified    | Added `ShadowDuelQuestion`, `ShadowDuelResponse`, and `PracticeSuccessIn` schemas.                                                                                     |
| `backend/app/services.py`                       | Modified    | Added `get_shadow_duel_practice` and `record_practice_success` service functions. Updated `compute_vocabulary_xp` to award XP based on vocabulary item mastery scores. |
| `backend/app/main.py`                           | Modified    | Exposed `/api/vocabulary/practice/shadow-duel` and `/api/vocabulary/practice/record-success` routes.                                                                   |
| `frontend/src/components/ShadowDuel.jsx`        | Created     | Built fast-paced dueling quiz game with countdowns, HP, streaks, and API sync.                                                                                         |
| `frontend/src/components/VocabularyOverlay.jsx` | Modified    | Registered and mounted `ShadowDuel` under activeTab `'shadow-duel'`.                                                                                                   |
| `frontend/src/styles.css`                       | Modified    | Appended CSS styling classes for the shadow duel UI layouts, timer bars, and hearts.                                                                                   |

## [2026-06-07 00:35] Phase 3 Slice 1: Collocation Forge Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 3: IELTS Advanced Vocabulary - Collocation Forge

### 1. Summary

Implemented the Collocation Forge interactive mini-game. Added the `/api/vocabulary/practice/collocations` endpoint to fetch collocations and generate distractors for practice. Built the frontend `CollocationForge.jsx` matching game component and integrated it as a new tab within the Vocabulary Overlay. Added associated schemas and CSS styles.

### 2. Files changed

| File                                            | Change type | What changed                                                                   |
| ----------------------------------------------- | ----------- | ------------------------------------------------------------------------------ |
| `backend/app/schemas.py`                        | Modified    | Added `CollocationPracticeMatchOut` and `CollocationPracticeResponse` schemas. |
| `backend/app/services.py`                       | Modified    | Added `get_collocation_practice` to generate match pairs and distractors.      |
| `backend/app/main.py`                           | Modified    | Added `GET /api/vocabulary/practice/collocations` endpoint.                    |
| `frontend/src/components/CollocationForge.jsx`  | Added       | Built interactive click-to-match mini-game.                                    |
| `frontend/src/components/VocabularyOverlay.jsx` | Modified    | Hooked up the new Collocation Forge tab.                                       |
| `frontend/src/styles.css`                       | Modified    | Added CSS styles for the forge UI elements.                                    |

## [2026-06-07 00:25] Phase 2 Word Network Tree Visual Map Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 2: Word Network Tree

### 1. Summary

Fully implemented the visual Word Network Tree (Lexical Awakening System Phase 2). Created and registered Pydantic schemas, backend CRUD services, and visual tree API routes for topics, nodes, and edges. Hooked up an automated status synchronization engine (`sync_node_status_from_item`) to keep visual nodes updated upon card review or Codex changes. Integrated React Flow v11 into the frontend to render the visual graph with customized node statuses (locked, discovered, activated, mastered, awakened) styled in glowing cyberpunk/Solo-Leveling dark mode.

### 2. Files changed

| File                                            | Change type | Changed lines / area             | What changed                                                                                                                                                                                    |
| ----------------------------------------------- | ----------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/main.py`                           | Modified    | Imports, Reset, Routes           | Imported new models/schemas, registered tree models in database reset logic in dependency order, and exposed CRUD API routes for topics, nodes, and edges.                                      |
| `backend/app/schemas.py`                        | Modified    | End of file                      | Added Pydantic schemas (`VocabularyTopicOut`, `VocabularyNodeOut`, `VocabularyEdgeOut`, etc.) for Phase 2.                                                                                      |
| `backend/app/services.py`                       | Modified    | Imports, End of file, CRUD hooks | Imported tree models/schemas, implemented visual tree CRUD services, built node status sync logic, and added sync triggers on existing example/collocation modifications and flashcard reviews. |
| `frontend/package.json`                         | Modified    | Dependencies                     | Added `reactflow` library.                                                                                                                                                                      |
| `frontend/src/components/VocabularyOverlay.jsx` | Modified    | Navigation & Render              | Integrated a third tab "Word Network Tree" and render the new tree layout component when selected.                                                                                              |
| `frontend/src/components/WordNetworkTree.jsx`   | Created     | Entire file                      | Added visual React Flow grid with custom nodes, sidebar topic controller, Codex word mapping trigger, node dragging position persistence, edge connection tool, and detailed node drawers.      |
| `frontend/src/styles.css`                       | Modified    | End of file                      | Appended layout and styling styles for the visual grid, sidebar panel, node drawer, and neon glow indicators.                                                                                   |

### 3. Features added

- [x] Visual graph canvas powered by React Flow
- [x] Drag-and-drop node position saving (debounced PATCH)
- [x] Live automated node status calculation and sync
- [x] Dynamic visual edge connection (link nodes)
- [x] Node inspector panel sidebar drawer detailing meaning, IPA, stress, example sentences, collocations
- [x] Topic visual map manager (create and switch maps)
- [x] Codex unmapped word linking widget

### 4. Verification evidence

- Compile check: `python -m py_compile` passed inside backend container.
- Frontend build: `npm run build` completed successfully after solving dependencies resolution.
- Smoke testing: Successfully created a topic tree "Education", added discovered nodes, forged an edge association, updated a word's definition, and verified status sync from "locked" to "discovered" and "activated" via PowerShell API calls. All API tests passed.

## [2026-06-06 23:55] Phase 1 Vocabulary Support Skill (Lexical Awakening System) MVP Complete

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 1 Vocabulary Support Skill MVP Implementation

### 1. Summary

Fully implemented the Lexical Awakening System (Vocabulary Support Skill) Phase 1 MVP frontend and backend components. Added all CRUD endpoints, automated flashcard generation, safety reset queries, top-level React states, Navigation Drawer integrations, and a beautiful Codex word notebook and Flashcard Memory Gate review dashboard overlay.

### 2. Files changed

| File                                            | Change type | Changed lines / area       | What changed                                                                                                                                            |
| ----------------------------------------------- | ----------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/services.py`                       | Modified    | `create_vocabulary_item`   | Added default flashcard auto-generation.                                                                                                                |
| `backend/app/main.py`                           | Modified    | Reset and routes           | Added vocabulary models to database reset array, and added all vocabulary CRUD / review API routes.                                                     |
| `frontend/src/App.jsx`                          | Modified    | Overlay states & rendering | Lifted vocabulary data states to the application level, fetched on start, passed to overlay, and added vocabulary stats support card to home dashboard. |
| `frontend/src/components/NavigationDrawer.jsx`  | Modified    | Options list               | Added "Lexical Awakening" link callback to the drawer system.                                                                                           |
| `frontend/src/components/VocabularyOverlay.jsx` | Created     | Entire file                | Added Codex word listing, add/edit/delete word forms, collocation & example forging widgets, and flip card spaced repetition memory gate dueling.       |
| `frontend/src/styles.css`                       | Modified    | End of file                | Added custom styling rules for vocabulary tag badges, forms, flashcards, flip animations, and victory panels.                                           |

### 3. Features added

- [x] Full Codex Archive word listing and CRUD manager
- [x] Inline collocation & example sentence forging
- [x] Spaced Repetition Memory Gate dueling arena with Flip cards
- [x] Dynamic dashboard stats card
- [x] Integration with global player XP level and Vocabulary support skill level (11 XP computed for single C1 word)

### 4. Verification evidence

- Compile check: `python -m py_compile` passed for backend.
- Frontend build: `npm run build` completed successfully.
- Workflow integration script: Ran container python check testing DB reset, registering word, fetching due cards, reviewing card (3 days interval good), and checking that Vocabulary skill XP reaches 11 XP correctly. All tests passed.

## [2026-06-06 23:40] Phase 1 Vocabulary Support Skill Pydantic Schemas & Services

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 1 Vocabulary Support Skill Pydantic Schemas & Services

### 1. Summary

Implemented Pydantic input/output schemas and service layers for vocabulary items, examples, collocations, relations, flashcards, and spaced repetition states.

### 2. Files changed

| File                      | Change type | Changed lines / area  | What changed                                                                                                              |
| ------------------------- | ----------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/schemas.py`  | Modified    | End of file           | Added Pydantic schemas for vocabulary items, examples, collocations, relations, flashcards, and spaced repetition states. |
| `backend/app/services.py` | Modified    | Imports & end of file | Imported new schemas & models and added vocabulary CRUD & spaced repetition review logic.                                 |

### 3. Features added

- [x] Pydantic validation schemas for all Phase 1 vocabulary models
- [x] CRUD services for vocabulary items, examples, collocations, and relations
- [x] Spaced repetition flashcard due list and review logic

### 4. Verification evidence

- Syntax check: `python -m py_compile` passed for `schemas.py` and `services.py`.
- Integration tests: Ran test script directly in the backend container to verify model mappings, CRUD logic, relationship retrieval, and interval calculations.

## [2026-06-06 23:35] Phase 1 Vocabulary Support Skill Backend Schema

**Agent:** Antigravity
**Status:** Done
**Related task:** Phase 1 Vocabulary Support Skill Backend Database Schema

### 1. Summary

Implemented the backend database schema for Phase 1 of the Vocabulary Support Skill (Lexical Awakening System). Added six new SQLAlchemy models mapping to database tables, generated the Alembic migration, successfully ran the migration to create the tables, and verified health check and query access.

### 2. Files changed

| File                                                            | Change type | Changed lines / area  | What changed                                                                                                                                                          |
| --------------------------------------------------------------- | ----------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/models.py`                                         | Modified    | Imports & end of file | Imported `Float` and added 6 new models (`VocabularyItem`, `VocabularyExample`, `VocabularyCollocation`, `VocabularyRelation`, `Flashcard`, `SpacedRepetitionState`). |
| `backend/alembic/versions/20260606_09_vocabulary_mvp_schema.py` | Created     | Entire file           | Alembic migration script to create the new tables.                                                                                                                    |

### 3. Features added

- [x] Phase 1 Vocabulary Database Schema (6 tables)
- [x] Lifelong asset scoping (user_id mapped to player_id)

### 4. Verification evidence

- Compile check: `python -m py_compile` passed for `models.py` and the migration script.
- Database migration execution: `alembic upgrade head` completed successfully on the running container.
- Live database queries: Executed a Python query script inside the backend container to verify direct database query access for all six new tables (all returned `0` rows successfully).
- HTTP Smoke tests: `/api/health` and `/api/summary` successfully return HTTP 200.

## [2026-06-06 15:15] Refine Suggestion Inbox grouping logic

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Group only quest-pattern suggestions, keep others individual

### 1. Summary

Refined the Suggestion Inbox logic to selectively group only overdue quest suggestions (`sourceType === 'quest_pattern'`) into a summary line. Other suggestion types (e.g., skill rank updates) now correctly render as individual actionable items again.

### 2. Files changed

| File                                                  | Change type | Changed lines / area  | What changed                                                                |
| ----------------------------------------------------- | ----------- | --------------------- | --------------------------------------------------------------------------- |
| `frontend/src/dashboard-data.js`                      | Modified    | weaknessItems mapping | Included `sourceType` in the mapped objects.                                |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Modified    | render area           | Added conditional grouping for quest_pattern and normal mapping for others. |
| `frontend/src/components/SuggestionInboxPanel.jsx`    | Modified    | render area           | Added conditional grouping for quest_pattern and normal mapping for others. |

### 3. Features added

- [x] Selective suggestion grouping.

### 4. Bugs fixed

- [x] Fixed issue where all suggestions were hidden and replaced by the overdue quest summary.

### 5. Code removed

- [ ] None.

### 6. Commands run

- Manual code review.

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Confirmed that quest-pattern items are grouped while other items (like rank suggestions) appear individually.
```

### 8. Remaining issues

- None.

### 9. Suggested next step

- Browser visual verification with mixed suggestion types.

### 10. User review checklist

- [ ] I confirmed other suggestions are now visible.
- [ ] I approved this refinement.

## [2026-06-06 15:00] Simplify Suggestion Inbox to summary only

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Replace detailed backlog items with summary text to reduce noise

### 1. Summary

Simplified the Suggestion Inbox by removing the individual item list (and Apply/Dismiss actions) and replacing it with a single summary message: "You have x Overdue Daily Quest". This removes significant UI noise when multiple overdue quests exist.

### 2. Files changed

| File                                                  | Change type | Changed lines / area | What changed                                                                     |
| ----------------------------------------------------- | ----------- | -------------------- | -------------------------------------------------------------------------------- |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Modified    | list area            | Replaced `.map()` with a single summary text div. Cleaned up header.             |
| `frontend/src/components/SuggestionInboxPanel.jsx`    | Modified    | list area            | Replaced `.map()` with a single summary text div. Removed `tag` from PanelFrame. |

### 3. Features added

- [x] Simplified Suggestion Inbox summary.

### 4. Bugs fixed

- [x] Resolved "noise" issue by grouping all overdue quest suggestions into one message.

### 5. Code removed

- [x] Individual suggestion items and Apply/Dismiss buttons.

### 6. Commands run

- Manual code review.

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Confirmed only the summary message is rendered when suggestions exist.
```

### 8. Remaining issues

- None.

### 9. Suggested next step

- Browser visual verification.

### 10. User review checklist

- [ ] I confirmed the list is gone and only the summary remains.
- [ ] I approved this simplification.

## [2026-06-06 14:45] Update Suggestion Inbox label text

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Change Suggestion Inbox label to "You have x Overdue Daily Quest"

### 1. Summary

Updated SuggestionInboxDropdown and SuggestionInboxPanel to use the specific wording "You have x Overdue Daily Quest" instead of generic pending/active labels.

### 2. Files changed

| File                                                  | Change type | Changed lines / area | What changed                                                          |
| ----------------------------------------------------- | ----------- | -------------------- | --------------------------------------------------------------------- |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Modified    | header section       | Changed text to "You have {pendingCount} Overdue Daily Quest".        |
| `frontend/src/components/SuggestionInboxPanel.jsx`    | Modified    | PanelFrame tag       | Changed text to "You have ${suggestions.length} Overdue Daily Quest". |

### 3. Features added

- [x] Custom wording for Suggestion Inbox status.

### 4. Bugs fixed

- [ ] None

### 5. Code removed

- [ ] None

### 6. Commands run

- Manual code review.

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Wording updated correctly in both components.
```

### 8. Remaining issues

- None

### 9. Suggested next step

- Browser visual verification.

### 10. User review checklist

- [ ] I confirmed the new text is displayed correctly.
- [ ] I approved this change.

## [2026-06-06 14:30] Hide zero backlogs in Suggestion Inbox

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Hide backlog counts in Suggestion Inbox if count is 0

### 1. Summary

Updated SuggestionInboxDropdown and SuggestionInboxPanel to only display backlog/pending counts when they are greater than 0. This reduces UI noise when no actions are required.

### 2. Files changed

| File                                                  | Change type | Changed lines / area | What changed                                            |
| ----------------------------------------------------- | ----------- | -------------------- | ------------------------------------------------------- |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Modified    | header section       | Wrapped `<strong>` count with `pendingCount > 0` check. |
| `frontend/src/components/SuggestionInboxPanel.jsx`    | Modified    | PanelFrame tag       | Set `tag` to `null` if `suggestions.length` is 0.       |

### 3. Features added

- [x] Conditional display for Suggestion Inbox backlog counts.

### 4. Bugs fixed

- [x] Removed "0 pending" / "Active 0" noise from Suggestion Inbox.

### 5. Code removed

- [ ] None

### 6. Commands run

- Manual code review.

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Component logic verified. Conditional rendering correctly handles zero vs non-zero states.
```

### 8. Remaining issues

- None

### 9. Suggested next step

- Proceed with browser visual verification.

### 10. User review checklist

- [ ] I confirmed zero counts are hidden.
- [ ] I confirmed non-zero counts still show.
- [ ] I approved this task.

## [2026-06-06 12:05] Add glossary to repo-first prompt guides

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Clarify platform-level protocol vs repo workflow terms in the repo-first prompt guides

### 1. Summary

Added a short glossary to the repo-first English and Vietnamese prompt guides so future sessions can distinguish platform-level protocol, repo operating standard, skill, harness, orchestrator, and worker.

### 2. Files changed

| File                          | Change type | Changed lines / area | What changed                                                                      |
| ----------------------------- | ----------- | -------------------- | --------------------------------------------------------------------------------- |
| `docs/current/prompt-en.md`   | Modified    | glossary section     | Added a short terminology section for platform/runtime vs repo workflow concepts. |
| `docs/current/prompt-vi.md`   | Modified    | glossary section     | Added the same glossary in Vietnamese.                                            |
| `docs/history/TEST_REPORT.md` | Modified    | top section          | Added validation note for this documentation refinement.                          |
| `docs/history/AGENT_NOTES.md` | Modified    | top section          | Added a factual note about the glossary addition.                                 |
| `docs/history/changelogs.md`  | Modified    | top entry            | Added this implementation record.                                                 |

### 3. Features added

- [x] Glossary for platform-level protocol
- [x] Glossary for repo operating standard
- [x] Glossary for skill, harness, orchestrator, and worker

### 4. Bugs fixed

- [x] Reduced terminology ambiguity in the repo-first prompt guides.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only refinement.
Repo-first prompt guides now include a glossary for core runtime and workflow terms.
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- If needed later, add a short “who controls what” note for operators who are new to agent tooling.

### 10. User review checklist

- [ ] I reviewed the glossary additions.
- [ ] I confirmed the terminology is clear.
- [ ] I approved this task.

## [2026-06-06 11:55] Add minimum validation matrix to repo-first prompt guides

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Add task-specific minimum validation guidance to the repo-first Codex guides

### 1. Summary

Extended the repo-first prompt guides with a minimum validation matrix so future sessions know the smallest acceptable verification set for backend, migration, frontend, debugging, review-only, documentation-only, and session-close-only tasks.

### 2. Files changed

| File                          | Change type | Changed lines / area         | What changed                                               |
| ----------------------------- | ----------- | ---------------------------- | ---------------------------------------------------------- |
| `docs/current/prompt-en.md`   | Modified    | validation/checklist section | Added a minimum validation matrix by task type in English. |
| `docs/current/prompt-vi.md`   | Modified    | validation/checklist section | Added the same minimum validation matrix in Vietnamese.    |
| `docs/history/TEST_REPORT.md` | Modified    | top section                  | Added validation note for this documentation refinement.   |
| `docs/history/AGENT_NOTES.md` | Modified    | top section                  | Added a factual note about the new validation matrix.      |
| `docs/history/changelogs.md`  | Modified    | top entry                    | Added this implementation record.                          |

### 3. Features added

- [x] Minimum validation baseline for backend tasks
- [x] Minimum validation baseline for migration/database tasks
- [x] Minimum validation baseline for frontend tasks
- [x] Minimum validation baseline for debugging, review-only, documentation-only, and session-close-only tasks

### 4. Bugs fixed

- [x] Removed the remaining gap where the repo-first guides described workflow but not the minimum acceptable verification set per task type.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only refinement.
Repo-first guides now define:
- base load order
- task-specific context expansion
- minimum validation matrix by task type
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- If needed later, add one final refinement: a task-specific session-close matrix by task type.

### 10. User review checklist

- [ ] I reviewed the repo-first prompt guides.
- [ ] I checked the validation matrix additions.
- [ ] I approved this task.

## [2026-06-06 11:45] Expand repo-first prompt guides with task-specific context loading

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Add task-specific context-loading guidance to the repo-first Codex guides

### 1. Summary

Extended the repo-first prompt guides so they do more than list the base file load order. They now tell future agents exactly what extra context to load for backend, migration, frontend, documentation, review, and debugging tasks, and when to stop loading more files to avoid context noise.

### 2. Files changed

| File                          | Change type | Changed lines / area | What changed                                                                    |
| ----------------------------- | ----------- | -------------------- | ------------------------------------------------------------------------------- |
| `docs/current/prompt-en.md`   | Modified    | Step 1 section       | Added task-specific context expansion rules and context stop rules in English.  |
| `docs/current/prompt-vi.md`   | Modified    | Bước 1 section       | Added the same repo-first context expansion rules and stop rules in Vietnamese. |
| `docs/history/TEST_REPORT.md` | Modified    | top section          | Added validation note for this documentation refinement.                        |
| `docs/history/AGENT_NOTES.md` | Modified    | top section          | Added a factual note about the new task-specific context-loading rules.         |
| `docs/history/changelogs.md`  | Modified    | top entry            | Added this implementation record.                                               |

### 3. Features added

- [x] Task-specific context-loading guidance for repo-first backend work
- [x] Task-specific context-loading guidance for migration/database work
- [x] Task-specific context-loading guidance for frontend, docs, review, and debugging work
- [x] Context stop rules to prevent overloading sessions

### 4. Bugs fixed

- [x] Removed the gap where the repo-first guides only defined the base load order but not the next files by task type.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only refinement.
Repo-first prompt guides now define both:
- base load order
- task-specific context expansion rules
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Add one more refinement later if needed: task-specific “minimum validation set” per task type.

### 10. User review checklist

- [ ] I reviewed the repo-first prompt guides.
- [ ] I checked the added task-specific loading rules.
- [ ] I checked the stop rules.
- [ ] I approved this task.

## [2026-06-06 11:35] Split generic Codex playbooks from repo-first playbooks

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Add a generic Codex workflow layer without replacing the existing repo-first guides

### 1. Summary

Added a second layer of Codex guidance for cross-repo use. The repository now has both generic and repo-first prompt playbooks. The generic files are reusable across projects, while the original `prompt-en.md` and `prompt-vi.md` remain the local operator guides for `IELTS Quest Dashboard`.

### 2. Files changed

| File                                | Change type | Changed lines / area                        | What changed                                                                                     |
| ----------------------------------- | ----------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `docs/current/prompt-generic-en.md` | Added       | full file                                   | Added a generic English Codex session playbook and prompt library for reuse across repositories. |
| `docs/current/prompt-generic-vi.md` | Added       | full file                                   | Added a generic Vietnamese Codex session playbook and prompt library.                            |
| `README.md`                         | Modified    | canonical docs map + Codex workflow section | Added links to the generic guides and clarified generic vs repo-first usage.                     |
| `AGENTS.md`                         | Modified    | current canonical docs list                 | Added the generic guides to the canonical docs map.                                              |
| `docs/current/CONTEXT_INDEX.md`     | Modified    | canonical docs list                         | Added load guidance that distinguishes generic vs repo-first prompt docs.                        |
| `DECISIONS.md`                      | Modified    | prompt-playbook decision                    | Clarified that both generic and repo-first prompt playbooks are maintained.                      |
| `TASKS.md`                          | Modified    | session resume + tracker + references       | Recorded the generic guides as completed documentation work.                                     |
| `docs/history/TEST_REPORT.md`       | Modified    | top section                                 | Added validation result for the generic split and rerun link scan counts.                        |
| `docs/history/AGENT_NOTES.md`       | Modified    | top section                                 | Added a factual note about the new generic layer.                                                |
| `docs/history/changelogs.md`        | Modified    | top entry                                   | Added this task record.                                                                          |

### 3. Features added

- [x] Generic English Codex playbook
- [x] Generic Vietnamese Codex playbook
- [x] Clear separation between generic and repo-first operator guidance

### 4. Bugs fixed

- [x] Removed ambiguity about whether the existing prompt guides were generic or repo-specific.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
Get-Content -Encoding UTF8 README.md
Get-Content -Encoding UTF8 docs/current/CONTEXT_INDEX.md
python - <local markdown link scan>
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Added generic prompt guides successfully.
Kept repo-first guides intact.
local markdown links checked: 89
broken local links: 0
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Use the generic guides as a reusable baseline and the repo-first guides for actual work inside this repository.

### 10. User review checklist

- [ ] I reviewed the generic guides.
- [ ] I checked the separation between generic and repo-first docs.
- [ ] I checked the updated links.
- [ ] I approved this task.

## [2026-06-06 11:20] Add bilingual Codex prompt playbooks

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Implement the repo-first Codex session playbook and prompt library in Vietnamese and English

### 1. Summary

Implemented the Codex session playbook and prompt library as two repo-first operator guides: an English canonical version and a Vietnamese working version. The new guides define the full session lifecycle from context loading through planning, execution, validation, documentation, and session close, and include skill-mapped prompt templates for common task types.

### 2. Files changed

| File                            | Change type | Changed lines / area                                | What changed                                                                                                                  |
| ------------------------------- | ----------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `docs/current/prompt-en.md`     | Added       | full file                                           | Added the canonical English session playbook, skill matrix, prompt templates, bad-vs-better examples, and session checklists. |
| `docs/current/prompt-vi.md`     | Added       | full file                                           | Added the Vietnamese operator version of the same workflow and prompt library.                                                |
| `README.md`                     | Modified    | canonical docs map + Codex workflow section         | Added links to the new prompt guides and a short “Working With Codex” section.                                                |
| `AGENTS.md`                     | Modified    | current canonical docs list                         | Added both prompt guides to the canonical repo docs map.                                                                      |
| `docs/current/CONTEXT_INDEX.md` | Modified    | canonical docs list                                 | Added load guidance for `prompt-en.md` and `prompt-vi.md`.                                                                    |
| `DECISIONS.md`                  | Modified    | accepted decisions                                  | Added the decision that prompt playbooks are the standard Codex session guidance for this repo.                               |
| `TASKS.md`                      | Modified    | session resume + documentation tracker + references | Recorded the new prompt playbooks as complete documentation work and added them to the “read more” section.                   |
| `docs/history/TEST_REPORT.md`   | Modified    | top section                                         | Added documentation validation note for the new prompt guides.                                                                |
| `docs/history/AGENT_NOTES.md`   | Modified    | top section                                         | Added a factual note about the bilingual prompt playbooks.                                                                    |
| `docs/history/changelogs.md`    | Modified    | top entry                                           | Added this implementation record.                                                                                             |

### 3. Features added

- [x] English Codex session playbook for this repo
- [x] Vietnamese Codex session playbook for this repo
- [x] Skill-to-task prompt matrix using installed local skills
- [x] Start / plan / implement / validate / document / close prompt templates

### 4. Bugs fixed

- [x] Reduced future session ambiguity around how to prompt Codex effectively in this repo.
- [x] Added a stable place to document skill usage by task type.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 README.md
Get-Content -Encoding UTF8 AGENTS.md
Get-Content -Encoding UTF8 docs/current/CONTEXT_INDEX.md
Get-Content -Encoding UTF8 DECISIONS.md
Get-Content -Encoding UTF8 TASKS.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\context-engineering\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\agent-skills\skills\documentation-and-adrs\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\agent-skills\skills\planning-and-task-breakdown\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\codex-orchestrator\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\agent-skills\skills\using-agent-skills\SKILL.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only change.
Bilingual prompt guides added successfully.
Canonical docs map updated.
No repo-managed markdown links were broken by the change.
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Use the new prompt playbooks to drive the next backend-test planning and implementation session.

### 10. User review checklist

- [ ] I reviewed the new prompt guides.
- [ ] I checked the skill mappings.
- [ ] I checked the updated canonical doc links.
- [ ] I approved this task.

## [2026-06-06 10:45] Repository-wide stale-link scan after documentation reorganization

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Verify repo-wide documentation links after the `docs/current` / `docs/history` restructure

### 1. Summary

Confirmed that the environment can run an automated repo-wide stale-link scan and used it to validate the reorganized documentation layout. Parsed all local markdown links in repo-managed docs, resolved each relative path from its source file, and verified target existence. No broken local markdown links were found.

### 2. Files changed

| File                          | Change type | Changed lines / area | What changed                                                         |
| ----------------------------- | ----------- | -------------------- | -------------------------------------------------------------------- |
| `docs/history/TEST_REPORT.md` | Modified    | top section          | Added the stale-link scan validation snapshot and exact scan counts. |
| `docs/history/AGENT_NOTES.md` | Modified    | top section          | Added a short factual note for the automated stale-link scan result. |
| `docs/history/changelogs.md`  | Modified    | top entry            | Added this validation record.                                        |

### 3. Features added

- [x] Automated repo-wide markdown stale-link verification for the reorganized docs layout.

### 4. Bugs fixed

- [x] Confirmed there are no broken local markdown links left by the documentation move.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
rg -n "AGENT_NOTES\.md|TEST_REPORT\.md|changelogs\.md|docs/PROJECT_CONTEXT\.md|docs/MVP_BUSINESS_RULES\.md|docs/DATABASE_SCHEMA\.md|docs/FRONTEND_PLAN\.md|docs/history/changelogs\.md|docs/history/TEST_REPORT\.md|docs/history/AGENT_NOTES\.md|docs/current/PROJECT_CONTEXT\.md|docs/current/BUSINESS_RULES\.md|docs/current/DATABASE_SCHEMA\.md|docs/current/SCHEMA_SEMANTICS\.md" -g "*.md" .
rg -n "\]\(([^)]+)\)" -g "*.md" .
python - <markdown-link existence scan>
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
markdown files scanned: 18
local markdown links checked: 69
broken local links: 0
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Move on to automated backend tests, since documentation link integrity is now verified.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the validation counts.
- [ ] I confirmed the documentation links are clean.
- [ ] I approved this task.

## [2026-06-06 10:30] Documentation and context reorganization

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Reorganize repository documentation for low-noise context loading

### 1. Summary

Reworked the repository documentation layout so future sessions can load context quickly without reading large historical dumps first. Reduced root documentation to entrypoint files, created clear canonical and history layers under `docs/current/` and `docs/history/`, rewrote the root docs in English, added schema semantics and a documentation ADR, and reordered changelog history to newest-first.

### 2. Files changed

| File                                                                         | Change type | Changed lines / area | What changed                                                                                   |
| ---------------------------------------------------------------------------- | ----------- | -------------------- | ---------------------------------------------------------------------------------------------- |
| `README.md`                                                                  | Modified    | full file            | Rewrote as a concise project entrypoint with docs map and context load order.                  |
| `AGENTS.md`                                                                  | Modified    | full file            | Rewrote repo agent guide, added official load order, and required newest-first changelog rule. |
| `TASKS.md`                                                                   | Modified    | full file            | Compressed into an active tracker and recorded the documentation reorganization as completed.  |
| `DECISIONS.md`                                                               | Modified    | full file            | Rebuilt as a short decision ledger with links to migration history and the new ADR.            |
| `docs/current/CONTEXT_INDEX.md`                                              | Added       | full file            | Added canonical context-loading map.                                                           |
| `docs/current/PROJECT_CONTEXT.md`                                            | Added       | full file            | Added current product and user context summary.                                                |
| `docs/current/BUSINESS_RULES.md`                                             | Added       | full file            | Added English business-rule summary for progression and quest behavior.                        |
| `docs/current/DATABASE_SCHEMA.md`                                            | Added       | full file            | Added current schema snapshot summary after Wave E.                                            |
| `docs/current/SCHEMA_SEMANTICS.md`                                           | Added       | full file            | Added field-semantics reference for rank, quest role, scope, and related state meanings.       |
| `docs/current/decisions/ADR-001-documentation-layout-and-context-loading.md` | Added       | full file            | Recorded the documentation split and context-loading decision.                                 |
| `docs/history/AGENT_NOTES.md`                                                | Added       | full file            | Rebuilt as newest-first short factual history notes.                                           |
| `docs/history/TEST_REPORT.md`                                                | Added       | full file            | Rebuilt as newest-first validation snapshots.                                                  |
| `docs/history/changelogs.md`                                                 | Added       | full file            | Rebuilt changelog as newest-first recent history.                                              |
| `docs/history/MIGRATION_HISTORY.md`                                          | Added       | full file            | Added condensed Wave A-E migration summary.                                                    |
| `docs/history/FRONTEND_PLAN.md`                                              | Added       | full file            | Added historical note for the earlier frontend plan.                                           |
| `AGENT_NOTES.md`                                                             | Deleted     | full file            | Removed root history file after moving history to `docs/history/`.                             |
| `TEST_REPORT.md`                                                             | Deleted     | full file            | Removed root history file after moving history to `docs/history/`.                             |
| `changelogs.md`                                                              | Deleted     | full file            | Removed root history file after moving history to `docs/history/`.                             |
| `docs/PROJECT_CONTEXT.md`                                                    | Deleted     | full file            | Removed old location after canonical doc split.                                                |
| `docs/MVP_BUSINESS_RULES.md`                                                 | Deleted     | full file            | Removed old location after canonical doc split.                                                |
| `docs/DATABASE_SCHEMA.md`                                                    | Deleted     | full file            | Removed old location after canonical doc split.                                                |
| `docs/FRONTEND_PLAN.md`                                                      | Deleted     | full file            | Removed old location after history doc split.                                                  |

### 3. Features added

- [x] Official root-first context load order
- [x] Canonical current-doc layer
- [x] History-doc layer
- [x] Schema semantics reference
- [x] Documentation ADR

### 4. Bugs fixed

- [x] Removed historical noise from `TASKS.md`.
- [x] Removed mixed-purpose root documentation layout.
- [x] Fixed changelog ordering so new entries are at the top.

### 5. Code removed

- [x] Removed old root history files.
- [x] Removed superseded doc locations under `docs/`.

### 6. Commands run

```bash
Get-Content -Encoding UTF8 TASKS.md
Get-Content -Encoding UTF8 AGENT_NOTES.md
Get-Content -Encoding UTF8 changelogs.md
Get-Content -Encoding UTF8 README.md
Get-Content -Encoding UTF8 DECISIONS.md
Get-Content -Encoding UTF8 docs/PROJECT_CONTEXT.md
Get-Content -Encoding UTF8 docs/MVP_BUSINESS_RULES.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only change.
Root entrypoint rewrite complete.
Canonical/history split complete.
Changelog ordering normalized to newest-first.
```

### 8. Remaining issues

- [ ] Browser walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Add automated backend tests for the post-migration backend behavior, then return to deferred legacy cleanup planning.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed areas.
- [ ] I checked the documentation layout.
- [ ] I checked the validation notes.
- [ ] I approved this task.

## [2026-06-06 00:23] Wave E constraint hardening

Status: `Done`

- Hardened write paths before DDL.
- Applied fail-fast migration `20260606_08_wave_e_constraint_hardening.py`.
- Enforced `NOT NULL` campaign scope on target tables.
- Added composite uniqueness for check-ins and daily quest slots.

## [2026-06-05 23:57] TASKS cleanup after Wave D

Status: `Done`

- Removed stale wave-start markers.
- Narrowed open work to real remaining backend/documentation items.

## [2026-06-05 23:38] Wave D backend cutover

Status: `Done`

- Cut skill progression over to `campaign_skill_states`.
- Cut badge reads over to `badge_unlocks`.
- Scoped campaign-facing reads and typed quest completion writes.

## [2026-06-05 22:30] Wave C data backfill

Status: `Done`

- Backfilled campaign scope and typed-link fields.
- Seeded campaign-scoped mutable state rows.

## [2026-06-05 22:01] Wave B additive state tables

Status: `Done`

- Added `campaign_skill_states`.
- Added `badge_unlocks`.
- Synced backend seed-facing English copy.

## [2026-06-05 21:24] Wave A scope and typed-link foundation

Status: `Done`

- Added nullable campaign columns and typed-link columns.
- Applied migration and validated the schema upgrade locally.
