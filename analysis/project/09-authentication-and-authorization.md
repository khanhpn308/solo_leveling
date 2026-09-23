# 09 — Authentication and authorization, end to end

Answers mission question **10**: how authentication and authorization actually behave — credential
issuance, storage and verification; token format, lifetime and client storage; every refresh, expiry
and silent-retry path including what the UI leaves behind when a session dies; the account lifecycle;
what authorization is enforced per route and what is only authenticated; the unauthenticated
surfaces with their real reachability distinguishing the app's own client from curl or a browser; and
the trust boundary the client is assumed to hold.

Discovery only — every finding below is stated as behaviour with its evidence, not as a defect to
fix. Companion documents: `07-api-contract-reference.md` (endpoint inventory, auth column),
`08-data-flow-traces.md` §2 (the session precondition), `02-current-architecture.md` §6 (the
pass-1 sketch this expands). Evidence convention and repo state: `README.md`.

---

## 1. Where authentication lives

**Entirely inside the FastAPI process, as a per-route dependency chain.** There is no gateway, no
auth middleware, no identity provider, no server-side session store and no reverse proxy
(`02` §6). `app = FastAPI(title="IELTS Quest Dashboard API", version="2.0.0")` (`main.py:208`) carries
**no global `dependencies=[...]`** — the only middleware registered is CORS (`main.py:210-217`).
Consequently each handler opts into authentication by declaring one of four dependency functions as
a parameter, and a handler that forgets to is public by default.

Three sites implement everything:

| Concern | File | Lines |
| --- | --- | --- |
| Password hashing + token codec | `backend/app/auth_utils.py` | whole file (74 lines) |
| Account/session/token routes | `backend/app/main.py` | `470-690` |
| Dependency chain | `backend/app/main.py` | `222-306`, `417-429` |

---

## 2. The credential, from creation to storage

### 2.1 Registration creates six rows in one transaction

`POST /api/auth/register` (`main.py:470-545`), body `AccountRegisterIn{email, password,
display_name?}` (`schemas.py:930-933`):

1. `email_normalized = email.strip().lower()`; duplicate → **400** `"Email already registered"`
   (`main.py:472-475`).
2. `Account(email, email_normalized, password_hash, display_name, status="active", role="user",
   onboarding_completed=False)` (`main.py:479-488`).
3. A `Player` bound to the account with `setup_completed=False` and `start_date = parse_start_date()`
   (`main.py:490-497`).
4. `AccountPreference` (`locale="vi"`, `timezone="Asia/Ho_Chi_Minh"`, `theme="dark"`,
   `notification_enabled=True`) (`main.py:499-507`).
5. `PlayerLearningProfile` (`main.py:509-517`).
6. `AccountSession` + `AccountSecurityEvent(event_type="register")` (`main.py:519-535`).

**No campaign is created.** `[DERIVED]` This is why onboarding is mandatory rather than optional:
`get_current_campaign` 404s for a player with no campaign (`main.py:269-275` →
`services.get_active_campaign` `services.py:242-257`), so every campaign-level route fails until
`POST /api/onboarding/activate-campaign` (`main.py:707-762`) runs and sets `active_campaign_id`.
`email_verified_at` is declared (`models.py:25`) and **never written anywhere** (grep over
`backend/app/*.py`: only the model line) — there is no verification flow, and nothing enforces
verification.

`[DERIVED]` **There is no server-side password policy.** `AccountRegisterIn` (`schemas.py:930-933`)
has no validators — no length, no complexity. The only rule is the browser attribute
`minLength={6}` on the register form (`Register.jsx:61`), which is absent from the login form's
password field (`Login.jsx:47-53`) and trivially bypassed by calling the API directly.

### 2.2 Password storage and verification

`hash_password` (`auth_utils.py:59-64`): PBKDF2-HMAC-SHA256, 100 000 rounds, 16 random salt bytes
(`os.urandom`), stored as the single string `pbkdf2_sha256$<rounds>$<salt_hex>$<key_hex>`.
`verify_password` (`auth_utils.py:66-74`) re-derives with the stored rounds/salt and compares with
`hmac.compare_digest`; any malformed stored value returns `False` rather than raising.

### 2.3 The access token

