# IELTS Quest Dashboard Tasks

Last updated: `2026-06-09` (session 8 — XP/Level/Rank redesign spec + implementation breakdown added below; specs in `spec/infor/` rewritten to canonical)

## Session Resume

- All Phases 4–15 of the "Big Update: Account, Onboarding & Rank Boss System" are complete and archived in `tasks-done.md`.
- Session 5: Backlog quest feature removed (Slices 1–7, 9); silent refresh on 401 wired; refresh token migrated to httpOnly cookie; `GET /api/rank-exams/status/{skill_id}` added.
- Session 7: Deterministic seed (no `Player.first()`), neutral register fallback, `activate-campaign` optional body, `/me` exposes `player.name` + `campaign` key, uvicorn `--reload` active.
- Backend: JWT auth wired end-to-end; 43/43 tests pass.
- Frontend: Auth Shell (Login/Register), Onboarding (3-step), Suggestion Inbox (Apply/Dismiss), Rank Boss UI (Notif + Exam + Result) all live.
- Vite build: ✓ 222 modules, 0 errors.

## Current State

- Full stack live: Docker Compose (`frontend :5173`, `backend :8000`, `mysql :3307`). Uvicorn chạy với `--reload` — edit `backend/` tự reload không cần restart.
- Auth: JWT register/login/logout/refresh; access token in localStorage; refresh token in httpOnly cookie `ielts_rt`; silent refresh on 401 → logout only if refresh fails.
- Seed: deterministic — demo player luôn thuộc `ad00000@gmail.com`, không dùng `Player.first()`. Register fallback dùng email prefix thay `"IELTS Hunter"`.
- Onboarding: 5-step UI (Name → Campaign → StartDate → Certificate → Confirm) → `POST /api/onboarding/activate-campaign` nhận optional `{ display_name, campaign_template_code, start_date }` → dashboard.
- Register: chỉ email + password (không còn form tên hiển thị).
- `/api/auth/me`: trả `player.name`, `player.display_name`, `campaign` (không còn `active_campaign`).
- StatusModal: nút "Đăng xuất" → `/login`.
- Rank Boss: eligible/boss_required/in_progress banners; exam screen với timer + MCQ; result screen CLEARED/FAILED; `GET /api/rank-exams/status/{skill_id}` exposes remaining daily attempts.
- Suggestion Inbox: Apply/Dismiss wired to backend, skill matrix refreshes after apply.
- Backlog quest feature: fully removed. Past-date quests expire immediately (no overdue state, no 50% XP).
- Canonical context: `docs/current/`; history/logs: `docs/history/`.

## Completed Tasks

All completed tasks have been archived and moved to [tasks-done.md](tasks-done.md).

## In Progress

- None

---

# Implementation Plan: XP / Level / Rank Redesign (2026-06-09)

Source of truth: [`spec/infor/ielts_xp_policy_rank_quest_spec.md`](spec/infor/ielts_xp_policy_rank_quest_spec.md) (canonical) + `player_level.md`, `quest.md`, `daily_quest.md`.

> **Spec-ref convention:** every task below has a `Spec ref:` line naming the exact file + section to read before implementing it. All spec files live in `spec/infor/`. When a `§N` appears inside acceptance/verification text without a filename, it refers to the file named on that task's `Spec ref:` line. The canonical file for all XP/level/rank **values** is `ielts_xp_policy_rank_quest_spec.md` — if any other doc disagrees on a number, that file wins.

## Overview

Re-architect the progression model: skill XP becomes the only thing that accrues; player XP becomes the **average of the 5 matrix skills** (no direct accrual); skill/player levels become **fine-grained (60 levels, 10 per rank)** on the curve `xp(L)=round(19*(L^1.6-1))`; Main Quests award **full XP to every matrix skill** in a session; Daily Quests expand to **9 slots**; Grammar→Writing and Collocation→Vocabulary as support sources; vocab data-entry capped at 40 XP/word; Writing/Speaking are not boss-gated; the collocation source file is importable to activate Vocabulary XP.

## Architecture Decisions

