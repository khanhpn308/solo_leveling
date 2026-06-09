from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func, update, and_, case
from sqlalchemy.orm import Session, joinedload

from .models import (
    Badge,
    BadgeUnlock,
    BossBattle,
    Campaign,
    CampaignSkillState,
    CertificateRecord,
    CheckIn,
    ErrorLog,
    MockTest,
    Player,
    Quest,
    Skill,
    SkillRankHistory,
    SkillRankSuggestion,
    SpeakingEntry,
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
    CollocationCollection,
    CollocationSection,
    CollocationTopic,
    CollocationItem,
    CampaignCollocationLink,
    PlayerCollocationProgress,
    CollocationFlashcard,
    RankXpThreshold,
    QuestXpPolicy,
    WeeklyMissionXpPolicy,
    MainQuestXpPolicy,
)
from .schemas import (

    VocabularyItemIn,
    VocabularyExampleIn,
    VocabularyRelationIn,
    FlashcardIn,
    VocabularyTopicIn,
    VocabularyNodeIn,
    VocabularyNodeUpdate,
    VocabularyEdgeIn,
    VocabularyErrorIn,
    CollocationCollectionIn,
    CollocationSectionIn,
    CollocationTopicIn,
    CollocationItemIn,
    CampaignCollocationLinkIn,
    PlayerCollocationProgressIn,
)


RANK_ORDER = ["F", "E", "D", "C", "B", "A", "S"]
CORE_SKILLS = {"Listening", "Reading", "Writing", "Speaking"}

# Level curve: xp(L) = round(19 * (L^1.6 - 1))  for L in 1..60
# 60 levels total; 10 levels per rank (L1-10=F, L11-20=E, ... L60=S)
# Source: spec/infor/ielts_xp_policy_rank_quest_spec.md §2
_LEVEL_XP: list[int] = [round(19 * (L ** 1.6 - 1)) for L in range(1, 61)]

# Rank min XP = XP required at the first level of each rank
RANK_MIN_XP: dict[str, int] = {
    "F": _LEVEL_XP[0],   # L1  = 0
    "E": _LEVEL_XP[10],  # L11 = 862
    "D": _LEVEL_XP[20],  # L21 = 2460
    "C": _LEVEL_XP[30],  # L31 = 4604
    "B": _LEVEL_XP[40],  # L41 = 7212
    "A": _LEVEL_XP[50],  # L51 = 10234
    "S": _LEVEL_XP[59],  # L60 = 13279
}

# First level of each rank (1-indexed)
_RANK_FIRST_LEVEL: dict[str, int] = {
    "F": 1, "E": 11, "D": 21, "C": 31, "B": 41, "A": 51, "S": 60,
}

DEFAULT_WEAK_POINTS = {
    "Listening": "Current strength; still needs work on Sections 3-4, distractors, and spelling.",
    "Reading": "Main weakness: limited vocabulary and limited confidence with long-sentence analysis.",
    "Writing": "Needs steady writing practice and review against the 4 IELTS criteria.",
    "Speaking": "Needs regular recording practice to improve fluency, pronunciation, and Part 3 reasoning.",
    "Vocabulary": "Study by topic, paraphrase pairs, and personalized example sentences.",
    "Collocation": "Used to make speaking and writing sound more natural and reduce word-combination errors.",
    "Grammar": "Strengthen tenses, relative clauses, passive voice, conditionals, and complex sentences.",
}

TRACKER_TYPE_TO_FIELD = {
    "error_log": "error_log_id",
    "writing_entry": "writing_entry_id",
    "speaking_entry": "speaking_entry_id",
    "mock_test": "mock_test_id",
}

FIELD_TO_TRACKER_TYPE = {
    "error_log_id": "error_log",
    "writing_entry_id": "writing_entry",
    "speaking_entry_id": "speaking_entry",
    "mock_test_id": "mock_test",
}


def level_from_xp(xp: int) -> int:
    """Return fine-grained level 1..60 for the given XP."""
    level = 1
    for i, threshold in enumerate(_LEVEL_XP):
        if xp >= threshold:
            level = i + 1
        else:
            break
    return level


