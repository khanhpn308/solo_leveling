# 03 — Open-question register

The audit's complete list of what could **not** be established from the repository, consolidated from
all six passes into one set. Nothing here is a per-pass log: each entry is a single question with
what is currently known, what would settle it, and which document holds the evidence. Items that the
audit *did* resolve are recorded in §4 so nothing was silently dropped.

**Organised by who can answer the question**, because that is what determines whether it blocks a
redesign:

| Owner | Count | Meaning |
| --- | --- | --- |
| **§1 A person** (product owner / operator) | 20 | the code contains the behaviour but not the intent; answering requires a decision or product knowledge |
| **§2 Runtime evidence** (needs a running stack) | 11 | the answer exists in the code but its *behaviour* cannot be read statically |
| **§3 Outside the repository** (deployment, ops, non-repo files) | 7 | the answer is not in this checkout at all |
| **§4 Closed during the audit** | 4 | resolved, with the evidence recorded |

IDs (`U-01`…`U-42`) are stable and cited by `07`, `08`, `09`, `10` and `11`. Measurement IDs
(`MF-01`…`MF-23`), which own every count more than one document states, live in `README.md`
§Canonical measured facts and are cited the same way.

---

## §1 — Answerable by a person

### Product intent

**U-07 — Is `Account.role` vestigial or a placeholder for RBAC?**
*Known:* declared (`models.py:23`), written as `"user"` at registration and in seeders, exposed to the
client in `AccountMeOut.role` (`schemas.py:952`), and **read by nothing** on either side (`09` §6.3).
No scopes, no permissions table, no admin surface. *Settle by:* operator intent, plus
`spec/feature/account_big_update_tasks_spec.md`.

**U-08 — What is the `account_tokens` table for?**
*Known:* the model exists with a `(account_id, purpose)` index and `consumed_at` (`models.py:56-74`)
and is referenced only by the `/api/dev/reset` wipe list. `Account.email_verified_at` is likewise
declared and never written. *Settle by:* reading the account spec and confirming whether email
verification or password reset was planned (overlaps U-38).

**U-11 — Is cross-tab / cross-device consistency a product requirement?**
*Known:* there is no push channel of any kind; five freshness mechanisms exist and are enumerated
(`07` §7.1) with every refetch trigger tabulated (`07` §7.2); `AccountPreference.notification_enabled`
is written and never read (U-20). *Settle by:* product intent — the code cannot answer it.

**U-18 — Is there meant to be any data-retention or privacy handling?**
*Known:* no retention policy, no PII classification, and no deletion path for
`account_security_events` (which stores `email_attempted` on every failed login, plus register /
refresh / logout events). The only bulk delete is the unauthenticated `POST /api/dev/reset`.
*Settle by:* product intent; for a single-user local tool the answer may be "not applicable".

**U-20 — Why is `account_preferences` written and never read?**
*Known:* four fields (`locale`, `timezone`, `theme`, `notification_enabled`) are written at
registration and seeding, and no read of any of them exists in `backend/app/`. The UI hardcodes dark
styling and `vi-VN` for the host clock. *Settle by:* intent — is a settings surface planned?

**U-21 — Is the rank-exam `mcq` / `multiple_choice` mismatch known?**
*Known:* behaviour is certain — `RankExamScreen.jsx:162` tests `question_type === 'mcq'` while the
backend only emits `"multiple_choice"` (`seed.py:2048`, `main.py:1718`), and neither string appears on
the other side (`06` §3 D-11 item (a)). *Settle by:* intent — known-broken MVP slice, or unnoticed
regression.

**U-22 — Are the empty vocabulary levels expected?**
*Known:* `_VOCAB_LEVELS_META` creates and links all four canonical levels on every boot
(`seed.py:2566-2583`), but only one vocab markdown file exists on disk, so three levels are empty by
construction. *Settle by:* intent — more content planned, or locked/empty is the design.

**U-23 — Is omitting the monthly boss claim intentional?**
*Known:* the endpoint is complete and carefully written — cleared-check, double-claim guard,
idempotency key, skill-XP award, and a deliberate "no player XP" comment (`main.py:1246-1267`) — and
no UI calls it. *Settle by:* intent; nothing in `TASKS.md`, `DECISIONS.md` or code comments explains it.

**U-24 — Are the dead components to be deleted or kept as alternates?**
*Known:* 9 components / 1285 lines are unreachable (`05` §4.1); `VocabularyOverlay.jsx` is a
full 870-line second implementation of the vocabulary surface, not a stub, and holds the **only**
reference to two endpoints that do not exist (`:142`, `:161`). *Settle by:* intent — superseded,
planned replacement, or A/B alternative.

