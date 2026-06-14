# Tasks — NOT Executed (Superseded / Abandoned)

Plans that were designed but **deliberately not implemented**. Kept for historical
context only. Do NOT execute. Moved out of `TASKS.md` on 2026-06-13 to keep it clean.

---

# Implementation Plan: Production Readiness — Phase 1a (Security & Infrastructure Triage) (2026-06-11) — ⚠️ SUPERSEDED

> **SUPERSEDED 2026-06-11** by the Small-Group Tool plan ([`docs/current/SMALL_GROUP_PLAN.md`](docs/current/SMALL_GROUP_PLAN.md)).
> Owner dropped the public-SaaS direction the same day. Only a tiny P0 subset (gate dev endpoints,
> remove hardcoded JWT secret, basic per-account data scoping) survives — it is re-scoped in the
> Small-Group Tool plan. The 14-task PR-1..PR-14 breakdown below is **historical, do NOT execute**.

**Owner:** khanhpn308 · **Grilled + locked:** 2026-06-11 (19-question grill + 5 task-design questions) · **Type:** Backend security/config + minimal frontend (cookie auth) + DevOps (CI, Dockerfile, compose.prod)

> **Canonical references (read these first — they hold the decisions, this plan only executes them):**
> - Roadmap + Definition of Done: [`docs/current/PRODUCTION_ROADMAP.md`](docs/current/PRODUCTION_ROADMAP.md) — §2 (12 DoD criteria), §3 (must-fix table), §4 Phase 1 P1a list.
> - ADR-004 (auth: PyJWT + fail-fast secret + httpOnly cookie + CSRF), ADR-005 (Pydantic Settings + ENVIRONMENT flag), ADR-006 (migrations release step) in [`docs/current/decisions/`](docs/current/decisions/).

## Goal

Make the app **safe to run on a public host** without yet doing the multi-tenant rewrite (that is P1b). Close every "publish-as-is = disaster" hole: no weak/default secrets, no unauthenticated dev backdoors, access token not stealable via XSS, abuse-protected auth, migrations decoupled from app start, plus the CI + error-monitoring needed to operate it. **Multi-tenant data isolation, email verify/forgot-password, and multi-template onboarding are explicitly NOT in P1a — they are P1b.**

## Scope decisions locked in this grill (do exactly these — do NOT re-decide)

1. **CSRF mechanism:** use the **`fastapi-csrf-protect`** library (not hand-rolled double-submit, not SameSite-only).
2. **Cookie paths:** access-token cookie `path=/`; refresh-token cookie keeps `path=/api/auth`.
3. **Email infra:** NOT in P1a → P1b. Do not add SMTP/SendGrid/verify flows here.
4. **Sentry:** wire the SDK reading `SENTRY_DSN` from env; if DSN is empty, Sentry is a no-op (disabled). Owner creates the Sentry project + supplies DSN at deploy time. Do not block on a real DSN.
5. **Prod artifacts:** create `docker-compose.prod.yml` (no `--reload`, no source volume mounts, DB port not published) AND a production `CMD` in the Dockerfile (no `--reload`).
6. **`ENVIRONMENT` flag** (`development` | `production`) is the central switch for: dev-endpoint registration, fail-fast strictness, cookie `Secure`, and whether `on_startup` migrates/seeds.

## Context — exact current state (READ BEFORE EDITING; file:line verified 2026-06-11)

- **Config is hardcoded / scattered `os.getenv`:**
  - `backend/app/auth_utils.py:8` — `SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-prod-123456789")` (weak fallback).
  - `backend/app/database.py:11-14` — `DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://ielts_user:ielts_password@mysql:3306/ielts_quest")` (default creds).
  - `backend/app/main.py:212` — `origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")`; middleware at `main.py:213-218`.
  - `docker-compose.yml:7-10` (MySQL creds inline), `:25` (`--reload`), `:28` (`APP_START_DATE`), `:30` (CORS hardcodes old EC2 IP `18.141.232.235`), `:38-41` (backend volume mounts), `:48` (`VITE_API_URL` hardcodes the old IP).
- **JWT is hand-rolled** with `hmac` in `backend/app/auth_utils.py:17-55` (`create_jwt`, `decode_jwt`). Callers: `main.py:12` imports them; `create_jwt` used at `main.py:554, 619, 660`; `decode_jwt` used in `get_current_account` at `main.py:234`. `requirements.txt` has **no** PyJWT.
- **Auth cookie/token wiring:**
  - `backend/app/api access` — frontend stores the access token in `localStorage` (`frontend/src/api/client.js:3` `TOKEN_KEY`, `:5-15` get/set/clear, `:33-83` `apiFetch` sends `Authorization: Bearer`). `attemptRefresh` at `client.js:17-31`.
  - Backend reads the Bearer via `HTTPBearer` + `get_current_account` (`main.py:221, 224-257`).
  - Refresh cookie helpers: `set_refresh_cookie` / `clear_refresh_cookie` (`main.py:464-479`), `httponly=True, samesite="lax", path="/api/auth"`. Tokens returned in body as `TokenOut(access_token=...)` at `main.py:554-556, 619-621, 660-662`.
