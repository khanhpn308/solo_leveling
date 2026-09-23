# 08 — Data-flow traces and layer ownership

Answers mission question **9**: a traced data path from datastore through the service layer to the
endpoint, then through the frontend API client into the component that renders it, for the flows a
user actually exercises — with the duplicate fetches, the derived state that is recomputed or
written on read, and the places the client and server disagree about shape or naming named
explicitly.

Companion to `07-api-contract-reference.md` (mission question 8: the endpoint inventory). Evidence
convention and repo state: `README.md`. Current state only — no proposals, no target state.

---

## 1. The layer stack, as the code actually arranges it

Every trace below moves through the same seven steps. There are no other layers: no repository
abstraction, no serializers module, no state container, no cache, no query layer.

| # | Layer | File | What it owns |
| --- | --- | --- | --- |
| L1 | MySQL tables | `backend/alembic/versions/*` (31 revisions) | persistence |
| L2 | ORM models | `backend/app/models.py` (57 models) | column definitions, relationships |
| L3 | Domain/derivation | `backend/app/services.py` (3267 lines) | XP ledger, recompute chains, scoring, progression |
| L4 | HTTP routes | `backend/app/main.py` (2874 lines, 121 paths) | auth dependency, scoping, response assembly |
| L5 | Response schemas | `backend/app/schemas.py` | Pydantic output shapes (100 of 121 paths) |
| L6 | API client | `frontend/src/api/client.js` (78 lines) | base URL, bearer token, 401→refresh→retry |
| L7 | View models + render | `frontend/src/App.jsx` (1029 lines), `dashboard-data.js` (817 lines) | client-side derivation, then React components |

`[DERIVED]` A distinguishing property of this codebase is that **L3 is reachable from L4 in exactly
one direction and L7 re-implements a slice of L3**. Two derivation layers exist — the Python
services layer and the JavaScript `dashboard-data.js` module — and both classify the same domain
concepts (quest status, XP progress, level curve). §6 and §7 quantify where.

---

## 2. The precondition every trace shares — the session flow

Nothing in §3–§4 can run without this, and it is the only flow that exists before the dashboard.

```
Login.jsx → authApi.login() → POST /api/auth/login {email,password}      main.py:547
  → AccountLoginIn → TokenOut{access_token, expires_in, …}
  → client.setTokens(data.access_token) → localStorage['ielts_access_token']   client.js:3-10
  → authApi.getMe() → GET /api/auth/me → MeResponseOut                   main.py:678
  → AuthContext{account, onboardingCompleted}
```

- The token lives in `localStorage` under `ielts_access_token` (`client.js:3`), **not** in a cookie.
  `credentials: 'include'` is sent on every request (`client.js:44`) so the refresh cookie also
  travels.
- Cold start is `AuthProvider.hydrateFromToken` (`AuthProvider.jsx:13-28`): if a token exists it
  calls `GET /api/auth/me`; on failure it clears the token. `[DERIVED]` There is no local expiry
  check and no `storage` listener, so a second tab neither learns about a login nor a logout
  (`07` §7.1).
- **Every request goes through `App.jsx`'s `api` wrapper, not `apiFetch` directly**
  (`App.jsx:146-158`). On a 401 it retries once after a silent refresh (`client.js:49-64`) and, if
  the retry also fails, calls `logout()` + `navigate('/login')` and **returns `undefined` instead of
  throwing** (`App.jsx:152-155`). `[DERIVED]` Callers that assume a shaped response therefore
  receive `undefined` at exactly the moment the session dies; the loader catches do not fire,
  because nothing was thrown. `client.js:71` also sets `error.sessionExpired = true`, and a
  repo-wide grep shows **no consumer of that flag anywhere** — the signal is written and never read.

---

## 3. Read traces

### T-1 — Cold boot to first paint

```
main.jsx:12-31 (router) → ProtectedRoute → AuthProvider.hydrateFromToken
  → GET /api/auth/me                                    main.py:678 → MeResponseOut
  → Onboarding gate (account.onboarding_completed)
  → AppDashboard mount
  → App.jsx:169-176  fires SIX loaders in one effect
```

The six loaders and the exact endpoints each one calls:

| Loader | Endpoints | State set | Lines |
| --- | --- | --- | --- |
| `loadInitialData` | `/summary`, `/profile`, `/quests`, `/checkins`, `/vocabulary`ᵃ, `/flashcards/due`ᵃ | `summary`, `profile`, `quests`, `checkins`, `vocabularyItems`, `dueFlashcards` | `App.jsx:371-401` (Promise.all `:378-385`, setters `:387-394`) |
| `loadMainQuestData` | `/study-plan/weeks`, `/main-quests` | `studyPlanWeeks`, `mainQuests` | `App.jsx:403-422` |
| `loadWeeklyMission` | `/weekly-mission/current` | `weeklyMission` | `App.jsx:424-453` |
| `loadSuggestions` | `/rank-suggestions`, `/weakness-suggestions` | `rankSuggestions`, `weaknessSuggestions` | `App.jsx:455-474` |
| `loadCertificates` | `/test-records` | `testRecords` | `App.jsx:476-491` |
| `loadBossBattles` | `/boss-battles` | `bossBattles` | `App.jsx:493-501` |

ᵃ only these two carry `.catch(() => [])`; the other four reject into the loader's `catch`, which
sets `appError` and renders the `API ERROR:` boot screen.

**Thirteen loader requests on first dashboard paint**, plus `/auth/me` (14 on a cold start). Every
one of them carries a bearer token and resolves the campaign server-side.

### T-2 — `/api/summary`: the datastore→component trace in full

This is the deepest read trace in the product and the one the whole dashboard renders from.

```
L1  tables: quests, campaign_skill_states, badges, badge_unlocks, boss_battles, players
L2  models.py: Quest(390), CampaignSkillState(507), Badge(497), BadgeUnlock(576),
    BossBattle(643), Player(114)
L3  services.refresh_progress_state()  services.py:804-816   ← WRITES before reading (§6)
    └ get_active_player → expire_all → get_campaign_skill_state_map
    └ sync_quest_statuses          services.py:259-308  (4 bulk UPDATEs)
    └ recompute_weekly_missions    services.py:315-423
    └ recompute_skill_progress × N services.py:681-803
    └ recompute_badges             services.py:424-479
    └ recompute_player_progress    services.py:480-552
    └ db.commit()
L4  GET /api/summary   main.py:764-831
    calls refresh_progress_state FIRST (main.py:766), then
    4 SQL aggregates over Quest (today_xp, week_xp, completed, total),
    get_campaign_skill_outputs (main.py:357-396), get_campaign_badge_outputs (main.py:398-425),
    8 BossBattle rows
L5  SummaryOut — EXCEPT player: dict, which is an untyped hand-built dict (main.py:799-813)
L6  apiFetch('/summary') → JSON
L7  useState(summary)  App.jsx:377,383
    → view = buildDashboardView(summary, quests, checkins)   App.jsx:228
      dashboard-data.js:539-607
    → view.player / view.skills / view.quests / view.todayQuests / view.weeklyMission /
      view.commandDeck / view.summary / view.badges / view.bosses
    → rendered by CommandHeader, RoadmapHero, SkillRadarPanel, DailyQuestPanel,
      WeeklyMissionPanel, BossOverlay, StatusModal  (App.jsx:862-971)
```

Three things in that trace matter for a redesigner:

1. **The GET writes.** `refresh_progress_state` is invoked at the top of `get_summary`
   (`main.py:766`) and commits (`services.py:815`). Reading the dashboard mutates the database:
   quest statuses are re-classified, badges are re-granted, streak/shield/day counters are
   recomputed, and `player.player_xp` is overwritten.
2. **The response is assembled, not serialized.** `SummaryOut.skills` comes from
   `get_campaign_skill_outputs`, which additionally runs one SQL sum per support skill
   (`main.py:363-377`) to build a `support_breakdown` that the client renders as a tooltip.
3. **`player` has no schema.** `SummaryOut.player: dict` (`schemas.py`) while every sibling field is
   typed. `[DERIVED]` The client reads it defensively as a result (`dashboard-data.js:540-560`,
   `player.total_xp ?? 0`, `player.player_level ?? null`, `player.player_rank ?? 'F'`).

### T-3 — `/api/quests` and the client's second classification pass

`GET /api/quests` (`main.py:994-1032`) refreshes state, then filters `session_type == "Daily Quest"`
and — because the client passes no query params — defaults `start,end = current_week_window(player)`
(`main.py:1007-1008`). `[DERIVED]` **The dashboard is therefore a one-week window, not all history,
even though the client treats `quests` as the full quest list** (`buildDashboardView` filters
`quest.week_no === currentWeekNo` itself, and `App.jsx:806` counts unclaimed rewards across whatever
arrived).

Each row is serialized by `serialize_quest` (`main.py:291-335`) — 40 fields, including the
server-computed `status`, `earned_xp`, `reward_claimed`, `completed_mode`. The client then **recomputes
an overlay on the same concepts**:

| Server sends | Client recomputes | Client function |
| --- | --- | --- |
| `status` (`pending`/`completed`/`expired`) | `status` | `getQuestStatus` `dashboard-data.js:398-405` |
| `completed_mode` | `completionMode` | `getCompletionMode` `:407-410` |
| `earned_xp` / `base_xp` / `xp` | `earnedXp` | `getQuestEarnedXp` `:412-414` |
| `reward_claimed` | `rewardClaimed` | `isQuestRewardClaimed` `:416-418` |
| — | the button label + which action to POST | `getQuestActionMeta` `:428-459` |

`buildDashboardView` writes both sets onto the same objects (`dashboard-data.js:569-583`), so the
server field keeps its name and the client's version sits beside it under a camelCase name. The
renderer uses the client version (`App.jsx:963-966` passes `view.todayQuests`).

---

## 4. Write traces

### T-4 — Complete a quest (the primary user action)

```
DailyQuestPanel onClick → App.handleQuestAction(quest, 'complete')          App.jsx:502
  → api(`/quests/${quest.id}/complete`, {method:'POST', body: JSON.stringify({})})
L4  main.py:1048-1076 — campaign auth; scoped `Quest.id == quest_id AND campaign_id == campaign.id`
L3  services.complete_quest_instance()  services.py:818-866
      guard: future date → ValueError; status == 'expired' → ValueError
      resolve_tracker_payload()  ← tracker_type must match the quest, else raises
      quest.completed = True; quest.reward_claimed = False; quest.earned_xp = base_xp or xp
      quest.status = 'completed'; quest.completed_mode = 'on_time'
      db.flush() → refresh_progress_state(db)   services.py:863   ← NO player/campaign args
      db.refresh(quest)
L5  QuestOut (40 fields)  → the response body is returned to the browser
L7  App.jsx:508-531 — the body is read ONLY to merge `earned_xp` into local reward bookkeeping
      (App.jsx:511-513), then FOUR loaders are refetched with silent:true:
      loadInitialData + loadWeeklyMission + loadSuggestions + loadMainQuestData
      = 11 more HTTP requests to render state the server had already recomputed
```

Two notes:

- **The nested recompute loses the resolved identity.** `complete_quest_instance` calls
  `refresh_progress_state(db)` with no arguments (`services.py:863`), which falls back to
  `get_active_player(db)` = `db.query(Player).first()` (`services.py:235-240`). By contrast the claim
  route passes both explicitly — and says why:
  `# Pass player+campaign so recompute_player_progress targets the correct account`
  (`main.py:1132-1134`). The two write paths on the same quest therefore disagree about whether the
  recompute is account-targeted. `[UNRESOLVED]` whether this is observable with one player row
  (U-03/U-28).
- **Double work.** The response already contains the fully recomputed quest, and the client discards
  it and refetches 13 endpoints. See §5.

### T-5 — Claim a quest (the XP-banking step)

```
App.handleQuestAction(quest, 'claim')  App.jsx:508
L4  main.py:1091-1137
      guards: not completed → 400; already claimed → 400
      skill_blocked: promotion_status ∈ {boss_required, in_progress} → SKIP the award, do NOT set
        reward_claimed, and return the unchanged quest          main.py:1107-1117
      idempotency_key = f"quest_claim:{quest.id}"                main.py:1119
L3  services.award_skill_xp(db, campaign_id, target_skill_id, xp, idempotency_key)  services.py:1378-1415
      if a SkillXpTransaction with that key exists → return (idempotent no-op)
      else insert ledger row; state.xp += xp; state.rank, state.level = get_rank_level(state.xp)
    quest.reward_claimed = True → commit
    refresh_progress_state(db, player=player, campaign=campaign)   main.py:1135
L7  body read only for `earned_xp` (App.jsx:511-513); 11 refetch requests follow
```

`[DERIVED]` The XP ledger is the one place where a write is genuinely transactional and
idempotency-guarded — `award_skill_xp` is the only writer of `campaign_skill_states.xp`
(`services.py:1391-1415`), and it is `[DERIVED]` keyed by a deterministic string, so a double-click
cannot double-award. Everything else that the UI calls "XP" is *derived*, not accrued — see §7.2.

### T-6 — Claim the weekly mission

`App.jsx:557-579` → `POST /api/weekly-missions/{id}/claim` (`main.py:1164-1190`) → same
`award_skill_xp` with key `f"weekly_mission_claim:{mission.id}"` and
`transaction_type="weekly_mission"` (`main.py:1184-1186`) → `refresh_progress_state` → then the client
refetches `loadInitialData` + `loadWeeklyMission` (7 requests). `[DERIVED]` The comment
`# no else: player never receives XP directly` (`main.py:1187`) points at the deliberate design that
`award_player_xp` is a **no-op** (`services.py:1416-1424`).

