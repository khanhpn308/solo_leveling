from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("email_normalized", name="uq_accounts_email_normalized"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    email_normalized: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="user", nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    player: Mapped["Player | None"] = relationship(back_populates="account", uselist=False)


class AccountSession(Base):
    __tablename__ = "account_sessions"
    __table_args__ = (
        UniqueConstraint("refresh_token_hash", name="uq_account_sessions_refresh_token_hash"),
        Index("ix_account_sessions_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoke_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    account: Mapped[Account] = relationship()


class AccountToken(Base):
    __tablename__ = "account_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_account_tokens_token_hash"),
        Index("ix_account_tokens_account_purpose", "account_id", "purpose"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    account: Mapped[Account] = relationship()


class AccountSecurityEvent(Base):
    __tablename__ = "account_security_events"
    __table_args__ = (
        Index("ix_account_security_events_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    email_attempted: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    account: Mapped[Account | None] = relationship()


class AccountPreference(Base):
    __tablename__ = "account_preferences"
    __table_args__ = (
        UniqueConstraint("account_id", name="uq_account_preferences_account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    locale: Mapped[str] = mapped_column(String(20), default="vi", nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Ho_Chi_Minh", nullable=False)
    theme: Mapped[str] = mapped_column(String(30), default="dark", nullable=False)
    accent_color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    daily_reminder_time: Mapped[Time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    account: Mapped[Account] = relationship()


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="IELTS Hunter")
    title: Mapped[str | None] = mapped_column(String(120), nullable=True, default=None)
    target: Mapped[str | None] = mapped_column(String(120), nullable=True, default=None)
    current_level: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    start_date: Mapped[date] = mapped_column(Date)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    display_name: Mapped[str] = mapped_column(String(120), default="IELTS Hunter")
    target_overall_band: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    target_listening_band: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    target_reading_band: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    target_writing_band: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    target_speaking_band: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    current_estimated_level: Mapped[str] = mapped_column(String(50), default="B1")
    strongest_skill: Mapped[str] = mapped_column(String(80), default="Listening")
    weakest_skill: Mapped[str] = mapped_column(String(80), default="Reading")
    study_days_per_week: Mapped[int] = mapped_column(Integer, default=4)
    session_minutes: Mapped[int] = mapped_column(Integer, default=120)
    daily_mini_study_minutes: Mapped[int] = mapped_column(Integer, default=20)
    player_xp: Mapped[int] = mapped_column(Integer, default=0)
    player_level: Mapped[int] = mapped_column(Integer, default=1)
    player_rank: Mapped[str] = mapped_column(String(2), default="F")
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    shield_count: Mapped[int] = mapped_column(Integer, default=1)
    shield_regen_progress: Mapped[int] = mapped_column(Integer, default=0)
    perfect_day_count: Mapped[int] = mapped_column(Integer, default=0)
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    active_campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True, index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, unique=True, index=True)

    active_campaign: Mapped["Campaign | None"] = relationship(
        "Campaign",
        foreign_keys=[active_campaign_id],
        post_update=True,
    )
    account: Mapped["Account | None"] = relationship(back_populates="player")
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        back_populates="player",
        foreign_keys="Campaign.player_id",
    )
    test_records: Mapped[list["TestRecord"]] = relationship(back_populates="player")
    badge_unlocks: Mapped[list["BadgeUnlock"]] = relationship(back_populates="player")
    learning_profile: Mapped["PlayerLearningProfile | None"] = relationship(back_populates="player", uselist=False, cascade="all, delete-orphan")
    certificate_records: Mapped[list["CertificateRecord"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    collocation_progresses: Mapped[list["PlayerCollocationProgress"]] = relationship(back_populates="player", cascade="all, delete-orphan")


class PlayerLearningProfile(Base):
    __tablename__ = "player_learning_profiles"
    __table_args__ = (
        UniqueConstraint("player_id", name="uq_player_learning_profiles_player_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    preferred_learning_style: Mapped[str] = mapped_column(String(50), default="mixed", nullable=False)
    dictionary_mode: Mapped[str] = mapped_column(String(50), default="bilingual_first", nullable=False)
    pronunciation_focus: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    collocation_focus: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    native_language: Mapped[str] = mapped_column(String(50), default="vi", nullable=False)
    interface_learning_language: Mapped[str] = mapped_column(String(50), default="mixed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    player: Mapped["Player"] = relationship(back_populates="learning_profile")


class CampaignTemplate(Base):
    __tablename__ = "campaign_templates"
    __table_args__ = (
        UniqueConstraint("code", name="uq_campaign_templates_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_type: Mapped[str] = mapped_column(String(30), default="IELTS", nullable=False)
    target_band: Mapped[str | None] = mapped_column(String(20), nullable=True)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    total_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    skill_quotas: Mapped[list["CampaignTemplateSkillQuota"]] = relationship(back_populates="campaign_template", cascade="all, delete-orphan")
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="campaign_template")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    campaign_template_id: Mapped[int | None] = mapped_column(ForeignKey("campaign_templates.id"), nullable=True, index=True)
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    setup_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    player: Mapped[Player] = relationship(
        "Player",
        back_populates="campaigns",
        foreign_keys=[player_id],
    )
    campaign_template: Mapped["CampaignTemplate | None"] = relationship("CampaignTemplate", back_populates="campaigns")
    settings: Mapped["CampaignSetting | None"] = relationship("CampaignSetting", back_populates="campaign", uselist=False, cascade="all, delete-orphan")
    skill_quest_quotas: Mapped[list["CampaignSkillQuestQuota"]] = relationship("CampaignSkillQuestQuota", back_populates="campaign", cascade="all, delete-orphan")
    vocabulary_settings: Mapped["VocabularySetting | None"] = relationship("VocabularySetting", back_populates="campaign", uselist=False, cascade="all, delete-orphan")

    roadmap_phases: Mapped[list["RoadmapPhase"]] = relationship(back_populates="campaign")
    study_plan_weeks: Mapped[list["StudyPlanWeek"]] = relationship(back_populates="campaign")
    study_plan_sessions: Mapped[list["StudyPlanSession"]] = relationship(back_populates="campaign")
    quests: Mapped[list["Quest"]] = relationship(back_populates="campaign")
    weekly_missions: Mapped[list["WeeklyMission"]] = relationship(back_populates="campaign")
    boss_battles: Mapped[list["BossBattle"]] = relationship(back_populates="campaign")
    error_logs: Mapped[list["ErrorLog"]] = relationship(back_populates="campaign")
    writing_entries: Mapped[list["WritingEntry"]] = relationship(back_populates="campaign")
    speaking_entries: Mapped[list["SpeakingEntry"]] = relationship(back_populates="campaign")
    mock_tests: Mapped[list["MockTest"]] = relationship(back_populates="campaign")
    skill_states: Mapped[list["CampaignSkillState"]] = relationship(back_populates="campaign")
    badge_unlocks: Mapped[list["BadgeUnlock"]] = relationship(back_populates="campaign")
    certificate_records: Mapped[list["CertificateRecord"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    rank_exam_attempts: Mapped[list["RankExamAttempt"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    collocation_links: Mapped[list["CampaignCollocationLink"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    collocation_progresses: Mapped[list["PlayerCollocationProgress"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class CampaignSetting(Base):
    __tablename__ = "campaign_settings"
    __table_args__ = (
        UniqueConstraint("campaign_id", name="uq_campaign_settings_campaign_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    target_certificate: Mapped[str] = mapped_column(String(30), default="IELTS", nullable=False)
    target_band: Mapped[str] = mapped_column(String(20), default="7.0-7.5", nullable=False)
    current_english_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_test_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    study_duration_months: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="settings")


class CampaignTemplateSkillQuota(Base):
    __tablename__ = "campaign_template_skill_quotas"
    __table_args__ = (
        UniqueConstraint("campaign_template_id", "skill_id", name="uq_template_skill_quota"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_template_id: Mapped[int] = mapped_column(ForeignKey("campaign_templates.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    daily_quota: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_quota: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_activity_types: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign_template: Mapped["CampaignTemplate"] = relationship(back_populates="skill_quotas")
    skill: Mapped["Skill"] = relationship()


class CampaignSkillQuestQuota(Base):
    __tablename__ = "campaign_skill_quest_quotas"
    __table_args__ = (
        UniqueConstraint("campaign_id", "skill_id", name="uq_campaign_skill_quest_quota"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    daily_quota: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_quota: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_activity_types: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="skill_quest_quotas")
    skill: Mapped["Skill"] = relationship()


class VocabularySetting(Base):
    __tablename__ = "vocabulary_settings"
    __table_args__ = (
        UniqueConstraint("campaign_id", name="uq_vocabulary_settings_campaign_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    daily_new_words_target: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    daily_flashcard_target: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    daily_collocation_target: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    daily_context_hunt_target: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    daily_error_review_target: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    vocab_review_mode: Mapped[str] = mapped_column(String(50), default="mixed", nullable=False)
    vocab_grouping_mode: Mapped[str] = mapped_column(String(50), default="topic", nullable=False)
    dictionary_mode: Mapped[str] = mapped_column(String(50), default="bilingual_first", nullable=False)
    example_sentence_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pronunciation_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    word_family_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    synonym_antonym_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    collocation_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    spaced_repetition_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="vocabulary_settings")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    icon: Mapped[str] = mapped_column(String(32), default="*")
    boss_gated: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)

    quests: Mapped[list["Quest"]] = relationship(back_populates="skill", foreign_keys="Quest.skill_id")
    templates: Mapped[list["QuestTemplate"]] = relationship(back_populates="primary_skill", foreign_keys="QuestTemplate.primary_skill_id")
    rank_suggestions: Mapped[list["SkillRankSuggestion"]] = relationship(back_populates="skill")
    rank_history: Mapped[list["SkillRankHistory"]] = relationship(back_populates="skill")
    weakness_suggestions: Mapped[list["WeaknessSuggestion"]] = relationship(back_populates="skill")
    campaign_states: Mapped[list["CampaignSkillState"]] = relationship(back_populates="skill")


class QuestTemplate(Base):
    __tablename__ = "quest_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    primary_skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    phase_id: Mapped[int | None] = mapped_column(ForeignKey("roadmap_phases.id"), nullable=True, index=True)
    material_id: Mapped[int | None] = mapped_column(ForeignKey("study_materials.id"), nullable=True, index=True)
    base_xp: Mapped[int] = mapped_column(Integer, default=10)
    difficulty: Mapped[str] = mapped_column(String(20), default="easy", index=True)
    difficulty_description: Mapped[str] = mapped_column(String(255), default="")
    quest_role: Mapped[str] = mapped_column(String(20), default="mini", index=True)
    resource_name: Mapped[str] = mapped_column(String(255), default="")
    resource_category: Mapped[str] = mapped_column(String(80), default="")
    resource_note: Mapped[str] = mapped_column(String(255), default="")
    allowed_phase_start: Mapped[int] = mapped_column(Integer, default=1)
    allowed_phase_end: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    # New fields for tracking and rewards
    quest_track_code: Mapped[str] = mapped_column(String(80), default="", index=True)
    activity_type: Mapped[str] = mapped_column(String(80), default="", index=True)
    reward_skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True, index=True)
    target_metric: Mapped[str] = mapped_column(String(80), default="")
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    completion_payload: Mapped[str] = mapped_column(Text, default="")

    primary_skill: Mapped[Skill] = relationship(back_populates="templates", foreign_keys=[primary_skill_id])
    phase: Mapped["RoadmapPhase | None"] = relationship(back_populates="quest_templates")
    material: Mapped["StudyMaterial | None"] = relationship(back_populates="quest_templates")
    quests: Mapped[list["Quest"]] = relationship(back_populates="template")
    reward_skill: Mapped[Skill | None] = relationship(foreign_keys=[reward_skill_id])


class Quest(Base):
    __tablename__ = "quests"
    __table_args__ = (
        UniqueConstraint(
            "campaign_id", "quest_date", "daily_slot_code",
            name="uq_quests_campaign_date_daily_slot"
        ),
        CheckConstraint(
            "(CASE WHEN error_log_id IS NULL THEN 1 ELSE 0 END + "
            "CASE WHEN writing_entry_id IS NULL THEN 1 ELSE 0 END + "
            "CASE WHEN speaking_entry_id IS NULL THEN 1 ELSE 0 END + "
            "CASE WHEN mock_test_id IS NULL THEN 1 ELSE 0 END) >= 3",
            name="ck_quests_only_one_tracker"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quest_date: Mapped[date] = mapped_column(Date, index=True)
    week_no: Mapped[int] = mapped_column(Integer, index=True)
    stage: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(200))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    source: Mapped[str] = mapped_column(String(255))
    details: Mapped[str] = mapped_column(Text)
    xp: Mapped[int] = mapped_column(Integer, default=10)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    session_type: Mapped[str] = mapped_column(String(80), default="Daily Quest")
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    phase_id: Mapped[int | None] = mapped_column(ForeignKey("roadmap_phases.id"), nullable=True, index=True)
    study_plan_week_id: Mapped[int | None] = mapped_column(ForeignKey("study_plan_weeks.id"), nullable=True, index=True)
    study_plan_session_id: Mapped[int | None] = mapped_column(ForeignKey("study_plan_sessions.id"), nullable=True, index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("quest_templates.id"), nullable=True, index=True)
    material_id: Mapped[int | None] = mapped_column(ForeignKey("study_materials.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    quest_role: Mapped[str] = mapped_column(String(20), default="mini", index=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="easy", index=True)
    base_xp: Mapped[int] = mapped_column(Integer, default=10)
    earned_xp: Mapped[int] = mapped_column(Integer, default=0)
    reward_claimed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    reward_claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    completion_note: Mapped[str] = mapped_column(String(255), default="")
    raw_score: Mapped[str] = mapped_column(String(120), default="")
    daily_slot_code: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    error_log_id: Mapped[int | None] = mapped_column(ForeignKey("error_logs.id"), nullable=True, index=True)
    writing_entry_id: Mapped[int | None] = mapped_column(ForeignKey("writing_entries.id"), nullable=True, index=True)
    speaking_entry_id: Mapped[int | None] = mapped_column(ForeignKey("speaking_entries.id"), nullable=True, index=True)
    mock_test_id: Mapped[int | None] = mapped_column(ForeignKey("mock_tests.id"), nullable=True, index=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # New campaign/quest tracking and reward fields
    quest_track_code: Mapped[str] = mapped_column(String(80), default="", index=True)
    activity_type: Mapped[str] = mapped_column(String(80), default="", index=True)
    reward_skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True, index=True)
    target_metric: Mapped[str] = mapped_column(String(80), default="")
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    completion_payload: Mapped[str] = mapped_column(Text, default="")

    @property
    def tracker_type(self) -> str:
        if self.error_log_id is not None:
            return "error_log"
        if self.writing_entry_id is not None:
            return "writing_entry"
        if self.speaking_entry_id is not None:
            return "speaking_entry"
        if self.mock_test_id is not None:
            return "mock_test"
        return ""

    @property
    def tracker_entry_id(self) -> int | None:
        if self.error_log_id is not None:
            return self.error_log_id
        if self.writing_entry_id is not None:
            return self.writing_entry_id
        if self.speaking_entry_id is not None:
            return self.speaking_entry_id
        if self.mock_test_id is not None:
            return self.mock_test_id
        return None

    skill: Mapped[Skill] = relationship(back_populates="quests", foreign_keys=[skill_id])
    campaign: Mapped[Campaign] = relationship(back_populates="quests")
    phase: Mapped["RoadmapPhase | None"] = relationship(back_populates="quests")
    study_plan_week: Mapped["StudyPlanWeek | None"] = relationship(back_populates="quests")
    study_plan_session: Mapped["StudyPlanSession | None"] = relationship(back_populates="quest")
    template: Mapped[QuestTemplate | None] = relationship(back_populates="quests")
    material: Mapped["StudyMaterial | None"] = relationship(back_populates="quests")
    reward_skill: Mapped[Skill | None] = relationship(foreign_keys=[reward_skill_id])




class CheckIn(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("campaign_id", "checkin_date", name="uq_checkins_campaign_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    checkin_date: Mapped[date] = mapped_column(Date, index=True)
    mood: Mapped[int] = mapped_column(Integer, default=3)
    energy: Mapped[int] = mapped_column(Integer, default=3)
    focus: Mapped[int] = mapped_column(Integer, default=3)
    note: Mapped[str] = mapped_column(Text, default="")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    icon: Mapped[str] = mapped_column(String(32), default="badge")
    description: Mapped[str] = mapped_column(String(255))
    unlocks: Mapped[list["BadgeUnlock"]] = relationship(back_populates="badge")


class CampaignSkillState(Base):
    __tablename__ = "campaign_skill_states"
    __table_args__ = (
        UniqueConstraint("campaign_id", "skill_id", name="uq_campaign_skill_states_campaign_skill"),
        Index("ix_campaign_skill_states_campaign_confirmed_rank", "campaign_id", "confirmed_rank"),
        Index("ix_campaign_skill_states_skill_id", "skill_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    xp: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[str] = mapped_column(String(2), default="F")
    confirmed_rank: Mapped[str] = mapped_column(String(2), default="F")
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced: Mapped[date | None] = mapped_column(Date, nullable=True)
    weak_point: Mapped[str] = mapped_column(String(255), default="")
    user_weakness_note: Mapped[str] = mapped_column(Text, default="")
    last_system_suggestion_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pending_rank: Mapped[str | None] = mapped_column(String(5), nullable=True)
    promotion_status: Mapped[str] = mapped_column(String(30), default="none", nullable=False)
    promotion_unlocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_rank_exam_attempt_id: Mapped[int | None] = mapped_column(ForeignKey("rank_exam_attempts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign: Mapped[Campaign] = relationship(back_populates="skill_states")
    skill: Mapped[Skill] = relationship(back_populates="campaign_states")
    last_rank_exam_attempt: Mapped["RankExamAttempt | None"] = relationship()


class SkillXpTransaction(Base):
    __tablename__ = "skill_xp_transactions"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_skill_xp_transactions_idempotency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    transaction_type: Mapped[str] = mapped_column(String(50), default="")
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    campaign: Mapped[Campaign] = relationship()
    skill: Mapped[Skill] = relationship()


class PlayerXpTransaction(Base):
    __tablename__ = "player_xp_transactions"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_player_xp_transactions_idempotency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    transaction_type: Mapped[str] = mapped_column(String(50), default="")
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # relationships
    campaign: Mapped[Campaign] = relationship()
    player: Mapped[Player] = relationship()


class BadgeUnlock(Base):
    __tablename__ = "badge_unlocks"
    __table_args__ = (
        UniqueConstraint("campaign_id", "badge_id", name="uq_badge_unlocks_campaign_badge"),
        Index("ix_badge_unlocks_player_id", "player_id"),
        Index("ix_badge_unlocks_badge_id", "badge_id"),
        Index("ix_badge_unlocks_source_boss_battle_id", "source_boss_battle_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"))
    source_boss_battle_id: Mapped[int | None] = mapped_column(ForeignKey("boss_battles.id"), nullable=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    player: Mapped[Player] = relationship(back_populates="badge_unlocks")
    campaign: Mapped[Campaign] = relationship(back_populates="badge_unlocks")
    badge: Mapped[Badge] = relationship(back_populates="unlocks")
    source_boss_battle: Mapped["BossBattle | None"] = relationship(back_populates="badge_unlocks")


class WeeklyMission(Base):
    __tablename__ = "weekly_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    week_end: Mapped[date] = mapped_column(Date, index=True)
    phase: Mapped[str] = mapped_column(String(80), index=True)
    pattern_code: Mapped[str] = mapped_column(String(80), default="", index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reward_claimed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    reward_claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # New fields for weekly mission skill routing (added in migration 20260607_11)
    primary_skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True, index=True)
    mission_track_code: Mapped[str] = mapped_column(String(80), default="", index=True)
    activity_type: Mapped[str] = mapped_column(String(80), default="", index=True)
    reward_skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True, index=True)
    boss_scope: Mapped[str] = mapped_column(String(50), default="player")

    campaign: Mapped[Campaign] = relationship(back_populates="weekly_missions")
    items: Mapped[list["WeeklyMissionItem"]] = relationship(back_populates="weekly_mission")
    primary_skill: Mapped[Skill | None] = relationship(foreign_keys=[primary_skill_id])
    reward_skill: Mapped[Skill | None] = relationship(foreign_keys=[reward_skill_id])




class WeeklyMissionItem(Base):
    __tablename__ = "weekly_mission_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    weekly_mission_id: Mapped[int] = mapped_column(ForeignKey("weekly_missions.id"), index=True)
    description: Mapped[str] = mapped_column(String(255))
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    weekly_mission: Mapped[WeeklyMission] = relationship(back_populates="items")


class BossBattle(Base):
    __tablename__ = "boss_battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stage: Mapped[str] = mapped_column(String(80), index=True)
    battle_date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(160))
    source: Mapped[str] = mapped_column(String(255))
    goal: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="Locked")
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    month_index: Mapped[int] = mapped_column(Integer, default=1, index=True)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0)
    badge_id: Mapped[int | None] = mapped_column(ForeignKey("badges.id"), nullable=True)
    result_status: Mapped[str] = mapped_column(String(20), default="locked", index=True)
    result_note: Mapped[str] = mapped_column(String(255), default="")
    practice_suggestion: Mapped[str] = mapped_column(String(255), default="")
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    boss_scope: Mapped[str] = mapped_column(String(50), default="player")
    reward_skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    reward_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    reward_claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaign: Mapped[Campaign | None] = relationship(back_populates="boss_battles")
    badge_unlocks: Mapped[list["BadgeUnlock"]] = relationship(back_populates="source_boss_battle")
    reward_skill: Mapped[Skill | None] = relationship(foreign_keys=[reward_skill_id])


class TestRecord(Base):
    __tablename__ = "test_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    test_type: Mapped[str] = mapped_column(String(20), index=True)
    test_date: Mapped[date] = mapped_column(Date, index=True)
    overall_score: Mapped[str] = mapped_column(String(50), default="")
    listening_score: Mapped[str] = mapped_column(String(50), default="")
    reading_score: Mapped[str] = mapped_column(String(50), default="")
    writing_score: Mapped[str] = mapped_column(String(50), default="")
    speaking_score: Mapped[str] = mapped_column(String(50), default="")
    cefr_level: Mapped[str] = mapped_column(String(20), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    player: Mapped[Player] = relationship(back_populates="test_records")
    rank_suggestions: Mapped[list["SkillRankSuggestion"]] = relationship(back_populates="source_test_record")
    rank_history: Mapped[list["SkillRankHistory"]] = relationship(back_populates="source_test_record")


class SkillRankSuggestion(Base):
    __tablename__ = "skill_rank_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    source_test_record_id: Mapped[int | None] = mapped_column(ForeignKey("test_records.id"), nullable=True, index=True)
    source_certificate_record_id: Mapped[int | None] = mapped_column(ForeignKey("certificate_records.id"), nullable=True, index=True)
    current_rank: Mapped[str] = mapped_column(String(2), default="F")
    suggested_rank: Mapped[str] = mapped_column(String(2), default="F")
    direction: Mapped[str] = mapped_column(String(10), default="same")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    skill: Mapped[Skill] = relationship(back_populates="rank_suggestions")
    source_test_record: Mapped[TestRecord | None] = relationship(back_populates="rank_suggestions")
    source_certificate_record: Mapped["CertificateRecord | None"] = relationship(back_populates="rank_suggestions")


class SkillRankHistory(Base):
    __tablename__ = "skill_rank_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    old_rank: Mapped[str] = mapped_column(String(2), default="F")
    new_rank: Mapped[str] = mapped_column(String(2), default="F")
    source_test_record_id: Mapped[int | None] = mapped_column(ForeignKey("test_records.id"), nullable=True, index=True)
    source_certificate_record_id: Mapped[int | None] = mapped_column(ForeignKey("certificate_records.id"), nullable=True, index=True)
    change_reason: Mapped[str] = mapped_column(String(255), default="")
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    skill: Mapped[Skill] = relationship(back_populates="rank_history")
    source_test_record: Mapped[TestRecord | None] = relationship(back_populates="rank_history")
    source_certificate_record: Mapped["CertificateRecord | None"] = relationship(back_populates="rank_history")


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    source: Mapped[str] = mapped_column(String(255), default="")
    error_description: Mapped[str] = mapped_column(Text)
    correction: Mapped[str] = mapped_column(Text, default="")
    cause: Mapped[str] = mapped_column(Text, default="")
    prevention: Mapped[str] = mapped_column(Text, default="")
    error_tag: Mapped[str] = mapped_column(String(80), default="", index=True)
    logged_date: Mapped[date] = mapped_column(Date, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="error_logs")


class WritingEntry(Base):
    __tablename__ = "writing_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(80), default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    draft_text: Mapped[str] = mapped_column(Text, default="")
    self_score: Mapped[str] = mapped_column(String(50), default="")
    estimated_band: Mapped[str] = mapped_column(String(20), default="")
    feedback_note: Mapped[str] = mapped_column(Text, default="")
    revised_text: Mapped[str] = mapped_column(Text, default="")
    entry_date: Mapped[date] = mapped_column(Date, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="writing_entries")


class SpeakingEntry(Base):
    __tablename__ = "speaking_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    part: Mapped[str] = mapped_column(String(40), default="")
    topic: Mapped[str] = mapped_column(String(255), default="")
    cue_or_question: Mapped[str] = mapped_column(Text, default="")
    self_score: Mapped[str] = mapped_column(String(50), default="")
    self_note: Mapped[str] = mapped_column(Text, default="")
    transcript_summary: Mapped[str] = mapped_column(Text, default="")
    entry_date: Mapped[date] = mapped_column(Date, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="speaking_entries")


class MockTest(Base):
    __tablename__ = "mock_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    test_type: Mapped[str] = mapped_column(String(80), default="", index=True)
    scope: Mapped[str] = mapped_column(String(20), default="full", index=True)
    source: Mapped[str] = mapped_column(String(255), default="")
    raw_score: Mapped[str] = mapped_column(String(50), default="")
    estimated_band: Mapped[str] = mapped_column(String(20), default="")
    estimated_band_override: Mapped[str] = mapped_column(String(20), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    test_date: Mapped[date] = mapped_column(Date, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="mock_tests")


class RoadmapPhase(Base):
    __tablename__ = "roadmap_phases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    phase_order: Mapped[int] = mapped_column(Integer, index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(120))
    month_start: Mapped[int] = mapped_column(Integer)
    month_end: Mapped[int] = mapped_column(Integer)
    week_start: Mapped[int] = mapped_column(Integer, index=True)
    week_end: Mapped[int] = mapped_column(Integer, index=True)
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    objective: Mapped[str] = mapped_column(Text, default="")
    focus_skills: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="roadmap_phases")
    phase_materials: Mapped[list["PhaseMaterial"]] = relationship(back_populates="phase")
    study_plan_weeks: Mapped[list["StudyPlanWeek"]] = relationship(back_populates="phase")
    study_plan_sessions: Mapped[list["StudyPlanSession"]] = relationship(back_populates="phase")
    quest_templates: Mapped[list["QuestTemplate"]] = relationship(back_populates="phase")
    quests: Mapped[list["Quest"]] = relationship(back_populates="phase")


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), default="", index=True)
    format: Mapped[str] = mapped_column(String(40), default="book")
    file_path: Mapped[str] = mapped_column(String(500), default="")
    skill_tags: Mapped[str] = mapped_column(String(255), default="")
    recommended_phase_start: Mapped[int] = mapped_column(Integer, default=1)
    recommended_phase_end: Mapped[int] = mapped_column(Integer, default=5)
    notes: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    phase_links: Mapped[list["PhaseMaterial"]] = relationship(back_populates="material")
    quest_templates: Mapped[list["QuestTemplate"]] = relationship(back_populates="material")
    quests: Mapped[list["Quest"]] = relationship(back_populates="material")


class PhaseMaterial(Base):
    __tablename__ = "phase_materials"
    __table_args__ = (UniqueConstraint("phase_id", "material_id", name="uq_phase_material"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("roadmap_phases.id"), index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("study_materials.id"), index=True)
    usage_purpose: Mapped[str] = mapped_column(String(120), default="")
    usage_frequency: Mapped[str] = mapped_column(String(80), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    display_order: Mapped[int] = mapped_column(Integer, default=1)

    phase: Mapped[RoadmapPhase] = relationship(back_populates="phase_materials")
    material: Mapped[StudyMaterial] = relationship(back_populates="phase_links")


class StudyPlanWeek(Base):
    __tablename__ = "study_plan_weeks"
    __table_args__ = (UniqueConstraint("campaign_id", "week_no", name="uq_study_plan_week_campaign_week"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("roadmap_phases.id"), index=True)
    week_no: Mapped[int] = mapped_column(Integer, index=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    week_end: Mapped[date] = mapped_column(Date, index=True)
    weekly_focus: Mapped[str] = mapped_column(Text, default="")
    weekly_output: Mapped[str] = mapped_column(Text, default="")
    material_summary: Mapped[str] = mapped_column(Text, default="")
    mini_task: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="study_plan_weeks")
    phase: Mapped[RoadmapPhase] = relationship(back_populates="study_plan_weeks")
    sessions: Mapped[list["StudyPlanSession"]] = relationship(back_populates="study_plan_week")
    quests: Mapped[list["Quest"]] = relationship(back_populates="study_plan_week")


class StudyPlanSession(Base):
    __tablename__ = "study_plan_sessions"
    __table_args__ = (UniqueConstraint("study_plan_week_id", "session_no", name="uq_study_plan_session_week_no"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("roadmap_phases.id"), index=True)
    study_plan_week_id: Mapped[int] = mapped_column(ForeignKey("study_plan_weeks.id"), index=True)
    week_no: Mapped[int] = mapped_column(Integer, index=True)
    session_no: Mapped[int] = mapped_column(Integer, index=True)
    study_date: Mapped[date] = mapped_column(Date, index=True)
    weekday_label: Mapped[str] = mapped_column(String(40), default="")
    session_label: Mapped[str] = mapped_column(String(40), default="")
    skill_summary: Mapped[str] = mapped_column(String(255), default="")
    task_detail: Mapped[str] = mapped_column(Text, default="")
    material_summary: Mapped[str] = mapped_column(Text, default="")
    deliverable: Mapped[str] = mapped_column(Text, default="")
    status_text: Mapped[str] = mapped_column(String(40), default="")
    note_text: Mapped[str] = mapped_column(Text, default="")
    mini_task: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    campaign: Mapped[Campaign] = relationship(back_populates="study_plan_sessions")
    phase: Mapped[RoadmapPhase] = relationship(back_populates="study_plan_sessions")
    study_plan_week: Mapped[StudyPlanWeek] = relationship(back_populates="sessions")
    quest: Mapped["Quest | None"] = relationship(back_populates="study_plan_session")


class WeaknessSuggestion(Base):
    __tablename__ = "weakness_suggestions"
    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN source_test_record_id IS NULL THEN 1 ELSE 0 END + "
            "CASE WHEN source_mock_test_id IS NULL THEN 1 ELSE 0 END + "
            "CASE WHEN source_error_log_id IS NULL THEN 1 ELSE 0 END + "
            "CASE WHEN source_quest_id IS NULL THEN 1 ELSE 0 END) >= 3",
            name="ck_weakness_suggestions_only_one_source"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), index=True)
    campaign_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    source_test_record_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("test_records.id"), nullable=True, index=True)
    source_mock_test_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("mock_tests.id"), nullable=True, index=True)
    source_error_log_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("error_logs.id"), nullable=True, index=True)
    source_quest_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("quests.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    @property
    def source_type(self) -> str:
        if self.source_test_record_id is not None:
            return "test_record"
        if self.source_mock_test_id is not None:
            return "mock_test"
        if self.source_error_log_id is not None:
            return "error_log"
        if self.source_quest_id is not None:
            return "quest_pattern"
        return "last_practiced"

    @property
    def source_ref_id(self) -> int | None:
        if self.source_test_record_id is not None:
            return self.source_test_record_id
        if self.source_mock_test_id is not None:
            return self.source_mock_test_id
        if self.source_error_log_id is not None:
            return self.source_error_log_id
        if self.source_quest_id is not None:
            return self.source_quest_id
        return None

    skill: Mapped[Skill] = relationship(back_populates="weakness_suggestions")


class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    word: Mapped[str] = mapped_column(String(255), index=True)
    normalized_word: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    part_of_speech: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cefr_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ielts_topic: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    meaning_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    meaning_vi: Mapped[str | None] = mapped_column(Text, nullable=True)
    register_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grammar_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    pronunciation_ipa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    word_stress: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mastery_rank: Mapped[str] = mapped_column(String(5), default="F", index=True)
    mastery_score: Mapped[int] = mapped_column(Integer, default=0)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    examples: Mapped[list["VocabularyExample"]] = relationship(back_populates="vocabulary_item", cascade="all, delete-orphan")
    flashcards: Mapped[list["Flashcard"]] = relationship(back_populates="vocabulary_item", cascade="all, delete-orphan")


class VocabularyExample(Base):
    __tablename__ = "vocabulary_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vocabulary_item_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_items.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    example_sentence: Mapped[str] = mapped_column(Text)
    example_meaning: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_corrected: Mapped[bool] = mapped_column(Boolean, default=False)
    correction_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vocabulary_item: Mapped[VocabularyItem] = relationship(back_populates="examples")



class CollocationLevel(Base):
    __tablename__ = "collocation_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    difficulty_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    icon: Mapped[str] = mapped_column(String(10), nullable=False, default="📕")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    collections: Mapped[list["CollocationCollection"]] = relationship(back_populates="coll_level")


class CollocationCollection(Base):
    __tablename__ = "collocation_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_book: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    level_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("collocation_levels.id", name="fk_colcol_level_id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    coll_level: Mapped["CollocationLevel | None"] = relationship(back_populates="collections")
    sections: Mapped[list["CollocationSection"]] = relationship(back_populates="collection", cascade="all, delete-orphan")
    campaign_links: Mapped[list["CampaignCollocationLink"]] = relationship(back_populates="collection", cascade="all, delete-orphan")


class CollocationSection(Base):
    __tablename__ = "collocation_sections"
    __table_args__ = (
        Index("ix_collocation_sections_collection_order", "collection_id", "section_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collocation_collections.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    collection: Mapped[CollocationCollection] = relationship(back_populates="sections")
    topics: Mapped[list["CollocationTopic"]] = relationship(back_populates="section", cascade="all, delete-orphan")


class CollocationTopic(Base):
    __tablename__ = "collocation_topics"
    __table_args__ = (
        Index("ix_collocation_topics_section_order", "section_id", "topic_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("collocation_sections.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topic_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    topic_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    section: Mapped[CollocationSection] = relationship(back_populates="topics")
    items: Mapped[list["CollocationItem"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class CollocationItem(Base):
    __tablename__ = "collocation_items"
    __table_args__ = (
        Index("ix_collocation_items_topic_order", "topic_id", "item_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("collocation_topics.id"), nullable=False)
    collocation: Mapped[str] = mapped_column(String(255), nullable=False)
    pronunciation_us: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meaning_vi: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_vi: Mapped[str | None] = mapped_column(Text, nullable=True)
    collocation_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    item_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    topic: Mapped[CollocationTopic] = relationship(back_populates="items")
    progresses: Mapped[list["PlayerCollocationProgress"]] = relationship(back_populates="collocation_item", cascade="all, delete-orphan")
    flashcards: Mapped[list["CollocationFlashcard"]] = relationship(back_populates="collocation_item", cascade="all, delete-orphan")


class CampaignCollocationLink(Base):
    __tablename__ = "campaign_collocation_links"
    __table_args__ = (
        UniqueConstraint("campaign_id", "collection_id", name="uq_campaign_colcol_link"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collocation_collections.id"), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    campaign: Mapped[Campaign] = relationship(back_populates="collocation_links")
    collection: Mapped[CollocationCollection] = relationship(back_populates="campaign_links")


class PlayerCollocationProgress(Base):
    __tablename__ = "player_collocation_progress"
    __table_args__ = (
        UniqueConstraint("player_id", "campaign_id", "collocation_item_id", name="uq_player_camp_col_item"),
        Index("ix_pcp_campaign_status", "campaign_id", "status"),
        Index("ix_pcp_player_campaign", "player_id", "campaign_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    collocation_item_id: Mapped[int] = mapped_column(ForeignKey("collocation_items.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="new", nullable=False)
    practice_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    player: Mapped[Player] = relationship(back_populates="collocation_progresses")
    campaign: Mapped[Campaign] = relationship(back_populates="collocation_progresses")
    collocation_item: Mapped[CollocationItem] = relationship(back_populates="progresses")



class VocabularyRelation(Base):
    __tablename__ = "vocabulary_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    source_word_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_items.id"), index=True)
    target_word_id: Mapped[int | None] = mapped_column(ForeignKey("vocabulary_items.id"), nullable=True, index=True)
    target_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    vocabulary_item_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_items.id"), index=True)
    card_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    front_text: Mapped[str] = mapped_column(Text)
    back_text: Mapped[str] = mapped_column(Text)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vocabulary_item: Mapped[VocabularyItem] = relationship(back_populates="flashcards")
    spaced_repetition_states: Mapped[list["SpacedRepetitionState"]] = relationship(back_populates="flashcard", cascade="all, delete-orphan")


class SpacedRepetitionState(Base):
    __tablename__ = "spaced_repetition_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    flashcard_id: Mapped[int] = mapped_column(ForeignKey("flashcards.id"), index=True)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetition_count: Mapped[int] = mapped_column(Integer, default=0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    flashcard: Mapped[Flashcard] = relationship(back_populates="spaced_repetition_states")


class VocabularyTopic(Base):
    __tablename__ = "vocabulary_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    topic_name: Mapped[str] = mapped_column(String(255))
    parent_topic_id: Mapped[int | None] = mapped_column(ForeignKey("vocabulary_topics.id"), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    nodes: Mapped[list["VocabularyNode"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class VocabularyNode(Base):
    __tablename__ = "vocabulary_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_topics.id"), index=True)
    vocabulary_item_id: Mapped[int | None] = mapped_column(ForeignKey("vocabulary_items.id"), nullable=True, index=True)
    node_label: Mapped[str] = mapped_column(String(255))
    node_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="locked")
    x_position: Mapped[float | None] = mapped_column(Float, nullable=True)
    y_position: Mapped[float | None] = mapped_column(Float, nullable=True)
    unlock_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    topic: Mapped[VocabularyTopic] = relationship(back_populates="nodes")


class VocabularyEdge(Base):
    __tablename__ = "vocabulary_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_nodes.id"), index=True)
    target_node_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_nodes.id"), index=True)
    edge_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    strength: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VocabularyError(Base):
    __tablename__ = "vocabulary_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    vocabulary_item_id: Mapped[int | None] = mapped_column(ForeignKey("vocabulary_items.id"), nullable=True, index=True)
    error_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wrong_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    defeated_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CertificateRecord(Base):
    __tablename__ = "certificate_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    certificate_type: Mapped[str] = mapped_column(String(30), default="IELTS", nullable=False)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    listening_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reading_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    writing_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    speaking_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_method: Mapped[str] = mapped_column(String(30), default="manual", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="submitted", nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    player: Mapped["Player"] = relationship(back_populates="certificate_records")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="certificate_records")
    rank_suggestions: Mapped[list["SkillRankSuggestion"]] = relationship(back_populates="source_certificate_record")
    rank_history: Mapped[list["SkillRankHistory"]] = relationship(back_populates="source_certificate_record")


class RankExamPool(Base):
    __tablename__ = "rank_exam_pools"
    __table_args__ = (
        Index("ix_rank_exam_pools_skill_rank", "skill_id", "from_rank", "to_rank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    from_rank: Mapped[str] = mapped_column(String(5), nullable=False)
    to_rank: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pass_percent: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    default_time_limit_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    max_attempts_per_day: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    xp_threshold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    skill: Mapped["Skill"] = relationship()
    versions: Mapped[list["RankExamVersion"]] = relationship(back_populates="pool", cascade="all, delete-orphan")


class RankExamVersion(Base):
    __tablename__ = "rank_exam_versions"
    __table_args__ = (
        Index("ix_rank_exam_versions_pool_id", "pool_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pool_id: Mapped[int] = mapped_column(ForeignKey("rank_exam_pools.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    version_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(30), default="normal", nullable=False)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    pool: Mapped["RankExamPool"] = relationship(back_populates="versions")
    questions: Mapped[list["RankExamQuestion"]] = relationship(back_populates="exam_version", cascade="all, delete-orphan")


class RankExamQuestion(Base):
    __tablename__ = "rank_exam_questions"
    __table_args__ = (
        Index("ix_rank_exam_questions_exam_version_id", "exam_version_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exam_version_id: Mapped[int] = mapped_column(ForeignKey("rank_exam_versions.id"), nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    options_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    correct_answer_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    exam_version: Mapped["RankExamVersion"] = relationship(back_populates="questions")


class RankExamAttempt(Base):
    __tablename__ = "rank_exam_attempts"
    __table_args__ = (
        Index("ix_rank_exam_attempts_campaign_skill", "campaign_id", "skill_id"),
        Index("ix_rank_exam_attempts_status", "status"),
        Index("ix_rank_exam_attempts_started_at", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    from_rank: Mapped[str] = mapped_column(String(5), nullable=False)
    to_rank: Mapped[str] = mapped_column(String(5), nullable=False)
    pool_id: Mapped[int] = mapped_column(ForeignKey("rank_exam_pools.id"), nullable=False)
    exam_version_id: Mapped[int] = mapped_column(ForeignKey("rank_exam_versions.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="in_progress", nullable=False)
    score_points: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False)
    score_percent: Mapped[float | None] = mapped_column(Float, default=0.00, nullable=True)
    pass_percent: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="rank_exam_attempts")
    skill: Mapped["Skill"] = relationship()
    pool: Mapped["RankExamPool"] = relationship()
    exam_version: Mapped["RankExamVersion"] = relationship()
    answers: Mapped[list["RankExamAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class RankExamAnswer(Base):
    __tablename__ = "rank_exam_answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_rank_exam_answer_attempt_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("rank_exam_attempts.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("rank_exam_questions.id"), nullable=False)
    answer_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    attempt: Mapped["RankExamAttempt"] = relationship(back_populates="answers")
    question: Mapped["RankExamQuestion"] = relationship()


class RankXpThreshold(Base):
    __tablename__ = "rank_xp_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rank_name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    min_xp: Mapped[int] = mapped_column(Integer, nullable=False)
    first_level: Mapped[int] = mapped_column(Integer, nullable=False)


class QuestXpPolicy(Base):
    __tablename__ = "quest_xp_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    activity_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    skill_code: Mapped[str] = mapped_column(String(50), nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)


class WeeklyMissionXpPolicy(Base):
    __tablename__ = "weekly_mission_xp_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mission_type: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    reward_target_skill: Mapped[str] = mapped_column(String(50), nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)


class MainQuestXpPolicy(Base):
    __tablename__ = "main_quest_xp_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tier_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)


class CollocationFlashcard(Base):
    __tablename__ = "collocation_flashcards"
    __table_args__ = (
        UniqueConstraint("player_id", "campaign_id", "collocation_item_id", name="uq_collocation_flashcard"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    collocation_item_id: Mapped[int] = mapped_column(ForeignKey("collocation_items.id"), nullable=False, index=True)
    familiarity: Mapped[str] = mapped_column(String(10), nullable=False, default="again")
    familiarity_set_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    player: Mapped["Player"] = relationship(foreign_keys=[player_id])
    campaign: Mapped["Campaign"] = relationship(foreign_keys=[campaign_id])
    collocation_item: Mapped["CollocationItem"] = relationship(back_populates="flashcards")


# ── Vocabulary Library (5-layer: Level → Topic → Unit → Section → Item) ──

class VocabLevel(Base):
    __tablename__ = "vocab_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    difficulty_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    icon: Mapped[str] = mapped_column(String(10), nullable=False, default="📗")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    topics: Mapped[list["VocabTopic"]] = relationship(back_populates="level", cascade="all, delete-orphan")
    campaign_links: Mapped[list["CampaignVocabLink"]] = relationship(back_populates="level", cascade="all, delete-orphan")


class VocabTopic(Base):
    __tablename__ = "vocab_topics"
    __table_args__ = (
        Index("ix_vocab_topics_level_order", "level_id", "topic_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("vocab_levels.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topic_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    level: Mapped[VocabLevel] = relationship(back_populates="topics")
    units: Mapped[list["VocabUnit"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class VocabUnit(Base):
    __tablename__ = "vocab_units"
    __table_args__ = (
        Index("ix_vocab_units_topic_order", "topic_id", "unit_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("vocab_topics.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    topic: Mapped[VocabTopic] = relationship(back_populates="units")
    sections: Mapped[list["VocabSection"]] = relationship(back_populates="unit", cascade="all, delete-orphan")


class VocabSection(Base):
    __tablename__ = "vocab_sections"
    __table_args__ = (
        Index("ix_vocab_sections_unit_order", "unit_id", "section_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("vocab_units.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    section_letter: Mapped[str | None] = mapped_column(String(5), nullable=True)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    unit: Mapped[VocabUnit] = relationship(back_populates="sections")
    items: Mapped[list["VocabLibraryItem"]] = relationship(back_populates="section", cascade="all, delete-orphan")


class VocabLibraryItem(Base):
    __tablename__ = "vocab_library_items"
    __table_args__ = (
        Index("ix_vocab_library_items_section_order", "section_id", "item_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("vocab_sections.id"), nullable=False, index=True)
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    part_of_speech: Mapped[str | None] = mapped_column(String(80), nullable=True)
    pronunciation_us: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meaning_vi: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_vi: Mapped[str | None] = mapped_column(Text, nullable=True)
    item_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    section: Mapped[VocabSection] = relationship(back_populates="items")
    flashcards: Mapped[list["VocabLibraryFlashcard"]] = relationship(back_populates="item", cascade="all, delete-orphan")


class VocabLibraryFlashcard(Base):
    __tablename__ = "vocab_library_flashcards"
    __table_args__ = (
        UniqueConstraint("player_id", "campaign_id", "vocab_library_item_id", name="uq_vocab_library_flashcard"),
        Index("ix_vocab_library_flashcards_player_campaign", "player_id", "campaign_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    vocab_library_item_id: Mapped[int] = mapped_column(ForeignKey("vocab_library_items.id"), nullable=False, index=True)
    familiarity: Mapped[str] = mapped_column(String(10), nullable=False, default="again")
    familiarity_set_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    player: Mapped["Player"] = relationship(foreign_keys=[player_id])
    campaign: Mapped["Campaign"] = relationship(foreign_keys=[campaign_id])
    item: Mapped["VocabLibraryItem"] = relationship(back_populates="flashcards")


class CampaignVocabLink(Base):
    __tablename__ = "campaign_vocab_links"
    __table_args__ = (
        UniqueConstraint("campaign_id", "vocab_level_id", name="uq_campaign_vocab_link"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    vocab_level_id: Mapped[int] = mapped_column(ForeignKey("vocab_levels.id"), nullable=False, index=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    campaign: Mapped["Campaign"] = relationship(foreign_keys=[campaign_id])
    level: Mapped[VocabLevel] = relationship(back_populates="campaign_links")

