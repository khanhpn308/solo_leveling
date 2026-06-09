# Plan: Phase 10 & 11 — Backend Ownership Protection + Frontend Auth Shell

Drafted: 2026-06-08  
Status: Ready to implement  
Author: Opus 4.8 planning session

---

## Decisions chốt trước khi code

| # | Quyết định | Lý do |
|---|-----------|-------|
| D1 | Cross-account resource → **404** (không 403) | Không lộ sự tồn tại của resource |
| D2 | Routing frontend → **react-router-dom** | Chuẩn, phục vụ Phase 12–14 |
| D3 | 401 → **logout** (không silent refresh) | Đơn giản cho MVP; nâng cấp sau |
| D4 | Token storage → **localStorage** | Đủ cho MVP; nâng cấp httpOnly cookie sau |
| D5 | Onboarding gate route → **/onboarding** | Phase 12 nối tiếp path này |

---

## Phase 10 — Backend Ownership Protection

### Mục tiêu
Mọi route campaign-scoped resolve player/campaign theo JWT account, không còn `db.query(Player).first()` trong đường đi của route nghiệp vụ.

### Tiêu chí hoàn thành
- [ ] Dependency `get_current_player` + `get_current_campaign` dùng chung (build trên `get_current_account`)
- [ ] ~70 call sites `get_player_or_404` / `get_active_player` → account-scoped
- [ ] Resource với `{id}` trong path verify ownership (cross-account → 404)
- [ ] 43 tests cũ + tests isolation mới đều pass
- [ ] Ownership chain documented trong `SCHEMA_SEMANTICS.md`

### Phạm vi LÀM
- Thêm `get_current_player`, `get_current_campaign` dependency
- Refactor `get_player_or_404` / `get_active_player` thành account-aware
- Wire auth vào tất cả route nghiệp vụ (~70 call sites)
- Ownership guard cho route có `{id}` trong path
- Cập nhật test fixtures + thêm `TestOwnershipIsolationPhase10`

### Phạm vi KHÔNG làm
- Không đổi response shape API
- Không làm multi-campaign
- Không động `/api/health`, `/api/dev/*`, `/api/auth/register|login|refresh`
- Không refactor logic XP / quest / rank
- Không làm frontend

### Lát cắt triển khai

#### Slice 10.1 — Dependency `get_current_player` + `get_current_campaign`
- Mô tả: Thêm 2 dependency cạnh `get_current_account` tại `main.py`. `get_current_player` query `Player.account_id == account.id` → 404 nếu chưa có. `get_current_campaign` gọi `get_active_campaign(db, player)`.
- Files: `backend/app/main.py`
- Verify: 2 account → 2 player khác nhau từ dependency

#### Slice 10.2 — Refactor helper account-aware, giữ seed path
- Mô tả: Đổi `get_active_player` nhận optional `account`, thêm `get_player_or_404_for_account(account, db)`. Giữ `get_active_player(db)` không có account cho seed/startup/dev routes.
- Files: `backend/app/services.py`, `backend/app/main.py`
- Verify: startup seed vẫn chạy; `/api/dev/reset` không break

#### Slice 10.3 — Wire auth nhóm GET read-only
- Mô tả: `/api/summary`, `/api/profile`, `/api/quests`, `/api/quests/today`, `/api/quests/backlog`, `/api/main-quests`, `/api/skills`, `/api/roadmap/phases`, `/api/study-plan/*`, `/api/weekly-mission/current`, `/api/badges`, `/api/boss-battles`, `/api/campaigns/current`
- Files: `backend/app/main.py`
- Verify: curl `/api/summary` không token → 401; với token → 200 đúng player

#### Slice 10.4 — Wire auth nhóm POST mutation
- Mô tả: `/api/quests/{id}/complete`, `/api/quests/{id}/uncomplete`, `/api/quests/{id}/claim`, `/api/weekly-missions/{id}/claim`, `/api/boss-battles/{id}/claim`, `/api/checkins`, `/api/test-records`, `/api/mock-tests`, `/api/writing-entries`, `/api/speaking-entries`, `/api/error-logs`, `/api/weakness-suggestions/*`, `/api/setup`
- Files: `backend/app/main.py`
- Verify: smoke POST từng nhóm với token hợp lệ

#### Slice 10.5 — Wire auth + ownership guard vocabulary/SRS + rank-exam
- Mô tả: Routes có `{id}` trong path phải verify resource thuộc campaign của account. Thêm guard helper `assert_owned_or_404(resource_campaign_id, campaign)`. Vocabulary scoped theo `player_id` (theo DECISIONS.md) — verify `vocabulary_item.player_id == player.id`.
- Files: `backend/app/main.py`, `backend/app/services.py` (helper nhỏ)
- Verify: account A tạo rank-exam attempt → account B GET attempt đó → 404; tương tự vocabulary item

#### Slice 10.6 — Fix test fixtures + `TestOwnershipIsolationPhase10`
- Mô tả: Cập nhật test classes cũ chưa có token (TestWaveDAndE, cũ hơn) để register+login trong setUp. Thêm `TestOwnershipIsolationPhase10`: 2 account, cross-access các resource đại diện bị chặn.
- Files: `backend/app/test_backend.py`
- Verify: toàn bộ suite pass; isolation test đỏ trước wiring, xanh sau

