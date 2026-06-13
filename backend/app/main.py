import os
from datetime import date, datetime, timedelta
from pydantic import BaseModel

from fastapi import Cookie, Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .database import get_db, run_database_bootstrap, wait_for_database
from .auth_utils import hash_password, verify_password, create_jwt, decode_jwt
from .models import (
    Account,
    AccountPreference,
    AccountSession,
    AccountSecurityEvent,
    AccountToken,
    PlayerLearningProfile,
    CampaignSetting,
    CampaignTemplate,
    CampaignTemplateSkillQuota,
    CampaignSkillQuestQuota,
    VocabularySetting,
    CertificateRecord,
    RankExamPool,
    RankExamVersion,
    RankExamQuestion,
    RankExamAttempt,
    RankExamAnswer,
    Badge,
    BadgeUnlock,
    BossBattle,
    CampaignSkillState,
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
    VocabularyItem,
    VocabularyExample,
    VocabularyRelation,
    Flashcard,
    SpacedRepetitionState,
    VocabularyTopic,
    VocabularyNode,
    VocabularyEdge,
    VocabularyError,
    CollocationLevel,
    CollocationCollection,
    CollocationSection,
    CollocationTopic,
    CollocationItem,
    CampaignCollocationLink,
    PlayerCollocationProgress,
    CollocationFlashcard,
    VocabLevel,
    VocabTopic,
    VocabUnit,
    VocabSection,
    VocabLibraryItem,
    VocabLibraryFlashcard,
    CampaignVocabLink,
    RankXpThreshold,
    QuestXpPolicy,
    WeeklyMissionXpPolicy,
    MainQuestXpPolicy,
)
from .schemas import (
    BadgeOut,
    BossBattleOut,
    CampaignOut,
    CheckInIn,
    CheckInOut,
    TestXpSkillOut,
    TestXpAwardIn,
    ErrorLogIn,
    ErrorLogOut,
    MockTestIn,
    MockTestOut,
    PlayerProfileOut,
    QuestCompletionIn,
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
    VocabularyExampleIn,
    VocabularyExampleOut,
    VocabularyRelationIn,
    VocabularyRelationOut,
    CollocationCollectionIn,
    CollocationCollectionOut,
    CollocationCollectionOutline,
    CollocationCollectionOutlineWithProgress,
    CampaignCollocationLinkOut,
    PlayerCollocationProgressOut,
    VocabularyItemIn,
    VocabularyItemOut,
    FlashcardIn,
    FlashcardOut,
    VocabularyTopicIn,
    VocabularyTopicOut,
    VocabularyNodeIn,
    VocabularyNodeOut,
    VocabularyNodeUpdate,
    VocabularyEdgeIn,
    VocabularyEdgeOut,
    VocabularyTreeOut,
    SpacedRepetitionStateOut,
    ReviewFlashcardIn,
    CollocationPracticeResponse,
    ShadowDuelResponse,
    PracticeSuccessIn,
    WordFamilyResponse,
    EchoChamberResponse,
    VocabularyErrorIn,
    VocabularyErrorOut,
    VocabularyBossExam,
    VocabularyBossSubmitIn,
    VocabularyBossSubmitOut,
    AccountRegisterIn,
    AccountLoginIn,
    OnboardingActivateIn,
    PlayerTargetsIn,
    TokenOut,
    AccountMeOut,
    PlayerMeOut,
    CampaignMeOut,
    MeResponseOut,
    OnboardingStatusOut,
    ManualCertificateIn,
    ManualCertificateOut,
    RankExamStartIn,
    RankExamQuestionOut,
    RankExamStartOut,
    RankExamAnswerIn,
    RankExamSubmitIn,
    RankExamSubmitOut,
    RankExamAttemptOut,
    RankExamStatusOut,
    SupportBreakdownItem,
    CollocationLevelOut,
    CollocationBrowseTopicOut,
    CollocationBrowseItemOut,
    CollocationFlashcardTopicOut,
    CollocationFlashcardItemOut,
    CollocationReviewIn,
    VocabLevelOut,
    VocabTopicOut,
    VocabUnitOut,
    VocabSectionOut,
    VocabWordOut,
    VocabReviewIn,
    VocabFlashcardDueOut,
)
from .seed import activate_campaign_for_player, ensure_quest_instances, ensure_roadmap_phases, ensure_skills, ensure_templates, parse_start_date, seed_database
from .services import (
    apply_rank_suggestion,
    apply_weakness_suggestion,
    complete_quest_instance,
    current_week_window,
    create_rank_suggestions_for_certificate,
    create_rank_suggestions_for_test,
    dismiss_rank_suggestion,
    dismiss_weakness_suggestion,
    ensure_weakness_suggestions,
    estimate_band_from_mock,
    get_active_campaign,
    get_campaign_skill_state_map,
    MATRIX_SKILLS,
    SUPPORT_ROUTING,
    refresh_progress_state,
    uncomplete_quest_instance,
)
from . import services
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

app = FastAPI(title="IELTS Quest Dashboard API", version="2.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Account:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    token = credentials.credentials
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found"
        )
    if account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    return account


# Test-only XP tool: gated to the seed account.
TEST_ACCOUNT_EMAIL = "ad00000@gmail.com"


def require_test_account(account: Account = Depends(get_current_account)) -> Account:
    if account.email_normalized != TEST_ACCOUNT_EMAIL:
        raise HTTPException(status_code=403, detail="Test tools are restricted to the seed account")
    return account


# Dev endpoints (reset / migrate / regenerate / test-xp) are disabled by default.
# Enable only on trusted dev environments via ENABLE_DEV_ENDPOINTS=true.
ENABLE_DEV_ENDPOINTS = os.getenv("ENABLE_DEV_ENDPOINTS", "").lower() in ("1", "true", "yes")


def require_dev_enabled() -> None:
    if not ENABLE_DEV_ENDPOINTS:
        raise HTTPException(status_code=404, detail="Not found")


def get_current_player(
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Player:
    player = db.query(Player).filter(Player.account_id == account.id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player profile not found for this account")
    return player


def get_current_campaign(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
) -> Campaign:
    try:
        return get_active_campaign(db, player)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def get_optional_campaign(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
) -> Campaign | None:
    try:
        return get_active_campaign(db, player)
    except ValueError:
        return None


# parse_start_date imported from .seed


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
        reward_claimed=quest.reward_claimed,
        reward_claimed_at=quest.reward_claimed_at,
        completed_mode=quest.completed_mode,
        completion_note=quest.completion_note,
        raw_score=quest.raw_score,
        tracker_type=quest.tracker_type,
        tracker_entry_id=quest.tracker_entry_id,
        daily_slot_code=quest.daily_slot_code,
        error_log_id=quest.error_log_id,
        writing_entry_id=quest.writing_entry_id,
        speaking_entry_id=quest.speaking_entry_id,
        mock_test_id=quest.mock_test_id,
        expired_at=quest.expired_at,
        reward_skill_id=getattr(quest, "reward_skill_id", None),
        reward_skill_name=getattr(quest, "reward_skill", None).name if getattr(quest, "reward_skill", None) else None,
    )


def serialize_skill_state(state: CampaignSkillState, support_breakdown: list[SupportBreakdownItem] | None = None) -> SkillOut:
    skill = state.skill
    return SkillOut(
        id=skill.id,
        name=skill.name,
        icon=skill.icon,
        xp=state.xp,
        rank=state.rank,
        confirmed_rank=state.confirmed_rank,
        level=state.level,
        streak=state.streak,
        last_practiced=state.last_practiced,
        weak_point=state.weak_point,
        user_weakness_note=state.user_weakness_note,
        promotion_status=state.promotion_status,
        pending_rank=state.pending_rank,
        support_breakdown=support_breakdown or [],
    )


def get_campaign_skill_outputs(db: Session, campaign: Campaign) -> list[SkillOut]:
    state_map = get_campaign_skill_state_map(db, campaign)

    # Pre-compute support XP per source skill (Grammar, Collocation) for support_breakdown.
    # spec: ielts_xp_policy_rank_quest_spec.md §1.1, §4
    support_xp_by_name: dict[str, int] = {}
    for src_name in SUPPORT_ROUTING:
        src_skill = db.query(Skill).filter(Skill.name == src_name).first()
        if src_skill:
            xp = (
                db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
                .filter(
                    Quest.campaign_id == campaign.id,
                    Quest.skill_id == src_skill.id,
                    Quest.session_type != "Main Quest",
                    Quest.completed == True,
                    Quest.reward_claimed == True,
                )
                .scalar()
                or 0
            )
            support_xp_by_name[src_name] = int(xp)

    # Build target→[breakdown items] map
    breakdown_by_target: dict[str, list[SupportBreakdownItem]] = {}
    for src_name, tgt_name in SUPPORT_ROUTING.items():
        item = SupportBreakdownItem(source=src_name, xp=support_xp_by_name.get(src_name, 0))
        breakdown_by_target.setdefault(tgt_name, []).append(item)

    # Only emit matrix skills (5 tiles); support sources excluded from the tile list.
    result: list[SkillOut] = []
    states = sorted(state_map.values(), key=lambda s: s.skill.id if s.skill else s.skill_id)
    for state in states:
        skill_name = state.skill.name if state.skill else ""
        if skill_name not in MATRIX_SKILLS:
            continue
        breakdown = breakdown_by_target.get(skill_name, [])
        result.append(serialize_skill_state(state, support_breakdown=breakdown))
    return result


def get_campaign_badge_outputs(db: Session, player: Player, campaign: Campaign) -> list[BadgeOut]:
    unlock_map = {
        item.badge_id: item
        for item in db.query(BadgeUnlock).filter(BadgeUnlock.campaign_id == campaign.id).all()
    }
    badges = db.query(Badge).order_by(Badge.id).all()
    return [
        BadgeOut(
            id=badge.id,
            name=badge.name,
            icon=badge.icon,
            description=badge.description,
            unlocked=badge.id in unlock_map,
            unlocked_at=unlock_map[badge.id].unlocked_at if badge.id in unlock_map else None,
        )
        for badge in badges
    ]


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


class RefreshTokenIn(BaseModel):
    refresh_token: str | None = None


REFRESH_COOKIE = "ielts_rt"


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=30 * 24 * 3600,
        path="/api/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/auth")


