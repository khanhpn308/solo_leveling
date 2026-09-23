# 07 — Interface contract reference

Answers mission question **8**: a contract reference for every interface the product exposes — each
backend route with method, path, auth requirement, request and response shape, and its client
consumer — plus every realtime mechanism, including the honest finding that none exists and what the
product does instead.

Current state only. Evidence convention and repo state are in `README.md`. Cross-references:
`02-current-architecture.md` §6 (auth internals), `05-frontend-routes-and-navigation.md` (navigation),
`06-domain-capability-inventory.md` (capability status).

---

## 1. How this inventory was produced

Every row below was extracted mechanically from `backend/app/main.py` (decorator line number, method,
path, the handler signature, and `response_model`), then the auth level and request model were derived
from the signature and the schema-class list in `backend/app/schemas.py`. Client consumers were
determined from the complete call-site dump of `grep -rn "api(\|apiFetch(" frontend/src` (every hit
read), with dynamic path composition resolved by hand.

- **121 route paths** exist across **118 handler functions** (three handlers carry two decorators —
  §6.4).
- Route counts by method: `GET` 59, `POST` 51, `PATCH` 3, `PUT` 1, `DELETE` 7.
- Every `response_model`-bearing route is listed with its model; `—` means the route declares **no**
  response model and returns an untyped dict (or nothing), so its shape is **not enforced and not
  documented by the code** — those are marked `[UNRESOLVED]` shapes in §7.

---

## 2. Authentication levels

Auth is a FastAPI dependency chain declared per route (`02-current-architecture.md` §6.2). Five
levels appear:

| Level | Meaning | Resolves |
| --- | --- | --- |
| `none` | no auth dependency | nothing |
| `account` | `Depends(get_current_account)` | verifies the bearer JWT, loads the `accounts` row, requires `status == "active"` (else 403) — `main.py:222-258` |
| `player` | `Depends(get_current_player)` (which depends on `account`) | the `players` row whose `account_id` matches, else **404** — `main.py:261-266` |
| `campaign` | `Depends(get_current_campaign)` (which depends on `player`) | the active campaign for that player, else **404** — `main.py:269-275` |

Measured distribution across the 121 paths (classifying each route by its **most restrictive**
dependency): `none` **14**, `account` **3**, `player` **37**, `campaign` **67**. All 14 `none` routes are
enumerated in `02-current-architecture.md` §6.3. Note that `campaign` is the *most* restrictive level
present — it implies a player, which implies an account — so the 67 `campaign` rows are the most
protected, and the 14 `none` rows are the unguarded surface.

**A level does not imply owner-scoping.** Every handler additionally filters by
`campaign.id` or `player.id` inline; there is no scoping middleware. Where a handler composes its own
query without that filter, an authenticated caller can reach another account's row — for example
`POST /api/boss-battles/{battle_id}/claim` filters by `campaign_id` correctly (`main.py:1248`), while
`GET /api/vocabulary/{item_id}` does **not** filter by player at all (`main.py:1906-1912`, delegates to
`services.get_vocabulary_item(db, item_id)` `services.py:1637-1644`). `[DERIVED]` Cross-account
isolation is therefore handler-by-handler, not systemic — see U-28.

---

## 3. Route inventory

Legend for the **Client** column: `App.jsx` / component name = called from there; `wrapper` = called
through `frontend/src/api/*.js`; `—` = **no client call anywhere**; `dead wrapper` = only reachable
through an exported wrapper that nothing imports (`05` §4.2).

### 3.1 System & auth — 6 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 443 | `GET /api/health` | none | — | — (dict) | — |
| 470 | `POST /api/auth/register` | none | `AccountRegisterIn` | `TokenOut` | `wrapper` *api/auth.js:3-8* → `AuthProvider.jsx:38-45` |
| 547 | `POST /api/auth/login` | none | `AccountLoginIn` | `TokenOut` | `wrapper` → `AuthProvider.jsx:35-37` |
| 612 | `POST /api/auth/refresh` | none | `RefreshTokenIn` (optional) | `TokenOut` | `client.js:17-31` (internal 401 retry); wrapper `refreshTokens` unused |
| 653 | `POST /api/auth/logout` | none | `RefreshTokenIn` (optional) | — | `wrapper` → `AuthProvider.jsx:47-56` |
| 678 | `GET /api/auth/me` | account | — | `MeResponseOut` | `wrapper` → `AuthProvider.jsx:23, 41, 59`; `App.jsx` uses the context |

