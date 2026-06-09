# Completed Tasks

Last updated: `2026-06-09` (session 8k — Main Quest Start-Date Rebase: MQ-1/2/3 + live smoke ✓)

## Session 8k — Main Quest Start-Date Rebase (lazy-purring-sundae.md)

> **Bug fixed:** Main quest dates were hard-anchored to `2026-06-04`. Picking any other onboarding start date left main-quest `quest_date` on the material.md absolute dates → first main quests rendered **expired**. Root cause: `material/material.md` stores absolute session dates; `parse_material_plan()` read them verbatim into `StudyPlanSession.study_date`, and main quests copied that via `quest_date=session.study_date`. Daily quests were already rebased off `campaign.start_date`; study-plan weeks/sessions were not.

### Task MQ-1 — `MATERIAL_ANCHOR_DATE` + `rebase_material_date` helper *(gap-check [x])*
- **File:** `backend/app/seed.py`
- Added `MATERIAL_ANCHOR_DATE = date(2026, 6, 4)` (seed.py:78 — Week1/Session1 in material.md, a Thursday).
- Added pure helper `rebase_material_date(material_date, campaign_start) -> date` returning `campaign_start + (material_date - MATERIAL_ANCHOR_DATE)` (seed.py:81-82). No DB.
- **Verified:** identity case `rebase(2026-06-04, 2026-06-04)==2026-06-04`; offset case `rebase(2026-06-06, 2026-07-15)==2026-07-17` (+2 preserved). PASS.

### Task MQ-2 — Rebase week + session dates + weekday label in `ensure_study_plan` *(gap-check [x])*
- **File:** `backend/app/seed.py` (`ensure_study_plan`, ~1126-1196)
- Week create + **update** branch: `week_start`/`week_end` wrapped in `rebase_material_date(..., campaign.start_date)`.
- Session create + **update** branch: `study_date` rebased; `weekday_label = rebased_date.strftime("%A")` (overrides material text, always matches real weekday).
- Existing-row update branches added (week + session) → re-seed self-heals dates.
- Main quests need no change — `quest_date=session.study_date` (seed.py:1511) inherits the rebased value.
- **Verified (live smoke):** campaign `start_date=2026-06-15` (Monday) → S1=2026-06-15, S2/S3/S4 = 17/19/21 (+0/+2/+4/+6); `weekday_label=Monday`; week1 start 2026-06-15, week2 2026-06-22 (+7, shares window with daily quests).
- **Risk cleared:** grep `test_backend.py` for literal weekday strings (`"Thursday"` etc.) → 0 hits; no test asserts material weekday labels.

### Task MQ-3 — Fallback start date `date.today()`, not stale `2026-06-04` *(gap-check [x])*
- **File:** `backend/app/seed.py` (`parse_start_date`, 2317-2321)
- Changed bare fallback from `"2026-06-04"` to `date.today()`; kept `APP_START_DATE` env override (`if raw: return date.fromisoformat(raw)` else `date.today()`).
- Container `docker-compose` sets `APP_START_DATE=2026-06-04` → demo seed stays deterministic via the override path; only the bare fallback changed.
- **Verified:** env unset → `parse_start_date()==date.today()`; env `2026-07-15` → returns that date.

### Latent gap fixed — `ensure_main_quest_instances` existing-branch date self-heal
- **File:** `backend/app/seed.py` (~1490)
- The existing-row branch of `ensure_main_quest_instances` updated title/xp/material but **not** `quest_date` → a re-seed of an existing campaign left main-quest dates stale.
- Added `existing.quest_date = session.study_date` + `existing.week_no = session.week_no` so re-seed keeps main-quest dates in sync with the rebased session date. (Dev path uses `/api/dev/reset` which deletes rows first; this is defensive for in-place re-seed.)

### Validated
- Backend suite: **61 passed, 0 failed** (`python -m pytest app/test_backend.py`).
- Live smoke: `/api/dev/reset` + register + `activate-campaign{start_date:2026-06-15}` → Main Quest #1 `pending` on 2026-06-15 (not expired); spacing/weekday/week-window all correct.
- No frontend change required (dates are backend-derived; FE renders status as-is).

---

## Session 8i — Task 18 Archived (Phase 10 — Frontend: Skill buff lines)

Last updated previously: `2026-06-09` (session 8i — Task 18 done; Checkpoint G ✓)

## Session 8i — Task 18 Archived (Phase 10 — Frontend: Skill buff lines)

### Task 18 — Skill cards render support sources as buff lines *(gap-check [x])*
- **Files:** `frontend/src/components/SkillCards.jsx`, `frontend/src/styles.css`
- `SupportBuffLines` component: renders each `support_breakdown` item as a one-liner `+N XP from {source}` (green when XP > 0; muted `—` when XP = 0). Full mode only — compact mode unchanged.
- Writing card → Grammar buff; Vocabulary card → Collocation buff. No rank/level badge on buff lines.
- Grammar/Collocation tile exclusion already enforced by backend `MATRIX_SKILLS`; no FE filter needed.
- CSS: `.skill-node__buffs` (flex-column, gap 4px), `.skill-node__buff--active` (var(--success)), `.skill-node__buff--empty` (var(--muted)).
- **Build:** ✓ 0 errors.

---

## Session 8h — Phase GAP-FIX-2: Tasks GAP-15-1 … GAP-15-4

### Task GAP-15-1 — Main quest XP reads `MainQuestXpPolicy` (closes hard-code path)

- **Root cause:** `infer_main_quest_xp` accepts `db=None` and reads `MainQuestXpPolicy` only when `db` is passed, but all 4 callsites in `ensure_main_quest_instances` (seed.py:1457, 1458, 1475, 1486) omitted `db=` → always used hard-coded tier values (45/35/25/60). Latent: hard-code values matched policy seed values.
- **Fix:** `backend/app/seed.py` — added `db=db` to all 4 `infer_main_quest_xp(...)` calls in `ensure_main_quest_instances`.
- **Test added:** `TestGap151MainQuestReadsPolicy.test_main_quest_xp_reads_policy_not_hardcode` — mutates `MainQuestXpPolicy.standard` 35→40, calls `infer_main_quest_xp(1, ..., db=db)`, asserts result=40 (policy read); also asserts result=35 when `db=None` (fallback intact). PASS.
- **Tasks closed:** GAP-15-1 gap-check → `[x]`.

### Task GAP-15-2 — `reset_database` wipes the 4 policy tables

- **Root cause:** `reset_database` delete-list in `main.py` omitted `RankXpThreshold`, `QuestXpPolicy`, `WeeklyMissionXpPolicy`, `MainQuestXpPolicy`. The `/api/dev/reset` endpoint never wiped them, masking future seed bugs.
- **Fix:** `backend/app/main.py` — added 4 policy models to imports and to the delete-list (placed before `Skill`, FK-safe).
- **Tasks closed:** GAP-15-2 gap-check → `[x]`.

### Task GAP-15-3 — All `WeeklyMissionXpPolicy` rows are reachable