@app.post("/api/auth/register", response_model=TokenOut)
def register(account_in: AccountRegisterIn, response: Response, db: Session = Depends(get_db)):
    email_normalized = account_in.email.strip().lower()
    existing = db.query(Account).filter(Account.email_normalized == email_normalized).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    name = (account_in.display_name or "").strip() or email_normalized.split("@")[0] or "New Hunter"

    account = Account(
        email=account_in.email,
        email_normalized=email_normalized,
        password_hash=hash_password(account_in.password),
        display_name=name,
        status="active",
        role="user",
        onboarding_completed=False
    )
    db.add(account)
    db.flush()

    player = Player(
        name=name,
        display_name=name,
        start_date=parse_start_date(),
        setup_completed=False,
        account_id=account.id
    )
    db.add(player)
    
    pref = AccountPreference(
        account_id=account.id,
        locale="vi",
        timezone="Asia/Ho_Chi_Minh",
        theme="dark",
        notification_enabled=True
    )
    db.add(pref)
    
    profile = PlayerLearningProfile(
        player=player,
        preferred_learning_style="mixed",
        dictionary_mode="bilingual_first",
        pronunciation_focus=True,
        collocation_focus=True,
        native_language="vi",
        interface_learning_language="mixed"
    )
    db.add(profile)
    db.flush()

    import base64
    import hashlib
    refresh_token = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    refresh_token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
    
    session = AccountSession(
        account_id=account.id,
        refresh_token_hash=refresh_token_hash,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    
    event = AccountSecurityEvent(
        account_id=account.id,
        event_type="register",
        email_attempted=email_normalized,
        success=True
    )
    db.add(event)
    db.commit()
    
    access_token = create_jwt({"sub": str(account.id)})
    set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token)


@app.post("/api/auth/login", response_model=TokenOut)
def login(login_in: AccountLoginIn, response: Response, db: Session = Depends(get_db)):
    email_normalized = login_in.email.strip().lower()
    account = db.query(Account).filter(Account.email_normalized == email_normalized).first()
    
    if account and account.status == "locked":
        if account.locked_until and account.locked_until > datetime.utcnow():
            raise HTTPException(status_code=403, detail="Account is locked. Try again later.")
        else:
            account.status = "active"
            account.failed_login_count = 0
            db.commit()

    if not account or not verify_password(login_in.password, account.password_hash):
        if account:
            account.failed_login_count += 1
            if account.failed_login_count >= 5:
                account.status = "locked"
                account.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.add(AccountSecurityEvent(
                account_id=account.id,
                event_type="login_failed",
                email_attempted=email_normalized,
                success=False,
                detail="Invalid password"
            ))
            db.commit()
        else:
            db.add(AccountSecurityEvent(
                event_type="login_failed",
                email_attempted=email_normalized,
                success=False,
                detail="Account not found"
            ))
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")
            
    account.failed_login_count = 0
    account.last_login_at = datetime.utcnow()
    
    import base64
    import hashlib
    refresh_token = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    refresh_token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
    
    session = AccountSession(
        account_id=account.id,
        refresh_token_hash=refresh_token_hash,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    
    db.add(AccountSecurityEvent(
        account_id=account.id,
        event_type="login_success",
        email_attempted=email_normalized,
        success=True
    ))
    db.commit()
    
    access_token = create_jwt({"sub": str(account.id)})
    set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token)