| Property | Value | Evidence |
| --- | --- | --- |
| Format | hand-written `header.payload.signature`, base64url, HS256 | `auth_utils.py:12-30` |
| Implementation | `hmac` + `hashlib` + stdlib `base64`/`json` — **no `python-jose`, no `pyjwt`, no external JWT library** | `auth_utils.py:1-5`, `requirements.txt` |
| Claims | `sub` = account id **as a string**, `iat`, `exp` | `auth_utils.py:19-21`; issued as `{"sub": str(account.id)}` (`main.py:542`) |
| Lifetime | **3600 s** (`create_jwt` default `expires_in=3600`) | `auth_utils.py:17` |
| Absent claims | no `iss`, no `aud`, no `jti`, no `nbf`, no scopes/roles | `auth_utils.py:17-30` |
| Verification | signature via `hmac.compare_digest`, then `exp < time.time()` → `None`; any exception → `None` | `auth_utils.py:32-55` |
| Revocation | **none** — no denylist, no session lookup, no `jti` tracking. A signed token is valid until `exp` | `auth_utils.py:32-55` |
| Signing key | `JWT_SECRET_KEY` env var, **falling back to a hardcoded literal** | `auth_utils.py:8` |

`[DERIVED]` The signing-key fallback is reachable in the shipped configuration: `JWT_SECRET_KEY`
appears **nowhere** in the repository except `auth_utils.py:8` — not in `.env.example` (which
contains only `APP_START_DATE`, `CORS_ORIGINS`, `DATABASE_URL`) and not in `docker-compose.yml`'s
environment blocks (`docker-compose.yml:26-31`). A deployment that uses the provided compose file
therefore signs tokens with the literal compiled into the source. Stated as behaviour: the key is
deterministic and public for that configuration; whether any deployment overrides it cannot be seen
from the repository (U-01/U-35).

Because decoding is stateless, **the account row is re-read on every request** (`main.py:247-258`),
which is what makes the `status` check effective — see §5.

### 2.4 The refresh token and its session row

Issued identically at register and login (`main.py:523-530`, `:589-596`): 32 bytes from
`os.urandom`, urlsafe-base64, and only the **SHA-256 hex of it** is persisted, in
`account_sessions.refresh_token_hash` — `String(64)`, `UniqueConstraint`
(`models.py:44`). The row carries `account_id`, `expires_at` (+30 days), and nullable
`user_agent`/`ip_address` columns that **no code ever writes**.

| Property | Value | Evidence |
| --- | --- | --- |
| One row per login (not per account) | inserted at each login/register | `main.py:526-530`, `:592-596` |
| Transport | httpOnly cookie `ielts_rt`, `samesite="lax"`, `max_age=30d`, `path="/api/auth"`, **no `secure`** | `REFRESH_COOKIE` `main.py:450`, setter `:453-462` |
| Alternative transport | a JSON body field `refresh_token` (`RefreshTokenIn`, `main.py:446-447`) | `main.py:615-618`, `:660-663` |
| Rotation | on every refresh the stored hash is **replaced in place** and `expires_at` extended +30 days | `main.py:637-639` |
| Reuse detection | none — there is no token family, no "previous hash" column, no reuse alarm | `models.py:36-54` |
| Revocation | logout sets `revoked_at` + `revoke_reason="User logged out"` | `main.py:664-670` |
| Expiry cleanup | none — expired/revoked rows are only deleted by the unauthenticated `/api/dev/reset` wipe list (`main.py:1523`) | — |

### 2.5 Where the client keeps them

- **Access token: `localStorage['ielts_access_token']`** (`client.js:3-15`). Not httpOnly, not
  per-tab, readable by any script on the origin, and survives tab close/reopen.
- **Refresh token: never touched by JavaScript** — it lives only in the httpOnly cookie, sent
  automatically because `credentials: 'include'` is set on every `fetch` (`client.js:44`).
- **No other client-side auth state**: `AuthProvider` holds `account` and `onboardingCompleted` in
  React state only (`AuthProvider.jsx:9-12`), with no persistence and no cross-tab sync (no
  `storage` listener — `07` §7.1).
- `[DERIVED]` The client never inspects `exp`. Expiry is discovered only by receiving a 401.

---

## 3. Credential → authorized data: the request path

Every authenticated request traverses this chain, in order. Each step is a FastAPI dependency, so a
failure short-circuits with the code shown.

