# 06 — Product domains and capability inventory

Answers mission question **7**: the product domains and capabilities that exist today. Current state
only. Every capability is labelled with how reachable it actually is, and half-built / dead /
unreachable items are called out rather than smoothed over. Evidence convention is in `README.md`.

---

## 1. Method and status vocabulary

Two independent inventories were compared:

1. **Client surface** — all 53 files in `frontend/src`, the 62 normalised API paths they call
   (`grep -rn "api(\|apiFetch(" frontend/src`, every call site read), and the import graph that
   determines what can render at all (`05-frontend-routes-and-navigation.md` §4).
2. **Server surface** — the 121 routes in `backend/app/main.py` (MF-01) and the 72 tables (MF-09) /
   94 service functions behind them (`01-discovery-inventory.md` §5-6).

| Label | Meaning |
| --- | --- |
| **LIVE** | Reachable from navigation **and** backed by a working endpoint that the UI actually calls. |
| **HALF-WIRED** | Reachable, but the client and server do not agree — a call that cannot succeed, or a capability the UI cannot finish. |
| **BACKEND-ONLY** | Endpoint(s) exist and are functional; **no reachable UI** calls them. |
| **DEAD UI** | Component exists but nothing imports it, so it can never render. |
| **ABSENT** | Neither side implements it. |

---

## 2. Summary table

| # | Domain | Client surface | Server surface | Status |
| --- | --- | --- | --- | --- |
| D-01 | Identity & sessions | Login, Register, AuthProvider, client.js | 5 auth routes + 5 tables | **LIVE** |
| D-02 | Onboarding & campaign activation | 5-step wizard | 3 routes, rewrites target bands + creates campaign | **LIVE** |
| D-03 | Campaign & 78-week roadmap | RoadmapHero, MainQuestMapPanel | roadmap phases, study plan, main quests | **LIVE** (two support endpoints unused) |
| D-04 | Skills & progression (XP/level/rank) | StatusModal skill matrix, top bar, support breakdown | `campaign_skill_states` + 2 XP ledgers + 4 policy tables | **LIVE** |
| D-05 | Daily quests (9 slots) | QuestOverlay → Daily tab | quota-driven generator | **LIVE** |
| D-06 | Weekly missions | support card + weekly tab | patterns, recompute, claim | **LIVE** |
| D-07 | Check-ins, streak & shield | StatusModal → Check-in | `checkins`, streak/shield recompute | **LIVE** |
| D-08 | Badges | StatusModal → Badge Wall | `badges` + `badge_unlocks` | **LIVE** (`/api/badges` unused; data comes via `/summary`) |
| D-09 | Trackers (error log / writing / speaking / mock test) | none reachable | 4 route families, 6 tables | **BACKEND-ONLY** |
| D-10 | Boss battles (monthly) | BossOverlay + dashboard card | list + claim | **HALF-WIRED** — list is fetched, **claim is unreachable** |
| D-11 | Rank exams (promotion bosses) | RankBossNotif → exam + result screens | unlock, start, status, submit | **HALF-WIRED** — MCQ renderer never matches; resume path broken |
| D-12 | Certificates & test records | CertificateOverlay | `/test-records`, `/certificates`, `/certificates/manual` | **LIVE** via `/test-records`; the `/certificates*` pair is **unused** |
| D-13 | Rank & weakness suggestions | top-bar inbox | 2 families × apply/dismiss | **LIVE** |
| D-14 | Vocabulary Codex (+ tree, SRS, errors) | Codex, Word Network Tree, Flashcard Gate, Error Dungeon | ~25 routes | **LIVE** mostly; relations + errors list unused |
| D-15 | Vocabulary practice games | Shadow Duel, Word Family, Echo Chamber | 4 practice routes | **LIVE** |
| D-16 | Vocabulary boss | Boss Battles tab | challenge + submit | **LIVE**, with client-side grading |
| D-17 | Collocations | Collocations tab, collocation flashcard sub-tab | 24 routes | **HALF-WIRED** — two calls hit routes that do not exist (dead UI) |
| D-18 | Vocabulary library (5-layer) | Vocabulary Library tab | 8 routes | **LIVE** |
| D-19 | Study materials & plan browsing | none | `/materials`, `/materials/{id}`, `/quest-templates` | **BACKEND-ONLY** |
| D-20 | Dev / maintenance utilities | none | 3 `/api/dev/*` routes | **BACKEND-ONLY**, unauthenticated |

