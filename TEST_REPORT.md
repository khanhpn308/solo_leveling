# Test Report

Last updated: 2026-06-05

## Current Runtime Snapshot

- Frontend home dashboard redesign is complete.
- `reviewer-gpt55`: `ACCEPT`.
- `npm.cmd run build`: passed.
- `npm.cmd run test:dashboard-data`: passed.
- `5 tests, 0 failures`.
- No browser screenshot or DOM walkthrough was captured.

## Scope

- Verify the completed frontend-only home dashboard redesign.
- Confirm that the redesign did not require API, schema, or Docker Compose changes.
- Record the validation that was actually run.

## Validation Notes

- The redesign uses existing backend endpoints for suggestion inbox actions and certificate records.
- No API contract changes were introduced.
- No database/schema changes were introduced.
- No Docker Compose changes were introduced.

## Commands Run

```powershell
npm.cmd run build
npm.cmd run test:dashboard-data
```

## Results

- `npm.cmd run build`: passed.
- `npm.cmd run test:dashboard-data`: passed.
- Automated data tests: `5 tests, 0 failures`.

## Remaining Frontend Verification Gap

- No browser visual walkthrough was captured.
- No screenshot-based confirmation of spacing, density, or overlay behavior is available in this report.

## Wave A Backend Validation Snapshot

### Scope

- Validate the first backend migration wave for campaign-scope and typed-link hardening.
- Confirm syntax health for the new migration plus touched FastAPI backend files.
- Record remaining runtime gaps before the next implementation slice.

### Commands Run

```powershell
python -m py_compile backend\app\main.py backend\app\models.py backend\app\schemas.py backend\app\services.py backend\alembic\versions\20260605_05_wave_a_scope_links.py
python -m pip install -r backend\requirements.txt
python -m alembic upgrade head
alembic upgrade head
python -c "from alembic.config import Config; from alembic import command; cfg=Config(r'alembic.ini'); cfg.set_main_option('sqlalchemy.url', 'mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest'); command.upgrade(cfg, 'head')"
@'
from sqlalchemy import create_engine, text
engine = create_engine('mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest')
checks = {
    'revision': 'SELECT version_num FROM alembic_version',
    'checkins_campaign': "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='checkins' AND COLUMN_NAME='campaign_id'",
    'quests_daily_slot': "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='quests' AND COLUMN_NAME='daily_slot_code'",
    'weakness_source_test': "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='weakness_suggestions' AND COLUMN_NAME='source_test_record_id'",
}
with engine.connect() as conn:
    for label, sql in checks.items():
        print(label, conn.execute(text(sql)).fetchall())
'@ | python -
curl.exe -s http://localhost:8000/api/health
curl.exe -s http://localhost:8000/api/checkins
curl.exe -s http://localhost:8000/api/test-records
```

### Results

- `python -m py_compile ...`: passed.
- `python -m pip install -r backend\requirements.txt`: passed.
- `python -m alembic upgrade head`: failed because the environment does not expose `alembic.__main__`.
- `alembic upgrade head`: failed because the `alembic` executable is not available on the current PATH.
- `python -c "... command.upgrade(..., 'head')"` from `backend/` with `sqlalchemy.url=...@localhost:3307/...`: passed.
- Read-only post-upgrade verification against MySQL: passed.
- Read-only API smoke checks for `/api/health`, `/api/checkins`, and `/api/test-records`: passed.

### Remaining Backend Verification Gap

- No functional verification has been run yet for fresh writes into the new nullable columns from FastAPI endpoints.

### Important Interpretation Note

- Existing rows in `/api/checkins` and `/api/test-records` still show `campaign_id = null`.
- This is expected in the current rollout because Wave A intentionally adds nullable scope columns first.
- Historical `campaign_id` backfill remains scheduled for Wave C.

## Wave B Backend Validation Snapshot

### Scope

- Validate the additive Wave B schema changes for campaign skill state and badge unlock tables.
- Confirm syntax health for touched backend files.
- Confirm the local MySQL database reaches the new Alembic head and the new tables are still empty.
- Record the translation-sync gap that remains outside the Python seed file.

### Commands Run