### 3.2 Onboarding — 2 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 692 | `GET /api/onboarding/status` | account | — | `OnboardingStatusOut` | `dead wrapper` (`getOnboardingStatus`, `05` §4.2) |
| 707 | `POST /api/onboarding/activate-campaign` | account | `OnboardingActivateIn` | — (dict) | `wrapper` → `Onboarding.jsx:56-62` |

### 3.3 Dashboard & campaign — 6 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 764 | `GET /api/summary` | campaign | — | `SummaryOut` | `App.jsx:379` |
| 832 | `GET /api/profile` | campaign | — | `PlayerProfileOut` | `App.jsx:380` |
| 839 | `PATCH /api/player/targets` | campaign | `PlayerTargetsIn` | `PlayerProfileOut` | `StatusModal.jsx:49`; `SetupSummaryPanel` (dead) |
| 863 | `POST /api/setup` | campaign | `SetupIn` | `PlayerProfileOut` | — |
| 901 | `GET /api/campaigns/current` | campaign | — | `CampaignOut` | — |
| 906 | `GET /api/skills` | campaign | — | `list[SkillOut]` | — |

### 3.4 Materials & plan — 7 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 912 | `GET /api/quest-templates` | none | — | `list[QuestTemplateOut]` | — |
| 917 | `GET /api/materials` | none | — | `list[StudyMaterialOut]` | — |
| 922 | `GET /api/materials/{material_id}` | none | — | `StudyMaterialOut` | — |
| 930 | `GET /api/roadmap/phases` | campaign | — | `list[RoadmapPhaseOut]` | — |
| 942 | `GET /api/study-plan/weeks` | campaign | — | `list[StudyPlanWeekOut]` | `App.jsx:410` |
| 953 | `GET /api/study-plan/current-week` | campaign | — | `StudyPlanWeekOut` | — |
| 972 | `GET /api/main-quests` | campaign | — | `list[QuestOut]` | `App.jsx:410` |

### 3.5 Quests, missions & check-ins — 9 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 994 | `GET /api/quests` | campaign | — | `list[QuestOut]` | `App.jsx:381` |
| 1034 | `GET /api/quests/today` | campaign | — | `list[QuestOut]` | — |
| 1048 | `POST /api/quests/{quest_id}/complete` | campaign | `QuestCompletionIn` | `QuestOut` | `App.jsx:508` (dynamic action) |
| 1078 | `POST /api/quests/{quest_id}/uncomplete` | campaign | — | `QuestOut` | **— never called** (§6.5) |
| 1091 | `POST /api/quests/{quest_id}/claim` | campaign | — | `QuestOut` | `App.jsx:508` (dynamic action) |
| 1138 | `GET /api/weekly-mission/current` | campaign | — | `WeeklyMissionOut` | `App.jsx:431` |
| 1164 | `POST /api/weekly-missions/{mission_id}/claim` | campaign | — | `WeeklyMissionOut` | `App.jsx:555` |
| 1192 | `POST /api/checkins` | campaign | `CheckInIn` | `CheckInOut` | `App.jsx:588` |
| 1220 | `GET /api/checkins` | campaign | — | `list[CheckInOut]` | `App.jsx:382` |

### 3.6 Badges & boss battles — 3 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1230 | `GET /api/badges` | campaign | — | `list[BadgeOut]` | — (badges arrive via `/api/summary`) |
| 1236 | `GET /api/boss-battles` | campaign | — | `list[BossBattleOut]` | `App.jsx:495` |
| 1246 | `POST /api/boss-battles/{battle_id}/claim` | campaign | — | `BossBattleOut` | **— never called** (`06` §D-10) |

### 3.7 Test records & certificates — 4 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1269 | `GET /api/test-records` | player | — | `list[TestRecordOut]` | `App.jsx:483` |
| 1279 | `POST /api/test-records` | campaign | `TestRecordIn` | `TestRecordOut` | `App.jsx:696` |
| 1338 | `POST /api/certificates/manual` | player | `ManualCertificateIn` | `ManualCertificateOut` | `dead wrapper` (`postManualCertificate`) |
| 1370 | `GET /api/certificates` | player | — | `list[ManualCertificateOut]` | — |

