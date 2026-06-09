# Agent Notes

Newest first.

## 2026-06-09 - Phase 7: Writing/Speaking non-boss-gated (Task 12)

- Added `boss_gated` field (`Boolean`, default `True`) to the `Skill` model in `models.py`.
- Created Alembic migration `20260609_16_add_boss_gated_to_skills.py` to add `boss_gated` column to the `skills` table with a server default of `1`.
- Updated `ensure_skills()` in `seed.py` to seed `boss_gated = False` for `"Writing"` and `"Speaking"` and `True` for all other skills (Listening, Reading, Vocabulary, Collocation, Grammar).
- Updated `recompute_skill_progress()` in `services.py` to bypass rank boss promotion gating when the skill's `boss_gated` is false, directly promoting `confirmed_rank` to `rank` and resetting/clearing exam/promotion states.
- Added guard to `/api/rank-exams/unlock` in `main.py` blocking exam unlocks for non-boss-gated skills with a `400 Bad Request`.
- Added `test_non_boss_gated_skills` unit test to `test_backend.py` asserting correct seeding, direct rank promotion on quest claim, and unlock endpoint block.
- Ran tests successfully; all 48 tests passed.
- Marked Task 12 as completed in `TASKS.md`, keeping gap checks unchecked for review.

---

## 2026-06-09 - Phase 6: Main Quest Full-XP + Skill Tiering (Tasks 10 and 11)

- Updated `infer_primary_skill` in `seed.py` to fall back to searching `task_detail` for matrix skill name keywords when resolving the primary skill, which properly maps S4 review sessions to their weekly dominant skill focus.
- Rewrote `infer_main_quest_xp` in `seed.py` to tier XP by skill column: S3 -> 45 XP, S1/S2 -> 35 XP, S4 standard review -> 25 XP, and mock exam -> 60 XP. Passed `session.task_detail` to the function calls.
- Added `resolve_main_quest_covered_skills` helper in `services.py` to map Main Quest session number and primary skill to the exact set of matrix skills covered (S1 -> Listening & Speaking, S2 -> Reading & Vocabulary, S3 -> Writing, S4 -> dominant skill).
- Refactored `recompute_skill_progress` in `services.py` to credit the full Main Quest earned XP to every resolved covered matrix skill. Excluded Main Quests from Daily Quest and support routing queries to avoid double-counting.
- Added `test_main_quest_xp_and_routing` unit/integration tests to `TestCollocationMasterData` in `test_backend.py`.
- Ran backend unit tests successfully; all 47 tests pass.
- Marked Tasks 10 and 11 as completed in `TASKS.md`, keeping gap checks unchecked for review.

## 2026-06-09 - Phase 5: 9 Daily Slots (Tasks 8 and 9)

- Verified that database schema `daily_slot_code` is `sa.String(length=20)` and natively supports the 9 slots without additional constraints.
- Updated `quest_template_seed()` in `seed.py` to seed exactly the 9 redesigned daily quest templates with their spec names, skills, and base XP values.
- Updated template quotas in `ensure_campaign_templates()` and campaign quotas copying in `ensure_campaign_settings_and_quotas()` to reflect the new 9-quest structure.
- Refactored `slot_mapping` and resolved daily quest `skill_id` using the template's primary skill (`primary_skill.name`) in `ensure_quest_instances()`, allowing correct support-source routing (Grammar -> Writing, Collocation -> Vocabulary).
- Added `test_nine_daily_slots_generation_and_routing` unit/integration test in `test_backend.py`.
- Ran the full test suite; all 46 tests passed successfully.
- Marked Tasks 8 and 9 as completed in `TASKS.md`, leaving the gap checks unchecked for peer review.

## 2026-06-09 - Task 7: Cap data-entry vocab XP at 40/word (mastery separate)

- Restructured `compute_vocabulary_xp` in `services.py` to cap vocabulary data-entry XP at 40 per word, keeping mastery score (up to 50) separate.
- Added queries to group examples and relations by item to prevent N+1 database queries when calculating XP.
- Added `test_vocabulary_anti_farm_cap` unit test in `test_backend.py` to assert correct capping behavior and that mastery score is added separately.
- Ran tests successfully; all 7 tests in `TestWaveDAndE` pass.
- Left the gap check unchecked in `TASKS.md` for peer review.

