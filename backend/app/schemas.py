from datetime import date, datetime

from pydantic import BaseModel, Field


class SkillOut(BaseModel):
    id: int
    name: str
    icon: str
    xp: int
    rank: str
    confirmed_rank: str
    level: int
    streak: int
    last_practiced: date | None
    weak_point: str
    user_weakness_note: str

    class Config:
        from_attributes = True


class CampaignOut(BaseModel):
    id: int
    player_id: int
    start_date: date
    end_date: date
    status: str
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class PlayerProfileOut(BaseModel):
    id: int
    display_name: str
    target_overall_band: str
    current_estimated_level: str
    strongest_skill: str
    weakest_skill: str
    study_days_per_week: int
    session_minutes: int
    daily_mini_study_minutes: int
    player_xp: int
    player_level: int
    player_rank: str
    current_streak: int
    best_streak: int
    shield_count: int
    shield_regen_progress: int
    perfect_day_count: int
    setup_completed: bool
    active_campaign_id: int | None

    class Config:
        from_attributes = True


class SetupIn(BaseModel):
    display_name: str
    roadmap_start_date: date
    target_overall_band: str
    current_estimated_level: str
    strongest_skill: str
    weakest_skill: str
    study_days_per_week: int = Field(ge=1, le=7)
    session_minutes: int = Field(ge=15, le=480)
    daily_mini_study_minutes: int = Field(ge=5, le=120)


class QuestCompletionIn(BaseModel):
    tracker_type: str = ""
    tracker_entry_id: int | None = None
    error_log_id: int | None = None
    writing_entry_id: int | None = None
    speaking_entry_id: int | None = None
    mock_test_id: int | None = None
    raw_score: str = ""
    completion_note: str = ""


class QuestOut(BaseModel):
    id: int
    quest_date: date
    week_no: int
    stage: str
    title: str
    skill_id: int
    skill_name: str
    source: str
    details: str
    xp: int
    completed: bool
    completed_at: datetime | None
    session_type: str
    campaign_id: int | None
    phase_id: int | None
    phase_title: str | None
    study_plan_week_id: int | None
    study_plan_session_id: int | None
    template_id: int | None
    material_id: int | None
    material_title: str | None
    status: str
    quest_role: str
    difficulty: str
    base_xp: int
    earned_xp: int
    reward_claimed: bool
    reward_claimed_at: datetime | None
    completed_mode: str | None
    completion_note: str
    raw_score: str
    tracker_type: str
    tracker_entry_id: int | None
    daily_slot_code: str | None
    error_log_id: int | None
    writing_entry_id: int | None
    speaking_entry_id: int | None
    mock_test_id: int | None
    expired_at: datetime | None


class QuestTemplateOut(BaseModel):
    id: int
    title: str
    description: str
    primary_skill_id: int
    phase_id: int | None
    material_id: int | None
    base_xp: int
    difficulty: str
    difficulty_description: str
    quest_role: str
    resource_name: str
    resource_category: str
    resource_note: str
    allowed_phase_start: int
    allowed_phase_end: int
    is_active: bool

    class Config:
        from_attributes = True


class StudyMaterialOut(BaseModel):
    id: int
    title: str
    category: str
    format: str
    file_path: str
    skill_tags: str
    recommended_phase_start: int
    recommended_phase_end: int
    notes: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PhaseMaterialOut(BaseModel):
    id: int
    material_id: int
    usage_purpose: str
    usage_frequency: str
    notes: str
    display_order: int
    material: StudyMaterialOut

    class Config:
        from_attributes = True


class RoadmapPhaseOut(BaseModel):
    id: int
    campaign_id: int
    phase_order: int
    code: str
    title: str
    month_start: int
    month_end: int
    week_start: int
    week_end: int
    start_date: date
    end_date: date
    objective: str
    focus_skills: str
    is_active: bool
    created_at: datetime
    phase_materials: list[PhaseMaterialOut]

    class Config:
        from_attributes = True


class StudyPlanSessionOut(BaseModel):
    id: int
    campaign_id: int
    phase_id: int
    study_plan_week_id: int
    week_no: int
    session_no: int
    study_date: date
    weekday_label: str
    session_label: str
    skill_summary: str
    task_detail: str
    material_summary: str
    deliverable: str
    status_text: str
    note_text: str
    mini_task: str

    class Config:
        from_attributes = True


