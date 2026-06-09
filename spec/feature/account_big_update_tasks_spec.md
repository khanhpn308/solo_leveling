# Big Update Specification: Account System, Onboarding, Certificate Suggestions, Skill Quest Quotas, and Rank Boss Exams

**Project:** IELTS Quest Dashboard  
**Document type:** Implementation task specification for Codex CLI / agent workflow  
**Target stack:** React frontend, FastAPI backend, MySQL database, Alembic migrations, Docker local development  
**Status:** Approved planning spec for phased implementation  
**Date:** 2026-06-07

---

## 0. Purpose

This file consolidates all tasks for the **Big Update: Add Account System**.

The update includes:

1. Account/Auth layer.
2. Required onboarding flow.
3. Manual certificate score input MVP.
4. Suggestion Inbox rank apply fix.
5. Campaign template and fixed campaign setup.
6. Skill-specific Daily Quest quota model.
7. Rank Boss Exam system for XP-based rank promotion.
8. Register/Login frontend.
9. Onboarding frontend.
10. Rank Boss frontend.
11. Backend ownership protection.
12. Documentation and tracker updates.

This file is intended for agents to load before implementation and to split work into multiple focused sessions.

---

## 1. Current Project Context

The current project already has these gameplay entities:

```text
players
campaigns
skills
campaign_skill_states
quests
weekly_missions
boss_battles
badges
badge_unlocks
checkins
error_logs
writing_entries
speaking_entries
mock_tests
test_records
skill_rank_suggestions
skill_rank_history
weakness_suggestions
roadmap_phases
study_materials
main_quest_plans
```

Current quest uniqueness:

```text
quests unique key:
(campaign_id, quest_date, daily_slot_code)
```

Current rank ladder:

```text
F → E → D → C → B → A → S
```

Current rank semantics:

```text
rank = calculated / displayed rank
confirmed_rank = approved rank after review/suggestion/promotion flow
```

---

## 2. Final Accepted Decisions

### 2.1 Account / Player / Campaign Relationship

MVP relationship:

```text
1 account = 1 player = 1 active campaign
```

Database should still preserve future expansion:

```text
players 1 --- many campaigns
```

Do not hard-code the schema to only one campaign forever.

### 2.2 Account Layer Does Not Replace Player

Add account/auth layer above `players`.

```text
accounts = login identity, security, sessions
players = game profile / learner identity
campaigns = concrete IELTS learning journey
```

Do not remove or replace `players`.

### 2.3 Onboarding Is Mandatory

Onboarding is the required first-time setup flow after registration.

```text
Register account
→ Login/session created
→ Onboarding
→ Optional manual certificate score input
→ Campaign confirmation
→ Activate campaign
→ Dashboard
```

User must not access dashboard before onboarding is completed.

### 2.4 Do Not Ask User to Configure Roadmap Logic

Do **not** ask the user to choose:

```text
current level
study duration
daily study time
vocabulary quota
reading quota
listening quota
skill quest quota
```

Reason:

```text
current level = evaluated from certificate/manual score if provided
study duration = fixed by campaign template
daily study time = not needed; user completes quests at their own pace
skill quest quota = fixed by campaign template / roadmap logic
```

### 2.5 No Internal Placement Test in MVP

If user has no certificate/manual score:

```text
all skill confirmed_rank = F
```

No internal placement test is needed in MVP.

### 2.6 Certificate MVP Uses Manual Score Input

MVP certificate flow:

```text
user manually enters IELTS scores
```

No file upload/storage is required in this phase.

### 2.7 Certificate Suggestions Do Not Require Rank Boss

Manual certificate score flow:

```text
manual score input
→ create skill_rank_suggestions
→ Suggestion Inbox
→ Apply
→ update campaign_skill_states.confirmed_rank directly
→ insert skill_rank_history
```

Certificate/manual suggestion **does not require Rank Boss Exam**.

### 2.8 XP-based Rank Promotion Requires Rank Boss

When skill XP reaches the next rank threshold:

```text
rank may calculate upward
confirmed_rank stays unchanged
promotion_status = boss_required
Rank Boss unlocks
Pass ≥80%
confirmed_rank updates
```

### 2.9 No Multi-rank Jump for XP-based Promotion

Even if XP is high enough for multiple ranks, promotion is always one rank at a time.

Example:

```text
confirmed_rank = F
rank_from_xp = C
pending_rank must be E only
unlock boss F → E only
```

After clearing F→E, the system may evaluate E→D on a later refresh if XP still qualifies.

### 2.10 Rank Boss Retry Rule

For each `campaign + skill + from_rank + to_rank`:

```text
maximum 2 attempts/day
```

If exceeded:

```text
Daily retry limit reached. Try again tomorrow.
```

### 2.11 Rank Boss Time Limit

MVP time limit:

```text
30 minutes for all Rank Boss exams
```

Later this can vary by skill, rank level, exam type, or question count.

### 2.12 Writing/Speaking Rank Boss Out of Scope

Do not implement Writing/Speaking Rank Boss in this phase.

Reason:

```text
Writing and Speaking require subjective/manual/AI-assisted grading.
```

Must be recorded in task tracker/backlog.

MVP Rank Boss skills:

```text
Vocabulary
Reading
Listening
Grammar
Collocation
```

### 2.13 Campaign Target

Current campaign target is fixed:

```text
IELTS 7.0–7.5
18-month roadmap
```

---

## 3. Scope Categories

### 3.1 Account-scoped

Authentication and account-level UI/security data.

```text
accounts
account_sessions
account_tokens
account_security_events
account_preferences
```

### 3.2 Player-wide

Long-term learner/game identity and cross-campaign data.

```text
players
player_learning_profiles
test_records
```

### 3.3 Campaign-scoped

Concrete learning journey data.