## 2026-06-08 - Collocation Master Data System Complete

- Cleaned up all legacy references to the deprecated `VocabularyCollocation` model and `vocabulary_collocations` database table in `services.py` and `test_backend.py`.
- Removed stale `joinedload(VocabularyItem.collocations)` loads from vocabulary and flashcard services.
- Refactored vocabulary boss checkpoints 3 (Collocation Hunter) and 4 (Lexical Awakening) inside `challenge_vocabulary_boss` to query from the new campaign-linked `CollocationItem` table.
- Added comprehensive unit test coverage verifying that calling the vocabulary boss checkpoint generation logic for boss 3 and 4 successfully builds spelling/phonetics and collocation questions using the new master collocation tables.
- Ran the full pytest suite. All 44 tests pass successfully with no errors or regressions.

## 2026-06-08 - Phase 9 M6: Integration Tests Complete + 3 Bug Fixes

- Added `TestRankExamPhase9` (16 tests) to `backend/app/test_backend.py`. All 43 tests pass.
- **Bug 1 fixed — `recompute_skill_progress` else-branch clobbered in-flight exam state**: Guard condition extended to `{"eligible", "boss_required", "in_progress", "passed"}` so recompute never resets `promotion_status` while an exam is active.
- **Bug 2 fixed — `sync_quest_statuses` overrode XP-blocked quest's earned_xp**: Guard `if not quest.earned_xp` changed to `if quest.earned_xp is None and not quest.reward_claimed` — prevents backfill from restoring 0-XP blocked quests to `xp` value.
- **Bug 3 fixed — XP penalty recompute race**: In `submit_rank_exam`, penalty (`state.xp -= 50`) moved to AFTER `refresh_progress_state` call with explicit `db.refresh(state)` so it is not overwritten by recompute.
- Root cause of Bug 2 discovered via systematic debug: `sync_quest_statuses` runs inside `refresh_progress_state` (called in claim endpoint), and `not quest.earned_xp` is truthy for 0 → backfilled to original `xp=20`.
- `refresh_progress_state` now calls `db.expire_all()` before `get_campaign_skill_state_map` to guarantee fresh reads after prior commits on same SQLite StaticPool session.

## 2026-06-08 - Pre-Phase 9: Promotion Status Design Resolved

- Decided to keep `eligible` state: player may accumulate XP freely while eligible, and chooses when to challenge the boss.
- Two-step unlock: `POST /api/rank-exams/unlock` (eligible → boss_required, XP blocked) then `POST /api/rank-exams/start` (boss_required → in_progress, attempt created).
- XP block rule: when `promotion_status` is `boss_required` or `in_progress`, quest claim for that skill awards 0 XP. Quest can still be completed.
- Daily cap: 2 attempts/day per (campaign_id, skill_id, from_rank). After 2 failures → subtract 50 from `campaign_skill_states.xp` (floor 0), reset to `eligible`, XP unblocked, retry tomorrow.
- Red dot UI cue triggered at `eligible` state.
- Full state machine, retry counting SQL pattern, and XP block rule documented in `docs/current/SCHEMA_SEMANTICS.md`.
- `services.py:recompute_skill_progress` currently jumps to `boss_required` directly — Phase 9 must fix this to `eligible`.
- Also added `POST /api/dev/regenerate-quests` endpoint (idempotent daily quest re-generator, no DB reset).

## 2026-06-07 - Phase 8: Backend Daily Quest Skill Quota Generator — Verified Already Complete

- Audited `seed.py:ensure_quest_instances` (line 1216) and confirmed it fully implements the Phase 8 spec: reads `CampaignSkillQuestQuota`, maps skill → slot codes, respects `daily_quota` limit, orders by `preferred_activity_types`, and enforces `(campaign_id, quest_date, daily_slot_code)` uniqueness both via DB constraint and in-memory dedup set.
- `activate_campaign_for_player` (line 1972) calls `ensure_quest_instances` at onboarding time — fully wired.
- No code changes needed. Phase 8 was implemented as part of Phase 4/6 work and not yet marked done.
- Next unstarted phase: **Pre-Phase 9** — resolve `promotion_status` state machine design before implementing Rank Boss logic.

## 2026-06-07 - Phase 7: Backend Manual Certificate and Suggestion Apply Fix Complete

- Implemented `map_ielts_score_to_rank` and `create_rank_suggestions_for_certificate` in `backend/app/services.py` to map scores to ranks `F` through `S` according to project progression semantics.
- Updated `apply_rank_suggestion` to update `state.confirmed_rank` (and `state.rank` if the suggestion is higher), clear any pending boss exam constraints, and log the `source_certificate_record_id` to history.
- Implemented `POST /api/certificates/manual` and `GET /api/certificates` endpoints in `backend/app/main.py`.
- Added spec-compliant endpoint aliases `@app.get("/api/skill-rank-suggestions")`, `@app.post("/api/skill-rank-suggestions/{suggestion_id}/apply")`, and `@app.post("/api/skill-rank-suggestions/{suggestion_id}/dismiss")` in `backend/app/main.py` to ensure backend routes match both the specification and frontend expectations.
- Updated campaign activation flow (`POST /api/onboarding/activate-campaign`) to automatically link pre-existing certificate records (created during onboarding step 1) to the new campaign, generating suggestions immediately.
- Refactored suggestion apply/dismiss endpoints to secure them with `Depends(get_current_account)` and ensure multi-user campaign isolation.
- Added and updated `TestCertificateAndSuggestionEndpoints` in `backend/app/test_backend.py` validating manual certificate mappings, pre/post-campaign suggestions, direct promotions, dismissals, and spec-compliant suggestion path verification.
- Ran backend unit tests inside the container. All 24 tests passed successfully.

## 2026-06-07 - Phase 6: Backend Onboarding and Campaign Activation Complete

- Implemented onboarding endpoints `/api/onboarding/status` and `/api/onboarding/activate-campaign` in `backend/app/main.py`.
- Linked `activate_campaign_for_player` programmatically within a single, atomic database commit transaction.
- Refactored `parse_start_date` function from `backend/app/main.py` into `backend/app/seed.py` so it can be resolved without circular import issues by the campaign activator.
- Implemented `TestOnboardingEndpoints` class in `backend/app/test_backend.py` covering onboarding status checks, manual certificate registration flags, transactional campaign activations, and authorization controls.
- Ran backend unit tests inside the container. All 20 tests passed successfully.

## 2026-06-07 - Phase 5: Backend Auth MVP Complete

- Added `TestAuthEndpoints` class to `backend/app/test_backend.py` containing 10 integration tests validating the auth lifecycle.
- Configured SQLite in-memory engine under `TestAuthEndpoints` with `StaticPool` and `connect_args={"check_same_thread": False}` to support multi-threaded test client requests by FastAPI's server workers.
- Fixed a bug in `POST /api/auth/register` where un-flushed `player.id` was passed to `PlayerLearningProfile`, resulting in database integrity failures. Swapped to using relationship object binding `player=player`.
- Fixed a bug in `POST /api/auth/login` where account lock status was verified after checking credentials, making account locking bypassed by incorrect passwords. Reordered lock checks to precede password validation.
- Appended `httpx` dependency to `backend/requirements.txt` and installed it in backend container to support TestClient.
- Successfully ran the entire test suite inside the container and confirmed all 16 tests pass cleanly.


## 2026-06-07 - Phase 4: Seed and Backfill Development Environment Seeding

- Modified `backend/app/seed.py` to shorten vocabulary slot codes (`vocabulary_flashcard` -> `vocab_flashcard`, `vocabulary_codex` -> `vocab_codex`, `vocabulary_collocation` -> `vocab_collocation`) to fit the database `String(20)` length constraint on `daily_slot_code`.
- Modified `backend/app/main.py` to temporarily disable MySQL foreign key checks (`SET FOREIGN_KEY_CHECKS = 0/1;`) in `reset_database` endpoint (`/api/dev/reset`) to ensure deletes succeed regardless of table dependency order.
- Enabled `PYTHONUNBUFFERED=1` in `docker-compose.yml` to allow instant flushing of container logs.
- Recreated the backend container and successfully invoked the `/api/dev/reset` endpoint, verifying that all dev accounts, preferences, learning profiles, campaign templates, vocabulary settings, and 30 rank exam pools are cleanly and idempotently seeded.


## 2026-06-07 - Phase 3: Certificate and Rank Boss Database Migration

- Defined SQLAlchemy 2.0 models for manual certificate input and the Rank Boss Exam system (`CertificateRecord`, `RankExamPool`, `RankExamVersion`, `RankExamQuestion`, `RankExamAttempt`, and `RankExamAnswer`) in `backend/app/models.py`.
- Modified `CampaignSkillState` with fields `pending_rank`, `promotion_status` (defaulting to `'none'`), `promotion_unlocked_at`, and `last_rank_exam_attempt_id` (pointing to `rank_exam_attempts.id`).
- Set up relationships in `Player` and `Campaign` classes to link with certificate records and rank attempts.
- Ran `alembic revision --autogenerate -m "add_certificate_and_rank_boss_tables"` inside the container to generate migration `53902275681a`.
- Cleaned the autogenerated Alembic migration of unrelated type change/index modification noise and explicitly named the foreign key constraint.
- Stamped the Alembic database state to `head` (`53902275681a`) because uvicorn's reload bootstrapping automatically ran and created the tables/columns in the MySQL container.
- Inspected the newly created tables and columns in MySQL and verified correct schema setup.
- Ran backend unit tests successfully inside the Docker container.

## 2026-06-07 - Phase 2: Campaign Template / Settings / Quota Database Migration

- Defined SQLAlchemy 2.0 models for template, settings, and quest quotas tables (`CampaignSetting`, `CampaignTemplateSkillQuota`, `CampaignSkillQuestQuota`, and `VocabularySetting`) in `backend/app/models.py`.
- Modified `Campaign` and `CampaignTemplate` with foreign keys, columns, and relationship back-population hooks.
- Ran `alembic revision --autogenerate -m "add_campaign_template_and_quotas"` inside the container to generate migration `53ec0dd9fb0d`.
- Cleaned the autogenerated Alembic migration of unrelated type change/index modification noise.
- Named the foreign key constraint on `campaigns` explicitly to avoid downgrade errors.
- Since the bootstrap script in `app/database.py` created the tables/columns upon container restart, stamped the Alembic database state to `head` (`53ec0dd9fb0d`) to align tracking.
- Inspected columns of new tables and confirmed correct data schema in MySQL.
- Verified backend unit tests pass cleanly inside the Docker container.

## 2026-06-07 - Phase 1: Account/Auth Database Migration

- Defined Pydantic-compatible SQLAlchemy 2.0 models for account-scoped tables: `Account`, `AccountSession`, `AccountToken`, `AccountSecurityEvent`, and `AccountPreference` in `backend/app/models.py`.
- Linked `Player` model with `account_id` foreign key pointing to `accounts.id` and established a bidirectional mapping.
- Ran `alembic revision --autogenerate -m "add_account_auth_tables"` inside the container to generate the initial script.
- Cleaned the autogenerated Alembic migration `b14757712bca_add_account_auth_tables.py` by removing index and type alteration noise on unrelated vocabulary/spaced-repetition tables to avoid runtime risks.
- Dropped pre-existing empty conflicting tables in local MySQL database and executed the migration (`alembic upgrade head`).
- Confirmed `players.account_id` unique key constraint exists.
- Ran backend unit tests successfully inside the Docker container.

## 2026-06-07 - Phase 0: Big Update Documentation and ADR Preparation