### 3.8 Suggestions — 6 paths (2 aliased, see §6.4)

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1290 | `GET /api/rank-suggestions` | campaign | — | `list[SkillRankSuggestionOut]` | `App.jsx:462` |
| 1291 | `GET /api/skill-rank-suggestions` | campaign | — | `list[SkillRankSuggestionOut]` | — (alias) |
| 1307 | `POST /api/rank-suggestions/{suggestion_id}/apply` | campaign | — | `SkillRankSuggestionOut` | `App.jsx:620-629` (dynamic) |
| 1308 | `POST /api/skill-rank-suggestions/{suggestion_id}/apply` | campaign | — | `SkillRankSuggestionOut` | — (alias) |
| 1325 | `POST /api/rank-suggestions/{suggestion_id}/dismiss` | campaign | — | `SkillRankSuggestionOut` | `App.jsx:620-629` (dynamic) |
| 1326 | `POST /api/skill-rank-suggestions/{suggestion_id}/dismiss` | campaign | — | `SkillRankSuggestionOut` | — (alias) |
| 1462 | `GET /api/weakness-suggestions` | campaign | — | `list[WeaknessSuggestionOut]` | `App.jsx:462` |
| 1477 | `POST /api/weakness-suggestions/{suggestion_id}/apply` | campaign | — | `WeaknessSuggestionOut` | `App.jsx:620-629` (dynamic) |
| 1490 | `POST /api/weakness-suggestions/{suggestion_id}/dismiss` | campaign | — | `WeaknessSuggestionOut` | `App.jsx:620-629` (dynamic) |

### 3.9 Trackers — 8 paths, **zero client consumers**

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1383 | `GET /api/error-logs` | campaign | — | `list[ErrorLogOut]` | — |
| 1393 | `POST /api/error-logs` | campaign | `ErrorLogIn` | `ErrorLogOut` | — |
| 1402 | `GET /api/writing-entries` | campaign | — | `list[WritingEntryOut]` | — |
| 1412 | `POST /api/writing-entries` | campaign | `WritingEntryIn` | `WritingEntryOut` | — |
| 1421 | `GET /api/speaking-entries` | campaign | — | `list[SpeakingEntryOut]` | — |
| 1431 | `POST /api/speaking-entries` | campaign | `SpeakingEntryIn` | `SpeakingEntryOut` | — |
| 1440 | `GET /api/mock-tests` | campaign | — | `list[MockTestOut]` | — |
| 1450 | `POST /api/mock-tests` | campaign | `MockTestIn` | `MockTestOut` | — |

### 3.10 Dev utilities — 3 paths, all `none`

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1498 | `POST /api/dev/reset` | none | — | — (counts dict) | — |
| 1587 | `POST /api/dev/run_migrations` | none | — | — (status dict) | — |
| 1877 | `POST /api/dev/regenerate-quests` | none | — | — (counts dict) | — |

### 3.11 Rank exams — 5 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1600 | `POST /api/rank-exams/unlock` | campaign | `RankExamStartIn` | — (dict) | `wrapper` → `App.jsx:648` |
| 1624 | `POST /api/rank-exams/start` | campaign | `RankExamStartIn` | `RankExamStartOut` | `wrapper` → `App.jsx:665` |
| 1730 | `GET /api/rank-exams/status/{skill_id}` | campaign | — | `RankExamStatusOut` | `dead wrapper` (`getRankExamStatus`) |
| 1760 | `GET /api/rank-exams/{attempt_id}` | campaign | — | `RankExamAttemptOut` | `dead wrapper` (`getRankExamAttempt`) |
| 1771 | `POST /api/rank-exams/{attempt_id}/submit` | campaign | `RankExamSubmitIn` | `RankExamSubmitOut` | `wrapper` → `RankExamScreen.jsx:51` |

### 3.12 Vocabulary core — 9 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1901 | `GET /api/vocabulary` | player | — | `list[VocabularyItemOut]` | `App.jsx:383` |
| 1906 | `GET /api/vocabulary/{item_id}` | player | — | `VocabularyItemOut` | — |
| 1914 | `POST /api/vocabulary` | player | `VocabularyItemIn` | `VocabularyItemOut` | `VocabularyWorkspace.jsx:307` |
| 1921 | `PUT /api/vocabulary/{item_id}` | player | `VocabularyItemIn` | `VocabularyItemOut` | `VocabularyWorkspace.jsx:302` |
| 1931 | `DELETE /api/vocabulary/{item_id}` | player | — | — | `VocabularyWorkspace.jsx:327` |
| 1941 | `POST /api/vocabulary/{item_id}/examples` | player | `VocabularyExampleIn` | `VocabularyExampleOut` | `VocabularyWorkspace.jsx:343` |
| 1951 | `DELETE /api/vocabulary/examples/{example_id}` | player | — | — | `VocabularyWorkspace.jsx:359` |
| 1961 | `POST /api/vocabulary/relations` | player | `VocabularyRelationIn` | `VocabularyRelationOut` | — |
| 1968 | `DELETE /api/vocabulary/relations/{relation_id}` | player | — | — | — |

