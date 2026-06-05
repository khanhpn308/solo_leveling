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
    ("Listening", "🎧", "Current strength; still needs work on Sections 3-4, distractors, and spelling."),
    ("Reading", "📖", "Main weakness: limited vocabulary and limited confidence with long-sentence analysis."),
    ("Writing", "✍️", "Needs steady writing practice and review against the 4 IELTS criteria."),
    ("Speaking", "🗣️", "Needs regular recording practice to improve fluency, pronunciation, and Part 3 reasoning."),
    ("Vocabulary", "🧠", "Study by topic, paraphrase pairs, and personalized example sentences."),
    ("Collocation", "🔗", "Used to make speaking and writing sound more natural and reduce word-combination errors."),
    ("Grammar", "⚙️", "Strengthen tenses, relative clauses, passive voice, conditionals, and complex sentences."),
]

BADGES = [
    ("7-Day Streak", "🔥", "Study continuously for 7 days."),
    ("Vocabulary Hunter", "🧠", "Reach 300 Vocabulary XP."),
    ("Grammar Fixer", "⚙️", "Reach 300 Grammar XP."),
    ("Listening Warrior", "🎧", "Reach 500 Listening XP."),
    ("Reading Decoder", "📖", "Reach 500 Reading XP."),
    ("Writing Starter", "✍️", "Reach 300 Writing XP."),
    ("Speaking Brave Mode", "🗣️", "Reach 300 Speaking XP."),
    ("Error Killer", "⚔️", "Log and fix many fully understood mistakes."),
    ("Band 6 Challenger", "🥈", "Clear the mid-roadmap checkpoint."),
    ("Band 7 Candidate", "🏆", "Finish the final mock-test sequence."),
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
        "title": "Months 1-3",
        "month_start": 1,
        "month_end": 3,
        "week_start": 1,
        "week_end": 13,
        "objective": "Build from B1 toward IELTS 5.0-5.5; strengthen grammar, vocabulary, long sentences, and core Listening/Reading skills.",
        "focus_skills": "Reading,Vocabulary,Grammar,Listening",
    },
    {
        "phase_order": 2,
        "code": "phase-2",
        "title": "Months 4-6",
        "month_start": 4,
        "month_end": 6,
        "week_start": 14,
        "week_end": 26,
        "objective": "Stabilize at IELTS 5.5 and begin clear IELTS strategies for all four skills.",
        "focus_skills": "Reading,Listening,Writing,Speaking",
    },
    {
        "phase_order": 3,
        "code": "phase-3",
        "title": "Months 7-9",
        "month_start": 7,
        "month_end": 9,
        "week_start": 27,
        "week_end": 39,
        "objective": "Move toward IELTS 6.0-6.5; switch to 6.5-7.5 materials and practice Writing/Speaking consistently.",
        "focus_skills": "Writing,Speaking,Reading,Vocabulary",
    },
    {
        "phase_order": 4,
        "code": "phase-4",
        "title": "Months 10-12",
        "month_start": 10,
        "month_end": 12,
        "week_start": 40,
        "week_end": 52,
        "objective": "Consolidate IELTS 6.5; start using Cambridge IELTS 17 by section and increase pace.",
        "focus_skills": "Reading,Listening,Writing,Collocation",
    },
    {
        "phase_order": 5,
        "code": "phase-5",
        "title": "Months 13-18",
        "month_start": 13,
        "month_end": 18,
        "week_start": 53,
        "week_end": 78,
        "objective": "Run mock tests, perform deep error review, and sharpen exam tactics for IELTS 7.0-7.5.",
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
        "notes": "Use as an orientation guide and practice-test source, not as a standalone course.",
    },
    {
        "title": "Complete IELTS Band 5.0-6.5",
        "category": "coursebook",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 2,
        "notes": "Primary backbone for the foundation stage.",
    },
    {
        "title": "Complete IELTS Bands 6.5-7.5",
        "category": "coursebook",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 3,
        "recommended_phase_end": 4,
        "notes": "Raise target band and topic difficulty.",
    },
    {
        "title": "English Grammar in Use",
        "category": "grammar",
        "format": "book",
        "skill_tags": "Grammar,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 2,
        "notes": "Strengthen core grammar and basic recurring errors.",
    },
    {
        "title": "Cambridge Grammar for IELTS",
        "category": "grammar",
        "format": "book",
        "skill_tags": "Grammar,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 5,
        "notes": "IELTS-specific grammar with focus on weak recurring errors.",
    },
    {
        "title": "English Vocabulary in Use Upper-Intermediate",
        "category": "vocabulary",
        "format": "book",
        "skill_tags": "Vocabulary,Reading,Writing",
        "recommended_phase_start": 1,
        "recommended_phase_end": 2,
        "notes": "Foundation vocabulary at B2 level.",
    },
    {
        "title": "IELTS Vocabulary for Bands 6.5 and above",
        "category": "vocabulary",
        "format": "book",
        "skill_tags": "Vocabulary,Reading,Writing",
        "recommended_phase_start": 3,
        "recommended_phase_end": 5,
        "notes": "Higher-band IELTS vocabulary.",
    },
    {
        "title": "Cambridge Academic Vocabulary in Use",
        "category": "vocabulary",
        "format": "book",
        "skill_tags": "Vocabulary,Reading,Writing",
        "recommended_phase_start": 3,
        "recommended_phase_end": 5,
        "notes": "Academic vocabulary for Reading and Writing.",
    },
    {
        "title": "English Collocations in Use Intermediate",
        "category": "collocation",
        "format": "book",
        "skill_tags": "Collocation,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 3,
        "notes": "Help speaking and writing sound more natural.",
    },
    {
        "title": "English Collocations in Use Advanced",
        "category": "collocation",
        "format": "book",
        "skill_tags": "Collocation,Writing,Speaking",
        "recommended_phase_start": 4,
        "recommended_phase_end": 5,
        "notes": "Raise output quality in later phases.",
    },
    {
        "title": "IELTS Advantage Reading Skills",
        "category": "reading",
        "format": "book",
        "skill_tags": "Reading,Vocabulary",
        "recommended_phase_start": 2,
        "recommended_phase_end": 5,
        "notes": "Strategies for each Reading question type.",
    },
    {
        "title": "IELTS Advantage - Speaking and Listening Skills",
        "category": "listening_speaking",
        "format": "book",
        "skill_tags": "Listening,Speaking",
        "recommended_phase_start": 2,
        "recommended_phase_end": 5,
        "notes": "Combine audio, transcript review, and recording practice.",
    },
    {
        "title": "IELTS Advantage Writing Skills",
        "category": "writing",
        "format": "book",
        "skill_tags": "Writing,Vocabulary,Grammar",
        "recommended_phase_start": 2,
        "recommended_phase_end": 5,
        "notes": "Writing Task 1/2 practice; get external correction when possible.",
    },
    {
        "title": "Cambridge IELTS 17",
        "category": "mock",
        "format": "book",
        "skill_tags": "Listening,Reading,Writing,Speaking",
        "recommended_phase_start": 4,
        "recommended_phase_end": 5,
        "notes": "Realistic mock practice; do not use too early.",
    },
    {
        "title": "Any current notebook",
        "category": "review",
        "format": "notes",
        "skill_tags": "Vocabulary,Grammar,Reading,Listening,Writing,Speaking",
        "recommended_phase_start": 1,
        "recommended_phase_end": 5,
        "notes": "Mini review, flashcards, transcript notes, and error recall.",
    },
]

