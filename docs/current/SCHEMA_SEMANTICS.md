# Schema Semantics

This file explains the business meaning of important state-like fields.

## Rank

Used by skills.

Allowed ladder:

- `F`
- `E`
- `D`
- `C`
- `B`
- `A`
- `S`

Meaning:

- lower ranks represent earlier progression
- higher ranks represent stronger demonstrated progress
- `confirmed_rank` is the accepted current rank after review/suggestion flow

## Quest Role

Used mainly by daily quest templates and instances.

Known values:

- `core`
  - the main high-value daily work
- `support`
  - reinforcement work that supports a main skill
- `mini`
  - short or lightweight maintenance work

## Daily Slot Code

Used only for daily-quest uniqueness protection.

Rules:

- for daily quest rows with `quest_role in ('core','support','mini')`, `daily_slot_code` must match the role
- non-daily quests can keep `daily_slot_code = null`

## Quest Status

Status values vary by surface, but conceptually represent where the user is in the loop:

- available / active
- completed but reward not yet claimed
- claimed
- failed / expired
- archived

Exact rendering is UI-dependent, but the backend uses this family of meanings.

## Completed vs Reward Claimed

- `completed = true` means the quest action was performed
- `reward_claimed = true` means the XP/reward was actually banked

These are intentionally separate.

## Scope

This project now uses two scope types:

- campaign-scoped
  - live progression surfaces
  - check-ins
  - suggestions
  - skill state
  - badge ownership
- player-wide
  - long-term test history

## Suggestion Source Fields

Legacy source fields:

- `source_type`
- `source_ref_id`

Preferred typed source fields:

- `source_test_record_id`
- `source_mock_test_id`
- `source_error_log_id`
- `source_quest_id`

The typed fields are preferred for new writes, but the legacy fields remain for compatibility.
