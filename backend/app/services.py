from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import (
    Badge,
    BossBattle,
    Campaign,
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
)

RANK_ORDER = ["F", "E", "D", "C", "B", "A", "S"]
CORE_SKILLS = {"Listening", "Reading", "Writing", "Speaking"}
RANK_THRESHOLDS = [
    (3500, "S", 7),
    (2500, "A", 6),
    (1700, "B", 5),
    (1000, "C", 4),
    (500, "D", 3),
    (200, "E", 2),
    (0, "F", 1),
]


def get_rank_level(xp: int) -> tuple[str, int]:
    for threshold, rank, level in RANK_THRESHOLDS:
        if xp >= threshold:
            return rank, level
    return "F", 1


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
    dirty = False
    quests = db.query(Quest).filter(Quest.campaign_id == campaign.id).all()
    for quest in quests:
        if quest.completed:
            if quest.status != "completed":
                quest.status = "completed"
                dirty = True
            if not quest.earned_xp:
                quest.earned_xp = quest.xp
                dirty = True
            continue
        if quest.quest_date < today:
            overdue_days = (today - quest.quest_date).days
            new_status = "overdue" if overdue_days <= 3 else "expired"
            if quest.status != new_status:
                quest.status = new_status
                dirty = True
            if new_status == "expired" and quest.expired_at is None:
                quest.expired_at = datetime.utcnow()
                dirty = True
        else:
            if quest.status != "pending":
                quest.status = "pending"
                dirty = True
            if quest.expired_at is not None:
                quest.expired_at = None
                dirty = True
    if dirty:
        db.commit()


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
    checkins = db.query(CheckIn).all()
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
        overdue_or_expired = len([quest for quest in week_quests if quest.completed_mode == "overdue" or quest.status in {"overdue", "expired"}])

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
            elif "check-in hoac mini review day" in description:
                progress = len(active_days)
            elif "check-in" in description and "note" in description:
                progress = noted_checkins
            elif "check-in" in description:
                progress = len(week_checkins)
            elif "error log/writing/speaking tracker" in description:
                progress = tracker_notes
            elif "diem yeu recurring" in description:
                progress = len(week_error_logs)
            elif "mini review lien quan output skill" in description:
                progress = len(
                    [
                        quest
                        for quest in completed_mini
                        if (quest.skill.name if quest.skill else "") in {"Writing", "Speaking", "Collocation"}
                    ]
                ) or len(completed_mini)
            elif "cau dai hoac paraphrase kho" in description:
                progress = tracker_notes or len(
                    [
                        quest
                        for quest in week_quests
                        if (quest.skill.name if quest.skill else "") in {"Reading", "Vocabulary", "Collocation"}
                    ]
                )
            elif "daily quest" in description:
                progress = daily_quest_count
            elif "overdue quests under 2" in description:
                progress = 1 if overdue_or_expired < 2 else 0

            _set_weekly_item_state(item, progress)

        if mission.items and all(item.status == "completed" for item in mission.items):
            mission.status = "completed"
            mission.completed_at = mission.completed_at or datetime.utcnow()
        else:
            mission.status = "active"
            mission.completed_at = None


def recompute_badges(db: Session) -> None:
    skill_xp = {skill.name: skill.xp for skill in db.query(Skill).all()}
    completed_count = db.query(Quest).filter(Quest.completed == True).count()
    badge_rules = {
        "Vocabulary Hunter": skill_xp.get("Vocabulary", 0) >= 300,
        "Grammar Fixer": skill_xp.get("Grammar", 0) >= 300,
        "Listening Warrior": skill_xp.get("Listening", 0) >= 500,
        "Reading Decoder": skill_xp.get("Reading", 0) >= 500,
        "Writing Starter": skill_xp.get("Writing", 0) >= 300,
        "Speaking Brave Mode": skill_xp.get("Speaking", 0) >= 300,
        "Error Killer": completed_count >= 100,
        "Band 6 Challenger": completed_count >= 150,
        "Band 7 Candidate": completed_count >= 250,
    }
    for badge in db.query(Badge).all():
        should_unlock = badge_rules.get(badge.name, False)
        if should_unlock and not badge.unlocked:
            badge.unlocked = True
            badge.unlocked_at = datetime.utcnow()


