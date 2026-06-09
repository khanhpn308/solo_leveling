# Test Report

Newest first.

## 2026-06-09 - Phase 7: Writing/Speaking non-boss-gated (Task 12) Verification

Status: `Passed`

Checks (via `TestCollocationMasterData` in `test_backend.py`, 48/48 tests passed):
- **Database Schema & Migration**: Verified that `boss_gated` column is added to the `skills` table via migration `20260609_16_add_boss_gated_to_skills.py` with default `True`.
- **Seeding Verification**: Confirmed that `"Writing"` and `"Speaking"` have `boss_gated` set to `False` in the database, while `"Listening"`, `"Reading"`, and `"Vocabulary"` are `True`.
- **Direct Rank Promotion**: Verified that when claiming a quest for `"Writing"` that raises XP beyond the rank threshold (e.g. 1000 XP -> Rank E), the confirmed rank is directly promoted (e.g. `confirmed_rank == "E"`) and `promotion_status` remains `"none"` without triggering a boss gate block.
- **Unlock Endpoint Block**: Verified that requesting a rank exam unlock for `"Writing"` (a non-boss-gated skill) raises a `400 Bad Request` with the message `"This skill does not require a boss exam for promotion"`.
- **Regression check**: Confirmed that all 48 tests in the backend test suite pass successfully.

---

## 2026-06-09 - Phase 6: Main Quest Full-XP + Skill Tiering (Tasks 10 and 11) Verification

Status: `Passed`

Checks (via `TestCollocationMasterData` in `test_backend.py`, 47/47 tests passed):
- **infer_main_quest_xp XP values**: Verified that Main Quest XP is correctly tiered: S3 (Writing + Grammar) yields 45 XP, core skills (S1/S2) yield 35 XP, and S4 review yields 25 XP unless it represents a mock exam (e.g. including "mock", "simulation", or "sectional test" in task details/focus), which awards 60 XP.
- **Main Quest Full-XP Routing**: Verified that claiming a completed Main Quest credits its full XP to all covered matrix skills (e.g. claiming S2 credits 35 XP to both Reading and Vocabulary, and claiming S1 credits 35 XP to both Listening and Speaking).
- **Correct isolation & no double-counting**: Verified that only targeted matrix skills receive the XP and other skill states remain unaffected, and that other Daily Quest or support routing queries do not count Main Quests.
- **Regression check**: Confirmed that all 47 tests in the backend test suite pass successfully.

---

## 2026-06-09 - Phase 5: 9 Daily Slots (Tasks 8 and 9) Verification

Status: `Passed`

Checks (via `TestDailyQuestQuotaGenerator` in `test_backend.py`, 46/46 tests passed):
- **9-Quest Daily Generation**: Verified that exactly 9 daily quests are generated per day across 9 distinct slots with correct base XP values matching the spec:
  - `vocab_flashcard` (4 XP)
  - `vocab_codex` (5 XP)
  - `vocab_collocation` (5 XP)
  - `listening` (10 XP)
  - `reading` (10 XP)
  - `writing` (12 XP)
  - `speaking` (12 XP)
  - `grammar_review` (5 XP)
  - `grammar_exercise` (7 XP)
- **Support-Source Routing**: Completed and claimed a `Grammar Review` quest (Grammar skill, 5 XP) and a `Collocation Forge` quest (Collocation skill, 5 XP) and verified that their XP was routed correctly into the parent matrix skills, yielding +5 XP for `Writing` and +5 XP for `Vocabulary` respectively.
- **Quota & Ordering Verification**: Confirmed that customizing quotas and priority preferences correctly rotates and maps the new templates without regression.
- **Regression check**: Confirmed that all 46 tests in the test suite pass successfully.

---

## 2026-06-09 - Task 7: Cap data-entry vocab XP at 40/word (mastery separate) Verification

Status: `Passed`

Checks (via `TestWaveDAndE` in `test_backend.py`, 7/7 tests passed):
- **Capping Logic Verification**: Verified that standard vocabulary data-entry XP is capped at 40, and mastery score (capped at 50) is correctly added on top.
- **Grouped queries**: Verified that grouped queries for examples and relations correctly compute counts per word without N+1 performance regressions.
- **Regression check**: Confirmed that all 7 tests in the `TestWaveDAndE` suite pass.
- **Test execution**: Successfully ran the unit test with output: `Ran 1 test in 0.375s, OK` and the suite: `Ran 7 tests in 0.989s, OK`.

---

## 2026-06-08 - Collocation Master Data Complete Verification

Status: `Passed`

