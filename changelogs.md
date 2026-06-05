## [2026-06-04 00:06] Sửa lỗi frontend Failed to fetch do bộ phân tích seed của backend

**Agent:** coder-gpt54  
**Status:** Partially done  
**Related task:** Sửa lỗi hiện tại ở frontend `API ERROR: Failed to fetch`

### 1. Tóm tắt

Đã sửa đúng nguyên nhân khiến frontend fetch thất bại bằng cách vá bộ phân tích seed khi backend khởi động. Các dòng session trong `material.md` lưu timestamp dạng `YYYY-MM-DD 00:00:00`, nhưng `parse_material_plan()` trước đó tách trường này như thể chỉ là ngày thuần, làm FastAPI crash khi khởi động và seed dữ liệu.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `backend/app/seed.py` | Chỉnh sửa | `L557-L565`, `L572-L611` | Gia cố phần parse khoảng ngày của roadmap và sửa logic parse timestamp của study session bằng `date.fromisoformat(cols[1].split()[0])` để seed lúc khởi động không còn bị crash. |
| `TASKS.md` | Chỉnh sửa | Các mục `Completed`, `In Progress`, `Known Issues / Risks`, `Next Candidate Tasks` khoảng `L21-L76` | Ghi lại nguyên nhân gốc cụ thể, kết quả xác minh API hiện tại và phần thiếu xác thực Docker/MySQL CLI còn lại. |
| `TEST_REPORT.md` | Chỉnh sửa | `L1-L107` | Thay ghi chú runtime đang chờ trước đó bằng phân tích nguyên nhân gốc hiện tại, các lệnh đã chạy, xác minh parser và kết quả endpoint đang hoạt động. |
| `changelogs.md` | Thêm mới | `L1-L54` | Thêm mục báo cáo triển khai này theo đúng format yêu cầu trong AGENTS. |

### 3. Tính năng đã thêm

- [ ] Không có

### 4. Lỗi đã sửa

- [x] Đã sửa lỗi backend crash khi khởi động do parse timestamp session trong `material.md` như ngày thuần.
- [x] Đã khôi phục việc frontend gọi API thành công bằng cách đưa `/api/health`, `/api/summary`, `/api/quests`, `/api/main-quests`, và `/api/study-plan/current-week` trở lại HTTP 200.

### 5. Mã đã loại bỏ

- [x] Không có

### 6. Lệnh đã chạy

```bash
Get-Content AGENTS.md
Get-Content TASKS.md
Get-Content TEST_REPORT.md
if (Test-Path changelogs.md) { Get-Content changelogs.md }
Get-Content C:\Users\Admin\.agents\skills\codex-implementation-worker\SKILL.md
Get-Content docker-compose.yml
Get-Content backend\app\main.py
Get-Content backend\app\database.py
Get-Content backend\app\seed.py
Get-Content frontend\src\App.jsx
Get-ChildItem backend\alembic\versions | Select-Object -ExpandProperty FullName
docker --version
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/health
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/summary
Get-Content backend\alembic\versions\20260603_01_mvp_additive_schema.py
Get-Content backend\alembic\versions\20260603_02_roadmap_material_mapping.py
Get-Content backend\alembic\versions\20260603_03_main_quest_plan_tables.py
netstat -ano | Select-String ':8000'
Get-Process -Id 4436 | Select-Object Id,ProcessName,Path
Get-Process -Id 8964 | Select-Object Id,ProcessName,Path
Get-Content backend\requirements.txt
curl.exe -v http://localhost:8000/api/health
curl.exe -v http://127.0.0.1:8000/api/health
curl.exe -v http://localhost:5173
python -m py_compile <backend/app python files>
python -m py_compile <backend/alembic python files>
python - <isolated AST parser verification>
python - <urllib endpoint/status verification>
mysql --version
git status --short
git diff --stat
git diff --unified=0 -- backend/app/seed.py TASKS.md TEST_REPORT.md changelogs.md
Get-Date -Format 'yyyy-MM-dd HH:mm'
```

### 7. Kết quả kiểm tra

- [x] Đạt
- [ ] Thất bại
- [ ] Chưa chạy

Chi tiết:

```text
backend/app py_compile: passed
backend/alembic py_compile: passed
isolated parse_material_plan(): weeks=78, sessions=312
/api/health: 200
/api/summary: 200
/api/quests: 200
/api/main-quests: 200
/api/study-plan/current-week: 200
API-derived counts: total_quests=1638, total_main_quests=312, total_study_plan_weeks=78
Docker CLI không khả dụng trong shell này
MySQL CLI không khả dụng trong shell này
```

### 8. Vấn đề còn lại

- [ ] Vẫn chưa thể xác minh trực tiếp bằng Docker Compose trong shell này vì `docker` CLI chưa được cài ở đây.
- [ ] Vẫn chưa thể kiểm tra trực tiếp số lượng bản ghi bằng MySQL trong shell này vì `mysql` CLI chưa được cài ở đây.

### 9. Bước tiếp theo được đề xuất

- Chạy thêm một lượt xác minh có Docker để lấy log backend và số lượng bản ghi trực tiếp từ MySQL, dù API local đang hoạt động ổn định trở lại.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 21:53] Frontend UI English localization pass

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Convert the current UI copy fully to English

### 1. Summary

Converted the active frontend UI copy from Vietnamese to English across dashboard panels, overlays, roadmap/main quest views, suggestion inbox, status/check-in surfaces, and certificate/weekly mission states. Also cleaned a few mojibake separators so the UI no longer shows broken encoding glyphs.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/dashboard-data.js` | Modified | diff hunks around `TRACKER_MODULES`, `MAIN_QUEST_PHASES`, `WEEKLY_MISSION_PATTERNS`, `getMainQuestStatusMeta`, `getSessionIntegrity`, `getSessionXpMeta`, `getCurrentPhaseLabel`, `buildWeaknessSuggestions`, `buildSuggestionInbox` | Converted derived UI labels/details to English so view-model data matches the new UI copy. |
| `frontend/src/App.jsx` | Modified | diff hunk around stat cards + weekly mission loading | Converted streak/day strings and weekly mission loading copy to English. |
| `frontend/src/components/DailyQuestPanel.jsx` | Modified | `statusLabel`, backlog header/list area | Converted daily/backlog labels to English. |
| `frontend/src/components/MainQuestMapPanel.jsx` | Modified | full component rewrite, main quest map sections | Converted all map labels/states to English and replaced broken separators with ASCII-safe copy. |
| `frontend/src/components/RoadmapHero.jsx` | Modified | full component rewrite, hero + phase overlay | Converted hero/phase overlay copy to English and removed mojibake separators. |
| `frontend/src/components/QuestOverlay.jsx` | Modified | main/archive quest states | Converted overlay copy to English. |
| `frontend/src/components/StatusModal.jsx` | Modified | check-in, badge, history sections | Converted status modal helper copy and empty states to English. |
| `frontend/src/components/CheckInPanel.jsx` | Modified | full component rewrite | Converted check-in UI to English and replaced broken star/separator glyphs with safe ASCII output. |
| `frontend/src/components/CampaignPanel.jsx` | Modified | campaign metrics and labels | Converted campaign/streak labels to English. |
| `frontend/src/components/CommandHeader.jsx` | Modified | hero subtitle and timeline fallback | Converted header copy to English. |
| `frontend/src/components/SetupSummaryPanel.jsx` | Modified | title/tag/setup cards | Converted setup panel copy to English. |
| `frontend/src/components/CertificateOverlay.jsx` | Modified | loading/empty/note fallback | Converted certificate overlay state copy to English. |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Modified | loading/empty states | Converted inbox dropdown copy to English. |
| `frontend/src/components/SuggestionInboxPanel.jsx` | Modified | empty state | Converted suggestion inbox panel copy to English. |
| `frontend/src/components/WeeklyMissionCard.jsx` | Modified | empty state | Converted weekly mission fallback copy to English. |
| `frontend/src/components/WeeklyMissionPanel.jsx` | Modified | progress label | Converted weekly mission summary copy to English. |
| `frontend/src/components/BossOverlay.jsx` | Modified | empty state | Converted boss overlay empty state to English. |
| `frontend/src/components/BossTimelinePanel.jsx` | Modified | timeline tag/date line | Converted timeline tag to English and replaced broken separator glyphs. |
| `frontend/src/dashboard-data.test.js` | Modified | assertions around main quest map text | Updated string-based expectations to match the new English view-model copy. |
| `changelogs.md` | Modified | tail entry | Added this task record. |

### 3. Features added

- [x] Full English UI copy pass across active dashboard panels and overlays.
- [x] Cleaned broken encoding separators in roadmap, boss timeline, check-in, and main quest map surfaces.

### 4. Bugs fixed

- [x] Suggestion, weekly mission, certificate, and quest/map fallback states no longer show Vietnamese copy.
- [x] Several mojibake sequences like `Â·` no longer appear in visible UI copy.
- [x] Dashboard-data test expectations now match the new English UI-derived strings.

### 5. Code removed

- [x] Removed leftover Vietnamese / mojibake copy from active frontend surfaces.
- [ ] None

### 6. Commands run

```bash
rg -n "..." frontend/src
Get-Content frontend/src/components/CertificateOverlay.jsx
Get-Content frontend/src/components/SuggestionInboxDropdown.jsx
Get-Content frontend/src/components/WeeklyMissionCard.jsx
Get-Content frontend/src/components/BossTimelinePanel.jsx
Get-Content frontend/src/components/CommandHeader.jsx
Get-Content frontend/src/components/SetupSummaryPanel.jsx
Get-Content frontend/src/components/SuggestionInboxPanel.jsx
Get-Content frontend/src/components/WeeklyMissionPanel.jsx
Get-Content frontend/src/dashboard-data.test.js
Get-Content frontend/src/dashboard-data.js
git diff --stat -- frontend/src changelogs.md
git diff --unified=0 -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/dashboard-data.test.js frontend/src/components/BossOverlay.jsx frontend/src/components/BossTimelinePanel.jsx frontend/src/components/CampaignPanel.jsx frontend/src/components/CertificateOverlay.jsx frontend/src/components/CheckInPanel.jsx frontend/src/components/CommandHeader.jsx frontend/src/components/DailyQuestPanel.jsx frontend/src/components/MainQuestMapPanel.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/RoadmapHero.jsx frontend/src/components/SetupSummaryPanel.jsx frontend/src/components/StatusModal.jsx frontend/src/components/SuggestionInboxDropdown.jsx frontend/src/components/SuggestionInboxPanel.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/WeeklyMissionPanel.jsx
npm.cmd run build
npm.cmd run test:dashboard-data
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
manual source scan: no Vietnamese copy matches remained in frontend/src for the searched patterns
```

### 8. Remaining issues

- [ ] No browser-side visual review was run in this pass.
- [ ] Date formatting still uses numeric local format; wording is English, but locale-specific date style was not changed in this task.

### 9. Suggested next step

- If you want the app fully English in presentation as well as wording, the next pass should standardize date/time formatting and review screenshots for any backend-provided Vietnamese content that may still appear at runtime.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 10:20] Task tracker refresh for remaining documentation work

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Record the current unfinished task in the repository tracker

### 1. Summary

Refreshed `TASKS.md` so the current remaining work is explicit in the repo tracker. The in-progress section now calls out the pending browser verification and the follow-up schema-semantics note, and the next-candidate list now points at a companion doc for enum-like field meanings.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `TASKS.md` | Modified | top-state sections around `L1-L75` | Updated the session state, added the remaining documentation task to `In Progress`, and changed the next-candidate list to the schema semantics note. |
| `changelogs.md` | Modified | new tail entry | Added this task record. |

### 3. Features added

- [x] Current unfinished task is now documented in the repo tracker.

### 4. Bugs fixed

- [x] Removed ambiguity about what remains open after the current schema/documentation pass.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content TASKS.md
Get-Content AGENT_NOTES.md
Get-Content TEST_REPORT.md
Get-Content changelogs.md -Tail 120
Get-Date -Format "yyyy-MM-dd HH:mm"
git diff --unified=0 -- TASKS.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
This was a documentation-only update. No runtime validation was required.
TASKS.md now includes the remaining open work explicitly.
```

### 8. Remaining issues

- [ ] The browser verification task is still pending.
- [ ] The schema-semantics companion note is still only a next candidate, not yet written.

### 9. Suggested next step

- If you want the tracker fully caught up, write the companion schema-semantics note next.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 10:09] Database schema inventory documentation

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Inspect the current MySQL database and document all tables and columns

### 1. Summary

Inspected the live local MySQL database schema from the running Docker container, cross-checked it against `backend/app/models.py`, and added a dedicated schema reference document. The new doc lists every current table in `ielts_quest`, its columns, types, nullability, key role, notable unique constraints, and the main foreign-key relationships.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/DATABASE_SCHEMA.md` | Added | Full file `L1-L390` | Added a live schema snapshot for the `ielts_quest` database including table inventory, field lists, unique constraints, and relationship summary. |
| `changelogs.md` | Modified | new tail entry | Added this task record. |

### 3. Features added

- [x] Dedicated database schema reference document for the project.
- [x] Live table inventory pulled from the running MySQL instance.
- [x] Column-by-column listing for all current database tables.

### 4. Bugs fixed

- [x] Removed ambiguity around which tables and fields currently exist in the local database.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content C:\Users\Admin\.agents\skills\backend-development\SKILL.md -TotalCount 120
Get-Content C:\Users\Admin\.agents\skills\agent-skills\skills\documentation-and-adrs\SKILL.md -TotalCount 120
Get-ChildItem backend\app
Get-ChildItem backend\alembic\versions
rg -n "class .*\(Base\)|__tablename__|Column\(|mapped_column\(|ForeignKey\(|relationship\(" backend/app backend/alembic/versions
docker compose ps
Get-Content docker-compose.yml
Get-Content backend/app/models.py -TotalCount 260
Get-Content backend/app/models.py | Select-Object -Skip 260 -First 280
docker compose exec -T mysql mysql -uielts_user -pielts_password -D ielts_quest -e "SHOW TABLES;"
docker compose exec -T mysql mysql -uielts_user -pielts_password -D ielts_quest -e "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'ielts_quest' ORDER BY TABLE_NAME, ORDINAL_POSITION;"
docker compose exec -T mysql mysql -uielts_user -pielts_password -D ielts_quest -e "SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = 'ielts_quest' AND REFERENCED_TABLE_NAME IS NOT NULL ORDER BY TABLE_NAME, COLUMN_NAME;"
docker compose exec -T mysql mysql -uielts_user -pielts_password -D ielts_quest -e "SELECT TABLE_NAME, INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS columns, NON_UNIQUE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = 'ielts_quest' GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE ORDER BY TABLE_NAME, INDEX_NAME;"
Get-ChildItem docs -Recurse
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Verified against the live `ielts_quest_mysql` container and `information_schema`.
Detected 24 current tables in schema `ielts_quest`.
Cross-check against `backend/app/models.py` completed.
No code/runtime validation was needed beyond schema inspection because this task only adds documentation.
```

### 8. Remaining issues

- [ ] The new document is a point-in-time snapshot and should be refreshed after future migrations.
- [ ] Business semantics for status fields are not yet documented separately.

### 9. Suggested next step

- Add a follow-up doc that explains status enums / field semantics and optionally generate a small ERD diagram.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 10:09] Daily quest claim button layout containment fix

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Fix daily quest `CLAIM` button overflow in the Quest Board daily tab

### 1. Summary

Adjusted the daily quest reward column so the `CLAIM` action stays fully inside the XP panel instead of overflowing past the right border. The fix widens the reward column to a stable minimum, makes the action button fill that column, and centers the XP text within the updated layout.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/styles.css` | Modified | `quest-node` and `quest-node__reward` layout block around `L1090-L1160` | Increased the daily quest reward-column width, added left padding inside the reward column, centered reward text, and made `.quest-action-button` stretch to the column width without forcing overflow. |
| `changelogs.md` | Modified | new tail entry | Added this task record. |

### 3. Features added

- [x] Daily quest claim action now remains visually contained within the XP column.

### 4. Bugs fixed

- [x] Fixed the `CLAIM` button border overflowing outside the daily quest reward column.

### 5. Code removed

- [x] Removed the old narrow reward-column constraint that was smaller than the action button.
- [ ] None

### 6. Commands run

```bash
Get-Content C:\Users\Admin\.agents\skills\frontend-design\SKILL.md -TotalCount 120
Get-Content C:\Users\Admin\.agents\skills\vercel-react-best-practices\SKILL.md -TotalCount 120
rg -n "backlog-item__actions|quest-action-button|daily-quest-card|xp" frontend/src/components/DailyQuestPanel.jsx frontend/src/styles.css
Get-Content frontend/src/components/DailyQuestPanel.jsx
Get-Content frontend/src/styles.css | Select-Object -Skip 1080 -First 160
Get-Content frontend/src/styles.css | Select-Object -Skip 1150 -First 90
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Static inspection confirms the reward column is now wider than the claim button minimum width and the button is constrained to 100% of that column.
Frontend build re-run completed successfully after the CSS fix.
Manual browser screenshot verification is still pending in this environment.
```

### 8. Remaining issues

- [ ] Manual browser verification is still needed to confirm the refined spacing feels right on the live daily tab.

### 9. Suggested next step

- Open the daily quest overlay in the browser and verify `COMPLETE`, `CLAIM`, and `CLAIMED` states across both desktop and narrow laptop widths.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 07:52] Quest surfaces English cleanup

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Convert the remaining daily / weekly / main quest UI copy fully to English

### 1. Summary

Cleaned the remaining quest-surface wording so the `main`, `daily`, and `archive` quest views no longer show mixed separators or leftover non-English-looking copy. Also normalized the current phase label generated from `dashboard-data.js`.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/components/DailyQuestPanel.jsx` | Modified | full component rewrite | Replaced broken separators with ASCII-safe `/`, adjusted the panel tag to `daily clears`, and kept all daily/backlog text consistently English. |
| `frontend/src/components/QuestOverlay.jsx` | Modified | full component rewrite | Cleaned `Current Main Quest` and archive metadata lines so they use English-only copy and safe separators. |
| `frontend/src/dashboard-data.js` | Modified | `getCurrentPhaseLabel()` | Normalized phase labels from `Month X-Y · ...` mojibake output to clean English `Month X-Y / ...`. |
| `changelogs.md` | Modified | tail entry | Added this task record. |

### 3. Features added

- [x] Quest overlays now use consistent English-only metadata separators.
- [x] Current phase labels for quest-related views are now clean English strings.

### 4. Bugs fixed

- [x] Daily quest cards no longer show broken `Â·` separators.
- [x] Main quest overlay header no longer shows mixed/broken separators.
- [x] Archive quest lines no longer show mixed/broken separators.

### 5. Code removed

- [x] Removed leftover broken separator glyphs from quest-related UI copy.
- [ ] None

### 6. Commands run

```bash
rg -n "..." frontend/src/components/DailyQuestPanel.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/MainQuestMapPanel.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/WeeklyMissionPanel.jsx frontend/src/dashboard-data.js
npm.cmd run build
npm.cmd run test:dashboard-data
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
manual source scan: the targeted quest surfaces no longer contain the broken separator copy that was still visible in runtime
```

### 8. Remaining issues

- [ ] Weekly mission content coming from backend payloads can still vary in wording, but the frontend surface copy is now English.
- [ ] No browser-automation screenshot pass was run in this fix.

### 9. Suggested next step

- Reload the Quest overlay and inspect the `Main`, `Daily`, `Weekly`, and `Archive` tabs. If any non-English text remains, it is likely backend-provided content and should be traced from the payload next.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 07:44] Status hero metric alignment tweak

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Center Level / Rank / Target content inside the status hero metric cards

### 1. Summary

Centered the content inside the `Level`, `Rank`, and `Target` cards in the status hero so labels and values sit cleanly in the middle of each card.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/styles.css` | Modified | `status-core__metrics article` block | Added centered grid alignment and centered text for the hero metric cards; also normalized the label spacing. |
| `changelogs.md` | Modified | tail entry | Added this task record. |

### 3. Features added

- [x] Centered layout for `Level`, `Rank`, and `Target` inside the status hero cards.

### 4. Bugs fixed

- [x] The `Rank F` and `Target 7.0-7.5` content no longer sits off-center inside their cards.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
npm.cmd run build
npm.cmd run test:dashboard-data
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
```

### 8. Remaining issues

- [ ] Final visual balance still depends on runtime review after reload.

### 9. Suggested next step

- Reload the status modal and inspect the three hero cards; if the target card still feels optically low, the next tweak should reduce its font size slightly and increase top padding by 2-4px only for non-neon values.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 07:39] Status modal layout polish and framing fix

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Fix the status modal framing artifact and improve B1 Awakener layout balance

### 1. Summary

Adjusted the status modal layout so the large translucent frame no longer wraps the top two sections, enlarged the portrait block, compacted the Level / Rank / Target cards, and centered the Mood / Energy / Focus values for a cleaner game-panel presentation.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/styles.css` | Modified | `status modal` block around `overlay-frame--status`, `status-shell__hero`, `status-avatar`, `status-core__metrics`, `status-condition-card` | Disabled the extra overlay inner frame for the status modal, widened the portrait column, reduced the metric card footprint, and centered the daily-condition cards. |
| `frontend/src/components/StatusModal.jsx` | Modified | recent check-in section near the bottom of the component | Replaced the remaining dot separator in recent check-in stats with ASCII-safe slash separators for visual consistency. |
| `changelogs.md` | Modified | tail entry | Added this task record. |

### 3. Features added

- [x] Status overlay no longer renders the extra inner frame around the top layout.
- [x] The B1 Awakener hero block now gives more visual weight to the portrait area.
- [x] Mood / Energy / Focus cards now center their values and labels more cleanly.

### 4. Bugs fixed

- [x] Removed the large faint framing artifact that visually wrapped the top two panels.
- [x] Prevented the top layout from feeling oversized relative to the lower Badge Wall and Recent Check-ins cards.
- [x] Cleaned the remaining recent-checkin separator style inside the modal.

### 5. Code removed

- [x] Removed the status modal's extra `overlay-frame::before` inner border treatment.
- [ ] None

### 6. Commands run

```bash
Get-Content frontend/src/components/StatusModal.jsx
Get-Content frontend/src/styles.css
Get-Content frontend/src/components/OverlayFrame.jsx
rg -n "status-modal|status-shell__hero|overlay-frame--status" frontend/src/styles.css frontend/src/components/StatusModal.jsx
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --unified=0 -- frontend/src/components/StatusModal.jsx frontend/src/styles.css
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
```

### 8. Remaining issues

- [ ] No browser-automation screenshot verification was run in this pass.
- [ ] Final visual balance still depends on your runtime review after reload.

### 9. Suggested next step

- Reload the app and inspect the status modal again; if the hero area still feels too tall, the next bounded pass should reduce the portrait column by another 8-12px and tighten the skill matrix card heights to match.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-04 21:37] Map mau rank F-S theo tier-color cho skill cards

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Skill rank tier color polish

### 1. Tóm tắt

Áp màu chữ `rank` của từng skill card theo bảng màu trong `tier-color.png` thay vì theo màu accent của từng skill. Từ nay `F -> S` sẽ có màu tier cố định, nhất quán giữa các skill.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/SkillCards.jsx` | Chỉnh sửa | khoảng `L1-L24`, `L44-L52` | Thêm helper `getRankClass(rank)` và gắn class tier vào `skill-rank-badge`. |
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.skill-rank-badge` khoảng `L1205-L1245` | Bỏ map màu rank theo `skill theme`, thay bằng map theo tier `S/A/B/C/D/E/F` với glow nhẹ theo từng màu. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry polish này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Rank của mỗi skill dùng màu tier cố định theo `tier-color.png`.

### 4. Lỗi đã sửa

- [x] Loại bỏ việc rank bị nhuộm theo màu skill theme thay vì theo tier.

### 5. Mã đã loại bỏ

- [x] Removed old `.skill-node--<accent> .skill-rank-badge strong` color mapping.

### 6. Lệnh đã chạy

```bash
rg --files -g "*tier-color*" -g "*.png"
Get-Content frontend/src/components/SkillCards.jsx | Select-Object -First 180
npm.cmd run build
npm.cmd run test:dashboard-data
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser screenshot sau đổi màu tier; cần nhìn runtime thật để tinh chỉnh độ sáng/glow nếu cần.

### 9. Bước tiếp theo được đề xuất

- Nếu cần bám ảnh mạnh hơn nữa, tinh chỉnh thêm gradient stroke hoặc outline cho chữ rank theo từng tier.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 21:29] Sửa layout lỗi nghiêm trọng của StatusModal

**Agent:** coder-gpt54
**Status:** Done
**Related task:** StatusModal emergency layout correction

### 1. Tóm tắt

Sửa lỗi layout nghiêm trọng của `StatusModal` theo screenshot mới: `rank` trong skill card bị trôi khỏi card, header status có quá nhiều text thừa, và bố cục chưa đúng ý đồ 4 phần. Bản vá này chuyển `StatusModal` thành layout 2x2 rõ ràng: 2 ô lớn hàng trên (`B1 Awakener`, `Skill Matrix`) và 2 ô nhỏ hàng dưới (`Badge Wall`, `Recent Check-ins`), đồng thời loại bỏ các text thừa mà user đã chỉ định.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/StatusModal.jsx` | Chỉnh sửa | khoảng `L1-L210` | Ẩn/loại text `Status Center`, subtitle, `Portrait profile`, note phụ của 3 condition card; chuyển structure modal sang 4 ô trực tiếp thay vì lồng `status-main-grid`; giữ `Badge Wall` và `Recent Check-ins` ở hàng dưới. |
| `frontend/src/styles.css` | Chỉnh sửa | khu vực status modal khoảng `L1650-L1835` và media query `L1988-L2000` | Thêm `status-modal--quad`, ẩn header copy của overlay status, sửa layout 2x2, sửa compact skill header/rank badge, và responsive collapse theo thứ tự 4 ô. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry fix layout này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] StatusModal chia thành 4 phần rõ ràng theo đúng layout user yêu cầu.
- [x] Header status chỉ còn nút close, bỏ toàn bộ text overlay thừa.
- [x] Compact skill cards giữ rank nằm đúng trong card.

### 4. Lỗi đã sửa

- [x] Sửa lỗi `rank` bị lệch hẳn khỏi skill cards.
- [x] Sửa lỗi hierarchy rối và text thừa trong phần status.
- [x] Sửa sai bố cục khiến `Badge Wall` và `Recent Check-ins` không nằm thành 2 ô nhỏ phía dưới.

### 5. Mã đã loại bỏ

- [x] Removed visible overlay header copy for `StatusModal`.
- [x] Removed condition helper texts: `Tinh than hom nay`, `Nang luong hien tai`, `Do tap trung`.

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/components/StatusModal.jsx | Select-Object -First 260
Get-Content frontend/src/components/SkillCards.jsx | Select-Object -First 180
Get-Content frontend/src/styles.css | Select-Object -Skip 1640 -First 240
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/components/StatusModal.jsx frontend/src/styles.css
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser walkthrough sau bản vá này; cần xác nhận lại bằng screenshot/runtime xem density của 4 ô đã hợp mắt chưa.

### 9. Bước tiếp theo được đề xuất

- Nếu 4 ô vẫn còn nặng, bước tiếp theo là giảm padding và giảm số cột của `Skill Matrix` trong modal.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 21:13] Retheme palette va redesign StatusModal theo color-ui/status-ui

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Palette retheme + compact status redesign

### 1. Tóm tắt

Đổi toàn bộ tone màu app sang hướng `teal/emerald` với `amber/gold` accent, bám gần hơn `color-ui.webp`. Đồng thời redesign `StatusModal` theo concept `status-ui.webp`: hero block cho `level/rank/xp`, số quan trọng có neon glow, `daily condition` gọn hơn, `Check-in` chuyển sang section expand, `skills` thành compact matrix, và `badge/history` thành phần phụ có thể thu gọn.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/StatusModal.jsx` | Chỉnh sửa | toàn bộ component khoảng `L1-L224` | Viết lại hierarchy của status modal: portrait tĩnh, hero stats, neon numbers, daily condition cards, expandable check-in, collapsible badge/history sections. |
| `frontend/src/components/SkillCards.jsx` | Chỉnh sửa | khoảng `L3-L44` | `compact` mode giờ thực sự compact: chỉ giữ `name + rank + level + xp + progress`, bỏ note/last practiced ở mode compact. |
| `frontend/src/styles.css` | Chỉnh sửa | `:root`, `body`, và khu status/skill styles khoảng `L1-L70`, `L1640-L1820`, cùng một số token dùng chung | Đổi palette toàn app sang teal/emerald + amber, thêm status neon-number treatment, layout mới cho status modal, style aux sections, compact skill cards, và panel lighting gần concept ảnh mẫu hơn. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry task redesign này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Palette toàn app đổi sang tone gần `color-ui.webp`.
- [x] `StatusModal` có hero block rõ cho `level / rank / xp`.
- [x] Số quan trọng trong `StatusModal` có hiệu ứng neon.
- [x] `Daily condition` gọn thành 3 stat card.
- [x] `Check-in` mở rộng theo nút thay vì lộ toàn bộ form ngay.
- [x] `Badge Wall` và `Recent Check-ins` trở thành section phụ/collapsible.