---

## 3. Domain detail

### D-01 Identity & sessions — LIVE

Account creation writes four rows plus an event in one commit: `Account`, `Player`,
`AccountPreference` (locale `vi`, tz `Asia/Ho_Chi_Minh`, dark, notifications on), `PlayerLearningProfile`
(`mixed` style, `bilingual_first` dictionary, `native_language: vi`), `AccountSession`
(`main.py:470-540`). Logout revokes the session row and clears the cookie (`main.py:653-676`).
Access token in `localStorage`; refresh token in an httpOnly cookie scoped to `/api/auth`
(`02-current-architecture.md` §6.1). The UI exposes login, register and logout and nothing else — no
password change, no reset, no email verification, no account deletion, no profile editing beyond
display name and target bands.

### D-02 Onboarding & campaign activation — LIVE

Covered in detail in `04-product-and-users.md` §2.4. Worth restating here because it is the only
place where the product asks the user anything about their goals: `POST /api/onboarding/activate-campaign`
persists five target bands, creates the campaign, back-links orphan certificate records, generates
rank suggestions from them, flips `onboarding_completed`, then recomputes progression
(`main.py:707-762`). Target bands are editable afterwards from the status modal
(`StatusModal.jsx:27-96` → `PATCH /api/player/targets`).

### D-03 Campaign & 78-week roadmap — LIVE

The campaign is a template row (`total_weeks=78`, `duration_months=18`, `seed.py:1789-1794`) with
78 `study_plan_weeks` and their sessions, 5 roadmap phases, and a main quest per session. The
dashboard renders it as `RoadmapHero` (phase track + 3 stat cards, `App.jsx:858-883`) and the Quest
overlay renders the week/session map (`MainQuestMapPanel.jsx:58-272`). Two consequences visible in
the code:

- **Phase metadata is duplicated client-side.** `MAIN_QUEST_PHASES` (5 phases, week ranges 1-13 /
  14-26 / 27-39 / 40-52 / 53-78) exists in `frontend/src/dashboard-data.js:53-89` while the server
  owns the phases in the database (`seed.py:ensure_roadmap_phases`). The frontend uses its copy to
  label phases; the server's copy drives the quests.
- **`GET /api/roadmap/phases` is never called** (unreferenced in `frontend/src`), as is
  `GET /api/study-plan/current-week` — the UI instead loads `/study-plan/weeks` wholesale
  (`App.jsx:410`).

### D-04 Skills & progression — LIVE

Two-layer model, both layers visible in the UI:

- **Five "matrix" skills** (Listening, Reading, Writing, Speaking, Vocabulary) are what the player
  total and the level/rank derive from; **Grammar and Collocation are support skills** whose XP is
  routed into Writing and Vocabulary respectively (`services.py:469-478`). The status modal renders
  the 5 tiles and, under each, the support-source breakdown
  (`SkillCards.jsx` `SupportBuffLines`; `support_breakdown` computed in `main.py:330-380`).
- **Player level/rank are backend-owned.** The client was explicitly gutted of its own formulas —
  `dashboard-data.js:458-460` carries the comment *"getPlayerLevel / getPlayerRank removed — player
  rank and level are backend-derived… See buildDashboardView"*, and `buildDashboardView` reads
  `player.player_level` / `player.player_rank` with the comment *"from backend — do not recompute
  from XP"* (`dashboard-data.js:563-565`). `getPlayerXpProgress` remains purely a bar-fill
  interpolation and is the one place the curve is copied (`:619-644`).
