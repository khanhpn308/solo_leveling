import os
from datetime import date, datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, wait_for_database
from .models import Badge, BossBattle, CheckIn, Player, Quest, Skill
from .schemas import BadgeOut, BossBattleOut, CheckInIn, CheckInOut, QuestOut, SkillOut, SummaryOut
from .seed import get_rank_level, seed_database

app = FastAPI(title="IELTS Quest Dashboard API", version="1.0.0")

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


@app.on_event("startup")
def on_startup() -> None:
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_database(db, parse_start_date())
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "online", "message": "IELTS Quest API is running"}


def current_week_window(player: Player) -> tuple[date, date]:
    today = date.today()
    if today < player.start_date:
        today = player.start_date
    days_from_start = (today - player.start_date).days
    week_start = player.start_date + timedelta(days=(days_from_start // 7) * 7)
    return week_start, week_start + timedelta(days=6)


def recompute_player_xp(db: Session) -> int:
    total = db.query(func.coalesce(func.sum(Quest.xp), 0)).filter(Quest.completed == True).scalar() or 0
    player = db.query(Player).first()
    if player:
        player.total_xp = int(total)
    return int(total)


def unlock_badges(db: Session) -> None:
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


def update_skill_after_change(db: Session, skill: Skill) -> None:
    skill.xp = int(db.query(func.coalesce(func.sum(Quest.xp), 0)).filter(
        Quest.skill_id == skill.id,
        Quest.completed == True,
    ).scalar() or 0)
    skill.rank, skill.level = get_rank_level(skill.xp)
    last = db.query(func.max(Quest.quest_date)).filter(Quest.skill_id == skill.id, Quest.completed == True).scalar()
    skill.last_practiced = last
    recompute_player_xp(db)
    unlock_badges(db)


@app.get("/api/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    player = db.query(Player).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player profile not found")

    week_start, week_end = current_week_window(player)
    today = date.today()
    if today < player.start_date:
        today = player.start_date

    today_xp = db.query(func.coalesce(func.sum(Quest.xp), 0)).filter(
        Quest.completed == True,
        Quest.quest_date == today,
    ).scalar() or 0
    week_xp = db.query(func.coalesce(func.sum(Quest.xp), 0)).filter(
        Quest.completed == True,
        Quest.quest_date >= week_start,
        Quest.quest_date <= week_end,
    ).scalar() or 0

    completed = db.query(Quest).filter(Quest.completed == True).count()
    total = db.query(Quest).count()
    skills = db.query(Skill).order_by(Skill.id).all()
    badges = db.query(Badge).order_by(Badge.id).all()
    boss_battles = db.query(BossBattle).order_by(BossBattle.battle_date).limit(8).all()

    player_data = {
        "name": player.name,
        "title": player.title,
        "target": player.target,
        "current_level": player.current_level,
        "start_date": player.start_date,
        "total_xp": player.total_xp,
        "week_start": week_start,
        "week_end": week_end,
    }

    return SummaryOut(
        player=player_data,
        total_completed_quests=completed,
        total_quests=total,
        today_xp=int(today_xp),
        week_xp=int(week_xp),
        current_streak=0,
        skills=skills,
        badges=badges,
        boss_battles=boss_battles,
    )


@app.get("/api/skills", response_model=list[SkillOut])
def get_skills(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.id).all()


@app.get("/api/quests", response_model=list[QuestOut])
def get_quests(
    db: Session = Depends(get_db),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    stage: str | None = Query(default=None),
    week_no: int | None = Query(default=None),
):
    player = db.query(Player).first()
    if not start and not end and not week_no and not stage:
        start, end = current_week_window(player)

    query = db.query(Quest).join(Skill)
    if start:
        query = query.filter(Quest.quest_date >= start)
    if end:
        query = query.filter(Quest.quest_date <= end)
    if stage:
        query = query.filter(Quest.stage == stage)
    if week_no:
        query = query.filter(Quest.week_no == week_no)

    quests = query.order_by(Quest.quest_date, Quest.id).all()
    return [
        QuestOut(
            id=q.id,
            quest_date=q.quest_date,
            week_no=q.week_no,
            stage=q.stage,
            title=q.title,
            skill_id=q.skill_id,
            skill_name=q.skill.name,
            source=q.source,
            details=q.details,
            xp=q.xp,
            completed=q.completed,
            completed_at=q.completed_at,
            session_type=q.session_type,
        )
        for q in quests
    ]


@app.post("/api/quests/{quest_id}/complete", response_model=QuestOut)
def complete_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    if not quest.completed:
        quest.completed = True
        quest.completed_at = datetime.utcnow()
        update_skill_after_change(db, quest.skill)
        db.commit()
        db.refresh(quest)
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
    )


@app.post("/api/quests/{quest_id}/uncomplete", response_model=QuestOut)
def uncomplete_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    if quest.completed:
        quest.completed = False
        quest.completed_at = None
        update_skill_after_change(db, quest.skill)
        db.commit()
        db.refresh(quest)
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
    )


@app.post("/api/checkins", response_model=CheckInOut)
def upsert_checkin(payload: CheckInIn, db: Session = Depends(get_db)):
    item = db.query(CheckIn).filter(CheckIn.checkin_date == payload.checkin_date).first()
    if item:
        item.mood = payload.mood
        item.energy = payload.energy
        item.note = payload.note
    else:
        item = CheckIn(
            checkin_date=payload.checkin_date,
            mood=payload.mood,
            energy=payload.energy,
            note=payload.note,
        )
        db.add(item)
    db.commit()
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
    return db.query(Badge).order_by(Badge.id).all()


@app.get("/api/boss-battles", response_model=list[BossBattleOut])
def get_boss_battles(db: Session = Depends(get_db)):
    return db.query(BossBattle).order_by(BossBattle.battle_date).all()


@app.post("/api/dev/reset")
def reset_database(db: Session = Depends(get_db)):
    for model in [Quest, BossBattle, Badge, Skill, Player, CheckIn]:
        db.query(model).delete()
    db.commit()
    seed_database(db, parse_start_date())
    return {"status": "reset", "message": "Database has been reset and seeded again."}