```text
campaigns
campaign_settings
campaign_skill_states
quests
weekly_missions
boss_battles
badge_unlocks
checkins
error_logs
writing_entries
speaking_entries
mock_tests
certificate_records
rank_exam_attempts
```

### 3.4 Template-scoped

Reusable roadmap/campaign configuration.

```text
campaign_templates
campaign_template_skill_quotas
quest_templates
rank_exam_pools
rank_exam_versions
rank_exam_questions
```

---

# 4. Database Design

## 4.1 Account/Auth Tables

### 4.1.1 `accounts`

```sql
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    email_normalized VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(120) NULL,
    avatar_url VARCHAR(500) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    role VARCHAR(30) NOT NULL DEFAULT 'user',
    onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
    onboarding_completed_at DATETIME NULL,
    email_verified_at DATETIME NULL,
    last_login_at DATETIME NULL,
    failed_login_count INT NOT NULL DEFAULT 0,
    locked_until DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_accounts_email_normalized (email_normalized)
);
```

Allowed `status`:

```text
active
pending_verification
disabled
locked
deleted
```

Allowed `role` for MVP:

```text
user
admin
```

### 4.1.2 Modify `players`

```sql
ALTER TABLE players
ADD COLUMN account_id BIGINT NULL,
ADD CONSTRAINT fk_players_account_id
    FOREIGN KEY (account_id) REFERENCES accounts(id),
ADD UNIQUE KEY uq_players_account_id (account_id);
```

Migration strategy:

```text
1. Add nullable account_id first.
2. Seed/create default dev account.
3. Backfill existing players.account_id.
4. Later migration may make account_id NOT NULL if safe.
```

### 4.1.3 `account_sessions`

```sql
CREATE TABLE account_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    refresh_token_hash CHAR(64) NOT NULL,
    user_agent VARCHAR(500) NULL,
    ip_address VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME NULL,
    expires_at DATETIME NOT NULL,
    revoked_at DATETIME NULL,
    revoke_reason VARCHAR(255) NULL,
    CONSTRAINT fk_account_sessions_account_id
        FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE KEY uq_account_sessions_refresh_token_hash (refresh_token_hash),
    INDEX ix_account_sessions_account_id (account_id),
    INDEX ix_account_sessions_expires_at (expires_at)
);
```

Rule:

```text
Never store raw refresh tokens. Only store refresh token hash.
```

### 4.1.4 `account_tokens`

```sql
CREATE TABLE account_tokens (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL,
    purpose VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    consumed_at DATETIME NULL,
    metadata_json JSON NULL,
    CONSTRAINT fk_account_tokens_account_id
        FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE KEY uq_account_tokens_token_hash (token_hash),
    INDEX ix_account_tokens_account_purpose (account_id, purpose)
);
```

Allowed `purpose`:

```text
email_verification
password_reset
change_email
```

### 4.1.5 `account_security_events`

```sql
CREATE TABLE account_security_events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NULL,
    event_type VARCHAR(80) NOT NULL,
    email_attempted VARCHAR(255) NULL,
    ip_address VARCHAR(100) NULL,
    user_agent VARCHAR(500) NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    detail TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_security_events_account_id
        FOREIGN KEY (account_id) REFERENCES accounts(id),
    INDEX ix_account_security_events_account_id (account_id),
    INDEX ix_account_security_events_event_type (event_type),
    INDEX ix_account_security_events_created_at (created_at)
);
```

Allowed `event_type`:

```text
register
login_success
login_failed
logout
refresh_token_used
refresh_token_revoked
password_changed
password_reset_requested
password_reset_completed
email_verified
account_locked
```

### 4.1.6 `account_preferences`

System preferences only.

```sql
CREATE TABLE account_preferences (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    locale VARCHAR(20) NOT NULL DEFAULT 'vi',
    timezone VARCHAR(80) NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
    theme VARCHAR(30) NOT NULL DEFAULT 'dark',
    accent_color VARCHAR(30) NULL,
    notification_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    daily_reminder_time TIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_preferences_account_id
        FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE KEY uq_account_preferences_account_id (account_id)
);
```

---

## 4.2 Learning Setup Tables

### 4.2.1 `player_learning_profiles`

Long-term learning preferences attached to player. Do not put campaign-specific goals here.

```sql
CREATE TABLE player_learning_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    player_id BIGINT NOT NULL,
    preferred_learning_style VARCHAR(50) DEFAULT 'mixed',
    dictionary_mode VARCHAR(50) DEFAULT 'bilingual_first',
    pronunciation_focus BOOLEAN DEFAULT TRUE,
    collocation_focus BOOLEAN DEFAULT TRUE,
    native_language VARCHAR(50) DEFAULT 'vi',
    interface_learning_language VARCHAR(50) DEFAULT 'mixed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_player_learning_profiles_player_id
        FOREIGN KEY (player_id) REFERENCES players(id),
    UNIQUE KEY uq_player_learning_profiles_player_id (player_id)
);
```

### 4.2.2 `campaign_templates`

Defines available roadmap/campaign types.

```sql
CREATE TABLE campaign_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(80) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    certificate_type VARCHAR(30) NOT NULL DEFAULT 'IELTS',
    target_band VARCHAR(20) NULL,
    duration_months INT NOT NULL,
    total_weeks INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_campaign_templates_code (code)
);
```

Initial seed:

```text
code = ielts_18_month_foundation
title = IELTS 18-Month Hunter Roadmap
certificate_type = IELTS
target_band = 7.0-7.5
duration_months = 18
total_weeks = 78
```

### 4.2.3 Modify `campaigns`

```sql
ALTER TABLE campaigns
ADD COLUMN campaign_template_id BIGINT NULL,
ADD COLUMN setup_completed BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN setup_completed_at DATETIME NULL;
```

