# Database Schema Snapshot

Updated: 2026-06-05  
Database: `ielts_quest`  
Source of truth for this document:
- Live MySQL `information_schema` queried from the running `ielts_quest_mysql` container
- Cross-check with `backend/app/models.py`

This snapshot reflects the current local database schema at the time of inspection.  
Note: the `COLUMN_DEFAULT` values shown by MySQL only cover database-level defaults. Many ORM defaults in `models.py` are application-side defaults and do not appear as SQL defaults in `information_schema`.

## Summary

- Total tables: `24`
- Migration table: `alembic_version`
- Main gameplay tables: `players`, `campaigns`, `skills`, `quests`, `weekly_missions`, `boss_battles`
- Planning tables: `roadmap_phases`, `study_materials`, `phase_materials`, `study_plan_weeks`, `study_plan_sessions`, `quest_templates`
- Tracking tables: `checkins`, `error_logs`, `writing_entries`, `speaking_entries`, `mock_tests`, `test_records`
- Recommendation / progression tables: `skill_rank_suggestions`, `skill_rank_history`, `weakness_suggestions`, `badges`

## Core Relationships

- `players.active_campaign_id -> campaigns.id`
- `campaigns.player_id -> players.id`
- `roadmap_phases.campaign_id -> campaigns.id`
- `study_plan_weeks.campaign_id -> campaigns.id`
- `study_plan_weeks.phase_id -> roadmap_phases.id`
- `study_plan_sessions.study_plan_week_id -> study_plan_weeks.id`
- `study_plan_sessions.phase_id -> roadmap_phases.id`
- `quest_templates.primary_skill_id -> skills.id`
- `quest_templates.phase_id -> roadmap_phases.id`
- `quest_templates.material_id -> study_materials.id`
- `quests.skill_id -> skills.id`
- `quests.campaign_id -> campaigns.id`
- `quests.phase_id -> roadmap_phases.id`
- `quests.study_plan_week_id -> study_plan_weeks.id`
- `quests.study_plan_session_id -> study_plan_sessions.id`
- `quests.template_id -> quest_templates.id`
- `quests.material_id -> study_materials.id`
- `weekly_missions.campaign_id -> campaigns.id`
- `weekly_mission_items.weekly_mission_id -> weekly_missions.id`
- `boss_battles.campaign_id -> campaigns.id`
- `boss_battles.badge_id -> badges.id`
- `error_logs.campaign_id -> campaigns.id`
- `error_logs.skill_id -> skills.id`
- `writing_entries.campaign_id -> campaigns.id`
- `speaking_entries.campaign_id -> campaigns.id`
- `mock_tests.campaign_id -> campaigns.id`
- `test_records.player_id -> players.id`
- `skill_rank_suggestions.skill_id -> skills.id`
- `skill_rank_suggestions.source_test_record_id -> test_records.id`
- `skill_rank_history.skill_id -> skills.id`
- `skill_rank_history.source_test_record_id -> test_records.id`
- `weakness_suggestions.skill_id -> skills.id`

## Table Definitions

### `alembic_version`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `version_num` | `varchar(32)` | NO | PK | Current Alembic revision |

### `badges`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `name` | `varchar(120)` | NO | UNIQUE | Badge name |
| `icon` | `varchar(32)` | NO |  | Icon code |
| `description` | `varchar(255)` | NO |  | Badge description |
| `unlocked` | `tinyint(1)` | NO |  | Unlock flag |
| `unlocked_at` | `datetime` | YES |  | Unlock timestamp |

### `boss_battles`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `stage` | `varchar(80)` | NO | IDX | Boss stage / tier |
| `battle_date` | `date` | NO | IDX | Scheduled date |
| `title` | `varchar(160)` | NO |  | Battle title |
| `source` | `varchar(255)` | NO |  | Resource source |
| `goal` | `varchar(255)` | NO |  | Target objective |
| `status` | `varchar(50)` | NO |  | UI / availability status |
| `campaign_id` | `int` | YES | FK | -> `campaigns.id` |
| `month_index` | `int` | NO | IDX | Roadmap month bucket |
| `reward_xp` | `int` | NO |  | Reward XP |
| `badge_id` | `int` | YES | FK | -> `badges.id` |
| `result_status` | `varchar(20)` | NO | IDX | Clear result state |
| `result_note` | `varchar(255)` | NO |  | Result note |
| `practice_suggestion` | `varchar(255)` | NO |  | Follow-up suggestion |
| `cleared_at` | `datetime` | YES |  | Clear timestamp |

