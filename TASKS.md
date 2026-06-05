# IELTS Quest Dashboard Tasks

## Session Resume State

Last updated: 2026-06-05

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

## Delegation Rule For Next Coding Work

- Do not code directly without user confirmation.
- Assign one small task at a time to `coder-gpt54`.
- After `coder-gpt54` finishes, ask `reviewer-gpt55` to review the diff.
- If `reviewer-gpt55` reports P0/P1 issues, send a focused fix task back to `coder-gpt54`.
- Repeat review after the fix before moving to the next task.
