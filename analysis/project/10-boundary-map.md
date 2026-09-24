# 10 — Boundary map: what must survive, what is presentation, what is frozen

Answers mission questions **11**, **12** and **13**: behaviour whose loss would change what the
product does; presentation layers that hold no authority; and interfaces that cannot move.

Every entry names the file that owns it and is marked with one of three verdicts:

| Verdict | Meaning |
| --- | --- |
| **SERVER-OWNED** | the rule is computed server-side; a client that stops sending its input still gets the same stored result, and a client that renders something else changes only what is shown |
| **PRESENTATION** | the layer holds no authority over stored state; replacing it changes no stored value |
| **CONTRACT** | an interface both sides currently agree on; changing one side alone breaks or silently re-shapes behaviour |
| **CLIENT-ONLY** | the rule has exactly one implementation and it is in the browser — nothing server-side reproduces it |

Discovery only; this is a map of what is, with no target design. Evidence convention in `README.md`.
Related: `06` (domain status labels), `07` (endpoint inventory), `08` (data flows), `09` (auth).

---

# Part A — Behaviour that defines the product (mission 11)

## A1. The progression engine

`services.refresh_progress_state` (`services.py:804-816`) is the single entry point to every derived
value in the product. It runs on 32 route sites plus startup and commits (`08` §6). Its steps and
their owners:

| Step | Rule | Owner | Any of it in the client? |
| --- | --- | --- | --- |
| 1 | Quest status/expiry reconciliation — 4 bulk `UPDATE`s setting `status='completed'`, backfilling `earned_xp = xp`, `status='expired'` + `expired_at` for past incomplete quests, `status='pending'` for future ones | `services.sync_quest_statuses` `services.py:259-308` | **Partly** — `getQuestStatus` re-derives a status label client-side (`dashboard-data.js:398-405`) but does not write |
| 2 | Weekly mission item counters, derived by matching English **description substrings** (`"reading core quest"`, `"check-in or mini-review days"`, …) against quest/check-in/tracker data | `services.recompute_weekly_missions` `services.py:315-423` | No |
| 3 | Per-skill XP, rank, level, last-practiced, promotion gating | `services.recompute_skill_progress` `services.py:681-803` | No — the client displays only |
| 4 | Badge unlocks by fixed thresholds | `services.recompute_badges` `services.py:424-479` | No |
| 5 | Player XP, rank, level, streak, best streak, shields, shield regen, perfect days | `services.recompute_player_progress` `services.py:480-552` | **Partly** — the level *bar fraction* is client-only (see A7) |

Rule content that has to survive verbatim if the product is to behave the same way:

- **XP composition** (`services.py:684-741`): skill XP = own quest XP + main-quest XP for covered
  skills + support-routed XP + vocabulary XP, floored at the confirmed rank's minimum. Only quests
  with `completed == True AND reward_claimed == True` count (`:687-694`).
- **Support routing** (`services.py:474-477`): `Grammar → Writing`, `Collocation → Vocabulary`; the
  five scoring tiles are `MATRIX_SKILLS = {Listening, Reading, Writing, Speaking, Vocabulary}`
  (`services.py:469`).
- **Rank/level curve** (`services.py:77-88`): `xp(L) = round(19*(L**1.6-1))` for L 1..60; rank F→S in
  bands of ten levels; `RANK_MIN_XP` derived from the same table.
- **Promotion state machine** (`services.py:775-803`): `eligible → boss_required → in_progress →
  passed/none`, with the guard that `eligible`/`boss_required`/`in_progress` are never clobbered by
  a recompute; skills with `boss_gated == False` (`models.py:345`) never enter the exam flow and have
  `confirmed_rank` synced straight from `rank`.
- **Badge thresholds** (`services.py:441-451`): fixed skill-XP floors (300/500), `Error Killer` at 10
  defeated vocabulary errors, `Band 6/7` at 150/250 completed quests.
- **Player XP is a mean, not a sum** (`services.py:488-493`): `round(mean of the 5 matrix skill XP)`.
  `award_player_xp` is an explicit no-op (`services.py:1416-1424`).
- **Streak/shield replay** (`services.py:519-551`): per-day replay from `campaign.start_date`; a day
  counts when it has ≥3 role-tagged quests (`core`/`support`/`mini`) and all were completed; shields
  absorb one missed day, cap at 2, regenerate every 3 perfect days; `perfect_day_count` additionally
  requires a check-in.

## A2. The XP ledger

