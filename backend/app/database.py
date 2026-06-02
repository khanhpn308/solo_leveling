import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError

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