- **Root cause:** `map_weekly_pattern_to_mission_type` only mapped 4 pattern codes (`balanced→listening_weekly`, `reading→reading_weekly`, `vocabulary→vocab_weekly`, `output→writing_weekly`). `speaking_weekly` and `grammar_weekly` policy rows (both XP=45) were dead — never read by any pattern.
- **Fix:** `backend/app/seed.py` — added two new pattern dicts in `weekly_mission_patterns` (`{phase_index}-speaking-focus` → `speaking_weekly`, `{phase_index}-grammar-focus` → `grammar_weekly`); added `"speaking"→speaking_weekly` and `"grammar"→grammar_weekly` branches to `map_weekly_pattern_to_mission_type` (before `"output"` branch to avoid early match).
- **Tests added:** `TestGap153WeeklyPolicyAllRowsReachable`:
  - `test_all_weekly_policy_mission_types_reachable` — asserts every `WeeklyMissionXpPolicy.mission_type` is reachable from at least one pattern code. PASS.
  - `test_speaking_weekly_missions_seeded` — asserts speaking_weekly missions exist after activate-campaign. PASS.
  - `test_grammar_weekly_missions_seeded` — asserts grammar_weekly missions exist after activate-campaign. PASS.
- **Tasks closed:** GAP-15-3 gap-check → `[x]`.

### Task GAP-15-4 — Fix stale spec-ref in Task 15 verification

- **Audit result:** No "Phase XP-3" or "§12 Phase XP-3 validation list" string existed in Task 15's Verification field — only in the description of GAP-15-4 itself. Self-resolved on audit.
- **Tasks closed:** GAP-15-4 gap-check → `[x]`.

### Validated

- Suite: **60 passed, 1 skipped, 0 failed** (+4 new tests: GAP-15-1 × 1, GAP-15-3 × 3).
- All GAP-15-1…4 gap-checks `[x]`. Task 15 gap-check `[x]`. Checkpoint GAP-2 `[x]`.

---

## Session 8h — Task 17 Archived (Phase 10 — Frontend: 9-slot Daily Board)

### Task 17 — 9-slot daily board + boss-lock badge *(gap-check [x])*
- **Files:** `frontend/src/components/DailyQuestPanel.jsx`, `frontend/src/components/QuestOverlay.jsx`, `frontend/src/App.jsx`, `frontend/src/styles.css`
- `SlotChip`: maps `daily_slot_code` → human label + accent colour per spec §5.1 slot table.
- `BossLockBadge`: reads `promotion_status` from skills array via `skillStatusMap` memoized in `DailyQuestPanel`. Shows amber lock badge when `promotion_status != "none"`. Writing/Speaking: backend never sets boss_required → badge never shows.
- `is-claim-ready` CSS: gold left-border + tinted background distinguishes completed-unclaimed from claimed.
- `skills` prop threaded: `App.jsx` → `QuestOverlay` → `DailyQuestPanel`.
- Summary card label updated "Daily Slots" (was "Daily Command"); total shows `max(slots, 9)`.
- **Build:** ✓ 0 errors.

---

## Session 8h — Task 16 Archived (Phase 10 — Frontend: Player Rank)

### Task 16 — Player shows RANK only; stale FE formulas removed *(gap-check [x])*
- **File:** `frontend/src/dashboard-data.js`
- Removed `PLAYER_RANK_THRESHOLDS` constant, `getPlayerLevel(totalXp)` fn, `getPlayerRank(totalXp)` fn.
- `buildDashboardView`: `level`/`rank` in player block now read `player.player_level` / `player.player_rank` from backend (no FE recompute).
- `buildPlayerSnapshot`: fallback chain no longer calls stale FE fns — uses `null`/`'F'` defaults.
- `getPlayerXpProgress`: default `level` param changed from `getPlayerLevel(totalXp)` → `1`.
- **Tests:** `npm run test:dashboard-data` 5/5 PASS; `npm run build` ✓ 222 modules 0 errors.
- **Gap noted:** `getPlayerXpProgress` body uses `(level-1)*120` curve (stale). Deferred — only affects progress bar width, not rank display.

---

## Session 8h — Task 15 Archived (Phase 9 — Policy Tables)

### Task 15 — Add + seed the 4 XP policy tables and read from them *(gap-check [x])*
- **Files:** `backend/app/seed.py`, `backend/app/main.py`, `backend/app/test_backend.py`, `backend/alembic/versions/20260609_17_add_policy_tables.py`
- Migration `20260609_17` creates `rank_xp_thresholds`, `quest_xp_policies`, `weekly_mission_xp_policies`, `main_quest_xp_policies` with unique indexes.
- `ensure_policy_tables` seeds all 4 tables with §2.3/§5.1/§6/§7 values; wired into `seed_database` + `activate_campaign_for_player`.
- Daily quests read `base_xp` from `QuestXpPolicy` via `ensure_templates`.
- Weekly missions read `reward_xp` from `WeeklyMissionXpPolicy` via pattern→mission_type mapping.
- Main quests read XP from `MainQuestXpPolicy` via `infer_main_quest_xp(db=db)` (GAP-15-1 fix).
- 4 policy tables wiped on `/api/dev/reset` (GAP-15-2 fix).
- All `WeeklyMissionXpPolicy` rows reachable (GAP-15-3 fix).
- `TestPolicyTables` (6 tests) + `TestGap151MainQuestReadsPolicy` (1 test) + `TestGap153WeeklyPolicyAllRowsReachable` (3 tests) — all PASS.

---

## Session 8g — Phase GAP-FIX: Tasks GAP-1 and GAP-2

### Task GAP-1 — `support_breakdown` excludes Main Quest XP

- **Root cause:** `get_campaign_skill_outputs` (main.py ~line 340) queried **all** claimed Grammar/Collocation quests to compute `support_xp_by_name`, but `recompute_skill_progress` (services.py:728) folds only **non-Main** support quests into the matrix skill XP. This made `support_breakdown.xp` disagree with the XP actually inside `state.xp` when a Grammar/Collocation Main Quest existed — violating the Task 5/6 "no double-count" contract.
- **Fix:** `backend/app/main.py` `get_campaign_skill_outputs` ~line 341: added `Quest.session_type != "Main Quest"` to the `support_xp_by_name` filter.
- **Test added:** `test_gap1_support_breakdown_excludes_main_quest_xp` — seeds Grammar Main Quest (100 XP) + Grammar Daily (30 XP), asserts Writing `support_breakdown[Grammar].xp == 30` (Main excluded). PASS.
- **Tasks closed:** Tasks 5 and 6 gap-check → `[x]`.

### Task GAP-2 — Collocation seed allows intra-topic duplicate strings

- **Root cause:** `ensure_collocations` (seed.py ~line 2203) used `{item.collocation: item}` as the dedup dict, so two collocation items with the same string but different `item_order` in the same topic would drop the second — violating §9 "allow duplicates". Latent (real file has 0 dup-string topics; seeded count == 1409).
- **Fix:** `backend/app/seed.py` `ensure_collocations`: changed dedup key to `{(item.item_order, item.collocation): item}`; lookup uses `key = (item_data["item_order"], colloc)`; `else` branch now references `existing_items[key]`.
- **Test added:** `test_gap2_collocation_seed_allows_duplicate_strings_different_order` — patches `collocations_file_path` + `parse_collocations_file` with a fixture containing 2 items with identical collocation strings at `item_order=1` and `item_order=2`; asserts seeded count == 2 and idempotent second run == 2. PASS.
- **Tasks closed:** Tasks 13 and 14 gap-check → `[x]`.

### Validated

- Suite: **50 passed, 1 skipped, 0 failed** (was 48 before session 8g).
- All Tasks 5–14 gap-checks are now `[x]`. Archived below.

---

## Session 8g — Tasks 5–14 Archived (XP / Level / Rank Redesign — Phases 3–8)