def rank_from_level(level: int) -> str:
    """Return rank F..S for a level 1..60 (10 levels per rank, S only at L60)."""
    if level >= 60:
        return "S"
    return RANK_ORDER[min((level - 1) // 10, 6)]


def get_rank_level(xp: int) -> tuple[str, int]:
    """Return (rank, fine-grained level 1..60) for the given XP."""
    lvl = level_from_xp(xp)
    return rank_from_level(lvl), lvl


def ensure_campaign_skill_states(db: Session, campaign: Campaign) -> list[CampaignSkillState]:
    states = (
        db.query(CampaignSkillState)
        .options(joinedload(CampaignSkillState.skill))
        .filter(CampaignSkillState.campaign_id == campaign.id)
        .all()
    )
    by_skill_id = {state.skill_id: state for state in states}
    for skill in db.query(Skill).order_by(Skill.id).all():
        if skill.id in by_skill_id:
            continue
        weak_point = DEFAULT_WEAK_POINTS.get(skill.name, "")
        state = CampaignSkillState(
            campaign_id=campaign.id,
            skill_id=skill.id,
            xp=0,
            rank="F",
            confirmed_rank="F",
            level=1,
            streak=0,
            last_practiced=None,
            weak_point=weak_point,
            user_weakness_note=weak_point,
            last_system_suggestion_at=None,
        )
        db.add(state)
        states.append(state)
        by_skill_id[skill.id] = state
    if db.new:
        db.flush()
        states = (
            db.query(CampaignSkillState)
            .options(joinedload(CampaignSkillState.skill))
            .filter(CampaignSkillState.campaign_id == campaign.id)
            .order_by(CampaignSkillState.skill_id)
            .all()
        )
    return states


def get_campaign_skill_state_map(db: Session, campaign: Campaign) -> dict[int, CampaignSkillState]:
    return {state.skill_id: state for state in ensure_campaign_skill_states(db, campaign)}


def resolve_tracker_payload(
    db: Session,
    tracker_type: str = "",
    tracker_entry_id: int | None = None,
    error_log_id: int | None = None,
    writing_entry_id: int | None = None,
    speaking_entry_id: int | None = None,
    mock_test_id: int | None = None,
) -> tuple[str, int | None, dict[str, int | None]]:
    typed_values = {
        "error_log_id": error_log_id,
        "writing_entry_id": writing_entry_id,
        "speaking_entry_id": speaking_entry_id,
        "mock_test_id": mock_test_id,
    }
    provided_typed = [(field_name, value) for field_name, value in typed_values.items() if value is not None]
    if len(provided_typed) > 1:
        raise ValueError("Only one typed tracker reference can be set per quest completion")

    if provided_typed:
        field_name, value = provided_typed[0]
        return FIELD_TO_TRACKER_TYPE[field_name], value, typed_values

    resolved = dict(typed_values)
    if tracker_entry_id is not None and tracker_type in TRACKER_TYPE_TO_FIELD:
        field_name = TRACKER_TYPE_TO_FIELD[tracker_type]
        model = {
            "error_log_id": ErrorLog,
            "writing_entry_id": WritingEntry,
            "speaking_entry_id": SpeakingEntry,
            "mock_test_id": MockTest,
        }[field_name]
        if db.get(model, tracker_entry_id):
            resolved[field_name] = tracker_entry_id
    return tracker_type, tracker_entry_id, resolved


def current_week_window(player: Player) -> tuple[date, date]:
    today = date.today()
    start_anchor = player.start_date
    if today < start_anchor:
        today = start_anchor
    days_from_start = (today - start_anchor).days
    week_start = start_anchor + timedelta(days=(days_from_start // 7) * 7)
    return week_start, week_start + timedelta(days=6)


def get_active_player(db: Session) -> Player:
    player = db.query(Player).first()
    if not player:
        raise ValueError("Player profile not found")
    return player


def get_active_campaign(db: Session, player: Player | None = None) -> Campaign:
    player = player or get_active_player(db)
    campaign = None
    if player.active_campaign_id:
        campaign = db.query(Campaign).filter(Campaign.id == player.active_campaign_id).first()
    if not campaign:
        campaign = (
            db.query(Campaign)
            .filter(Campaign.player_id == player.id)
            .order_by(Campaign.created_at.desc(), Campaign.id.desc())
            .first()
        )
    if not campaign:
        raise ValueError("Active campaign not found")
    return campaign


def sync_quest_statuses(db: Session, campaign: Campaign) -> None:
    today = date.today()
    now = datetime.utcnow()
    cid = campaign.id

    # Bulk-update completed quests whose status column is stale
    db.execute(
        update(Quest)
        .where(and_(Quest.campaign_id == cid, Quest.completed == True, Quest.status != "completed"))
        .values(status="completed")
        .execution_options(synchronize_session=False)
    )
    # Bulk-fix earned_xp = xp for completed-unclaimed quests missing earned_xp
    db.execute(
        update(Quest)
        .where(and_(
            Quest.campaign_id == cid,
            Quest.completed == True,
            Quest.reward_claimed == False,
            Quest.earned_xp == None,
        ))
        .values(earned_xp=Quest.xp)
        .execution_options(synchronize_session=False)
    )
    # Bulk-expire past incomplete quests
    db.execute(
        update(Quest)
        .where(and_(
            Quest.campaign_id == cid,
            Quest.completed == False,
            Quest.quest_date < today,
            Quest.status != "expired",
        ))
        .values(status="expired", expired_at=now)
        .execution_options(synchronize_session=False)
    )
    # Bulk-reset future quests to pending
    db.execute(
        update(Quest)
        .where(and_(
            Quest.campaign_id == cid,
            Quest.completed == False,
            Quest.quest_date >= today,
            Quest.status != "pending",
        ))
        .values(status="pending", expired_at=None)
        .execution_options(synchronize_session=False)
    )
    db.flush()


def _set_weekly_item_state(item: WeeklyMissionItem, value: int) -> None:
    item.current_count = max(0, min(value, item.target_count))
    item.status = "completed" if item.current_count >= item.target_count else "active"


def recompute_weekly_missions(db: Session, campaign: Campaign) -> None:
    missions = (
        db.query(WeeklyMission)
        .options(joinedload(WeeklyMission.items))
        .filter(WeeklyMission.campaign_id == campaign.id)
        .order_by(WeeklyMission.week_start)
        .all()
    )
    if not missions:
        return

    quests = (
        db.query(Quest)
        .options(joinedload(Quest.skill))
        .filter(Quest.campaign_id == campaign.id, Quest.completed == True)
        .all()
    )
    checkins = db.query(CheckIn).filter(CheckIn.campaign_id == campaign.id).all()
    error_logs = db.query(ErrorLog).filter(ErrorLog.campaign_id == campaign.id).all()
    writing_entries = db.query(WritingEntry).filter(WritingEntry.campaign_id == campaign.id).all()
    speaking_entries = db.query(SpeakingEntry).filter(SpeakingEntry.campaign_id == campaign.id).all()

    for mission in missions:
        week_quests = [quest for quest in quests if mission.week_start <= quest.quest_date <= mission.week_end]
        week_checkins = [item for item in checkins if mission.week_start <= item.checkin_date <= mission.week_end]
        week_error_logs = [item for item in error_logs if mission.week_start <= item.logged_date <= mission.week_end]
        week_writing = [item for item in writing_entries if mission.week_start <= item.entry_date <= mission.week_end]
        week_speaking = [item for item in speaking_entries if mission.week_start <= item.entry_date <= mission.week_end]

        completed_core = [quest for quest in week_quests if quest.quest_role == "core"]
        completed_support = [quest for quest in week_quests if quest.quest_role == "support"]
        completed_mini = [quest for quest in week_quests if quest.quest_role == "mini"]
        daily_quest_count = len([quest for quest in week_quests if quest.session_type == "Daily Quest"])
        noted_checkins = len([item for item in week_checkins if (item.note or "").strip()])
        tracker_notes = len(week_error_logs) + len(week_writing) + len(week_speaking)
        active_days = {
            *(item.checkin_date for item in week_checkins),
            *(quest.quest_date for quest in completed_mini),
        }
        for item in mission.items:
            description = item.description.lower()
            progress = min(item.target_count, daily_quest_count)

            if "reading core quest" in description:
                progress = len(
                    [
                        quest
                        for quest in completed_core
                        if (quest.skill.name if quest.skill else "") == "Reading"
                    ]
                )
            elif "vocabulary/collocation support quest" in description:
                progress = len(
                    [
                        quest
                        for quest in completed_support
                        if (quest.skill.name if quest.skill else "") in {"Vocabulary", "Collocation"}
                    ]
                )
            elif "writing/speaking core quest" in description:
                progress = len(
                    [
                        quest
                        for quest in completed_core
                        if (quest.skill.name if quest.skill else "") in {"Writing", "Speaking"}
                    ]
                )
            elif "core quest" in description:
                progress = len(completed_core)
            elif "check-in or mini-review days" in description or "check-in hoac mini review day" in description:
                progress = len(active_days)
            elif "check-in" in description and "note" in description:
                progress = noted_checkins
            elif "check-in" in description:
                progress = len(week_checkins)
            elif "error log/writing/speaking trackers" in description or "error log/writing/speaking tracker" in description:
                progress = tracker_notes
            elif "recurring weak points" in description or "diem yeu recurring" in description:
                progress = len(week_error_logs)
            elif "mini review tied to an output skill" in description or "mini review lien quan output skill" in description:
                progress = len(
                    [
                        quest
                        for quest in completed_mini
                        if (quest.skill.name if quest.skill else "") in {"Writing", "Speaking", "Collocation"}
                    ]
                ) or len(completed_mini)
            elif "long sentences or difficult paraphrases" in description or "cau dai hoac paraphrase kho" in description:
                progress = tracker_notes or len(
                    [
                        quest
                        for quest in week_quests
                        if (quest.skill.name if quest.skill else "") in {"Reading", "Vocabulary", "Collocation"}
                    ]
                )
            elif "daily quest" in description:
                progress = daily_quest_count


            _set_weekly_item_state(item, progress)

        if mission.items and all(item.status == "completed" for item in mission.items):
            mission.status = "completed"
            mission.completed_at = mission.completed_at or datetime.utcnow()
        else:
            mission.status = "active"
            mission.completed_at = None


def recompute_badges(db: Session, player: Player, campaign: Campaign, state_map: dict[int, CampaignSkillState]) -> None:
    skill_xp = {
        state.skill.name: state.xp
        for state in state_map.values()
        if state.skill is not None
    }
    completed_count = (
        db.query(Quest)
        .filter(Quest.campaign_id == campaign.id, Quest.completed == True)
        .count()
    )
    defeated_errors_count = (
        db.query(VocabularyError)
        .filter(VocabularyError.player_id == player.id)
        .filter(VocabularyError.status == "defeated")
        .count()
    )
    badge_rules = {
        "Vocabulary Hunter": skill_xp.get("Vocabulary", 0) >= 300,
        "Grammar Fixer": skill_xp.get("Grammar", 0) >= 300,
        "Listening Warrior": skill_xp.get("Listening", 0) >= 500,
        "Reading Decoder": skill_xp.get("Reading", 0) >= 500,
        "Writing Starter": skill_xp.get("Writing", 0) >= 300,
        "Speaking Brave Mode": skill_xp.get("Speaking", 0) >= 300,
        "Error Killer": defeated_errors_count >= 10,
        "Band 6 Challenger": completed_count >= 150,
        "Band 7 Candidate": completed_count >= 250,
    }
    existing_unlocks = {
        item.badge_id: item
        for item in db.query(BadgeUnlock).filter(BadgeUnlock.campaign_id == campaign.id).all()
    }
    for badge in db.query(Badge).all():
        should_unlock = badge_rules.get(badge.name, False)
        if should_unlock and badge.id not in existing_unlocks:
            db.add(
                BadgeUnlock(
                    player_id=player.id,
                    campaign_id=campaign.id,
                    badge_id=badge.id,
                    unlocked_at=datetime.utcnow(),
                )
            )


MATRIX_SKILLS = {"Listening", "Reading", "Writing", "Speaking", "Vocabulary"}

# Support sources: XP from these skills is routed into the target matrix skill.
# Grammar quests/missions contribute to Writing; Collocation to Vocabulary.
# spec: ielts_xp_policy_rank_quest_spec.md §1.1, §4, §7
SUPPORT_ROUTING: dict[str, str] = {
    "Grammar": "Writing",
    "Collocation": "Vocabulary",
}


def recompute_player_progress(
    db: Session,
    player: Player,
    campaign: Campaign,
    state_map: dict | None = None,
) -> None:
    # player_xp = mean of 5 matrix skill XP (no direct accrual)
    # spec: ielts_xp_policy_rank_quest_spec.md §1.2 + player_level.md §1
    if state_map is None:
        state_map = get_campaign_skill_state_map(db, campaign)
    matrix_xp_values = [
        state.xp or 0
        for state in state_map.values()
        if state.skill and state.skill.name in MATRIX_SKILLS
    ]
    player.player_xp = round(sum(matrix_xp_values) / 5) if matrix_xp_values else 0
    player.total_xp = player.player_xp
    player.player_rank, player.player_level = get_rank_level(player.player_xp)

    # Aggregate per-day counts instead of loading all quest rows
    day_rows = (
        db.query(
            Quest.quest_date,
            func.count(Quest.id).label("total"),
            func.sum(case((Quest.completed == True, 1), else_=0)).label("done"),
        )
        .filter(Quest.campaign_id == campaign.id, Quest.quest_role.in_(["core", "support", "mini"]))
        .group_by(Quest.quest_date)
        .all()
    )
    by_day: dict[date, tuple[int, int]] = {r.quest_date: (r.total, r.done) for r in day_rows}

    checkin_dates = {
        item.checkin_date
        for item in db.query(CheckIn.checkin_date).filter(CheckIn.campaign_id == campaign.id).all()
    }

    current_streak = 0
    best_streak = 0
    shield_count = min(max(player.shield_count, 0), 2)
    regen_progress = 0
    perfect_days = 0
    cursor = campaign.start_date
    today = date.today()
    while cursor <= today:
        total, done = by_day.get(cursor, (0, 0))
        is_daily_day = total >= 3
        fully_completed = is_daily_day and done >= total
        if fully_completed:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
            regen_progress += 1
            if regen_progress >= 3:
                if shield_count < 2:
                    shield_count += 1
                regen_progress = 0
            if cursor in checkin_dates:
                perfect_days += 1
        elif is_daily_day:
            if current_streak > 0 and shield_count > 0:
                shield_count -= 1
            else:
                current_streak = 0
                regen_progress = 0
        cursor += timedelta(days=1)

    player.current_streak = current_streak
    player.best_streak = max(player.best_streak, best_streak)
    player.shield_count = shield_count
    player.shield_regen_progress = regen_progress
    player.perfect_day_count = perfect_days


def compute_vocabulary_xp(db: Session, player_id: int) -> int:
    items = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id).all()
    
    # Group examples by vocabulary_item_id to prevent N+1 queries
    example_counts = {}
    examples_query = (
        db.query(VocabularyExample.vocabulary_item_id, func.count(VocabularyExample.id))
        .filter(VocabularyExample.player_id == player_id)
        .group_by(VocabularyExample.vocabulary_item_id)
        .all()
    )
    for item_id, count in examples_query:
        example_counts[item_id] = count

    # Group relations by source_word_id to prevent N+1 queries
    relation_counts = {}
    relations_query = (
        db.query(
            VocabularyRelation.source_word_id,
            VocabularyRelation.relation_type,
            func.count(VocabularyRelation.id)
        )
        .filter(VocabularyRelation.player_id == player_id)
        .group_by(VocabularyRelation.source_word_id, VocabularyRelation.relation_type)
        .all()
    )
    for source_word_id, r_type, count in relations_query:
        if source_word_id not in relation_counts:
            relation_counts[source_word_id] = {"syn_ant": 0, "family": 0}
        if r_type in ["synonym", "antonym"]:
            relation_counts[source_word_id]["syn_ant"] += count
        elif r_type == "word_family":
            relation_counts[source_word_id]["family"] += count

    vocab_xp = 0
    for item in items:
        # Base word created
        data_entry_xp = 2
        if item.meaning_en:
            data_entry_xp += 2
        if item.meaning_vi:
            data_entry_xp += 2
        if item.part_of_speech:
            data_entry_xp += 2
        if item.pronunciation_ipa:
            data_entry_xp += 3

        # Examples associated with this word (+5 each)
        examples_for_word = example_counts.get(item.id, 0)
        data_entry_xp += examples_for_word * 5

        # Relations associated with this word
        relations_for_word = relation_counts.get(item.id, {"syn_ant": 0, "family": 0})
        data_entry_xp += relations_for_word["syn_ant"] * 3
        data_entry_xp += relations_for_word["family"] * 5

        # Cap data-entry XP at 40/word
        capped_data_entry = min(data_entry_xp, 40)

        # Add mastery score (capped at 50 per word, counted separately on top of 40 cap)
        mastery_xp = min(item.mastery_score or 0, 50)

        vocab_xp += capped_data_entry + mastery_xp

    collocation_count = (
        db.query(PlayerCollocationProgress)
        .filter(
            PlayerCollocationProgress.player_id == player_id,
            PlayerCollocationProgress.status.in_(["learning", "practiced", "mastered"])
        )
        .count()
    )
    vocab_xp += collocation_count * 5

    # Error Dungeon XP: Log (+1 XP), Correct (+5 XP), Defeat (+20 XP)
    errors = db.query(VocabularyError).filter(VocabularyError.player_id == player_id).all()
    vocab_xp += len(errors) * 1
    vocab_xp += sum(err.defeated_count for err in errors) * 5
    vocab_xp += sum(20 for err in errors if err.status == 'defeated')

    # Add XP from cleared Vocabulary Bosses (based on unlocked badges & confirmed rank)
    skill_state = db.query(CampaignSkillState).join(Skill, Skill.id == CampaignSkillState.skill_id)\
        .filter(CampaignSkillState.campaign_id == db.query(Campaign.id).filter(Campaign.player_id == player_id, Campaign.status == 'active').scalar())\
        .filter(Skill.name == "Vocabulary").first()
    if skill_state and skill_state.confirmed_rank in ["E", "D", "C", "B", "A", "S"]:
        vocab_xp += 60

    unlocked_badge_names = db.query(Badge.name).join(BadgeUnlock, BadgeUnlock.badge_id == Badge.id)\
        .filter(BadgeUnlock.player_id == player_id).all()
    unlocked_badge_names = [b[0] for b in unlocked_badge_names]
    
    if "Memory Streak Badge I" in unlocked_badge_names:
        vocab_xp += 80
    if "Writing Lexical Buff" in unlocked_badge_names:
        vocab_xp += 100
    if "Lexical Awakener" in unlocked_badge_names:
        vocab_xp += 200

    return vocab_xp


def resolve_main_quest_covered_skills(quest: Quest) -> set[str]:
    session_no = None
    if quest.study_plan_session:
        session_no = quest.study_plan_session.session_no
    else:
        title_lower = quest.title.lower()
        if "s1" in title_lower or "session 1" in title_lower:
            session_no = 1
        elif "s2" in title_lower or "session 2" in title_lower:
            session_no = 2
        elif "s3" in title_lower or "session 3" in title_lower:
            session_no = 3
        elif "s4" in title_lower or "session 4" in title_lower:
            session_no = 4

    primary_skill_name = quest.skill.name if quest.skill else "Reading"
    if session_no == 1:
        return {"Listening", "Speaking"}
    if session_no == 2:
        return {"Reading", "Vocabulary"}
    if session_no == 3:
        return {"Writing"}
    if session_no == 4:
        return {primary_skill_name}
    return {primary_skill_name}


def recompute_skill_progress(db: Session, campaign: Campaign, state: CampaignSkillState) -> None:
    skill_name = state.skill.name if state.skill else None

    # Own quests XP (quests whose skill_id == this skill, excluding Main Quests)
    earned_non_main = (
        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
        .filter(
            Quest.campaign_id == campaign.id,
            Quest.session_type != "Main Quest",
            Quest.skill_id == state.skill_id,
            Quest.completed == True,
            Quest.reward_claimed == True,
        )
        .scalar()
        or 0
    )

    # Main quests: fetch all completed/claimed main quests in this campaign and resolve covered skills
    main_quests = (
        db.query(Quest)
        .filter(
            Quest.campaign_id == campaign.id,
            Quest.session_type == "Main Quest",
            Quest.completed == True,
            Quest.reward_claimed == True,
        )
        .all()
    )
    earned_main = 0
    for mq in main_quests:
        covered = resolve_main_quest_covered_skills(mq)
        if skill_name in covered:
            earned_main += int(mq.earned_xp or mq.base_xp or 0)

    earned = earned_non_main + earned_main

    # Support-source routing: add earned XP from quests of skills that route INTO this skill.
    # (Exclude Main Quests because they are already resolved/routed in earned_main)
    # Grammar → Writing, Collocation → Vocabulary  (spec: ielts_xp_policy_rank_quest_spec.md §1.1, §4)
    routed_earned = 0
    if skill_name in MATRIX_SKILLS:
        for src_name, tgt_name in SUPPORT_ROUTING.items():
            if tgt_name == skill_name:
                src_skill = db.query(Skill).filter(Skill.name == src_name).first()
                if src_skill:
                    routed_earned += (
                        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
                        .filter(
                            Quest.campaign_id == campaign.id,
                            Quest.session_type != "Main Quest",
                            Quest.skill_id == src_skill.id,
                            Quest.completed == True,
                            Quest.reward_claimed == True,
                        )
                        .scalar()
                        or 0
                    )

    vocab_xp = 0
    if skill_name == "Vocabulary":
        vocab_xp = compute_vocabulary_xp(db, campaign.player_id)

    state.xp = int(earned) + int(routed_earned) + vocab_xp
    # Ensure XP never drops below the confirmed_rank minimum (from certificate apply)
    confirmed_min_xp = 0
    try:
        policy = db.query(RankXpThreshold).filter_by(rank_name=state.confirmed_rank).first()
        if policy:
            confirmed_min_xp = policy.min_xp
        else:
            confirmed_min_xp = RANK_MIN_XP.get(state.confirmed_rank, 0)
    except Exception:
        confirmed_min_xp = RANK_MIN_XP.get(state.confirmed_rank, 0)

    if state.xp < confirmed_min_xp:
        state.xp = confirmed_min_xp
    state.rank, state.level = get_rank_level(state.xp)
    # Ensure rank never drops below confirmed_rank
    if state.confirmed_rank in RANK_ORDER and state.rank in RANK_ORDER:
        if RANK_ORDER.index(state.rank) < RANK_ORDER.index(state.confirmed_rank):
            state.rank = state.confirmed_rank
            state.level = _RANK_FIRST_LEVEL.get(state.confirmed_rank, 1)

    # Sync confirmed_rank directly to rank and clear promotion states if not boss-gated
    is_boss_gated = state.skill.boss_gated if state.skill else True
    if not is_boss_gated:
        state.confirmed_rank = state.rank
        state.promotion_status = "none"
        state.pending_rank = None
        state.promotion_unlocked_at = None

    state.last_practiced = (
        db.query(func.max(Quest.quest_date))
        .filter(
            Quest.campaign_id == campaign.id,
            Quest.skill_id == state.skill_id,
            Quest.completed == True,
        )
        .scalar()
    )

    # Rank Boss promotion gating logic:
    calc_idx = RANK_ORDER.index(state.rank) if state.rank in RANK_ORDER else 0
    conf_idx = RANK_ORDER.index(state.confirmed_rank) if state.confirmed_rank in RANK_ORDER else 0

    if calc_idx > conf_idx:
        next_rank_str = RANK_ORDER[conf_idx + 1]
        # Set eligible if not already in an active/locked exam state
        if state.promotion_status not in {"eligible", "boss_required", "in_progress", "passed"}:
            state.pending_rank = next_rank_str
            state.promotion_status = "eligible"
            state.promotion_unlocked_at = datetime.utcnow()
    else:
        # Only reset when no active exam is in flight.
        # eligible/boss_required/in_progress must not be clobbered — the player
        # earned eligibility before the recompute (or a penalty dropped XP below
        # the threshold, but the exam flow continues until resolved).
        if state.promotion_status not in {"eligible", "boss_required", "in_progress", "passed"}:
            state.pending_rank = None
            state.promotion_status = "none"
            state.promotion_unlocked_at = None


def refresh_progress_state(db: Session, player: Player | None = None, campaign: Campaign | None = None) -> None:
    player = player or get_active_player(db)
    campaign = campaign or get_active_campaign(db, player)
    db.expire_all()
    state_map = get_campaign_skill_state_map(db, campaign)
    sync_quest_statuses(db, campaign)
    recompute_weekly_missions(db, campaign)
    for state in state_map.values():
        recompute_skill_progress(db, campaign, state)
    recompute_badges(db, player, campaign, state_map)
    recompute_player_progress(db, player, campaign, state_map)
    db.commit()


def complete_quest_instance(
    db: Session,
    quest: Quest,
    tracker_type: str = "",
    tracker_entry_id: int | None = None,
    error_log_id: int | None = None,
    writing_entry_id: int | None = None,
    speaking_entry_id: int | None = None,
    mock_test_id: int | None = None,
    raw_score: str = "",
    completion_note: str = "",
) -> Quest:
    today = date.today()
    if quest.quest_date > today:
        raise ValueError("Future quest cannot be completed yet")
    if quest.status == "expired":
        raise ValueError("Expired quest cannot be completed")
    if not quest.completed:
        tracker_type, tracker_entry_id, typed_values = resolve_tracker_payload(
            db,
            tracker_type=tracker_type,
            tracker_entry_id=tracker_entry_id,
            error_log_id=error_log_id,
            writing_entry_id=writing_entry_id,
            speaking_entry_id=speaking_entry_id,
            mock_test_id=mock_test_id,
        )
        quest.completed = True
        quest.completed_at = datetime.utcnow()
        quest.reward_claimed = False
        quest.reward_claimed_at = None
        for field_name, value in typed_values.items():
            if value is not None:
                setattr(quest, field_name, value)
        quest.raw_score = raw_score or quest.raw_score
        quest.completion_note = completion_note or quest.completion_note
        quest.status = "completed"
        quest.completed_mode = "on_time"
        quest.earned_xp = quest.base_xp or quest.xp
    db.flush()
    refresh_progress_state(db)
    db.refresh(quest)
    return quest


# ---------------------------------------------------------------------------
# I4-2: Collocation flashcard service helpers
# ---------------------------------------------------------------------------

_FAMILIARITY_DECAY_ORDER = ["again", "hard", "good"]  # easy never decays


def effective_familiarity(
    stored: str,
    familiarity_set_at: datetime | None,
    now: datetime | None = None,
) -> str:
    """Compute effective familiarity after 7-day-per-tier lazy decay.

    Rules (spec: TASKS.md Phase 4 owner decision):
    - 'easy' never decays — always returned as-is (graduated).
    - For again/hard/good: drop one tier per full 7-day window since
      familiarity_set_at, floored at 'again'.
    - If familiarity_set_at is None, treat as freshly set (no decay).
    """
    if stored == "easy":
        return "easy"
    if familiarity_set_at is None or stored not in _FAMILIARITY_DECAY_ORDER:
        return stored if stored in _FAMILIARITY_DECAY_ORDER else "again"
    if now is None:
        now = datetime.utcnow()
    elapsed_days = (now - familiarity_set_at).total_seconds() / 86400.0
    tiers_dropped = int(elapsed_days // 7)
    if tiers_dropped == 0:
        return stored
    current_index = _FAMILIARITY_DECAY_ORDER.index(stored)
    decayed_index = max(0, current_index - tiers_dropped)
    return _FAMILIARITY_DECAY_ORDER[decayed_index]


def try_autocomplete_collocation_forge(
    db: Session,
    player_id: int,
    campaign_id: int,
    today: date,
) -> bool:
    """Auto-complete today's Collocation Forge daily quest if player reviewed
    5+ DISTINCT collocations today (anti-farm: distinct item count per day).

    Only marks completed=True, reward_claimed stays False (claim stays manual).
    Idempotent — safe to call multiple times.

    Returns True if the quest was newly auto-completed, False otherwise.
    """
    # Count distinct collocation_item_id reviewed today
    distinct_count = (
        db.query(func.count(func.distinct(CollocationFlashcard.collocation_item_id)))
        .filter(
            CollocationFlashcard.player_id == player_id,
            CollocationFlashcard.campaign_id == campaign_id,
            func.date(CollocationFlashcard.familiarity_set_at) == today,
        )
        .scalar()
        or 0
    )
    if distinct_count < 5:
        return False

    # Find today's Collocation Forge daily quest
    forge_quest = (
        db.query(Quest)
        .filter(
            Quest.campaign_id == campaign_id,
            Quest.session_type == "Daily Quest",
            Quest.quest_date == today,
            Quest.daily_slot_code == "vocab_collocation",
        )
        .first()
    )
    if forge_quest is None:
        return False  # edge case: no quest generated for today
    if forge_quest.completed:
        return False  # already completed (manual or earlier)

    # Auto-complete (no tracker proof needed — this IS the proof)
    forge_quest.completed = True
    forge_quest.completed_at = datetime.utcnow()
    forge_quest.reward_claimed = False
    forge_quest.reward_claimed_at = None
    forge_quest.status = "completed"
    forge_quest.completed_mode = "on_time"
    forge_quest.earned_xp = forge_quest.base_xp or forge_quest.xp
    forge_quest.completion_note = "Auto-completed: 5 distinct collocations reviewed today"
    db.flush()
    return True


def uncomplete_quest_instance(db: Session, quest: Quest) -> Quest:
    if quest.completed:
        if quest.reward_claimed:
            raise ValueError("Claimed quest cannot be rolled back")
        quest.completed = False
        quest.completed_at = None
        quest.earned_xp = 0
        quest.reward_claimed = False
        quest.reward_claimed_at = None
        quest.completed_mode = None
        quest.error_log_id = None
        quest.writing_entry_id = None
        quest.speaking_entry_id = None
        quest.mock_test_id = None
    db.flush()
    refresh_progress_state(db)
    db.refresh(quest)
    return quest


def compare_ranks(current_rank: str, suggested_rank: str) -> str:
    current_index = RANK_ORDER.index(current_rank) if current_rank in RANK_ORDER else 0
    suggested_index = RANK_ORDER.index(suggested_rank) if suggested_rank in RANK_ORDER else 0
    if suggested_index > current_index:
        return "up"
    if suggested_index < current_index:
        return "down"
    return "same"


def normalize_cefr_rank(level: str) -> str:
    mapping = {
        "A1": "F",
        "A2": "E",
        "B1": "C",
        "B2": "B",
        "C1": "A",
        "C2": "S",
    }
    return mapping.get(level.upper(), "F")


def infer_rank_from_test_record(test_record: TestRecord, skill_name: str) -> str:
    if test_record.test_type in {"Aptis", "CEFR"}:
        score = ""
        if skill_name == "Listening":
            score = test_record.listening_score
        elif skill_name == "Reading":
            score = test_record.reading_score
        elif skill_name == "Writing":
            score = test_record.writing_score
        elif skill_name == "Speaking":
            score = test_record.speaking_score
        score = score or test_record.cefr_level or test_record.overall_score
        return normalize_cefr_rank(score)

    if test_record.test_type == "TOEIC":
        raw_score = ""
        if skill_name == "Listening":
            raw_score = test_record.listening_score
        elif skill_name == "Reading":
            raw_score = test_record.reading_score
        elif skill_name == "Writing":
            raw_score = test_record.writing_score
        elif skill_name == "Speaking":
            raw_score = test_record.speaking_score
        try:
            numeric = int(float(raw_score))
        except (TypeError, ValueError):
            numeric = 0
        if numeric >= 400:
            return "B"
        if numeric >= 300:
            return "C"
        if numeric >= 150:
            return "D"
        if numeric > 0:
            return "E"
        return "F"

    if test_record.test_type == "IELTS":
        raw_score = ""
        if skill_name == "Listening":
            raw_score = test_record.listening_score
        elif skill_name == "Reading":
            raw_score = test_record.reading_score
        elif skill_name == "Writing":
            raw_score = test_record.writing_score
        elif skill_name == "Speaking":
            raw_score = test_record.speaking_score
        else:
            raw_score = test_record.overall_score
        try:
            numeric = float(raw_score)
        except (TypeError, ValueError):
            numeric = 0.0
        if numeric >= 7.5:
            return "S"
        if numeric >= 6.5:
            return "A"
        if numeric >= 5.5:
            return "B"
        if numeric >= 4.5:
            return "C"
        if numeric > 0:
            return "D"
        return "F"
    return "F"


def create_rank_suggestions_for_test(db: Session, test_record: TestRecord) -> list[SkillRankSuggestion]:
    created: list[SkillRankSuggestion] = []
    campaign = db.query(Campaign).filter(Campaign.id == test_record.campaign_id).first()
    state_map = get_campaign_skill_state_map(db, campaign) if campaign else {}
    for skill in db.query(Skill).filter(Skill.name.in_(["Listening", "Reading", "Writing", "Speaking"])).all():
        state = state_map.get(skill.id)
        suggested_rank = infer_rank_from_test_record(test_record, skill.name)
        if suggested_rank == "F" and not any(
            [
                test_record.listening_score,
                test_record.reading_score,
                test_record.writing_score,
                test_record.speaking_score,
                test_record.overall_score,
                test_record.cefr_level,
            ]
        ):
            continue
        suggestion = SkillRankSuggestion(
            skill_id=skill.id,
            campaign_id=test_record.campaign_id,
            source_test_record_id=test_record.id,
            current_rank=state.confirmed_rank if state else "F",
            suggested_rank=suggested_rank,
            direction=compare_ranks(state.confirmed_rank if state else "F", suggested_rank),
            status="pending",
        )
        db.add(suggestion)
        created.append(suggestion)
    return created


def map_ielts_score_to_rank(score: float | None) -> str:
    if score is None:
        return "F"
    if score >= 7.0:
        return "S"
    elif score >= 6.5:
        return "A"
    elif score >= 6.0:
        return "B"
    elif score >= 5.0:
        return "C"
    elif score >= 4.5:
        return "D"
    elif score >= 4.0:
        return "E"
    else:
        return "F"


def create_rank_suggestions_for_certificate(db: Session, cert: CertificateRecord) -> list[SkillRankSuggestion]:
    if not cert.campaign_id:
        return []
    
    campaign = db.query(Campaign).filter(Campaign.id == cert.campaign_id).first()
    if not campaign:
        return []
        
    state_map = get_campaign_skill_state_map(db, campaign)
    created: list[SkillRankSuggestion] = []
    
    # Component skills (direct score mapping)
    components = {
        "Listening": cert.listening_score,
        "Reading": cert.reading_score,
        "Writing": cert.writing_score,
        "Speaking": cert.speaking_score,
    }
    # Inferred skills — no direct IELTS band; use overall_score as proxy
    # Grammar + Collocation are support sources (not matrix skills), so excluded here.
    inferred = {
        "Vocabulary": cert.overall_score,
    }

    all_skills = {**components, **inferred}

    for skill_name, score in all_skills.items():
        if score is not None:
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if skill:
                state = state_map.get(skill.id)
                current_rank = state.confirmed_rank if state else "F"
                suggested_rank = map_ielts_score_to_rank(score)

                existing = db.query(SkillRankSuggestion).filter(
                    SkillRankSuggestion.campaign_id == cert.campaign_id,
                    SkillRankSuggestion.skill_id == skill.id,
                    SkillRankSuggestion.status == "pending"
                ).first()

                if existing:
                    existing.suggested_rank = suggested_rank
                    existing.current_rank = current_rank
                    existing.direction = compare_ranks(current_rank, suggested_rank)
                    existing.source_certificate_record_id = cert.id
                    created.append(existing)
                else:
                    suggestion = SkillRankSuggestion(
                        skill_id=skill.id,
                        campaign_id=cert.campaign_id,
                        source_certificate_record_id=cert.id,
                        current_rank=current_rank,
                        suggested_rank=suggested_rank,
                        direction=compare_ranks(current_rank, suggested_rank),
                        status="pending"
                    )
                    db.add(suggestion)
                    created.append(suggestion)

    db.flush()
    return created


def award_skill_xp(
    db: Session,
    campaign_id: int,
    skill_id: int,
    xp: int,
    idempotency_key: str,
    transaction_type: str = "quest_reward",
) -> None:
    from .models import SkillXpTransaction, CampaignSkillState

    if not idempotency_key:
        raise ValueError("idempotency_key is required for xp transactions")

    existing = db.query(SkillXpTransaction).filter(SkillXpTransaction.idempotency_key == idempotency_key).first()
    if existing:
        return

    tx = SkillXpTransaction(
        campaign_id=campaign_id,
        skill_id=skill_id,
        xp=xp,
        transaction_type=transaction_type,
        idempotency_key=idempotency_key,
    )
    db.add(tx)

    state = db.query(CampaignSkillState).filter(CampaignSkillState.campaign_id == campaign_id, CampaignSkillState.skill_id == skill_id).first()
    if not state:
        # create state if missing
        state = CampaignSkillState(campaign_id=campaign_id, skill_id=skill_id, xp=0, rank="F", confirmed_rank="F", level=1, streak=0)
        db.add(state)
        db.flush()

    state.xp = (state.xp or 0) + (xp or 0)
    state.rank, state.level = get_rank_level(state.xp)
    db.flush()


def award_player_xp(
    db: Session,
    campaign_id: int,
    player_id: int,
    xp: int,
    idempotency_key: str,
    transaction_type: str = "mission_reward",
) -> None:
    # NO-OP: player never accrues XP directly.
    # player_xp = mean(5 matrix skills), computed in recompute_player_progress.
    # spec: ielts_xp_policy_rank_quest_spec.md §1.2
    pass


def apply_rank_suggestion(db: Session, suggestion: SkillRankSuggestion) -> SkillRankSuggestion:
    campaign = db.query(Campaign).filter(Campaign.id == suggestion.campaign_id).first()
    if not campaign:
        raise ValueError("Campaign not found for rank suggestion")
    state = get_campaign_skill_state_map(db, campaign).get(suggestion.skill_id)
    if not state:
        raise ValueError("Campaign skill state not found")
    old_rank = state.confirmed_rank
    state.confirmed_rank = suggestion.suggested_rank

    # Elevate XP to the minimum for the confirmed rank so the progress bar reflects reality
    min_xp = 0
    try:
        policy = db.query(RankXpThreshold).filter_by(rank_name=suggestion.suggested_rank).first()
        if policy:
            min_xp = policy.min_xp
        else:
            min_xp = RANK_MIN_XP.get(suggestion.suggested_rank, 0)
    except Exception:
        min_xp = RANK_MIN_XP.get(suggestion.suggested_rank, 0)

    if (state.xp or 0) < min_xp:
        state.xp = min_xp

    # Elevate state.rank to match confirmed_rank (certificate bypasses boss)
    if compare_ranks(state.rank, suggestion.suggested_rank) == "up":
        state.rank = suggestion.suggested_rank
    state.rank, state.level = get_rank_level(state.xp)
    # Ensure rank is never below confirmed_rank
    if RANK_ORDER.index(state.rank) < RANK_ORDER.index(state.confirmed_rank):
        state.rank = state.confirmed_rank
        state.level = _RANK_FIRST_LEVEL.get(state.confirmed_rank, 1)

    # Reset pending exam/boss promotion status
    state.pending_rank = None
    state.promotion_status = "none"
    state.promotion_unlocked_at = None
    
    suggestion.status = "applied"
    suggestion.resolved_at = datetime.utcnow()
    db.add(
        SkillRankHistory(
            skill_id=suggestion.skill_id,
            campaign_id=suggestion.campaign_id,
            old_rank=old_rank,
            new_rank=state.confirmed_rank,
            source_test_record_id=suggestion.source_test_record_id,
            source_certificate_record_id=suggestion.source_certificate_record_id,
            change_reason="Applied from pending suggestion",
        )
    )
    db.commit()
    db.refresh(suggestion)
    return suggestion


def dismiss_rank_suggestion(db: Session, suggestion: SkillRankSuggestion) -> SkillRankSuggestion:
    suggestion.status = "dismissed"
    suggestion.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


def estimate_band_from_mock(raw_score: str, test_type: str) -> str:
    if test_type not in {"Listening", "Reading"}:
        return ""
    try:
        score = int(float(raw_score))
    except (TypeError, ValueError):
        return ""
    if score >= 35:
        return "8.0"
    if score >= 30:
        return "7.0"
    if score >= 25:
        return "6.0"
    if score >= 20:
        return "5.5"
    if score >= 15:
        return "5.0"
    return "4.5"


def append_weakness_note(state: CampaignSkillState, detail: str) -> None:
    parts = [part.strip() for part in state.user_weakness_note.split("\n") if part.strip()]
    if detail.strip() not in parts:
        parts.append(detail.strip())
        state.user_weakness_note = "\n".join(parts)


def ensure_weakness_suggestions(db: Session, campaign: Campaign) -> None:
    today = date.today()
    fourteen_days_ago = today - timedelta(days=14)
    thirty_days_ago = today - timedelta(days=30)
    state_map = get_campaign_skill_state_map(db, campaign)

    dirty = False

    for skill in db.query(Skill).all():
        state = state_map.get(skill.id)
        if not state:
            continue
        active_count = (
            db.query(WeaknessSuggestion)
            .filter(
                WeaknessSuggestion.campaign_id == campaign.id,
                WeaknessSuggestion.skill_id == skill.id,
                WeaknessSuggestion.status == "pending",
            )
            .count()
        )
        if active_count >= 2:
            continue

        if state.last_practiced:
            inactivity_limit = 7 if skill.name in CORE_SKILLS else 5
            if (today - state.last_practiced).days >= inactivity_limit and active_count < 2:
                db.add(
                    WeaknessSuggestion(
                        skill_id=skill.id,
                        campaign_id=campaign.id,
                        title=f"{skill.name}: refresh needed",
                        detail="This skill has not been practiced recently enough for the current roadmap cadence.",
                        severity="medium",
                    )
                )
                state.last_system_suggestion_at = datetime.utcnow()
                active_count += 1
                dirty = True

        repeated_errors = (
            db.query(ErrorLog.error_tag, func.count(ErrorLog.id).label("error_count"))
            .filter(
                ErrorLog.campaign_id == campaign.id,
                ErrorLog.skill_id == skill.id,
                ErrorLog.logged_date >= thirty_days_ago,
            )
            .group_by(ErrorLog.error_tag)
            .having(func.count(ErrorLog.id) >= 3)
            .all()
        )
        if repeated_errors and active_count < 2:
            tag = repeated_errors[0][0] or "repeat-error"
            sample_error_log_id = (
                db.query(ErrorLog.id)
                .filter(
                    ErrorLog.campaign_id == campaign.id,
                    ErrorLog.skill_id == skill.id,
                    ErrorLog.error_tag == tag,
                    ErrorLog.logged_date >= thirty_days_ago,
                )
                .order_by(ErrorLog.logged_date.desc(), ErrorLog.id.desc())
                .limit(1)
                .scalar()
            )
            db.add(
                WeaknessSuggestion(
                    skill_id=skill.id,
                    campaign_id=campaign.id,
                    source_error_log_id=sample_error_log_id,
                    title=f"{skill.name}: repeated error pattern",
                    detail=f'The error tag "{tag}" has repeated at least 3 times in the last 30 days.',
                    severity="high",
                )
            )
            state.last_system_suggestion_at = datetime.utcnow()
            dirty = True

    if dirty:
        db.commit()


def apply_weakness_suggestion(db: Session, suggestion: WeaknessSuggestion) -> WeaknessSuggestion:
    campaign = db.query(Campaign).filter(Campaign.id == suggestion.campaign_id).first()
    if not campaign:
        raise ValueError("Campaign not found for weakness suggestion")
    state = get_campaign_skill_state_map(db, campaign).get(suggestion.skill_id)
    if not state:
        raise ValueError("Campaign skill state not found")
    append_weakness_note(state, suggestion.detail)
    suggestion.status = "applied"
    suggestion.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


def dismiss_weakness_suggestion(db: Session, suggestion: WeaknessSuggestion) -> WeaknessSuggestion:
    suggestion.status = "dismissed"
    suggestion.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


# --- Vocabulary Support Skill Services ---

def get_vocabulary_items(db: Session, player_id: int) -> list[VocabularyItem]:
    return (
        db.query(VocabularyItem)
        .options(joinedload(VocabularyItem.examples))
        .filter(VocabularyItem.player_id == player_id)
        .all()
    )


def get_vocabulary_item(db: Session, vocabulary_item_id: int) -> VocabularyItem | None:
    return (
        db.query(VocabularyItem)
        .options(joinedload(VocabularyItem.examples))
        .filter(VocabularyItem.id == vocabulary_item_id)
        .first()
    )


def create_vocabulary_item(db: Session, player_id: int, item_in: VocabularyItemIn) -> VocabularyItem:
    db_item = VocabularyItem(
        player_id=player_id,
        word=item_in.word,
        normalized_word=item_in.normalized_word,
        part_of_speech=item_in.part_of_speech,
        cefr_level=item_in.cefr_level,
        ielts_topic=item_in.ielts_topic,
        meaning_en=item_in.meaning_en,
        meaning_vi=item_in.meaning_vi,
        register_label=item_in.register_label,
        grammar_note=item_in.grammar_note,
        pronunciation_ipa=item_in.pronunciation_ipa,
        word_stress=item_in.word_stress,
        source_type=item_in.source_type,
        source_reference=item_in.source_reference,
        mastery_rank=item_in.mastery_rank,
        mastery_score=item_in.mastery_score,
        is_archived=item_in.is_archived,
    )
    db.add(db_item)
    db.flush()

    front_text = db_item.word
    if db_item.part_of_speech:
        front_text += f" ({db_item.part_of_speech})"
    if db_item.pronunciation_ipa:
        front_text += f" {db_item.pronunciation_ipa}"

    back_parts = []
    if db_item.meaning_en:
        back_parts.append(f"EN: {db_item.meaning_en}")
    if db_item.meaning_vi:
        back_parts.append(f"VI: {db_item.meaning_vi}")
    back_text = "\n".join(back_parts) or "No definition provided"

    db_card = Flashcard(
        player_id=player_id,
        vocabulary_item_id=db_item.id,
        card_type="meaning_recall",
        front_text=front_text,
        back_text=back_text,
        status="new",
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_vocabulary_item(db: Session, vocabulary_item_id: int, item_in: VocabularyItemIn) -> VocabularyItem | None:
    db_item = db.query(VocabularyItem).filter(VocabularyItem.id == vocabulary_item_id).first()
    if not db_item:
        return None
    for field, value in item_in.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    sync_node_status_from_item(db, db_item.player_id, vocabulary_item_id)
    return db_item


def delete_vocabulary_item(db: Session, vocabulary_item_id: int) -> bool:
    db_item = db.query(VocabularyItem).filter(VocabularyItem.id == vocabulary_item_id).first()
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True


def create_vocabulary_example(db: Session, player_id: int, vocabulary_item_id: int, example_in: VocabularyExampleIn) -> VocabularyExample:
    db_example = VocabularyExample(
        vocabulary_item_id=vocabulary_item_id,
        player_id=player_id,
        example_sentence=example_in.example_sentence,
        example_type=example_in.example_type,
        is_corrected=example_in.is_corrected,
        correction_note=example_in.correction_note,
    )
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    sync_node_status_from_item(db, player_id, vocabulary_item_id)
    return db_example


def delete_vocabulary_example(db: Session, example_id: int) -> bool:
    db_example = db.query(VocabularyExample).filter(VocabularyExample.id == example_id).first()
    if not db_example:
        return False
    vocabulary_item_id = db_example.vocabulary_item_id
    player_id = db_example.player_id
    db.delete(db_example)
    db.commit()
    sync_node_status_from_item(db, player_id, vocabulary_item_id)
    return True



def create_vocabulary_relation(db: Session, player_id: int, relation_in: VocabularyRelationIn) -> VocabularyRelation:
    db_relation = VocabularyRelation(
        player_id=player_id,
        source_word_id=relation_in.source_word_id,
        target_word_id=relation_in.target_word_id,
        target_text=relation_in.target_text,
        relation_type=relation_in.relation_type,
        note=relation_in.note,
    )
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def delete_vocabulary_relation(db: Session, relation_id: int) -> bool:
    db_relation = db.query(VocabularyRelation).filter(VocabularyRelation.id == relation_id).first()
    if not db_relation:
        return False
    db.delete(db_relation)
    db.commit()
    return True


def get_flashcards(db: Session, player_id: int) -> list[Flashcard]:
    return (
        db.query(Flashcard)
        .options(
            joinedload(Flashcard.vocabulary_item).joinedload(VocabularyItem.examples)
        )
        .filter(Flashcard.player_id == player_id)
        .all()
    )


def create_flashcard(db: Session, player_id: int, card_in: FlashcardIn) -> Flashcard:
    db_card = Flashcard(
        player_id=player_id,
        vocabulary_item_id=card_in.vocabulary_item_id,
        card_type=card_in.card_type,
        front_text=card_in.front_text,
        back_text=card_in.back_text,
        hint=card_in.hint,
        difficulty=card_in.difficulty,
        status=card_in.status,
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def get_due_flashcards(db: Session, player_id: int) -> list[Flashcard]:
    today = date.today()
    return (
        db.query(Flashcard)
        .options(
            joinedload(Flashcard.vocabulary_item).joinedload(VocabularyItem.examples)
        )
        .outerjoin(SpacedRepetitionState, Flashcard.id == SpacedRepetitionState.flashcard_id)
        .filter(Flashcard.player_id == player_id)
        .filter(
            (SpacedRepetitionState.due_date <= today)
            | (Flashcard.status == "new")
            | (SpacedRepetitionState.id.is_(None))
        )
        .all()
    )


def review_flashcard(db: Session, player_id: int, flashcard_id: int, result: str) -> SpacedRepetitionState:
    if result not in ["again", "hard", "good", "easy"]:
        raise ValueError("Invalid review result")

    state = db.query(SpacedRepetitionState).filter(
        SpacedRepetitionState.player_id == player_id,
        SpacedRepetitionState.flashcard_id == flashcard_id
    ).first()

    if not state:
        state = SpacedRepetitionState(
            player_id=player_id,
            flashcard_id=flashcard_id,
            ease_factor=2.5,
            interval_days=0,
            repetition_count=0,
        )
        db.add(state)

    interval_mapping = {
        "again": 0,
        "hard": 1,
        "good": 3,
        "easy": 7
    }
    interval_days = interval_mapping[result]
    
    state.interval_days = interval_days
    state.repetition_count += 1
    state.last_reviewed_at = datetime.utcnow()
    state.due_date = date.today() + timedelta(days=interval_days)
    
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if flashcard:
        flashcard.status = "reviewing" if result == "again" else "active"

    db.commit()
    db.refresh(state)
    if flashcard:
        sync_node_status_from_item(db, player_id, flashcard.vocabulary_item_id)
    return state


def get_vocabulary_topics(db: Session, player_id: int) -> list[VocabularyTopic]:
    return db.query(VocabularyTopic).filter(VocabularyTopic.player_id == player_id).all()


def create_vocabulary_topic(db: Session, player_id: int, topic_in: VocabularyTopicIn) -> VocabularyTopic:
    db_topic = VocabularyTopic(
        player_id=player_id,
        topic_name=topic_in.topic_name,
        parent_topic_id=topic_in.parent_topic_id,
        description=topic_in.description,
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


def get_topic_tree(db: Session, player_id: int, topic_id: int) -> tuple[VocabularyTopic | None, list[VocabularyNode], list[VocabularyEdge]]:
    topic = db.query(VocabularyTopic).filter(VocabularyTopic.player_id == player_id, VocabularyTopic.id == topic_id).first()
    if not topic:
        return None, [], []
    nodes = db.query(VocabularyNode).filter(VocabularyNode.player_id == player_id, VocabularyNode.topic_id == topic_id).all()
    
    # Get all node IDs to filter edges
    node_ids = [n.id for n in nodes]
    edges = []
    if node_ids:
        edges = db.query(VocabularyEdge).filter(
            VocabularyEdge.player_id == player_id,
            VocabularyEdge.source_node_id.in_(node_ids),
            VocabularyEdge.target_node_id.in_(node_ids)
        ).all()
    return topic, nodes, edges


def create_vocabulary_node(db: Session, player_id: int, node_in: VocabularyNodeIn) -> VocabularyNode:
    db_node = VocabularyNode(
        player_id=player_id,
        topic_id=node_in.topic_id,
        vocabulary_item_id=node_in.vocabulary_item_id,
        node_label=node_in.node_label,
        node_type=node_in.node_type,
        status=node_in.status,
        x_position=node_in.x_position,
        y_position=node_in.y_position,
        unlock_requirement=node_in.unlock_requirement,
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    if db_node.vocabulary_item_id:
        sync_node_status_from_item(db, player_id, db_node.vocabulary_item_id)
        db.refresh(db_node)
    return db_node


def update_vocabulary_node(db: Session, player_id: int, node_id: int, node_in: VocabularyNodeUpdate) -> VocabularyNode | None:
    db_node = db.query(VocabularyNode).filter(VocabularyNode.player_id == player_id, VocabularyNode.id == node_id).first()
    if not db_node:
        return None
    for field, value in node_in.model_dump(exclude_unset=True).items():
        setattr(db_node, field, value)
    db.commit()
    db.refresh(db_node)
    return db_node


def create_vocabulary_edge(db: Session, player_id: int, edge_in: VocabularyEdgeIn) -> VocabularyEdge:
    db_edge = VocabularyEdge(
        player_id=player_id,
        source_node_id=edge_in.source_node_id,
        target_node_id=edge_in.target_node_id,
        edge_type=edge_in.edge_type,
        strength=edge_in.strength,
    )
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge


def delete_vocabulary_edge(db: Session, player_id: int, edge_id: int) -> bool:
    db_edge = db.query(VocabularyEdge).filter(VocabularyEdge.player_id == player_id, VocabularyEdge.id == edge_id).first()
    if not db_edge:
        return False
    db.delete(db_edge)
    db.commit()
    return True


def sync_node_status_from_item(db: Session, player_id: int, item_id: int) -> None:
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id).first()
    if not item:
        return

    has_meaning = bool(item.meaning_en or item.meaning_vi)
    has_pos = bool(item.part_of_speech)

    example_count = db.query(VocabularyExample).filter(VocabularyExample.vocabulary_item_id == item_id).count()
    has_example = example_count > 0

    # Check player_collocation_progress status for items containing this word
    word = item.word.lower()
    collocation_progress_count = (
        db.query(PlayerCollocationProgress)
        .join(CollocationItem, PlayerCollocationProgress.collocation_item_id == CollocationItem.id)
        .filter(
            PlayerCollocationProgress.player_id == player_id,
            PlayerCollocationProgress.status.in_(["practiced", "mastered"]),
            CollocationItem.collocation.like(f"%{word}%")
        )
        .count()
    )
    has_collocation = collocation_progress_count > 0

    # Spaced repetition states
    srs = db.query(SpacedRepetitionState).join(Flashcard, Flashcard.id == SpacedRepetitionState.flashcard_id)\
            .filter(Flashcard.vocabulary_item_id == item_id).first()

    status = "locked"
    if item.mastery_rank in ["A", "S"]:
        status = "awakened"
    elif srs and (srs.repetition_count >= 3 or srs.interval_days >= 3) and has_collocation:
        status = "mastered"
    elif srs and srs.repetition_count > 0:
        status = "stabilized"
    elif has_meaning and has_pos and has_example:
        status = "activated"
    elif has_meaning:
        status = "discovered"

    # Find nodes and update status
    nodes = db.query(VocabularyNode).filter(VocabularyNode.vocabulary_item_id == item_id).all()
    for node in nodes:
        node.status = status
    db.commit()


import random

def _extract_core_word(collocation: str, db: Session) -> str:
    # Clean and split into words
    words = [w.strip("(),.?!").lower() for w in collocation.split() if w.strip("(),.?!")]
    
    # Check if any word matches a vocabulary item
    for w in words:
        if len(w) > 2:
            vocab_exists = db.query(VocabularyItem).filter(VocabularyItem.word == w).first()
            if vocab_exists:
                return vocab_exists.word.capitalize()
                
    # Fallback: return the last word that is not a common preposition/article
    ignore_words = {"a", "an", "the", "in", "on", "at", "to", "for", "with", "by", "of", "from", "up", "out", "off", "and", "or"}
    for w in reversed(words):
        if w not in ignore_words:
            return w.capitalize()
            
    return collocation.capitalize()


def get_collocation_practice(db: Session, player_id: int, count: int = 5):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player or not player.active_campaign_id:
        return {"matches": [], "distractors": []}
    campaign_id = player.active_campaign_id

    # Get all collocation items linked to the campaign
    items = (
        db.query(CollocationItem)
        .join(CollocationTopic, CollocationItem.topic_id == CollocationTopic.id)
        .join(CollocationSection, CollocationTopic.section_id == CollocationSection.id)
        .join(CollocationCollection, CollocationSection.collection_id == CollocationCollection.id)
        .join(CampaignCollocationLink, CollocationCollection.id == CampaignCollocationLink.collection_id)
        .filter(CampaignCollocationLink.campaign_id == campaign_id)
        .all()
    )
    if not items:
        return {"matches": [], "distractors": []}

    # Get player progress for these items to prioritize new/learning ones
    progresses = db.query(PlayerCollocationProgress).filter_by(
        player_id=player_id,
        campaign_id=campaign_id,
    ).all()
    progress_map = {p.collocation_item_id: p.status for p in progresses}

    prioritized_items = []
    other_items = []
    for item in items:
        status = progress_map.get(item.id, "new")
        if status in ("new", "learning"):
            prioritized_items.append(item)
        else:
            other_items.append(item)

    random.shuffle(prioritized_items)
    random.shuffle(other_items)

    selected_items = prioritized_items[:count]
    if len(selected_items) < count:
        selected_items += other_items[:(count - len(selected_items))]

    matches = []
    for item in selected_items:
        core_word = _extract_core_word(item.collocation, db)
        matches.append({
            "collocation_id": item.id,
            "core_word": core_word,
            "collocation": item.collocation,
            "collocation_type": item.collocation_type or "Collocation"
        })

    selected_ids = {item.id for item in selected_items}
    remaining_items = [item for item in items if item.id not in selected_ids]
    
    # Shuffle remaining items to get random distractors
    random.shuffle(remaining_items)
    distractors = [item.collocation for item in remaining_items[:3]]

    return {"matches": matches, "distractors": distractors}


def get_shadow_duel_practice(db: Session, player_id: int, count: int = 10):
    FALLBACK_SHADOW_DUEL = [
        # Synonyms
        {"word": "abundant", "question_type": "synonym", "correct_answer": "plentiful", "distractors": ["scarce", "limited", "heavy"]},
        {"word": "acquire", "question_type": "synonym", "correct_answer": "obtain", "distractors": ["lose", "give", "avoid"]},
        {"word": "advocate", "question_type": "synonym", "correct_answer": "support", "distractors": ["oppose", "ignore", "destroy"]},
        {"word": "ambiguous", "question_type": "synonym", "correct_answer": "unclear", "distractors": ["precise", "obvious", "simple"]},
        {"word": "compulsory", "question_type": "synonym", "correct_answer": "mandatory", "distractors": ["optional", "voluntary", "free"]},
        {"word": "enhance", "question_type": "synonym", "correct_answer": "improve", "distractors": ["damage", "reduce", "maintain"]},
        {"word": "obstacle", "question_type": "synonym", "correct_answer": "barrier", "distractors": ["aid", "helper", "bridge"]},
        {"word": "reliable", "question_type": "synonym", "correct_answer": "dependable", "distractors": ["doubtful", "weak", "unstable"]},
        # Antonyms
        {"word": "benefit", "question_type": "antonym", "correct_answer": "drawback", "distractors": ["advantage", "gain", "profit"]},
        {"word": "urban", "question_type": "antonym", "correct_answer": "rural", "distractors": ["modern", "crowded", "suburban"]},
        {"word": "temporary", "question_type": "antonym", "correct_answer": "permanent", "distractors": ["short", "brief", "limited"]},
        {"word": "significant", "question_type": "antonym", "correct_answer": "insignificant", "distractors": ["noticeable", "important", "major"]},
        {"word": "obsolete", "question_type": "antonym", "correct_answer": "modern", "distractors": ["outdated", "old", "ancient"]},
        {"word": "vague", "question_type": "antonym", "correct_answer": "clear", "distractors": ["dim", "uncertain", "misty"]},
        # Register (informal -> formal/better IELTS writing)
        {"word": "kids", "question_type": "register", "correct_answer": "children", "distractors": ["infants", "toddlers", "youths"], "register_note": "In IELTS Writing Task 2, use 'children' or 'offspring' instead of informal 'kids'."},
        {"word": "cop", "question_type": "register", "correct_answer": "police officer", "distractors": ["detective", "soldier", "security guard"], "register_note": "In IELTS, use 'police officer' or 'law enforcement' instead of informal slang 'cop'."},
        {"word": "get", "question_type": "register", "correct_answer": "receive / obtain", "distractors": ["take", "give", "bring"], "register_note": "Use more academic verbs like 'obtain', 'acquire', or 'receive' instead of 'get'."},
        {"word": "bad", "question_type": "register", "correct_answer": "detrimental / negative", "distractors": ["poor", "terrible", "awful"], "register_note": "Use 'detrimental' or 'unfavorable' to sound more academic than the generic word 'bad'."},
        {"word": "think", "question_type": "register", "correct_answer": "believe / maintain", "distractors": ["know", "assume", "guess"], "register_note": "Use 'maintain', 'believe', or 'opine' instead of 'think' for expressing arguments."}
    ]

    questions = []

    # 1. Try to query relations from DB
    relations = (
        db.query(VocabularyRelation)
        .filter(VocabularyRelation.player_id == player_id)
        .filter(VocabularyRelation.relation_type.in_(["synonym", "antonym", "register_alternative"]))
        .all()
    )

    all_items = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id).all()
    item_map = {item.id: item for item in all_items}
    word_list = [item.word for item in all_items]

    for rel in relations:
        source_item = item_map.get(rel.source_word_id)
        if not source_item:
            continue

        target_word = ""
        if rel.target_word_id:
            target_item = item_map.get(rel.target_word_id)
            if target_item:
                target_word = target_item.word
        elif rel.target_text:
            target_word = rel.target_text

        if not target_word:
            continue

        qtype = "synonym"
        if rel.relation_type == "antonym":
            qtype = "antonym"
        elif rel.relation_type == "register_alternative":
            qtype = "register"

        # Generate distractors from DB vocabulary items, excluding source & target
        possible_distractors = [w for w in word_list if w != source_item.word and w != target_word]
        while len(possible_distractors) < 3:
            possible_distractors.append(random.choice(["easy", "hard", "make", "take", "give", "result", "factor"]))
        
        distractors = random.sample(possible_distractors, 3)
        options = [target_word] + distractors
        random.shuffle(options)

        questions.append({
            "word": source_item.word,
            "question_type": qtype,
            "correct_answer": target_word,
            "options": options,
            "register_note": rel.note if qtype == "register" else None
        })

    # 2. Check for items with register labels directly
    register_items = [item for item in all_items if item.register_label and item.register_label.lower() == "informal"]
    for item in register_items:
        if any(q["word"] == item.word and q["question_type"] == "register" for q in questions):
            continue

        correct_ans = "people / individuals"
        if item.meaning_en:
            correct_ans = item.meaning_en.split(",")[0]
        
        possible_distractors = [w for w in word_list if w != item.word and w != correct_ans]
        while len(possible_distractors) < 3:
            possible_distractors.append(random.choice(["easy", "hard", "make", "take", "give"]))
        distractors = random.sample(possible_distractors, 3)
        options = [correct_ans] + distractors
        random.shuffle(options)

        questions.append({
            "word": item.word,
            "question_type": "register",
            "correct_answer": correct_ans,
            "options": options,
            "register_note": f"Change informal '{item.word}' to academic '{correct_ans}'."
        })

    # 3. Fallback to hardcoded list if we don't have enough (less than 10 relations)
    if len(questions) < count:
        needed = count - len(questions)
        fallback_pool = [q for q in FALLBACK_SHADOW_DUEL if not any(existing["word"] == q["word"] and existing["question_type"] == q["question_type"] for existing in questions)]
        
        selected_fallbacks = random.sample(fallback_pool, min(needed, len(fallback_pool)))
        for fb in selected_fallbacks:
            options = [fb["correct_answer"]] + fb["distractors"]
            random.shuffle(options)
            questions.append({
                "word": fb["word"],
                "question_type": fb["question_type"],
                "correct_answer": fb["correct_answer"],
                "options": options,
                "register_note": fb.get("register_note")
            })

    random.shuffle(questions)
    return {"questions": questions[:count]}


def record_practice_success(db: Session, player_id: int, words: list[str]) -> dict:
    updated_count = 0
    for word_str in words:
        item = (
            db.query(VocabularyItem)
            .filter(VocabularyItem.player_id == player_id)
            .filter(VocabularyItem.word == word_str)
            .first()
        )
        if item:
            item.mastery_score = (item.mastery_score or 0) + 2
            score = item.mastery_score
            if score >= 50:
                item.mastery_rank = "S"
            elif score >= 40:
                item.mastery_rank = "A"
            elif score >= 30:
                item.mastery_rank = "B"
            elif score >= 20:
                item.mastery_rank = "C"
            elif score >= 10:
                item.mastery_rank = "D"
            elif score >= 5:
                item.mastery_rank = "E"
            else:
                item.mastery_rank = "F"
            
            sync_node_status_from_item(db, player_id, item.id)
            updated_count += 1
            
    db.commit()
    return {"status": "success", "updated_count": updated_count}


def get_word_families_practice(db: Session, player_id: int) -> dict:
    FALLBACK_FAMILIES = [
        {
            "family_id": "fam-produce",
            "root_word": "produce",
            "nodes": [
                {"id": "node-produce", "label": "produce", "part_of_speech": "verb", "meaning": "to make or grow something", "cefr_level": "B1", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-product", "label": "product", "part_of_speech": "noun", "meaning": "something that is made", "cefr_level": "B1", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-production", "label": "production", "part_of_speech": "noun", "meaning": "the process of making something", "cefr_level": "B2", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-productive", "label": "productive", "part_of_speech": "adjective", "meaning": "achieving a lot", "cefr_level": "B2", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-productivity", "label": "productivity", "part_of_speech": "noun", "meaning": "rate of production", "cefr_level": "C1", "mastery_rank": "F", "is_discovered": False}
            ],
            "edges": [
                {"id": "edge-p-prod", "source": "node-produce", "target": "node-product", "label": "noun"},
                {"id": "edge-p-prodb", "source": "node-produce", "target": "node-production", "label": "noun"},
                {"id": "edge-p-produc", "source": "node-produce", "target": "node-productive", "label": "adjective"},
                {"id": "edge-p-productiv", "source": "node-productive", "target": "node-productivity", "label": "noun"}
            ]
        },
        {
            "family_id": "fam-communicate",
            "root_word": "communicate",
            "nodes": [
                {"id": "node-communicate", "label": "communicate", "part_of_speech": "verb", "meaning": "to share information", "cefr_level": "B1", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-communication", "label": "communication", "part_of_speech": "noun", "meaning": "exchange of information", "cefr_level": "B1", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-communicative", "label": "communicative", "part_of_speech": "adjective", "meaning": "talkative / willing to talk", "cefr_level": "C1", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-communicator", "label": "communicator", "part_of_speech": "noun", "meaning": "a person who communicates", "cefr_level": "C1", "mastery_rank": "F", "is_discovered": False}
            ],
            "edges": [
                {"id": "edge-c-comm", "source": "node-communicate", "target": "node-communication", "label": "noun"},
                {"id": "edge-c-commc", "source": "node-communicate", "target": "node-communicative", "label": "adjective"},
                {"id": "edge-c-commu", "source": "node-communicate", "target": "node-communicator", "label": "noun"}
            ]
        },
        {
            "family_id": "fam-create",
            "root_word": "create",
            "nodes": [
                {"id": "node-create", "label": "create", "part_of_speech": "verb", "meaning": "to make something new", "cefr_level": "A2", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-creation", "label": "creation", "part_of_speech": "noun", "meaning": "the act of making something", "cefr_level": "B2", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-creative", "label": "creative", "part_of_speech": "adjective", "meaning": "having original ideas", "cefr_level": "B1", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-creativity", "label": "creativity", "part_of_speech": "noun", "meaning": "quality of being creative", "cefr_level": "B2", "mastery_rank": "F", "is_discovered": False},
                {"id": "node-creator", "label": "creator", "part_of_speech": "noun", "meaning": "person who creates", "cefr_level": "B2", "mastery_rank": "F", "is_discovered": False}
            ],
            "edges": [
                {"id": "edge-cr-creat", "source": "node-create", "target": "node-creation", "label": "noun"},
                {"id": "edge-cr-creatc", "source": "node-create", "target": "node-creative", "label": "adjective"},
                {"id": "edge-cr-creativ", "source": "node-creative", "target": "node-creativity", "label": "noun"},
                {"id": "edge-cr-creato", "source": "node-create", "target": "node-creator", "label": "noun"}
            ]
        }
    ]

    all_items = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id).all()
    item_map = {item.word.lower(): item for item in all_items}

    def sync_family_discovery(fam):
        for node in fam["nodes"]:
            word_key = node["label"].lower()
            if word_key in item_map:
                db_item = item_map[word_key]
                node["is_discovered"] = True
                node["cefr_level"] = db_item.cefr_level or node["cefr_level"]
                node["mastery_rank"] = db_item.mastery_rank
                if db_item.meaning_en:
                    node["meaning"] = db_item.meaning_en

    for fam in FALLBACK_FAMILIES:
        sync_family_discovery(fam)

    db_families = []
    relations = (
        db.query(VocabularyRelation)
        .filter(VocabularyRelation.player_id == player_id)
        .filter(VocabularyRelation.relation_type == "word_family")
        .all()
    )

    from collections import defaultdict
    grouped = defaultdict(list)
    for rel in relations:
        grouped[rel.source_word_id].append(rel)

    for src_id, rels in grouped.items():
        src_item = db.query(VocabularyItem).filter(VocabularyItem.id == src_id).first()
        if not src_item:
            continue

        nodes = []
        edges = []
        
        src_node_id = f"node-{src_item.id}"
        nodes.append({
            "id": src_node_id,
            "label": src_item.word,
            "part_of_speech": src_item.part_of_speech,
            "meaning": src_item.meaning_en,
            "cefr_level": src_item.cefr_level,
            "mastery_rank": src_item.mastery_rank,
            "is_discovered": True
        })

        for i, rel in enumerate(rels):
            target_word = ""
            target_pos = None
            target_meaning = None
            target_cefr = None
            target_rank = "F"
            is_disc = False

            if rel.target_word_id:
                t_item = db.query(VocabularyItem).filter(VocabularyItem.id == rel.target_word_id).first()
                if t_item:
                    target_word = t_item.word
                    target_pos = t_item.part_of_speech
                    target_meaning = t_item.meaning_en
                    target_cefr = t_item.cefr_level
                    target_rank = t_item.mastery_rank
                    is_disc = True
            elif rel.target_text:
                target_word = rel.target_text
                word_key = target_word.lower()
                if word_key in item_map:
                    t_item = item_map[word_key]
                    target_pos = t_item.part_of_speech
                    target_meaning = t_item.meaning_en
                    target_cefr = t_item.cefr_level
                    target_rank = t_item.mastery_rank
                    is_disc = True

            if not target_word:
                continue

            target_node_id = f"node-rel-{rel.id}"
            nodes.append({
                "id": target_node_id,
                "label": target_word,
                "part_of_speech": target_pos,
                "meaning": target_meaning,
                "cefr_level": target_cefr,
                "mastery_rank": target_rank,
                "is_discovered": is_disc
            })

            edges.append({
                "id": f"edge-rel-{rel.id}",
                "source": src_node_id,
                "target": target_node_id,
                "label": target_pos or "derived"
            })

        db_families.append({
            "family_id": f"fam-db-{src_item.id}",
            "root_word": src_item.word,
            "nodes": nodes,
            "edges": edges
        })

    all_families = db_families + FALLBACK_FAMILIES
    return {"families": all_families}


def get_echo_chamber_practice(db: Session, player_id: int, count: int = 10) -> dict:
    FALLBACK_ECHO = [
        {"word": "significant", "part_of_speech": "adjective", "pronunciation_ipa": "/sɪɡˈnɪfɪkənt/", "word_stress": "sig-NIF-i-cant", "syllables": ["sig", "nif", "i", "cant"], "stressed_index": 1, "silent_letters": []},
        {"word": "academic", "part_of_speech": "adjective", "pronunciation_ipa": "/ˌækəˈdemɪk/", "word_stress": "ac-a-DEM-ic", "syllables": ["ac", "a", "dem", "ic"], "stressed_index": 2, "silent_letters": []},
        {"word": "education", "part_of_speech": "noun", "pronunciation_ipa": "/ˌedʒuˈkeɪʃn/", "word_stress": "ed-u-CA-tion", "syllables": ["ed", "u", "ca", "tion"], "stressed_index": 2, "silent_letters": []},
        {"word": "Wednesday", "part_of_speech": "noun", "pronunciation_ipa": "/ˈwenzdeɪ/", "word_stress": "WEDNES-day", "syllables": ["wednes", "day"], "stressed_index": 0, "silent_letters": ["d"]},
        {"word": "doubt", "part_of_speech": "noun", "pronunciation_ipa": "/daʊt/", "word_stress": "DOUBT", "syllables": ["doubt"], "stressed_index": 0, "silent_letters": ["b"]},
        {"word": "knowledge", "part_of_speech": "noun", "pronunciation_ipa": "/ˈnɒlɪdʒ/", "word_stress": "KNOWL-edge", "syllables": ["knowl", "edge"], "stressed_index": 0, "silent_letters": ["k", "w"]},
        {"word": "honest", "part_of_speech": "adjective", "pronunciation_ipa": "/ˈɒnɪst/", "word_stress": "HON-est", "syllables": ["hon", "est"], "stressed_index": 0, "silent_letters": ["h"]},
        {"word": "foreign", "part_of_speech": "adjective", "pronunciation_ipa": "/ˈfɒrən/", "word_stress": "FOR-eign", "syllables": ["for", "eign"], "stressed_index": 0, "silent_letters": ["g"]},
        {"word": "receipt", "part_of_speech": "noun", "pronunciation_ipa": "/rɪˈsiːt/", "word_stress": "re-CEIPT", "syllables": ["re", "ceipt"], "stressed_index": 1, "silent_letters": ["p"]},
        {"word": "island", "part_of_speech": "noun", "pronunciation_ipa": "/ˈaɪlənd/", "word_stress": "IS-land", "syllables": ["is", "land"], "stressed_index": 0, "silent_letters": ["s"]}
    ]

    questions = []

    # Query custom items with IPA & stress
    items = (
        db.query(VocabularyItem)
        .filter(VocabularyItem.player_id == player_id)
        .filter(VocabularyItem.pronunciation_ipa != None)
        .filter(VocabularyItem.word_stress != None)
        .all()
    )

    for item in items:
        stress_str = item.word_stress.strip()
        if not stress_str:
            continue
        
        raw_syllables = stress_str.split("-")
        syllables = [s.lower() for s in raw_syllables]
        
        stressed_idx = 0
        for i, s in enumerate(raw_syllables):
            if any(c.isupper() for c in s):
                stressed_idx = i
                break
                
        silent_letters = []
        word_lower = item.word.lower()
        if "mb" in word_lower and word_lower.endswith("mb"):
            silent_letters.append("b")
        if "kn" in word_lower:
            silent_letters.append("k")
        if "wr" in word_lower:
            silent_letters.append("w")
        if "ps" in word_lower and word_lower.startswith("ps"):
            silent_letters.append("p")

        questions.append({
            "word": item.word,
            "part_of_speech": item.part_of_speech,
            "pronunciation_ipa": item.pronunciation_ipa,
            "word_stress": item.word_stress,
            "syllables": syllables,
            "stressed_index": stressed_idx,
            "silent_letters": silent_letters
        })

    # Combine and fallback
    if len(questions) < count:
        needed = count - len(questions)
        fallback_pool = [q for q in FALLBACK_ECHO if not any(existing["word"].lower() == q["word"].lower() for existing in questions)]
        selected = random.sample(fallback_pool, min(needed, len(fallback_pool)))
        questions.extend(selected)

    random.shuffle(questions)
    return {"questions": questions[:count]}


def get_active_vocabulary_errors(db: Session, player_id: int) -> list[VocabularyError]:
    return (
        db.query(VocabularyError)
        .filter(VocabularyError.player_id == player_id, VocabularyError.status == "active")
        .all()
    )


def get_all_vocabulary_errors(db: Session, player_id: int) -> list[VocabularyError]:
    return (
        db.query(VocabularyError)
        .filter(VocabularyError.player_id == player_id)
        .all()
    )


def create_vocabulary_error(db: Session, player_id: int, error_in: VocabularyErrorIn) -> VocabularyError:
    db_error = VocabularyError(
        player_id=player_id,
        vocabulary_item_id=error_in.vocabulary_item_id,
        error_type=error_in.error_type,
        wrong_text=error_in.wrong_text,
        corrected_text=error_in.corrected_text,
        explanation=error_in.explanation,
        status="active",
        defeated_count=0,
    )
    db.add(db_error)
    db.commit()
    db.refresh(db_error)
    return db_error


def update_vocabulary_error(db: Session, player_id: int, error_id: int, error_in: VocabularyErrorIn) -> VocabularyError | None:
    db_error = db.query(VocabularyError).filter(VocabularyError.id == error_id, VocabularyError.player_id == player_id).first()
    if not db_error:
        return None
    for field, value in error_in.model_dump(exclude_unset=True).items():
        setattr(db_error, field, value)
    db.commit()
    db.refresh(db_error)
    return db_error


def defeat_vocabulary_error(db: Session, player_id: int, error_id: int) -> VocabularyError | None:
    db_error = db.query(VocabularyError).filter(VocabularyError.id == error_id, VocabularyError.player_id == player_id).first()
    if not db_error:
        return None
    db_error.defeated_count += 1
    # Check if defeated: defeated_count >= 3 AND created_at is older than 7 days
    if db_error.defeated_count >= 3 and db_error.created_at <= datetime.utcnow() - timedelta(days=7):
        db_error.status = "defeated"
    db.commit()
    db.refresh(db_error)
    return db_error


def get_vocabulary_boss_status(db: Session, player_id: int) -> dict:
    player = db.query(Player).filter(Player.id == player_id).first()
    campaign = db.query(Campaign).filter(Campaign.player_id == player_id, Campaign.status == "active").first()
    if not campaign:
        campaign = db.query(Campaign).filter(Campaign.player_id == player_id).order_by(Campaign.id.desc()).first()

    # Get skill state
    vocab_skill = db.query(Skill).filter(Skill.name == "Vocabulary").first()
    skill_state = None
    if vocab_skill and campaign:
        skill_state = db.query(CampaignSkillState).filter(
            CampaignSkillState.campaign_id == campaign.id,
            CampaignSkillState.skill_id == vocab_skill.id
        ).first()

    # Stats queries
    total_words = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id).count()
    
    total_reviews = db.query(func.sum(SpacedRepetitionState.repetition_count))\
        .filter(SpacedRepetitionState.player_id == player_id).scalar() or 0
        
    total_examples = db.query(VocabularyExample).filter(VocabularyExample.player_id == player_id).count()
    
    total_collocations = (
        db.query(PlayerCollocationProgress)
        .filter(
            PlayerCollocationProgress.player_id == player_id,
            PlayerCollocationProgress.status.in_(["learning", "practiced", "mastered"])
        )
        .count()
    )
    
    total_nodes = db.query(VocabularyNode).filter(VocabularyNode.player_id == player_id)\
        .filter(VocabularyNode.status != "locked").count()
        
    total_stabilized = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id)\
        .filter(VocabularyItem.mastery_rank.in_(["D", "C", "B", "A", "S"])).count()
        
    total_mastered = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id)\
        .filter(VocabularyItem.mastery_rank.in_(["C", "B", "A", "S"])).count()
        
    total_errors_corrected = db.query(func.sum(VocabularyError.defeated_count))\
        .filter(VocabularyError.player_id == player_id).scalar() or 0
        
    total_errors_defeated = db.query(VocabularyError).filter(VocabularyError.player_id == player_id)\
        .filter(VocabularyError.status == "defeated").count()
        
    total_fixed_phrases = (
        db.query(PlayerCollocationProgress)
        .join(CollocationItem, PlayerCollocationProgress.collocation_item_id == CollocationItem.id)
        .filter(
            PlayerCollocationProgress.player_id == player_id,
            PlayerCollocationProgress.status.in_(["learning", "practiced", "mastered"]),
            CollocationItem.collocation_type.like("%phrase%")
        )
        .count()
    )
        
    total_topic_words_used = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id)\
        .filter(VocabularyItem.ielts_topic.isnot(None))\
        .filter(VocabularyItem.mastery_score > 0).count()
        
    total_family_relations = db.query(VocabularyRelation).filter(VocabularyRelation.player_id == player_id)\
        .filter(VocabularyRelation.relation_type == "word_family").count()

    # Check badge unlocks to see if boss cleared
    unlocked_badge_names = []
    if campaign:
        unlocked_badge_names = [
            bu.badge.name for bu in db.query(BadgeUnlock).filter(BadgeUnlock.campaign_id == campaign.id).all()
        ]

    # Boss 1: Foundation Scan
    boss1_cleared = False
    if skill_state and skill_state.confirmed_rank in ["E", "D", "C", "B", "A", "S"]:
        boss1_cleared = True
    
    boss1_reqs = {
        "words": {"current": total_words, "target": 100, "met": total_words >= 100},
        "reviews": {"current": total_reviews, "target": 60, "met": total_reviews >= 60},
        "examples": {"current": total_examples, "target": 30, "met": total_examples >= 30},
        "collocations": {"current": total_collocations, "target": 20, "met": total_collocations >= 20},
        "nodes": {"current": total_nodes, "target": 5, "met": total_nodes >= 5},
    }
    boss1_ready = all(r["met"] for r in boss1_reqs.values())

    # Boss 2: Monthly Checkpoint
    boss2_cleared = "Memory Streak Badge I" in unlocked_badge_names
    boss2_reqs = {
        "words": {"current": total_words, "target": 150, "met": total_words >= 150},
        "reviews": {"current": total_reviews, "target": 100, "met": total_reviews >= 100},
        "stabilized": {"current": total_stabilized, "target": 30, "met": total_stabilized >= 30},
        "errors_corrected": {"current": total_errors_corrected, "target": 10, "met": total_errors_corrected >= 10},
    }
    boss2_ready = all(r["met"] for r in boss2_reqs.values()) and boss1_cleared

    # Boss 3: Collocation Hunter
    boss3_cleared = "Writing Lexical Buff" in unlocked_badge_names
    boss3_reqs = {
        "collocations": {"current": total_collocations, "target": 150, "met": total_collocations >= 150},
        "fixed_phrases": {"current": total_fixed_phrases, "target": 30, "met": total_fixed_phrases >= 30},
        "topic_words_used": {"current": total_topic_words_used, "target": 20, "met": total_topic_words_used >= 20},
    }
    boss3_ready = all(r["met"] for r in boss3_reqs.values()) and boss2_cleared

    # Boss 4: Lexical Awakening
    boss4_cleared = "Lexical Awakener" in unlocked_badge_names
    boss4_reqs = {
        "words": {"current": total_words, "target": 500, "met": total_words >= 500},
        "mastered": {"current": total_mastered, "target": 250, "met": total_mastered >= 250},
        "collocations": {"current": total_collocations, "target": 100, "met": total_collocations >= 100},
        "family_relations": {"current": total_family_relations, "target": 50, "met": total_family_relations >= 50},
        "defeated_errors": {"current": total_errors_defeated, "target": 30, "met": total_errors_defeated >= 30},
    }
    boss4_ready = all(r["met"] for r in boss4_reqs.values()) and boss3_cleared

    return {
        "bosses": [
            {
                "id": 1,
                "title": "Foundation Scan",
                "stage": "Month 1-3 Checkpoint",
                "goal": "Verify core vocabulary retention and collocations.",
                "reward_xp": 60,
                "status": "cleared" if boss1_cleared else ("ready" if boss1_ready else "locked"),
                "requirements": boss1_reqs,
            },
            {
                "id": 2,
                "title": "Monthly Checkpoint",
                "stage": "Month 4-6 Checkpoint",
                "goal": "Prove vocabulary stability and error resolution.",
                "reward_xp": 80,
                "status": "cleared" if boss2_cleared else ("ready" if boss2_ready else "locked"),
                "requirements": boss2_reqs,
            },
            {
                "id": 3,
                "title": "Collocation Hunter",
                "stage": "Month 7-9 Checkpoint",
                "goal": "Master complex collocation structures and phrases.",
                "reward_xp": 100,
                "status": "cleared" if boss3_cleared else ("ready" if boss3_ready else "locked"),
                "requirements": boss3_reqs,
            },
            {
                "id": 4,
                "title": "Lexical Awakening",
                "stage": "Final Campaign Checkpoint",
                "goal": "Achieve complete lexical mastery for Band 7.5.",
                "reward_xp": 200,
                "status": "cleared" if boss4_cleared else ("ready" if boss4_ready else "locked"),
                "requirements": boss4_reqs,
            }
        ]
    }


def challenge_vocabulary_boss(db: Session, player_id: int, boss_id: int) -> dict:
    items = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id).all()
    if not items:
        items = [
            VocabularyItem(id=1, word="significant", part_of_speech="adjective", meaning_en="important or large", meaning_vi="quan trọng", pronunciation_ipa="/sɪɡˈnɪfɪkənt/"),
            VocabularyItem(id=2, word="analyze", part_of_speech="verb", meaning_en="examine in detail", meaning_vi="phân tích", pronunciation_ipa="/ˈæn.əl.aɪz/"),
            VocabularyItem(id=3, word="evidence", part_of_speech="noun", meaning_en="facts or information indicating truth", meaning_vi="bằng chứng", pronunciation_ipa="/ˈev.ɪ.dəns/"),
            VocabularyItem(id=4, word="benefit", part_of_speech="noun", meaning_en="an advantage or profit gained", meaning_vi="lợi ích", pronunciation_ipa="/ˈben.ɪ.fɪt/"),
            VocabularyItem(id=5, word="challenge", part_of_speech="noun", meaning_en="a call to take part in a contest", meaning_vi="thử thách", pronunciation_ipa="/ˈtʃæl.ɪndʒ/"),
        ]

    import random
    questions = []

    def get_meaning_options(correct_meaning, all_items):
        options = {correct_meaning}
        pool = [it.meaning_en or it.meaning_vi for it in all_items if it.meaning_en or it.meaning_vi]
        pool = [p for p in pool if p != correct_meaning]
        while len(options) < 4 and pool:
            options.add(random.choice(pool))
        fallbacks = ["to learn something new", "an unexpected outcome", "a clear explanation", "to make something better"]
        while len(options) < 4:
            options.add(fallbacks[len(options)])
        opts = list(options)
        random.shuffle(opts)
        return opts

    def get_collocation_options(correct_val):
        options = {correct_val}
        parts = correct_val.split()
        if len(parts) >= 2:
            verbs = ["make", "take", "do", "get", "give", "express", "gain"]
            nouns = ["decision", "mistake", "homework", "opinion", "advantage", "effort", "break"]
            for v in verbs:
                for n in nouns:
                    candidate = f"{v} {n}"
                    if candidate != correct_val:
                        options.add(candidate)
                        if len(options) == 4:
                            break
        fallbacks = ["make a decision", "take a break", "gain an advantage", "do homework"]
        for f in fallbacks:
            if len(options) < 4 and f != correct_val:
                options.add(f)
        opts = list(options)
        random.shuffle(opts)
        return opts

    if boss_id == 1:
        selected_items = random.choices(items, k=min(len(items), 20))
        for i, item in enumerate(selected_items):
            correct = item.meaning_en or item.meaning_vi or "No meaning"
            questions.append({
                "id": f"q-meaning-{i}",
                "question_type": "meaning_recall",
                "prompt": f"What is the meaning of the word '{item.word}'?",
                "choices": get_meaning_options(correct, items),
                "correct_answer": correct,
                "word_id": item.id
            })

        player = db.query(Player).filter(Player.id == player_id).first()
        campaign_id = player.active_campaign_id if player else None
        collocations = []
        if campaign_id:
            collocations = (
                db.query(CollocationItem)
                .join(CollocationTopic, CollocationItem.topic_id == CollocationTopic.id)
                .join(CollocationSection, CollocationTopic.section_id == CollocationSection.id)
                .join(CollocationCollection, CollocationSection.collection_id == CollocationCollection.id)
                .join(CampaignCollocationLink, CollocationCollection.id == CampaignCollocationLink.collection_id)
                .filter(CampaignCollocationLink.campaign_id == campaign_id)
                .all()
            )
        if not collocations:
            collocations = [
                CollocationItem(id=1, collocation="express an opinion", collocation_type="verb + noun"),
                CollocationItem(id=2, collocation="gain an advantage", collocation_type="verb + noun"),
                CollocationItem(id=3, collocation="make a mistake", collocation_type="verb + noun"),
            ]
        selected_collocs = random.choices(collocations, k=min(len(collocations), 10))
        for i, col in enumerate(selected_collocs):
            parts = col.collocation.split()
            prompt = col.collocation
            if len(parts) >= 2:
                prompt = f"Complete the collocation: '_____ {parts[-1]}'"
            
            # Find core word to match vocabulary item id
            core_word = _extract_core_word(col.collocation, db)
            vocab_item = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id, VocabularyItem.word == core_word.lower()).first()
            word_id = vocab_item.id if vocab_item else None
            
            questions.append({
                "id": f"q-colloc-{i}",
                "question_type": "collocation",
                "prompt": prompt,
                "choices": get_collocation_options(col.collocation),
                "correct_answer": col.collocation,
                "word_id": word_id
            })

        relations = db.query(VocabularyRelation).filter(VocabularyRelation.player_id == player_id)\
            .filter(VocabularyRelation.relation_type.in_(["synonym", "antonym"])).all()
        if not relations:
            relations = [
                VocabularyRelation(id=1, source_word_id=1, target_text="important", relation_type="synonym"),
                VocabularyRelation(id=2, source_word_id=1, target_text="insignificant", relation_type="antonym"),
            ]
        selected_rels = random.choices(relations, k=min(len(relations), 5))
        for i, rel in enumerate(selected_rels):
            src_item = db.query(VocabularyItem).filter(VocabularyItem.id == rel.source_word_id).first()
            word_str = src_item.word if src_item else "significant"
            prompt = f"Identify the {rel.relation_type} of '{word_str}':"
            correct = rel.target_text or "important"
            
            options = {correct}
            pool = ["difficult", "simple", "unusual", "frequent", "extreme"]
            while len(options) < 4 and pool:
                options.add(pool.pop(random.randint(0, len(pool)-1)))
            opts = list(options)
            random.shuffle(opts)
            
            questions.append({
                "id": f"q-relation-{i}",
                "question_type": "synonym_antonym",
                "prompt": prompt,
                "choices": opts,
                "correct_answer": correct,
                "word_id": rel.source_word_id
            })

        examples = db.query(VocabularyExample).filter(VocabularyExample.player_id == player_id).all()
        if not examples:
            examples = [
                VocabularyExample(id=1, vocabulary_item_id=1, example_sentence="The new policy had a significant impact on education."),
                VocabularyExample(id=2, vocabulary_item_id=2, example_sentence="We need to analyze the data before making a choice."),
            ]
        selected_exs = random.choices(examples, k=min(len(examples), 5))
        for i, ex in enumerate(selected_exs):
            ex_item = db.query(VocabularyItem).filter(VocabularyItem.id == ex.vocabulary_item_id).first()
            word_str = ex_item.word if ex_item else "significant"
            prompt = ex.example_sentence.replace(word_str, "_____")
            if prompt == ex.example_sentence:
                prompt = ex.example_sentence.replace(word_str.lower(), "_____")
            
            options = {word_str}
            pool = [it.word for it in items if it.word != word_str]
            while len(options) < 4 and pool:
                options.add(random.choice(pool))
            opts = list(options)
            random.shuffle(opts)
            
            questions.append({
                "id": f"q-example-{i}",
                "question_type": "sentence_completion",
                "prompt": f"Complete the sentence: '{prompt}'",
                "choices": opts,
                "correct_answer": word_str,
                "word_id": ex.vocabulary_item_id
            })

    elif boss_id == 2:
        selected_items = random.choices(items, k=min(len(items), 10))
        for i, item in enumerate(selected_items):
            correct = item.meaning_en or item.meaning_vi or "No meaning"
            questions.append({
                "id": f"q-meaning-{i}",
                "question_type": "meaning_recall",
                "prompt": f"Define the word '{item.word}':",
                "choices": get_meaning_options(correct, items),
                "correct_answer": correct,
                "word_id": item.id
            })
        examples = db.query(VocabularyExample).filter(VocabularyExample.player_id == player_id).all()
        if not examples:
            examples = [
                VocabularyExample(id=1, vocabulary_item_id=1, example_sentence="This is a significant discovery."),
            ]
        selected_exs = random.choices(examples, k=min(len(examples), 10))
        for i, ex in enumerate(selected_exs):
            ex_item = db.query(VocabularyItem).filter(VocabularyItem.id == ex.vocabulary_item_id).first()
            word_str = ex_item.word if ex_item else "significant"
            prompt = ex.example_sentence.replace(word_str, "_____")
            
            options = {word_str}
            pool = [it.word for it in items if it.word != word_str]
            while len(options) < 4 and pool:
                options.add(random.choice(pool))
            opts = list(options)
            random.shuffle(opts)
            
            questions.append({
                "id": f"q-example-{i}",
                "question_type": "sentence_completion",
                "prompt": f"Complete: '{prompt}'",
                "choices": opts,
                "correct_answer": word_str,
                "word_id": ex.vocabulary_item_id
            })

    elif boss_id == 3:
        player = db.query(Player).filter(Player.id == player_id).first()
        campaign_id = player.active_campaign_id if player else None
        collocations = []
        if campaign_id:
            collocations = (
                db.query(CollocationItem)
                .join(CollocationTopic, CollocationItem.topic_id == CollocationTopic.id)
                .join(CollocationSection, CollocationTopic.section_id == CollocationSection.id)
                .join(CollocationCollection, CollocationSection.collection_id == CollocationCollection.id)
                .join(CampaignCollocationLink, CollocationCollection.id == CampaignCollocationLink.collection_id)
                .filter(CampaignCollocationLink.campaign_id == campaign_id)
                .all()
            )
        if not collocations:
            collocations = [
                CollocationItem(id=1, collocation="express an opinion", collocation_type="verb + noun"),
            ]
        selected_collocs = random.choices(collocations, k=min(len(collocations), 20))
        for i, col in enumerate(selected_collocs):
            parts = col.collocation.split()
            prompt = f"Match the correct verb partner for '_____ {parts[-1]}':" if len(parts) >= 2 else f"Identify the collocation partnership for '{col.collocation}'"
            correct = parts[0] if len(parts) >= 2 else col.collocation
            
            options = {correct}
            pool = ["make", "take", "do", "get", "give", "express", "gain", "raise", "pose", "bring"]
            while len(options) < 4 and pool:
                options.add(pool.pop(random.randint(0, len(pool)-1)))
            opts = list(options)
            random.shuffle(opts)
            
            # Find core word to match vocabulary item id
            core_word = _extract_core_word(col.collocation, db)
            vocab_item = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id, VocabularyItem.word == core_word.lower()).first()
            word_id = vocab_item.id if vocab_item else None
            
            questions.append({
                "id": f"q-colloc-{i}",
                "question_type": "collocation",
                "prompt": prompt,
                "choices": opts,
                "correct_answer": correct,
                "word_id": word_id
            })

    else:
        selected_items = random.choices(items, k=min(len(items), 15))
        for i, item in enumerate(selected_items):
            correct = item.meaning_en or item.meaning_vi or "No meaning"
            questions.append({
                "id": f"q-meaning-{i}",
                "question_type": "mixed",
                "prompt": f"Define the word '{item.word}':",
                "choices": get_meaning_options(correct, items),
                "correct_answer": correct,
                "word_id": item.id
            })
        
        player = db.query(Player).filter(Player.id == player_id).first()
        campaign_id = player.active_campaign_id if player else None
        collocations = []
        if campaign_id:
            collocations = (
                db.query(CollocationItem)
                .join(CollocationTopic, CollocationItem.topic_id == CollocationTopic.id)
                .join(CollocationSection, CollocationTopic.section_id == CollocationSection.id)
                .join(CollocationCollection, CollocationSection.collection_id == CollocationCollection.id)
                .join(CampaignCollocationLink, CollocationCollection.id == CampaignCollocationLink.collection_id)
                .filter(CampaignCollocationLink.campaign_id == campaign_id)
                .all()
            )
        if not collocations:
            collocations = [
                CollocationItem(id=1, collocation="express an opinion"),
            ]
        selected_collocs = random.choices(collocations, k=min(len(collocations), 15))
        for i, col in enumerate(selected_collocs):
            parts = col.collocation.split()
            prompt = f"Which word fits best in: '_____ {parts[-1]}'?" if len(parts) >= 2 else f"Choose collocation: '{col.collocation}'"
            correct = parts[0] if len(parts) >= 2 else col.collocation
            
            options = {correct}
            pool = ["make", "take", "do", "get", "give", "express", "gain"]
            while len(options) < 4 and pool:
                options.add(random.choice(pool))
            opts = list(options)
            random.shuffle(opts)
            
            # Find core word to match vocabulary item id
            core_word = _extract_core_word(col.collocation, db)
            vocab_item = db.query(VocabularyItem).filter(VocabularyItem.player_id == player_id, VocabularyItem.word == core_word.lower()).first()
            word_id = vocab_item.id if vocab_item else None
            
            questions.append({
                "id": f"q-colloc-{i}",
                "question_type": "collocation",
                "prompt": prompt,
                "choices": opts,
                "correct_answer": correct,
                "word_id": word_id
            })

    return {"boss_id": boss_id, "questions": questions}