### 3.13 Flashcards & spaced repetition — 4 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 1977 | `GET /api/flashcards` | player | — | `list[FlashcardOut]` | — |
| 1982 | `POST /api/flashcards` | player | `FlashcardIn` | `FlashcardOut` | — (cards are created as a side effect of item create, §8.3) |
| 1987 | `GET /api/flashcards/due` | player | — | `list[FlashcardOut]` | `App.jsx:384` |
| 1992 | `POST /api/flashcards/{card_id}/review` | player | `ReviewFlashcardIn` | `SpacedRepetitionStateOut` | `VocabularyWorkspace.jsx:387` |

### 3.14 Vocabulary tree — 8 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2005 | `GET /api/vocabulary/tree/topics` | player | — | `list[VocabularyTopicOut]` | `WordNetworkTree.jsx:120` |
| 2010 | `POST /api/vocabulary/tree/topics` | player | `VocabularyTopicIn` | `VocabularyTopicOut` | `WordNetworkTree.jsx:137` |
| 2015 | `GET /api/vocabulary/tree/{topic_id}` | player | — | `VocabularyTreeOut` | `WordNetworkTree.jsx:155` |
| 2023 | `POST /api/vocabulary/tree/nodes` | player | `VocabularyNodeIn` | `VocabularyNodeOut` | `WordNetworkTree.jsx:260` |
| 2037 | `PATCH /api/vocabulary/tree/nodes/{node_id}` | player | `VocabularyNodeUpdate` | `VocabularyNodeOut` | `WordNetworkTree.jsx:201` |
| 2046 | `POST /api/vocabulary/tree/edges` | player | `VocabularyEdgeIn` | `VocabularyEdgeOut` | `WordNetworkTree.jsx:219` |
| 2057 | `DELETE /api/vocabulary/tree/edges/{edge_id}` | player | — | — | `WordNetworkTree.jsx:312` |
| 2066 | `POST /api/vocabulary/tree/sync-all` | player | — | — (dict) | `WordNetworkTree.jsx:324` |

### 3.15 Vocabulary practice games — 5 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2156 | `GET /api/vocabulary/practice/collocations` | player | — | `CollocationPracticeResponse` | — |
| 2161 | `GET /api/vocabulary/practice/shadow-duel` | player | — | `ShadowDuelResponse` | `ShadowDuel.jsx:81` |
| 2166 | `POST /api/vocabulary/practice/record-success` | player | `PracticeSuccessIn` | — | `ShadowDuel.jsx:167`, `WordFamilyEvolution.jsx:231`, `EchoChamber.jsx:206` |
| 2173 | `GET /api/vocabulary/practice/word-family` | player | — | `WordFamilyResponse` | `WordFamilyEvolution.jsx:128` |
| 2178 | `GET /api/vocabulary/practice/echo-chamber` | player | — | `EchoChamberResponse` | `EchoChamber.jsx:49` |

### 3.16 Vocabulary errors — 5 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2183 | `POST /api/vocabulary/errors` | player | `VocabularyErrorIn` | `VocabularyErrorOut` | — |
| 2190 | `GET /api/vocabulary/errors/active` | player | — | `list[VocabularyErrorOut]` | `VocabularyWorkspace.jsx:259` |
| 2195 | `GET /api/vocabulary/errors` | player | — | `list[VocabularyErrorOut]` | — |
| 2200 | `PATCH /api/vocabulary/errors/{error_id}` | player | `VocabularyErrorIn` | `VocabularyErrorOut` | — |
| 2209 | `POST /api/vocabulary/errors/{error_id}/defeat` | player | — | `VocabularyErrorOut` | `ErrorDungeon.jsx:87` |