PHASE_MATERIAL_PLAN = {
    1: [
        ("The Official Cambridge Guide to IELTS", "orientation", "1-2 sessions/week when needed", "Use to understand format and basic tactics."),
        ("Complete IELTS Band 5.0-6.5", "core", "1 unit every 1-2 weeks", "Primary foundation-stage backbone."),
        ("English Grammar in Use", "support", "2-3 units/week", "Focus on common errors."),
        ("Cambridge Grammar for IELTS", "support", "1 unit/week", "Apply grammar in Writing and Speaking."),
        ("English Vocabulary in Use Upper-Intermediate", "support", "2 units/week", "Record vocabulary in chunks and write example sentences."),
        ("English Collocations in Use Intermediate", "support", "1-2 units/week", "Start with Study, Work, and Academic units."),
    ],
    2: [
        ("Complete IELTS Band 5.0-6.5", "core", "1 unit every 1-2 weeks", "Continue strengthening IELTS foundations."),
        ("The Official Cambridge Guide to IELTS", "orientation", "1-2 sessions/week when needed", "Use to lock in the format of each task type."),
        ("Cambridge Grammar for IELTS", "support", "1 unit/week", "Continue IELTS grammar work."),
        ("English Vocabulary in Use Upper-Intermediate", "support", "2 units/week", "Maintain foundation vocabulary."),
        ("English Collocations in Use Intermediate", "support", "1-2 units/week", "Maintain collocation output."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 session/week", "Review fewer tasks more deeply."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 task/week", "Start task-focused writing."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 session/week", "Combine speaking recordings with transcript review."),
    ],
    3: [
        ("Complete IELTS Bands 6.5-7.5", "core", "1 unit every 1-2 weeks", "Move into harder topics."),
        ("Cambridge Grammar for IELTS", "support", "review weak areas", "Only revisit currently weak units."),
        ("IELTS Vocabulary for Bands 6.5 and above", "support", "1-2 units/week", "Prioritize common test topics."),
        ("Cambridge Academic Vocabulary in Use", "support", "1-2 units/week", "Raise academic range."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 session/week", "Higher-level Reading strategy work."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 task/week", "Increase focus on Task 2."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 session/week", "Push Part 2/3 and fluency."),
    ],
    4: [
        ("Complete IELTS Bands 6.5-7.5", "core", "1 unit every 1-2 weeks", "Consolidate 6.5-level foundations."),
        ("The Official Cambridge Guide to IELTS", "orientation", "1 session/week when needed", "Review guidance and task types."),
        ("Cambridge Grammar for IELTS", "support", "review weak areas", "Only fix recurring errors."),
        ("Cambridge Academic Vocabulary in Use", "support", "1-2 units/week", "Academic vocabulary for essays and reading."),
        ("English Collocations in Use Advanced", "support", "1 unit/week", "Raise output quality."),
        ("Cambridge IELTS 17", "mock", "sectional -> full test", "Use carefully to preserve mock material."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 session/week", "Detailed review of Reading task types."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 task/week", "Review task strategy."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 session/week", "Speaking and Listening review."),
    ],
    5: [
        ("Cambridge IELTS 17", "mock", "ramp toward full tests", "Run mocks and review after each one."),
        ("The Official Cambridge Guide to IELTS", "orientation", "when needed", "Finalize real-exam checklist."),
        ("Cambridge Grammar for IELTS", "support", "error-fix only", "No more broad study here."),
        ("IELTS Vocabulary for Bands 6.5 and above", "support", "1-2 units/week", "Review target-topic vocabulary when needed."),
        ("Cambridge Academic Vocabulary in Use", "support", "1-2 units/week", "Academic essay and reading vocabulary."),
        ("English Collocations in Use Advanced", "support", "1 unit/week", "Make output sound more natural."),
        ("IELTS Advantage Writing Skills", "skill_focus", "1 task/week", "Weekly writing correction."),
        ("IELTS Advantage - Speaking and Listening Skills", "skill_focus", "1 session/week", "Speaking recording and review."),
        ("IELTS Advantage Reading Skills", "skill_focus", "1 session/week", "Reading strategy and error review."),
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
        1: "Months 1-3",
        2: "Months 4-6",
        3: "Months 7-9",
        4: "Months 10-12",
        5: "Months 13-18",
    }
    return mapping.get(phase_index, "Months 13-18")


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
            "description": "Complete 1 reading passage, mark it, and analyze 3-5 long sentences.",
            "skill": "Reading",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage Reading Skills",
            "base_xp": 25,
            "difficulty": "normal",
            "difficulty_description": "Detailed reading and analysis.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Reading Skills",
            "resource_category": "book",
            "resource_note": "Focus on paraphrase recognition and long-sentence parsing.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Listening Core Sweep",
            "description": "Complete 1 listening task, review the transcript, and note distractors and spelling traps.",
            "skill": "Listening",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage - Speaking and Listening Skills",
            "base_xp": 20,
            "difficulty": "normal",
            "difficulty_description": "Task completion plus transcript review.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Speaking and Listening Skills",
            "resource_category": "book",
            "resource_note": "Improve Section 3-4 quality.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Writing Core Draft",
            "description": "Write 1 paragraph or short response and self-review it against IELTS criteria.",
            "skill": "Writing",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage Writing Skills",
            "base_xp": 25,
            "difficulty": "normal",
            "difficulty_description": "Drafting plus self-review.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Writing Skills",
            "resource_category": "book",
            "resource_note": "Task 1 or Task 2 depending on phase.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Speaking Core Record",
            "description": "Record Speaking Part 1/2/3, listen back, and note 3 points to improve.",
            "skill": "Speaking",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage - Speaking and Listening Skills",
            "base_xp": 25,
            "difficulty": "normal",
            "difficulty_description": "Recording plus self-evaluation.",
            "quest_role": "core",
            "resource_name": "IELTS Advantage Speaking and Listening Skills",
            "resource_category": "book",
            "resource_note": "Focus on fluency and reasoning.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Vocabulary Support Pack",
            "description": "Learn 10 new words, 3 collocations, and 2 paraphrase pairs.",
            "skill": "Vocabulary",
            "phase_code": "phase-1",
            "material_title": "English Vocabulary in Use Upper-Intermediate",
            "base_xp": 10,
            "difficulty": "easy",
            "difficulty_description": "Short and easy to sustain.",
            "quest_role": "support",
            "resource_name": "English Vocabulary in Use Upper-Intermediate",
            "resource_category": "book",
            "resource_note": "Use in phases 1-2, then revisit later.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Grammar Support Forge",
            "description": "Study 1 grammar point, do a short exercise, and write 3 application sentences.",
            "skill": "Grammar",
            "phase_code": "phase-1",
            "material_title": "Cambridge Grammar for IELTS",
            "base_xp": 15,
            "difficulty": "easy",
            "difficulty_description": "Guided review.",
            "quest_role": "support",
            "resource_name": "Cambridge Grammar for IELTS",
            "resource_category": "book",
            "resource_note": "Return to related units when errors appear.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Collocation Support Pack",
            "description": "Study 5 collocations and write 3 sentences with personal context.",
            "skill": "Collocation",
            "phase_code": "phase-1",
            "material_title": "English Collocations in Use Intermediate",
            "base_xp": 10,
            "difficulty": "easy",
            "difficulty_description": "Quick support loop.",
            "quest_role": "support",
            "resource_name": "English Collocations in Use Intermediate",
            "resource_category": "book",
            "resource_note": "Switch to Advanced in later phases.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Mini Review Burst",
            "description": "Quick 5-10 minute review: flashcards, transcript notes, or error recall.",
            "skill": "Vocabulary",
            "phase_code": "phase-1",
            "material_title": "Any current notebook",
            "base_xp": 5,
            "difficulty": "easy",
            "difficulty_description": "Very light to protect the streak.",
            "quest_role": "mini",
            "resource_name": "Any current notebook",
            "resource_category": "review",
            "resource_note": "Mini quest can follow the day's main skill.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
        },
        {
            "title": "Mock Reading Raid",
            "description": "Complete a timed Reading set and summarize mistakes; intended for phases 4-5.",
            "skill": "Reading",
            "phase_code": "phase-4",
            "material_title": "Cambridge IELTS 17",
            "base_xp": 40,
            "difficulty": "hard",
            "difficulty_description": "Timed practice with post-task analysis.",
            "quest_role": "core",
            "resource_name": "Cambridge IELTS 17",
            "resource_category": "mock",
            "resource_note": "Only appears in phases 4-5.",
            "allowed_phase_start": 4,
            "allowed_phase_end": 5,
        },
        {
            "title": "Mock Listening Raid",
            "description": "Complete a timed Listening set and review the transcript carefully; intended for phases 4-5.",
            "skill": "Listening",
            "phase_code": "phase-4",
            "material_title": "Cambridge IELTS 17",
            "base_xp": 40,
            "difficulty": "hard",
            "difficulty_description": "Timed practice with transcript review after the set.",
            "quest_role": "core",
            "resource_name": "Cambridge IELTS 17",
            "resource_category": "mock",
            "resource_note": "Only appears in phases 4-5.",
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
            "description": "Keep a steady rhythm across the 4 main skills and the support loop.",
            "reward_xp": 40,
            "items": [
                ("Complete at least 3 core quests", 3),
                ("Have at least 4 check-in or mini-review days", 4),
                ("Add at least 2 notes to Error Log/Writing/Speaking trackers", 2),
            ],
        },
        {
            "pattern_code": f"{phase_index}-reading-focus",
            "title": f"Weekly Mission - {phase_name} Reading Focus",
            "description": "Focus on raising Reading and Vocabulary this week.",
            "reward_xp": 45,
            "items": [
                ("Complete 2 Reading core quests", 2),
                ("Complete 3 Vocabulary/Collocation support quests", 3),
                ("Analyze 5 long sentences or difficult paraphrases", 5),
            ],
        },
        {
            "pattern_code": f"{phase_index}-output-focus",
            "title": f"Weekly Mission - {phase_name} Output Focus",
            "description": "Increase Writing and Speaking output to reduce avoidance.",
            "reward_xp": 45,
            "items": [
                ("Complete 2 Writing/Speaking core quests", 2),
                ("Self-review at least 2 recurring weak points", 2),
                ("Complete 1 mini review tied to an output skill", 1),
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
        else:
            previous_weak_point = skill.weak_point
            skill.icon = icon
            skill.weak_point = weak_point
            if not (skill.user_weakness_note or "").strip() or skill.user_weakness_note == previous_weak_point:
                skill.user_weakness_note = weak_point
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
        else:
            badge.icon = icon
            badge.description = description
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
        else:
            material.category = item["category"]
            material.format = item["format"]
            material.skill_tags = item["skill_tags"]
            material.recommended_phase_start = item["recommended_phase_start"]
            material.recommended_phase_end = item["recommended_phase_end"]
            material.notes = item["notes"]
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
        else:
            phase.title = item["title"]
            phase.month_start = item["month_start"]
            phase.month_end = item["month_end"]
            phase.week_start = item["week_start"]
            phase.week_end = item["week_end"]
            phase.objective = item["objective"]
            phase.focus_skills = item["focus_skills"]
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
                existing.usage_purpose = usage_purpose
                existing.usage_frequency = usage_frequency
                existing.notes = notes
                existing.display_order = display_order
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
            template.description = item["description"]
            template.primary_skill_id = skill_by_name[item["skill"]].id
            template.phase_id = phase_by_code[item["phase_code"]].id
            template.material_id = material_by_title[item["material_title"]].id
            template.base_xp = item["base_xp"]
            template.difficulty = item["difficulty"]
            template.difficulty_description = item["difficulty_description"]
            template.quest_role = item["quest_role"]
            template.resource_name = item["resource_name"]
            template.resource_category = item["resource_category"]
            template.resource_note = item["resource_note"]
            template.allowed_phase_start = item["allowed_phase_start"]
            template.allowed_phase_end = item["allowed_phase_end"]
            template.is_active = True
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
                    existing = (
                        db.query(Quest)
                        .filter(
                            Quest.campaign_id == campaign.id,
                            Quest.quest_date == quest_date,
                            Quest.quest_role == template.quest_role,
                            Quest.session_type == "Daily Quest",
                        )
                        .first()
                    )
                    if existing:
                        skill = next(skill for skill in skill_by_name.values() if skill.id == template.primary_skill_id)
                        phase = phase_by_code[f"phase-{phase_index}"]
                        existing.stage = phase_name
                        existing.title = template.title
                        existing.skill_id = skill.id
                        existing.source = template.resource_name
                        existing.details = template.description
                        existing.phase_id = phase.id
                        existing.template_id = template.id
                        existing.material_id = template.material_id
                        existing.difficulty = template.difficulty
                        existing.base_xp = template.base_xp
                        existing.xp = template.base_xp
                        existing.daily_slot_code = template.quest_role
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
                        daily_slot_code=template.quest_role,
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
            session_week = week_by_no.get(session.week_no)
            material_names = normalize_material_names(session.material_summary)
            primary_material = material_by_title.get(material_names[0]) if material_names else None
            existing.stage = session_week.phase.title if session_week else phase_label(phase_for_week(session.week_no))
            existing.title = f"Main Quest W{session.week_no:02d} - {session.session_label}"
            existing.source = session.material_summary
            existing.details = session.task_detail
            existing.phase_id = session.phase_id
            existing.material_id = primary_material.id if primary_material else None
            existing.base_xp = infer_main_quest_xp(session.session_no, session.skill_summary)
            existing.xp = infer_main_quest_xp(session.session_no, session.skill_summary)
            existing.completion_note = session.deliverable
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
            item_specs = [
                ("Complete any 2 daily quests", 2),
                ("Create 1 check-in and 1 weakness note", 2),
            ]
            mission = (
                db.query(WeeklyMission)
                .filter(WeeklyMission.campaign_id == campaign.id, WeeklyMission.week_start == week_start)
                .first()
            )
            if not mission:
                mission = WeeklyMission(
                    campaign_id=campaign.id,
                    week_start=week_start,
                    week_end=week_end,
                    phase=phase_label(phase_index),
                    pattern_code="onboarding",
                    title="Onboarding Week",
                    description="Get used to the dashboard, check-ins, and a lighter quest loop.",
                    reward_xp=25,
                    status="active",
                )
                db.add(mission)
                db.flush()
            else:
                mission.week_end = week_end
                mission.phase = phase_label(phase_index)
                mission.pattern_code = "onboarding"
                mission.title = "Onboarding Week"
                mission.description = "Get used to the dashboard, check-ins, and a lighter quest loop."
                mission.reward_xp = 25
            existing_items = (
                db.query(WeeklyMissionItem)
                .filter(WeeklyMissionItem.weekly_mission_id == mission.id)
                .order_by(WeeklyMissionItem.id)
                .all()
            )
            for position, (description, target_count) in enumerate(item_specs):
                if position < len(existing_items):
                    existing_items[position].description = description
                    existing_items[position].target_count = target_count
                else:
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

        mission = (
            db.query(WeeklyMission)
            .filter(WeeklyMission.campaign_id == campaign.id, WeeklyMission.week_start == week_start)
            .first()
        )
        if not mission:
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
        else:
            mission.week_end = week_end
            mission.phase = phase_label(phase_index)
            mission.pattern_code = pattern["pattern_code"]
            mission.title = pattern["title"]
            mission.description = pattern["description"]
            mission.reward_xp = pattern["reward_xp"]
        existing_items = (
            db.query(WeeklyMissionItem)
            .filter(WeeklyMissionItem.weekly_mission_id == mission.id)
            .order_by(WeeklyMissionItem.id)
            .all()
        )
        for position, (description, target_count) in enumerate(pattern["items"]):
            if position < len(existing_items):
                existing_items[position].description = description
                existing_items[position].target_count = target_count
            else:
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
    badge_cycle = [badge.id for badge in badges[: min(len(badges), 10)]]
    for month_index in range(1, 19):
        battle_date = campaign.start_date + timedelta(days=(month_index * 30) - 1)
        relative_week = max(1, ((battle_date - campaign.start_date).days // 7) + 1)
        phase_name = phase_label(phase_for_week(relative_week))
        boss = (
            db.query(BossBattle)
            .filter(BossBattle.campaign_id == campaign.id, BossBattle.month_index == month_index)
            .first()
        )
        if not boss:
            boss = BossBattle(
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
            db.add(boss)
        else:
            boss.stage = phase_name
            boss.battle_date = battle_date
            boss.title = month_boss_title(month_index)
            boss.source = "Dashboard roadmap"
            boss.goal = "Complete checkpoint test, record score, and review errors before moving on."
            boss.reward_xp = 100 if month_index in {6, 12, 18} else 60
            boss.badge_id = badge_cycle[(month_index - 1) % len(badge_cycle)] if badge_cycle else None
            boss.practice_suggestion = "Review weakest skill before this checkpoint."


def ensure_test_records(db: Session, player: Player, campaign: Campaign) -> None:
    if db.query(TestRecord).filter(TestRecord.player_id == player.id).count() > 0:
        return

    records = [
        TestRecord(
            player_id=player.id,
            campaign_id=campaign.id,
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
            campaign_id=campaign.id,
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
    ensure_test_records(db, player, campaign)
    db.commit()
