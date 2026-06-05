# IELTS Quest Dashboard Tasks

## Session Resume State

Last updated: 2026-06-04

## Current Project State

- The frontend home dashboard redesign is complete, reviewer-accepted, and frontend-only.
- No API contract changes, no database/schema changes, and no Docker Compose changes were required for this redesign.
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
- Validation recorded for the completed redesign:
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
- Wired the certificate overlay to the existing test-records API.
- Added a boss overlay that surfaces the current boss first.
- Kept the avatar picker as placeholder-only UI.
- Kept the redesign aligned with the existing backend and data model.

## In Progress

- Browser visual walkthrough / screenshot verification remains pending.

## Known Issues / Risks

- Browser automation is unavailable in this environment, so visual confirmation is still missing.
- The redesign depends on existing suggestion and test-record APIs, so future backend changes could affect those overlays even though no contracts changed in this task.
- Worktree is dirty and contains unrelated frontend/backend/generated changes from prior work; do not revert user changes.

## Next Candidate Tasks

1. Capture a browser visual review of the home dashboard.
   - Confirm spacing, overlay density, and mobile/laptop responsiveness.

2. Tighten any UI polish found in visual review.
   - Adjust density, hierarchy, or hover/focus states only if needed.

3. Expand documentation for the new dashboard surfaces if needed.
   - Add more product detail only if the team wants a fuller spec.

## Delegation Rule For Next Coding Work

- Do not code directly without user confirmation.
- Assign one small task at a time to `coder-gpt54`.
- After `coder-gpt54` finishes, ask `reviewer-gpt55` to review the diff.
- If `reviewer-gpt55` reports P0/P1 issues, send a focused fix task back to `coder-gpt54`.
- Repeat review after the fix before moving to the next task.