### T-7 — Check-in

`App.jsx:581-608` → `POST /api/checkins` with `{checkin_date: getTodayISO(), mood, energy, focus, note}`
→ `main.py:1192-1218` upserts by `(campaign_id, checkin_date)` → `refresh_progress_state` (because
streaks and perfect-day counts read check-ins) → `CheckInOut` → client refetches `loadInitialData`
only (6 requests) → `view.commandDeck.activeCheckIn` picks today's row for the panel
(`dashboard-data.js:593-597`).

### T-8 — Rank exam: unlock → start → submit

```
App.jsx:641-683
  POST /api/rank-exams/unlock   main.py:1600-1622   → dict (no response_model)
  POST /api/rank-exams/start    main.py:1624-1728   → RankExamStartOut
        guards: promotion_status must be 'boss_required'; pending_rank + confirmed_rank required;
        ≤2 attempts/day per (campaign, skill, from_rank); an active RankExamPool row must exist
        picks a RankExamVersion not already used today; creates RankExamAttempt (expires_at =
        started_at + time_limit); sets promotion_status='in_progress'
        returns questions as RankExamQuestionOut{id, question_type, prompt, instruction, options_json}
  RankExamScreen.jsx:37-55  local answers map → payload [{question_id, answer_json}]
  POST /api/rank-exams/{attempt_id}/submit  main.py:1771-1878
        scoped attempt by id AND campaign_id (main.py:1777-1780)
        timed_out = expires_at < utcnow()
        per answer: is_correct = not timed_out and (ans_in.answer_json == q.correct_answer_json)
        score_percent = round(points/total_points*100, 2); passed = not timed_out and
          score_percent >= attempt.pass_percent
        on pass: confirmed_rank/rank ← to_rank, pending_rank=None, promotion_status='none',
          SkillRankHistory row inserted
        on fail with the daily cap hit: promotion_status='eligible' and a −50 XP penalty applied
          AFTER refresh_progress_state (main.py:1859-1866) so the recompute cannot undo it
  RankExamScreen auto-submits at 0 s (RankExamScreen.jsx:56-62); RankExamResultScreen renders
  RankExamSubmitOut
  App.jsx:681-683 then refetches loadInitialData + loadSuggestions
```

`[DERIVED]` The exam is the strictest contract in the product: the correct answers never leave the
server, scoring is server-side, and the pass threshold is stored per pool (`attempt.pass_percent`).
It is also the flow most damaged by the `question_type` mismatch recorded in `06` §D-11a and `07`
§6.1: the client's only MCQ branch tests `'mcq'` while the server emits `'multiple_choice'`, so every
question renders as a free-text box whose string cannot equal the stored answer.

### T-9 — Flashcard review: three separate mechanisms behind one UI word

`VocabularyWorkspace` exposes one "review" concept with three server implementations that share
nothing. This is the clearest example in the repo of the same user-facing noun working three ways.

| Card type | Endpoint | Server state | Scheduling rule | Client reads response? |
| --- | --- | --- | --- | --- |
| Codex vocabulary | `POST /api/flashcards/{card_id}/review` `main.py:1992` | new `SpacedRepetitionState` row per card | `interval_days = {again:0, hard:1, good:3, easy:7}`; sets `due_date`; `repetition_count += 1`; `flashcard.status` flips to `reviewing`/`active`; then `sync_node_status_from_item` (`services.py:1816-1857`) | **No** — response discarded (`VocabularyWorkspace.jsx:381-394`) |
| Vocab library | `POST /api/vocab-library/words/{item_id}/flashcard/review` `main.py:2805` | `familiarity` + `familiarity_set_at` columns on the `vocab_library_flashcards` row | set-and-decay: `effective_familiarity` drops one tier per 7 elapsed days, floored at `again`, `easy` never decays (`services.py:868-897`); no due date column | **No** (`:471-489`) |
| Collocation | `POST /api/collocations/{item_id}/flashcard/review` `main.py:2477` | `familiarity` + `familiarity_set_at` on `collocation_flashcards` | same 7-day decay as above, then `try_autocomplete_collocation_forge` (`services.py:1097-1152`) | **Yes** — reads `collocation_forge_autocompleted` (`VocabularyWorkspace.jsx:62-68`) |

