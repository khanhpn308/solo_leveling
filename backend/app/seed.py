from datetime import date, timedelta
from sqlalchemy.orm import Session
from .models import Player, Skill, Quest, Badge, BossBattle

SKILLS = [
    ("Listening", "🎧", "Điểm mạnh hiện tại; cần nâng Section 3–4, distractor và spelling."),
    ("Reading", "📖", "Điểm yếu chính: thiếu từ vựng và chưa quen phân tích câu dài."),
    ("Writing", "✍️", "Cần viết đều, sửa lỗi theo Task Response, Coherence, Lexical Resource, Grammar."),
    ("Speaking", "🗣️", "Cần ghi âm đều, tăng fluency, pronunciation và Part 3 reasoning."),
    ("Vocabulary", "🧠", "Học theo topic, paraphrase pairs và ví dụ cá nhân hóa."),
    ("Collocation", "🔗", "Dùng để nói/viết tự nhiên hơn, giảm lỗi kết hợp từ."),
    ("Grammar", "⚙️", "Củng cố thì, mệnh đề quan hệ, bị động, câu điều kiện, câu phức."),
]

BADGES = [
    ("7-Day Streak", "🔥", "Học liên tục 7 ngày."),
    ("Vocabulary Hunter", "🧠", "Hoàn thành 300 XP Vocabulary."),
    ("Grammar Fixer", "⚙️", "Hoàn thành 300 XP Grammar."),
    ("Listening Warrior", "🎧", "Hoàn thành 500 XP Listening."),
    ("Reading Decoder", "📖", "Hoàn thành 500 XP Reading."),
    ("Writing Starter", "✍️", "Hoàn thành 300 XP Writing."),
    ("Speaking Brave Mode", "🗣️", "Hoàn thành 300 XP Speaking."),
    ("Error Killer", "⚔️", "Hoàn thành nhiều nhiệm vụ review lỗi."),
    ("Band 6 Challenger", "🥈", "Vượt qua giai đoạn tháng 7–12."),
    ("Band 7 Candidate", "🏆", "Hoàn thành mock tests giai đoạn cuối."),
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


def get_rank_level(xp: int) -> tuple[str, int]:
    for threshold, rank, level in RANK_THRESHOLDS:
        if xp >= threshold:
            return rank, level
    return "F", 1


def stage_for_week(week_no: int) -> str:
    if week_no <= 13:
        return "Tháng 1–3"
    if week_no <= 26:
        return "Tháng 4–6"
    if week_no <= 39:
        return "Tháng 7–9"
    if week_no <= 52:
        return "Tháng 10–12"
    return "Tháng 13–18"


def main_resources_for_stage(stage: str) -> dict[str, str]:
    if stage == "Tháng 1–3":
        return {
            "Listening": "Complete IELTS Band 5.0–6.5 + audio",
            "Reading": "Complete IELTS Band 5.0–6.5",
            "Writing": "English Grammar in Use + viết đoạn ngắn",
            "Speaking": "Complete IELTS Band 5.0–6.5",
            "Vocabulary": "English Vocabulary in Use Upper-Intermediate",
            "Collocation": "English Collocations in Use Intermediate",
            "Grammar": "English Grammar in Use + Cambridge Grammar for IELTS",
        }
    if stage == "Tháng 4–6":
        return {
            "Listening": "The Official Cambridge Guide to IELTS",
            "Reading": "IELTS Advantage Reading Skills",
            "Writing": "IELTS Advantage Writing Skills",
            "Speaking": "IELTS Advantage Speaking and Listening Skills",
            "Vocabulary": "English Vocabulary in Use Upper-Intermediate",
            "Collocation": "English Collocations in Use Intermediate",
            "Grammar": "Cambridge Grammar for IELTS",
        }
    if stage == "Tháng 7–9":
        return {
            "Listening": "Complete IELTS Bands 6.5–7.5 + IELTS Advantage S&L",
            "Reading": "IELTS Advantage Reading Skills + Complete IELTS 6.5–7.5",
            "Writing": "IELTS Advantage Writing Skills",
            "Speaking": "IELTS Advantage Speaking and Listening Skills",
            "Vocabulary": "IELTS Vocabulary for Bands 6.5 and above",
            "Collocation": "English Collocations in Use Intermediate",
            "Grammar": "Cambridge Grammar for IELTS",
        }
    if stage == "Tháng 10–12":
        return {
            "Listening": "Cambridge IELTS 17 + Complete IELTS 6.5–7.5",
            "Reading": "Cambridge IELTS 17 + IELTS Advantage Reading Skills",
            "Writing": "IELTS Advantage Writing Skills + Cambridge IELTS 17",
            "Speaking": "IELTS Advantage Speaking and Listening Skills",
            "Vocabulary": "Cambridge Academic Vocabulary in Use",
            "Collocation": "English Collocations in Use Advanced",
            "Grammar": "Cambridge Grammar for IELTS",
        }
    return {
        "Listening": "Cambridge IELTS 17 full tests",
        "Reading": "Cambridge IELTS 17 full tests",
        "Writing": "IELTS Advantage Writing Skills + weekly feedback",
        "Speaking": "IELTS Advantage S&L + mock speaking recordings",
        "Vocabulary": "IELTS Vocabulary 6.5+ review + Academic Vocabulary",
        "Collocation": "English Collocations in Use Advanced",
        "Grammar": "Cambridge Grammar for IELTS error-based review",
    }


def quest_templates(stage: str):
    r = main_resources_for_stage(stage)
    if stage == "Tháng 13–18":
        return [
            (0, "Full Listening Raid", "Listening", r["Listening"], "Làm full Listening test, chữa đáp án, nghe lại transcript và ghi lỗi distractor/spelling.", 60, "Main Quest"),
            (1, "Vocabulary Recovery", "Vocabulary", r["Vocabulary"], "Review 15–20 từ/cụm đã sai hoặc quên; đặt 3 câu cá nhân hóa.", 15, "Daily Quest"),
            (2, "Full Reading Dungeon", "Reading", r["Reading"], "Làm full Reading hoặc 2 passages trong 60 phút; phân tích câu sai và paraphrase.", 60, "Main Quest"),
            (3, "Grammar Error Repair", "Grammar", r["Grammar"], "Ôn đúng nhóm lỗi đang lặp lại trong Writing/Reading; viết 5 câu ứng dụng.", 15, "Daily Quest"),
            (4, "Writing Boss Draft", "Writing", r["Writing"], "Viết Task 2 hoặc Task 1 theo thời gian thật; tự sửa theo 4 tiêu chí IELTS.", 50, "Main Quest"),
            (5, "Speaking Arena", "Speaking", r["Speaking"], "Ghi âm Part 1 + Part 2 hoặc Part 3; nghe lại và ghi lỗi.", 35, "Daily Quest"),
            (6, "Weekly Status Review", "Collocation", r["Collocation"], "Review collocations dùng được cho bài viết/nói tuần này; cập nhật Error Log.", 20, "Review Quest"),
        ]
    return [
        (0, "Listening Gate", "Listening", r["Listening"], "Làm bài nghe theo unit, chữa transcript, ghi keyword/paraphrase và shadowing 5 câu.", 30, "Main Quest"),
        (1, "Vocabulary Crystal", "Vocabulary", r["Vocabulary"], "Học 10 từ/cụm mới, ghi nghĩa tiếng Việt, ví dụ và 1 paraphrase pair.", 15, "Daily Quest"),
        (2, "Reading Dungeon", "Reading", r["Reading"], "Làm bài đọc theo unit/dạng câu hỏi, chữa lỗi, phân tích 3–5 câu dài theo S–V–O.", 35, "Main Quest"),
        (3, "Grammar Forge", "Grammar", r["Grammar"], "Học 1 điểm ngữ pháp, làm bài tập ngắn và viết 3 câu ứng dụng.", 15, "Daily Quest"),
        (4, "Writing Scroll", "Writing", r["Writing"], "Viết câu/đoạn/Task theo giai đoạn; tự sửa lỗi thì, mạo từ, số ít/số nhiều và liên kết ý.", 35, "Main Quest"),
        (5, "Speaking Echo", "Speaking", r["Speaking"], "Ghi âm 2–3 câu Part 1 hoặc 1 cue card ngắn; nghe lại và ghi 3 lỗi.", 20, "Daily Quest"),
        (6, "Collocation Loot", "Collocation", r["Collocation"], "Học 1 nhóm collocations, chọn 5 cụm dùng được cho Writing/Speaking.", 20, "Review Quest"),
    ]


def seed_database(db: Session, start_date: date) -> None:
    if db.query(Player).count() > 0:
        return

    player = Player(start_date=start_date)
    db.add(player)

    skill_by_name = {}
    for name, icon, weak_point in SKILLS:
        skill = Skill(name=name, icon=icon, weak_point=weak_point)
        db.add(skill)
        skill_by_name[name] = skill

    for name, icon, description in BADGES:
        db.add(Badge(name=name, icon=icon, description=description))

    db.flush()

    total_weeks = 78
    for week_no in range(1, total_weeks + 1):
        stage = stage_for_week(week_no)
        week_start = start_date + timedelta(days=(week_no - 1) * 7)
        for day_offset, title, skill_name, source, details, xp, session_type in quest_templates(stage):
            db.add(
                Quest(
                    quest_date=week_start + timedelta(days=day_offset),
                    week_no=week_no,
                    stage=stage,
                    title=title,
                    skill_id=skill_by_name[skill_name].id,
                    source=source,
                    details=details,
                    xp=xp,
                    session_type=session_type,
                )
            )

    boss_weeks = [4, 13, 26, 39, 52, 65, 78]
    boss_titles = [
        "Month 1 Mini Boss: Listening + Reading Check",
        "Month 3 Foundation Boss: Grammar + Short Writing + Speaking Part 1",
        "Month 6 IELTS 5.5 Checkpoint",
        "Month 9 Band 6 Challenger",
        "Month 12 Cambridge IELTS 17 Gate",
        "Month 15 Mock Test Raid",
        "Month 18 Final IELTS Simulation",
    ]
    for week_no, title in zip(boss_weeks, boss_titles):
        stage = stage_for_week(week_no)
        battle_date = start_date + timedelta(days=(week_no * 7) - 1)
        db.add(
            BossBattle(
                stage=stage,
                battle_date=battle_date,
                title=title,
                source="Dashboard schedule + IELTS materials",
                goal="Hoàn thành bài kiểm tra, ghi điểm, phân tích lỗi và mở khóa nhiệm vụ giai đoạn tiếp theo.",
                status="Locked",
            )
        )

    db.commit()
