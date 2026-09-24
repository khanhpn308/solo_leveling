# 01 — Baseline repository discovery inventory

Strictly read-only. Every row below names a file that was opened during this pass unless marked
`[UNRESOLVED]`. See `README.md` for the evidence convention.

---

## 1. Top-level layout (as found on disk)

```
.claude/launch.json  .codegraph/  .env.example  .freebuff/  .mcp.json  .vscode/settings.json
AGENTS.md  CLAUDE.md  DECISIONS.md  README.md  TASKS.md  tasks-done.md  prompt-en.md  prompt-vi.md
backend/  docker-compose.yml  docs/{current,history}/  error/  frontend/  guideline/  img/
material/  plans/  spec/{feature,infor}/
```

Verified by `find . -maxdepth 2`. Tracked-file distribution (from `git ls-files`, top two path
segments):

| Path | Tracked files | Meaning |
| --- | --- | --- |
| `frontend/node_modules` | 1533 | installed dependencies are **committed** |
| `backend/alembic` | 57 | 31 migration scripts + framework + `__pycache__` |
| `frontend/src` | 53 | application source |
| `backend/app` | 19 | 8 modules + `__pycache__` |
| `frontend/dist` | 11 | **built bundle is committed** (9 of the 11 are bundles under `dist/assets/`; MF-23) |
| `docs/current` | 11 | canonical docs |
| `docs/history` | 5 | history docs |
| `spec/*` | 7 | product/feature specs |
| `material/*` | 3 | seed source markdown |

**No root `.gitignore` exists** (`cat .gitignore` → no such file). That is the direct cause of
`node_modules/`, `dist/`, `__pycache__/` (35 tracked files) and `.vite-dev.log` being tracked. Tracked
totals at the errata pass: **1754** files, of which `frontend/node_modules/` **1533**, this audit
**12**, `frontend/dist/` **11**, `__pycache__` **35**, other **163** — **[MF-23]**.

---

## 2. Manifests (real, as parsed)

### `frontend/package.json` (opened)
- `name: ielts-quest-dashboard`, `version 1.0.0`, `private: true`, `type: module`.
- Scripts: `dev` → `vite --host 0.0.0.0`; `build` → `vite build`; `preview` → `vite preview --host 0.0.0.0`;
  `test:dashboard-data` → `node --test src/dashboard-data.test.js`. **No `lint` script.**
- Dependencies (all under `dependencies`, none in `devDependencies`): `@vitejs/plugin-react ^4.3.4`,
  `react ^18.3.1`, `react-dom ^18.3.1`, `react-router-dom ^7.17.0`, `reactflow ^11.11.4`,
  `vite ^5.4.19`.
- `frontend/package-lock.json` is committed, yet `frontend/Dockerfile` runs `npm install` (not
  `npm ci`) — see U-06.

### `backend/requirements.txt` (opened)
Pinned: `fastapi==0.115.6`, `uvicorn[standard]==0.32.1`, `SQLAlchemy==2.0.36`, `alembic==1.14.0`,
`PyMySQL==1.1.1`, `cryptography==44.0.0`, `pydantic==2.10.3`, `python-dotenv==1.0.1`, plus
unpinned `httpx`.

**Declared but never imported by any module under `backend/app/`** (verified by
`grep -rn "httpx" app/`, `grep -rn "dotenv\|cryptography" app/` → no matches): `httpx`,
`python-dotenv`, `cryptography`. `cryptography` is a documented PyMySQL requirement for MySQL 8
auth, but no direct use is visible in this repo.

### Environment template — `.env.example` (opened; **key names only**)
Contains three keys: `DATABASE_URL`, `APP_START_DATE`, `CORS_ORIGINS`. There is **no `.env` file on
disk** at repo root or in `backend/` (`ls -la .env` → absent).

---

## 3. Runtime entry points

### Backend — FastAPI ASGI app
- `backend/app/main.py:208`: `app = FastAPI(title="IELTS Quest Dashboard API", version="2.0.0")`.
- Served by `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`, declared twice:
  `docker-compose.yml:25` (compose `command`) and `backend/Dockerfile:16` (image `CMD`).