def recompute_player_progress(db: Session, player: Player, campaign: Campaign) -> None:
    completed_quests = (
        db.query(Quest)
        .filter(Quest.campaign_id == campaign.id, Quest.completed == True, Quest.reward_claimed == True)
        .all()
    )
    quest_xp = sum(quest.earned_xp or 0 for quest in completed_quests)
    mission_xp = (
        db.query(func.coalesce(func.sum(WeeklyMission.reward_xp), 0))
        .filter(
            WeeklyMission.campaign_id == campaign.id,
            WeeklyMission.status == "completed",
            WeeklyMission.reward_claimed == True,
        )
        .scalar()
        or 0
    )
    boss_xp = (
        db.query(func.coalesce(func.sum(BossBattle.reward_xp), 0))
        .filter(BossBattle.campaign_id == campaign.id, BossBattle.result_status == "cleared")
        .scalar()
        or 0
    )
    player.player_xp = int(quest_xp + mission_xp + boss_xp)
    player.total_xp = player.player_xp
    player.player_rank, player.player_level = get_rank_level(player.player_xp)

    daily_quests = (
        db.query(Quest)
        .filter(Quest.campaign_id == campaign.id, Quest.quest_role.in_(["core", "support", "mini"]))
        .all()
    )
    by_day: dict[date, list[Quest]] = {}
    for quest in daily_quests:
        by_day.setdefault(quest.quest_date, []).append(quest)

    checkin_dates = {
        item.checkin_date
        for item in db.query(CheckIn.checkin_date).all()
    }

    current_streak = 0
    best_streak = 0
    shield_count = min(max(player.shield_count, 0), 2)
    regen_progress = 0
    perfect_days = 0
    cursor = campaign.start_date
    today = date.today()
    while cursor <= today:
        quests_for_day = by_day.get(cursor, [])
        is_daily_day = len(quests_for_day) >= 3
        fully_completed = is_daily_day and all(quest.completed for quest in quests_for_day[:3])
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


def recompute_skill_progress(db: Session, skill: Skill) -> None:
    earned = (
        db.query(func.coalesce(func.sum(Quest.earned_xp), 0))
        .filter(Quest.skill_id == skill.id, Quest.completed == True, Quest.reward_claimed == True)
        .scalar()
        or 0
    )
    skill.xp = int(earned)
    skill.rank, skill.level = get_rank_level(skill.xp)
    skill.last_practiced = (
        db.query(func.max(Quest.quest_date))
        .filter(Quest.skill_id == skill.id, Quest.completed == True)
        .scalar()
    )


def refresh_progress_state(db: Session) -> None:
    player = get_active_player(db)
    campaign = get_active_campaign(db, player)
    sync_quest_statuses(db, campaign)
    recompute_weekly_missions(db, campaign)
    for skill in db.query(Skill).all():
        recompute_skill_progress(db, skill)
    recompute_badges(db)
    recompute_player_progress(db, player, campaign)
    db.commit()


def complete_quest_instance(
    db: Session,
    quest: Quest,
    tracker_type: str = "",
    tracker_entry_id: int | None = None,
    raw_score: str = "",
    completion_note: str = "",
) -> Quest:
    today = date.today()
    if quest.quest_date > today:
        raise ValueError("Future quest cannot be completed yet")
    if quest.status == "expired":
        raise ValueError("Expired quest cannot be completed")
    if not quest.completed:
        quest.completed = True
        quest.completed_at = datetime.utcnow()
        quest.reward_claimed = False
        quest.reward_claimed_at = None
        quest.tracker_type = tracker_type or quest.tracker_type
        quest.tracker_entry_id = tracker_entry_id if tracker_entry_id is not None else quest.tracker_entry_id
        quest.raw_score = raw_score or quest.raw_score
        quest.completion_note = completion_note or quest.completion_note
        if quest.quest_date < today:
            quest.status = "completed"
            quest.completed_mode = "overdue"
            quest.earned_xp = max(1, int((quest.base_xp or quest.xp) * 0.5))
        else:
            quest.status = "completed"
            quest.completed_mode = "on_time"
            quest.earned_xp = quest.base_xp or quest.xp
    refresh_progress_state(db)
    db.refresh(quest)
    return quest


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
        quest.tracker_entry_id = None
        quest.tracker_type = ""
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
    for skill in db.query(Skill).filter(Skill.name.in_(["Listening", "Reading", "Writing", "Speaking"])).all():
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
            source_test_record_id=test_record.id,
            current_rank=skill.confirmed_rank,
            suggested_rank=suggested_rank,
            direction=compare_ranks(skill.confirmed_rank, suggested_rank),
            status="pending",
        )
        db.add(suggestion)
        created.append(suggestion)
    skill_map = {skill.name: skill for skill in db.query(Skill).all()}
    if "Vocabulary" in skill_map:
        suggestion = SkillRankSuggestion(
            skill_id=skill_map["Vocabulary"].id,
            source_test_record_id=test_record.id,
            current_rank=skill_map["Vocabulary"].confirmed_rank,
            suggested_rank=normalize_cefr_rank(test_record.cefr_level or "B1"),
            direction=compare_ranks(skill_map["Vocabulary"].confirmed_rank, normalize_cefr_rank(test_record.cefr_level or "B1")),
            status="pending",
        )
        db.add(suggestion)
        created.append(suggestion)
    return created


