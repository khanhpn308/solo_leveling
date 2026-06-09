# AGENTS.md

Root agent guide for `IELTS Quest Dashboard`.

## Project

- Product: local gamified IELTS Academic dashboard.
- Goal: help the user reach IELTS `7.0-7.5` over an 18-month campaign.
- Stack: React + Vite, FastAPI, MySQL, Docker Compose.
- Direction: game-style progression, quests, skills, levels, badges, and review loops.

## Source of Truth

- `docs/current/` = current product, schema, business rules, prompts, and ADRs.
- `docs/history/` = changelogs, test reports, migration notes, old plans, and session notes.
- Do not treat history docs as current truth unless a canonical doc points to them.

## Load Context

Read in this order:

1. `AGENTS.md`
2. `README.md`
3. `TASKS.md`
4. `DECISIONS.md`
5. `docs/current/CONTEXT_INDEX.md`

Then read only task-specific canonical docs.

Stop loading context when these are clear:

- task type
- likely files to change
- existing pattern to follow
- goal, constraints, risks, and next steps

## Workflow

1. **Ground the repo**: understand current state before editing.
2. **Lock the task contract**: define goal, done criteria, scope, constraints, and risks.
3. **Plan only when needed**: plan first for multi-file, backend, schema, API, migration, or broad UI work.
4. **Execute in small slices**: change only what is necessary; no unrelated cleanup.
5. **Verify before done**: prefer syntax/type checks, focused smoke checks, changed-behavior tests, then review for risky work.
6. **Update docs and close cleanly**: record what changed, what was validated, what remains open, what to read next, and move completed tasks from `TASKS.md` to `tasks-done.md`.

## Engineering Rules

- Keep the app runnable with Docker Compose.
- Do not remove existing features unless explicitly requested.
- Prefer additive, low-risk schema and API evolution.
- Keep public API response shapes stable unless the user approves a contract change.
- Keep repository documentation in English.
- Follow existing repo patterns before introducing new ones.

## Documentation Rules

Update only after meaningful changes:

- `TASKS.md`: active task status.
- `tasks-done.md`: archived completed tasks list.
- `docs/history/changelogs.md`: newest entry first.
- `docs/history/TEST_REPORT.md`: validation evidence.
- `docs/history/AGENT_NOTES.md`: short factual notes only.
- `DECISIONS.md` or `docs/current/decisions/ADR-*`: enduring architecture/workflow decisions.

## Skill Routing

Use the smallest sufficient skill set:

- Planning: `planning-and-task-breakdown`
- Docs / ADR: `documentation-and-adrs`
- Backend: `backend-development`, plus `fastapi-templates`, `api-and-interface-design`, `mysql` when needed
- Frontend: `frontend-ui-engineering` or `frontend-design` or `ui-ux-pro-max`, plus `browser-testing-with-devtools` when visual verification matters
- Debug: `debugging-and-error-recovery`, plus `test-driven-development` when behavior must be locked
- Migration: `deprecation-and-migration`, plus `mysql`
- Review: `code-review-and-quality`
- Wrap-up: `documentation-and-adrs`

## Session Close Format

End each coding session with:

- Changed:
- Validated:
- Still open:
- Next session should read:
