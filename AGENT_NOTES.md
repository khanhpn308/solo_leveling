# Agent Notes

## 2026-06-05 - Wave A backend implementation started

- Started coding `Wave A` for campaign-scope and typed-link hardening.
- Installed backend Python requirements into the active Windows Python environment so Alembic and SQLAlchemy are usable from the host shell.
- Added a new Alembic revision: `20260605_05_wave_a_scope_links.py`.
- Implemented additive nullable columns for:
  - `checkins.campaign_id`
  - `test_records.campaign_id`
  - `skill_rank_suggestions.campaign_id`
  - `skill_rank_history.campaign_id`
  - `weakness_suggestions.campaign_id`
  - `quests.daily_slot_code`
  - typed tracker/source FK columns on `quests` and `weakness_suggestions`
- Updated backend ORM and response schemas to expose the new nullable fields without removing legacy fields.
- Updated backend write paths to start filling `campaign_id` for new check-ins, test records, rank suggestions, rank history, and weakness suggestions.
- Fixed `/api/dev/reset` deletion order so the new foreign keys do not break local reset/seed flow.
- Validation so far:
  - `python -m py_compile backend/app/main.py backend/app/models.py backend/app/schemas.py backend/app/services.py backend/alembic/versions/20260605_05_wave_a_scope_links.py`: passed
- `python -c "... command.upgrade(..., 'head')"` with URL override `localhost:3307`: passed
- Read-only SQLAlchemy verification confirmed:
  - `alembic_version = 20260605_05`
  - `checkins.campaign_id` exists
  - `quests.daily_slot_code` exists
  - `weakness_suggestions.source_test_record_id` exists
- Validation still pending:
  - API/runtime smoke checks after migration

## 2026-06-05 - Wave B additive state tables and backend English text sync

- Started coding `Wave B` for additive campaign skill state and badge unlock tables.
- Added Alembic revision `20260605_06_wave_b_state_tables.py`.
- Added new SQLAlchemy models:
  - `CampaignSkillState`
  - `BadgeUnlock`
- Added model relationships for:
  - `Player.badge_unlocks`
  - `Campaign.skill_states`
  - `Campaign.badge_unlocks`
  - `Skill.campaign_states`
  - `Badge.unlocks`
  - `BossBattle.badge_unlocks`
- Updated `/api/dev/reset` delete order to include the new Wave B child tables before parent rows.
- Translated seeded backend user-facing text in `backend/app/seed.py` from Vietnamese to English for:
  - skill defaults
  - badge descriptions
  - roadmap phase labels/objectives
  - study-material notes
  - quest template descriptions and notes
  - weekly mission descriptions/items
- Kept `services.py` weekly-mission description matching backward-compatible for old Vietnamese rows already in the DB.
- Added seed synchronization behavior so repeated startup seeding updates existing system-seeded rows instead of only creating missing ones.
- Validation so far:
  - `python -m py_compile backend/app/main.py backend/app/models.py backend/app/services.py backend/app/seed.py backend/alembic/versions/20260605_06_wave_b_state_tables.py`: passed
  - host-side Alembic upgrade to `20260605_06`: passed
  - read-only MySQL verification confirmed:
    - `campaign_skill_states` exists
    - `badge_unlocks` exists
    - both new tables are empty immediately after migration
    - named indexes/unique constraints exist
- Remaining gap:
  - `material.md` still contains Vietnamese study-plan source text and has not been translated in this slice
  - live API smoke checks after backend restart/reset remain pending

## 2026-06-05 - Wave B material translation and reset smoke

- Translated `material.md` to English so backend seed-fed roadmap/session source text is no longer Vietnamese.
- Fixed a real `/api/dev/reset` failure caused by the `players.active_campaign_id -> campaigns.id` foreign key.
- Reset fix approach:
  - null out `Player.active_campaign_id`
  - flush
  - then run the existing destructive delete loop
- Restarted the backend container to force startup seed sync against the updated source files.
- Ran live smoke checks after reset for:
  - `/api/health`
  - `/api/dev/reset`
  - `/api/skills`
  - `/api/badges`
  - `/api/materials`
  - `/api/roadmap/phases`
  - `/api/weekly-mission/current`
- Validation outcome:
  - reset now returns HTTP 200
  - skill/badge payload shapes stayed unchanged
  - seed-backed materials, roadmap phases, and weekly mission text now return English content
- Remaining caveat:
  - some `material.md` English phrasing is machine-translated and serviceable, but not fully polished editorial English

## 2026-06-04 - Documentation sync for completed home dashboard redesign

- Updated project docs to reflect the frontend-only home dashboard redesign truthfully.
- Confirmed the completed redesign includes:
  - compact home shell
  - top bar with level/rank, avatar modal trigger, suggestion inbox dropdown, and host time
  - roadmap phase hero with overall roadmap start/end
  - bottom stat cards
  - burger navigation with Quest submenu, Certificate, and Boss
  - quest overlay tabs Main / Daily / Weekly / Archive
  - certificate overlay wired to existing test-records API
  - boss overlay with current boss first
  - avatar picker placeholder only
  - real suggestion inbox actions via existing backend suggestion endpoints
- Recorded validation truth:
  - `npm.cmd run build`: passed
  - `npm.cmd run test:dashboard-data`: passed
  - `5 tests, 0 failures`
- Final reviewer rerun: `ACCEPT`
- Browser screenshot / visual walkthrough remains unavailable and is still the only notable verification gap.

## 2026-06-06 - Wave E constraint hardening

- Completed Wave E backend/database hardening after the Wave D cutover.
- Hardened write paths before DDL:
  - `/api/checkins` now upserts strictly by `(campaign_id, checkin_date)`
  - removed the pre-Wave-E global same-date fallback
  - seed-generated daily quests now always write `daily_slot_code`
  - seeded `TestRecord` rows now always write `campaign_id`
- Added Alembic revision `20260606_08_wave_e_constraint_hardening.py`.
- Wave E migration now:
  - syncs missing `daily_slot_code` narrowly
  - fails fast if any target `campaign_id` remains null
  - fails fast if duplicate future unique keys exist
  - changes target `campaign_id` columns to `NOT NULL`
  - replaces `uq_checkin_date` with `uq_checkins_campaign_date`
  - adds `uq_quests_campaign_date_daily_slot`
  - includes a real schema downgrade
- Validation completed:
  - `python -m py_compile`: passed
  - pre-migration reset logic via current backend code: passed
  - Alembic upgrade to `20260606_08`: passed
  - post-migration SQL audits: all target null/duplicate counts are `0`
  - live HTTP smoke on `127.0.0.1:8010`: passed for
    - `/api/health`
    - `/api/checkins` GET/POST create/POST update
    - `/api/summary`
    - `/api/weekly-mission/current`
    - `/api/quests/today`
    - `/api/dev/reset`
- Remaining gap:
  - automated backend tests for Wave D/Wave E behavior still do not exist
