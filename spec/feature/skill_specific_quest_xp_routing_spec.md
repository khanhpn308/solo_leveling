# Skill-Specific Quest XP Routing & Vocabulary Daily Quest Specification

**Project:** IELTS Quest Dashboard  
**Audience:** Codex CLI / Backend + Frontend agents  
**Status:** Approved architecture decision  
**Scope:** Quest system, Vocabulary Daily Quests, Skill XP, Player XP, Weekly Missions, Boss reward routing

---

## 0. Executive Decision

Do **not** create a separate table such as `daily_vocabulary_quests` or `vocabulary_daily_quests`.

Keep the existing generic Quest system and extend it so that quests can be:

- skill-specific;
- activity-specific;
- reward-routed either to Skill XP or Player XP;
- tracked safely through transaction tables to prevent duplicate XP claims.

Final XP routing decision:

| Source | XP Destination |
|---|---|
| Daily Quest with clear skill | Skill XP |
| Weekly Mission with clear skill | Skill XP |
| Skill-specific Boss Battle | Skill XP |
| Overall / Phase Boss Battle | Player XP |
| Campaign milestone / global achievement | Player XP |

Vocabulary should have multiple small Daily Quests, for example:

- Vocabulary / Flashcard Gate
- Vocabulary / Codex Entry
- Vocabulary / Collocation Forge
- Vocabulary / Context Hunt
- Vocabulary / Error Dungeon

---

## 1. Background Context

The current project already has a generic quest architecture:

- `quest_templates`: blueprint table for generated quests.
- `quests`: concrete quest instances assigned to a campaign and date.
- `weekly_missions`: parent weekly mission.
- `weekly_mission_items`: mission requirements.
- `campaign_skill_states`: stores skill XP, level, rank, confirmed rank, streak, and last practiced date.

The current quest system already supports:

- Daily Quests
- Main Quests
- Weekly Missions
- Quest Archive
- Quest status lifecycle
- Reward claiming
- Claimed XP recalculation

Therefore, Vocabulary Daily Quest should be implemented as a **skill-specific quest track** inside the existing system, not as a separate database family.

---

## 2. Design Principles

### 2.1 Skill XP is the learning source of truth

Daily learning progress should be reflected in the related skill.

Examples:

```text
Vocabulary / Flashcard Gate    -> Vocabulary XP
Reading / Passage Scan         -> Reading XP
Listening / Dictation Drill    -> Listening XP
Writing / Sentence Upgrade     -> Writing XP
Speaking / Shadowing Drill     -> Speaking XP
```

### 2.2 Player XP is the global achievement layer

Player XP should not receive every small Daily Quest reward directly.

Player XP represents major global progress:

- Overall Boss clear
- Phase Boss clear
- Campaign milestone
- Long-term achievement

### 2.3 Player Level is derived display, not daily learning source

Player Level should remain a high-level dashboard indicator.

Daily study progress should primarily be visible through:

- `campaign_skill_states.xp`
- `campaign_skill_states.level`
- `campaign_skill_states.rank`
- Skill Matrix progress bars

### 2.4 Multiple Daily Quests per skill are allowed

A skill can have multiple daily micro-quests.

Example for Vocabulary:

```text
vocabulary_flashcard
vocabulary_codex
vocabulary_collocation
vocabulary_context
vocabulary_error
```

Do not enforce uniqueness by `(campaign_id, quest_date, skill_id)`, because that would block multiple Vocabulary quests on the same day.

---

## 3. Recommended Data Model Changes

## 3.1 Extend `quest_templates`

Add fields:

```sql
ALTER TABLE quest_templates
ADD COLUMN quest_track_code VARCHAR(50) NULL,
ADD COLUMN activity_type VARCHAR(80) NULL,
ADD COLUMN reward_skill_id INT NULL,
ADD COLUMN target_metric VARCHAR(80) NULL,
ADD COLUMN target_count INT NULL,
ADD COLUMN expected_minutes INT NULL;
```

### Field meanings

| Column | Meaning |
|---|---|
| `quest_track_code` | Broad quest family, e.g. `vocabulary`, `reading`, `listening` |
| `activity_type` | Specific gameplay/activity type, e.g. `flashcard_gate`, `codex_entry` |
| `reward_skill_id` | Skill that receives XP when the quest is claimed |
| `target_metric` | What the quest measures, e.g. `cards_reviewed`, `words_added` |
| `target_count` | Required amount for completion |
| `expected_minutes` | Expected study time |

