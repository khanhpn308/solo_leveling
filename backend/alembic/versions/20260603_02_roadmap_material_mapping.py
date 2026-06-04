"""Add roadmap phase and study material mapping tables.

Revision ID: 20260603_02
Revises: 20260603_01
Create Date: 2026-06-03 23:20:00
"""

from datetime import timedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "20260603_02"
down_revision = "20260603_01"
branch_labels = None
depends_on = None


ROADMAP_PHASES = [
    ("phase-1", "Thang 1-3", 1, 3, 1, 13, "Tu B1 len nen IELTS 5.0-5.5; cung co grammar, vocabulary, cau dai, Listening/Reading nen.", "Reading,Vocabulary,Grammar,Listening"),
    ("phase-2", "Thang 4-6", 4, 6, 14, 26, "On dinh IELTS 5.5; bat dau hoc chien thuat IELTS ro rang cho 4 ky nang.", "Reading,Listening,Writing,Speaking"),
    ("phase-3", "Thang 7-9", 7, 9, 27, 39, "Tang len IELTS 6.0-6.5; chuyen sang tai lieu 6.5-7.5 va luyen Writing/Speaking deu.", "Writing,Speaking,Reading,Vocabulary"),
    ("phase-4", "Thang 10-12", 10, 12, 40, 52, "Cung co IELTS 6.5; bat dau dung Cambridge IELTS 17 tung phan va tang toc do.", "Reading,Listening,Writing,Collocation"),
    ("phase-5", "Thang 13-18", 13, 18, 53, 78, "Luyen de, sua loi sau, toi uu ky thuat phong thi; muc tieu IELTS 7.0-7.5.", "Reading,Listening,Writing,Speaking,Grammar"),
]


