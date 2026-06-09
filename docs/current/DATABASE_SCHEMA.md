# Database Schema Snapshot

This is the current high-level schema shape after designing the Account System, Onboarding, and Rank Boss updates.

## Main Entities

### Account-scoped (Auth & Identity)
- `accounts`: User authentication and security status
- `account_sessions`: Session refresh token hashes
- `account_tokens`: OTP and email/verification token hashes
- `account_security_events`: Audit log of security and auth actions
- `account_preferences`: System preferences (locale, theme, timezone)

### Player-wide (Cross-campaign profile & history)
- `players`: Learners/game profile linked to accounts
- `player_learning_profiles`: Long-term learning styles and configurations
- `test_records`: Long-term IELTS test history

### Campaign-scoped (Learning progress & state instances)
- `campaigns`: Active study campaigns
- `campaign_settings`: Individual campaign setup configurations
- `campaign_skill_states`: Current campaign-scoped skill levels
- `quests`: Quest instances (main, daily, weekly)
- `weekly_missions`: Weekly target goals
- `boss_battles`: Boss battle completion records
- `badges`: Badges defined in system
- `badge_unlocks`: Unlocked badge records for active campaign
- `checkins`: Daily checkin trackers
- `error_logs`: Review log for mistakes
- `writing_entries`: Submitted writing task responses
- `speaking_entries`: Submitted speaking task responses
- `mock_tests`: Complete mock tests
- `certificate_records`: Manually input IELTS scores
- `skill_rank_suggestions`: Suggestions for skill rank promotions, optionally linked to certificate records
- `skill_rank_history`: Historical log of all skill rank transitions
- `rank_exam_attempts`: Completed/active Rank Boss exam attempts
- `rank_exam_answers`: Selected answers for exam questions

### Template & Definition-scoped (Roadmap rules & content)
- `campaign_templates`: Predefined roadmap configurations
- `campaign_template_skill_quotas`: Predefined quest quotas per template
- `campaign_skill_quest_quotas`: Copy of quest quotas for active campaign
- `vocabulary_settings`: Study preferences for vocabulary learning
- `skills`: Supported skills (Vocabulary, Reading, etc.)
- `rank_exam_pools`: Skill rank transition exam definitions
- `rank_exam_pools.xp_threshold`: XP required for a rank transition (seeded values)
- `rank_exam_versions`: Versions of Rank Boss exams
- `rank_exam_questions`: Specific questions for exam versions
- `roadmap_phases`: Roadmap milestones
- `study_materials`: Reference learning materials
- `main_quest_plans`: Roadmap sequence plans

## Important Current Invariants

- `checkins.campaign_id` is `NOT NULL`
- `test_records.campaign_id` is `NOT NULL`
- `skill_rank_suggestions.campaign_id` is `NOT NULL`
- `skill_rank_history.campaign_id` is `NOT NULL`
- `weakness_suggestions.campaign_id` is `NOT NULL`
- `quests.campaign_id` is `NOT NULL`
- `players.account_id` is nullable (one-to-one mapping to `accounts.id`, unique)
- `campaign_settings.campaign_id` is `NOT NULL` (unique)
- `campaign_skill_quest_quotas.campaign_id` is `NOT NULL` (unique key with `skill_id`)
- `rank_exam_attempts.campaign_id` and `rank_exam_attempts.skill_id` are `NOT NULL`
- `rank_exam_pools.xp_threshold` must match the minimum XP required for the target rank (E: 500, D: 1200, C: 2500, B: 4500, A: 7000, S: 10000)

## Current Source-Of-Truth Split

Definition-style tables:

- `skills`
- `badges`
- `campaign_templates`
- `rank_exam_pools`

Campaign-scoped mutable state:

- `campaign_skill_states`
- `badge_unlocks`
- `campaign_skill_quest_quotas`
- `vocabulary_settings`

## Link Strategy

Legacy compatibility fields (`tracker_type`, `tracker_entry_id` for quests and `source_type`, `source_ref_id` for weakness suggestions) have been removed from the database as physical columns. They are now exposed as virtual Python `@property` getters computed dynamically from the typed link fields.

Typed nullable link fields are the physical columns used in the database:

- `quests.error_log_id`
- `quests.writing_entry_id`
- `quests.speaking_entry_id`
- `quests.mock_test_id`
- `weakness_suggestions.source_test_record_id`
- `weakness_suggestions.source_certificate_record_id`
- `weakness_suggestions.source_mock_test_id`
- `weakness_suggestions.source_error_log_id`
- `weakness_suggestions.source_quest_id`
- `skill_rank_suggestions.source_certificate_record_id` *(links certificate records to promotion suggestions)*
- `skill_rank_history.source_certificate_record_id` *(links certificate records to rank history audit trail)*

## Constraint Snapshot

- `accounts` unique key: `uq_accounts_email_normalized` on `email_normalized`
- `account_sessions` unique key: `uq_account_sessions_refresh_token_hash` on `refresh_token_hash`
- `account_tokens` unique key: `uq_account_tokens_token_hash` on `token_hash`
- `account_preferences` unique key: `uq_account_preferences_account_id` on `account_id`
- `players` unique key: `uq_players_account_id` on `account_id`
- `player_learning_profiles` unique key: `uq_player_learning_profiles_player_id` on `player_id`
- `campaign_templates` unique key: `uq_campaign_templates_code` on `code`
- `campaign_settings` unique key: `uq_campaign_settings_campaign_id` on `campaign_id`
- `campaign_template_skill_quotas` unique key: `uq_template_skill_quota` on `(campaign_template_id, skill_id)`
- `campaign_skill_quest_quotas` unique key: `uq_campaign_skill_quest_quota` on `(campaign_id, skill_id)`
- `vocabulary_settings` unique key: `uq_vocabulary_settings_campaign_id` on `campaign_id`
- `checkins` unique key: `(campaign_id, checkin_date)`
- daily quest protection key on `quests`: `(campaign_id, quest_date, daily_slot_code)`
- `campaign_skill_states` unique key: `(campaign_id, skill_id)`
- `badge_unlocks` unique key: `(campaign_id, badge_id)`
- `rank_exam_answers` unique key: `uq_rank_exam_answer_attempt_question` on `(attempt_id, question_id)`
- check constraint on `quests` (`ck_quests_only_one_tracker`): enforces that at most one of the typed tracker foreign keys is populated.
- check constraint on `weakness_suggestions` (`ck_weakness_suggestions_only_one_source`): enforces that at most one of the typed source foreign keys is populated.

## Read Alongside

For field meaning, read [SCHEMA_SEMANTICS.md](SCHEMA_SEMANTICS.md).
For migration history, read [../history/MIGRATION_HISTORY.md](../history/MIGRATION_HISTORY.md).
