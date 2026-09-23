# 02 — Current system architecture (as-is)

Everything below is what the repository **is**, not what it should be. Line references are to the
working-tree state recorded in `README.md`. Anything not confirmable from a file that was opened is
marked `[UNRESOLVED]` and repeated in `03-unresolved.md`.

---

## 1. One-paragraph summary

A **three-container, single-tenant, offline-first-by-omission local application**. A React 18 SPA
served by the Vite dev server in a `node:20-alpine` container talks over plain HTTP + CORS to a
single FastAPI process (`uvicorn --reload`) in a `python:3.12-slim` container, which owns all logic
and all state in one MySQL 8.4 container. There is **no reverse proxy, no TLS, no cache, no message
broker, no queue, no background worker, no third-party service, and no realtime channel**. The
backend is one 2874-line module with 121 routes, a 3267-line domain module, a 2784-line idempotent
seeder that runs on every boot, and 72 SQLAlchemy tables managed by 31 Alembic revisions applied
automatically at process start. Authentication is a hand-rolled HS256 JWT (access, 1 h, in
`localStorage`) plus an opaque rotating refresh token (30 d, httpOnly cookie), enforced by an
explicit FastAPI dependency chain that **14 of the 121 routes do not use**.

---

## 2. Runtime topology

```
                    BROWSER (developer's machine)
                    ┌───────────────────────────────────────────────┐
                    │ SPA bundle served by Vite dev server          │
                    │  localStorage: ielts_access_token             │
                    │  cookie (path=/api/auth): ielts_rt            │
                    └───────────────┬───────────────────────────────┘
        GET :5173 / (HTML+ESM)      │   fetch  http://localhost:8000/api/*   (cross-origin, CORS)
                                    │   Authorization: Bearer <access JWT>
                                    │   Cookie: ielts_rt   (only on /api/auth/*)
                                    ▼
   docker compose default bridge network (no proxy, no TLS, no ingress controller)
   ┌──────────────────────┐        ┌───────────────────────────────────────────────┐
   │ frontend             │        │ backend                                       │
   │ node:20-alpine       │        │ python:3.12-slim                              │
   │ npm run dev → vite   │        │ uvicorn app.main:app --reload                 │
   │ :5173 published      │        │ :8000 published                               │
   │ mounts ./frontend/src│        │ mounts ./backend:/app  (shadows image COPY)   │
   └──────────────────────┘        │ mounts material/*.md + folders  (:ro)         │
                                   └───────────────────┬───────────────────────────┘
                                                       │ SQLAlchemy 2.0 + PyMySQL
                                                       │ mysql+pymysql://…@mysql:3306/ielts_quest
                                                       ▼
                                   ┌───────────────────────────────────────────────┐
                                   │ mysql  (image mysql:8.4)                      │
                                   │ :3306 in-network, published as host :3307     │
                                   │ volume mysql_data:/var/lib/mysql              │
                                   │ healthcheck: mysqladmin ping                  │
                                   └───────────────────────────────────────────────┘
```

Evidence: `docker-compose.yml:1-56` (services, ports, volumes, env keys, healthcheck, `depends_on:
condition: service_healthy`), `frontend/Dockerfile:1-14`, `backend/Dockerfile:1-16`,
`backend/app/database.py:11-19` (DSN, driver), `frontend/src/api/client.js:1` (API base URL),
`frontend/vite.config.js:1-13` (dev server host, **no `server.proxy`**).

### Layers present / absent