### 3.17 Vocabulary boss — 3 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2218 | `GET /api/vocabulary/boss/status` | player | — | — (dict) | `VocabularyWorkspace.jsx:262` |
| 2223 | `POST /api/vocabulary/boss/{boss_id}/challenge` | player | — | `VocabularyBossExam` | `VocabularyBoss.jsx:16` |
| 2236 | `POST /api/vocabulary/boss/{boss_id}/submit` | player | `VocabularyBossSubmitIn` | `VocabularyBossSubmitOut` | `VocabularyBoss.jsx:57` |

### 3.18 Collocation collections & progress — 8 paths, **all unconsumed**

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2074 | `GET /api/collocation-collections` | none | — | `list[CollocationCollectionOut]` | — |
| 2079 | `POST /api/collocation-collections` | none | `CollocationCollectionIn` | `CollocationCollectionOut` | — |
| 2087 | `GET /api/collocation-collections/{collection_id}` | none | — | `CollocationCollectionOutline` | — |
| 2095 | `GET /api/collocation-collections/{collection_id}/progress` | campaign | — | `CollocationCollectionOutlineWithProgress` | — |
| 2108 | `POST /api/campaigns/current/collocation-collections/{collection_id}/link` | campaign | — | `CampaignCollocationLinkOut` | — |
| 2121 | `DELETE /api/campaigns/current/collocation-collections/{collection_id}/link` | campaign | — | — | — |
| 2133 | `GET /api/campaigns/current/collocation-collections` | campaign | — | `list[CollocationCollectionOut]` | — |
| 2141 | `POST /api/collocation-items/{item_id}/progress` | campaign | — | `PlayerCollocationProgressOut` | — |

### 3.19 Collocations (browse + flashcards) — 8 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2247 | `GET /api/collocations/levels` | campaign | — | `list[CollocationLevelOut]` | `CollocationForge.jsx:110` |
| 2316 | `GET /api/collocations/topics` | campaign | — | `list[CollocationBrowseTopicOut]` | `CollocationForge.jsx:122, 183` |
| 2363 | `GET /api/collocations/topics/{topic_id}/items` | campaign | — | `list[CollocationBrowseItemOut]` | `CollocationForge.jsx:158, 180` |
| 2413 | `POST /api/collocations/{item_id}/flashcard` | campaign | — | — (dict) | `CollocationForge.jsx:190` |
| 2453 | `DELETE /api/collocations/{item_id}/flashcard` | campaign | — | — (dict) | `CollocationForge.jsx:202` |
| 2477 | `POST /api/collocations/{item_id}/flashcard/review` | campaign | `CollocationReviewIn` | — (dict) | `VocabularyWorkspace.jsx:59` |
| 2516 | `GET /api/collocations/flashcard/topics` | campaign | — | `list[CollocationFlashcardTopicOut]` | `VocabularyWorkspace.jsx:85, 414` |
| 2569 | `GET /api/collocations/flashcard/topics/{topic_id}` | campaign | — | `list[CollocationFlashcardItemOut]` | `VocabularyWorkspace.jsx:46` |

### 3.20 Vocabulary library — 9 paths

| Line | Method & path | Auth | Request | Response | Client |
| --- | --- | --- | --- | --- | --- |
| 2627 | `GET /api/vocab-library/levels` | campaign | — | `list[VocabLevelOut]` | `VocabularyLibrary.jsx:122` |
| 2649 | `GET /api/vocab-library/levels/{level_id}/topics` | campaign | — | `list[VocabTopicOut]` | `VocabularyLibrary.jsx` via `api(fetchPath)` in `drillInto` |
| 2671 | `GET /api/vocab-library/topics/{topic_id}/units` | campaign | — | `list[VocabUnitOut]` | same `drillInto` mechanism |
| 2697 | `GET /api/vocab-library/units/{unit_id}/sections` | campaign | — | `list[VocabSectionOut]` | same `drillInto` mechanism |
| 2724 | `GET /api/vocab-library/sections/{section_id}/words` | campaign | — | `list[VocabWordOut]` | `VocabularyLibrary.jsx:145` |
| 2759 | `POST /api/vocab-library/words/{item_id}/flashcard` | campaign | — | — (dict), HTTP 201 | `VocabularyLibrary.jsx:157` |
| 2788 | `DELETE /api/vocab-library/words/{item_id}/flashcard` | campaign | — | — (dict) | `VocabularyLibrary.jsx:166` |
| 2805 | `POST /api/vocab-library/words/{item_id}/flashcard/review` | campaign | `VocabReviewIn` | — (dict) | `VocabularyWorkspace.jsx:478` |
| 2830 | `GET /api/vocab-library/flashcards/due` | campaign | — | `list[VocabFlashcardDueOut]` | `VocabularyWorkspace.jsx:426` |