### 4.2.4 `campaign_settings`

Campaign-specific learning setup.

```sql
CREATE TABLE campaign_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    target_certificate VARCHAR(30) NOT NULL DEFAULT 'IELTS',
    target_band VARCHAR(20) NOT NULL DEFAULT '7.0-7.5',
    current_english_level VARCHAR(50) NULL,
    start_date DATE NOT NULL,
    target_test_date DATE NULL,
    study_duration_months INT NOT NULL DEFAULT 18,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_campaign_settings_campaign_id
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    UNIQUE KEY uq_campaign_settings_campaign_id (campaign_id)
);
```

Do not include:

```text
daily_study_minutes
study_days_per_week
daily_revision_minutes
weekly_deep_study_minutes
daily_quest_count_preference
```

### 4.2.5 `campaign_template_skill_quotas`

Template-level quest quota per skill.

```sql
CREATE TABLE campaign_template_skill_quotas (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_template_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    daily_quota INT NOT NULL DEFAULT 0,
    weekly_quota INT NULL,
    priority INT NOT NULL DEFAULT 100,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    preferred_activity_types JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_campaign_template_skill_quotas_template_id
        FOREIGN KEY (campaign_template_id) REFERENCES campaign_templates(id),
    CONSTRAINT fk_campaign_template_skill_quotas_skill_id
        FOREIGN KEY (skill_id) REFERENCES skills(id),
    UNIQUE KEY uq_template_skill_quota (campaign_template_id, skill_id)
);
```

Initial seed example:

```text
Vocabulary = 3 quests/day
Reading = 1 quest/day
Listening = 1 quest/day
Grammar = 1 quest/day
Collocation = 1 quest/day
Writing = 0 quests/day in this first phase
Speaking = 0 quests/day in this first phase
```

### 4.2.6 `campaign_skill_quest_quotas`

Campaign instance copy of template skill quota.

```sql
CREATE TABLE campaign_skill_quest_quotas (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    daily_quota INT NOT NULL DEFAULT 0,
    weekly_quota INT NULL,
    priority INT NOT NULL DEFAULT 100,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    preferred_activity_types JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_campaign_skill_quest_quotas_campaign_id
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    CONSTRAINT fk_campaign_skill_quest_quotas_skill_id
        FOREIGN KEY (skill_id) REFERENCES skills(id),
    UNIQUE KEY uq_campaign_skill_quest_quota (campaign_id, skill_id)
);
```

### 4.2.7 `vocabulary_settings`

Vocabulary settings are system/campaign-controlled defaults, not user-edited roadmap logic.

```sql
CREATE TABLE vocabulary_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    daily_new_words_target INT DEFAULT 5,
    daily_flashcard_target INT DEFAULT 20,
    daily_collocation_target INT DEFAULT 3,
    daily_context_hunt_target INT DEFAULT 5,
    daily_error_review_target INT DEFAULT 3,
    vocab_review_mode VARCHAR(50) DEFAULT 'mixed',
    vocab_grouping_mode VARCHAR(50) DEFAULT 'topic',
    dictionary_mode VARCHAR(50) DEFAULT 'bilingual_first',
    example_sentence_required BOOLEAN DEFAULT TRUE,
    pronunciation_required BOOLEAN DEFAULT FALSE,
    word_family_required BOOLEAN DEFAULT FALSE,
    synonym_antonym_required BOOLEAN DEFAULT FALSE,
    collocation_required BOOLEAN DEFAULT TRUE,
    spaced_repetition_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_vocabulary_settings_campaign_id
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    UNIQUE KEY uq_vocabulary_settings_campaign_id (campaign_id)
);
```

---

## 4.3 Certificate / Manual Score Tables

### 4.3.1 `certificate_records`

MVP uses manual entry only.