```
fetch(`${API_BASE}${path}`, {headers: {Authorization: `Bearer <localStorage token>`},
                             credentials: 'include'})
   │  client.js:33-47
   ▼
security = HTTPBearer(auto_error=False)                     main.py:220
   │  missing/blank header → credentials is None
   ▼
get_current_account                                         main.py:222-258
   ├─ not credentials .......................... 401 "Missing authorization header"
   ├─ decode_jwt(token) is None
   │    (bad signature, malformed, expired) ..... 401 "Invalid or expired access token"
   ├─ payload["sub"] missing ................... 401 "Invalid token payload"
   ├─ no Account with that id .................. 401 "Account not found"
   └─ account.status != "active" ............... 403 "Account is inactive"
   ▼
get_current_player  (accounts.id → players.account_id)      main.py:261-266
   └─ no Player row ............................ 404 "Player profile not found for this account"
   ▼
get_current_campaign  → services.get_active_campaign       main.py:269-275
   └─ no active campaign and none owned ........ 404 (detail from services.py:257)
   ▼
handler body → inline `campaign_id` / `player_id` filters → response_model
```

Two variants exist off this chain:

- `get_optional_campaign` (`main.py:278-286`) — identical but returns `None` instead of 404.
  `[DERIVED]` It has exactly **one** consumer: `POST /api/certificates/manual` (`main.py:1342`), which
  is therefore usable by an account that has never activated a campaign.
- `get_player_or_404` / `get_campaign_or_404` (`main.py:417-429`) — **not auth functions**. They call
  `services.get_active_player(db)` = `db.query(Player).first()` (`services.py:235-240`), i.e. the
  first player row in the database, and raise 404 if none. A handler that uses them instead of
  `Depends(...)` is **unauthenticated and acts on an arbitrary player**. `[DERIVED]` Exactly one
  handler does: `POST /api/dev/regenerate-quests` (`main.py:1877-1880`).

`[DERIVED]` The `403` branch is only reachable in one scenario (see §5): the `Account.status` check
is the single authorization predicate in the entire dependency chain, and it distinguishes only
"active" from "not active".

---

## 4. Refresh, expiry and silent retry

### 4.1 The single retry

`apiFetch` (`client.js:33-73`) is the only place retries happen:

```
response.status === 401
  → attemptRefresh(): POST /api/auth/refresh, credentials:'include', no body   client.js:17-31
       res.ok  → setTokens(data.access_token); return true
       !res.ok or throw → return false
  → if refreshed: replay the ORIGINAL request once with the new bearer header  client.js:54-64
       retry not ok → throw Error(text) with .status
  → if not refreshed: throw Error(text) with .status = 401 and .sessionExpired = true
```

Notes grounded in the code:

- The retry reuses the same `options` object, so a POST body is replayed verbatim — including
  mutations. `[DERIVED]` Only server-side idempotency guards (the XP-ledger keys, §8) make that safe;
  endpoints without one would run twice.
- `attemptRefresh` sends **no body**, so the refresh token must come from the cookie. The
  `RefreshTokenIn`-in-body path (`main.py:615-618`) has no client caller.
- Retry depth is exactly one: there is no loop, so a token that is still rejected logs the user out.
- **`error.sessionExpired` is written and never read** — a grep over `frontend/src` returns the
  assignment (`client.js:71`) and nothing else.

### 4.2 Rotation and what a concurrent refresh does

Rotation replaces `refresh_token_hash` in place (`main.py:637-639`), so the previous raw token stops
resolving immediately. `[DERIVED]` Because there is no grace window and no token family, a second
refresh presented shortly after the first (an interleaved request, or a second browser tab holding
the same cookie) finds no matching non-revoked row and receives
`401 "Invalid or expired refresh token"` (`main.py:629-631`) — and, per §4.3, a 401 that survives the
retry ends the session. Whether this is observable depends on how many parallel 401s the client can
produce, which §5 of `08` suggests is high (13 parallel loader requests on boot).

### 4.3 What the UI does when the session actually dies

This is the second half of the 401 path, and it is **not** in `client.js`:

```javascript
const api = useCallback(async (path, options = {}) => {
  try { return await apiFetch(path, options) }
  catch (err) {
    if (err.status === 401) {
      await logout()            // POST /api/auth/logout, then clearTokens(), setAccount(null)
      navigate('/login')
      return                    // ← returns undefined, does NOT rethrow
    }
    throw err
  }
}, [logout, navigate])
```
(`App.jsx:146-158`; `logout` at `AuthProvider.jsx:47-56`)

`[DERIVED]` Consequences, all following from the bare `return`:

1. Every caller receives `undefined` where it expects a payload.
2. Loader `catch` blocks never run, so their error state is never set: `loadInitialData` proceeds to
   `setSummary(undefined)`, `setProfile(undefined)`, … (`App.jsx:387-394`), and the
   `if (silent) throw error` branches are unreachable for this failure.