- **Dev endpoints (unauthenticated except test-xp):**
  - `POST /api/dev/reset` (`main.py:1510`), `POST /api/dev/run_migrations` (`main.py:1599`), `POST /api/dev/regenerate-quests` (`main.py:1959`) — **no auth**.
  - `/api/dev/test-xp/*` (`main.py:1612, 1640`) — gated by `require_test_account` (`main.py:264-267`) checking the hardcoded email `TEST_ACCOUNT_EMAIL = "ad00000@gmail.com"` (`main.py:261`).
- **Seed account hardcoded:** `seed.py:925-929` creates `ad00000@gmail.com` every seed via `ensure_account_and_profile`.
- **Migrations + seed run at startup:** `on_startup` (`main.py:443-452`) → `run_database_bootstrap()` (`database.py:49-67`, which runs `command.upgrade(head)`) then `seed_database(db, parse_start_date())` + `refresh_progress_state(db)` **every container start**.
- **Rate limiting:** only login lockout (5 fails → 15-min lock) at `main.py:564-594`. No global limiter. `requirements.txt` has no `slowapi`.
- **Tests:** `backend/app/test_backend.py` — 68 tests (auth suite `TestAuthEndpoints` at `:495-742`; they assert `data["access_token"]` in the response body and `"ielts_rt"` in `response.cookies` — these assertions WILL change when access token moves to a cookie). Frontend: 1 test (`npm run test:dashboard-data`). No CI workflow (`.github/` absent).
- **Health:** `GET /api/health` exists (`main.py:455-457`). Only MySQL has a Docker healthcheck (`docker-compose.yml:15-19`); backend has none.
- **Versions (pin compatibly):** FastAPI 0.115.6, Pydantic 2.10.3, SQLAlchemy 2.0.36, uvicorn 0.32.1, Python 3.12 (`requirements.txt`, `backend/Dockerfile`). Frontend: React 18.3, Vite 5.4 (`frontend/package.json`).

## Architecture Decisions (for this plan)

- **One `Settings` object is the only config reader.** Every `os.getenv` in `auth_utils.py`, `database.py`, `main.py` migrates to `from .config import settings`. Rationale: ADR-005; required vars fail loudly.
- **`ENVIRONMENT` gates behavior, not separate code paths where avoidable.** Dev endpoints are registered behind an `if settings.is_dev` guard; fail-fast runs in a validator that only hard-errors in production. Rationale: keep dev ergonomics, production safety.
- **Access token in httpOnly cookie; keep returning it in the body too during transition is NOT done** — body stops carrying it, frontend stops reading localStorage. Rationale: ADR-004; half-measures leave the XSS hole open.
- **Migrations move OUT of `on_startup` for production.** A `scripts/migrate.py` / `alembic upgrade head` release step runs once; `on_startup` only migrates/seeds when `settings.is_dev`. Rationale: ADR-006.

## Dependency graph (implementation order)

```
PR-1 (Settings/config)  ← foundation, everything imports it
   ├── PR-2 (fail-fast secret + sweep defaults)
   ├── PR-3 (PyJWT swap)
   ├── PR-4 (gate dev endpoints by ENV)
   ├── PR-5 (no hardcoded seed in prod)
   ├── PR-6 (CORS from settings)
   ├── PR-7 (BE: access token → httpOnly cookie) ──┬── PR-8 (FE: drop localStorage, cookie auth)
   │                                                └── PR-9 (CSRF via fastapi-csrf-protect)
   ├── PR-10 (global rate limit slowapi)
   ├── PR-11 (migrations out of startup + release step)
   ├── PR-12 (fix auth tests for cookie change)  ← depends on PR-7/8/9
   ├── PR-13 (GitHub Actions CI)                  ← depends on PR-12 (tests must be green)
   └── PR-14 (Sentry BE+FE + backend healthcheck + compose.prod/Dockerfile prod)
```

## Task List

### Slice 1 — Central config (foundation)