### 4. Lỗi đã sửa

- [x] Giảm độ dài và sự rối của status modal cũ.
- [x] Loại bỏ compact mode chưa đủ compact của khối skills trong status.
- [x] Đồng bộ lại visual hierarchy để status screen có cảm giác system/game rõ hơn.

### 5. Mã đã loại bỏ

- [x] Removed avatar picker emphasis from `StatusModal`.
- [x] Removed legacy full-detail compact skill rendering inside status modal.

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/components/StatusModal.jsx | Select-Object -First 320
Get-Content frontend/src/styles.css | Select-Object -First 260
rg -n "compact ?=|compact\\}|compact \\?|SkillCards" frontend/src
Get-Content frontend/src/components/SkillCards.jsx | Select-Object -First 260
Get-Content frontend/src/components/BadgeWallPanel.jsx | Select-Object -First 220
Get-Content frontend/src/styles.css | Select-String -Pattern 'status-modal|status-avatar|status-profile|xp-meter|profile-signal-grid|checkin-grid|checkin-history|skill-grid|skill-node|badge-grid|modal-block' -Context 3,10
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/components/StatusModal.jsx frontend/src/components/SkillCards.jsx frontend/src/styles.css
git diff --unified=0 -- frontend/src/components/StatusModal.jsx frontend/src/components/SkillCards.jsx frontend/src/styles.css
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser screenshot walkthrough để xác nhận mức độ bám sát `color-ui.webp` và `status-ui.webp` trong runtime thật.
- [ ] Một số panel ngoài `StatusModal` mới được retheme qua color tokens, chưa có redesign layout sâu.

### 9. Bước tiếp theo được đề xuất

- Nếu muốn bám concept mạnh hơn nữa, vòng tiếp theo nên polish riêng `HomeTopBar` và `Suggestion Inbox` theo cùng visual language của palette mới.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:48] Chuyen phase detail sang full overlay scroll rieng

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Roadmap phase overlay refinement

### 1. Tóm tắt

Điều chỉnh lại interaction của roadmap theo yêu cầu mới: bấm vào từng phase không còn bung detail inline trong hero nữa, mà mở một `full overlay` kích thước cố định. Bên trong overlay, danh sách `weeks + sessions` của phase có vùng scroll riêng để người dùng lăn chuột xem hết nội dung.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/RoadmapHero.jsx` | Chỉnh sửa | khu vực state + render roadmap/phase detail khoảng `L1-L167` | Thêm state mở overlay, đổi click phase sang mở `OverlayFrame`, loại bỏ panel detail inline, và render phase detail trong overlay với scroll area riêng. |
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.overlay-frame--phase`, `.roadmap-phase-overlay__scroll`, roadmap phase detail block, mobile media query khoảng `L450-L590`, `L1645-L1658` | Bỏ container detail inline cũ, thêm style overlay phase cố định, count badge ở header actions, custom scrollbar và giới hạn chiều cao vùng scroll riêng. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry refinement này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Click phase mở full overlay riêng.
- [x] Overlay phase có kích thước cố định.
- [x] Weeks + sessions của phase cuộn trong vùng nội bộ bằng chuột.

### 4. Lỗi đã sửa

- [x] Loại bỏ cách hiển thị inline quá dài trong hero khi mở session của phase.

### 5. Mã đã loại bỏ

- [x] Removed inline `roadmap-phase-detail` container from the main hero flow.

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/components/OverlayFrame.jsx | Select-Object -First 220
Get-Content frontend/src/styles.css | Select-String -Pattern 'overlay-shell|overlay-frame|overlay-frame__body|overlay-frame__header' -Context 2,12
Get-Content frontend/src/components/QuestOverlay.jsx | Select-Object -First 200
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/components/RoadmapHero.jsx frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser walkthrough để kiểm tra cảm giác scroll của overlay phase trên dữ liệu dài thực tế.

### 9. Bước tiếp theo được đề xuất

- Nếu overlay còn quá dày thông tin, bước tiếp theo là cho từng week trong overlay collapse/expand.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:40] Bo chip current phase va mo session theo phase khi click

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Roadmap phase interaction refinement

### 1. Tóm tắt

Bỏ chip `Current phase` theo yêu cầu. Đồng thời biến 5 phase card trong `roadmap hero` thành các điểm chọn tương tác: khi bấm vào một phase, giao diện sẽ mở toàn bộ `weeks + sessions` thuộc riêng phase đó ngay bên dưới roadmap, thay vì chỉ có summary card.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/RoadmapHero.jsx` | Chỉnh sửa | toàn bộ component khoảng `L1-L156` | Thêm local state chọn phase, bỏ chip current, biến roadmap card thành button, render panel detail cho phase đang chọn, flatten sessions theo phase và group lại theo week. |
| `frontend/src/App.jsx` | Chỉnh sửa | khu vực props truyền vào `RoadmapHero` khoảng `L255-L263` | Truyền `mainQuestMap` vào hero để lấy dữ liệu tuần/session đầy đủ cho phase detail. |
| `frontend/src/styles.css` | Chỉnh sửa | khu vực roadmap hero và media query mobile khoảng `L350-L560`, `L1640-L1650` | Bỏ style chip current phase cũ, thêm style cho roadmap card selectable, phase-detail panel, week/session card, selected state, và responsive layout cho detail panel. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry refinement này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Click vào phase để xem toàn bộ session của riêng phase đó.
- [x] Phase detail hiển thị theo tuần và theo session ngay trong home hero.
- [x] Phase được chọn có selected state riêng, tách biệt với current phase highlight.

### 4. Lỗi đã sửa

- [x] Loại bỏ chip `Current phase` khỏi roadmap theo yêu cầu mới.
- [x] Bổ sung thiếu hụt UX khi roadmap chỉ cho xem summary mà không xem được session theo phase.

### 5. Mã đã loại bỏ

- [x] Removed `roadmap-phase__status` chip rendering and its CSS treatment.

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/App.jsx | Select-Object -Skip 90 -First 320
Get-Content frontend/src/dashboard-data.js | Select-Object -Skip 640 -First 90
Get-Content frontend/src/components/MainQuestMapPanel.jsx | Select-Object -First 260
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/components/RoadmapHero.jsx frontend/src/App.jsx frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser walkthrough để kiểm tra mật độ nội dung của phase-detail panel khi số session nhiều.

### 9. Bước tiếp theo được đề xuất

- Nếu phase-detail quá dài, bước tiếp theo là cho panel này collapse theo week hoặc mở trong overlay riêng.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:34] Tang do noi bat cho pha hien tai tren roadmap track

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Roadmap current phase highlight redesign

### 1. Tóm tắt

Thiết kế lại visual của 5 phase card trên `roadmap track` để pha hiện tại nổi bật rõ ràng hơn. Pha current giờ có `Current phase` chip riêng, card nhô cao hơn, viền/glow mạnh hơn, beam sáng hơn, progress bar sáng hơn, và halo phía trên để tạo cảm giác active command node thay vì chỉ đổi border nhẹ.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/RoadmapHero.jsx` | Chỉnh sửa | khu vực render `roadmap.map(...)` | Thêm `roadmap-phase__status` chip cho phase hiện tại. |
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.roadmap-track`, `.roadmap-phase`, `.roadmap-phase__status`, `.roadmap-phase--current`, `@keyframes roadmap-current-pulse` khoảng `L350-L500` | Nâng cấp treatment của roadmap card: radius, layered background, hover, current halo/glow/lift, brighter beam, stronger progress, pulse beacon, reduced-motion fallback. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry redesign này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Current phase có chip nhãn riêng.
- [x] Current phase được highlight bằng lift + halo + stronger beam/progress.
- [x] Các phase upcoming/cleared có phân cấp thị giác rõ hơn.

### 4. Lỗi đã sửa

- [x] Sửa vấn đề current phase chưa đủ nổi bật trên roadmap track.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content C:\Users\Admin\.agents\skills\frontend-design\SKILL.md | Select-Object -First 120
rg -n "roadmap|phase|currentPhase|isCurrent|roadmap-track|roadmap-phase" frontend/src
Get-Content frontend/src/styles.css | Select-String -Pattern 'roadmap-track|roadmap-phase|hero-panel|phase' -Context 3,12
Get-Content frontend/src/components/RoadmapHero.jsx | Select-Object -First 220
Get-Content frontend/src/styles.css | Select-Object -Skip 340 -First 160
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/components/RoadmapHero.jsx frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser screenshot verification sau redesign mới; cần bạn xem trực quan xem mức nổi bật đã đủ hay chưa.

### 9. Bước tiếp theo được đề xuất

- Nếu muốn current phase mạnh hơn nữa, có thể cho 4 phase còn lại thu nhỏ nhẹ hoặc nối chúng bằng track line có checkpoint sáng tại current node.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:23] Sua lai neo Suggestion Inbox theo topbar-cluster

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Suggestion Inbox viewport-right alignment follow-up

### 1. Tóm tắt

Ảnh runtime cho thấy dropdown vẫn chưa sát mép phải vì nó đang neo theo `bell button`, trong khi bên phải chuông vẫn còn cụm `HOST` nên mọi công thức `right` đều bị lệch gốc. Bản sửa này đổi containing block của dropdown sang `topbar-cluster`, rồi mới áp dụng offset theo shell margin + topbar padding để dropdown bám đúng về mép phải màn hình.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.topbar-cluster`, `.inbox-cluster`, `.inbox-dropdown`, media query `max-width: 980px` | Đặt `topbar-cluster` thành containing block, đổi `inbox-cluster` sang `static`, cập nhật công thức `right` mới, và reset `right: 0` cho màn hình hẹp. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry follow-up này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Dropdown Suggestion Inbox neo theo cụm topbar phải, giúp canh viewport-right đúng hơn.

### 4. Lỗi đã sửa

- [x] Sửa sai gốc định vị khiến inbox vẫn lệch trái dù đã tăng offset.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/components/HomeTopBar.jsx | Select-Object -First 220
Get-Content frontend/src/styles.css | Select-String -Pattern 'topbar-cluster|topbar-clock|system-icon-button--bell|inbox-cluster|home-topbar' -Context 2,8
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Cần bạn xác nhận lại bằng screenshot/runtime sau khi reload vì đây là fix theo layout math.

### 9. Bước tiếp theo được đề xuất

- Nếu còn lệch nhẹ, tinh chỉnh cuối cùng chỉ còn là giảm/tăng thêm `8px-16px` trên `right` offset.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:17] Canh Suggestion Inbox sat le phai man hinh

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Suggestion Inbox viewport-right alignment

### 1. Tóm tắt