```sql
CREATE TABLE certificate_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    player_id BIGINT NOT NULL,
    campaign_id BIGINT NULL,
    certificate_type VARCHAR(30) NOT NULL DEFAULT 'IELTS',
    overall_score DECIMAL(4,1) NULL,
    listening_score DECIMAL(4,1) NULL,
    reading_score DECIMAL(4,1) NULL,
    writing_score DECIMAL(4,1) NULL,
    speaking_score DECIMAL(4,1) NULL,
    input_method VARCHAR(30) NOT NULL DEFAULT 'manual',
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    note TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME NULL,
    CONSTRAINT fk_certificate_records_player_id
        FOREIGN KEY (player_id) REFERENCES players(id),
    CONSTRAINT fk_certificate_records_campaign_id
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

Allowed `input_method`:

```text
manual
file_upload
admin_import
```

MVP uses:

```text
manual
```

---

## 4.4 Rank Boss Exam Tables

### 4.4.1 `rank_exam_pools`

```sql
CREATE TABLE rank_exam_pools (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_id BIGINT NOT NULL,
    from_rank VARCHAR(5) NOT NULL,
    to_rank VARCHAR(5) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    pass_percent INT NOT NULL DEFAULT 80,
    default_time_limit_minutes INT NOT NULL DEFAULT 30,
    max_attempts_per_day INT NOT NULL DEFAULT 2,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_rank_exam_pools_skill_id
        FOREIGN KEY (skill_id) REFERENCES skills(id),
    INDEX ix_rank_exam_pools_skill_rank (skill_id, from_rank, to_rank)
);
```

### 4.4.2 `rank_exam_versions`

```sql
CREATE TABLE rank_exam_versions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    pool_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    version_code VARCHAR(80) NULL,
    total_questions INT NOT NULL,
    total_points INT NOT NULL,
    difficulty VARCHAR(30) DEFAULT 'normal',
    time_limit_minutes INT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_rank_exam_versions_pool_id
        FOREIGN KEY (pool_id) REFERENCES rank_exam_pools(id),
    INDEX ix_rank_exam_versions_pool_id (pool_id)
);
```

Backend should use:

```text
rank_exam_versions.time_limit_minutes if not null
else rank_exam_pools.default_time_limit_minutes
```

### 4.4.3 `rank_exam_questions`

```sql
CREATE TABLE rank_exam_questions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    exam_version_id BIGINT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    instruction TEXT NULL,
    options_json JSON NULL,
    correct_answer_json JSON NULL,
    explanation TEXT NULL,
    points INT NOT NULL DEFAULT 1,
    order_index INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rank_exam_questions_exam_version_id
        FOREIGN KEY (exam_version_id) REFERENCES rank_exam_versions(id),
    INDEX ix_rank_exam_questions_exam_version_id (exam_version_id)
);
```

Allowed MVP `question_type`:

```text
multiple_choice
gap_fill
matching
```

Out of scope:

```text
writing_short
speaking_prompt
audio_response
manual_grading
```

### 4.4.4 `rank_exam_attempts`

```sql
CREATE TABLE rank_exam_attempts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    campaign_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    from_rank VARCHAR(5) NOT NULL,
    to_rank VARCHAR(5) NOT NULL,
    pool_id BIGINT NOT NULL,
    exam_version_id BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'in_progress',
    score_points INT DEFAULT 0,
    total_points INT NOT NULL,
    score_percent DECIMAL(5,2) DEFAULT 0.00,
    pass_percent INT NOT NULL DEFAULT 80,
    time_limit_minutes INT NOT NULL DEFAULT 30,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    submitted_at DATETIME NULL,
    passed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rank_exam_attempts_campaign_id
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    CONSTRAINT fk_rank_exam_attempts_skill_id
        FOREIGN KEY (skill_id) REFERENCES skills(id),
    CONSTRAINT fk_rank_exam_attempts_pool_id
        FOREIGN KEY (pool_id) REFERENCES rank_exam_pools(id),
    CONSTRAINT fk_rank_exam_attempts_exam_version_id
        FOREIGN KEY (exam_version_id) REFERENCES rank_exam_versions(id),
    INDEX ix_rank_exam_attempts_campaign_skill (campaign_id, skill_id),
    INDEX ix_rank_exam_attempts_status (status),
    INDEX ix_rank_exam_attempts_started_at (started_at)
);
```

Allowed `status`:

```text
in_progress
submitted
passed
failed
expired
abandoned
```

### 4.4.5 `rank_exam_answers`

```sql
CREATE TABLE rank_exam_answers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    attempt_id BIGINT NOT NULL,
    question_id BIGINT NOT NULL,
    answer_json JSON NULL,
    is_correct BOOLEAN NULL,
    points_awarded INT DEFAULT 0,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rank_exam_answers_attempt_id
        FOREIGN KEY (attempt_id) REFERENCES rank_exam_attempts(id),
    CONSTRAINT fk_rank_exam_answers_question_id
        FOREIGN KEY (question_id) REFERENCES rank_exam_questions(id),
    UNIQUE KEY uq_rank_exam_answer_attempt_question (attempt_id, question_id)
);
```

### 4.4.6 Modify `campaign_skill_states`

```sql
ALTER TABLE campaign_skill_states
ADD COLUMN pending_rank VARCHAR(5) NULL,
ADD COLUMN promotion_status VARCHAR(30) DEFAULT 'none',
ADD COLUMN promotion_unlocked_at DATETIME NULL,
ADD COLUMN last_rank_exam_attempt_id BIGINT NULL;
```

Allowed `promotion_status`:

```text
none
eligible
boss_required
in_progress
passed
failed
```

---

# 5. Backend API Design

## 5.1 Auth APIs

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
```

## 5.2 Onboarding APIs

```text
GET  /api/onboarding/status
POST /api/onboarding/activate-campaign
```

Preferred MVP flow:

```text
1. POST /api/certificates/manual or skip
2. POST /api/onboarding/activate-campaign
```

## 5.3 Certificate APIs

```text
POST /api/certificates/manual
GET  /api/certificates
```

Manual score submission must:

```text
1. create certificate_records
2. map scores to suggested ranks
3. create skill_rank_suggestions
4. return created suggestions or summary
```

## 5.4 Suggestion APIs

```text
POST /api/skill-rank-suggestions/{id}/apply
POST /api/skill-rank-suggestions/{id}/dismiss
```

Apply certificate/manual suggestion:

```text
1. validate ownership
2. update campaign_skill_states.confirmed_rank
3. update campaign_skill_states.rank if needed
4. insert skill_rank_history
5. mark suggestion applied
6. return updated skill state
```

No Rank Boss required for certificate/manual suggestion.

## 5.5 Rank Boss APIs

```text
POST /api/rank-exams/start
GET  /api/rank-exams/{attempt_id}
POST /api/rank-exams/{attempt_id}/submit
```

Start exam rules:

```text
1. validate ownership
2. validate skill exists
3. validate promotion_status = boss_required
4. validate target rank = next rank only
5. validate attempts today < 2
6. find active pool by skill_id + from_rank + to_rank
7. randomly select one active exam version
8. create attempt
9. set expires_at = started_at + 30 minutes
10. return attempt + questions
```

Submit exam rules:

```text
1. validate attempt ownership
2. reject if expired
3. grade objective questions
4. score_percent = score_points / total_points * 100
5. if score_percent >= 80:
   - attempt status = passed
   - campaign_skill_states.confirmed_rank = to_rank
   - clear pending_rank
   - promotion_status = passed
   - last_rank_exam_attempt_id = attempt.id
   - insert skill_rank_history
6. if score_percent < 80:
   - attempt status = failed
   - promotion_status = failed or boss_required
   - confirmed_rank unchanged
7. return result
```