class StudyPlanWeekOut(BaseModel):
    id: int
    campaign_id: int
    phase_id: int
    week_no: int
    week_start: date
    week_end: date
    weekly_focus: str
    weekly_output: str
    material_summary: str
    mini_task: str
    sessions: list[StudyPlanSessionOut]

    class Config:
        from_attributes = True


class CheckInIn(BaseModel):
    checkin_date: date
    mood: int = Field(ge=1, le=5)
    energy: int = Field(ge=1, le=5)
    focus: int = Field(default=3, ge=1, le=5)
    note: str = ""


class CheckInOut(BaseModel):
    id: int
    campaign_id: int | None
    checkin_date: date
    mood: int
    energy: int
    focus: int
    note: str

    class Config:
        from_attributes = True


class BadgeOut(BaseModel):
    id: int
    name: str
    icon: str
    description: str
    unlocked: bool
    unlocked_at: datetime | None

    class Config:
        from_attributes = True


class WeeklyMissionItemOut(BaseModel):
    id: int
    description: str
    target_count: int
    current_count: int
    status: str

    class Config:
        from_attributes = True


class WeeklyMissionOut(BaseModel):
    id: int
    campaign_id: int
    week_start: date
    week_end: date
    phase: str
    pattern_code: str
    title: str
    description: str
    reward_xp: int
    status: str
    completed_at: datetime | None
    reward_claimed: bool
    reward_claimed_at: datetime | None
    items: list[WeeklyMissionItemOut]

    class Config:
        from_attributes = True


class BossBattleOut(BaseModel):
    id: int
    stage: str
    battle_date: date
    title: str
    source: str
    goal: str
    status: str
    campaign_id: int | None
    month_index: int
    reward_xp: int
    badge_id: int | None
    result_status: str
    result_note: str
    practice_suggestion: str
    cleared_at: datetime | None

    class Config:
        from_attributes = True


class TestRecordIn(BaseModel):
    test_type: str
    test_date: date
    overall_score: str = ""
    listening_score: str = ""
    reading_score: str = ""
    writing_score: str = ""
    speaking_score: str = ""
    cefr_level: str = ""
    note: str = ""


class TestRecordOut(TestRecordIn):
    id: int
    player_id: int
    campaign_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class SkillRankSuggestionOut(BaseModel):
    id: int
    skill_id: int
    campaign_id: int | None
    source_test_record_id: int | None
    current_rank: str
    suggested_rank: str
    direction: str
    status: str
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class ErrorLogIn(BaseModel):
    skill_id: int
    source: str = ""
    error_description: str
    correction: str = ""
    cause: str = ""
    prevention: str = ""
    error_tag: str = ""
    logged_date: date


class ErrorLogOut(ErrorLogIn):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


class WritingEntryIn(BaseModel):
    task_type: str = ""
    prompt: str = ""
    draft_text: str = ""
    self_score: str = ""
    estimated_band: str = ""
    feedback_note: str = ""
    revised_text: str = ""
    entry_date: date


class WritingEntryOut(WritingEntryIn):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


class SpeakingEntryIn(BaseModel):
    part: str = ""
    topic: str = ""
    cue_or_question: str = ""
    self_score: str = ""
    self_note: str = ""
    transcript_summary: str = ""
    entry_date: date


class SpeakingEntryOut(SpeakingEntryIn):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


class MockTestIn(BaseModel):
    test_type: str = ""
    scope: str = "full"
    source: str = ""
    raw_score: str = ""
    estimated_band: str = ""
    estimated_band_override: str = ""
    note: str = ""
    test_date: date


class MockTestOut(MockTestIn):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


class WeaknessSuggestionOut(BaseModel):
    id: int
    skill_id: int
    campaign_id: int | None
    source_type: str
    source_ref_id: int | None
    source_test_record_id: int | None
    source_mock_test_id: int | None
    source_error_log_id: int | None
    source_quest_id: int | None
    title: str
    detail: str
    severity: str
    status: str
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class SummaryOut(BaseModel):
    player: dict
    total_completed_quests: int
    total_quests: int
    today_xp: int
    week_xp: int
    current_streak: int
    skills: list[SkillOut]
    badges: list[BadgeOut]
    boss_battles: list[BossBattleOut]
