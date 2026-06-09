# IELTS Quest Dashboard Tasks

Last updated: `2026-06-09` (session 8l — PLAN added + fully grilled: "Target / Suggest / Collocations Overhaul" (4 owner issues #1–#4). All decisions locked, 0 open questions. 12 tasks (I3-1; I1-1/2/3; I2-1/2; I4-1…I4-7). Phases 1–3: target String(20)/default 6.5, onboarding drops cert step (Welcome→Target→Campaign→StartDate→Confirm), editable panel via PATCH /api/player/targets, #3 stop-create + data-migration dismiss. Phase 4: own table collocation_flashcards, add-to-flashcard, neon decay 1 tier/7d (lazy-on-read), easy-graduates, re-add→again, 2-way flip, + review-5-distinct/day auto-completes Collocation Forge daily quest (claim manual). NOT yet implemented; see plan section below)

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

- **All Tasks 5–18 implemented + gap-checked (session 8h–8i). Checkpoint G ✓.** Suite: **60/1/0 BE** + **5/5 FE** + **build ✓**.

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
  - **Gap check:** [x] GAP-1 fixed (session 8g) — `main.py:get_campaign_skill_outputs` now filters `session_type != "Main Quest"` in support_xp_by_name query; `test_gap1_support_breakdown_excludes_main_quest_xp` PASS. → **Archived to tasks-done.md (session 8g)**

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
  - **Gap check:** [x] GAP-1 fixed (session 8g) — same fix as Task 5; Collocation support_breakdown also filtered to non-Main quests. → **Archived to tasks-done.md (session 8g)**

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
  - **Gap check:** [x] Audited (session 8f) — no gaps. `compute_vocabulary_xp` caps data-entry at 40 (`min(data_entry_xp,40)`) + `min(mastery,50)` separately; suite green. (Archive at Checkpoint GAP with the batch.)

### Checkpoint C (after Tasks 5–7)
- [x] Grammar→Writing, Collocation→Vocabulary verified (Tasks 5+6 done); vocab farm capped (Task 7 done); player average still sane.

### Phase 5 — 9 daily slots

- [x] **Task 8: Migration to widen daily_slot_code to 9 values.** *(M, migration)*
  - **Description:** Alembic migration `YYYYMMDD_NN_daily_slots_9.py`. Keep the column type/length and the unique constraint `(campaign_id, quest_date, daily_slot_code)`. If any enum/check constraint restricts the 3 old values, replace it with the 9-value set (`vocab_flashcard, vocab_codex, vocab_collocation, listening, reading, writing, speaking, grammar_review, grammar_exercise`). Provide `upgrade()`+`downgrade()`. Optionally backfill/relabel existing 3-slot rows.
  - **Spec ref:** `daily_quest.md` §1.B (9 daily_slot_code + unique constraint) + `ielts_xp_policy_rank_quest_spec.md` §5 (Daily Quest Structure).
  - **Acceptance criteria:**
    - [x] `alembic upgrade head` succeeds on a populated DB and on an empty DB.
    - [x] Inserting 9 distinct-slot daily quests for one date/campaign does not violate the unique constraint.
    - [x] `downgrade()` reverses cleanly.
  - **Verification:** upgrade on a seeded DB; insert 9 slots; assert no IntegrityError; downgrade.
  - **Dependencies:** None (schema), but land before Task 9.
  - **Files:** `backend/alembic/versions/*.py`, `backend/app/models.py` (comment/length if needed).
  - **Gap check:** [x] Audited (session 8f) — no gaps. Migration `20260609_15` is a no-op placeholder (column already `String(20)`, no enum/check constraint to widen); `upgrade()`/`downgrade()` clean. (Archive at Checkpoint GAP.)

- [x] **Task 9: Daily quest generation produces 9 slots/day.** *(M, backend)*
  - **Description:** Update daily-quest generation/seed to emit the 9 slots with correct skill_id and routed XP per XP policy §5.1. Grammar slots carry skill routing to Writing; collocation slot to Vocabulary.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §5.1 (Daily Quest XP table, per-slot XP + routing) + `daily_quest.md` §1.B.
  - **Acceptance criteria:**
    - [x] A generated day has exactly 9 daily quests with the 9 slot codes.
    - [x] Each quest's `base_xp`/`xp` matches the §5.1 table.
  - **Verification:** `/api/dev/reset`; inspect one day's daily quests = 9 rows, correct XP/skill.
  - **Dependencies:** Task 8, Task 5/6 (routing).
  - **Files:** `backend/app/seed.py`, `backend/app/services.py`.
  - **Gap check:** [x] Audited (session 8f) — no gaps. Quota seed = Vocab 3 + Reading 1 + Listening 1 + Grammar 2 + Writing 1 + Speaking 1 = **9 slots** (Collocation 0); `slot_mapping` defines 9 distinct slot codes; suite green. (Archive at Checkpoint GAP.)

### Checkpoint D (after Tasks 8–9)
- [x] 9 slots seed without constraint errors; XP per slot correct; existing data migrated.

### Phase 6 — Main Quest full-XP + skill tiering

- [x] **Task 10: Rewrite infer_main_quest_xp to tier by skill column.** *(S, backend)*
  - **Description:** Replace session-number tiering with skill-based tiering from the session's skill summary: Writing/Speaking-heavy → 45 (heavy_output); Listening/Reading → 35 (standard); Review/Error → 25; sectional/mock test → 60. Keep deterministic & idempotent.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §6 (Main Quest XP Policy — tier-by-skill table) + `quest.md` §3.E (Main Quest Seeding & XP Generation).
  - **Acceptance criteria:**
    - [x] S3 (Writing+Grammar) → 45; S1/S2 → 35; S4 review → 25; mock session → 60.
  - **Verification:** seed; sample one of each session type; assert XP.
  - **Dependencies:** None.
  - **Files:** `backend/app/seed.py`.
  - **Gap check:** [x] Audited (session 8f) — no gaps. `infer_main_quest_xp` returns 45/35/25/60 by session+keywords and reads `MainQuestXpPolicy` when `db` passed; `test_main_quest_xp_and_routing` green. (Archive at Checkpoint GAP.)

- [x] **Task 11: Main Quest full-XP routing to every matrix skill in the session.** *(M, backend)*
  - **Description:** When a Main Quest is claimed, credit its full earned XP to **each** matrix skill the session covers (parse the multi-skill column; map Grammar→Writing). Because a single `Quest.skill_id` can't represent 2 skills, decide the mechanism (recommended: keep `Quest.skill_id` as the primary and add a session→skills resolver in `recompute_skill_progress` that, for main quests, credits all covered matrix skills). Document the chosen mechanism in `quest.md` if it deviates.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §6 (Full-XP rule: full tier XP to every matrix skill in session) + §4 routing + `quest.md` §3.E; session skill columns from `material/material.md`.
  - **Acceptance criteria:**
    - [x] Claiming an S2 main quest (35) raises BOTH Reading and Vocabulary by 35.
    - [x] Main quests add no player XP directly (player only via averages).
    - [x] No skill is double-credited within one claim.
  - **Verification:** claim an S2 main quest; assert Reading+35 and Vocabulary+35; player average recomputed.
  - **Dependencies:** Task 3, Task 5, Task 10.
  - **Files:** `backend/app/services.py`, `backend/app/seed.py`.
  - **Gap check:** [x] Audited (session 8f) — no gaps. `resolve_main_quest_covered_skills` maps S1→{Listening,Speaking}, S2→{Reading,Vocabulary}, S3→{Writing}, S4→primary; `recompute_skill_progress` credits full `earned_xp` to each covered skill, no double-count; `test_main_quest_xp_and_routing` green. (Archive at Checkpoint GAP.)

### Checkpoint E (after Tasks 10–11)
- [x] Main quest XP tiers correct; full-XP to all session skills; balance check vs §2.3 thresholds.

### Phase 7 — Writing/Speaking un-gate boss

- [x] **Task 12: Make Writing/Speaking non-boss-gated.** *(S, backend)*
  - **Description:** Add `boss_gated` per skill (column on `skills` preferred; migration + seed). In `recompute_skill_progress`, when `boss_gated=False`, set `confirmed_rank = rank`, `promotion_status="none"`, `pending_rank=None` — never create a boss requirement.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §3.1 (Boss-gating per skill — Writing/Speaking NO) + §3 implementation note (`boss_gated` column); `player_level.md` §3.D.
  - **Acceptance criteria:**
    - [x] Writing/Speaking with enough XP show `confirmed_rank == rank` and no "boss_required".
    - [x] Vocabulary/Reading/Listening keep the boss flow.
  - **Verification:** push Writing XP over a rank threshold; assert confirmed_rank advances, no boss banner.
  - **Dependencies:** Task 1.
  - **Files:** `backend/app/models.py`, `backend/alembic/versions/*.py`, `backend/app/seed.py`, `backend/app/services.py`.
  - **Gap check:** [x] Audited (session 8f) — no gaps. Migration `20260609_16` adds `skills.boss_gated` (default 1); seed sets Writing/Speaking=False, others=True; `recompute_skill_progress` auto-confirms rank when `not boss_gated`; `test_non_boss_gated_skills` green. (Archive at Checkpoint GAP.)

### Checkpoint F (after Tasks 12–14)
- [x] W/S confirmed_rank tracks XP; collocations seeded idempotently; "Collocation XP not rising" resolved (Vocabulary XP increases on collocation progress).

### Phase 8 — Collocation parser & seed

- [x] **Task 13: Collocation markdown parser.** *(M, backend)*
  - **Description:** Parser for `material/vocabularies/month1-6/English_Collocations_campaign1-3_3-6.md` → in-memory structure (collection → sections `## N` → topics `_Section:_` → items). Tolerate noisy IPA, allow duplicates, `meaning_en=None`. Pure function, unit-testable.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §9 (Collocation Import — parser mapping + robustness requirements).
  - **Acceptance criteria:**
    - [x] Parses ~1,467 items across 60 sections without raising.
    - [x] A known row (`ancient monument`) maps all 5 columns correctly.
  - **Verification:** run parser on the file; assert counts and one sample row.
  - **Dependencies:** None.
  - **Files:** `backend/app/seed.py` (or a helper module).
  - **Gap check:** [x] GAP-2 fixed (session 8g) — seed dedup key changed to `(item_order, collocation)`; parser allows duplicates; `test_gap2_collocation_seed_allows_duplicate_strings_different_order` PASS. → **Archived to tasks-done.md (session 8g)**

- [x] **Task 14: Idempotent seed of collocations + campaign link.** *(M, backend)*
  - **Description:** Seed parsed data into `CollocationCollection/Section/Topic/Item` + `CampaignCollocationLink` for the active campaign, using `get_or_create` on `(collection, section_order, item_order, collocation)`. Re-running adds no duplicates.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §9 (idempotency key, campaign link, daily_collocation_target=3) + §8 (collocation → Vocabulary +5).
  - **Acceptance criteria:**
    - [x] After two `/api/dev/reset` runs, `collocation_items` count is stable.
    - [x] Collocation Forge daily quest can pull 3 items/day.
  - **Verification:** reset twice; assert stable counts; verify Vocabulary XP rises after progressing a collocation.
  - **Dependencies:** Task 13, Task 6.
  - **Files:** `backend/app/seed.py`.
  - **Gap check:** [x] GAP-2 fixed (session 8g) — same fix as Task 13; `ensure_collocations` dedup key `(item_order, collocation)`; idempotency preserved; stable count on real file (1409). → **Archived to tasks-done.md (session 8g)**

### Phase 9 — Policy tables (optional hardening)

- [x] **Task 15: Add + seed the 4 XP policy tables and read from them.** *(L → split if needed, backend)*
  - **Description:** Implement `rank_xp_thresholds`, `quest_xp_policies`, `weekly_mission_xp_policies`, `main_quest_xp_policies` per XP policy §10; seed from §5–§7; switch generation/reward code to read policies (keep `quest_templates.base_xp` compatible). Split into per-table sub-tasks if it exceeds one session.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §10 (Recommended DB Policy Tables) + §5.1 (quest XP), §6 (main quest tiers), §7 (weekly mission XP), §2.3 (rank thresholds).
  - **Acceptance criteria:**
    - [x] Generated quests read XP from policy rows (e.g. reading=10, grammar_exercise=7→Writing). `test_daily_quest_xp_from_policy` PASS.
    - [x] Seed idempotent; no duplicate policy rows. `test_policy_idempotent` PASS.
  - **Verification:** 6 new tests in `TestPolicyTables` — all PASS. Suite 56/1/0.
  - **Dependencies:** Tasks 1, 9, 10.
  - **Files:** `backend/app/seed.py` (wire `ensure_policy_tables` into both `seed_database` + `activate_campaign_for_player`), `backend/app/test_backend.py`.
  - **Gap check:** [x] All 4 gaps patched (session 8h) — GAP-15-1 db= pass, GAP-15-2 reset wipes policy tables, GAP-15-3 speaking+grammar weekly patterns added, GAP-15-4 self-resolved. Suite ≥56/1/0. → **Archived to tasks-done.md (session 8h)**

### Phase 10 — Frontend

- [x] **Task 16: Player shows RANK only; distinguish from skill rank.** *(M, frontend)*
  - **Description:** Top Bar / Roadmap Hero / Status Modal surface player **rank** (not raw XP/level as primary). Clearly label "Overall Rank" vs per-skill rank.
  - **Spec ref:** `player_level.md` §1 (player rank = only UI value) + §2 (Display & UX — player vs skill rank distinct) + `ielts_xp_policy_rank_quest_spec.md` §1.2.
  - **Acceptance criteria:**
    - [x] Player rank visible; player raw XP not presented as a competing primary stat. `buildDashboardView` now passes `player_rank` from backend directly.
    - [x] Skill matrix ranks visually distinct from player rank. Backend `player_rank` ≠ per-skill `rank` field.
    - [x] **(Gap from Task 3)** `PLAYER_RANK_THRESHOLDS`, `getPlayerLevel`, `getPlayerRank` removed from `dashboard-data.js`. `buildDashboardView` lines 568-569 now read `player.player_level` / `player.player_rank` from backend. `buildPlayerSnapshot` fallback no longer calls stale FE fns. `getPlayerXpProgress` default param updated.
    - [x] **(Gap from Task 3)** `total_xp` not surfaced as "total XP" primary stat — `rank` field in `buildDashboardView` now comes from `player.player_rank` (backend avg-of-5-skills rank). Dashboard consumes rank label only.
  - **Verification:** `npm run test:dashboard-data` 5/5 PASS; `npm run build` ✓ 222 modules 0 errors.
  - **Dependencies:** Task 3.
  - **Files:** `frontend/src/dashboard-data.js`.
  - **Gap check:** [x] Audited (session 8h); **GAP-16-1 fixed session 8j** — `getPlayerXpProgress` previously used a flat `(level-1)*120` curve that did NOT match the backend `19*(L^1.6-1)` curve (StatusModal XP bar % + "XP to next level" were wrong, e.g. 900 XP @ L11 showed 0%/420 instead of 29%/94). Rewrote to mirror backend `_LEVEL_XP` floors + max-level cap + null-level fallback; regression test `getPlayerXpProgress mirrors the backend...` PASS (6/6 FE). → **Archived to tasks-done.md (session 8h; GAP-16-1 session 8j).**

- [x] **Task 17: Daily board renders 9 slots; locked confirmed_rank state.** *(M, frontend)*
  - **Description:** Render 9 daily quest cards with correct XP labels; show completed-unclaimed (Claim button) distinctly from completed-claimed; show "Rank X (Boss required)" when `rank > confirmed_rank` for boss-gated skills; never show that state for Writing/Speaking.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §5 / §5.1 (9 slots + XP) + §3.1 (boss-gating); `daily_quest.md` §1.B; `player_level.md` §2 (locked confirmed_rank).
  - **Acceptance criteria:**
    - [x] 9 cards render with §5.1 XP; `SlotChip` shows slot label per `SLOT_LABELS` map; `is-claim-ready` CSS class + gold border distinguishes completed-unclaimed from claimed.
    - [x] `BossLockBadge` shows when `promotion_status != "none"` — reads from skills array via `skillStatusMap`; Writing/Speaking never show boss lock (backend never sets boss_required for non-boss-gated skills).
  - **Verification:** `npm run build` ✓ 0 errors. Browser smoke pending (requires running stack).
  - **Dependencies:** Tasks 9, 12.
  - **Files:** `frontend/src/components/DailyQuestPanel.jsx`, `frontend/src/components/QuestOverlay.jsx`, `frontend/src/App.jsx`, `frontend/src/styles.css`.
  - **Gap check:** [x] Audited (session 8h) — no blocking gaps. `boss_gated` not exposed in `SkillOut` — not needed: `promotion_status="none"` for W/S guarantees badge never shows. → **Archived to tasks-done.md (session 8h)**

- [x] **Task 18: Skill cards render support sources as buff lines (no separate tiles).** *(M, frontend)*
  - **Description:** Per owner decision (2026-06-09), Grammar/Collocation are **not** rendered as standalone skill-matrix tiles. Remove them from the matrix grid. Inside the **Writing** card add a secondary buff line `+N XP from Grammar`; inside the **Vocabulary** card add `+N XP from Collocation`. Source data: the `support_breakdown` field on each matrix skill from `/summary` (Tasks 5/6). No F–S rank/level shown for the support sources. If a buff XP is 0 (e.g. collocations not yet imported), show a muted/empty state rather than hiding the line entirely (so the learner knows the source exists).
  - **Spec ref:** `player_level.md` §2.A (Support sources in the UI — buff line, 5 tiles) + `ielts_xp_policy_rank_quest_spec.md` §1.1 UI note + §4 routing.
  - **Acceptance criteria:**
    - [x] Skill matrix shows exactly 5 tiles — backend `MATRIX_SKILLS` excludes Grammar/Collocation from `/summary` skills list; FE renders whatever backend sends (no FE filter needed). Compact mode (`StatusModal`) similarly unaffected.
    - [x] Writing card shows a Grammar buff line; Vocabulary card shows a Collocation buff line, each with the routed XP from `support_breakdown`. Rendered by `SupportBuffLines` component in full mode only.
    - [x] Support buff lines have no rank/level badge; only the parent matrix skill carries rank. `SupportBuffLines` renders plain `+N XP from {source}` text (no `skill-rank-badge`).
  - **Verification:** `npm run build` ✓ 0 errors. Browser smoke pending (requires running stack).
  - **Dependencies:** Tasks 5, 6, 16.
  - **Files:** `frontend/src/components/SkillCards.jsx`, `frontend/src/styles.css`.
  - **Gap check:** [x] Audited; **GAP-18-1 fixed session 8j** — original implementation put `SupportBuffLines` ONLY in the non-compact `SkillCards` branch, but that branch is reachable solely via `SkillMatrixPanel`, which is **imported nowhere** (dead component). The single live skill-card render is `StatusModal` in `compact` mode → buff lines never displayed. Fix: also render `SupportBuffLines` in the compact branch (the live surface). Dead `SkillMatrixPanel` + full-mode branch flagged for cleanup (background task). Grammar/Collocation tile exclusion is backend (MATRIX_SKILLS). `support_breakdown` passthrough via `...skill`. Build ✓. → **Archived to tasks-done.md (session 8i; GAP-18-1 session 8j).**

### Checkpoint G (Complete)
- [x] All acceptance criteria met; `alembic upgrade head` clean on empty+populated DB; Vite build passes ✓; player rank + skill ranks correct end-to-end; collocation import activates Vocabulary XP. **Session 8i: Task 18 implemented + gap-checked. Session 8j: Phase 10 gap audit (GAP-16-1, GAP-18-1) fixed.** Ready for review.

---

## Phase GAP-FIX-3 — Patches from Phase 10 (Frontend) gap audit (session 8j)

> Audit context: deep re-read of the live render paths for Tasks 16/17/18. Two gaps found — both **user-facing** (wrong numbers / invisible feature), unlike the earlier latent gaps. Fixed + locked with a FE test where applicable.

- [x] **Task GAP-16-1: `getPlayerXpProgress` must mirror the backend level curve.** *(S, frontend)*
  - **Description:** `getPlayerXpProgress` computed level floors as `(level-1)*120` / `level*120` — a flat 120-XP-per-level step that does NOT match the backend curve `xp(L)=round(19*(L^1.6-1))` (`services.py:_LEVEL_XP`). The StatusModal XP bar `percent` and "N XP to next level" were therefore wrong for every level > 1. Example: 900 XP at L11 (rank E) → old code returned 0% / 420 XP (floor 1200 > 900, clamped), real answer 29% / 94 XP (floor 862, next 994).
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §2.1 (level curve formula) — must equal backend `_LEVEL_XP`.
  - **Acceptance criteria:**
    - [x] FE builds a `LEVEL_XP_FLOORS` table identical to backend `_LEVEL_XP` (`round(19*(L^1.6-1))`, L 1..60).
    - [x] `getPlayerXpProgress` uses the curve floors; handles max level 60 (bar 100%, remaining 0) and null level (derive from XP, no NaN).
    - [x] Regression test asserts L11/L1/L60/null cases against real backend floors (862, 994, 0, 13279). `getPlayerXpProgress mirrors the backend...` PASS.
  - **Verification:** `npm run test:dashboard-data` 6/6 PASS; `npm run build` ✓.
  - **Dependencies:** Task 16.
  - **Files:** `frontend/src/dashboard-data.js`, `frontend/src/dashboard-data.test.js`.
  - **Gap check:** [x] Done — fix + test landed (session 8j).

- [x] **Task GAP-18-1: Support buff lines must render on the LIVE skill-card surface.** *(S, frontend)*
  - **Description:** Task 18 added `SupportBuffLines` only to the **non-compact** branch of `SkillCards`. That branch renders solely through `SkillMatrixPanel`, which is **imported nowhere** (dead component). The only live `SkillCards` render is `StatusModal` in `compact` mode → the buff lines never appeared to the user, so Task 18's acceptance ("Writing card shows Grammar buff line") was not actually met in the running app. Fix: render `SupportBuffLines` in the compact branch too. Dead `SkillMatrixPanel.jsx` + full-mode branch flagged for separate cleanup (background task).
  - **Spec ref:** `player_level.md` §2.A (buff line inside the parent skill card) + Task 18 acceptance.
  - **Acceptance criteria:**
    - [x] `SupportBuffLines` renders in the compact `SkillCards` branch (StatusModal "Skill Matrix").
    - [x] Writing compact card shows the Grammar buff; Vocabulary compact card shows the Collocation buff; muted `—` when XP 0.
    - [x] Build clean.
  - **Verification:** `npm run build` ✓. Browser smoke pending (requires running stack).
  - **Dependencies:** Task 18.
  - **Files:** `frontend/src/components/SkillCards.jsx`.
  - **Gap check:** [x] Done — fix landed (session 8j). **Dead-code cleanup completed (session 8j):** deleted `SkillMatrixPanel.jsx` (imported nowhere) and the unreachable non-compact branch of `SkillCards.jsx`; removed now-unused `formatDate` import; `compact` prop dropped from the signature (the live StatusModal call still passes it harmlessly). Build + 6/6 FE green.

### Checkpoint GAP-3 (after GAP-16-1, GAP-18-1)
- [x] Both Phase 10 gaps fixed (session 8j); FE 6/6 PASS; build ✓. Player XP bar now matches backend curve; support buff lines visible on the live StatusModal skill matrix; dead `SkillMatrixPanel` + full-mode `SkillCards` branch removed.

---

## Phase GAP-FIX — Patches from Tasks 5–14 gap audit (session 8f)

> Audit context: test suite **48 passed / 1 skipped / 0 fail** at audit time. Both gaps below are **latent** (not triggered by current seed data) but violate the Task 5/6 "no double-count" contract and the §9 "allow duplicates" robustness requirement. Fix defensively + lock behavior with a test, then flip the matching tasks' gap-check to `[x]`.

- [x] **Task GAP-1: Match `support_breakdown` to actually-folded XP (exclude Main Quests).** *(XS, backend)*
  - **Description:** In `main.py:get_campaign_skill_outputs` (~line 340), the query computing `support_xp_by_name` sums **all** Grammar/Collocation claimed quests, but `recompute_skill_progress` (services.py:728) folds only **non-Main** support quests into the matrix skill (Main Quests are routed separately via `resolve_main_quest_covered_skills`, which maps to MATRIX skills only). Add `Quest.session_type != "Main Quest"` to the `support_xp_by_name` query so `support_breakdown.xp` always equals the Grammar/Collocation XP actually folded into Writing/Vocabulary `state.xp` (Task 5/6 "no double-count" contract).
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §1.1, §4 (routing) + Task 5/6 acceptance ("Sum of routed support XP must equal the contribution already folded ... no double-count").
  - **Acceptance criteria:**
    - [x] `support_xp_by_name` query filters `session_type != "Main Quest"`.
    - [x] New test: Grammar Main Quest (100 XP claimed) + Grammar Daily (30 XP claimed) → Writing `support_breakdown[Grammar].xp` == 30 (Main excluded). `test_gap1_support_breakdown_excludes_main_quest_xp` PASS.
  - **Verification:** full suite 50/1/0 PASS.
  - **Dependencies:** None.
  - **Files:** `backend/app/main.py`, `backend/app/test_backend.py`.
  - **Gap check:** [x] Done — fix + test landed (session 8g). → **Archived to tasks-done.md (session 8g)**

- [x] **Task GAP-2: Collocation seed must keep intra-topic duplicates.** *(S, backend)*
  - **Description:** `ensure_collocations` (seed.py ~line 2204) dedups items by `collocation` string per topic, so a duplicated collocation within one topic is silently dropped — violating §9 "allow duplicates". Change the idempotency key to `(topic_id, item_order, collocation)` so re-seeding stays idempotent while duplicates are preserved. (Current real file: 60 sections / 1409 items / 0 dup topics → no behavior change today; this is robustness for noisy future imports.)
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §9 (idempotency key `(collection, section_order, item_order, collocation)`, allow duplicates).
  - **Acceptance criteria:**
    - [x] Two `ensure_collocations` runs → stable `collocation_items` count (idempotent preserved).
    - [x] Fixture topic with two identical `collocation` strings (item_order=1, item_order=2) seeds **2** rows, not 1; idempotent on second run. `test_gap2_collocation_seed_allows_duplicate_strings_different_order` PASS.
  - **Verification:** full suite 50/1/0 PASS; real file seeded count 1409 stable.
  - **Dependencies:** None.
  - **Files:** `backend/app/seed.py`, `backend/app/test_backend.py`.
  - **Gap check:** [x] Done — fix + test landed (session 8g). → **Archived to tasks-done.md (session 8g)**

### Checkpoint GAP (after GAP-1, GAP-2)
- [x] Both patches landed (session 8g); suite 50/1/0; Tasks 5, 6, 13, 14 gap-check `[x]` (GAP-1 + GAP-2 resolved); Tasks 7–12 gap-check `[x]` (no gaps found); archived Tasks 5–14 to `tasks-done.md`.

---

## Phase GAP-FIX-2 — Patches from Task 15 gap audit (session 8g)

> Audit context: Task 15 implemented (session 8g) — 4 policy tables + migration `20260609_17` + `ensure_policy_tables` wired into `seed_database` & `activate_campaign_for_player`; daily quest XP, weekly mission XP, and `RankXpThreshold` reads confirmed; 6 `TestPolicyTables` tests pass; suite **56/1/0**. Audit then found 4 residual gaps below — all **latent** (current hard-code values == policy values, so behavior unchanged today) but they break the §10 "single source of truth / avoid hard-coding" intent or leave dead/uncleaned rows. Fix each + lock with a test where applicable, then flip Task 15 gap-check `[x]`.

- [x] **Task GAP-15-1: Main quest XP must read `MainQuestXpPolicy` (close the hard-code path).** *(XS, backend)*
  - **Description:** `infer_main_quest_xp(session_no, skill_summary, task_detail, db=None)` (seed.py:679) reads `MainQuestXpPolicy` only when `db` is passed, but all 4 callsites in `ensure_main_quest_instances` (seed.py:1457, 1458, 1475, 1486) call it **without `db=`** → main quest XP always falls through to the hard-coded tier values (45/35/25/60), never the policy table. Violates §10 ("avoid hard-coding"). Latent because the hard-code matches the seed values today. Pass `db=db` to all 4 calls so `MainQuestXpPolicy` is the source of truth.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §10 (DB policy tables, avoid hard-coding) + §6 (main quest tiers).
  - **Acceptance criteria:**
    - [x] All 4 `infer_main_quest_xp(...)` calls in `ensure_main_quest_instances` pass `db=db`.
    - [x] New test: mutate a `MainQuestXpPolicy.xp_reward` row (e.g. `standard` 35→40), re-run main-quest seeding, assert the matching main quest `base_xp`/`xp` reflects 40 (proves policy is read, not hard-code). `test_main_quest_xp_reads_policy_not_hardcode` PASS.
  - **Verification:** `pytest -k "policy or main_quest"`; full suite ≥56 pass.
  - **Dependencies:** Task 15.
  - **Files:** `backend/app/seed.py`, `backend/app/test_backend.py`.
  - **Gap check:** [x] Done — fix + test landed (session 8h). → **Archived to tasks-done.md at Checkpoint GAP-2.**

- [x] **Task GAP-15-2: `reset_database` must wipe the 4 policy tables.** *(XS, backend)*
  - **Description:** `reset_database` (main.py:1446 delete-list) omits `RankXpThreshold`, `QuestXpPolicy`, `WeeklyMissionXpPolicy`, `MainQuestXpPolicy`, so `/api/dev/reset` never truly resets them. The idempotent get-or-create in `ensure_policy_tables` hides this (no duplicates, values re-asserted), but a "reset" that leaves rows untouched is misleading and would mask a future seed bug. Add the 4 models to the delete-list (FK-safe: they have no inbound FKs, so order is free — place near the other policy/template deletes). Import them in main.py if not already.
  - **Spec ref:** Task 15 acceptance ("Seed idempotent; no duplicate policy rows") + repo rule "`/api/dev/reset` works".
  - **Acceptance criteria:**
    - [x] 4 policy models added to `reset_database` delete-list; imports present (`RankXpThreshold`, `QuestXpPolicy`, `WeeklyMissionXpPolicy`, `MainQuestXpPolicy` imported and in delete-list before `Skill`).
    - [x] After two `/api/dev/reset` runs the policy row counts are correct and stable (7 ranks, 9 quest, 7 weekly, 5 main).
  - **Verification:** smoke `/api/dev/reset` ×2 → query 4 tables; `pytest -k policy` still green.
  - **Dependencies:** Task 15.
  - **Files:** `backend/app/main.py`.
  - **Gap check:** [x] Done — fix landed (session 8h). → **Archived to tasks-done.md at Checkpoint GAP-2.**

- [x] **Task GAP-15-3: Give `speaking_weekly` + `grammar_weekly` policy rows a reader (or drop them).** *(XS, backend)*
  - **Description:** `ensure_policy_tables` seeds 7 `WeeklyMissionXpPolicy` rows, but `map_weekly_pattern_to_mission_type` (seed.py:715) only maps the 4 seeded weekly pattern codes (`balanced→listening_weekly`, `reading→reading_weekly`, `vocabulary→vocab_weekly`, `output→writing_weekly`) + `onboarding`. So `speaking_weekly` and `grammar_weekly` rows are never read — dead data. Per §7 both Speaking (45) and Grammar (45→Writing) are real weekly rewards. **Recommended:** add a Speaking-focus and Grammar-focus weekly pattern (with matching `pattern_code` substrings) + map branches so all 7 policy rows have a reader. Alternative (if owner prefers fewer missions): drop the 2 unused rows from the seed.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §7 (Weekly XP: Speaking 45, Grammar 45→Writing).
  - **Acceptance criteria:**
    - [x] Every seeded `WeeklyMissionXpPolicy.mission_type` is reachable from at least one seeded weekly `pattern_code` via `map_weekly_pattern_to_mission_type` (no dead rows). Added `speaking-focus` + `grammar-focus` patterns + `map_weekly_pattern_to_mission_type` branches `"speaking"→speaking_weekly`, `"grammar"→grammar_weekly`.
    - [x] A generated week surfaces Speaking-focus and Grammar-focus missions. `test_speaking_weekly_missions_seeded` + `test_grammar_weekly_missions_seeded` PASS. Full mapping coverage asserted in `test_all_weekly_policy_mission_types_reachable`.
  - **Verification:** assert mapping coverage in a test; `pytest -k weekly` green.
  - **Dependencies:** Task 15.
  - **Files:** `backend/app/seed.py`, `backend/app/test_backend.py`.
  - **Gap check:** [x] Done — fix + 3 tests landed (session 8h). → **Archived to tasks-done.md at Checkpoint GAP-2.**

- [x] **Task GAP-15-4: Fix stale spec-ref in Task 15 verification line.** *(Trivial, docs)*
  - **Description:** Task 15 "Verification" cited "XP policy §12 Phase XP-3 validation list" — no such section exists (`ielts_xp_policy_rank_quest_spec.md` §12 = "Notes for Future Tuning"). Repoint to the real §11 (Final Values Summary) which lists the canonical XP numbers the policy tables must match.
  - **Spec ref:** `ielts_xp_policy_rank_quest_spec.md` §11 (Final Values Summary).
  - **Acceptance criteria:**
    - [x] Task 15 verification line no longer references the nonexistent §12 Phase XP-3 list. Audited: no "Phase XP-3" string exists in TASKS.md outside this task's own description — stale ref was never written into Task 15's Verification field directly; the field was already clean. GAP-15-4 self-resolved.
  - **Verification:** grep TASKS.md for "Phase XP-3" → 0 hits outside this description.
  - **Dependencies:** None.
  - **Files:** `TASKS.md`.
  - **Gap check:** [x] Done — self-resolved on audit (session 8h). → **Archived to tasks-done.md at Checkpoint GAP-2.**

### Checkpoint GAP-2 (after GAP-15-1 … GAP-15-4)
- [x] All 4 patches landed (session 8h); full suite passes (≥56/1/0); main quest XP reads `MainQuestXpPolicy` (GAP-15-1), reset wipes 4 policy tables (GAP-15-2), all `WeeklyMissionXpPolicy` rows reachable (GAP-15-3), stale spec-ref self-resolved (GAP-15-4). **Task 15** gap-check `[x]` → archived to `tasks-done.md`.

> **Audit verdict per task (session 8f):** Tasks 7, 8, 9, 10, 11, 12 — **no gaps found** (code matches acceptance; suite green; quota seed = 9 slots; boss_gated seeded W/S=False; main-quest tiers via policy table). Tasks 5, 6 — blocked by **GAP-1**. Tasks 13, 14 — blocked by **GAP-2** (robustness only). Task 15 note: `ensure_policy_tables` + `infer_main_quest_xp(db=...)` already read `MainQuestXpPolicy` — Task 15 is **partially implemented**; revisit its checklist before claiming done.

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
  - **Whole suite: 50/50 PASS (session 8g, 1 skipped).**

---

## Archived Plan: Deterministic Demo Player + Neutral Register Fallback (hereisadraftripplingwind.md)

> Source plan: `plans/hereisadraftripplingwind.md`. All steps completed in **session 7**. Transcribed here for traceability with gap checks.

### Context

Root cause: `seed.py:ensure_player()` used `Player.first()` — nondeterministic, could corrupt real users' data. `register()` hardcoded `"IELTS Hunter"`. `activate-campaign` took no body.

- [x] **Step 1: Extract `ensure_demo_account`, make `ensure_player` deterministic.** *(S, backend)*
  - **Description:** Added `ensure_demo_account(db) -> Account` helper with idempotent dev+ad00000 account creation. Rewrote `ensure_player` to query `Player.filter(account_id == demo_account.id).first()` instead of `Player.first()`. New Player created with `account_id=demo_account.id` at birth. `Player.first()` removed entirely.
  - **Acceptance criteria:**
    - [x] `Player.first()` no longer appears in `seed.py`.
    - [x] `ensure_player` always returns the Player owned by `ad00000@gmail.com`.
    - [x] Re-running seed on a DB with real user accounts does NOT attach demo Campaign/Quests to a real user's Player.
  - **Verification:** grep `Player.first()` in seed.py → 0 hits; `/api/dev/reset` × 2 → stable count, ad00000 owns exactly 1 Player.
  - **Files:** `backend/app/seed.py`.
  - **Gap check:** [x] Done (session 7) — deterministic seed confirmed in Session Resume line. `Player.first()` removed. No corruption path remains.

- [x] **Step 2: Simplify `ensure_account_and_profile`, remove stale `player.account_id` reassignment.** *(XS, backend)*
  - **Description:** Replaced inline dev/ad00000 creation inside `ensure_account_and_profile` with call to `ensure_demo_account(db)`. Removed `player.account_id = main_account.id` line (Player already linked at creation in Step 1). `AccountPreference` + `PlayerLearningProfile` creation preserved.
  - **Acceptance criteria:**
    - [x] `ensure_account_and_profile` no longer reassigns `player.account_id`.
    - [x] Seed call order in `seed_database` unchanged; function stays idempotent.
  - **Verification:** `seed_database()` runs without error on fresh and populated DB.
  - **Files:** `backend/app/seed.py`.
  - **Gap check:** [x] Done (session 7) — idempotency preserved; no duplicate Player created on re-seed.

- [x] **Step 3: Neutral register fallback — drop `"IELTS Hunter"` hardcode.** *(XS, backend)*
  - **Description:** In `register()` (`main.py`), compute `name = (display_name or "").strip() or email_normalized.split("@")[0] or "New Hunter"`. Use that for `Account.display_name` and `Player.name`/`Player.display_name`. No `"IELTS Hunter"` string in the register path.
  - **Acceptance criteria:**
    - [x] Registering with no display_name → name derived from email prefix, not `"IELTS Hunter"`.
    - [x] Registering with a display_name → that name used.
  - **Verification:** register new account without display_name → `GET /api/auth/me` returns email-prefix name.
  - **Files:** `backend/app/main.py`.
  - **Gap check:** [x] Done (session 7) — Session Resume: "Register fallback dùng email prefix thay `'IELTS Hunter'`". `/api/auth/me` verified.

- [x] **Step 4: `activate-campaign` accepts optional `display_name` + `campaign_template_code` body.** *(S, backend)*
  - **Description:** Added `OnboardingActivateIn(display_name, campaign_template_code)` schema. Route signature changed to `body: OnboardingActivateIn | None = None` (backward-compatible). Body applied: if `body.display_name` → set `player.display_name` + `player.name`; `template_code` forwarded to `activate_campaign_for_player`. Default code `"ielts_18_month_foundation"` preserved.
  - **Acceptance criteria:**
    - [x] `POST /api/onboarding/activate-campaign` with no body → existing behavior unchanged.
    - [x] With `{"display_name":"Test", "campaign_template_code":"ielts_18_month_foundation"}` → player name updated, correct campaign activated.
    - [x] Schema `OnboardingActivateIn` defined in `schemas.py` and imported in `main.py`.
  - **Verification:** Session 7 — Onboarding 5-step UI wired to this endpoint, browser-verified.
  - **Files:** `backend/app/schemas.py`, `backend/app/main.py`.
  - **Gap check:** [x] Done (session 7) — Onboarding flow browser-verified. Endpoint accepts optional body; no regression on no-body callers.

### Checkpoint (hereisadraftripplingwind plan — Complete)
- [x] All 4 steps done (session 7). Deterministic seed: demo Player always `ad00000@gmail.com`, no `Player.first()`. Neutral name fallback from email prefix. `activate-campaign` optional body accepted. Onboarding UI wired end-to-end.

### Deferred items from this plan (still open)
- [ ] **Multi-campaign selection in onboarding** — seed N templates, choose 1 of N (currently only 1 template seeded). Tracked in Deferred Backlog above.
- [ ] **Runtime isolation test** — register new account → verify its Player/Campaign data completely separate from ad00000's. Not yet automated (manual only).

---

## Completed Plan: Main Quest Start-Date Rebase (lazy-purring-sundae.md)

> **DONE (session 8k).** All MQ-1/2/3 + Checkpoints MQ-A/MQ-B complete + live-smoke verified. Archived to [tasks-done.md](tasks-done.md). Bug fixed: main quest dates now rebase off `campaign.start_date` (offset from `MATERIAL_ANCHOR_DATE=2026-06-04`); onboarding with any start date no longer produces expired main quest #1.

---

---

# Implementation Plan: Target / Suggest / Collocations Overhaul (2026-06-09, session 8l plan)

> 4 owner-reported issues. Grounded against live code: Onboarding.jsx, SetupSummaryPanel.jsx, services.py (`create_rank_suggestions_for_certificate`), VocabularyWorkspace.jsx + CollocationForge.jsx, models.py (`CollocationItem`, `PlayerCollocationProgress`).
>
> **Root-cause findings (debugging skill triage):**
> - **#1** Onboarding target is captured as 5 separate number inputs (overall + 4 skills) but only `overall` is sent (`target_band` single string); the 4-skill targets are discarded. Suggest-rank is driven **only** by certificate real scores (`/certificates/manual` → `create_rank_suggestions_for_certificate`), **not** by onboarding target — confirmed by grep (no target→suggest path). So #1 is: (a) make target a **dropdown** (4.0…9.0) for overall + 4 skills, (b) persist all 5, (c) explicitly ensure no suggest logic ever reads target.
> - **#2** `SetupSummaryPanel.jsx` hard-codes the Target card to `player.target` (single string "7.0–7.5") + a hard-coded prose line. No per-skill target shown. Needs an onboarding-style 5-row (overall + 4 skill) target panel reading persisted per-skill targets.
> - **#3** `services.py:create_rank_suggestions_for_certificate` (lines 1040–1045) still seeds an `inferred` dict with `Grammar` + `Collocation` mapped to `overall_score` → creates rank suggestions for 2 skills that were removed from the matrix (owner decision 2026-06-09, Task 18). Must drop both from suggestion generation. Same for `create_rank_suggestions_for_test` if it covers them.
> - **#4** "+ Forge Collocation" button (`VocabularyWorkspace.jsx:559`) POSTs `/vocabulary/{id}/collocations` — **route + model do not exist** → `{"detail":"Not Found"}`. **Owner decision: do NOT build per-word collocations.** Instead repurpose the existing master-data collocation system into a **"Collocations" browser** (topic list → cards from `CollocationItem`) plus a **collocation flashcard** system in its **own table `collocation_flashcards`** (separate from `flashcards`). Browse cards click → "Add to flashcard"; the Flashcard tab splits into **Vocabulary | Collocation**; reviewing a collocation flashcard (duel-style flip loop) sets a 4-level familiarity (again/hard/good/easy). A **neon border** (grey/green/blue/yellow) driven by `effective_familiarity` shows on **both** browse + flashcard cards; familiarity **decays one tier per 7 days** (`good→hard→again`), `easy` **graduates** (leaves flashcard, stays yellow in browse, never decays). Also fixes a found bug: the vocabulary flashcard only flips one-way. **Full owner-confirmed model + per-task detail: see the box at the start of Phase 4 below (grilled session 8l).**

## Architecture Decisions

- **Target is descriptive, never drives suggestions.** Per-skill target bands are stored on `Player` and shown/edited in UI only. Rank suggestions remain certificate-only. Rationale: owner intent — target is a goal, the certificate is evidence.
- **Per-skill target via 4 additive nullable `String(20)` columns on `players`** (`target_listening_band`, `target_reading_band`, `target_writing_band`, `target_speaking_band`), keeping existing `target_overall_band`. Stored as band strings ("6.5"), no numeric conversion. `target` legacy string retained for back-compat display fallback.
- **Onboarding drops the Certificate step; targets edited later via a dedicated `PATCH /api/player/targets`.** Certificate entry moves entirely to the dashboard `CertificateOverlay`. Rationale: cleanly separates goal (target) from evidence (certificate); a single-purpose PATCH avoids overloading `/api/setup`.
- **Reuse the existing collocation master-data stack for #4** — no per-word table. Card data comes from `CollocationItem` (collocation, pronunciation_us, meaning_vi, example_en, example_vi).
- **Collocation flashcards in a NEW dedicated table `collocation_flashcards`** (separate from `flashcards`/`spaced_repetition_state`), holding `familiarity` (`again|hard|good|easy`, default `again`) + `familiarity_set_at`. No ease_factor/interval SRS. **Decay** = `effective_familiarity` drops one tier per full 7-day window since `familiarity_set_at` (`good→hard→again`), floored `again`, computed lazily on read; **`easy` graduates** (excluded from flashcard lists, never decays). `PlayerCollocationProgress` is left untouched for the legacy practice quest. Rationale: owner decision — keep the two systems separate; simple linear decay matches the stated "drop one level after 7 days" exactly.
- **Collocation Forge is the one evidence-backed daily quest.** All quests are honor-system (`complete_quest_instance` sets `completed=True` with no proof). Per owner, reviewing **5 distinct collocations/day** is the proof that auto-`complete`s Collocation Forge (claim stays manual). Anti-farm: count is `DISTINCT collocation_item_id` per day, not raw review count. Rationale: owner wants real review to drive that quest without changing the global complete/claim contract.

## Dependency Graph

```
#3 (remove Grammar/Collocation from cert suggest)   ── independent, do first (smallest, highest-confidence bugfix)
#1 schema (4 target cols + onboarding dropdown + persist) ──┐
        │                                                    │
#2 (SetupSummaryPanel reads per-skill targets) ─────────────┘ (needs #1 persistence + columns)
#4 schema (familiarity cols) ── #4 backend (decay + endpoints) ── #4 frontend (Collocations tab + neon cards)
```

## Task List

> **Owner-confirmed decisions (grill session 8l) for Phases 1–3 — read before implementing:**
> - **Constant for dropdowns:** define one shared band list `BAND_OPTIONS = ["4.0","4.5","5.0","5.5","6.0","6.5","7.0","7.5","8.0","8.5","9.0"]` (strings). Used by onboarding target step + dashboard target panel.
> - **Target persistence type = `String(20)`** (matches existing `target_overall_band`). Dropdown value is the string itself; no numeric conversion anywhere.
> - **Default target value = `"6.5"`** for all 5 dropdowns when none is set.
> - **Onboarding loses the Certificate step entirely.** New 5-step order: Welcome → **Target** → Campaign → StartDate → Confirm. Certificate entry now lives only in the dashboard (`CertificateOverlay.jsx`, already exists). All certificate code is removed from `Onboarding.jsx`.
> - **Dashboard target panel is editable in place** via a new dedicated endpoint `PATCH /api/player/targets`, saved with an explicit **"Lưu mục tiêu"** button shown only when dirty.
> - **Issue #3 cleanup = stop-creating (code) + dismiss-existing (data migration).** The inbox endpoint has no matrix filter, so old pending Grammar/Collocation rows must be dismissed by a one-time data migration.

### Phase 1 — Issue #3: stop suggesting ranks for removed Grammar/Collocation skills

- [x] **Task I3-1: Drop Grammar + Collocation from certificate rank-suggestion generation + dismiss existing rows.** *(S, backend)*
  - **Description:** Two parts — stop creating + clean up existing.
    1. **Stop creating (code):** In `services.py:create_rank_suggestions_for_certificate`, delete the `"Grammar": cert.overall_score` and `"Collocation": cert.overall_score` entries from the `inferred` dict (currently services.py:1041–1045). After the edit `inferred = {"Vocabulary": cert.overall_score}` only, so `all_skills` (= `{**components, **inferred}`) resolves to exactly the 5 matrix skills (Listening, Reading, Writing, Speaking, Vocabulary).
    2. **Audit the test path (already clean — confirm only, no edit):** `create_rank_suggestions_for_test` (services.py:975) already iterates only `["Listening","Reading","Writing","Speaking"]`; `infer_rank_from_test_record` (services.py:903) is skill-name driven and never names Grammar/Collocation. Verify with grep; note in the PR that no change was needed.
    3. **Clean up existing rows (data migration):** `GET /api/rank-suggestions` (main.py:1241) returns ALL pending suggestions for the campaign with **no matrix-skill filter**, so pre-existing pending Grammar/Collocation `SkillRankSuggestion` rows would still surface in the inbox. Add an Alembic **data migration** `YYYYMMDD_NN_dismiss_grammar_collocation_suggestions.py`:
       - `upgrade()`: `op.execute("UPDATE skill_rank_suggestions SET status='dismissed', resolved_at=NOW() WHERE status='pending' AND skill_id IN (SELECT id FROM skills WHERE name IN ('Grammar','Collocation'))")`
       - `downgrade()`: safe no-op (cannot reliably un-dismiss) — add a comment saying so.
  - **Spec ref:** Task 18 owner decision (Grammar/Collocation = buff sources, not matrix tiles, no independent rank) + `player_level.md` §2.A. Grill 8l: stop-create + data-migration dismiss (chosen over endpoint filter).
  - **Acceptance criteria:**
    - [x] `inferred` in `create_rank_suggestions_for_certificate` contains only `Vocabulary`; posting a manual certificate generates suggestions for exactly the 5 matrix skills — none for Grammar or Collocation.
    - [x] `grep -n "Grammar\|Collocation"` shows no occurrence inside any `SkillRankSuggestion`-building function.
    - [x] Data migration `20260609_18` upgrade() dismisses all pending rows; downgrade() no-op documented; `alembic upgrade head` clean.
    - [x] Tests updated: expected count 7 → 5; `assertNotIn("Grammar")` + `assertNotIn("Collocation")`. Suite 61/1/0.
  - **Verification:** `pytest -k "certificate or suggestion"` → 5 suggestions pass; full suite 61/1/0.
  - **Dependencies:** None.
  - **Files:** `backend/app/services.py`, `backend/alembic/versions/20260609_18_*.py`, `backend/app/test_backend.py`.
  - **Gap check:** [x] No gaps — code change + data migration + test update all consistent. Implemented session 8m.

### Checkpoint I3 (after Task I3-1)
- [x] Certificate suggestions = 5 matrix skills only; Grammar/Collocation dismissed via migration `20260609_18`; suite 61/1/0.

### Phase 2 — Issue #1: target as dropdowns (overall + 4 skills), persisted, never drives suggest

- [x] **Task I1-1: Add 4 per-skill target columns to `players`.** *(S, migration)*
  - **Description:** Alembic migration `YYYYMMDD_NN_add_per_skill_target_bands.py` adding **nullable** `target_listening_band`, `target_reading_band`, `target_writing_band`, `target_speaking_band` (all `String(20)`) to `players`. Mirror the 4 columns on `models.py:Player` (next to the existing `target_overall_band` at models.py:125). `upgrade()` adds the 4 columns; `downgrade()` drops them. Keep `target_overall_band` + legacy `target` untouched.
  - **Spec ref:** repo rule "additive, low-risk schema evolution"; grill 8l (String(20), per-skill).
  - **Acceptance criteria:**
    - [x] Migration `20260609_19` clean; downgrade drops 4 columns.
    - [x] `Player` model exposes all 4 new target fields; DB columns confirmed via DESCRIBE.
  - **Verification:** `alembic current` → `20260609_19 (head)`; DESCRIBE players shows 4 new varchar(20) cols.
  - **Dependencies:** None.
  - **Files:** `backend/alembic/versions/20260609_19_*.py`, `backend/app/models.py`.
  - **Gap check:** [x] No gaps. Implemented session 8m.

- [x] **Task I1-2: Onboarding — remove Certificate step, add Target step before Campaign, persist all 5 bands.** *(M, frontend + backend)*
  - **Description:** Rework `Onboarding.jsx` to the new 5-step flow **Welcome → Target → Campaign → StartDate → Confirm**:
    - **Remove all certificate code** from `Onboarding.jsx`: the `StepCertificate` component, `handleSkipCert`, `handleUseCert`, `scores`/`hasCert`/`EMPTY_SCORES` state, the `postManualCertificate` import + call, and the certificate branch in `StepConfirm`. (Certificate entry stays available post-onboarding via the existing `CertificateOverlay.jsx`.)
    - **New `StepTarget` component** (rendered as step 2, before Campaign): 5 `<select>` dropdowns labelled Overall / Listening / Reading / Writing / Speaking, each with `BAND_OPTIONS` (4.0…9.0), default `"6.5"`. State: replace the old `campaignTargetBand` string with `targets = { overall, listening, reading, writing, speaking }` (all default `"6.5"`).
    - **Renumber steps** + `StepDots total={5}`: 1 Welcome, 2 Target, 3 Campaign, 4 StartDate, 5 Confirm. `StepConfirm` shows the 5 target bands (replacing the removed certificate/"Rank khởi đầu F" block) + name + campaign + start date.
    - **Wire persistence:** extend `activateCampaign(...)` (`api/auth.js`) to send the 5 target bands; extend `OnboardingActivateIn` (`schemas.py`) with `target_overall_band` + 4 skill bands (optional strings); in `activate-campaign` (main.py:698-701) persist all 5 onto the `Player` columns (overall keeps setting legacy `player.target = f"IELTS Academic {overall}"`).
    - **Do NOT call any suggestion code** from the target path — `activate-campaign` already only suggests from linked certificates, which no longer exist at onboarding.
  - **Spec ref:** Owner issue #1 + grill 8l (drop certificate step; Target before Campaign; dropdowns 4.0–9.0 default 6.5; target never suggests).
  - **Acceptance criteria:**
    - [x] Onboarding: 5 steps Welcome→Target→Campaign→StartDate→Confirm; StepCertificate + all cert code removed.
    - [x] StepTarget: 5 `<select>` dropdowns, BAND_OPTIONS 4.0–9.0, default 6.5.
    - [x] `activateCampaign` extended to send `targets` object; `OnboardingActivateIn` + `activate-campaign` route persist all 5 bands.
    - [x] `StepConfirm` shows 5 target bands, no hasCert/scores branch. Build ✓.
  - **Verification:** `npm run build` ✓ 222 modules 0 errors.
  - **Dependencies:** Task I1-1.
  - **Files:** `frontend/src/pages/Onboarding.jsx`, `frontend/src/api/auth.js`, `backend/app/schemas.py`, `backend/app/main.py`.
  - **Gap check:** [x] No gaps. Implemented session 8m.

- [x] **Task I1-3: Expose per-skill targets on the profile contract + `PATCH /api/player/targets` update endpoint.** *(M, backend)*
  - **Description:**
    - **Read:** add the 4 new target fields to `PlayerProfileOut` (schemas.py:44-47 area) so `GET /api/auth/me` (and any `/summary` player block the dashboard target panel reads) returns `target_overall_band` + 4 skill bands. Additive optional fields — no consumer breaks.
    - **Update:** new endpoint `PATCH /api/player/targets` with body schema `PlayerTargetsIn { target_overall_band, target_listening_band, target_reading_band, target_writing_band, target_speaking_band }` (all optional `str`). It updates only the provided target columns on the current player (also refresh legacy `player.target` from overall when overall provided), commits, returns `PlayerProfileOut`. Does **not** touch any other field and **never** calls suggestion code. Add a thin `api/auth.js` (or appropriate client) helper `updatePlayerTargets(targets)`.
  - **Spec ref:** "Keep API responses additive"; grill 8l (editable dashboard panel via dedicated PATCH endpoint).
  - **Acceptance criteria:**
    - [x] `PlayerProfileOut` + `PlayerMeOut` expose 4 new optional target fields.
    - [x] `PATCH /api/player/targets` (with `PlayerTargetsIn`) persists partial/full updates, returns `PlayerProfileOut`, creates 0 suggestions. `test_patch_player_targets` PASS.
    - [x] `updatePlayerTargets(targets)` helper added to `api/auth.js`.
  - **Verification:** `pytest -k "target"` → test_patch_player_targets PASS; suite 61/1/0.
  - **Dependencies:** Task I1-1.
  - **Files:** `backend/app/schemas.py`, `backend/app/main.py`, `frontend/src/api/auth.js`, `backend/app/test_backend.py`.
  - **Gap check:** [x] No gaps. Implemented session 8m.

### Checkpoint I1 (after Tasks I1-1…I1-3)
- [x] Onboarding (no certificate step) persists 5 target bands via dropdowns; profile exposes them; PATCH updates them; suggestions never from targets. Suite 61/1/0.

### Phase 3 — Issue #2: editable per-skill target panel on the dashboard

- [x] **Task I2-1: Replace SetupSummaryPanel hard-coded target with an editable per-skill target panel.** *(M, frontend)*
  - **Description:** In `SetupSummaryPanel.jsx` replace the single hard-coded Target card (currently `<strong>{player.target}</strong>` + the prose "Current level is around B1, with Listening stronger than Reading.", SetupSummaryPanel.jsx:8-12) with an **editable** target section:
    - 5 dropdowns (Overall / Listening / Reading / Writing / Speaking), options `BAND_OPTIONS`, pre-filled from the profile target fields (Task I1-3); when a skill band is null, fall back to `target_overall_band`, then legacy `target`, then `"6.5"`.
    - Visual style mirrors the onboarding `StepTarget` (same labels + layout) so dashboard ≈ onboarding.
    - Track dirty state; show a **"Lưu mục tiêu"** button only when a value changed. On click call `updatePlayerTargets(...)` (`PATCH /api/player/targets`), then refresh the profile + show a brief "Đã lưu" confirmation; handle error with an inline message.
    - Remove the stale hard-coded prose line.
    - The panel needs the profile target data: ensure the component receives it (extend the `player` prop passed by `App.jsx`/`dashboard-data.js` snapshot to include the 5 bands, or fetch profile here — prefer passing via the existing snapshot to avoid an extra fetch).
  - **Spec ref:** Owner issue #2 + grill 8l (editable in place, "Lưu mục tiêu" button, dirty-only, onboarding-style).
  - **Acceptance criteria:**
    - [x] `TargetEditor` component in StatusModal: 5 dropdowns, BAND_OPTIONS, pre-filled from `player.targetOverall/Listening/Reading/Writing/Speaking`; null fallback to overall→legacy→6.5; no hard-code.
    - [x] Dirty state → "Lưu mục tiêu" button appears; save calls `updatePlayerTargets` + `onProfileRefresh`; shows "Đã lưu".
    - [x] `buildPlayerSnapshot` in dashboard-data.js passes `targetOverall/Listening/Reading/Writing/Speaking`; App.jsx passes `onProfileRefresh` to StatusModal.
    - [x] Build ✓ 222 modules. CSS `.target-editor`/`.target-save-btn`/`.target-save-msg` added.
  - **Note:** Implemented as `TargetEditor` AuxSection inside StatusModal (the live render surface), not inside the unmounted `SetupSummaryPanel`. Functional requirement fully met.
  - **Verification:** `npm run build` ✓; browser smoke pending (requires running stack).
  - **Dependencies:** Task I1-3.
  - **Files:** `frontend/src/components/StatusModal.jsx`, `frontend/src/styles.css`, `frontend/src/dashboard-data.js`, `frontend/src/App.jsx`.
  - **Gap check:** [x] No gaps — `SetupSummaryPanel` was dead (not mounted); `TargetEditor` placed on live surface. Implemented session 8m.

- [x] **Task I2-2: Order daily quest cards by claim status (claim-ready top, claimed bottom).** *(S, frontend)*
  - **Description:** In `DailyQuestPanel.jsx` the quest stack currently renders `enrichedQuests` in raw array order (DailyQuestPanel.jsx:196-203) with no sort. Add a stable sort before rendering so cards are grouped by claim status:
    - **Group 0 (top): claim-ready** = `quest.completed && !quest.rewardClaimed` (the existing `isClaimReady` condition, DailyQuestPanel.jsx:76).
    - **Group 1 (middle): not yet completed** = `!quest.completed`.
    - **Group 2 (bottom): claimed** = `quest.completed && quest.rewardClaimed`.
    Within each group preserve the original relative order (stable sort — assign a rank 0/1/2 and `Array.prototype.sort` by rank only, or use a stable partition). Apply the sort to **both** the unfiltered list and the skill-filtered list (sort after filtering). Do not change card markup or any other behavior — display order only.
    - **Note:** `rewardClaimed` is the field the component already reads (DailyQuestPanel.jsx:76, 156); confirm its source in `dashboard-data.js` quest mapping and use the same field name (do not introduce `reward_claimed` vs `rewardClaimed` drift).
  - **Spec ref:** Owner request (session 8l) — claim-ready quests float to the top, claimed quests sink to the bottom.
  - **Acceptance criteria:**
    - [x] `claimGroup(quest)` returns 0/1/2; `sortByClaimStatus(list)` stable-sorts via `[...list].sort((a,b) => claimGroup(a)-claimGroup(b))`.
    - [x] Applied after filter in both unfiltered and skill-filtered render paths.
    - [x] No change to card markup, buttons, or counts.
  - **Verification:** `npm run build` ✓ 222 modules 0 errors.
  - **Dependencies:** None.
  - **Files:** `frontend/src/components/DailyQuestPanel.jsx`.
  - **Gap check:** [x] No gaps. Implemented session 8m.

### Checkpoint I2 (after Tasks I2-1, I2-2)
- [x] Target editor in StatusModal (live surface) with 5 dropdowns + "Lưu mục tiêu"; daily quest cards sorted claim-ready → not-done → claimed. Build ✓.

### Phase 4 — Issue #4: "Collocations" browser + collocation flashcards (neon familiarity + 7-day decay)

> **Owner-confirmed model (grill session 8l) — read before implementing any I4 task:**
> - The "Collocation Forge" tab becomes **"Collocations"** = a *browser*: topic list → click topic → **cards** (one per `CollocationItem`). Card layout (hide a row when its field is null): **the full collocation phrase `collocation` as the largest text** → `pronunciation_us` directly beneath it → `meaning_vi` → `example_en` → `example_vi` beneath the English example. `collocation_type` shown as a small tag.
> - **Familiarity is NOT set on the browse card.** Clicking a browse card shows an **"Add to flashcard"** action. Familiarity (again/hard/good/easy) is produced **only by reviewing the collocation flashcard**, mirroring vocabulary flashcards.
> - **Collocation flashcards live in their OWN table `collocation_flashcards` (NOT the `flashcards` table).** No `ease_factor`/interval SRS. The row stores `familiarity` (default `'again'`) + `familiarity_set_at`.
> - **Decay:** `effective_familiarity` = stored `familiarity` dropped **one tier per full 7-day window** since `familiarity_set_at` (`good→hard→again`), floored at `again`. Pressing a review button re-sets the level + resets the 7-day anchor. **`easy` does NOT decay** — see graduation rule.
> - **`easy` = graduation:** pressing `easy` removes the card from the **Flashcard** tab immediately (no decay). It stays in the **Collocations browse** with a **yellow** neon border permanently (until the user re-adds it). So decay only ever applies to cards still in flashcard with familiarity ∈ {again, hard, good}.
> - **Neon border (applies on BOTH the browse cards AND the flashcard cards), driven by the same `effective_familiarity`:** `again` → grey, no glow ("locked"); `hard` → faint light-green neon, very low glow; `good` → soft blue neon; `easy` → yellow neon, strong glow.
> - **Browse card states:** not-yet-added (no `collocation_flashcards` row) → grey border **+ "Add to flashcard" button**. Added-but-`again` (just added, or decayed back) → grey border **+ "✓ Đã thêm" badge** (and a remove control). The grey border is identical for both; the **badge** is what distinguishes "not added" from "added & again".
> - **Flashcard tab is split into two sub-tabs: `Vocabulary` | `Collocation`.** The `Collocation` sub-tab lists **only topics that contain at least one added collocation flashcard**; click a topic → **review loop** over all added cards in that topic (graduated `easy` cards excluded). The loop is the same duel-style flip UI as vocabulary (flip to reveal → 4 buttons again/hard/good/easy).

- [ ] **Task I4-1: New `collocation_flashcards` table (own SRS-less familiarity store).** *(S, migration)*
  - **Description:** Alembic migration `YYYYMMDD_NN_add_collocation_flashcards.py` creating `collocation_flashcards`: `id`, `player_id` (FK players), `campaign_id` (FK campaigns), `collocation_item_id` (FK collocation_items), `familiarity` (`String(10)`, default `'again'`, not null), `familiarity_set_at` (`DateTime`, nullable), `created_at`. `UniqueConstraint(player_id, campaign_id, collocation_item_id)`. Add the model + relationships in `models.py`. `upgrade()`+`downgrade()`. Do **not** touch `flashcards`/`spaced_repetition_state` (owner: separate table, separate logic). Leave the existing `PlayerCollocationProgress` for the legacy practice quest untouched.
  - **Spec ref:** Owner grill (B) — collocation flashcards in their own table; (A) — familiarity + 7-day decay, no ease_factor.
  - **Acceptance criteria:**
    - [ ] Migration clean on empty + populated DB; `downgrade()` drops the table cleanly.
    - [ ] `CollocationFlashcard` model + relationships import without error; unique constraint enforced.
  - **Verification:** upgrade/downgrade on seeded DB; backend imports.
  - **Dependencies:** None.
  - **Files:** `backend/alembic/versions/*.py`, `backend/app/models.py`.
  - **Gap check:** [ ]

- [ ] **Task I4-2: Backend — add/remove flashcard, set-familiarity (review), 7-day decay, browse + flashcard read endpoints.** *(L → may split, backend)*
  - **Description:** Implement in `services.py` + routes in `main.py` + schemas:
    - `effective_familiarity(stored_level, familiarity_set_at, now) -> str` pure helper: from stored level, drop one tier per full 7-day window (`good→hard→again`), floored `again`. `easy` rows are graduated and excluded from flashcard reads (do not decay them).
    - **Add/remove flashcard:** `POST /api/collocations/{item_id}/flashcard` (get-or-create row, familiarity defaults `again`, set anchor) → idempotent; **if the row exists and is graduated (`easy`), re-adding RESETS it to `again` + new anchor** (owner decision, grill 8l). `DELETE /api/collocations/{item_id}/flashcard` (remove). Scope to current campaign.
    - **Review (set familiarity):** `POST /api/collocations/{item_id}/flashcard/review` body `{ "result": "again|hard|good|easy" }` → set `familiarity=result` + `familiarity_set_at=utcnow()`. If `result=="easy"` the card is **graduated** (still a row, but excluded from flashcard lists). Invalid result → 422.
    - **Browse read:** `GET /api/collocations/topics` (topics in the campaign's linked collections) + `GET /api/collocations/topics/{topic_id}/items` → each item's `CollocationItem` fields + `effective_familiarity` (grey/again if no row) + `is_added` (has row) flag. Scope via `CampaignCollocationLink`.
    - **Flashcard read:** `GET /api/collocations/flashcard/topics` → only topics that have ≥1 **non-graduated** added card; `GET /api/collocations/flashcard/topics/{topic_id}` → the non-graduated added cards in that topic with `effective_familiarity`, for the review loop.
  - **Spec ref:** Owner grill: add-to-flashcard (not set on browse), own table, decay 1 tier/7 days, easy graduates + leaves flashcard, browse+flashcard reads, neon driven by `effective_familiarity`.
  - **Acceptance criteria:**
    - [ ] `effective_familiarity`: good@0d→good; good@8d→hard; good@15d→again; hard@8d→again; again stays again; easy is reported as easy (graduated, not decayed).
    - [ ] `POST .../flashcard` is idempotent (2nd call no duplicate, unique constraint holds); `DELETE` removes it.
    - [ ] `review` with `easy` → card excluded from `GET .../flashcard/topics/{id}` thereafter but still present (yellow) in browse read.
    - [ ] Flashcard topic list excludes topics whose only cards are graduated.
    - [ ] Browse items carry `is_added` + `effective_familiarity`.
    - [ ] The `review` endpoint, after writing the row, **triggers the daily-quest auto-complete check (Task I4-7)** within the same request (so completing the 5th distinct review of the day marks the Collocation Forge quest completed in that response).
  - **Verification:** unit-test the decay table + graduation; smoke add→review good→read shows good→backdate 8d→read shows hard; review easy→gone from flashcard, yellow in browse.
  - **Dependencies:** Task I4-1.
  - **Files:** `backend/app/services.py`, `backend/app/schemas.py`, `backend/app/main.py`, `backend/app/test_backend.py`.
  - **Gap check:** [ ]

- [ ] **Task I4-3: Frontend — rename tab to "Collocations"; topic list → topic → neon browse cards + Add-to-flashcard.** *(M, frontend)*
  - **Description:** Repurpose `CollocationForge.jsx` + its `VocabularyWorkspace.jsx` tab label/icon into **"Collocations"** (browse): (1) topic list from `GET /api/collocations/topics`; (2) click topic → cards from `GET /api/collocations/topics/{id}/items`; (3) card layout (hide null rows): **`collocation` largest** → `pronunciation_us` under it → `meaning_vi` → `example_en` → `example_vi` under EN; `collocation_type` small tag; (4) **neon border by `effective_familiarity`**: again→grey no-glow, hard→faint light-green, good→soft blue, easy→strong yellow; (5) click a card → **"Add to flashcard"**; if already added show **"✓ Đã thêm"** badge + a remove control (`DELETE .../flashcard`). Remove the old quiz/forge MCQ flow + dead `practice/collocations` consumption.
  - **Spec ref:** Owner grill: browse card layout, full-phrase largest, hide-null, neon on browse cards, add-to-flashcard + "✓ Đã thêm" + remove.
  - **Acceptance criteria:**
    - [ ] Sidebar tab reads "Collocations"; opening shows a topic list; selecting a topic renders cards in the specified field order with null rows hidden.
    - [ ] Border reflects `effective_familiarity` (grey/green/blue/yellow); not-added card shows "Add to flashcard"; added card shows "✓ Đã thêm" + remove.
    - [ ] Old MCQ forge flow removed; no dead `practice/collocations` call remains.
  - **Verification:** `npm run build` ✓; browser smoke — pick topic, add a card → badge appears; reviewed-good card shows blue border in browse.
  - **Dependencies:** Task I4-2.
  - **Files:** `frontend/src/components/CollocationForge.jsx` (rename/refactor), `frontend/src/components/VocabularyWorkspace.jsx`, `frontend/src/styles.css`.
  - **Gap check:** [ ]

- [ ] **Task I4-4: Frontend — Flashcard tab split (Vocabulary | Collocation) + collocation review loop.** *(M, frontend)*
  - **Description:** In `VocabularyWorkspace.jsx` Flashcard tab, add a sub-tab switch **Vocabulary | Collocation**. Vocabulary keeps the current due-card loop. Collocation sub-tab: list topics from `GET /api/collocations/flashcard/topics` (only topics with ≥1 non-graduated added card); click topic → **review loop** over `GET /api/collocations/flashcard/topics/{id}` using the same duel flip UI; flip reveals the meaning/examples; 4 buttons again/hard/good/easy → `POST .../flashcard/review`; the active card's border uses `effective_familiarity`. After review the loop advances; `easy` graduates the card (drops from the list). Loop covers **all** non-graduated cards in the topic.
  - **Spec ref:** Owner grill: Flashcard split Vocab|Colloc; Colloc topics = only those with added cards; review loop (flip) reusing vocab duel UI; easy graduates.
  - **Acceptance criteria:**
    - [ ] Flashcard tab shows Vocabulary | Collocation sub-tabs; Collocation lists only topics with added (non-graduated) cards.
    - [ ] Selecting a collocation topic runs a flip review loop with 4 result buttons writing via the review endpoint; pressing `easy` removes the card from the loop.
    - [ ] Active card border matches `effective_familiarity`.
  - **Verification:** `npm run build` ✓; browser smoke — add 2 cards in a topic → Collocation sub-tab lists that topic → review loop runs → easy graduates one.
  - **Dependencies:** Task I4-2, Task I4-3, Task I4-6 (shared flip component).
  - **Files:** `frontend/src/components/VocabularyWorkspace.jsx`, `frontend/src/styles.css`.
  - **Gap check:** [ ]

- [ ] **Task I4-5: Remove the dead per-word "+ Forge Collocation" button + add-collocation handlers.** *(S, frontend)*
  - **Description:** In `VocabularyWorkspace.jsx` remove the Codex-card "+ Forge Collocation" UI (lines ~525–561), `handleAddCollocation`, `handleDeleteCollocation`, and the `item.collocations` rendering block that always renders empty (no backend support; owner decided not to build per-word collocations). Also remove the dead `collocations[0]` block on the vocabulary flashcard back (VocabularyWorkspace.jsx ~712–730) which reads `vocabulary_item.collocations` that the backend never populates. Keep the Examples section (its routes exist). Confirm nothing else references the removed handlers.
  - **Spec ref:** Owner decision (#4) — per-word collocations not built; the 404 source is removed rather than backed.
  - **Acceptance criteria:**
    - [ ] No "+ Forge Collocation" button or per-word collocation add/delete UI remains in the Codex card.
    - [ ] No FE call to `POST /vocabulary/{id}/collocations` or `DELETE /vocabulary/collocations/{id}` remains (404 path gone).
    - [ ] Dead `vocabulary_item.collocations` flashcard-back block removed; Examples add/delete still works.
  - **Verification:** grep FE for `/collocations` POST/DELETE on the vocabulary path → 0 hits; `npm run build` ✓.
  - **Dependencies:** None.
  - **Files:** `frontend/src/components/VocabularyWorkspace.jsx`.
  - **Gap check:** [ ]

- [ ] **Task I4-6: Fix vocabulary flashcard flip to be two-way (Definition ↔ Recall).** *(S, frontend)*
  - **Description:** The vocabulary flashcard currently flips one-way only: the front has "Reveal Definition" (`setShowAnswer(true)`) but the back has **no** control to flip back to the "Recall Meaning" front (VocabularyWorkspace.jsx ~636–736; `showAnswer` never set back to false except on next card). Add a flip-back affordance on the card back (e.g. a "Recall Meaning" button or making the card click toggle `showAnswer`). Apply the same two-way flip to the new collocation review loop (Task I4-4) so both behave identically.
  - **Spec ref:** Owner grill — "flashcard hiện 1 chiều, không có nút quay lại Recall Meaning; thêm tính năng này".
  - **Acceptance criteria:**
    - [ ] Vocabulary flashcard back has a control that flips back to the Recall (front) face; toggling works repeatedly within one card.
    - [ ] The collocation review loop uses the same two-way flip behavior.
    - [ ] Difficulty buttons still submit review correctly after flipping back and forth.
  - **Verification:** `npm run build` ✓; browser smoke — flip to Definition, flip back to Recall, flip again, then rate.
  - **Dependencies:** None (shared component consumed by Task I4-4).
  - **Files:** `frontend/src/components/VocabularyWorkspace.jsx`.
  - **Gap check:** [ ]

- [ ] **Task I4-7: Auto-complete the "Collocation Forge" daily quest when 5 distinct collocations are reviewed in a day.** *(M, backend)*
  - **Description:** Owner decision (grill 8l): unlike every other quest (which is honor-system — `complete_quest_instance` just sets `completed=True` with no proof), the **Collocation Forge** daily quest becomes the first **evidence-backed** quest: reviewing collocation flashcards is its proof of work. The seeded quest is title `"Collocation Forge"`, skill `Collocation`, slot `vocab_collocation`, `base_xp=5`, description "Practice 5 collocations in sentences and submit 3 valid personal examples." (seed.py:494-507).
    - Add `try_autocomplete_collocation_forge(db, player_id, campaign_id, today)` in `services.py`, called at the **end of the review write** (Task I4-2 `POST /api/collocations/{item_id}/flashcard/review`, after `familiarity_set_at` is updated and flushed).
    - **Count rule (owner = distinct/day, anti-farm):** `distinct = COUNT(DISTINCT collocation_item_id) FROM collocation_flashcards WHERE player_id=? AND campaign_id=? AND DATE(familiarity_set_at)=today`. Reviewing the same card twice in a day counts once.
    - If `distinct >= 5`: find today's Daily Quest with title `"Collocation Forge"` (or slot `vocab_collocation`) for this campaign (`session_type="Daily Quest"`, `quest_date==today`); if found and not yet completed, call `complete_quest_instance(db, quest)` (idempotent). **Only auto-`complete`, NOT auto-`claim`** — the user still presses Claim on the dashboard to receive +5 Vocabulary XP, identical to every other quest.
    - **Edge cases (all no-op, no error):** (1) quest already completed (manually or earlier today) → `complete_quest_instance` is idempotent, do nothing; (2) no Collocation Forge quest generated for today → skip silently; (3) further reviews after reaching 5 → quest already completed, no-op.
  - **Spec ref:** Owner grill 8l — review 5 distinct collocations (any topic) in a day auto-completes the Collocation Forge daily quest; complete-only (claim stays manual); distinct-per-day count to prevent farming.
  - **Acceptance criteria:**
    - [ ] Reviewing 5 distinct collocations in one day marks today's "Collocation Forge" daily quest `completed=True`, `reward_claimed=False` (claim-ready).
    - [ ] Reviewing the same card 5 times does NOT complete it (distinct count = 1).
    - [ ] After auto-complete, the user can Claim → +5 Vocabulary XP (existing claim flow, unchanged).
    - [ ] All 3 edge cases are no-ops (no exception): already-completed, no-quest-today, extra-reviews.
  - **Verification:** test: review 5 distinct → quest completed (not claimed); review 1 card 5× → not completed; claim after → Vocabulary +5; run with no quest present → no error.
  - **Dependencies:** Task I4-1, Task I4-2.
  - **Files:** `backend/app/services.py`, `backend/app/main.py`, `backend/app/test_backend.py`.
  - **Gap check:** [ ]

### Checkpoint I4 (after Tasks I4-1…I4-7)
- [ ] "Collocations" tab browses topics → neon cards (full-phrase largest, null rows hidden) with Add-to-flashcard; Flashcard tab split Vocabulary|Collocation; collocation review loop sets familiarity in `collocation_flashcards`; familiarity decays one tier per 7 days (`easy` graduates + leaves flashcard, stays yellow in browse); neon border identical on browse + flashcard; vocab flashcard flips two-way; reviewing 5 distinct collocations/day auto-completes the Collocation Forge daily quest (claim stays manual, +5 Vocabulary XP); dead per-word "+ Forge Collocation" 404 path removed; build + suite green.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Per-skill target columns unused by older summary consumers | Low | Additive nullable cols; FE reads with fallback to overall/legacy `target`. |
| Removing Grammar/Collocation suggestions breaks existing tests asserting count 7 | Med | Task I3-1 updates `test_manual_certificate_creation_*` to expect 5. |
| Decay computed on read drifts if also persisted | Med | Single source: `effective_familiarity(stored, set_at, now)` pure fn; reads compute on the fly. If persisting back, write only when the decayed tier changes. |
| Neon border CSS clarity across 4 levels | Low | Distinct hue + glow intensity per level; grey = no glow for "locked". Same component on browse + flashcard. |
| Old Forge MCQ flow / `practice/collocations` left half-wired | Med | Task I4-3 removes the quiz flow; grep for dead consumers. |
| `easy` graduation vs decay edge cases (does easy decay? re-add after graduate?) | Med | Owner-decided: `easy` never decays + leaves flashcard but stays yellow in browse; re-adding resets to `again`. Locked by I4-2 acceptance tests. |
| Two new tables/relations on `players`+collocation create migration ordering churn | Low | Both additive; independent migrations (I1-1, I4-1); no cross-FK between them. |

## Open Questions (for owner)

> **None remaining — all decided in grill session 8l.**

> **Resolved in grill session 8l:**
> - **#1:** target type `String(20)`, default `6.5`; onboarding drops the certificate step (Welcome→Target→Campaign→StartDate→Confirm).
> - **#2:** dashboard target panel editable via `PATCH /api/player/targets` + "Lưu mục tiêu" button (dirty-only).
> - **#3:** cleanup = stop-create (remove from `inferred`) + one-time data-migration dismiss of existing pending Grammar/Collocation suggestions.
> - **#4 decay:** **lazy-on-read** (no scheduler) — `effective_familiarity` computed at read time; always correct when viewed.
> - **#4 re-add:** re-adding a graduated (`easy`) card resets familiarity to `again`.
> - **#4 XP / quest link:** reviewing collocation flashcards is **not** direct XP. Instead, reviewing **5 distinct collocations in a day** auto-`complete`s the "Collocation Forge" daily quest (Task I4-7); the user still Claims for +5 Vocabulary XP. (This makes Collocation Forge the only evidence-backed quest; all others stay honor-system.)
> - **#4 card/flashcard UX:** own table `collocation_flashcards`, add-to-flashcard, neon decay 1 tier/7d, easy-graduates, 2-way flip.

---

## Where To Read More

- Completed Tasks: [tasks-done.md](tasks-done.md)
- Migration summary: [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)
- Latest validation: [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md)
- Latest implementation log: [docs/history/changelogs.md](docs/history/changelogs.md)
- Generic Codex guide (EN): [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md)
- Generic Codex guide (VI): [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md)
- Codex operator guide (EN): [docs/current/prompt-en.md](docs/current/prompt-en.md)
- Codex operator guide (VI): [docs/current/prompt-vi.md](docs/current/prompt-vi.md)
