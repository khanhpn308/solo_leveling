# Implementation Plan: Main Quest must start from the user-chosen onboarding date

## Context

**Bug (serious):** Main quests are hard-anchored to **2026-06-04**. When a user picks any other start date in onboarding, the main-quest dates stay on the material.md absolute dates, so the first main quests render as **expired** (their `quest_date` is in the past relative to the chosen start).

**Root cause:** `material/material.md` stores **absolute** session dates (Week 1 Session 1 = `2026-06-04`, a Thursday; 4 sessions/week on Thu/Sat/Mon/Wed). `parse_material_plan()` (`seed.py:617`) reads them as-is into `StudyPlanSession.study_date` (`seed.py:1164`), and main quests copy that verbatim: `Quest.quest_date = session.study_date` (`seed.py:1494`).

Meanwhile **daily quests are correct** — `ensure_quest_instances()` computes every date relatively: `week_start = campaign.start_date + timedelta(days=(week_no-1)*7)` (`seed.py:1354`). `RoadmapPhase` dates are already rebased the same way (`seed.py:1045-1046`). Only the study-plan weeks/sessions (and therefore main quests) ignore `campaign.start_date`.

**Goal:** Rebase study-plan week + session dates off `campaign.start_date`, preserving the material plan's inter-session spacing (offset from the material anchor), and recompute the weekday label from the rebased date. Main quests then inherit the correct dates automatically.

**Owner decisions (confirmed):**
- **Weekday label:** recompute from the rebased `study_date` (so labels always match the real weekday).
- **Existing data:** only fix new campaigns; clean old ones via `/api/dev/reset`. No backfill migration.

## Architecture Decisions

- **Offset-rebasing, anchored to a single constant.** Introduce `MATERIAL_ANCHOR_DATE = date(2026, 6, 4)` (= Week 1 Session 1 in material.md). For every parsed week/session date `d`, store `campaign.start_date + (d - MATERIAL_ANCHOR_DATE)`. This preserves the exact cadence (Thu→Sat→Mon→Wed = +0/+2/+4/+6, weeks 7 days apart) while sliding the whole plan to the user's start. Mirrors the existing daily-quest / roadmap-phase rebasing approach.
- **Rebase at the `ensure_study_plan` layer, not in `parse_material_plan`.** `parse_material_plan()` is a pure parser with no `campaign` context; keep it returning raw material dates. Do the rebasing where `campaign.start_date` is in scope (`ensure_study_plan`), so the parser stays reusable/testable and the offset origin is explicit.
- **Recompute `weekday_label` from the rebased date** (`rebased.strftime("%A")`), overriding the material text. Single write point in `ensure_study_plan`.
- **Main quests need zero changes** — they read `session.study_date`, which is now correct.
- **Idempotency caveat:** the existing-row update branches in `ensure_study_plan` / `ensure_main_quest_instances` currently do **not** refresh dates on re-run. Since the fix targets fresh campaigns (reset-based), the create branch is what matters; we additionally make the update branch rewrite `study_date`/`week_start`/`week_end`/`weekday_label` so a re-seed self-heals (defensive, low-risk).

## Dependency Graph

```
MATERIAL_ANCHOR_DATE constant + rebase helper   (Task 1)
        │
ensure_study_plan rebases week + session dates   (Task 2)   ← main quests inherit via study_date
        │
Default-start-date cleanup (parse_start_date)    (Task 3, independent hardening)
        │
Verification: reset + onboard with a non-anchor date  (Checkpoint)
```

## Task List

### Phase 1: Rebase the study plan

#### Task 1: Add material-anchor constant + date-rebase helper
**Description:** In `seed.py`, add `MATERIAL_ANCHOR_DATE = date(2026, 6, 4)` near the other module constants and a tiny helper `rebase_material_date(material_date, campaign_start) -> date` returning `campaign_start + (material_date - MATERIAL_ANCHOR_DATE)`. Pure function, no DB.

**Acceptance criteria:**
- [ ] `MATERIAL_ANCHOR_DATE` defined once; equals the Week1/Session1 date in material.md.
- [ ] `rebase_material_date(date(2026,6,4), date(2026,6,4)) == date(2026,6,4)` (identity when start == anchor).
- [ ] `rebase_material_date(date(2026,6,6), date(2026,7,15)) == date(2026,7,17)` (preserves +2 offset).

**Verification:** import seed; call helper with the two cases above.

**Dependencies:** None.

**Files likely touched:** `backend/app/seed.py`.

**Estimated scope:** XS (1 file).