---

## 4. Paths no client calls — the "ignored" set

**49 of 121 paths (40%) have no consumer anywhere in `frontend/src`**, including the four
reachable only through dead wrappers. Grouped by why:

| Group | Count | Paths |
| --- | --- | --- |
| Backend-only capabilities with no UI (`06` §D-09, §D-19, §D-20) | 17 | the 8 tracker routes, the 3 dev routes, `quest-templates`, `materials`, `materials/{id}`, `roadmap/phases`, `study-plan/current-week`, `certificates` |
| Unconsumed sub-features of domains that *are* shipped | 17 | `vocabulary/relations` ×2, `flashcards` GET+POST, single-item `vocabulary/{item_id}`, `vocabulary/errors` GET/PATCH/POST, `practice/collocations`, and all 8 collocation-collection/progress routes |
| Exists but the UI has no wired action | 4 | `boss-battles/{id}/claim`, `quests/{id}/uncomplete`, `setup`, `skills` |
| Reachable only through a dead exported wrapper | 4 | `onboarding/status`, `certificates/manual`, `rank-exams/status/{skill_id}`, `rank-exams/{attempt_id}` |
| Aliased duplicate prefixes | 3 | the `/api/skill-rank-suggestions/*` trio (§6.4) |
| Superseded — the data arrives in `/api/summary` | 2 | `badges`, `campaigns/current` |
| Redundant duplicate | 1 | `quests/today` (returns the same rows as `/quests`; the client filters locally) |
| `health` | 1 | no UI health check |

Note that `auth/refresh` looks unconsumed from the wrapper list but is in fact called on every 401 —
internally, by `client.js:17-31`, not through the exported `refreshTokens` wrapper. It is therefore
**live**, and is not counted above.

---

## 5. Client calls to routes that do not exist

Exactly two, both in dead UI, both in `VocabularyOverlay.jsx`:

| Client call | Line | Route exists? |
| --- | --- | --- |
| `POST /api/vocabulary/{item_id}/collocations` | `VocabularyOverlay.jsx:142` | **No.** Verified against all 121 paths; the only `collocations` routes are `/api/collocations/*` and `/api/vocabulary/practice/collocations` (`06` §D-17). |
| `DELETE /api/vocabulary/collocations/{collocation_id}` | `VocabularyOverlay.jsx:161` | **No.** Same verification. |

Because `VocabularyOverlay` is imported by nothing (`05` §4.1), neither call can currently fire. They
are nevertheless the only evidence in the repo of an intended "attach a collocation to a Codex word"
flow — see U-24.

---

## 6. Contract-shape observations

### 6.1 Routes with no `response_model` — 21 of 121 paths

Extracted by testing every decorator for the absence of `response_model=`. These return untyped dicts
(or nothing), so **their response shape is declared nowhere in the code** and is `[UNRESOLVED]` except
where a consumer reveals its expectations:

| Path | Why it is notable |
| --- | --- |
| `GET /api/health` | trivially `{status, message}` — only visible from the handler body |
| `POST /api/auth/logout` | returns `{"detail": …}` |
| `POST /api/onboarding/activate-campaign` | returns `{"detail": …}` while being the most consequential onboarding write (`main.py:707-762`) |
| `POST /api/dev/{reset,run_migrations,regenerate-quests}` | 3 routes, all returning ad-hoc status/count dicts |
| `POST /api/rank-exams/unlock` | returns a bare dict on which the client's toast depends (`App.jsx:648-653`) |
| `DELETE /api/vocabulary/{item_id}` | returns a dict |
| `DELETE /api/vocabulary/examples/{example_id}` | returns a dict |
| `DELETE /api/vocabulary/relations/{relation_id}` | returns a dict |
| `DELETE /api/vocabulary/tree/edges/{edge_id}` | returns a dict |
| `POST /api/vocabulary/tree/sync-all` | returns a count dict |
| `DELETE /api/campaigns/current/collocation-collections/{collection_id}/link` | returns nothing |
| `POST /api/vocabulary/practice/record-success` | returns a dict consumed by three components' `onXPUpdate` path |
| `GET /api/vocabulary/boss/status` | **highest risk**: a nested dict whose `bosses[].id/status/title` shape is read by `main.py:2228` *and* rendered by `VocabularyBoss.jsx` — coupling with no schema between them |
| `POST /api/collocations/{item_id}/flashcard` | returns a dict |
| `DELETE /api/collocations/{item_id}/flashcard` | returns a dict |
| `POST /api/collocations/{item_id}/flashcard/review` | returns a dict whose `collocation_forge_autocompleted` flag the client reads (`VocabularyWorkspace.jsx:62-64`) |
| `POST /api/vocab-library/words/{item_id}/flashcard` | returns a dict at HTTP 201 |
| `DELETE /api/vocab-library/words/{item_id}/flashcard` | returns a dict |
| `POST /api/vocab-library/words/{item_id}/flashcard/review` | returns a dict |

