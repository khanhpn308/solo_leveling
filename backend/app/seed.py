from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
import re

from sqlalchemy.orm import Session

from .models import (
    Badge,
    BossBattle,
    Campaign,
    PhaseMaterial,
    Player,
    Quest,
    QuestTemplate,
    RoadmapPhase,
    Skill,
    StudyPlanSession,
    StudyPlanWeek,
    StudyMaterial,
    TestRecord,
    WeeklyMission,
    WeeklyMissionItem,
)
from .services import create_rank_suggestions_for_test

SKILLS = [
    ("Listening", "🎧", "Diem manh hien tai; can nang Section 3-4, distractor va spelling."),
    ("Reading", "📖", "Diem yeu chinh: thieu tu vung va chua quen phan tich cau dai."),
    ("Writing", "✍️", "Can viet deu, sua loi theo 4 tieu chi IELTS."),
    ("Speaking", "🗣️", "Can ghi am deu, tang fluency, pronunciation va Part 3 reasoning."),
    ("Vocabulary", "🧠", "Hoc theo topic, paraphrase pairs va vi du ca nhan hoa."),
    ("Collocation", "🔗", "Dung de noi va viet tu nhien hon, giam loi ket hop tu."),
    ("Grammar", "⚙️", "Cung co thi, menh de quan he, bi dong, cau dieu kien va cau phuc."),
]

BADGES = [
    ("7-Day Streak", "🔥", "Hoc lien tuc 7 ngay."),
    ("Vocabulary Hunter", "🧠", "Hoan thanh 300 XP Vocabulary."),
    ("Grammar Fixer", "⚙️", "Hoan thanh 300 XP Grammar."),
    ("Listening Warrior", "🎧", "Hoan thanh 500 XP Listening."),
    ("Reading Decoder", "📖", "Hoan thanh 500 XP Reading."),
    ("Writing Starter", "✍️", "Hoan thanh 300 XP Writing."),
    ("Speaking Brave Mode", "🗣️", "Hoan thanh 300 XP Speaking."),
    ("Error Killer", "⚔️", "Ghi va sua nhieu loi da hieu ro."),
    ("Band 6 Challenger", "🥈", "Vuot qua checkpoint giua roadmap."),
    ("Band 7 Candidate", "🏆", "Hoan thanh chuoi mock test cuoi roadmap."),
]

RANK_THRESHOLDS = [
    (3500, "S", 7),
    (2500, "A", 6),
    (1700, "B", 5),
    (1000, "C", 4),
    (500, "D", 3),
    (200, "E", 2),
    (0, "F", 1),
]

ROADMAP_PHASES = [
    {
        "phase_order": 1,
        "code": "phase-1",
        "title": "Thang 1-3",
        "month_start": 1,
        "month_end": 3,
        "week_start": 1,
        "week_end": 13,
        "objective": "Tu B1 len nen IELTS 5.0-5.5; cung co grammar, vocabulary, cau dai, Listening/Reading nen.",
        "focus_skills": "Reading,Vocabulary,Grammar,Listening",
    },
    {
        "phase_order": 2,
        "code": "phase-2",
        "title": "Thang 4-6",
        "month_start": 4,
        "month_end": 6,
        "week_start": 14,
        "week_end": 26,
        "objective": "On dinh IELTS 5.5; bat dau hoc chien thuat IELTS ro rang cho 4 ky nang.",
        "focus_skills": "Reading,Listening,Writing,Speaking",
    },
    {
        "phase_order": 3,
        "code": "phase-3",
        "title": "Thang 7-9",
        "month_start": 7,
        "month_end": 9,
        "week_start": 27,
        "week_end": 39,
        "objective": "Tang len IELTS 6.0-6.5; chuyen sang tai lieu 6.5-7.5 va luyen Writing/Speaking deu.",
        "focus_skills": "Writing,Speaking,Reading,Vocabulary",
    },
    {
        "phase_order": 4,
        "code": "phase-4",
        "title": "Thang 10-12",
        "month_start": 10,
        "month_end": 12,
        "week_start": 40,
        "week_end": 52,
        "objective": "Cung co IELTS 6.5; bat dau dung Cambridge IELTS 17 tung phan va tang toc do.",
        "focus_skills": "Reading,Listening,Writing,Collocation",
    },
    {
        "phase_order": 5,
        "code": "phase-5",
        "title": "Thang 13-18",
        "month_start": 13,
        "month_end": 18,
        "week_start": 53,
        "week_end": 78,
        "objective": "Luyen de, sua loi sau, toi uu ky thuat phong thi; muc tieu IELTS 7.0-7.5.",
        "focus_skills": "Reading,Listening,Writing,Speaking,Grammar",
    },
]