#### Task 2: Rebase week + session dates (and weekday label) in `ensure_study_plan`
**Description:** In `ensure_study_plan()` (`seed.py:1111`), wrap every material date in `rebase_material_date(..., campaign.start_date)`:
- Week create branch (`seed.py:1131-1132`): `week_start` / `week_end`.
- Session create branch (`seed.py:1164`): `study_date`; and set `weekday_label = rebased_study_date.strftime("%A")` instead of `row["weekday_label"]`.
- Also update the **existing-row update branches** (week + session) to rewrite these fields so a re-seed self-heals.

Main quests (`ensure_main_quest_instances`) need no change — `quest_date=session.study_date` now carries the rebased value.

**Acceptance criteria:**
- [ ] For a campaign whose `start_date` ≠ 2026-06-04, the first `StudyPlanSession.study_date` equals `campaign.start_date` (Week1/Session1), not 2026-06-04.
- [ ] The first Main Quest's `quest_date` equals `campaign.start_date`; it is `pending`, not `expired`, when start_date ≥ today.
- [ ] Session inter-spacing preserved: sessions 1→2→3→4 land on `start, start+2, start+4, start+6`.
- [ ] `weekday_label` matches `study_date.strftime("%A")` (e.g. a Monday start ⇒ Session 1 label `Monday`).
- [ ] `StudyPlanWeek.week_start` of week N == `campaign.start_date + (N-1)*7` days, aligning with daily-quest `week_start`.

**Verification:**
- `POST /api/dev/reset` then onboard / `activate-campaign` with `start_date` = a near-future Monday.
- Query the main quest map (`/api/main-quests` or `/summary`): assert first session date == chosen start, status pending, weekday label correct.
- Cross-check a daily quest and a main quest for the same week share the same `week_start` window.

**Dependencies:** Task 1.

**Files likely touched:** `backend/app/seed.py`.

**Estimated scope:** S (1 file).

### Checkpoint: After Tasks 1–2
- [ ] Backend boots; `/api/dev/reset` succeeds.
- [ ] Onboarding with a non-anchor start date ⇒ main quest #1 on that exact date, status `pending`.
- [ ] Existing backend test suite still green (`60/1/0`), esp. main-quest XP/routing tests that depend on session ordering.

### Phase 2: Hardening (independent)

#### Task 3: Make the fallback start date "today", not the stale 2026-06-04
**Description:** `parse_start_date()` (`seed.py:2300`) defaults to `2026-06-04` via `APP_START_DATE`. With rebasing in place this only matters when `start_date` is omitted, but defaulting to a past hard date still produces expired quests for the demo/seed path. Change the fallback to `date.today()` (keep the `APP_START_DATE` env override for deterministic seeds). Confirm the deterministic startup seed (`seed_database`) still behaves (it may rely on a fixed date — if so, keep the env var set there and only change the *bare* fallback).

**Acceptance criteria:**
- [ ] With `APP_START_DATE` unset and no `start_date` passed, a new campaign starts today (no expired main quest #1).
- [ ] `APP_START_DATE` env override still respected for deterministic seeding.
- [ ] Startup `seed_database()` demo campaign still seeds without errors.

**Verification:** unset env; `activate_campaign_for_player(db, player)` with no start_date; assert campaign.start_date == today and first main quest pending.

**Dependencies:** Task 2 (so the date actually propagates).

**Files likely touched:** `backend/app/seed.py`.

**Estimated scope:** XS (1 file).

### Checkpoint: Complete
- [ ] All acceptance criteria met.
- [ ] Reset + onboard with: (a) today, (b) a future Monday, (c) omitted start date — all produce a pending main quest #1 on the right date with a correct weekday label.
- [ ] Daily and main quests for week 1 share the same calendar window.
- [ ] Backend suite green; build unaffected (no FE change required).

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing-row update branch in `ensure_study_plan` doesn't refresh dates → stale dates on re-seed of the same campaign | Med | Task 2 also rewrites dates in the update branch; dev path uses `/api/dev/reset` which deletes rows first. |
| Tests assume material weekday labels (Thu/Sat/Mon/Wed) | Low | Labels now derive from date; update any test asserting literal `"Thursday"` for a non-anchor start. Grep test_backend for weekday assertions. |
| `seed_database()` deterministic demo relies on fixed 2026-06-04 | Med | Keep `APP_START_DATE` for the demo seed if needed; only change the bare fallback (Task 3). Verify startup seed after the change. |
| Week range parsing (`week_start/week_end`) edge: material week_end is +6 from week_start | Low | Rebase both endpoints with the same helper; spacing preserved by construction. |
| Main quest map "current session" pointer logic keyed on dates | Low | Pointer logic is relative to today vs quest_date; rebasing makes it correct, not worse. Smoke-check the map after reset. |

## Open Questions
- None blocking. (Weekday-label and existing-data decisions already confirmed by owner: recompute label; fix new campaigns only.)
