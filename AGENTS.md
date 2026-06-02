# Repository Guidelines

## Project name
IELTS Quest Dashboard

## Project purpose
This is a local gamified IELTS Academic self-study dashboard for an 18-month roadmap starting from 04/06/2026.

The user is a Vietnamese learner aiming for IELTS Academic 7.0–7.5 within 18 months. Current level is around B1, with Listening as the strongest skill and Reading weakness mainly caused by limited vocabulary and difficulty understanding long sentences.

## Tech stack
- Frontend: React + Vite
- Backend: FastAPI
- Database: MySQL
- Deployment: Docker Compose
- Runs locally only

## Core design direction
The UI should feel like a game status dashboard inspired by Solo Leveling:
- Dark fantasy / system interface style
- Neon blue or cyan highlights
- Status panel
- Skill rank from F to S
- XP, levels, quests, badges, boss battles
- Strong gamification to reduce boredom and help maintain study streaks

Do not copy copyrighted UI assets or exact protected designs. Use an original interface inspired by the general idea of game-like status screens.

## Main skills to track
1. Listening
2. Reading
3. Writing
4. Speaking
5. Vocabulary
6. Collocation
7. Grammar

Each skill must have:
- XP
- Level
- Rank: F, E, D, C, B, A, S
- Progress bar
- Last practiced date
- Weakness note

## XP system
XP is calculated by completed tasks, not by study time.

Example XP values:
- Learn 10 new words: +10 XP
- Review old vocabulary: +5 XP
- Complete one Listening task: +20 XP
- Review transcript: +15 XP
- Shadowing 5 sentences: +10 XP
- Complete one Reading passage: +25 XP
- Analyze 5 long sentences: +15 XP
- Write one paragraph: +25 XP
- Write one full Writing Task 2: +50 XP
- Record Speaking Part 1: +15 XP
- Record Speaking Part 2: +25 XP
- Full Listening test: +60 XP
- Full Reading test: +60 XP
- Add corrected mistake to Error Log: +10 XP

## Study roadmap phases
The roadmap starts on 04/06/2026 and is divided into:

1. Month 1–3
2. Month 4–6
3. Month 7–9
4. Month 10–12
5. Month 13–18

## Learning resources
The user already has:
- IELTS Advantage - Speaking and Listening Skills (Ebook + Audio)
- Cambridge Grammar for IELTS
- English Grammar in Use
- IELTS Advantage Reading Skills
- Cambridge IELTS 17
- Complete IELTS Bands 6.5–7.5
- Complete IELTS Band 5.0–6.5
- The Official Cambridge Guide to IELTS
- English Collocations in Use Intermediate
- English Vocabulary in Use Upper-Intermediate
- IELTS Vocabulary for Bands 6.5 and above
- Cambridge Academic Vocabulary in Use
- English Collocations in Use Advanced
- IELTS Advantage Writing Skills

## Required main features
1. Dashboard / Player Profile
2. Skill Progress panel
3. Quest Board
4. Daily Quest
5. Weekly Mission
6. Boss Battle
7. Badge Wall
8. Mood / Energy Check-in
9. Error Log
10. Writing Tracker
11. Speaking Tracker
12. Mock Test Tracker

## Mood / Energy tracking
Each day should allow the user to record:
- Mood
- Energy level
- Focus level
- Short note

This is used to help the user understand which days are productive or tiring.

## Design requirements
- Strong gamified feeling
- Rank display must use F → E → D → C → B → A → S
- Progress should be visual, not only numeric
- Dashboard should feel rewarding and motivating
- Avoid clutter
- Vietnamese UI labels are preferred
- English technical terms may appear, but should be understandable

## Development expectations
When modifying the project:
1. Explain the change briefly.
2. Keep the app runnable with Docker Compose.
3. Do not remove existing features unless requested.
4. Prefer clean, simple, maintainable code.
5. Update seed data carefully.
6. Test backend syntax when possible.
7. Keep frontend responsive for laptop screens.

## Useful commands
Run the full project:

```bash
docker compose up --build
```
## Local development URLs

When the project is running with Docker Compose:

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- MySQL host: localhost
- MySQL port: 3307

Use these URLs to understand how the local app is accessed.