### Task 5 — Route Grammar quest XP into Writing *(gap-check [x])*
- **Files:** `backend/app/services.py`, `backend/app/schemas.py`, `backend/app/main.py`
- `SUPPORT_ROUTING = {Grammar: Writing, Collocation: Vocabulary}` in services.py.
- `recompute_skill_progress` folds non-Main Grammar quest XP into Writing matrix state.
- `/summary` Writing entry exposes `support_breakdown: [{source:"Grammar", xp:N}]` (no double-count).
- Grammar excluded from MATRIX_SKILLS tile list.
- **Gap:** GAP-1 found (support_breakdown over-counted Main Quests) → fixed in Task GAP-1.

### Task 6 — Confirm Collocation routing into Vocabulary *(gap-check [x])*
- **Files:** `backend/app/services.py`, `backend/app/schemas.py`, `backend/app/main.py`
- Collocation quest XP (Daily only) folds into Vocabulary via SUPPORT_ROUTING.
- `/summary` Vocabulary entry exposes `support_breakdown: [{source:"Collocation", xp:N}]`.
- Collocation excluded from tile list; `compute_vocabulary_xp` adds +5 per collocation progression.
- **Gap:** same GAP-1 root cause → fixed in Task GAP-1.

### Task 7 — Cap data-entry vocab XP at 40/word *(gap-check [x])*
- **File:** `backend/app/services.py`
- `compute_vocabulary_xp`: data-entry per-word capped `min(data_entry_xp, 40)`; mastery `min(mastery_score, 50)` added on top.
- No gaps found in audit.

### Task 8 — Migration to widen daily_slot_code to 9 values *(gap-check [x])*
- **File:** `backend/alembic/versions/20260609_15_daily_slots_9.py`
- No-op placeholder: column already `String(20)`, no enum constraint. `upgrade()`/`downgrade()` both `pass`.
- No gaps found in audit.

### Task 9 — Daily quest generation produces 9 slots/day *(gap-check [x])*
- **File:** `backend/app/seed.py`
- `ensure_quest_instances` slot_mapping: Vocab 3 + Reading 1 + Listening 1 + Grammar 2 + Writing 1 + Speaking 1 = **9 slots/day**.
- Quota seed = 9; unique constraint `(campaign_id, quest_date, daily_slot_code)` enforces uniqueness.
- No gaps found in audit.

### Task 10 — Rewrite infer_main_quest_xp to tier by skill *(gap-check [x])*
- **File:** `backend/app/seed.py`
- `infer_main_quest_xp`: Writing/Speaking-heavy → 45; Listening/Reading → 35; Review/Error → 25; mock test → 60. Reads `MainQuestXpPolicy` when `db` passed.
- `test_main_quest_xp_and_routing` PASS.
- No gaps found in audit.

### Task 11 — Main Quest full-XP routing to every matrix skill in session *(gap-check [x])*
- **Files:** `backend/app/services.py`, `backend/app/seed.py`
- `resolve_main_quest_covered_skills`: S1→{Listening,Speaking}, S2→{Reading,Vocabulary}, S3→{Writing}, S4→primary.
- `recompute_skill_progress` credits full `earned_xp` to each covered skill; no double-count.
- `test_main_quest_xp_and_routing` green.
- No gaps found in audit.

### Task 12 — Make Writing/Speaking non-boss-gated *(gap-check [x])*
- **Files:** `backend/app/models.py`, `backend/alembic/versions/20260609_16_add_boss_gated_to_skills.py`, `backend/app/seed.py`, `backend/app/services.py`
- Migration adds `skills.boss_gated Boolean server_default=1`; seed sets Writing=False, Speaking=False, others=True.
- `recompute_skill_progress`: `if not state.skill.boss_gated` → auto-confirm rank, `promotion_status="none"`.
- `test_non_boss_gated_skills` green.
- No gaps found in audit.

### Task 13 — Collocation markdown parser *(gap-check [x])*
- **File:** `backend/app/seed.py` (`parse_collocations_file`)
- Parses 60 sections, 1409 items; `ancient monument` maps all 5 columns; tolerates noisy IPA.
- **Gap:** GAP-2 found at seed step (ensure_collocations dedup) → fixed in Task GAP-2.

### Task 14 — Idempotent seed of collocations + campaign link *(gap-check [x])*
- **File:** `backend/app/seed.py` (`ensure_collocations`)
- Seeds `CollocationCollection/Section/Topic/Item` + `CampaignCollocationLink`; get-or-create idempotent.
- `test_collocation_parser_and_seed` verifies stable count on two seeds + Vocabulary XP +5 per progression.
- **Gap:** GAP-2 → fixed: dedup key changed from `collocation` string to `(item_order, collocation)` tuple.

---

## Session 8d — Fix Pre-existing Certificate Suggestion Failures

### Bug: `test_manual_certificate_creation_pre_campaign` (0 suggestions after activate)
- **Root cause:** `activate_campaign` (main.py) linked pre-existing certs to the new campaign but never called `create_rank_suggestions_for_certificate`. Result: 0 suggestions.
- **Fix:** After `cert.campaign_id = campaign.id` + `db.flush()`, now calls `create_rank_suggestions_for_certificate(db, cert)` for each cert.

### Bug: `test_manual_certificate_creation_post_campaign` (4 != 7 suggestions)
- **Root cause:** `create_rank_suggestions_for_certificate` (services.py) only iterated 4 component skills. Vocabulary/Grammar/Collocation never got suggestions.
- **Fix:** Added `inferred = {Vocabulary, Grammar, Collocation: cert.overall_score}`. Merged with `components` before loop — all 7 skills create `SkillRankSuggestion`. Vocab/Grammar/Collocation rank derived from `map_ielts_score_to_rank(overall_score)`.

### Validated
- `TestCertificateAndSuggestionEndpoints` 4 tests: PASS
- Full suite: **44/44 PASS**

---

## Session 8c — XP/Level/Rank Redesign: Tasks 1–4 + Gap Fixes

### Task 1 — Replace rank threshold table with 60-level curve model
- **File:** `backend/app/services.py`
- **What:** Replaced 7-tuple `RANK_THRESHOLDS` with `_LEVEL_XP` (60-entry list from `xp(L)=round(19*(L^1.6-1))`). Added `level_from_xp(xp)->int`, `rank_from_level(L)->str` (10 levels/rank, S at L60 only), `get_rank_level(xp)->(rank,level)`. Kept `RANK_MIN_XP` dict (F=0, E=862, D=2460, C=4604, B=7212, A=10234, S=13279). Removed old `RANK_ORDER` constant tied to the flat 7-threshold model.
- **Verified:** `level_from_xp(0)=1`, `(862)=11`, `(13279)=60`; `get_rank_level(861)=("F",10)`, `(862)=("E",11)`, `(13279)=("S",60)`. Backend imports clean.
- **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §2.1–§2.3.

### Task 2 — Reconcile confirmed_rank floor with fine-grained level
- **File:** `backend/app/services.py`
- **What:** Replaced `next(lvl for _,r,lvl in RANK_THRESHOLDS if r==confirmed_rank)` with `_RANK_FIRST_LEVEL.get(state.confirmed_rank, 1)` in `recompute_skill_progress` (≈line 638) and `apply_rank_suggestion` (≈line 1047). Added `_RANK_FIRST_LEVEL` dict (F=1, E=11, D=21, C=31, B=41, A=51, S=60). No remaining stale tuple unpacking.
- **Verified:** `confirmed_rank="D"` → `state.level=21`, `state.xp` floored at 2460. Grep: 0 refs to old 3-element RANK_THRESHOLDS.
- **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §3, §2.2.