- Updated `DECISIONS.md` to record the accepted architectural decisions for the Big Update (Account system, mandatory onboarding, manual certificate rank suggestion application, XP-based Rank Boss promotion retries/limits, out-of-scope Writing/Speaking exams, and skill quota daily quest slots).
- Expanded `docs/current/DATABASE_SCHEMA.md` to categorize account-scoped tables, player-wide tables, campaign-scoped tables, and template/definition tables, along with new unique keys and foreign key constraints.
- Updated `docs/current/SCHEMA_SEMANTICS.md` to define new state/status fields (`pending_rank`, `promotion_status`, `accounts.status`, `accounts.role`, and `rank_exam_attempts.status`) and scope layers.
- Appended the detailed checklist tracking the 16 implementation phases (Phase 0 to Phase 15) to `TASKS.md` and registered deferred backlog items.

## 2026-06-07 - Add database check constraints for typed links

- Generated Alembic migration `089adadeddde_add_typed_links_check_constraints.py` to add MySQL check constraints:
  - `ck_quests_only_one_tracker` checks that at most one of `error_log_id`, `writing_entry_id`, `speaking_entry_id`, or `mock_test_id` is set.
  - `ck_weakness_suggestions_only_one_source` checks that at most one of `source_test_record_id`, `source_mock_test_id`, `source_error_log_id`, or `source_quest_id` is set.
- Added automated verification test `test_check_constraints` in `backend/app/test_backend.py`.
- Ran migrations (`alembic upgrade head`) and successfully validated all 6 backend tests.
- Archived completed Deferred Backlog items to `tasks-done.md`.

## 2026-06-07 - Verify Boss claim reward routing and fix main.py import NameError

- Added `test_boss_reward_routing` inside `backend/app/test_backend.py` covering skill-specific and player-scoped boss claim routing logic.
- Fixed a `NameError` in `backend/app/main.py` caused by a missing import of `datetime` by adding it to `from datetime import date, datetime, timedelta`.
- Ran backend unit tests successfully inside the Docker container to verify the new claim reward routing logic.
- Updated `TASKS.md` to set the related boss reward transaction verification tasks to `Done`.

## 2026-06-07 - Complete visual verification screenshots

- Wrote a Node.js automation script using `puppeteer-core` in `scratch/capture.js` to drive the host Chrome instance.
- Captured three screenshots verifying dashboard and key overlays:
  - `d:/better_english/ielts-quest-dashboard/img/dashboard_main.png` (Main command core dashboard view)
  - `d:/better_english/ielts-quest-dashboard/img/vocabulary_workspace.png` (Vocabulary support skill workspace via navigation drawer trigger)
  - `d:/better_english/ielts-quest-dashboard/img/quest_overlay.png` (Daily Quest Panel layout)
- Verified all screenshots captured correct, active React components.
- Marked task 1 under Next Tasks in `TASKS.md` as `Done`.

## 2026-06-07 - Fix frontend "Failed to fetch" connection issue

- Changed API fallback URL in `frontend/src/App.jsx` from `localhost` to `127.0.0.1`.
- Changed `VITE_API_URL` in `docker-compose.yml` for the frontend service to `http://127.0.0.1:8000/api`.
- Recreated the frontend container using `docker compose up -d` to apply environment variable updates.
- This ensures the browser connects directly using `127.0.0.1` loopback IP, bypassing IPv6 resolution mismatches or HSTS / HTTPS-first upgrade policies in modern Chrome on Windows hosts.

## 2026-06-07 - Skill-Specific Quest XP Routing Decision and Tasks Tracking

- Read and analyzed `spec/feature/skill_specific_quest_xp_routing_spec.md`.
- Added a new tracker section to `TASKS.md` detailing the 7 implementation tasks for the Quest XP Routing & Vocabulary Daily Quest feature.
- Recorded the decision to reuse the generic Quest system and add transaction-based XP routing tables (`skill_xp_transactions`, `player_xp_transactions`) in `DECISIONS.md`.
- Marked `Task 1 — Docs / ADR Decision` subtasks as `Done` in `TASKS.md`.

## 2026-06-07 - Quest System Specification Update and Translation

