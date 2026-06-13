# All-Phases Execution Prompts — Production Roadmap (Phase 1 / 2 / 3)

> **⚠️ SUPERSEDED (2026-06-11).** Owner dropped the public-SaaS direction. The app is now a small-group
> tool — see [`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md). The P1b / Phase 2 / Phase 3 breakdown
> and execution prompts below are NOT pursued. Retained for history.

> **Cấu trúc 2 tầng (đã chốt).** Vì chỉ **P1a** có task breakdown chi tiết sẵn; **P1b / Phase 2 /
> Phase 3** mới là định hướng (chưa có task). Nên mỗi phase lớn có 2 loại prompt:
> - **Tầng A — BREAKDOWN:** bảo agent grill bạn + lập task chi tiết vào `TASKS.md` (giống cách P1a đã làm).
>   Chạy tầng A TRƯỚC, để KHÔNG agent nào phải tự bịa task khi thực thi.
> - **Tầng B — THỰC THI:** chạy task sau khi tầng A đã đẻ ra task trong TASKS.md.
>
> **Thứ tự tổng:** P1a (đã có) → P1b → Phase 2 → Phase 3. Mỗi phase: breakdown xong → review với bạn →
> mới thực thi → mới sang phase sau.
>
> **Nguồn sự thật:** [`../PRODUCTION_ROADMAP.md`](../PRODUCTION_ROADMAP.md) (§2 DoD, §3 must-fix, §4 phases),
> ADR-002..006 trong [`../decisions/`](../decisions/), và [`../../TASKS.md`](../../TASKS.md).
>
> **Tiêu chí đã thống nhất (áp dụng MỌI phase, đã grill 2026-06-11):**
> - Đối tượng: public multi-tenant SaaS, scale nhỏ (vài chục–vài trăm), miễn phí, chưa billing.
> - Giữ TOÀN BỘ tính năng (không cắt). Multi-tenant: shared DB, scope theo `account_id`, sửa tận gốc.
> - Auth: PyJWT + fail-fast secret + access token httpOnly cookie + CSRF (`fastapi-csrf-protect`).
> - Config: Pydantic Settings + `ENVIRONMENT` flag. Deploy: Managed PaaS (Render/Railway) + Student credit.
> - Migration: release step, không seed prod. Chạy LOCAL (có codegraph + Docker). Single-agent tuần tự.
> - Mỗi quyết định kiến trúc mới → DỪNG hỏi user. Dùng codegraph trước Read/Grep. Docs tiếng Anh.

---

# ═══════════════════════════════════════════════════════════
# PHASE 1 — SaaS Foundation (đạt 12 Definition of Done)
# ═══════════════════════════════════════════════════════════

Phase 1 chia 2 sub-milestone: **P1a** (bảo mật/hạ tầng — ĐÃ breakdown) và **P1b** (multi-tenant hoá).

## P1a — đã có sẵn

> P1a (14 task PR-1→PR-14) đã breakdown trong `TASKS.md` và có prompt thực thi riêng:
> [`P1a-EXECUTION-PROMPTS.md`](P1a-EXECUTION-PROMPTS.md) (8 phase: PHASE 0→7).
> **Làm P1a XONG (cả 12 gap-check [x] + 5 checkpoint xanh) rồi mới sang P1b.**

## P1b — Tầng A: PROMPT BREAKDOWN (chạy SAU khi P1a xong)

```
Bạn lập task breakdown chi tiết cho P1b (multi-tenant hoá toàn bộ tính năng) vào TASKS.md. Đây là
phiên ĐỊNH HƯỚNG + BREAKDOWN — KHÔNG code (trừ ghi TASKS.md). Chạy local (codegraph + Docker có).

PHA 1 — NẠP NGỮ CẢNH (codegraph trước Read/Grep):
- CLAUDE.md (engineering rules, Gap-check gate).
- docs/current/PRODUCTION_ROADMAP.md §4 "P1b" + §2 DoD (#1 isolation, #3 email, #10 multi-template,
  #11 page-speed, #12 a11y) + §3 must-fix #1/#5.
- ADR-002 (multi-tenancy shared DB, scope account_id), ADR-004 (auth — nền cho email verify).
- Xác nhận hiện trạng single-player qua codegraph: services.py get_active_player (db.query(Player).first()),
  get_active_campaign; main.py các dependency get_current_player/get_current_campaign vs get_player_or_404;
  đếm route + chỗ resolve player (Grep get_player_or_404|get_active_player|get_current_player trong main.py).
- models.py: cột email_verified_at (chết), AccountToken (cho verify/reset?); CampaignTemplate +
  activate_campaign_for_player (nền multi-template).

PHA 2 — GRILL (kích skill grill-me): hỏi user TỪNG CÂU, mỗi câu kèm khuyến nghị + căn cứ codegraph, cho tới
khi mỗi nhánh chốt cụ thể. Bao phủ tối thiểu:
- Cơ chế sửa isolation: xác nhận "đổi tận gốc — xoá get_active_player().first(), mọi resolve nhận account"
  (đã chốt) → map cụ thể: route nào đang dùng đường sai? sửa theo nhóm nào trước?
- Test cross-account: phạm vi sweep (mọi route? hay nhóm)? chạy trong CI thế nào?
- Email service: nhà cung cấp nào (SendGrid/SES/Resend)? template email? token verify/reset lưu ở đâu
  (AccountToken có sẵn?) TTL bao lâu? rate-limit gửi (đã có slowapi từ P1a)?
- Multi-template onboarding: bao nhiêu template (beginner/intermediate/target band)? nội dung mỗi template
  soạn ở đâu (việc thủ công, tách khỏi code)? UI chọn template ở onboarding hiện tại sửa thế nào?
- Page-speed: ngưỡng đo cụ thể (LCP? thời gian tới dashboard)? giảm ~10 API gọi lúc load (App.jsx) bằng
  cách nào — gộp endpoint hay cache refresh_progress_state?
- A11y: chuẩn nào (WCAG mức nào)? phạm vi (mobile đã làm dở ui_mobile)?
Quy tắc grill: không chấp nhận câu mơ hồ; mâu thuẫn → chỉ ra; hệ quả chưa thấy → nêu rồi hỏi lại.

PHA 3 — BREAKDOWN vào TASKS.md (theo skill planning-and-task-breakdown):
- Thêm block "Implementation Plan: Production Readiness — Phase 1b" ở đầu TASKS.md (sau mục Planned),
  KHÔNG đụng block cũ. Format GIỐNG P1a: mỗi task có Description / Reference (file:line đã verify qua
  codegraph) / Acceptance / Verification / Dependencies / Files / Estimated scope / Gap check: [ ].
- Slice gợi ý (điều chỉnh theo grill): (1) Đổi tận gốc resolve + chuẩn hoá dependency; (2) Test cross-account
  trong CI; (3) Email verify + forgot/reset + email service; (4) Multi-template onboarding (code) + ghi chú
  nội dung thủ công tách riêng; (5) Page-speed; (6) A11y/responsive. Đặt Checkpoint giữa các slice.
- Mỗi task nhỏ ≤5 file, S/M size. Task nào L → chẻ nhỏ. Ghi rõ task nào CHẶN (isolation phải xong trước
  khi mở route mới).
- KHÔNG bịa file:line — verify từng cái qua codegraph trước khi ghi.

KẾT THÚC: xuất danh sách task P1b + xin user duyệt. KHÔNG thực thi code. Cập nhật prompt thực thi P1b
(tầng B dưới) nếu cần khớp slice thực tế.
```

## P1b — Tầng B: PROMPT THỰC THI (chạy SAU khi tầng A đẻ task)

```
Thực thi P1b theo các task vừa breakdown trong TASKS.md (block "Production Readiness — Phase 1b"),
single-agent, tuần tự, local (codegraph + Docker).

⚠️ TASK CHẶN: data-isolation (xoá get_active_player().first(), mọi resolve nhận account) PHẢI xong +
test cross-account XANH trước khi làm bất kỳ task nào mở thêm bề mặt cho user. Đây là DoD #1, must-fix #1.

PHA 0 — nạp ngữ cảnh: CLAUDE.md, PRODUCTION_ROADMAP §4 P1b, ADR-002, ADR-004, block P1b trong TASKS.md.
codegraph xác minh lại file:line trước mỗi task.

PHA 1 — skill theo loại việc:
- Isolation rewrite + email + backend: backend-development (+ fastapi-templates, mysql khi cần).
- Multi-template onboarding code: backend-development + frontend-ui-engineering.
- Test cross-account: test-driven-development.
- Page-speed: performance-optimization + vercel-react-best-practices.
- A11y/responsive: frontend-ui-engineering + web-design-guidelines.
- Review gap + docs cuối: code-review-and-quality + documentation-and-adrs.

PHA 2 — thực thi tuần tự theo slice trong TASKS.md. Sau mỗi task: chạy verify trong Acceptance của task.
Sau mỗi slice: review diff (code-review-and-quality). KHÔNG sang Checkpoint tiếp khi verify chưa xanh.
Đặc biệt: sau slice isolation, chạy test cross-account chứng minh 2 account không thấy dữ liệu nhau.

PHA 3 — ĐIỂM ĐÃ CHỐT (không quyết lại; điểm NGOÀI list → DỪNG hỏi user):
- Isolation: "đổi tận gốc, để máy bắt lỗi" — KHÔNG audit route-by-route thủ công.
- Multi-tenant = shared DB, scope account_id (ADR-002) — KHÔNG instance-per-customer.
- Token/auth: giữ cookie+CSRF từ P1a; email verify đặt account status chờ verify trước khi active.
- Nội dung từng template = việc thủ công TÁCH KHỎI code (task code chỉ làm cơ chế chọn template).

PHA 4 — GAP-CHECK (code-review-and-quality) + DOCS (documentation-and-adrs, tiếng Anh):
- Verdict Gap check [x]/[ ] từng task. Smoke: 2 account không leak; email verify+reset chạy; chọn template
  → campaign riêng; page-speed đạt ngưỡng; a11y pass.
- changelogs.md / TEST_REPORT.md / AGENT_NOTES.md; tick TASKS.md; archive sang tasks-done.md khi đủ gap-check [x].
- Session Close: Changed/Validated/Still open/Next. "Next" = Phase 2.

TIÊU CHÍ THOÁT P1b = THOÁT PHASE 1: cả 12 DoD xanh → ĐƯỢC mở đăng ký cho người lạ. Đây là cột mốc lớn —
DỪNG, báo user trước khi tuyên bố Phase 1 hoàn thành.
```

---

# ═══════════════════════════════════════════════════════════
# PHASE 2 — Expansion (sau khi có user thật)
# ═══════════════════════════════════════════════════════════

> Chỉ bắt đầu khi Phase 1 đã xong + đã có user thật + có tín hiệu retention. Phase 2 phụ thuộc phản hồi
> user nên KHÔNG breakdown trước quá xa — chạy tầng A để định hình lại theo thực tế lúc đó.

## Phase 2 — Tầng A: PROMPT BREAKDOWN

```
Bạn định hướng + breakdown Phase 2 (Expansion) vào TASKS.md. Phiên ĐỊNH HƯỚNG — KHÔNG code (trừ TASKS.md).

PHA 1 — NẠP NGỮ CẢNH: CLAUDE.md; PRODUCTION_ROADMAP §4 Phase 2 (cá nhân hoá roadmap, SRS thật SM-2,
staging, tính năng theo feedback); ADR liên quan. codegraph xác nhận hiện trạng:
- SRS hiện "giả": services.py review_flashcard map cứng again=0/hard=1/good=3/easy=7, ease_factor lưu
  nhưng KHÔNG dùng → SM-2 thật cần sửa hàm này + dùng ease_factor.
- Roadmap/quest hiện sinh từ template cố định (seed.py) → cá nhân hoá cần engine sinh theo user.
- Chưa có staging (Phase 1 auto-deploy thẳng prod).

PHA 2 — GRILL (skill grill-me) các nhánh chưa rõ:
- Cá nhân hoá roadmap: engine sinh quest/plan theo user dựa trên gì (trình độ test đầu vào? mục tiêu band?
  tốc độ học?). Đây là sản phẩm lớn — phạm vi Phase 2 tới đâu (MVP cá nhân hoá vs full)?
- SRS SM-2: thuật toán chính xác (SM-2 chuẩn? biến thể?) — ảnh hưởng ease_factor/interval/repetition.
  Có migrate dữ liệu SRS cũ không?
- Staging: môi trường staging trên PaaS (instance riêng? DB riêng?) — chi phí + workflow promote.
- Tính năng mới theo feedback: liệt kê ứng viên, grill user loại bớt (như đã làm ở Phase 1).
- Retention metric: đo "measurable retention" bằng gì (DoD thoát Phase 2)?

PHA 3 — BREAKDOWN vào TASKS.md (skill planning-and-task-breakdown): block "Phase 2 — Expansion",
format giống P1a/P1b, mỗi task có file:line verify qua codegraph, Acceptance/Verification/Gap check.
Ghi rõ task nào phụ thuộc dữ liệu user thật (không làm được khi chưa có user).

KẾT THÚC: xuất task + xin user duyệt. KHÔNG code. Ghi ADR mới nếu có quyết định kiến trúc lớn
(vd engine cá nhân hoá, thuật toán SRS) — ADR-007+.
```

## Phase 2 — Tầng B: PROMPT THỰC THI (sau tầng A)

```
Thực thi Phase 2 theo task vừa breakdown (block "Phase 2 — Expansion" trong TASKS.md), single-agent,
tuần tự, local. Quy trình giống P1b tầng B:

- Nạp ngữ cảnh (CLAUDE.md, roadmap §4 Phase 2, block Phase 2 TASKS.md, ADR liên quan). codegraph trước Read.
- Skill theo việc: backend-development (engine cá nhân hoá, SRS); test-driven-development (lock thuật toán
  SRS bằng test trước khi sửa — SM-2 dễ sai); mysql (nếu schema đổi cho cá nhân hoá); performance-optimization
  (nếu engine nặng); documentation-and-adrs (ghi ADR-007+).
- Thực thi tuần tự, verify mỗi task, review mỗi slice. SRS: viết test SM-2 boundary TRƯỚC khi sửa
  review_flashcard (TDD) để không phá dữ liệu học của user thật.
- ĐIỂM CHỐT: bám quyết định từ tầng A; bất kỳ kiến trúc mới ngoài đó → DỪNG hỏi user.
- Gap-check (code-review-and-quality) + docs (documentation-and-adrs). Session Close. Next = Phase 3.

LƯU Ý DỮ LIỆU THẬT: Phase 2 chạy khi đã có user → mọi migration/đổi SRS phải additive + có rollback;
KHÔNG xoá/đổi dữ liệu học của user. Test trên staging (nếu task staging đã xong) trước khi lên prod.
```

---

# ═══════════════════════════════════════════════════════════
# PHASE 3 — Scale (khi có traffic/nhu cầu kinh doanh thật)
# ═══════════════════════════════════════════════════════════

> Chỉ bắt đầu khi có traffic thật chạm giới hạn HOẶC có nhu cầu doanh thu. Tối ưu scale sớm = lãng phí
> (roadmap §6). Phase 3 phụ thuộc số liệu tải thật → breakdown dựa trên bottleneck đo được, không đoán.

## Phase 3 — Tầng A: PROMPT BREAKDOWN

```
Bạn định hướng + breakdown Phase 3 (Scale) vào TASKS.md. Phiên ĐỊNH HƯỚNG — KHÔNG code (trừ TASKS.md).

PHA 1 — NẠP NGỮ CẢNH + ĐO: CLAUDE.md; PRODUCTION_ROADMAP §4 Phase 3 (billing, scale, sửa
refresh_progress_state, connection pool, index, read replica); ADR-003 (deploy). codegraph + đo thật:
- refresh_progress_state chạy mỗi GET (main.py get_skills/get_badges...) → xác nhận đây có phải bottleneck
  thật bằng SỐ LIỆU (không đoán): profile request, đo thời gian, đếm query/request.
- Connection pool hiện tại (database.py engine config), index hiện có (xem migrations), N+1 query.
- Billing: chưa có gì → là tính năng mới hoàn toàn.

PHA 2 — GRILL (skill grill-me):
- Billing: mô hình (gói nào? giá?), nhà cung cấp (Stripe?), xử lý hoàn tiền/hết hạn/downgrade. Đây là
  lớp lớn — chỉ làm khi CÓ người trả tiền chắc chắn (đã chốt Phase 3).
- Scale target: bao nhiêu user đồng thời thật cần chịu? (định ngưỡng đo được cho DoD thoát).
- refresh_progress_state: cache (Redis? in-memory?) hay tính event-driven? trade-off đúng đắn vs phức tạp.
- DB scale: read replica có thật cần ở quy mô này không, hay chỉ index + pool là đủ?

PHA 3 — BREAKDOWN vào TASKS.md (skill planning-and-task-breakdown + performance-optimization + mysql):
block "Phase 3 — Scale", mỗi task có baseline SỐ LIỆU đo được (before) + target (after) trong Acceptance
— scale task PHẢI có metric, không "làm cho nhanh hơn" chung chung. Ghi ADR cho quyết định lớn (billing,
caching strategy, replica) — ADR-008+.

KẾT THÚC: xuất task + xin user duyệt. KHÔNG code.
```

## Phase 3 — Tầng B: PROMPT THỰC THI (sau tầng A)

```
Thực thi Phase 3 theo task vừa breakdown (block "Phase 3 — Scale" trong TASKS.md), single-agent,
tuần tự, local. Quy trình:

- Nạp ngữ cảnh + đo baseline TRƯỚC khi tối ưu (số liệu before phải có).
- Skill theo việc: performance-optimization (refresh_progress_state, query), mysql (index, pool, replica),
  backend-development (billing/Stripe), test-driven-development (lock hành vi trước khi tối ưu),
  documentation-and-adrs (ADR-008+).
- Mỗi task tối ưu: đo before → sửa → đo after → so với target trong Acceptance. KHÔNG merge nếu không đạt
  metric hoặc nếu làm hỏng hành vi (test phải xanh).
- Billing: làm trên staging trước; test webhook Stripe; KHÔNG để lỗi billing ảnh hưởng dữ liệu học.
- ĐIỂM CHỐT: bám tầng A; kiến trúc mới ngoài đó → DỪNG hỏi user.
- Gap-check + docs + Session Close.

LƯU Ý: Phase 3 động vào hiệu năng + tiền của user thật → mọi thay đổi phải reversible, test kỹ trên staging,
có rollback plan. Đây là phase rủi ro vận hành cao nhất.
```

---

## Ràng buộc + quy ước áp dụng cho TẤT CẢ phase

- **Quy trình bất biến mỗi phase:** Tầng A (grill + breakdown vào TASKS.md) → user duyệt → Tầng B (thực thi
  tuần tự, verify mỗi task, review mỗi slice) → gap-check → docs → Session Close → user duyệt cột mốc.
- **Không bịa task:** không phase nào được thực thi khi chưa có task breakdown trong TASKS.md. Chưa có → chạy tầng A.
- **Skill (theo CLAUDE.md routing, KHÔNG codex-*):** grill-me, planning-and-task-breakdown, backend-development,
  fastapi-templates, frontend-ui-engineering, test-driven-development, performance-optimization, mysql,
  code-review-and-quality, documentation-and-adrs, web-design-guidelines, vercel-react-best-practices.
- **Bất biến kỹ thuật:** app luôn chạy Docker Compose; docs tiếng Anh; additive/low-risk; giữ API shape ổn định;
  KHÔNG xoá feature; codegraph trước Read/Grep; chạy local (codegraph + Docker).
- **Gap-check gate (CLAUDE.md):** task phải `Gap check: [x]` mới được archive sang tasks-done.md.
- **Quyết định kiến trúc mới (ngoài cái đã chốt) → DỪNG hỏi user.** Worker không tự quyết.
- **Dữ liệu user thật (Phase 2/3):** mọi thay đổi additive + reversible + test trên staging trước prod.

## Bản đồ tổng

| Phase lớn | Sub | Tầng A (breakdown) | Tầng B (thực thi) | Trạng thái |
|---|---|---|---|---|
| Phase 1 | P1a | (đã có trong TASKS.md) | [`P1a-EXECUTION-PROMPTS.md`](P1a-EXECUTION-PROMPTS.md) | ✅ sẵn sàng thực thi |
| Phase 1 | P1b | prompt trong file này | prompt trong file này | ⏳ breakdown trước |
| Phase 2 | — | prompt trong file này | prompt trong file này | ⏳ chờ user thật |
| Phase 3 | — | prompt trong file này | prompt trong file này | ⏳ chờ traffic/doanh thu |

**Thứ tự:** P1a → (duyệt) → P1b breakdown → (duyệt) → P1b thực thi → (duyệt cột mốc Phase 1) →
Phase 2 breakdown → … → Phase 3.