### Gap A — Dead code in seed.py (found during Task 1-2 audit)
- **File:** `backend/app/seed.py`
- **What:** Deleted stale `RANK_THRESHOLDS` block (lines 68–76) and dead `get_rank_level` function (lines 350–354) from seed.py. Both were copies of old code with wrong thresholds (3500=S, 200=E) and had no callers.
- **Verified:** Grep: 0 refs to `RANK_THRESHOLDS` or `get_rank_level` in seed.py.

### Gap B — Stale xp_threshold values in RankExamPool seed (found during Task 1-2 audit)
- **File:** `backend/app/seed.py`
- **What:** Updated `transitions` in `seed_rank_exam_pools()` to use canonical RANK_MIN_XP values (F→E=862, E→D=2460, D→C=4604, C→B=7212, B→A=10234, A→S=13279). Previously used old values (A→S=10000). Added idempotent update: if `pool.xp_threshold != thresh` then update.
- **Verified:** Seed values match `ielts_xp_policy_rank_quest_spec.md` §2.3 table exactly.

### Task 3 — Derive player_xp from 5 matrix skills; remove direct accrual
- **File:** `backend/app/services.py`
- **What:** Added `MATRIX_SKILLS = {"Listening", "Reading", "Writing", "Speaking", "Vocabulary"}`. Rewrote `recompute_player_progress` — no longer sums quest/mission/boss/vocab XP; instead averages 5 matrix skill CampaignSkillState.xp values (`round(mean(...))`). Updated `refresh_progress_state` to pass `state_map` to `recompute_player_progress` (ensures skills computed before player avg). Keeps streak/shield/perfect-day block intact.
- **Verified:** Mock test with skills=[1000,2000,0,0,0] → player_xp=600. Grammar/Collocation excluded from average. `/summary` player block = mean-derived.
- **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §1.2; `player_level.md` §1.

### Task 4 — Remove all direct player-XP accrual call sites
- **Files:** `backend/app/services.py`, `backend/app/main.py`
- **What:** `award_player_xp` made a no-op (function kept for import compat, body = `pass` + spec comment). In `main.py`, removed `else` branches that called `award_player_xp` for: weekly mission claim without `reward_skill_id`, boss claim without `reward_skill_id`. Check-in route already streak-only (confirmed by audit). No code path now increments `player.player_xp` directly.
- **Verified:** Grep `player_xp` — only derived assignment in `recompute_player_progress`. Boss/mission player-side `else` branches gone. Check-in: streak/shield updated, no XP call.
- **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §4, §1.2; `player_level.md` §1.

### Gap C — test_boss_reward_routing asserted old contract (found during Task 3-4 audit)
- **File:** `backend/app/test_backend.py`
- **What:** Updated `test_boss_reward_routing` part 2 to assert new spec behavior: boss with `reward_skill_id=None` creates NO `PlayerXpTransaction`, `player_xp` is UNCHANGED (not +500). Previous assertion tested the removed direct-accrual path.
- **Verified:** Test PASS.

### Gap D — Frontend stale player level/rank formulas (documented, deferred to Task 16)
- **File:** `frontend/src/dashboard-data.js` (≈line 568-569)
- **What:** `buildDashboardView` overwrites `player_level`/`player_rank` from backend by recomputing via `getPlayerLevel` (floor/120+1) and `getPlayerRank` (PLAYER_RANK_THRESHOLDS). After Task 3, `total_xp`=avg-5-skills, so these FE formulas give wrong results. **Not fixed here** — scoped to Task 16 (frontend phase).

### Gap E — total_xp semantic mismatch (documented, deferred to Task 16)
- **File:** `backend/app/main.py` (≈line 726)
- **What:** `total_xp = player.player_xp` — field name says "total" but value is now avg-5-skills. **Not fixed here** — scoped to Task 16.

### Test suite
- 42/44 pass. 2 remaining pre-existing failures: `test_manual_certificate_creation_pre_campaign` + `_post_campaign` (suggestion-infer logic incomplete, unrelated to Tasks 1–4).

## Session 8b — Boss-Gated Quest Claim XP Leak Fix

### Bug: `reward_claimed=True` leaking XP when skill is boss-blocked
- **Root cause:** `POST /api/quests/{id}/claim` (`main.py:~1015`) set `quest.reward_claimed=True` even when `skill_blocked=True`. Because `recompute_skill_progress` sums `earned_xp` of all `reward_claimed=True` quests, the XP leaked back into the skill state despite `award_skill_xp` being skipped.
- **Contract chosen:** option (a) — do NOT mark `reward_claimed=True` when skill is boss-blocked. The quest stays claimable; once the boss is beaten and `promotion_status` returns to `"eligible"`, the user can claim again and receive XP normally.
- **Fix:** `backend/app/main.py` (~line 1011): added early return path when `skill_blocked=True` — return the current (unchanged) quest without setting `reward_claimed` or calling `refresh_progress_state`.
- **Verified:** `TestRankExamPhase9.test_quest_claim_suppresses_xp_when_boss_required` → PASS; `test_quest_claim_awards_xp_normally_when_eligible` → PASS. Both run inside the container via `python -m unittest`.

### Pre-existing test count
- Known failures in `TASKS.md` reduced from 3 to 2. Remaining: `TestCertificateAndSuggestionEndpoints.test_manual_certificate_creation_pre_campaign` and `_post_campaign` (suggestion-infer logic incomplete). Suite now 42/44 pass.

---

## Session 7 — Deterministic Seed + /me Fixes + Uvicorn Reload

### Slice 1–3: `seed.py` deterministic demo player
- `Done` `backend/app/seed.py`: thêm `ensure_demo_account()` helper — idempotent, tạo `dev@example.com` + `ad00000@gmail.com` accounts; `ensure_player` dùng `Player.account_id == demo_account.id` thay `Player.first()` — loại bỏ cross-account corruption path; `ensure_account_and_profile` delegate account creation sang helper, xóa dòng `player.account_id` reassign.

### Slice 4: `main.py` neutral register fallback
- `Done` `backend/app/main.py`: `register()` bỏ `"IELTS Hunter"` hardcode — dùng `name = stripped_display_name or email_prefix or "New Hunter"` cho `Account.display_name`, `Player.name`, `Player.display_name`.

### Slice 5: `activate-campaign` optional body
- `Done` `backend/app/schemas.py`: thêm `OnboardingActivateIn(display_name, campaign_template_code)`.
- `Done` `backend/app/main.py`: `activate_campaign` nhận `body: OnboardingActivateIn | None = None` — set player name nếu có, pass `template_code` vào `activate_campaign_for_player`.

### Fix: `/me` response `player.name` + `campaign` key
- `Done` `backend/app/schemas.py`: thêm `name: str` vào `PlayerMeOut`; đổi `active_campaign` → `campaign` trong `MeResponseOut`.
- `Done` `backend/app/main.py`: đổi kwarg `active_campaign=` → `campaign=` trong `MeResponseOut(...)`.

### Fix: uvicorn `--reload`
- `Done` `docker-compose.yml`: thêm `--reload` flag vào uvicorn command — backend tự reload khi file trong `./backend` thay đổi.