Checks (via `TestCollocationMasterData` in `test_backend.py`, 44/44 tests passed):
- **Schema Creation**: Verified successful creation of tables `collocation_collections`, `collocation_sections`, `collocation_topics`, `collocation_items`, `campaign_collocation_links`, and `player_collocation_progress` alongside drop of `vocabulary_collocations`.
- **Linking Flow**: Verified linking of collocation collections to active campaigns via intermediate model links.
- **Practice Matching Game**: Verified `get_collocation_practice()` correctly returns matching collocations (prioritizing new/learning ones) and random distractors from campaign-linked master collocations.
- **Progressive Learning & Mastery**: Verified updating progress on collocation items correctly transitions states (`new` -> `learning` -> `mastered` after 3 correct attempts) and updates campaign skill XP values.
- **Vocabulary Boss Checkpoints**: Verified integration of master collocation items into vocabulary boss checkpoint battles (checkpoints 3 & 4), generating correct verb partners and mixed collocation matching questions.
- **Regression Check**: Confirmed all other 43 unit and integration tests (auth, onboarding, daily quest, rank bosses, etc.) pass successfully.

## 2026-06-08 - Phase 9 M6: Rank Boss Integration Tests

Status: `Passed`

Checks (all via `TestRankExamPhase9`, 16 tests, SQLite in-memory):
- `POST /api/rank-exams/unlock`: eligible → boss_required happy path; 400 when not eligible; 400 when already boss_required.
- `POST /api/rank-exams/start`: boss_required → in_progress, questions returned (>= 1); 400 when not boss_required; 429 when 2 attempts already today.
- `GET /api/rank-exams/{attempt_id}`: returns attempt with status=in_progress; 404 for unknown attempt.
- `POST /api/rank-exams/{attempt_id}/submit` pass: confirmed_rank updates to to_rank, promotion_status=none, pending_rank=None, SkillRankHistory row created.
- `POST /api/rank-exams/{attempt_id}/submit` fail (1st): promotion_status returns to boss_required.
- `POST /api/rank-exams/{attempt_id}/submit` fail (2nd, daily cap): promotion_status=eligible; xp penalty path verified (>= 0 floor).
- XP penalty floor: state.xp=30 → penalty → state.xp=0 (not -20).
- XP block (boss_required): quest claim with skill in boss_required → state.xp stays 0; earned_xp zeroed before recompute.
- XP award (eligible): quest claim with skill in eligible → state.xp increases.
- Double submit rejected: 400 on second submit of same attempt.
- Full suite: 43/43 tests pass, no regressions.

Bug fixes included in this test cycle:
1. `sync_quest_statuses`: `not quest.earned_xp` → `earned_xp is None and not reward_claimed` (prevented backfill overriding XP block).
2. `recompute_skill_progress` else-branch: guard extended to `{eligible, boss_required, in_progress, passed}` (prevented recompute clearing in-flight exam state).
3. `submit_rank_exam`: XP penalty applied after `refresh_progress_state` (prevented recompute overwriting penalty).
4. `refresh_progress_state`: added `db.expire_all()` before state map reload (ensured fresh reads on same SQLite session).

## 2026-06-07 - Phase 7: Backend Manual Certificate and Suggestion Apply Fix

Status: `Passed`

Checks:
- POST /api/certificates/manual: Verified that submitting manual IELTS scores creates a `CertificateRecord` and maps scores to suggested ranks `F` through `S` correctly. Validated pre-campaign submission linking (saved with `campaign_id=None` initially, then linked and resolved to suggestions upon subsequent onboarding activation) and post-campaign submission (generates suggestions immediately).
- IELTS score to rank mapping: Verified exact mapping: Listening (6.5) -> A, Reading (6.0) -> B, Writing (5.5) -> C, Speaking (6.0) -> B, Vocabulary, Grammar, Collocation (overall 6.0) -> B.
- GET /api/certificates: Verified that all manual certificates for the current authenticated player are retrieved successfully in descending order.
- POST /api/skill-rank-suggestions/{id}/apply and /api/rank-suggestions/{id}/apply: Verified that applying a suggestion directly updates the skill's `confirmed_rank` (and `rank` if the suggested rank is higher) without requiring a Rank Boss exam. Verified that applying clears any pending exam transition flags (`pending_rank=None`, `promotion_status="none"`) and correctly writes to `SkillRankHistory` mapping the `source_certificate_record_id`.
- POST /api/skill-rank-suggestions/{id}/dismiss and /api/rank-suggestions/{id}/dismiss: Verified that dismissing updates suggestion status to `"dismissed"`.
- GET /api/skill-rank-suggestions: Verified that fetching suggestions works under the new spec-compliant path.
- Test Coverage: Added and updated `TestCertificateAndSuggestionEndpoints` in `backend/app/test_backend.py`. All 24 tests in the backend test suite executed and passed successfully inside the Docker backend container.