def submit_vocabulary_boss_result(db: Session, player_id: int, boss_id: int, score_pct: float) -> dict:
    player = db.query(Player).filter(Player.id == player_id).first()
    campaign = db.query(Campaign).filter(Campaign.player_id == player_id, Campaign.status == "active").first()
    if not campaign:
        campaign = db.query(Campaign).filter(Campaign.player_id == player_id).order_by(Campaign.id.desc()).first()

    passed = score_pct >= 75.0
    reward_xp = 0
    message = "You did not pass the boss challenge. Try again!"

    if passed:
        vocab_skill = db.query(Skill).filter(Skill.name == "Vocabulary").first()
        skill_state = None
        if vocab_skill and campaign:
            skill_state = db.query(CampaignSkillState).filter(
                CampaignSkillState.campaign_id == campaign.id,
                CampaignSkillState.skill_id == vocab_skill.id
            ).first()

        if boss_id == 1:
            reward_xp = 60
            if skill_state:
                skill_state.confirmed_rank = "E"
            message = "Congratulations! Boss defeated. You unlocked Vocabulary Rank E!"
        elif boss_id == 2:
            reward_xp = 80
            badge = db.query(Badge).filter(Badge.name == "Memory Streak Badge I").first()
            if badge and campaign:
                existing = db.query(BadgeUnlock).filter(BadgeUnlock.campaign_id == campaign.id, BadgeUnlock.badge_id == badge.id).first()
                if not existing:
                    db.add(BadgeUnlock(player_id=player_id, campaign_id=campaign.id, badge_id=badge.id))
            message = "Congratulations! Boss defeated. You unlocked the 'Memory Streak Badge I'!"
        elif boss_id == 3:
            reward_xp = 100
            badge = db.query(Badge).filter(Badge.name == "Writing Lexical Buff").first()
            if badge and campaign:
                existing = db.query(BadgeUnlock).filter(BadgeUnlock.campaign_id == campaign.id, BadgeUnlock.badge_id == badge.id).first()
                if not existing:
                    db.add(BadgeUnlock(player_id=player_id, campaign_id=campaign.id, badge_id=badge.id))
            message = "Congratulations! Boss defeated. You unlocked the 'Writing Lexical Buff'!"
        elif boss_id == 4:
            reward_xp = 200
            badge = db.query(Badge).filter(Badge.name == "Lexical Awakener").first()
            if badge and campaign:
                existing = db.query(BadgeUnlock).filter(BadgeUnlock.campaign_id == campaign.id, BadgeUnlock.badge_id == badge.id).first()
                if not existing:
                    db.add(BadgeUnlock(player_id=player_id, campaign_id=campaign.id, badge_id=badge.id))
            message = "Congratulations! Boss defeated. You unlocked the ultimate 'Lexical Awakener' badge!"

        if campaign:
            refresh_progress_state(db)

    return {"passed": passed, "score_pct": score_pct, "reward_xp": reward_xp, "message": message}