### `campaigns`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `player_id` | `int` | NO | FK | -> `players.id` |
| `start_date` | `date` | NO | IDX | Campaign start |
| `end_date` | `date` | NO | IDX | Campaign end |
| `status` | `varchar(20)` | NO | IDX | Campaign state |
| `created_at` | `datetime` | NO | IDX | Created timestamp |
| `completed_at` | `datetime` | YES |  | Completion timestamp |

### `checkins`

Unique constraints:
- `uq_checkin_date` on `checkin_date`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `checkin_date` | `date` | NO | UNIQUE | One check-in per day |
| `mood` | `int` | NO |  | Mood score |
| `energy` | `int` | NO |  | Energy score |
| `focus` | `int` | NO |  | Focus score |
| `note` | `text` | NO |  | Freeform note |

### `error_logs`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `skill_id` | `int` | NO | FK | -> `skills.id` |
| `source` | `varchar(255)` | NO |  | Source material |
| `error_description` | `text` | NO |  | Mistake detail |
| `correction` | `text` | NO |  | Correct form |
| `cause` | `text` | NO |  | Root cause |
| `prevention` | `text` | NO |  | Prevention note |
| `error_tag` | `varchar(80)` | NO | IDX | Category tag |
| `logged_date` | `date` | NO | IDX | Log date |

### `mock_tests`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `test_type` | `varchar(80)` | NO | IDX | Listening / Reading / Full... |
| `scope` | `varchar(20)` | NO | IDX | Usually `full` or partial |
| `source` | `varchar(255)` | NO |  | Test source |
| `raw_score` | `varchar(50)` | NO |  | Raw mark |
| `estimated_band` | `varchar(20)` | NO |  | Derived band |
| `estimated_band_override` | `varchar(20)` | NO |  | Manual override |
| `note` | `text` | NO |  | Notes |
| `test_date` | `date` | NO | IDX | Test date |

### `phase_materials`

Unique constraints:
- `uq_phase_material` on (`phase_id`, `material_id`)

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `phase_id` | `int` | NO | FK | -> `roadmap_phases.id` |
| `material_id` | `int` | NO | FK | -> `study_materials.id` |
| `usage_purpose` | `varchar(120)` | NO |  | Why this material is used |
| `usage_frequency` | `varchar(80)` | NO |  | Usage cadence |
| `notes` | `text` | NO |  | Mapping notes |
| `display_order` | `int` | NO |  | Sort order |

### `players`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `name` | `varchar(120)` | NO |  | Legacy player name |
| `title` | `varchar(120)` | NO |  | Player title |
| `target` | `varchar(120)` | NO |  | Legacy target text |
| `current_level` | `varchar(50)` | NO |  | Legacy current level |
| `start_date` | `date` | NO |  | Journey start date |
| `total_xp` | `int` | NO |  | Legacy XP total |
| `display_name` | `varchar(120)` | NO |  | Current UI display name |
| `target_overall_band` | `varchar(20)` | NO |  | IELTS target band |
| `current_estimated_level` | `varchar(50)` | NO |  | Current estimate |
| `strongest_skill` | `varchar(80)` | NO |  | Strongest area |
| `weakest_skill` | `varchar(80)` | NO |  | Weakest area |
| `study_days_per_week` | `int` | NO |  | Planned weekly days |
| `session_minutes` | `int` | NO |  | Session length |
| `daily_mini_study_minutes` | `int` | NO |  | Mini-study target |
| `player_xp` | `int` | NO |  | Current player XP |
| `player_level` | `int` | NO |  | Current player level |
| `player_rank` | `varchar(2)` | NO |  | Rank F-S |
| `current_streak` | `int` | NO |  | Active streak |
| `best_streak` | `int` | NO |  | Best streak |
| `shield_count` | `int` | NO |  | Streak shield count |
| `shield_regen_progress` | `int` | NO |  | Shield regen progress |
| `perfect_day_count` | `int` | NO |  | Perfect day total |
| `setup_completed` | `tinyint(1)` | NO |  | Setup completion flag |
| `active_campaign_id` | `int` | YES | FK | -> `campaigns.id` |