STUDY_MATERIALS = [
    {
        "title": "The Official Cambridge Guide to IELTS",
        "category": "guide",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 5,
        "notes": "Dung nhu sach dinh huong va practice test, khong hoc don.",
    },
    {
        "title": "Complete IELTS Band 5.0-6.5",
        "category": "coursebook",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 2,
        "notes": "Truc chinh giai doan nen.",
    },
    {
        "title": "Complete IELTS Bands 6.5-7.5",
        "category": "coursebook",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 3,
        "recommended_phase_end": 4,
        "notes": "Tang band va tang do kho topic.",
    },
    {
        "title": "English Grammar in Use",
        "category": "grammar",
        "format": "book",
        "skill_tags": "Grammar,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 2,
        "notes": "Cung co grammar nen va loi co ban.",
    },
    {
        "title": "Cambridge Grammar for IELTS",
        "category": "grammar",
        "format": "book",
        "skill_tags": "Grammar,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 5,
        "notes": "Grammar gan voi bai thi IELTS va xu ly loi yeu.",
    },
    {
        "title": "English Vocabulary in Use Upper-Intermediate",
        "category": "vocabulary",
        "format": "book",
        "skill_tags": "Vocabulary,Reading,Writing",
        "recommended_phase_start": 1,
        "recommended_phase_end": 2,
        "notes": "Tu vung nen B2.",
    },
    {
        "title": "IELTS Vocabulary for Bands 6.5 and above",
        "category": "vocabulary",
        "format": "book",
        "skill_tags": "Vocabulary,Reading,Writing",
        "recommended_phase_start": 3,
        "recommended_phase_end": 5,
        "notes": "Tu vung IELTS band cao.",
    },
    {
        "title": "Cambridge Academic Vocabulary in Use",
        "category": "vocabulary",
        "format": "book",
        "skill_tags": "Vocabulary,Reading,Writing",
        "recommended_phase_start": 3,
        "recommended_phase_end": 5,
        "notes": "Hoc thuat cho Reading/Writing.",
    },
    {
        "title": "English Collocations in Use Intermediate",
        "category": "collocation",
        "format": "book",
        "skill_tags": "Collocation,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 3,
        "notes": "Noi/viet tu nhien hon.",
    },
    {
        "title": "English Collocations in Use Advanced",
        "category": "collocation",
        "format": "book",
        "skill_tags": "Collocation,Writing,Speaking",
        "recommended_phase_start": 4,
        "recommended_phase_end": 5,
        "notes": "Nang chat luong output o phase sau.",
    },
    {
        "title": "IELTS Advantage Reading Skills",
        "category": "reading",
        "format": "book",
        "skill_tags": "Reading,Vocabulary",
        "recommended_phase_start": 2,
        "recommended_phase_end": 5,
        "notes": "Chien thuat tung dang Reading.",
    },
    {
        "title": "IELTS Advantage - Speaking and Listening Skills",
        "category": "listening_speaking",
        "format": "book",
        "skill_tags": "Listening,Speaking",
        "recommended_phase_start": 2,
        "recommended_phase_end": 5,
        "notes": "Ket hop audio, transcript, recording.",
    },
    {
        "title": "IELTS Advantage Writing Skills",
        "category": "writing",
        "format": "book",
        "skill_tags": "Writing,Vocabulary,Grammar",
        "recommended_phase_start": 2,
        "recommended_phase_end": 5,
        "notes": "Writing Task 1/2, nen gui sua bai neu co the.",
    },
    {
        "title": "Cambridge IELTS 17",
        "category": "mock",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 4,
        "recommended_phase_end": 5,
        "notes": "Luyen de sat thi that, khong dung qua som.",
    },
    {
        "title": "Any current notebook",
        "category": "review",
        "format": "notes",
        "skill_tags": "Vocabulary,Grammar,Reading,Listening,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 5,
        "notes": "Mini review, flashcard, transcript note, error recall.",
    },
]