Điều chỉnh lại vị trí của `Suggestion Inbox` để dropdown không còn bám mép phải của `home shell`, mà dịch ra đúng về lề phải của màn hình. Cách sửa là đổi `right` offset sang công thức bù cả gutter 20px lẫn phần margin phát sinh khi shell bị khóa ở `1520px`.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.inbox-dropdown` khoảng `L564-L570` | Đổi `right: 0`/neo shell sang công thức `calc(-20px - max(0px, (100vw - 1560px) / 2))` để bám lề phải viewport. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry bugfix/canh lề này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Dropdown Suggestion Inbox bám sát lề phải màn hình ổn định hơn trên cả viewport hẹp và rộng.

### 4. Lỗi đã sửa

- [x] Sửa lệch vị trí khi inbox chỉ bám mép phải của layout shell thay vì mép phải của màn hình.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Date -Format "yyyy-MM-dd HH:mm"
Get-Content frontend/src/styles.css | Select-String -Pattern 'inbox-dropdown \\{|right: calc' -Context 0,4
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser visual verification để xác nhận khoảng cách mép phải đúng như mong muốn ở mọi viewport.

### 9. Bước tiếp theo được đề xuất

- Nếu vẫn muốn sát hơn nữa, có thể đổi từ khoảng cách 20px xuống 12px hoặc 8px theo đúng cảm giác thị giác mong muốn của bạn.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:13] Them stagger nhe cho suggestion card trong Inbox

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Suggestion Inbox stagger animation polish

### 1. Tóm tắt

Tinh chỉnh thêm animation cho `Suggestion Inbox` bằng stagger nhẹ trên từng suggestion card khi dropdown mở. Cách này tăng cảm giác system UI nhưng không cần đổi logic click-outside hay state timing của dropdown.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `@keyframes suggestion-node-enter`, `.inbox-dropdown .suggestion-node`, `prefers-reduced-motion` khoảng `L600-L680`, `L1140-L1175` | Thêm keyframe enter cho card, delay theo `nth-child`, và đảm bảo reduced-motion đặt `opacity: 1` để không bị ẩn card. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry polish này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Suggestion card xuất hiện theo nhịp stagger nhẹ khi mở inbox.
- [x] Motion vẫn có fallback reduced-motion an toàn.

### 4. Lỗi đã sửa

- [x] Không có bug logic mới; đây là polish animation cho danh sách suggestion.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/styles.css | Select-String -Pattern 'suggestion-node:hover|inbox-dropdown-enter|prefers-reduced-motion|suggestion-list' -Context 2,10
Get-Content frontend/src/styles.css | Select-Object -Skip 560 -First 120
Get-Content frontend/src/styles.css | Select-Object -Skip 1120 -First 80
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser runtime verification để cảm nhận timing motion trên UI thật.

### 9. Bước tiếp theo được đề xuất

- Nếu muốn hoàn thiện hơn nữa, có thể thêm component/browser test cho open state hoặc tinh chỉnh timing theo số lượng suggestion thực tế.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:09] Them sticky header va motion nhe cho Suggestion Inbox

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Suggestion Inbox sticky header + entrance motion

### 1. Tóm tắt

Tinh chỉnh thêm `Suggestion Inbox` để phần header luôn bám trên cùng khi cuộn danh sách và dropdown có animation mở rất nhẹ theo hướng top-right. Đồng thời thêm fallback `prefers-reduced-motion` để tránh ép motion với người dùng muốn giảm chuyển động.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.inbox-dropdown`, `.inbox-dropdown__header`, `@keyframes inbox-dropdown-enter` khoảng `L568-L650` | Thêm animation enter, đặt header thành `position: sticky`, bổ sung nền blur cho header, và thêm media query `prefers-reduced-motion`. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry polish này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Header của Suggestion Inbox sticky khi cuộn.
- [x] Dropdown có entrance motion nhẹ hơn, hợp theme system UI.
- [x] Có fallback reduced-motion cho accessibility.

### 4. Lỗi đã sửa

- [x] Không có bug logic mới; đây là polish tương tác/thị giác.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/styles.css | Select-String -Pattern 'prefers-reduced-motion|inbox-dropdown__header|inbox-dropdown|@keyframes' -Context 2,8
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/styles.css changelogs.md
git diff --unified=0 -- frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser screenshot/runtime verification để quan sát motion thật.

### 9. Bước tiếp theo được đề xuất

- Nếu muốn hoàn thiện hơn nữa, có thể thêm click-outside transition hoặc subtle stagger cho từng suggestion card.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:08] Polish visual Suggestion Inbox theo theme game UI

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Suggestion Inbox visual polish

### 1. Tóm tắt

Tinh chỉnh thêm look-and-feel của `Suggestion Inbox` để đồng bộ hơn với dark fantasy / neon system UI: dropdown có lớp nền sâu hơn, header được tách bằng divider, scrollbar đổi sang cyan glow, và suggestion card có hover state rõ hơn nhưng vẫn giữ scope thuần CSS.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `inbox-dropdown`, `.suggestion-list`, `.suggestion-node`, `.suggestion-actions` khoảng `L560-L690` | Thêm background gradient, border-radius, multi-layer shadow, divider cho header, custom scrollbar, fade mask ở vùng scroll, hover glow cho suggestion card, và polish cho action button. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry visual polish này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Scrollbar custom theo theme neon-cyan.
- [x] Suggestion card có hover feedback rõ hơn.
- [x] Dropdown có chiều sâu thị giác và phân tách header/list tốt hơn.

### 4. Lỗi đã sửa

- [x] Không có bug logic mới; đây là polish trực quan cho vùng scroll và dropdown.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content C:\Users\Admin\.agents\skills\frontend-design\SKILL.md | Select-Object -First 120
Get-Content C:\Users\Admin\.agents\skills\ui-ux-pro-max\SKILL.md | Select-Object -First 120
Get-Content C:\Users\Admin\.agents\skills\vercel-react-best-practices\SKILL.md | Select-Object -First 120
Get-Content frontend/src/styles.css | Select-String -Pattern 'inbox-dropdown|suggestion-node|suggestion-actions|system-badge|empty-state' -Context 3,10
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/styles.css changelogs.md
git diff --unified=0 -- frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser screenshot verification để chốt spacing/hover/scrollbar trên runtime thật.

### 9. Bước tiếp theo được đề xuất

- Nếu muốn polish thêm, có thể thêm sticky header hoặc subtle entrance animation cho inbox dropdown.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:05] Tinh chỉnh UI Suggestion Inbox dropdown

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Suggestion Inbox dropdown scroll + right alignment

### 1. Tóm tắt

Tinh chỉnh UI cho `Suggestion Inbox` để dropdown luôn bám về lề phải cụm top bar, chiều cao vùng danh sách được cố định ở mức tương đương khoảng 4 suggestion card, và có thể cuộn chuột để xem các item còn lại mà không làm dropdown kéo dài quá mức.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `inbox-dropdown` khoảng `L430-L450` | Khóa `left: auto` để dropdown bám mép phải, thêm giới hạn `max-height` + `overflow-y: auto` cho `.suggestion-list` bên trong inbox. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry task UI tweak này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Dropdown Suggestion Inbox có vùng list cao cố định và cuộn được.
- [x] Dropdown bám lề phải của top bar ổn định hơn.

### 4. Lỗi đã sửa

- [x] Suggestion Inbox không còn nở quá dài khi có nhiều item.
- [x] Suggestion Inbox giữ canh phải thay vì lệch vào giữa khi mở dropdown.

### 5. Mã đã loại bỏ

- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content frontend/src/styles.css | Select-String -Pattern 'inbox-cluster|inbox-dropdown|suggestion-list|home-topbar' -Context 3,12
Get-Content frontend/src/components/SuggestionInboxDropdown.jsx | Select-Object -First 220
Get-Content changelogs.md | Select-Object -Last 120
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/styles.css changelogs.md
git diff --unified=0 -- frontend/src/styles.css changelogs.md
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Vấn đề còn lại

- [ ] Chưa có browser visual verification để chụp dropdown thật trong runtime.

### 9. Bước tiếp theo được đề xuất

- Nếu cần khóa chặt hơn hành vi UI, bổ sung component/browser test cho Suggestion Inbox open/scroll/alignment.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 20:00] Sửa dropdown Suggestion Inbox bị ẩn ở top bar

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Home dashboard redesign post-accept bugfix

### 1. Tóm tắt

Đã sửa lỗi khi bấm icon chuông không thấy Suggestion Inbox. Nguyên nhân là `home-topbar` đang dùng `overflow: hidden`, làm dropdown được render nhưng bị cắt khỏi vùng nhìn thấy. Patch này mở overflow cho top bar và nâng `z-index` của cụm inbox để dropdown nổi đúng trên header.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/styles.css` | Chỉnh sửa | khu vực `.home-topbar`, `.inbox-cluster` | Đổi `home-topbar` sang `overflow: visible`, thêm `z-index`, và nâng `z-index` cho `inbox-cluster`. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry bugfix này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Không có

### 4. Lỗi đã sửa

- [x] Sửa lỗi dropdown Suggestion Inbox bị cắt và không hiển thị khi bấm icon chuông.

### 5. Mã đã loại bỏ

- [x] None

### 6. Lệnh đã chạy

```bash
Get-Content frontend\src\components\SuggestionInboxDropdown.jsx
Get-Content frontend\src\components\HomeTopBar.jsx
rg -n "inbox|suggestion|bell|topbar|overflow|z-index|home-topbar" frontend/src/styles.css frontend/src/App.jsx frontend/src/components
Get-Content frontend\src\styles.css | Select-Object -Skip 120 -First 220
Get-Date -Format "yyyy-MM-dd HH:mm"
npm.cmd run build
npm.cmd run test:dashboard-data
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
```

### 8. Vấn đề còn lại

- [ ] Browser visual walkthrough vẫn chưa có, nên fix này mới được xác minh bằng code path + build/test chứ chưa có screenshot thủ công.

### 9. Bước tiếp theo được đề xuất

- Khi có browser walkthrough, xác nhận thêm dropdown layering và click-outside behavior trên viewport thật.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 17:35] Home dashboard redesign - compact hero shell

**Agent:** coder-gpt54
**Status:** Done
**Related task:** approved frontend-first home-dashboard redesign

### 1. Summary

Đã thay home view cũ bằng compact hero dashboard theo hướng dark fantasy/system UI, giữ frontend-only và dùng lại API hiện có. Home mới có top-right cluster, roadmap phase track ở giữa, 3 stat cards phía dưới, nav drawer qua burger, Suggestion Inbox thật bằng `rank-suggestions` + `weakness-suggestions`, status modal có check-in + skill cards, quest/certificate/boss overlays, và form thêm certificate dùng `test-records` API hiện có.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
|---|---|---|---|
| `frontend/src/App.jsx` | Modified | `App component`, gần như toàn file | Rebuild toàn bộ app shell: fetch tách theo surface, state cho drawer/dropdown/modal/overlays, wiring `summary/profile/checkins/study-plan/main-quests/weekly-mission/suggestions/test-records/boss-battles`, quest toggle, suggestion apply/dismiss, check-in save, certificate create. |
| `frontend/src/styles.css` | Modified | `home-shell`, `topbar`, `hero-panel`, `overlay-frame`, `status-modal`, `quest/main-quest/skill/certificate/boss sections`, gần như toàn file | Thay CSS home cũ bằng hệ style mới cho compact hero dashboard và giữ render ổn cho các panel/overlay tái sử dụng. |
| `frontend/src/dashboard-data.js` | Modified | tail helpers sau `buildDashboardView()` | Thêm view-model helpers cho player snapshot, XP progress, roadmap phase track, merged suggestion inbox, certificate filtering, và boss current/timeline selection. |
| `frontend/src/components/SkillMatrixPanel.jsx` | Modified | toàn component | Đổi sang dùng `SkillCards` để tái sử dụng style skill detail trong status modal và panel cũ. |
| `frontend/src/components/SkillCards.jsx` | Added | `L1-L46` | Shared skill card renderer cho status modal và panel skill matrix. |
| `frontend/src/components/OverlayFrame.jsx` | Added | `L1-L25` | Khung overlay chung cho quest/certificate/boss/status surfaces. |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Added | `L1-L61` | Bell dropdown với loading/error và apply/dismiss actions thật. |
| `frontend/src/components/NavigationDrawer.jsx` | Added | `L1-L31` | Burger drawer cho Quest / Certificate / Boss. |
| `frontend/src/components/HomeTopBar.jsx` | Added | `L1-L53` | Top-right cluster gồm level/rank, avatar trigger, bell pending count, host time. |
| `frontend/src/components/RoadmapHero.jsx` | Added | `L1-L65` | Hero section với roadmap phase-level track và 3 stat cards. |
| `frontend/src/components/StatusModal.jsx` | Added | `L1-L173` | Center status modal với avatar placeholder picker, XP meter, check-in controls, badge placeholder, và detailed skill cards. |
| `frontend/src/components/WeeklyMissionCard.jsx` | Added | `L1-L35` | Weekly mission card riêng cho overlay tab weekly. |
| `frontend/src/components/QuestOverlay.jsx` | Added | `L1-L68` | Full overlay với tabs Main / Daily / Weekly / Archive disabled. |
| `frontend/src/components/CertificateOverlay.jsx` | Added | `L1-L149` | Certificate list filter theo IELTS/Aptis/TOEIC/TOEFL và form tạo record mới qua API cũ. |
| `frontend/src/components/BossOverlay.jsx` | Added | `L1-L38` | Boss overlay với current boss hero trước, timeline sau. |
| `changelogs.md` | Modified | tail section | Thêm mục changelog cho redesign này. |

### 3. Features added

- [x] Compact home hero dashboard thay cho old side-column home layout.
- [x] Top-right cluster với level/rank text, avatar trigger, bell pending count, và host date/time.
- [x] Suggestion Inbox dropdown dùng thật `rank-suggestions` + `weakness-suggestions` và endpoints apply/dismiss.
- [x] Status modal với XP progress, check-in controls, badge placeholder, avatar picker placeholder, và detailed skill cards.
- [x] Burger drawer mở các surface Quest / Certificate / Boss.
- [x] Quest overlay có tabs Main / Daily / Weekly / Archive disabled.
- [x] Certificate overlay dùng `test-records` API để list + create records.
- [x] Boss overlay ưu tiên current boss rồi tới timeline/list.

### 4. Bugs fixed

- [x] Khôi phục frontend runnable sau khi `App.jsx` bị dở dang trong lượt interrupted trước.
- [x] Loại bỏ việc home vẫn phụ thuộc layout dashboard cũ nhiều cột ở view chính.
- [x] Tách loading/error theo từng surface chính thay vì dồn hết vào một panel cũ.

### 5. Code removed

- [x] Removed old home dashboard layout/styles khỏi view chính bằng cách thay bằng compact hero shell.
- [x] Không đụng backend hoặc API contract.

### 6. Commands run

```bash
Get-Content frontend\src\components\HomeTopBar.jsx
Get-Content frontend\src\components\RoadmapHero.jsx
Get-Content frontend\src\components\StatusModal.jsx
Get-Content frontend\src\components\QuestOverlay.jsx
Get-Content frontend\src\components\CertificateOverlay.jsx
Get-Content frontend\src\components\BossOverlay.jsx
Get-Content frontend\src\dashboard-data.js
git diff --check -- frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components/SkillCards.jsx frontend/src/components/OverlayFrame.jsx frontend/src/components/SuggestionInboxDropdown.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/RoadmapHero.jsx frontend/src/components/StatusModal.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/CertificateOverlay.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/SkillMatrixPanel.jsx
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --stat -- frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components/SkillCards.jsx frontend/src/components/OverlayFrame.jsx frontend/src/components/SuggestionInboxDropdown.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/RoadmapHero.jsx frontend/src/components/StatusModal.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/CertificateOverlay.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/SkillMatrixPanel.jsx changelogs.md
git diff --unified=0 -- frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components/SkillCards.jsx frontend/src/components/OverlayFrame.jsx frontend/src/components/SuggestionInboxDropdown.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/RoadmapHero.jsx frontend/src/components/StatusModal.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/CertificateOverlay.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/SkillMatrixPanel.jsx changelogs.md
git status --short frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components frontend/src/dashboard-data.test.js changelogs.md
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
git diff --check (scoped files): passed; only LF->CRLF warnings from Git working copy normalization on App.jsx/styles.css
npm.cmd run build: passed
vite production build completed successfully
npm.cmd run test:dashboard-data: passed
5 tests, 0 failures
```

### 8. Remaining issues

- [x] None bắt buộc trong phạm vi task này.
- [ ] Avatar picker mới là placeholder UI, chưa có upload/persistence theo scope đã khóa.
- [ ] Chưa có browser screenshot walkthrough trong changelog này; validation hiện tại là build + automated data tests.

### 9. Suggested next step

- Chạy một lượt browser review trực quan trên `http://localhost:5173` để duyệt spacing, dropdown/modal states, và data density với payload thật nếu muốn tăng độ tin cậy UI trước reviewer pass.