### `quest_templates`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `title` | `varchar(200)` | NO |  | Template title |
| `description` | `text` | NO |  | Template description |
| `primary_skill_id` | `int` | NO | FK | -> `skills.id` |
| `phase_id` | `int` | YES | FK | -> `roadmap_phases.id` |
| `material_id` | `int` | YES | FK | -> `study_materials.id` |
| `base_xp` | `int` | NO |  | Base XP reward |
| `difficulty` | `varchar(20)` | NO | IDX | Difficulty tag |
| `difficulty_description` | `varchar(255)` | NO |  | Human description |
| `quest_role` | `varchar(20)` | NO | IDX | `main`, `core`, `mini`, ... |
| `resource_name` | `varchar(255)` | NO |  | Resource name |
| `resource_category` | `varchar(80)` | NO |  | Resource category |
| `resource_note` | `varchar(255)` | NO |  | Resource note |
| `allowed_phase_start` | `int` | NO |  | Earliest phase |
| `allowed_phase_end` | `int` | NO |  | Latest phase |
| `is_active` | `tinyint(1)` | NO | IDX | Active flag |

### `quests`

This is the main quest instance table used by the app.

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `quest_date` | `date` | NO | IDX | Planned date |
| `week_no` | `int` | NO | IDX | Roadmap week |
| `stage` | `varchar(80)` | NO | IDX | Main stage / section |
| `title` | `varchar(200)` | NO |  | Quest title |
| `skill_id` | `int` | NO | FK | -> `skills.id` |
| `source` | `varchar(255)` | NO |  | Material source |
| `details` | `text` | NO |  | Quest detail |
| `xp` | `int` | NO |  | Legacy XP field |
| `completed` | `tinyint(1)` | NO | IDX | Completion flag |
| `completed_at` | `datetime` | YES |  | Completion timestamp |
| `session_type` | `varchar(80)` | NO |  | Daily / Main / Weekly-related |
| `campaign_id` | `int` | YES | FK | -> `campaigns.id` |
| `phase_id` | `int` | YES | FK | -> `roadmap_phases.id` |
| `study_plan_week_id` | `int` | YES | FK | -> `study_plan_weeks.id` |
| `study_plan_session_id` | `int` | YES | FK | -> `study_plan_sessions.id` |
| `template_id` | `int` | YES | FK | -> `quest_templates.id` |
| `material_id` | `int` | YES | FK | -> `study_materials.id` |
| `status` | `varchar(20)` | NO | IDX | Pending / overdue / completed / expired |
| `quest_role` | `varchar(20)` | NO | IDX | Main / core / mini |
| `difficulty` | `varchar(20)` | NO | IDX | Easy / medium / hard |
| `base_xp` | `int` | NO |  | Base XP |
| `earned_xp` | `int` | NO |  | Effective XP after completion logic |
| `completed_mode` | `varchar(20)` | YES |  | Completion mode |
| `completion_note` | `varchar(255)` | NO |  | Completion note |
| `raw_score` | `varchar(120)` | NO |  | Optional raw score |
| `tracker_type` | `varchar(40)` | NO |  | Related tracker type |
| `tracker_entry_id` | `int` | YES |  | Related tracker row id |
| `expired_at` | `datetime` | YES |  | Expiry timestamp |
| `reward_claimed` | `tinyint(1)` | NO | IDX | Reward claim state |
| `reward_claimed_at` | `datetime` | YES |  | Reward claim timestamp |

### `roadmap_phases`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `phase_order` | `int` | NO | IDX | 1..n ordering |
| `code` | `varchar(40)` | NO | IDX | Phase code |
| `title` | `varchar(120)` | NO |  | Phase title |
| `month_start` | `int` | NO |  | Start month |
| `month_end` | `int` | NO |  | End month |
| `week_start` | `int` | NO | IDX | Start week |
| `week_end` | `int` | NO | IDX | End week |
| `start_date` | `date` | NO | IDX | Phase start date |
| `end_date` | `date` | NO | IDX | Phase end date |
| `objective` | `text` | NO |  | Phase objective |
| `focus_skills` | `varchar(255)` | NO |  | Focus skills summary |
| `is_active` | `tinyint(1)` | NO | IDX | Active flag |
| `created_at` | `datetime` | NO | IDX | Created timestamp |

### `skill_rank_history`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `skill_id` | `int` | NO | FK | -> `skills.id` |
| `old_rank` | `varchar(2)` | NO |  | Previous rank |
| `new_rank` | `varchar(2)` | NO |  | New rank |
| `source_test_record_id` | `int` | YES | FK | -> `test_records.id` |
| `change_reason` | `varchar(255)` | NO |  | Reason for rank change |
| `changed_at` | `datetime` | NO | IDX | Change timestamp |