3. With `summary` undefined, `view` is `null` (`App.jsx:227-230`), so the shell renders nothing and
   the router has navigated to `/login` (`App.jsx:775`).
4. `AuthProvider.logout` calls `POST /api/auth/logout` best-effort, so the session row is revoked and
   the cookie cleared; the client's `clearTokens()` removes the access token.

`[UNRESOLVED]` (U-34) Whether returning `undefined` instead of rethrowing is intended degradation or
an unfinished path could not be determined from the code; the observable difference is only visible
with a running browser session.

### 4.4 What a failed read leaves in component state

| Trigger | What is set | What renders |
| --- | --- | --- |
| Any loader rejects with a non-401 (network down, 500, 404) | `appError` via `commitState(() => setAppError(error.message))` (`App.jsx:396-397`, `:417-418`, …) | full-screen `API ERROR: <message>` (`App.jsx:770-772`) |
| Cold boot, still loading, no summary yet | `appLoading` true | `SYSTEM LOADING...` (`App.jsx:766-768`) |
| `/vocabulary` or `/flashcards/due` reject | nothing — both carry `.catch(() => [])` | dashboard renders with empty vocabulary lists (`App.jsx:383-384`) |
| Session death (401 that survives retry) | loaders resolve with `undefined`; `account` cleared by `logout()` | `view === null` → `return null` (`App.jsx:775`), so a blank page until the router lands on `/login` |
| `ProtectedRoute` while `/auth/me` is in flight | `loading` true | `return null` — a blank screen (`ProtectedRoute.jsx:7`) |
| `/auth/me` fails on a cold start with a stored token | `clearTokens()` then `setLoading(false)` (`AuthProvider.jsx:21-25`) | redirect to `/login` |

`[DERIVED]` There is no React error boundary and no 404/500 route anywhere (`03` U-25), so a render
error in any child of `App` is not caught by the product code.

### 4.5 Cold start with a stored token

`AuthProvider.hydrateFromToken` (`AuthProvider.jsx:13-28`) reads the token from `localStorage`; if
present it calls `GET /api/auth/me` (`main.py:678-690`) and sets `account` +
`onboardingCompleted` from `me.account`. On any failure it clears the token silently. `[DERIVED]`
`/auth/me` is the only route that returns the account (`AccountMeOut`, `schemas.py:947-957`), so it
is also the only source of `onboarding_completed` on reload — which is what decides whether
`ProtectedRoute` sends the user to `/onboarding` or into the app.

---

## 5. Account lifecycle and the states a user can be in

`Account.status` is `String(30)` defaulting to `"active"` (`models.py:22`). Only two values are ever
written, both verified by grep over `main.py` and `seed.py`:

| Value | Written by | Effect |
| --- | --- | --- |
| `"active"` | registration (`main.py:484`), seeders (`seed.py:917`, `:932`) | passes `get_current_account` |
| `"locked"` | login brute-force counter (`main.py:564`) | 403 on every authenticated route; blocked at login while `locked_until` is in the future |

There is no `"disabled"`, `"suspended"`, `"pending"` or `"deleted"` anywhere, and no endpoint changes
`status` except the login path. `[DERIVED]` Note the case-sensitivity trap: `seed.py:1723` writes
`status="Locked"` — that is a **different model** (a mock-test `result_status`), not an account.

The lockout rule (`main.py:552-565`): if `status == "locked"` and `locked_until > utcnow()` → 403
`"Account is locked. Try again later."`; if the window has passed, the account is silently restored
to `"active"` with `failed_login_count = 0`. A wrong password increments the counter and writes an
`AccountSecurityEvent(event_type="login_failed", detail="Invalid password")`; at ≥5 it sets
`status="locked"` and `locked_until = utcnow + 15 min`. A successful login resets the counter and
stamps `last_login_at`.

**The states a user actually passes through**, expressed in the code:

| State | Determined by | What the user can reach |
| --- | --- | --- |
| Unauthenticated | no token / expired token | `/login`, `/register`, `/onboarding` (see §6.4) |
| Registered, no campaign | `Player` exists, `active_campaign_id` is NULL | `/onboarding` only — every campaign route 404s |
| Onboarded, no evidence | `accounts.onboarding_completed = true` | the full dashboard (`/*` behind `ProtectedRoute`) |
| Locked | `status="locked"` within `locked_until` | nothing; 403 at login and on every API call |
| Token expired, cookie alive | `exp` passed, session row unrevoked | the app, once the silent refresh succeeds |
| Logged out | session `revoked_at` set, token cleared | `/login`; the old refresh token no longer resolves |