- **Player XP is derived, never accrued.** `recompute_player_progress` stops summing quest/mission/boss/vocab and instead averages the 5 matrix skill XP. Rationale: single source of truth (skills), avoids double-count, makes player rank reflect balanced learning.
- **Fine-grained level curve in code, rank thresholds in DB.** `rank_xp_thresholds` holds the 7 rank min-XP rows; per-level XP is computed from the formula. Rationale: anti-hard-code (XP policy §10) while keeping 60 rows out of the DB.
- **Support sources route into matrix skills.** Grammar→Writing, Collocation→Vocabulary at the routing layer, not via separate ranks. Rationale: owner decision; keeps player average over exactly 5 skills.
- **9 daily slots via additive migration.** Widen `daily_slot_code` value set; keep the existing unique constraint shape `(campaign_id, quest_date, daily_slot_code)`. Rationale: low-risk additive evolution.
- **Policy tables seed-driven & idempotent.** Follow existing `get_or_create` seed pattern.

## Dependency Graph

```
Phase 0 (docs) ─ done in this session
      │
Phase 1: rank_xp_thresholds + level curve  ──┐
      │                                       │
Phase 2: player_xp = avg(5 skills)            │ (rank model must exist first)
      │                                       │
Phase 3: support routing (Grammar→Writing,    │
          Collocation→Vocabulary)             │
      │                                       │
Phase 4: vocab cap 40/word                    │
      │                                       │
Phase 5: 9 daily slots (migration + gen)      │
      │                                       │
Phase 6: Main Quest full-XP + skill tiering   │
      │                                       │
Phase 7: Writing/Speaking un-gate boss        │
      │                                       │
Phase 8: collocation parser + seed            │
      │                                       │
Phase 9: policy tables (optional hardening)   │
      │                                       │
Phase 10: frontend (rank-only player, 9 slots, locked confirmed_rank)
```

## Task List

### Phase 1 — Level curve & rank thresholds (foundation)

- [x] **Task 1: Replace rank threshold table with level-curve model.** *(S, backend)*
  - **Description:** In `services.py`, replace the 7-tuple `RANK_THRESHOLDS` with the curve `xp(L)=round(19*(L^1.6-1))`. Add `level_from_xp(xp)->int (1..60)` and `rank_from_level(L)->str` (10 levels/rank, S only at L60). Keep `get_rank_level(xp)->(rank, level)` returning the fine-grained level. Keep `RANK_MIN_XP` populated from rank first-levels (F=0 E=862 D=2460 C=4604 B=7212 A=10234 S=13279).
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §2 (Level Curve & Rank Mapping) — formula §2.1, rank mapping §2.2, threshold table §2.3; cross-check `player_level.md` §1.A.
  - **Acceptance criteria:**
    - [x] `level_from_xp(0)=1`, `level_from_xp(862)=11`, `level_from_xp(13279)=60`.
    - [x] `get_rank_level(861)=("F",10)`, `get_rank_level(862)=("E",11)`, `get_rank_level(13279)=("S",60)`.
    - [x] `RANK_MIN_XP` matches the §2.3 table.
  - **Verification:** unit-check the boundaries above; `alembic upgrade head` not required; backend imports without error.
  - **Dependencies:** None.
  - **Files:** `backend/app/services.py`.
  - **Gap check:** [x] Done — Gap A (seed.py dead code) + Gap B (xp_threshold values) found & fixed. No unresolved gaps. → **Archived to tasks-done.md (session 8c)**

- [x] **Task 2: Reconcile confirmed_rank floor with fine-grained level.** *(S, backend)*
  - **Description:** In `recompute_skill_progress`, the line that sets `state.level = next(lvl for _,r,lvl in RANK_THRESHOLDS if r==confirmed_rank)` must use the new `rank→first-level` mapping (e.g. confirmed E → level 11 floor). Ensure `state.xp` floor = `RANK_MIN_XP[confirmed_rank]` still holds.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §3 (Rank vs Confirmed Rank) + §2.2 rank→first-level mapping.
  - **Acceptance criteria:**
    - [x] A skill with `confirmed_rank="D"` and XP below 2460 is floored to level 21 / 2460 XP.
    - [x] No reference to the old 3-element threshold tuple remains.
  - **Verification:** grep shows no stale `RANK_THRESHOLDS` tuple unpacking; smoke `/api/dev/reset` then `/summary` returns sane levels.
  - **Dependencies:** Task 1.
  - **Files:** `backend/app/services.py`.
  - **Gap check:** [x] Done — no additional gaps beyond Task 1's Gap A/B. → **Archived to tasks-done.md (session 8c)**

### Checkpoint A (after Tasks 1–2)
- [x] Backend boots; `/api/dev/reset` + `/summary` succeed; sample skill XP maps to expected level/rank.