| Layer | Present? | Evidence |
| --- | --- | --- |
| Browser client | Yes — React 18 + Vite SPA, 4 route branches | `frontend/src/main.jsx:12-31` |
| Server-rendered UI | No | `frontend/index.html` is a bare `#root` shell |
| API service | Yes — 1 FastAPI process | `backend/app/main.py:208`, `docker-compose.yml:25` |
| Separate worker / cron | **No** | no Celery/RQ/APScheduler/`BackgroundTasks`; only `@app.on_event("startup")` `main.py:431` |
| Datastore | Yes — MySQL 8.4, 72 tables | `docker-compose.yml:2-20`, `backend/app/models.py` |
| Cache | **No** | no Redis/Memcached/in-process cache; engine has only `pool_pre_ping`/`pool_recycle` (`database.py:15-19`) |
| Message broker / queue | **No** | no Kafka/RabbitMQ/MQTT/Redis client anywhere |
| Realtime (WS/SSE) | **No** | see `01-discovery-inventory.md` §7 |
| Reverse proxy / API gateway | **No** | zero matches for nginx/traefik/caddy/`proxy_pass` |
| TLS termination | **No** | plain HTTP on all three published ports |
| External/third-party APIs | **No** | zero outbound HTTP client usage in `backend/app/` |
| Object storage / CDN | **No** | static assets live in the SPA bundle only |
| Container orchestration beyond compose | **No** | no k8s/helm manifests, no CI |

---

## 3. Service and network boundaries

- **Three services, one network, no proxy.** `frontend`, `backend` and `mysql` are separate
  containers on the compose default bridge network. Only `backend` and `mysql` need to talk to each
  other (service DNS name `mysql` inside `DATABASE_URL`, `docker-compose.yml:32`); `frontend`
  `depends_on: backend` (`docker-compose.yml:40-41`) but its `VITE_API_URL` is
  `http://localhost:8000/api`, i.e. the **browser**, not the container, is the client.
- **Boundary that matters:** the browser origin is `http://localhost:5173` while the API origin is
  `http://localhost:8000` — a genuine cross-origin boundary, which is why CORS is load-bearing here
  and why `credentials: 'include'` appears on all three browser fetch paths
  (`frontend/src/api/client.js:21, :44, :58`).
- **All three ports are published to the host** (`3307:3306`, `8000:8000`, `5173:5173`), so the
  trust boundary is "whoever can reach the host", not the container network. The `/api/dev/*`
  endpoints (§6) are reachable from that boundary with no credential.
- **Committed history shows at least one non-local deployment**: HEAD's `docker-compose.yml` pointed
  `VITE_API_URL` at a public IP and `CORS_ORIGINS` still lists that IP. How that host was
  provisioned, and whether it is still live, is not in the repository → U-01.
- **Volume topology is a dev-mode decision with architectural consequences:**
  `./backend:/app` shadows the image build, so in compose the running code is the host working tree
  with `--reload`; the markdown seeding sources are mounted read-only; `frontend/src` and
  `frontend/public` are mounted so the Vite dev server serves live edits
  (`docker-compose.yml:36-49`).

---

## 4. Request lifecycle (verified path)

1. **Bootstrap.** `AuthProvider` reads `localStorage['ielts_access_token']`; if absent it stops
   loading without calling the API (`frontend/src/auth/AuthProvider.jsx:15-27`,
   `frontend/src/api/client.js:3-6`).
2. **Gate.** `ProtectedRoute` returns `null` while loading, redirects to `/login` when not
   authenticated and to `/onboarding` when `onboarding_completed` is false
   (`frontend/src/auth/ProtectedRoute.jsx:5-13`). This is **client-side UX only**; it is not an
   authorization control.
3. **Shell mount.** `App` fires six loaders once (`frontend/src/App.jsx:169-176`). The vocabulary
   workspace is a separate `React.lazy` view (`frontend/src/App.jsx:33`, `currentView` switch at
   `:130`).
4. **Transport.** `apiFetch` (`frontend/src/api/client.js:33-83`) sets
   `Content-Type: application/json`, attaches `Authorization: Bearer <token>` when present, always
   sends `credentials: 'include'`, and on **HTTP 401** attempts exactly one silent refresh then one
   retry; if that fails it throws an error flagged `sessionExpired`, which `App.jsx:151-153` turns
   into `logout()` + navigate to `/login`.
5. **Edge.** `CORSMiddleware` (`backend/app/main.py:210-217`) admits the configured origins with
   credentials, all methods and all headers.
6. **Auth resolution.** The route's parameter list is the enforcement point:
   `get_current_account` → `get_current_player` → `get_current_campaign`
   (`backend/app/main.py:222-306`).