- **Rank promotion is a state machine** exposed to the client as strings:
  `none`, `eligible`, `boss_required`, `in_progress`, `passed` (`services.py:789-798`, `:1440-1460`;
  consumed by `RankBossNotif.jsx:6-8`). Promotion also has an alternate path: a certificate-derived
  rank suggestion can raise `confirmed_rank` without an exam (`services.py:1430-1460`).
- **Anti-farm caps exist server-side** and are invisible in the UI, e.g. the vocabulary data-entry
  cap (`TASKS.md:27` "Cap data-entry vocab XP at 40/word"; `compute_vocabulary_xp`
  `services.py:553-650`).

### D-05 Daily quests — LIVE

The daily board is **generated, not authored**: `ensure_quest_instances` reads
`CampaignSkillQuestQuota` per skill and fills that many slots per day
(`seed.py:1332-1420`). The seeded quota defines **9 daily slots** —

| Skill | Daily quota |
| --- | --- |
| Vocabulary | 3 |
| Reading | 1 |
| Listening | 1 |
| Grammar | 2 |
| Collocation | 0 |
| Writing | 1 |
| Speaking | 1 |

(`seed.py:1798-1806`; the shape is corroborated by migration `20260609_15_daily_slots_9.py` and by
`TASKS.md:17` "9-slot daily board + boss-lock badge").

The UI shows them in the Quest overlay's Daily tab (`DailyQuestPanel.jsx:170-214`), including a
`SlotChip` for `daily_slot_code` and a `BossLockBadge` for quests gated behind a boss, and each card
walks the COMPLETE → CLAIM → CLAIMED sequence (`dashboard-data.js:428-455`). `GET /api/quests/today`
exists but is unused — the client filters the full `/quests` payload (`dashboard-data.js:398-406`).

### D-06 Weekly missions — LIVE

Three seeded patterns, A/B/C, each with three objective lines (`WEEKLY_MISSION_PATTERNS`
`dashboard-data.js:91-138`; server-side `weekly_mission_patterns` `seed.py:818-891`). Completion is
derived, not stored: `recompute_weekly_missions` (`services.py:315-423`) plus per-item
`_set_weekly_item_state` (`:310-313`). The client recomputes its own objective counters from the
mission payload (`App.jsx:246-268` summariser, `:64-90`) and shows a fallback mission derived from
the week pattern when the live feed has not arrived (`App.jsx:236-260`) — a visible "Pattern
fallback" vs "Live weekly sync" label (`App.jsx:301-303`). Claiming posts
`/api/weekly-missions/{id}/claim` (`App.jsx:555`).

### D-07 Check-ins, streak & shield — LIVE

One check-in per day with mood / energy / focus / note (`StatusModal.jsx:220-262`;
`POST /api/checkins` `App.jsx:588-595`). `getQuestStatus`-style guards keep the draft in sync with
the server value (`App.jsx:330-336`). Streak, best streak, shield count and shield regen are fields
on `players` (`models.py:138-143`), recomputed server-side and displayed as stat cards
(`App.jsx:811-829`). `GET /api/checkins` returns the history shown in the status modal
(`App.jsx:382`).

### D-08 Badges — LIVE

Badge definitions are seeded (`ensure_badges` `seed.py:1016-1030`), ownership is campaign-scoped in
`badge_unlocks`, and recomputation happens inside `recompute_badges` (`services.py:424-468`). The UI
renders them as a collapsible wall inside the status modal with locked/unlocked styling
(`StatusModal.jsx:303-322`). **`GET /api/badges` is never called** — the badge list arrives inside
`GET /api/summary` (`SummaryOut.badges`, `schemas.py`), so the dedicated route is redundant from the
client's point of view.

### D-09 Trackers (error log, writing, speaking, mock tests) — **BACKEND-ONLY**