- **Startup hook** `backend/app/main.py:431-441`: on `@app.on_event("startup")` it calls
  `wait_for_database()` → `run_database_bootstrap()` → `seed_database(db, parse_start_date())` →
  `refresh_progress_state(db)`. The process therefore **self-migrates and self-seeds on every boot**
  and will not start without a reachable, writable database plus the material markdown files.
- Only one ASGI app exists; **there is no router package and no `APIRouter`** — all 121 HTTP routes (MF-01)
  are declared directly on `app` in the single 2874-line `backend/app/main.py`
  (`grep -c '^@app\\.(get|post|put|patch|delete)'` → 121; breakdown GET 59, POST 51, PATCH 3,
  PUT 1, DELETE 7). **[MF-01, MF-04]**

### Frontend — Vite + React SPA
- HTML entry `frontend/index.html:9` loads `/src/main.jsx`.
- `frontend/src/main.jsx:12-31`: `createRoot` + `React.StrictMode` + `BrowserRouter` and exactly
  four route branches — `/login`, `/register`, `/onboarding`, and `/*` wrapped in
  `<ProtectedRoute><App/></ProtectedRoute>`.
- Dev server config `frontend/vite.config.js:1-13`: only plugin `react` and `server.host: '0.0.0.0'`
  with polling watch (`usePolling`, `interval: 100`, `ignored: []`). **No `server.proxy`**, so the
  browser talks to the API cross-origin (see CORS below).
- `frontend/src/App.jsx` (1029 lines) is the single in-app shell: it holds ~30 pieces of `useState`
  for the dashboard, quests, overlays, toasts and the rank-exam flow, and switches the whole
  workspace between `'dashboard'` and `'vocabulary'` via `currentView` (`frontend/src/App.jsx:130`).
  It is the only place that composes most panels; the heavy overlays are `React.lazy` imports
  (`frontend/src/App.jsx:29-33`).

---

## 4. Frontend application surface

- 53 files under `frontend/src`; **40 in `components/`**, 3 in `pages/` (`Login.jsx`,
  `Register.jsx`, `Onboarding.jsx`), plus `api/` (3 files), `auth/` (2 files), `App.jsx`,
  `main.jsx`, `dashboard-data.js`, `dashboard-data.test.js`, `styles.css`.
- Styling: **one hand-written global stylesheet**, `frontend/src/styles.css`, 6276 lines. No
  Tailwind, no CSS framework, no CSS modules (`grep -rn "tailwind\|bootstrap" src/ package.json` →
  no matches).
- Only `react-router-dom` and `reactflow` provide third-party UI behaviour (`reactflow` drives the
  `WordNetworkTree`/`WordFamilyEvolution` vocab graphs — see component names and the
  `reactflow` dependency in `frontend/package.json`).
- `frontend/src/dashboard-data.js` (817 lines) is a **pure client-side view-model + domain-logic
  module**: it exports `RANK_ORDER`, `SKILL_THEME`, `MAIN_QUEST_PHASES`, and builders such as
  `buildDashboardView`, `buildMainQuestMap`, `getSkillProgress`, `getPlayerXpProgress`,
  `buildSuggestionInbox`, `buildBossView` (31 exports total, `grep -n '^export'`). `App.jsx` calls
  these inside `useMemo` to shape API payloads into view state
  (`frontend/src/App.jsx:216-241`).
- `dashboard-data.js:619` `getPlayerXpProgress` reimplements the backend level curve; the frontend
  test asserts it "mirrors the backend 19*(L^1.6-1) curve", and the backend source of that curve is
  `backend/app/services.py:74-77` (`xp(L) = round(19 * (L**1.6 - 1))`, L 1..60). The same curve
  therefore exists twice, in two languages (see U-05).

### Client → server calls (mechanically extracted)
`grep -rhoE "(api|apiFetch)\\(.[^)]*" src/` over `frontend/src` yields **62 distinct API paths after
normalising template expressions** (`${…}` → `{}`, trailing `/` stripped) — 64 distinct raw strings
before normalisation. For comparison, the 121 backend routes collapse to **105 distinct path
templates** under the same normalisation. **[MF-01, MF-03, MF-21]** Only 11 files call the API at all:

| Calls | File |
| --- | --- |
| 17 | `src/App.jsx` |
| 14 | `src/components/VocabularyWorkspace.jsx` |
| 10 | `src/components/VocabularyOverlay.jsx` |
| 8 | `src/components/WordNetworkTree.jsx` |
| 7 | `src/components/CollocationForge.jsx` |
| 3 | `src/components/VocabularyLibrary.jsx` |
| 2 each | `WordFamilyEvolution.jsx`, `VocabularyBoss.jsx`, `ShadowDuel.jsx`, `EchoChamber.jsx` |
| 1 | `src/components/ErrorDungeon.jsx` |

So the vocabulary/collocation feature set — not the dashboard — carries the largest share of the
client's API surface.

---

## 5. Backend application surface

| File | Lines | Role |
| --- | --- | --- |
| `backend/app/main.py` | 2874 | FastAPI app, CORS, auth dependencies, **all 121 routes** (MF-01), serializers, dev endpoints |
| `backend/app/services.py` | 3267 | 94 domain functions: XP/level/rank maths, quest completion, recompute passes, vocab/collocation/rank-exam logic |
| `backend/app/seed.py` | 2784 | 52 functions (MF-16): idempotent seeding of skills/badges/templates/quests/missions/bosses, markdown parsers |
| `backend/app/models.py` | 1559 | SQLAlchemy 2.0 models — **72 `__tablename__` declarations** (MF-09) |
| `backend/app/schemas.py` | 1272 | Pydantic I/O models — **119 classes** (MF-10) |
| `backend/app/test_backend.py` | 3004 | unittest suite (see §9) |
| `backend/app/database.py` | 67 | engine, session factory, `get_db`, bootstrap/migrate |
| `backend/app/auth_utils.py` | 74 | hand-rolled JWT + password hashing |

### Route groups (extracted from the decorator list in `main.py`)
- `/api/health` — 1.
- `/api/auth/*` — register, login, refresh, logout, me (5).
- `/api/onboarding/*` — status, activate-campaign (2).
- Core dashboard — `/api/summary`, `/api/profile`, `/api/player/targets`, `/api/setup`,
  `/api/campaigns/current`, `/api/skills`, `/api/quest-templates`, `/api/materials[/{id}]`,
  `/api/roadmap/phases`, `/api/study-plan/weeks|current-week` (~11).
- Quests & progression — `/api/main-quests`, `/api/quests`, `/api/quests/today`,
  `/api/quests/{id}/complete|uncomplete|claim`, `/api/weekly-mission/current`,
  `/api/weekly-missions/{id}/claim`, `/api/checkins`, `/api/badges`, `/api/boss-battles[/{id}/claim]`,
  `/api/test-records`, rank + weakness suggestion apply/dismiss (both under two alias prefixes),
  `/api/certificates[/manual]` (~25).
- Trackers & logs — `/api/error-logs`, `/api/writing-entries`, `/api/speaking-entries`,
  `/api/mock-tests`, `/api/weakness-suggestions` (5).
- Dev — `/api/dev/reset`, `/api/dev/run_migrations`, `/api/dev/regenerate-quests` (3).
- Rank exams — `/api/rank-exams/unlock|start|status/{skill_id}|{attempt_id}|{attempt_id}/submit` (5).
- Vocabulary — CRUD, examples, relations, flashcards, spaced repetition, tree (topics/nodes/edges),
  practice (collocations/shadow-duel/word-family/echo-chamber), errors, boss (~40).
- Collocations — collections/sections/topics/items, campaign links, item progress, browse levels,
  browse topics/items, per-item flashcards + review (~24).
- Vocab library — levels → topics → units → sections → words, flashcards + due + review (~9).

### Dev-facing endpoints with surprising reach
- `backend/app/main.py:1498-1583` `POST /api/dev/reset`: sets `FOREIGN_KEY_CHECKS = 0`, deletes
  every row of **all 72 model tables** (including `Account`, `Campaign`, `Player`, `Skill`; MF-09),
  commits, then re-seeds. No token requirement, no environment gate, and **the frontend never calls
  it** (absent from the 62-path client list; MF-21) — it is curl-only.
- `backend/app/main.py:1587-1597` `POST /api/dev/run_migrations`: runs
  `alembic_command.upgrade(cfg, "head")` using `AlembicConfig("alembic.ini")` — a **relative** path,
  so it depends on the process CWD.