### Phase 2 — Player XP as average of 5 matrix skills

- [x] **Task 3: Derive player_xp from the 5 matrix skills; remove direct accrual.** *(M, backend)*
  - **Description:** Rewrite `recompute_player_progress` so it no longer sums `quest_xp + mission_xp + boss_xp + vocab_xp`. Instead: read the 5 matrix `CampaignSkillState.xp` (Listening, Reading, Writing, Speaking, Vocabulary), `player.player_xp = round(mean(...))`, `player.total_xp = player.player_xp`, `player.player_rank, player.player_level = get_rank_level(player_xp)`. Keep the streak/shield/perfect-day block intact. Ensure `recompute_skill_progress` runs for all skills **before** the player average (ordering in `refresh_progress_state`).
  - **Spec ref:** `player_level.md` §1 (Player Level/Rank — DERIVED) + `ielts_xp_policy_rank_quest_spec.md` §1.2 (Player XP derived, no accrual) + §4 routing table (Player → nothing).
  - **Acceptance criteria:**
    - [x] With skills [1000, 2000, 0, 0, 0] player_xp = 600.
    - [x] Collocation/Grammar skill XP does NOT affect player_xp.
    - [x] `award_player_xp` is removed or made a no-op (and no caller breaks).
  - **Verification:** unit-check the average; `/summary` player block reflects the mean; no double-count vs skill totals.
  - **Dependencies:** Task 1, and skills must recompute first.
  - **Files:** `backend/app/services.py`.
  - **Gap check:** [x] Done — Gap C (test_boss_reward_routing old contract) fixed; Gap D (FE stale formulas) + Gap E (total_xp naming) documented → deferred to Task 16. → **Archived to tasks-done.md (session 8c)**

- [x] **Task 4: Audit & remove player-XP callers.** *(S, backend)*
  - **Description:** Find every call site that added XP to the player (check-in +XP, boss→player, mission→player) and remove the player-XP side (keep skill-XP side and streak/shield). Check-in becomes streak-only.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §4 routing table (Weekly Check-in = streak only, Player = nothing) + §1.2; `player_level.md` §1.
  - **Acceptance criteria:**
    - [x] No code path increments `player.player_xp` directly.
    - [x] Check-in still updates streak/shield, awards no XP.
  - **Verification:** grep `player_xp` shows only the derived assignment in Task 3; check-in smoke test increments streak only.
  - **Dependencies:** Task 3.
  - **Files:** `backend/app/services.py`, `backend/app/main.py`.
  - **Gap check:** [x] Done — no new gaps beyond Task 3 gaps. → **Archived to tasks-done.md (session 8c)**

### Checkpoint B (after Tasks 3–4)
- [x] `/summary` shows player rank = average-derived; no XP double-counting; check-in is streak-only.

### Phase 3 — Support-source routing (Grammar→Writing, Collocation→Vocabulary)

- [x] **Task 5: Route Grammar quest XP into Writing.** *(M, backend)*
  - **Description:** Grammar daily quests, Grammar weekly mission, and the Grammar component of S3 main quests must contribute to the **Writing** `CampaignSkillState`, not a Grammar state. Implement via a routing map `skill_name → target_matrix_skill` ({Grammar: Writing, Collocation: Vocabulary, else identity}) used by `recompute_skill_progress`'s quest aggregation (sum quests whose routed skill == this matrix skill).
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §1.1 (support sources) + §4 routing table + §7 (Grammar Weekly → Writing); UI buff line: `player_level.md` §2.A + xp_policy §1.1 UI note.
  - **Acceptance criteria:**
    - [x] Claiming a Grammar Exercise (+7) raises Writing XP by 7.
    - [x] The Grammar `CampaignSkillState` no longer surfaces an independent rank in `/summary` (excluded from the matrix tile list).
    - [x] `/summary` exposes, on the **Writing** matrix entry, a `support_breakdown: [{source:"Grammar", xp:<routed>}]` field so the frontend can render the buff line inside the Writing card (owner UI decision 2026-06-09). Sum of routed support XP must equal the Grammar contribution already folded into Writing `xp` (no double-count).
  - **Verification:** seed → claim a grammar quest → Writing XP increases; `/summary` Writing entry shows `support_breakdown` Grammar xp matching the delta; player average reflects it via Writing.
  - **Dependencies:** Task 3.
  - **Files:** `backend/app/services.py`, `backend/app/schemas.py`, `backend/app/main.py`.
  - **Gap check:** [ ] Chưa kiểm tra — cần audit sau khi implement Task 6 xong.

