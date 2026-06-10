from datetime import date, datetime

from pydantic import BaseModel, Field


class SupportBreakdownItem(BaseModel):
    source: str
    xp: int


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
    promotion_status: str = "none"
    pending_rank: str | None = None
    support_breakdown: list[SupportBreakdownItem] = []

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
    target_listening_band: str | None = None
    target_reading_band: str | None = None
    target_writing_band: str | None = None
    target_speaking_band: str | None = None
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
    reward_skill_id: int | None
    reward_skill_name: str | None


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
    boss_scope: str = "player"
    reward_skill_id: int | None = None
    reward_skill_name: str | None = None
    reward_claimed: bool = False
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


class VocabularyExampleIn(BaseModel):
    example_sentence: str
    example_meaning: str | None = None
    example_type: str | None = None
    is_corrected: bool = False
    correction_note: str | None = None


class VocabularyExampleOut(VocabularyExampleIn):
    id: int
    vocabulary_item_id: int
    player_id: int
    created_at: datetime

    class Config:
        from_attributes = True



# Collocation Collection Schemas
class CollocationCollectionIn(BaseModel):
    code: str
    title: str
    description: str | None = None
    source_book: str | None = None
    level: str | None = None
    is_active: bool = True

class CollocationCollectionOut(CollocationCollectionIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Collocation Section Schemas
class CollocationSectionIn(BaseModel):
    collection_id: int
    title: str
    section_order: int

class CollocationSectionOut(CollocationSectionIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Collocation Topic Schemas
class CollocationTopicIn(BaseModel):
    section_id: int
    title: str
    topic_number: int | None = None
    topic_order: int

class CollocationTopicOut(CollocationTopicIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Collocation Item Schemas
class CollocationItemIn(BaseModel):
    topic_id: int
    collocation: str
    pronunciation_us: str | None = None
    meaning_vi: str | None = None
    example_en: str | None = None
    example_vi: str | None = None
    collocation_type: str | None = None
    item_order: int = 0

class CollocationItemOut(CollocationItemIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Campaign Collocation Link Schemas
class CampaignCollocationLinkIn(BaseModel):
    campaign_id: int
    collection_id: int
    display_order: int = 0

class CampaignCollocationLinkOut(CampaignCollocationLinkIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Player Collocation Progress Schemas
class PlayerCollocationProgressIn(BaseModel):
    player_id: int
    campaign_id: int
    collocation_item_id: int
    status: str = "new"
    practice_count: int = 0
    correct_count: int = 0
    last_practiced_at: datetime | None = None

class PlayerCollocationProgressOut(PlayerCollocationProgressIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Complex/Nested/Progress schemas
class CollocationItemOutWithProgress(CollocationItemOut):
    progress: PlayerCollocationProgressOut | None = None

    class Config:
        from_attributes = True

class CollocationTopicOutline(CollocationTopicOut):
    items: list[CollocationItemOut] = []

    class Config:
        from_attributes = True

class CollocationTopicOutlineWithProgress(CollocationTopicOut):
    items: list[CollocationItemOutWithProgress] = []

    class Config:
        from_attributes = True

class CollocationSectionOutline(CollocationSectionOut):
    topics: list[CollocationTopicOutline] = []

    class Config:
        from_attributes = True

class CollocationSectionOutlineWithProgress(CollocationSectionOut):
    topics: list[CollocationTopicOutlineWithProgress] = []

    class Config:
        from_attributes = True

class CollocationCollectionOutline(CollocationCollectionOut):
    sections: list[CollocationSectionOutline] = []

    class Config:
        from_attributes = True

class CollocationCollectionOutlineWithProgress(CollocationCollectionOut):
    sections: list[CollocationSectionOutlineWithProgress] = []

    class Config:
        from_attributes = True



class VocabularyRelationIn(BaseModel):
    source_word_id: int
    target_word_id: int | None = None
    target_text: str | None = None
    relation_type: str | None = None
    note: str | None = None


class VocabularyRelationOut(VocabularyRelationIn):
    id: int
    player_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VocabularyItemIn(BaseModel):
    word: str
    normalized_word: str | None = None
    part_of_speech: str | None = None
    cefr_level: str | None = None
    ielts_topic: str | None = None
    meaning_en: str | None = None
    meaning_vi: str | None = None
    register_label: str | None = None
    grammar_note: str | None = None
    pronunciation_ipa: str | None = None
    word_stress: str | None = None
    source_type: str | None = None
    source_reference: str | None = None
    mastery_rank: str = "F"
    mastery_score: int = 0
    is_archived: bool = False


class VocabularyItemOut(VocabularyItemIn):
    id: int
    player_id: int
    created_at: datetime
    updated_at: datetime
    examples: list[VocabularyExampleOut] = []

    class Config:
        from_attributes = True


class FlashcardIn(BaseModel):
    vocabulary_item_id: int
    card_type: str | None = None
    front_text: str
    back_text: str
    hint: str | None = None
    difficulty: int = 1
    status: str = "new"


class FlashcardOut(FlashcardIn):
    id: int
    player_id: int
    created_at: datetime
    vocabulary_item: VocabularyItemOut | None = None

    class Config:
        from_attributes = True


class SpacedRepetitionStateOut(BaseModel):
    id: int
    player_id: int
    flashcard_id: int
    ease_factor: float
    interval_days: int
    repetition_count: int
    due_date: date | None
    last_reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewFlashcardIn(BaseModel):
    result: str


class VocabularyTopicIn(BaseModel):
    topic_name: str
    parent_topic_id: int | None = None
    description: str | None = None


class VocabularyTopicOut(VocabularyTopicIn):
    id: int
    player_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VocabularyNodeIn(BaseModel):
    topic_id: int
    vocabulary_item_id: int | None = None
    node_label: str
    node_type: str | None = None
    status: str = "locked"
    x_position: float | None = None
    y_position: float | None = None
    unlock_requirement: str | None = None


class VocabularyNodeUpdate(BaseModel):
    node_label: str | None = None
    status: str | None = None
    x_position: float | None = None
    y_position: float | None = None
    unlock_requirement: str | None = None


class VocabularyNodeOut(VocabularyNodeIn):
    id: int
    player_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VocabularyEdgeIn(BaseModel):
    source_node_id: int
    target_node_id: int
    edge_type: str | None = None
    strength: int = 1


class VocabularyEdgeOut(VocabularyEdgeIn):
    id: int
    player_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VocabularyTreeOut(BaseModel):
    topic: VocabularyTopicOut
    nodes: list[VocabularyNodeOut]
    edges: list[VocabularyEdgeOut]

class CollocationPracticeMatchOut(BaseModel):
    collocation_id: int
    core_word: str
    collocation: str
    collocation_type: str | None

class CollocationPracticeResponse(BaseModel):
    matches: list[CollocationPracticeMatchOut]
    distractors: list[str]


class ShadowDuelQuestion(BaseModel):
    word: str
    question_type: str  # synonym, antonym, register
    correct_answer: str
    options: list[str]
    register_note: str | None = None


class ShadowDuelResponse(BaseModel):
    questions: list[ShadowDuelQuestion]


class PracticeSuccessIn(BaseModel):
    words: list[str]
    xp_gained: int


class WordFamilyNode(BaseModel):
    id: str
    label: str
    part_of_speech: str | None = None
    meaning: str | None = None
    cefr_level: str | None = None
    mastery_rank: str | None = None
    is_discovered: bool


class WordFamilyEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str | None = None


class WordFamilyGroup(BaseModel):
    family_id: str
    root_word: str
    nodes: list[WordFamilyNode]
    edges: list[WordFamilyEdge]


class WordFamilyResponse(BaseModel):
    families: list[WordFamilyGroup]


class EchoChamberQuestion(BaseModel):
    word: str
    part_of_speech: str | None = None
    pronunciation_ipa: str | None = None
    word_stress: str | None = None
    syllables: list[str] = []
    stressed_index: int | None = None
    silent_letters: list[str] = []


class EchoChamberResponse(BaseModel):
    questions: list[EchoChamberQuestion]


class VocabularyErrorIn(BaseModel):
    vocabulary_item_id: int | None = None
    error_type: str
    wrong_text: str
    corrected_text: str
    explanation: str | None = None


class VocabularyErrorOut(VocabularyErrorIn):
    id: int
    player_id: int
    status: str
    defeated_count: int
    created_at: datetime
    word: str | None = None

    class Config:
        from_attributes = True


class BossQuestion(BaseModel):
    id: str
    question_type: str
    prompt: str
    choices: list[str] = []
    correct_answer: str
    word_id: int | None = None


class VocabularyBossExam(BaseModel):
    boss_id: int
    questions: list[BossQuestion]


class VocabularyBossSubmitIn(BaseModel):
    score_pct: float


class VocabularyBossSubmitOut(BaseModel):
    passed: bool
    score_pct: float
    reward_xp: int
    message: str


class OnboardingActivateIn(BaseModel):
    display_name: str | None = None
    campaign_template_code: str | None = None
    start_date: date | None = None
    target_band: str | None = None
    target_overall_band: str | None = None
    target_listening_band: str | None = None
    target_reading_band: str | None = None
    target_writing_band: str | None = None
    target_speaking_band: str | None = None


class PlayerTargetsIn(BaseModel):
    target_overall_band: str | None = None
    target_listening_band: str | None = None
    target_reading_band: str | None = None
    target_writing_band: str | None = None
    target_speaking_band: str | None = None


class AccountRegisterIn(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class AccountLoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class AccountMeOut(BaseModel):
    id: int
    email: str
    display_name: str | None
    status: str
    role: str
    onboarding_completed: bool
    onboarding_completed_at: datetime | None

    class Config:
        from_attributes = True


class PlayerMeOut(BaseModel):
    id: int
    name: str
    display_name: str
    player_level: int
    player_rank: str
    player_xp: int
    target: str | None = None
    target_overall_band: str | None = None
    target_listening_band: str | None = None
    target_reading_band: str | None = None
    target_writing_band: str | None = None
    target_speaking_band: str | None = None

    class Config:
        from_attributes = True


class CampaignMeOut(BaseModel):
    id: int
    status: str
    start_date: date
    end_date: date

    class Config:
        from_attributes = True


class MeResponseOut(BaseModel):
    account: AccountMeOut
    player: PlayerMeOut | None = None
    campaign: CampaignMeOut | None = None


class OnboardingStatusOut(BaseModel):
    onboarding_completed: bool
    has_certificate: bool


class ManualCertificateIn(BaseModel):
    overall_score: float | None = None
    listening_score: float | None = None
    reading_score: float | None = None
    writing_score: float | None = None
    speaking_score: float | None = None


class ManualCertificateOut(BaseModel):
    id: int
    overall_score: float | None
    listening_score: float | None
    reading_score: float | None
    writing_score: float | None
    speaking_score: float | None
    created_at: datetime

    class Config:
        from_attributes = True


class RankExamStartIn(BaseModel):
    skill_id: int


class RankExamQuestionOut(BaseModel):
    id: int
    question_type: str
    prompt: str
    instruction: str | None
    options_json: dict | list | None

    class Config:
        from_attributes = True


class RankExamStartOut(BaseModel):
    attempt_id: int
    skill_id: int
    from_rank: str
    to_rank: str
    time_limit_minutes: int
    expires_at: datetime
    questions: list[RankExamQuestionOut]


class RankExamAnswerIn(BaseModel):
    question_id: int
    answer_json: dict | list | str | None


class RankExamSubmitIn(BaseModel):
    answers: list[RankExamAnswerIn]


class RankExamSubmitOut(BaseModel):
    attempt_id: int
    passed: bool
    score_percent: float
    score_points: int
    total_points: int
    confirmed_rank: str


class RankExamAttemptOut(BaseModel):
    id: int
    campaign_id: int
    skill_id: int
    from_rank: str
    to_rank: str
    status: str
    score_points: int | None
    total_points: int
    score_percent: float | None
    passed: bool | None
    started_at: datetime
    expires_at: datetime | None
    submitted_at: datetime | None

    class Config:
        from_attributes = True


class RankExamStatusOut(BaseModel):
    skill_id: int
    promotion_status: str
    confirmed_rank: str | None
    pending_rank: str | None
    daily_cap: int
    attempts_today: int
    attempts_remaining: int


# ---------------------------------------------------------------------------
# I4-2: Collocation flashcard browser + review schemas
# ---------------------------------------------------------------------------

class CollocationBrowseTopicOut(BaseModel):
    """A topic with its section context, returned by GET /api/collocations/topics."""
    id: int
    title: str
    topic_order: int
    section_title: str
    section_order: int
    item_count: int = 0
    # Progress: collocations whose effective_familiarity is hard/good/easy (not again/new)
    completed_count: int = 0

    class Config:
        from_attributes = True


class CollocationBrowseItemOut(BaseModel):
    """An item enriched with flashcard state, returned by GET /api/collocations/topics/{id}/items."""
    id: int
    collocation: str
    pronunciation_us: str | None = None
    meaning_vi: str | None = None
    example_en: str | None = None
    example_vi: str | None = None
    collocation_type: str | None = None
    item_order: int = 0
    # Flashcard state
    effective_familiarity: str = "again"  # again/hard/good/easy
    is_added: bool = False

    class Config:
        from_attributes = True


class CollocationFlashcardTopicOut(BaseModel):
    """A topic that has ≥1 non-graduated added flashcard, returned by GET /api/collocations/flashcard/topics."""
    id: int
    title: str
    topic_order: int
    section_title: str
    card_count: int = 0

    class Config:
        from_attributes = True


class CollocationFlashcardItemOut(BaseModel):
    """A non-graduated flashcard for review, returned by GET /api/collocations/flashcard/topics/{id}."""
    id: int
    collocation: str
    pronunciation_us: str | None = None
    meaning_vi: str | None = None
    example_en: str | None = None
    example_vi: str | None = None
    collocation_type: str | None = None
    item_order: int = 0
    effective_familiarity: str = "again"

    class Config:
        from_attributes = True


class CollocationReviewIn(BaseModel):
    """Body for POST /api/collocations/{item_id}/flashcard/review."""
    result: str  # again | hard | good | easy