- `backend/app/main.py:1877-1899` `POST /api/dev/regenerate-quests`: resolves the player through
  `get_player_or_404(db)` (`main.py:417-427`), which delegates to `services.get_active_player(db)`
  — i.e. the **first row of `players`**, not the caller's player (no caller, since it is
  unauthenticated).

---

## 6. Database-related code

- **Engine** `backend/app/database.py:11-19`: `DATABASE_URL` (env, with a MySQL default string),
  `create_engine(..., pool_pre_ping=True, pool_recycle=3600)`. No connection-pool size config, no
  caching layer.
- Session factory `database.py:22`; request-scoped `get_db` generator `database.py:41-46`.
- `wait_for_database(max_retries=30, delay_seconds=2)` `database.py:31-38` — 60 s startup budget.
- `run_database_bootstrap()` `database.py:45-63`: if `alembic.ini` is missing → `create_all`;
  if the schema is empty → `create_all` + `alembic stamp head`; otherwise → `alembic upgrade head`.
  **Migrations run from application startup**, not from a separate deploy step.
- Alembic: `backend/alembic.ini` (script_location `alembic`, `sqlalchemy.url` pointing at
  `127.0.0.1:3307`), `backend/alembic/env.py:36-52` (overrides the URL from `$DATABASE_URL` when
  set), and **31 version files** in `backend/alembic/versions/` — 23 named
  `2026MMDD_NN_*.py` plus 8 hash-named ones, including an explicit `20260607_13_merge_heads.py`
  (evidence of a merged, multi-head migration history).
- Models: **72 tables** in `models.py`. Distinct clusters: accounts/sessions/tokens/security events/
  preferences (6), players + learning profiles + campaigns + settings + quotas + vocab settings (8),
  skills + quests + templates + quest xp policies (6), XP ledger (`campaign_skill_states`,
  `skill_xp_transactions`, `player_xp_transactions`, `rank_xp_thresholds`, `main_quest_xp_policies`,
  `weekly_mission_xp_policies`, `quest_xp_policies`), badges, weekly missions, boss battles,
  test records, rank suggestions/history, certificates, rank exams (5), study material/plan (6),
  trackers (4), vocabulary (13), collocations (7), vocab library (7).
- Seed **data source is markdown on disk**, resolved at runtime:
  `seed.py:557-578` `material_file_path()` (`MATERIAL_PLAN_PATH` → fallbacks
  `<repo>/material.md`, `backend/material.md`, `./material.md`),
  `seed.py:2061-2085` `collocations_file_path()` (`COLLOCATIONS_PATH` → fallbacks into
  `material/collocation/English_Collocations_campaign1-3_3-6_polished.md`),
  `seed.py:2543-2555` `_vocab_materials_root()` (`VOCABULARIES_PATH` → `material/vocabularies`).
  On disk: `material/material.md`, `material/collocation/…polished.md`,
  `material/vocabularies/pre-intermediate_intermediate/vocab.md` (3 files total), **plus a second,
  separate `backend/material.md`**.

---

## 7. Realtime layers — **none found**

Searched `backend/app/` for `WebSocket|websocket|sse|StreamingResponse|EventSource|MQTT|broker|
scheduler|background` and `frontend/src` for `EventSource|WebSocket`:
- The only `websocket`-adjacent import is `fastapi`'s standard import list; **no `WebSocket` route,
  no `StreamingResponse`, no SSE, no message broker client, no background task queue, no scheduler**
  exists in the repository.
- Frontend timers are all local UI, not data sync: `frontend/src/App.jsx:163-167` (60 s clock tick
  for `hostNow`), `frontend/src/components/RankExamScreen.jsx:13` (exam countdown),
  `frontend/src/components/ShadowDuel.jsx:39` (mini-game timer).
- Data freshness is therefore **load-once-on-mount plus explicit user action**:
  `frontend/src/App.jsx:169-176` runs `loadInitialData / loadMainQuestData / loadWeeklyMission /
  loadSuggestions / loadCertificates / loadBossBattles` exactly once with an empty dependency array.
- `frontend/src/components/usePresenceLayer.jsx` is **not** a realtime presence layer — it is an
  overlay enter/exit mount-animation and focus-trap hook (`EXIT_DURATION_MS = 140`,
  `usePresenceLayer` return `{isMounted, phase, rootRef}`).

**Caches: none.** No Redis/Memcached client, no in-process cache library, no HTTP cache headers set
anywhere in `main.py`.