### 10. User review checklist

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 18:01] Home dashboard redesign - focused spec fix cycle

**Agent:** coder-gpt54
**Status:** Done
**Related task:** orchestrator review fix cycle for home-dashboard redesign

### 1. Summary

Đã sửa 6 điểm lệch spec còn lại của home-dashboard redesign: host clock có năm, burger Quest có child actions Main/Daily/Weekly/Archive, roadmap hero có line tổng start/end, Main tab của Quest overlay ưu tiên current/today main quest trước full map, `currentBoss` luôn có `uiStatus` normalize, và top-right level/rank được nén gọn hơn.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
|---|---|---|---|
| `frontend/src/App.jsx` | Modified | `formatHostDateTime`, memo block, `RoadmapHero` props, `NavigationDrawer` props | Thêm năm vào host clock format, derive roadmap bounds từ `studyPlanWeeks`, truyền roadmap bounds đã format, và đổi Quest drawer wiring sang mở tab cụ thể. |
| `frontend/src/dashboard-data.js` | Modified | tail helper section | Thêm `buildRoadmapBounds()` và sửa `buildBossView()` để `currentBoss` cũng nhận `uiStatus` normalize giống timeline items. |
| `frontend/src/components/NavigationDrawer.jsx` | Modified | drawer action area | Thay 1 nút Quest bằng group/submenu Main / Daily / Weekly / Archive disabled. |
| `frontend/src/components/HomeTopBar.jsx` | Modified | top-right compact level cluster | Rút gọn hiển thị level/rank thành number + rank letter, bỏ label clutter kiểu `Lv.` / `Rank`. |
| `frontend/src/components/RoadmapHero.jsx` | Modified | roadmap center area | Thêm line tổng roadmap start/end dưới phase track. |
| `frontend/src/components/QuestOverlay.jsx` | Modified | Main tab render path | Thêm card current/today main quest nổi bật trước `MainQuestMapPanel`, dùng `currentWeekNo/currentSessionId` từ `mainQuestMap`. |
| `frontend/src/styles.css` | Modified | `topbar-level`, `roadmap-bounds`, `nav-drawer__group/subactions`, `current-main-quest`, responsive sections | Bổ sung style cho compact top-right cluster, roadmap bounds line, quest submenu buttons, và current main quest priority card. |
| `changelogs.md` | Modified | tail section | Thêm mục changelog cho focused fix cycle này. |

### 3. Features added

- [x] Quest submenu trong burger drawer với Main / Daily / Weekly / Archive.
- [x] Overall roadmap start/end line dưới phase track.
- [x] Priority card cho current/today main quest trong Main tab.

### 4. Bugs fixed

- [x] Host clock thiếu năm.
- [x] `currentBoss.uiStatus` không còn bị thiếu trên boss hero.
- [x] Top-right level/rank không còn verbose như bản trước.

### 5. Code removed

- [x] Removed single Quest drawer button assumption.
- [x] Removed explicit `Lv.` / `Rank` label clutter from top-right compact display.

### 6. Commands run

```bash
Get-Content frontend\src\App.jsx
Get-Content frontend\src\components\NavigationDrawer.jsx
Get-Content frontend\src\components\HomeTopBar.jsx
Get-Content frontend\src\components\RoadmapHero.jsx
Get-Content frontend\src\components\QuestOverlay.jsx
Get-Content frontend\src\components\BossOverlay.jsx
Get-Content frontend\src\dashboard-data.js
rg -n "topbar-level|roadmap-bounds|nav-drawer__actions|status-modal|quest-main-tab|current-main-quest" frontend\src\styles.css
Get-Content frontend\src\styles.css | Select-Object -First 260
Get-Content frontend\src\styles.css | Select-Object -Skip 260 -First 340
Get-Content frontend\src\styles.css | Select-Object -Skip 600 -First 280
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components/NavigationDrawer.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/RoadmapHero.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/BossOverlay.jsx changelogs.md
git diff --stat -- frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components/NavigationDrawer.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/RoadmapHero.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/BossOverlay.jsx changelogs.md
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
vite production build completed successfully
npm.cmd run test:dashboard-data: passed
5 tests, 0 failures
git diff --check (scoped files): passed; only LF->CRLF normalization warnings on App.jsx/styles.css from Git working copy handling
```

### 8. Remaining issues

- [x] None in this fix cycle's narrow scope.
- [ ] Avatar picker remains placeholder-only by locked scope.
- [ ] Browser visual walkthrough still not captured in this cycle.

### 9. Suggested next step

- Reviewer pass or a quick browser-only UI review to confirm the current-main-quest emphasis and drawer submenu feel right with live payloads.

### 10. User review checklist

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 08:12] MQM-01 - Thêm Main Quest Map read-only theo study-plan và main-quests

**Agent:** coder-gpt54  
**Status:** Partially done  
**Related task:** MQM-01

### 1. Tóm tắt