### Verified
- `py_compile` 3 files: 0 lỗi.
- `Player.first()` trong `seed.py`: 0 kết quả.
- `"IELTS Hunter"` trong `register()`: 0 kết quả.
- Runtime: reset ×2 idempotent; register fallback = email prefix; `activate-campaign` với body set name đúng; 3 accounts × 3 players isolated; restart với real accounts không corrupt.
- `/me`: `player.name` = "IELTS Hunter" ✓; `campaign.id` = 24 ✓; `active_campaign` key không còn ✓.
- Uvicorn log: `Will watch for changes in these directories: ['/app']` ✓.

## Session 6 — Collocation Master Data

### Phase 1–4: Collocation Master Data Complete

- `Done` `backend/alembic/versions/950b4a9af4c2_add_collocation_master_data.py`: created migration table structure mapping `CollocationCollection` -> `CollocationSection` -> `CollocationTopic` -> `CollocationItem`, intermediate `CampaignCollocationLink`, and progress tracker `PlayerCollocationProgress`; dropped legacy `vocabulary_collocations` table.
- `Done` `backend/app/models.py`: defined SQLAlchemy models (`CollocationCollection`, `CollocationSection`, `CollocationTopic`, `CollocationItem`, `CampaignCollocationLink`, `PlayerCollocationProgress`) with proper cascading rules. Added relationships to `Campaign` and `Player` and removed legacy `VocabularyCollocation`.
- `Done` `backend/app/schemas.py`: updated nested outline and progress schema responses, removed legacy `VocabularyCollocationIn`/`VocabularyCollocationOut` schemas.
- `Done` `backend/app/services.py`: deleted legacy `VocabularyCollocation` queries and model references, updated `get_collocation_practice()`, `sync_node_status_from_item()`, and boss check-in generation logic to query from the new `CollocationItem` table.
- `Done` `backend/app/main.py`: registered collection outline/CRUD, campaign-collection linking, and collocation item progress logging endpoint handlers.
- `Done` `backend/app/test_backend.py`: imported collocation models and added `TestCollocationMasterData` suite verifying the end-to-end flow of collocation matching game practice, progressive learning/mastery, and vocabulary boss check-ins. All 44 tests pass successfully.

## Session 5 — Auth Hardening, Backlog Removal, Rank Exam Status

### Backlog Quest Feature Removal

- `Done` `backend/app/services.py` `sync_quest_statuses`: collapsed `"overdue"` → `"expired"`; all past-date daily quests expire immediately
- `Done` `backend/app/services.py` `complete_quest_instance`: removed 50% XP branch; always full XP with `completed_mode = "on_time"`
- `Done` `backend/app/main.py`: deleted `GET /api/quests/backlog` route (`get_backlog_quests`)
- `Done` `frontend/src/dashboard-data.js`: deleted `getBacklogQuests`, `backlogQuests`, `backlogCount`; removed `'overdue'` from `getQuestStatus`; simplified `getCompletionMode` and `getQuestEarnedXp`; updated weekly mission texts
- `Done` `frontend/src/App.jsx`: removed `backlogQuests={view.backlogQuests}` prop
- `Done` `frontend/src/components/QuestOverlay.jsx`: removed `backlogQuests` prop threading and `backlog={backlogQuests}` from DailyQuestPanel invocation
- `Done` `frontend/src/components/DailyQuestPanel.jsx`: removed `backlog` prop, `renderBacklogCard` function, Backlog summary card (`backlogCount`), and "Overdue Backlog" section
- `Done` `frontend/src/dashboard-data.test.js`: updated `'overdue'` → `'expired'` assertions; removed `view.backlogQuests.*` assertions; 5/5 tests pass
- `Done` Vite build ✓ 222 modules, 0 errors; grep confirms 0 dangling backlog refs in `frontend/src`

### Silent Refresh on 401 (D3)

- `Done` `frontend/src/api/client.js`: `apiFetch` intercepts 401 → calls `attemptRefresh()` (POST `/auth/refresh` with `credentials: include`) → retries original request with new token; throws `sessionExpired = true` if refresh fails
- `Done` `frontend/src/App.jsx`: existing `err.status === 401 → logout → /login` handler unchanged — correctly triggers only after silent refresh fails

### httpOnly Cookie for Refresh Token (D4)

- `Done` `backend/app/schemas.py`: `TokenOut.refresh_token` → `str | None = None` (no longer returned in body)
- `Done` `backend/app/main.py`: imported `Cookie, Response`; added `REFRESH_COOKIE = "ielts_rt"` constant; added `set_refresh_cookie` / `clear_refresh_cookie` helpers (`httponly=True, samesite="lax", path="/api/auth"`)
- `Done` `backend/app/main.py` `register` + `login`: set `ielts_rt` cookie, removed `refresh_token` from JSON response
- `Done` `backend/app/main.py` `refresh`: reads cookie `ielts_rt` (priority) or body fallback; rotates token; sets new cookie
- `Done` `backend/app/main.py` `logout`: reads cookie or body; revokes session; clears cookie
- `Done` `frontend/src/api/client.js`: removed `REFRESH_KEY`; `setTokens` accepts only `accessToken`; all `fetch` calls use `credentials: "include"`
- `Done` `frontend/src/api/auth.js`: `logout()` no longer accepts/sends refresh token argument; `refreshTokens()` sends no body (cookie auto-sent)
- `Done` `frontend/src/auth/AuthProvider.jsx`: removed `REFRESH_KEY` import and all refresh token localStorage reads/writes

### GET /api/rank-exams/status/{skill_id} (O1)

- `Done` `backend/app/schemas.py`: added `RankExamStatusOut` (skill_id, promotion_status, confirmed_rank, pending_rank, daily_cap, attempts_today, attempts_remaining)
- `Done` `backend/app/main.py`: added `GET /api/rank-exams/status/{skill_id}` route placed before `GET /api/rank-exams/{attempt_id}` (avoids FastAPI path conflict); counts today's attempts against 2/day cap
- `Done` `frontend/src/api/rankExam.js`: added `getRankExamStatus(skillId)` export
- `Done` Backend syntax check ✓; Vite build ✓

---

## Big Update: Account, Onboarding & Rank Boss System

### Phase 10 — Backend Ownership Protection

- `Done` Added `get_current_player`, `get_current_campaign`, `get_optional_campaign` FastAPI Depends chain in `main.py`
- `Done` Replaced ~70 call sites of `get_player_or_404` / `get_active_player` with account-scoped dependencies
- `Done` Added ownership guards on all routes with `{id}` in path (cross-account → 404)
- `Done` Renamed route handler `get_current_campaign` → `get_current_campaign_route` to avoid name conflict with dependency
- `Done` Vocabulary routes use `player_id` ownership (per DECISIONS.md); campaign routes use `campaign_id`
- `Done` `POST /api/certificates/manual` uses `get_optional_campaign` — supports pre-campaign cert submission
- `Done` Updated `TestWaveDAndE` fixtures: StaticPool, `app.dependency_overrides`, TestClient; 43/43 tests pass
- `Done` Documented ownership chain `Account→Player→Campaign→Resource` in `docs/current/SCHEMA_SEMANTICS.md`

### Phase 11 — Frontend Auth Shell