### Example template

```text
title: Flashcard Gate
primary_skill_id: Vocabulary
reward_skill_id: Vocabulary
quest_track_code: vocabulary
activity_type: flashcard_gate
target_metric: cards_reviewed
target_count: 20
expected_minutes: 10
base_xp: 30
quest_role: support
difficulty: normal
```

---

## 3.2 Extend `quests`

Add fields:

```sql
ALTER TABLE quests
ADD COLUMN quest_track_code VARCHAR(50) NULL,
ADD COLUMN activity_type VARCHAR(80) NULL,
ADD COLUMN reward_skill_id INT NULL,
ADD COLUMN target_metric VARCHAR(80) NULL,
ADD COLUMN target_count INT NULL,
ADD COLUMN completion_payload JSON NULL;
```

### `completion_payload` examples

#### Flashcard Gate

```json
{
  "cards_reviewed": 20,
  "correct_count": 16,
  "again_count": 2,
  "hard_count": 2,
  "good_count": 12,
  "easy_count": 4
}
```

#### Codex Entry

```json
{
  "new_words_added": 5,
  "words_with_meaning_en": 5,
  "words_with_meaning_vi": 5,
  "words_with_examples": 3
}
```

#### Collocation Forge

```json
{
  "collocations_forged": 10,
  "correct_matches": 8,
  "example_sentences_created": 3
}
```

---

## 3.3 Reinterpret `daily_slot_code`

Current usage:

```text
core
support
mini
```

Recommended new usage:

```text
vocabulary_flashcard
vocabulary_codex
vocabulary_collocation
vocabulary_context
vocabulary_error
reading_scan
listening_dictation
writing_sentence
speaking_shadowing
grammar_pattern
collocation_forge
```

The existing unique constraint can still work if `daily_slot_code` becomes the unique quest slot for the day:

```text
(campaign_id, quest_date, daily_slot_code)
```

This allows multiple Vocabulary quests in the same day as long as each has a different `daily_slot_code`.

Do **not** replace it with:

```text
(campaign_id, quest_date, skill_id)
```

That would prevent multiple daily quests for one skill.

---

## 3.4 Add `skill_xp_transactions`

Purpose:

- prevent duplicate XP claiming;
- make XP reward history auditable;
- allow recomputation of skill states from transaction records.

```sql
CREATE TABLE skill_xp_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    source_type VARCHAR(80) NOT NULL,
    source_id BIGINT NOT NULL,
    xp_amount INT NOT NULL,
    reason VARCHAR(255),
    awarded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_skill_xp_source (
        campaign_id,
        skill_id,
        source_type,
        source_id
    )
);
```

### Example rows

```text
campaign_id: 1
skill_id: Vocabulary
source_type: quest
source_id: 532
xp_amount: 30
reason: Daily Vocabulary Flashcard Gate claimed
```

```text
campaign_id: 1
skill_id: Vocabulary
source_type: weekly_mission
source_id: 12
xp_amount: 120
reason: Weekly Vocabulary Expansion claimed
```

```text
campaign_id: 1
skill_id: Vocabulary
source_type: boss_battle
source_id: 4
xp_amount: 60
reason: Vocabulary Boss 01 cleared
```

---

## 3.5 Add `player_xp_transactions`

Purpose:

- keep Player XP separate from Skill XP;
- award only global/overall progress;
- prevent duplicate Player XP claiming.

```sql
CREATE TABLE player_xp_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    source_type VARCHAR(80) NOT NULL,
    source_id BIGINT NOT NULL,
    xp_amount INT NOT NULL,
    reason VARCHAR(255),
    awarded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_player_xp_source (
        campaign_id,
        source_type,
        source_id
    )
);
```

### Example rows

```text
campaign_id: 1
source_type: phase_boss
source_id: 1
xp_amount: 100
reason: Phase 01 Boss - Foundation Scan cleared
```

```text
campaign_id: 1
source_type: campaign_milestone
source_id: 5
xp_amount: 200
reason: Month 3 Foundation milestone cleared
```

---

## 3.6 Extend `weekly_missions`

Add fields:

```sql
ALTER TABLE weekly_missions
ADD COLUMN primary_skill_id INT NULL,
ADD COLUMN mission_track_code VARCHAR(50) NULL,
ADD COLUMN activity_type VARCHAR(80) NULL,
ADD COLUMN reward_skill_id INT NULL;
```

### Example Weekly Vocabulary Mission

