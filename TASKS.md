# IELTS Quest Dashboard Tasks

Last updated: `2026-06-10` (session 8n+6 — **Status / Topbar / Roadmap / Lexical UI Refinement COMPLETE** — Tasks 1-11. Gap check: [x]. Status hero avatar+name on one row + square avatar (desktop+mobile, JSX); metrics/condition 3-col on mobile; topbar bell-right + clock-under-avatar; roadmap h2+strong same row; VL flashcard topic lobby + difficulty-selectors buttons (backend `topic_id`/`topic_title` added, no migration); level-block 1-col, coll-section-nav full height, flashcard ENTER fits viewport. Build ✓ 248 modules. Mobile verified 375px + desktop verified 1536px (DevTools): desktop status hero avatar-square+name 1-row + metrics/condition 3-col, dashboard topbar/roadmap original layout intact, no mobile-rule leak. Previously session 8n+5 — **Mobile Responsive Redesign IMPLEMENTED** — MR-1..MR-13 CSS done, verified 375px DevTools: dashboard 1-col ✅, vocab tab-strip ✅, overlay full-screen ✅, no overflow ✅. Fix: khối `<600px` phải đặt SAU toàn bộ Vocabulary CSS ở cuối file. Previously session 8n+4 — **planned: Mobile Responsive Redesign** (14 tasks MR-1..MR-14, CSS-only `<600px`, desktop unchanged). UX locked via grill (A1–A8). See plan block `Mobile Responsive Redesign` below + plan file `~/.claude/plans/ph-n-3-majestic-snowglobe.md`. Previously: session 8n+3 — **planned: Vocab Library 5-layer + Collocation Level/Section upgrade** (7 tasks B1–B3, A1–A4). Open Decision #6/#7 locked. See plan block below. Previously: session 8l-C — **C-1 + C-2 COMPLETE + gap-checked**. Parser rewritten: `_Section:_` → CollocationSection (10), `## N.` → CollocationTopic (60, topic_number=N). Global dedup. Volume mount added. Suite: **68/0/1 BE**. Parser smoke: 10 sections / 60 topics / 1409 unique items.)

## Session Resume

- All Phases 4–15 of the "Big Update: Account, Onboarding & Rank Boss System" are complete and archived in `tasks-done.md`.
- Session 5: Backlog quest feature removed (Slices 1–7, 9); silent refresh on 401 wired; refresh token migrated to httpOnly cookie; `GET /api/rank-exams/status/{skill_id}` added.
- Session 7: Deterministic seed (no `Player.first()`), neutral register fallback, `activate-campaign` optional body, `/me` exposes `player.name` + `campaign` key, uvicorn `--reload` active.
- Backend: JWT auth wired end-to-end; 43/43 tests pass.
- Frontend: Auth Shell (Login/Register), Onboarding (3-step), Suggestion Inbox (Apply/Dismiss), Rank Boss UI (Notif + Exam + Result) all live.
- Vite build: ✓ 222 modules, 0 errors.

## Current State

- Full stack live: Docker Compose (`frontend :5173`, `backend :8000`, `mysql :3307`). Uvicorn chạy với `--reload` — edit `backend/` tự reload không cần restart.
- Auth: JWT register/login/logout/refresh; access token in localStorage; refresh token in httpOnly cookie `ielts_rt`; silent refresh on 401 → logout only if refresh fails.
- Seed: deterministic — demo player luôn thuộc `ad00000@gmail.com`, không dùng `Player.first()`. Register fallback dùng email prefix thay `"IELTS Hunter"`.
- Onboarding: 5-step UI (Name → Campaign → StartDate → Certificate → Confirm) → `POST /api/onboarding/activate-campaign` nhận optional `{ display_name, campaign_template_code, start_date }` → dashboard.
- Register: chỉ email + password (không còn form tên hiển thị).
- `/api/auth/me`: trả `player.name`, `player.display_name`, `campaign` (không còn `active_campaign`).
- StatusModal: nút "Đăng xuất" → `/login`.
- Rank Boss: eligible/boss_required/in_progress banners; exam screen với timer + MCQ; result screen CLEARED/FAILED; `GET /api/rank-exams/status/{skill_id}` exposes remaining daily attempts.
- Suggestion Inbox: Apply/Dismiss wired to backend, skill matrix refreshes after apply.
- Backlog quest feature: fully removed. Past-date quests expire immediately (no overdue state, no 50% XP).
- Canonical context: `docs/current/`; history/logs: `docs/history/`.

## Completed Tasks

All completed tasks have been archived and moved to [tasks-done.md](tasks-done.md).

## In Progress

- **All Tasks 5–18 implemented + gap-checked (session 8h–8i). Checkpoint G ✓.** Suite: **60/1/0 BE** + **5/5 FE** + **build ✓**.
- **Session 8l: all 12 "Target / Suggest / Collocations Overhaul" tasks complete + gap-checked.** Suite: **67/0/1 BE** + **build ✓**.

## Planned (not yet implemented)

- **🟢 Small-Group Tool — feature work continues.** P0 hygiene + bug-fix sweep + mobile sweep are DONE (2026-06-13, see blocks below). Remaining feature work per [`docs/current/SMALL_GROUP_PLAN.md`](docs/current/SMALL_GROUP_PLAN.md) is data-driven deep testing / new features when prioritized.

## Archived elsewhere

- **Completed implementation plans** (Flashcard, Collocation Neon/Seed, XP Redesign, Target/Suggest Overhaul, Vocab Library, Mobile Responsive MR-1..14) → [`tasks-done.md`](tasks-done.md).
- **Superseded / not-executed plans** (Production Readiness Phase 1a SaaS, PR-1..PR-14) → [`tasks-NOT-exe.md`](tasks-NOT-exe.md). Do NOT execute.

---

# Implementation Plan: Small-Group Tool — P0 Hygiene (2026-06-13)

**Owner:** khanhpn308 · **Plan doc:** [`docs/current/SMALL_GROUP_PLAN.md`](docs/current/SMALL_GROUP_PLAN.md) · **Plan file:** `~/.claude/plans/m-c-nh-d-ng-codegraph-vast-pascal.md` · **Type:** Backend security/config (no FE).

## Goal

App chạy trên 1 server chung internet-facing cho nhóm 5–20 người. Đóng 3 lỗ hổng rẻ + nguy hiểm salvage từ P1a (đã chốt bỏ SaaS). P0 done = không request nào wipe được DB, JWT secret không đoán được, user không ghi đè tiến độ nhau.

## Tasks

- [x] **Task P0-1 — Gate `/api/dev/*` sau `ENABLE_DEV_ENDPOINTS` (default off).** *(S, backend)*
  - Thêm hằng `ENABLE_DEV_ENDPOINTS` + dependency `require_dev_enabled` (404 khi off) tại `backend/app/main.py`. Áp `dependencies=[Depends(require_dev_enabled)]` cho cả 5 route: `/api/dev/reset`, `/api/dev/run_migrations`, `/api/dev/regenerate-quests`, `/api/dev/test-xp/skills`, `/api/dev/test-xp/award` (2 route test-xp giữ thêm `require_test_account`). `docker-compose.yml`: `ENABLE_DEV_ENDPOINTS` default `true` cho dev.
  - **Verified:** guard OFF→404 / ON→pass; cả 5 route mang guard (introspect `app.routes`).
  - **Gap check:** [x] Done — đồng nhất 1 cơ chế (dependency 404), không route hở; test-xp 2 lớp.

- [x] **Task P0-2 — Bỏ JWT secret fallback yếu (hard-fail).** *(S, backend)*
  - `backend/app/auth_utils.py:8`: đọc `JWT_SECRET_KEY` không fallback; thiếu → `RuntimeError` rõ ràng (trỏ README + `.env.example`). Chữ ký `create_jwt`/`decode_jwt` không đổi. `docker-compose.yml`: `JWT_SECRET_KEY` default dev. `.env.example` + README mục "Deploy / Environment" (hướng dẫn `openssl rand -hex 32`, giải thích hard-fail). `test_backend.py` set env test-only trước import.
  - **Verified:** import không secret → RuntimeError; grep `super-secret-key` → rỗng; 68/68 test OK với env test.
  - **Gap check:** [x] Done — KHÔNG migrate PyJWT (out of scope). localStorage token giữ nguyên.

- [x] **Task P0-3 — Dọn dead path `Player.first()`.** *(S, backend)*
  - Xóa `get_campaign_or_404` (0 caller) + `get_player_or_404` (1 caller). `regenerate_quests` đổi sang `get_current_player`/`get_current_campaign` (account-scoped). Bỏ import `get_active_player` thừa khỏi `main.py`. Giữ `services.py:get_active_player` (fallback defensive, callers luôn truyền player).
  - **Verified:** grep 2 helper → rỗng; 68/68 test OK; không route production/dev nào đi qua `Player.first()`.
  - **Gap check:** [x] Done — route production đã account-scoped từ trước; task này khóa lại + dọn dead code.

### Checkpoint P0 (after P0-1..P0-3)
- [x] 68/68 backend unittest OK. Guard 5/5 route. Hard-fail xác nhận. grep clean.
- [x] Round-trip login + scoping 2-account qua API: register→login→`/auth/me` 200; token A→player#7, token B→player#8 (tách biệt); no-token→401. Backend recreate nhận env compose mới (crash-loop trước đó = hard-fail hoạt động đúng khi container cũ thiếu `JWT_SECRET_KEY`).

---

## MR sweep verification — 2026-06-13 (MR-14 / Gap check: [x])

**Status: MR-1..MR-13 implemented (CSS block `styles.css:5796`) + sweep-verified. MR-3 skipped (no real dedup found — no mobile spacing var added). MR-14 = this sweep.**

Verified on preview (seed account `ad00000@gmail.com`) at 360 / 375 / 430px — **zero horizontal overflow** on every screen (`document.scrollWidth === clientWidth` at all widths):
- Dashboard: topbar, inbox bell, roadmap hero + phase cards, stat cards, support panels — all stack 1-col, no overflow (MR-4/5/6 ✓).
- Overlays full-screen sheet + sticky `×`: Status (hero/metrics/condition/skill-matrix), Quest (Main/Daily/Weekly/Archive tab-row + body), Nav drawer, Rank Exam — all clean (MR-1/7/8 ✓).
- Vocab workspace: 10-tab horizontal scrolling tab-strip works (`nav.scrollWidth > clientWidth`); all 10 tabs (Codex, Tree, Flashcard, Collocations, Library, Shadow Duel, Word Family, Echo Chamber, Error Dungeon, Boss) → no overflow; Collocation 3-layer (level→section→topic) stacks 1-col (MR-2/9/10/11/12/13 ✓).
- Desktop 1280px: layout structurally unchanged (mobile block is `max-width:599.98px`, last-in-source — no leak) (B4 ✓).
- `npm run build` ✓ 225 modules.

**Note:** deep gameplay-tab content (Tree canvas/bottom-sheet, Shadow Duel/Echo arenas) renders only with vocab data; seed account had an empty Codex, so only the layout shell was exercised. Flagged for the data-driven pass if needed.

**Out-of-scope bug found during sweep (→ moved to bug sweep C):** TODAY SYNC support panel renders `<strong>` and the XP `<span>` with no separation ("Need check-in0 XP banked today") on **both desktop and mobile** — a markup/spacing issue, not a mobile-only regression.

## Bug sweep — 6 systems — 2026-06-13 (Gap check: [x])

Walked all 6 systems on preview (seed account; seeded 1 vocab + flashcards via API to exercise SRS). Console clean throughout; all feature APIs 200.

- **[C#1] Rank exam "Resume Exam" 400 → FIXED.** Inbox in_progress boss item called `POST /rank-exams/start`, which only accepted `boss_required` → 400, UI swallowed it. Backend now resumes the live attempt. (Backend `python -m unittest` 68/68 OK.)
- **[C#2] Support-panel headline/detail run together (desktop+mobile) → FIXED.** `.support-panel strong/span` were `display:inline`; set to block.
- **Quest/XP** ✓ complete→claim 200, daily clears incremented.
- **SRS / Flashcard Gate** ✓ flip → grade (`/flashcards/{id}/review` 200) → DUE 2→0 → "Gate Cleared".
- **Collocation** ✓ level→section→topic browse, all `/collocations/*` 200.
- **Vocab Codex** ✓ create form opens; `/vocabulary` CRUD 200.
- **Boss** ✓ `/boss-battles` 200, overlay renders.

No further bugs found. (SM-2 SRS is intentionally simplified per SMALL_GROUP_PLAN — not a bug.)

---

# Implementation Plan: IPA Pronunciation (SpeakButton) — 2026-06-13

**Owner:** khanhpn308 · **Grilled + locked** (7 questions) · **Type:** Frontend only · **Branch:** `feat/ipa-pronunciation`

## Goal

Add a 🔊 pronunciation button next to words/collocations everywhere IPA is shown, using the browser's Web Speech API (no backend, no audio files — also works for user-created words). Locked decisions: (1) Web Speech API; (2) reusable `<SpeakButton>` backed by `utils/speak.js`; (3) speaks the raw word/collocation, NOT the IPA text; (4) 6+ spots; (5) cancel-then-replay, active-icon on speak, hidden when unsupported, cached voices + `voiceschanged`; (6) fixed `en-US`/rate 1 (opts overridable for future settings).

## Tasks

- [x] **IPA-1 — `frontend/src/utils/speak.js`** *(gap-check [x])* — `speak(text, opts)` + `isSpeechSupported()`; caches voices, refreshes on `voiceschanged`; defaults en-US/rate 1/pitch 1; `onStart`/`onEnd` callbacks; cancels prior utterance.
- [x] **IPA-2 — `frontend/src/components/SpeakButton.jsx`** *(gap-check [x])* — 🔊 button; `is-speaking` state (🔈) via onStart/onEnd; returns null when unsupported; `e.stopPropagation()` so it never flips/opens its parent card; aria-label. CSS `.speak-button` in `styles.css`.
- [x] **IPA-3 — Wire into all spots** *(gap-check [x])* — Codex card + flashcards (`VocabularyWorkspace.jsx`: vocab card, collocation flashcard, vocab flashcard, VL flashcard), Vocabulary Library (`VocabularyLibrary.jsx`), Collocation (`CollocationForge.jsx`), Word Network Tree node drawer (`WordNetworkTree.jsx`). Text = `word`/`collocation`/`node.word`. (`VocabularyOverlay.jsx` skipped — dead component, not imported.)

### Checkpoint IPA *(gap-check [x])*
- [x] `npm run build` ✓ 225 modules. Console clean.
- [x] Preview verify: Codex 🔊 → `speak()` called with `{text:"meticulous", lang:"en-US", rate:1}`. Collocation → 26 buttons, speaks full phrase "ancient monument", stopPropagation holds (card not opened). Buttons render 26×26 next to IPA.
- [ ] **Owner to confirm audio + active-icon on a real device** (headless preview can't play audio / fire onstart).

---


## Where To Read More

- Completed Tasks: [tasks-done.md](tasks-done.md)
- Superseded / not-executed plans: [tasks-NOT-exe.md](tasks-NOT-exe.md)
- Migration summary: [docs/history/MIGRATION_HISTORY.md](docs/history/MIGRATION_HISTORY.md)
- Latest validation: [docs/history/TEST_REPORT.md](docs/history/TEST_REPORT.md)
- Latest implementation log: [docs/history/changelogs.md](docs/history/changelogs.md)
- Generic Codex guide (EN): [docs/current/prompt-generic-en.md](docs/current/prompt-generic-en.md)
- Generic Codex guide (VI): [docs/current/prompt-generic-vi.md](docs/current/prompt-generic-vi.md)
- Codex operator guide (EN): [docs/current/prompt-en.md](docs/current/prompt-en.md)
- Codex operator guide (VI): [docs/current/prompt-vi.md](docs/current/prompt-vi.md)