- `Done` `frontend/src/api/client.js`: fetch wrapper with `Authorization: Bearer`, `TOKEN_KEY`/`REFRESH_KEY` constants, `getToken`/`setTokens`/`clearTokens`, 401 error propagation
- `Done` `frontend/src/api/auth.js`: register, login, logout, getMe, getOnboardingStatus API calls
- `Done` `frontend/src/auth/AuthProvider.jsx`: AuthContext, `hydrateFromToken` on mount, login/logout/register/refreshAuth callbacks, `onboardingCompleted` state
- `Done` `frontend/src/auth/ProtectedRoute.jsx`: loading→null, !auth→/login, !onboarded→/onboarding
- `Done` `frontend/src/pages/Login.jsx`, `Register.jsx`: form pages with Vietnamese error messages, navigate after auth
- `Done` `frontend/src/main.jsx`: BrowserRouter + AuthProvider + Routes wrapping App
- `Done` `frontend/src/App.jsx`: `api()` useCallback with 401→logout→navigate('/login') handler; removed inline API_URL
- `Done` Auth CSS added to `styles.css` (`.auth-page`, `.auth-card`, `.auth-title`, `.auth-subtitle`, `.auth-form`, `.auth-label`, `.auth-input`, `.auth-btn`, `.auth-error`, `.auth-footer`, `.auth-link`)
- `Done` Installed `react-router-dom` via npm

### Phase 12 — Frontend Onboarding UI

- `Done` `frontend/src/pages/Onboarding.jsx`: 3-step flow — Welcome → Manual Certificate (IELTS score inputs, skippable) → Confirm + activate
- `Done` `frontend/src/api/auth.js`: added `postManualCertificate(scores)` and `activateCampaign()`
- `Done` `auth/AuthProvider.jsx`: exposed `refreshAuth()` for Onboarding to sync state post-activate
- `Done` Flow: submit cert (optional) → `POST /api/certificates/manual` → `POST /api/onboarding/activate-campaign` → `refreshAuth()` → navigate('/')
- `Done` Onboarding CSS added to `styles.css` (`.onboarding-page`, `.onboarding-card`, `.onboarding-dots`, `.onboarding-scores`, `.onboarding-score-chip`, `.onboarding-btn-primary`, `.onboarding-btn-ghost`, etc.)

### Phase 13 — Frontend Suggestion Inbox Fix

- `Done` `SuggestionInboxDropdown.jsx`: Apply/Dismiss buttons wired, pending state labels ("Applying..."/"Dismissing..."), English empty states
- `Done` `SuggestionInboxPanel.jsx`: aligned with Dropdown — added `pendingByKey`/`onApply`/`onDismiss` props, consistent labels
- `Done` `dashboard-data.js`: rank suggestion title format `Rank F → E` (was `Update rank F -> E`); English detail strings
- `Done` `App.jsx`: toast messages in English ("Suggestion applied"/"Suggestion dismissed"/"Action failed")
- `Done` `handleSuggestionAction` already fully wired from Phase 11 — calls correct endpoints, reloads `loadSuggestions + loadInitialData` after action

### Phase 14 — Frontend Rank Boss UI

- `Done` `backend/app/schemas.py`: `SkillOut` exposes `promotion_status: str = "none"` and `pending_rank: str | None = None`
- `Done` `backend/app/main.py`: `serialize_skill_state` populates `promotion_status` and `pending_rank` from `CampaignSkillState`
- `Done` `frontend/src/api/rankExam.js` (new): `unlockRankExam`, `startRankExam`, `getRankExamAttempt`, `submitRankExam`
- `Done` `frontend/src/components/RankBossNotif.jsx` (new): fixed bottom-right banner, detects `eligible`/`boss_required`/`in_progress` skills, Unlock Boss / Start Exam / Resume Exam buttons
- `Done` `frontend/src/components/RankExamScreen.jsx` (new): exam overlay — timer countdown (critical <60s), question navigator dots, MCQ radio + free-text textarea, auto-submit on expiry
- `Done` `frontend/src/components/RankExamResultScreen.jsx` (new): result overlay — CLEARED/FAILED banner, score/accuracy/rank stats, retry button (failed only)
- `Done` `App.jsx`: state (`examData`, `examSkill`, `examResult`, `isExamOpen`, `isExamResultOpen`); handlers `handleUnlockBoss`, `handleStartExam`, `handleExamResult`, `handleExamClose`; rendered `RankBossNotif`, `RankExamScreen`, `RankExamResultScreen`
- `Done` Rank Boss + Exam CSS added to `styles.css`

### Phase 15 — Final Hardening, Tests, and Documentation

- `Done` Backend: 43/43 tests pass (`python -m pytest app/test_backend.py`)
- `Done` Frontend: Vite build ✓ 218 modules, 0 errors
- `Done` `docs/current/SCHEMA_SEMANTICS.md`: added `SkillOut API Contract (Phase 14)` section documenting `promotion_status` + `pending_rank` fields
- `Done` `docs/history/changelogs.md`: added entry `[2026-06-08] Phase 10–14` with full summary of all changed files
- `Done` `TASKS.md` deferred backlog: removed stale "Phase 12 onboarding UI" item (Phase 12 is done)

### Phase 0 — Documentation / ADR / Tracker Preparation

- `Done` Add Account/Auth architecture decisions to `DECISIONS.md`
- `Done` Add new scope category: `account-scoped` to documentation
- `Done` Record mandatory onboarding, no internal placement test, and manual certificate score MVP
- `Done` Record certificate suggestions apply directly to confirmed rank
- `Done` Record XP-based Rank Boss promotion (one rank at a time, max 2 attempts/day, 30-min time limit)
- `Done` Record Writing/Speaking Rank Boss out of scope (track in backlog)
- `Done` Record skill quota daily quest generation logic

### Phase 1 — Account/Auth Database Migration

- `Done` Create `Account` model (id, email, password_hash, display_name, avatar_url, status, role, onboarding_completed, etc.)
- `Done` Create `AccountSession` model (refresh_token_hash, user_agent, ip_address, expires_at, revoked_at, etc.)
- `Done` Create `AccountToken` model (token_hash, purpose, expires_at, consumed_at, etc.)
- `Done` Create `AccountSecurityEvent` model (event_type, success, detail, etc.)
- `Done` Create `AccountPreference` model (locale, timezone, theme, notification_enabled, etc.)
- `Done` Modify `players` table (add nullable `account_id` foreign key, unique key)
- `Done` Generate and run Alembic migration

### Phase 2 — Campaign Template / Settings / Quota Database Migration

- `Done` Create `PlayerLearningProfile` model
- `Done` Create `CampaignTemplate` model (seed IELTS 18-month foundation template)
- `Done` Modify `campaigns` table (add `campaign_template_id`, `setup_completed`, `setup_completed_at`)
- `Done` Create `CampaignSetting` model
- `Done` Create `CampaignTemplateSkillQuota` model
- `Done` Create `CampaignSkillQuestQuota` model
- `Done` Create `VocabularySetting` model
- `Done` Generate and run Alembic migration

### Phase 3 — Certificate and Rank Boss Database Migration

- `Done` Create `CertificateRecord` model (manual input fields, status, note, etc.)
- `Done` Create `RankExamPool` model (skill_id, from_rank, to_rank, pass_percent, etc.)
- `Done` Create `RankExamVersion` model (pool_id, version_code, total_questions, etc.)
- `Done` Create `RankExamQuestion` model (exam_version_id, question_type, prompt, options_json, etc.)
- `Done` Create `RankExamAttempt` model (campaign_id, skill_id, from_rank, to_rank, status, passed, etc.)
- `Done` Create `RankExamAnswer` model (attempt_id, question_id, answer_json, is_correct, etc.)
- `Done` Modify `campaign_skill_states` (add `pending_rank`, `promotion_status`, `promotion_unlocked_at`, `last_rank_exam_attempt_id`)
- `Done` Generate and run Alembic migration