```powershell
python -m py_compile backend\app\main.py backend\app\models.py backend\app\services.py backend\app\seed.py backend\alembic\versions\20260605_06_wave_b_state_tables.py
python -c "from alembic.config import Config; from alembic import command; cfg=Config(r'alembic.ini'); cfg.set_main_option('sqlalchemy.url', 'mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest'); command.upgrade(cfg, 'head')"
curl.exe -s http://localhost:8000/api/skills
curl.exe -s http://localhost:8000/api/badges
@'
from sqlalchemy import create_engine, text
engine = create_engine('mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest')
with engine.connect() as conn:
    print('revision', conn.execute(text("SELECT version_num FROM alembic_version")).fetchall())
    print('campaign_skill_states_table', conn.execute(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='campaign_skill_states'")).fetchall())
    print('badge_unlocks_table', conn.execute(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='badge_unlocks'")).fetchall())
    print('campaign_skill_states_count', conn.execute(text("SELECT COUNT(*) FROM campaign_skill_states")).scalar())
    print('badge_unlocks_count', conn.execute(text("SELECT COUNT(*) FROM badge_unlocks")).scalar())
'@ | python -
@'
from sqlalchemy import create_engine, text
engine = create_engine('mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest')
queries = {
    'campaign_skill_states_indexes': "SELECT INDEX_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='campaign_skill_states' ORDER BY INDEX_NAME",
    'badge_unlocks_indexes': "SELECT INDEX_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA='ielts_quest' AND TABLE_NAME='badge_unlocks' ORDER BY INDEX_NAME",
}
with engine.connect() as conn:
    for name, sql in queries.items():
        print(name, conn.execute(text(sql)).fetchall())
'@ | python -
```

### Results

- `python -m py_compile ...`: passed.
- Wave B Alembic upgrade with host-side URL override from `backend/`: passed.
- Read-only MySQL verification for revision/table existence/counts: passed.
- Read-only MySQL verification for named indexes/unique constraints: passed.
- Read-only API calls to `/api/skills` and `/api/badges`: reachable, but still returned old Vietnamese seed text from existing rows in the current running environment.

### Remaining Backend Verification Gap

- No empty/resettable-DB validation has been run yet for Wave B.
- No `/api/dev/reset` validation has been run yet for the new child-table delete order.
- No reliable live API verification has been run yet against a restarted backend process that has loaded the new seed-sync logic.
- `material.md` still contains Vietnamese study-plan source text, so English-only backend text is not complete yet.

## Wave B Reset + English Seed Smoke

### Scope

- Validate the translated `material.md` source in the live backend seed flow.
- Validate backend restart + `/api/dev/reset` after the Wave B table additions.
- Confirm key seed-backed endpoints now return English text.

### Commands Run

```powershell
Get-Content -Encoding UTF8 material.md -TotalCount 70
rg -n "^\#\# " material.md
python -m pip install deep-translator
@'
... translation pass for material.md ...
'@ | py -3.13 -
rg -n "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]" material.md
docker restart ielts_quest_backend
curl.exe -s http://localhost:8000/api/health
curl.exe -i -s -X POST http://localhost:8000/api/dev/reset
@'
... SQLAlchemy delete-order repro script ...
'@ | py -3.13 -
python -m py_compile backend\app\main.py
curl.exe -s http://localhost:8000/api/skills
curl.exe -s http://localhost:8000/api/badges
curl.exe -s http://localhost:8000/api/materials
curl.exe -s http://localhost:8000/api/roadmap/phases
curl.exe -s http://localhost:8000/api/weekly-mission/current
```

### Results

- `material.md` translation pass: completed.
- Accent-character scan on `material.md`: clean after the second pass.
- Backend restart: passed.
- `/api/health`: passed after restart.
- Initial `/api/dev/reset`: failed with HTTP 500.
- Root cause repro via host-side SQLAlchemy script: `players.active_campaign_id` blocked `Campaign` deletion.
- Reset fix in `backend/app/main.py`: passed after setting `Player.active_campaign_id = null` before delete loop.
- `python -m py_compile backend\app\main.py`: passed.
- `/api/dev/reset`: passed after fix.
- `/api/skills`: passed, shape unchanged, English text returned.
- `/api/badges`: passed, shape unchanged, English text returned.
- `/api/materials`: passed, English text returned.
- `/api/roadmap/phases`: passed, English text returned.
- `/api/weekly-mission/current`: passed, English text returned.