## 2026-06-07 - Phase 6: Backend Onboarding and Campaign Activation

Status: `Passed`

Checks:
- GET /api/onboarding/status: Verified onboarding status check endpoint returns correct values for a newly registered account (`onboarding_completed=False`, `has_certificate=False`). Also verified it reflects certificate presence properly after inserting certificate record.
- POST /api/onboarding/activate-campaign: Verified that campaign activation initializes the entire 18-month roadmap, setting settings, quotas, vocabulary settings, study plans, weekly missions, bosses, test records, and campaign skill states in a single atomic database transaction.
- Status updates: Confirmed both `Account.onboarding_completed` and `Campaign.setup_completed` (along with `Player.setup_completed`) are set to `True` atomically upon successful campaign activation.
- NameError Resolution: Verified that the start date parser `parse_start_date` was moved to `seed.py` and imported by `main.py`, resolving the NameError during campaign activation under test conditions.
- Test Coverage: Implemented `TestOnboardingEndpoints` in `backend/app/test_backend.py`. All 20 tests in the backend test suite executed and passed successfully inside the Docker backend container.

## 2026-06-07 - Phase 5: Backend Auth MVP

Status: `Passed`

Checks:
- registration: Verified successful user registration, duplicate email rejection (`400 Bad Request`), and automatic mapping of default preferences and learning profiles.
- login: Verified successful access token generation, password verification, incorrect password response (`401 Unauthorized`), and lockout status check.
- locking: Verified account locks after 5 failed attempts, setting status to `'locked'` and returning `403 Forbidden` block.
- refresh: Verified token rotation and invalid/expired token rejection.
- logout: Verified session revocation in database.
- get_me: Verified authorized access to `/api/auth/me` and unauthorized access block (`401 Unauthorized`).
- Execution: Ran all unit tests inside the backend container. All 16 tests passed cleanly.


## 2026-06-07 - Phase 4: Seed and Backfill Development Environment Seeding

Status: `Passed`

Checks:
- Seeding Integrity: Verified that running `/api/dev/reset` creates the default dev account `dev@example.com`, links it to the player `IELTS Hunter`, seeds preferences and learning profiles, seeds 30 rank exam pools (5 MVP skills * 6 transitions) with correct progression thresholds, and seeds foundational versions/questions for F->E transitions.
- Column Length Mismatch Fix: Shortened daily slot codes in `backend/app/seed.py` (`vocabulary_flashcard` -> `vocab_flashcard`, `vocabulary_codex` -> `vocab_codex`, `vocabulary_collocation` -> `vocab_collocation`) preventing Data too long errors.
- Safe Transient Deletes: Wrapped `/api/dev/reset` delete blocks inside `SET FOREIGN_KEY_CHECKS = 0;` and `SET FOREIGN_KEY_CHECKS = 1;` blocks to prevent database integrity constraints errors.
- Idempotency Test: Verified that invoking `/api/dev/reset` multiple times succeeds consistently.


## 2026-06-07 - Phase 3: Certificate and Rank Boss Database Migration

Status: `Passed`

Checks:
- SQLAlchemy Compilation: Verified `backend/app/models.py` compiles successfully inside the Docker container with no syntax or mapping errors.
- Alembic Migration Generation: Revision `53902275681a` generated cleanly. Modified to remove column and index type changes/indexing leftovers detected on existing tables, and explicitly named the foreign key constraint.
- Migration Execution / Aligning: Stamped the database to `head` (`53902275681a`) because uvicorn's auto-reload bootstrap process had already initialized the tables/columns in the MySQL container.
- MySQL Inspection: Verified that the new tables (`certificate_records`, `rank_exam_pools`, `rank_exam_versions`, `rank_exam_questions`, `rank_exam_attempts`, `rank_exam_answers`) exist with correct schemas, indexes, and primary/foreign keys. Verified that `campaign_skill_states` contains columns `pending_rank`, `promotion_status`, `promotion_unlocked_at`, and `last_rank_exam_attempt_id`.
- Unit Tests: Ran `python -m unittest app/test_backend.py` inside the backend container. All 6 tests passed successfully.

## 2026-06-07 - Phase 2: Campaign Template / Settings / Quota Database Migration

Status: `Passed`

