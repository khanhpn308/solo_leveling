# IELTS Quest Dashboard - Quy tắc nghiệp vụ MVP

## Mục đích
Đây là bản tóm tắt nghiệp vụ đã chốt sau 100 câu hỏi làm rõ. Dùng file này làm context sản phẩm chính cho giai đoạn MVP.

## Phạm vi sản phẩm
- Ưu tiên MVP trước.
- 1 người dùng local duy nhất.
- Ghi nhận học tập thủ công trước.
- MVP chưa có auth, chưa có multi-user.

## Mô hình sản phẩm cốt lõi
- App là dashboard tự học IELTS Academic được game hóa.
- Người dùng học qua các quest sinh từ template có sẵn.
- XP đến từ task hoàn thành, không đến từ thời gian học.
- UI phải hiện đồng thời hồ sơ học tập và progression game.

## 7 kỹ năng cần theo dõi
- Listening
- Reading
- Writing
- Speaking
- Vocabulary
- Collocation
- Grammar

## Mô hình quest
- Chỉ dùng template. MVP không có tạo quest tự do.
- Mỗi template có:
  - 1 skill chính
  - XP cố định
  - độ khó: `easy`, `normal`, `hard`
  - mô tả mức độ khó
  - phase được phép xuất hiện
  - tài nguyên/sách liên kết
- Khung XP theo độ khó:
  - `easy`: `5-15`
  - `normal`: `20-30`
  - `hard`: `40-60`
- Khi hoàn thành quest, lưu kết quả ngắn gọn:
  - `status`
  - `completed_at`
  - `earned_xp`
  - ghi chú ngắn
  - `raw_score` nếu phù hợp
  - liên kết sang tracker nếu phù hợp

## Trạng thái quest
- `pending`
- `completed`
- `overdue`
- `expired`

## Vòng lặp daily quest
- Hệ thống tự sinh, user không tự chọn.
- Sinh khi user mở app lần đầu trong ngày.
- Chỉ sinh cho hôm nay, không sinh bù các ngày đã lỡ.
- Mỗi ngày có đúng `3` quest:
  - `1 core`
  - `1 support`
  - `1 mini`
- `core` theo lịch phase có ưu tiên tần suất.
- Phân bổ `core` tuần của Phase 1:
  - Reading `3`
  - Listening `2`
  - Writing `1`
  - Speaking `1`
- Phân bổ `support` tuần của Phase 1:
  - Vocabulary `4`
  - Grammar `2`
  - Collocation `1`
- Mini quest phải dễ hoàn thành để giữ nhịp, nhưng vẫn phải có giá trị học thật.
- MVP không có reroll.
- Daily quest phải hoàn thành trong cùng ngày local. Không có grace period.

## Backlog và hoàn thành muộn
- Daily quest bỏ lỡ sẽ thành backlog.
- Làm backlog không ảnh hưởng đến streak.
- Làm backlog chỉ nhận `50%` XP gốc.
- Backlog chỉ được làm bù trong `3` ngày.
- Quá `3` ngày sẽ thành `expired`.
- Quest làm muộn phải được đánh dấu là hoàn thành muộn, không gộp chung với hoàn thành đúng hạn.

## Vòng lặp weekly mission
- Weekly mission tách riêng khỏi daily quest.
- Weekly mission có thưởng riêng.
- Thưởng chỉ cộng vào `player XP`, không cộng vào skill.
- Weekly mission tính theo tuần lịch.
- Tuần bắt đầu vào `Thứ Hai`.
- Mỗi phase có `2-3` mẫu weekly mission luân phiên.
- Nếu campaign bắt đầu giữa tuần, tuần đầu là onboarding week rút gọn.
- Onboarding week dùng bộ mission riêng, nhẹ hơn.

## Vòng lặp boss battle
- Mỗi tháng có `1` boss.
- Boss là bài test/checkpoint lớn được theme hóa, không phải combat system.
- Boss được gán cố định theo phase/tháng.
- Reward của boss:
  - player XP lớn
  - badge
  - đánh dấu clear trên timeline
- Nếu không clear boss, hiện trạng thái `underprepared` kèm gợi ý luyện bù.
- Boss không bao giờ khóa phase.

## Mô hình phase và campaign
- `1 campaign = 1 roadmap 18 tháng`
- Campaign bắt đầu khi user hoàn tất setup ban đầu.
- Không cho reset sớm.
- `roadmap_start_date` chỉ được sửa trước khi campaign bắt đầu.
- Đã bắt đầu thì khóa lại.
- Hết 18 tháng, campaign kết thúc với trạng thái `completed`.
- Phase đi theo timeline campaign, không đi theo kết quả boss.

## Hồ sơ và setup ban đầu
- Setup ban đầu bắt buộc thu thập:
  - `display_name`
  - `roadmap_start_date`
  - `target_overall_band`
  - `current_estimated_level`
  - `strongest_skill`
  - `weakest_skill`
  - `study_days_per_week`
  - `session_minutes`
  - `daily_mini_study_minutes`
- Setup cũng phải thu thập điểm/chứng chỉ đầu vào để gợi ý skill rank.

## Nguồn điểm/chứng chỉ đầu vào
- `IELTS`
- `TOEIC`
- `Aptis`
- `CEFR` nhập tay

## Quy tắc test history
- Cho phép nhiều record điểm/chứng chỉ.
- Mỗi record bắt buộc có ngày thi/ngày kết quả.
- Khi evidence mâu thuẫn:
  - ưu tiên kết quả mới hơn
  - nếu cùng thời điểm, ưu tiên `IELTS > Aptis > CEFR > TOEIC`
- Thêm test record mới chỉ cập nhật gợi ý.
- Không tự động ghi đè `confirmed skill rank`.