`[UNRESOLVED]` U-29 records that these 21 shapes cannot be verified without executing the server.

### 6.2 `SummaryOut.player` is a raw `dict`

`SummaryOut` declares `player: dict` (`schemas.py`), not a Pydantic model, while all of its other
fields are typed (`skills: list[SkillOut]`, `badges: list[BadgeOut]`, `boss_battles:
list[BossBattleOut]`, plus four `int` counters). `[DERIVED]` The player sub-object is therefore the
only part of the dashboard payload with no schema at all, which is consistent with the client reading
it defensively (`buildDashboardView` `dashboard-data.js:541-567` reads `player.total_xp ?? 0`,
`player.player_level ?? null`, `player.player_rank ?? 'F'`).

### 6.3 Request models are almost always optional-body or absent

Only 4 routes take a **required** body beyond path params (`register`, `login`, `activate-campaign`,
`complete`). Nine routes accept an optional body purely to support cookie-based refresh
(`TokenOut`/`RefreshTokenIn` pattern, `main.py:452-476`). Most mutations take their input from the path
and rely on the campaign/player context for everything else — e.g. `POST /api/quests/{id}/claim` has no
body at all (`main.py:1091`).

### 6.4 Three handlers are decorated twice (backwards-compatible aliases)

| Handler | Decorators | Line |
| --- | --- | --- |
| `get_rank_suggestions` | `GET /api/rank-suggestions` **and** `GET /api/skill-rank-suggestions` | `main.py:1290-1291` |
| `post_apply_rank_suggestion` | `POST /api/rank-suggestions/{id}/apply` **and** `/api/skill-rank-suggestions/{id}/apply` | `main.py:1307-1308` |
| `post_dismiss_rank_suggestion` | `POST /api/rank-suggestions/{id}/dismiss` **and** `/api/skill-rank-suggestions/{id}/dismiss` | `main.py:1325-1326` |

The client calls the **shorter** `/rank-suggestions/*` form (`App.jsx:462, 620-629`). The longer form is
unused but live, and it is why the OpenAPI document contains 121 paths for 118 functions.

### 6.5 `POST /api/quests/{id}/uncomplete` is unreachable by construction

The route is fully implemented (`main.py:1078-1089` → `services.uncomplete_quest_instance`
`services.py:1154-1172`) and the client even has a pending-state label ready for it —
`if (pendingState === 'uncomplete') return { label: 'Rolling back...' }`
(`dashboard-data.js:435-437`). But **nothing ever returns `action: 'uncomplete'`**: `getQuestActionMeta`
only ever yields `action: 'complete'` or `action: 'claim'` (`dashboard-data.js:444, 454`), and the single
call site passes that value straight through (`App.jsx:508`). `[DERIVED]` The rollback affordance is
half-built on both ends and inert in practice; TASKS.md:20 records that the backlog/rollback concept
was removed, which explains the missing producer.

---

## 7. Realtime mechanisms — the honest finding

**There are none. There is no WebSocket, no SSE, no MQTT, no message broker, no long-polling, no
websocket-adjacent library, and no server push of any kind.** Evidence and the full absence argument
are in `01-discovery-inventory.md` §7; re-verified for this pass with these searches over
`frontend/src`, which returned **no matches** for any of:

`new WebSocket`, `new EventSource`, `XMLHttpRequest`, `navigator.onLine`, `sessionStorage`.

And in `backend/app/`: no `WebSocket`, no `StreamingResponse`, no `EventSourceResponse`, no
`MQTT`/`Kafka`/`Redis`/`RabbitMQ` client, no `BackgroundTasks`, no scheduler
(`01-discovery-inventory.md` §7).

### 7.1 What the product does instead

Five distinct mechanisms cover every freshness need. This is the complete list — there is nothing
else.