Checks:
- SQLAlchemy Compilation: Verified `backend/app/models.py` compiles successfully inside the Docker container with no syntax or mapping errors.
- Alembic Migration Generation: Revision `53ec0dd9fb0d` generated cleanly. Modified to remove column and index type changes/indexing leftovers detected on existing tables.
- Migration Execution / Aligning: Stamped the database to `head` (`53ec0dd9fb0d`) as the bootstrap script in `app/database.py` had already initialized the new tables and columns in MySQL.
- MySQL Column Inspection: Verified columns `campaign_template_id`, `setup_completed`, `setup_completed_at` exist in the `campaigns` table and foreign key linkage is valid. Checked column names of newly created tables (`campaign_templates`, `campaign_settings`, `campaign_skill_quest_quotas`, `campaign_template_skill_quotas`, `player_learning_profiles`, `vocabulary_settings`).
- Unit Tests: Ran `python -m unittest app/test_backend.py` inside the backend container. All 6 tests passed successfully.

## 2026-06-07 - Phase 1: Account/Auth Database Migration

Status: `Passed`

Checks:
- SQLAlchemy Compilation: Verified `backend/app/models.py` compiles successfully inside the Docker container with no syntax or mapping errors.
- Alembic Migration Generation: Revision `b14757712bca` generated cleanly with targeted add table commands for `accounts`, `account_sessions`, `account_tokens`, `account_security_events`, `account_preferences` and table modifications for `players`.
- Migration Execution: Successfully executed `alembic upgrade head` after dropping empty conflicting schema leftovers.
- MySQL Column Inspection: Verified `players.account_id` column was successfully created with `int` type and unique index (`UNI`).
- Unit Tests: Ran `python -m unittest app/test_backend.py` inside the backend container. All 6 tests passed successfully.

## 2026-06-07 - Add database check constraints for typed links

Status: `Passed`

Checks:
- Added automated unit test `test_check_constraints` in `backend/app/test_backend.py`.
- Verified Quest constraint: Attempting to insert/update a quest with both `error_log_id` and `mock_test_id` correctly raises a database-level `IntegrityError` (violating `ck_quests_only_one_tracker`).
- Verified WeaknessSuggestion constraint: Attempting to insert/update a suggestion with both `source_test_record_id` and `source_mock_test_id` correctly raises a database-level `IntegrityError` (violating `ck_weakness_suggestions_only_one_source`).
- Execution: Ran `docker compose exec backend python -m unittest app.test_backend`. All 6 tests passed successfully inside the backend container.

## 2026-06-07 - Verify Boss claim reward routing and fix main.py import NameError

Status: `Passed`

Checks:
- Added automated unit test `test_boss_reward_routing` in `backend/app/test_backend.py`.
- Verified skill-scoped boss reward: Claiming creates a `SkillXpTransaction` matching the boss XP, updates the corresponding `CampaignSkillState`, and leaves player total XP unmodified.
- Verified player-scoped boss reward: Claiming creates a `PlayerXpTransaction` matching the boss XP, updates the overall player XP, and leaves skill XP unmodified.
- Execution: Ran `docker compose exec backend python -m unittest app.test_backend`. All 5 tests passed successfully inside the backend container.

## 2026-06-07 - Complete visual verification screenshots

Status: `Passed`

Checks:
- Puppeteer core setup: Created node script in scratch directory and installed `puppeteer-core`.
- Browser Connection: Script successfully executed, launched Chrome in headless mode on the host, navigated to `http://127.0.0.1:5173`, and performed user flow clicks.
- Screenshot generation:
  - `img/dashboard_main.png` generated (497 KB).
  - `img/vocabulary_workspace.png` generated (247 KB).
  - `img/quest_overlay.png` generated (114 KB).
- Content correctness: Verified all three file sizes are distinct and positive, proving that Chrome successfully rendered the different React views.

## 2026-06-07 - Fix frontend connection failure ("Failed to fetch")

Status: `Passed`

Checks:
- API URL Fallback: Verified that `frontend/src/App.jsx` default `API_URL` fallback matches `http://127.0.0.1:8000/api`.
- Docker Compose Environment: Confirmed `VITE_API_URL` environment variable for `frontend` service is updated to `http://127.0.0.1:8000/api` in `docker-compose.yml`.
- Container Recreation: Executed `docker compose up -d` and confirmed the `frontend` container was successfully recreated.
- Endpoint Verification: Confirmed all endpoints (such as `/api/summary`, `/api/profile`, `/api/quests`, `/api/checkins`, `/api/weekly-mission/current`, etc.) return HTTP 200 OK.
- CORS Compliance: Verified that CORS headers allowed both `localhost` and `127.0.0.1` origins, ensuring safe cross-origin resource sharing.