- [x] **Task 6: Confirm Collocation routing into Vocabulary.** *(S, backend)*
  - **Description:** `compute_vocabulary_xp` already adds `collocation_count*5`. Ensure Collocation daily quest (`vocab_collocation`) and any Collocation weekly mission also route to Vocabulary, consistent with Task 5's routing map. Exclude Collocation from the matrix display like Grammar.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §1.1 (support sources) + §4 routing + §8 (Vocabulary XP, collocation +5); UI buff line: `player_level.md` §2.A.
  - **Acceptance criteria:**
    - [x] Learning a collocation (status→learning) raises Vocabulary XP by 5.
    - [x] No standalone Collocation rank shown (excluded from the matrix tile list).
    - [x] `/summary` exposes, on the **Vocabulary** matrix entry, a `support_breakdown: [{source:"Collocation", xp:<routed>}]` field (same shape as Task 5) for the buff line inside the Vocabulary card. No double-count vs Vocabulary `xp`.
  - **Verification:** progress one `PlayerCollocationProgress` → Vocabulary XP +5; `/summary` Vocabulary entry shows `support_breakdown` Collocation xp.
  - **Dependencies:** Task 5.
  - **Files:** `backend/app/services.py`, `backend/app/schemas.py`, `backend/app/main.py`.
  - **Gap check:** [ ] Chưa kiểm tra — cần audit Tasks 5+6 cùng nhau trước khi archive.

### Phase 4 — Vocabulary anti-farm cap

- [x] **Task 7: Cap data-entry vocab XP at 40/word (mastery separate).** *(S, backend)*
  - **Description:** In `compute_vocabulary_xp`, restructure per-word accrual so the **data-entry sum** (create +2, meaning_en, meaning_vi, part_of_speech, pronunciation_ipa, that word's examples, that word's relations) is capped at 40/word; add `min(mastery_score,50)` **on top** of the cap.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §8 (Vocabulary XP & Anti-Farm Cap — 40/word data-entry, mastery +50 separate); `player_level.md` §3.C.
  - **Acceptance criteria:**
    - [x] A word with maxed data-entry yields ≤40 (+ up to 50 mastery).
    - [x] Existing low-data words unchanged.
  - **Verification:** unit-check a word with many examples stays ≤40 data-entry portion.
  - **Dependencies:** Task 6 (same function).
  - **Files:** `backend/app/services.py`.
  - **Gap check:** [x] Done — verified via unit test `test_vocabulary_anti_farm_cap` in `test_backend.py`. No new gaps found.

### Checkpoint C (after Tasks 5–7)
- [x] Grammar→Writing, Collocation→Vocabulary verified (Tasks 5+6 done); vocab farm capped (Task 7 done); player average still sane.

### Phase 5 — 9 daily slots

- [ ] **Task 8: Migration to widen daily_slot_code to 9 values.** *(M, migration)*
  - **Description:** Alembic migration `YYYYMMDD_NN_daily_slots_9.py`. Keep the column type/length and the unique constraint `(campaign_id, quest_date, daily_slot_code)`. If any enum/check constraint restricts the 3 old values, replace it with the 9-value set (`vocab_flashcard, vocab_codex, vocab_collocation, listening, reading, writing, speaking, grammar_review, grammar_exercise`). Provide `upgrade()`+`downgrade()`. Optionally backfill/relabel existing 3-slot rows.
  - **Spec ref:** `daily_quest.md` §1.B (9 daily_slot_code + unique constraint) + `ielts_xp_policy_rank_quest_spec.md` §5 (Daily Quest Structure).
  - **Acceptance criteria:**
    - [ ] `alembic upgrade head` succeeds on a populated DB and on an empty DB.
    - [ ] Inserting 9 distinct-slot daily quests for one date/campaign does not violate the unique constraint.
    - [ ] `downgrade()` reverses cleanly.
  - **Verification:** upgrade on a seeded DB; insert 9 slots; assert no IntegrityError; downgrade.
  - **Dependencies:** None (schema), but land before Task 9.
  - **Files:** `backend/alembic/versions/*.py`, `backend/app/models.py` (comment/length if needed).
  - **Gap check:** [ ] Chưa implement.