7. **Handler.** The route body runs ORM queries **inline** and additionally calls domain functions
   from `services.py` / `seed.py` imported at `main.py:157-206`. There is no service-interface
   boundary: e.g. badge/skill serialization helpers live in `main.py:330-400` while quest completion
   lives in `services.py:818`.
8. **Side effects on reads — the dominant cross-cutting behaviour.** `refresh_progress_state`
   (`backend/app/services.py:804-816`) calls `db.expire_all()`, recomputes quest statuses, weekly
   missions, per-skill progress, badges and player progress, then **commits**. It is invoked from
   **33 sites in `main.py`** — the startup hook (`main.py:438`) plus **32 route call sites**
   (`main.py:759, 766, 834, 858, 896, 908, 980, 1007, 1036, 1133, 1187, 1215, 1232, 1464, 1576,
   1859, 1917, 1927, 1937, 1947, 1956, 1964, 1973, 1999, 2033, 2042, 2053, 2062, 2169, 2186, 2205,
   2214`; derived by `grep -n 'refresh_progress_state(' app/main.py`), including plain reads such as
   `GET /api/summary` (`:766`) and `GET /api/skills` (`:908`). Roughly a quarter of all routes
   therefore write derived state, and there is no background job that could do it instead.
9. **Persistence.** One SQLAlchemy `Session` per request via `get_db`
   (`backend/app/database.py:41-46`), `autocommit=False`, commits performed inside handlers.
10. **Response shaping.** `response_model` is declared on **100 of the 121 routes**
    (`grep -c 'response_model=' app/main.py` → 100; `backend/app/schemas.py` holds 119 Pydantic
    classes), alongside hand-written serializer helpers (`serialize_quest` `main.py:311-353`,
    `serialize_skill_state` `main.py:356-376`) used by the routes that return unmodelled shapes.

---

## 5. Datastore architecture

- **Single MySQL 8.4 instance, single schema (`ielts_quest`), no replicas, no sharding, no second
  datastore.** `docker-compose.yml:2-20`, `backend/app/database.py:11-13`.
- **Schema ownership is shared three ways, which is worth flagging for later sections:**
  1. Alembic revisions — 31 files in `backend/alembic/versions/`, driven by `alembic/env.py` with
     `target_metadata = Base.metadata` (`env.py:13`) and `compare_type=True` (`env.py:24, 46`).
  2. `Base.metadata.create_all` as the **first-run** path (`database.py:52, 58`), followed by
     `command.stamp(alembic_cfg, "head")` (`database.py:59`) — the schema is created from the models
     and then *declared* to be at head.
  3. **Runtime seeding**, which is not schema but is persisted reference data: `seed_database`
     (`seed.py:2685+`) is called from the startup hook on every boot and from `POST /api/dev/reset`.
- **Migrations are applied by the application process, not by a deploy step**
  (`database.py:45-63` invoked from `main.py:435`). There is no separate migration job in compose,
  no migration CI, and the test suite bypasses Alembic entirely by calling `create_all`
  (`test_backend.py:27-33`).
- **Reference data is code-and-markdown driven.** Skills, badges, quest templates, weekly mission
  patterns, bosses, rank-exam pools, collocation levels/items and the vocabulary library are all
  generated deterministically from constants and parsers in `seed.py`, reading
  `material/material.md`, `material/collocation/English_Collocations_campaign1-3_3-6_polished.md`
  and `material/vocabularies/**/vocab.md` via `MATERIAL_PLAN_PATH` / `COLLOCATIONS_PATH` /
  `VOCABULARIES_PATH` with filesystem fallbacks (`seed.py:557-578`, `2061-2085`, `2543-2555`).
  Because seeding runs at startup, **the material files are runtime inputs, not just dev fixtures** —
  and in compose they are mounted read-only into the backend container
  (`docker-compose.yml:37-39`).