- [ ] **Task PR-1: Add a Pydantic `Settings` class as the single config source.** *(M, backend)*
  - **Description:** Create `backend/app/config.py` with a `pydantic-settings` `BaseSettings` subclass named `Settings` exposing every config value the app needs, loaded from env (and `.env` in dev). Instantiate a module-level `settings = Settings()`. Add a `.env.example` at repo root listing every key with placeholder (no real) values. Add `pydantic-settings` to `requirements.txt`.
  - **Reference (read before coding):** current scattered readers at `auth_utils.py:8`, `database.py:11-14`, `main.py:212`, and the env vars set in `docker-compose.yml:26-31, 47-49`. ADR-005 in `docs/current/decisions/ADR-005-config-pydantic-settings-environment-flag.md`.
  - **Fields to expose (exact names — agent must not invent others):**
    - `environment: str` (default `"development"`; allowed `development|production`) + a `is_dev`/`is_prod` property.
    - `jwt_secret_key: str` (NO default — required).
    - `database_url: str` (keep the current dev default ONLY when `environment=development`; see PR-2 for prod enforcement).
    - `cors_origins: str` (comma-separated; default `"http://localhost:5173"`) + a `cors_origins_list` property that splits/strips.
    - `app_start_date: str | None` (default `None`).
    - `sentry_dsn: str | None` (default `None`).
    - `cookie_secure: bool` (default derived: `True` when prod else `False`).
    - `csrf_secret_key: str | None` (required in prod; used by PR-9).
  - **Acceptance criteria:**
    - [ ] `from app.config import settings` works; `settings.environment` reads `ENVIRONMENT` env (default `development`).
    - [ ] `settings.cors_origins_list` returns a stripped list.
    - [ ] `requirements.txt` includes `pydantic-settings` (pin a 2.x compatible with pydantic 2.10.3).
    - [ ] `.env.example` lists: `ENVIRONMENT, JWT_SECRET_KEY, CSRF_SECRET_KEY, DATABASE_URL, CORS_ORIGINS, APP_START_DATE, SENTRY_DSN` (placeholders only, no secrets).
  - **Verification:** `python -c "from app.config import settings; print(settings.environment)"` inside the backend container prints `development`; `pip install -r requirements.txt` succeeds.
  - **Dependencies:** None.
  - **Files:** `backend/app/config.py` (new), `backend/requirements.txt`, `.env.example` (new).
  - **Estimated scope:** Medium (2-3 files).
  - **Gap check:** [ ]

### Slice 2 — Secrets fail-fast + JWT library