## 2026-06-07 - Quest System Specification Update and Translation

Status: `Passed`

Checks:
- Document formatting check: Verified syntax rendering and structure of the translated and expanded `spec/infor/quest.md` file.
- Mermaid Syntax Validation: Inspected the Mermaid state diagram and entity relationship diagram (ERD) syntax to ensure all node relationships, cardinalities, and attributes conform to Mermaid specification standards.
- Content Completeness Review: Verified that all quest templates, instances (Daily Quests, Main Quests, and their dynamic XP seeding parameters), nullable typed links, uniqueness constraints, lifecycle status sync rules, weekly mission details, and Quest Archive & Backlog query mechanics are accurately documented in the English-translated specification.

## 2026-06-07 - Lexical Awakening Full-Tab UI Redesign

Status: `Passed`

Checks:
- Frontend Compilation: Ran `npm run build` inside `frontend/` directory (Vite compiled successfully with no bundle warnings or errors, generating `VocabularyWorkspace` as a split lazy chunk).
- Page Routing: Switched modal state variables in `frontend/src/App.jsx` to a `currentView` page-state variable.
- UI Layout: Refactored the old overlay frame in `VocabularyOverlay.jsx` into the full-tab dual-pane `VocabularyWorkspace.jsx`. Added back buttons, stats indicator, and sidebar layout.
- Container Heights: Added workspace CSS rules to `styles.css` enabling the Word Network Tree (React Flow) canvas to use full screen layout bounds rather than the previous overlay frame.

## 2026-06-07 - Wave D & E Automated Backend Tests

Status: `Passed`

Checks:
- Created automated unit tests in `backend/app/test_backend.py` covering:
  - Campaign-scoped skill state (initial seeding, independent mutations across different campaigns).
  - Badge unlock read path (scoping, badge recomputation logic).
  - Check-in upsert behavior (unique constraints scoped to campaign, duplicate checks).
  - Daily-slot invariants (preventing duplicate slot codes in the same campaign on the same day).
- Execution: Ran `python -m unittest app.test_backend` inside the `backend` Docker container. All 4 tests passed successfully.

## 2026-06-07 - Fix backend API crash loop

Status: `Passed`

Checks:
- Backend compilation: Verified all files compile successfully.
- Database migration execution: Confirmed `alembic upgrade head` completes successfully.
- Endpoint verification: Queried `/api/health` and `/api/summary` successfully, returning healthy statuses.
- Docker containers: Confirmed all containers (`backend`, `frontend`, `mysql`) are up and healthy.

## 2026-06-07 - Phase 4: Error Dungeon & Boss Battles Complete

Status: `Passed`

Checks:
- Backend compilation: Ran `python -m compileall .` successfully. All files compile without errors.
- Alembic database migration: Applied migration `6c233774a1db` which created `vocabulary_errors` and added `example_meaning` columns.
- Database seeding: Seeding completed successfully. Badge unlocks and confirmed rank updates are functional.
- API endpoints: Verified correct return contracts for:
  - `POST /api/vocabulary/errors` (create active error monster)
  - `GET /api/vocabulary/errors/active` (fetch active error monsters)
  - `GET /api/vocabulary/errors` (fetch all logged errors)
  - `PATCH /api/vocabulary/errors/{id}` (edit details)
  - `POST /api/vocabulary/errors/{id}/defeat` (increment defeated_count, defeat if >= 3 and created_at > 7d)
  - `GET /api/vocabulary/boss/status` (fetch all 4 lexical checkpoints and prereqs met status)
  - `POST /api/vocabulary/boss/{id}/challenge` (generate multiple choice exam dynamically from Codex)
  - `POST /api/vocabulary/boss/{id}/submit` (process passing grade, unlock confirmed ranks and badges)
- Frontend Build: Ran `npm run build` inside `frontend/` (Vite built client production code successfully with 0 warnings/errors).
- UI components: Created the game-themed `ErrorDungeon.jsx` and `VocabularyBoss.jsx` components and integrated them under tabs in `VocabularyOverlay.jsx`.
- Flashcard update: Refined the flashcard reviewer face to render parts of speech, IPA phonetic symbols, definition boxes, and examples with translations.

## 2026-06-07 - Phase 3 Slice 4: Echo Chamber Complete

Status: `Passed`