- Translated the Vietnamese quest specification (`spec/infor/quest.md`) to English.
- Expanded the specification with detailed definitions and schemas for `QuestTemplate` and `Quest` instances.
- Documented Main Quests (roadmap session linkages, dynamic XP rules, unique constraint bypasses).
- Documented Quest Archive and Backlog query mechanics, backlog grace periods, and late completion/claiming.
- Documented nullable typed evidence tracking columns (`error_log_id`, `writing_entry_id`, `speaking_entry_id`, `mock_test_id`).
- Detailed the uniqueness constraint `uq_quests_campaign_date_daily_slot` on quests.
- Documented the status lifecycle transitions and `sync_quest_statuses` logic (handling overdue and expired tasks).
- Detailed the 50% XP penalty rule for late completions and reward banking explicit claiming mechanisms.
- Documented the parent-child structure of Weekly Missions (`weekly_missions` and `weekly_mission_items`) and detail progress item triggers.
- Updated the Mermaid ERD visualization to model all entities, templates, and evidence tracker linkages.

## 2026-06-07 - Lexical Awakening Full-Tab UI Redesign

- Created `frontend/src/components/VocabularyWorkspace.jsx` to render the full-tab view, removing `OverlayFrame` wraps.
- Implemented state-based view switching (`currentView` of `'dashboard'` or `'vocabulary'`) in `frontend/src/App.jsx`.
- Modified navigation drawers, top bars, and command panel buttons to trigger the new view.
- Added comprehensive layout and navigation styles in `frontend/src/styles.css`, adjusting the heights of child components (like `WordNetworkTree`'s React Flow canvas) to utilize full screen height bounds.
- Verified that the production build (`npm run build`) runs and compiles cleanly with zero warnings or errors.

## 2026-06-07 - Wave D & E Automated Backend Tests

- Created `backend/app/test_backend.py` to write automated tests for Wave D & E behavior.
- Covered campaign-scoped skill state management, campaign-scoped badge unlocks, campaign-scoped check-in uniqueness, and daily-slot code unique constraints.
- Updated `backend/app/models.py` to add `__table_args__` unique constraints for `Quest` and `CheckIn` models to match the database schema exactly.
- Ran tests successfully inside the Docker backend container.

## 2026-06-07 - Fix backend API crash loop

- Diagnosed the root cause of `API ERROR: Failed to fetch` as a backend crash loop on startup.
- The app crashed during database inspection in `refresh_progress_state` because the `vocabulary_errors` table was missing.
- Modified migration `6c233774a1db_add_vocabulary_errors.py` to make table and column creation idempotent.
- Ran migration successfully and verified that backend starts and registers `/api/health` as online.

## 2026-06-07 - Phase 4: Error Dungeon & Boss Battles Complete

- Created `vocabulary_errors` database table via Alembic migration `6c233774a1db`.
- Added `example_meaning` fields to `vocabulary_examples` and `vocabulary_collocations` tables.
- Implemented Error Dungeon CRUD endpoints and `ErrorDungeon.jsx` component displaying mistakes as HP-based monsters.
- Implemented Vocabulary Boss checkpoint status, challenge, and submit endpoints and `VocabularyBoss.jsx` component with dynamic multiple choice exams.
- Tied vocabulary boss completions and defeated error counts to badge unlocks (`Memory Streak Badge I`, `Lexical Awakener`, `Writing Lexical Buff`, and `Error Killer`).
- Upgraded the Flashcard Gate component to render structured metadata (word types, US pronunciation IPA, and examples with translations).
- Verified backend compilation and frontend Vite build compile successfully.

## 2026-06-07 - Phase 3 Slice 4: Echo Chamber Complete

- Added Pydantic schemas for Echo Chamber questions and responses.
- Implemented `get_echo_chamber_practice` in services to extract stress syllable indices and common silent letter patterns.
- Exposed echo-chamber endpoint in main.py.
- Created `EchoChamber.jsx` component integrating browser-native speech synthesis, click-to-stress syllable buttons, and click-to-hunt silent character blocks.
- Integrated Echo Chamber as a new tab in VocabularyOverlay.jsx.
- Appended styling rules in styles.css.
- Verified compilation and Vite production build.

## 2026-06-07 - Phase 3 Slice 3: Word Family Evolution Complete

- Added Pydantic schemas for Word Family nodes, edges, groups, and responses.
- Implemented `get_word_families_practice` to group related items into React Flow node/edge objects, with discovery sync and default fallback word families.
- Exposed word-family endpoint in main.py.
- Created `WordFamilyEvolution.jsx` component with React Flow diagram drawing, details sidebar, and interactive sentence gap quizzes.
- Integrated Word Family as a new tab in VocabularyOverlay.jsx.
- Appended styling rules in styles.css.
- Verified compilation and Vite production build.

## 2026-06-07 - Phase 3 Slice 2: Shadow Duel Complete

- Added Pydantic schemas for Shadow Duel questions/responses and recording practice success.
- Implemented `get_shadow_duel_practice` in services to fetch relations (synonyms, antonyms, registers) with a robust in-code IELTS fallback dataset.
- Implemented `record_practice_success` to increment word `mastery_score` and automatically advance `mastery_rank`.
- Updated `compute_vocabulary_xp` to award XP based on vocabulary item mastery scores.
- Exposed shadow-duel and record-success endpoints in main.py.
- Created `ShadowDuel.jsx` frontend component with live countdown timers, HP, streaks, and success logging.
- Integrated Shadow Duel as a new tab in VocabularyOverlay.jsx.
- Verified compilation and Vite production build.

## 2026-06-07 - Phase 2 Word Network Tree Visual Map Complete

- Added Pydantic schemas for visual topics, nodes, and edges, and connected them to backend router paths.
- Registered tree models in reset_database dependency order to prevent foreign key errors during database wipe.
- Built services for tree fetch, node and edge CRUD, and automated node status mapping based on Codex details.
- Installed reactflow in frontend Docker container, updated package.json dependency.
- Integrated Word Network Tree tab button and rendering layout in VocabularyOverlay.jsx.
- Created WordNetworkTree.jsx React component providing React Flow visual grid, node inspector details drawer, and Codex unmapped word linker.
- Validated compile and build, smoke tested API routes and auto-sync status logic.

## 2026-06-06 - Phase 1 Vocabulary Support Skill (Lexical Awakening System) MVP Complete

- Completed all Phase 1 CRUD endpoints in main.py, adding automatic default card generation on word creation.
- Avoided circular imports by cleanly referencing services.py functions and schema objects.
- Integrated Vocabulary items into `/api/dev/reset` to prevent database delete foreign key constraints.
- Built a gorgeous React-based Overlay containing both search-enabled Codex Word Archive list and Flip Spaced Repetition Card reviewing.
- Added a new support panel button for "Vocabulary Today" on the home dashboard to show live, reactive word counts and due reviews.
- Verified everything compiles and builds with Vite, and passed a strict container integration script.

## 2026-06-06 - Phase 1 Vocabulary Support Skill Pydantic Schemas & Services

- Added Pydantic input and output schemas for examples, collocations, relations, items, flashcards, and spaced repetition states.
- Implemented corresponding DB service functions in services.py, including due card calculations and review handling with simple interval mappings (again -> 0d, hard -> 1d, good -> 3d, easy -> 7d).
- Wrote and executed a direct python test script in the running backend container to verify the correctness of the new service layer logic.

## 2026-06-06 - Phase 1 Vocabulary Support Skill Backend Schema

- Added six tables to models.py: vocabulary_items, vocabulary_examples, vocabulary_collocations, vocabulary_relations, flashcards, spaced_repetition_state.
- Mapped spec's user_id to player_id (ForeignKey to players.id) for lifelong asset persistence.
- Generated and executed Alembic migration 20260606_09_vocabulary_mvp_schema.py.
- Successfully verified DB queries and live API health.

## 2026-06-06 - Refine Suggestion Inbox grouping logic

- Fixed "eager suppression" bug by checking `sourceType`.
- Only `quest_pattern` (overdue quests) are grouped into the summary line.
- All other types (rank, last_practiced, error_pattern) remain as detailed articles.

## 2026-06-06 - Simplify Suggestion Inbox to summary only

- Removed the detailed suggestion list and Apply/Dismiss buttons.
- Replaced with a single summary message "You have x Overdue Daily Quest".
- Simplified headers in Dropdown and Panel.

## 2026-06-06 - Update Suggestion Inbox label text

- Changed label text to "You have x Overdue Daily Quest" in both Suggestion Inbox components.
- Maintained the zero-count hiding logic.

## 2026-06-06 - Hide zero backlogs in Suggestion Inbox

- Wrapped Suggestion Inbox backlog counts with conditional checks (> 0).
- Applied to both `SuggestionInboxDropdown` (header) and `SuggestionInboxPanel` (tag).

## 2026-06-06 - Repo-first glossary addition

- Added a short glossary to the repo-first prompt guides.
- The glossary now distinguishes platform rules from project workflow standards.

## 2026-06-06 - Repo-first minimum validation matrix

- Expanded the repo-first prompt guides with a minimum validation matrix by task type.
- Added validation baselines for:
  - backend
  - migration/database
  - frontend
  - debugging
  - review-only
  - documentation-only
  - session-close-only

## 2026-06-06 - Repo-first context loading expansion

- Expanded the repo-first prompt guides with task-specific context-loading rules.
- Added separate guidance for:
  - backend
  - migration/database
  - frontend
  - documentation
  - review
  - debugging
- Added stop rules so future sessions do not over-load context.

## 2026-06-06 - Generic prompt playbook split

- Added a generic layer on top of the existing repo-first prompt guides.
- New files:
  - `docs/current/prompt-generic-en.md`
  - `docs/current/prompt-generic-vi.md`
- Repo-first files remain the local source for this project:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- Updated docs maps so future sessions can choose correctly between generic and repo-specific guidance.

## 2026-06-06 - Bilingual Codex prompt playbooks

- Added repo-first Codex operator guides in:
  - `docs/current/prompt-en.md`
  - `docs/current/prompt-vi.md`
- The English file is the canonical version for repo docs.
- The Vietnamese file mirrors the workflow for direct operator use.
- Updated root/canonical doc references so future sessions can discover the guides from `README.md`, `AGENTS.md`, and `docs/current/CONTEXT_INDEX.md`.

## 2026-06-06 - Repository-wide stale-link scan

- Confirmed the environment can now run a repo-wide stale-link scan.
- Ran an automated markdown-link existence check across repo-managed docs.
- Excluded `node_modules` and `.git`.
- Result:
  - markdown files scanned: `18`
  - local markdown links checked: `69`
  - broken links: `0`

## 2026-06-06 - Documentation and context reorganization

- Reorganized documentation for low-noise context loading.
- Reduced root documentation to four entrypoints:
  - `README.md`
  - `AGENTS.md`
  - `TASKS.md`
  - `DECISIONS.md`
- Created `docs/current/` for canonical project context.
- Created `docs/history/` for implementation history and validation logs.
- Rewrote root entrypoints in English.
- Added:
  - `CONTEXT_INDEX.md`
  - `SCHEMA_SEMANTICS.md`
  - ADR for documentation layout and context loading
- Normalized current documentation to English.
- Reordered changelog to newest-first.

## 2026-06-06 - Wave E constraint hardening

- Completed backend/database hardening after the Wave D cutover.
- Enforced `NOT NULL` campaign scope on the target tables.
- Replaced the old global check-in uniqueness with campaign-scoped uniqueness.
- Added daily-slot uniqueness protection for campaign-scoped daily quests.
- Validation passed on local migration and HTTP smoke.
- Remaining gap:
  - automated backend tests still missing

## 2026-06-05 - Wave D application cutover

- Switched live skill reads/writes to `campaign_skill_states`.
- Switched live badge reads to `badge_unlocks`.
- Scoped suggestions and check-ins to the active campaign.
- Added typed quest completion dual-write behavior.

## 2026-06-05 - Wave C data backfill

- Backfilled campaign scope and typed-link fields.
- Seeded campaign-scoped skill state.
- Seeded badge unlock rows when qualifying source rows existed.

## 2026-06-05 - Wave B additive state tables

- Added `campaign_skill_states`.
- Added `badge_unlocks`.
- Updated backend seed-fed English text.
- Fixed reset order for the new child tables.

## 2026-06-05 - Wave A nullable scope and typed-link columns

- Added campaign-scope columns and typed tracker/source link columns.
- Updated backend write paths to begin filling the new fields.
