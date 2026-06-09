# Plan: Deterministic per-account demo Player + idempotent seed + neutral name fallback (backend-only)

## Context

Logging in as `ad00000` shows the hardcoded name **"IELTS Hunter"** instead of a real name. Investigation confirmed the draft's root-cause analysis on the backend, **and surfaced a blocker the draft missed**:

**Root cause (confirmed):**
- `seed.py:853 ensure_player()` queries `Player.first()` — a nondeterministic "orphan" Player that carries the full sample Campaign + Quest data — then `seed.py:1700 ensure_account_and_profile()` links that Player to `ad00000@gmail.com` via `player.account_id = main_account.id` (line 1760). The Player's name/display_name is hardcoded `"IELTS Hunter"` (lines 858, 863).
- `seed_database()` runs on **every app startup** (`main.py:358-364`), not just `/api/dev/reset`. So if real registered accounts already exist, `Player.first()` can return a **real user's** Player, attach the demo Campaign/Quests to it (`ensure_campaign`), and link it to ad00000 → cross-account data corruption.
- `register()` (`main.py:408,417-418`) hardcodes `"IELTS Hunter"` as the display-name fallback.
- `activate-campaign` (`main.py:635`) takes no body — no way to set a name or choose a campaign.
- Already correct (no change needed): `Player.account_id` is unique-per-account; `activate_campaign_for_player()` (`seed.py:1988`) already accepts `template_code` and is idempotent; `dashboard-data.js:658 buildPlayerSnapshot` already prioritizes `profile.display_name`.

**Blocker found — working tree is half-migrated and cannot boot:**
A prior session modified `main.py`, `main.jsx`, `App.jsx` to wire in an auth/onboarding layer, but the imported files **do not exist anywhere in this clone** (likely untracked locally, not pushed):
- `backend/app/auth_utils.py` (imported `main.py:12`) → **backend won't import / uvicorn won't start**.
- `frontend/src/auth/AuthProvider.jsx`, `auth/ProtectedRoute.jsx`, `api/client.js`, `api/rankExam.js`, `pages/{Login,Register,Onboarding}.jsx` → **Vite won't build**.

**Decision (user):** Do **backend-only** now. The grounded backend changes are made and statically verified here; the frontend Onboarding/campaign-selection work is handed off as a written spec to apply once the missing files are restored. **Runtime verification (uvicorn, `/api/dev/reset`, `/api/summary`) is not possible in this clone** because `auth_utils.py` is absent — see Verification.

## Goal

Make the demo Player **deterministic and idempotent**: always the Player owned by `ad00000@gmail.com`, never a random `Player.first()`. Seed never touches real users' Players. Remove the `"IELTS Hunter"` hardcode from registration. Let `activate-campaign` optionally accept a display name + campaign code so the (future) Onboarding UI can set them.

## Out of scope

- Creating the missing `auth_utils.py` or any frontend file (user chose backend-only).
- New schema migrations — all needed columns (`account_id`, `display_name`, `campaign_template_id`) already exist.
- Multi-campaign seeding (only the existing single template) — recorded as a deferred task.
- Auth/JWT/refresh flow; StatusModal layout.

## Seed flow: before → after

```
BEFORE (nondeterministic, corruption-prone)
  seed_database
    ├─ ensure_player ── Player.first()  ← may return ANY player (incl. real user)
    ├─ ensure_campaign(player)          ← attaches demo Campaign/Quests to that player
    └─ ensure_account_and_profile(player)
          ├─ create dev + ad00000 accounts
          └─ player.account_id = ad00000.id   ← links whatever .first() returned

AFTER (deterministic, idempotent)
  seed_database
    ├─ ensure_player
    │     ├─ ensure_demo_account() ──────────────┐ create/return ad00000 (+dev)
    │     ├─ Player.filter(account_id==ad00000)  │ find demo player by account
    │     └─ if none: create Player(account_id=ad00000)  ← linked at creation
    ├─ ensure_campaign(player)          ← demo data always on ad00000's player
    └─ ensure_account_and_profile(player)
          ├─ ensure_demo_account() (idempotent)
          ├─ AccountPreference + PlayerLearningProfile
          └─ (no account_id reassignment — already linked)
```

## Steps (backend)

### Step 1 — `seed.py`: extract `ensure_demo_account`, make `ensure_player` deterministic
**File:** `backend/app/seed.py`

- Add helper `ensure_demo_account(db: Session) -> Account` containing the dev + ad00000 account-creation logic currently inside `ensure_account_and_profile` (`seed.py:1701-1731`). Idempotent (query by `email_normalized` first). Return the `ad00000@gmail.com` account.
- Rewrite `ensure_player(db, start_date)` (`seed.py:853`):
  - `demo_account = ensure_demo_account(db)`
  - `player = db.query(Player).filter(Player.account_id == demo_account.id).first()`
  - if found → `return player` (preserves a name the user may have set; no overwrite).
  - else → create the demo Player exactly as today but add `account_id=demo_account.id`. Keep `"IELTS Hunter"` as the seed default name **only** for this freshly-created demo player (acceptable: it's the demo account's initial name, overwritable via onboarding/rename).
  - **Remove `Player.first()` entirely.**