---

## 8. Reverse proxy / infrastructure / containers

- **No reverse proxy.** Searched for `nginx|traefik|caddy|reverse.proxy|proxy_pass` across
  `*.yml|*.yaml|*.conf|*.md|Dockerfile` → **zero matches**. Ingress is direct port publishing
  (`3307:3306`, `8000:8000`, `5173:5173` in `docker-compose.yml`).
- **No TLS anywhere** in the compose file or Dockerfiles.
- `docker-compose.yml` (56 lines, opened): three services.
  - `mysql` — image `mysql:8.4`, `container_name ielts_quest_mysql`, `restart: unless-stopped`,
    named volume `mysql_data:/var/lib/mysql`, port `3307:3306`, healthcheck `mysqladmin ping`
    (with credentials inline), `MYSQL_DATABASE/USER/PASSWORD/ROOT_PASSWORD` set inline.
  - `backend` — `build: ./backend`, port `8000:8000`, `depends_on: mysql: service_healthy`,
    restart `unless-stopped`; env keys `DATABASE_URL`, `APP_START_DATE`, `MATERIAL_PLAN_PATH`,
    `CORS_ORIGINS`, `PYTHONUNBUFFERED`; volumes `./backend:/app` plus three
    **`:ro`** material mounts (`material.md`, `material/vocabularies`, `material/collocation`).
    The bind mount shadows the image's `COPY . .`, so in compose the code runs from the host tree
    with `--reload`.
  - `frontend` — `build: ./frontend`, port `5173:5173`, restart `unless-stopped`; env keys
    `VITE_API_URL`, `CHOKIDAR_USEPOLLING`, `CHOKIDAR_INTERVAL`; volumes `./frontend/src`,
    `./frontend/public`, `./frontend/vite.config.js:ro`.
- **Working-tree change (pre-existing, not made by this audit)** — `git diff docker-compose.yml`
  shows exactly one line: `VITE_API_URL` changed from `http://<public-ip>:8000/api` to
  `http://localhost:8000/api`. The committed HEAD value pointed the browser at a **remote host**.
  `CORS_ORIGINS` in the working tree still allows `http://localhost:5173`,
  `http://127.0.0.1:5173` and `http://<the same public ip>:5173` (docker-compose.yml:30).
- `backend/Dockerfile` (16 lines): `python:3.12-slim`, `pip install -r requirements.txt`,
  `COPY . .`, `EXPOSE 8000`, `CMD uvicorn … --reload`. **No multi-stage build; `--reload` baked into
  the image.**
- `frontend/Dockerfile` (14 lines): `node:20-alpine`, `npm install`, copies `index.html`,
  `vite.config.js`, `public`, `src`, `EXPOSE 5173`, `CMD ["npm","run","dev"]`.
  **The container runs the Vite dev server**; `npm run build` / `vite preview` exist in
  `package.json` but are wired to nothing (no compose service, no script, no proxy) — the committed
  `frontend/dist/` is therefore a **build artifact with no consumer in this repo**.
- Local URLs are documented in `README.md`: frontend `:5173`, backend docs `:8000/docs`,
  MySQL `localhost:3307`.

---

## 9. Tests

| Suite | File | Runner | Count | Executed? |
| --- | --- | --- | --- | --- |
| Frontend domain logic | `frontend/src/dashboard-data.test.js` | `node:test` + `node:assert/strict` | 6 tests (`ℹ tests 6`) | **Yes — 6 pass, 0 fail** |
| Backend API/domain | `backend/app/test_backend.py` | `unittest` + `fastapi.testclient.TestClient` | 68 `def test_` across 11 `TestCase` classes | **No — no Python in the audit shell (U-04)** |

Backend test file facts that were read: it builds **in-memory SQLite** with
`StaticPool`/`check_same_thread=False` (`test_backend.py:27-33`, and again `:497-501` for the auth
class), creates the schema with `Base.metadata.create_all` — i.e. **tests bypass Alembic**, so
migrations are not covered — and overrides `get_db`/`get_current_player`/`get_current_campaign` via
FastAPI dependency injection. Test classes: `TestWaveDAndE`, `TestAuthEndpoints`,
`TestOnboardingEndpoints`, `TestCertificateAndSuggestionEndpoints`, `TestDailyQuestQuotaGenerator`,
`TestRankExamPhase9`, `TestCollocationMasterData`, `TestPolicyTables`,
`TestGap151MainQuestReadsPolicy`, `TestGap153WeeklyPolicyAllRowsReachable`, `TestCollocationFlashcards`.
The test module lives **inside the app package** (`backend/app/`), so `COPY . .` ships it into the
backend image. There is **no test config file** (no `pytest.ini`, `pyproject.toml`, `setup.cfg`),
no coverage config and no CI to run it.