The three "due" definitions are equally different: codex due = `due_date <= today OR status='new' OR
no state row` (`services.py:1798-1814`); vocab-library due = computed in the endpoint
(`main.py:2830-2870`); collocation has no due list at all — it is browsed by topic
(`main.py:2516-2567`).

### T-10 — Create a vocabulary item (a write that creates a second row)

`POST /api/vocabulary` (`main.py:1914-1919`) → `services.create_vocabulary_item`
(`services.py:1646-1694`) inserts a `VocabularyItem` **and then a `Flashcard`** built from it
(`card_type="meaning_recall"`, `front_text` = word + part of speech + IPA, `back_text` = EN/VI
meanings, `status="new"`). `[DERIVED]` There is no UI that creates flashcards directly, so
`POST /api/flashcards` (`main.py:1982`) has no caller (`07` §3.13) — every flashcard in the product
is a side effect of adding a vocabulary word. `VocabularyWorkspace.jsx:300-330` then calls
`onLoadData()` → `loadInitialData` → 6 refetches, i.e. `/vocabulary` and `/flashcards/due` are
re-fetched from inside the component that was handed both as props.

---

## 5. Where the same data is fetched twice

Measured from the loaders in §3 and §4. This is not incidental duplication — the client's refresh
strategy is "mutate, then re-read broadly", and the read sets overlap.

| Duplicate | Evidence |
| --- | --- |
| `/summary` + `/profile` both call `refresh_progress_state` and both expose overlapping player fields (`total_xp`, `player_rank`, `player_level`, `shield_count`, `perfect_day_count`) — two requests, one payload in practice | `main.py:766, 834`; `dashboard-data.js:646-676` merges them with `??` fallbacks |
| `/badges` returns what `/summary.badges` already contains | `main.py:1230-1234`; no client caller (`07` §4) |
| `/quests/today` returns the same rows as `/quests` (the client filters by `quest_date` locally) | `main.py:1034-1046`; `dashboard-data.js:497-506` |
| `loadInitialData` refetches `/vocabulary` + `/flashcards/due` while the vocabulary workspace holds them as props and calls `onLoadData()` (=`loadInitialData`) on open, on create, on close, and via `onProfileRefresh` | `App.jsx:788-798, 948`; `VocabularyWorkspace.jsx:251-256` |
| Every quest action refetches 4 loaders = 11 requests, of which `/summary`, `/profile`, `/quests`, `/checkins`, `/vocabulary`, `/flashcards/due` were the ones the action had just recomputed server-side | `App.jsx:526-531` |
| `loadWeeklyMission` has three call sites (mount, quest action, weekly claim), each one re-reading a mission the server recomputed during the write | `App.jsx:172, 528, 568` |
| Opening the vocabulary workspace refetches `/vocabulary` (already in parent state) *and* the parent's close handler refetches it again | `App.jsx:791-798` |

`[DERIVED]` A single quest completion round trip is therefore **1 write + 11 reads**, and a session
that completes 10 quests issues ~110 requests for 10 writes. Whether this is a deliberate simplicity
choice or unfinished optimisation is `[UNRESOLVED]` (U-32).

---

## 6. Derived state recomputed or written on read

### 6.1 `refresh_progress_state` runs on 8 GET routes

`refresh_progress_state` (`services.py:804-816`) is called from 32 route sites plus startup
(`main.py:438`). Eight of those are **plain GETs** — reading them writes:

| GET route | Line | What the read recomputes and commits |
| --- | --- | --- |
| `/api/summary` | `main.py:766` | all of §6.2 |
| `/api/profile` | `main.py:834` | all of §6.2, then `db.refresh(player)` |
| `/api/skills` | `main.py:908` | all of §6.2, then the skill tile list |
| `/api/main-quests` | `main.py:980` | all of §6.2 |
| `/api/quests` | `main.py:1007` | all of §6.2 |
| `/api/quests/today` | `main.py:1036` | all of §6.2 |
| `/api/badges` | `main.py:1232` | including badge recomputation |
| `/api/weakness-suggestions` | `main.py:1464` | including `ensure_weakness_suggestions` |

`[UNRESOLVED]` U-32: whether these eight read-side refreshes are load-bearing (i.e. whether anything
would diverge if they stopped) cannot be decided statically.

### 6.2 The recompute chain, and what each step overwrites