def has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def has_column(inspector, table_name: str, column_name: str) -> bool:
    if not has_table(inspector, table_name):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def ensure_column(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not has_column(inspector, table_name, column.name):
        op.add_column(table_name, column)


def has_index(inspector, table_name: str, index_name: str) -> bool:
    if not has_table(inspector, table_name):
        return False
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def ensure_index(table_name: str, index_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not has_index(inspector, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def create_tables() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not has_table(inspector, "study_materials"):
        op.create_table(
            "study_materials",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("format", sa.String(length=40), nullable=False, server_default="book"),
            sa.Column("file_path", sa.String(length=500), nullable=False, server_default=""),
            sa.Column("skill_tags", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("recommended_phase_start", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("recommended_phase_end", sa.Integer(), nullable=False, server_default="5"),
            sa.Column("notes", sa.Text(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("title", name="uq_study_materials_title"),
        )
        op.create_index("ix_study_materials_title", "study_materials", ["title"])
        op.create_index("ix_study_materials_category", "study_materials", ["category"])
        op.create_index("ix_study_materials_is_active", "study_materials", ["is_active"])
        op.create_index("ix_study_materials_created_at", "study_materials", ["created_at"])

    if not has_table(inspector, "roadmap_phases"):
        op.create_table(
            "roadmap_phases",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("phase_order", sa.Integer(), nullable=False),
            sa.Column("code", sa.String(length=40), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("month_start", sa.Integer(), nullable=False),
            sa.Column("month_end", sa.Integer(), nullable=False),
            sa.Column("week_start", sa.Integer(), nullable=False),
            sa.Column("week_end", sa.Integer(), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("objective", sa.Text(), nullable=False),
            sa.Column("focus_skills", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_roadmap_phases_campaign_id", "roadmap_phases", ["campaign_id"])
        op.create_index("ix_roadmap_phases_phase_order", "roadmap_phases", ["phase_order"])
        op.create_index("ix_roadmap_phases_code", "roadmap_phases", ["code"])
        op.create_index("ix_roadmap_phases_week_start", "roadmap_phases", ["week_start"])
        op.create_index("ix_roadmap_phases_week_end", "roadmap_phases", ["week_end"])
        op.create_index("ix_roadmap_phases_start_date", "roadmap_phases", ["start_date"])
        op.create_index("ix_roadmap_phases_end_date", "roadmap_phases", ["end_date"])
        op.create_index("ix_roadmap_phases_is_active", "roadmap_phases", ["is_active"])
        op.create_index("ix_roadmap_phases_created_at", "roadmap_phases", ["created_at"])

    if not has_table(inspector, "phase_materials"):
        op.create_table(
            "phase_materials",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("phase_id", sa.Integer(), sa.ForeignKey("roadmap_phases.id"), nullable=False),
            sa.Column("material_id", sa.Integer(), sa.ForeignKey("study_materials.id"), nullable=False),
            sa.Column("usage_purpose", sa.String(length=120), nullable=False, server_default=""),
            sa.Column("usage_frequency", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("notes", sa.Text(), nullable=False),
            sa.Column("display_order", sa.Integer(), nullable=False, server_default="1"),
            sa.UniqueConstraint("phase_id", "material_id", name="uq_phase_material"),
        )
        op.create_index("ix_phase_materials_phase_id", "phase_materials", ["phase_id"])
        op.create_index("ix_phase_materials_material_id", "phase_materials", ["material_id"])


def seed_materials_and_phases() -> None:
    bind = op.get_bind()
    material_rows = [
        ("The Official Cambridge Guide to IELTS", "guide", "book", "Listening,Reading,Writing,Speaking", 1, 5, "Dung nhu sach dinh huong va practice test, khong hoc don."),
        ("Complete IELTS Band 5.0-6.5", "coursebook", "book", "Listening,Reading,Writing,Speaking", 1, 2, "Truc chinh giai doan nen."),
        ("Complete IELTS Bands 6.5-7.5", "coursebook", "book", "Listening,Reading,Writing,Speaking", 3, 4, "Tang band va tang do kho topic."),
        ("English Grammar in Use", "grammar", "book", "Grammar,Writing,Speaking", 1, 2, "Cung co grammar nen va loi co ban."),
        ("Cambridge Grammar for IELTS", "grammar", "book", "Grammar,Writing,Speaking", 1, 5, "Grammar gan voi bai thi IELTS va xu ly loi yeu."),
        ("English Vocabulary in Use Upper-Intermediate", "vocabulary", "book", "Vocabulary,Reading,Writing", 1, 2, "Tu vung nen B2."),
        ("IELTS Vocabulary for Bands 6.5 and above", "vocabulary", "book", "Vocabulary,Reading,Writing", 3, 5, "Tu vung IELTS band cao."),
        ("Cambridge Academic Vocabulary in Use", "vocabulary", "book", "Vocabulary,Reading,Writing", 3, 5, "Hoc thuat cho Reading/Writing."),
        ("English Collocations in Use Intermediate", "collocation", "book", "Collocation,Writing,Speaking", 1, 3, "Noi/viet tu nhien hon."),
        ("English Collocations in Use Advanced", "collocation", "book", "Collocation,Writing,Speaking", 4, 5, "Nang chat luong output o phase sau."),
        ("IELTS Advantage Reading Skills", "reading", "book", "Reading,Vocabulary", 2, 5, "Chien thuat tung dang Reading."),
        ("IELTS Advantage - Speaking and Listening Skills", "listening_speaking", "book", "Listening,Speaking", 2, 5, "Ket hop audio, transcript, recording."),
        ("IELTS Advantage Writing Skills", "writing", "book", "Writing,Vocabulary,Grammar", 2, 5, "Writing Task 1/2, nen gui sua bai neu co the."),
        ("Cambridge IELTS 17", "mock", "book", "Listening,Reading,Writing,Speaking", 4, 5, "Luyen de sat thi that, khong dung qua som."),
        ("Any current notebook", "review", "notes", "Vocabulary,Grammar,Reading,Listening,Writing,Speaking", 1, 5, "Mini review, flashcard, transcript note, error recall."),
    ]
    for row in material_rows:
        existing_id = bind.execute(
            text("SELECT id FROM study_materials WHERE title = :title LIMIT 1"),
            {"title": row[0]},
        ).scalar()
        if existing_id:
            continue
        bind.execute(
            text(
                """
                INSERT INTO study_materials
                    (title, category, format, skill_tags, recommended_phase_start, recommended_phase_end, notes, is_active, created_at)
                VALUES
                    (:title, :category, :format, :skill_tags, :phase_start, :phase_end, :notes, 1, NOW())
                """
            ),
            {
                "title": row[0],
                "category": row[1],
                "format": row[2],
                "skill_tags": row[3],
                "phase_start": row[4],
                "phase_end": row[5],
                "notes": row[6],
            },
        )

    campaigns = bind.execute(text("SELECT id, start_date FROM campaigns")).mappings().all()
    for campaign in campaigns:
        for phase_order, phase in enumerate(ROADMAP_PHASES, start=1):
            code, title, month_start, month_end, week_start, week_end, objective, focus_skills = phase
            existing_id = bind.execute(
                text(
                    """
                    SELECT id FROM roadmap_phases
                    WHERE campaign_id = :campaign_id AND code = :code
                    LIMIT 1
                    """
                ),
                {"campaign_id": campaign["id"], "code": code},
            ).scalar()
            if existing_id:
                continue
            start_date = campaign["start_date"] + timedelta(days=(week_start - 1) * 7)
            end_date = campaign["start_date"] + timedelta(days=(week_end * 7) - 1)
            bind.execute(
                text(
                    """
                    INSERT INTO roadmap_phases
                        (campaign_id, phase_order, code, title, month_start, month_end, week_start, week_end, start_date, end_date, objective, focus_skills, is_active, created_at)
                    VALUES
                        (:campaign_id, :phase_order, :code, :title, :month_start, :month_end, :week_start, :week_end, :start_date, :end_date, :objective, :focus_skills, 1, NOW())
                    """
                ),
                {
                    "campaign_id": campaign["id"],
                    "phase_order": phase_order,
                    "code": code,
                    "title": title,
                    "month_start": month_start,
                    "month_end": month_end,
                    "week_start": week_start,
                    "week_end": week_end,
                    "start_date": start_date,
                    "end_date": end_date,
                    "objective": objective,
                    "focus_skills": focus_skills,
                },
            )


def backfill_links() -> None:
    bind = op.get_bind()

    bind.execute(
        text(
            """
            UPDATE quest_templates qt
            JOIN study_materials sm ON sm.title = qt.resource_name
            SET qt.material_id = sm.id
            WHERE qt.material_id IS NULL AND qt.resource_name <> ''
            """
        )
    )

    bind.execute(
        text(
            """
            UPDATE quests q
            JOIN quest_templates qt ON qt.id = q.template_id
            SET q.material_id = qt.material_id
            WHERE q.material_id IS NULL AND qt.material_id IS NOT NULL
            """
        )
    )

    campaigns = bind.execute(text("SELECT id FROM campaigns")).mappings().all()
    for campaign in campaigns:
        phase_rows = bind.execute(
            text(
                """
                SELECT id, week_start, week_end
                FROM roadmap_phases
                WHERE campaign_id = :campaign_id
                ORDER BY phase_order
                """
            ),
            {"campaign_id": campaign["id"]},
        ).mappings().all()
        for phase in phase_rows:
            bind.execute(
                text(
                    """
                    UPDATE quests
                    SET phase_id = :phase_id
                    WHERE campaign_id = :campaign_id
                      AND phase_id IS NULL
                      AND week_no BETWEEN :week_start AND :week_end
                    """
                ),
                {
                    "phase_id": phase["id"],
                    "campaign_id": campaign["id"],
                    "week_start": phase["week_start"],
                    "week_end": phase["week_end"],
                },
            )

    bind.execute(
        text(
            """
            UPDATE quest_templates qt
            JOIN roadmap_phases rp
              ON rp.phase_order = qt.allowed_phase_start
            JOIN campaigns c
              ON c.id = rp.campaign_id
            SET qt.phase_id = rp.id
            WHERE qt.phase_id IS NULL
              AND c.id = (
                  SELECT MIN(id) FROM campaigns
              )
            """
        )
    )


def upgrade() -> None:
    create_tables()
    ensure_column("quest_templates", sa.Column("phase_id", sa.Integer(), sa.ForeignKey("roadmap_phases.id"), nullable=True))
    ensure_column("quest_templates", sa.Column("material_id", sa.Integer(), sa.ForeignKey("study_materials.id"), nullable=True))
    ensure_column("quests", sa.Column("phase_id", sa.Integer(), sa.ForeignKey("roadmap_phases.id"), nullable=True))
    ensure_column("quests", sa.Column("material_id", sa.Integer(), sa.ForeignKey("study_materials.id"), nullable=True))

    ensure_index("quest_templates", "ix_quest_templates_phase_id", ["phase_id"])
    ensure_index("quest_templates", "ix_quest_templates_material_id", ["material_id"])
    ensure_index("quests", "ix_quests_phase_id", ["phase_id"])
    ensure_index("quests", "ix_quests_material_id", ["material_id"])

    seed_materials_and_phases()
    backfill_links()


def downgrade() -> None:
    pass