`onboarding_completed` is a separate flag from `status` and is the only gate the client enforces
itself (`ProtectedRoute.jsx:11`). `[DERIVED]` `AuthProvider` sets it from `me.account` on hydrate,
login, register and `refreshAuth`, but nothing ever sets it to `false` again, so the client's view of
it can only become stale upward within a session.

---

## 6. Authorization: what is actually enforced

### 6.1 The four levels, measured

Declared per route as a parameter; classified by the most restrictive dependency present.

| Level | Dependency | Enforced by | Count |
| --- | --- | --- | --- |
| `none` | — | nothing | **14** |
| `account` | `get_current_account` | valid token + `status == "active"` | **3** |
| `player` | `get_current_player` | + a `players` row for that account | **37** |
| `campaign` | `get_current_campaign` | + an active campaign for that player | **67** |

### 6.2 What a level does *not* imply

A level authenticates; it does not scope. There is no scoping middleware and no row-level policy, so
**ownership is enforced only by the `WHERE` clause each handler writes by hand**. Three patterns
appear in the code that was read:

| Pattern | Example | Evidence |
| --- | --- | --- |
| Correctly scoped | `POST /api/quests/{id}/claim` filters `Quest.id == quest_id AND Quest.campaign_id == campaign.id` | `main.py:1093-1098` |
| Correctly scoped | `POST /api/rank-exams/{attempt_id}/submit` filters by attempt id **and** campaign id | `main.py:1777-1780` |
| Correctly scoped | `POST /api/boss-battles/{id}/claim` filters by `campaign_id` | `main.py:1248` |
| **Unscoped lookup** | `GET /api/vocabulary/{item_id}` → `services.get_vocabulary_item(db, item_id)` with no player filter | `main.py:1906-1912` → `services.py:1637-1644` |
| **Owner resolved globally** | `POST /api/vocabulary/practice/record-success` → `services.record_practice_success(db, player.id, …)` is fine, but then calls `refresh_progress_state(db)` with no player/campaign — which falls back to `Player.first()` | `main.py:2167-2169`, `services.py:804-806` |
| **Owner resolved globally** | `POST /api/quests/{id}/complete` → `complete_quest_instance` → `refresh_progress_state(db)` (no args) | `services.py:863` |
| Owner passed explicitly | `POST /api/quests/{id}/claim` → `refresh_progress_state(db, player=player, campaign=campaign)`, with the comment *"Pass player+campaign so recompute_player_progress targets the correct account"* | `main.py:1132-1135` |

`[UNRESOLVED]` (U-28) The **full set** of unscoped handlers was not enumerated; the mechanical pass
described above is the remaining work, and whether any of them is exploitable depends on whether a
second account can exist with its own data at all (U-03 — the seeder binds one player to a hardcoded
account and `get_active_player` returns the first row).
`[DERIVED]` The observable consequence today is narrower but real: on any single-account
deployment these paths resolve to the only player, so the missing filter has no visible effect; the
pattern is what matters for a second account.

### 6.3 Authenticated but otherwise unrestricted — there is no authorization model

- `Account.role` is declared (`models.py:23`), written as `"user"` at registration (`main.py:485`)
  and in seeders (`seed.py:918`, `:933`), **exposed to the client** in `AccountMeOut.role`
  (`schemas.py:952`) — and **never read anywhere**: `grep -rn "\.role\b|role=="` over
  `main.py`, `services.py`, `seed.py` returns no matches, and a scan of `frontend/src` finds no use
  either (the only hit is the word "role" inside a quiz sentence,
  `WordFamilyEvolution.jsx:86`).
- There are no scopes, no permissions table, no admin surface, and no route that behaves differently
  for any account.
- `[DERIVED]` Therefore the effective authorization model is binary: *authenticated and active*, or
  not. Every authenticated account has identical capability over the whole dataset its
  campaign/player filters reach — and, where those filters are missing or global, over rows that
  belong to another campaign.

### 6.4 Routes that are public in the client router