Frontend test notes: `dashboard-data.test.js:1-4` imports `node:test`, `node:assert/strict` and
`node:child_process`; the DST cases use `spawnSync` to re-run node under a different `TZ`.

---

## 10. Scripts & automation

- **No shell scripts, no Makefile, no task runner.** The only runnable entry points are
  `package.json` scripts (4) and the compose file. There is no `scripts/` directory, no
  `manage.py`, no `start.sh`.
- Root markdown files that act as process glue rather than documentation of code:
  `AGENTS.md` (agent workflow + context load order), `CLAUDE.md`, `DECISIONS.md`,
  `TASKS.md` (149 750 bytes — largest tracked markdown), `tasks-done.md` (55 443 bytes),
  `prompt-en.md` / `prompt-vi.md` (1 byte each — effectively empty stubs).
- Editor/agent tooling config: `.claude/launch.json` (a `frontend` launch config on port 5173),
  `.vscode/settings.json` (contains only an Espressif IDF path — unrelated to this project),
  `.mcp.json` (registers a `codegraph` MCP server), `.codegraph/{.gitignore,daemon.pid}`.

---

## 11. CI configuration — **none found**

`ls -la .github .gitlab-ci.yml Jenkinsfile .circleci` → all four absent. No `.woodpecker`,
`.drone.yml`, `azure-pipelines.yml`, `.travis.yml` or `bitbucket-pipelines.yml` were found in the
root listing or the tracked-file list. **No pipeline, no automated test run, no build gate, no
image push exists in this repository.** (Search was limited to these conventional locations —
recorded as U-12.)

---

## 12. Generated & vendored code

- `frontend/node_modules/` — 1533 tracked files (vendored dependency tree).
- `frontend/dist/` — 9 minified asset files + `index.html`, committed. Total ~669 KB of JS/CSS in
  `assets/`, e.g. `index-DgK1V2iM.js` (299 351 B), `VocabularyWorkspace-BFLW5paV.js` (228 083 B),
  `index-C6I3zGjs.css` (99 979 B). `dist/index.html` references the hashed bundles directly.
  The committed bundle still contains the route string `/me` and `/logout` payloads
  (`frontend/dist/assets/VocabularyWorkspace-BFLW5paV.js`), confirming it was built from a source
  tree that already had the auth client.
- `backend/app/__pycache__/` and `backend/alembic/versions/__pycache__/` — 35 tracked `.pyc` files.
- `frontend/package-lock.json` — generated, committed.
- `frontend/.vite-dev.log` and `frontend/.vite-dev.err.log` — tracked and **both 0 bytes**, so they
  carry no runtime evidence.

---

## 13. External integrations — **none found**

- `grep -rn "httpx|import requests|urllib|aiohttp|socket\." backend/app/` → **no matches**.
- `grep -rn "http://|https://" backend/app/*.py` filtered for non-local origins → **no matches**.
  The only URLs in backend code are the `CORS_ORIGINS` default (`main.py:210`) and the
  `DATABASE_URL` default (`database.py:11-13`).
- No email/SMS/push provider, no payment SDK, no analytics SDK, no LLM/AI client, no object storage,
  no OAuth/social-login provider, no observability/APM agent. The only "external" surface in the repo
  is the remote HTTP origin recorded in `docker-compose.yml` (§8) and the IP listed in
  `CORS_ORIGINS`.

---

## 14. Authentication & authorization code (inventory; architecture in `02`)