```text
title: Weekly Vocabulary Expansion
primary_skill_id: Vocabulary
reward_skill_id: Vocabulary
mission_track_code: vocabulary
activity_type: weekly_vocabulary_expansion
reward_xp: 120
```

Mission items:

```text
- Review 100 flashcards
- Add 30 new words to Codex
- Forge 20 collocations
- Complete 5 Context Hunt tasks
- Defeat 5 vocabulary errors
```

---

## 4. XP Routing Logic

## 4.1 Daily Quest Claim

Current system has explicit reward claiming. Keep that flow.

New logic:

```text
POST /api/quests/{id}/claim
-> Load quest
-> Ensure quest.completed == true
-> Ensure quest.reward_claimed == false
-> Determine target skill:
   reward_skill_id if present
   else skill_id
-> Insert skill_xp_transactions
-> Mark reward_claimed = true
-> Set reward_claimed_at
-> Recompute campaign_skill_states
-> Recompute player summary
```

### Important rule

Daily Quest should not create a `player_xp_transactions` row.

---

## 4.2 Weekly Mission Claim

```text
POST /api/weekly-missions/{id}/claim
-> Load weekly mission
-> Ensure status == completed
-> Ensure reward_claimed == false
-> If reward_skill_id is present:
      insert skill_xp_transactions
   Else:
      insert player_xp_transactions
-> Mark reward_claimed = true
-> Recompute skill states and player summary
```

Recommended direction:

- Vocabulary Weekly Mission should have `reward_skill_id = Vocabulary`.
- Future Reading/Listening/Writing/Speaking weekly missions should also have clear `reward_skill_id`.
- Only global weekly missions should route to Player XP.

---

## 4.3 Boss Battle Reward Routing

Final approved rule:

```text
Skill-specific Boss Battle -> Skill XP
Overall / Phase Boss Battle -> Player XP
```

Examples:

```text
Vocabulary Boss 01 - Foundation Scan
-> +60 Vocabulary XP
-> skill_xp_transactions

Reading Boss 01 - Passage Hunter
-> +60 Reading XP
-> skill_xp_transactions

Phase 01 Boss - Foundation Scan
-> +100 Player XP
-> player_xp_transactions
```

Recommended boss fields:

```text
boss_scope: skill | phase | overall
reward_skill_id: nullable
reward_xp: integer
```

Routing rule:

```text
if boss_scope == "skill" and reward_skill_id is not null:
    award Skill XP
else:
    award Player XP
```

---

## 5. Vocabulary Daily Quest Templates

Seed these first.

## 5.1 Vocabulary / Flashcard Gate

```text
title: Memory Gate
quest_track_code: vocabulary
activity_type: flashcard_gate
daily_slot_code: vocabulary_flashcard
target_metric: cards_reviewed
target_count: 20
expected_minutes: 10
base_xp: 30
reward_skill_id: Vocabulary
```

Task detail:

```text
Review 20 due flashcards. Mark each card as Again, Hard, Good, or Easy.
```

---

## 5.2 Vocabulary / Codex Entry

```text
title: Codex Entry
quest_track_code: vocabulary
activity_type: codex_entry
daily_slot_code: vocabulary_codex
target_metric: words_added
target_count: 5
expected_minutes: 10
base_xp: 25
reward_skill_id: Vocabulary
```

Task detail:

```text
Add 5 new vocabulary items to the Vocabulary Codex.
Each item should include meaning, part of speech, and one example sentence if possible.
```

---

## 5.3 Vocabulary / Collocation Forge

```text
title: Collocation Forge
quest_track_code: vocabulary
activity_type: collocation_forge
daily_slot_code: vocabulary_collocation
target_metric: collocations_forged
target_count: 10
expected_minutes: 10
base_xp: 30
reward_skill_id: Vocabulary
```

Task detail:

```text
Forge 10 collocations from known vocabulary items.
Examples: express an opinion, make a mistake, take a break.
```

---

## 5.4 Vocabulary / Context Hunt

```text
title: Context Hunt
quest_track_code: vocabulary
activity_type: context_hunt
daily_slot_code: vocabulary_context
target_metric: context_guesses
target_count: 5
expected_minutes: 10
base_xp: 25
reward_skill_id: Vocabulary
```

Task detail:

```text
Guess the meaning of 5 unknown words from context before checking the dictionary.
```

---

## 5.5 Vocabulary / Error Dungeon