`main.jsx:17-28` registers `/login`, `/register`, `/onboarding` as plain routes (`:17-19`) and wraps
**only** `path="/*"` in `ProtectedRoute` (`:20-27`). `[DERIVED]` `/onboarding` is therefore publicly reachable: an
unauthenticated visitor can load it, and the only thing that stops them is the 401 returned by
`POST /api/onboarding/activate-campaign` (which is `account`-level, `main.py:707`). There is no
client-side route guard between "not logged in" and the onboarding form.

---

## 7. The unauthenticated surfaces, and how reachable each one really is

**14 paths carry no auth dependency.** Verified by reading each handler signature; the list matches
`02` §6.3.

| Path | Line | Reached by the app's own client? | Reached by curl / browser? |
| --- | --- | --- | --- |
| `GET /api/health` | `main.py:443` | no — no client call anywhere | yes, unauthenticated, trivial |
| `POST /api/auth/register` | `:470` | **yes** — `Register.jsx:29` → `api/auth.js:3` | yes |
| `POST /api/auth/login` | `:547` | **yes** — `Login.jsx:20` → `api/auth.js:11` | yes |
| `POST /api/auth/refresh` | `:612` | **yes** — `client.js:17-31`, on every 401 (not via the exported wrapper) | yes, if the cookie is present |
| `POST /api/auth/logout` | `:653` | **yes** — `AuthProvider.jsx:48` | yes |
| `GET /api/quest-templates` | `:912` | no — no client call (`07` §4) | yes |
| `GET /api/materials` | `:917` | no | yes |
| `GET /api/materials/{material_id}` | `:922` | no | yes |
| `POST /api/dev/reset` | `:1498` | **no** | **yes, with no credential of any kind** |
| `POST /api/dev/run_migrations` | `:1587` | **no** | **yes, no credential** |
| `POST /api/dev/regenerate-quests` | `:1877` | **no** | **yes, no credential**; acts on `Player.first()` via `get_player_or_404` (`:1880`) |
| `GET /api/collocation-collections` | `:2074` | no | yes |
| `POST /api/collocation-collections` | `:2079` | no | **yes — anonymous write to global master data** |
| `GET /api/collocation-collections/{collection_id}` | `:2087` | no | yes |

Reading these as behaviour rather than risk:

- The four `/api/auth/*` routes are public **by necessity**; they are the credential exchange.
- Everything else in the list is public **by omission** — the handler was written without a
  dependency. `[DERIVED]` None of them is called from `frontend/src`, so the SPA's own code can only
  reach them if a browser-driven interaction is added or a developer calls them from the console.
- `POST /api/dev/reset` (`main.py:1498-1583`) is the most consequential: it disables foreign-key
  checks, nulls `Players.active_campaign_id` / `account_id` and `Campaigns.campaign_template_id`,
  then deletes from a long model list including `RankExam*`, `AccountSession` (`:1523`) and the rest
  of the tracked tables, and reseeds. It requires no header, no cookie and no environment gate —
  `[DERIVED]` the only thing that keeps it out of a production path is that nobody builds a link to
  it. Reachable over the network by anyone who can open `:8000`.
- `POST /api/collocation-collections` (`main.py:2079-2085`) writes a row into a table that is
  campaign-agnostic master data (only a duplicate `code` is rejected), and
  `GET /api/collocation-collections/{id}` reads any collection (`:2087-2093`).
- `POST /api/dev/regenerate-quests` is the one unauthenticated route that reaches *player* data: it
  regenerates quests for whatever `Player.first()` returns rather than for the caller.

**Distinguishing the two reachability paths, stated plainly:**

| | Through the app's own client | Through curl / a browser |
| --- | --- | --- |
| Where the request originates | the SPA bundle, whose call sites are the 62 paths inventoried in `07` | any HTTP client, or `fetch` typed into DevTools on the origin |
| Auth needed | whatever the route enforces; the SPA always attaches the token when it has one (`client.js:35-39`) | whatever the route enforces — the four `/api/auth/*` and the three `/api/dev/*` need nothing |
| CORS applies | the request is same-origin after `VITE_API_URL`, so CORS is not consulted for the SPA's own calls | a *browser* page on another origin is blocked from reading responses unless its origin is in `CORS_ORIGINS` (`main.py:211`, `docker-compose.yml:30`); **curl is not subject to CORS at all** |
| Practical consequence | the public surface is effectively the auth routes plus anything a UI path triggers | the full 121-path surface, including the 49 paths the UI never calls (`07` §4) |

`[DERIVED]` The `CORS_ORIGINS` default in compose includes a **public IP origin**
(`http://18.141.232.235:5173`, `docker-compose.yml:30`), so a page served from that host is
allow-listed to read credentialed responses. Whether that host is live is U-01.