### Step 2 — `seed.py`: simplify `ensure_account_and_profile`
**File:** `backend/app/seed.py:1700`

- Replace the inline dev/ad00000 creation with `main_account = ensure_demo_account(db)`.
- Keep `AccountPreference` and `PlayerLearningProfile` creation (lines 1734-1757).
- **Remove** `player.account_id = main_account.id` (line 1760) — the Player is already linked in `ensure_player`.
- Return `main_account`.
- Call order in `seed_database` (`seed.py:1957`) is unchanged: `ensure_player` now self-bootstraps the account, and `ensure_account_and_profile` stays idempotent.

### Step 3 — `main.py`: neutral register fallback (drop "IELTS Hunter")
**File:** `backend/app/main.py:404-418`

- Compute once: `name = (account_in.display_name or "").strip() or email_normalized.split("@")[0] or "New Hunter"`.
- Use `name` for both `Account.display_name` and `Player.name`/`Player.display_name`. No `"IELTS Hunter"`.
- Leave ORM defaults in `models.py` untouched (register/onboarding always set a name).

### Step 4 — `main.py` + `schemas.py`: `activate-campaign` accepts optional name + campaign code
**Files:** `backend/app/schemas.py` (near `AccountRegisterIn`, ~line 900), `backend/app/main.py:635`

- Add schema:
  ```python
  class OnboardingActivateIn(BaseModel):
      display_name: str | None = None
      campaign_template_code: str | None = None
  ```
  Import it in `main.py`'s schema import block.
- Change the route signature to accept an optional body (backward-compatible — current callers send none):
  `def activate_campaign(body: OnboardingActivateIn | None = None, account=Depends(...), db=Depends(...))`.
- In the body: if `body and body.display_name and body.display_name.strip()` → set `player.display_name = player.name = body.display_name.strip()`.
- Pass the code through: `template_code = (body.campaign_template_code if body else None) or "ielts_18_month_foundation"`, then `activate_campaign_for_player(db, player, template_code=template_code)`. (Function already defaults to the same code, so existing behavior is preserved.)

### Step 5 — `TASKS.md`
- Mark in progress/done: "Deterministic per-account demo Player + idempotent seed + neutral register fallback + activate-campaign accepts name/campaign code (backend)".
- Deferred backlog: "Frontend onboarding name input + campaign selection (blocked on restoring `auth_utils.py` + frontend `auth/api/pages` layer)" and "Multi-campaign selection — seed N templates, choose 1 of N, persist `campaign_template_code`".

## Frontend handoff spec (NOT implemented — apply once missing files restored)

When `frontend/src/pages/Onboarding.jsx` and the `api/` layer exist again:
- Add a required **display name** input (state `displayName`) and a **campaign selection** step showing one card ("IELTS 18-Month Hunter Roadmap", code `ielts_18_month_foundation`), selected by default, rendered as a list so N campaigns can be added later.
- Add `activateCampaign(displayName, campaignCode)` to the onboarding API helper, POSTing `{ display_name, campaign_template_code }` to `/api/onboarding/activate-campaign` (now accepted by Step 4).
- `handleActivate` passes both, then `refreshAuth()` → `navigate('/')`.

## Verification

**Possible in this clone (do now):**
- Syntax-check the edited modules without importing third-party deps:
  `python -m py_compile backend/app/seed.py backend/app/main.py backend/app/schemas.py` → must succeed.
- Static review against the before/after diagram: confirm `Player.first()` no longer appears in `seed.py`, and `ensure_player` links `account_id` at creation.

**Blocked until `auth_utils.py` is restored + Docker up (document for the user):**
1. `docker compose up`; `docker logs ielts_quest_backend` clean (no ImportError).
2. Idempotency: `POST /api/dev/reset` twice → `SELECT count(*) FROM players` stable; ad00000 owns exactly one Player with the demo Campaign + Quests.
3. Demo account: login `ad00000@gmail.com` → `GET /api/summary` has sample data; `display_name` is the demo name (or the name set via rename/onboarding), never leaked as a random player's.
4. Isolation: register a new account → `POST /api/onboarding/activate-campaign` with `{"display_name":"Test User","campaign_template_code":"ielts_18_month_foundation"}` → `GET /api/summary` returns "Test User" with its own campaign; confirm its `player_id`/`campaign_id` differ from ad00000's and it sees none of ad00000's data.
5. Restart the backend with real accounts present → confirm no real Player gets the demo Campaign attached (the `Player.first()` corruption path is gone).

## Risks / notes

- `/api/dev/reset` deletes all Accounts **and** Players (`main.py:1386-1441`) then re-seeds, so there's no stale-`account_id` duplicate-player case; `ensure_player` recreates one demo Player cleanly.
- `activate-campaign` body is optional → existing/no-body callers keep working; `activate_campaign_for_player` stays idempotent (returns the existing active campaign if present).
- Registered accounts' Players remain empty until they activate a campaign — by design.
- Vocabulary/Flashcard/LearningProfile are scoped by `player_id` (not campaign); fine here since 1 account = 1 player. Flag for the future multi-campaign task.
- The backend cannot be run here (`auth_utils.py` missing); this plan delivers statically-verified code plus exact runtime steps the user runs after restoring the auth layer.