### `skill_rank_suggestions`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `skill_id` | `int` | NO | FK | -> `skills.id` |
| `source_test_record_id` | `int` | YES | FK | -> `test_records.id` |
| `current_rank` | `varchar(2)` | NO |  | Current rank |
| `suggested_rank` | `varchar(2)` | NO |  | Suggested rank |
| `direction` | `varchar(10)` | NO |  | Up / down / same |
| `status` | `varchar(20)` | NO | IDX | Pending / applied / dismissed |
| `created_at` | `datetime` | NO | IDX | Created timestamp |
| `resolved_at` | `datetime` | YES |  | Resolution timestamp |

### `skills`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `name` | `varchar(80)` | NO | UNIQUE | Skill name |
| `icon` | `varchar(32)` | NO |  | Icon code |
| `xp` | `int` | NO |  | Current skill XP |
| `rank` | `varchar(2)` | NO |  | Display rank |
| `confirmed_rank` | `varchar(2)` | NO | IDX | Confirmed rank |
| `level` | `int` | NO |  | Skill level |
| `streak` | `int` | NO |  | Skill streak |
| `last_practiced` | `date` | YES | IDX | Last practice date |
| `weak_point` | `varchar(255)` | NO |  | System weak point note |
| `user_weakness_note` | `text` | NO |  | User note |
| `last_system_suggestion_at` | `datetime` | YES | IDX | Last suggestion timestamp |

### `speaking_entries`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `part` | `varchar(40)` | NO |  | Speaking part |
| `topic` | `varchar(255)` | NO |  | Topic |
| `cue_or_question` | `text` | NO |  | Prompt |
| `self_score` | `varchar(50)` | NO |  | Self score |
| `self_note` | `text` | NO |  | Reflection note |
| `transcript_summary` | `text` | NO |  | Transcript summary |
| `entry_date` | `date` | NO | IDX | Entry date |

### `study_materials`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `title` | `varchar(255)` | NO | UNIQUE | Material title |
| `category` | `varchar(80)` | NO | IDX | Category |
| `format` | `varchar(40)` | NO |  | Book / ebook / audio... |
| `file_path` | `varchar(500)` | NO |  | Local file path |
| `skill_tags` | `varchar(255)` | NO |  | Tagged skills |
| `recommended_phase_start` | `int` | NO |  | Recommended start phase |
| `recommended_phase_end` | `int` | NO |  | Recommended end phase |
| `notes` | `text` | NO |  | Notes |
| `is_active` | `tinyint(1)` | NO | IDX | Active flag |
| `created_at` | `datetime` | NO | IDX | Created timestamp |

### `study_plan_sessions`

Unique constraints:
- `uq_study_plan_session_week_no` on (`study_plan_week_id`, `session_no`)

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `phase_id` | `int` | NO | FK | -> `roadmap_phases.id` |
| `study_plan_week_id` | `int` | NO | FK | -> `study_plan_weeks.id` |
| `week_no` | `int` | NO | IDX | Roadmap week |
| `session_no` | `int` | NO | IDX | Session number in week |
| `study_date` | `date` | NO | IDX | Planned date |
| `weekday_label` | `varchar(40)` | NO |  | Weekday text |
| `session_label` | `varchar(40)` | NO |  | Session label |
| `skill_summary` | `varchar(255)` | NO |  | Skill summary |
| `task_detail` | `text` | NO |  | Task detail |
| `material_summary` | `text` | NO |  | Material summary |
| `deliverable` | `text` | NO |  | Expected deliverable |
| `status_text` | `varchar(40)` | NO |  | Session status text |
| `note_text` | `text` | NO |  | Notes |
| `mini_task` | `text` | NO |  | Mini-task |
| `created_at` | `datetime` | NO | IDX | Created timestamp |

### `study_plan_weeks`

Unique constraints:
- `uq_study_plan_week_campaign_week` on (`campaign_id`, `week_no`)

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `phase_id` | `int` | NO | FK | -> `roadmap_phases.id` |
| `week_no` | `int` | NO | IDX | Roadmap week |
| `week_start` | `date` | NO | IDX | Week start |
| `week_end` | `date` | NO | IDX | Week end |
| `weekly_focus` | `text` | NO |  | Weekly focus |
| `weekly_output` | `text` | NO |  | Weekly output |
| `material_summary` | `text` | NO |  | Material summary |
| `mini_task` | `text` | NO |  | Mini-task |
| `created_at` | `datetime` | NO | IDX | Created timestamp |