- **Table clusters (72 tables, `models.py`):** identity/session (6), learning profile + campaign
  config (8), skills/quests/templates (6), the XP & rank ledger (`campaign_skill_states`,
  `skill_xp_transactions`, `player_xp_transactions`, `rank_xp_thresholds`, three policy tables),
  badges, weekly missions, boss battles, test records, rank suggestions/history, certificates,
  rank exams (5), roadmap/study-plan/material (6), trackers (4), vocabulary (13), collocations (7),
  vocab library (7).
- **Ledger design worth noting for later sections:** XP is not a single number. `Player` keeps
  `total_xp`/`player_xp`/`player_level`/`player_rank`/`current_streak` (`models.py:123-143`), while
  per-skill XP lives in `campaign_skill_states` and is also journalled in
  `skill_xp_transactions` / `player_xp_transactions`. The curve is
  `xp(L) = round(19 * (L**1.6 - 1))` for L 1..60 (`services.py:74-77`), rank F→S from level
  (`services.py:131-141`). The frontend duplicates this curve (`frontend/src/dashboard-data.js:619`).
- **Multi-tenancy posture.** Tenancy keys exist (`accounts`, `players.account_id` nullable **unique**
  FKs — `models.py:146`; `campaigns`, `campaign_skill_states`, `badge_unlocks` all campaign-scoped).
  Account-scoped routes resolve the player from the token (`main.py:270-275`). But
  `services.get_active_player(db)` returns `db.query(Player).first()` (`services.py:235-240`), and
  `material_file_path()`-seeded player ownership is fixed at boot by `ensure_player`
  (`seed.py:943`). So isolation is **partial and incidental** rather than an enforced invariant →
  multi-user behaviour is U-03.

---

## 6. Where authentication sits

**Answer: entirely inside the FastAPI process, as a per-route dependency chain. There is no gateway,
no auth middleware, no identity provider, and no server-side session store.**

### 6.1 Credential mechanics
| Concern | Implementation | Evidence |
| --- | --- | --- |
| Password hashing | PBKDF2-HMAC-SHA256, 100 000 rounds, 16 random salt bytes, stored `pbkdf2_sha256$<rounds>$<salt>$<key>` | `auth_utils.py:59-74` |
| Access token | Hand-written HS256 JWT (`hmac`+`hashlib`+base64url), claims `sub`=account id, `iat`, `exp`; default TTL **3600 s** | `auth_utils.py:12-40`; issued at `main.py:542`, `:607`, `:648` |
| Signing key | `JWT_SECRET_KEY` env var with a **hardcoded fallback** | `auth_utils.py:8` |
| Refresh token | 32 random bytes, urlsafe-base64, **SHA-256 hash stored** in `account_sessions.refresh_token_hash`, 30-day expiry, rotated on every refresh | issued `main.py:523-524`, `:589-590`; rotated `:634-637` |
| Refresh transport | httpOnly cookie `ielts_rt`, `samesite=lax`, `path=/api/auth`, `max_age=30 d`, **no `secure`** | `main.py:452`, setter `:455-462`, clearer `:465-466` |
| Logout | Marks the session row `revoked_at` + `revoke_reason`, writes a security event, clears the cookie | `main.py:653-676` (event `:668-670`) |
| Brute force | `failed_login_count` ≥5 → `status="locked"` + `locked_until=now+15 min`, auto-cleared after expiry | `main.py:553-557`, `:562-565` |
| Audit trail | `account_security_events` rows for register / login_success / login_failed / refresh_token_used / logout | `main.py:533-535`, `:566-577`, `:599-601`, `:641-643`, `:668-670` |
| Client storage | Access token in `localStorage['ielts_access_token']`; refresh token never readable by JS | `frontend/src/api/client.js:3-15` |

### 6.2 Enforcement chain (`backend/app/main.py:222-306`)
- `get_current_account` — `HTTPBearer(auto_error=False)`; 401 if the header is missing; `decode_jwt`
  returns `None` on bad signature/expiry → 401; 401 if `sub` is absent; 401 if no `Account` row;
  **403 if `account.status != "active"`** (so a locked account is rejected).
- `get_current_player` — `Player` by `account_id`, else **404**.
- `get_current_campaign` / `get_optional_campaign` — delegates to
  `services.get_active_campaign` (`services.py:242-257`), 404 if none, or `None` for the optional
  variant.
