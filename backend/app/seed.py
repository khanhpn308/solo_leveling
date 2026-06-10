from __future__ import annotations

import os
from datetime import date, timedelta, datetime
from pathlib import Path
import re

from sqlalchemy.orm import Session

from .models import (
    Account,
    AccountPreference,
    Badge,
    BossBattle,
    Campaign,
    CampaignSetting,
    CampaignTemplate,
    CampaignTemplateSkillQuota,
    CampaignSkillQuestQuota,
    CertificateRecord,
    PlayerLearningProfile,
    PhaseMaterial,
    Player,
    Quest,
    QuestTemplate,
    RankExamPool,
    RankExamVersion,
    RankExamQuestion,
    RoadmapPhase,
    Skill,
    StudyPlanSession,
    StudyPlanWeek,
    StudyMaterial,
    TestRecord,
    VocabularySetting,
    WeeklyMission,
    WeeklyMissionItem,
    CollocationCollection,
    CollocationSection,
    CollocationTopic,
    CollocationItem,
    CampaignCollocationLink,
    RankXpThreshold,
    QuestXpPolicy,
    WeeklyMissionXpPolicy,
    MainQuestXpPolicy,
)
from .auth_utils import hash_password
from .services import create_rank_suggestions_for_test, link_collection_to_campaign

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
    ("Memory Streak Badge I", "🌟", "Clear the Vocabulary Monthly Checkpoint (Boss 02)."),
    ("Lexical Awakener", "🌌", "Clear the final Lexical Awakening Boss Battle (Boss 04)."),
    ("Writing Lexical Buff", "📜", "Clear the Collocation Hunter Boss Battle (Boss 03)."),
]


MATERIAL_ANCHOR_DATE = date(2026, 6, 4)  # Week 1 Session 1 in material.md (Thursday)