### Schema Migration — Pre-Phase Fix

- `Done` Add `source_certificate_record_id` FK to `skill_rank_suggestions` and `skill_rank_history` (P1/M2)
- `Done` Add CHECK constraint `ck_promotion_status` on `campaign_skill_states` (P3)
- `Done` Run migration `30b9013e0a20` on host (fixing duplicate index errors)
- `Done` Run migration `30b9013e0a20` inside Docker container `ielts_quest_backend`
- `Done` Add `skill_rank_suggestions` and `skill_rank_history` to `DATABASE_SCHEMA.md` entity listing (P5)
- `Done` Document atomicity requirement for `onboarding_completed` + `setup_completed` in `SCHEMA_SEMANTICS.md` (P4)

### Phase 4 — Seed and Backfill

- `Done` Seed default dev account and link to default player
- `Done` Seed `account_preferences` and `player_learning_profiles`
- `Done` Seed `campaign_templates` (IELTS 18-Month Hunter Roadmap) & `campaign_template_skill_quotas`
- `Done` Seed `vocabulary_settings` defaults
- `Done` Seed `rank_exam_pools` & versions/objective questions for MVP skills (Vocabulary, Reading, Listening, Grammar, Collocation) for F→E rank
- `Done` Define XP threshold values per rank transition and seed into `rank_exam_pools.xp_threshold` (M3)
- `Done` Ensure seed is idempotent and `/api/dev/reset` works

### Phase 5 — Backend Auth MVP

- `Done` Implement `POST /api/auth/register` (password hashing, duplicate check)
- `Done` Implement `POST /api/auth/login` (verify password, session creation, failed attempts count, status lock check)
- `Done` Implement `POST /api/auth/refresh` (token rotation, refresh hash check, expire validation)
- `Done` Implement `POST /api/auth/logout` (revoke session)
- `Done` Implement `GET /api/auth/me` (access verification using HTTPBearer token, mapping accounts, players, active campaigns)
- `Done` Fix registration non-null foreign key SQLite constraint issues by passing `player=player` relationship reference instead of `player_id=player.id`
- `Done` Fix login account locking check order to prevent timing side-channel attacks and PBKDF2 executions on locked accounts
- `Done` Write comprehensive API endpoints integration tests in `TestAuthEndpoints` class in `test_backend.py`

### Phase 6 — Backend Onboarding and Campaign Activation

- `Done` Implement `GET /api/onboarding/status` to return status and certificate existence
- `Done` Implement `POST /api/onboarding/activate-campaign` to programmatically initialize campaign-scoped settings, quotas, study plan sessions, templates, quest instances, weekly missions, bosses, test records, and campaign skill states
- `Done` Ensure `onboarding_completed` + `setup_completed` are set atomically in same database transaction
- `Done` Write comprehensive backend integration tests in `TestOnboardingEndpoints` class in `test_backend.py` verifying status checks, activation flows, database side-effects, and unauthorized access

### Pre-Phase 9 — Resolve Promotion Status Design

- `Done` Decided to keep `eligible` state: player XP flows freely until player explicitly unlocks boss exam via `POST /api/rank-exams/unlock`
- `Done` Decided: `POST /api/rank-exams/unlock` transitions `eligible → boss_required` (XP blocked from this point)
- `Done` Decided: XP block applies when `promotion_status` is `boss_required` or `in_progress` — quest claim for that skill awards 0 XP
- `Done` Decided: after 2 failed attempts in a day → subtract 50 from `campaign_skill_states.xp` (floor 0), reset to `eligible` (XP unblocked, retry tomorrow)
- `Done` Documented full state machine with all 7 transitions in `docs/current/SCHEMA_SEMANTICS.md`
- `Done` Documented retry limit counting rule (SQL pattern) in `docs/current/SCHEMA_SEMANTICS.md`
- `Done` Documented XP block rule in `docs/current/SCHEMA_SEMANTICS.md`
- `Done` Note: `recompute_skill_progress` in `services.py:589` currently sets `boss_required` directly — must be fixed in Phase 9 to set `eligible` instead

### Phase 9 — Backend Rank Boss Logic (M6: Integration Tests)

- `Done` Detect XP-based rank eligibility — fixed `services.py:recompute_skill_progress` to set `promotion_status = "eligible"` instead of jumping to `boss_required`
- `Done` Implement `POST /api/rank-exams/unlock` (eligible → boss_required, XP blocked)
- `Done` Implement `POST /api/rank-exams/start` (boss_required → in_progress, enforce 2/day cap, select version)
- `Done` Implement `GET /api/rank-exams/{attempt_id}` (campaign-scoped ownership)
- `Done` Implement `POST /api/rank-exams/{attempt_id}/submit` (grade, pass → confirmed_rank++, fail+cap → -50 XP → eligible)
- `Done` XP block on quest claim when skill `promotion_status` is `boss_required` or `in_progress`
- `Done` Backend integration tests (M6): 16 tests in `TestRankExamPhase9` covering unlock, start, get, submit pass/fail/penalty/floor, XP block, retry cap, double-submit — all 43 suite tests pass
- `Done` Bug fix: `sync_quest_statuses` `not quest.earned_xp` guard → `earned_xp is None and not reward_claimed` (XP-blocked quest backfill prevented)
- `Done` Bug fix: `recompute_skill_progress` else-branch guard extended to `{eligible, boss_required, in_progress, passed}` (recompute no longer clobbers in-flight exam state)
- `Done` Bug fix: XP penalty in `submit_rank_exam` moved after `refresh_progress_state` with explicit `db.refresh(state)` (penalty survives recompute)
- `Done` Bug fix: `refresh_progress_state` added `db.expire_all()` before state map reload (ensures fresh reads on shared SQLite session)

### Phase 8 — Backend Daily Quest Skill Quota Generator Update

- `Done` Quest generator reads `campaign_skill_quest_quotas` — implemented in `seed.py:ensure_quest_instances` (line 1216)
- `Done` Generate quests by skill quota and slot codes (`vocab_flashcard`, `reading_scan`, etc.) with `preferred_activity_types` ordering
- `Done` Uniqueness enforced via UniqueConstraint `uq_quests_campaign_date_daily_slot` on `(campaign_id, quest_date, daily_slot_code)` plus in-memory dedup in generator
- `Done` Generator called from both `seed_database` and `activate_campaign_for_player` — fully wired at onboarding activation

### Phase 7 — Backend Manual Certificate and Suggestion Apply Fix

- `Done` Define score-to-rank mapping logic for IELTS certificate scores based on SCHEMA_SEMANTICS.md
- `Done` Implement `POST /api/certificates/manual` to save IELTS scores and create skill rank suggestions with certificate references
- `Done` Implement `GET /api/certificates` to query manual certificates of the authenticated player
- `Done` Update `apply_rank_suggestion` to directly update `confirmed_rank` (and `rank` if the suggested rank is higher) and clear pending exam transition state
- `Done` Implement suggestion dismissal updating status to `dismissed`
- `Done` Write comprehensive integration tests in `TestCertificateAndSuggestionEndpoints` class in `test_backend.py` verifying pre-campaign/post-campaign certificate registrations, suggestions mapping, direct rank updates, and dismiss actions


