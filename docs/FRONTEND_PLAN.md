# IELTS Quest Dashboard - Kế hoạch thiết kế frontend

## Trạng thái
- Đã duyệt.
- Chỉ là kế hoạch triển khai.
- Chưa bao gồm thay đổi code.

## Mục tiêu
- Thiết kế lại frontend từ `frontend/src` theo `docs/MVP_BUSINESS_RULES.md`.
- Giữ tinh thần game hóa đậm, nhưng vẫn là dashboard học tập dùng được hằng ngày.
- Ưu tiên trải nghiệm laptop trước, vẫn dùng tốt trên mobile.

## Định hướng thẩm mỹ
- Chủ đề: `Hunter System / IELTS Command Center`.
- Phong cách: dark fantasy + system interface + tactical dashboard.
- Màu chính: cyan / neon blue.
- Màu phụ:
  - amber cho reward / badge / perfect day
  - red-orange cho boss / warning / expired
  - green cho completed / recovery
- Ngôn ngữ hiển thị: tiếng Việt là chính, giữ lại một số thuật ngữ ngắn như `XP`, `Rank`, `Quest`, `Boss`, `Streak`.

## Đánh giá hiện trạng frontend
- `frontend/src/App.jsx` đang là một component lớn, gom cả gọi API và render UI.
- `frontend/src/styles.css` đã có nền dark + neon nhưng còn generic, chưa phản ánh đầy đủ nghiệp vụ MVP mới.
- Frontend hiện tại mới bám các API:
  - `/summary`
  - `/quests`
  - `/checkins`
- Chưa có cấu trúc cho setup ban đầu, weekly mission, backlog, streak/shield, trackers, suggestion inbox.

## Nguyên tắc thiết kế
- Không làm landing page.
- Mở app là màn hình sử dụng thật.
- Hiển thị đồng thời:
  - hồ sơ năng lực học tập
  - progression game
- Tách rõ:
  - `Skill Rank` = năng lực xác nhận
  - `XP/Level` = tiến độ cày trong app
- Tránh card chồng card quá dày.
- Dùng panel rõ vai trò, scan nhanh được.

## Cấu trúc sản phẩm frontend dự kiến
- `Màn setup ban đầu`
- `Dashboard chính`
- `Skill matrix`
- `Quest board`
- `Weekly mission`
- `Boss timeline`
- `Mood / energy / focus check-in`
- `Trackers`
- `Suggestion inbox`

## Cấu trúc màn hình chi tiết

### 1. Setup ban đầu
- Thu thập:
  - hồ sơ người học
  - roadmap start date
  - mục tiêu band
  - lịch học
  - test history
- Hệ thống gợi ý `Skill Rank` từ evidence.
- User xác nhận trước khi bắt đầu campaign.

### 2. Dashboard chính
- Hiển thị:
  - Player Rank
  - Player Level
  - tổng XP
  - campaign hiện tại
  - phase hiện tại
  - thời gian tuần hiện tại
  - streak / shield / perfect day
- Đây là màn hình trung tâm sau khi vào app.

### 3. Skill matrix
- 7 skill cards.
- Mỗi card hiển thị:
  - tên skill
  - icon
  - confirmed rank
  - level
  - XP
  - progress bar
  - last practiced
  - weakness note
  - system suggestions nếu có

### 4. Quest board
- Daily quest hôm nay:
  - `1 core`
  - `1 support`
  - `1 mini`
- Trạng thái rõ:
  - `pending`
  - `completed`
  - `overdue`
  - `expired`
- Có khu backlog riêng.
- Daily quest là trọng tâm thao tác nhanh nhất của dashboard.

### 5. Weekly mission
- Panel riêng, không trộn vào daily quest.
- Hiển thị:
  - tên mission tuần
  - tiến độ
  - reward player XP
  - trạng thái tuần onboarding nếu áp dụng

### 6. Boss timeline
- Mỗi tháng 1 boss.
- Hiển thị theo timeline hoặc danh sách checkpoint.
- Mỗi boss cần có:
  - tên
  - ngày
  - phase
  - mục tiêu
  - trạng thái `clear` hoặc `underprepared`
  - reward

### 7. Check-in
- 1 check-in mỗi ngày.
- Hiển thị:
  - mood
  - energy
  - focus
  - note
- Có lịch sử gần nhất để nhìn nhịp học.

### 8. Trackers
- Error Log
- Writing Tracker
- Speaking Tracker
- Mock Test Tracker
- Dự kiến dùng tab hoặc segmented navigation trong cùng một panel lớn.

### 9. Suggestion inbox
- Chứa:
  - pending skill-rank suggestions
  - weakness suggestions
- Mỗi mục có hành động:
  - `Apply`
  - `Dismiss`

## Kế hoạch component
- `AppShell`
- `SetupWizard`
- `DashboardPage`
- `PlayerStatusPanel`
- `CampaignTimeline`
- `StreakShieldPanel`
- `DailyQuestPanel`
- `QuestCard`
- `BacklogPanel`
- `SkillMatrix`
- `SkillCard`
- `WeeklyMissionPanel`
- `BossBattlePanel`
- `MoodCheckInPanel`
- `TrackerTabs`
- `ErrorLogPanel`
- `WritingTrackerPanel`
- `SpeakingTrackerPanel`
- `MockTestPanel`
- `SuggestionInbox`

## Kế hoạch kỹ thuật frontend
- Refactor `App.jsx` thành nhiều component nhỏ.
- Tách logic API khỏi component render.
- Giữ React + Vite hiện tại.
- Chỉ thêm dependency mới khi thật cần.
- Ưu tiên CSS thuần trước, chưa cần framework UI.

## Kế hoạch CSS / design system
- Tạo bộ biến thiết kế:
  - màu
  - typography
  - spacing
  - panel surface
  - border
  - motion
- Thay font hiện tại bằng bộ font có cá tính hơn.
- Giữ radius nhỏ, panel sắc nét, cảm giác system UI.
- Dùng texture nhẹ:
  - grid
  - scanline
  - noise rất mỏng
- Tránh layout marketing, tránh card quá bo tròn, tránh giao diện generic.

## Nhu cầu dữ liệu từ backend
Frontend MVP hoàn chỉnh sẽ cần backend cung cấp hoặc mở rộng các nhóm dữ liệu sau:
- profile/setup
- campaign hiện tại
- daily quests hôm nay
- backlog
- weekly mission
- boss timeline
- skills với confirmed rank + XP/level
- streak / shield / perfect day
- trackers
- suggestions

## Thứ tự triển khai dự kiến
1. Tách `App.jsx` thành khung component nhỏ nhưng vẫn chạy được.
2. Thiết kế lại shell tổng và design system.
3. Làm màn setup ban đầu.
4. Làm dashboard chính + daily quest + streak/shield + check-in.
5. Làm skill matrix + weekly mission + boss timeline.
6. Làm trackers + suggestion inbox.
7. Kiểm tra build và responsive.

## Ràng buộc khi triển khai
- Không xóa feature cũ nếu chưa thay thế tương đương.
- Giữ app chạy được với Docker Compose.
- Ưu tiên text tiếng Việt dễ hiểu.
- Bám chặt `docs/MVP_BUSINESS_RULES.md` khi hiện thực UI.