Đã thêm Main Quest Map read-only trên frontend bằng cách tải `study-plan/weeks` và `main-quests`, ghép dữ liệu theo `study_plan_session_id`, rồi render thành cây `5 phase / 78 tuần / session`. Panel mới có loading/error riêng để không làm hỏng Daily Quest, mặc định thu gọn nhưng tự mở phase/tuần hiện tại và đánh dấu session trùng ngày học hiện tại theo `study_date`.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/App.jsx` | Chỉnh sửa | `L36-L41`, `L68-L99`, `L148-L155` | Thêm state/fetch riêng cho Main Quest data, memo hóa `buildMainQuestMap()`, và gắn `MainQuestMapPanel` vào luồng dashboard mà không đụng Daily Quest toggle. |
| `frontend/src/dashboard-data.js` | Chỉnh sửa | `L57-L93`, `L134-L262` | Khai báo metadata 5 phase, helper chuẩn hóa ngày/tách material list, và hàm `buildMainQuestMap()` để ghép `StudyPlanSession` với `Main Quest` theo `study_plan_session_id`. |
| `frontend/src/components/MainQuestMapPanel.jsx` | Thêm mới | `L1-L208` | Tạo panel read-only theo pattern `PanelFrame` với phase/week/session expand-collapse, highlight tuần/buổi hiện tại, hiển thị ngày học, skill, task, material, deliverable, trạng thái và XP. |
| `frontend/src/styles.css` | Chỉnh sửa | `L729-L985` | Bổ sung style cho empty warning, phase/week/session map, chip trạng thái và responsive rules cho Main Quest Map trên laptop/mobile. |
| `TASKS.md` | Chỉnh sửa | `L19`, `L57-L64`, `L68-L70`, `L77-L78`, `L89-L92` | Cập nhật trạng thái dự án, đánh dấu MQM-01 đã xong, ghi rủi ro còn lại và chuyển next step sang reviewer pass. |
| `TEST_REPORT.md` | Chỉnh sửa | `L114-L145` | Thêm mục xác thực riêng cho MQM-01, ghi rõ `npm run build` bị chặn bởi execution policy và `npm.cmd run build` đã pass. |
| `AGENT_NOTES.md` | Thêm mới | `L1-L8` | Ghi báo cáo ngắn cho orchestrator về phạm vi MQM-01, validation và giới hạn còn lại. |
| `changelogs.md` | Chỉnh sửa | `L110-L164` | Thêm mục changelog cho MQM-01 theo đúng format bắt buộc. |

### 3. Tính năng đã thêm

- [x] Main Quest Map read-only tách biệt với Daily Quest, render đủ phase/week/session từ dữ liệu backend.
- [x] Phase/week có expand-collapse để giảm clutter, tự mở phase/tuần hiện tại và đánh dấu session cùng ngày học hiện tại.
- [x] Mỗi session hiển thị ngày học, skill summary, task detail, material summary/source đầy đủ, deliverable, trạng thái và XP.

### 4. Lỗi đã sửa

- [x] Không để lỗi tải Main Quest data làm sập toàn bộ dashboard; panel có loading/error riêng.
- [x] Tách lỗi tải Main Quest khỏi phần còn lại của dashboard để không ảnh hưởng Daily Quest.

### 5. Mã đã loại bỏ

- [x] Không có

### 6. Lệnh đã chạy

```bash
Get-Content AGENTS.md
Get-Content TASKS.md
Get-Content changelogs.md
Get-Content TEST_REPORT.md
Get-Content docs/PROJECT_CONTEXT.md
Get-Content docs/FRONTEND_PLAN.md
Get-Content docs/MVP_BUSINESS_RULES.md
git status --short
Get-Content C:\Users\Admin\.agents\skills\codex-implementation-worker\SKILL.md
Get-Content material.md
Get-Content frontend/src/App.jsx
Get-Content frontend/src/dashboard-data.js
Get-Content frontend/src/styles.css
Get-Content frontend/src/components/PanelFrame.jsx
Get-Content frontend/src/components/DailyQuestPanel.jsx
Get-Content backend/app/main.py
Get-Content backend/app/schemas.py
rg --files frontend/src/components
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/study-plan/weeks
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/main-quests
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/study-plan/current-week
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/main-quests?week_no=1
npm run build
npm.cmd run build
git diff --stat -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/styles.css frontend/src/components/MainQuestMapPanel.jsx TASKS.md TEST_REPORT.md AGENT_NOTES.md changelogs.md
git diff --unified=0 -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/styles.css frontend/src/components/MainQuestMapPanel.jsx TASKS.md TEST_REPORT.md AGENT_NOTES.md changelogs.md
Get-Date -Format 'yyyy-MM-dd HH:mm'
```

### 7. Kết quả kiểm tra

- [ ] Đạt
- [ ] Thất bại
- [x] Chưa chạy

Chi tiết:

```text
npm run build: failed because PowerShell blocked npm.ps1 by execution policy
npm.cmd run build: passed
vite production build completed successfully
Frontend build passed.
Live API/browser validation for end-to-end MQM rendering was not run from this shell and remained pending.
```

### 8. Vấn đề còn lại

- [ ] Chưa có xác minh trực quan trong browser rằng ngày 2026-06-04 đang highlight đúng `Week 1 / Session 1`.
- [ ] `frontend/src/App.jsx` và `frontend/src/styles.css` đã dirty từ trước, nên diff với `HEAD` lớn hơn phạm vi MQM-01 thực tế.

### 9. Bước tiếp theo được đề xuất

- Reviewer pass cho MQM-01, sau đó mở app trong browser để xác nhận live payload và highlight tuần 1 / buổi 1.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 09:05] MQM-01 - Focused fix cycle cho timezone, join integrity va XP semantics

**Agent:** coder-gpt54  
**Status:** Partially done  
**Related task:** MQM-01 reviewer fix cycle

### 1. Summary

Da sua 4 nhom loi reviewer cho Main Quest Map: date-only formatting an toan timezone, phat hien integrity loi khi join `study_plan_session_id`, doi cach hien thi XP theo `Reward/Earned` dung API, va cap nhat tai lieu/changelog cho dung runtime hien tai. Panel van read-only va Daily Quest khong bi sua logic.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
|---|---|---|---|
| `frontend/src/dashboard-data.js` | Modified | `L12`, `L125-L273`, `L306-L414` | Them helper parse/format date-safe cho date-only, sua cac phep so sanh ngay de tranh UTC shift, va thay `Map overwrite` bang merge co canh bao missing/duplicate/orphan + XP metadata. |
| `frontend/src/components/MainQuestMapPanel.jsx` | Modified | `L9-L22`, `L53-L198` | Them integrity warning banner, status/xp labels moi, warning cap session, `aria-expanded`, `aria-controls`, va logic mo them current phase/week khi data reload. |
| `frontend/src/styles.css` | Modified | `L63-L64`, `L753-L900` | Them `:focus-visible`, style cho integrity warning/session warning, va tone warning cho chip/session. |
| `TASKS.md` | Modified | `L19-L20`, `L50-L70`, `L74-L79`, `L83-L87` | Sua mo ta runtime hien tai: Docker CLI co san, Compose khong co service dang chay, API 8000 dang reset tren receive, browser/live chua verify. |
| `TEST_REPORT.md` | Modified | `L5-L11`, `L70-L97`, `L118-L145` | Tach `Current Runtime Snapshot` khoi ket qua lich su, them synthetic checks va ghi ro runtime hien tai chua verify. |
| `AGENT_NOTES.md` | Modified | `L10-L19` | Bo sung ghi chu fix cycle va trang thai runtime hien tai. |
| `changelogs.md` | Modified | `MQM-01 entry status/details`, `new entry tail section` | Ha muc claim cua MQM-01 cu xuong `Partially done` va them entry moi cho focused fix cycle. |

### 3. Features added

- [x] Integrity warning counts cho missing session link, duplicate session link, va orphan Main Quest.
- [x] XP labels theo semantics API: `Reward` cho pending/non-completed, `Earned` cho completed.
- [x] Accessibility metadata cho phase/week toggles (`aria-expanded`, `aria-controls`) va focus-visible.

### 4. Bugs fixed

- [x] Date-only `YYYY-MM-DD` khong con bi parse UTC lam lech ngay o timezone am.
- [x] Duplicate `study_plan_session_id` khong con bi overwrite im lang trong `Map`.
- [x] Session missing/trung khong con trong nhu pending hop le voi `0 XP`.
- [x] Bao cao runtime/changelog khong con ghi nhu the live API dang healthy o hien tai.

### 5. Code removed

- [x] Removed silent one-to-one overwrite assumption in Main Quest join logic.
- [ ] None

### 6. Commands run

```bash
Get-Content frontend/src/dashboard-data.js
Get-Content frontend/src/components/MainQuestMapPanel.jsx
Get-Content frontend/src/App.jsx
Get-Content TASKS.md
Get-Content TEST_REPORT.md
Get-Content AGENT_NOTES.md
Get-Content changelogs.md
netstat -ano | Select-String ':8000'
docker --version
docker compose ps
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/health
Get-Process -Id 5872 | Select-Object Id,ProcessName,Path
npm.cmd run build
node --input-type=module - < synthetic MQM integrity/timezone checks
node --input-type=module - < Asia/Saigon formatDate check
node --input-type=module - < America/Los_Angeles formatDate check
git diff --check
git diff --stat -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/styles.css frontend/src/components/MainQuestMapPanel.jsx TASKS.md TEST_REPORT.md AGENT_NOTES.md changelogs.md
git diff --unified=0 -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/styles.css frontend/src/components/MainQuestMapPanel.jsx TASKS.md TEST_REPORT.md AGENT_NOTES.md changelogs.md
Get-Date -Format 'yyyy-MM-dd HH:mm'
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
git diff --check (full repo): failed because unrelated existing AGENTS.md changes contain trailing whitespace / blank line noise
git diff --check (MQM-scoped files): passed
Synthetic MQM checks: passed
Asia/Saigon => 04/06/2026
America/Los_Angeles => 04/06/2026
Current API health request: receive reset from localhost:8000
docker compose ps: no running services
```

### 8. Remaining issues

- [ ] Browser/live rendering cua Main Quest Map van chua duoc verify.
- [ ] API runtime hien tai khong phuc vu request on dinh tu shell nay, nen chua co xac minh voi payload song.

### 9. Suggested next step

- Khoi dong lai project services va verify Main Quest Map trong browser de dong vong MQM-01.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new or modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-04 08:44] Daily Quest DST regression fix trong dashboard-data

**Agent:** coder-gpt54
**Status:** Done
**Related task:** MQM reviewer follow-up - Daily Quest DST regression

### 1. Summary

Da sua regression cuoi cung trong `frontend/src/dashboard-data.js`: bo toan bo phep tru milliseconds chia `86400000` cho logic ngay lich cua Daily Quest va thay bang calendar-day ordinal dua tren `Date.UTC(year, month - 1, day)`. Cach nay tranh sai lech `overdue/expired`, `completionMode`, `currentWeekNo`, `staleDays`, va `daysUntilStart` khi qua DST.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
|---|---|---|---|
| `frontend/src/dashboard-data.js` | Modified | `L164-L175`, `L374-L469` | Them `getCalendarDayOrdinal()` / `getCalendarDayDiff()` va doi cac logic chenh lech ngay lich cua Daily Quest sang helper DST-safe. |
| `TEST_REPORT.md` | Modified | `MQM-01 Frontend Validation` section | Bo sung synthetic DST checks trong `America/Los_Angeles` va ghi ro day math da chuyen sang calendar-day ordinals. |
| `AGENT_NOTES.md` | Modified | `Daily Quest DST fix` section cuoi file | Ghi lai pham vi fix, DST validation, va xac nhan MQM checks van pass. |
| `changelogs.md` | Modified | tail section | Them entry changelog cho vong DST fix nay. |

### 3. Features added

- [x] DST-safe calendar-day helper cho cac phep tinh ngay lich trong frontend Daily Quest logic.
- [x] Synthetic validation cho DST edge cases o `America/Los_Angeles`.

### 4. Bugs fixed

- [x] Loai bo nguy co off-by-one khi tinh `overdue/expired` qua ngay doi gio DST.
- [x] Loai bo nguy co sai `completionMode`, `currentWeekNo`, `staleDays`, va `daysUntilStart` do elapsed milliseconds.

### 5. Code removed

- [x] Removed elapsed-millisecond `/ 86400000` assumptions from Daily Quest date-diff paths.
- [ ] None

### 6. Commands run

```bash
Get-Content frontend/src/dashboard-data.js
Get-Content TEST_REPORT.md
Get-Content AGENT_NOTES.md
Get-Content changelogs.md
npm.cmd run build
node --input-type=module - < synthetic DST regression checks with TZ=America/Los_Angeles
node --input-type=module - < synthetic MQM integrity/timezone checks
git diff --check -- frontend/src/dashboard-data.js TEST_REPORT.md AGENT_NOTES.md changelogs.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
Scoped git diff --check: passed
America/Los_Angeles DST checks:
- 2026-03-07 -> 2026-03-08 = overdue
- 2026-03-04 -> 2026-03-08 = expired
- completed prior date => completionMode overdue
MQM synthetic checks re-run: passed
Live/browser verification: still not run
```

### 8. Remaining issues

- [ ] Live API/browser verification remains pending.
- [ ] Runtime backend in this shell still does not provide stable live payload validation.

### 9. Suggested next step

- Proceed to re-review, then verify browser behavior once services are running again.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new or modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-04 10:xx] Final live verification va reviewer acceptance cho MQM-01

**Agent:** coder-gpt54
**Status:** Done
**Related task:** MQM-01 final closeout

### 1. Summary

Da cap nhat tai lieu de dong vong MQM-01 sau khi orchestrator xac minh live runtime va reviewer-gpt55 ACCEPT. Trang thai hien tai la Docker/API/MySQL deu pass tren moi truong song; han che con lai chi la chua co screenshot/DOM walkthrough do browser automation khong kha dung.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
|---|---|---|---|
| `TASKS.md` | Modified | `Current Project State`, `Completed`, `In Progress`, `Known Issues / Risks`, `Next Candidate Tasks` | Doi tu snapshot runtime stale sang trang thai live da verify, danh dau reviewer pass, va cap nhat next candidate sang browser visual check / automated tests / main quest completion rules. |
| `TEST_REPORT.md` | Modified | `Current Runtime Snapshot`, `Live Runtime Verification`, `MQM-01 Frontend Validation` sections | Ghi ro ket qua Docker/API/frontend/MySQL song, cap nhat reviewer ACCEPT, va giu limitation browser visual unavailable cho dung su that runtime. |
| `AGENT_NOTES.md` | Modified | tail section | Them ghi chu closeout voi reviewer ACCEPT, live verification counts, va limitation browser automation unavailable. |
| `changelogs.md` | Modified | tail section | Them entry closeout nay theo full AGENTS format. |

### 3. Features added

- [x] No code feature change; documentation now reflects final accepted live state.

### 4. Bugs fixed

- [x] Removed stale documentation claims that services were down or API verification was blocked.
- [x] Recorded final reviewer acceptance and live Docker/API/DB verification truthfully.

### 5. Code removed

- [x] None

### 6. Commands run

```bash
Get-Content TASKS.md
Get-Content TEST_REPORT.md
Get-Content AGENT_NOTES.md
Get-Content changelogs.md
git diff --check -- TASKS.md TEST_REPORT.md AGENT_NOTES.md changelogs.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
reviewer-gpt55: ACCEPT
docker compose up --build -d: passed
docker compose ps: frontend/backend/mysql running, mysql healthy
GET /api/health: online
frontend http://localhost:5173: returns Vite HTML
API counts: total_quests=1638, current-window quests=21, main_quests=312, study_plan_weeks=78
Current week payload: week=1, sessions=4, week_start=2026-06-04, first session date=2026-06-04, material_summary populated
MySQL counts: study_plan_weeks=78, study_plan_sessions=312, main_quests=312, daily_quests=1638
Scoped git diff --check: passed
Browser automation unavailable; no screenshot/DOM walkthrough captured
```

### 8. Remaining issues

- [ ] Browser visual screenshot/DOM walkthrough was not captured because browser automation is unavailable.

### 9. Suggested next step

- Neu can them do tin cay UI, thuc hien browser visual verification hoac them automated frontend/runtime tests trong mot task rieng.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new or modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.
## [2026-06-04 14:42] Thêm kiểm tra tự động cho Main Quest Map và Daily Quest date logic

**Agent:** coder-gpt54
**Status:** Done
**Related task:** add automated frontend/runtime checks for Main Quest Map and Daily Quest date logic

### 1. Tóm tắt

Đã thêm bộ kiểm tra runtime phía frontend, không cần dependency mới, để khóa hành vi ghép dữ liệu `study-plan weeks/sessions` với `main-quests` và logic ngày của Daily Quest. Ở vòng fix này, test đã được làm ổn định theo múi giờ host bằng local mock không offset và ca child-process có `TZ` tường minh, đồng thời bổ sung assertions băng qua ranh giới DST thật trong `America/Los_Angeles`.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/package.json` | Chỉnh sửa | `@@ -9 +9,2 @@` | Thêm script `test:dashboard-data` để chạy bộ kiểm tra bằng Node test runner sẵn có. |
  | `frontend/src/dashboard-data.test.js` | Thêm mới | `L1-L343` | Thêm test runtime cho `buildMainQuestMap`, `getQuestStatus`, `getCompletionMode`, `getQuestEarnedXp`, `buildDashboardView`, helper spawn theo `TZ`, và assertions DST thật cho `America/Los_Angeles`. |
| `changelogs.md` | Chỉnh sửa | `L475-L570` | Cập nhật mục changelog để phản ánh fix cycle này, line range hiện tại, và kết quả xác minh theo nhiều múi giờ. |

### 3. Tính năng đã thêm

- [x] Thêm lệnh ổn định `npm.cmd run test:dashboard-data` cho kiểm tra frontend/date logic mục tiêu.
- [x] Thêm test tự động cho integrity join giữa study-plan sessions và main quests.
- [x] Thêm test tự động cho logic ngày Daily Quest và ca DST/múi giờ.
- [x] Xác minh cùng một suite dưới `UTC`, `Asia/Ho_Chi_Minh`, và `America/Los_Angeles`.

### 4. Lỗi đã sửa

- [x] Ngăn hồi quy cho lỗi session không có main quest khớp, link trùng, hoặc main quest mồ côi bằng test tự động.
- [x] Ngăn hồi quy cho các trạng thái ngày sai lệch quanh `overdue`, `expired`, XP khi hoàn thành trễ, và tính tuần hiện tại/ngày chờ bắt đầu.
- [x] Ngăn hồi quy cho bug cũ kiểu chia mili-giây `/86400000` bằng assertions qua ngày đổi DST và tuần bắc qua DST.

### 5. Mã đã loại bỏ

- [x] None

### 6. Lệnh đã chạy

```bash
Get-Content AGENTS.md
Get-ChildItem -Force
git status --short
Get-Content C:\Users\Admin\.agents\skills\codex-implementation-worker\SKILL.md
Get-Content frontend\package.json
Get-Content frontend\src\dashboard-data.js
Get-Content changelogs.md -TotalCount 120
rg --files frontend | rg "test|spec|vitest|jest|dashboard-data"
npm test -- --runInBand
npm run test:dashboard-data
npm.cmd run test:dashboard-data
npm.cmd run build
git diff --unified=0 -- frontend/package.json frontend/src/dashboard-data.test.js changelogs.md
git status --short frontend\package.json frontend\src\dashboard-data.test.js changelogs.md
Get-Date -Format "yyyy-MM-dd HH:mm"
(Get-Content frontend\src\dashboard-data.test.js | Measure-Object -Line).Lines
(Get-Content frontend\package.json | Measure-Object -Line).Lines
Get-Content changelogs.md -TotalCount 5
$env:TZ='UTC'; npm.cmd run test:dashboard-data
$env:TZ='Asia/Ho_Chi_Minh'; npm.cmd run test:dashboard-data
$env:TZ='America/Los_Angeles'; npm.cmd run test:dashboard-data
git diff --unified=0 -- frontend/src/dashboard-data.test.js changelogs.md
rg -n "Thêm kiểm tra tự động|dashboard-data.test.js|test:dashboard-data" changelogs.md frontend\package.json frontend\src\dashboard-data.test.js
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm test -- --runInBand: failed because frontend/package.json has no generic test script
npm run test:dashboard-data: failed in PowerShell because npm.ps1 is blocked by execution policy
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
npm.cmd run build: passed (Vite production build completed)
TZ=UTC => npm.cmd run test:dashboard-data passed (5 tests, 0 failures)
TZ=Asia/Ho_Chi_Minh => npm.cmd run test:dashboard-data passed (5 tests, 0 failures)
TZ=America/Los_Angeles => npm.cmd run test:dashboard-data passed (5 tests, 0 failures)
```

