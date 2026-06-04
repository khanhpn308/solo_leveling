import os
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .database import get_db, run_database_bootstrap, wait_for_database
from .models import (
    Badge,
    BossBattle,
    Campaign,
    CheckIn,
    ErrorLog,
    MockTest,
    PhaseMaterial,
    Player,
    Quest,
    QuestTemplate,
    RoadmapPhase,
    Skill,
    SkillRankHistory,
    SkillRankSuggestion,
    SpeakingEntry,
    StudyPlanSession,
    StudyPlanWeek,
    StudyMaterial,
    TestRecord,
    WeaknessSuggestion,
    WeeklyMission,
    WeeklyMissionItem,
    WritingEntry,
)
from .schemas import (
    BadgeOut,
    BossBattleOut,
    CampaignOut,
    CheckInIn,
    CheckInOut,
    ErrorLogIn,
    ErrorLogOut,
    MockTestIn,
    MockTestOut,
    PlayerProfileOut,
    QuestOut,
    QuestTemplateOut,
    RoadmapPhaseOut,
    SetupIn,
    SkillOut,
    SkillRankSuggestionOut,
    SpeakingEntryIn,
    SpeakingEntryOut,
    StudyPlanSessionOut,
    StudyPlanWeekOut,
    StudyMaterialOut,
    SummaryOut,
    TestRecordIn,
    TestRecordOut,
    WeaknessSuggestionOut,
    WeeklyMissionOut,
    WritingEntryIn,
    WritingEntryOut,
)
from .seed import seed_database
from .services import (
    apply_rank_suggestion,
    apply_weakness_suggestion,
    complete_quest_instance,
    current_week_window,
    create_rank_suggestions_for_test,
    dismiss_rank_suggestion,
    dismiss_weakness_suggestion,
    ensure_weakness_suggestions,
    estimate_band_from_mock,
    get_active_campaign,
    get_active_player,
    refresh_progress_state,
    uncomplete_quest_instance,
)