### `test_records`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `player_id` | `int` | NO | FK | -> `players.id` |
| `test_type` | `varchar(20)` | NO | IDX | Test type |
| `test_date` | `date` | NO | IDX | Test date |
| `overall_score` | `varchar(50)` | NO |  | Overall score |
| `listening_score` | `varchar(50)` | NO |  | Listening score |
| `reading_score` | `varchar(50)` | NO |  | Reading score |
| `writing_score` | `varchar(50)` | NO |  | Writing score |
| `speaking_score` | `varchar(50)` | NO |  | Speaking score |
| `cefr_level` | `varchar(20)` | NO |  | CEFR estimate |
| `note` | `text` | NO |  | Notes |
| `created_at` | `datetime` | NO | IDX | Created timestamp |

### `weakness_suggestions`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `skill_id` | `int` | NO | FK | -> `skills.id` |
| `source_type` | `varchar(40)` | NO | IDX | Origin type |
| `source_ref_id` | `int` | YES |  | Optional source row id |
| `title` | `varchar(200)` | NO |  | Suggestion title |
| `detail` | `text` | NO |  | Suggestion detail |
| `severity` | `varchar(20)` | NO |  | Severity |
| `status` | `varchar(20)` | NO | IDX | Pending / resolved / dismissed |
| `created_at` | `datetime` | NO | IDX | Created timestamp |
| `resolved_at` | `datetime` | YES |  | Resolved timestamp |

### `weekly_mission_items`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `weekly_mission_id` | `int` | NO | FK | -> `weekly_missions.id` |
| `description` | `varchar(255)` | NO |  | Objective text |
| `target_count` | `int` | NO |  | Required count |
| `current_count` | `int` | NO |  | Current count |
| `status` | `varchar(20)` | NO | IDX | Objective state |

### `weekly_missions`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `week_start` | `date` | NO | IDX | Week start |
| `week_end` | `date` | NO | IDX | Week end |
| `phase` | `varchar(80)` | NO | IDX | Phase label |
| `pattern_code` | `varchar(80)` | NO | IDX | Mission pattern code |
| `title` | `varchar(200)` | NO |  | Mission title |
| `description` | `text` | NO |  | Mission description |
| `reward_xp` | `int` | NO |  | Reward XP |
| `status` | `varchar(20)` | NO | IDX | Mission state |
| `completed_at` | `datetime` | YES |  | Completion timestamp |
| `reward_claimed` | `tinyint(1)` | NO | IDX | Reward claim state |
| `reward_claimed_at` | `datetime` | YES |  | Reward claim timestamp |

### `writing_entries`

| Column | Type | Null | Key | Notes |
| --- | --- | --- | --- | --- |
| `id` | `int` | NO | PK | Auto increment |
| `campaign_id` | `int` | NO | FK | -> `campaigns.id` |
| `task_type` | `varchar(80)` | NO |  | Writing task type |
| `prompt` | `text` | NO |  | Prompt |
| `draft_text` | `text` | NO |  | Draft answer |
| `self_score` | `varchar(50)` | NO |  | Self score |
| `estimated_band` | `varchar(20)` | NO |  | Estimated band |
| `feedback_note` | `text` | NO |  | Feedback note |
| `revised_text` | `text` | NO |  | Revised answer |
| `entry_date` | `date` | NO | IDX | Entry date |

## Important Notes

### Reward-claim fields

The schema now includes explicit reward-claim tracking:
- `quests.reward_claimed`
- `quests.reward_claimed_at`
- `weekly_missions.reward_claimed`
- `weekly_missions.reward_claimed_at`

This supports the current frontend flow where XP is only banked after `CLAIM`.

### Legacy vs current player / XP fields

The `players` and `quests` tables still contain some legacy fields alongside the newer loop:
- `players.total_xp` and `players.player_xp`
- `players.current_level` and `players.current_estimated_level`
- `quests.xp`, `quests.base_xp`, and `quests.earned_xp`

These should be treated carefully in future refactors because not all fields represent the same layer of logic.

### Recommended next schema doc additions

- Add a second document for business meanings of each status field:
  - `quests.status`
  - `quests.quest_role`
  - `weekly_missions.status`
  - `weekly_mission_items.status`
  - `skill_rank_suggestions.status`
  - `weakness_suggestions.status`
- Add an ERD diagram for onboarding if this schema continues to grow.
