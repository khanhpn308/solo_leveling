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