| Step | Function | Overwrites |
| --- | --- | --- |
| 1 | `sync_quest_statuses` `services.py:259-308` | 4 bulk `UPDATE`s on `quests`: `status='completed'`, `earned_xp = xp` backfill, `status='expired'` + `expired_at` for past incomplete quests, `status='pending'` reset for future ones |
| 2 | `recompute_weekly_missions` `services.py:315-423` | weekly mission item counters, statuses, completion |
| 3 | `recompute_skill_progress` × each state `services.py:681-803` | skill streak, `last_practiced`, weak point notes, promotion status transitions |
| 4 | `recompute_badges` `services.py:424-479` | inserts `BadgeUnlock` rows |
| 5 | `recompute_player_progress` `services.py:480-552` | `player_xp`, `total_xp`, `player_rank`, `player_level`, `current_streak`, `best_streak`, `shield_count`, `shield_regen_progress`, `perfect_day_count` |
| 6 | `db.commit()` `services.py:815` | persists all of the above |

`[DERIVED]` Consequences a redesigner must plan around:

- `quests.status` and `quests.earned_xp` are **caches of date-dependent computations**, refreshed
  only when some request happens to trigger step 1. Nothing schedules it — `[DERIVED]` if the app is
  left open overnight, the DB still holds yesterday's classification until the next request.
- `player.current_streak`, `shield_count` and `perfect_day_count` are recomputed by replaying every
  day from `campaign.start_date` to today on **every refresh** (`services.py:520-551`) — a loop whose
  cost grows with campaign age (548 days by design).
- Step 5 is why `award_player_xp` can be a no-op and why T-5's "player never receives XP directly"
  comment holds: `player_xp = round(mean of the 5 MATRIX_SKILLS xp values)`
  (`services.py:488-493`; `MATRIX_SKILLS` at `services.py:469`). Player XP is an *average of
  skills*, not a sum of awards.

### 6.3 Derived state the client recomputes on top

Computed in the browser on every render of the dashboard and never persisted or reconciled:

| Client derivation | Where | Server equivalent |
| --- | --- | --- |
| skill bar percent | `getSkillProgress(skill.xp)` `dashboard-data.js:461-467` | **none** — see §7.1 |
| player XP bar fraction | `getPlayerXpProgress(totalXp, level)` `:619-644` | level comes from the server; the fractional bar is client-only |
| quest status / mode / earned XP / claimed flag | `:398-418` | `status`, `completed_mode`, `earned_xp`, `reward_claimed` |
| actionable quest label and pending text | `getQuestActionMeta` `:428-459` | none |
| weekly mission percent + objective counts for the live path | `summarizeWeeklyMissionProgress` (called from `App.jsx:275`) | `WeeklyMission.status` + item counters |
| weekly mission **identity** when the live feed is absent | `getWeeklyPattern` + `WEEKLY_MISSION_PATTERNS` `:91-119, 493-495` | none — the pattern table exists only in the client |
| weakness suggestions on the summary card | `buildWeaknessSuggestions` `:508-536` | `/weakness-suggestions` (persisted, and separately rendered) |
| flashcard review "XP earned" | `VocabularyWorkspace.jsx:383-384, 861` | **none** — never awarded; see §7.3 |
| vocab boss score | `VocabularyBoss.jsx` computes and posts only `score_pct` | `submit_vocabulary_boss_result` accepts it (`services.py:2993-3046`) |

---

## 7. Where client and server disagree about shape or naming

### 7.1 The skill progress ladder exists only in the client, and it disagrees with the ranks

`dashboard-data.js:4` declares `const SKILL_XP_THRESHOLDS = [0, 500, 1200, 2500, 4500, 7000, 10000]`
and `getSkillProgress` (`:461-467`) turns `skill.xp` into the percentage that the skill radar renders
(`:566`). Verified by grep: **`1200`, `2500` and `4500` appear nowhere in `backend/app/`** — not in
`services.py`, `main.py`, `schemas.py`, `models.py` or `seed.py`. The server's own curves are
`_LEVEL_XP = [round(19*(L**1.6-1)) for L in 1..60]` (`services.py:77`) and `RANK_MIN_XP` derived from
it (`services.py:79-88`: F 0, E 862, D 2460, C 4604, B 7212, A 10234, S 13279).

`[DERIVED]` The two are not the same scale, and they disagree at the top end: the client bar
saturates at 10000, but rank **S** requires 13279. A skill with 10000 XP therefore renders a **full
bar while the server reports rank B** (10000 → `level_from_xp` = 50 → `rank_from_level(50)` =
`RANK_ORDER[4]` = `B`). The client shows the bar; the server owns the rank; there is no shared
constant between them.