- `backend/app/auth_utils.py` — the entire crypto layer: `base64url_encode/decode`, `create_jwt`
  (HS256 written by hand with `hmac`+`hashlib.sha256`), `decode_jwt` (constant-time compare, `exp`
  check, returns `None` on any failure), `hash_password` / `verify_password`
  (PBKDF2-HMAC-SHA256, 100 000 rounds, 16 random salt bytes, stored as
  `pbkdf2_sha256$<rounds>$<salt-hex>$<key-hex>`).
  `auth_utils.py:8` defines `SECRET_KEY = os.getenv("JWT_SECRET_KEY", "<hardcoded fallback>")` —
  the fallback literal is present in the tracked file (value not reproduced here).
- `backend/app/main.py:219` `security = HTTPBearer(auto_error=False)` and `main.py:222-306`:
  `get_current_account` → `get_current_player` → `get_current_campaign` / `get_optional_campaign`.
- Token/session routes `main.py:470-676`; refresh cookie constant `main.py:452`
  (`REFRESH_COOKIE = "ielts_rt"`), setters `main.py:454-462`.
- Stored state: `accounts` (`password_hash`, `status`, `role`, `failed_login_count`, `locked_until`,
  `onboarding_completed`), `account_sessions` (`refresh_token_hash`, `expires_at`, `revoked_at`,
  `last_used_at`), `account_security_events` (event log).
- Frontend: `frontend/src/api/client.js` (token storage + 401-refresh-retry), `api/auth.js`
  (8 wrappers), `auth/AuthProvider.jsx` (React context), `auth/ProtectedRoute.jsx` (14 lines, three
  redirect rules).

## 15. Notable security observations (facts read from files, no values reproduced)

| # | Location | Observation |
| --- | --- | --- |
| S-1 | `auth_utils.py:8` | Signing key falls back to a **hardcoded literal** when `JWT_SECRET_KEY` is unset, so a deployment that forgets the env var still starts with a known key. |
| S-2 | `main.py:470-540`, `main.py:547-608`, `schemas.py` `AccountRegisterIn`/`AccountLoginIn` | Registration and login. Login has a lockout (≥5 failures → `status="locked"`, `locked_until` +15 min, auto-cleared once past). The input schemas are bare `email: str` / `password: str` — **no `EmailStr`, no length or strength constraint** on either endpoint. |
| S-3 | `main.py:454-462` | Refresh cookie is `httponly` + `samesite=lax` + `path=/api/auth` + 30-day `max_age`, but **no `secure` flag**, and CORS runs with `allow_credentials=True`. |
| S-4 | `main.py:210-217` | CORS allowlist comes from a comma-split env var with `allow_methods=["*"]`, `allow_headers=["*"]`, credentials enabled. |
| S-5 | `main.py:1498`, `1587`, `1877` | Three `/api/dev/*` endpoints — including a full data wipe — with **no authentication dependency and no environment gate**; they rely on the deployment never exposing port 8000 publicly. |
| S-6 | `main.py:2079` | `POST /api/collocation-collections` is **unauthenticated** and writes global master data (`code` uniqueness is the only check). |
| S-7 | `seed.py:909-940` | Boot-time seeding creates **two accounts with hardcoded email/password literals**, one of which is returned as the "main" account. No values reproduced here. |
| S-8 | `docker-compose.yml` | MySQL root/user passwords are **inline literals** in a tracked file, and the healthcheck embeds the root password on the command line. |
| S-9 | `main.py:485`, `seed.py:918`,`:933` | `Account.role` is written (`"user"`) but **never read**: `grep -rn "\\.role\\b|role==" main.py services.py seed.py` → no matches. There is no role/permission check anywhere. |
| S-10 | `services.py:235-240` | `get_active_player(db)` returns `db.query(Player).first()` — the **first player row in the database**, not the authenticated caller. Used by `main.py:1880` (unauthenticated dev route). |
| S-11 | `frontend/src/api/client.js:6-10` | Access token is kept in `localStorage` under key `ielts_access_token` (readable by any script on the origin). |
| S-12 | `schemas.py` `TokenOut` vs `main.py:539`,`:605`,`:648` | `TokenOut` declares `refresh_token: str \| None`, but all three token handlers return only `TokenOut(access_token=...)`; the refresh token is delivered **only** as the `ielts_rt` cookie, so that response field is always `null`. |
| S-13 | `main.py:612-650` | Refresh performs rotation (the stored hash is replaced) but **does not revoke the old token's reuse window**: a replayed pre-rotation cookie simply fails the hash lookup rather than triggering session revocation. No reuse-detection branch was read. |