```text
title: Error Dungeon
quest_track_code: vocabulary
activity_type: error_dungeon
daily_slot_code: vocabulary_error
target_metric: errors_corrected
target_count: 3
expected_minutes: 10
base_xp: 20
reward_skill_id: Vocabulary
```

Task detail:

```text
Correct 3 vocabulary-related errors such as wrong collocation, wrong word form, wrong register, or wrong preposition.
```

---

## 6. Backend FastAPI Requirements

## 6.1 Models

Update:

```text
backend/app/models.py
```

Add columns to:

```text
QuestTemplate
Quest
WeeklyMission
```

Add models:

```text
SkillXpTransaction
PlayerXpTransaction
```

---

## 6.2 Alembic Migration

Project uses:

- `backend/alembic/`
- `backend/alembic/versions/`
- `backend/alembic.ini`
- startup bootstrap with `run_database_bootstrap()`
- auto `alembic upgrade head` when DB already exists
- `Base.metadata.create_all` + `alembic stamp head` when DB is empty
- seed flow through `seed_database(db, start_date)`

Migration requirements:

```text
- Create a new Alembic revision.
- Add nullable columns first to avoid breaking existing data.
- Create transaction tables.
- Add unique constraints for transaction idempotency.
- Avoid destructive changes.
- Keep existing quest lifecycle fields.
```

---

## 6.3 Reward Service Logic

Create or update service functions:

```text
award_skill_xp(
    db,
    campaign_id,
    skill_id,
    source_type,
    source_id,
    xp_amount,
    reason
)

award_player_xp(
    db,
    campaign_id,
    source_type,
    source_id,
    xp_amount,
    reason
)
```

Both functions must be idempotent through unique constraints.

---

## 6.4 Recompute Skill Progress

Update `recompute_skill_progress` so skill XP can be computed from:

```text
skill_xp_transactions
+ existing vocabulary activity XP if still needed
```

Recommended transition:

- Short term: include both claimed quest XP and vocab computed XP if current code depends on it.
- Long term: normalize all claimable rewards into `skill_xp_transactions`.

Avoid double-counting Vocabulary XP if existing `compute_vocabulary_xp` already contributes.

---

## 6.5 Recompute Player Level

Update player XP calculation so Player XP comes from:

```text
player_xp_transactions
+ optional global legacy sources during migration period
```

Do not include every claimed Daily Quest directly in Player XP.

---

## 7. Frontend React Requirements

## 7.1 Quest Board

Add grouping/filtering by:

```text
skill
quest_track_code
activity_type
status
```

Recommended tabs:

```text
All
Vocabulary
Reading
Listening
Writing
Speaking
Grammar
Collocation
```

Vocabulary section should show:

```text
Memory Gate
Codex Entry
Collocation Forge
Context Hunt
Error Dungeon
```

Each card should display:

```text
- Skill receiving XP
- Activity type
- Target metric
- Target count
- Completion payload summary if completed
- Claim button if completed but unclaimed
```

---

## 7.2 Skill Matrix

When a quest is claimed:

```text
Vocabulary XP increases
Vocabulary Level/Rank recalculates
Player Level only changes when Player XP transaction exists
```

Show clearly:

```text
Reward: +30 Vocabulary XP
```

Not:

```text
Reward: +30 Player XP
```

---

## 7.3 Vocabulary UI Integration

Future screens:

```text
Vocabulary Dashboard
Vocabulary Codex
Flashcard Gate
Word Network Tree
Collocation Forge
Context Hunt
Error Dungeon
```

The first implementation slice does not need to build all screens.

---

## 8. Implementation Plan for Codex CLI

Do not implement all in one session. Use small verifiable slices.

## Task 1 — Docs / ADR Decision

Files likely:

```text
DECISIONS.md
TASKS.md
docs/current/*
docs/history/changelogs.md
docs/history/AGENT_NOTES.md
```

Output:

```text
- Record final XP routing decision.
- Record no separate Vocabulary Daily Quest table.
- Record quest extension strategy.
```

Validation:

```text
- Docs updated.
- No source code modified.
```

---

## Task 2 — Models + Alembic Migration

Files likely:

```text
backend/app/models.py
backend/alembic/versions/*.py
```

Output:

```text
- Add new quest/template/weekly fields.
- Add skill_xp_transactions.
- Add player_xp_transactions.
```

Validation:

```text
alembic upgrade head
backend startup
database tables/columns exist
```

---

## Task 3 — Seed Vocabulary Quest Templates

Files likely:

```text
backend/app/seed.py
backend/app/models.py
```

Output:

```text
Seed:
- Vocabulary / Flashcard Gate
- Vocabulary / Codex Entry
- Vocabulary / Collocation Forge
- Vocabulary / Context Hunt
- Vocabulary / Error Dungeon
```

Validation:

```text
/api/dev/reset
GET quest templates
Vocabulary templates exist and are not duplicated
```

---

## Task 4 — Quest Claim Reward Routing

Files likely:

```text
backend/app/services.py
backend/app/routes/*.py
backend/app/schemas.py
```

Output:

```text
Daily Quest claim creates skill_xp_transactions.
No duplicate reward on second claim.
Skill state recalculates.
```

Validation:

```text
Complete quest
Claim quest
Check skill_xp_transactions row
Check campaign_skill_states.xp
Reclaim same quest should not duplicate XP
```

---

## Task 5 — Weekly Mission Skill Reward

Files likely:

```text
backend/app/services.py
backend/app/routes/*.py
backend/app/models.py
backend/app/seed.py
```

Output:

```text
Weekly mission with reward_skill_id routes to Skill XP.
Global mission without reward_skill_id routes to Player XP.
```

Validation:

```text
Complete weekly vocabulary mission
Claim
Check skill_xp_transactions
Check Vocabulary XP
```

---

## Task 6 — Boss Reward Routing

Files likely:

```text
backend/app/models.py
backend/app/services.py
backend/app/routes/*.py
```

Output:

```text
Skill Boss -> Skill XP
Phase/Overall Boss -> Player XP
```

Validation:

```text
Clear Vocabulary Boss
Check skill_xp_transactions

Clear Phase Boss
Check player_xp_transactions
```

---

## Task 7 — Frontend Quest Board

Files likely:

```text
frontend/src/*
```

Output:

```text
- Show quest skill reward.
- Group/filter quests by skill and activity type.
- Display Vocabulary Daily Quest group.
```

Validation:

```text
npm run build
manual browser smoke test
Quest Board UI shows correct reward destination
```

---

## 9. Agent Workflow Requirements

Before each coding task, agent must follow the project workflow.

## 9.1 Ground Repo Before Work

Read in order:

```text
AGENTS.md
README.md
TASKS.md
DECISIONS.md
docs/current/CONTEXT_INDEX.md
```

Stop when:

```text
- Task type is identified.
- Files likely to be modified are identified.
- Existing pattern to follow is identified.
- Goal, constraints, and next steps are clear.
```

---

## 9.2 Lock Task Contract

Before implementation, write:

```text
Goal
Completion Criteria
In Scope
Out of Scope
Constraints
Risks
```

---

## 9.3 Plan Before Broad Tasks

Plan first if task:

```text
- touches multiple files;
- changes backend behavior;
- changes schema or API contract;
- involves Alembic migration;
- requires validation sequence.
```

---

## 9.4 Execute in Small Slices

Rules:

```text
- Touch only necessary files.
- Follow existing repo patterns.
- No unrelated cleanup.
- Every slice must be verifiable.
```

---

## 9.5 Verify

Priority:

```text
1. Syntax / type checks
2. Focused smoke checks
3. Tests for changed behavior
4. Manual review for medium/high risk changes
```

---

## 9.6 Update Docs and Trackers

After meaningful changes, update:

```text
TASKS.md
docs/history/TEST_REPORT.md
docs/history/AGENT_NOTES.md
docs/history/changelogs.md
DECISIONS.md or ADR
```

---

## 9.7 Session Wrap-up

Every session must end with:

```text
What changed
What was validated
What remains open
What to read first next session
```

---

## 10. Final Contract Summary for Agent

```text
Do not create separate daily quest tables for Vocabulary.

Keep the generic Quest system.

Extend quests and quest_templates with:
- quest_track_code
- activity_type
- reward_skill_id
- target_metric
- target_count
- completion_payload

Extend weekly_missions with:
- primary_skill_id
- mission_track_code
- activity_type
- reward_skill_id

Daily Quest XP must be awarded to one target skill only.

A skill can have multiple Daily Quests per day through specific daily_slot_code values.

Weekly Mission XP must be awarded to Skill XP when reward_skill_id is present.

Skill-specific Boss Battle must award Skill XP.

Overall or Phase Boss Battle must award Player XP.

Use transaction tables to prevent duplicate XP claiming:
- skill_xp_transactions for skill rewards
- player_xp_transactions for global/player rewards

Player Level is a high-level progression display.
Skill Level is the main source of learning progress.
```