---

## 8. The trust boundary: client-supplied values the server treats as authority

This is the part of authorization that is not in the dependency chain: places where the client's
claim is accepted as the fact.

| Client-supplied value | Endpoint | What the server does with it | Evidence |
| --- | --- | --- | --- |
| `score_pct: float` | `POST /api/vocabulary/boss/{boss_id}/submit` | `passed = score_pct >= 75.0`, then **sets `campaign_skill_states.confirmed_rank = "E"`** (boss 1) and inserts `BadgeUnlock` rows (bosses 2–4) | `schemas.py:899-901`, `main.py:2236-2242`, `services.py:2999`, `:3015`, `:3017-3040` |
| `BossQuestion.correct_answer` (server **sends** it) | `POST /api/vocabulary/boss/{boss_id}/challenge` | the exam payload includes `correct_answer` per question, so grading happens in the browser | `schemas.py:885-891` field list; `VocabularyBoss.jsx` |
| `raw_score: str` | `POST /api/quests/{quest_id}/complete` | stored on the quest (`services.py:852`) and later read by `estimate_band_from_mock` to produce rank suggestions | `schemas.py:92`; `services.py:1494-1512` |
| `xp_gained: int` | `POST /api/vocabulary/practice/record-success` | **accepted and ignored** — the service reads only `payload.words` | `schemas.py:818-820` vs `main.py:2168` |
| `words: list[str]` | same | each matching word gets `mastery_score += 2` and a re-derived `mastery_rank`; then `refresh_progress_state(db)` runs | `services.py:2206-2237`, `main.py:2169` |
| test-record scores | `POST /api/test-records` | `create_rank_suggestions_for_test` creates a suggestion; applying it (`POST /api/rank-suggestions/{id}/apply`) sets `confirmed_rank` **and raises `state.xp` to the rank's `min_xp`** ("Elevate XP to the minimum for the confirmed rank"), then writes a `SkillRankHistory` row | `schemas.py:342-351`; `services.py:1438-1477` |
| certificate scores | `POST /api/certificates/manual` | same suggestion+apply path; the code comment reads *"certificate bypasses boss"* | `schemas.py:999-1004`; `services.py:1454` |
| `tracker_entry_id` | `QuestCompletionIn` | existence-checked (`db.get(model, tracker_entry_id)`) but **not ownership-checked**, so another player's entry id could be linked to the caller's quest | `services.py:216-217` |
| `checkin_date` | `POST /api/checkins` | any date accepted; upsert keyed on `(campaign_id, checkin_date)`, which feeds streak and perfect-day recomputation | `schemas.py:253-258`; `main.py:1192-1218` |

`[DERIVED]` Two distinct situations are visible in that table, and conflating them would misstate the
boundary:

1. **By design** — the product is a manual tracker whose stated purpose is that the user records
   their own test scores, certificates, check-ins and practice. For those, the client *is* the
   authority, and `POST /api/test-records` and `/api/certificates/manual` being content-unrestricted
   is consistent with that.
2. **Not obviously design** — the *consequences* of that input are computed server-side and exceed
   what   the user entered: applying a rank suggestion rewrites `confirmed_rank` **and fabricates XP**
   to the rank floor (`services.py:1438, 1451-1452`), and the vocabulary boss turns a bare `score_pct`
   into a confirmed rank while the answers needed to earn it were shipped to the client
   (`schemas.py:890`). Both are authenticated and owner-scoped; neither is gated on server-side
   evidence. The rank-exam path in `08` §T-8 is the contrast — there the answers stay on the server
   and the threshold is stored per pool.

`[DERIVED]` For completeness: the client also supplies values that the server *does* validate —
`CheckInIn.mood/energy/focus` are bounded by `Field(ge=1, le=5)` (`schemas.py:255-257`), and the
collocation/vocabulary review endpoints reject any `result` outside
`{"again","hard","good","easy"}` (`main.py:2486-2488`, `services.py:1817-1818`).

---

## 9. Transport, origin and network assumptions

Facts the auth system relies on, all from tracked files:

- **No TLS anywhere.** No reverse proxy, no certificate config, no `https` in any tracked
  configuration; the cookie is set without `secure` (`main.py:453-462`) and CORS origins are
  `http://` (`docker-compose.yml:30`). `[DERIVED]` The bearer token and the refresh cookie therefore
  travel in cleartext on any non-loopback deployment — the committed public-IP origin (§7) shows at
  least one such deployment existed.
