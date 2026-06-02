from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="IELTS Hunter")
    title: Mapped[str] = mapped_column(String(120), default="B1 Awakener")
    target: Mapped[str] = mapped_column(String(120), default="IELTS Academic 7.0–7.5")
    current_level: Mapped[str] = mapped_column(String(50), default="B1")
    start_date: Mapped[date] = mapped_column(Date)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    icon: Mapped[str] = mapped_column(String(16), default="✦")
    xp: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[str] = mapped_column(String(2), default="F")
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced: Mapped[date | None] = mapped_column(Date, nullable=True)
    weak_point: Mapped[str] = mapped_column(String(255), default="")

    quests: Mapped[list["Quest"]] = relationship(back_populates="skill")


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quest_date: Mapped[date] = mapped_column(Date, index=True)
    week_no: Mapped[int] = mapped_column(Integer, index=True)
    stage: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(200))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    source: Mapped[str] = mapped_column(String(255))
    details: Mapped[str] = mapped_column(Text)
    xp: Mapped[int] = mapped_column(Integer, default=10)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    session_type: Mapped[str] = mapped_column(String(80), default="Daily Quest")

    skill: Mapped[Skill] = relationship(back_populates="quests")


class CheckIn(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("checkin_date", name="uq_checkin_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    checkin_date: Mapped[date] = mapped_column(Date, index=True)
    mood: Mapped[int] = mapped_column(Integer, default=3)
    energy: Mapped[int] = mapped_column(Integer, default=3)
    note: Mapped[str] = mapped_column(Text, default="")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    icon: Mapped[str] = mapped_column(String(16), default="🏅")
    description: Mapped[str] = mapped_column(String(255))
    unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BossBattle(Base):
    __tablename__ = "boss_battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stage: Mapped[str] = mapped_column(String(80), index=True)
    battle_date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(160))
    source: Mapped[str] = mapped_column(String(255))
    goal: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="Locked")