| # | Mechanism | Where | What it refreshes | Interval |
| --- | --- | --- | --- | --- |
| M-1 | **Load once on mount** | `App.jsx:169-176` | the six dataset loaders (data only) | once per mount |
| M-2 | **Refetch after a user action** | 17 call sites, §7.2 | the datasets each action can affect | on demand |
| M-3 | **Fixed-interval local clock tick** | `App.jsx:163-167` | `hostNow` → the top-bar "Host" time only. **Not data.** | 60 s |
| M-4 | **In-component countdown timers** | `RankExamScreen.jsx:13` (1 s, drives auto-submit), `ShadowDuel.jsx:39` (1 s game timer) | local UI state only | 1 s |
| M-5 | **Manual close/reopen and view switches** | every `open*()` helper `App.jsx:712-772`, workspace `onClose` `App.jsx:790-793` | the shell re-renders; the workspace close triggers `loadInitialData` | on demand |

Additional client-side browser APIs that are *not* data channels but affect behaviour:

- **`window.speechSynthesis`** — the Echo Chamber renders pronunciation by calling
  `new SpeechSynthesisUtterance(text)` with `en-US` and speaking it (`EchoChamber.jsx:65-77`). This
  is browser text-to-speech, one-directional. **No speech recognition exists** (no
  `SpeechRecognition`/`webkitSpeechRecognition` anywhere), so the app cannot listen.
- **`localStorage`** — the access token only (`api/client.js:3-15`). No `storage` event listener, so
  a second tab does not learn about a login or logout.
- **DOM listeners** — the *only* `addEventListener` calls in the entire frontend are `keydown` and
  `pointerdown` inside `usePresenceLayer.jsx:111-116`, used to close overlays and trap Tab. There is
  no `visibilitychange`, no `focus`/`blur`, no `online`/`offline`, no `popstate` handler.

### 7.2 Every refetch trigger (M-2), in full

18 sites carry `silent: true`; the table below lists what the user did and what gets reloaded.
`loadInitialData` = `/summary` + `/profile` + `/quests` + `/checkins` + `/vocabulary` +
`/flashcards/due`.

| User action | Refetch set | Evidence |
| --- | --- | --- |
| First mount (all six loaders) | initial + main quests + weekly + suggestions + certificates + boss battles | `App.jsx:171-176` |
| Complete or claim a quest | initial, weekly, suggestions, **main quests** (4 loaders) | `App.jsx:526-531` |
| Claim a weekly mission | initial, weekly | `App.jsx:566-569` |
| Save a check-in | initial | `App.jsx:599` |
| Apply/dismiss a suggestion | suggestions, initial | `App.jsx:630-633` |
| Unlock a rank-exam boss | initial | `App.jsx:658` |
| Exam result received | initial, suggestions | `App.jsx:681-683` |
| Exam closed/dismissed | initial | `App.jsx:692` |
| Create a certificate/test record | certificates, suggestions | `App.jsx:701-704` |
| Close the vocabulary workspace | initial | `App.jsx:792` |
| Vocabulary workspace `onLoadData` callback | initial | `App.jsx:797` |
| Status-modal profile refresh (`onProfileRefresh`) | initial | `App.jsx:948` |

`[DERIVED]` Two consequences a redesigner needs: **(1)** `main quests` is only refetched by the
quest-action path, so completing a daily quest after a long session can leave the roadmap week map
stale for everything except that one action; **(2)** no path refetches `boss-battles` after the initial
mount (`loadBossBattles` is called only at `App.jsx:176`), so the Boss overlay's data is the snapshot
taken when the app was opened.

### 7.3 Latency and staleness characteristics

- Every write is **synchronous server-side**: `complete`, `claim`, `weekly claim`, `checkins`, and
  `suggestion apply` all call `refresh_progress_state` *inside* the request before returning
  (`main.py:1135, 1185, 1213, 1320`; see `08-data-flow-traces.md` §4). There is no optimistic UI and
  no deferred job, so the response already reflects the recomputed state and the client's immediate
  refetch mostly re-reads what it was just told.
- Conversely, because the client discards the response body for most mutations and refetches instead
  (`App.jsx:526-531`),**the same data is fetched twice** for every quest action — see
  `08-data-flow-traces.md` §5.
- Freshness across tabs/devices is undefined: two browsers pointed at the same backend will not see
  each other's writes until a reload. `[UNRESOLVED]` U-11 remains open on whether that matters.