**U-30 — Are three different quantities meant to be called "XP"?**
*Known:* `summary.today_xp`/`week_xp` are SQL sums over claimed quests (`main.py:770-790`); the player
level bar reads `player_xp`, which is `round(mean of the 5 matrix skill XP)` (`services.py:488-493`);
per-skill figures are the ledger. `08` §7.2. *Settle by:* product intent; `docs/current/BUSINESS_RULES.md`
was inventoried, not adjudicated.

**U-31 — Is the client's skill-progress ladder intentional?**
*Known:* `SKILL_XP_THRESHOLDS = [0,500,1200,2500,4500,7000,10000]` (`dashboard-data.js:4`) is the only
implementation of every skill-bar percentage, and its values appear **nowhere** in `backend/app/`; it
saturates at 10 000 while rank S needs 13 279 (`services.py:79-88`), so a full bar can sit beside rank
B. No test, comment or doc mentions it. *Settle by:* intent.

**U-33 — Was the review screen's XP display ever backed by a server award?**
*Known:* `VocabularyWorkspace.jsx:383-384` computes `again:0/hard:1/good:2/easy:3` locally and renders
`+{reviewXpEarned * 10}` (`:861`); the endpoint it calls awards nothing
(`services.py:1816-1857`). *Settle by:* intent / task history.

**U-38 — Is the account lifecycle meant to stop at two states?**
*Known:* `Account.status` has exactly two written values (`"active"` `main.py:484`, `"locked"`
`main.py:564`) and one enforcement branch (`09` §5); `email_verified_at` and the whole `AccountToken`
model have no writer or reader outside the reset wipe list. *Settle by:* intent (overlaps U-08).

**U-39 — Are the client-supplied authorities deliberate?**
*Known:* `POST /api/vocabulary/boss/{id}/submit` grades on a posted `score_pct` and writes
`confirmed_rank` (`services.py:2999`, `:3015`) while its own challenge endpoint ships
`correct_answer` (`schemas.py:890`); applying a rank suggestion rewrites skill XP to the rank floor
(`services.py:1451-1452`); `xp_gained` is accepted and ignored. The user *is* the intended authority
for their own test scores and check-ins — the open part is whether the server-side **consequences**
were meant to derive from unverified input. `09` §8. *Settle by:* intent.

**U-40 — Is the client's weekly-mission pattern table meant to mirror the server's?**
*Known:* they are **different data**: `dashboard-data.js:91-119` holds three patterns (`A/B/C`) whose
items are sentence `lines`, while `seed.weekly_mission_patterns` (`seed.py:818-891`) holds six per
phase with items, target counts and `reward_xp` 40/45/50 plus a 25-XP onboarding week. The client's
fallback renders through the same component with `rewardXp` hardcoded to 50 and items synthesized at
`target_count: 1` (`App.jsx:254-268`), and its label says "player XP" while the claim awards skill XP
(`08` §T-6). The same question applies to the duplicated phase boundaries
(`dashboard-data.js:53-90`, `:485-491` vs `seed.py:366-388`). *Settle by:* intent / task history.

**U-41 — Are the client-only progression values load-bearing for anything a user compares?**
*Known:* `10` Part A9 lists thirteen rules with exactly one implementation in the browser; only the
player level curve is covered by the frontend test suite. *Settle by:* product intent plus a
comparison of the two weekly-pattern tables against `TASKS.md`.

**U-42 — Is the de-facto contract meant to be narrower than the declared one?**
*Known:* `[DERIVED]` the client reads 21 of `QuestOut`'s 40 fields and comparable subsets of
`PlayerProfileOut`/`SkillOut`, measured by property access — so destructured, spread and string-keyed
reads are not counted and the true set is larger (`10` §C1). *Settle by:* a per-field trace to a render
site, plus intent about the unused fields.

### Spec and backlog adjudication

**U-16 — Do `spec/`, `docs/current/`, `TASKS.md` and `tasks-done.md` agree with the code?**
*Known:* all were **inventoried only**; `docs/current/DATABASE_SCHEMA.md` and `SCHEMA_SEMANTICS.md`
claim to describe the schema while `models.py`/Alembic are the executable truth, and `04` §5 records
seven documented-vs-implemented contradictions already found. A full adjudication is a reading task
plus a product judgement. *Settle by:* a document-by-document comparison.