---

# 6. Frontend UI Design

## 6.1 Register Page

Route:

```text
/register
```

Fields:

```text
email
password
confirm password
display_name
```

Behavior:

```text
POST /api/auth/register
success -> auth session created -> redirect /onboarding
```

## 6.2 Login Page

Route:

```text
/login
```

Fields:

```text
email
password
```

Behavior:

```text
POST /api/auth/login
GET /api/auth/me
if onboarding_completed = false -> /onboarding
if true -> dashboard
```

## 6.3 Auth Provider + Protected Routes

Frontend auth state:

```text
account
player
activeCampaign
isAuthenticated
isLoading
onboardingCompleted
```

Protected routes:

```text
/
/dashboard
/quests
/skills
/vocabulary
/roadmap
/profile
/rank-boss/*
```

Routing rules:

```text
unauthenticated -> /login
authenticated but onboarding incomplete -> /onboarding
authenticated and onboarding complete -> dashboard
```

## 6.4 Onboarding Shell

Route:

```text
/onboarding
```

Screens:

```text
1. Welcome Hunter
2. Manual Certificate Input
3. Campaign Confirmation
4. Start Campaign
```

Do not ask user to configure:

```text
current level
study duration
daily study time
vocabulary quota
reading quota
listening quota
skill quest quota
```

## 6.5 Manual Certificate Input Screen

Route:

```text
/onboarding/certificate
```

Fields:

```text
certificate_type default IELTS
overall_score
listening_score
reading_score
writing_score
speaking_score
```

Must support:

```text
Skip for now
```

If skipped:

```text
all skill confirmed_rank remains F
```

## 6.6 Campaign Confirmation Screen

Route:

```text
/onboarding/campaign-confirmation
```

Display only:

```text
Campaign: IELTS 18-Month Hunter Roadmap
Target: IELTS 7.0–7.5
Duration: 18 months
Quest rhythm: fixed by campaign template
Skill quotas: fixed by roadmap
```

Button:

```text
Start Campaign
```

Calls:

```text
POST /api/onboarding/activate-campaign
```

## 6.7 Suggestion Inbox Apply Fix

Current issue:

```text
Suggestion Inbox shows Update rank F -> C, but Apply does not update rank.
```

Required:

```text
Apply certificate/manual suggestion directly updates confirmed_rank.
UI refreshes Skill Matrix after Apply.
Suggestion status changes to applied.
Dismiss marks suggestion dismissed.
```

## 6.8 Rank Boss Unlock UI

When XP-based promotion unlocks boss:

```text
Rank Boss Unlocked
Skill: Vocabulary
Current confirmed rank: F
Target rank: E
Pass condition: 80%
Time limit: 30 minutes
Attempts today: 0/2
```

Button:

```text
Start Boss
```

## 6.9 Rank Boss Exam Screen

Route:

```text
/rank-boss/:attemptId
```

UI:

```text
SYSTEM GATE OPENED
Rank Boss: Vocabulary F → E
Pass condition: 80%
Time limit: 30:00
Questions: current / total
Submit
```

MVP skills:

```text
Vocabulary
Reading
Listening
Grammar
Collocation
```

Out of scope:

```text
Writing Boss
Speaking Boss
subjective grading
audio recording
manual review
```

## 6.10 Rank Boss Result Screen

If passed:

```text
Cleared
Score: 85%
Rank E confirmed
```

If failed:

```text
Failed
Score: 70%
Rank remains F
Attempts remaining today: 1/2
```

If attempts exhausted:

```text
Try again tomorrow
```

---

# 7. Daily Quest Quota Update

Old logic:

```text
core/support/mini fixed daily roles
```

New logic:

```text
skill quota + activity type
```

Daily slot code should become specific:

```text
vocabulary_flashcard
vocabulary_codex
vocabulary_collocation
reading_scan
listening_dictation
grammar_pattern
collocation_forge
```

Keep uniqueness:

```text
(campaign_id, quest_date, daily_slot_code)
```

Do not change to:

```text
(campaign_id, quest_date, skill_id)
```

because one skill can have multiple daily quests.

---

# 8. Phased Implementation Plan

Each phase should be completed in a separate focused session unless the agent explicitly confirms it is safe to combine.

---

## Phase 0 — Documentation / ADR / Tracker Preparation

### Goal

Record architecture decisions before coding.

### Files likely to edit

```text
DECISIONS.md
TASKS.md
docs/current/CONTEXT_INDEX.md
docs/current/DATABASE_SCHEMA.md
docs/current/SCHEMA_SEMANTICS.md
docs/history/changelogs.md
docs/history/AGENT_NOTES.md
```

### Tasks

```text
1. Add Account/Auth architecture decision.
2. Add new scope category: account-scoped.
3. Record mandatory onboarding.
4. Record no internal placement test.
5. Record manual certificate score MVP.
6. Record certificate suggestions apply directly.
7. Record XP-based Rank Boss promotion.
8. Record Writing/Speaking Rank Boss out of scope and backlog.
9. Record skill quota daily quest generation.
```

### Validation

```text
Docs changed only.
No source code changed.
```

---

## Phase 1 — Account/Auth Database Migration

### Goal

Add account/auth tables and link players to accounts.

### Files likely to edit

```text
backend/app/models.py
backend/alembic/versions/*.py
```

### Tasks

```text
1. Add Account model.
2. Add AccountSession model.
3. Add AccountToken model.
4. Add AccountSecurityEvent model.
5. Add AccountPreference model.
6. Add players.account_id nullable.
7. Add indexes/constraints.
8. Generate Alembic migration.
```

### Validation

```text
alembic upgrade head
backend startup succeeds
empty DB bootstrap succeeds
existing DB upgrade succeeds
tables exist
players.account_id exists
```