- [ ] **Task 9: Daily quest generation produces 9 slots/day.** *(M, backend)*
  - **Description:** Update daily-quest generation/seed to emit the 9 slots with correct skill_id and routed XP per XP policy §5.1. Grammar slots carry skill routing to Writing; collocation slot to Vocabulary.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §5.1 (Daily Quest XP table, per-slot XP + routing) + `daily_quest.md` §1.B.
  - **Acceptance criteria:**
    - [ ] A generated day has exactly 9 daily quests with the 9 slot codes.
    - [ ] Each quest's `base_xp`/`xp` matches the §5.1 table.
  - **Verification:** `/api/dev/reset`; inspect one day's daily quests = 9 rows, correct XP/skill.
  - **Dependencies:** Task 8, Task 5/6 (routing).
  - **Files:** `backend/app/seed.py`, `backend/app/services.py`.
  - **Gap check:** [ ] Chưa implement.

### Checkpoint D (after Tasks 8–9)
- [ ] 9 slots seed without constraint errors; XP per slot correct; existing data migrated.

### Phase 6 — Main Quest full-XP + skill tiering

- [ ] **Task 10: Rewrite infer_main_quest_xp to tier by skill column.** *(S, backend)*
  - **Description:** Replace session-number tiering with skill-based tiering from the session's skill summary: Writing/Speaking-heavy → 45 (heavy_output); Listening/Reading → 35 (standard); Review/Error → 25; sectional/mock test → 60. Keep deterministic & idempotent.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §6 (Main Quest XP Policy — tier-by-skill table) + `quest.md` §3.E (Main Quest Seeding & XP Generation).
  - **Acceptance criteria:**
    - [ ] S3 (Writing+Grammar) → 45; S1/S2 → 35; S4 review → 25; mock session → 60.
  - **Verification:** seed; sample one of each session type; assert XP.
  - **Dependencies:** None.
  - **Files:** `backend/app/seed.py`.
  - **Gap check:** [ ] Chưa implement.

- [ ] **Task 11: Main Quest full-XP routing to every matrix skill in the session.** *(M, backend)*
  - **Description:** When a Main Quest is claimed, credit its full earned XP to **each** matrix skill the session covers (parse the multi-skill column; map Grammar→Writing). Because a single `Quest.skill_id` can't represent 2 skills, decide the mechanism (recommended: keep `Quest.skill_id` as the primary and add a session→skills resolver in `recompute_skill_progress` that, for main quests, credits all covered matrix skills). Document the chosen mechanism in `quest.md` if it deviates.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §6 (Full-XP rule: full tier XP to every matrix skill in session) + §4 routing + `quest.md` §3.E; session skill columns from `material/material.md`.
  - **Acceptance criteria:**
    - [ ] Claiming an S2 main quest (35) raises BOTH Reading and Vocabulary by 35.
    - [ ] Main quests add no player XP directly (player only via averages).
    - [ ] No skill is double-credited within one claim.
  - **Verification:** claim an S2 main quest; assert Reading+35 and Vocabulary+35; player average recomputed.
  - **Dependencies:** Task 3, Task 5, Task 10.
  - **Files:** `backend/app/services.py`, `backend/app/seed.py`.
  - **Gap check:** [ ] Chưa implement.

### Checkpoint E (after Tasks 10–11)
- [ ] Main quest XP tiers correct; full-XP to all session skills; balance check vs §2.3 thresholds.

### Phase 7 — Writing/Speaking un-gate boss

- [ ] **Task 12: Make Writing/Speaking non-boss-gated.** *(S, backend)*
  - **Description:** Add `boss_gated` per skill (column on `skills` preferred; migration + seed). In `recompute_skill_progress`, when `boss_gated=False`, set `confirmed_rank = rank`, `promotion_status="none"`, `pending_rank=None` — never create a boss requirement.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §3.1 (Boss-gating per skill — Writing/Speaking NO) + §3 implementation note (`boss_gated` column); `player_level.md` §3.D.
  - **Acceptance criteria:**
    - [ ] Writing/Speaking with enough XP show `confirmed_rank == rank` and no "boss_required".
    - [ ] Vocabulary/Reading/Listening keep the boss flow.
  - **Verification:** push Writing XP over a rank threshold; assert confirmed_rank advances, no boss banner.
  - **Dependencies:** Task 1.
  - **Files:** `backend/app/models.py`, `backend/alembic/versions/*.py`, `backend/app/seed.py`, `backend/app/services.py`.
  - **Gap check:** [ ] Chưa implement.