def create_collocation_collection(db: Session, collection_in: CollocationCollectionIn) -> CollocationCollection:
    db_collection = CollocationCollection(
        code=collection_in.code,
        title=collection_in.title,
        description=collection_in.description,
        source_book=collection_in.source_book,
        level=collection_in.level,
        is_active=collection_in.is_active,
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection


def get_collocation_collection(db: Session, collection_id: int) -> CollocationCollection | None:
    return db.query(CollocationCollection).filter(CollocationCollection.id == collection_id).first()


def get_collocation_collection_by_code(db: Session, code: str) -> CollocationCollection | None:
    return db.query(CollocationCollection).filter(CollocationCollection.code == code).first()


def get_collocation_collections(db: Session, skip: int = 0, limit: int = 100) -> list[CollocationCollection]:
    return db.query(CollocationCollection).offset(skip).limit(limit).all()


def delete_collocation_collection(db: Session, collection_id: int) -> bool:
    db_collection = db.query(CollocationCollection).filter(CollocationCollection.id == collection_id).first()
    if not db_collection:
        return False
    db.delete(db_collection)
    db.commit()
    return True


def create_collocation_section(db: Session, section_in: CollocationSectionIn) -> CollocationSection:
    db_section = CollocationSection(
        collection_id=section_in.collection_id,
        title=section_in.title,
        section_order=section_in.section_order,
    )
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section


def get_collocation_section(db: Session, section_id: int) -> CollocationSection | None:
    return db.query(CollocationSection).filter(CollocationSection.id == section_id).first()


def delete_collocation_section(db: Session, section_id: int) -> bool:
    db_section = db.query(CollocationSection).filter(CollocationSection.id == section_id).first()
    if not db_section:
        return False
    db.delete(db_section)
    db.commit()
    return True


def create_collocation_topic(db: Session, topic_in: CollocationTopicIn) -> CollocationTopic:
    db_topic = CollocationTopic(
        section_id=topic_in.section_id,
        title=topic_in.title,
        topic_number=topic_in.topic_number,
        topic_order=topic_in.topic_order,
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


def get_collocation_topic(db: Session, topic_id: int) -> CollocationTopic | None:
    return db.query(CollocationTopic).filter(CollocationTopic.id == topic_id).first()


def delete_collocation_topic(db: Session, topic_id: int) -> bool:
    db_topic = db.query(CollocationTopic).filter(CollocationTopic.id == topic_id).first()
    if not db_topic:
        return False
    db.delete(db_topic)
    db.commit()
    return True


def create_collocation_item(db: Session, item_in: CollocationItemIn) -> CollocationItem:
    db_item = CollocationItem(
        topic_id=item_in.topic_id,
        collocation=item_in.collocation,
        pronunciation_us=item_in.pronunciation_us,
        meaning_vi=item_in.meaning_vi,
        example_en=item_in.example_en,
        example_vi=item_in.example_vi,
        collocation_type=item_in.collocation_type,
        item_order=item_in.item_order,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_collocation_item(db: Session, item_id: int) -> CollocationItem | None:
    return db.query(CollocationItem).filter(CollocationItem.id == item_id).first()


def delete_collocation_item(db: Session, item_id: int) -> bool:
    db_item = db.query(CollocationItem).filter(CollocationItem.id == item_id).first()
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True


def link_collection_to_campaign(db: Session, campaign_id: int, collection_id: int, display_order: int = 0) -> CampaignCollocationLink:
    existing = db.query(CampaignCollocationLink).filter_by(campaign_id=campaign_id, collection_id=collection_id).first()
    if existing:
        existing.display_order = display_order
        db.commit()
        db.refresh(existing)
        return existing
    link = CampaignCollocationLink(
        campaign_id=campaign_id,
        collection_id=collection_id,
        display_order=display_order,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def unlink_collection_from_campaign(db: Session, campaign_id: int, collection_id: int) -> bool:
    link = db.query(CampaignCollocationLink).filter_by(campaign_id=campaign_id, collection_id=collection_id).first()
    if not link:
        return False
    db.delete(link)
    db.commit()
    return True


def get_campaign_collections(db: Session, campaign_id: int) -> list[CollocationCollection]:
    links = db.query(CampaignCollocationLink).filter_by(campaign_id=campaign_id).order_by(CampaignCollocationLink.display_order).all()
    return [link.collection for link in links if link.collection.is_active]


def get_player_collocation_progress(db: Session, player_id: int, campaign_id: int, collocation_item_id: int) -> PlayerCollocationProgress | None:
    return db.query(PlayerCollocationProgress).filter_by(
        player_id=player_id,
        campaign_id=campaign_id,
        collocation_item_id=collocation_item_id,
    ).first()


def update_player_collocation_progress(
    db: Session,
    player_id: int,
    campaign_id: int,
    collocation_item_id: int,
    status: str | None = None,
    correct: bool | None = None,
) -> PlayerCollocationProgress:
    progress = get_player_collocation_progress(db, player_id, campaign_id, collocation_item_id)
    if not progress:
        progress = PlayerCollocationProgress(
            player_id=player_id,
            campaign_id=campaign_id,
            collocation_item_id=collocation_item_id,
            status="new",
            practice_count=0,
            correct_count=0,
        )
        db.add(progress)
        db.flush()

    if status is not None:
        progress.status = status
    if correct is not None:
        progress.practice_count += 1
        if correct:
            progress.correct_count += 1
        progress.last_practiced_at = datetime.utcnow()
        if progress.correct_count >= 3 and progress.status in ("new", "learning", "practiced"):
            progress.status = "mastered"
        elif progress.practice_count >= 1 and progress.status == "new":
            progress.status = "learning"

    progress.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(progress)
    return progress


def get_collocation_outline_with_progress(db: Session, player_id: int, campaign_id: int, collection_id: int) -> CollocationCollection | None:
    collection = db.query(CollocationCollection).filter(CollocationCollection.id == collection_id).first()
    if not collection:
        return None
    
    progress_map = {
        p.collocation_item_id: p
        for p in db.query(PlayerCollocationProgress).filter(
            PlayerCollocationProgress.player_id == player_id,
            PlayerCollocationProgress.campaign_id == campaign_id
        ).all()
    }
    
    for section in collection.sections:
        for topic in section.topics:
            for item in topic.items:
                item.progress = progress_map.get(item.id)
                
    return collection