| Rule | Owner | Notes |
| --- | --- | --- |
| The only writer of `campaign_skill_states.xp` by accrual | `services.award_skill_xp` `services.py:1378-1415` | requires an `idempotency_key`; returns early if a `SkillXpTransaction` with that key exists; **raises `ValueError` if the key is empty** |
| Keys currently in use | `main.py:1119` `f"quest_claim:{quest.id}"`; `main.py:1184-1186` `f"weekly_mission_claim:{mission.id}"` with `transaction_type="weekly_mission"` | quest and weekly claims are the only two accrual paths |
| The ledger tables | `skill_xp_transactions` (`models.py:539`), `player_xp_transactions` (`models.py:557`) | the player table is written by nothing in the code that was read |
| Rank history | `SkillRankHistory` rows via `services.apply_rank_suggestion` (`services.py:1464-1473`) and the exam pass path (`main.py:1828-1833`) | the audit trail of rank changes |

Vocabulary XP is a **second, formula-based** XP source with no ledger rows at all — recomputed from
journal state on every refresh (`services.compute_vocabulary_xp` `services.py:553-646`):

- per word: 2 base + 2 `meaning_en` + 2 `meaning_vi` + 2 part-of-speech + 3 IPA, **capped at 40**;
- plus `min(mastery_score, 50)` per word;
- plus 5 per collocation in `learning/practiced/mastered`;
- plus error-dungeon XP: 1 per logged error, 5 per `defeated_count`, 20 per defeated error;
- plus boss bonuses: 60 (any confirmed rank ≥ E), 80 / 100 / 200 for the three boss badges.

`[DERIVED]` So deleting a vocabulary word or un-defeating an error lowers skill XP retroactively,
whereas a claimed quest raises it permanently — two different notions of "earned" inside one number.

## A3. Quest scheduling and completion

Everything here is server-seeded; none of it is in the client.

| Rule | Owner |
| --- | --- |
| Campaign length 548 days, end date = start + 548 | `seed.campaign_end_date` `seed.py:389-390` |
| 78 weeks × 7 days × per-skill slot generation, idempotent on `(quest_date, daily_slot_code)` | `seed.ensure_quest_instances` `seed.py:1325-1482` |
| Which slots exist per skill (Vocabulary: flashcard/codex/collocation; Reading/Listening/Writing/Speaking: one each; Grammar: review/exercise) | `seed.py:1341-1362` |
| How many per day per skill, and the preferred activity order | `CampaignSkillQuestQuota.daily_quota` / `preferred_activity_types` (`seed.py:1330-1338`, `:1388-1394`) |
| Daily rotation order (21-entry cycle, one variant for phases 1-3 and another for 4+) | `seed.daily_template_rotation` `seed.py:1275-1322` |
| Phase boundaries (weeks 1-13, 14-26, 27-39, 40-52, 53-78) and labels | `seed.phase_for_week` / `phase_label` `seed.py:366-388` |
| Quest XP per template | `QuestTemplate.base_xp` seeded in `seed.quest_template_seed` `seed.py:393-556` |
| Main-quest XP from the material markdown | `seed.infer_main_quest_xp` `seed.py:693-714` |
| Completion guards (future date → error, `expired` → error, one typed tracker reference only, tracker row existence) | `services.complete_quest_instance` `services.py:818-866`; `services.resolve_tracker_payload` `services.py:188-222` |
| `earned_xp = base_xp or xp` on completion; claim sets `reward_claimed` and awards via the ledger, with a **skill-blocked branch** that skips the award and leaves `reward_claimed` false while the skill's exam is pending | `services.py:856`; `main.py:1107-1117` |
| Rollback | `services.uncomplete_quest_instance` `services.py:1154-1171` — raises if the reward was already claimed; **no client path ever calls it** (`07` §6.5) |
| Weekly mission patterns (6 per phase, with `reward_xp` 40/45/50 and a special 25-XP onboarding week) | `seed.weekly_mission_patterns` `seed.py:818-891`; `seed.ensure_weekly_missions` `seed.py:1562-1703` |
| Monthly bosses | `seed.ensure_bosses` `seed.py:1705`; `seed.month_boss_title` `seed.py:893` |
| Rank-exam pools/questions per rank transition | `seed.ensure_rank_exam_pools` `seed.py:1930-2059` |
| Which quests the dashboard shows (default one-week window when no filters are passed) | `main.py:1007-1008` |

## A4. Rank exam grading — the strictest flow

`SERVER-OWNED` and self-contained (`main.py:1600-1878`):

- Unlock/start guards: `promotion_status == "boss_required"`, a pending and a confirmed rank, an
  active pool for that transition, **max 2 attempts per day** per `(campaign, skill, from_rank)`,
  version selection avoiding versions already used today (`main.py:1641-1660`).
- The attempt row carries its own `pass_percent`, `total_points`, `time_limit_minutes`, `expires_at`.
- Grading is `ans_in.answer_json == q.correct_answer_json` for each stored question, compared
  **server-side** (`main.py:1797-1805`), with `timed_out` suppressing both correctness and the pass.