### 8. Vấn đề còn lại

- [x] None trong phạm vi fix cycle này.

### 9. Bước tiếp theo được đề xuất

- Nếu cần mở rộng thêm coverage, bổ sung các ca biên cho `buildMainQuestMap` khi API trả về tuần trống hoặc dữ liệu ngày không hợp lệ, hoặc đưa suite này vào pipeline frontend chung sau này.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.

## [2026-06-04 19:48] Home dashboard redesign - reviewer fix cycle

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Home dashboard redesign reviewer fix cycle

### 1. Tóm tắt

Đã sửa các lỗi P1 còn lại sau review cho home dashboard redesign: backlog/archive không còn gọi đường lỗi backend với quest expired hoặc future, boss UI ưu tiên `result_status` khi có, status modal hiển thị lại Badge Wall và recent check-ins, và overlay/drawer có focus management + Escape handling mà không còn giật focus về nút close khi form re-render.

### 2. Tệp đã thay đổi

| Tệp | Loại thay đổi | Dòng / khu vực thay đổi | Nội dung thay đổi |
|---|---|---|---|
| `frontend/src/components/DailyQuestPanel.jsx` | Chỉnh sửa | `@@ -2 +2 @@`, `@@ -11 +12,2 @@`, `@@ -70 +72,7 @@` | Thêm `getTodayISO()` và chặn click cho backlog quest expired/future; backlog quest hợp lệ trở thành nút complete thật. |
| `frontend/src/components/QuestOverlay.jsx` | Chỉnh sửa | `@@ -3 +3 @@`, `@@ -11 +11 @@`, `@@ -111 +112 @@`, `@@ -117 +117,38 @@` | Bật tab Archive, thêm panel archive từ quest window hiện tại, và disable action cho quest expired/future. |
| `frontend/src/components/OverlayFrame.jsx` | Chỉnh sửa | khoảng `L1-L95` | Đổi overlay sang dialog có `aria-labelledby`, focus trap, Escape close, restore focus, và dùng `onCloseRef` để tránh cướp focus khi re-render. |
| `frontend/src/components/NavigationDrawer.jsx` | Chỉnh sửa | khoảng `L1-L113` | Thêm dialog semantics, focus trap, Escape close, nút close riêng, và bật Archive trong submenu Quest. |
| `frontend/src/dashboard-data.js` | Chỉnh sửa | `@@ -748 +749 @@`, `@@ -759 +760 @@`, `@@ -770 +771,2 @@`, `@@ -775 +777,2 @@` | Boss view dùng `result_status` ưu tiên để tính `uiStatus` và `displayStatus`. |
| `frontend/src/components/BossTimelinePanel.jsx` | Chỉnh sửa | `@@ -18 +18 @@` | Timeline hiển thị `displayStatus` + `uiStatus` thay vì `status` thô. |
| `frontend/src/components/BossOverlay.jsx` | Chỉnh sửa | `@@ -26 +26 @@` | Boss hero hiển thị `displayStatus`. |
| `frontend/src/components/StatusModal.jsx` | Chỉnh sửa | `@@ -1 +2 @@`, `@@ -27 +30,2 @@`, `@@ -170 +174 @@`, `@@ -173 +177,25 @@` | Khôi phục Badge Wall thật và recent check-in history trong status modal. |
| `frontend/src/App.jsx` | Chỉnh sửa | `@@ -382 +382 @@`, `@@ -403 +404,2 @@`, `@@ -415 +418 @@` | Truyền `badges`, `recentCheckins`, `allQuests`; support panel boss dùng `displayStatus`. |
| `frontend/src/styles.css` | Chỉnh sửa | `@@ -793 +794,6 @@`, `@@ -1172 +1179,11 @@`, `@@ -1219 +1236,2 @@` | Bổ sung style cho backlog button, nav drawer header/close button, và icon close navigation. |
| `changelogs.md` | Chỉnh sửa | tail section | Thêm entry fix cycle này theo format AGENTS. |

### 3. Tính năng đã thêm

- [x] Archive tab khả dụng để duyệt quest trong cửa sổ hiện tại.
- [x] Overlay và navigation drawer có keyboard handling tốt hơn.
- [x] Status modal hiển thị lại badge và recent check-ins thật.

### 4. Lỗi đã sửa

- [x] Không còn cho complete quest expired hoặc future từ backlog/archive.
- [x] Không còn dùng sai `status` khi backend có `result_status` cho boss result.
- [x] Không còn giật focus về nút close khi nhập/check-in trong status modal.
- [x] Không còn thiếu Badge Wall và recent check-in history trong status modal.

### 5. Mã đã loại bỏ

- [x] Removed broken close-handler dependency pattern that re-focused overlays on every re-render.
- [ ] None

### 6. Lệnh đã chạy

```bash
Get-Content frontend\src\components\DailyQuestPanel.jsx
Get-Content frontend\src\components\BossTimelinePanel.jsx
Get-Content frontend\src\components\OverlayFrame.jsx
Get-Content frontend\src\components\StatusModal.jsx
Get-Content frontend\src\dashboard-data.js | Select-Object -Skip 720 -First 90
Get-Content frontend\src\App.jsx | Select-Object -Skip 300 -First 180
Get-Content backend\app\services.py | Select-Object -Skip 220 -First 60
Get-Content frontend\src\components\QuestOverlay.jsx
Get-Content frontend\src\components\NavigationDrawer.jsx
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/App.jsx frontend/src/styles.css frontend/src/dashboard-data.js frontend/src/components/DailyQuestPanel.jsx frontend/src/components/BossTimelinePanel.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/OverlayFrame.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/StatusModal.jsx
git diff --unified=0 -- frontend/src/components/DailyQuestPanel.jsx frontend/src/components/BossTimelinePanel.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/OverlayFrame.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/StatusModal.jsx frontend/src/dashboard-data.js frontend/src/App.jsx frontend/src/styles.css
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Kết quả kiểm tra

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
git diff --check: passed except LF/CRLF normalization warnings only
reviewer-gpt55 rerun: ACCEPT
```

### 8. Vấn đề còn lại

- [ ] Browser visual walkthrough vẫn chưa có.
- [x] Không còn P0/P1 sau reviewer rerun.

### 9. Bước tiếp theo được đề xuất

- Nếu cần tăng độ tin cậy UI, bổ sung browser visual walkthrough hoặc component/browser tests cho focus trap và disabled quest actions.

### 10. Checklist người dùng cần rà soát

- [ ] Tôi đã rà soát các tệp được thay đổi.
- [ ] Tôi đã kiểm tra phạm vi dòng được thay đổi.
- [ ] Tôi đã kiểm tra tính năng mới hoặc đã chỉnh sửa.
- [ ] Tôi đã kiểm tra kết quả xác thực.
- [ ] Tôi đã phê duyệt tác vụ này.
## [2026-06-05 08:48] Phase 1 UX smoothing - game system daily loop

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Phase 1 UX Smoothing - Game System Daily Loop

### 1. Summary

Implemented the first UX smoothing slice for the dashboard daily loop. The frontend now has a shared presence layer for overlay/drawer/inbox surfaces, lazy-loaded heavy overlays with visible fallback shells, per-item pending feedback for quests and suggestions, inline check-in save feedback, and a small toast rack plus reward pulse for daily progress actions.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/App.jsx` | Modified | `L1-L617`, especially import/state blocks, `load*` helpers, mutation handlers, and overlay render section | Reworked the app shell to lazy-load heavy overlays, keep transient mutation state in one place, use `startTransition` for non-urgent refreshes, add toast handling, and wire per-action feedback into quest/check-in/suggestion flows. |
| `frontend/src/components/usePresenceLayer.jsx` | Added | `L1-L109` | Added the shared interaction helper for presence timing, focus restore, `Esc`, optional focus trap, outside-dismiss, and delayed unmount. |
| `frontend/src/components/OverlayFrame.jsx` | Modified | full file / dialog shell behavior | Migrated overlays to the shared presence helper so exit animation can complete before unmount while keeping dialog semantics and focus control. |
| `frontend/src/components/NavigationDrawer.jsx` | Modified | full file / drawer shell behavior | Migrated the navigation drawer to the shared presence helper for focus restore, outside-dismiss, and delayed unmount. |
| `frontend/src/components/SuggestionInboxDropdown.jsx` | Modified | full file / inbox open-close behavior and action buttons | Added shared presence behavior for the inbox dropdown and per-row pending states for apply/dismiss actions. |
| `frontend/src/components/DailyQuestPanel.jsx` | Modified | full file / quest button rendering and summary cards | Added pressed/pending/success feedback for daily and backlog quests plus reward pulse styling hooks on the daily quest progress summary. |
| `frontend/src/components/QuestOverlay.jsx` | Modified | overlay wrapper and archive tab area | Routed quest feedback props through the overlay and added pending/success handling for archive actions. |
| `frontend/src/components/StatusModal.jsx` | Modified | check-in editor section and overlay wrapper | Added inline save feedback, saving-state button lock, control disabling while saving, and presence-aware overlay mounting. |
| `frontend/src/components/CertificateOverlay.jsx` | Modified | overlay wrapper | Switched the certificate surface to the shared overlay behavior so it participates in lazy mount and exit motion. |
| `frontend/src/components/BossOverlay.jsx` | Modified | overlay wrapper and boss hero meta line | Switched the boss surface to the shared overlay behavior and cleaned the stage/date separator copy. |
| `frontend/src/components/OverlayShellFallback.jsx` | Added | `L1-L24` | Added a fallback overlay shell so lazy-loaded heavy overlays never open into a blank pause. |
| `frontend/src/components/ToastRack.jsx` | Added | `L1-L14` | Added the small toast rack used for quest, check-in, suggestion, and failure feedback. |
| `frontend/src/styles.css` | Modified | motion token block, overlay/drawer/inbox animation sections, quest/support feedback sections, toast/fallback styles around `L33-L78`, `L804-L890`, `L1055-L1146`, `L1445-L1646`, `L1891-L1982`, `L2094-L2235` | Standardized motion tokens, added delayed-unmount motion states, pending/success visual feedback, inline feedback styling, toast/fallback shells, and reduced-motion coverage for the new interactions. |
| `changelogs.md` | Modified | new tail entry | Added this task record. |

### 3. Features added

- [x] Shared presence layer for overlays, the navigation drawer, and the suggestion inbox dropdown.
- [x] Lazy loading plus fallback shell for heavy overlays: Status, Quest, Certificate, and Boss.
- [x] Per-item pending feedback for quest completion and suggestion actions.
- [x] Inline check-in save acknowledgment plus non-blocking error feedback.
- [x] Toast rack and reward pulse microfeedback for the daily loop.

### 4. Bugs fixed

- [x] Overlay and drawer close actions no longer hard-unmount before exit motion can play.
- [x] Suggestion apply/dismiss no longer locks the entire inbox while one row is updating.
- [x] Daily quest actions now guard against double-submit during the active mutation.
- [x] Opening a lazy overlay no longer risks a blank pause with no visible shell.

### 5. Code removed

- [x] Removed duplicated focus-trap / escape-handling logic from `OverlayFrame` and `NavigationDrawer` by centralizing it in `usePresenceLayer`.
- [ ] None

### 6. Commands run

```bash
Get-ChildItem -Force
rg --files
Get-Content AGENTS.md
Get-Content TASKS.md
Get-Content changelogs.md
Get-Content frontend\package.json
Get-Content frontend\src\App.jsx
Get-Content frontend\src\styles.css
Get-Content frontend\src\components\OverlayFrame.jsx
Get-Content frontend\src\components\NavigationDrawer.jsx
Get-Content frontend\src\components\SuggestionInboxDropdown.jsx
Get-Content frontend\src\components\DailyQuestPanel.jsx
Get-Content frontend\src\components\StatusModal.jsx
Get-Content frontend\src\components\QuestOverlay.jsx
Get-Content frontend\src\components\BossOverlay.jsx
Get-Content frontend\src\components\CertificateOverlay.jsx
Get-Content frontend\src\components\WeeklyMissionCard.jsx
Get-Content frontend\src\components\CheckInPanel.jsx
Get-Content frontend\src\dashboard-data.js
rg -n "statusLabel|earnedXp|quest_date|backlogQuests|todayQuests|buildSuggestionInbox|key:" frontend/src/dashboard-data.js frontend/src/dashboard-data.test.js
rg -n "quest-node|backlog-item|system-button|overlay-shell|drawer-shell|support-panel|empty-state|checkin-pill|suggestion-actions|inbox-cluster|overlay-frame__body|panel-frame__header|status-checkin-editor|subsection-divider" frontend/src/styles.css
git status --short
git diff --stat -- frontend/src/App.jsx frontend/src/styles.css frontend/src/components/OverlayFrame.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/SuggestionInboxDropdown.jsx frontend/src/components/DailyQuestPanel.jsx frontend/src/components/StatusModal.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/CertificateOverlay.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/usePresenceLayer.jsx frontend/src/components/OverlayShellFallback.jsx frontend/src/components/ToastRack.jsx changelogs.md
git diff --unified=0 -- frontend/src/App.jsx frontend/src/styles.css frontend/src/components/OverlayFrame.jsx frontend/src/components/NavigationDrawer.jsx frontend/src/components/SuggestionInboxDropdown.jsx frontend/src/components/DailyQuestPanel.jsx frontend/src/components/StatusModal.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/CertificateOverlay.jsx frontend/src/components/BossOverlay.jsx frontend/src/components/usePresenceLayer.jsx frontend/src/components/OverlayShellFallback.jsx frontend/src/components/ToastRack.jsx
npm.cmd run build
npm.cmd run test:dashboard-data
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
npm.cmd run build: passed
npm.cmd run test:dashboard-data: passed
dashboard-data suite: 5 tests, 0 failures
Manual browser smoke check for overlay/daily-loop interactions: not run in this environment
```

### 8. Remaining issues

- [ ] Manual interaction verification for overlay open/close motion, focus behavior, and daily loop feedback is still pending.
- [ ] No browser automation or screenshot pass was captured for the new lazy fallback and toast states.

### 9. Suggested next step

- Run a manual laptop smoke check for nav/inbox/status/quest interactions and confirm that pending, toast, and success pulse states feel correct in the live browser.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 09:43] Weekly touchpoint polish for Phase 1 UX smoothing

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Finish the missing weekly touchpoint polish from Phase 1 UX smoothing

### 1. Summary

Finished the remaining weekly touchpoint slice in the frontend. The weekly mission support surface now acts like a real touchpoint that opens the Weekly quest tab, weekly mission data is normalized into a stable progress/state model with fallback behavior, and weekly mission progress now emits pulse/toast feedback when quest updates advance the mission.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `frontend/src/App.jsx` | Modified | weekly helpers + weekly mission state around `formatHostDateTime()`, `loadWeeklyMission()`, `weeklyTouchpoint` memo, and the support-panel render block | Added weekly mission normalization, weekly progress snapshot comparison, weekly pulse/toast feedback, and made the weekly support surface open the Weekly tab directly. |
| `frontend/src/components/QuestOverlay.jsx` | Modified | weekly tab props / `WeeklyMissionCard` call site | Routed weekly loading, error, and pulse state into the Weekly tab card. |
| `frontend/src/components/WeeklyMissionCard.jsx` | Modified | full component rewrite | Upgraded the weekly overlay card with live/fallback state labels, progress meter, helper copy, and normalized objective rows. |
| `frontend/src/components/WeeklyMissionPanel.jsx` | Modified | full component rewrite | Brought the compact weekly panel in line with the new normalized weekly mission shape for future reuse. |
| `frontend/src/dashboard-data.js` | Modified | `WEEKLY_MISSION_PATTERNS` titles around `L98-L122` | Replaced the remaining dot separators in weekly mission titles with ASCII-safe `/` separators. |
| `frontend/src/styles.css` | Modified | weekly/support styles around `L811-L824`, `L1456-L1512`, `L2252-L2278` | Added interactive styling for the weekly support panel plus progress/state visuals for weekly mission cards and pulse styling for weekly updates. |
| `TASKS.md` | Modified | current state / completed / in-progress / next candidate sections near the top of the file | Recorded that weekly touchpoint polish is done and noted the current frontend build regression plus remaining manual/browser follow-up. |
| `changelogs.md` | Modified | new tail entry | Added this task record. |

### 3. Features added

- [x] Clickable weekly support touchpoint that opens the Weekly quest board.
- [x] Normalized weekly mission model with progress percent, state label, fallback source label, and helper copy.
- [x] Weekly progress pulse and toast feedback when quest completion advances the weekly mission.
- [x] Weekly overlay card now shows a progress meter and per-objective progress labels.

### 4. Bugs fixed

- [x] Weekly mission titles no longer show the remaining non-ASCII separator glyph.
- [x] Weekly mission fallback no longer collapses to a blank/minimal state when the live weekly payload is unavailable.
- [x] Weekly progress changes were previously silent; they now produce visible weekly feedback in the loop.

### 5. Code removed

- [x] Removed the old flat weekly-card rendering path in favor of the normalized weekly touchpoint presentation.
- [ ] None

### 6. Commands run

```bash
Get-Content C:\Users\Admin\.agents\skills\agent-skills\skills\incremental-implementation\SKILL.md
Get-Content C:\Users\Admin\.agents\skills\agent-skills\skills\frontend-ui-engineering\SKILL.md
Get-Content frontend\src\components\WeeklyMissionCard.jsx
Get-Content frontend\src\components\WeeklyMissionPanel.jsx
rg -n "WeeklyMission|weekly|mission" frontend/src/App.jsx frontend/src/components frontend/src/styles.css frontend/src/dashboard-data.js
Get-Content frontend\src\App.jsx
Get-Content frontend\src\dashboard-data.js
Get-Content frontend\src\components\QuestOverlay.jsx
Get-Content frontend\src\components\PanelFrame.jsx
Get-Content frontend\src\components\HomeTopBar.jsx
Get-Content frontend\src\styles.css | Select-Object -Skip 880 -First 180
Get-Content frontend\src\styles.css | Select-Object -Skip 2140 -First 140
rg -n "support-panel|weekly-highlight|mission-card|mission-item|mission-lines|weekly-progress" frontend/src/styles.css
npm.cmd run build
npm.cmd run test:dashboard-data
git diff --check -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/components/QuestOverlay.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/WeeklyMissionPanel.jsx frontend/src/styles.css TASKS.md changelogs.md
git diff --unified=0 -- frontend/src/App.jsx frontend/src/dashboard-data.js frontend/src/components/QuestOverlay.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/components/WeeklyMissionPanel.jsx frontend/src/styles.css TASKS.md changelogs.md
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [ ] Passed
- [x] Failed
- [ ] Not run