### Remaining Backend Verification Gap

- `material.md` is now English-only at the character level, but some generated phrasing is still awkward and may need manual polishing later.
- Empty-DB migration validation for Wave B is still not separately isolated from the normal local seeded database flow.

## Wave E Constraint Hardening Validation

### Scope

- Validate Wave E write-path hardening before schema enforcement.
- Validate Wave E Alembic migration to `20260606_08`.
- Validate post-migration SQL integrity and backend endpoint behavior.

### Commands Run

```powershell
python -m py_compile backend\app\main.py backend\app\models.py backend\app\seed.py backend\alembic\versions\20260606_08_wave_e_constraint_hardening.py
@'
import os
os.environ['DATABASE_URL'] = 'mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest'
from app.database import SessionLocal
from app.main import reset_database
from app.models import Quest, TestRecord

db = SessionLocal()
try:
    result = reset_database(db=db)
    daily_slot_null = db.query(Quest).filter(Quest.session_type == 'Daily Quest', Quest.quest_role.in_(['core', 'support', 'mini']), Quest.daily_slot_code.is_(None)).count()
    null_test_campaign = db.query(TestRecord).filter(TestRecord.campaign_id.is_(None)).count()
    print({'reset_result': result, 'daily_slot_null': daily_slot_null, 'null_test_campaign': null_test_campaign})
finally:
    db.close()
'@ | python -
@'
from alembic.config import Config
from alembic import command
cfg = Config(r'alembic.ini')
cfg.set_main_option('sqlalchemy.url', 'mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest')
command.upgrade(cfg, 'head')
print('upgrade_ok')
'@ | python -
@'
import pymysql
conn = pymysql.connect(host='localhost', port=3307, user='ielts_user', password='ielts_password', database='ielts_quest', charset='utf8mb4')
cur = conn.cursor()
...
'@ | python -
$env:DATABASE_URL='mysql+pymysql://ielts_user:ielts_password@localhost:3307/ielts_quest'
$proc = Start-Process python -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8010' -WorkingDirectory 'D:\better_english\ielts-quest-dashboard\backend' -WindowStyle Hidden -PassThru
...
Invoke-WebRequest http://127.0.0.1:8010/api/health
Invoke-WebRequest http://127.0.0.1:8010/api/checkins
Invoke-WebRequest -Method POST http://127.0.0.1:8010/api/checkins
Invoke-WebRequest http://127.0.0.1:8010/api/summary
Invoke-WebRequest http://127.0.0.1:8010/api/weekly-mission/current
Invoke-WebRequest http://127.0.0.1:8010/api/quests/today
Invoke-WebRequest -Method POST http://127.0.0.1:8010/api/dev/reset
```

### Results

- `python -m py_compile`: passed.
- Pre-migration reset logic using the current backend code: passed.
- Pre-migration seed safety checks:
  - daily quest rows with `daily_slot_code is null`: `0`
  - seeded `test_records` with `campaign_id is null`: `0`
- Wave E Alembic upgrade to `20260606_08`: passed.
- Post-migration SQL checks: passed.
- `SHOW CREATE TABLE` verification: passed.
- Live HTTP smoke on `127.0.0.1:8010`: passed.

### Post-Migration SQL Audit

- `checkins.campaign_id is null`: `0`
- `test_records.campaign_id is null`: `0`
- `skill_rank_suggestions.campaign_id is null`: `0`
- `skill_rank_history.campaign_id is null`: `0`
- `weakness_suggestions.campaign_id is null`: `0`
- `quests.campaign_id is null`: `0`
- daily quest `daily_slot_code is null`: `0`
- duplicate `(campaign_id, checkin_date)` rows: `0`
- duplicate `(campaign_id, quest_date, daily_slot_code)` daily quests: `0`

### HTTP Smoke Result

- `/api/health`: `200`
- `/api/checkins` GET: `200`
- `/api/checkins` POST create: `200`
- `/api/checkins` POST update: `200`
- `/api/summary`: `200`
- `/api/weekly-mission/current`: `200`
- `/api/quests/today`: `200`
- `/api/dev/reset`: `200`

### Remaining Backend Verification Gap

- Automated backend tests for Wave D/Wave E behavior are still missing.
- Validation used live local smoke plus SQL audit; there is still no dedicated integration test suite in the repo.