@app.post("/api/auth/refresh", response_model=TokenOut)
def refresh(
    response: Response,
    token_in: RefreshTokenIn | None = None,
    ielts_rt: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    raw_token = ielts_rt or (token_in.refresh_token if token_in else None)
    if not raw_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    import hashlib
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    session = db.query(AccountSession).filter(
        AccountSession.refresh_token_hash == token_hash,
        AccountSession.revoked_at == None
    ).first()

    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    import base64
    new_refresh_token = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    new_hash = hashlib.sha256(new_refresh_token.encode('utf-8')).hexdigest()

    session.refresh_token_hash = new_hash
    session.last_used_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(days=30)

    db.add(AccountSecurityEvent(
        account_id=session.account_id,
        event_type="refresh_token_used",
        success=True
    ))
    db.commit()

    access_token = create_jwt({"sub": str(session.account_id)})
    set_refresh_cookie(response, new_refresh_token)
    return TokenOut(access_token=access_token)


@app.post("/api/auth/logout")
def logout(
    response: Response,
    token_in: RefreshTokenIn | None = None,
    ielts_rt: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    raw_token = ielts_rt or (token_in.refresh_token if token_in else None)
    if raw_token:
        import hashlib
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        session = db.query(AccountSession).filter(AccountSession.refresh_token_hash == token_hash).first()
        if session:
            session.revoked_at = datetime.utcnow()
            session.revoke_reason = "User logged out"
            db.add(AccountSecurityEvent(
                account_id=session.account_id,
                event_type="logout",
                success=True
            ))
            db.commit()
    clear_refresh_cookie(response)
    return {"detail": "Successfully logged out"}


@app.get("/api/auth/me", response_model=MeResponseOut)
def me(account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.account_id == account.id).first()
    campaign = None
    if player and player.active_campaign_id:
        campaign = db.query(Campaign).filter(Campaign.id == player.active_campaign_id).first()
        
    return MeResponseOut(
        account=account,
        player=player,
        campaign=campaign
    )


@app.get("/api/onboarding/status", response_model=OnboardingStatusOut)
def onboarding_status(
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    player = db.query(Player).filter(Player.account_id == account.id).first()
    has_certificate = False
    if player:
        has_certificate = db.query(CertificateRecord).filter(CertificateRecord.player_id == player.id).first() is not None
    return OnboardingStatusOut(
        onboarding_completed=account.onboarding_completed,
        has_certificate=has_certificate
    )


@app.post("/api/onboarding/activate-campaign")
def activate_campaign(
    body: OnboardingActivateIn | None = None,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db)
):
    player = db.query(Player).filter(Player.account_id == account.id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player profile not found")

    if body and body.display_name and body.display_name.strip():
        player.display_name = body.display_name.strip()
        player.name = body.display_name.strip()

    # Persist target bands from onboarding (overall + 4 skills)
    if body:
        overall = body.target_overall_band or body.target_band
        if overall and overall.strip():
            player.target_overall_band = overall.strip()
            player.target = f"IELTS Academic {overall.strip()}"
        if body.target_listening_band:
            player.target_listening_band = body.target_listening_band.strip()
        if body.target_reading_band:
            player.target_reading_band = body.target_reading_band.strip()
        if body.target_writing_band:
            player.target_writing_band = body.target_writing_band.strip()
        if body.target_speaking_band:
            player.target_speaking_band = body.target_speaking_band.strip()

    template_code = (body.campaign_template_code if body else None) or "ielts_18_month_foundation"
    start_date = (body.start_date if body else None)

    # Activate the campaign
    campaign = activate_campaign_for_player(db, player, template_code=template_code, start_date=start_date)

    # Link pre-existing certificate records to campaign and generate suggestions
    certs = db.query(CertificateRecord).filter(
        CertificateRecord.player_id == player.id,
        CertificateRecord.campaign_id == None
    ).all()
    for cert in certs:
        cert.campaign_id = campaign.id
        db.flush()
        create_rank_suggestions_for_certificate(db, cert)

    # Mark onboarding and campaign setup completed atomically
    account.onboarding_completed = True
    account.onboarding_completed_at = datetime.utcnow()

    db.commit()

    # Recompute/refresh progression state
    refresh_progress_state(db, player=player, campaign=campaign)
    
    return {"detail": "Campaign activated successfully"}


@app.get("/api/summary", response_model=SummaryOut)
def get_summary(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    refresh_progress_state(db, player=player, campaign=campaign)
    week_start, week_end = current_week_window(player)
    today = max(date.today(), player.start_date)

    today_xp = (
        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
        .filter(Quest.completed == True, Quest.reward_claimed == True, Quest.quest_date == today, Quest.campaign_id == campaign.id)
        .scalar()
        or 0
    )
    week_xp = (
        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
        .filter(
            Quest.completed == True,
            Quest.reward_claimed == True,
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
    skills = get_campaign_skill_outputs(db, campaign)
    badges = get_campaign_badge_outputs(db, player, campaign)
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
def get_profile(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    refresh_progress_state(db, player=player, campaign=campaign)
    db.refresh(player)
    return player


@app.patch("/api/player/targets", response_model=PlayerProfileOut)
def patch_player_targets(
    payload: PlayerTargetsIn,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    if payload.target_overall_band is not None:
        player.target_overall_band = payload.target_overall_band.strip()
        player.target = f"IELTS Academic {payload.target_overall_band.strip()}"
    if payload.target_listening_band is not None:
        player.target_listening_band = payload.target_listening_band.strip()
    if payload.target_reading_band is not None:
        player.target_reading_band = payload.target_reading_band.strip()
    if payload.target_writing_band is not None:
        player.target_writing_band = payload.target_writing_band.strip()
    if payload.target_speaking_band is not None:
        player.target_speaking_band = payload.target_speaking_band.strip()
    db.commit()
    refresh_progress_state(db, player=player, campaign=campaign)
    db.refresh(player)
    return player


@app.post("/api/setup", response_model=PlayerProfileOut)
def post_setup(payload: SetupIn, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
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
    refresh_progress_state(db, player=player, campaign=campaign)
    db.refresh(player)
    return player


@app.get("/api/campaigns/current", response_model=CampaignOut)
def get_current_campaign_route(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return campaign


@app.get("/api/skills", response_model=list[SkillOut])
def get_skills(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    refresh_progress_state(db, player=player, campaign=campaign)
    return get_campaign_skill_outputs(db, campaign)


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
def get_roadmap_phases(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    campaign = campaign
    return (
        db.query(RoadmapPhase)
        .options(joinedload(RoadmapPhase.phase_materials).joinedload(PhaseMaterial.material))
        .filter(RoadmapPhase.campaign_id == campaign.id)
        .order_by(RoadmapPhase.phase_order)
        .all()
    )


@app.get("/api/study-plan/weeks", response_model=list[StudyPlanWeekOut])
def get_study_plan_weeks(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return (
        db.query(StudyPlanWeek)
        .options(joinedload(StudyPlanWeek.sessions))
        .filter(StudyPlanWeek.campaign_id == campaign.id)
        .order_by(StudyPlanWeek.week_no)
        .all()
    )


@app.get("/api/study-plan/current-week", response_model=StudyPlanWeekOut)
def get_current_study_plan_week(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
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
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
    week_no: int | None = Query(default=None),
    phase_id: int | None = Query(default=None),
):
    refresh_progress_state(db, player=player, campaign=campaign)
    query = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material), joinedload(Quest.reward_skill))
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
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    stage: str | None = Query(default=None),
    week_no: int | None = Query(default=None),
    phase_id: int | None = Query(default=None),
    material_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    refresh_progress_state(db, player=player, campaign=campaign)
    if not start and not end and not week_no and not stage and not phase_id and not material_id and not status:
        start, end = current_week_window(player)

    query = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material), joinedload(Quest.reward_skill))
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
def get_today_quests(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    refresh_progress_state(db, player=player, campaign=campaign)
    today = date.today()
    quests = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material), joinedload(Quest.reward_skill))
        .filter(Quest.campaign_id == campaign.id, Quest.quest_date == today, Quest.session_type == "Daily Quest")
        .order_by(Quest.id)
        .all()
    )
    return [serialize_quest(quest) for quest in quests]


@app.post("/api/quests/{quest_id}/complete", response_model=QuestOut)
def complete_quest(quest_id: int, payload: QuestCompletionIn | None = None, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    quest = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material), joinedload(Quest.reward_skill))
        .filter(Quest.id == quest_id, Quest.campaign_id == campaign.id)
        .first()
    )
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    payload = payload or QuestCompletionIn()
    try:
        return serialize_quest(
            complete_quest_instance(
                db,
                quest,
                tracker_type=payload.tracker_type,
                tracker_entry_id=payload.tracker_entry_id,
                error_log_id=payload.error_log_id,
                writing_entry_id=payload.writing_entry_id,
                speaking_entry_id=payload.speaking_entry_id,
                mock_test_id=payload.mock_test_id,
                raw_score=payload.raw_score,
                completion_note=payload.completion_note,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/quests/{quest_id}/uncomplete", response_model=QuestOut)
def uncomplete_quest(quest_id: int, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    quest = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material), joinedload(Quest.reward_skill))
        .filter(Quest.id == quest_id, Quest.campaign_id == campaign.id)
        .first()
    )
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return serialize_quest(uncomplete_quest_instance(db, quest))


@app.post("/api/quests/{quest_id}/claim", response_model=QuestOut)
def claim_quest_reward(quest_id: int, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    quest = (
        db.query(Quest)
        .options(joinedload(Quest.skill), joinedload(Quest.phase), joinedload(Quest.material), joinedload(Quest.reward_skill))
        .filter(Quest.id == quest_id, Quest.campaign_id == campaign.id)
        .first()
    )
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    if not quest.completed:
        raise HTTPException(status_code=400, detail="Quest must be completed before claiming reward")
    if quest.reward_claimed:
        raise HTTPException(status_code=400, detail="Quest reward has already been claimed")

    idempotency_key = f"quest_claim:{quest.id}"
    xp_amount = int(quest.earned_xp or quest.base_xp or 0)

    # XP block: if skill is locked behind boss exam, suppress skill XP award
    skill_blocked = False
    if quest.skill_id:
        skill_state = db.query(CampaignSkillState).filter(
            CampaignSkillState.campaign_id == campaign.id,
            CampaignSkillState.skill_id == quest.skill_id,
        ).first()
        if skill_state and skill_state.promotion_status in {"boss_required", "in_progress"}:
            skill_blocked = True

    if skill_blocked:
        # Boss exam not yet passed — do not mark reward_claimed so XP can be claimed
        # later once the block is lifted.  Return the current (unchanged) quest state.
        db.refresh(quest)
        return serialize_quest(quest)

    target_skill_id = getattr(quest, "reward_skill_id", None) or quest.skill_id
    if target_skill_id:
        services.award_skill_xp(db, campaign.id, target_skill_id, xp_amount, idempotency_key)

    quest.reward_claimed = True
    quest.reward_claimed_at = quest.reward_claimed_at or quest.completed_at
    db.commit()
    # Pass player+campaign so recompute_player_progress targets the correct account
    refresh_progress_state(db, player=player, campaign=campaign)
    db.refresh(quest)
    return serialize_quest(quest)


@app.get("/api/weekly-mission/current", response_model=WeeklyMissionOut)
def get_current_weekly_mission(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
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


@app.post("/api/weekly-missions/{mission_id}/claim", response_model=WeeklyMissionOut)
def claim_weekly_mission_reward(mission_id: int, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    mission = (
        db.query(WeeklyMission)
        .options(joinedload(WeeklyMission.items))
        .filter(WeeklyMission.id == mission_id, WeeklyMission.campaign_id == campaign.id)
        .first()
    )
    if not mission:
        raise HTTPException(status_code=404, detail="Weekly mission not found")
    if mission.status != "completed":
        raise HTTPException(status_code=400, detail="Weekly mission must be completed before claiming reward")
    if mission.reward_claimed:
        raise HTTPException(status_code=400, detail="Weekly mission reward has already been claimed")
    idempotency_key = f"weekly_mission_claim:{mission.id}"
    xp_amount = int(mission.reward_xp or 0)
    if getattr(mission, "reward_skill_id", None):
        services.award_skill_xp(db, campaign.id, mission.reward_skill_id, xp_amount, idempotency_key, transaction_type="weekly_mission")
    # no else: player never receives XP directly (spec: ielts_xp_policy_rank_quest_spec.md §1.2)

    mission.reward_claimed = True
    mission.reward_claimed_at = mission.reward_claimed_at or mission.completed_at
    db.commit()
    refresh_progress_state(db, player=player, campaign=campaign)
    db.refresh(mission)
    return mission


@app.post("/api/checkins", response_model=CheckInOut)
def upsert_checkin(payload: CheckInIn, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    item = (
        db.query(CheckIn)
        .filter(CheckIn.campaign_id == campaign.id, CheckIn.checkin_date == payload.checkin_date)
        .first()
    )
    if item:
        item.mood = payload.mood
        item.energy = payload.energy
        item.focus = payload.focus
        item.note = payload.note
    else:
        item = CheckIn(
            campaign_id=campaign.id,
            checkin_date=payload.checkin_date,
            mood=payload.mood,
            energy=payload.energy,
            focus=payload.focus,
            note=payload.note,
        )
        db.add(item)
    db.commit()
    refresh_progress_state(db, player=player, campaign=campaign)
    db.refresh(item)
    return item


@app.get("/api/checkins", response_model=list[CheckInOut])
def get_checkins(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db), start: date | None = None, end: date | None = None):
    query = db.query(CheckIn).filter(CheckIn.campaign_id == campaign.id)
    if start:
        query = query.filter(CheckIn.checkin_date >= start)
    if end:
        query = query.filter(CheckIn.checkin_date <= end)
    return query.order_by(CheckIn.checkin_date.desc()).limit(30).all()


@app.get("/api/badges", response_model=list[BadgeOut])
def get_badges(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    refresh_progress_state(db, player=player, campaign=campaign)
    return get_campaign_badge_outputs(db, player, campaign)


@app.get("/api/boss-battles", response_model=list[BossBattleOut])
def get_boss_battles(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return (
        db.query(BossBattle)
        .filter(BossBattle.campaign_id == campaign.id)
        .order_by(BossBattle.battle_date)
        .all()
    )


@app.post("/api/boss-battles/{battle_id}/claim", response_model=BossBattleOut)
def claim_boss_reward(battle_id: int, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    battle = db.query(BossBattle).filter(BossBattle.id == battle_id, BossBattle.campaign_id == campaign.id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="Boss battle not found")
    if not battle.cleared_at:
        raise HTTPException(status_code=400, detail="Boss must be cleared before claiming reward")
    if getattr(battle, "reward_claimed", False):
        raise HTTPException(status_code=400, detail="Boss reward already claimed")

    idempotency_key = f"boss_claim:{battle.id}"
    xp_amount = int(battle.reward_xp or 0)
    if getattr(battle, "reward_skill_id", None):
        services.award_skill_xp(db, campaign.id, battle.reward_skill_id, xp_amount, idempotency_key, transaction_type="boss")
    # no else: player never receives XP directly (spec: ielts_xp_policy_rank_quest_spec.md §1.2)

    battle.reward_claimed = True
    battle.reward_claimed_at = datetime.utcnow()
    db.commit()
    db.refresh(battle)
    return battle


@app.get("/api/test-records", response_model=list[TestRecordOut])
def get_test_records(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return (
        db.query(TestRecord)
        .filter(TestRecord.player_id == player.id)
        .order_by(TestRecord.test_date.desc(), TestRecord.id.desc())
        .all()
    )


@app.post("/api/test-records", response_model=TestRecordOut)
def create_test_record(payload: TestRecordIn, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    record = TestRecord(player_id=player.id, campaign_id=campaign.id, **payload.model_dump())
    db.add(record)
    db.flush()
    create_rank_suggestions_for_test(db, record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/rank-suggestions", response_model=list[SkillRankSuggestionOut])
@app.get("/api/skill-rank-suggestions", response_model=list[SkillRankSuggestionOut])
def get_rank_suggestions(
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
    include_resolved: bool = False
):
    query = (
        db.query(SkillRankSuggestion)
        .filter(SkillRankSuggestion.campaign_id == campaign.id)
        .order_by(SkillRankSuggestion.created_at.desc(), SkillRankSuggestion.id.desc())
    )
    if not include_resolved:
        query = query.filter(SkillRankSuggestion.status == "pending")
    return query.all()


@app.post("/api/rank-suggestions/{suggestion_id}/apply", response_model=SkillRankSuggestionOut)
@app.post("/api/skill-rank-suggestions/{suggestion_id}/apply", response_model=SkillRankSuggestionOut)
def post_apply_rank_suggestion(
    suggestion_id: int,
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    suggestion = (
        db.query(SkillRankSuggestion)
        .options(joinedload(SkillRankSuggestion.skill))
        .filter(SkillRankSuggestion.id == suggestion_id, SkillRankSuggestion.campaign_id == campaign.id)
        .first()
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="Rank suggestion not found")
    return apply_rank_suggestion(db, suggestion)


@app.post("/api/rank-suggestions/{suggestion_id}/dismiss", response_model=SkillRankSuggestionOut)
@app.post("/api/skill-rank-suggestions/{suggestion_id}/dismiss", response_model=SkillRankSuggestionOut)
def post_dismiss_rank_suggestion(
    suggestion_id: int,
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    suggestion = db.query(SkillRankSuggestion).filter(SkillRankSuggestion.id == suggestion_id, SkillRankSuggestion.campaign_id == campaign.id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Rank suggestion not found")
    return dismiss_rank_suggestion(db, suggestion)


@app.post("/api/certificates/manual", response_model=ManualCertificateOut)
def post_manual_certificate(
    cert_in: ManualCertificateIn,
    player: Player = Depends(get_current_player),
    campaign: Campaign | None = Depends(get_optional_campaign),
    db: Session = Depends(get_db)
):
    
    cert = CertificateRecord(
        player_id=player.id,
        campaign_id=campaign.id if campaign else None,
        certificate_type="IELTS",
        overall_score=cert_in.overall_score,
        listening_score=cert_in.listening_score,
        reading_score=cert_in.reading_score,
        writing_score=cert_in.writing_score,
        speaking_score=cert_in.speaking_score,
        input_method="manual",
        status="submitted"
    )
    db.add(cert)
    db.flush()
    
    # Generate suggestions immediately if campaign is active
    if campaign:
        create_rank_suggestions_for_certificate(db, cert)
        
    db.commit()
    db.refresh(cert)
    return cert


@app.get("/api/certificates", response_model=list[ManualCertificateOut])
def get_certificates(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    return (
        db.query(CertificateRecord)
        .filter(CertificateRecord.player_id == player.id)
        .order_by(CertificateRecord.created_at.desc(), CertificateRecord.id.desc())
        .all()
    )


@app.get("/api/error-logs", response_model=list[ErrorLogOut])
def get_error_logs(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return (
        db.query(ErrorLog)
        .filter(ErrorLog.campaign_id == campaign.id)
        .order_by(ErrorLog.logged_date.desc(), ErrorLog.id.desc())
        .all()
    )


@app.post("/api/error-logs", response_model=ErrorLogOut)
def create_error_log(payload: ErrorLogIn, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    item = ErrorLog(campaign_id=campaign.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/writing-entries", response_model=list[WritingEntryOut])
def get_writing_entries(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return (
        db.query(WritingEntry)
        .filter(WritingEntry.campaign_id == campaign.id)
        .order_by(WritingEntry.entry_date.desc(), WritingEntry.id.desc())
        .all()
    )


@app.post("/api/writing-entries", response_model=WritingEntryOut)
def create_writing_entry(payload: WritingEntryIn, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    item = WritingEntry(campaign_id=campaign.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/speaking-entries", response_model=list[SpeakingEntryOut])
def get_speaking_entries(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return (
        db.query(SpeakingEntry)
        .filter(SpeakingEntry.campaign_id == campaign.id)
        .order_by(SpeakingEntry.entry_date.desc(), SpeakingEntry.id.desc())
        .all()
    )


@app.post("/api/speaking-entries", response_model=SpeakingEntryOut)
def create_speaking_entry(payload: SpeakingEntryIn, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    item = SpeakingEntry(campaign_id=campaign.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/mock-tests", response_model=list[MockTestOut])
def get_mock_tests(campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    return (
        db.query(MockTest)
        .filter(MockTest.campaign_id == campaign.id)
        .order_by(MockTest.test_date.desc(), MockTest.id.desc())
        .all()
    )


@app.post("/api/mock-tests", response_model=MockTestOut)
def create_mock_test(payload: MockTestIn, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    data = payload.model_dump()
    if not data["estimated_band"]:
        data["estimated_band"] = estimate_band_from_mock(data["raw_score"], data["test_type"])
    item = MockTest(campaign_id=campaign.id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/weakness-suggestions", response_model=list[WeaknessSuggestionOut])
def get_weakness_suggestions(player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db), include_resolved: bool = False):
    refresh_progress_state(db, player=player, campaign=campaign)
    ensure_weakness_suggestions(db, campaign)
    query = (
        db.query(WeaknessSuggestion)
        .options(joinedload(WeaknessSuggestion.skill))
        .filter(WeaknessSuggestion.campaign_id == campaign.id)
        .order_by(WeaknessSuggestion.created_at.desc(), WeaknessSuggestion.id.desc())
    )
    if not include_resolved:
        query = query.filter(WeaknessSuggestion.status == "pending")
    return query.all()


@app.post("/api/weakness-suggestions/{suggestion_id}/apply", response_model=WeaknessSuggestionOut)
def post_apply_weakness_suggestion(suggestion_id: int, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    suggestion = (
        db.query(WeaknessSuggestion)
        .options(joinedload(WeaknessSuggestion.skill))
        .filter(WeaknessSuggestion.id == suggestion_id, WeaknessSuggestion.campaign_id == campaign.id)
        .first()
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="Weakness suggestion not found")
    return apply_weakness_suggestion(db, suggestion)


@app.post("/api/weakness-suggestions/{suggestion_id}/dismiss", response_model=WeaknessSuggestionOut)
def post_dismiss_weakness_suggestion(suggestion_id: int, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    suggestion = db.query(WeaknessSuggestion).filter(WeaknessSuggestion.id == suggestion_id, WeaknessSuggestion.campaign_id == campaign.id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Weakness suggestion not found")
    return dismiss_weakness_suggestion(db, suggestion)


@app.post("/api/dev/reset", dependencies=[Depends(require_dev_enabled)])
def reset_database(db: Session = Depends(get_db)):
    from sqlalchemy import text
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    db.commit()
    try:
        db.query(Player).update({Player.active_campaign_id: None, Player.account_id: None})
        db.query(Campaign).update({Campaign.campaign_template_id: None})
        db.flush()
        for model in [
            RankExamAnswer,
            RankExamAttempt,
            RankExamQuestion,
            RankExamVersion,
            RankExamPool,
            CertificateRecord,
            VocabularySetting,
            CampaignSkillQuestQuota,
            CampaignSetting,
            CampaignTemplateSkillQuota,
            CampaignTemplate,
            PlayerLearningProfile,
            AccountPreference,
            AccountSecurityEvent,
            AccountToken,
            AccountSession,
            Account,

            VocabularyError,
            VocabularyEdge,
            VocabularyNode,
            VocabularyTopic,

            SpacedRepetitionState,
            Flashcard,
            VocabularyRelation,
            VocabularyExample,
            VocabularyItem,
            BadgeUnlock,
            PlayerCollocationProgress,
            CollocationFlashcard,
            CampaignCollocationLink,
            CollocationItem,
            CollocationTopic,
            CollocationSection,
            CollocationCollection,
            CampaignSkillState,
            WeaknessSuggestion,
            SkillRankHistory,
            SkillRankSuggestion,
            CheckIn,
            Quest,
            WeeklyMissionItem,
            WeeklyMission,
            BossBattle,
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
            RankXpThreshold,
            QuestXpPolicy,
            WeeklyMissionXpPolicy,
            MainQuestXpPolicy,
            Skill,
            Campaign,
            Player,
        ]:
            db.query(model).delete()
        db.commit()
        seed_database(db, parse_start_date())
        refresh_progress_state(db)
    finally:
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.commit()

    # return counts for verification
    template_count = db.query(QuestTemplate).count()
    weekly_count = db.query(WeeklyMission).count()
    return {"status": "reset", "message": "Database has been reset and seeded again.", "quest_templates": template_count, "weekly_missions": weekly_count}


@app.post("/api/dev/run_migrations", dependencies=[Depends(require_dev_enabled)])
def run_migrations(db: Session = Depends(get_db)):
    """Run Alembic migrations (dev-only)."""
    try:
        cfg = AlembicConfig("alembic.ini")
        alembic_command.upgrade(cfg, "head")
        return {"status": "ok", "message": "Migrations applied (head)."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# --- Test XP Tool (seed account ad00000@gmail.com only) ---

@app.get("/api/dev/test-xp/skills", response_model=list[TestXpSkillOut], dependencies=[Depends(require_dev_enabled)])
def get_test_xp_skills(
    account: Account = Depends(require_test_account),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """List every skill with its current xp + manual_xp_bonus for the test panel."""
    refresh_progress_state(db)
    rows = (
        db.query(CampaignSkillState, Skill)
        .join(Skill, Skill.id == CampaignSkillState.skill_id)
        .filter(CampaignSkillState.campaign_id == campaign.id)
        .order_by(Skill.id)
        .all()
    )
    return [
        TestXpSkillOut(
            skill_id=state.skill_id,
            name=skill.name,
            xp=state.xp or 0,
            manual_xp_bonus=state.manual_xp_bonus or 0,
            rank=state.rank,
            level=state.level,
        )
        for state, skill in rows
    ]


@app.post("/api/dev/test-xp/award", response_model=TestXpSkillOut, dependencies=[Depends(require_dev_enabled)])
def award_test_xp(
    payload: TestXpAwardIn,
    account: Account = Depends(require_test_account),
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Add `delta` to a skill's manual_xp_bonus (floor 0), or reset it to 0.
    Survives refresh_progress_state via recompute_skill_progress."""
    state = (
        db.query(CampaignSkillState)
        .filter(
            CampaignSkillState.campaign_id == campaign.id,
            CampaignSkillState.skill_id == payload.skill_id,
        )
        .first()
    )
    if not state:
        raise HTTPException(status_code=404, detail="Skill state not found for this campaign")

    if payload.reset:
        state.manual_xp_bonus = 0
    else:
        state.manual_xp_bonus = max(0, (state.manual_xp_bonus or 0) + payload.delta)
    db.flush()
    refresh_progress_state(db, player, campaign)
    db.refresh(state)

    skill = db.query(Skill).filter(Skill.id == state.skill_id).first()
    return TestXpSkillOut(
        skill_id=state.skill_id,
        name=skill.name if skill else "",
        xp=state.xp or 0,
        manual_xp_bonus=state.manual_xp_bonus or 0,
        rank=state.rank,
        level=state.level,
    )


# --- Rank Exam Routes ---

@app.post("/api/rank-exams/unlock")
def unlock_rank_exam(payload: RankExamStartIn, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    """Transition eligible -> boss_required. Player explicitly chooses to start promotion process."""

    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if not skill.boss_gated:
        raise HTTPException(status_code=400, detail="This skill does not require a boss exam for promotion")

    state = db.query(CampaignSkillState).filter(
        CampaignSkillState.campaign_id == campaign.id,
        CampaignSkillState.skill_id == payload.skill_id,
    ).first()
    if not state:
        raise HTTPException(status_code=404, detail="Skill state not found")
    if state.promotion_status != "eligible":
        raise HTTPException(status_code=400, detail=f"Skill is not eligible for promotion (current: {state.promotion_status})")

    state.promotion_status = "boss_required"
    db.commit()
    return {"skill_id": payload.skill_id, "promotion_status": "boss_required", "pending_rank": state.pending_rank}


def _resume_in_progress_exam(db: Session, campaign: Campaign, state: CampaignSkillState) -> RankExamStartOut | None:
    """Return the live in-progress attempt for a skill as a RankExamStartOut, or None
    if no resumable attempt exists. Prefers the attempt the state points at, else the
    most recent in_progress one. Used so "Resume Exam" re-opens the running exam."""
    attempt = None
    if getattr(state, "last_rank_exam_attempt_id", None):
        attempt = db.query(RankExamAttempt).filter(
            RankExamAttempt.id == state.last_rank_exam_attempt_id,
            RankExamAttempt.campaign_id == campaign.id,
            RankExamAttempt.status == "in_progress",
        ).first()
    if not attempt:
        attempt = (
            db.query(RankExamAttempt)
            .filter(
                RankExamAttempt.campaign_id == campaign.id,
                RankExamAttempt.skill_id == state.skill_id,
                RankExamAttempt.status == "in_progress",
            )
            .order_by(RankExamAttempt.started_at.desc(), RankExamAttempt.id.desc())
            .first()
        )
    if not attempt:
        return None

    questions = db.query(RankExamQuestion).filter(
        RankExamQuestion.exam_version_id == attempt.exam_version_id,
    ).order_by(RankExamQuestion.order_index).all()

    return RankExamStartOut(
        attempt_id=attempt.id,
        skill_id=attempt.skill_id,
        from_rank=attempt.from_rank,
        to_rank=attempt.to_rank,
        time_limit_minutes=attempt.time_limit_minutes,
        expires_at=attempt.expires_at,
        questions=[
            RankExamQuestionOut(
                id=q.id,
                question_type=q.question_type,
                prompt=q.prompt,
                instruction=q.instruction,
                options_json=q.options_json,
            ) for q in questions
        ],
    )


@app.post("/api/rank-exams/start", response_model=RankExamStartOut)
def start_rank_exam(payload: RankExamStartIn, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    """Transition boss_required -> in_progress. Creates exam attempt, enforces 2/day cap.
    If the skill is already in_progress, resumes (returns the live attempt) instead of erroring."""

    state = db.query(CampaignSkillState).filter(
        CampaignSkillState.campaign_id == campaign.id,
        CampaignSkillState.skill_id == payload.skill_id,
    ).first()
    if not state:
        raise HTTPException(status_code=404, detail="Skill state not found")

    # Resume: an exam already in progress returns its current attempt instead of
    # erroring, so the "Resume Exam" action can re-open the live exam screen.
    if state.promotion_status == "in_progress":
        resume = _resume_in_progress_exam(db, campaign, state)
        if resume is not None:
            return resume
        # No live attempt found despite the in_progress flag — fall through and
        # treat it as a fresh start (defensive; keeps the skill unblockable).

    if state.promotion_status != "boss_required":
        raise HTTPException(status_code=400, detail=f"Exam not unlocked for this skill (current: {state.promotion_status})")
    if not state.pending_rank or not state.confirmed_rank:
        raise HTTPException(status_code=400, detail="No pending rank transition found")

    # Enforce 2 attempts/day cap
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    attempts_today = db.query(RankExamAttempt).filter(
        RankExamAttempt.campaign_id == campaign.id,
        RankExamAttempt.skill_id == payload.skill_id,
        RankExamAttempt.from_rank == state.confirmed_rank,
        RankExamAttempt.started_at >= today_start,
    ).count()
    if attempts_today >= 2:
        raise HTTPException(status_code=429, detail="Daily attempt limit reached (max 2/day). Try again tomorrow.")

    # Find active exam pool for this rank transition
    pool = db.query(RankExamPool).filter(
        RankExamPool.skill_id == payload.skill_id,
        RankExamPool.from_rank == state.confirmed_rank,
        RankExamPool.to_rank == state.pending_rank,
        RankExamPool.is_active == True,
    ).first()
    if not pool:
        raise HTTPException(status_code=404, detail="No exam pool found for this rank transition")

    # Pick a random active version not used today
    used_version_ids = [
        a.exam_version_id for a in db.query(RankExamAttempt).filter(
            RankExamAttempt.campaign_id == campaign.id,
            RankExamAttempt.skill_id == payload.skill_id,
            RankExamAttempt.from_rank == state.confirmed_rank,
            RankExamAttempt.started_at >= today_start,
        ).all()
    ]
    version_query = db.query(RankExamVersion).filter(
        RankExamVersion.pool_id == pool.id,
        RankExamVersion.is_active == True,
    )
    if used_version_ids:
        version_query = version_query.filter(RankExamVersion.id.notin_(used_version_ids))
    version = version_query.first()
    if not version:
        # Fall back to any active version if all used
        version = db.query(RankExamVersion).filter(
            RankExamVersion.pool_id == pool.id,
            RankExamVersion.is_active == True,
        ).first()
    if not version:
        raise HTTPException(status_code=404, detail="No exam version available")

    time_limit = version.time_limit_minutes or pool.default_time_limit_minutes
    now = datetime.utcnow()
    attempt = RankExamAttempt(
        campaign_id=campaign.id,
        skill_id=payload.skill_id,
        from_rank=state.confirmed_rank,
        to_rank=state.pending_rank,
        pool_id=pool.id,
        exam_version_id=version.id,
        status="in_progress",
        total_points=version.total_points,
        pass_percent=pool.pass_percent,
        time_limit_minutes=time_limit,
        started_at=now,
        expires_at=now + timedelta(minutes=time_limit),
    )
    db.add(attempt)
    state.promotion_status = "in_progress"
    db.flush()
    state.last_rank_exam_attempt_id = attempt.id
    db.commit()

    questions = db.query(RankExamQuestion).filter(
        RankExamQuestion.exam_version_id == version.id,
    ).order_by(RankExamQuestion.order_index).all()

    return RankExamStartOut(
        attempt_id=attempt.id,
        skill_id=payload.skill_id,
        from_rank=attempt.from_rank,
        to_rank=attempt.to_rank,
        time_limit_minutes=time_limit,
        expires_at=attempt.expires_at,
        questions=[
            RankExamQuestionOut(
                id=q.id,
                question_type=q.question_type,
                prompt=q.prompt,
                instruction=q.instruction,
                options_json=q.options_json,
            ) for q in questions
        ],
    )


@app.get("/api/rank-exams/status/{skill_id}", response_model=RankExamStatusOut)
def get_rank_exam_status(skill_id: int, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    """Return promotion state and remaining daily attempts for a skill."""
    state = db.query(CampaignSkillState).filter(
        CampaignSkillState.campaign_id == campaign.id,
        CampaignSkillState.skill_id == skill_id,
    ).first()
    if not state:
        raise HTTPException(status_code=404, detail="Skill state not found")

    daily_cap = 2
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    attempts_today = db.query(RankExamAttempt).filter(
        RankExamAttempt.campaign_id == campaign.id,
        RankExamAttempt.skill_id == skill_id,
        RankExamAttempt.from_rank == state.confirmed_rank,
        RankExamAttempt.started_at >= today_start,
    ).count()

    return RankExamStatusOut(
        skill_id=skill_id,
        promotion_status=state.promotion_status or "none",
        confirmed_rank=state.confirmed_rank,
        pending_rank=state.pending_rank,
        daily_cap=daily_cap,
        attempts_today=attempts_today,
        attempts_remaining=max(0, daily_cap - attempts_today),
    )


@app.get("/api/rank-exams/{attempt_id}", response_model=RankExamAttemptOut)
def get_rank_exam_attempt(attempt_id: int, campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    attempt = db.query(RankExamAttempt).filter(
        RankExamAttempt.id == attempt_id,
        RankExamAttempt.campaign_id == campaign.id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    return attempt


@app.post("/api/rank-exams/{attempt_id}/submit", response_model=RankExamSubmitOut)
def submit_rank_exam(attempt_id: int, payload: RankExamSubmitIn, player: Player = Depends(get_current_player), campaign: Campaign = Depends(get_current_campaign), db: Session = Depends(get_db)):
    """Grade exam, update confirmed_rank on pass, apply XP penalty on daily cap hit."""

    attempt = db.query(RankExamAttempt).filter(
        RankExamAttempt.id == attempt_id,
        RankExamAttempt.campaign_id == campaign.id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    if attempt.status != "in_progress":
        raise HTTPException(status_code=400, detail=f"Attempt already finalized (status: {attempt.status})")

    now = datetime.utcnow()
    timed_out = attempt.expires_at and now > attempt.expires_at

    state = db.query(CampaignSkillState).filter(
        CampaignSkillState.campaign_id == campaign.id,
        CampaignSkillState.skill_id == attempt.skill_id,
    ).first()

    # Grade answers
    questions = {q.id: q for q in db.query(RankExamQuestion).filter(
        RankExamQuestion.exam_version_id == attempt.exam_version_id,
    ).all()}

    score_points = 0
    for ans_in in payload.answers:
        q = questions.get(ans_in.question_id)
        if not q:
            continue
        is_correct = not timed_out and (ans_in.answer_json == q.correct_answer_json)
        points_awarded = q.points if is_correct else 0
        score_points += points_awarded
        db.add(RankExamAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            answer_json=ans_in.answer_json,
            is_correct=is_correct,
            points_awarded=points_awarded,
            answered_at=now,
        ))

    score_percent = round((score_points / attempt.total_points) * 100, 2) if attempt.total_points else 0.0
    passed = not timed_out and score_percent >= attempt.pass_percent

    attempt.score_points = score_points
    attempt.score_percent = score_percent
    attempt.passed = passed
    attempt.submitted_at = now
    attempt.status = "passed" if passed else ("expired" if timed_out else "failed")

    confirmed_rank = attempt.from_rank

    if passed and state:
        # Promote rank
        old_rank = state.confirmed_rank
        state.confirmed_rank = attempt.to_rank
        state.rank = attempt.to_rank
        state.pending_rank = None
        state.promotion_status = "none"
        state.promotion_unlocked_at = None
        confirmed_rank = attempt.to_rank
        db.add(SkillRankHistory(
            skill_id=attempt.skill_id,
            campaign_id=campaign.id,
            old_rank=old_rank,
            new_rank=attempt.to_rank,
            change_reason=f"Passed rank exam attempt {attempt.id}",
        ))
    apply_xp_penalty = False
    if not passed and state:
        # Count today's attempts (including this one)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        attempts_today = db.query(RankExamAttempt).filter(
            RankExamAttempt.campaign_id == campaign.id,
            RankExamAttempt.skill_id == attempt.skill_id,
            RankExamAttempt.from_rank == attempt.from_rank,
            RankExamAttempt.started_at >= today_start,
        ).count()

        if attempts_today >= 2:
            state.promotion_status = "eligible"
            apply_xp_penalty = True
        else:
            state.promotion_status = "boss_required"

    db.commit()
    services.refresh_progress_state(db, player=player, campaign=campaign)

    # Apply XP penalty after refresh so recompute doesn't override it
    if apply_xp_penalty and state:
        db.refresh(state)
        state.xp = max(0, (state.xp or 0) - 50)
        db.commit()

    return RankExamSubmitOut(
        attempt_id=attempt.id,
        passed=passed,
        score_percent=score_percent,
        score_points=score_points,
        total_points=attempt.total_points,
        confirmed_rank=confirmed_rank,
    )


@app.post("/api/dev/regenerate-quests", dependencies=[Depends(require_dev_enabled)])
def regenerate_quests(
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Re-run daily quest generator for the logged-in user's active campaign (dev-only)."""
    skill_by_name = ensure_skills(db)
    phase_by_code = ensure_roadmap_phases(db, campaign)
    material_by_title = {m.title: m for m in db.query(StudyMaterial).all()}
    template_by_title = ensure_templates(db, skill_by_name, phase_by_code, material_by_title)
    before_count = db.query(Quest).filter(Quest.campaign_id == campaign.id, Quest.session_type == "Daily Quest").count()
    ensure_quest_instances(db, campaign, skill_by_name, template_by_title, phase_by_code)
    db.commit()
    after_count = db.query(Quest).filter(Quest.campaign_id == campaign.id, Quest.session_type == "Daily Quest").count()
    return {
        "status": "ok",
        "campaign_id": campaign.id,
        "quests_before": before_count,
        "quests_after": after_count,
        "quests_added": after_count - before_count,
    }


# --- Vocabulary Support Skill Routes ---

@app.get("/api/vocabulary", response_model=list[VocabularyItemOut])
def get_vocabulary_items(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_vocabulary_items(db, player.id)


@app.get("/api/vocabulary/{item_id}", response_model=VocabularyItemOut)
def get_vocabulary_item(item_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id, VocabularyItem.player_id == player.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")
    return services.get_vocabulary_item(db, item_id)


@app.post("/api/vocabulary", response_model=VocabularyItemOut)
def create_vocabulary_item(item_in: VocabularyItemIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    item = services.create_vocabulary_item(db, player.id, item_in)
    refresh_progress_state(db)
    return services.get_vocabulary_item(db, item.id)


@app.put("/api/vocabulary/{item_id}", response_model=VocabularyItemOut)
def update_vocabulary_item(item_id: int, item_in: VocabularyItemIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    owned = db.query(VocabularyItem).filter(VocabularyItem.id == item_id, VocabularyItem.player_id == player.id).first()
    if not owned:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")
    item = services.update_vocabulary_item(db, item_id, item_in)
    refresh_progress_state(db)
    return item


@app.delete("/api/vocabulary/{item_id}")
def delete_vocabulary_item(item_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    owned = db.query(VocabularyItem).filter(VocabularyItem.id == item_id, VocabularyItem.player_id == player.id).first()
    if not owned:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")
    services.delete_vocabulary_item(db, item_id)
    refresh_progress_state(db)
    return {"status": "deleted", "message": "Vocabulary item has been deleted"}


@app.post("/api/vocabulary/{item_id}/examples", response_model=VocabularyExampleOut)
def create_vocabulary_example(item_id: int, example_in: VocabularyExampleIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id, VocabularyItem.player_id == player.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")
    example = services.create_vocabulary_example(db, player.id, item_id, example_in)
    refresh_progress_state(db)
    return example


@app.delete("/api/vocabulary/examples/{example_id}")
def delete_vocabulary_example(example_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    success = services.delete_vocabulary_example(db, example_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vocabulary example not found")
    refresh_progress_state(db)
    return {"status": "deleted", "message": "Vocabulary example has been deleted"}



@app.post("/api/vocabulary/relations", response_model=VocabularyRelationOut)
def create_vocabulary_relation(relation_in: VocabularyRelationIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    relation = services.create_vocabulary_relation(db, player.id, relation_in)
    refresh_progress_state(db)
    return relation


@app.delete("/api/vocabulary/relations/{relation_id}")
def delete_vocabulary_relation(relation_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    success = services.delete_vocabulary_relation(db, relation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vocabulary relation not found")
    refresh_progress_state(db)
    return {"status": "deleted", "message": "Vocabulary relation has been deleted"}


@app.get("/api/flashcards", response_model=list[FlashcardOut])
def get_flashcards(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_flashcards(db, player.id)


@app.post("/api/flashcards", response_model=FlashcardOut)
def create_flashcard(card_in: FlashcardIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.create_flashcard(db, player.id, card_in)


@app.get("/api/flashcards/due", response_model=list[FlashcardOut])
def get_due_flashcards(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_due_flashcards(db, player.id)


@app.post("/api/flashcards/{card_id}/review", response_model=SpacedRepetitionStateOut)
def review_flashcard(card_id: int, payload: ReviewFlashcardIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.player_id == player.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    try:
        state = services.review_flashcard(db, player.id, card_id, payload.result)
        refresh_progress_state(db)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/vocabulary/tree/topics", response_model=list[VocabularyTopicOut])
def get_vocabulary_topics(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_vocabulary_topics(db, player.id)


@app.post("/api/vocabulary/tree/topics", response_model=VocabularyTopicOut)
def create_vocabulary_topic(topic_in: VocabularyTopicIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.create_vocabulary_topic(db, player.id, topic_in)


@app.get("/api/vocabulary/tree/{topic_id}", response_model=VocabularyTreeOut)
def get_vocabulary_tree(topic_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    topic, nodes, edges = services.get_topic_tree(db, player.id, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"topic": topic, "nodes": nodes, "edges": edges}


@app.post("/api/vocabulary/tree/nodes", response_model=VocabularyNodeOut)
def create_vocabulary_node(node_in: VocabularyNodeIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    topic = db.query(VocabularyTopic).filter(VocabularyTopic.id == node_in.topic_id, VocabularyTopic.player_id == player.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if node_in.vocabulary_item_id:
        item = db.query(VocabularyItem).filter(VocabularyItem.id == node_in.vocabulary_item_id, VocabularyItem.player_id == player.id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Vocabulary item not found")
    node = services.create_vocabulary_node(db, player.id, node_in)
    refresh_progress_state(db)
    return node


@app.patch("/api/vocabulary/tree/nodes/{node_id}", response_model=VocabularyNodeOut)
def update_vocabulary_node(node_id: int, node_in: VocabularyNodeUpdate, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    node = services.update_vocabulary_node(db, player.id, node_id, node_in)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    refresh_progress_state(db)
    return node


@app.post("/api/vocabulary/tree/edges", response_model=VocabularyEdgeOut)
def create_vocabulary_edge(edge_in: VocabularyEdgeIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    src = db.query(VocabularyNode).filter(VocabularyNode.id == edge_in.source_node_id, VocabularyNode.player_id == player.id).first()
    tgt = db.query(VocabularyNode).filter(VocabularyNode.id == edge_in.target_node_id, VocabularyNode.player_id == player.id).first()
    if not src or not tgt:
        raise HTTPException(status_code=404, detail="Source or target node not found")
    edge = services.create_vocabulary_edge(db, player.id, edge_in)
    refresh_progress_state(db)
    return edge


@app.delete("/api/vocabulary/tree/edges/{edge_id}")
def delete_vocabulary_edge(edge_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    success = services.delete_vocabulary_edge(db, player.id, edge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Edge not found")
    refresh_progress_state(db)
    return {"status": "deleted", "message": "Edge has been deleted"}


@app.post("/api/vocabulary/tree/sync-all")
def sync_all_nodes(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    items = db.query(VocabularyItem).filter(VocabularyItem.player_id == player.id).all()
    for item in items:
        services.sync_node_status_from_item(db, player.id, item.id)
    return {"status": "synced", "message": f"Synced statuses for all nodes of player {player.id}"}


@app.get("/api/collocation-collections", response_model=list[CollocationCollectionOut])
def get_collocation_collections_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_collocation_collections(db, skip=skip, limit=limit)


@app.post("/api/collocation-collections", response_model=CollocationCollectionOut)
def create_collocation_collection_endpoint(collection_in: CollocationCollectionIn, db: Session = Depends(get_db)):
    db_collection = services.get_collocation_collection_by_code(db, collection_in.code)
    if db_collection:
        raise HTTPException(status_code=400, detail="Collection code already exists")
    return services.create_collocation_collection(db, collection_in)


@app.get("/api/collocation-collections/{collection_id}", response_model=CollocationCollectionOutline)
def get_collocation_collection_outline_endpoint(collection_id: int, db: Session = Depends(get_db)):
    collection = services.get_collocation_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collocation collection not found")
    return collection


@app.get("/api/collocation-collections/{collection_id}/progress", response_model=CollocationCollectionOutlineWithProgress)
def get_collocation_collection_progress_endpoint(
    collection_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    collection = services.get_collocation_outline_with_progress(db, player_id=player.id, campaign_id=campaign.id, collection_id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collocation collection not found")
    return collection


@app.post("/api/campaigns/current/collocation-collections/{collection_id}/link", response_model=CampaignCollocationLinkOut)
def link_collection_endpoint(
    collection_id: int,
    display_order: int = 0,
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    collection = services.get_collocation_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collocation collection not found")
    return services.link_collection_to_campaign(db, campaign_id=campaign.id, collection_id=collection_id, display_order=display_order)


@app.delete("/api/campaigns/current/collocation-collections/{collection_id}/link")
def unlink_collection_endpoint(
    collection_id: int,
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    success = services.unlink_collection_from_campaign(db, campaign_id=campaign.id, collection_id=collection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"detail": "Collection unlinked successfully"}


@app.get("/api/campaigns/current/collocation-collections", response_model=list[CollocationCollectionOut])
def get_campaign_collections_endpoint(
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    return services.get_campaign_collections(db, campaign_id=campaign.id)


@app.post("/api/collocation-items/{item_id}/progress", response_model=PlayerCollocationProgressOut)
def update_collocation_progress_endpoint(
    item_id: int,
    status: str | None = None,
    correct: bool | None = None,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db)
):
    item = services.get_collocation_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Collocation item not found")
    return services.update_player_collocation_progress(db, player_id=player.id, campaign_id=campaign.id, collocation_item_id=item_id, status=status, correct=correct)


@app.get("/api/vocabulary/practice/collocations", response_model=CollocationPracticeResponse)
def get_collocation_practice_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_collocation_practice(db, player.id)


@app.get("/api/vocabulary/practice/shadow-duel", response_model=ShadowDuelResponse)
def get_shadow_duel_practice_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_shadow_duel_practice(db, player.id)


@app.post("/api/vocabulary/practice/record-success")
def record_practice_success_endpoint(payload: PracticeSuccessIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    result = services.record_practice_success(db, player.id, payload.words)
    refresh_progress_state(db)
    return result


@app.get("/api/vocabulary/practice/word-family", response_model=WordFamilyResponse)
def get_word_family_practice_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_word_families_practice(db, player.id)


@app.get("/api/vocabulary/practice/echo-chamber", response_model=EchoChamberResponse)
def get_echo_chamber_practice_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_echo_chamber_practice(db, player.id)


@app.post("/api/vocabulary/errors", response_model=VocabularyErrorOut)
def create_vocabulary_error_endpoint(payload: VocabularyErrorIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    error = services.create_vocabulary_error(db, player.id, payload)
    refresh_progress_state(db)
    return error


@app.get("/api/vocabulary/errors/active", response_model=list[VocabularyErrorOut])
def get_active_vocabulary_errors_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_active_vocabulary_errors(db, player.id)


@app.get("/api/vocabulary/errors", response_model=list[VocabularyErrorOut])
def get_all_vocabulary_errors_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_all_vocabulary_errors(db, player.id)


@app.patch("/api/vocabulary/errors/{error_id}", response_model=VocabularyErrorOut)
def update_vocabulary_error_endpoint(error_id: int, payload: VocabularyErrorIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    error = services.update_vocabulary_error(db, player.id, error_id, payload)
    if not error:
        raise HTTPException(status_code=404, detail="Vocabulary error not found")
    refresh_progress_state(db)
    return error


@app.post("/api/vocabulary/errors/{error_id}/defeat", response_model=VocabularyErrorOut)
def defeat_vocabulary_error_endpoint(error_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    error = services.defeat_vocabulary_error(db, player.id, error_id)
    if not error:
        raise HTTPException(status_code=404, detail="Vocabulary error not found")
    refresh_progress_state(db)
    return error


@app.get("/api/vocabulary/boss/status")
def get_vocabulary_boss_status_endpoint(player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    return services.get_vocabulary_boss_status(db, player.id)


@app.post("/api/vocabulary/boss/{boss_id}/challenge", response_model=VocabularyBossExam)
def challenge_vocabulary_boss_endpoint(boss_id: int, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    if boss_id not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Invalid boss ID")
    status = services.get_vocabulary_boss_status(db, player.id)
    boss_info = next((b for b in status["bosses"] if b["id"] == boss_id), None)
    if not boss_info:
        raise HTTPException(status_code=404, detail="Boss not found")
    if boss_info["status"] == "locked":
         raise HTTPException(status_code=400, detail="Boss is locked. Meet the requirements first!")
    return services.challenge_vocabulary_boss(db, player.id, boss_id)


@app.post("/api/vocabulary/boss/{boss_id}/submit", response_model=VocabularyBossSubmitOut)
def submit_vocabulary_boss_endpoint(boss_id: int, payload: VocabularyBossSubmitIn, player: Player = Depends(get_current_player), db: Session = Depends(get_db)):
    if boss_id not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Invalid boss ID")
    return services.submit_vocabulary_boss_result(db, player.id, boss_id, payload.score_pct)


# ---------------------------------------------------------------------------
# I4-2: Collocation browser + flashcard endpoints
# ---------------------------------------------------------------------------

@app.get("/api/collocations/levels", response_model=list[CollocationLevelOut])
def get_collocation_levels(
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Browse: all collocation levels with weighted completion % for current player/campaign."""
    from datetime import datetime as _dt
    from sqlalchemy import func as sqlfunc

    levels = db.query(CollocationLevel).order_by(CollocationLevel.difficulty_order).all()
    if not levels:
        return []

    # collection_ids linked to campaign, grouped by level_id
    link_rows = (
        db.query(CampaignCollocationLink.collection_id, CollocationCollection.level_id)
        .join(CollocationCollection, CollocationCollection.id == CampaignCollocationLink.collection_id)
        .filter(CampaignCollocationLink.campaign_id == campaign.id)
        .all()
    )
    linked_ids = [r.collection_id for r in link_rows]
    collections_by_level: dict[int, list[int]] = {}
    for r in link_rows:
        if r.level_id is not None:
            collections_by_level.setdefault(r.level_id, []).append(r.collection_id)

    # Collection count per level
    coll_count_by_level: dict[int, int] = {k: len(v) for k, v in collections_by_level.items()}

    # Weighted completion via shared helper (only if there are linked collections)
    grains = services.compute_collocation_completion(
        db, player.id, campaign.id, linked_ids, _dt.utcnow()
    ) if linked_ids else {"level": {}}
    level_grain: dict[int, tuple[int, int]] = grains["level"]

    result = []
    for lv in levels:
        done, total = level_grain.get(lv.id, (0, 0))
        # Also count unlinked collections under this level for total_words
        if lv.id not in collections_by_level:
            # Level has no linked collections — find all collections under this level for total count
            unlinked_ids = [
                r.id for r in db.query(CollocationCollection.id)
                .filter(CollocationCollection.level_id == lv.id)
                .all()
            ]
            if unlinked_ids:
                item_total = db.query(sqlfunc.count(CollocationItem.id)).join(
                    CollocationTopic, CollocationTopic.id == CollocationItem.topic_id
                ).join(
                    CollocationSection, CollocationSection.id == CollocationTopic.section_id
                ).filter(CollocationSection.collection_id.in_(unlinked_ids)).scalar() or 0
                total = item_total
        pct = round(done / total * 100, 1) if total > 0 else 0.0
        result.append(CollocationLevelOut(
            id=lv.id,
            name=lv.name,
            difficulty_order=lv.difficulty_order,
            icon=lv.icon,
            collection_count=coll_count_by_level.get(lv.id, 0),
            total_words=total,
            completed_words=done,
            pct=pct,
            locked=(total == 0),
        ))
    return result


@app.get("/api/collocations/topics", response_model=list[CollocationBrowseTopicOut])
def get_collocation_browse_topics(
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Browse: all topics in the campaign-linked collections, enriched with item_count + section_id."""
    # Get collection IDs linked to this campaign
    link_ids = [
        row.collection_id
        for row in db.query(CampaignCollocationLink.collection_id)
        .filter(CampaignCollocationLink.campaign_id == campaign.id)
        .all()
    ]
    if not link_ids:
        return []

    from datetime import datetime as _dt
    now = _dt.utcnow()

    # Use shared helper for all completion grains
    grains = services.compute_collocation_completion(db, player.id, campaign.id, link_ids, now)
    topic_grain: dict[int, tuple[int, int]] = grains["topic"]

    topics = (
        db.query(CollocationTopic)
        .join(CollocationSection, CollocationSection.id == CollocationTopic.section_id)
        .filter(CollocationSection.collection_id.in_(link_ids))
        .order_by(CollocationSection.section_order, CollocationTopic.topic_order)
        .all()
    )
    result = []
    for t in topics:
        done, total = topic_grain.get(t.id, (0, 0))
        result.append(CollocationBrowseTopicOut(
            id=t.id,
            title=t.title,
            topic_order=t.topic_order,
            section_id=t.section_id if t.section else 0,
            section_title=t.section.title if t.section else "",
            section_order=t.section.section_order if t.section else 0,
            item_count=total,
            completed_count=done,
        ))
    return result


@app.get("/api/collocations/topics/{topic_id}/items", response_model=list[CollocationBrowseItemOut])
def get_collocation_browse_items(
    topic_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Browse: items in a topic with effective_familiarity + is_added from collocation_flashcards."""
    from datetime import datetime as _dt
    items = (
        db.query(CollocationItem)
        .filter(CollocationItem.topic_id == topic_id)
        .order_by(CollocationItem.item_order)
        .all()
    )
    # Fetch all flashcard rows for this player/campaign in one query
    item_ids = [i.id for i in items]
    fc_map: dict[int, CollocationFlashcard] = {}
    if item_ids:
        rows = (
            db.query(CollocationFlashcard)
            .filter(
                CollocationFlashcard.player_id == player.id,
                CollocationFlashcard.campaign_id == campaign.id,
                CollocationFlashcard.collocation_item_id.in_(item_ids),
            )
            .all()
        )
        fc_map = {r.collocation_item_id: r for r in rows}

    now = _dt.utcnow()
    result = []
    for item in items:
        fc = fc_map.get(item.id)
        eff = services.effective_familiarity(fc.familiarity, fc.familiarity_set_at, now) if fc else "again"
        result.append(CollocationBrowseItemOut(
            id=item.id,
            collocation=item.collocation,
            pronunciation_us=item.pronunciation_us,
            meaning_vi=item.meaning_vi,
            example_en=item.example_en,
            example_vi=item.example_vi,
            collocation_type=item.collocation_type,
            item_order=item.item_order,
            effective_familiarity=eff,
            is_added=fc is not None,
        ))
    return result


@app.post("/api/collocations/{item_id}/flashcard")
def add_collocation_flashcard(
    item_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Add flashcard for an item (idempotent). Re-adding a graduated 'easy' card resets to 'again'."""
    existing = (
        db.query(CollocationFlashcard)
        .filter(
            CollocationFlashcard.player_id == player.id,
            CollocationFlashcard.campaign_id == campaign.id,
            CollocationFlashcard.collocation_item_id == item_id,
        )
        .first()
    )
    if existing:
        if existing.familiarity == "easy":
            # Re-add: graduate reset to again; clear familiarity_set_at (reset to unreviewed state)
            existing.familiarity = "again"
            existing.familiarity_set_at = None
            db.commit()
        return {"detail": "flashcard exists", "familiarity": existing.familiarity}
    # Verify item exists
    item = db.query(CollocationItem).filter(CollocationItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Collocation item not found")
    fc = CollocationFlashcard(
        player_id=player.id,
        campaign_id=campaign.id,
        collocation_item_id=item_id,
        familiarity="again",
        familiarity_set_at=None,  # Set only on first review, not on add
    )
    db.add(fc)
    db.commit()
    return {"detail": "flashcard added", "familiarity": "again"}


@app.delete("/api/collocations/{item_id}/flashcard")
def remove_collocation_flashcard(
    item_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Remove a flashcard row (removes from flashcard tab; still browsable)."""
    fc = (
        db.query(CollocationFlashcard)
        .filter(
            CollocationFlashcard.player_id == player.id,
            CollocationFlashcard.campaign_id == campaign.id,
            CollocationFlashcard.collocation_item_id == item_id,
        )
        .first()
    )
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    db.delete(fc)
    db.commit()
    return {"detail": "flashcard removed"}


@app.post("/api/collocations/{item_id}/flashcard/review")
def review_collocation_flashcard(
    item_id: int,
    body: CollocationReviewIn,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Set familiarity (again/hard/good/easy) for a collocation flashcard, then check auto-complete."""
    valid_results = {"again", "hard", "good", "easy"}
    if body.result not in valid_results:
        raise HTTPException(status_code=422, detail=f"result must be one of {valid_results}")
    fc = (
        db.query(CollocationFlashcard)
        .filter(
            CollocationFlashcard.player_id == player.id,
            CollocationFlashcard.campaign_id == campaign.id,
            CollocationFlashcard.collocation_item_id == item_id,
        )
        .first()
    )
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found — add it first")
    fc.familiarity = body.result
    fc.familiarity_set_at = datetime.utcnow()
    db.flush()
    # I4-7: Auto-complete Collocation Forge daily quest if 5 distinct reviewed today
    today = date.today()
    autocompleted = services.try_autocomplete_collocation_forge(
        db, player_id=player.id, campaign_id=campaign.id, today=today
    )
    db.commit()
    return {
        "detail": "familiarity updated",
        "familiarity": fc.familiarity,
        "collocation_forge_autocompleted": autocompleted,
    }


@app.get("/api/collocations/flashcard/topics", response_model=list[CollocationFlashcardTopicOut])
def get_collocation_flashcard_topics(
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Flashcard: topics with ≥1 non-graduated (familiarity != 'easy') added card."""
    from datetime import datetime as _dt
    now = _dt.utcnow()
    # Fetch all non-easy flashcard rows for this player/campaign
    fc_rows = (
        db.query(CollocationFlashcard)
        .filter(
            CollocationFlashcard.player_id == player.id,
            CollocationFlashcard.campaign_id == campaign.id,
            CollocationFlashcard.familiarity != "easy",
        )
        .all()
    )
    # Apply lazy decay — exclude cards that decay to same level (they still show)
    # Group by topic_id
    topic_card_counts: dict[int, int] = {}
    for fc in fc_rows:
        eff = services.effective_familiarity(fc.familiarity, fc.familiarity_set_at, now)
        # 'easy' after decay still = graduated (shouldn't happen since stored != easy,
        # but guard defensively)
        if eff == "easy":
            continue
        item = db.query(CollocationItem).filter(CollocationItem.id == fc.collocation_item_id).first()
        if item:
            topic_card_counts[item.topic_id] = topic_card_counts.get(item.topic_id, 0) + 1

    if not topic_card_counts:
        return []

    topics = (
        db.query(CollocationTopic)
        .filter(CollocationTopic.id.in_(list(topic_card_counts.keys())))
        .order_by(CollocationTopic.topic_order)
        .all()
    )
    result = []
    for t in topics:
        result.append(CollocationFlashcardTopicOut(
            id=t.id,
            title=t.title,
            topic_order=t.topic_order,
            section_title=t.section.title if t.section else "",
            card_count=topic_card_counts.get(t.id, 0),
        ))
    return result


@app.get("/api/collocations/flashcard/topics/{topic_id}", response_model=list[CollocationFlashcardItemOut])
def get_collocation_flashcard_items(
    topic_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Flashcard: non-graduated added cards in a topic for the review loop."""
    from datetime import datetime as _dt
    now = _dt.utcnow()
    fc_rows = (
        db.query(CollocationFlashcard)
        .join(CollocationItem, CollocationItem.id == CollocationFlashcard.collocation_item_id)
        .filter(
            CollocationFlashcard.player_id == player.id,
            CollocationFlashcard.campaign_id == campaign.id,
            CollocationFlashcard.familiarity != "easy",
            CollocationItem.topic_id == topic_id,
        )
        .order_by(CollocationItem.item_order)
        .all()
    )
    result = []
    for fc in fc_rows:
        eff = services.effective_familiarity(fc.familiarity, fc.familiarity_set_at, now)
        item = fc.collocation_item
        result.append(CollocationFlashcardItemOut(
            id=item.id,
            collocation=item.collocation,
            pronunciation_us=item.pronunciation_us,
            meaning_vi=item.meaning_vi,
            example_en=item.example_en,
            example_vi=item.example_vi,
            collocation_type=item.collocation_type,
            item_order=item.item_order,
            effective_familiarity=eff,
        ))
    return result







# ════════════════════════════════════════════════════════════════════
# Vocabulary Library API  (vocab-library/*)
# ════════════════════════════════════════════════════════════════════

def _vocab_level_ids_for_campaign(db: Session, campaign_id: int) -> list[int]:
    return [
        r.vocab_level_id
        for r in db.query(CampaignVocabLink.vocab_level_id)
        .filter(CampaignVocabLink.campaign_id == campaign_id)
        .all()
    ]


@app.get("/api/vocab-library/levels", response_model=list[VocabLevelOut])
def vl_get_levels(
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    from datetime import datetime as _dt
    level_ids = _vocab_level_ids_for_campaign(db, campaign.id)
    levels = db.query(VocabLevel).order_by(VocabLevel.difficulty_order).all()
    grains = services.compute_vocab_completion(db, player.id, campaign.id, level_ids, _dt.utcnow()) if level_ids else {"level": {}}
    lv_grain = grains["level"]
    result = []
    for lv in levels:
        done, total = lv_grain.get(lv.id, (0, 0))
        pct = round(done / total * 100, 1) if total > 0 else 0.0
        result.append(VocabLevelOut(
            id=lv.id, name=lv.name, difficulty_order=lv.difficulty_order, icon=lv.icon,
            total_words=total, completed_words=done, pct=pct, locked=(total == 0),
        ))
    return result


@app.get("/api/vocab-library/levels/{level_id}/topics", response_model=list[VocabTopicOut])
def vl_get_topics(
    level_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    from datetime import datetime as _dt
    topics = db.query(VocabTopic).filter_by(level_id=level_id).order_by(VocabTopic.topic_order).all()
    grains = services.compute_vocab_completion(db, player.id, campaign.id, [level_id], _dt.utcnow())
    tp_grain = grains["topic"]
    result = []
    for t in topics:
        done, total = tp_grain.get(t.id, (0, 0))
        pct = round(done / total * 100, 1) if total > 0 else 0.0
        result.append(VocabTopicOut(
            id=t.id, level_id=t.level_id, title=t.title, topic_order=t.topic_order,
            total_words=total, completed_words=done, pct=pct,
        ))
    return result


@app.get("/api/vocab-library/topics/{topic_id}/units", response_model=list[VocabUnitOut])
def vl_get_units(
    topic_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    from datetime import datetime as _dt
    topic = db.query(VocabTopic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    units = db.query(VocabUnit).filter_by(topic_id=topic_id).order_by(VocabUnit.unit_order).all()
    grains = services.compute_vocab_completion(db, player.id, campaign.id, [topic.level_id], _dt.utcnow())
    un_grain = grains["unit"]
    result = []
    for u in units:
        done, total = un_grain.get(u.id, (0, 0))
        pct = round(done / total * 100, 1) if total > 0 else 0.0
        result.append(VocabUnitOut(
            id=u.id, topic_id=u.topic_id, title=u.title,
            unit_number=u.unit_number, unit_order=u.unit_order,
            total_words=total, completed_words=done, pct=pct,
        ))
    return result


@app.get("/api/vocab-library/units/{unit_id}/sections", response_model=list[VocabSectionOut])
def vl_get_sections(
    unit_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    from datetime import datetime as _dt
    unit = db.query(VocabUnit).filter_by(id=unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    topic = db.query(VocabTopic).filter_by(id=unit.topic_id).first()
    sections = db.query(VocabSection).filter_by(unit_id=unit_id).order_by(VocabSection.section_order).all()
    grains = services.compute_vocab_completion(db, player.id, campaign.id, [topic.level_id], _dt.utcnow())
    sec_grain = grains["section"]
    result = []
    for s in sections:
        done, total = sec_grain.get(s.id, (0, 0))
        pct = round(done / total * 100, 1) if total > 0 else 0.0
        result.append(VocabSectionOut(
            id=s.id, unit_id=s.unit_id, title=s.title,
            section_letter=s.section_letter, section_order=s.section_order,
            total_words=total, completed_words=done, pct=pct,
        ))
    return result


@app.get("/api/vocab-library/sections/{section_id}/words", response_model=list[VocabWordOut])
def vl_get_words(
    section_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    from datetime import datetime as _dt
    now = _dt.utcnow()
    words = db.query(VocabLibraryItem).filter_by(section_id=section_id).order_by(VocabLibraryItem.item_order).all()
    item_ids = [w.id for w in words]
    fc_map: dict[int, VocabLibraryFlashcard] = {}
    if item_ids:
        for fc in db.query(VocabLibraryFlashcard).filter(
            VocabLibraryFlashcard.vocab_library_item_id.in_(item_ids),
            VocabLibraryFlashcard.player_id == player.id,
            VocabLibraryFlashcard.campaign_id == campaign.id,
        ).all():
            fc_map[fc.vocab_library_item_id] = fc

    result = []
    for w in words:
        fc = fc_map.get(w.id)
        eff = services.effective_familiarity(fc.familiarity, fc.familiarity_set_at, now) if fc else "again"
        result.append(VocabWordOut(
            id=w.id, section_id=w.section_id, word=w.word,
            part_of_speech=w.part_of_speech, pronunciation_us=w.pronunciation_us,
            meaning_vi=w.meaning_vi, example_en=w.example_en, example_vi=w.example_vi,
            item_order=w.item_order,
            effective_familiarity=eff,
            is_added=(fc is not None),
        ))
    return result


@app.post("/api/vocab-library/words/{item_id}/flashcard", status_code=201)
def vl_add_flashcard(
    item_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    item = db.query(VocabLibraryItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Word not found")
    fc = db.query(VocabLibraryFlashcard).filter_by(
        player_id=player.id, campaign_id=campaign.id, vocab_library_item_id=item_id,
    ).first()
    if fc:
        if fc.familiarity == "easy":
            from datetime import datetime as _dt
            fc.familiarity = "again"
            fc.familiarity_set_at = _dt.utcnow()
            db.flush()
    else:
        db.add(VocabLibraryFlashcard(
            player_id=player.id, campaign_id=campaign.id, vocab_library_item_id=item_id,
            familiarity="again",
        ))
        db.flush()
    db.commit()
    return {"status": "ok"}


@app.delete("/api/vocab-library/words/{item_id}/flashcard", status_code=200)
def vl_remove_flashcard(
    item_id: int,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    fc = db.query(VocabLibraryFlashcard).filter_by(
        player_id=player.id, campaign_id=campaign.id, vocab_library_item_id=item_id,
    ).first()
    if fc:
        db.delete(fc)
        db.flush()
        db.commit()
    return {"status": "ok"}


@app.post("/api/vocab-library/words/{item_id}/flashcard/review", status_code=200)
def vl_review_flashcard(
    item_id: int,
    body: VocabReviewIn,
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """XP-neutral review: only updates familiarity + familiarity_set_at. No quest trigger."""
    from datetime import datetime as _dt
    valid = {"again", "hard", "good", "easy"}
    if body.result not in valid:
        raise HTTPException(status_code=422, detail=f"result must be one of {valid}")
    fc = db.query(VocabLibraryFlashcard).filter_by(
        player_id=player.id, campaign_id=campaign.id, vocab_library_item_id=item_id,
    ).first()
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found - add it first")
    fc.familiarity = body.result
    fc.familiarity_set_at = _dt.utcnow()
    db.flush()
    db.commit()
    return {"status": "ok", "familiarity": body.result}


@app.get("/api/vocab-library/flashcards/due", response_model=list[VocabFlashcardDueOut])
def vl_get_due_flashcards(
    player: Player = Depends(get_current_player),
    campaign: Campaign = Depends(get_current_campaign),
    db: Session = Depends(get_db),
):
    """Return all vocab-library flashcards that are due for review (familiarity != 'easy' or added today)."""
    from datetime import datetime as _dt
    now = _dt.utcnow()
    fcs = (
        db.query(VocabLibraryFlashcard)
        .filter_by(player_id=player.id, campaign_id=campaign.id)
        .all()
    )
    result = []
    for fc in fcs:
        eff = services.effective_familiarity(fc.familiarity, fc.familiarity_set_at, now)
        item = fc.item
        if item is None:
            continue
        section = item.section
        unit = section.unit if section else None
        topic = unit.topic if (unit and unit.topic) else None
        level = topic.level if topic else None
        result.append(VocabFlashcardDueOut(
            id=item.id,
            section_id=item.section_id,
            word=item.word,
            part_of_speech=item.part_of_speech,
            pronunciation_us=item.pronunciation_us,
            meaning_vi=item.meaning_vi,
            example_en=item.example_en,
            example_vi=item.example_vi,
            item_order=item.item_order,
            effective_familiarity=eff,
            is_added=True,
            familiarity=fc.familiarity,
            familiarity_set_at=fc.familiarity_set_at,
            section_title=section.title if section else "",
            unit_title=unit.title if unit else "",
            level_name=level.name if level else "",
            topic_id=topic.id if topic else 0,
            topic_title=topic.title if topic else "",
        ))
    return result