## Skill rank và progression
- Hai lớp này tách riêng.
- `Skill Rank` = mức năng lực đã xác nhận từ evidence.
- `Player Rank` = progression game suy ra từ player level.
- UI phải hiện cả hai.
- `Confirmed skill rank` chỉ đổi khi user áp dụng gợi ý hệ thống.
- Không cho sửa tay trực tiếp sau khi đã xác nhận.
- Phải lưu lịch sử thay đổi `confirmed skill rank`.
- Đổi `confirmed skill rank` không được kéo theo thay đổi skill XP hay skill level.

## Progression của player và skill
- Dùng đồng thời:
  - `player_xp`, `player_level`, `player_rank`
  - `xp`, `level`, `rank` cho từng skill
- `player rank` được suy ra từ `player level`.
- Skill XP chỉ đến từ việc làm quest.
- Thưởng XP của weekly mission chỉ cộng vào player XP.

## Streak, shield, perfect day
- Streak yêu cầu hoàn thành đủ `3 daily quest` trong ngày đó.
- Chỉ `3 daily quest` của ngày hiện tại mới tính streak.
- Backlog, weekly mission, boss không tính vào streak ngày.
- `perfect day` tách riêng với streak.
- Điều kiện `perfect day`:
  - hoàn thành đủ `3 daily quest`
  - có check-in trong ngày đó
- Check-in có thể làm bất kỳ lúc nào trong ngày.
- Mỗi ngày chỉ có `1` check-in, nhưng được phép sửa bản ghi ngày đó.

## Quy tắc shield
- Miss 1 ngày sẽ tốn `1` shield nếu còn shield và streak vẫn được giữ.
- Mỗi `3` ngày streak liên tiếp sẽ hồi `1` shield.
- Tối đa dự trữ `2` shield.
- Ngày được shield cứu streak vẫn giữ streak, nhưng không tính vào tiến độ hồi shield.
- Nếu hết shield và tiếp tục miss ngày cần thiết:
  - `current_streak` reset về `0`
  - tiến độ hồi shield reset về `0`
  - `best_streak` vẫn được giữ
- Miss nhiều ngày mà không mở app vẫn phải tính là miss thật theo lịch.

## Mood / energy / focus
- Check-in hằng ngày là tùy chọn, nhưng phải có nhắc mỗi ngày.
- Trường dữ liệu:
  - `mood` `1-5`
  - `energy` `1-5`
  - `focus` `1-5`
  - ghi chú ngắn tùy chọn

## Error log
- Chỉ lưu lỗi đã hiểu và đã sửa.
- Mỗi record nên có:
  - skill
  - nguồn lỗi
  - mô tả lỗi
  - câu/cách sửa
  - nguyên nhân
  - cách tránh lặp lại
  - ngày ghi
  - `error_tag`

## Writing tracker
- Lưu đầy đủ bài viết và feedback.
- Trường tối thiểu:
  - loại bài
  - đề bài/prompt
  - nội dung bản nháp
  - điểm tự chấm hoặc estimated band
  - feedback note
  - revised text nếu có
  - ngày

## Speaking tracker
- MVP chưa lưu file audio.
- Lưu:
  - part
  - topic
  - cue/question
  - self score
  - self note
  - transcript summary
  - date

## Mock test tracker
- Theo dõi cả `full` và `partial`.
- Trường đề xuất:
  - `test_type`
  - `scope`
  - `source`
  - `raw_score`
  - `estimated_band`
  - `note`
  - `date`
- Với Listening/Reading:
  - user nhập `raw_score`
  - hệ thống tự đổi `estimated_band` nếu đã có rule map
- Nếu rule chưa rõ, vẫn có thể cho override thủ công.

## Weakness note và weakness suggestion
- Giữ `2` lớp riêng:
  - `user_weakness_note`
  - `system_weakness_suggestion`
- User có thể accept suggestion của hệ thống.
- Khi accept, suggestion được copy vào user note theo kiểu append, không overwrite.
- Chống lặp cơ bản:
  - nếu text giống hệt đã tồn tại trong note thì không append
- Mỗi skill tối đa `2` active suggestion cùng lúc.

## Nguồn sinh system weakness suggestion
- pattern kết quả mock test
- `error_tag` lặp lại trong error log
- pattern quest `overdue/expired`
- lâu không luyện skill đó

## Quy tắc sinh suggestion
- Từ mock test:
  - chỉ sinh khi có pattern lặp lại
  - xét `3` record gần nhất
  - sinh suggestion nếu có `2+` kết quả dưới ngưỡng mong đợi hoặc xu hướng giảm 2 lần liên tiếp
- Từ error log:
  - xét trong `30` ngày gần nhất
  - nếu cùng skill có `3+` log cùng `error_tag`
- Từ overdue/expired:
  - xét trong `14` ngày gần nhất
  - nếu cùng skill có `3+` quest overdue/expired
  - hoặc cùng loại template bị expired `2+` lần
- Từ `last_practiced`:
  - core skills: ngưỡng `7` ngày
  - support skills: ngưỡng `5` ngày

## Vòng đời suggestion
- Suggestion hiện trong profile/skill detail dưới dạng pending item.
- User có thể `Apply` hoặc `Dismiss`.
- Pending suggestion không có hạn hết hiệu lực.
- Nếu đã dismiss, suggestion có thể xuất hiện lại nếu có evidence mới.
- Nếu evidence mới gợi ý rank thấp hơn:
  - chỉ thông báo/pending suggestion
  - không tự động áp dụng
  - không ép xác nhận ngay

## Ghi chú cho thiết kế kỹ thuật
Nên tách rõ schema thành các nhóm:
- profile/global progression
- campaign timeline
- quest templates
- quest instances/completions
- test evidence
- confirmed rank history
- weakness suggestions
- trackers và logs