- Pass → `confirmed_rank`/`rank` advanced, `pending_rank` cleared, `SkillRankHistory` written
  (`main.py:1815-1834`). Second failure of the day → `promotion_status = "eligible"` and a **−50 XP
  penalty applied after the recompute** so it cannot be undone (`main.py:1859-1866`).

## A5. Spaced repetition — three mechanisms, all server-side

| Mechanism | Owner | Rule |
| --- | --- | --- |
| Codex flashcards | `services.review_flashcard` `services.py:1816-1857` | fixed ladder `again 0 / hard 1 / good 3 / easy 7` days; `due_date`; `repetition_count`; flips `flashcard.status`; then `sync_node_status_from_item` |
| Vocab-library flashcards | `main.py:2805-2828` + `services.effective_familiarity` `services.py:868-897` | set familiarity; **lazy 7-day-per-tier decay**, floored at `again`, `easy` never decays |
| Collocation flashcards | `main.py:2477-2514` + the same decay function | identical familiarity + decay, then `try_autocomplete_collocation_forge` (`services.py:1097-1152`) |
| "Due" definition (codex) | `services.get_due_flashcards` `services.py:1798-1814` | `due_date <= today OR status='new' OR no state row` |
| Vocabulary-tree node status | `services.sync_node_status_from_item` `services.py:1949-1998` | derived from item mastery |
| Collocation Forge daily quest auto-complete | `services.try_autocomplete_collocation_forge` `services.py:1097-1152` | five distinct reviews in one day |

## A6. Auth and account behaviour

`SERVER-OWNED`, and documented in full in `09`: credential issuance and verification, the 3600 s
access token, refresh rotation, the login lockout counter, the `status != "active"` → 403 gate, and
the seeder's demo-account/player binding (`seed.ensure_demo_account` `seed.py:909`, `ensure_player`
`:943`, `ensure_account_and_profile` `:1833`).

## A7. Seeding and self-migration

`SERVER-OWNED`, and load-bearing for the product's content:

| Behaviour | Owner |
| --- | --- |
| Boot order: wait for DB → bootstrap schema → seed → `refresh_progress_state` | `main.py:431-441` (`@app.on_event("startup")`) |
| Create-or-`upgrade` Alembic to head; `create_all` + `stamp` only on an empty database | `database.run_database_bootstrap` `database.py:39-57` |
| 52 idempotent `ensure_*` seeders | `seed.seed_database` `seed.py:2685` |
| The curriculum is parsed at boot from markdown — `material/material.md` (mounted) and
  `backend/material.md` | `seed.material_file_path` `seed.py:557-579`, `parse_material_plan` `:596-650` |
| Collocation and vocabulary libraries parsed from markdown/CSV on disk | `seed.collocations_file_path` `:2061`, `parse_collocations_file` `:2087`, `parse_vocab_file` `:2403` |
| Campaign activation for a player | `seed.activate_campaign_for_player` `seed.py:2721`; `main.py:707-762` |
| `/api/dev/run_migrations` and `/api/dev/regenerate-quests` re-run parts of this at runtime, unauthenticated | `main.py:1587`, `:1877` |

## A8. Rank and weakness suggestion engines

| Rule | Owner |
| --- | --- |
| Band inferred from a mock-test raw score | `services.estimate_band_from_mock` `services.py:1494-1512` |
| Rank inferred from a test record per skill | `services.infer_rank_from_test_record` `services.py:1196-1263`; `map_ielts_score_to_rank` `:1296-1314` |
| Suggestions created for a test record / a manual certificate | `services.create_rank_suggestions_for_test` `:1264-1295`; `create_rank_suggestions_for_certificate` `:1315-1377` |
| Applying a suggestion: sets `confirmed_rank`, **elevates `state.xp` to the rank floor**, resets promotion state, writes history | `services.apply_rank_suggestion` `services.py:1430-1484` |
| Persisted weakness suggestions | `services.ensure_weakness_suggestions` `services.py:1521-1602` |
| Collocation/vocabulary completion percentages (weighted) | `services.compute_collocation_completion` `:898-999`; `compute_vocab_completion` `:1000-1096` |
| Vocabulary boss catalogue, requirements and cleared-state derivation | `services.get_vocabulary_boss_status` `services.py:2530-2686` |

## A9. Behaviour that lives **only** in the client

This is the honest list of things a server-only change cannot fix and a client replacement would have
to re-implement. Each is `CLIENT-ONLY`.

