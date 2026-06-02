# IELTS Quest Dashboard

Website chạy local để theo dõi lộ trình tự học IELTS Academic 18 tháng theo phong cách game hóa mạnh, lấy cảm hứng từ giao diện dark fantasy/status panel. Dự án dùng:

- Frontend: React + Vite
- Backend: FastAPI
- Database: MySQL
- Runtime: Docker Compose

> Lưu ý: giao diện chỉ lấy cảm hứng từ phong cách status/game UI, không dùng tài sản hình ảnh hoặc thương hiệu của bất kỳ tác phẩm cụ thể nào.

---

## 1. Chạy dự án

Yêu cầu máy đã cài Docker Desktop.

```bash
cd ielts-quest-dashboard
docker compose up --build
```

Mở trình duyệt:

```text
Frontend: http://localhost:5173
Backend API docs: http://localhost:8000/docs
MySQL: localhost:3307
```

Tài khoản database mặc định trong `docker-compose.yml`:

```text
Database: ielts_quest
User: ielts_user
Password: ielts_password
Root password: root_password
```

---

## 2. Cấu trúc dự án

```text
ielts-quest-dashboard/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       └── seed.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        └── styles.css
```

---

## 3. Logic game hóa

### Skill được theo dõi

- Listening
- Reading
- Writing
- Speaking
- Vocabulary
- Collocation
- Grammar

### Rank F → S

| Rank |        XP |
| ---- | --------: |
| F    |     0–199 |
| E    |   200–499 |
| D    |   500–999 |
| C    | 1000–1699 |
| B    | 1700–2499 |
| A    | 2500–3499 |
| S    |     3500+ |

### XP tính theo nhiệm vụ hoàn thành

Khi tick hoàn thành quest, backend tự cộng XP cho skill tương ứng, tính lại rank/level và mở badge nếu đủ điều kiện.

---

## 4. Dữ liệu được seed sẵn

Dashboard bắt đầu từ ngày `04/06/2026` và tự tạo 78 tuần học, chia theo giai đoạn:

- Tháng 1–3
- Tháng 4–6
- Tháng 7–9
- Tháng 10–12
- Tháng 13–18

Mỗi tuần có 7 quest:

- Listening Gate / Full Listening Raid
- Vocabulary Crystal / Vocabulary Recovery
- Reading Dungeon / Full Reading Dungeon
- Grammar Forge / Grammar Error Repair
- Writing Scroll / Writing Boss Draft
- Speaking Echo / Speaking Arena
- Collocation Loot / Weekly Status Review

---

## 5. API chính

```text
GET  /api/summary
GET  /api/skills
GET  /api/quests
GET  /api/quests?stage=Tháng 1–3
GET  /api/quests?week_no=1
POST /api/quests/{quest_id}/complete
POST /api/quests/{quest_id}/uncomplete
POST /api/checkins
GET  /api/checkins
GET  /api/badges
GET  /api/boss-battles
POST /api/dev/reset
```

---

## 6. Cách reset dữ liệu

Cách nhanh nhất:

```bash
curl -X POST http://localhost:8000/api/dev/reset
```

Hoặc vào API docs:

```text
http://localhost:8000/docs
```

rồi chạy endpoint `POST /api/dev/reset`.

---

## 7. Gợi ý phát triển tiếp

Các chức năng nên thêm sau:

1. Login local bằng tài khoản cá nhân.
2. Trang Writing Tracker riêng.
3. Trang Speaking Tracker có upload link file ghi âm.
4. Biểu đồ XP theo tuần.
5. Calendar view theo tháng.
6. Import/export CSV.
7. Boss Battle score input cho Listening/Reading/Writing/Speaking.
8. Streak thật theo ngày học liên tục.
