# P1a Execution Prompts — Phase 1a (Production Readiness)

> **⚠️ SUPERSEDED (2026-06-11).** Owner dropped the public-SaaS direction. The app is now a small-group
> tool — see [`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md). Only a tiny "P0 hygiene" subset of the
> prompts below is still relevant (gate dev endpoints, remove hardcoded secret, basic data scoping).
> Do NOT execute these 14-task prompts as-is. Retained for history.

> **Cách dùng:** Mỗi PHASE dưới đây là một prompt độc lập, dán vào một phiên Claude Code mới
> **tại máy local** (có codegraph MCP + Docker). Chạy lần lượt PHASE 0 → 7. Mỗi phase tự verify,
> dừng + báo nếu mơ hồ. **Single-agent, tuần tự** (đã chốt — P1a là chuỗi phụ thuộc, không song song).
>
> **Nguồn sự thật:** task chi tiết nằm trong [`../../TASKS.md`](../../TASKS.md) → block
> "Implementation Plan: Production Readiness — Phase 1a" (PR-1→PR-14). Các prompt này CHỈ điều phối;
> mọi acceptance/verification/file:line lấy từ TASKS.md.
>
> **Đã chốt qua grill (2026-06-11) — KHÔNG quyết lại:**
> 1. CSRF = thư viện `fastapi-csrf-protect`. 2. Cookie: access `path=/`, refresh `path=/api/auth`.
> 3. Email infra = P1b (KHÔNG làm ở P1a). 4. Sentry wire + DSN qua env (trống → no-op).
> 5. Prod artifacts = `docker-compose.prod.yml` + Dockerfile CMD không `--reload`.
> 6. `ENVIRONMENT` flag là công tắc trung tâm.
> 7. Chạy local Claude Code (có codegraph + docker). 8. CẤM đụng P1b trong mọi phase.
>
> **Tiêu chí thoát P1a (DoD do P1a phủ):** #2 no weak secret · #4 safe tokens · #5 no backdoor
> · #6 abuse protection · #7 CI green · #8 observable · partial #9 (deploy artifacts + migration release).
> Còn lại (#1 isolation, #3 email auth, #10 multi-template, #11 page speed, #12 a11y) = **P1b**.

---

## PHASE 0 — Nạp ngữ cảnh + bản đồ thực thi (READ-ONLY)

```
Bạn sắp thực thi Phase 1a (Production Readiness) của ielts-quest-dashboard, single-agent, tuần tự,
tại máy local (có codegraph MCP + Docker). Phase này CHỈ nạp ngữ cảnh — KHÔNG sửa code.

Đọc đúng thứ tự (dùng codegraph_explore TRƯỚC khi Read/Grep — quy tắc CLAUDE.md):
1. CLAUDE.md — engineering rules. Ghi nhớ cứng: app luôn chạy được Docker Compose; docs tiếng Anh;
   KHÔNG xóa feature; codegraph trước Read/Grep; Gap-check gate (task phải `Gap check: [x]` mới archive);
   Session Close format cuối phiên.
2. docs/current/PRODUCTION_ROADMAP.md — §2 (12 Definition of Done), §3 (must-fix), §4 Phase 1 P1a.
3. docs/current/decisions/ADR-004 (PyJWT + httpOnly cookie + CSRF), ADR-005 (Pydantic Settings +
   ENVIRONMENT flag), ADR-006 (migrations release step).
4. TASKS.md → block "Implementation Plan: Production Readiness — Phase 1a" (≈ dòng 44). ĐÂY LÀ SPEC.
   Đọc kỹ: "Scope decisions locked" (6 điểm), "Context — exact current state" (file:line đã verify),
   "Dependency graph", 14 task PR-1→PR-14, 5 Checkpoint, bảng Risk, Open Questions.

Sau đó dùng codegraph_explore xác minh lại các file:line trọng yếu (code có thể đã đổi so với plan):
- backend/app/auth_utils.py:8 (JWT secret fallback) + :17-55 (create_jwt/decode_jwt)
- backend/app/database.py:11-14 (DATABASE_URL default) + :49-67 (run_database_bootstrap)
- backend/app/main.py:210-218 (app + CORS), :221-257 (HTTPBearer + get_current_account),
  :443-452 (on_startup), :455-457 (/api/health), :464-479 (cookie helpers),
  :482-687 (auth routes), :1510/1599/1959 (dev routes), :1612/1640 (test-xp)
- frontend/src/api/client.js (localStorage token + apiFetch)
- backend/app/test_backend.py (TestAuthEndpoints :495-742)

XUẤT: một đoạn "Bản đồ thực thi" (5-8 gạch đầu dòng):
- Xác nhận file:line nào trong plan vẫn đúng, cái nào đã lệch (nếu lệch, ghi rõ dòng mới).
- Thứ tự 8 slice theo dependency graph (PR-1 là nền).
- Đánh dấu Slice 4 (PR-7/8/9 auth cookie + CSRF) là điểm rủi ro cao nhất.
- Liệt kê 5 dependency mới phải thêm: pydantic-settings, PyJWT, fastapi-csrf-protect, slowapi, sentry-sdk[fastapi] (BE) + @sentry/react (FE).

KHÔNG sửa file nào ở phase này. Khi xong, dừng và chờ tôi bảo sang PHASE 1.
```

---

## PHASE 1 — Slice 1: Central config (PR-1, nền móng)

```
Thực thi Task PR-1 trong TASKS.md (block Production Readiness — Phase 1a). Kích skill
`backend-development`. Đây là nền — mọi task sau import nó.

Làm ĐÚNG theo PR-1 trong TASKS.md (đọc lại task đó nguyên văn):
- Tạo backend/app/config.py với pydantic-settings BaseSettings tên `Settings`, module-level `settings`.
- Các field ĐÚNG TÊN (không tự đặt thêm): environment, jwt_secret_key, database_url, cors_origins (+
  property cors_origins_list), app_start_date, sentry_dsn, cookie_secure, csrf_secret_key. + property is_dev/is_prod.
- Thêm pydantic-settings vào backend/requirements.txt (pin 2.x tương thích pydantic 2.10.3).
- Tạo .env.example ở repo root: ENVIRONMENT, JWT_SECRET_KEY, CSRF_SECRET_KEY, DATABASE_URL,
  CORS_ORIGINS, APP_START_DATE, SENTRY_DSN (placeholder, KHÔNG giá trị thật).

ĐIỂM ĐÃ CHỐT (không quyết lại): version pin phải để `pip install -r requirements.txt` PASS (acceptance gate).
Nếu xung đột version với FastAPI 0.115.6 / Pydantic 2.10.3 → DỪNG, báo tôi, KHÔNG tự đổi core.

VERIFY (theo PR-1): trong container backend chạy
  python -c "from app.config import settings; print(settings.environment)"  → in "development"
  pip install -r requirements.txt → thành công
Đối chiếu đủ 4 Acceptance criteria của PR-1. Báo cáo: file đã đổi + kết quả verify.
KHÔNG đụng task khác. Khi xong, dừng chờ PHASE 2.
```

---

## PHASE 2 — Slice 2: Fail-fast secret + PyJWT (PR-2, PR-3) → Checkpoint 1

```
Thực thi Task PR-2 rồi PR-3 trong TASKS.md, tuần tự. Kích skill `backend-development`
(+ `fastapi-templates` cho phần JWT nếu cần). Đây là auth-critical — cẩn thận.

PR-2 (fail-fast secret):
- Trong Settings (PR-1): production THIẾU jwt_secret_key / csrf_secret_key / database_url non-default
  → app TỪ CHỐI khởi động (RuntimeError nêu rõ var thiếu). development → vẫn dùng dev default (local không gãy).
- Xóa fallback "super-secret-key..." ở auth_utils.py:8 (đọc settings.jwt_secret_key).
- Xóa default-creds production ở database.py:11-14 (giữ dev default sau env check).
- auth_utils.py + database.py đọc từ settings, KHÔNG os.getenv trực tiếp.
- VERIFY: `ENVIRONMENT=production python -c "import app.main"` → lỗi rõ ràng; bỏ env → dev boot.
  `grep -r "super-secret-key" backend/` → rỗng.

PR-3 (PyJWT):
- Viết lại create_jwt/decode_jwt (auth_utils.py:17-55) dùng PyJWT (HS256), secret từ settings.jwt_secret_key.
- GIỮ NGUYÊN signature + return shape: create_jwt({"sub": str(id)}); decode_jwt trả payload dict hoặc
  None khi lỗi (catch jwt.PyJWTError → None, KHÔNG raise ra ngoài). Giữ exp=1h, iat. Callers ở
  main.py:234/554/619/660 KHÔNG đổi.
- Thêm PyJWT (2.x) vào requirements.txt; xóa code hmac/base64 thủ công.
- VERIFY: round-trip {"sub":"5"} → decode đúng; token hỏng/hết hạn/rác → None.

CHECKPOINT 1 (sau PR-2,3): backend dev boot bình thường; production thiếu secret → fail-fast rõ;
JWT round-trip qua PyJWT; không còn chuỗi weak-secret trong repo.

ĐIỂM ĐÃ CHỐT: pin PyJWT tương thích; nếu test auth gãy do đổi JWT → KHÔNG sửa test vội ở đây,
ghi nhận để PHASE 6 (PR-12) sửa. Báo cáo + dừng chờ PHASE 3.
```

---

## PHASE 3 — Slice 3: Đóng dev backdoor (PR-4, PR-5, PR-6) → Checkpoint 2

```
Thực thi PR-4, PR-5, PR-6 trong TASKS.md (làm được song song nhưng single-agent thì tuần tự).
Kích skill `backend-development`. Đây là việc cơ học, rủi ro thấp — bám đúng acceptance.

PR-4 (gate dev endpoints): /api/dev/reset (main.py:1510), /api/dev/run_migrations (:1599),
/api/dev/regenerate-quests (:1959), /api/dev/test-xp/* (:1612,1640) phải 404 ở production.
  ĐIỂM ĐÃ CHỐT: dùng "if settings.is_dev" bọc ĐĂNG KÝ route, áp dụng ĐỒNG NHẤT cả 5 route
  (KHÔNG trộn cơ chế per-route guard). Thêm test test_dev_routes_404_in_production.
  VERIFY: TestClient với environment=production → /api/dev/reset → 404; dev → hoạt động như cũ.

PR-5 (seed account gate): seed.py:925-929 tạo ad00000@gmail.com → bọc "if settings.is_dev".
  Production KHÔNG mint account hardcode (defense-in-depth dù PR-11 đã skip seed ở prod).
  VERIFY: gọi seed với environment=production → query account ad00000 → none; dev → có.

PR-6 (CORS từ settings): main.py:212 thay bằng settings.cors_origins_list; allow_credentials=True giữ.
  Xóa IP cũ 18.141.232.235 khỏi mọi nơi (gồm docker-compose.yml:30, :48).
  VERIFY: `grep -r "18.141.232.235"` → rỗng.

CHECKPOINT 2 (sau PR-4,5,6): production → dev routes 404, không seed account hardcode, CORS chỉ từ env,
IP cũ biến mất. Dev không đổi. Báo cáo + dừng chờ PHASE 4.
```

---

## PHASE 4 — Slice 4: Access token → httpOnly cookie + CSRF (PR-7 → PR-8 → PR-9) → Checkpoint 3

```
⚠️ PHASE RỦI RO CAO NHẤT. Thực thi PR-7 → PR-8 → PR-9 TUẦN TỰ (không đảo thứ tự). Đổi sai = mọi
request auth gãy. Kích skill `backend-development` + `fastapi-templates` (PR-7/9), `frontend-ui-engineering` (PR-8).

PR-7 (BE: access token → cookie): thêm set_access_cookie/clear_access_cookie giống refresh helpers
(main.py:464-479) nhưng cookie name `ielts_at`, httponly=True, samesite="lax",
secure=settings.cookie_secure, path="/" (CHỐT), max_age=3600. register/login/refresh (:554-556/619-621/660-662)
set cookie + body KHÔNG còn trả access_token. logout (:665-687) clear access cookie.
get_current_account (:224-257) đọc token từ cookie ielts_at (Cookie(default=None)) THAY HTTPBearer;
bỏ HTTPBearer (:221,225). Refresh cookie cũng thêm secure=settings.cookie_secure (vẫn path=/api/auth).

PR-8 (FE: bỏ localStorage): client.js — xóa TOKEN_KEY/getToken/setTokens/clearTokens (:3-15);
apiFetch (:33-83) KHÔNG thêm Authorization header (cookie tự gửi vì credentials:'include' đã có).
attemptRefresh (:17-31) bỏ setTokens. Sửa caller đọc access_token (grep access_token/setTokens/getToken
trong AuthProvider.jsx, Login.jsx, Register.jsx) — auth state = "/auth/me 200" thay vì token localStorage.
VERIFY: grep localStorage trong frontend/src → không còn token; sau login DevTools localStorage trống token.

PR-9 (CSRF): CHỐT thư viện fastapi-csrf-protect (KHÔNG hand-roll). Thêm vào requirements.txt, config từ
settings.csrf_secret_key. Phát csrf_token cookie (đọc được, KHÔNG httpOnly). Yêu cầu X-CSRF-Token header
trên POST/PUT/PATCH/DELETE; GET KHÔNG chặn. FE apiFetch đọc csrf_token cookie, gắn header cho non-GET.
VERIFY: POST không header → 403; có token → pass; login→quest-claim vẫn chạy.

CHECKPOINT 3 (sau PR-7,8,9): access token là httpOnly cookie (path=/), không còn localStorage;
CSRF chặn POST giả; login→dashboard→claim quest chạy end-to-end trong browser (docker compose up).
Nếu phá hợp đồng FE nào ngoài dự kiến → DỪNG báo tôi. Báo cáo + dừng chờ PHASE 5.
```

---

## PHASE 5 — Slice 5+6: Rate limit + Migration release step (PR-10, PR-11) → Checkpoint 4

```
Thực thi PR-10 rồi PR-11 trong TASKS.md. Kích skill `backend-development`.

PR-10 (rate limit slowapi): thêm slowapi vào requirements.txt; Limiter key theo IP; đăng ký exception
handler. ĐIỂM ĐÃ CHỐT giá trị: register 5/hour/IP, login 10/min/IP, default 120/min/IP. Giữ login lockout
hiện có (main.py:564-594) — rate limit là lớp ngoài bổ sung.
VERIFY: loop POST /api/auth/register quá ngưỡng → 429; 1 login bình thường → 200.

PR-11 (migration ra khỏi startup): on_startup (main.py:443-452) → run_database_bootstrap + seed_database
+ refresh_progress_state chỉ chạy khi settings.is_dev. Production: thêm backend/scripts/migrate.py chạy
`alembic upgrade head` một lần (release step). wait_for_database() giữ ở mọi env.
VERIFY: environment=production boot trên DB đã migrate → không seed thêm, app serve; chạy migrate script
trên DB rỗng → schema lên head; dev vẫn migrate+seed như cũ.

CHECKPOINT 4 (sau PR-10,11): auth endpoints rate-limited; production startup không migrate/seed;
release migrate step verify trên DB rỗng. Báo cáo + dừng chờ PHASE 6.
```

---

## PHASE 6 — Slice 7: Tests xanh + CI (PR-12, PR-13)

```
Thực thi PR-12 rồi PR-13. PR-12 kích skill `test-driven-development`; PR-13 là DevOps.

PR-12 (sửa test cho cookie auth): test_backend.py TestAuthEndpoints (:495-742) hiện assert
data["access_token"] trong body + dùng Bearer header. Sửa thành: assert cookie ielts_at được set,
auth qua cookie jar của TestClient (không Authorization header), gắn CSRF header cho mutation.
Thêm test: test_dev_routes_404_in_production (PR-4), JWT round-trip/tamper (PR-3), register 429 (PR-10),
CSRF-missing 403 (PR-9). Mọi test non-auth khác giữ xanh.
VERIFY: chạy full backend suite → tất cả xanh (68 đã sửa + test mới).

PR-13 (GitHub Actions CI): tạo .github/workflows/ci.yml — push/PR vào main: Python 3.12, cài
backend/requirements.txt, chạy backend suite (test dùng SQLite in-memory + StaticPool, KHÔNG cần DB ngoài —
xem test_backend.py:497-506); Node, npm ci + npm run build + npm run test:dashboard-data trong frontend/.
Fail job nếu test/build fail. KHÔNG có deploy step (PaaS tự auto-deploy từ main).
VERIFY: workflow xanh trên code hiện tại (sau PR-12).

Báo cáo + dừng chờ PHASE 7.
```

---

## PHASE 7 — Slice 8: Observability + prod artifacts (PR-14) → Checkpoint 5 → Gap-check + Docs

```
Thực thi PR-14, rồi chạy review gap + ghi docs đóng P1a.

PR-14 (4 phần): kích skill `backend-development` + `frontend-ui-engineering`.
1. Sentry BE: sentry-sdk[fastapi] vào requirements.txt; init trong main.py CHỈ khi settings.sentry_dsn
   có giá trị (DSN trống → no-op). 2. Sentry FE: @sentry/react vào package.json; init đọc
   import.meta.env.VITE_SENTRY_DSN, no-op khi trống (init ở frontend/src/main.jsx — xác nhận entry file).
3. Backend healthcheck: thêm Docker healthcheck cho service backend (curl/wget GET /api/health, đã có ở
   main.py:455-457). 4. Prod artifacts: tạo docker-compose.prod.yml (CMD không --reload, KHÔNG source
   volume mount, KHÔNG publish port MySQL, env từ secrets); sửa backend/Dockerfile CMD mặc định bỏ --reload
   (dev --reload chuyển sang command override trong docker-compose.yml dev).
VERIFY: `docker compose -f docker-compose.prod.yml config` hợp lệ; DSN trống → app chạy bình thường;
npm run build xanh với @sentry/react.

CHECKPOINT 5 — P1a complete:
- Backend + frontend suite xanh trong CI trên main.
- Smoke production-mode (roadmap §7): thiếu secret → fail-fast; /api/dev/reset → 404; token chỉ ở cookie
  (không localStorage); CSRF chặn POST giả; register → 429; startup không migrate/seed;
  grep sạch "super-secret-key" + "18.141.232.235".

GAP-CHECK (kích skill `code-review-and-quality`):
- Đối chiếu TỪNG PR (PR-1→PR-14) với Acceptance criteria trong TASKS.md.
- Phán verdict `Gap check: [x]` hoặc `[ ]` (kèm lý do/defer) cho từng PR. KHÔNG đánh [x] ẩu —
  đây là điều kiện archive theo CLAUDE.md Gap-check gate.

GHI DOCS (kích skill `documentation-and-adrs`, tiếng Anh):
- docs/history/changelogs.md — entry mới nhất TRÊN CÙNG: P1a đổi gì.
- docs/history/TEST_REPORT.md — output suite (pass/fail) + CI link.
- docs/history/AGENT_NOTES.md — ghi chú factual ngắn.
- TASKS.md — tick [x] + dán verdict `Gap check: [x]` từng PR. CHỈ archive sang tasks-done.md khi TẤT CẢ
  gap-check [x]. Còn [ ] → giữ trong TASKS.md.

ĐÓNG PHIÊN (Session Close format CLAUDE.md):
- Changed: / Validated: / Still open: / Next session should read:
- "Next" = P1b (multi-tenant data isolation, email verify, multi-template) — CHƯA breakdown, để phiên sau.
```

---

## Ràng buộc áp dụng cho MỌI phase

- App phải luôn chạy được bằng Docker Compose (dev compose giữ `--reload`; prod artifact riêng ở PR-14).
- Docs tiếng Anh. KHÔNG xóa feature. Thay đổi additive, low-risk. Giữ API response shape ổn định.
- Dùng codegraph TRƯỚC khi Read/Grep thủ công.
- Worker gặp điểm mơ hồ NGOÀI các "ĐIỂM ĐÃ CHỐT" → DỪNG, hỏi user. KHÔNG tự quyết kiến trúc mới.
- **CẤM đụng P1b** trong mọi phase: KHÔNG sửa `get_active_player`/data-isolation, KHÔNG email verify/
  forgot-password, KHÔNG multi-template onboarding, KHÔNG page-speed/a11y. Thấy cần → ghi "Still open".
- Phạm vi đúng 14 task PR-1→PR-14. Mỗi phase verify xanh mới sang phase sau.

## Bản đồ Phase → Task → Checkpoint

| Phase | Task PR | Checkpoint | Skill chính |
|---|---|---|---|
| 0 | (nạp ngữ cảnh) | — | codegraph (read-only) |
| 1 | PR-1 | — | backend-development |
| 2 | PR-2, PR-3 | Checkpoint 1 | backend-development, fastapi-templates |
| 3 | PR-4, PR-5, PR-6 | Checkpoint 2 | backend-development |
| 4 | PR-7, PR-8, PR-9 | Checkpoint 3 | backend-development, fastapi-templates, frontend-ui-engineering |
| 5 | PR-10, PR-11 | Checkpoint 4 | backend-development |
| 6 | PR-12, PR-13 | — | test-driven-development |
| 7 | PR-14 | Checkpoint 5 | backend-development, frontend-ui-engineering, code-review-and-quality, documentation-and-adrs |
