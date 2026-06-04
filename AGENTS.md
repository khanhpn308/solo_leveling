# Repository Guidelines

## Project name

IELTS Quest Dashboard

## Project purpose

This is a local gamified IELTS Academic self-study dashboard for an 18-month roadmap starting from 04/06/2026.

The user is a Vietnamese learner aiming for IELTS Academic 7.0-7.5 within 18 months. Current level is around B1, with Listening as the strongest skill and Reading weakness mainly caused by limited vocabulary and difficulty understanding long sentences.

## Tech stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: MySQL
- Deployment: Docker Compose
- Runs locally only

## Core design direction

The UI should feel like a game status dashboard inspired by Solo Leveling:

- Dark fantasy / system interface style
- Neon blue or cyan highlights
- Status panel
- Skill rank from F to S
- XP, levels, quests, badges, boss battles
- Strong gamification to reduce boredom and help maintain study streaks

Do not copy copyrighted UI assets or exact protected designs. Use an original interface inspired by the general idea of game-like status screens.

## Main skills to track

1. Listening
2. Reading
3. Writing
4. Speaking
5. Vocabulary
6. Collocation
7. Grammar

Each skill must have:

- XP
- Level
- Rank: F, E, D, C, B, A, S
- Progress bar
- Last practiced date
- Weakness note

## XP system

XP is calculated by completed tasks, not by study time.

Example XP values:

- Learn 10 new words: +10 XP
- Review old vocabulary: +5 XP
- Complete one Listening task: +20 XP
- Review transcript: +15 XP
- Shadowing 5 sentences: +10 XP
- Complete one Reading passage: +25 XP
- Analyze 5 long sentences: +15 XP
- Write one paragraph: +25 XP
- Write one full Writing Task 2: +50 XP
- Record Speaking Part 1: +15 XP
- Record Speaking Part 2: +25 XP
- Full Listening test: +60 XP
- Full Reading test: +60 XP
- Add corrected mistake to Error Log: +10 XP

## Study roadmap phases

The roadmap starts on 04/06/2026 and is divided into:

1. Month 1-3
2. Month 4-6
3. Month 7-9
4. Month 10-12
5. Month 13-18

## Learning resources

The user already has:

- IELTS Advantage - Speaking and Listening Skills (Ebook + Audio)
- Cambridge Grammar for IELTS
- English Grammar in Use
- IELTS Advantage Reading Skills
- Cambridge IELTS 17
- Complete IELTS Bands 6.5-7.5
- Complete IELTS Band 5.0-6.5
- The Official Cambridge Guide to IELTS
- English Collocations in Use Intermediate
- English Vocabulary in Use Upper-Intermediate
- IELTS Vocabulary for Bands 6.5 and above
- Cambridge Academic Vocabulary in Use
- English Collocations in Use Advanced
- IELTS Advantage Writing Skills

## Required main features

1. Dashboard / Player Profile
2. Skill Progress panel
3. Quest Board
4. Daily Quest
5. Weekly Mission
6. Boss Battle
7. Badge Wall
8. Mood / Energy Check-in
9. Error Log
10. Writing Tracker
11. Speaking Tracker
12. Mock Test Tracker

## Mood / Energy tracking

Each day should allow the user to record:

- Mood
- Energy level
- Focus level
- Short note

This is used to help the user understand which days are productive or tiring.

## Design requirements

- Strong gamified feeling
- Rank display must use F -> E -> D -> C -> B -> A -> S
- Progress should be visual, not only numeric
- Dashboard should feel rewarding and motivating
- Avoid clutter
- Vietnamese UI labels are preferred
- English technical terms may appear, but should be understandable

## Development expectations

When modifying the project:

1. Explain the change briefly.
2. Keep the app runnable with Docker Compose.
3. Do not remove existing features unless requested.
4. Prefer clean, simple, maintainable code.
5. Update seed data carefully.
6. Test backend syntax when possible.
7. Keep frontend responsive for laptop screens.

## Useful commands

Run the full project:

```bash
docker compose up --build
```

## Local development URLs

When the project is running with Docker Compose:

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- MySQL host: localhost
- MySQL port: 3307

Use these URLs to understand how the local app is accessed.

## Multi-agent workflow

This project uses a multi-agent Codex workflow.

### Root orchestrator

The root orchestrator should use GPT-5.5 with xhigh reasoning.

Responsibilities:

- Understand the full project context.
- Read AGENTS.md, SPEC.md, TASKS.md, and relevant files before acting.
- Make architecture-level decisions.
- Break large work into small tasks.
- Delegate implementation tasks to coder-gpt54.
- Delegate review tasks to reviewer-gpt55.
- Decide whether a task is complete or needs another fix cycle.
- Keep the final decision in the root thread.

The root orchestrator should not start coding immediately unless the user explicitly asks for a direct implementation.

### coder-gpt54

Use coder-gpt54 for implementation work.

Responsibilities:

- Write code.
- Fix bugs.
- Add or update tests.
- Update seed data when needed.
- Run relevant backend/frontend validation commands when possible.
- Report changed files, commands run, and test results.

Limitations:

- Do not make architecture-level decisions.
- Do not remove existing features unless explicitly instructed.
- Do not modify unrelated files.
- If requirements are unclear, stop and report the ambiguity.

### reviewer-gpt55

Use reviewer-gpt55 for important review tasks.

Responsibilities:

- Review code diffs.
- Check architecture consistency.
- Check bugs, regressions, security risks, and missing tests.
- Provide findings by severity:
  - P0: critical issue
  - P1: important issue
  - P2: improvement

