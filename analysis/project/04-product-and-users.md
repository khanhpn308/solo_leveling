# 04 — The product as it exists today, and its users

Answers mission questions **1** (what the product actually does for its users) and **2** (who those
users and roles are). Describes current state only. Evidence convention and repo state are in
`README.md`; structural facts referenced here are established in `01`/`02`.

---

## 1. What the product is

`README.md:1-3` states the product plainly: *"Local IELTS Academic self-study dashboard with a
game-style progression loop."* The code corroborates that framing in three ways that are worth
separating from the docs' claims, because they are what the running system actually does:

1. **It is single-user and local by construction.** The entire runtime is one compose file with three
   containers, two published HTTP ports, no TLS, no proxy and no external service
   (`docker-compose.yml:1-56`; `02-current-architecture.md` §2). There is no admin console, no
   sharing, no export, no import.
2. **It is a tracker of an externally-authored study plan, not a content platform.** The curriculum
   is *not* in the database as authored content — it is parsed at boot from markdown on disk:
   `material/material.md` for the 78-week roadmap and main quests
   (`backend/app/seed.py:557-578`, `parse_material_plan` `:596`), the polished collocation file
   (`seed.py:2061-2085`, `parse_collocations_file` `:2087`), and
   `material/vocabularies/**/vocab.md` (`seed.py:2543-2559`, `parse_vocab_file` `:2403`). The product
   *schedules, scores and gamifies* study that the user does elsewhere.
3. **It is a closed loop the user drives by hand.** Every state change originates from a click; there
   is no realtime channel, no background job, and no notification delivery
   (`01-discovery-inventory.md` §7). The client loads its six datasets once per mount
   (`frontend/src/App.jsx:169-176`).

### 1.1 The loop the code implements

Read from `frontend/src/App.jsx` (the shell) plus the two UI panels that drive most actions:

```
1. Campaign exists      onboarding wizard → POST /api/onboarding/activate-campaign
                        pages/Onboarding.jsx:56-62 → api/auth.js:36-50 → backend/app/main.py:707-762
2. Daily quests appear  GET /api/summary + GET /api/quests   (App.jsx:379-381)
                        generated server-side from per-skill quotas (seed.py:1332-1413)
3. User studies, then clicks COMPLETE     POST /api/quests/{id}/complete   (App.jsx:508-510)
4. XP is NOT banked     explicit second step: POST /api/quests/{id}/claim  (same call site,
                        `action` variable); the button label walks COMPLETE → CLAIM → CLAIMED
                        (dashboard-data.js:428-455)
5. Claiming banks XP    toast "Reward claimed … banked +N XP" (App.jsx:361-378, 513-517)
6. Derived state recomputes on read       GET /api/summary → refresh_progress_state
                        (backend/app/main.py:766 → services.py:804-816)
7. Visible progression  level/rank in the top bar (HomeTopBar.jsx:28-35), skill matrix
                        (StatusModal.jsx:282-290), roadmap hero (App.jsx:858-864)
8. Suggestions appear   GET /api/rank-suggestions + /api/weakness-suggestions
                        (App.jsx:462 → 462-468), surfaced in the top-bar inbox
                        (HomeTopBar.jsx:37-48)
9. Optional side loops  check-ins (App.jsx:588-597), badges, boss battles, rank exams,
                        vocabulary + collocation practice
```

The "reward claim gates XP banking" rule is deliberate, not incidental: it is recorded as an accepted
decision in `DECISIONS.md` ("Reward claim gates XP banking", 2026-06-05) and again in
`docs/current/BUSINESS_RULES.md` §"Reward Claim Rule". The code matches it — `markQuestRewardClaimed`
is what fires the success animation and toast (`App.jsx:369-378`), and `getQuestActionMeta` returns
the `claim` action only when `completed && !rewardClaimed`
(`frontend/src/dashboard-data.js:440-448`).

### 1.2 What the product measures