app = FastAPI(title="IELTS Quest Dashboard API", version="2.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_start_date() -> date:
    raw = os.getenv("APP_START_DATE", "2026-06-04")
    return date.fromisoformat(raw)


def serialize_quest(quest: Quest) -> QuestOut:
    return QuestOut(
        id=quest.id,
        quest_date=quest.quest_date,
        week_no=quest.week_no,
        stage=quest.stage,
        title=quest.title,
        skill_id=quest.skill_id,
        skill_name=quest.skill.name,
        source=quest.source,
        details=quest.details,
        xp=quest.xp,
        completed=quest.completed,
        completed_at=quest.completed_at,
        session_type=quest.session_type,
        campaign_id=quest.campaign_id,
        phase_id=quest.phase_id,
        phase_title=quest.phase.title if quest.phase else None,
        study_plan_week_id=quest.study_plan_week_id,
        study_plan_session_id=quest.study_plan_session_id,
        template_id=quest.template_id,
        material_id=quest.material_id,
        material_title=quest.material.title if quest.material else None,
        status=quest.status,
        quest_role=quest.quest_role,
        difficulty=quest.difficulty,
        base_xp=quest.base_xp,
        earned_xp=quest.earned_xp,
        completed_mode=quest.completed_mode,
        completion_note=quest.completion_note,
        raw_score=quest.raw_score,
        tracker_type=quest.tracker_type,
        tracker_entry_id=quest.tracker_entry_id,
        expired_at=quest.expired_at,
    )


def get_player_or_404(db: Session) -> Player:
    try:
        return get_active_player(db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def get_campaign_or_404(db: Session, player: Player | None = None) -> Campaign:
    try:
        return get_active_campaign(db, player)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.on_event("startup")
def on_startup() -> None:
    wait_for_database()
    run_database_bootstrap()
    db = next(get_db())
    try:
        seed_database(db, parse_start_date())
        refresh_progress_state(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "online", "message": "IELTS Quest API is running"}


@app.get("/api/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    refresh_progress_state(db)
    player = get_player_or_404(db)
    campaign = get_campaign_or_404(db, player)
    week_start, week_end = current_week_window(player)
    today = max(date.today(), player.start_date)

    today_xp = (
        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
        .filter(Quest.completed == True, Quest.quest_date == today, Quest.campaign_id == campaign.id)
        .scalar()
        or 0
    )
    week_xp = (
        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
        .filter(
            Quest.completed == True,
            Quest.quest_date >= week_start,
            Quest.quest_date <= week_end,
            Quest.campaign_id == campaign.id,
        )
        .scalar()
        or 0
    )
    completed = (
        db.query(Quest)
        .filter(Quest.completed == True, Quest.campaign_id == campaign.id, Quest.session_type == "Daily Quest")
        .count()
    )
    total = db.query(Quest).filter(Quest.campaign_id == campaign.id, Quest.session_type == "Daily Quest").count()
    skills = db.query(Skill).order_by(Skill.id).all()
    badges = db.query(Badge).order_by(Badge.id).all()
    boss_battles = (
        db.query(BossBattle)
        .filter(BossBattle.campaign_id == campaign.id)
        .order_by(BossBattle.battle_date)
        .limit(8)
        .all()
    )

    player_data = {
        "name": player.display_name or player.name,
        "title": player.title,
        "target": player.target or f"IELTS Academic {player.target_overall_band}",
        "current_level": player.current_estimated_level or player.current_level,
        "start_date": player.start_date,
        "total_xp": player.player_xp,
        "week_start": week_start,
        "week_end": week_end,
        "player_rank": player.player_rank,
        "player_level": player.player_level,
        "shield_count": player.shield_count,
        "perfect_day_count": player.perfect_day_count,
    }

    return SummaryOut(
        player=player_data,
        total_completed_quests=completed,
        total_quests=total,
        today_xp=int(today_xp),
        week_xp=int(week_xp),
        current_streak=player.current_streak,
        skills=skills,
        badges=badges,
        boss_battles=boss_battles,
    )


@app.get("/api/profile", response_model=PlayerProfileOut)
def get_profile(db: Session = Depends(get_db)):
    refresh_progress_state(db)
    return get_player_or_404(db)


@app.post("/api/setup", response_model=PlayerProfileOut)
def post_setup(payload: SetupIn, db: Session = Depends(get_db)):
    player = get_player_or_404(db)
    campaign = get_campaign_or_404(db, player)
    today = date.today()
    if payload.roadmap_start_date != campaign.start_date and today >= campaign.start_date:
        raise HTTPException(status_code=400, detail="Roadmap start date is locked after the campaign begins")

    if payload.roadmap_start_date != campaign.start_date:
        delta = payload.roadmap_start_date - campaign.start_date
        campaign.start_date = payload.roadmap_start_date
        campaign.end_date = payload.roadmap_start_date + timedelta(days=548)
        player.start_date = payload.roadmap_start_date
        for quest in db.query(Quest).filter(Quest.campaign_id == campaign.id).all():
            quest.quest_date = quest.quest_date + delta
        for mission in db.query(WeeklyMission).filter(WeeklyMission.campaign_id == campaign.id).all():
            mission.week_start = mission.week_start + delta
            mission.week_end = mission.week_end + delta
        for boss in db.query(BossBattle).filter(BossBattle.campaign_id == campaign.id).all():
            boss.battle_date = boss.battle_date + delta

    player.display_name = payload.display_name
    player.name = payload.display_name
    player.target_overall_band = payload.target_overall_band
    player.target = f"IELTS Academic {payload.target_overall_band}"
    player.current_estimated_level = payload.current_estimated_level
    player.current_level = payload.current_estimated_level
    player.strongest_skill = payload.strongest_skill
    player.weakest_skill = payload.weakest_skill
    player.study_days_per_week = payload.study_days_per_week
    player.session_minutes = payload.session_minutes
    player.daily_mini_study_minutes = payload.daily_mini_study_minutes
    player.setup_completed = True

    db.commit()
    refresh_progress_state(db)
    db.refresh(player)
    return player


@app.get("/api/campaigns/current", response_model=CampaignOut)
def get_current_campaign(db: Session = Depends(get_db)):
    player = get_player_or_404(db)
    return get_campaign_or_404(db, player)


@app.get("/api/skills", response_model=list[SkillOut])
def get_skills(db: Session = Depends(get_db)):
    refresh_progress_state(db)
    return db.query(Skill).order_by(Skill.id).all()


@app.get("/api/quest-templates", response_model=list[QuestTemplateOut])
def get_quest_templates(db: Session = Depends(get_db)):
    return db.query(QuestTemplate).order_by(QuestTemplate.id).all()


@app.get("/api/materials", response_model=list[StudyMaterialOut])
def get_study_materials(db: Session = Depends(get_db)):
    return db.query(StudyMaterial).filter(StudyMaterial.is_active == True).order_by(StudyMaterial.title).all()


@app.get("/api/materials/{material_id}", response_model=StudyMaterialOut)
def get_study_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found")
    return material


@app.get("/api/roadmap/phases", response_model=list[RoadmapPhaseOut])
def get_roadmap_phases(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(RoadmapPhase)
        .options(joinedload(RoadmapPhase.phase_materials).joinedload(PhaseMaterial.material))
        .filter(RoadmapPhase.campaign_id == campaign.id)
        .order_by(RoadmapPhase.phase_order)
        .all()
    )


@app.get("/api/study-plan/weeks", response_model=list[StudyPlanWeekOut])
def get_study_plan_weeks(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(StudyPlanWeek)
        .options(joinedload(StudyPlanWeek.sessions))
        .filter(StudyPlanWeek.campaign_id == campaign.id)
        .order_by(StudyPlanWeek.week_no)
        .all()
    )


@app.get("/api/study-plan/current-week", response_model=StudyPlanWeekOut)
def get_current_study_plan_week(db: Session = Depends(get_db)):
    player = get_player_or_404(db)
    campaign = get_campaign_or_404(db, player)
    current_week_start, current_week_end = current_week_window(player)
    week = (
        db.query(StudyPlanWeek)
        .options(joinedload(StudyPlanWeek.sessions))
        .filter(
            StudyPlanWeek.campaign_id == campaign.id,
            StudyPlanWeek.week_start <= current_week_end,
            StudyPlanWeek.week_end >= current_week_start,
        )
        .order_by(StudyPlanWeek.week_no)
        .first()
    )
    if not week:
        raise HTTPException(status_code=404, detail="Study plan week not found")
    return week


@app.get("/api/main-quests", response_model=list[QuestOut])
def get_main_quests(
    db: Session = Depends(get_db),
    week_no: int | None = Query(default=None),
    phase_id: int | None = Query(default=None),
):
    refresh_progress_state(db)
    player = get_player_or_404(db)
    campaign = get_campaign_or_404(db, player)
    query = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material))
        .filter(Quest.campaign_id == campaign.id, Quest.session_type == "Main Quest")
    )
    if week_no:
        query = query.filter(Quest.week_no == week_no)
    if phase_id:
        query = query.filter(Quest.phase_id == phase_id)
    quests = query.order_by(Quest.quest_date, Quest.id).all()
    return [serialize_quest(quest) for quest in quests]