Limitations:

- Do not edit files directly.
- Do not rewrite code unless asked.
- Give exact file paths and clear suggested fixes.

### Shared communication files

Use these files to communicate between agents:

- SPEC.md: product requirements and feature details.
- TASKS.md: current implementation plan.
- DECISIONS.md: architecture and product decisions.
- AGENT_NOTES.md: short reports from agents.
- TEST_REPORT.md: validation and test results.

### Required workflow

For medium or large changes:

1. Root orchestrator reads the project context.
2. Root orchestrator creates or updates TASKS.md.
3. User confirms the plan when needed.
4. Root orchestrator delegates one bounded task to coder-gpt54.
5. coder-gpt54 implements the task and reports results.
6. Root orchestrator delegates review to reviewer-gpt55.
7. If reviewer-gpt55 finds P0 or P1 issues, root orchestrator sends a focused fix task back to coder-gpt54.
8. Repeat until the change is accepted.
9. Root orchestrator summarizes final changes, files changed, tests run, and known limitations.

### Completion standard

A task is only complete when:

- The requested feature or fix is implemented.
- The app remains runnable with Docker Compose.
- Existing features are not broken.
- Important tests or syntax checks are run when possible.
- Any skipped validation is explained clearly.

## Mandatory changelog checklist

All implementation agents must update `changelogs.md` after each coding task.

The changelog must be written in a clear, visual, and review-friendly format so the user can quickly understand what changed.

### Required changelog information

Each changelog entry must include:

1. Date and time
2. Agent name
3. Task name
4. Task status
5. Summary of the change
6. Files changed
7. Changed line ranges or diff hunks
8. Features added
9. Bugs fixed
10. Code removed, if any
11. Commands run
12. Validation result
13. Remaining issues
14. Suggested next step
15. Review checklist

### Line change requirement

When possible, the agent must use `git diff --unified=0` or an equivalent diff view to identify changed line ranges.

If exact line numbers are difficult to determine because the file changed heavily, the agent must write:

- the affected function/component/section name;
- the approximate line range;
- a short explanation of what changed there.

Do not simply write “updated frontend” or “fixed backend”. The changelog must identify the concrete files and code areas.

### Required changelog format

Use this format for every task:

````md
## [YYYY-MM-DD HH:mm] Task name

**Agent:** coder-gpt54  
**Status:** Done / Partially done / Blocked  
**Related task:** Task name or TASKS.md item

### 1. Summary

Short explanation of what changed and why.

### 2. Files changed

| File           | Change type                | Changed lines / area   | What changed      |
| -------------- | -------------------------- | ---------------------- | ----------------- |
| `path/to/file` | Added / Modified / Deleted | `L10-L35` or diff hunk | Clear explanation |

### 3. Features added

- [ ] Feature 1
- [ ] Feature 2

### 4. Bugs fixed

- [ ] Bug 1
- [ ] Bug 2

### 5. Code removed

- [ ] Removed unused code / cache / obsolete logic
- [ ] None

### 6. Commands run

```bash
command here
```
````

### 7. Validation result

- [ ] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Write test/lint/build/runtime result here.
```

### 8. Remaining issues

- [ ] None
- [ ] Issue 1
- [ ] Issue 2

### 9. Suggested next step

- Next recommended action.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

```

### Completion rule

A coding task must not be marked as complete unless `changelogs.md` has been updated.

The final response from the orchestrator must mention that `changelogs.md` was updated.
```

## Cost-aware multi-agent workflow

This project uses a cost-aware multi-agent workflow.

### Model usage policy

Do not use GPT-5.5 xhigh for routine work.

Use `web-architect-gpt55-xhigh` only for:

- major frontend architecture decisions;
- major UI/UX direction changes;
- database schema changes;
- API contract changes;
- Docker Compose changes;
- dependency additions;
- authentication/security-related changes;
- large refactors;
- high-risk product decisions.

Use lower-cost agents for routine work:

- `web-dispatcher-gpt54` for daily coordination.
- `web-docs-gpt54-mini` for TASKS.md, DECISIONS.md, changelogs.md, TEST_REPORT.md.
- `coder-gpt54` for implementation.
- `reviewer-gpt55` for review.

### Dispatcher rule

The main dispatcher must not read the entire repository unless necessary.

Prefer:

- reading AGENTS.md, TASKS.md, changelogs.md, TEST_REPORT.md first;
- targeted file reads;
- `git status --short`;
- `git diff --stat`;
- `git diff --unified=0`.

### Documentation delegation rule

The dispatcher should delegate documentation updates to `web-docs-gpt54-mini`.

GPT-5.5 xhigh must not be used to write routine changelog, task list, decision log, or test report entries.

### Architecture decision rule

Call `web-architect-gpt55-xhigh` before:

- changing database schema;
- changing API contracts;
- changing Docker Compose configuration;
- adding dependencies;
- large frontend refactors;
- changing core XP/level/rank logic;
- changing data model for quests, badges, mood tracking, mock tests, writing tracker, or speaking tracker.

### Changelog rule

Every implementation task must update `changelogs.md`.

The changelog must include:

- Date and time
- Agent name
- Task name
- Task status
- Files changed
- Changed line ranges or changed areas
- Features added
- Bugs fixed
- Code removed
- Commands run
- Frontend/backend/database/Docker validation result
- Remaining issues
- User review checklist

Do not mark a task as complete unless `changelogs.md` is updated.