### Checkpoint F (after Tasks 12–14)
- [ ] W/S confirmed_rank tracks XP; collocations seeded idempotently; "Collocation XP not rising" resolved (Vocabulary XP increases on collocation progress).

### Phase 8 — Collocation parser & seed

- [ ] **Task 13: Collocation markdown parser.** *(M, backend)*
  - **Description:** Parser for `material/vocabularies/month1-6/English_Collocations_campaign1-3_3-6.md` → in-memory structure (collection → sections `## N` → topics `_Section:_` → items). Tolerate noisy IPA, allow duplicates, `meaning_en=None`. Pure function, unit-testable.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §9 (Collocation Import — parser mapping + robustness requirements).
  - **Acceptance criteria:**
    - [ ] Parses ~1,467 items across 60 sections without raising.
    - [ ] A known row (`ancient monument`) maps all 5 columns correctly.
  - **Verification:** run parser on the file; assert counts and one sample row.
  - **Dependencies:** None.
  - **Files:** `backend/app/seed.py` (or a helper module).
  - **Gap check:** [ ] Chưa implement.

- [ ] **Task 14: Idempotent seed of collocations + campaign link.** *(M, backend)*
  - **Description:** Seed parsed data into `CollocationCollection/Section/Topic/Item` + `CampaignCollocationLink` for the active campaign, using `get_or_create` on `(collection, section_order, item_order, collocation)`. Re-running adds no duplicates.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §9 (idempotency key, campaign link, daily_collocation_target=3) + §8 (collocation → Vocabulary +5).
  - **Acceptance criteria:**
    - [ ] After two `/api/dev/reset` runs, `collocation_items` count is stable.
    - [ ] Collocation Forge daily quest can pull 3 items/day.
  - **Verification:** reset twice; assert stable counts; verify Vocabulary XP rises after progressing a collocation.
  - **Dependencies:** Task 13, Task 6.
  - **Files:** `backend/app/seed.py`.
  - **Gap check:** [ ] Chưa implement.

### Phase 9 — Policy tables (optional hardening)

- [ ] **Task 15: Add + seed the 4 XP policy tables and read from them.** *(L → split if needed, backend)*
  - **Description:** Implement `rank_xp_thresholds`, `quest_xp_policies`, `weekly_mission_xp_policies`, `main_quest_xp_policies` per XP policy §10; seed from §5–§7; switch generation/reward code to read policies (keep `quest_templates.base_xp` compatible). Split into per-table sub-tasks if it exceeds one session.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §10 (Recommended DB Policy Tables) + §5.1 (quest XP), §6 (main quest tiers), §7 (weekly mission XP), §2.3 (rank thresholds).
  - **Acceptance criteria:**
    - [ ] Generated quests read XP from policy rows (e.g. reading_daily=10, grammar_exercise=7→Writing).
    - [ ] Seed idempotent; no duplicate policy rows.
  - **Verification:** XP policy §12 Phase XP-3 validation list.
  - **Dependencies:** Tasks 1, 9, 10.
  - **Files:** `backend/app/models.py`, `backend/alembic/versions/*.py`, `backend/app/seed.py`, `backend/app/services.py`.
  - **Gap check:** [ ] Chưa implement.

### Phase 10 — Frontend