@app.get("/api/quests", response_model=list[QuestOut])
def get_quests(
    db: Session = Depends(get_db),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    stage: str | None = Query(default=None),
    week_no: int | None = Query(default=None),
    phase_id: int | None = Query(default=None),
    material_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    refresh_progress_state(db)
    player = get_player_or_404(db)
    campaign = get_campaign_or_404(db, player)
    if not start and not end and not week_no and not stage and not phase_id and not material_id and not status:
        start, end = current_week_window(player)

    query = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material))
        .filter(Quest.campaign_id == campaign.id, Quest.session_type == "Daily Quest")
    )
    if start:
        query = query.filter(Quest.quest_date >= start)
    if end:
        query = query.filter(Quest.quest_date <= end)
    if stage:
        query = query.filter(Quest.stage == stage)
    if week_no:
        query = query.filter(Quest.week_no == week_no)
    if phase_id:
        query = query.filter(Quest.phase_id == phase_id)
    if material_id:
        query = query.filter(Quest.material_id == material_id)
    if status:
        query = query.filter(Quest.status == status)
    quests = query.order_by(Quest.quest_date, Quest.id).all()
    return [serialize_quest(quest) for quest in quests]


@app.get("/api/quests/today", response_model=list[QuestOut])
def get_today_quests(db: Session = Depends(get_db)):
    refresh_progress_state(db)
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    today = date.today()
    quests = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material))
        .filter(Quest.campaign_id == campaign.id, Quest.quest_date == today, Quest.session_type == "Daily Quest")
        .order_by(Quest.id)
        .all()
    )
    return [serialize_quest(quest) for quest in quests]


@app.get("/api/quests/backlog", response_model=list[QuestOut])
def get_backlog_quests(db: Session = Depends(get_db)):
    refresh_progress_state(db)
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    quests = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material))
        .filter(Quest.campaign_id == campaign.id, Quest.status == "overdue", Quest.session_type == "Daily Quest")
        .order_by(Quest.quest_date, Quest.id)
        .all()
    )
    return [serialize_quest(quest) for quest in quests]


