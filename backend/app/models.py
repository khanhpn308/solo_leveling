from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="IELTS Hunter")
    title: Mapped[str] = mapped_column(String(120), default="B1 Awakener")
    target: Mapped[str] = mapped_column(String(120), default="IELTS Academic 7.0-7.5")
    current_level: Mapped[str] = mapped_column(String(50), default="B1")
    start_date: Mapped[date] = mapped_column(Date)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    display_name: Mapped[str] = mapped_column(String(120), default="IELTS Hunter")
    target_overall_band: Mapped[str] = mapped_column(String(20), default="7.0-7.5")
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

    active_campaign: Mapped["Campaign | None"] = relationship(
        "Campaign",
        foreign_keys=[active_campaign_id],
        post_update=True,
    )
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        back_populates="player",
        foreign_keys="Campaign.player_id",
    )
    test_records: Mapped[list["TestRecord"]] = relationship(back_populates="player")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    player: Mapped[Player] = relationship(
        "Player",
        back_populates="campaigns",
        foreign_keys=[player_id],
    )
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


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    icon: Mapped[str] = mapped_column(String(32), default="*")
    xp: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[str] = mapped_column(String(2), default="F")
    confirmed_rank: Mapped[str] = mapped_column(String(2), default="F", index=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    weak_point: Mapped[str] = mapped_column(String(255), default="")
    user_weakness_note: Mapped[str] = mapped_column(Text, default="")
    last_system_suggestion_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)

    quests: Mapped[list["Quest"]] = relationship(back_populates="skill")
    templates: Mapped[list["QuestTemplate"]] = relationship(back_populates="primary_skill")
    rank_suggestions: Mapped[list["SkillRankSuggestion"]] = relationship(back_populates="skill")
    rank_history: Mapped[list["SkillRankHistory"]] = relationship(back_populates="skill")
    weakness_suggestions: Mapped[list["WeaknessSuggestion"]] = relationship(back_populates="skill")


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

    primary_skill: Mapped[Skill] = relationship(back_populates="templates")
    phase: Mapped["RoadmapPhase | None"] = relationship(back_populates="quest_templates")
    material: Mapped["StudyMaterial | None"] = relationship(back_populates="quest_templates")
    quests: Mapped[list["Quest"]] = relationship(back_populates="template")


class Quest(Base):
    __tablename__ = "quests"

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
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True, index=True)
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
    tracker_type: Mapped[str] = mapped_column(String(40), default="")
    tracker_entry_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    skill: Mapped[Skill] = relationship(back_populates="quests")
    campaign: Mapped[Campaign | None] = relationship(back_populates="quests")
    phase: Mapped["RoadmapPhase | None"] = relationship(back_populates="quests")
    study_plan_week: Mapped["StudyPlanWeek | None"] = relationship(back_populates="quests")
    study_plan_session: Mapped["StudyPlanSession | None"] = relationship(back_populates="quest")
    template: Mapped[QuestTemplate | None] = relationship(back_populates="quests")
    material: Mapped["StudyMaterial | None"] = relationship(back_populates="quests")


class CheckIn(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("checkin_date", name="uq_checkin_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
    unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


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

    campaign: Mapped[Campaign] = relationship(back_populates="weekly_missions")
    items: Mapped[list["WeeklyMissionItem"]] = relationship(back_populates="weekly_mission")


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
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True, index=True)
    month_index: Mapped[int] = mapped_column(Integer, default=1, index=True)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0)
    badge_id: Mapped[int | None] = mapped_column(ForeignKey("badges.id"), nullable=True)
    result_status: Mapped[str] = mapped_column(String(20), default="locked", index=True)
    result_note: Mapped[str] = mapped_column(String(255), default="")
    practice_suggestion: Mapped[str] = mapped_column(String(255), default="")
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    campaign: Mapped[Campaign | None] = relationship(back_populates="boss_battles")


class TestRecord(Base):
    __tablename__ = "test_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
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
    source_test_record_id: Mapped[int | None] = mapped_column(ForeignKey("test_records.id"), nullable=True, index=True)
    current_rank: Mapped[str] = mapped_column(String(2), default="F")
    suggested_rank: Mapped[str] = mapped_column(String(2), default="F")
    direction: Mapped[str] = mapped_column(String(10), default="same")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    skill: Mapped[Skill] = relationship(back_populates="rank_suggestions")
    source_test_record: Mapped[TestRecord | None] = relationship(back_populates="rank_suggestions")


class SkillRankHistory(Base):
    __tablename__ = "skill_rank_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    old_rank: Mapped[str] = mapped_column(String(2), default="F")
    new_rank: Mapped[str] = mapped_column(String(2), default="F")
    source_test_record_id: Mapped[int | None] = mapped_column(ForeignKey("test_records.id"), nullable=True, index=True)
    change_reason: Mapped[str] = mapped_column(String(255), default="")
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    skill: Mapped[Skill] = relationship(back_populates="rank_history")
    source_test_record: Mapped[TestRecord | None] = relationship(back_populates="rank_history")


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(40), default="", index=True)
    source_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    skill: Mapped[Skill] = relationship(back_populates="weakness_suggestions")