- **Two XP currencies, both ledgered.** Player XP (`players.player_xp`, `players.total_xp`) and
  per-skill XP (`campaign_skill_states.xp`, journalled in `skill_xp_transactions` /
  `player_xp_transactions`). The curve is `xp(L) = round(19·(L^1.6 − 1))` for L 1..60
  (`backend/app/services.py:74-77`), and rank F→S is derived from that level
  (`services.py:131-141`).
- **Five "matrix" skills count toward the player total; two are support-only.**
  `MATRIX_SKILLS = {Listening, Reading, Writing, Speaking, Vocabulary}` and
  `SUPPORT_ROUTING = {Grammar → Writing, Collocation → Vocabulary}`
  (`services.py:469-478`); the frontend mirrors this grouping with the labels `Core` vs `Support`
  (`frontend/src/dashboard-data.js:9-17`).
- **Commitment mechanics**: streak and best streak, a shield with regen progress (2 max)
  (`models.py:138-143`; rendered as stat cards `App.jsx:834-853`), and a daily check-in of
  mood / energy / focus / note (`App.jsx:575-583`).
- **Pressure mechanics**: quests expire rather than going "overdue" — `getQuestStatus` returns
  `expired` for any past-date incomplete quest (`dashboard-data.js:398-406`), and `getCompletionMode`
  only ever returns `'on_time'` (`:407-410`). `TASKS.md:20` confirms this was intentional:
  *"Backlog quest feature: fully removed. Past-date quests expire immediately (no overdue state, no
  50% XP)."*

### 1.3 Product-level design constraints that are visible in code

The game flavour is not decoration bolted on — it is the vocabulary of the domain model and of the
UI copy: skill **ranks** `F`–`S`, **promotion status**, **boss battles**, **badges**, a **Lexical
Codex**, an **Error Dungeon**, **Shadow Duel**, **Echo Chamber**, **Word Family Evolution**, and a
"System Overlay" header motif (`frontend/src/components/OverlayFrame.jsx:31-33`) with
`SYSTEM LOADING...` / `SYSTEM GATE CLEARED` boot and result screens
(`App.jsx:775`, `RankExamResultScreen.jsx:11-16`).

---

## 2. Who the users are

### 2.1 The declared target user

`README.md:5-6` fixes the campaign start at `2026-06-04` and an 18-month horizon.
`docs/current/PROJECT_CONTEXT.md:5-15` declares the profile:

> current level around `B1`; strongest area: Listening; weaker area: Reading, especially vocabulary
> range and long-sentence comprehension; long-term target: IELTS Academic `7.0-7.5`.

`AGENTS.md:5-7` restates it as "the user", singular. Every preference default points the same way:
`AccountPreference(locale="vi", timezone="Asia/Ho_Chi_Minh", theme="dark",
notification_enabled=True)` on registration (`backend/app/main.py:504-510`) and in seeding
(`seed.py:1835-1842`), and `PlayerLearningProfile(preferred_learning_style="mixed",
dictionary_mode="bilingual_first", native_language="vi", interface_learning_language="mixed")`
(`main.py:512-520`). `[DERIVED]` The product is built for one Vietnamese-speaking IELTS candidate on
one machine, and the schema's multi-account shape is provisioned but unexercised (see `03-unresolved.md`
U-03).

### 2.2 The role model that exists in code

There is exactly **one role**, and it is not enforced:

| Concept | Where it lives | Is it used? |
| --- | --- | --- |
| `accounts.role` (`String(30)`, default `"user"`) | `backend/app/models.py:22` | Written at registration (`main.py:485`) and in two seeders (`seed.py:918`, `:933`); **never read** anywhere (`01-discovery-inventory.md` S-9). No route, dependency or service branches on it. |
| `accounts.status` (`active` / `locked`) | `models.py:21` | Enforced — `get_current_account` raises 403 when `status != "active"` (`main.py:254-258`), and login sets `locked` after 5 failures (`main.py:562-565`). |
| `account_preferences` | `models.py:94-103` | Written on registration; never read by any route that was opened. `[UNRESOLVED]` U-20. |
| No `admin`, `teacher`, `student`, `owner` or membership concept | — | No role, scope, permission table, or authorization check exists in `backend/app/` (absence search in `03-unresolved.md` §5). |