@app.post("/api/quests/{quest_id}/complete", response_model=QuestOut)
def complete_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material))
        .filter(Quest.id == quest_id)
        .first()
    )
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    try:
        return serialize_quest(complete_quest_instance(db, quest))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/quests/{quest_id}/uncomplete", response_model=QuestOut)
def uncomplete_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material))
        .filter(Quest.id == quest_id)
        .first()
    )
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return serialize_quest(uncomplete_quest_instance(db, quest))


@app.get("/api/weekly-mission/current", response_model=WeeklyMissionOut)
def get_current_weekly_mission(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    today = date.today()
    mission = (
        db.query(WeeklyMission)
        .options(joinedload(WeeklyMission.items))
        .filter(
            WeeklyMission.campaign_id == campaign.id,
            WeeklyMission.week_start <= today,
            WeeklyMission.week_end >= today,
        )
        .first()
    )
    if not mission:
        mission = (
            db.query(WeeklyMission)
            .options(joinedload(WeeklyMission.items))
            .filter(WeeklyMission.campaign_id == campaign.id)
            .order_by(WeeklyMission.week_start)
            .first()
        )
    if not mission:
        raise HTTPException(status_code=404, detail="Weekly mission not found")
    return mission


@app.post("/api/checkins", response_model=CheckInOut)
def upsert_checkin(payload: CheckInIn, db: Session = Depends(get_db)):
    item = db.query(CheckIn).filter(CheckIn.checkin_date == payload.checkin_date).first()
    if item:
        item.mood = payload.mood
        item.energy = payload.energy
        item.focus = payload.focus
        item.note = payload.note
    else:
        item = CheckIn(
            checkin_date=payload.checkin_date,
            mood=payload.mood,
            energy=payload.energy,
            focus=payload.focus,
            note=payload.note,
        )
        db.add(item)
    db.commit()
    refresh_progress_state(db)
    db.refresh(item)
    return item


@app.get("/api/checkins", response_model=list[CheckInOut])
def get_checkins(db: Session = Depends(get_db), start: date | None = None, end: date | None = None):
    query = db.query(CheckIn)
    if start:
        query = query.filter(CheckIn.checkin_date >= start)
    if end:
        query = query.filter(CheckIn.checkin_date <= end)
    return query.order_by(CheckIn.checkin_date.desc()).limit(30).all()


@app.get("/api/badges", response_model=list[BadgeOut])
def get_badges(db: Session = Depends(get_db)):
    refresh_progress_state(db)
    return db.query(Badge).order_by(Badge.id).all()


@app.get("/api/boss-battles", response_model=list[BossBattleOut])
def get_boss_battles(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(BossBattle)
        .filter(BossBattle.campaign_id == campaign.id)
        .order_by(BossBattle.battle_date)
        .all()
    )


@app.get("/api/test-records", response_model=list[TestRecordOut])
def get_test_records(db: Session = Depends(get_db)):
    player = get_player_or_404(db)
    return (
        db.query(TestRecord)
        .filter(TestRecord.player_id == player.id)
        .order_by(TestRecord.test_date.desc(), TestRecord.id.desc())
        .all()
    )


@app.post("/api/test-records", response_model=TestRecordOut)
def create_test_record(payload: TestRecordIn, db: Session = Depends(get_db)):
    player = get_player_or_404(db)
    record = TestRecord(player_id=player.id, **payload.model_dump())
    db.add(record)
    db.flush()
    create_rank_suggestions_for_test(db, record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/rank-suggestions", response_model=list[SkillRankSuggestionOut])
def get_rank_suggestions(db: Session = Depends(get_db), include_resolved: bool = False):
    query = db.query(SkillRankSuggestion).order_by(SkillRankSuggestion.created_at.desc(), SkillRankSuggestion.id.desc())
    if not include_resolved:
        query = query.filter(SkillRankSuggestion.status == "pending")
    return query.all()


@app.post("/api/rank-suggestions/{suggestion_id}/apply", response_model=SkillRankSuggestionOut)
def post_apply_rank_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = (
        db.query(SkillRankSuggestion)
        .options(joinedload(SkillRankSuggestion.skill))
        .filter(SkillRankSuggestion.id == suggestion_id)
        .first()
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="Rank suggestion not found")
    return apply_rank_suggestion(db, suggestion)


@app.post("/api/rank-suggestions/{suggestion_id}/dismiss", response_model=SkillRankSuggestionOut)
def post_dismiss_rank_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = db.query(SkillRankSuggestion).filter(SkillRankSuggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Rank suggestion not found")
    return dismiss_rank_suggestion(db, suggestion)


@app.get("/api/error-logs", response_model=list[ErrorLogOut])
def get_error_logs(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(ErrorLog)
        .filter(ErrorLog.campaign_id == campaign.id)
        .order_by(ErrorLog.logged_date.desc(), ErrorLog.id.desc())
        .all()
    )


@app.post("/api/error-logs", response_model=ErrorLogOut)
def create_error_log(payload: ErrorLogIn, db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    item = ErrorLog(campaign_id=campaign.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/writing-entries", response_model=list[WritingEntryOut])
def get_writing_entries(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(WritingEntry)
        .filter(WritingEntry.campaign_id == campaign.id)
        .order_by(WritingEntry.entry_date.desc(), WritingEntry.id.desc())
        .all()
    )


@app.post("/api/writing-entries", response_model=WritingEntryOut)
def create_writing_entry(payload: WritingEntryIn, db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    item = WritingEntry(campaign_id=campaign.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/speaking-entries", response_model=list[SpeakingEntryOut])
def get_speaking_entries(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(SpeakingEntry)
        .filter(SpeakingEntry.campaign_id == campaign.id)
        .order_by(SpeakingEntry.entry_date.desc(), SpeakingEntry.id.desc())
        .all()
    )


@app.post("/api/speaking-entries", response_model=SpeakingEntryOut)
def create_speaking_entry(payload: SpeakingEntryIn, db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    item = SpeakingEntry(campaign_id=campaign.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/mock-tests", response_model=list[MockTestOut])
def get_mock_tests(db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    return (
        db.query(MockTest)
        .filter(MockTest.campaign_id == campaign.id)
        .order_by(MockTest.test_date.desc(), MockTest.id.desc())
        .all()
    )


@app.post("/api/mock-tests", response_model=MockTestOut)
def create_mock_test(payload: MockTestIn, db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    data = payload.model_dump()
    if not data["estimated_band"]:
        data["estimated_band"] = estimate_band_from_mock(data["raw_score"], data["test_type"])
    item = MockTest(campaign_id=campaign.id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/weakness-suggestions", response_model=list[WeaknessSuggestionOut])
def get_weakness_suggestions(db: Session = Depends(get_db), include_resolved: bool = False):
    campaign = get_campaign_or_404(db, get_player_or_404(db))
    refresh_progress_state(db)
    ensure_weakness_suggestions(db, campaign)
    query = (
        db.query(WeaknessSuggestion)
        .options(joinedload(WeaknessSuggestion.skill))
        .order_by(WeaknessSuggestion.created_at.desc(), WeaknessSuggestion.id.desc())
    )
    if not include_resolved:
        query = query.filter(WeaknessSuggestion.status == "pending")
    return query.all()


@app.post("/api/weakness-suggestions/{suggestion_id}/apply", response_model=WeaknessSuggestionOut)
def post_apply_weakness_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = (
        db.query(WeaknessSuggestion)
        .options(joinedload(WeaknessSuggestion.skill))
        .filter(WeaknessSuggestion.id == suggestion_id)
        .first()
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="Weakness suggestion not found")
    return apply_weakness_suggestion(db, suggestion)


@app.post("/api/weakness-suggestions/{suggestion_id}/dismiss", response_model=WeaknessSuggestionOut)
def post_dismiss_weakness_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = db.query(WeaknessSuggestion).filter(WeaknessSuggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Weakness suggestion not found")
    return dismiss_weakness_suggestion(db, suggestion)


@app.post("/api/dev/reset")
def reset_database(db: Session = Depends(get_db)):
    for model in [
        Quest,
        WeeklyMissionItem,
        WeeklyMission,
        BossBattle,
        SkillRankHistory,
        SkillRankSuggestion,
        WeaknessSuggestion,
        ErrorLog,
        WritingEntry,
        SpeakingEntry,
        MockTest,
        Badge,
        TestRecord,
        StudyPlanSession,
        StudyPlanWeek,
        QuestTemplate,
        PhaseMaterial,
        RoadmapPhase,
        StudyMaterial,
        Skill,
        Campaign,
        Player,
        CheckIn,
    ]:
        db.query(model).delete()
    db.commit()
    seed_database(db, parse_start_date())
    refresh_progress_state(db)
    return {"status": "reset", "message": "Database has been reset and seeded again."}
