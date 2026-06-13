# Production Roadmap — ielts-quest-dashboard

## Status

**SUPERSEDED (2026-06-11)** by [`SMALL_GROUP_PLAN.md`](SMALL_GROUP_PLAN.md).

The owner changed direction the same day: **dropped the public multi-tenant SaaS goal**. The app is
now a **small-group internal tool** (5–20 known users on one shared server), prioritizing **feature
completion over production hardening**. The heavy SaaS work below (full multi-tenant rewrite, email
verify, anti-bot rate limiting, multi-template content) is **no longer pursued**. A minimal "P0
hygiene" subset is kept (gate dev endpoints, remove hardcoded secret, basic per-account data scoping)
— see the small-group plan. ADR-002…006 are likewise superseded.

This document and its ADRs are retained for decision history (in case the public-SaaS direction is
revived later), not as current truth.

---

> _Historical content below — the original public-SaaS roadmap. Do NOT treat as current._

## Original Status (historical)

Active direction. Every decision below was made by the product owner after a structured
grill-me interview (19 questions). This is not a one-sided agent proposal — it records the
owner's decisions. Current-state claims are grounded in codegraph queries against the repo.

## Date

2026-06-11

---

## Context — why this roadmap exists

The project is currently **dev/demo, not production-ready**. The owner wants to turn it into a
**public multi-tenant SaaS** (anyone can sign up). The core problem, confirmed via codegraph:

- **The business core is fundamentally single-player.** `get_active_player(db)` is
  `db.query(Player).first()` ([backend/app/services.py:235](../../backend/app/services.py)) — it
  returns the *first* player in the DB regardless of who is logged in. The auth layer
  (`Account` / JWT / session) is complete, and some newer endpoints *do* scope correctly by
  `account.id` ([backend/app/main.py:274](../../backend/app/main.py)), but many older endpoints
  still go through the `.first()` path. → **If two users exist, their data leaks across accounts.**
- The app was **previously deployed publicly** (IP `18.141.232.235`, EC2 Singapore — now off) with a
  dev configuration: uvicorn `--reload`, volume mounts, a hardcoded JWT secret default, and
  unauthenticated dev endpoints.

Goal: a product direction plus a safe, repeatable path to production that is feasible for the
current single-developer team and stack — no over-engineered architecture.

---

## 1. Product direction (decided)

| Axis | Decision | Rationale |
|---|---|---|
| **Audience** | Public multi-tenant SaaS (open sign-up) | Owner's decision, accepting the cost of a multi-tenant rewrite |
| **Scale** | Small: tens–hundreds of users, **free, no billing** | No real users yet; optimizing for thousands now is premature. Scale + billing → Phase 3 |
| **Features** | **Keep all of them**, make every one multi-tenant | Owner chose not to cut; accepts Phase 1 as a **3–6 month full-time** project, no rush to ship |
| **Per-user content** | **A few templates by level/goal** (beginner / intermediate / target band) | Reuses the existing `CampaignTemplate`. Deep personalization (a roadmap-generation engine) → Phase 2 |

### In scope for Phase 1 (kept + made multi-tenant)
Daily/Main Quest, XP/rank/level, Boss battles, Badges, Weekly missions, Vocabulary library
(codex/tree/errors/boss), Collocation, Flashcard SRS (3 systems), Rank exam, Suggestion inbox,
Check-in, the 18-month study plan, Certificate records, multi-template onboarding.

### Out of scope for Phase 1 (deferred — with reasons)
- **True roadmap personalization** (an engine that generates quests/plans per user) → Phase 2. A separate product on its own; large.
- **Billing / Stripe / paid tiers** → Phase 3. No confirmed paying users.
- **Scale to thousands** (read replicas, sharding, fixing `refresh_progress_state`) → Phase 3. The bottleneck does not exist yet.
- **Staging environment** → Phase 2. Phase 1 uses PaaS auto-deploy straight from `main` → prod (acceptable while users are few).
- **Real SM-2 SRS** → Phase 2 (see tech debt). Currently a hardcoded map `again=0 / hard=1 / good=3 / easy=7`; `ease_factor` is stored but unused ([backend/app/services.py:1835](../../backend/app/services.py)).

---

## 2. "Production-ready" definition for Phase 1 (Definition of Done)

