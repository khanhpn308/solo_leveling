import os
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://ielts_user:ielts_password@mysql:3306/ielts_quest",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def wait_for_database(max_retries: int = 30, delay_seconds: int = 2) -> None:
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            return
        except OperationalError:
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_database_bootstrap() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    alembic_ini = base_dir / "alembic.ini"
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if not alembic_ini.exists():
        Base.metadata.create_all(bind=engine)
        return

    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    if not existing_tables:
        Base.metadata.create_all(bind=engine)
        command.stamp(alembic_cfg, "head")
        return

    command.upgrade(alembic_cfg, "head")