- **CORS is the only browser-side control**: `allow_credentials=True`, `allow_methods=["*"]`,
  `allow_headers=["*"]`, origin allowlist from `CORS_ORIGINS` split on commas (`main.py:210-217`).
  `[DERIVED]` Because `allow_credentials` is true and both methods and headers are wildcards, the
  origin list is the sole restriction; no method is excluded.
- **The dev database port is published** with credentials inline in a tracked file
  (`docker-compose.yml:6-10`, host port 3307) — outside the application's auth chain entirely.
- **The Vite dev server (`:5173`) has no auth**: the SPA bundle is public. It contains no secrets but
  does contain the API base URL and every endpoint it calls (`02` §6.4).
- The refresh cookie's `path="/api/auth"` (`main.py:461`) means it is attached only to
  `/api/auth/*` requests; combined with `SameSite=Lax` it is not sent on cross-site POSTs.

---

## 10. Which auth behaviours are load-bearing for the product today

Ordered by what would visibly change if the behaviour were absent. This is a statement of current
dependency, not a recommendation.

1. **The bearer token on 118 of 121 routes.** Everything except the public surface in §7 depends on
   `get_current_account` resolving `sub` → an `Account` row.
2. **The silent refresh.** The access token lives 3600 s; a session longer than an hour survives only
   because `client.js:49-52` retries through `/api/auth/refresh`. Without it, every session would end
   at 60 minutes.
3. **The refresh cookie being httpOnly and cookie-borne.** It is the only durable credential; the
   in-body alternative has no client caller.
4. **`onboarding_completed` in the `/auth/me` payload.** It is the sole input to the client's
   onboarding gate (`ProtectedRoute.jsx:11`), and `refreshAuth()` after campaign activation
   (`Onboarding.jsx:60-62`) is what moves the user out of `/onboarding` without a re-login.
5. **`get_current_campaign`'s 404.** Because no campaign exists until onboarding runs, this 404 is
   what makes onboarding mandatory for every campaign-level route (§2.1).
6. **The login lockout counter.** It is the product's only rate limit; there is none on `/register`,
   `/refresh`, or any other endpoint.
7. **Per-handler `campaign_id`/`player_id` filters.** With one role and one enforced level, these
   inline `WHERE` clauses are the entire row-level isolation mechanism (§6.2).
8. **Server-side grading in the rank-exam path only.** The `08` §T-8 exam flow trusts nothing from the
   client; every other scored surface (§8) accepts a client verdict.

---

## 11. Unresolved (added to `03-unresolved.md` §H)

- **U-35 — Whether `JWT_SECRET_KEY` is set in any real deployment.** The key is absent from
  `.env.example` and `docker-compose.yml`, so the compose configuration uses the hardcoded fallback;
  whether an operator injects it elsewhere is outside the repository. *Settle by:* inspecting the
  running environment (`printenv JWT_SECRET_KEY` on the host, or the compose `config` output).
- **U-36 — Whether the deployment is reachable off-localhost at all**, and over TLS. Related to U-01;
  it decides whether the missing `secure` flag, the cleartext bearer token and the public-IP CORS
  origin are theoretical or live. *Settle by:* network facts about the host, plus `docker compose ps`.
- **U-37 — Whether concurrent refreshes are reachable in practice.** Rotation is single-shot with no
  grace window (`main.py:631-637`) while the client issues up to 13 parallel requests on boot
  (`08` §3 T-1). Whether two of them can 401 in the same window and end the session was **not tested**
  (needs U-04). *Settle by:* running the stack with a 1-second access-token TTL and observing a
  reload.
- **U-38 — Whether the account lifecycle is intended to stay at two states.** `status` has exactly
  two written values and one enforcement branch; `email_verified_at` exists without a writer;
  `AccountToken` (purpose/token_hash/consumed_at) exists without a reader. Whether
  verification/reset/deactivation are planned is not stated in the code. *Settle by:* `spec/` +
  operator intent (overlaps U-08).
- **U-39 — Whether the client-supplied authority in §8 is a deliberate trade-off.** The vocabulary
  boss writes `confirmed_rank` from a posted `score_pct` while its own exam payload ships the
  answers, which the rank-exam path deliberately does not do. No comment, test or task entry
  explains the difference (pass 2's U-21 covers the adjacent MCQ defect). *Settle by:* product intent
  and `TASKS.md`.