def apply_rank_suggestion(db: Session, suggestion: SkillRankSuggestion) -> SkillRankSuggestion:
    skill = suggestion.skill
    old_rank = skill.confirmed_rank
    skill.confirmed_rank = suggestion.suggested_rank
    suggestion.status = "applied"
    suggestion.resolved_at = datetime.utcnow()
    db.add(
        SkillRankHistory(
            skill_id=skill.id,
            old_rank=old_rank,
            new_rank=skill.confirmed_rank,
            source_test_record_id=suggestion.source_test_record_id,
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


def append_weakness_note(skill: Skill, detail: str) -> None:
    parts = [part.strip() for part in skill.user_weakness_note.split("\n") if part.strip()]
    if detail.strip() not in parts:
        parts.append(detail.strip())
        skill.user_weakness_note = "\n".join(parts)


def ensure_weakness_suggestions(db: Session, campaign: Campaign) -> None:
    today = date.today()
    fourteen_days_ago = today - timedelta(days=14)
    thirty_days_ago = today - timedelta(days=30)

    for skill in db.query(Skill).options(joinedload(Skill.weakness_suggestions)).all():
        active_count = sum(1 for item in skill.weakness_suggestions if item.status == "pending")
        if active_count >= 2:
            continue

        overdue_count = (
            db.query(Quest)
            .filter(
                Quest.campaign_id == campaign.id,
                Quest.skill_id == skill.id,
                Quest.quest_date >= fourteen_days_ago,
                Quest.status.in_(["overdue", "expired"]),
            )
            .count()
        )
        if overdue_count >= 3 and active_count < 2:
            db.add(
                WeaknessSuggestion(
                    skill_id=skill.id,
                    source_type="quest_pattern",
                    title=f"{skill.name}: quest completion is slipping",
                    detail="Several recent quests were overdue or expired. Reduce task complexity and restore a lighter repetition loop.",
                    severity="high",
                )
            )
            skill.last_system_suggestion_at = datetime.utcnow()
            active_count += 1

        if skill.last_practiced:
            inactivity_limit = 7 if skill.name in CORE_SKILLS else 5
            if (today - skill.last_practiced).days >= inactivity_limit and active_count < 2:
                db.add(
                    WeaknessSuggestion(
                        skill_id=skill.id,
                        source_type="last_practiced",
                        title=f"{skill.name}: refresh needed",
                        detail="This skill has not been practiced recently enough for the current roadmap cadence.",
                        severity="medium",
                    )
                )
                skill.last_system_suggestion_at = datetime.utcnow()
                active_count += 1

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
            db.add(
                WeaknessSuggestion(
                    skill_id=skill.id,
                    source_type="error_log",
                    title=f"{skill.name}: repeated error pattern",
                    detail=f'The error tag "{tag}" has repeated at least 3 times in the last 30 days.',
                    severity="high",
                )
            )
            skill.last_system_suggestion_at = datetime.utcnow()

    db.commit()


def apply_weakness_suggestion(db: Session, suggestion: WeaknessSuggestion) -> WeaknessSuggestion:
    append_weakness_note(suggestion.skill, suggestion.detail)
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