PHASE_MATERIAL_PLAN = {
    1: [
        ("The Official Cambridge Guide to IELTS", "orientation", "1-2 buoi/tuan khi can", "Dung de hieu format va ky thuat co ban."),
        ("Complete IELTS Band 5.0-6.5", "core", "1 unit/1-2 tuan", "Truc chinh giai doan nen."),
        ("English Grammar in Use", "support", "2-3 units/tuan", "Tap trung loi thuong gap."),
        ("Cambridge Grammar for IELTS", "support", "1 unit/tuan", "Ung dung vao Writing/Speaking."),
        ("English Vocabulary in Use Upper-Intermediate", "support", "2 units/tuan", "Ghi tu theo cum va dat cau."),
        ("English Collocations in Use Intermediate", "support", "1-2 units/tuan", "Chon unit Study/Work/Academic truoc."),
    ],
    2: [
        ("Complete IELTS Band 5.0-6.5", "core", "1 unit/1-2 tuan", "Tiep tuc on nen IELTS."),
        ("The Official Cambridge Guide to IELTS", "orientation", "1-2 buoi/tuan khi can", "Dung de chot format cac dang bai."),
        ("Cambridge Grammar for IELTS", "support", "1 unit/tuan", "Tiep tuc grammar IELTS."),
        ("English Vocabulary in Use Upper-Intermediate", "support", "2 units/tuan", "Duy tri vocab nen."),
        ("English Collocations in Use Intermediate", "support", "1-2 units/tuan", "Duy tri collocation output."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 buoi/tuan", "Chua bai ky hon lam nhieu."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 bai/tuan", "Bat dau task-focused writing."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 buoi/tuan", "Ket hop speaking recording va transcript."),
    ],
    3: [
        ("Complete IELTS Bands 6.5-7.5", "core", "1 unit/1-2 tuan", "Chuyen len topic kho hon."),
        ("Cambridge Grammar for IELTS", "support", "on loi yeu", "Chi quay lai unit dang yeu."),
        ("IELTS Vocabulary for Bands 6.5 and above", "support", "1-2 units/tuan", "Uu tien topic hay gap."),
        ("Cambridge Academic Vocabulary in Use", "support", "1-2 units/tuan", "Tang chat hoc thuat."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 buoi/tuan", "Reading strategy level cao hon."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 bai/tuan", "Tang tam trong Task 2."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 buoi/tuan", "Tang Part 2/3 va fluency."),
    ],
    4: [
        ("Complete IELTS Bands 6.5-7.5", "core", "1 unit/1-2 tuan", "Cung co nen 6.5."),
        ("The Official Cambridge Guide to IELTS", "orientation", "1 buoi/tuan khi can", "Review guideline va dang bai."),
        ("Cambridge Grammar for IELTS", "support", "on loi yeu", "Chi sua loi recurring."),
        ("Cambridge Academic Vocabulary in Use", "support", "1-2 units/tuan", "Essay va reading hoc thuat."),
        ("English Collocations in Use Advanced", "support", "1 unit/tuan", "Nang chat luong output."),
        ("Cambridge IELTS 17", "mock", "tung phan -> full test", "Dung can than de giu bo de."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 buoi/tuan", "Chua ky cac dang reading."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 bai/tuan", "Review task strategy."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 buoi/tuan", "Speaking/listening review."),
    ],
    5: [
        ("Cambridge IELTS 17", "mock", "tang dan den full test", "Luyen de va review sau bai."),
        ("The Official Cambridge Guide to IELTS", "orientation", "khi can", "Chot checklist thi that."),
        ("Cambridge Grammar for IELTS", "support", "chi sua loi", "Khong hoc lan man nua."),
        ("IELTS Vocabulary for Bands 6.5 and above", "support", "1-2 units/tuan", "Gap topic thi on muc tieu."),
        ("Cambridge Academic Vocabulary in Use", "support", "1-2 units/tuan", "Essay va reading academic."),
        ("English Collocations in Use Advanced", "support", "1 unit/tuan", "Lam output tu nhien hon."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 bai/tuan", "Weekly writing correction."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 buoi/tuan", "Speaking recording/review."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 buoi/tuan", "Reading strategy va error review."),
    ],
}

MATERIAL_ALIASES = {
    "The Official Cambridge Guide to IELTS": "The Official Cambridge Guide to IELTS",
    "Complete IELTS Band 5.0–6.5": "Complete IELTS Band 5.0-6.5",
    "Complete IELTS Band 5.0-6.5": "Complete IELTS Band 5.0-6.5",
    "Complete IELTS Bands 6.5–7.5": "Complete IELTS Bands 6.5-7.5",
    "Complete IELTS Bands 6.5-7.5": "Complete IELTS Bands 6.5-7.5",
    "English Grammar in Use": "English Grammar in Use",
    "Cambridge Grammar for IELTS": "Cambridge Grammar for IELTS",
    "English Vocabulary in Use Upper-Intermediate": "English Vocabulary in Use Upper-Intermediate",
    "IELTS Vocabulary for Bands 6.5 and above": "IELTS Vocabulary for Bands 6.5 and above",
    "Cambridge Academic Vocabulary in Use": "Cambridge Academic Vocabulary in Use",
    "English Collocations in Use Intermediate": "English Collocations in Use Intermediate",
    "English Collocations in Use Advanced": "English Collocations in Use Advanced",
    "IELTS Advantage Reading Skills": "IELTS Advantage Reading Skills",
    "IELTS Advantage Writing Skills": "IELTS Advantage Writing Skills",
    "IELTS Advantage Speaking and Listening Skills": "IELTS Advantage - Speaking and Listening Skills",
    "Official Guide": "The Official Cambridge Guide to IELTS",
    "The Official Cambridge Guide": "The Official Cambridge Guide to IELTS",
    "audio/transcript": "Any current notebook",
    "Vocabulary notebook": "Any current notebook",
    "Cambridge IELTS 17": "Cambridge IELTS 17",
}


def get_rank_level(xp: int) -> tuple[str, int]:
    for threshold, rank, level in RANK_THRESHOLDS:
        if xp >= threshold:
            return rank, level
    return "F", 1


def phase_label(phase_index: int) -> str:
    mapping = {
        1: "Thang 1-3",
        2: "Thang 4-6",
        3: "Thang 7-9",
        4: "Thang 10-12",
        5: "Thang 13-18",
    }
    return mapping.get(phase_index, "Thang 13-18")


def phase_for_week(week_no: int) -> int:
    if week_no <= 13:
        return 1
    if week_no <= 26:
        return 2
    if week_no <= 39:
        return 3
    if week_no <= 52:
        return 4
    return 5


def campaign_end_date(start_date: date) -> date:
    return start_date + timedelta(days=548)


def quest_template_seed() -> list[dict]:
    return [
        {
            "title": "Reading Core Sweep",
            "description": "Lam 1 reading passage, cham lai, va phan tich 3-5 cau dai.",
            "skill": "Reading",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage Reading Skills",
            "base_xp": 25,
            "difficulty": "normal",
            "difficulty_description": "Doc va phan tich chi tiet.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Reading Skills",
            "resource_category": "book",
            "resource_note": "Tap trung paraphrase va long sentence parsing.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Listening Core Sweep",
            "description": "Lam 1 listening task, review transcript, ghi distractor va spelling.",
            "skill": "Listening",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage - Speaking and Listening Skills",
            "base_xp": 20,
            "difficulty": "normal",
            "difficulty_description": "Can do va transcript review.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Speaking and Listening Skills",
            "resource_category": "book",
            "resource_note": "Tang chat luong Section 3-4.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Writing Core Draft",
            "description": "Viet 1 doan hoac 1 bai ngan va tu sua theo tieu chi IELTS.",
            "skill": "Writing",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage Writing Skills",
            "base_xp": 25,
            "difficulty": "normal",
            "difficulty_description": "Can draft va self-review.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Writing Skills",
            "resource_category": "book",
            "resource_note": "Task 1/2 tuy phase.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Speaking Core Record",
            "description": "Record Speaking Part 1/2/3, nghe lai va ghi 3 diem can sua.",
            "skill": "Speaking",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage - Speaking and Listening Skills",
            "base_xp": 25,
            "difficulty": "normal",
            "difficulty_description": "Can ghi am va tu danh gia.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Speaking and Listening Skills",
            "resource_category": "book",
            "resource_note": "Tap trung fluency va reasoning.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Vocabulary Support Pack",
            "description": "Hoc 10 tu moi, 3 collocations va 2 paraphrase pairs.",
            "skill": "Vocabulary",
            "phase_code": "phase-1",
            "material_title": "English Vocabulary in Use Upper-Intermediate",
            "base_xp": 10,
            "difficulty": "easy",
            "difficulty_description": "Ngan, de duy tri nhip.",
            "quest_role": "support",
            "resource_name": "English Vocabulary in Use Upper-Intermediate",
            "resource_category": "book",
            "resource_note": "Dung cho phase 1-2 va review ve sau.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Grammar Support Forge",
            "description": "Hoc 1 diem grammar, lam bai tap ngan va viet 3 cau ung dung.",
            "skill": "Grammar",
            "phase_code": "phase-1",
            "material_title": "Cambridge Grammar for IELTS",
            "base_xp": 15,
            "difficulty": "easy",
            "difficulty_description": "Review co huong dan.",
            "quest_role": "support",
            "resource_name": "Cambridge Grammar for IELTS",
            "resource_category": "book",
            "resource_note": "Gap error thi quay lai unit lien quan.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Collocation Support Pack",
            "description": "Hoc 5 collocations va viet 3 cau co context ca nhan.",
            "skill": "Collocation",
            "phase_code": "phase-1",
            "material_title": "English Collocations in Use Intermediate",
            "base_xp": 10,
            "difficulty": "easy",
            "difficulty_description": "Quick support loop.",
            "quest_role": "support",
            "resource_name": "English Collocations in Use Intermediate",
            "resource_category": "book",
            "resource_note": "Phase sau chuyen len Advanced.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Mini Review Burst",
            "description": "Review nhanh 5-10 phut: flashcard, transcript note hoac error recall.",
            "skill": "Vocabulary",
            "phase_code": "phase-1",
            "material_title": "Any current notebook",
            "base_xp": 5,
            "difficulty": "easy",
            "difficulty_description": "Rat nhe de giu streak.",
            "quest_role": "mini",
            "resource_name": "Any current notebook",
            "resource_category": "review",
            "resource_note": "Mini quest co the lien skill chinh hom do.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Mock Reading Raid",
            "description": "Lam reading timed set va tong hop loi sai, phu hop phase 4-5.",
            "skill": "Reading",
            "phase_code": "phase-4",
            "material_title": "Cambridge IELTS 17",
            "base_xp": 40,
            "difficulty": "hard",
            "difficulty_description": "Timed practice, phan tich sau bai.",
            "quest_role": "core",
            "resource_name": "Cambridge IELTS 17",
            "resource_category": "mock",
            "resource_note": "Chi xuat hien phase 4-5.",
            "allowed_phase_start": 4,
            "allowed_phase_end": 5,
        },
        {
            "title": "Mock Listening Raid",
            "description": "Lam listening timed set va review transcript ky, phu hop phase 4-5.",
            "skill": "Listening",
            "phase_code": "phase-4",
            "material_title": "Cambridge IELTS 17",
            "base_xp": 40,
            "difficulty": "hard",
            "difficulty_description": "Timed practice, transcript review sau bai.",
            "quest_role": "core",
            "resource_name": "Cambridge IELTS 17",
            "resource_category": "mock",
            "resource_note": "Chi xuat hien phase 4-5.",
            "allowed_phase_start": 4,
            "allowed_phase_end": 5,
        },
    ]


def material_file_path() -> Path:
    candidates: list[Path] = []

    configured_path = os.getenv("MATERIAL_PLAN_PATH")
    if configured_path:
        candidates.append(Path(configured_path))

    current_file = Path(__file__).resolve()
    candidates.extend(
        [
            current_file.parents[2] / "material.md",
            current_file.parents[1] / "material.md",
            Path.cwd() / "material.md",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"material.md not found. Checked: {searched}")


def parse_date_range(value: str) -> tuple[date, date]:
    normalized = value.replace("â€“", "–").replace("—", "–")
    if "–" in normalized:
        start_raw, end_raw = [item.strip() for item in normalized.split("–", 1)]
    else:
        start_raw, end_raw = [item.strip() for item in re.split(r"\s+-\s+", normalized, maxsplit=1)]
    start_day, start_month, start_year = [int(part) for part in start_raw.split("/")]
    end_day, end_month, end_year = [int(part) for part in end_raw.split("/")]
    return date(start_year, start_month, start_day), date(end_year, end_month, end_day)


def split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_material_plan() -> tuple[list[dict], list[dict]]:
    text = material_file_path().read_text(encoding="utf-8")
    week_rows: list[dict] = []
    session_rows: list[dict] = []

    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = split_markdown_row(line)
        if (
            len(cols) >= 6
            and cols[0].isdigit()
            and "/" in cols[1]
            and any(separator in cols[1] for separator in ("–", "â€“", "—", " - "))
            and not cols[1].startswith("202")
        ):
            week_start, week_end = parse_date_range(cols[1])
            week_rows.append(
                {
                    "week_no": int(cols[0]),
                    "week_start": week_start,
                    "week_end": week_end,
                    "weekly_focus": cols[2],
                    "weekly_output": cols[3],
                    "material_summary": cols[4],
                    "mini_task": cols[5],
                }
            )

    session_pattern = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2}) 00:00:00\s*\|", re.M)
    for match in session_pattern.finditer(text):
        full_line = text[match.start() : text.find("\n", match.start())]
        cols = split_markdown_row(full_line)
        if len(cols) < 11:
            continue
        study_date = date.fromisoformat(cols[1].split()[0])
        session_rows.append(
            {
                "week_no": int(cols[0]),
                "study_date": study_date,
                "weekday_label": cols[2],
                "session_label": cols[3],
                "skill_summary": cols[4],
                "task_detail": cols[5],
                "material_summary": cols[6],
                "deliverable": cols[7],
                "status_text": cols[8],
                "note_text": "" if cols[9] == "NaN" else cols[9],
                "mini_task": cols[10],
            }
        )

    return week_rows, session_rows


def normalize_material_names(raw_value: str) -> list[str]:
    items = []
    for part in [item.strip() for item in raw_value.split(";") if item.strip()]:
        normalized = MATERIAL_ALIASES.get(part)
        if not normalized:
            for alias, canonical in MATERIAL_ALIASES.items():
                if alias in part or part in alias:
                    normalized = canonical
                    break
        if normalized:
            items.append(normalized)
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped


def infer_primary_skill(skill_summary: str) -> str:
    ordered = ["Listening", "Reading", "Writing", "Speaking", "Vocabulary", "Collocation", "Grammar"]
    for skill_name in ordered:
        if skill_name.lower() in skill_summary.lower():
            return skill_name
    return "Reading"


def infer_main_quest_xp(session_no: int, skill_summary: str) -> int:
    if session_no == 1:
        return 35
    if session_no == 2:
        return 40
    if session_no == 3:
        return 40
    if "Error log" in skill_summary or "Review" in skill_summary:
        return 25
    return 30


def weekly_mission_patterns(phase_index: int) -> list[dict]:
    phase_name = phase_label(phase_index)
    return [
        {
            "pattern_code": f"{phase_index}-balanced",
            "title": f"Weekly Mission - {phase_name} Balance",
            "description": "Giu nhip hoc deu tren 4 ky nang chinh va support loop.",
            "reward_xp": 40,
            "items": [
                ("Hoan thanh it nhat 3 core quest", 3),
                ("Co it nhat 4 check-in hoac mini review day", 4),
                ("Them it nhat 2 ghi chu vao Error Log/Writing/Speaking tracker", 2),
            ],
        },
        {
            "pattern_code": f"{phase_index}-reading-focus",
            "title": f"Weekly Mission - {phase_name} Reading Focus",
            "description": "Tap trung nang reading va vocabulary trong tuan nay.",
            "reward_xp": 45,
            "items": [
                ("Hoan thanh 2 Reading core quest", 2),
                ("Hoan thanh 3 Vocabulary/Collocation support quest", 3),
                ("Phan tich 5 cau dai hoac paraphrase kho", 5),
            ],
        },
        {
            "pattern_code": f"{phase_index}-output-focus",
            "title": f"Weekly Mission - {phase_name} Output Focus",
            "description": "Tang writing va speaking output de giam tri hoan.",
            "reward_xp": 45,
            "items": [
                ("Co 2 Writing/Speaking core quest duoc hoan thanh", 2),
                ("Tu review it nhat 2 diem yeu recurring", 2),
                ("Hoan thanh 1 mini review lien quan output skill", 1),
            ],
        },
    ]


def month_boss_title(month_index: int) -> str:
    if month_index == 1:
        return "Boss 01 - Foundation Scan"
    if month_index == 6:
        return "Boss 06 - IELTS 5.5 Checkpoint"
    if month_index == 12:
        return "Boss 12 - Cambridge Gate"
    if month_index == 18:
        return "Boss 18 - Final Simulation"
    return f"Boss {month_index:02d} - Monthly Checkpoint"


def onboarding_week_start(start_date: date) -> date:
    return start_date - timedelta(days=start_date.weekday())


def ensure_player(db: Session, start_date: date) -> Player:
    player = db.query(Player).first()
    if player:
        return player
    player = Player(
        name="IELTS Hunter",
        title="B1 Awakener",
        target="IELTS Academic 7.0-7.5",
        current_level="B1",
        start_date=start_date,
        display_name="IELTS Hunter",
        target_overall_band="7.0-7.5",
        current_estimated_level="B1",
        strongest_skill="Listening",
        weakest_skill="Reading",
        study_days_per_week=4,
        session_minutes=120,
        daily_mini_study_minutes=20,
        player_xp=0,
        player_level=1,
        player_rank="F",
        current_streak=0,
        best_streak=0,
        shield_count=1,
        shield_regen_progress=0,
        perfect_day_count=0,
        setup_completed=True,
    )
    db.add(player)
    db.flush()
    return player


def ensure_campaign(db: Session, player: Player, start_date: date) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.player_id == player.id).first()
    if campaign:
        if not player.active_campaign_id:
            player.active_campaign_id = campaign.id
        return campaign
    campaign = Campaign(
        player_id=player.id,
        start_date=start_date,
        end_date=campaign_end_date(start_date),
        status="active",
    )
    db.add(campaign)
    db.flush()
    player.active_campaign_id = campaign.id
    return campaign


def ensure_skills(db: Session) -> dict[str, Skill]:
    skill_by_name: dict[str, Skill] = {}
    for name, icon, weak_point in SKILLS:
        skill = db.query(Skill).filter(Skill.name == name).first()
        if not skill:
            skill = Skill(
                name=name,
                icon=icon,
                weak_point=weak_point,
                user_weakness_note=weak_point,
                confirmed_rank="F",
            )
            db.add(skill)
            db.flush()
        skill_by_name[name] = skill
    return skill_by_name


def ensure_badges(db: Session) -> list[Badge]:
    badges: list[Badge] = []
    for name, icon, description in BADGES:
        badge = db.query(Badge).filter(Badge.name == name).first()
        if not badge:
            badge = Badge(name=name, icon=icon, description=description)
            db.add(badge)
            db.flush()
        badges.append(badge)
    return badges


def ensure_materials(db: Session) -> dict[str, StudyMaterial]:
    material_by_title: dict[str, StudyMaterial] = {}
    for item in STUDY_MATERIALS:
        material = db.query(StudyMaterial).filter(StudyMaterial.title == item["title"]).first()
        if not material:
            material = StudyMaterial(**item)
            db.add(material)
            db.flush()
        material_by_title[material.title] = material
    return material_by_title


def ensure_roadmap_phases(db: Session, campaign: Campaign) -> dict[str, RoadmapPhase]:
    phase_by_code: dict[str, RoadmapPhase] = {}
    for item in ROADMAP_PHASES:
        phase = (
            db.query(RoadmapPhase)
            .filter(RoadmapPhase.campaign_id == campaign.id, RoadmapPhase.code == item["code"])
            .first()
        )
        if not phase:
            start_date = campaign.start_date + timedelta(days=(item["week_start"] - 1) * 7)
            end_date = campaign.start_date + timedelta(days=(item["week_end"] * 7) - 1)
            phase = RoadmapPhase(
                campaign_id=campaign.id,
                phase_order=item["phase_order"],
                code=item["code"],
                title=item["title"],
                month_start=item["month_start"],
                month_end=item["month_end"],
                week_start=item["week_start"],
                week_end=item["week_end"],
                start_date=start_date,
                end_date=end_date,
                objective=item["objective"],
                focus_skills=item["focus_skills"],
                is_active=True,
            )
            db.add(phase)
            db.flush()
        phase_by_code[phase.code] = phase
    return phase_by_code


def ensure_phase_materials(
    db: Session,
    phase_by_code: dict[str, RoadmapPhase],
    material_by_title: dict[str, StudyMaterial],
) -> None:
    phase_lookup = {phase.phase_order: phase for phase in phase_by_code.values()}
    for phase_order, material_rows in PHASE_MATERIAL_PLAN.items():
        phase = phase_lookup.get(phase_order)
        if not phase:
            continue
        for display_order, (material_title, usage_purpose, usage_frequency, notes) in enumerate(material_rows, start=1):
            material = material_by_title[material_title]
            existing = (
                db.query(PhaseMaterial)
                .filter(PhaseMaterial.phase_id == phase.id, PhaseMaterial.material_id == material.id)
                .first()
            )
            if existing:
                continue
            db.add(
                PhaseMaterial(
                    phase_id=phase.id,
                    material_id=material.id,
                    usage_purpose=usage_purpose,
                    usage_frequency=usage_frequency,
                    notes=notes,
                    display_order=display_order,
                )
            )


def ensure_study_plan(
    db: Session,
    campaign: Campaign,
    phase_by_code: dict[str, RoadmapPhase],
) -> tuple[dict[int, StudyPlanWeek], list[StudyPlanSession]]:
    week_rows, session_rows = parse_material_plan()
    week_by_no: dict[int, StudyPlanWeek] = {}

    for row in week_rows:
        phase = phase_by_code[f"phase-{phase_for_week(row['week_no'])}"]
        week = (
            db.query(StudyPlanWeek)
            .filter(StudyPlanWeek.campaign_id == campaign.id, StudyPlanWeek.week_no == row["week_no"])
            .first()
        )
        if not week:
            week = StudyPlanWeek(
                campaign_id=campaign.id,
                phase_id=phase.id,
                week_no=row["week_no"],
                week_start=row["week_start"],
                week_end=row["week_end"],
                weekly_focus=row["weekly_focus"],
                weekly_output=row["weekly_output"],
                material_summary=row["material_summary"],
                mini_task=row["mini_task"],
            )
            db.add(week)
            db.flush()
        week_by_no[week.week_no] = week

    session_entities: list[StudyPlanSession] = []
    for row in session_rows:
        week = week_by_no.get(row["week_no"])
        if not week:
            continue
        session_no_match = re.search(r"(\d+)", row["session_label"])
        session_no = int(session_no_match.group(1)) if session_no_match else 1
        session = (
            db.query(StudyPlanSession)
            .filter(
                StudyPlanSession.study_plan_week_id == week.id,
                StudyPlanSession.session_no == session_no,
            )
            .first()
        )
        if not session:
            session = StudyPlanSession(
                campaign_id=campaign.id,
                phase_id=week.phase_id,
                study_plan_week_id=week.id,
                week_no=week.week_no,
                session_no=session_no,
                study_date=row["study_date"],
                weekday_label=row["weekday_label"],
                session_label=row["session_label"],
                skill_summary=row["skill_summary"],
                task_detail=row["task_detail"],
                material_summary=row["material_summary"],
                deliverable=row["deliverable"],
                status_text=row["status_text"],
                note_text=row["note_text"],
                mini_task=row["mini_task"],
            )
            db.add(session)
            db.flush()
        session_entities.append(session)

    return week_by_no, session_entities


def ensure_templates(
    db: Session,
    skill_by_name: dict[str, Skill],
    phase_by_code: dict[str, RoadmapPhase],
    material_by_title: dict[str, StudyMaterial],
) -> dict[str, QuestTemplate]:
    template_by_title: dict[str, QuestTemplate] = {}
    for item in quest_template_seed():
        template = db.query(QuestTemplate).filter(QuestTemplate.title == item["title"]).first()
        if not template:
            template = QuestTemplate(
                title=item["title"],
                description=item["description"],
                primary_skill_id=skill_by_name[item["skill"]].id,
                phase_id=phase_by_code[item["phase_code"]].id,
                material_id=material_by_title[item["material_title"]].id,
                base_xp=item["base_xp"],
                difficulty=item["difficulty"],
                difficulty_description=item["difficulty_description"],
                quest_role=item["quest_role"],
                resource_name=item["resource_name"],
                resource_category=item["resource_category"],
                resource_note=item["resource_note"],
                allowed_phase_start=item["allowed_phase_start"],
                allowed_phase_end=item["allowed_phase_end"],
                is_active=True,
            )
            db.add(template)
            db.flush()
        else:
            template.phase_id = template.phase_id or phase_by_code[item["phase_code"]].id
            template.material_id = template.material_id or material_by_title[item["material_title"]].id
        template_by_title[template.title] = template
    return template_by_title


def daily_template_rotation(phase_index: int) -> list[str]:
    if phase_index <= 3:
        return [
            "Reading Core Sweep",
            "Vocabulary Support Pack",
            "Mini Review Burst",
            "Listening Core Sweep",
            "Grammar Support Forge",
            "Mini Review Burst",
            "Reading Core Sweep",
            "Collocation Support Pack",
            "Mini Review Burst",
            "Listening Core Sweep",
            "Vocabulary Support Pack",
            "Mini Review Burst",
            "Writing Core Draft",
            "Grammar Support Forge",
            "Mini Review Burst",
            "Reading Core Sweep",
            "Vocabulary Support Pack",
            "Mini Review Burst",
            "Speaking Core Record",
            "Collocation Support Pack",
            "Mini Review Burst",
        ]
    return [
        "Mock Reading Raid",
        "Vocabulary Support Pack",
        "Mini Review Burst",
        "Mock Listening Raid",
        "Grammar Support Forge",
        "Mini Review Burst",
        "Reading Core Sweep",
        "Collocation Support Pack",
        "Mini Review Burst",
        "Listening Core Sweep",
        "Vocabulary Support Pack",
        "Mini Review Burst",
        "Writing Core Draft",
        "Grammar Support Forge",
        "Mini Review Burst",
        "Speaking Core Record",
        "Collocation Support Pack",
        "Mini Review Burst",
        "Reading Core Sweep",
        "Vocabulary Support Pack",
        "Mini Review Burst",
    ]


def ensure_quest_instances(
    db: Session,
    campaign: Campaign,
    skill_by_name: dict[str, Skill],
    template_by_title: dict[str, QuestTemplate],
    phase_by_code: dict[str, RoadmapPhase],
) -> None:
    existing_daily_keys = {
        (quest.quest_date, quest.quest_role)
        for quest in db.query(Quest.quest_date, Quest.quest_role)
        .filter(Quest.campaign_id == campaign.id)
        .all()
    }

    total_weeks = 78
    for week_no in range(1, total_weeks + 1):
        phase_index = phase_for_week(week_no)
        phase_name = phase_label(phase_index)
        week_start = campaign.start_date + timedelta(days=(week_no - 1) * 7)
        rotation = daily_template_rotation(phase_index)
        for day_offset in range(7):
            base = day_offset * 3
            titles = rotation[base : base + 3]
            for template_title in titles:
                template = template_by_title[template_title]
                quest_date = week_start + timedelta(days=day_offset)
                if (quest_date, template.quest_role) in existing_daily_keys:
                    continue
                skill = next(skill for skill in skill_by_name.values() if skill.id == template.primary_skill_id)
                phase = phase_by_code[f"phase-{phase_index}"]
                db.add(
                    Quest(
                        quest_date=quest_date,
                        week_no=week_no,
                        stage=phase_name,
                        title=template.title,
                        skill_id=skill.id,
                        source=template.resource_name,
                        details=template.description,
                        xp=template.base_xp,
                        session_type="Daily Quest",
                        campaign_id=campaign.id,
                        phase_id=phase.id,
                        template_id=template.id,
                        material_id=template.material_id,
                        status="pending",
                        quest_role=template.quest_role,
                        difficulty=template.difficulty,
                        base_xp=template.base_xp,
                        earned_xp=0,
                    )
                )
                existing_daily_keys.add((quest_date, template.quest_role))


def ensure_main_quest_instances(
    db: Session,
    campaign: Campaign,
    skill_by_name: dict[str, Skill],
    material_by_title: dict[str, StudyMaterial],
    week_by_no: dict[int, StudyPlanWeek],
    sessions: list[StudyPlanSession],
) -> None:
    for session in sessions:
        existing = (
            db.query(Quest)
            .filter(Quest.study_plan_session_id == session.id, Quest.session_type == "Main Quest")
            .first()
        )
        if existing:
            continue
        primary_skill_name = infer_primary_skill(session.skill_summary)
        primary_skill = skill_by_name[primary_skill_name]
        material_names = normalize_material_names(session.material_summary)
        primary_material = material_by_title.get(material_names[0]) if material_names else None
        session_week = week_by_no.get(session.week_no)
        db.add(
            Quest(
                quest_date=session.study_date,
                week_no=session.week_no,
                stage=session_week.phase.title if session_week else phase_label(phase_for_week(session.week_no)),
                title=f"Main Quest W{session.week_no:02d} - {session.session_label}",
                skill_id=primary_skill.id,
                source=session.material_summary,
                details=session.task_detail,
                xp=infer_main_quest_xp(session.session_no, session.skill_summary),
                session_type="Main Quest",
                campaign_id=campaign.id,
                phase_id=session.phase_id,
                study_plan_week_id=session.study_plan_week_id,
                study_plan_session_id=session.id,
                template_id=None,
                material_id=primary_material.id if primary_material else None,
                status="pending",
                quest_role="main",
                difficulty="normal",
                base_xp=infer_main_quest_xp(session.session_no, session.skill_summary),
                earned_xp=0,
                completion_note=session.deliverable,
            )
        )


def backfill_quest_phase_and_material(
    db: Session,
    campaign: Campaign,
    phase_by_code: dict[str, RoadmapPhase],
) -> None:
    quests = db.query(Quest).filter(Quest.campaign_id == campaign.id).all()
    for quest in quests:
        phase_index = phase_for_week(quest.week_no)
        phase = phase_by_code.get(f"phase-{phase_index}")
        if phase and not quest.phase_id:
            quest.phase_id = phase.id
        if not quest.material_id and quest.template_id:
            template = db.query(QuestTemplate).filter(QuestTemplate.id == quest.template_id).first()
            if template and template.material_id:
                quest.material_id = template.material_id


def ensure_weekly_missions(db: Session, campaign: Campaign) -> None:
    if db.query(WeeklyMission).filter(WeeklyMission.campaign_id == campaign.id).count() > 0:
        return

    current_start = onboarding_week_start(campaign.start_date)
    week_count = ((campaign.end_date - current_start).days // 7) + 1
    for index in range(week_count):
        week_start = current_start + timedelta(days=index * 7)
        week_end = week_start + timedelta(days=6)
        relative_week = max(1, ((week_start - campaign.start_date).days // 7) + 1)
        phase_index = phase_for_week(relative_week)
        patterns = weekly_mission_patterns(phase_index)
        pattern = patterns[index % len(patterns)]
        if index == 0:
            mission = WeeklyMission(
                campaign_id=campaign.id,
                week_start=week_start,
                week_end=week_end,
                phase=phase_label(phase_index),
                pattern_code="onboarding",
                title="Onboarding Week",
                description="Lam quen dashboard, check-in va quest loop nhe hon.",
                reward_xp=25,
                status="active",
            )
            db.add(mission)
            db.flush()
            for description, target_count in [
                ("Hoan thanh 2 daily quest bat ky", 2),
                ("Tao 1 check-in va 1 note ve weakness", 2),
            ]:
                db.add(
                    WeeklyMissionItem(
                        weekly_mission_id=mission.id,
                        description=description,
                        target_count=target_count,
                        current_count=0,
                        status="pending",
                    )
                )
            continue

        mission = WeeklyMission(
            campaign_id=campaign.id,
            week_start=week_start,
            week_end=week_end,
            phase=phase_label(phase_index),
            pattern_code=pattern["pattern_code"],
            title=pattern["title"],
            description=pattern["description"],
            reward_xp=pattern["reward_xp"],
            status="active",
        )
        db.add(mission)
        db.flush()
        for description, target_count in pattern["items"]:
            db.add(
                WeeklyMissionItem(
                    weekly_mission_id=mission.id,
                    description=description,
                    target_count=target_count,
                    current_count=0,
                    status="pending",
                )
            )


def ensure_bosses(db: Session, campaign: Campaign, badges: list[Badge]) -> None:
    if db.query(BossBattle).filter(BossBattle.campaign_id == campaign.id).count() > 0:
        return

    badge_cycle = [badge.id for badge in badges[: min(len(badges), 10)]]
    for month_index in range(1, 19):
        battle_date = campaign.start_date + timedelta(days=(month_index * 30) - 1)
        relative_week = max(1, ((battle_date - campaign.start_date).days // 7) + 1)
        phase_name = phase_label(phase_for_week(relative_week))
        db.add(
            BossBattle(
                stage=phase_name,
                battle_date=battle_date,
                title=month_boss_title(month_index),
                source="Dashboard roadmap",
                goal="Complete checkpoint test, record score, and review errors before moving on.",
                status="Locked",
                campaign_id=campaign.id,
                month_index=month_index,
                reward_xp=100 if month_index in {6, 12, 18} else 60,
                badge_id=badge_cycle[(month_index - 1) % len(badge_cycle)] if badge_cycle else None,
                result_status="locked",
                result_note="",
                practice_suggestion="Review weakest skill before this checkpoint.",
            )
        )


def ensure_test_records(db: Session, player: Player) -> None:
    if db.query(TestRecord).filter(TestRecord.player_id == player.id).count() > 0:
        return

    records = [
        TestRecord(
            player_id=player.id,
            test_type="TOEIC",
            test_date=date(2026, 1, 15),
            listening_score="395",
            reading_score="270",
            speaking_score="95",
            writing_score="120",
            note="Initial known benchmark from project context.",
        ),
        TestRecord(
            player_id=player.id,
            test_type="Aptis",
            test_date=date(2026, 2, 20),
            overall_score="B1",
            listening_score="B2",
            reading_score="B1",
            speaking_score="B1",
            writing_score="B1",
            cefr_level="B1",
            note="Initial Aptis profile from project context.",
        ),
    ]
    for record in records:
        db.add(record)
    db.flush()
    for record in records:
        create_rank_suggestions_for_test(db, record)


def seed_database(db: Session, start_date: date) -> None:
    player = ensure_player(db, start_date)
    campaign = ensure_campaign(db, player, start_date)
    skill_by_name = ensure_skills(db)
    badges = ensure_badges(db)
    material_by_title = ensure_materials(db)
    phase_by_code = ensure_roadmap_phases(db, campaign)
    ensure_phase_materials(db, phase_by_code, material_by_title)
    week_by_no, study_plan_sessions = ensure_study_plan(db, campaign, phase_by_code)
    template_by_title = ensure_templates(db, skill_by_name, phase_by_code, material_by_title)
    ensure_quest_instances(db, campaign, skill_by_name, template_by_title, phase_by_code)
    ensure_main_quest_instances(db, campaign, skill_by_name, material_by_title, week_by_no, study_plan_sessions)
    backfill_quest_phase_and_material(db, campaign, phase_by_code)
    ensure_weekly_missions(db, campaign)
    ensure_bosses(db, campaign, badges)
    ensure_test_records(db, player)
    db.commit()
