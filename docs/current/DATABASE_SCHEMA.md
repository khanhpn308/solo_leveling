# Database Schema Snapshot

This is the current high-level schema shape after migration Wave `E`.

## Main Entities

Core owner and campaign tables:

- `players`
- `campaigns`

Progression and quest tables:

- `skills`
- `campaign_skill_states`
- `quests`
- `weekly_missions`
- `boss_battles`
- `badges`
- `badge_unlocks`

Tracking and evidence tables:

- `checkins`
- `error_logs`
- `writing_entries`
- `speaking_entries`
- `mock_tests`
- `test_records`
- `skill_rank_suggestions`
- `skill_rank_history`
- `weakness_suggestions`

Roadmap and content tables:

- `roadmap_phases`
- `study_materials`
- `main_quest_plans`

## Important Current Invariants

- `checkins.campaign_id` is `NOT NULL`
- `test_records.campaign_id` is `NOT NULL`
- `skill_rank_suggestions.campaign_id` is `NOT NULL`
- `skill_rank_history.campaign_id` is `NOT NULL`
- `weakness_suggestions.campaign_id` is `NOT NULL`
- `quests.campaign_id` is `NOT NULL`

## Current Source-Of-Truth Split

Definition-style tables:

- `skills`
- `badges`

Campaign-scoped mutable state:

- `campaign_skill_states`
- `badge_unlocks`

## Link Strategy

Legacy compatibility fields still exist:

- `quests.tracker_type`
- `quests.tracker_entry_id`
- `weakness_suggestions.source_type`
- `weakness_suggestions.source_ref_id`

Typed nullable link fields also exist and are the preferred current path:

- `quests.error_log_id`
- `quests.writing_entry_id`
- `quests.speaking_entry_id`
- `quests.mock_test_id`
- `weakness_suggestions.source_test_record_id`
- `weakness_suggestions.source_mock_test_id`
- `weakness_suggestions.source_error_log_id`
- `weakness_suggestions.source_quest_id`

## Constraint Snapshot

- `checkins` unique key: `(campaign_id, checkin_date)`
- daily quest protection key on `quests`: `(campaign_id, quest_date, daily_slot_code)`
- `campaign_skill_states` unique key: `(campaign_id, skill_id)`
- `badge_unlocks` unique key: `(campaign_id, badge_id)`

## Read Alongside

For field meaning, read [SCHEMA_SEMANTICS.md](SCHEMA_SEMANTICS.md).
For migration history, read [../history/MIGRATION_HISTORY.md](../history/MIGRATION_HISTORY.md).