| Rule | Owner | Consequence |
| --- | --- | --- |
| Skill progress-bar percentage from a private ladder `[0,500,1200,2500,4500,7000,10000]` | `dashboard-data.js:4`, `getSkillProgress` `:461-467` | saturates at 10 000 while rank S needs 13 279 (`08` §7.1); the server has no equivalent value |
| Player level-bar fraction re-derived from the same curve | `dashboard-data.js:614-638`, `getPlayerXpProgress` `:619-644` | the *level* comes from the server; only the fraction is client-side |
| Weekly mission **identity** when the live mission is absent, from a 3-pattern table (`A/B/C`, `lines`) that is **different data** from the server's 6-per-phase patterns | `dashboard-data.js:91-119`, `getWeeklyPattern` `:493-495`; consumed by `buildDashboardView` `:585-591`; merged in `App.jsx:252-321` | renders a fabricated mission whose `rewardXp` is hardcoded 50 and whose items are synthesized with `target_count: 1` (`App.jsx:254-268`) |
| Quest action affordance and labels (`COMPLETE` / `CLAIM` / `CLAIMED` / `Expired` / `Locked`) | `getQuestActionMeta` `dashboard-data.js:428-459` | the client decides which POST a quest offers; the server accepts both and rejects out of order |
| Phase boundaries and labels for the roadmap | `MAIN_QUEST_PHASES` `:53-90`, `getCurrentPhaseLabel` `:485-491` | duplicates `seed.phase_for_week`/`phase_label` with different label text |
| Client-side weakness suggestions for the summary card | `buildWeaknessSuggestions` `:508-536` | a second suggestion engine beside `ensure_weakness_suggestions` |
| Review-session XP display (`again:0, hard:1, good:2, easy:3` × 10) | `VocabularyWorkspace.jsx:383-384`, `:861` | no endpoint awards it (`08` §7.3) |
| Game scoring in Shadow Duel / Echo Chamber / Word Family | `ShadowDuel.jsx`, `EchoChamber.jsx` (`:197`, `:248`), `WordFamilyEvolution.jsx` | the score is client-side; only its consequence (mastery via `POST /vocabulary/practice/record-success`) is server-derived |
| Vocabulary boss score | `VocabularyBoss.jsx` → `score_pct` | the server accepts the number and writes `confirmed_rank` (`09` §8) |
| Exam countdown and auto-submit timing | `RankExamScreen.jsx:6-30`, `:56-62` | the server owns `expires_at` and grades with its own clock, but only the client decides when the submit fires |
| "Today" | `getTodayISO()` `dashboard-data.js:184-190` (browser local date) | the server uses its own `date.today()` (`main.py:767`, `services.py:833`); both sides independently decide which quests are today's and which are expired |
| Presentational status wording for main quests | `getMainQuestStatusMeta` `:209-219` | maps server `status` strings to labels |
| Overlay open/close, tab selection, form drafts, exam answers, flashcard cursors | `App.jsx` (`:79-140`), `VocabularyWorkspace.jsx` (`:211-241`), `RankExamScreen.jsx` (`:33-35`) | session-only; a reload loses them (`05` §3) |

---

# Part B — Presentation layers that hold no authority (mission 12)

## B1. The component inventory

40 files in `frontend/src/components/` (plus `App.jsx` and 3 route pages — MF-19), 6276 lines of
`styles.css` (MF-20). `[DERIVED]` Counted from the files: 19 components call `useState` and **21 call it zero
times** — those 21 are pure functions of props and have no stored state to preserve.

**Stateless (21)** — safe to replace without touching behaviour, provided the props keep arriving:
`OverlayFrame` (60), `HomeTopBar` (59), `NavigationDrawer` (77), `ToastRack` (16), `PanelFrame` (21),
`SkillCards` (68), `CommandHeader` (52), `CampaignPanel` (45), `WeeklyMissionCard` (71),
`WeeklyMissionPanel` (37), `CheckInPanel` (71), `SuggestionInboxPanel` (44),
`SuggestionInboxDropdown` (91), `BadgeWallPanel` (19), `BossOverlay` (36), `BossTimelinePanel` (26),
`RankExamResultScreen` (66), `OverlayShellFallback` (25), `TrackersPanel` (23),
`LevelBlock` (46), `QuestOverlay` (216).

**Stateful (19)** — but in every case the state is presentational: open/closed, selected tab, form
draft, cursor, countdown, hover. The two exceptions where the state *is* the only implementation of a
rule are called out in B4.