So the only two actor distinctions the system actually enforces are **authenticated vs not** and
**active vs locked**.

### 2.3 The lifecycle states a single user passes through

Reading `ProtectedRoute.jsx`, `AuthProvider.jsx`, `main.py:678-762` and `pages/Onboarding.jsx`, one
human moves through five states, three of which are enforced by redirects:

| # | State | How it is represented | How the user moves on | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Anonymous | no `localStorage` token | `POST /api/auth/register` or `/login` | `AuthProvider.jsx:15-19`; `ProtectedRoute.jsx:9` → `/login` |
| 2 | Registered, un-onboarded | `Account.onboarding_completed = false` | complete the 5-step `/onboarding` flow | `ProtectedRoute.jsx:11` → `/onboarding`; `main.py:753-754` sets the flag |
| 3 | Active campaign owner | `Account.onboarding_completed = true`, `Player.active_campaign_id` set | use the dashboard; nothing else is gated | `main.py:739-761`; `MainQuestMapPanel`/`App.jsx` render unconditionally |
| 4 | Rank-promotion candidate | `CampaignSkillState.promotion_status ∈ {eligible, boss_required, in_progress, passed}` | unlock then pass a rank exam | `services.py:789-798`, `:1440-1460`; `RankBossNotif.jsx:6-8` |
| 5 | Locked (reversible) | `Account.status = "locked"`, `locked_until` | retry after 15 minutes | `main.py:553-557` |

`[DERIVED]` Because state 3 is never re-checked, a user whose campaign is later closed or whose
account loses its player would hit 404s from `get_current_player`/`get_current_campaign`
(`main.py:270-306`) rather than being redirected anywhere — there is no error route, only the
`API ERROR:` boot screen (`App.jsx:771-773`).

### 2.4 Onboarding: what a new user is actually asked for

`frontend/src/pages/Onboarding.jsx` is a five-step wizard driven by a local `step` counter
(`:38-43`), not by routes:

| Step | Component | Asks for | Sent where |
| --- | --- | --- | --- |
| 1 | `StepWelcome` `:143-168` | display name (optional, `maxLength=40`) | `display_name` |
| 2 | `StepTarget` `:170-200` | target band per skill — 5 selects, each `4.0`…`9.0`, default `6.5` | `target_overall/listening/reading/writing/speaking_band` |
| 3 | `StepCampaign` | campaign template choice | `campaign_template_code` |
| 4 | `StepStartDate` | campaign start date, defaulting to today | `start_date` |
| 5 | `StepConfirm` | review + submit | `POST /api/onboarding/activate-campaign` |

Two facts about step 3 that matter for a reader checking this against the code: the template list is a
**single-element hardcoded array** with one option marked `recommended: true`
(`Onboarding.jsx:24-33`), and the backend defaults to that same code when the field is omitted
(`main.py:730`, `"ielts_18_month_foundation"`). `[DERIVED]` The "choose a campaign" step has no
choice today.

The server side of activation is not a thin write: it re-labels the player, persists all five target
bands, creates the campaign, back-links any pre-existing certificate records to it, generates rank
suggestions from those certificates, sets `onboarding_completed`, commits, and then recomputes the
whole progression state (`main.py:707-762`).

---

## 3. What the product deliberately is *not*

Each of these is an absence, verified by the scan named in `03-unresolved.md` §5 rather than by
reading a file:

- **Not multi-user-facing.** No user list, no switching, no invitation, no sharing, no leaderboard,
  no social or comparative surface of any kind.
- **Not a teacher/student product.** No assignment, review, grading or feedback-exchange concept; the
  only grading in the system is automatic (`services.py:2999`, `main.py:1815`).
- **Not a planner/authoring tool.** The curriculum arrives as markdown on disk; there is no UI to
  add a phase, quest template, skill or material.
- **Not a delivery channel.** `notification_enabled` exists as a preference
  (`main.py:506`) but nothing sends anything anywhere; feedback is in-app toasts
  (`App.jsx:342-364`) and inline banners only.