- Routes opt in **by declaring these as parameters**. There is no router-level dependency, no
  middleware guard, and no global `dependencies=[...]` on `FastAPI(...)` (`main.py:208`).

### 6.3 Authorization
- **There is no authorization model.** `Account.role` is written as `"user"` at registration and
  seeding (`main.py:485`, `seed.py:918`,`:933`) and is **never read** anywhere
  (`grep -rn "\.role\b|role==" main.py services.py seed.py` → no matches). No scopes, no ownership
  checks beyond "does this row belong to the caller's campaign/player" filters written inline in
  each handler, no admin surface.
- **14 of 121 routes carry no auth dependency** (extracted by reading each decorator and its
  signature block): `/api/health` (`main.py:443`), `/api/auth/register|login|refresh|logout`
  (`:470`, `:547`, `:612`, `:653`), `/api/quest-templates` (`:912`), `/api/materials` and
  `/api/materials/{id}` (`:917`, `:922`), and the three `/api/dev/*` routes
  (`:1498`, `:1587`, `:1877`), plus `GET/POST /api/collocation-collections` and
  `GET /api/collocation-collections/{id}` (`:2074`, `:2079`, `:2087`).
  Consequences worth carrying into later sections: `POST /api/dev/reset` **wipes all 57 model
  tables and re-seeds with no credential of any kind** (`main.py:1498-1583`), and
  `POST /api/collocation-collections` lets an anonymous caller write global master data
  (`main.py:2079-2085`).
- **No defence in depth on the identity side either:** the JWT is a stored-value bearer token
  (`localStorage`, no `HttpOnly`), refresh tries are single-shot (`client.js:33-45`), and the
  refresh cookie's `lax`/no-`secure` combination assumes a plain-HTTP local origin.

### 6.4 What authentication does *not* cover
- The Vite dev server has no auth; anyone who can reach `:5173` gets the full SPA bundle (which
  contains no secrets, but does contain the API base URL and every route name).
- MySQL is published on host port 3307 with credentials that are inline in a tracked file
  (`docker-compose.yml:6-10`).
- There is no CORS restriction on which *methods* may be called, and credentials are allowed, so the
  origin allowlist is the only browser-side control (`main.py:210-217`).

---

## 7. Cross-cutting characteristics (as-is)

1. **Single-process, single-module backend.** All 121 routes are in `main.py`; there is no router
   package, no DI container, no service interface. Route handlers mix HTTP concerns, ORM queries and
   domain rules (`main.py:330-400` vs `services.py:818`).
2. **Recompute-on-read.** Progression state is derived lazily and committed during GETs: 32 route
   call sites invoke `refresh_progress_state` (`services.py:804-816`), including read-only handlers
   such as `main.py:766` and `:908`, so the same request can write.
3. **Self-healing startup.** Every boot runs wait → create/stamp/upgrade → seed → refresh
   (`main.py:431-441`), making the process responsible for schema *and* reference data, and making
   `material/*.md` a runtime dependency.
4. **Deterministic, idempotent seeders.** 52 seed functions use "ensure_*" naming and
   query-before-insert patterns (`seed.py`), so restarts converge rather than duplicate.
5. **No realtime, no push, no background work.** Freshness depends on the user acting; the SPA loads
   its six datasets exactly once per mount (`App.jsx:169-176`).
6. **Client-heavy derived state.** 31 pure builder functions in `dashboard-data.js` turn API payloads
   into view models, including a client reimplementation of rank/XP maths
   (`dashboard-data.js:461-645`).
7. **Dev-mode artifacts are committed** (`node_modules` ×1533, `dist/` ×9 assets, `__pycache__`
   ×35), and **no `.gitignore` exists**, so the repository cannot distinguish source from output.
8. **No quality gates.** No CI, no lint config, no type checking (plain JSX, plain Python without
   type checking config), one jest-less frontend test file, and a backend suite that cannot run
   without a Python environment the audit host does not have (U-04).