The *player* level curve is the opposite case: `dashboard-data.js:611-638` re-derives the identical
formula in JavaScript with the comment `MUST mirror backend services.py:_LEVEL_XP`, and
`dashboard-data.js:1-2` documents that `PLAYER_RANK_THRESHOLDS` was deleted so rank/level come from
the backend. `[DERIVED]` One curve is deliberately duplicated, the other (skill XP) is a private
client invention with no server counterpart — and the frontend test suite asserts only the duplicated
one. Whether the skill ladder is intended is `[UNRESOLVED]` (U-31).

### 7.2 Three different things are called "XP"

| Name in UI | Source | Semantics |
| --- | --- | --- |
| "XP banked today" (`App.jsx:879`) | `summary.today_xp` | SQL sum of `Quest.earned_xp` where `completed AND reward_claimed` for today (`main.py:770-777`) — a **quest** total |
| Player level bar (`dashboard-data.js:674`) | `profile.player_xp` → `getPlayerXpProgress` | `round(mean(5 matrix skill XP))` (`services.py:488-493`) — a **mean** |
| Per-skill XP on the radar | `summary.skills[].xp` | the real ledger: `award_skill_xp` writes `SkillXpTransaction` + `state.xp` |
| `+{reviewXpEarned * 10}` in the review screen | `VocabularyWorkspace.jsx:861` | **nothing** — see §7.3 |

`[DERIVED]` Because one is a sum of scored quests and the other is a mean of skills, the two numbers
rendered adjacent on the dashboard move in different directions for the same user action: claiming a
quest increases skill XP and therefore the player mean, while `today_xp` counts the claimed quest
value; but `week_xp` and `today_xp` count *only* claimed quests, whereas `state.xp` includes rewards
from weekly missions and rank exams too. `[UNRESOLVED]` whether this is intended presentation or
accreted naming (U-30).

### 7.3 The review screen displays XP that is never awarded

`VocabularyWorkspace.jsx:383-384` computes `const xpEarned = {again:0, hard:1, good:2, easy:3}[result]`,
accumulates it in `reviewXpEarned`, and `:861` renders `+{reviewXpEarned * 10}` as a session total.
The endpoint it posts to is `POST /api/flashcards/{card_id}/review`, whose service
(`services.review_flashcard` `services.py:1816-1857`) only updates `SpacedRepetitionState` and
`flashcard.status`, then calls `sync_node_status_from_item`. **No XP row is written and no XP is
awarded**, and the response (`SpacedRepetitionStateOut`) is discarded. `[DERIVED]` The number is a
pure UI artifact that nothing reconciles against the ledger. Whether an award was ever intended is
`[UNRESOLVED]` (U-33).

### 7.4 Two sources of truth for the weekly mission, merged into one object