def rebase_material_date(material_date: date, campaign_start: date) -> date:
    return campaign_start + (material_date - MATERIAL_ANCHOR_DATE)


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
            "title": "Reading Daily",
            "description": "Complete 1 reading passage, mark it, and analyze 3-5 long sentences.",
            "skill": "Reading",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage Reading Skills",
            "base_xp": 10,
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
            "title": "Listening Daily",
            "description": "Complete 1 listening task, review the transcript, and note distractors and spelling traps.",
            "skill": "Listening",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage - Speaking and Listening Skills",
            "base_xp": 10,
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
            "title": "Writing Daily",
            "description": "Write 1 paragraph or short response and self-review it against IELTS criteria.",
            "skill": "Writing",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage Writing Skills",
            "base_xp": 12,
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
            "title": "Speaking Daily",
            "description": "Record Speaking Part 1/2/3, listen back, and note 3 points to improve.",
            "skill": "Speaking",
            "phase_code": "phase-2",
            "material_title": "IELTS Advantage - Speaking and Listening Skills",
            "base_xp": 12,
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
            "title": "Flashcard Gate",
            "description": "Review 20 flashcards using the spaced-repetition gate and mark 5 as mastered.",
            "skill": "Vocabulary",
            "phase_code": "phase-1",
            "material_title": "Any current notebook",
            "base_xp": 4,
            "difficulty": "easy",
            "difficulty_description": "Flashcard review gate.",
            "quest_role": "support",
            "resource_name": "Any current notebook",
            "resource_category": "review",
            "resource_note": "Spaced repetition session.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
            "quest_track_code": "vocab_memory",
            "activity_type": "flashcard_review",
            "target_metric": "mastered_count",
            "target_count": 5,
            "completion_payload": "{\"mastered\":5}",
        },
        {
            "title": "Codex Entry",
            "description": "Create 1 codex entry: add a new word with meaning, example, and one collocation.",
            "skill": "Vocabulary",
            "phase_code": "phase-1",
            "material_title": "Any current notebook",
            "base_xp": 5,
            "difficulty": "easy",
            "difficulty_description": "Create and save a codex entry.",
            "quest_role": "support",
            "resource_name": "Any current notebook",
            "resource_category": "review",
            "resource_note": "Personalized vocabulary entry.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
            "quest_track_code": "vocab_codex",
            "activity_type": "codex_create",
            "target_metric": "entries_created",
            "target_count": 1,
            "completion_payload": "{\"entries\":1}",
        },
        {
            "title": "Collocation Forge",
            "description": "Practice 5 collocations in sentences and submit 3 valid personal examples.",
            "skill": "Collocation",
            "phase_code": "phase-1",
            "material_title": "English Collocations in Use Intermediate",
            "base_xp": 5,
            "difficulty": "easy",
            "difficulty_description": "Produce collocation examples.",
            "quest_role": "support",
            "resource_name": "English Collocations in Use Intermediate",
            "resource_category": "book",
            "resource_note": "Write personal-context sentences.",
            "allowed_phase_start": 1,
            "allowed_phase_end": 5,
            "quest_track_code": "vocab_collocation",
            "activity_type": "collocation_practice",
            "target_metric": "examples_submitted",
            "target_count": 3,
            "completion_payload": "{\"examples\":3}",
        },
        {
            "title": "Grammar Review",
            "description": "Study 1 grammar point, do a short exercise, and write 3 application sentences.",
            "skill": "Grammar",
            "phase_code": "phase-1",
            "material_title": "Cambridge Grammar for IELTS",
            "base_xp": 5,
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
            "title": "Grammar Exercise",
            "description": "Study 1 grammar point, do a short exercise, and write 3 application sentences.",
            "skill": "Grammar",
            "phase_code": "phase-1",
            "material_title": "Cambridge Grammar for IELTS",
            "base_xp": 7,
            "difficulty": "easy",
            "difficulty_description": "Guided review.",
            "quest_role": "support",
            "resource_name": "Cambridge Grammar for IELTS",
            "resource_category": "book",
            "resource_note": "Return to related units when errors appear.",
            "allowed_phase_start": 1,
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


def infer_primary_skill(skill_summary: str, task_detail: str = "") -> str:
    ordered = ["Listening", "Reading", "Writing", "Speaking", "Vocabulary", "Collocation", "Grammar"]
    for skill_name in ordered:
        if skill_name.lower() in skill_summary.lower():
            return skill_name
    for skill_name in ordered:
        if skill_name.lower() in task_detail.lower():
            return skill_name
    return "Reading"


def infer_main_quest_tier(session_no: int, skill_summary: str, task_detail: str = "") -> str:
    if session_no == 3:
        return "heavy_output"
    if session_no in (1, 2):
        return "standard"
    if session_no == 4:
        combined = (skill_summary + " " + task_detail).lower()
        if "mock" in combined or "simulation" in combined or "sectional test" in combined:
            return "mock"
        return "review_error_logging"
    return "review_error_logging"


def infer_main_quest_xp(session_no: int, skill_summary: str, task_detail: str = "", db: Session | None = None) -> int:
    if db is not None:
        try:
            tier = infer_main_quest_tier(session_no, skill_summary, task_detail)
            policy = db.query(MainQuestXpPolicy).filter_by(tier_code=tier).first()
            if policy:
                return policy.xp_reward
        except Exception:
            pass

    if session_no == 3:
        return 45
    if session_no in (1, 2):
        return 35
    if session_no == 4:
        combined = (skill_summary + " " + task_detail).lower()
        if "mock" in combined or "simulation" in combined or "sectional test" in combined:
            return 60
        return 25
    return 25


def map_template_to_activity_code(title: str) -> str:
    title_lower = title.lower()
    if "reading daily" in title_lower: return "reading"
    if "listening daily" in title_lower: return "listening"
    if "writing daily" in title_lower: return "writing"
    if "speaking daily" in title_lower: return "speaking"
    if "flashcard gate" in title_lower: return "vocab_flashcard"
    if "codex entry" in title_lower: return "vocab_codex"
    if "collocation forge" in title_lower: return "vocab_collocation"
    if "grammar review" in title_lower: return "grammar_review"
    if "grammar exercise" in title_lower: return "grammar_exercise"
    return title_lower.replace(" ", "_")


def map_weekly_pattern_to_mission_type(pattern_code: str) -> str:
    pattern_lower = pattern_code.lower()
    if "balanced" in pattern_lower: return "listening_weekly"
    if "reading" in pattern_lower: return "reading_weekly"
    if "vocabulary" in pattern_lower or "vocab" in pattern_lower: return "vocab_weekly"
    if "grammar" in pattern_lower: return "grammar_weekly"
    if "speaking" in pattern_lower: return "speaking_weekly"
    if "output" in pattern_lower: return "writing_weekly"
    if "onboarding" in pattern_lower: return "onboarding"
    return pattern_lower


def ensure_policy_tables(db: Session) -> None:
    # 1. Rank XP Thresholds
    rank_thresholds = [
        ("F", 0, 1),
        ("E", 862, 11),
        ("D", 2460, 21),
        ("C", 4604, 31),
        ("B", 7212, 41),
        ("A", 10234, 51),
        ("S", 13279, 60),
    ]
    for rank_name, min_xp, first_level in rank_thresholds:
        existing = db.query(RankXpThreshold).filter_by(rank_name=rank_name).first()
        if not existing:
            db.add(RankXpThreshold(rank_name=rank_name, min_xp=min_xp, first_level=first_level))
        else:
            existing.min_xp = min_xp
            existing.first_level = first_level
    db.flush()

    # 2. Quest XP Policies
    quest_policies = [
        ("vocab_flashcard", "Vocabulary", 4),
        ("vocab_codex", "Vocabulary", 5),
        ("vocab_collocation", "Vocabulary", 5),
        ("listening", "Listening", 10),
        ("reading", "Reading", 10),
        ("writing", "Writing", 12),
        ("speaking", "Speaking", 12),
        ("grammar_review", "Writing", 5),
        ("grammar_exercise", "Writing", 7),
    ]
    for activity_code, skill_code, xp_reward in quest_policies:
        existing = db.query(QuestXpPolicy).filter_by(activity_code=activity_code).first()
        if not existing:
            db.add(QuestXpPolicy(activity_code=activity_code, skill_code=skill_code, xp_reward=xp_reward))
        else:
            existing.skill_code = skill_code
            existing.xp_reward = xp_reward
    db.flush()

    # 3. Weekly Mission XP Policies
    weekly_policies = [
        ("vocab_weekly", "Vocabulary", 55),
        ("listening_weekly", "Listening", 40),
        ("reading_weekly", "Reading", 40),
        ("writing_weekly", "Writing", 45),
        ("speaking_weekly", "Speaking", 45),
        ("grammar_weekly", "Writing", 45),
        ("onboarding", "Writing", 25),
    ]
    for mission_type, skill_name, xp_reward in weekly_policies:
        existing = db.query(WeeklyMissionXpPolicy).filter_by(mission_type=mission_type).first()
        if not existing:
            db.add(WeeklyMissionXpPolicy(mission_type=mission_type, reward_target_skill=skill_name, xp_reward=xp_reward))
        else:
            existing.reward_target_skill = skill_name
            existing.xp_reward = xp_reward
    db.flush()

    # 4. Main Quest XP Policies
    main_policies = [
        ("light_intro", 25),
        ("standard", 35),
        ("heavy_output", 45),
        ("review_error_logging", 25),
        ("mock", 60),
    ]
    for tier_code, xp_reward in main_policies:
        existing = db.query(MainQuestXpPolicy).filter_by(tier_code=tier_code).first()
        if not existing:
            db.add(MainQuestXpPolicy(tier_code=tier_code, xp_reward=xp_reward))
        else:
            existing.xp_reward = xp_reward
    db.flush()


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
            "pattern_code": f"{phase_index}-vocabulary-expansion",
            "title": f"Weekly Mission - {phase_name} Vocabulary Expansion",
            "description": "Expand vocabulary: create codex entries, review flashcards, and log contexts.",
            "reward_xp": 50,
            "reward_skill": "Vocabulary",
            "items": [
                ("Create 2 codex entries", 2),
                ("Review 30 flashcards via spaced repetition", 30),
                ("Save 5 contextual sentences for target words", 5),
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
        {
            "pattern_code": f"{phase_index}-speaking-focus",
            "title": f"Weekly Mission - {phase_name} Speaking Focus",
            "description": "Drill Speaking fluency and pronunciation through structured practice.",
            "reward_xp": 45,
            "reward_skill": "Speaking",
            "items": [
                ("Complete 2 Speaking core quests", 2),
                ("Record and self-assess 3 speaking responses", 3),
                ("Log 2 pronunciation or fluency notes in Error Log", 2),
            ],
        },
        {
            "pattern_code": f"{phase_index}-grammar-focus",
            "title": f"Weekly Mission - {phase_name} Grammar Focus",
            "description": "Strengthen grammar structures to improve Writing accuracy.",
            "reward_xp": 45,
            "reward_skill": "Writing",
            "items": [
                ("Complete 2 Grammar Exercise or Grammar Review quests", 2),
                ("Apply 3 grammar rules in Writing practice", 3),
                ("Review 2 error log grammar entries", 2),
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


def ensure_demo_account(db: Session) -> Account:
    account = db.query(Account).filter(Account.email_normalized == "dev@example.com").first()
    if not account:
        account = Account(
            email="dev@example.com",
            email_normalized="dev@example.com",
            password_hash=hash_password("password123"),
            display_name="Dev User",
            status="active",
            role="user",
            onboarding_completed=True,
            onboarding_completed_at=datetime.utcnow(),
        )
        db.add(account)
        db.flush()

    main_account = db.query(Account).filter(Account.email_normalized == "ad00000@gmail.com").first()
    if not main_account:
        main_account = Account(
            email="ad00000@gmail.com",
            email_normalized="ad00000@gmail.com",
            password_hash=hash_password("khanhxx007"),
            display_name="AD00000",
            status="active",
            role="user",
            onboarding_completed=True,
            onboarding_completed_at=datetime.utcnow(),
        )
        db.add(main_account)
        db.flush()

    return main_account


def ensure_player(db: Session, start_date: date) -> Player:
    demo_account = ensure_demo_account(db)
    player = db.query(Player).filter(Player.account_id == demo_account.id).first()
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
        account_id=demo_account.id,
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
    for name, icon, _ in SKILLS:
        skill = db.query(Skill).filter(Skill.name == name).first()
        boss_gated = name not in ("Writing", "Speaking")
        if not skill:
            skill = Skill(
                name=name,
                icon=icon,
                boss_gated=boss_gated,
            )
            db.add(skill)
            db.flush()
        else:
            skill.icon = icon
            skill.boss_gated = boss_gated
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
        rebased_start = rebase_material_date(row["week_start"], campaign.start_date)
        rebased_end = rebase_material_date(row["week_end"], campaign.start_date)
        if not week:
            week = StudyPlanWeek(
                campaign_id=campaign.id,
                phase_id=phase.id,
                week_no=row["week_no"],
                week_start=rebased_start,
                week_end=rebased_end,
                weekly_focus=row["weekly_focus"],
                weekly_output=row["weekly_output"],
                material_summary=row["material_summary"],
                mini_task=row["mini_task"],
            )
            db.add(week)
            db.flush()
        else:
            week.week_start = rebased_start
            week.week_end = rebased_end
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
        rebased_date = rebase_material_date(row["study_date"], campaign.start_date)
        rebased_label = rebased_date.strftime("%A")
        if not session:
            session = StudyPlanSession(
                campaign_id=campaign.id,
                phase_id=week.phase_id,
                study_plan_week_id=week.id,
                week_no=week.week_no,
                session_no=session_no,
                study_date=rebased_date,
                weekday_label=rebased_label,
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
        else:
            session.study_date = rebased_date
            session.weekday_label = rebased_label
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
        activity_code = map_template_to_activity_code(item["title"])
        policy = db.query(QuestXpPolicy).filter_by(activity_code=activity_code).first()
        base_xp = policy.xp_reward if policy else item["base_xp"]

        template = db.query(QuestTemplate).filter(QuestTemplate.title == item["title"]).first()
        if not template:
            template = QuestTemplate(
                title=item["title"],
                description=item["description"],
                primary_skill_id=skill_by_name[item["skill"]].id,
                phase_id=phase_by_code[item["phase_code"]].id,
                material_id=material_by_title[item["material_title"]].id,
                base_xp=base_xp,
                difficulty=item["difficulty"],
                difficulty_description=item["difficulty_description"],
                quest_role=item["quest_role"],
                resource_name=item["resource_name"],
                resource_category=item["resource_category"],
                resource_note=item["resource_note"],
                allowed_phase_start=item["allowed_phase_start"],
                allowed_phase_end=item["allowed_phase_end"],
                is_active=True,
                quest_track_code=item.get("quest_track_code", ""),
                activity_type=item.get("activity_type", ""),
                reward_skill_id=skill_by_name[item["skill"]].id if item.get("reward_skill_id") == item.get("skill") else None,
                target_metric=item.get("target_metric", ""),
                target_count=item.get("target_count", 1),
                completion_payload=item.get("completion_payload", ""),
            )
            db.add(template)
            db.flush()
        else:
            template.description = item["description"]
            template.primary_skill_id = skill_by_name[item["skill"]].id
            template.phase_id = phase_by_code[item["phase_code"]].id
            template.material_id = material_by_title[item["material_title"]].id
            template.base_xp = base_xp
            template.difficulty = item["difficulty"]
            template.difficulty_description = item["difficulty_description"]
            template.quest_role = item["quest_role"]
            template.resource_name = item["resource_name"]
            template.resource_category = item["resource_category"]
            template.resource_note = item["resource_note"]
            template.allowed_phase_start = item["allowed_phase_start"]
            template.allowed_phase_end = item["allowed_phase_end"]
            template.is_active = True
        # Update optional new fields
        template.quest_track_code = item.get("quest_track_code", getattr(template, "quest_track_code", ""))
        template.activity_type = item.get("activity_type", getattr(template, "activity_type", ""))
        # reward_skill_id can be provided as a skill name
        if item.get("reward_skill_id"):
            rs = item.get("reward_skill_id")
            if isinstance(rs, str) and rs in skill_by_name:
                template.reward_skill_id = skill_by_name[rs].id
        template.target_metric = item.get("target_metric", getattr(template, "target_metric", ""))
        template.target_count = item.get("target_count", getattr(template, "target_count", 1))
        template.completion_payload = item.get("completion_payload", getattr(template, "completion_payload", ""))
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
    # 1. Fetch active quotas for this campaign
    quotas = db.query(CampaignSkillQuestQuota).filter(
        CampaignSkillQuestQuota.campaign_id == campaign.id,
        CampaignSkillQuestQuota.is_active == True
    ).all()

    # Map skill name to quota
    quota_by_skill_name = {q.skill.name: q for q in quotas if q.skill}

    # Map skill/activity combinations to distinct daily slot codes and templates
    slot_mapping = {
        "Vocabulary": [
            ("vocab_flashcard", "Flashcard Gate"),
            ("vocab_codex", "Codex Entry"),
            ("vocab_collocation", "Collocation Forge")
        ],
        "Reading": [
            ("reading", "Reading Daily")
        ],
        "Listening": [
            ("listening", "Listening Daily")
        ],
        "Grammar": [
            ("grammar_review", "Grammar Review"),
            ("grammar_exercise", "Grammar Exercise")
        ],
        "Writing": [
            ("writing", "Writing Daily")
        ],
        "Speaking": [
            ("speaking", "Speaking Daily")
        ]
    }

    # Fetch existing quest daily slot codes to avoid duplicates
    existing_daily_keys = {
        (quest.quest_date, quest.daily_slot_code)
        for quest in db.query(Quest.quest_date, Quest.daily_slot_code)
        .filter(Quest.campaign_id == campaign.id, Quest.session_type == "Daily Quest")
        .all()
    }

    total_weeks = 78
    for week_no in range(1, total_weeks + 1):
        phase_index = phase_for_week(week_no)
        phase_name = phase_label(phase_index)
        week_start = campaign.start_date + timedelta(days=(week_no - 1) * 7)
        phase = phase_by_code.get(f"phase-{phase_index}")
        phase_id = phase.id if phase else None

        for day_offset in range(7):
            quest_date = week_start + timedelta(days=day_offset)

            for skill_name, slots in slot_mapping.items():
                quota = quota_by_skill_name.get(skill_name)
                if not quota or quota.daily_quota <= 0:
                    continue

                # Reorder slots based on preferred_activity_types
                preferred = quota.preferred_activity_types
                pref_list = []
                if isinstance(preferred, list):
                    pref_list = [str(x) for x in preferred]
                elif isinstance(preferred, str):
                    pref_list = [preferred]

                ordered_slots = []
                if pref_list:
                    for pref_act in pref_list:
                        for slot_code, title in slots:
                            template = template_by_title.get(title)
                            act_type = getattr(template, "activity_type", "") if template else ""
                            if act_type == pref_act and (slot_code, title) not in ordered_slots:
                                ordered_slots.append((slot_code, title))
                    for slot_code, title in slots:
                        if (slot_code, title) not in ordered_slots:
                            ordered_slots.append((slot_code, title))
                else:
                    ordered_slots = slots

                # Generate daily quests up to the quota limit
                limit = min(quota.daily_quota, len(ordered_slots))
                for i in range(limit):
                    slot_code, template_title = ordered_slots[i]

                    if (quest_date, slot_code) in existing_daily_keys:
                        existing = db.query(Quest).filter(
                            Quest.campaign_id == campaign.id,
                            Quest.quest_date == quest_date,
                            Quest.daily_slot_code == slot_code,
                            Quest.session_type == "Daily Quest"
                        ).first()
                        if existing and template_title in template_by_title:
                            template = template_by_title[template_title]
                            skill = skill_by_name.get(template.primary_skill.name) or skill_by_name.get(skill_name)
                            existing.stage = phase_name
                            existing.title = template.title
                            existing.skill_id = skill.id if skill else existing.skill_id
                            existing.source = template.resource_name
                            existing.details = template.description
                            existing.phase_id = phase_id or existing.phase_id
                            existing.template_id = template.id
                            existing.material_id = template.material_id
                            existing.difficulty = template.difficulty
                            existing.base_xp = template.base_xp
                            existing.xp = template.base_xp
                            existing.quest_role = template.quest_role
                            existing.quest_track_code = getattr(template, "quest_track_code", "")
                            existing.activity_type = getattr(template, "activity_type", "")
                            existing.reward_skill_id = getattr(template, "reward_skill_id", None)
                            existing.target_metric = getattr(template, "target_metric", "")
                            existing.target_count = getattr(template, "target_count", 1)
                            existing.completion_payload = getattr(template, "completion_payload", "")
                        continue

                    if template_title in template_by_title:
                        template = template_by_title[template_title]
                        skill = skill_by_name.get(template.primary_skill.name) or skill_by_name.get(skill_name)
                        if skill:
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
                                    phase_id=phase_id,
                                    template_id=template.id,
                                    material_id=template.material_id,
                                    status="pending",
                                    quest_role=template.quest_role,
                                    daily_slot_code=slot_code,
                                    difficulty=template.difficulty,
                                    base_xp=template.base_xp,
                                    earned_xp=0,
                                    quest_track_code=getattr(template, "quest_track_code", ""),
                                    activity_type=getattr(template, "activity_type", ""),
                                    reward_skill_id=getattr(template, "reward_skill_id", None),
                                    target_metric=getattr(template, "target_metric", ""),
                                    target_count=getattr(template, "target_count", 1),
                                    completion_payload=getattr(template, "completion_payload", ""),
                                )
                            )
                            existing_daily_keys.add((quest_date, slot_code))


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
            existing.quest_date = session.study_date  # self-heal: keep main quest date in sync with rebased session date
            existing.week_no = session.week_no
            existing.stage = session_week.phase.title if session_week else phase_label(phase_for_week(session.week_no))
            existing.title = f"Main Quest W{session.week_no:02d} - {session.session_label}"
            existing.source = session.material_summary
            existing.details = session.task_detail
            existing.phase_id = session.phase_id
            existing.material_id = primary_material.id if primary_material else None
            existing.base_xp = infer_main_quest_xp(session.session_no, session.skill_summary, session.task_detail, db=db)
            existing.xp = infer_main_quest_xp(session.session_no, session.skill_summary, session.task_detail, db=db)
            existing.completion_note = session.deliverable
            continue
        primary_skill_name = infer_primary_skill(session.skill_summary, session.task_detail)
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
                xp=infer_main_quest_xp(session.session_no, session.skill_summary, session.task_detail, db=db),
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
                base_xp=infer_main_quest_xp(session.session_no, session.skill_summary, session.task_detail, db=db),
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
            policy = db.query(WeeklyMissionXpPolicy).filter_by(mission_type="onboarding").first()
            reward_xp = policy.xp_reward if policy else 25
            reward_skill_id = None
            if policy:
                skill = db.query(Skill).filter_by(name=policy.reward_target_skill).first()
                if skill:
                    reward_skill_id = skill.id

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
                    reward_xp=reward_xp,
                    status="active",
                    reward_skill_id=reward_skill_id,
                    primary_skill_id=reward_skill_id,
                )
                db.add(mission)
                db.flush()
            else:
                mission.week_end = week_end
                mission.phase = phase_label(phase_index)
                mission.pattern_code = "onboarding"
                mission.title = "Onboarding Week"
                mission.description = "Get used to the dashboard, check-ins, and a lighter quest loop."
                mission.reward_xp = reward_xp
                mission.reward_skill_id = reward_skill_id
                mission.primary_skill_id = reward_skill_id
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

        mission_type = map_weekly_pattern_to_mission_type(pattern["pattern_code"])
        policy = db.query(WeeklyMissionXpPolicy).filter_by(mission_type=mission_type).first()
        reward_xp = policy.xp_reward if policy else pattern["reward_xp"]
        reward_skill_id = None
        if policy:
            skill = db.query(Skill).filter_by(name=policy.reward_target_skill).first()
            if skill:
                reward_skill_id = skill.id
        elif pattern.get("reward_skill") and pattern.get("reward_skill") in [s.name for s in db.query(Skill).all()]:
            skill = db.query(Skill).filter(Skill.name == pattern.get("reward_skill")).first()
            reward_skill_id = skill.id

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
                reward_xp=reward_xp,
                status="active",
                primary_skill_id=reward_skill_id,
                mission_track_code=pattern.get("pattern_code", ""),
                activity_type=pattern.get("activity_type", ""),
                reward_skill_id=reward_skill_id,
            )
            db.add(mission)
            db.flush()
        else:
            mission.week_end = week_end
            mission.phase = phase_label(phase_index)
            mission.pattern_code = pattern["pattern_code"]
            mission.title = pattern["title"]
            mission.description = pattern["description"]
            mission.reward_xp = reward_xp
            mission.reward_skill_id = reward_skill_id
            mission.primary_skill_id = reward_skill_id
        mission.mission_track_code = pattern.get("pattern_code", mission.mission_track_code)
        mission.activity_type = pattern.get("activity_type", mission.activity_type)
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


def ensure_campaign_templates(db: Session, skill_by_name: dict[str, Skill]) -> CampaignTemplate:
    template = db.query(CampaignTemplate).filter(CampaignTemplate.code == "ielts_18_month_foundation").first()
    if not template:
        template = CampaignTemplate(
            code="ielts_18_month_foundation",
            title="IELTS 18-Month Hunter Roadmap",
            description="Complete game-styled progress tracking toward IELTS 7.0-7.5 target over an 18-month duration.",
            certificate_type="IELTS",
            target_band="7.0-7.5",
            duration_months=18,
            total_weeks=78,
            is_active=True
        )
        db.add(template)
        db.flush()
    
    # quotas mapping
    quotas = {
        "Vocabulary": 3,
        "Reading": 1,
        "Listening": 1,
        "Grammar": 2,
        "Collocation": 0,
        "Writing": 1,
        "Speaking": 1,
    }
    for skill_name, daily_val in quotas.items():
        skill = skill_by_name.get(skill_name)
        if skill:
            quota = db.query(CampaignTemplateSkillQuota).filter(
                CampaignTemplateSkillQuota.campaign_template_id == template.id,
                CampaignTemplateSkillQuota.skill_id == skill.id
            ).first()
            if not quota:
                quota = CampaignTemplateSkillQuota(
                    campaign_template_id=template.id,
                    skill_id=skill.id,
                    daily_quota=daily_val,
                    weekly_quota=daily_val * 7,
                    priority=100,
                    is_active=True,
                    preferred_activity_types=[]
                )
                db.add(quota)
            else:
                quota.daily_quota = daily_val
                quota.weekly_quota = daily_val * 7
                quota.is_active = True
    db.flush()
    return template


def ensure_account_and_profile(db: Session, player: Player) -> Account:
    main_account = ensure_demo_account(db)

    pref = db.query(AccountPreference).filter(AccountPreference.account_id == main_account.id).first()
    if not pref:
        pref = AccountPreference(
            account_id=main_account.id,
            locale="vi",
            timezone="Asia/Ho_Chi_Minh",
            theme="dark",
            notification_enabled=True
        )
        db.add(pref)

    profile = db.query(PlayerLearningProfile).filter(PlayerLearningProfile.player_id == player.id).first()
    if not profile:
        profile = PlayerLearningProfile(
            player_id=player.id,
            preferred_learning_style="mixed",
            dictionary_mode="bilingual_first",
            pronunciation_focus=True,
            collocation_focus=True,
            native_language="vi",
            interface_learning_language="mixed"
        )
        db.add(profile)

    db.flush()
    return main_account


def ensure_campaign_settings_and_quotas(db: Session, campaign: Campaign, template: CampaignTemplate, skill_by_name: dict[str, Skill]) -> None:
    # campaign template link
    if not campaign.campaign_template_id:
        campaign.campaign_template_id = template.id
        campaign.setup_completed = True
        campaign.setup_completed_at = datetime.utcnow()
        
    # settings
    setting = db.query(CampaignSetting).filter(CampaignSetting.campaign_id == campaign.id).first()
    if not setting:
        setting = CampaignSetting(
            campaign_id=campaign.id,
            target_certificate="IELTS",
            target_band="7.0-7.5",
            current_english_level="B1",
            start_date=campaign.start_date,
            study_duration_months=18
        )
        db.add(setting)
        
    # skill quotas
    for quota_temp in template.skill_quotas:
        quota = db.query(CampaignSkillQuestQuota).filter(
            CampaignSkillQuestQuota.campaign_id == campaign.id,
            CampaignSkillQuestQuota.skill_id == quota_temp.skill_id
        ).first()
        if not quota:
            quota = CampaignSkillQuestQuota(
                campaign_id=campaign.id,
                skill_id=quota_temp.skill_id,
                daily_quota=quota_temp.daily_quota,
                weekly_quota=quota_temp.weekly_quota,
                priority=quota_temp.priority,
                is_active=quota_temp.is_active,
                preferred_activity_types=quota_temp.preferred_activity_types
            )
            db.add(quota)
        else:
            quota.daily_quota = quota_temp.daily_quota
            quota.weekly_quota = quota_temp.weekly_quota
            quota.is_active = quota_temp.is_active
            
    # vocabulary settings
    vocab_setting = db.query(VocabularySetting).filter(VocabularySetting.campaign_id == campaign.id).first()
    if not vocab_setting:
        vocab_setting = VocabularySetting(
            campaign_id=campaign.id,
            daily_new_words_target=5,
            daily_flashcard_target=20,
            daily_collocation_target=3,
            daily_context_hunt_target=5,
            daily_error_review_target=3,
            vocab_review_mode="mixed",
            vocab_grouping_mode="topic",
            dictionary_mode="bilingual_first",
            example_sentence_required=True,
            pronunciation_required=False,
            word_family_required=False,
            synonym_antonym_required=False,
            collocation_required=True,
            spaced_repetition_enabled=True
        )
        db.add(vocab_setting)
    db.flush()


def ensure_rank_exam_pools(db: Session, skill_by_name: dict[str, Skill]) -> None:
    # Seed F -> E pools for MVP skills: Vocabulary, Reading, Listening, Grammar, Collocation
    mvp_skills = ["Vocabulary", "Reading", "Listening", "Grammar", "Collocation"]
    
    questions_data = {
        "Vocabulary": [
            ("What is the synonym of 'abandon'?", ["Keep", "Leave", "Find", "Hold"], "Leave"),
            ("What is the antonym of 'abundant'?", ["Scarce", "Plentiful", "Rich", "Full"], "Scarce"),
            ("Select the word that means 'to make something better':", ["Aggravate", "Ameliorate", "Decline", "Worsen"], "Ameliorate"),
            ("Choose the correct word for: 'lasting for a very short time'", ["Ephemeral", "Permanent", "Eternal", "Constant"], "Ephemeral"),
            ("Identify the correct synonym for 'capricious':", ["Unpredictable", "Stable", "Reliable", "Constant"], "Unpredictable"),
        ],
        "Reading": [
            ("What reading technique is used to find a specific piece of information (e.g., a date)?", ["Skimming", "Scanning", "Intensive Reading", "Extensive Reading"], "Scanning"),
            ("Skimming a text helps to identify what?", ["Specific names", "The main idea/gist", "Spelling errors", "Detailed definitions"], "The main idea/gist"),
            ("In IELTS Reading, 'Not Given' means what?", ["The statement contradicts the writer's view", "The statement agrees with the writer's view", "There is no information to verify the statement", "The text contains spelling mistakes"], "There is no information to verify the statement"),
            ("Which type of question asks you to match paragraphs to headings?", ["Matching Headings", "True/False/Not Given", "Multiple Choice", "Sentence Completion"], "Matching Headings"),
            ("When a synonym is used in a question instead of the exact word from the text, this is called:", ["Distraction", "Paraphrasing", "Skimming", "Coherence"], "Paraphrasing"),
        ],
        "Listening": [
            ("What should you do during the time provided before a listening section starts?", ["Read the questions and predict answers", "Write down your final answers", "Listen to section 4 immediately", "Rest and close your eyes"], "Read the questions and predict answers"),
            ("In dictation, what spelling is crucial for credit?", ["Correct spelling", "Approximate spelling", "Phonetic spelling", "Capitalized spelling only"], "Correct spelling"),
            ("What are speakers likely to use to lead you to select the wrong option?", ["Distractors/corrections", "Clear accents", "Simple sentences", "Slow speech"], "Distractors/corrections"),
            ("A question asks for a 'number only'. What is a valid answer?", ["Three", "3", "3 words", "Third"], "3"),
            ("If a speaker says: 'I wanted to go on Tuesday, but then we decided on Friday.' What day did they agree on?", ["Tuesday", "Wednesday", "Friday", "Monday"], "Friday"),
        ],
        "Grammar": [
            ("Choose the correct form: 'If I ___ you, I would study harder.'", ["am", "was", "were", "be"], "were"),
            ("Identify the passive voice sentence:", ["She wrote a letter.", "A letter was written by her.", "She is writing a letter.", "She has written a letter."], "A letter was written by her."),
            ("Complete the sentence: 'By next December, I ___ this course.'", ["will finish", "will have finished", "finish", "finished"], "will have finished"),
            ("Which relative pronoun is used for non-defining clauses about things?", ["who", "which", "whom", "whose"], "which"),
            ("Identify the correct conditional: 'If it rains, the ground ___ wet.'", ["gets", "would get", "got", "will got"], "gets"),
        ],
        "Collocation": [
            ("Select the correct collocation: 'make a ___'", ["mistake", "error", "crime", "fault"], "mistake"),
            ("Which verb collocates with 'homework'?", ["do", "make", "create", "write"], "do"),
            ("Complete the collocation: 'bear in ___'", ["head", "brain", "mind", "thoughts"], "mind"),
            ("Choose the natural combination:", ["fast food", "quick food", "rapid food", "swift food"], "fast food"),
            ("Which word fits best: 'pay ___ to details'", ["attention", "focus", "notice", "regard"], "attention"),
        ]
    }
    
    # xp_threshold = RANK_MIN_XP of the target rank (ielts_xp_policy_rank_quest_spec.md §2.3)
    transitions = [
        ("F", "E", 862),
        ("E", "D", 2460),
        ("D", "C", 4604),
        ("C", "B", 7212),
        ("B", "A", 10234),
        ("A", "S", 13279),
    ]

    for skill_name in mvp_skills:
        skill = skill_by_name.get(skill_name)
        if not skill:
            continue
        
        for from_r, to_r, thresh in transitions:
            # Check pool
            pool = db.query(RankExamPool).filter(
                RankExamPool.skill_id == skill.id,
                RankExamPool.from_rank == from_r,
                RankExamPool.to_rank == to_r
            ).first()
            
            if not pool:
                pool = RankExamPool(
                    skill_id=skill.id,
                    from_rank=from_r,
                    to_rank=to_r,
                    title=f"{skill_name} {from_r} to {to_r} Rank Boss Exam",
                    description=f"Prove your {skill_name} competency to rank up from {from_r} to {to_r}.",
                    pass_percent=80,
                    default_time_limit_minutes=30,
                    max_attempts_per_day=2,
                    xp_threshold=thresh,
                    is_active=True
                )
                db.add(pool)
                db.flush()
            else:
                if pool.xp_threshold != thresh:
                    pool.xp_threshold = thresh
                    db.flush()
                
            # Seed version and questions only for F -> E transition
            if from_r == "F" and to_r == "E":
                # Check version
                version = db.query(RankExamVersion).filter(
                    RankExamVersion.pool_id == pool.id,
                    RankExamVersion.version_code == "v1_mvp"
                ).first()
                
                if not version:
                    version = RankExamVersion(
                        pool_id=pool.id,
                        title=f"{skill_name} Foundational Quiz Version 1",
                        version_code="v1_mvp",
                        total_questions=5,
                        total_points=5,
                        difficulty="normal",
                        time_limit_minutes=30,
                        is_active=True
                    )
                    db.add(version)
                    db.flush()
                    
                # Questions
                q_list = questions_data[skill_name]
                for idx, (prompt, options, correct) in enumerate(q_list):
                    q_exists = db.query(RankExamQuestion).filter(
                        RankExamQuestion.exam_version_id == version.id,
                        RankExamQuestion.order_index == idx
                    ).first()
                    if not q_exists:
                        db.add(
                            RankExamQuestion(
                                exam_version_id=version.id,
                                question_type="multiple_choice",
                                prompt=prompt,
                                instruction="Choose the correct multiple-choice option.",
                                options_json=options,
                                correct_answer_json=correct,
                                explanation=f"The correct answer is '{correct}' based on foundational {skill_name} rules.",
                                points=1,
                                order_index=idx
                            )
                        )
    db.flush()


def collocations_file_path() -> Path:
    candidates: list[Path] = []

    configured_path = os.getenv("COLLOCATIONS_PATH")
    if configured_path:
        candidates.append(Path(configured_path))

    current_file = Path(__file__).resolve()
    # C-1: repointed to the polished (OCR-denoised) file
    rel_path = Path("material/vocabularies/month1-6/English_Collocations_campaign1-3_3-6_polished.md")
    candidates.extend(
        [
            current_file.parents[2] / rel_path,
            current_file.parents[1] / rel_path,
            Path.cwd() / rel_path,
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Collocations file not found. Checked: {searched}")


def parse_collocations_file(filepath: Path) -> dict:
    """Parse the polished collocation markdown file into a structured dict.

    File hierarchy (polished format):
        ## N. Topic Title          ← CollocationTopic (60 total)
        _Section: Section Name_    ← CollocationSection (10 total); appears once
                                     per ## N. block, directly after the heading.
                                     Consecutive topics sharing the same section
                                     name belong to the same section.
        | col | pron | vi | ex_en | ex_vi |   ← CollocationItem rows

    Parser rules (C-1):
    - Open a new Section when the `_Section:_` label changes from the previous
      one seen (not when a `## N.` heading appears).
    - Each `## N. Title` becomes a Topic inside the current section; topic_number
      = N, topic_order = 1-based counter within its section.
    - Item global dedup (C-2): a collocation phrase already seen anywhere in the
      collection is skipped — first occurrence wins.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    sections: list[dict] = []
    # Map section_name → section dict (for fast lookup / dedup)
    section_by_name: dict[str, dict] = {}
    section_order_counter = 0

    current_section: dict | None = None
    current_topic: dict | None = None
    pending_topic_number: int | None = None
    pending_topic_title: str | None = None
    item_order_count = 0

    re_heading = re.compile(r"^##\s+(\d+)\.\s+(.*)")
    re_section_label = re.compile(r"^_(?:Section|Topic):\s+(.+?)_\s*$")

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # --- ## N. Topic heading ---
        heading_match = re_heading.match(line_stripped)
        if heading_match:
            pending_topic_number = int(heading_match.group(1))
            pending_topic_title = heading_match.group(2).strip()
            current_topic = None  # topic not created yet — wait for _Section:_ line
            item_order_count = 0
            continue

        # --- _Section: Name_ label ---
        section_match = re_section_label.match(line_stripped)
        if section_match:
            section_name = section_match.group(1).strip()

            # Open a new section only when the name changes
            if section_name not in section_by_name:
                section_order_counter += 1
                sec = {
                    "section_order": section_order_counter,
                    "title": section_name,
                    "topics": [],
                }
                sections.append(sec)
                section_by_name[section_name] = sec

            current_section = section_by_name[section_name]

            # Create the topic that was buffered by the preceding ## N. heading
            if pending_topic_title is not None and pending_topic_number is not None:
                topic_order = len(current_section["topics"]) + 1
                current_topic = {
                    "title": pending_topic_title,
                    "topic_number": pending_topic_number,
                    "topic_order": topic_order,
                    "items": [],
                }
                current_section["topics"].append(current_topic)
                pending_topic_title = None
                pending_topic_number = None
                item_order_count = 0
            continue

        # --- Table row ---
        if line_stripped.startswith("|") and line_stripped.endswith("|"):
            parts = [p.strip() for p in line_stripped.split("|")[1:-1]]
            if not parts:
                continue
            collocation = parts[0]
            if collocation.lower() in ("collocation", "---") or "---" in collocation:
                continue

            if current_topic is None:
                continue  # orphan row before any topic — skip

            pronunciation_us = parts[1] if len(parts) > 1 else None
            meaning_vi       = parts[2] if len(parts) > 2 else None
            example_en       = parts[3] if len(parts) > 3 else None
            example_vi       = parts[4] if len(parts) > 4 else None

            if pronunciation_us == "": pronunciation_us = None
            if meaning_vi       == "": meaning_vi       = None
            if example_en       == "": example_en       = None
            if example_vi       == "": example_vi       = None

            item_order_count += 1
            current_topic["items"].append({
                "collocation":     collocation,
                "pronunciation_us": pronunciation_us,
                "meaning_vi":       meaning_vi,
                "example_en":       example_en,
                "example_vi":       example_vi,
                "item_order":       item_order_count,
            })

    return {
        "code":        "intermediate-collocations",
        "title":       "English Collocations in Use Intermediate",
        "description": "English Collocations in Use Intermediate — polished (OCR-denoised)",
        "source_book": "English Collocations in Use Intermediate",
        "level":       "Intermediate",
        "sections":    sections,
    }


def ensure_collocations(db: Session, campaign: Campaign) -> None:
    try:
        filepath = collocations_file_path()
        data = parse_collocations_file(filepath)
    except FileNotFoundError:
        return

    # 1. Get or create CollocationCollection
    collection = db.query(CollocationCollection).filter_by(code=data["code"]).first()
    if not collection:
        collection = CollocationCollection(
            code=data["code"],
            title=data["title"],
            description=data["description"],
            source_book=data["source_book"],
            level=data["level"],
            is_active=True
        )
        db.add(collection)
        db.flush()

    # 2. Link to campaign
    link_collection_to_campaign(db, campaign.id, collection.id)

    # 3. Sections & Topics & Items (idempotent)
    # C-2: global dedup — track collocation phrases seen anywhere in this
    # collection so each phrase is stored at most once (first occurrence wins).
    globally_seen: set[str] = set()

    # Pre-populate from items already in DB for this collection (idempotent re-seed)
    existing_in_db = (
        db.query(CollocationItem.collocation)
        .join(CollocationTopic, CollocationItem.topic_id == CollocationTopic.id)
        .join(CollocationSection, CollocationTopic.section_id == CollocationSection.id)
        .filter(CollocationSection.collection_id == collection.id)
        .all()
    )
    for (phrase,) in existing_in_db:
        globally_seen.add(phrase)

    for section_data in data["sections"]:
        section = db.query(CollocationSection).filter_by(
            collection_id=collection.id,
            section_order=section_data["section_order"]
        ).first()
        if not section:
            section = CollocationSection(
                collection_id=collection.id,
                title=section_data["title"],
                section_order=section_data["section_order"]
            )
            db.add(section)
            db.flush()
        else:
            if section.title != section_data["title"]:
                section.title = section_data["title"]
                db.flush()

        for topic_data in section_data["topics"]:
            # C-1: topic_number comes from topic_data (the ## N value), not section_order
            topic_number = topic_data.get("topic_number", section_data["section_order"])
            topic = db.query(CollocationTopic).filter_by(
                section_id=section.id,
                title=topic_data["title"]
            ).first()
            if not topic:
                topic = CollocationTopic(
                    section_id=section.id,
                    title=topic_data["title"],
                    topic_number=topic_number,
                    topic_order=topic_data["topic_order"]
                )
                db.add(topic)
                db.flush()
            else:
                changed = False
                if topic.topic_order != topic_data["topic_order"]:
                    topic.topic_order = topic_data["topic_order"]
                    changed = True
                if topic.topic_number != topic_number:
                    topic.topic_number = topic_number
                    changed = True
                if changed:
                    db.flush()

            # C-2: global dedup — skip phrases already seen in this collection
            existing_items = {
                item.collocation: item
                for item in db.query(CollocationItem).filter_by(topic_id=topic.id).all()
            }

            for item_data in topic_data["items"]:
                colloc = item_data["collocation"]

                # Already in DB for this collection (from a different topic) → skip
                if colloc in globally_seen and colloc not in existing_items:
                    continue

                globally_seen.add(colloc)

                if colloc not in existing_items:
                    new_item = CollocationItem(
                        topic_id=topic.id,
                        collocation=colloc,
                        pronunciation_us=item_data["pronunciation_us"],
                        meaning_vi=item_data["meaning_vi"],
                        example_en=item_data["example_en"],
                        example_vi=item_data["example_vi"],
                        collocation_type=None,
                        item_order=item_data["item_order"]
                    )
                    db.add(new_item)
                else:
                    item = existing_items[colloc]
                    if item.pronunciation_us != item_data["pronunciation_us"]:
                        item.pronunciation_us = item_data["pronunciation_us"]
                    if item.meaning_vi != item_data["meaning_vi"]:
                        item.meaning_vi = item_data["meaning_vi"]
                    if item.example_en != item_data["example_en"]:
                        item.example_en = item_data["example_en"]
                    if item.example_vi != item_data["example_vi"]:
                        item.example_vi = item_data["example_vi"]
                    if item.item_order != item_data["item_order"]:
                        item.item_order = item_data["item_order"]

            db.flush()


def seed_database(db: Session, start_date: date) -> None:
    player = ensure_player(db, start_date)
    campaign = ensure_campaign(db, player, start_date)
    skill_by_name = ensure_skills(db)
    badges = ensure_badges(db)
    material_by_title = ensure_materials(db)

    # Run Phase 4 extensions
    template = ensure_campaign_templates(db, skill_by_name)
    ensure_account_and_profile(db, player)
    ensure_campaign_settings_and_quotas(db, campaign, template, skill_by_name)
    ensure_rank_exam_pools(db, skill_by_name)
    ensure_policy_tables(db)  # must run before ensure_templates (templates read QuestXpPolicy)

    phase_by_code = ensure_roadmap_phases(db, campaign)
    ensure_phase_materials(db, phase_by_code, material_by_title)
    week_by_no, study_plan_sessions = ensure_study_plan(db, campaign, phase_by_code)
    template_by_title = ensure_templates(db, skill_by_name, phase_by_code, material_by_title)
    ensure_quest_instances(db, campaign, skill_by_name, template_by_title, phase_by_code)
    ensure_main_quest_instances(db, campaign, skill_by_name, material_by_title, week_by_no, study_plan_sessions)
    backfill_quest_phase_and_material(db, campaign, phase_by_code)
    ensure_weekly_missions(db, campaign)
    ensure_bosses(db, campaign, badges)
    ensure_collocations(db, campaign)
    db.commit()


def parse_start_date() -> date:
    raw = os.getenv("APP_START_DATE")
    if raw:
        return date.fromisoformat(raw)
    return date.today()


def activate_campaign_for_player(db: Session, player: Player, template_code: str = "ielts_18_month_foundation", start_date: date | None = None) -> Campaign:
    skill_by_name = ensure_skills(db)
    badges = ensure_badges(db)
    material_by_title = ensure_materials(db)

    template = db.query(CampaignTemplate).filter(CampaignTemplate.code == template_code).first()
    if not template:
        template = ensure_campaign_templates(db, skill_by_name)

    if start_date is None:
        start_date = parse_start_date()
    end_date = campaign_end_date(start_date)
    
    # check if there is already an active campaign for this player (idempotence)
    campaign = db.query(Campaign).filter(
        Campaign.player_id == player.id,
        Campaign.status == "active"
    ).first()
    
    if not campaign:
        campaign = Campaign(
            player_id=player.id,
            campaign_template_id=template.id,
            start_date=start_date,
            end_date=end_date,
            status="active",
            setup_completed=True,
            setup_completed_at=datetime.utcnow()
        )
        db.add(campaign)
        db.flush()
        
    player.active_campaign_id = campaign.id
    player.setup_completed = True
    player.start_date = start_date
    # Only set target from template if player has no custom target yet
    if template.target_band and not player.target_overall_band:
        player.target_overall_band = template.target_band
        player.target = f"IELTS Academic {template.target_band}"
    db.flush()

    ensure_campaign_settings_and_quotas(db, campaign, template, skill_by_name)
    ensure_rank_exam_pools(db, skill_by_name)
    ensure_policy_tables(db)  # must run before ensure_templates

    phase_by_code = ensure_roadmap_phases(db, campaign)
    ensure_phase_materials(db, phase_by_code, material_by_title)
    week_by_no, study_plan_sessions = ensure_study_plan(db, campaign, phase_by_code)
    template_by_title = ensure_templates(db, skill_by_name, phase_by_code, material_by_title)
    ensure_quest_instances(db, campaign, skill_by_name, template_by_title, phase_by_code)
    ensure_main_quest_instances(db, campaign, skill_by_name, material_by_title, week_by_no, study_plan_sessions)
    backfill_quest_phase_and_material(db, campaign, phase_by_code)
    ensure_weekly_missions(db, campaign)
    ensure_bosses(db, campaign, badges)
    ensure_collocations(db, campaign)

    # ensure campaign skill states are created
    from .services import ensure_campaign_skill_states
    ensure_campaign_skill_states(db, campaign)
    
    db.flush()
    return campaign