- **Not an assessment product.** Rank exams are MCQ-or-free-text
  (`RankExamScreen.jsx:157-193`) mixed with free text, and Writing/Speaking promotion bosses are
  explicitly deferred as out of scope in `DECISIONS.md` ("Subjective Rank Bosses … deferred").

---

## 4. Language of the product

`docs/current/PROJECT_CONTEXT.md:41` and `AGENTS.md:34` both assert the frontend is English-first,
and `AGENTS.md:33` requires repository documentation in English. The code is **mixed**, and the
Vietnamese is not incidental:

| Surface | Language | Evidence |
| --- | --- | --- |
| Login / Register / Onboarding pages | Vietnamese | `pages/Login.jsx:35,39,42,51,58`; `pages/Register.jsx:35,39,42,52,58`; `pages/Onboarding.jsx` (17 Vietnamese strings) |
| Status modal logout button and target section | Vietnamese | `StatusModal.jsx` ("Mục tiêu IELTS", "Đăng xuất", "Đã lưu", "Đang lưu…") |
| Dashboard, quests, overlays, vocabulary workspace | English | `OverlayFrame.jsx`, `QuestOverlay.jsx`, all 10 vocabulary modules |
| Host clock format | Vietnamese locale | `App.jsx:36-44` (`Intl.DateTimeFormat('vi-VN', …)`) |
| Two seed test-evidence strings | English | `dashboard-data.js:19-22` |

`[DERIVED]` The pattern is chronological rather than intentional: the auth/onboarding shell and the
status modal were written against Vietnamese copy, the later dashboard and vocabulary surfaces in
English. Only 5 of 53 source files contain Vietnamese diacritics.

---

## 5. Product statements in docs that the code contradicts

Listed because a second engineer reconciling this audit against `docs/` will hit them. Each is a
doc-vs-code disagreement, not a judgement about which is right.

| Doc claim | Code reality | Evidence |
| --- | --- | --- |
| `PROJECT_CONTEXT.md:41` "the frontend is already in an English-first state" | 5 of 53 source files are Vietnamese; the whole auth + onboarding entry path is Vietnamese | §4 above |
| `PROJECT_CONTEXT.md:30-37` lists "error log / writing tracker / speaking tracker / mock test tracker" among Main Feature Surfaces | The backend implements all four (`main.py:1383-1460`); **no frontend component calls any of them**, and the only component that renders them (`TrackersPanel.jsx`, which also carries `TRACKER_MODULES` with statuses `Ready`/`Preparing`) is imported by nothing | `03-unresolved.md` U-10; `06-domain-capability-inventory.md` §3 D-09 |
| `TASKS.md:16` describes onboarding as "5-step UI (Name → Campaign → StartDate → **Certificate** → Confirm)" | Step 2 is **target bands**, not certificate entry; the certificate step does not exist in the wizard, and `postManualCertificate` is dead code | `Onboarding.jsx:24-33,170-200`; `api/auth.js:29-34` |
| `DECISIONS.md` (2026-06-08) "401 handling → immediate logout (no silent refresh)" | Silent refresh-then-retry is implemented in the API client | `frontend/src/api/client.js:17-45` |
| `DECISIONS.md` (2026-06-08) "Token storage → localStorage. httpOnly cookie deferred" | The refresh token **is** in an httpOnly cookie (`ielts_rt`) | `main.py:452-462`; `TASKS.md:16` records the later migration |
| `MOBILE_RESPONSIVE_PLAN.md` A4/Task 2 says the vocab sidebar has "11 nav tabs" | There are **10** nav buttons plus a 3-way flashcard sub-tab | `VocabularyWorkspace.jsx:532-605`; `06-domain-capability-inventory.md` D-11 |
| `README.md:26` and `AGENTS.md` describe the repo as runnable via `docker compose up --build` on ports 5173/8000/3307 | Consistent, but the committed `frontend/dist/` is served by nothing and the containers run both dev servers | `01-discovery-inventory.md` §8 |