| Component | Lines | `useState` | What its state is |
| --- | --- | --- | --- |
| `VocabularyWorkspace.jsx` | 1208 | 30 | active tab, form draft, search, review cursors, per-sub-tab selections |
| `VocabularyOverlay.jsx` *(dead)* | 870 | 17 | the same concerns, in the superseded implementation |
| `WordNetworkTree.jsx` | 579 | 8 | selected topic, node drag/edge drafts |
| `CollocationForge.jsx` | 411 | 11 | drill level/topic, sidebar state |
| `EchoChamber.jsx` | 406 | 15 | game stage, lives, letter selections |
| `WordFamilyEvolution.jsx` | 388 | 9 | game stage, node placement |
| `StatusModal.jsx` | 356 | 8 | which status section is open, target-editor draft |
| `ShadowDuel.jsx` | 334 | 13 | game round, timer, streak |
| `MainQuestMapPanel.jsx` | 276 | 2 | selected week/session |
| `VocabularyLibrary.jsx` | 255 | 4 | drill navigation |
| `VocabularyBoss.jsx` | 248 | 4 | exam progress |
| `ErrorDungeon.jsx` | 236 | 4 | encounter state |
| `DailyQuestPanel.jsx` | 218 | 1 | filter |
| `RankExamScreen.jsx` | 197 | 5 | current question, answers, submitting |
| `RoadmapHero.jsx` | 181 | 2 | collapsed state |
| `CertificateOverlay.jsx` | 160 | 3 | form draft |
| `usePresenceLayer.jsx` (hook) | 132 | 2 | overlay presence + keyboard trap |
| `SetupSummaryPanel.jsx` *(dead)* | 124 | 4 | setup draft |
| `RankBossNotif.jsx` | 92 | 1 | banner dismissal |

**Dead by reachability** (`05` §4.1; MF-19): 9 of the 40 — 1285 lines — plus 5 exported API wrappers that no
component imports.

## B2. Styling and layout

`frontend/src/styles.css` (6276 lines) is the entire visual layer; there is no CSS-in-JS, no
component library, no design-token file, and no CSS modules. `[DERIVED]` Its section comments show the
file is organised by feature area (daily board, vocabulary workspace, each mini-game, auth pages,
onboarding, rank exam, collocation browser, vocabulary library), so it is already partitioned along
the same seams as the components. Theme is hardcoded dark (`04`), and `AccountPreference.theme` is
written and never read (`03` U-20).

## B3. Formatting helpers and view models

`dashboard-data.js` (817 lines — MF-20) is the whole client-side derivation layer: **25 exported functions, 6
exported constants, plus 14 module-private helpers/tables**.

| Group | Members | Authority |
| --- | --- | --- |
| Date formatting/parsing | `formatDate`, `toIsoDate`, `parseDateValue`, `getCalendarDayOrdinal`, `getCalendarDayDiff`, `getTodayISO` | none over stored data; `getTodayISO` is the only "today" the client has |
| Collection formatting | `splitSummaryItems`, `uniqueItems` | none |
| Constants | `RANK_ORDER`, `SKILL_THEME`, `TEST_EVIDENCE`, `TRACKER_MODULES`, `CERTIFICATE_TYPES`, `MAIN_QUEST_PHASES` | `MAIN_QUEST_PHASES` duplicates server phase boundaries; `TRACKER_MODULES` labels a surface with no UI (`05` §4.4); `TEST_EVIDENCE` is hardcoded sample data |
| View builders | `buildDashboardView`, `buildMainQuestMap`, `buildRoadmapPhaseTrack`, `buildRoadmapBounds`, `buildPlayerSnapshot`, `buildSuggestionInbox`, `filterCertificateRecords`, `buildBossView` | pure functions of API payloads → props |
| Rules (see A9) | `getQuestStatus`, `getCompletionMode`, `getQuestEarnedXp`, `isQuestRewardClaimed`, `getQuestRewardValue`, `getQuestActionMeta`, `getSkillProgress`, `getPlayerXpProgress`, `getWeeklyPattern`, `getMainQuestPhaseMeta`, `getMainQuestStatusMeta`, `getSessionIntegrity`, `getSessionXpMeta`, `normalizeBossState` | the CLIENT-ONLY set |

`[DERIVED]` Internal inconsistency inside that last group, worth knowing before replacing it:
`getQuestEarnedXp` returns `quest.xp` (`:412-414`) while `getQuestRewardValue` and `getSessionXpMeta`
read `earned_xp` with `xp` as fallback (`:420-426`, `:241-280`) — so "earned XP" in the daily panel
and "reward value" elsewhere can be different numbers for the same quest.

## B4. Looks replaceable but is not

Per-screen honesty. Each row is a rule or state whose only implementation is in the UI layer.