#### Slice 10.7 — Document ownership chain
- Mô tả: Ghi chain `account → player → active_campaign → {quest, attempt, certificate, vocabulary_item...}` và quy ước 401 vs 404 vào SCHEMA_SEMANTICS.md.
- Files: `docs/current/SCHEMA_SEMANTICS.md`
- Verify: doc khớp code

### Docs cập nhật sau Phase 10
- `TASKS.md` → tick Phase 10, move to tasks-done.md
- `docs/current/SCHEMA_SEMANTICS.md` (ownership chain)
- `docs/history/changelogs.md`
- `docs/history/TEST_REPORT.md`
- `docs/history/AGENT_NOTES.md`

---

## Phase 11 — Frontend Auth Shell

### Mục tiêu
AuthProvider + JWT storage + Login/Register pages + ProtectedRoute. Dashboard poll `/api/summary` kèm token; 401 → auto logout.

### Tiêu chí hoàn thành
- [ ] `AuthProvider` cung cấp `{ token, account, login, logout, isAuthenticated, loading }`
- [ ] Login + Register hoạt động, lưu token localStorage, xử lý lỗi 401/duplicate
- [ ] `ProtectedRoute`: chưa login → `/login`; `onboarding_completed=false` → `/onboarding` (placeholder)
- [ ] Dashboard load đúng dữ liệu theo account; 401 → auto logout
- [ ] App chạy qua Docker Compose, không vỡ luồng với account đã onboard

### Phạm vi LÀM
- `react-router-dom` routing
- `apiClient` fetch wrapper (gắn token, parse lỗi)
- `AuthProvider` + `useAuth` context
- Trang Login, Register
- `ProtectedRoute` component
- Wire token vào poll `/api/summary`

### Phạm vi KHÔNG làm
- Không build UI onboarding nhiều bước (Phase 12)
- Không OAuth, reset password (deferred)
- Không silent refresh (defer, ghi task mở)
- Không redesign dashboard hiện có

### Lát cắt triển khai

#### Slice 11.1 — `apiClient` + token storage
- Mô tả: Fetch wrapper đọc token từ localStorage, gắn `Authorization: Bearer`, parse lỗi. Hằng `API_BASE`. Export `apiFetch(path, options)`.
- Files: `frontend/src/api/client.js` (mới), `frontend/src/api/auth.js` (mới — wrap register/login/me/refresh/logout endpoints)
- Verify: gọi `/api/health` + `/api/auth/me` qua client

#### Slice 11.2 — `AuthProvider` + `useAuth`
- Mô tả: State `{ token, account, loading }`. `login()` gọi `auth.login()` → lưu localStorage → set state. `logout()` xóa storage + state. `useEffect` mount: đọc token từ storage → gọi `/api/auth/me` → hydrate account + `onboarding_completed`.
- Files: `frontend/src/auth/AuthProvider.jsx` (mới), `frontend/src/auth/useAuth.js` (mới)
- Verify: mount với token hợp lệ → state hydrated; token hỏng → state cleared

#### Slice 11.3 — Trang Login + Register
- Mô tả: Form email/password, gọi `useAuth().login()` / `useAuth().register()`, hiển thị lỗi (sai mật khẩu, email trùng), redirect sau thành công.
- Files: `frontend/src/pages/Login.jsx` (mới), `frontend/src/pages/Register.jsx` (mới), `frontend/src/styles.css` (thêm style form)
- Verify: đăng ký account mới → redirect vào app; login sai → hiển thị lỗi

#### Slice 11.4 — Routing + `ProtectedRoute` + bọc App
- Mô tả: Thêm `react-router-dom`. Route: `/login`, `/register`, `/onboarding` (placeholder), `/` (dashboard). `ProtectedRoute`: chưa login → `/login`; `onboarding_completed=false` → `/onboarding`.
- Files: `frontend/src/App.jsx`, `frontend/src/auth/ProtectedRoute.jsx` (mới), `frontend/src/main.jsx`, `frontend/package.json` (thêm dep)
- Verify: truy cập `/` khi chưa login → redirect `/login`; sau login đúng → vào dashboard

#### Slice 11.5 — Wire token vào poll `/api/summary` + 401 handler
- Mô tả: Đổi fetch `/api/summary` trong App sang `apiFetch`. Nếu 401 → gọi `logout()` → redirect `/login`.
- Files: `frontend/src/App.jsx`
- Verify: token hết hạn → auto về `/login`; token hợp lệ → dashboard load đúng data account

### Deps cần cài
```
npm install react-router-dom
```

### Docs cập nhật sau Phase 11
- `TASKS.md` → tick Phase 11, move to tasks-done.md
- `docs/history/changelogs.md`
- `docs/history/AGENT_NOTES.md`
- `docs/current/PROJECT_CONTEXT.md` (mô tả auth shell)

---

## Tasks mở để upgrade sau (ghi vào TASKS.md deferred)

1. **localStorage → httpOnly cookie**: nâng cấp token storage khi backend hỗ trợ Set-Cookie; giảm rủi ro XSS.
2. **Silent refresh 401**: thay vì logout ngay khi 401, thử `/api/auth/refresh` trước; logout nếu refresh fail.
3. **Route `/onboarding`**: Phase 12 nối tiếp path này để build multi-step onboarding UI.

---

## Thứ tự & dependency

```
Phase 10 (backend) → Phase 11 (frontend)
  ├── Slice 11.1–11.3: có thể bắt đầu song song (auth routes đã có)
  └── Slice 11.5: cần Phase 10 xong (dashboard data scope đúng account)
```