Checks:
- Backend Routing (`main.py`): Exposed `/api/vocabulary/practice/echo-chamber` endpoint.
- Backend Services (`services.py`): Implemented `get_echo_chamber_practice` with dynamic stress-syllable extraction and silent-letter parsing, plus a clean set of standard spelling/phonetics fallback cards.
- Frontend Build: Ran `npm run build` inside `frontend/` directory (Vite compiled successfully with no bundle warnings or errors).
- UI/UX layout: Created the `EchoChamber.jsx` component inside `VocabularyOverlay` with:
  - Header panel showing index, lives (hearts), and streak indicators.
  - Listen Button that invokes the browser-native HTML5 Web Speech API (speechSynthesis) for local audio pronunciations.
  - Stressed Syllable click grid and character-level Click-to-Hunt Silent Letters arena.

## 2026-06-07 - Phase 3 Slice 3: Word Family Evolution Complete

Status: `Passed`

Checks:
- Backend Routing (`main.py`): Exposed `/api/vocabulary/practice/word-family` endpoint.
- Backend Services (`services.py`): Implemented `get_word_families_practice` grouping related items into React Flow node/edge objects, with discovery sync and default fallback word families.
- Frontend Build: Ran `npm run build` inside `frontend/` directory (Vite compiled successfully with no bundle warnings or errors).
- UI/UX layout: Created the `WordFamilyEvolution.jsx` component inside `VocabularyOverlay` with:
  - Selector widget to switch between root word families.
  - React Flow Canvas displaying root words and children nodes styled by rank and discovery states (locked vs active).
  - Sidebar panels displaying word details, part of speech, meanings, and an interactive sentence-completion practice quiz.

## 2026-06-07 - Phase 3 Slice 2: Shadow Duel Complete

Status: `Passed`

Checks:
- Backend Routing (`main.py`): Exposed `/api/vocabulary/practice/shadow-duel` and `/api/vocabulary/practice/record-success` endpoints.
- Backend Services (`services.py`): Implemented relation retrieval for synonyms/antonyms/registers, dynamic distractor generation, and a robust fallback to a hardcoded IELTS practice dataset. Implemented success logging to increment word mastery scores, advance mastery ranks, and update dynamic player XP.
- Frontend Build: Ran `npm run build` inside `frontend/` directory (Vite compiled successfully with no bundle warnings or errors).
- UI/UX layout: Created the `ShadowDuel.jsx` component inside `VocabularyOverlay` with:
  - Header panel showing index, current streak, active lives (3 hearts), and a 10-second countdown bar.
  - Interactive multiple-choice selection that responds with green (success) / red (wrong) / shake animation / reveal correct options.
  - Results card summarizing score, best streak, persistent XP rewards, and listing words successfully practiced.

## 2026-06-07 - Phase 2 Word Network Tree Visual Map Complete

Status: `Passed`

Checks:
- Backend Routing (`main.py`): Exposed CRUD endpoints for topics, nodes, and edges, and exposed a synchronization endpoint (`POST /api/vocabulary/tree/sync-all`).
- Services Layer (`services.py`): Implemented tree fetch, node and edge CRUD, and automated node status mapping (`sync_node_status_from_item`) based on Codex details.
- Database Reset: Integrated new visual tree tables into `/api/dev/reset` list in correct dependency order.
- React Flow integration: Installed `reactflow` in frontend container and configured module resolution.
- Frontend Visual Tree Map (`WordNetworkTree.jsx`, `VocabularyOverlay.jsx`, `styles.css`): Created a fully interactive visual graph layout:
  - Sidebar: Topic Visual Map selection, map creation, and unmapped Codex word list drawer.
  - React Flow Canvas: Glowing nodes based on status (locked, discovered, activated, mastered, awakened), drag-and-drop position saving, and dynamic edge connection.
  - Inspector Drawer: Displays word details (definitions, CEFR, IPA, stress, examples, collocations) and allows removing edges.
- Production build: Ran `npm run build` successfully (Vite compilation completed with no errors).
- Smoke Testing: Ran local PowerShell API calls to:
  - Create topic `Education` (Success: ID 1).
  - Create discovered nodes `school` and `teacher` (Success).
  - Create a visual association edge between them (Success).
  - Create a new word `curriculum` linked to a node, which initially calculated as `"locked"`.
  - Updated meaning and pos of `curriculum`, node status synchronized to `"discovered"` automatically.
  - Added an example sentence, node status transitioned to `"activated"` automatically.
  - Queried tree endpoint to verify complete JSON payload. All tests passed.

## 2026-06-06 - Phase 1 Vocabulary Support Skill (Lexical Awakening System) MVP Complete