12 statements, each **verifiable** (one checkbox). Phase 1 is "done" only when all are true:

1. **Data isolation** — cross-account test green: two accounts never see each other's data on *any* route. No `get_active_player().first()` path remains.
2. **No weak secrets** — the app **refuses to start** if `JWT_SECRET_KEY` / DB credentials are missing; no secret lives in the repo.
3. **Complete auth** — register → real email verification → login; forgot password → reset via email works.
4. **Safe tokens** — access token in an httpOnly cookie + CSRF; no longer in localStorage.
5. **No backdoor** — `/api/dev/*` returns 404 in production; no hardcoded seed account in production.
6. **Abuse protection** — rate limiting blocks register/forgot-password spam (protects email cost).
7. **CI green** — GitHub Actions runs the full test suite (including cross-account) green on `main`.
8. **Observable** — Sentry captures BE + FE errors; `/api/health` wired to the PaaS; uptime ping running.
9. **Repeatable deploy** — app runs on the PaaS over HTTPS + a real domain; migrations run as a release step; the DB has automatic backups.
10. **Multi-template onboarding** — a new user picks a level template and gets their own campaign.
11. **Page performance** — meets the page-speed threshold set (note the debt: App.jsx fires ~10 parallel API calls on load, and many endpoints run `refresh_progress_state`).
12. **Accessibility + responsive** — works well on mobile + meets basic a11y (continuing the in-progress `ui_mobile` work).

---

## 3. Must-fix blockers for production (Phase 1, high priority)

Ordered by danger if published as-is:

| # | Must-fix | Codegraph evidence | Consequence if skipped |
|---|---|---|---|
| 1 | **Multi-tenant data isolation** | `get_active_player().first()` (services.py:235); ~123 routes, 137 player-resolve call sites | Cross-account data leak |
| 2 | **JWT secret fail-fast + PyJWT** | hardcoded default (auth_utils.py:8); hand-rolled hmac | Forge tokens → take over any account |
| 3 | **Disable dev endpoints + hardcoded seed in prod** | `/api/dev/reset` unauthenticated (main.py:1510); `ad00000@gmail.com` (seed.py:925) | One request wipes the whole DB for all users |
| 4 | **Access token → httpOnly cookie + CSRF** | localStorage (client.js:3) | XSS harvests tokens at scale |
| 5 | **Email verify + forgot-password + email infra** | `email_verified_at` exists but is dead (models.py:25); no SMTP | Spam accounts; users lose their account when they forget the password |
| 6 | **Global rate limit (strict auth) + CORS from config** | only login has lockout (main.py:575); CORS hardcodes the old IP (docker-compose.yml:30) | Bots spam register → burn email credit; wrong CORS |
| 7 | **Pydantic Settings + .env.example + compose.prod** | secrets/hosts hardcoded in compose; no ENV flag | Foundation for #2/#3/#9; without it there is no dev/prod split |
| 8 | **Migration release step + no seed in prod** | auto-migrate + seed on every startup (main.py:443) | Migration race when scaling; junk seed in prod |

---

## 4. Phased roadmap

### Phase 1 — SaaS foundation (goal: meet all 12 DoD criteria)
A 3–6 month / one-developer project. Split into two sub-milestones for a mid-point checkpoint:

**P1a — Security & infrastructure triage** (do FIRST, no feature dependency)
- Pydantic Settings + `.env.example` + an `ENVIRONMENT` flag + `compose.prod` (must-fix #7).
- JWT → PyJWT + fail-fast secret; sweep all default passwords (#2).
- Disable `/api/dev/*` + the hardcoded seed by ENV (#3).
- Access token → httpOnly cookie + CSRF (change `apiFetch` to drop the Bearer header, change `get_current_account` to read the cookie) (#4).
- Global rate limit (slowapi) + CORS from config (#6).
- Split migrations into a release step, no seed in prod (#8).
- GitHub Actions CI runs the existing 68 tests + lint, green on `main` (DoD #7).
- Sentry BE + FE + wired healthcheck + structured logging + UptimeRobot (DoD #8).
- **Exit criteria for P1a:** secret fail-fast, no backdoor, safe tokens, rate limit, CI green, observability — all verifiable.

**P1b — Make every feature multi-tenant** (after P1a)
- **Fix at the root:** remove the `get_active_player().first()` variant, make every resolve require an account; standardize all routes onto `get_current_player` / `get_current_campaign` (#1). Let the compiler/runtime surface every caller not yet fixed.
- **Strict cross-account test:** two accounts, sweep every route, assert no leak — runs in CI (#1, DoD #7).
- Email verify + forgot/reset password + email-service integration (#5).
- Multi-template onboarding: code to pick a template by level + author content per template (**the content authoring is a large manual effort, tracked separately from code**) (DoD #10).
- Page speed: set a threshold + reduce on-load API calls / cache `refresh_progress_state` (DoD #11).
- A11y + responsive: finish mobile, meet basic a11y (DoD #12).
- **Exit criteria for P1b = Phase 1 exit:** all 12 DoD criteria green → open sign-up to strangers.

### Phase 2 — Expansion (after real users exist)
- Deep roadmap personalization (an engine that generates quests/plans per user).
- Real SRS (SM-2, using `ease_factor`).
- A staging environment before production.
- New learning features driven by user feedback.
- **Exit criteria:** personalization + safe staging in place; measurable retention.

### Phase 3 — Scale (when real traffic / a business need arises)
- Billing (Stripe), paid tiers.
- Scale optimization: fix `refresh_progress_state` (runs on every GET), connection pool, indexes, read replicas if needed.
- Thousands of concurrent users.
- **Exit criteria:** sustains the target load + has revenue.

---

## 5. ADRs (recorded under docs/current/decisions/)

`ADR-001` already exists. New ADRs start at **ADR-002**:

- **ADR-002 — Multi-tenancy: shared DB, row-level scoping by `account_id`.** Decided on public multi-tenant SaaS; fix the data-access layer at the root; do NOT use instance-per-customer.
- **ADR-003 — Deploy target: Managed PaaS (Render/Railway) + GitHub Student credit.** Cost-vs-ops trade-off; rejected self-managed VPS and serverless. Note: confirm the current Student offer before locking the provider.
- **ADR-004 — Auth: PyJWT + fail-fast secret + access token in an httpOnly cookie + CSRF.** Replaces the hand-rolled JWT; leaves localStorage.
- **ADR-005 — Config: Pydantic Settings + an `ENVIRONMENT` flag as the central switch** (dev endpoints / seed / cookie Secure / fail-fast).
- **ADR-006 — Migrations: a separate release step, NOT auto-migrate/seed in `on_startup` in production.**

---

## 6. Risks & deferrals

| Deferred | To | Why |
|---|---|---|
| Per-user roadmap personalization | Phase 2 | A separate product; needs an engine + content, not infrastructure |
| Real SRS (SM-2) | Phase 2 | The current SRS is "fake" but usable; improving it doesn't block production |
| Billing | Phase 3 | No paying users |
| Scale to thousands + `refresh_progress_state` | Phase 3 | The bottleneck does not exist yet; optimizing early is waste |
| Staging | Phase 2 | Few users; accept auto-deploy straight to prod early on |

**Biggest (non-technical) risk:** Phase 1 is a 3–6 month single-developer project with "keep all
features" → **burnout / abandonment mid-way**. Mitigated by: the P1a/P1b split with a checkpoint,
P1a being independently shippable (the app is safe even before full multi-tenant content), and not
opening public sign-up until all 12 criteria are met.

---

## 7. Verification (per must-fix, when executing the roadmap)

- **Isolation (#1):** automated cross-account test in CI — create two accounts, sweep every route, assert no leak. The single most important test in the project.
- **Secret fail-fast (#2):** run the app without `JWT_SECRET_KEY` set → it must crash with a clear message.
- **No backdoor (#3):** with `ENVIRONMENT=production`, call `/api/dev/reset` → 404.
- **Cookie + CSRF (#4):** log in → the access token does not appear in localStorage (DevTools); a request missing the CSRF token is rejected.
- **Email (#5):** register → receive a real verification email; forgot → reset works.
- **Rate limit (#6):** spam `/auth/register` past the threshold → blocked.
- **CI (#7):** every PR runs the tests green; all 68+ tests pass.
- **Observability (#8):** throw a deliberate error → it appears in Sentry; the PaaS restarts when `/api/health` fails.
- **Deploy (#9):** push `main` → PaaS auto-deploys over HTTPS; migrations run once at release; the DB has snapshots.