**U-17 — Are the progression business rules correct against the specs?**
*Known:* the XP ledger, rank-promotion state machine, badge recomputation, weekly-mission matching,
collocation familiarity decay and the rank-exam pass threshold were **read at a structural level
only**; their correctness against `spec/infor/ielts_xp_policy_rank_quest_spec.md` is unverified.
*Settle by:* a rule-by-rule comparison.

**U-15 — What is the relevance of the non-code artifacts?**
*Known:* `error/error1.jpg`, `img/dashboard_main.png`, `img/quest_overlay.png`,
`img/vocabulary_workspace.png`, `img/planning/*` (6 files),
`guideline/vocabulary_learning_guideline_pre_intermediate.md`, `plans/*.md` (4 files, two naming
conventions) were inventoried but not interpreted. Also committed but unrelated to this project:
`.vscode/settings.json` contains an **ESP-IDF** setup path from a different toolchain.
*Settle by:* knowing which artifacts are current.

---

## §2 — Answerable by runtime evidence

**U-02 — Does the committed `frontend/dist/` correspond to the current source?**
*Known:* `dist/index.html` references hashed bundles; there is no build manifest, no recorded build
time and no CI, so hashes cannot be matched to a commit from the repository alone. *Settle by:*
running `npm run build` and diffing emitted hashes.

**U-03 — Does multi-account use actually work end to end?**
*Known:* the schema supports it (`players.account_id` nullable **and unique**, `models.py:146`;
campaign-scoped tables) and account-scoped routes resolve the player from the JWT
(`main.py:270-275`) — but `services.get_active_player` returns `db.query(Player).first()`
(`services.py:235-240`) and startup seeding binds a player to a hardcoded account
(`seed.py:909-940`, `:943`). Whether a second registered account gets an isolated campaign was **not
tested**. *Settle by:* running the backend and registering two accounts.

**U-04 — Do the backend tests pass?**
*Known:* `backend/app/test_backend.py` holds **68 tests in 11 classes** and was **read, not executed**
— the audit shell has `node`/`npm` but no working Python interpreter. The suite also runs on in-memory
SQLite with `create_all`, so it cannot validate the MySQL path or the 31 Alembic revisions.
*Settle by:* a Python environment with `requirements.txt` installed, then
`python -m unittest app.test_backend` from `backend/`.

**U-19 — Can two writers race on the same progression row?**
*Known:* every request gets a fresh session (`database.py:41-46`); `campaign_skill_states` has 30
mutation sites across 6 functions (`11` R-2); no optimistic locking or `SELECT … FOR UPDATE` pattern
appears in the code that was read. *Settle by:* concurrent requests against a running stack.

**U-25 — What does a rejected loader actually leave on screen?**
*Known:* the render for each failure is tabulated statically (`09` §4.4) — `API ERROR:` screen for a
rejected loader, silent `[]` for the two guarded ones, blank page for session death — and there is no
React error boundary and no 404/500 route anywhere. *Settle by:* running the UI with a failing
endpoint.

**U-26 — Is the UI accessible?**
*Known:* patterns are consistent (dialogs with `role`/`aria-modal`/`aria-labelledby`, `aria-label` on
icon-only buttons, Escape and Tab trapping — `05` §5) but no screen-reader, keyboard-order or contrast
testing was performed and no accessibility tooling exists in the repo. *Settle by:* a browser session
and manual testing.

**U-28 — Which handlers are unscoped?**
*Known:* the three scoping patterns are identified with examples, and
`get_player_or_404`/`get_campaign_or_404` are shown to be **not** auth functions — one handler uses
them (`09` §3, §6.2). `GET /api/vocabulary/{item_id}` does not filter by player
(`main.py:1906-1912`). The **full** set was not enumerated. *Settle by:* a mechanical pass over all 121
handlers for a `player_id`/`campaign_id` predicate, then a two-account test (needs U-03).

**U-29 — What are the shapes of the 21 routes with no `response_model`?**
*Known:* they return untyped dicts or nothing (`07` §6.1), including
`GET /api/vocabulary/boss/status` (a nested `bosses[]` read by both `main.py:2228` and
`VocabularyBoss.jsx`) and `POST /api/onboarding/activate-campaign`. *Settle by:* issuing the requests
against a running backend, or reading each handler body end-to-end.

