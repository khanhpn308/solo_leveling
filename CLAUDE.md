# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run the full stack
```bash
docker compose up --build
```

### Run individual services
```bash
docker compose up mysql          # DB only
docker compose up backend        # API + DB
docker compose up frontend       # Frontend + all deps
```

### Local URLs
- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`
- MySQL: `localhost:3307` (user: `ielts_user`, password: `ielts_password`, db: `ielts_quest`)

### Frontend dev (inside container or with Node locally)
```bash
cd frontend
npm run dev          # Vite dev server
npm run build        # Production build
npm run test:dashboard-data   # Only existing frontend test
```

### Run Alembic migrations (inside backend container or via API)
```bash
# Via API endpoint (dev only):
POST http://localhost:8000/api/dev/run_migrations

# Or exec into the container:
docker exec -it ielts_quest_backend alembic upgrade head
```

### Reset and re-seed the database (dev only)
```
POST http://localhost:8000/api/dev/reset
```

## Architecture

### Stack
- **Frontend**: React 18 + Vite, no TypeScript, no CSS framework — raw JSX + `src/styles.css`
- **Backend**: FastAPI + SQLAlchemy 2 (sync sessions) + Alembic migrations
- **DB**: MySQL 8.4 (port 3307 externally, 3306 internally)
- **Runtime**: Docker Compose; backend volume-mounts `./backend` so edits hot-reload via uvicorn

### Backend layout (`backend/app/`)
| File | Role |
|---|---|
| `main.py` | All FastAPI routes (single file) |
| `models.py` | All SQLAlchemy ORM models |
| `schemas.py` | All Pydantic I/O schemas |
| `services.py` | Business logic — XP award, quest completion, rank/weakness suggestions, vocabulary, SRS |
| `seed.py` | Deterministic DB seed run at startup (idempotent) |
| `database.py` | Engine, session factory, bootstrap, health-wait |
| `auth_utils.py` | JWT create/decode, password hash/verify |

### Data model mental model
The progression hierarchy is: `Account → Player → Campaign → CampaignSkillState / Quest / BossBattle / BadgeUnlock`.

- **Account** — auth entity (email/password/JWT sessions).
- **Player** — study profile, XP totals, streaks, level.
- **Campaign** — the active 18-month study run. All gameplay data is scoped to a campaign.
- **CampaignSkillState** — per-skill XP, rank (`F`→`S`), streaks within a campaign.
- **Quest** — individual study sessions; `session_type` is `"Daily Quest"` or `"Main Quest"`.
- **XP flow**: complete quest → mark `completed` → call `/claim` → `award_player_xp` or `award_skill_xp` writes an idempotency-keyed `XpTransaction` row → `refresh_progress_state` recomputes totals.

### Frontend layout (`frontend/src/`)
All UI state comes from polling `/api/summary`. Components are standalone JSX files under `src/components/`. The main dashboard is `App.jsx` which renders a panel grid.

### Migrations
All schema changes go through Alembic (`backend/alembic/versions/`). Migration filenames follow `YYYYMMDD_NN_description.py`. Waves A–E are complete. New migrations must include `upgrade()` and `downgrade()`.

### Seeding
`seed.py:seed_database()` runs on every container start and is fully idempotent — it uses `get_or_create`-style guards. It seeds skills, badges, campaign template, roadmap phases, quest schedule, boss battles, and weekly missions from `material.md`.

## Source of Truth

- `docs/current/` = current product, schema, business rules, prompts, ADRs.
- `docs/history/` = changelogs, test reports, migration notes, old plans, session notes.
- Do not treat history docs as current truth unless a canonical doc points to them.

## Workflow

1. **Ground the repo** — understand current state before editing.
2. **Lock the task contract** — define goal, done criteria, scope, constraints, risks.
3. **Plan when needed** — plan first for multi-file, backend, schema, API, migration, or broad UI work.
4. **Execute in small slices** — change only what is necessary; no unrelated cleanup.
5. **Verify before done** — syntax/type checks → smoke checks → changed-behavior tests → review for risky work.
6. **Update docs and close** — record what changed, what was validated, what remains open, what to read next; move completed tasks from `TASKS.md` to `tasks-done.md`.

**Gap-check gate:** A task must have `**Gap check:** [x]` before it can be moved to `tasks-done.md`. After implementing a task, audit for gaps (missing edge cases, stale callers, doc mismatches, broken tests). Mark `[x]` once all gaps are found + fixed (or explicitly deferred with a note). Never archive a task with `[ ]` gap check.

Stop loading context once these are clear: task type, likely files to change, existing pattern to follow, goal/constraints/risks/next steps.

## Engineering Rules

- Keep app runnable with Docker Compose.
- Do not remove existing features unless explicitly requested.
- Prefer additive, low-risk schema and API evolution.
- Keep public API response shapes stable unless the user approves a contract change.
- Keep repository documentation in English.
- Follow existing repo patterns before introducing new ones.

## Documentation Rules

Update only after meaningful changes:

| File | When |
|---|---|
| `TASKS.md` | active task status |
| `tasks-done.md` | archive completed tasks |
| `docs/history/changelogs.md` | newest entry first |
| `docs/history/TEST_REPORT.md` | validation evidence |
| `docs/history/AGENT_NOTES.md` | short factual notes only |
| `DECISIONS.md` / `docs/current/decisions/ADR-*` | enduring arch/workflow decisions |

## Skill Routing

| Task | Skills |
|---|---|
| Planning | `planning-and-task-breakdown` |
| Docs / ADR | `documentation-and-adrs` |
| Backend | `backend-development`, + `fastapi-templates`, `api-and-interface-design`, `mysql` when needed |
| Frontend | `frontend-ui-engineering` or `frontend-design` or `ui-ux-pro-max`, + `browser-testing-with-devtools` for visual verification |
| Debug | `debugging-and-error-recovery`, + `test-driven-development` when behavior must be locked |
| Migration | `deprecation-and-migration`, + `mysql` |
| Review | `code-review-and-quality` |
| Wrap-up | `documentation-and-adrs` |

## Session Close Format

End each coding session with:

```
- Changed:
- Validated:
- Still open:
- Next session should read:
```

## Context load order for new sessions

1. `AGENTS.md`
2. `README.md`
3. `TASKS.md`
4. `DECISIONS.md`
5. `docs/current/CONTEXT_INDEX.md`

Then load only the canonical doc relevant to the task:
- Schema changes → `docs/current/DATABASE_SCHEMA.md` + `docs/current/SCHEMA_SEMANTICS.md`
- Business logic → `docs/current/BUSINESS_RULES.md`
- Product direction → `docs/current/PROJECT_CONTEXT.md`