| Screen / component | What looks replaceable | What is actually load-bearing |
| --- | --- | --- |
| Daily quest board (`DailyQuestPanel`) | layout, card styling, filter | the **action decision** — `getQuestActionMeta` (`dashboard-data.js:428-459`) is the only thing that decides whether a quest offers COMPLETE or CLAIM; the server accepts either call and rejects only out-of-order states |
| Weekly mission card (`WeeklyMissionCard`) | copy, progress bar | the mission **identity and items** when `/weekly-mission/current` has not resolved — `WEEKLY_MISSION_PATTERNS` + the `App.jsx:254-268` synthesis, with `sourceLabel` recording which source is displayed |
| Skill radar (`SkillCards`) | tiles, colours, ordering | the **bar percentage** — `SKILL_XP_THRESHOLDS`; the server sends `xp`/`rank`/`level` and no percentage |
| Player header (`RoadmapHero`/level block) | the bar | the **fractional level progress** — `LEVEL_XP_FLOORS`; level and rank themselves are server-owned |
| Vocabulary workspace (`VocabularyWorkspace`) | tabs, grids, cards | the flashcard review **XP readout** (`reviewXpEarned * 10`), the *only* place that number exists; the collocation-forge auto-complete acknowledgement (reads a dict field with no schema); the component also calls `onLoadData` on open/close/create, so it is a **refresh trigger** (`08` §5) |
| Shadow Duel / Echo Chamber / Word Family | boards, animations | the **scoring**; only the resulting `words` list is sent, and mastery (+2 per word, then `compute_vocabulary_xp`) is derived from it |
| Error Dungeon | encounter flow | which error is defeated is a server call, but the *progression through a dungeon* exists only here |
| Vocabulary Boss | question rendering, lives | the **grading** — `correct_answer` is shipped per question and the client posts a bare `score_pct` |
| Rank exam screen | countdown ring, question layout | the **timer-driven auto-submit** (`RankExamScreen.jsx:56-62`) and the answers map, which is lost on reload; "Resume Exam" on `RankBossNotif` starts a *new* attempt because nothing calls `getRankExamAttempt` (`05` §4.3) |
| Status modal / check-in | form layout | `checkInDraft` and `getTodayISO()`'s notion of today, which decide what is submitted |
| Overlays generally | `OverlayFrame`, `usePresenceLayer`, `OverlayShellFallback` | the Escape/Tab keyboard contract and focus handling live here (`05` §5); there are no routes behind the overlays, so a redesign that introduces URLs changes deep-linking behaviour, not data |
| Auth pages → onboarding | form markup, Vietnamese copy | the **post-onboarding transition** relies on `refreshAuth()` then `navigate('/')` (`Onboarding.jsx:60-62`), because the route gate reads `onboardingCompleted` from context |
| `SetupSummaryPanel`, `TrackersPanel`, `CampaignPanel`, `BadgeWallPanel`, `CheckInPanel`, `WeeklyMissionPanel`, `SuggestionInboxPanel`, `CommandHeader` | everything — they render nothing | they are **already unreachable**; `TRACKER_MODULES`' four module labels have no live renderer |
| `VocabularyOverlay` (870 lines, 17 `useState`) | everything | it contains the only client reference to two routes that **do not exist** (`POST /api/vocabulary/{id}/collocations`, `DELETE /api/vocabulary/collocations/{id}`) — so it is also the only written-down evidence of an unbuilt feature (`07` §5) |

---

# Part C — Interfaces that cannot move (mission 13)

## C1. Declared response shapes

| Fact | Evidence |
| --- | --- |
| **100 of 121 paths declare a `response_model`**; the other **21 return untyped dicts or nothing** (MF-08) | `07` §6.1 — the 21 include `GET /api/vocabulary/boss/status` (a nested structure read by both `main.py:2228` and `VocabularyBoss.jsx`) and the three destructive `/api/dev/*` routes |
| `SummaryOut.player` is a raw `dict` while every sibling field is typed | `07` §6.2 |
| Three handlers are aliased onto two paths each (six paths, three functions) | `main.py:1290-1291`, `:1307-1308`, `:1325-1326` |
| 14 routes carry no auth dependency; 4 are `account`, 37 `player`, 67 `campaign` | `09` §6.1 |

`[DERIVED]` **Declared vs actually-consumed field sets.** The client reads a strict subset of each
model, so the models are wider than the contract in practice:

| Model | Declared fields | Fields the client reads | Note |
| --- | --- | --- | --- |
| `QuestOut` (`serialize_quest` `main.py:291-335`) | 40 | 21 distinct (`quest.completed` ×18, `quest.id` ×13, `status` ×7, `quest_date` ×5, `earned_xp` ×5, `xp`, `week_no`, `title`, `base_xp`, `skill_name`, `reward_skill_name`, `reward_claimed`, `reward_claimed_at`, `study_plan_session_id`, `source`, `skill_confirmed_rank`, `promotion_status`, `details`, `daily_slot_code`, `confirmed_rank`, …) | `[DERIVED]` via `grep -rho "\bquest\.[a-z_]*"` over `frontend/src` |
| `PlayerProfileOut` | — | 20 distinct `profile.*` reads incl. `shield_regen_progress`, `best_streak`, `daily_mini_study_minutes` | same method |
| `SkillOut` | — | 14 distinct `skill.*` reads incl. `support_breakdown`, `pending_rank`, `promotion_status`, `last_practiced` | same method |