**U-32 — Is recompute-on-read load-bearing?**
*Known:* 8 plain GETs call `refresh_progress_state` and commit (`08` §6.1) and there is no scheduler,
so nothing else refreshes `quests.status`, `quests.earned_xp`, badge unlocks or streak counters.
*Settle by:* observing those columns over days with the GET-side refresh removed (needs U-04).

**U-34 — Is the session-death path intended as it stands?**
*Known:* `App.jsx:152-155` handles a 401 that survives the silent refresh by logging out, navigating
and **returning `undefined` instead of throwing**, so loader `catch` blocks never run;
`client.js:71` sets `error.sessionExpired`, read by nothing (`09` §4.3). *Settle by:* a browser session
with an expired token.

**U-37 — Are concurrent refresh attempts reachable?**
*Known:* rotation replaces `account_sessions.refresh_token_hash` in place with no grace window or token
family (`main.py:637-639`) while the client fires up to 13 parallel requests on boot (`08` §3 T-1);
the second refresh gets `401 "Invalid or expired refresh token"` (`main.py:630-631`), which ends the
session. *Settle by:* running the stack with a short access-token TTL and reloading.

---

## §3 — Answerable outside the repository

**U-01 — How is this application actually deployed, and is it running anywhere?**
*Known:* `HEAD`'s compose file set `VITE_API_URL` to a public IP and `CORS_ORIGINS` still lists
`http://<ip>:5173`; the working tree has since reverted `VITE_API_URL` to localhost (uncommitted, not
this audit's change). There is no IaC, no production Dockerfile, no deploy script, no TLS config and no
CI. *Settle by:* the operator, plus `docker compose config`/`ps` on the host.

**U-06 — Does the lockfile match what the Dockerfile installs?**
*Known:* `frontend/package-lock.json` is committed but `frontend/Dockerfile:6` runs `npm install`,
which may resolve differently; the committed `node_modules/` (1533 files) may be out of sync with
either. No lockfile check was possible without installing. *Settle by:* `npm ci --dry-run` in a scratch
copy.

**U-12 — Could CI exist outside the conventional locations that were checked?**
*Known:* checked and **absent**: `.github/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`,
`.woodpecker`, `.drone.yml`, `azure-pipelines.yml`, `.travis.yml`, `bitbucket-pipelines.yml`,
`.buildkite/`, `.teamcity/`, `.appveyor.yml`, `.gitea/`. A pipeline driven entirely by an external
system would be invisible here. *Settle by:* the forge's settings.

**U-14 — What else lives in or beside the checkout that is not tracked?**
*Known:* `.freebuff/` is untracked (0 tracked files) beside tracked tooling directories
(`.claude/launch.json`, `.codegraph/` — including a **tracked `daemon.pid`** and the repository's only
`.gitignore`, scoped to that tool — and `.mcp.json` for a "codegraph" server). Whether a dev server or
database has been running recently was **not** verified (no `docker ps`, no port probing).
*Settle by:* `docker ps` / port probing on the host.

**U-27 — How much design rationale lives outside the repository?**
*Known:* `TASKS.md:3,41` reference plan files under `~/.claude/plans/` (e.g.
`ph-n-3-majestic-snowglobe.md`) that are not in the repo. *Settle by:* reading those files.

**U-35 — Is `JWT_SECRET_KEY` set in any real deployment?**
*Known:* `auth_utils.py:8` falls back to a hardcoded literal, and the variable name appears **nowhere
else** in the repository — not in `.env.example` (three keys: `APP_START_DATE`, `CORS_ORIGINS`,
`DATABASE_URL`) and not in `docker-compose.yml`, so the shipped composition signs with the
compiled-in key (`09` §2.3). *Settle by:* `printenv JWT_SECRET_KEY` on the host, or the compose
`config` output.

**U-36 — Is the deployment reachable off-localhost, and over TLS?**
*Known:* the refresh cookie is set without `secure` (`main.py:453-462`), the bearer token travels in a
plain header, and `CORS_ORIGINS` in compose includes a public IP origin (`docker-compose.yml:30`).
Whether any of that is live is a network fact. Related to U-01. *Settle by:* host/DNS/TLS facts.

---

## §4 — Closed during the audit

Recorded so it is clear nothing was dropped. Each was resolved by evidence rather than by a decision.

| ID | Original question | Resolution |
| --- | --- | --- |
| **U-05** | How much backend↔frontend logic duplication is there? | **Enumerated.** The player level curve is deliberately mirrored (`services.py:77` ↔ `dashboard-data.js:614-617`, and the frontend test asserts the mirror); phase boundaries are duplicated with different label text; the weekly mission patterns are two different data sets; the skill ladder has no server counterpart at all; quest status/mode/earned-XP are computed on both sides (`10` §A9, §C5). Residual intent questions live in U-31, U-40, U-41. |
| **U-09** | Which `material.md` copy is authoritative, and do they agree? | **They do not agree and one is empty.** `backend/material.md` is **0 bytes**; `material/material.md` is **238 258 bytes**. `material_file_path()` (`seed.py:557-579`) returns the first *existing* candidate: compose sets `MATERIAL_PLAN_PATH=/app/material.md` (the 238 KB mount), while a non-Docker run falls through to `<repo root>/material.md` (absent) and then `<repo>/backend/material.md` (**the empty one**), so study-plan weeks, sessions and main quests would seed empty while daily quests still generate. Recorded as risk `11` R-5. |
| **U-10** | Is the client/server contract drift real, and are the backend-only paths intentional? | **Real, and the client side is dead UI.** Exactly two client calls target routes that do not exist (`VocabularyOverlay.jsx:142`, `:161`) and both live in a component imported by nothing, so neither can fire (`07` §5). The path-set diff is now explained at the capability level: 49 of 121 paths have no consumer, grouped by why (`07` §4). Residual intent question is U-24. |
| **U-13** | Is there any lint/format/type-check configuration? | **None exists.** An exhaustive check of tracked files returns no `eslint`/`prettier`/`ruff`/`pyproject`/`tsconfig`/`setup.cfg`/`mypy`/`editorconfig`/`pre-commit`/`Makefile` outside `node_modules`; no `.gitignore` exists at the root either. Consistent with `02` §7.8. |

---

## §5 — Absence claims and their searches (reviewability appendix)

Every "there is no X" statement in this deliverable rests on the search below, not on proof. Absence is
only as strong as the search that failed.

| Claim | Search performed |
| --- | --- |
| No reverse proxy / TLS | `grep -ril "nginx\|traefik\|caddy\|reverse.proxy\|proxy_pass"` over `*.yml *.yaml *.conf *.md Dockerfile` → 0 matches |
| No realtime channel | keyword scan for `WebSocket\|websocket\|sse\|StreamingResponse\|EventSource` in `backend/app/` → only incidental substring matches, no import; and in `frontend/src` no `new WebSocket`, `new EventSource`, `XMLHttpRequest` |
| No broker / cache / queue | no Redis, Memcached, Kafka, RabbitMQ or MQTT client in `requirements.txt` or imports |
| No scheduler / background work | no `BackgroundTasks`, no APScheduler/Celery, no cron or systemd unit |
| No outbound integrations | `grep -rn "httpx\|import requests\|urllib\|aiohttp\|socket\." backend/app/` → 0 matches; no non-local URLs in `backend/app/*.py` |
| No CI | 13 conventional CI paths checked (see U-12) and `git ls-files` filtered for `ci` → nothing outside `node_modules` |
| No RBAC | `grep -rn "\.role\b\|role=="` over `main.py`, `services.py`, `seed.py` → 0 matches; `frontend/src` scan → no use |
| No email verification | `grep -rn "email_verified_at" backend/app/*.py` → only the column definition (`models.py:25`) |
| No server-side password policy | `AccountRegisterIn` (`schemas.py:930-933`) has no validators; the only rule is the browser attribute `minLength={6}` (`Register.jsx:61`), absent from the login form |
| No rate limiting beyond the login lockout | no `slowapi`/limiter/middleware in `main.py` or `requirements.txt`; the only counter is `failed_login_count` → `locked` (`main.py:560-565`), applied to `/api/auth/login` only |
| No access-token revocation | `decode_jwt` (`auth_utils.py:32-55`) checks signature + `exp` only; no denylist, no `jti`, no session lookup |
| No `secure` flag on the refresh cookie | `set_refresh_cookie` (`main.py:453-462`) sets `httponly`/`samesite`/`max_age`/`path`; `secure` is never passed |
| No `.gitignore` at the repository root | root listing shows only `.claude`, `.codegraph`, `.env.example`, `.freebuff`, `.git`, `.mcp.json`, `.vscode`; the only `.gitignore` is scoped inside `.codegraph/` |
| No frontend error boundary or 404 route | `05` §5; `App.jsx` failure surfaces are three `boot-screen` strings (`:766`, `:770`, `:775`) |
| No `TASKS.md`-referenced plan files in the repo | paths point at `~/.claude/plans/` (U-27) |