`/weekly-mission/current` supplies a persisted `WeeklyMission` with items (`main.py:1138-1162`), held
in `weeklyMission` state. `buildDashboardView` *also* synthesizes a `weeklyMission` object from
client constants (`dashboard-data.js:585-591`, pattern from `WEEKLY_MISSION_PATTERNS:91-119`,
`rewardXp: 50` hardcoded, `progress` counted from the client's quest array). `App.jsx:252-321` then
merges them: the real mission wins if present, and a `sourceLabel` of `'Live weekly sync'` vs
`'Pattern fallback'` records which one is being displayed (`App.jsx:309`). `[DERIVED]` The fallback
fabricates items with `current_count: 0, target_count: 1, status: 'Pending'`, so a client-side
pattern is rendered through the same component as server data and is only distinguishable by that
label.

### 7.5 One field name, two different id spaces

Both flashcard APIs call their identifier `id`, and the client uses the same expression `card.id` for
both:

| Client call | `card.id` means | Evidence |
| --- | --- | --- |
| `/flashcards/${card.id}/review` | the **flashcard** id | `VocabularyWorkspace.jsx:387`; `FlashcardOut.id` |
| `/vocab-library/words/${card.id}/flashcard/review` | the **vocabulary item** id | `VocabularyWorkspace.jsx:478`; `VocabFlashcardDueOut.id = item.id` (`main.py:2855`) |

`[DERIVED]` Both calls are correct — the endpoints genuinely address different id spaces — but the
shared field name makes them look interchangeable, and the same pattern appears a third time for
collocations (`/collocations/{item_id}/flashcard/review`, where the payload carries no id at all and
the item id is in the path). A redesign that unifies the review screen must resolve this naming
ambiguity first.

### 7.6 Shape gaps already measured in pass 3

- **21 of 121 paths declare no `response_model`** (`07` §6.1) — including
  `GET /api/vocabulary/boss/status`, whose nested `bosses[]` shape is read by `main.py:2228` and
  rendered by `VocabularyBoss.jsx` with no schema between them.
- **`SummaryOut.player` is a raw `dict`** (`07` §6.2).
- **One route's purpose is undocumented**: `POST /api/onboarding/activate-campaign` returns
  `{"detail": …}` while performing the most consequential onboarding write (`main.py:707-762`).
- **Aliased duplicates**: three handlers carry two decorators each (`main.py:1290-1291, 1307-1308,
  1325-1326`), which is why the OpenAPI document lists 121 paths for 118 functions.

---

## 8. Who owns each piece of state — the ownership table

The summary a redesigner needs: for each datum the UI shows, which layer is authoritative, whether
it is persisted, and whether the client keeps its own copy.

| State | Authoritative owner | Persisted? | Client copy? |
| --- | --- | --- | --- |
| Account identity, onboarding flag | `accounts` row via `/auth/me` | yes | context only |
| Campaign window / start date | `campaigns` + `players.start_date` | yes | `getCurrentWeekNo` re-derives the week number from `start_date` locally (`dashboard-data.js:469-484`) |
| Quest existence, dates, titles, `base_xp` | `quests` (seeded from markdown) | yes | no |
| `quest.completed` / `reward_claimed` | `quests`, written only by complete/claim endpoints | yes | `rewardClaimed` recomputed client-side |
| `quest.status` | server, **recomputed on read** | yes (as a cache) | recomputed again in `getQuestStatus` |
| `quest.earned_xp` | server, set on complete and backfilled on read | yes | recomputed in `getQuestEarnedXp` |
| Skill XP (the ledger) | `skill_xp_transactions` + `campaign_skill_states.xp`, written only by `award_skill_xp` | yes | displayed raw |
| Skill rank / level | server, derived from skill XP by `get_rank_level` | yes (denormalized) | not recomputed |
| Skill bar percent | **client only** (private ladder) | no | yes, and it is the only source |
| Player XP | server, derived mean of 5 matrix skills | yes (derived column) | bar fraction re-derived |
| Player rank / level | server | yes | consumed as-is |
| Streak / shields / perfect days | server, recomputed from quest history on every refresh | yes | no |
| Today/week XP counters | server, SQL over claimed quests | no (computed per request) | no |
| Badge unlocks | server, recomputed in refresh | yes | no |
| Boss battle rows / status | server (`/summary.boss_battles`, `/boss-battles`); claim route unwired | yes | `buildBossView` maps status | 
| Weekly mission (live) | `weekly_missions` + items, recomputed in refresh | yes | percent recomputed |
| Weekly mission (pattern) | **client only** (`WEEKLY_MISSION_PATTERNS`) | no | yes |
| Rank exam questions / answers / scoring | server (`rank_exam_*` tables) | yes | answers held in `useState`, lost on reload |
| Flashcard scheduling (codex) | server (`spaced_repetition_state`) | yes | no |
| Flashcard familiarity (library, collocation) | server (column + 7-day decay function) | yes | no |
| Review-session XP display | **client only, never persisted** | no | yes |
| Vocabulary boss score | computed by the **client**, accepted by the server | yes (as posted) | yes |
| Collocation/vocab collection progress | server (`player_collocation_progress`); no client caller | yes | no |
| Error/writing/speaking/mock trackers | server tables exist; no client caller | yes | no |

`[DERIVED]` The pattern in the table is that the server owns every *persisted* fact, while the client
owns a parallel set of *presentational* derivations — and in three places (skill bar percent, weekly
pattern, review XP) the client owns the fact itself because no server counterpart exists.

---

## 9. What could not be traced

- **Any runtime confirmation.** Nothing here was executed: no dev server, no container, no database,
  no request was issued. Every trace is a static reading of both sides of the wire; the caller/route
  match was verified mechanically (`07` §1), but no response body was ever observed. U-04 still
  applies.
- **Whether the double-fetch and read-write patterns are visible as latency.** U-19 (concurrency) and
  U-25 (partial-failure behaviour) remain open; the request counts in §5 are counts of call sites,
  not measurements.
- **Whether the client's private derivation tables ever agreed with the server.** No changelog,
  comment or test records a value for `SKILL_XP_THRESHOLDS` other than the current one; U-05 is
  narrowed here (see `03-unresolved.md` §G) but the *history* is not recoverable from the repo.
- **Whether the recompute-on-read frequency is load-bearing.** `[UNRESOLVED]` whether removing the
  8 GET-side refreshes would change any observable behaviour — that requires running the stack.
- **The four `/api/dev/*` and the unauthenticated collocation-collection writes** are traced
  structurally (`07` §3.10, §3.18) but were deliberately not exercised.