## Active Documentation Reorganization Tracker

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

## Next Tasks

1. `Done` Capture a browser visual review of the current dashboard and overlays.
2. `Done` Add automated backend tests for:
   - campaign-scoped skill state
   - badge unlock read path
   - check-in upsert behavior
   - daily-slot invariants
3. `Done` Browser visual walkthrough / screenshot verification. (Done: captured dashboard_main, vocabulary_workspace, and quest_overlay)

## Vocabulary Support Skill (Lexical Awakening System) Tracker

### Phase 1: Core Vocabulary System (MVP)

- `Done` Backend: Create tables (`vocabulary_items`, `vocabulary_examples`, `vocabulary_collocations`, `vocabulary_relations`, `flashcards`, `spaced_repetition_state`) via Alembic migration.
- `Done` Backend: Build Pydantic schemas and service layers for Codex items and flashcards.
- `Done` Backend: Implement CRUD routes for vocabulary items, examples, and collocations.
- `Done` Backend: Implement Flashcard review and spaced repetition endpoints.
- `Done` Backend: Integrate XP award logic to "vocabulary" support skill.
- `Done` Frontend: Implement Vocabulary Dashboard / stats panel.
- `Done` Frontend: Implement Codex Archive view & CRUD interface.
- `Done` Frontend: Implement Flashcard Gate review battle page.
- `Done` Verification: Run syntax, build, and smoke verification for Phase 1.

### Phase 2: Word Network Tree

- `Done` Backend: Create tables (`vocabulary_topics`, `vocabulary_nodes`, `vocabulary_edges`). (Done in migration `20260607_10`)
- `Done` Backend: Build endpoints to fetch, create, and link topic trees and nodes.
- `Done` Frontend: Implement Word Network Tree view using React Flow.
- `Done` Integration: Update node states dynamically based on card review/mastery states.

### Phase 3: IELTS Advanced Vocabulary

- `Done` Frontend/Backend: Implement Collocation Forge matching game.
- `Done` Frontend/Backend: Implement Word Family Evolution display.
- `Done` Frontend/Backend: Implement synonym/antonym/register Shadow Duel.
- `Done` Frontend/Backend: Implement pronunciation/stress Echo Chamber.

### Phase 4: Boss and Error System

- `Done` Backend: Create table `vocabulary_errors` and logic for Error Dungeon.
- `Done` Frontend: Implement Error Dungeon screen.
- `Done` Backend/Frontend: Implement Vocabulary Boss checkpoint battles.
- `Done` Integration: Connect vocabulary achievements with badge wall unlocks.

## Skill-Specific Quest XP Routing & Vocabulary Daily Quest Tracker

### Task 1 — Docs / ADR Decision

- `Done` Record final XP routing decision in `DECISIONS.md`.
- `Done` Record decision not to create separate Vocabulary Daily Quest tables.
- `Done` Record quest extension strategy.
- `Done` Update `docs/history/AGENT_NOTES.md` and `docs/history/changelogs.md`.

### Task 2 — Models + Alembic Migration

- `Done` Add new fields (`quest_track_code`, `activity_type`, `reward_skill_id`, `target_metric`, `target_count`, `completion_payload`) to `Quest` and `QuestTemplate` models in `backend/app/models.py`. (Changed: `backend/app/models.py`)
- `Done` Add new fields (`primary_skill_id`, `mission_track_code`, `activity_type`, `reward_skill_id`) to `WeeklyMission` model in `backend/app/models.py`. (Changed: `backend/app/models.py`)
- `Done` Create `SkillXpTransaction` model/table with unique idempotency constraint. (Changed: `backend/app/models.py`)
- `Done` Create `PlayerXpTransaction` model/table with unique idempotency constraint. (Changed: `backend/app/models.py`)
- `Done` Generate and add Alembic migration file for the new columns and transaction tables (file created: `backend/alembic/versions/20260607_11_quest_and_xp_transactions.py`). Migration runner endpoint added — run migrations using `/api/dev/run_migrations`.

### Task 3 — Seed Vocabulary Quest Templates

- `Done` Add seeding logic for the 5 Vocabulary Daily Quest templates (Memory Gate, Codex Entry, Collocation Forge, Context Hunt, Error Dungeon) in `backend/app/seed.py`. (Changed: `backend/app/seed.py`)
- `Done` Verify seeding resets via `/api/dev/reset` and verify templates in DB. (Done: endpoint returns counts for templates and weekly missions for quick verification)

### Task 4 — Quest Claim Reward Routing

- `Done` Update quest claim endpoint (`POST /api/quests/{id}/claim`) to verify quest status and record transactions. (Changed: `backend/app/main.py`)
- `Done` Implement `award_skill_xp` and `award_player_xp` service logic to record to transaction tables and update `campaign_skill_states`/player XP. (Changed: `backend/app/services.py`)
- `Done` Ensure idempotency of daily quest claiming using idempotency keys on transactions.

### Task 5 — Weekly Mission Skill Reward

- `Done` Update weekly mission claim endpoint (`POST /api/weekly-missions/{id}/claim`) to verify status and record transactions. (Changed: `backend/app/main.py`)
- `Done` Route reward to `SkillXpTransaction` if `reward_skill_id` is present, else `PlayerXpTransaction`. (Changed: `backend/app/services.py`)
- `Done` Seed the `Weekly Vocabulary Expansion` mission template with `reward_skill_id = Vocabulary`. (Changed: `backend/app/seed.py`)

### Task 6 — Boss Reward Routing

- `Done` Extend Boss Battle models/endpoints with `boss_scope`, `reward_skill_id`, `reward_claimed` and `reward_claimed_at`. (Changed: `backend/app/models.py`)
- `Done` Implement routing logic: Skill-specific Boss -> `SkillXpTransaction`; Overall / Phase Boss -> `PlayerXpTransaction`. (Changed: `backend/app/main.py`, `backend/app/services.py`)
- `Done` Verify correct transactions are created for boss kills. (Done: added automated unit tests in `app.test_backend`)

### Task 7 — Frontend Quest Board

- `Done` Update React frontend to show target skill reward on Quest cards and added a quick skill filter and completion payload display. (Changed: `frontend/src/components/DailyQuestPanel.jsx`)
- `Done` Add tab filtering/grouping by skill/track (All, Vocabulary, Reading, Listening, etc.) on Quest Board. (Changed: `frontend/src/components/DailyQuestPanel.jsx`, `frontend/src/styles.css`)
- `Done` Show completion payload summary and claim button for completed but unclaimed quests on both active and backlog cards. (Changed: `frontend/src/components/DailyQuestPanel.jsx`)

## Deferred Backlog Cleanup

- `Done` Drop legacy quest tracker fields (`tracker_type`, `tracker_entry_id`) from database schema.
- `Done` Drop legacy weakness source fields (`source_type`, `source_ref_id`) from database schema.
- `Done` Drop global mutable state columns from `skills` in database schema and models.
- `Done` Drop global unlock-state columns from `badges` in database schema and models.
- `Done` Add stricter typed-source / typed-tracker check constraints (`ck_quests_only_one_tracker` and `ck_weakness_suggestions_only_one_source`) in both SQLite and MySQL. (Done: implemented in `models.py`, added in Alembic migration `089adadeddde`, and verified via automated tests)