Details:

```text
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
npm.cmd run build: failed in Vite/Rolldown with [plugin vite:build-html] "fileName" / "name" must not be absolute; received "D:/better_english/ielts-quest-dashboard/frontend/index.html"
Manual browser smoke check: not run in this environment
git diff --check: passed except LF/CRLF normalization warnings only
```

### 8. Remaining issues

- [ ] Frontend production build is currently blocked by the Vite/Rolldown HTML emit error above.
- [ ] Manual interaction verification for the weekly touchpoint and the broader overlay/daily-loop motion is still pending.

### 9. Suggested next step

- Run one focused follow-up on the frontend build regression, then do a manual laptop smoke check of the Weekly touchpoint in the live browser.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.

## [2026-06-05 10:01] Reward claim flow for main / daily / weekly missions

**Agent:** coder-gpt54
**Status:** Done
**Related task:** Add burger-button reward dot and explicit CLAIM flow for main, daily, and weekly mission rewards

### 1. Summary

Implemented an explicit reward-claim loop across the dashboard. Quest completion no longer banks XP immediately; instead, completed main/daily quests and completed weekly missions surface `CLAIM` actions, the burger button shows a red notification dot while rewards are waiting, and backend progress now only counts claimed quest/weekly XP.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `backend/app/models.py` | Modified | `Quest` and `WeeklyMission` models around their reward/status fields | Added `reward_claimed` and `reward_claimed_at` fields for quest and weekly mission reward tracking. |
| `backend/app/schemas.py` | Modified | `QuestOut`, `WeeklyMissionOut` | Exposed the new claim-state fields to the frontend. |
| `backend/app/services.py` | Modified | `sync_quest_statuses()`, new `recompute_weekly_missions()`, `recompute_player_progress()`, `recompute_skill_progress()`, `complete_quest_instance()`, `uncomplete_quest_instance()` | Shifted XP accounting to claimed rewards only, recomputed weekly mission objective progress from live quest/check-in/tracker data, and blocked rollback after a claimed quest reward. |
| `backend/app/main.py` | Modified | `serialize_quest()`, summary XP queries, new quest/weekly claim endpoints | Added `/api/quests/{id}/claim` and `/api/weekly-missions/{id}/claim`, plus summary XP queries that only count claimed rewards. |
| `backend/alembic/versions/20260605_04_reward_claim_flow.py` | Added | full file | Added the additive migration for reward-claim columns and backfilled existing completed quest/weekly rewards as already claimed so current progress does not drop. |
| `frontend/src/dashboard-data.js` | Modified | `getSessionXpMeta()`, new quest-action helpers, `buildDashboardView()` | Normalized reward-claimed state for quests and added shared UI helpers for `COMPLETE` / `CLAIM` / `CLAIMED` button states. |
| `frontend/src/App.jsx` | Modified | quest/weekly action handlers, weekly touchpoint memo, top-shell support copy, overlay props | Replaced the old complete-only quest mutation flow with explicit claim actions, weekly-claim handling, pending reward count, and updated top-shell status text. |
| `frontend/src/components/HomeTopBar.jsx` | Modified | burger button | Added the red notification dot for pending reward claims. |
| `frontend/src/components/DailyQuestPanel.jsx` | Modified | full component rewrite | Replaced card-as-button behavior with explicit per-quest action buttons and reward-state messaging. |
| `frontend/src/components/MainQuestMapPanel.jsx` | Modified | full component rewrite | Added `COMPLETE` / `CLAIM` controls to main-quest session cards and kept the roadmap expansion behavior intact. |
| `frontend/src/components/QuestOverlay.jsx` | Modified | main/daily/archive/weekly action wiring | Routed claim actions through all quest tabs and connected weekly mission claim handling. |
| `frontend/src/components/WeeklyMissionCard.jsx` | Modified | claim row below progress block | Added a gated weekly reward claim button and reward-cache copy. |
| `frontend/src/styles.css` | Modified | topbar notify dot + quest/claim action styles around quest/main/weekly sections | Added the burger-dot indicator plus button states/layout support for claim actions. |
| `frontend/src/dashboard-data.test.js` | Modified | completed main-quest fixture expectation | Updated the test fixture to reflect the new claimed reward wording. |
| `TASKS.md` | Modified | top project state and next steps | Recorded the new reward-claim loop and refreshed validation/project-state notes. |
| `changelogs.md` | Modified | new tail entry | Added this task record. |

### 3. Features added

- [x] Explicit `CLAIM` reward flow for completed daily quests.
- [x] Explicit `CLAIM` reward flow for completed main quests.
- [x] Explicit `CLAIM` reward flow for completed weekly missions.
- [x] Burger-button red notification dot while reward claims are pending.
- [x] Backend claim endpoints and additive schema support for quest/weekly claim state.

### 4. Bugs fixed

- [x] XP is no longer banked prematurely on quest completion before the player claims it.
- [x] Weekly mission progress is now derived from live weekly quest/check-in/tracker activity instead of staying static.
- [x] Main quest cards previously had no direct mission action path; they now expose complete/claim controls.

### 5. Code removed

- [x] Removed the old implicit "complete immediately grants XP" frontend assumption.
- [ ] None

### 6. Commands run

```bash
Get-Content C:\Users\Admin\.agents\skills\frontend-design\SKILL.md
Get-Content C:\Users\Admin\.agents\skills\vercel-react-best-practices\SKILL.md
rg -n "claim|reward|xp|complete|completed|weekly-mission|main-quests|quests/" backend frontend/src
Get-Content frontend\src\components\DailyQuestPanel.jsx
Get-Content backend\app\main.py
Get-Content backend\app\services.py | Select-Object -Skip 150 -First 150
Get-Content backend\app\models.py | Select-Object -Skip 120 -First 140
Get-Content backend\app\schemas.py | Select-Object -Skip 70 -First 260
Get-Content frontend\src\components\MainQuestMapPanel.jsx
Get-Content frontend\src\components\NavigationDrawer.jsx
Get-Content backend\app\database.py
Get-ChildItem backend\alembic\versions | Select-Object -ExpandProperty Name
Get-Content backend\alembic\versions\20260603_01_mvp_additive_schema.py | Select-Object -Skip 430 -First 80
Get-Content frontend\src\dashboard-data.test.js
Get-Content frontend\src\styles.css | Select-Object -Skip 1070 -First 320
Get-Content frontend\src\components\QuestOverlay.jsx
Get-Content frontend\src\components\HomeTopBar.jsx
python -m py_compile backend\app\main.py backend\app\models.py backend\app\schemas.py backend\app\services.py backend\app\database.py backend\alembic\versions\20260605_04_reward_claim_flow.py
npm.cmd run test:dashboard-data
npm.cmd run build
Remove-Item -Recurse -Force backend\app\__pycache__,backend\alembic\versions\__pycache__
git status --short
git diff --stat -- backend/app/main.py backend/app/models.py backend/app/schemas.py backend/app/services.py backend/alembic/versions/20260605_04_reward_claim_flow.py frontend/src/App.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/DailyQuestPanel.jsx frontend/src/components/MainQuestMapPanel.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/dashboard-data.js frontend/src/dashboard-data.test.js frontend/src/styles.css TASKS.md changelogs.md
git diff --unified=0 -- backend/app/main.py backend/app/models.py backend/app/schemas.py backend/app/services.py backend/alembic/versions/20260605_04_reward_claim_flow.py frontend/src/App.jsx frontend/src/components/HomeTopBar.jsx frontend/src/components/DailyQuestPanel.jsx frontend/src/components/MainQuestMapPanel.jsx frontend/src/components/QuestOverlay.jsx frontend/src/components/WeeklyMissionCard.jsx frontend/src/dashboard-data.js frontend/src/dashboard-data.test.js frontend/src/styles.css TASKS.md changelogs.md
Get-Date -Format "yyyy-MM-dd HH:mm"
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
python -m py_compile backend/app/*.py + migration: exited 0
npm.cmd run test:dashboard-data: passed (5 tests, 0 failures)
npm.cmd run build: passed
Manual browser smoke check: not run in this environment
```

### 8. Remaining issues

- [ ] Manual browser verification is still needed for the new `Complete -> Claim` loop across main/daily/weekly tabs.
- [ ] The worktree still contains unrelated existing frontend edits and generated dist changes outside this focused task.

### 9. Suggested next step

- Run a live browser smoke check that confirms the burger-dot indicator, quest action states, weekly claim gating, and XP/rank updates only after claim.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed line ranges.
- [ ] I checked the new/modified feature.
- [ ] I checked validation results.
- [ ] I approved this task.