- [ ] **Task PR-2: Fail-fast on missing secrets in production; remove weak defaults.** *(S, backend)*
  - **Description:** In `Settings` (PR-1), make the app **refuse to start in production** if `jwt_secret_key`, `csrf_secret_key`, or a non-default `database_url` is missing. Implement a `model_validator` (or `__post_init__`-style check) that raises a clear `RuntimeError` listing the missing/weak vars **only when `environment=production`**. In `development`, allow the existing dev defaults so local dev keeps working. Remove the hardcoded fallback string at `auth_utils.py:8` (it now reads `settings.jwt_secret_key`). Remove the default-creds fallback at `database.py:11-14` for production (keep dev default behind the env check).
  - **Reference:** `auth_utils.py:8`, `database.py:11-14`. DoD #2 + must-fix #2 in roadmap. Verification example in roadmap §7.
  - **Acceptance criteria:**
    - [ ] With `ENVIRONMENT=production` and no `JWT_SECRET_KEY`, the app raises at import/startup with a message naming the missing var (does NOT silently use a default).
    - [ ] With `ENVIRONMENT=development` and no env set, the app still boots using dev defaults (local dev unbroken).
    - [ ] No occurrence of the string `super-secret-key-change-in-prod` remains in the repo (grep clean).
    - [ ] `auth_utils.py` and `database.py` read from `settings`, not `os.getenv` directly.
  - **Verification:** `ENVIRONMENT=production python -c "import app.main"` → fails with the clear error; unset → dev boots. `grep -r "super-secret-key" backend/` returns nothing.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/config.py`, `backend/app/auth_utils.py`, `backend/app/database.py`.
  - **Estimated scope:** Small (3 files).
  - **Gap check:** [ ]

- [ ] **Task PR-3: Replace hand-rolled JWT with PyJWT.** *(M, backend)*
  - **Description:** Rewrite `create_jwt` / `decode_jwt` in `auth_utils.py:17-55` to use the `PyJWT` library (HS256), reading the secret from `settings.jwt_secret_key`. Keep the **same function signatures and return shapes** so callers in `main.py` (`create_jwt({"sub": str(account.id)})` at `:554,619,660`; `decode_jwt(token)` at `:234`) need no change. Preserve behavior: `decode_jwt` returns the payload dict on success or `None` on any failure (invalid signature / expired / malformed) — PyJWT raises, so catch `jwt.PyJWTError` and return `None`. Keep `exp` = 1h and `iat`. Add `PyJWT` to `requirements.txt`.
  - **Reference:** `auth_utils.py:17-55` (current impl), callers at `main.py:234,554,619,660`. `get_current_account` at `main.py:224-257`. ADR-004.
  - **Acceptance criteria:**
    - [ ] `create_jwt({"sub":"5"})` returns a token that `decode_jwt(...)` decodes back to a payload with `sub=="5"`, plus `exp`/`iat`.
    - [ ] `decode_jwt` of a tampered/expired/garbage token returns `None` (never raises out).
    - [ ] No caller signature changed; `main.py` imports unchanged (`from .auth_utils import ... create_jwt, decode_jwt`).
    - [ ] `requirements.txt` includes `PyJWT` (2.x); `hmac`/manual base64 JWT code removed.
  - **Verification:** existing `TestAuthEndpoints` still drive login/refresh/me; add/adjust a unit asserting round-trip + `None` on tamper. Suite green after PR-12.
  - **Dependencies:** PR-1, PR-2.
  - **Files:** `backend/app/auth_utils.py`, `backend/requirements.txt`.
  - **Estimated scope:** Medium (2 files, but auth-critical).
  - **Gap check:** [ ]

### Checkpoint 1 (after PR-1..PR-3)
- [ ] Backend boots in dev unchanged; `ENVIRONMENT=production` without secrets fails fast with a clear message; JWT round-trips via PyJWT; no weak-secret string in repo.

### Slice 3 — Close the dev backdoors

- [ ] **Task PR-4: Gate all `/api/dev/*` routes behind `ENVIRONMENT`.** *(S, backend)*
  - **Description:** Ensure `/api/dev/reset` (`main.py:1510`), `/api/dev/run_migrations` (`main.py:1599`), `/api/dev/regenerate-quests` (`main.py:1959`), and `/api/dev/test-xp/*` (`main.py:1612,1640`) are **not reachable in production** (return 404 / not registered). Preferred mechanism: wrap their registration in `if settings.is_dev:` so they are not added to the app at all in production (cleaner than a per-route guard). If wrapping `@app.post` decorators is awkward given file structure, instead add a dependency that raises `HTTPException(404)` when `settings.is_prod` to every dev route. Pick ONE mechanism and apply consistently.
  - **Reference:** dev routes at `main.py:1510, 1599, 1959, 1612, 1640`; `require_test_account` at `main.py:264-267`. DoD #5, must-fix #3.
  - **Acceptance criteria:**
    - [ ] With `ENVIRONMENT=production`, `POST /api/dev/reset` returns 404.
    - [ ] With `ENVIRONMENT=development`, all dev routes still work as today.
    - [ ] The mechanism is uniform across all 5 dev routes (no route left ungated).
  - **Verification:** `TestClient` with `settings.environment` monkeypatched to `production` → `/api/dev/reset` → 404; dev → 200/expected. Add a test `test_dev_routes_404_in_production`.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/main.py`, `backend/app/test_backend.py`.
  - **Estimated scope:** Small (2 files).
  - **Gap check:** [ ]

- [ ] **Task PR-5: Do not create the hardcoded seed account in production.** *(S, backend)*
  - **Description:** In `seed.py`, the seed creates `ad00000@gmail.com` via `ensure_account_and_profile` (`seed.py:925-929`, called from `seed_database` at `seed.py:2703`). Guard the hardcoded-account creation so it only runs in development (`if settings.is_dev`). The rest of the seed (skills, badges, templates, etc.) may still run in dev; in production the whole `seed_database` is skipped by PR-11 anyway, but this guard is a defense-in-depth so even a manual dev-seed call in a prod DB won't mint the known account.
  - **Reference:** `seed.py:925-929`, `ensure_account_and_profile`; `seed_database` at `seed.py:2694-2720`. DoD #5.
  - **Acceptance criteria:**
    - [ ] In production, no `ad00000@gmail.com` account is created by any seed path.
    - [ ] In development, the seed account still exists (dev workflows unbroken).
  - **Verification:** call `ensure_account_and_profile` (or `seed_database`) with `settings.environment="production"` → query Account for `ad00000@gmail.com` → none. Dev → present.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/seed.py`.
  - **Estimated scope:** Small (1 file).
  - **Gap check:** [ ]

- [ ] **Task PR-6: Build CORS allow-list from `settings`, drop the hardcoded IP.** *(XS, backend)*
  - **Description:** Replace `origins = os.getenv("CORS_ORIGINS", ...)` at `main.py:212` with `settings.cors_origins_list`. Remove the old EC2 IP from any default. Production sets real domains via the `CORS_ORIGINS` env. Keep `allow_credentials=True` (required for cookie auth).
  - **Reference:** `main.py:212-218`; `docker-compose.yml:30` (old IP to drop). DoD #6.
  - **Acceptance criteria:**
    - [ ] CORS middleware reads `settings.cors_origins_list`.
    - [ ] No `18.141.232.235` remains anywhere in the repo (grep clean).
    - [ ] `allow_credentials=True` preserved.
  - **Verification:** start with `CORS_ORIGINS="https://example.com"` → preflight from that origin allowed; `grep -r "18.141.232.235"` empty.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/main.py`, `docker-compose.yml`.
  - **Estimated scope:** XS (2 files, small edits).
  - **Gap check:** [ ]

### Checkpoint 2 (after PR-4..PR-6)
- [ ] `ENVIRONMENT=production`: dev routes 404, no hardcoded seed account, CORS from env only, old IP gone. Dev unchanged.

### Slice 4 — Access token → httpOnly cookie + CSRF

- [ ] **Task PR-7: Backend — issue access token as an httpOnly cookie; read it in `get_current_account`.** *(M, backend)*
  - **Description:** Add `set_access_cookie(response, token)` / `clear_access_cookie(response)` mirroring the refresh helpers (`main.py:464-479`) but with cookie name `ielts_at`, `httponly=True`, `samesite="lax"`, `secure=settings.cookie_secure`, **`path="/"`** (locked decision), `max_age=3600`. In `register`/`login`/`refresh` (`main.py:554-556, 619-621, 660-662`) call `set_access_cookie` in addition to (then **instead of**) putting it in the body — final state: body no longer returns `access_token` (return `{"detail":"ok"}` or keep `TokenOut` with token omitted/None per FE contract in PR-8). In `logout` (`main.py:665-687`) also clear the access cookie. Update `get_current_account` (`main.py:224-257`) to read the token from the `ielts_at` cookie (via `Cookie(default=None)`) **instead of** `HTTPBearer`; drop the `HTTPBearer` dependency (`main.py:221,225`). Apply the same `secure=settings.cookie_secure` to the existing refresh cookie (`set_refresh_cookie` at `main.py:467-475`).
  - **Reference:** cookie helpers `main.py:464-479`; auth endpoints `main.py:482-687`; `get_current_account` `main.py:221-257`; `security = HTTPBearer(...)` `main.py:221`. ADR-004. Locked: access cookie `path=/`, refresh stays `path=/api/auth`.
  - **Acceptance criteria:**
    - [ ] After login, the response sets an `ielts_at` httpOnly cookie (`path=/`, `secure` per env) and the body no longer contains a usable `access_token`.
    - [ ] `get_current_account` authenticates from the `ielts_at` cookie; a request with no cookie → 401.
    - [ ] `HTTPBearer` removed; no route still expects an `Authorization` header.
    - [ ] Refresh + logout set/clear the access cookie; refresh cookie now also `secure=settings.cookie_secure`, still `path=/api/auth`.
  - **Verification:** `TestClient` login → assert `"ielts_at"` in `response.cookies`; subsequent `client.get("/api/auth/me")` (cookie jar carries it) → 200. Covered by PR-12 test updates.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/main.py`.
  - **Estimated scope:** Medium (1 file, many call sites).
  - **Gap check:** [ ]

- [ ] **Task PR-8: Frontend — stop using localStorage; rely on the cookie.** *(M, frontend)*
  - **Description:** In `frontend/src/api/client.js`: remove `TOKEN_KEY`/`getToken`/`setTokens`/`clearTokens` localStorage logic (`:3-15`); `apiFetch` (`:33-83`) stops adding the `Authorization` header (the browser sends the `ielts_at` cookie automatically since `credentials:'include'` is already set at `:44`). `attemptRefresh` (`:17-31`) already uses `credentials:'include'` — keep it, but it no longer calls `setTokens` (`:26`). Update any caller that read the returned `access_token` (e.g. `AuthProvider.jsx`, `Login.jsx`, `Register.jsx` — grep `access_token`, `setTokens`, `getToken`) to drop that usage; auth state becomes "did `/auth/me` succeed" rather than "is there a token in localStorage". Add the CSRF header per PR-9.
  - **Reference:** `frontend/src/api/client.js:1-83`; `frontend/src/auth/AuthProvider.jsx`; `frontend/src/pages/Login.jsx`, `Register.jsx`. ADR-004.
  - **Acceptance criteria:**
    - [ ] No reference to `localStorage` for the access token remains in `frontend/src/` (grep clean).
    - [ ] `apiFetch` sends no `Authorization` header; relies on the cookie.
    - [ ] After login, `localStorage` contains no token (verify in DevTools per roadmap §7).
    - [ ] App still loads the dashboard after login (auth gate driven by `/auth/me`).
  - **Verification:** `npm run build` green; manual: login → DevTools → Application → Local Storage empty of token → dashboard loads. `grep -rn "localStorage" frontend/src` shows no token usage.
  - **Dependencies:** PR-7.
  - **Files:** `frontend/src/api/client.js`, `frontend/src/auth/AuthProvider.jsx`, `frontend/src/pages/Login.jsx`, `frontend/src/pages/Register.jsx` (only where token usage exists — grep to confirm scope).
  - **Estimated scope:** Medium (3-5 files).
  - **Gap check:** [ ]

- [ ] **Task PR-9: Add CSRF protection via `fastapi-csrf-protect`.** *(M, backend + frontend)*
  - **Description:** Add `fastapi-csrf-protect` to `requirements.txt`. Configure it reading `settings.csrf_secret_key`. Issue a CSRF token to the client (a readable cookie, e.g. `csrf_token`, NOT httpOnly, set on login/refresh and/or a `GET /api/auth/csrf` endpoint). Require a matching `X-CSRF-Token` header on all **state-changing** requests (POST/PUT/PATCH/DELETE) — protect at least the auth + mutation routes. On the frontend, `apiFetch` reads the `csrf_token` cookie and adds the `X-CSRF-Token` header for non-GET requests. Follow the library's documented FastAPI pattern (load config via `@CsrfProtect.load_config`, validate with `csrf_protect.validate_csrf(request)`).
  - **Reference:** library docs (fastapi-csrf-protect); auth routes `main.py:482-687`; `apiFetch` `client.js:33-83`. ADR-004 (CSRF is the easy-to-get-wrong part — follow the lib).
  - **Acceptance criteria:**
    - [ ] A non-GET request without a valid `X-CSRF-Token` is rejected (403).
    - [ ] The frontend automatically attaches the token from the `csrf_token` cookie on mutations; normal app flows still work.
    - [ ] GET requests are not blocked by CSRF.
    - [ ] `csrf_secret_key` is required in production (ties to PR-2).
  - **Verification:** `TestClient` POST without the header → 403; with the issued token → succeeds. Manual: login + complete a quest still works (FE attaches header).
  - **Dependencies:** PR-7, PR-8.
  - **Files:** `backend/app/main.py`, `backend/requirements.txt`, `frontend/src/api/client.js`.
  - **Estimated scope:** Medium (3 files).
  - **Gap check:** [ ]

### Checkpoint 3 (after PR-7..PR-9)
- [ ] Access token is an httpOnly cookie (`path=/`), gone from localStorage; CSRF rejects forged mutations; login→dashboard→quest-claim works end-to-end in the browser.

### Slice 5 — Abuse protection

- [ ] **Task PR-10: Global rate limiting via `slowapi` (strict on auth).** *(M, backend)*
  - **Description:** Add `slowapi` to `requirements.txt`. Wire a `Limiter` (key by client IP) into the app, register its exception handler, and apply limits: **strict** on `POST /api/auth/register` and (when added in P1b) forgot-password — these trigger email/cost; **moderate** on `POST /api/auth/login` and `/api/auth/refresh`; a **loose** default for the rest. Keep the existing login lockout (`main.py:564-594`) — rate limit is an additional outer layer. Make limit values read from settings or sane constants (e.g. register: 5/hour/IP; login: 10/min/IP; default: 120/min/IP) — pick values in this band and note them.
  - **Reference:** existing login lockout `main.py:564-594`; auth routes `main.py:482-687`; `app = FastAPI(...)` `main.py:210`. DoD #6, must-fix #6. slowapi docs.
  - **Acceptance criteria:**
    - [ ] Exceeding the register limit from one IP returns 429.
    - [ ] Login/refresh have their own (looser) limits; normal use is not throttled.
    - [ ] The existing 5-fail login lockout still works (both layers coexist).
    - [ ] A default limit applies app-wide.
  - **Verification:** loop `POST /api/auth/register` past the threshold in a test → 429; a single normal login → 200.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/main.py`, `backend/requirements.txt`.
  - **Estimated scope:** Medium (2 files).
  - **Gap check:** [ ]

### Slice 6 — Migrations decoupled from startup

- [ ] **Task PR-11: Run migrations as a release step; don't migrate/seed on startup in production.** *(M, backend + DevOps)*
  - **Description:** Change `on_startup` (`main.py:443-452`) so `run_database_bootstrap()` + `seed_database()` + `refresh_progress_state()` run **only when `settings.is_dev`**. For production, add `backend/scripts/migrate.py` (or document the command) that runs `alembic upgrade head` once as a release/pre-deploy step. Keep `wait_for_database()` on startup in all envs. Ensure the PaaS/`compose.prod` (PR-14) invokes the migrate step before the app serves.
  - **Reference:** `on_startup` `main.py:443-452`; `run_database_bootstrap` `database.py:49-67`; `seed_database` `seed.py:2694`. ADR-006.
  - **Acceptance criteria:**
    - [ ] In production, app startup does NOT auto-run `seed_database` or auto-`upgrade` (no migration race with multiple instances).
    - [ ] A release command (`alembic upgrade head` / `scripts/migrate.py`) brings a fresh prod DB to head.
    - [ ] In development, startup still migrates + seeds (current behavior preserved).
    - [ ] `wait_for_database()` still runs in both envs.
  - **Verification:** with `ENVIRONMENT=production`, boot against an already-migrated DB → no seed rows added, app serves; run the migrate script on an empty DB → schema at head.
  - **Dependencies:** PR-1.
  - **Files:** `backend/app/main.py`, `backend/scripts/migrate.py` (new).
  - **Estimated scope:** Medium (2 files).
  - **Gap check:** [ ]

### Checkpoint 4 (after PR-10..PR-11)
- [ ] Auth endpoints rate-limited; production startup is migration/seed-free; release migrate step verified on an empty DB.

### Slice 7 — Tests green + CI

- [ ] **Task PR-12: Update the auth test suite for cookie-based tokens + CSRF.** *(M, backend)*
  - **Description:** The 68-test suite (`test_backend.py`) asserts `data["access_token"]` in the body and reads it as a Bearer header (`TestAuthEndpoints` `:495-742`, e.g. `:537,592,718-724`). Rewrite these to: assert the `ielts_at` cookie is set, drive authenticated requests via the `TestClient` cookie jar (not an `Authorization` header), and attach the CSRF header on mutations. Add the new tests referenced above: `test_dev_routes_404_in_production` (PR-4), JWT round-trip/tamper (PR-3), register rate-limit 429 (PR-10), CSRF-missing 403 (PR-9). Keep every other (non-auth) test passing.
  - **Reference:** `test_backend.py` `TestAuthEndpoints:495-742`, `TestOnboardingEndpoints:745+` (also obtains tokens at `:781-785`). PR-3/4/7/8/9/10 acceptance criteria.
  - **Acceptance criteria:**
    - [ ] Full backend suite green (68 existing adjusted + the new ones).
    - [ ] No test still asserts a usable `access_token` in the response body.
    - [ ] New tests for: dev-route 404 in prod, JWT round-trip+tamper, register 429, CSRF 403.
  - **Verification:** run the backend test suite (e.g. `python -m pytest` / the project's runner) → all green.
  - **Dependencies:** PR-3, PR-4, PR-7, PR-8, PR-9, PR-10.
  - **Files:** `backend/app/test_backend.py`.
  - **Estimated scope:** Medium (1 file, many edits).
  - **Gap check:** [ ]

- [ ] **Task PR-13: GitHub Actions CI — run backend + frontend tests + lint on every PR.** *(S, DevOps)*
  - **Description:** Add `.github/workflows/ci.yml` that, on push/PR to `main`: sets up Python 3.12, installs `backend/requirements.txt`, runs the backend test suite (with a throwaway SQLite/MySQL service as the existing tests use in-memory SQLite — confirm from `test_backend.py:497-506`); sets up Node, runs `npm ci` + `npm run build` + `npm run test:dashboard-data` in `frontend/`. Fail the job on any test/build failure. (No deploy step — PaaS auto-deploys from `main`.)
  - **Reference:** `test_backend.py:495-526` (in-memory SQLite + `StaticPool`, no external DB needed); `frontend/package.json` scripts (`build`, `test:dashboard-data`). DoD #7, roadmap CI decision (CI test-only + PaaS auto-deploy).
  - **Acceptance criteria:**
    - [ ] `ci.yml` runs backend tests + `npm run build` + the frontend test on PRs to `main`.
    - [ ] The workflow is green on the current code (after PR-12).
    - [ ] A failing test fails the workflow.
  - **Verification:** open a PR (or push) → Actions runs → green; intentionally break a test locally → workflow would fail.
  - **Dependencies:** PR-12 (tests must pass first).
  - **Files:** `.github/workflows/ci.yml` (new).
  - **Estimated scope:** Small (1 file).
  - **Gap check:** [ ]

### Slice 8 — Observability + production artifacts

- [ ] **Task PR-14: Sentry (BE+FE) + backend healthcheck + `compose.prod.yml` + prod Dockerfile CMD.** *(M, backend + frontend + DevOps)*
  - **Description:** Four production-readiness pieces:
    1. **Sentry backend:** add `sentry-sdk[fastapi]` to `requirements.txt`; init it in `main.py` only when `settings.sentry_dsn` is set (no-op when empty). 
    2. **Sentry frontend:** add `@sentry/react` to `frontend/package.json`; init reading `import.meta.env.VITE_SENTRY_DSN`, no-op when empty.
    3. **Backend healthcheck:** add a Docker `healthcheck` for the backend service (curl/wget `GET /api/health`, which exists at `main.py:455-457`) so the PaaS/compose can restart-on-unhealthy.
    4. **Production artifacts:** create `docker-compose.prod.yml` — backend `CMD` WITHOUT `--reload`, NO source volume mounts (`./backend:/app`, `./frontend/src` removed), MySQL port NOT published, envs come from real env/secrets (no inline creds). Update `backend/Dockerfile` so its default `CMD` (currently `--reload` at `Dockerfile:14`) is production-safe (no `--reload`); dev `--reload` lives in the dev `docker-compose.yml` command override.
  - **Reference:** `GET /api/health` `main.py:455-457`; `docker-compose.yml:1-62` (dev — keep as dev); `backend/Dockerfile:14` (`--reload` CMD to fix); `frontend/package.json`. DoD #8, #9. ADR-003. Sentry "wire + env DSN" decision (no real DSN required).
  - **Acceptance criteria:**
    - [ ] With `SENTRY_DSN` set, a deliberately-thrown backend error is reported to Sentry; with it empty, Sentry is disabled and the app runs normally.
    - [ ] Frontend Sentry inits only when `VITE_SENTRY_DSN` is set.
    - [ ] The backend service has a Docker healthcheck hitting `/api/health`.
    - [ ] `docker-compose.prod.yml` exists: no `--reload`, no source mounts, DB port unpublished, creds from env.
    - [ ] `backend/Dockerfile` default `CMD` has no `--reload`; dev reload is set via the dev compose `command` override.
  - **Verification:** `docker compose -f docker-compose.prod.yml config` validates; boot prod compose → backend healthy via healthcheck; throw a test error with a dummy DSN → appears in Sentry (or, DSN empty → no crash, app fine). `npm run build` green with `@sentry/react`.
  - **Dependencies:** PR-1 (settings/env). Independent of the auth slice; can run in parallel with PR-7..PR-12 if desired.
  - **Files:** `backend/app/main.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/src/main.jsx` (Sentry init — confirm entry file), `docker-compose.prod.yml` (new), `backend/Dockerfile`, `docker-compose.yml` (move `--reload` to dev command override).
  - **Estimated scope:** Medium (5+ files — if it feels Large, split Sentry from compose into two sessions).
  - **Gap check:** [ ]

### Checkpoint 5 — P1a complete (after PR-12..PR-14)
- [ ] Backend + frontend test suites green in CI on `main`.
- [ ] Production-mode smoke (roadmap §7): no weak secret (fails fast), `/api/dev/reset`→404, access token cookie-only (not in localStorage), CSRF rejects forged POST, register rate-limited, startup migration/seed-free, Sentry wired, backend healthcheck live, `compose.prod` validates.
- [ ] **DoD criteria satisfied by P1a:** #2 (no weak secrets), #4 (safe tokens), #5 (no backdoor), #6 (abuse protection), #7 (CI green), #8 (observable), partial #9 (deploy artifacts + migration release step; HTTPS/domain/backup are deploy-time on the PaaS). **Remaining for P1b:** #1 (isolation), #3 (email auth), #10 (multi-template), #11 (page speed), #12 (a11y).
- [ ] Review with owner before starting P1b.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Moving access token to a cookie silently breaks every authenticated FE call | High | PR-7 + PR-8 are paired; PR-12 rewrites the auth tests; Checkpoint 3 requires a full browser login→quest-claim. |
| CSRF wired wrong → either everything 403s or nothing is protected | High | Locked to `fastapi-csrf-protect` (don't hand-roll); PR-9 acceptance tests both the reject (no token→403) and the allow (with token→pass) paths. |
| Fail-fast secret breaks local dev | Med | PR-2 only hard-errors when `ENVIRONMENT=production`; dev keeps defaults. Acceptance criterion checks dev still boots. |
| Gating dev routes leaves one route ungated | Med | PR-4 mandates ONE uniform mechanism across all 5 dev routes + a `test_dev_routes_404_in_production`. |
| 68 existing tests assume body token / Bearer header | High | PR-12 is a dedicated task with the suite-green acceptance criterion; PR-13 (CI) depends on PR-12. |
| Sentry/PaaS specifics unknown at build time | Low | Sentry no-ops without a DSN; compose.prod validated with `config`; real DSN/domain/backup are deploy-time, not code. |
| `pydantic-settings`/`PyJWT`/`slowapi`/`fastapi-csrf-protect` version conflicts with pinned FastAPI/Pydantic | Med | PR-1/3/9/10 pin versions compatible with FastAPI 0.115.6 + Pydantic 2.10.3; `pip install -r requirements.txt` is an acceptance gate. |

## Open Questions (for owner)

> **None for P1a — all design points locked in the 2026-06-11 grill:** CSRF = `fastapi-csrf-protect`; access cookie `path=/`, refresh `path=/api/auth`; email infra deferred to P1b; Sentry wired with env DSN (owner supplies later); prod artifacts = `compose.prod.yml` + prod Dockerfile CMD; `ENVIRONMENT` flag is the central switch.
>
> **Deferred to P1b (do NOT attempt in P1a):** multi-tenant data isolation (the `get_active_player().first()` rewrite), email verify + forgot-password, multi-template onboarding, page-speed, a11y/responsive. These get their own task breakdown after P1a is reviewed.

---