This is the largest capability gap in the product.

- **Server**: six tables (`error_logs`, `writing_entries`, `speaking_entries`, `mock_tests`,
  `test_records` and the quest linkage columns `error_log_id`/`writing_entry_id`/`speaking_entry_id`/
  `mock_test_id` on `quests` — serialized at `main.py:327-330`, accepted on completion at
  `main.py:1066-1069`), four route families with full CRUD (`main.py:1383-1461`), tracker-type↔field
  mapping (`services.py:105-119`), and `resolve_tracker_payload` wiring them into quest completion
  (`services.py:188-224`).
- **Client**: **zero call sites.** `grep -rn "error-logs|writing-entries|speaking-entries|mock-tests"
  frontend/src` → no matches; none of the four appears in the 62-path client inventory.
- **The only component that would render them is dead.** `TrackersPanel.jsx` renders
  `TRACKER_MODULES` (`dashboard-data.js:24-49`), which declares Error Log `Ready` and
  Writing/Speaking/Mock Test `Preparing`, and is imported by nothing (`05` §4.1).
- **Consequence**: quests whose `tracker_type` expects one of these entries
  (`services.py:105-119`, `TRACKERS`/`TRACKER_TYPE_TO_FIELD`) cannot be completed through the
  tracker path from the UI at all. `[DERIVED]` The client only ever completes a quest with no
  tracker payload (`App.jsx:508-510` posts no body), so the tracker-linked completion branches are
  unreachable from the shipped UI.

### D-10 Boss battles (monthly) — **HALF-WIRED**

- Server: `BossBattle` rows generated one per month (`ensure_bosses` `seed.py:1705-1743`,
  `month_boss_title` `:893-903`), `GET /api/boss-battles` (`main.py:1236-1244`), and a fully
  implemented `POST /api/boss-battles/{battle_id}/claim` (`main.py:1246-1267`) that requires the
  boss to be cleared, rejects a second claim, awards skill XP under an idempotency key
  `boss_claim:{id}`, and **deliberately awards no player XP** — with the in-code note *"player never
  receives XP directly (spec: ielts_xp_policy_rank_quest_spec.md §1.2)"* (`main.py:1247-1265`).
- Client: `BossOverlay` renders the current boss hero and the full timeline
  (`BossOverlay.jsx:8-35`, `BossTimelinePanel.jsx`), and the dashboard shows a read-only "Boss
  Status" card (`App.jsx:916-918`). The data comes from `GET /api/boss-battles` (`App.jsx:495`).- **Gap**: `POST /api/boss-battles/{id}/claim` is called by **nothing**. `grep -rn "boss-battles"
