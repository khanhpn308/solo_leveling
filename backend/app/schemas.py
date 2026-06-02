from datetime import date, datetime
from pydantic import BaseModel, Field


class SkillOut(BaseModel):
    id: int
    name: str
    icon: str
    xp: int
    rank: str
    level: int
    streak: int
    last_practiced: date | None
    weak_point: str

    class Config:
        from_attributes = True


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


class CheckInIn(BaseModel):
    checkin_date: date
    mood: int = Field(ge=1, le=5)
    energy: int = Field(ge=1, le=5)
    note: str = ""


class CheckInOut(BaseModel):
    id: int
    checkin_date: date
    mood: int
    energy: int
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


class BossBattleOut(BaseModel):
    id: int
    stage: str
    battle_date: date
    title: str
    source: str
    goal: str
    status: str

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