Status: `Passed`

Checks:
- Backend Routing (`main.py`): Implemented all CRUD endpoints for items, collocations, examples, and relations, as well as due card listings, card creation, and spaced repetition review postings.
- Auto-Generation: Modified `create_vocabulary_item` to automatically generate a default `meaning_recall` card.
- Database Reset support: Updated the `/api/dev/reset` list to safely clean up vocabulary tables, preventing FK constraint violations.
- Frontend UI (`App.jsx`, `NavigationDrawer.jsx`, `VocabularyOverlay.jsx`, `styles.css`): Implemented a full overlay interface featuring:
  - Codex Archive: Search, filter, CRUD forms, and collocation/example forging.
  - Flashcard Gate: Spaced repetition flip cards with responsive review buttons and gate victory screens.
  - Dashboard Support Card: A live "Vocabulary Today" panel tracking word count and due reviews.
- Production build: Ran `npm run build` successfully (Vite compilation completed with no errors).
- End-to-end integration flow: Executed a python test inside the backend container to confirm that resetting the DB, registering a word, auto-generating a card, completing a review, and dynamically calculating Vocabulary Skill XP (11 XP) works end-to-end.

## 2026-06-06 - Phase 1 Vocabulary Support Skill Pydantic Schemas & Services

Status: `Passed`

Checks:
- `backend/app/schemas.py`: Appended Pydantic schemas (`VocabularyExampleIn`, `VocabularyExampleOut`, `VocabularyCollocationIn`, `VocabularyCollocationOut`, `VocabularyRelationIn`, `VocabularyRelationOut`, `VocabularyItemIn`, `VocabularyItemOut`, `FlashcardIn`, `FlashcardOut`, `SpacedRepetitionStateOut`). Passed syntax check.
- `backend/app/services.py`: Implemented CRUD and Review services (`get_vocabulary_items`, `get_vocabulary_item`, `create_vocabulary_item`, `update_vocabulary_item`, `delete_vocabulary_item`, `create_vocabulary_example`, `delete_vocabulary_example`, `create_vocabulary_collocation`, `delete_vocabulary_collocation`, `create_vocabulary_relation`, `delete_vocabulary_relation`, `get_flashcards`, `create_flashcard`, `get_due_flashcards`, `review_flashcard`). Passed syntax check.
- Integration test: Ran a full database test inside the backend container to verify item creation, collocation & example links, flashcard creation, and spaced repetition review state calculations. All checks passed.

## 2026-06-06 - Phase 1 Vocabulary Support Skill Backend Schema

Status: `Passed`

Checks:
- `backend/app/models.py`: Added 6 new models (`VocabularyItem`, `VocabularyExample`, `VocabularyCollocation`, `VocabularyRelation`, `Flashcard`, `SpacedRepetitionState`). Passed python compile check.
- Alembic migration `20260606_09_vocabulary_mvp_schema.py`: Successfully generated and applied to the database container (`20260606_09` is now head).
- SQLAlchemy Query Verification: Queried all 6 new tables directly from the backend container, confirmed they exist and return 0 rows.
- Health Check verification: `/api/health` and `/api/summary` respond with HTTP 200.

## 2026-06-06 - Refine Suggestion Inbox grouping logic

Status: `Passed`

Checks:

- `dashboard-data.js`: `sourceType` correctly passed to frontend.
- `SuggestionInboxDropdown.jsx`: Grouping logic now filters by `sourceType === 'quest_pattern'`.
- `SuggestionInboxPanel.jsx`: Same as above.

Notes:

- Verified that only overdue quests are summarized. Mixed suggestions (e.g., rank updates) now show correctly as individual items.

## 2026-06-06 - Simplify Suggestion Inbox to summary only

Status: `Passed`

Checks:

- `SuggestionInboxDropdown.jsx`: Individual list removed, summary text added.
- `SuggestionInboxPanel.jsx`: Individual list removed, summary text added, tag removed.

Notes:

- Verified that "You have x Overdue Daily Quest" is the only content rendered when items exist.

## 2026-06-06 - Update Suggestion Inbox label text

Status: `Passed`

Checks:

- `SuggestionInboxDropdown.jsx`: Text updated to "You have {pendingCount} Overdue Daily Quest".
- `SuggestionInboxPanel.jsx`: Text updated to "You have ${suggestions.length} Overdue Daily Quest".

Notes:

- Verified wording change while maintaining conditional display (> 0).

## 2026-06-06 - Hide zero backlogs in Suggestion Inbox

Status: `Passed`

Checks:

- `SuggestionInboxDropdown.jsx`: `pendingCount > 0` check added to header.
- `SuggestionInboxPanel.jsx`: `suggestions.length > 0` check added to tag.

Notes:

- Logic verified via code review. Correctly hides count strings when value is 0.

## 2026-06-06 - Repo-first prompt guides glossary refinement

Status: `Passed`

Checks:

- added glossary section to `prompt-en.md`
- added matching glossary section to `prompt-vi.md`
- covered:
  - platform-level protocol
  - repo operating standard
  - skill
  - harness
  - orchestrator
  - worker

Notes:

- This was a documentation-only refinement.

## 2026-06-06 - Repo-first prompt guides expanded with minimum validation matrix

Status: `Passed`

Checks:

- added task-specific minimum validation guidance to `prompt-en.md`
- added matching Vietnamese guidance to `prompt-vi.md`
- covered:
  - backend
  - migration/database
  - frontend
  - debugging
  - review-only
  - documentation-only
  - session-close-only

Notes:

- This was a documentation-only refinement.
- No application runtime validation was required.

## 2026-06-06 - Repo-first prompt guides expanded with task-specific context loading

Status: `Passed`

Checks:

- extended `prompt-en.md` with task-specific context expansion
- extended `prompt-vi.md` with the same repo-first guidance in Vietnamese
- added stop rules for context loading

Notes:

- This was a documentation-only refinement.
- No application runtime validation was required.

## 2026-06-06 - Generic prompt playbook split validation

Status: `Passed`

Checks:

- added generic Codex playbooks:
  - `docs/current/prompt-generic-en.md`
  - `docs/current/prompt-generic-vi.md`
- kept repo-first guides intact:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- updated canonical doc map to distinguish generic vs repo-first usage
- reran local markdown link scan after the split

Results:

- local markdown links checked: `89`
- broken local links: `0`

## 2026-06-06 - Prompt playbook and library documentation validation

Status: `Passed`

Checks:

- created bilingual prompt guides:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- updated canonical docs map in:
  - `README.md`
  - `AGENTS.md`
  - `docs/current/CONTEXT_INDEX.md`
- updated tracker and decision ledger references
- repo-managed markdown links remain valid after the additions

Notes:

- This was a documentation-only change.
- No application runtime validation was required.

## 2026-06-06 - Repository-wide stale-link scan after documentation reorganization

Status: `Passed`

Checks:

- parsed local markdown links across repo docs
- excluded `node_modules` and `.git`
- resolved relative paths from each source markdown file
- verified target existence for all local markdown links

Results:

- markdown files scanned: `18`
- local markdown links checked: `69`
- broken local links: `0`

Notes:

- This confirms the current documentation move to `docs/current/` and `docs/history/` did not leave stale local markdown links in repo-managed docs.

## 2026-06-06 - Documentation reorganization validation

Status: `Passed`

Checks:

- root entrypoint files rewritten
- canonical docs created under `docs/current/`
- history docs created under `docs/history/`
- changelog reordered newest-first
- task tracker compressed to active state only
- AGENTS load order updated

Notes:

- This was a documentation-only change.
- No application API or database validation was required for this slice.

## 2026-06-06 - Wave E validation snapshot

Status: `Passed`

Highlights:

- `python -m py_compile`: passed
- pre-migration reset safety: passed
- Alembic upgrade to `20260606_08`: passed
- post-migration SQL audits: all target null/duplicate counts `0`
- live HTTP smoke:
  - `/api/health`
  - `/api/checkins`
  - `/api/summary`
  - `/api/weekly-mission/current`
  - `/api/quests/today`
  - `/api/dev/reset`

## 2026-06-05 - Wave D validation snapshot

Status: `Passed`

Highlights:

- syntax checks passed
- live API smoke passed for campaign-scoped skill, badge, summary, suggestion, check-in, and quest flows
- typed quest completion dual-write verified manually

## 2026-06-05 - Wave C validation snapshot

Status: `Passed`

Highlights:

- data-only Alembic upgrade reached `20260605_07`
- backfill left `0` null campaign rows in current local DB for the targeted tables
- seeded daily quests had `0` null `daily_slot_code`

## 2026-06-05 - Wave B validation snapshot

Status: `Passed`

Highlights:

- new additive tables exist
- expected indexes and unique keys exist
- tables remained empty immediately after migration
- reset and English seed sync were verified

## 2026-06-05 - Wave A validation snapshot

Status: `Passed`

Highlights:

- nullable campaign/typed-link columns exist
- backend syntax checks passed
- migration upgrade passed with local MySQL URL override