- [ ] **Task 16: Player shows RANK only; distinguish from skill rank.** *(M, frontend)*
  - **Description:** Top Bar / Roadmap Hero / Status Modal surface player **rank** (not raw XP/level as primary). Clearly label "Overall Rank" vs per-skill rank.
  - **Spec ref:** `player_level.md` §1 (player rank = only UI value) + §2 (Display & UX — player vs skill rank distinct) + `ielts_xp_policy_rank_quest_spec.md` §1.2.
  - **Acceptance criteria:**
    - [ ] Player rank visible; player raw XP not presented as a competing primary stat.
    - [ ] Skill matrix ranks visually distinct from player rank.
    - [ ] **(Gap from Task 3)** `frontend/src/dashboard-data.js` `buildDashboardView` (≈line 568-569) currently overwrites player level/rank by recomputing from `totalXp` via the stale FE formulas `getPlayerLevel` (`floor(totalXp/120)+1`) and `getPlayerRank` (`PLAYER_RANK_THRESHOLDS`). After Task 3, `total_xp` = avg of 5 skills (small number), so these FE formulas produce WRONG level/rank. Must consume backend `player_level`/`player_rank` directly (as `composePlayerProfile` at ≈line 638-640 already does), and delete or retire `getPlayerLevel`/`getPlayerRank`/`PLAYER_RANK_THRESHOLDS` (and update `dashboard-data.test.js` which still seeds `total_xp` and asserts the old curve).
    - [ ] **(Gap from Task 3)** `/summary` `total_xp` field (`main.py:726`) now equals `player_xp` = avg-of-5-skills, NOT a cumulative total. Either rename/retire it on the UI or stop surfacing it as "total XP" — the player surfaces RANK only.
  - **Verification:** browser smoke (devtools skill); compare against `/summary`; confirm displayed player level/rank == backend values (not FE-recomputed).
  - **Dependencies:** Task 3.
  - **Files:** `frontend/src/components/*`, `frontend/src/*`, `frontend/src/dashboard-data.js`, `frontend/src/dashboard-data.test.js`.
  - **Gap check:** [ ] Chưa implement.

- [ ] **Task 17: Daily board renders 9 slots; locked confirmed_rank state.** *(M, frontend)*
  - **Description:** Render 9 daily quest cards with correct XP labels; show completed-unclaimed (Claim button) distinctly from completed-claimed; show "Rank X (Boss required)" when `rank > confirmed_rank` for boss-gated skills; never show that state for Writing/Speaking.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §5 / §5.1 (9 slots + XP) + §3.1 (boss-gating); `daily_quest.md` §1.B; `player_level.md` §2 (locked confirmed_rank).
  - **Acceptance criteria:**
    - [ ] 9 cards render with §5.1 XP; claim flow visible.
    - [ ] Boss-required lock shows only for boss-gated skills.
  - **Verification:** browser smoke against a seeded day.
  - **Dependencies:** Tasks 9, 12.
  - **Files:** `frontend/src/components/*`.
  - **Gap check:** [ ] Chưa implement.

- [ ] **Task 18: Skill cards render support sources as buff lines (no separate tiles).** *(M, frontend)*
  - **Description:** Per owner decision (2026-06-09), Grammar/Collocation are **not** rendered as standalone skill-matrix tiles. Remove them from the matrix grid. Inside the **Writing** card add a secondary buff line `+N XP from Grammar`; inside the **Vocabulary** card add `+N XP from Collocation`. Source data: the `support_breakdown` field on each matrix skill from `/summary` (Tasks 5/6). No F–S rank/level shown for the support sources. If a buff XP is 0 (e.g. collocations not yet imported), show a muted/empty state rather than hiding the line entirely (so the learner knows the source exists).
  - **Spec ref:** `player_level.md` §2.A (Support sources in the UI — buff line, 5 tiles) + `ielts_xp_policy_rank_quest_spec.md` §1.1 UI note + §4 routing.
  - **Acceptance criteria:**
    - [ ] Skill matrix shows exactly 5 tiles (Listening, Reading, Writing, Speaking, Vocabulary). No Grammar/Collocation tile.
    - [ ] Writing card shows a Grammar buff line; Vocabulary card shows a Collocation buff line, each with the routed XP from `support_breakdown`.
    - [ ] Support buff lines have no rank/level badge; only the parent matrix skill carries rank.
  - **Verification:** browser smoke against `/summary`; confirm 5 tiles + 2 buff lines; values match `support_breakdown`.
  - **Dependencies:** Tasks 5, 6, 16.
  - **Files:** `frontend/src/components/*` (skill matrix / skill card components).
  - **Gap check:** [ ] Chưa implement.

### Checkpoint G (Complete)
- [ ] All acceptance criteria met; `alembic upgrade head` clean on empty+populated DB; Vite build passes; player rank + skill ranks correct end-to-end; collocation import activates Vocabulary XP. Ready for review.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Main Quest "one skill_id, two skills" representation | High | Use a session→skills resolver in recompute (Task 11) rather than schema change; document in `quest.md`. |
| Removing player accrual breaks callers (boss/mission/checkin) | High | Task 4 audit grep before/after; keep skill-side intact. |
| 9-slot migration on partially-migrated DBs | Med | Provide downgrade; test on populated + empty DB; keep constraint shape. |
| Skill recompute order (player avg before skills updated) | Med | Enforce ordering in `refresh_progress_state` (skills first, then player). |
| Curve makes S unreachable / too easy | Med | Validate §2.3 week-reached estimates after full-XP routing; tune only with data (XP policy §12). |
| Collocation parser chokes on noisy IPA | Low | Tolerant parsing (Task 13); unit test on the real file. |