---

## Phase 2 — Campaign Template / Settings / Quota Database Migration

### Goal

Add campaign setup and quota tables.

### Files likely to edit

```text
backend/app/models.py
backend/alembic/versions/*.py
```

### Tasks

```text
1. Add PlayerLearningProfile model.
2. Add CampaignTemplate model.
3. Add campaign_template_id/setup fields to Campaign.
4. Add CampaignSetting model.
5. Add CampaignTemplateSkillQuota model.
6. Add CampaignSkillQuestQuota model.
7. Add VocabularySetting model.
8. Generate Alembic migration.
```

### Validation

```text
alembic upgrade head
backend startup succeeds
all new tables exist
campaign setup fields exist
```

---

## Phase 3 — Certificate and Rank Boss Database Migration

### Goal

Add manual certificate and Rank Boss exam database.

### Files likely to edit

```text
backend/app/models.py
backend/alembic/versions/*.py
```

### Tasks

```text
1. Add CertificateRecord model.
2. Add RankExamPool model.
3. Add RankExamVersion model.
4. Add RankExamQuestion model.
5. Add RankExamAttempt model.
6. Add RankExamAnswer model.
7. Add campaign_skill_states promotion fields.
8. Generate Alembic migration.
```

### Validation

```text
alembic upgrade head
backend startup succeeds
rank exam tables exist
certificate_records exists
campaign_skill_states promotion fields exist
```

---

## Phase 4 — Seed and Backfill

### Goal

Make startup and dev reset work with account/campaign template settings.

### Files likely to edit

```text
backend/app/seed.py
backend/app/database.py
backend/app/models.py
```

### Tasks

```text
1. Seed default dev account if needed.
2. Seed default player linked to account.
3. Seed account_preferences.
4. Seed player_learning_profiles.
5. Seed campaign_templates.
6. Seed IELTS 18-month campaign template.
7. Seed campaign_template_skill_quotas.
8. Seed vocabulary_settings defaults.
9. Seed rank exam pools for MVP skills.
10. Seed at least one exam version per MVP pool.
11. Seed objective questions.
12. Ensure seed is idempotent.
13. Ensure /api/dev/reset does not unintentionally destroy all accounts unless explicitly dev-only.
```

### MVP Rank Boss seed skills

```text
Vocabulary F→E
Reading F→E
Listening F→E
Grammar F→E
Collocation F→E
```

### Out of scope seed

```text
Writing Boss
Speaking Boss
higher rank pools unless requested
```

### Validation

```text
docker compose up
backend startup succeeds
/api/dev/reset succeeds
default campaign template exists
skill quotas exist
rank exam pools exist
seed does not duplicate records
```

---

## Phase 5 — Backend Auth MVP

### Goal

Implement register/login/refresh/logout/me.

### Files likely to edit

```text
backend/app/routes/auth.py
backend/app/auth/passwords.py
backend/app/auth/tokens.py
backend/app/auth/dependencies.py
backend/app/main.py
backend/app/schemas.py
backend/app/services.py
```