## C2. Enum-like string literals both sides compare

`[DERIVED]` The client compares these literals directly, so the server's exact spelling is part of the
interface:

| Literal | Where the server writes it | Where the client tests it |
| --- | --- | --- |
| `"expired"`, `"completed"`, `"pending"` (quest status) | `services.sync_quest_statuses` `services.py:259-308` | `getQuestActionMeta` `dashboard-data.js:450`; `getMainQuestStatusMeta` `:209-219` |
| `"in_progress"`, `"boss_required"`, `"eligible"`, `"passed"`, `"none"` (promotion status) | `services.py:773-803`, `main.py:1663`, `:1837-1848` | `RankBossNotif.jsx` branches on `promotion_status`; `buildSuggestionInbox` |
| badge names as **rule keys** | `services.py:441-451`, `main.py` boss rewards, `services.py:3027-3044` | quoted badge names appear in `get_vocabulary_boss_status` consumers |
| `"again" | "hard" | "good" | "easy"` (review results) | `services.py:1817-1820`, `main.py:2486-2488` | every review button |
| quest `session_type` `"Daily Quest"` / `"Main Quest"`, quest `quest_role` `"core"`/`"support"`/`"mini"` | seeded in `seed.ensure_quest_instances`; filtered in `services.py:693-720`, `main.py:1019` | `buildMainQuestMap` filters `session_type` |
| `mastery_rank` letters `D/C/B/A/S` | `services.py:2216-2231` (award), `:2565-2568` and `:2621`/`:2639` (boss requirements read them back) | vocabulary library/mastery badges |

## C3. Auth surface

`CONTRACT`, fully specified in `09`:

- Access token: hand-rolled HS256, claim `sub` = **account id as a string**, `exp`; 3600 s; no
  revocation.
- Refresh token: cookie **`ielts_rt`** at **`path=/api/auth`**, httpOnly, `SameSite=Lax`, 30 days;
  body field `refresh_token` accepted as the alternative carrier.
- Client storage key: **`ielts_access_token`** in `localStorage` (`client.js:3`).
- 401 semantics: one silent refresh + replay of the original request, including its body; then
  `App.jsx:152-155` logs out, navigates, and returns `undefined` instead of throwing (`09` §4.3).
- The client never reads `exp` and never decodes the token.

## C4. Transport and configuration

| Item | Value | Evidence |
| --- | --- | --- |
| API base | `import.meta.env.VITE_API_URL \|\| 'http://127.0.0.1:8000/api'` — **the `/api` prefix is part of every client path** | `client.js:1` |
| Compose override | `VITE_API_URL: http://localhost:8000/api` | `docker-compose.yml:48` |
| Backend port / dev port | 8000 / 5173 | `docker-compose.yml:33`, `:52` |
| MySQL host port | 3307, credentials inline in the compose file | `docker-compose.yml:6-12` |
| CORS | origin allowlist from `CORS_ORIGINS` (compose value includes a public IP origin), credentials allowed, all methods/headers | `main.py:210-217`, `docker-compose.yml:30` |
| Env keys in `.env.example` | `APP_START_DATE`, `CORS_ORIGINS`, `DATABASE_URL` — **`JWT_SECRET_KEY` is absent**, so the compiled-in fallback applies | `auth_utils.py:8`, `09` §2.3 |
| Curriculum inputs | `MATERIAL_PLAN_PATH: /app/material.md` mounted read-only; `backend/material.md` as the fallback path | `docker-compose.yml:29`, `seed.py:557-579` |

## C5. Already broken or drifted — do not inherit as safety

`[DERIVED]` These are places where the two sides do **not** currently agree, so a redesign that treats
today's shapes as authoritative would freeze a defect:

| Drift | Evidence |
| --- | --- |
| Two client calls target routes that do not exist (`POST /api/vocabulary/{id}/collocations`, `DELETE /api/vocabulary/collocations/{id}`) | `VocabularyOverlay.jsx:142`, `:161` — in dead UI, so unreachable today (`07` §5) |
| Rank exams cannot be answered: the client's only MCQ branch tests `question_type === 'mcq'` while the backend only emits `'multiple_choice'` | `RankExamScreen.jsx:162`; `seed.py:2048`, `main.py:1718` (`06` §3 D-11 item (a), U-21) |
| Monthly boss rewards cannot be claimed: the endpoint is complete and no UI calls it | `main.py:1246-1267`; `07` §4 |
| The vocab boss writes `confirmed_rank` from a client-supplied `score_pct` while its own exam ships `correct_answer` | `services.py:2999`, `:3015`; `schemas.py:890` (`09` §8) |
| The review screen shows XP nothing awards | `VocabularyWorkspace.jsx:861` vs `services.py:1816-1857` |
| **Two different weekly-mission pattern tables** exist (client 3 patterns with `lines`; server 6 per phase with items and `reward_xp`) | `dashboard-data.js:91-119` vs `seed.py:818-891` |
| Two different "today"s (browser local vs server local) drive today's quests and expiry | `dashboard-data.js:184-190` vs `main.py:767` |
| Client skill ladder saturates at 10 000 while rank S needs 13 279 | `dashboard-data.js:4` vs `services.py:79-88` |
| Client "earned XP" reads `quest.xp` while reward value reads `earned_xp` | `dashboard-data.js:412-414` vs `:420-426` |
| `POST /api/quests/{id}/uncomplete` exists and is unreachable by construction | `main.py:1078`; `07` §6.5 |
| 49 of 121 paths have no client consumer (MF-21); 21 paths have no response model (MF-08) | `07` §4, §6.1 |
| Client-side `onboardingCompleted` can only move upward within a session | `AuthProvider.jsx:9-12`, `09` §5 |
| `error.sessionExpired` set and never read | `client.js:71`, `09` §4.1 |
| Duplicate refresh logic: the exported `refreshTokens` wrapper is unused while `client.js` refreshes internally | `api/auth.js:64-66` vs `client.js:17-31` |

---

# Part D — The map in one table

| Surface | Behaviour behind it | Verdict |
| --- | --- | --- |
| Dashboard summary, skill radar, badges, streak, shields | recompute chain, badge rules, streak replay | SERVER-OWNED (bar % is CLIENT-ONLY) |
| Daily quest board | quest generation, completion/claim guards, ledger | SERVER-OWNED (action affordance is CLIENT-ONLY) |
| Main quest map | main-quest instances, covered-skill XP | SERVER-OWNED |
| Weekly mission | pattern definitions, item recompute, claim award | SERVER-OWNED (fallback identity is CLIENT-ONLY) |
| Check-in | upsert by campaign+date, streak/perfect-day inputs | SERVER-OWNED |
| Rank boss banners + exam | unlock/start guards, 2/day cap, grading, penalty, history | SERVER-OWNED (timer/auto-submit is CLIENT-ONLY) |
| Certificate / test record → rank suggestion | inference, suggestion creation, apply (rank + XP floor) | SERVER-OWNED |
| Vocabulary workspace: codex | item CRUD + flashcard side effect, SM ladder | SERVER-OWNED |
| Vocabulary workspace: flashcards | three separate review mechanisms | SERVER-OWNED (XP readout is CLIENT-ONLY) |
| Vocabulary workspace: games | mastery from posted `words` | scoring CLIENT-ONLY, consequence SERVER-OWNED |
| Vocabulary boss | requirements + cleared derivation; `score_pct` accepted | SERVER-OWNED (grading input is CLIENT-ONLY) |
| Collocation forge / library | familiarity decay, forge auto-complete, weighted completion | SERVER-OWNED |
| Word network tree | node-status derivation from mastery | SERVER-OWNED |
| Trackers (error/writing/speaking/mock) | full server CRUD | SERVER-OWNED with no renderer |
| Auth + onboarding | credentials, session, campaign activation | SERVER-OWNED except the post-activation redirect |
| All overlays, panels, styles, formatters, view builders | no stored state | PRESENTATION |
| 9 dead components, 5 dead wrappers | nothing | PRESENTATION (unreachable in both senses) |
| Every route path, response model, status literal, cookie/header/storage key, env key | — | CONTRACT |

---

# Part E — What this map could not establish

- **Runtime confirmation of any verdict.** Every judgement here is static: the "SERVER-OWNED"
  labels assert where a rule is *implemented*, not that it produces correct output — that needs a
  running stack (U-04).
- **Whether the client-only rules have ever disagreed with the server in practice.** The skill
  ladder, the weekly fallback and the review XP are provably divergent *in code*; whether a user has
  ever seen the difference was not observable.
- **The full breadth of the contract in one direction.** The de-facto field sets in C1 are measured
  from property *accesses*; fields reached through destructuring, spreads (`{...quest}`) or
  string-keyed lookups are not counted, so the real consumed set is a superset.
- **Whether the duplicate weekly-pattern table is meant to mirror the server's** (U-40) and whether
  the client-only progression values are load-bearing for any comparison the user makes (U-31).
- **Which dead UI is destined to return.** `VocabularyOverlay` (870 lines) and the four tracker
  modules are unreachable, but nothing in the repository states whether they are abandoned or
  pending (U-24). A redesign that deletes them would remove the only written record of two intended
  endpoints.