## Open Questions (for owner before/while implementing)

- S4 "Review/Mini test/Error log" — which matrix skill receives its XP (dominant weekly skill?) and when is it `mock` (60) vs `review` (25)? Needs a rule for the seed resolver.
- ~~Should Grammar/Collocation `CampaignSkillState` rows be hidden from `/summary` matrix entirely, or shown as "support" without rank?~~ **RESOLVED (owner, 2026-06-09): show inside the parent skill card.** Grammar appears as a buff line inside the Writing card (`+N XP from Grammar`); Collocation as a buff line inside the Vocabulary card. They have **no independent F–S rank/level** and are **not** separate matrix tiles. `/summary` must expose, per matrix skill, a `support_breakdown` (source name + routed XP) so the frontend can render the buff line. See Task 5/6 (backend breakdown) + Task 18 (frontend card).
- Backfill policy for existing campaigns' already-claimed quest XP after routing changes (recompute on next refresh vs one-off migration).

## Deferred Backlog

- [ ] Writing Rank Boss Exam system (requires subjective grading/AI review)
- [ ] Speaking Rank Boss Exam system (requires audio recording and subjective grading/AI review)
- [ ] File-based certificate upload (OCR/parser)
- [ ] Email verification & password reset email integration
- [ ] OAuth/social login integration
- [ ] Multi-campaign support (multiple active campaigns and campaign switching UI)
- [x] Frontend onboarding name input + campaign selection + start date picker — DONE (session 7, browser-verified)
- [ ] Multi-campaign selection in onboarding — seed N templates, choose 1 of N (currently only 1 template seeded)
- [ ] Admin account management dashboard
- [ ] Batch apply/dismiss for suggestions — avoid N clicks when certificate creates N suggestions (O2)
- [ ] `campaign_skill_states.last_rank_change_at` timestamp — UI "Rank E since 3 days ago" (O3)
- [ ] Webhook/event on rank promotion for badge integration (O4)
- [ ] Badge unlock trigger on rank-up success
- [x] XP → player level progression mapping — SPEC'D (see "XP / Level / Rank Redesign" plan below; player level now derived from 5-skill average)
- [ ] Production deploy: add `Secure` flag to `ielts_rt` cookie (currently omitted for HTTP dev localhost)

## Known Risks

- Browser automation via Playwright: available (verified session 7).
- Manual smoke coverage exists, but automated backend coverage is still thin for the new migration behavior.
- Legacy compatibility fields still exist in the database by design.
- Badge/level integration with rank promotion is **not yet defined** — spec focuses on rank only (consistency review gap).
- Migration `30b9013e0a20` requires careful handling of duplicate indexes on partially-migrated databases.
- httpOnly cookie `ielts_rt` uses `SameSite=Lax` (no `Secure`) — safe for localhost HTTP dev only; must add `Secure=True` before production HTTPS deploy.
- **Pre-existing test failures — ALL FIXED (session 8d):**
  - ~~`TestCertificateAndSuggestionEndpoints.test_manual_certificate_creation_pre_campaign`~~ — FIXED: `activate_campaign` now calls `create_rank_suggestions_for_certificate` after linking certs.
  - ~~`TestCertificateAndSuggestionEndpoints.test_manual_certificate_creation_post_campaign`~~ — FIXED: `create_rank_suggestions_for_certificate` now infers Vocabulary/Grammar/Collocation from `overall_score`.
  - ~~`TestRankExamPhase9.test_quest_claim_suppresses_xp_when_boss_required`~~ — FIXED (session 8b).
  - **Whole suite: 44/44 PASS.**

## Where To Read More

- Completed Tasks: [tasks-done.md](tasks-done.md)
- Migration summary: [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)
- Latest validation: [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md)
- Latest implementation log: [docs/history/changelogs.md](docs/history/changelogs.md)
- Generic Codex guide (EN): [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md)
- Generic Codex guide (VI): [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md)
- Codex operator guide (EN): [docs/current/prompt-en.md](docs/current/prompt-en.md)
- Codex operator guide (VI): [docs/current/prompt-vi.md](docs/current/prompt-vi.md)