### APIs

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
```

### Tasks

```text
1. Password hashing.
2. Password verification.
3. Access token generation.
4. Refresh token generation.
5. Refresh token hashing.
6. Refresh session storage.
7. Refresh token rotation.
8. Security event logging.
9. Auth schemas.
10. Auth route registration in FastAPI app.
```

### Validation

```text
Register new account
Duplicate email rejected
Login success
Wrong password fails
GET /api/auth/me works
Refresh works
Logout revokes session
```

---

## Phase 6 — Backend Onboarding and Campaign Activation

### Goal

Implement mandatory onboarding and campaign activation.

### Files likely to edit

```text
backend/app/routes/onboarding.py
backend/app/services.py
backend/app/schemas.py
backend/app/models.py
```

### APIs

```text
GET  /api/onboarding/status
POST /api/onboarding/activate-campaign
```

### Tasks

```text
1. Return onboarding status.
2. Activate first campaign from IELTS 18-month template.
3. Create campaign_settings.
4. Copy campaign_template_skill_quotas to campaign_skill_quest_quotas.
5. Create vocabulary_settings.
6. Create campaign_skill_states.
7. Generate main quests.
8. Generate first daily quests from skill quotas.
9. Mark accounts.onboarding_completed = true.
10. Mark campaigns.setup_completed = true.
```

### Validation

```text
New account cannot access dashboard before onboarding.
Activate campaign creates campaign.
Campaign settings exist.
Skill states exist.
Quest quotas exist.
Daily quests generated.
Account onboarding completed.
```

---

## Phase 7 — Backend Manual Certificate and Suggestion Apply Fix

### Goal

Manual certificate input and working Suggestion Inbox Apply.

### Files likely to edit

```text
backend/app/routes/certificates.py
backend/app/routes/skill_rank_suggestions.py
backend/app/services.py
backend/app/schemas.py
```

### APIs

```text
POST /api/certificates/manual
GET  /api/certificates
POST /api/skill-rank-suggestions/{id}/apply
POST /api/skill-rank-suggestions/{id}/dismiss
```

### Tasks

```text
1. Save manual IELTS scores to certificate_records.
2. Map scores to rank suggestions.
3. Create skill_rank_suggestions.
4. Fix Apply endpoint.
5. Apply directly updates confirmed_rank.
6. Insert skill_rank_history.
7. Dismiss updates suggestion status.
8. Return updated Skill Matrix state or summary.
```

### Important Rule

```text
Certificate/manual rank suggestion does not require Rank Boss.
```

### Validation

```text
Submit manual scores.
Suggestions appear.
Click Apply.
confirmed_rank updates.
Skill Matrix updates.
skill_rank_history records change.
Dismiss hides suggestion.
```

---

## Phase 8 — Backend Daily Quest Skill Quota Generator Update

### Goal

Change daily quest generation to use per-skill quota and activity type.

### Files likely to edit

```text
backend/app/services.py
backend/app/seed.py
backend/app/routes/quests.py
backend/app/models.py
```

### Tasks

```text
1. Read campaign_skill_quest_quotas.
2. For each active skill quota, generate daily quests.
3. Use preferred_activity_types to choose activity types.
4. Use daily_slot_code as specific slot, e.g. vocabulary_flashcard.
5. Keep unique key (campaign_id, quest_date, daily_slot_code).
6. Do not use skill_id as daily uniqueness key.
7. Preserve Quest Archive and existing lifecycle logic.
```

### Validation

```text
Vocabulary quota = 3 creates 3 vocabulary daily quests.
Reading quota = 1 creates 1 reading daily quest.
Listening quota = 1 creates 1 listening daily quest.
No duplicate daily_slot_code for same date.
Archive/backlog still works.
```

---

## Phase 9 — Backend Rank Boss Logic

### Goal

Implement XP-based rank promotion with boss exam.

### Files likely to edit

```text
backend/app/routes/rank_exams.py
backend/app/services.py
backend/app/schemas.py
backend/app/models.py
```

### APIs

```text
POST /api/rank-exams/start
GET  /api/rank-exams/{attempt_id}
POST /api/rank-exams/{attempt_id}/submit
```

### Tasks

```text
1. Detect XP-based rank eligibility.
2. Set pending_rank to next rank only.
3. Set promotion_status = boss_required.
4. Start exam from active pool.
5. Randomly select one active exam version.
6. Enforce max 2 attempts/day.
7. Set time limit 30 minutes.
8. Grade objective answers.
9. Pass if score >=80%.
10. On pass update confirmed_rank.
11. On fail keep confirmed_rank unchanged.
12. Insert skill_rank_history on pass.
```

### Out of scope

```text
Writing Boss
Speaking Boss
Subjective grading
AI grading
Audio recording
Manual review
```

### Validation

```text
XP threshold unlocks boss.
pending_rank = next rank only.
Start exam creates attempt.
Third attempt same day blocked.
Expired attempt rejected.
Score >=80 passes.
Score <80 fails.
Pass updates confirmed_rank.
Fail keeps confirmed_rank.
```

---

## Phase 10 — Backend Ownership Protection

### Goal

Make existing APIs account-aware and prevent cross-account access.

### Files likely to edit

```text
backend/app/routes/*.py
backend/app/services.py
backend/app/auth/dependencies.py
```

### Tasks

```text
1. Add get_current_account dependency.
2. Resolve current_player from account.
3. Resolve active/current campaign from player.
4. Filter campaign-scoped queries by authenticated campaign.
5. Protect quest, mission, boss, checkin, error log, mock test, vocabulary, and certificate endpoints.
6. Protect rank exam attempts by campaign ownership.
7. Adjust /api/dev/reset behavior for dev mode.
```

### Validation

```text
User A cannot read User B campaign.
User A cannot mutate User B quests.
User A cannot access User B rank exam attempt.
Dashboard works after login.
Quest completion and claim still work.
```

---

## Phase 11 — Frontend Auth Shell

### Goal

Add account registration/login and protected route behavior.

### Files likely to edit

```text
frontend/src/api/*
frontend/src/auth/*
frontend/src/pages/Register*
frontend/src/pages/Login*
frontend/src/routes/*
frontend/src/components/*
```

### Tasks

```text
1. Add AuthProvider.
2. Add /register page.
3. Add /login page.
4. Add protected route wrapper.
5. Add logout action.
6. Add /auth/me bootstrap.
7. Add API client token handling.
8. Redirect unauthenticated users to /login.
9. Redirect authenticated but onboarding incomplete users to /onboarding.
```

### Register fields

```text
email
password
confirm password
display_name
```

### Login fields

```text
email
password
```

### Validation

```text
npm run build
empty register validation works
password mismatch validation works
duplicate email error displays
login success redirects
wrong password shows error
logout works
protected routes redirect correctly
```

---

## Phase 12 — Frontend Onboarding UI

### Goal

Create mandatory onboarding flow.

### Files likely to edit

```text
frontend/src/pages/Onboarding*
frontend/src/components/onboarding/*
frontend/src/api/*
frontend/src/routes/*
```

### Screens

```text
1. Welcome Hunter
2. Manual Certificate Input
3. Campaign Confirmation
4. Start Campaign
```

### Do not ask user to configure

```text
current level
study duration
daily study time
vocabulary quota
reading quota
listening quota
skill quest quota
```

### Manual Certificate Screen

Fields:

```text
certificate_type default IELTS
overall_score
listening_score
reading_score
writing_score
speaking_score
```

Must support:

```text
Skip for now
```

Skip behavior:

```text
all skill confirmed_rank remains F
```

### Campaign Confirmation Display

```text
Campaign: IELTS 18-Month Hunter Roadmap
Target: IELTS 7.0–7.5
Duration: 18 months
Quest rhythm: fixed by campaign template
Skill quotas: fixed by roadmap
```

### Validation

```text
User cannot access dashboard before onboarding complete.
Manual score submission works.
Skip works.
Start Campaign activates campaign.
Dashboard loads after activation.
```

---

## Phase 13 — Frontend Suggestion Inbox Fix

### Goal

Fix Apply/Dismiss UI behavior.

### Files likely to edit

```text
frontend/src/components/SuggestionInbox*
frontend/src/api/*
frontend/src/components/SkillMatrix*
```

### Tasks

```text
1. Apply calls backend apply endpoint.
2. Dismiss calls backend dismiss endpoint.
3. After Apply, refresh skill state.
4. Skill Matrix shows updated confirmed_rank.
5. Suggestion card status updates or disappears.
```

### Validation

```text
Manual certificate creates suggestions.
Suggestion Inbox shows suggestions.
Click Apply.
Skill rank updates.
Click Dismiss.
Suggestion is dismissed.
```

---

## Phase 14 — Frontend Rank Boss UI

### Goal

Implement boss-style UI for Rank Boss Exam.

### Files likely to edit

```text
frontend/src/pages/RankBoss*
frontend/src/components/rank-boss/*
frontend/src/api/*
frontend/src/routes/*
```

### Screens

```text
Rank Boss Unlocked Modal
Rank Boss Exam Screen
Rank Boss Result Screen
```

### Unlock UI

Display:

```text
Skill name
Current confirmed rank
Target next rank
Pass requirement: 80%
Time limit: 30 minutes
Attempts today: 0/2, 1/2, 2/2
```

### Exam UI

```text
SYSTEM GATE OPENED
Rank Boss: Vocabulary F → E
Pass condition: 80%
Time limit: 30:00
Questions: current / total
Submit
```

### Result UI

If passed:

```text
Cleared
Score %
Rank confirmed
```

If failed:

```text
Failed
Score %
Attempts remaining
Try again tomorrow if 2/2
```

### Out of scope note

```text
Do not implement Writing/Speaking boss UI in this phase.
Add backlog task for future Writing/Speaking subjective boss design.
```

### Validation

```text
Start boss works.
Timer displays.
Answers submit.
Pass result displays.
Fail result displays.
Third attempt blocked.
```

---

## Phase 15 — Final Hardening, Tests, and Documentation

### Goal

Validate the whole Big Update and update docs.

### Files likely to edit

```text
TASKS.md
DECISIONS.md
docs/current/DATABASE_SCHEMA.md
docs/current/SCHEMA_SEMANTICS.md
docs/history/MIGRATION_HISTORY.md
docs/history/TEST_REPORT.md
docs/history/AGENT_NOTES.md
docs/history/changelogs.md
```

### Tasks

```text
1. Update DATABASE_SCHEMA.md snapshot.
2. Update SCHEMA_SEMANTICS.md with account-scoped and rank boss semantics.
3. Update migration history.
4. Update test report.
5. Update changelog.
6. Add unresolved backlog:
   - Writing/Speaking Rank Boss
   - file-based certificate upload
   - password reset email integration
   - OAuth/social login if needed
```

### Validation

```text
backend tests or smoke checks pass
frontend build passes
docker compose up passes
register/login/onboarding flow passes
manual certificate suggestion flow passes
daily quest generation passes
rank boss pass/fail flow passes
```

---

# 9. Agent Workflow Requirements

Every agent session must follow the project workflow.

## 9.1 Grounding Order

Read:

```text
AGENTS.md
README.md
TASKS.md
DECISIONS.md
docs/current/CONTEXT_INDEX.md
DATABASE_SCHEMA.md
SCHEMA_SEMANTICS.md
account_big_update_tasks_spec.md
```

Stop when:

```text
Task type is identified.
Files likely to be modified are identified.
Existing pattern to follow is identified.
Goal, constraints, and next steps are clear.
```

## 9.2 Task Contract

Before coding, write:

```text
Goal:
Completion Criteria:
In Scope:
Out of Scope:
Constraints:
Risks:
Files likely to modify:
Validation plan:
```

## 9.3 Planning Rule

Plan first if task:

```text
touches multiple files
changes backend behavior
changes schema or API contract
involves Alembic migration
requires validation sequence
```

## 9.4 Execution Rule

```text
Touch only necessary files.
Follow existing repo patterns.
No unrelated cleanup.
Every slice must be verifiable.
```

## 9.5 Verification Priority

```text
1. Syntax/type checks
2. Focused smoke checks
3. Tests for changed behavior
4. Review for medium/high risk changes
```

## 9.6 Documentation Updates

After meaningful changes update:

```text
TASKS.md
docs/history/TEST_REPORT.md
docs/history/AGENT_NOTES.md
docs/history/changelogs.md
DECISIONS.md or ADR
DATABASE_SCHEMA.md if schema changes
SCHEMA_SEMANTICS.md if field meaning changes
```

## 9.7 Session Wrap-up

End every session with:

```text
What changed:
What was validated:
What remains open:
What to read first next session:
```

---

# 10. Backlog Items Not for This Big Update Slice

Record but do not implement unless explicitly assigned:

```text
Writing Rank Boss
Speaking Rank Boss
Subjective/manual/AI-assisted boss grading
Audio recording for Speaking Boss
File upload certificate
Certificate OCR/parser
Email verification sending
Password reset email sending
OAuth/social login
Multiple active campaigns
Campaign switching UI
Admin account management
```

---

# 11. Recommended First Agent Task

Start with Phase 0 only.

Do not write backend code in the first session.

First prompt for agent:

```text
Read:
- AGENTS.md
- README.md
- TASKS.md
- DECISIONS.md
- docs/current/CONTEXT_INDEX.md
- DATABASE_SCHEMA.md
- SCHEMA_SEMANTICS.md
- account_big_update_tasks_spec.md

Then update docs with the Big Update decision:
- Account/Auth layer sits above players.
- 1 account = 1 player = 1 active campaign for MVP.
- players keep 1-to-many campaigns for future expansion.
- onboarding is mandatory.
- no internal placement test.
- certificate MVP is manual score input.
- certificate suggestions apply directly to confirmed_rank.
- XP-based rank promotion requires Rank Boss.
- Rank Boss is one rank at a time.
- max 2 Rank Boss attempts/day.
- 30-minute default Rank Boss time limit.
- Writing/Speaking Rank Boss out of scope and must be tracked as backlog.
- Daily quests are generated from skill quotas, not user-chosen quotas.
```