frontend/src` returns exactly one hit — the GET at `App.jsx:495`. `[DERIVED]` A user can see that a
boss is defeated and that a reward exists, but cannot claim it from the interface, so monthly boss
XP is unreachable in practice. Whether that omission is intentional is **U-23** — unlike the deferred
subjective rank bosses, nothing in the docs or comments explains it.

### D-11 Rank exams (promotion bosses) — **HALF-WIRED**

- Server, fully implemented: `POST /rank-exams/unlock` (`main.py:1600-1621`), `POST /rank-exams/start`
  with a **2-attempts-per-day cap** and pool/version selection (`main.py:1624-1728`, cap at
  `:1641-1648`), `GET /rank-exams/status/{skill_id}` exposing `attempts_remaining`
  (`main.py:1730-1758`), `GET /rank-exams/{attempt_id}` for an existing attempt
  (`main.py:1760-1769`), and `POST /rank-exams/{attempt_id}/submit`, which marks a late submission
  timed out, zeroes every answer's points and fails the attempt
  (`main.py:1785, 1802, 1815-1821`). Pools are seeded with `pass_percent=80` and
  `default_time_limit_minutes=30` (`seed.py:2002-2003`), matching `DECISIONS.md`.
- Client: `RankBossNotif` shows three banner states — eligible → **Unlock Boss**, `boss_required` →
  **Start Exam**, `in_progress` → **Resume Exam** (`RankBossNotif.jsx:36-87`); `RankExamScreen`
  renders MCQ or free text, a question jump row, and a countdown
  (`RankExamScreen.jsx:157-193`); `RankExamResultScreen` shows CLEARED/FAILED, score, accuracy and the
  new rank (`RankExamResultScreen.jsx`).
- **Gaps**:
  - **(a) The MCQ renderer can never trigger.** `QuestionInput` shows the option list only when
    `question_type === 'mcq'` (`RankExamScreen.jsx:162`), but the backend stores and returns
    `question_type="multiple_choice"` (`seed.py:2048`; echoed verbatim at `main.py:1718`) — and the
    string `"mcq"` **appears nowhere in `backend/app/`**, just as `"multiple_choice"` appears
    nowhere in `frontend/src` except that one comparison. `[DERIVED]` Every rank-exam question
    therefore renders as the free-text textarea at `RankExamScreen.jsx:185-192`, the option list is
    never shown, and because submission is an exact comparison against the option text
    (`main.py:1802`, seeded answers are option strings such as `"Leave"` — `seed.py:1936`) a user
    cannot realistically answer. Rank exams are reachable, persisted, timed and scored, but **not
    passable through the shipped UI**. Whether this mismatch is known or unnoticed is **U-21**.
  - **(b) Resume is not resume.** The **Resume Exam** button calls `startRankExam`, not the resume
    endpoint, so a reloaded in-progress exam is restarted and consumes one of the two daily attempts
    — `getRankExamAttempt` is dead code (`05` §4.3).
  - **(c) No attempt counter.** `getRankExamStatus` is never called, so the UI never shows the
    remaining daily attempts even though the server computes them (`main.py:1755-1756`).
- Writing and Speaking promotion bosses do not exist by design (`DECISIONS.md`: subjective grading
  deferred), so those two skills can only be promoted through a certificate-derived suggestion.
  `[DERIVED]` Note the asymmetry this creates: those are exactly the two skills the deferred feature
  would have covered, and they are also the two whose promotion has no working exam path in the UI,
  so their only route is a certificate-derived rank suggestion (D-13).

### D-12 Certificates & test records — LIVE (one of three entry points)

Three overlapping server paths exist and the client uses the least obvious one:

| Endpoint | Purpose | Called? |
| --- | --- | --- |
| `GET /api/test-records` | list records | **yes** — `App.jsx:483` |
| `POST /api/test-records` | create a record | **yes** — `App.jsx:696-699` (the certificate form) |
| `POST /api/certificates/manual` | create a certificate + generate rank suggestions | **no** — only reachable via the dead `postManualCertificate` wrapper (`api/auth.js:29-34`) |
| `GET /api/certificates` | list certificate records | **no** |

`[DERIVED]` Because the live form posts to `/test-records` rather than `/certificates/manual`, the
certificate-specific handling — the `create_rank_suggestions_for_certificate` branch and the
`campaign_id` back-link written in `main.py:1338-1368` — is not what the UI triggers; suggestions for
UI-created records must instead come from the `/test-records` path
(`create_rank_suggestions_for_test`, `services.py:1264-1294`). The overlay's own subtitle states the
approach: *"Existing test records filtered to exam certificates, with live create via the current
API."* (`CertificateOverlay.jsx:42-44`). The 4-value certificate enum `['IELTS','APTIS','TOEIC','TOEFL']`
(`dashboard-data.js:51`) is the exam picker.

### D-13 Rank & weakness suggestions — LIVE

Two independent families (`skill_rank_suggestions`, `weakness_suggestions`), each with apply/dismiss
(`main.py:1290-1336` and `:1462-1496`). On the client they are loaded together
(`App.jsx:462`), merged into one inbox (`buildSuggestionInbox`, `dashboard-data.js:728-773`), and
actioned through a **dynamically composed path** —
`` const path = item.type === 'rank' ? `/rank-suggestions/${item.id}/${action}` :
`/weakness-suggestions/${item.id}/${action}` `` (`App.jsx:620-629`). This is the reason both families
appear as "unreferenced" in a literal path diff; they are live. Applying a rank suggestion can raise
`confirmed_rank` directly (`services.py:1430-1485`).

### D-14 Vocabulary Codex, tree, SRS and errors — LIVE

Four sub-domains under `player_id` scope (vocabulary is deliberately *not* campaign-scoped — see
`DECISIONS.md` 2026-06-06 "Map user_id to player_id… lifelong study assets"):

| Sub-domain | UI | Notable server detail |
| --- | --- | --- |
| Codex (word CRUD, examples, filter/search) | `VocabularyWorkspace.jsx` Codex tab (`:611-824`), 10 fields in the create form (`INITIAL_FORM` `:11-25`) | `sync_node_status_from_item` keeps tree nodes in step (`services.py:1949-1997`) |
| Word Network Tree | `WordNetworkTree.jsx` — react-flow canvas, node drawer, edge CRUD, "sync all" (`:120-324`) | edges are the storage for word relations; `POST /api/vocabulary/tree/sync-all` |
| Flashcards + spaced repetition | Flashcard Gate tab, 3 sub-tabs | `review_flashcard` (`services.py:1816-1857`); familiarity decay order `again → hard → good`, `easy` never decays (`services.py:867-898`) |
| Error Dungeon | `ErrorDungeon.jsx` — monster-per-error-type battle, "defeat" action (`:87`) | `defeat_vocabulary_error` (`services.py:2517-2528`); `VocabularyError` has a `defeated` state |

Unused server surface in this domain: `GET/PATCH /api/vocabulary/errors` (the full list, as opposed
to `/active`) and the whole `/api/vocabulary/relations` pair are never called — relations are
represented as **tree edges** in the UI instead. `GET /api/vocabulary/practice/collocations` is also
unreferenced.

### D-15 Vocabulary practice games — LIVE

Three mini-games, all read a generated drill set and report success back:

| Game | Component | Reads | Writes |
| --- | --- | --- | --- |
| Shadow Duel | `ShadowDuel.jsx` (334 lines) | `/vocabulary/practice/shadow-duel` | `/vocabulary/practice/record-success` |
| Word Family | `WordFamilyEvolution.jsx` (388 lines) | `/vocabulary/practice/word-family` | same |
| Echo Chamber | `EchoChamber.jsx` (406 lines) | `/vocabulary/practice/echo-chamber` | same |

All three post to the single `/api/vocabulary/practice/record-success` route
(`services.py:2206-2238`), which takes a list of words — so the three games share one reward path.
Two of the generators are **hardcoded question banks inside the service**, not database-driven:
`get_shadow_duel_practice` (`services.py:2081-2204`) and `get_word_families_practice`
(`:2240-2400`) contain literal word/pronunciation/stress/syllable lists (e.g. `services.py:2404-2413`).
`[DERIVED]` These drills do not depend on what the user has actually studied.

### D-16 Vocabulary boss — LIVE

Distinct from both monthly boss battles and rank exams. `get_vocabulary_boss_status`
(`services.py:2530-2686`) derives bosses from unlocked badges and confirmed rank, with a hardcoded
boss catalogue at `services.py:2647+`; `challenge_vocabulary_boss` (`:2688-2991`) builds an exam
(question types seen: `meaning_recall`, `collocation`, `synonym_antonym`, `sentence_completion`,
`mixed` — `services.py:2742, 2782, 2812, 2842, 2855`); `submit_vocabulary_boss_result`
(`:2993-3046`) scores it with a **75% pass threshold** (`services.py:2999`) and grants a reward that
includes setting `confirmed_rank` (e.g. `"E"` for boss 1 — `services.py:3016-3020`). The pass
threshold differs from the rank-exam pool's 80% (`seed.py:2002`) because they are two different
features — worth stating because the two "boss" words are easy to conflate.

**Grading authority sits on the client in this domain, unlike rank exams.** The challenge response
type `BossQuestion` carries `correct_answer: str` as a first-class field (`schemas.py:885-891`), and
`challenge_vocabulary_boss` populates it on every question (`services.py:2744`). `VocabularyBoss.jsx:52`
grades locally by comparing the user's answer against `q.correct_answer`, then posts only a
percentage: `VocabularyBossSubmitIn` is a single field `score_pct: float` (`schemas.py:899-900`),
which the endpoint passes straight through to the service (`main.py:2243-2245`). `[DERIVED]` A client
can therefore submit a passing score and receive the rank promotion, and the correct answers are
visible in the network response during a supposedly closed exam. This differs from the rank-exam
domain, where the answers, the scoring and the pass threshold are all server-side
(`main.py:1798-1821`).

### D-17 Collocations — **HALF-WIRED**

- Server: 24 routes covering a 4-level browse tree (`collocation_levels` → `collections` →
  `sections` → `topics` → `items`), campaign linking, per-item progress, per-item flashcards and
  review (`main.py:2074-2626`).
- Client: `CollocationForge.jsx` implements the browse → level → section → topic → items drill-down
  and add/remove flashcard (`:110-202`); the Flashcard Gate's Collocation sub-tab reviews them
  through an inline component defined at the top of the workspace file
  (`VocabularyWorkspace.jsx:26-204`, mounted at `:1028-1048`).
- **Gap 1 — calls to routes that do not exist.** `VocabularyOverlay.jsx:142` posts to
  ``/vocabulary/${itemId}/collocations`` and `:161` deletes
  ``/vocabulary/collocations/${collocationId}``. Neither route is declared anywhere in `main.py`
  (verified against the full 121-route inventory, MF-01: the only `collocations` routes are the
  `/api/collocations/*` family plus `/api/vocabulary/practice/collocations`). Because
  `VocabularyOverlay` is dead UI (`05` §4.1) this is currently harmless — but it means the *only*
  code in the repo that tries to attach a collocation to a vocabulary word cannot work.
- **Gap 2 — the collocation↔vocabulary-word link is not wired in the live UI.** The live collocation
  surface (`CollocationForge`) manages collocations as their own mastered catalogue with their own
  progress and flashcards; it never associates one with a Codex word. `[DERIVED]` The
  "Collocation → Vocabulary support routing" that `services.py:474-478` defines therefore applies to
  XP, not to the UI's data model.
- Five of the 24 routes are unreferenced by the client: the whole `/api/collocation-collections*`
  family (unauthenticated, `main.py:2074-2093`), `/api/collocation-collections/{id}/progress`,
  `/api/collocation-items/{id}/progress`, and the campaign link/unlink pair.

### D-18 Vocabulary library (5-layer) — LIVE

`vocab_levels → topics → units → sections → items` plus its own flashcards and due/review endpoints
(`main.py:2627-2874`). Seeded from the folder structure under `material/vocabularies/`
(`ensure_vocab_library` `seed.py:2557-2683`, `_seed_vocab_tree` `:2617`), with all 4 canonical levels
from `_VOCAB_LEVELS_META` always created and linked to the campaign, and levels without a `vocab.md`
created as locked/empty. UI: `VocabularyLibrary.jsx` (255 lines) with a
level block drill-down and 3-way flashcard sub-tab inside the Flashcard Gate
(`VocabularyWorkspace.jsx:426-490`, `:1049+`). Only **one** vocab markdown file exists on disk
(`material/vocabularies/pre-intermediate_intermediate/vocab.md`), so three of the four levels are
empty by construction — see U-22.

### D-19 Study materials & plan browsing — **BACKEND-ONLY**

`GET /api/materials`, `GET /api/materials/{id}` and `GET /api/quest-templates` are implemented
(`main.py:912-929`) but called by nothing in `frontend/src`. Materials reach the UI only indirectly,
as `material_title` embedded in quest payloads (`serialize_quest` `main.py:340`), and the roadmap
overlay uses `/study-plan/weeks` + `/main-quests` instead of `/roadmap/phases`.

### D-20 Dev / maintenance utilities — **BACKEND-ONLY**

`POST /api/dev/reset`, `POST /api/dev/run_migrations`, `POST /api/dev/regenerate-quests`
(`main.py:1498-1583`, `:1587-1597`, `:1877-1899`). No UI references any of them. `reset` deletes
every row of all 72 model tables (MF-09) and re-seeds; `regenerate-quests` re-runs the daily generator for whichever
player row comes first (`get_player_or_404` → `services.get_active_player` `services.py:235-240`).
All three are unauthenticated (`02-current-architecture.md` §6.3).

---

## 4. Cross-cutting findings from the two inventories

**F-1 — Three capabilities have a working backend and no reachable UI**: the four trackers (D-09),
materials/quest-template browsing (D-19), and the dev utilities (D-20). Of these only D-09 is
user-facing, and `PROJECT_CONTEXT.md:30-37` lists it as a Main Feature Surface.

**F-2 — Three user-facing outcomes are unreachable or unachievable despite complete endpoints**:
claiming a defeated monthly boss (§3 D-10), passing a rank exam (§3 D-11 item (a)), and resuming an
in-progress rank exam (§3 D-11 item (b)) — `D-11a`/`D-11b` were inline labels here, never sections.
All three are **HALF-WIRED** rather than BACKEND-ONLY, because the UI presents
the *state* without the *mechanism* — a "Boss Status" card with no claim action, an exam screen with
a renderer whose branch condition never matches, and a "Resume Exam" button wired to the wrong
endpoint.

**F-3 — Nine of 40 components (22%, 1285 JSX lines) can never render** (MF-19). The largest is
`VocabularyOverlay.jsx` at 870 lines, a complete second implementation of the vocabulary surface that
`VocabularyWorkspace.jsx` superseded (`05` §4.1). Its presence means the repo contains *two*
vocabulary UIs, only one of which is wired.

**F-4 — Five exported API wrappers and five route families are dead code**
(`05` §4.2; D-12, D-14, D-17). The strongest case is the certificate pair: the UI creates records
through `/test-records` while `/certificates/manual` — the endpoint built for exactly that purpose —
sits unused.

**F-5 — The client is the only thing that decides what the user can do.** Because all navigation is
state (`05` §1.1), and because `App.jsx` loads a fixed set of six datasets once
(`App.jsx:169-176`), a capability is reachable if and only if some component happens to call its
endpoint. There is no capability registry, no feature flag and no server-declared navigation — so
"what the product currently does" and "what `App.jsx` currently renders" are the same question.

**F-6 — Grading trust is inconsistent across the two exam systems.** Rank exams compute correctness
and the pass threshold server-side (`main.py:1798-1821`); the vocabulary boss scores on the client
and posts a percentage the server accepts (`schemas.py:899-900`, `main.py:2243-2245`) while also
shipping `correct_answer` in the response (`schemas.py:885-891`). Both grant rank changes: the
former sets `confirmed_rank` after a pass (`main.py:1825-1845`), the latter sets it directly from
the submitted score (`services.py:3016-3020`).

**F-7 — Documentation drift on capability state.** `docs/current/PROJECT_CONTEXT.md` and
`dashboard-data.js`'s `TRACKER_MODULES` both describe trackers as Main Feature Surfaces in
`Ready`/`Preparing` states, and neither statement is renderable or actionable today. Conversely
`TASKS.md:16` accurately records the auth/refresh state that `DECISIONS.md` predates. See
`04-product-and-users.md` §5 for the full list.
