# Implementation Plan: Mobile Responsive Redesign (Dashboard + Vocabulary Workspace)

## Overview

Add mobile responsiveness to the entire IELTS Quest Dashboard and Vocabulary Workspace. The current Solo-Leveling UI (neon/glow, fixed-width panel grid, 300px sidebar) breaks badly below ~600px. Strategy is **adapt the existing layout**: desktop (`>= 600px`) stays byte-identical; all mobile rules live in a single compact breakpoint block in `frontend/src/styles.css`. No mobile-first rebuild, no new libraries, **no JSX/logic changes** — all chosen patterns are achievable with CSS only.

## Architecture Decisions

| # | Decision | Rationale |
|---|---|---|
| A1 | **One compact breakpoint: `@media (max-width: 599.98px)`** | Content-based, not device-based. Every fixed-width row collapses below ~600px (vocab sidebar 300px, coll nav 256px, topbar 3-col, support grid, tree sidebar 280px). Aligns with Material/Android "compact" (`<600dp`, ~99.96% of phones in portrait). `.98` prevents overlap with any future `min-width: 600px` rule. Single tier — no intermediate tablet layer. |
| A2 | Breakpoint block lives **after the existing `@media (max-width: 640px)` block** in `styles.css` (currently ends ~line 2715), in source order so it can override base + the 980/640 tiers. Opens with a banner comment: `/* ===== MOBILE COMPACT (<600px) — content-based, all mobile rules below ===== */`. | Cascade order: later rules win at equal specificity; placing it last lets `<600` win over the `640`/`980` rules without `!important`. |
| A3 | **Dashboard stack: keep DOM order** (topbar → RoadmapHero → support cards). No CSS `order`, no JSX reorder. | Hero is identity/progress, natural to see first; support cards are one swipe away; reorder adds risk for no clear gain. (Grilled + confirmed.) |
| A4 | **Vocab sidebar (11 nav tabs) → horizontal scrolling tab-strip.** `.vocab-workspace` flips to `flex-direction:column`; `.vocab-sidebar` becomes a full-width, auto-height, top-sticky strip; `.vocab-sidebar__nav` becomes `flex-direction:row; overflow-x:auto; flex-wrap:nowrap`, nav buttons `flex-shrink:0`. | CSS-only, no JSX. Level-1 navigation only — independent of inner-tab layers. (Grilled + confirmed.) |
| A5 | **App overlays (Status/Quest/Boss/Certificate) → full-screen sheet + sticky header.** `.overlay-frame { inset:0; width:100%; max-width:100%; max-height:100vh; transform:none; border-radius:0; }`; `.overlay-frame__header { position:sticky; top:0; }` so the `×` close stays in reach. | Narrow screens want full bleed; sticky header avoids "trapping" the user when content is long. (Grilled + confirmed.) |
| A6 | **Inner multi-layer tabs → collapse nested column grids to 1 column**, handled per-tab in that tab's task. Independent of the tab-strip. | Collocation (3-layer), Codex form grid, Shadow Duel / Word Family / Echo Chamber grids each collapse `2fr/3fr/repeat(n)` → `1fr`. |
| A7 | **Word Network Tree (react-flow) → CSS adapt, keep canvas.** Sidebar collapses above a full-width canvas (fixed ~60vh); rely on react-flow touch pan/zoom + MiniMap + `fitView`; node-drawer becomes a **bottom-sheet** (overlays canvas, keeps pan position). | react-flow supports touch; CSS-only keeps the feature on mobile. Bottom-sheet keeps the canvas visible vs. inline block which would jump the canvas. (Grilled + confirmed; option A chosen.) |
| A8 | Keep Solo-Leveling theme (neon/glow) on mobile; only adjust layout / spacing / sizing. No new framework, no React Router / Tailwind. CSS only, in `frontend/src/styles.css`. | Repo constraint (CLAUDE.md). |

## Affected screens / components (from codegraph)

**Dashboard** (`App.jsx` render tree; partial coverage exists at 980/640):
- `HomeTopBar` — `.home-topbar` (grid `auto/1fr/auto`), `.topbar-cluster` (level/clock `min-width`), `.inbox-dropdown` (negative `right` offset).
- `RoadmapHero` — `.roadmap-track`, stat cards (Streak/Shield/Main Quest).
- `.home-shell__support` — 4 panels (Today Sync, Vocabulary, Weekly Mission, Boss).
- Quest/roadmap nested panels via overlays: `MainQuestMapPanel`, `DailyQuestPanel`, `WeeklyMissionCard`, `PanelArchive`, `current-main-quest`.

**App overlays** (`OverlayFrame` + `NavigationDrawer`):
- `StatusModal`, `QuestOverlay` (tab-row main/daily/weekly/archive), `BossOverlay` (`boss-hero`, `BossTimelinePanel`), `CertificateOverlay` (`certificate-form`, `certificate-card`).
- `.nav-drawer`, `.toast-rack`.

**Vocabulary Workspace** (`VocabularyWorkspace.jsx` — NO mobile rules today):
- Shell: `.vocab-workspace` (flex-row), `.vocab-sidebar` (300px), `.vocab-sidebar__stats` (3-col), `.vocab-sidebar__nav` (11 buttons), `.vocab-content` (pad 32/40).
- Tabs: Codex (`.codex-controls`, `.vocab-form .form-grid`), Collocations (`CollocationForge`), Flashcard Gate (`.flip-card`, `.arena-*`, 3 sub-modes), Vocabulary Library, Shadow Duel (`.shadow-duel`), Word Family (`.word-family-evolution`), Echo Chamber (`.echo-chamber`), Error Dungeon (`.dungeon`), Boss Battles.

**Word Network Tree** (`WordNetworkTree.jsx`):
- `.vocab-tree-layout` (row) = `.vocab-tree-sidebar` (280px: topics + codex linker + sync) | `.vocab-tree-canvas` (ReactFlow + Controls + MiniMap) | `.vocab-tree-drawer` (320px node detail).

**Collocation** (`CollocationForge.jsx`):
- `.coll-browser__body` (flex-row), `.coll-section-nav` (256px), `.coll-topic-box-grid` (2-col), `.coll-items-grid` (`auto-fill minmax(260px,1fr)`), `.coll-item-card`.

---

## Task List

> All edits are CSS-only, inside the single `@media (max-width: 599.98px)` block, unless a task says otherwise. Every task's verification includes: desktop unchanged at `>= 600px`, and DevTools-MCP screenshots at **360 / 375 / 390 / 412 / 430px** with no horizontal overflow / clipping / unreadable text.

### Phase 1: Foundation (shared patterns)

#### Task 1: Create the compact breakpoint block + overlay full-screen-sheet pattern
**Description:** Establish the single `@media (max-width: 599.98px)` section (per A2, with banner comment) and implement the app-overlay full-screen-sheet + sticky-header pattern (A5) inside it. This is the shared scaffold every later task writes into.
**Acceptance criteria:**
- [ ] New `@media (max-width: 599.98px)` block exists after the `640px` block with the banner comment; no rules below 600px live anywhere else.
- [ ] `.overlay-frame` (+ `.overlay-frame--phase`, `.nav-drawer`) render as full-bleed sheets (`inset:0; width:100%; max-height:100vh; transform:none; border-radius:0`); `.overlay-frame__header` is `position:sticky; top:0` with a solid background so the `×` is always reachable.
- [ ] `.toast-rack` inset nudged to fit (already `min(360px, 100vw-28px)`).
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): open each overlay (Status/Quest/Boss/Cert) at 360 & 430px — sheet fills screen, header+× stay pinned while body scrolls; at 1280px overlays look identical to current.
**Dependencies:** None.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** S (1 file).

#### Task 2: Vocab workspace shell → tab-strip pattern
**Description:** Convert the vocab shell from a 300px sidebar + content row into a stacked layout with a top horizontal scrolling tab-strip (A4), so every vocab tab inherits a usable frame on mobile.
**Acceptance criteria:**
- [ ] `.vocab-workspace` is `flex-direction:column` at <600; `.vocab-sidebar` is full-width, auto-height, sticky top, with a sensible max-height.
- [ ] `.vocab-sidebar__nav` is `row` + `overflow-x:auto` + `flex-wrap:nowrap`; nav buttons `flex-shrink:0`; all 11 reachable by horizontal scroll; active state visible.
- [ ] `.vocab-sidebar__stats` (3-col) and `.vocab-sidebar__title-block` fit without overflow (shrink/hide title block if it eats vertical space); `.vocab-content` padding reduced (~14–16px).
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): at 360px, tab-strip scrolls horizontally through all 11 tabs, content below uses full width; at 1280px the sidebar is the original 300px column.
**Dependencies:** Task 1 (uses the same block).
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** S (1 file).

### Checkpoint: Foundation
- [ ] `npm run build` clean.
- [ ] Overlays = full-screen sheets with sticky header on mobile; vocab shell = stacked + tab-strip.
- [ ] Desktop (>=600px) visually unchanged for both.
- [ ] Review with human before proceeding.

### Phase 2: Dashboard home

#### Task 3: Topbar + inbox dropdown
**Description:** Verify/repair the top bar and notification inbox on narrow screens (most already covered at 980, residual gaps at 360).
**Acceptance criteria:**
- [ ] `.home-topbar` stacks cleanly (1-col) with no overflow at 360px; `.topbar-cluster` level/clock `min-width` don't force horizontal scroll.
- [ ] `.inbox-dropdown` is clamped to viewport (`right:0; left:auto; width:min(<existing>, calc(100vw-24px))`) — never bleeds off-screen at 360px.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): topbar + open inbox at 360/430px fit within viewport; 1280px unchanged.
**Dependencies:** Task 1.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** S.

#### Task 4: Roadmap hero + stat cards + support panels
**Description:** Ensure the hero, the 3 stat cards, and the 4 support panels stack to 1 column and wrap long text without overflow.
**Acceptance criteria:**
- [ ] `.roadmap-track`, stat-card grid, and `.home-shell__support` are single-column at <600; long titles wrap (no clipped text).
- [ ] No element exceeds viewport width at 360px.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): hero+support at 360/390/430px — all readable, stacked, no overflow; 1280px unchanged.
**Dependencies:** Task 1.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** S.

#### Task 5: Quest/roadmap nested panels (overlay bodies)
**Description:** Collapse the nested grids inside quest/roadmap panels (`current-main-quest`, `main-quest-session__grid`, `main-quest-map__summary`, `quest-summary`, `backlog-item`) to 1 column at <600. Some only have rules at 980/640 today.
**Acceptance criteria:**
- [ ] All listed grids are 1-col at <600; headers/meta rows stack; reward/action rows wrap.
- [ ] No overflow at 360px inside the Quest overlay.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): Quest overlay (main/daily/weekly/archive tabs) at 360/430px — all panels stacked, claim buttons reachable.
**Dependencies:** Task 1, Task 3, Task 4.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** M.

### Checkpoint: Dashboard
- [ ] `npm run build` clean.
- [ ] Home + topbar + inbox + all overlays usable end-to-end at 360–430px.
- [ ] Desktop unchanged.

### Phase 3: Overlay content detail

#### Task 6: Status / Boss / Certificate overlay bodies
**Description:** Verify and adjust the content grids inside Status (`status-modal--quad`, `status-core__metrics`, `status-badge-grid`), Boss (`boss-hero`, `BossTimelinePanel`), and Certificate (`certificate-form`, `certificate-card__scores`) overlays so they read well inside the full-screen sheet.
**Acceptance criteria:**
- [ ] Status quad/metrics/badge grids → 1-col; Boss hero + timeline stack; certificate form fields → 1-col, score row wraps.
- [ ] No overflow / clipped controls at 360px.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): each overlay at 360/430px fully usable (forms submittable, scores readable); 1280px unchanged.
**Dependencies:** Task 1.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** M.

### Phase 4: Vocabulary Workspace screens

#### Task 7: Codex Archive tab
**Description:** Make the Codex tab usable: controls row stacks, create/edit form grid → 1-col, word cards/list full-width.
**Acceptance criteria:**
- [ ] `.codex-controls` stacks (search full-width + button below); `.vocab-form .form-grid` → 1-col; textareas full-width.
- [ ] Codex list / cards readable at 360px, no overflow.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): Codex tab + open create form at 360/430px — all fields usable; 1280px unchanged.
**Dependencies:** Task 2.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** S.

#### Task 8: Collocations tab (3-layer)
**Description:** Stack the 3-layer Collocation browser: body row → column, section-nav full-width, topic-box grid → 1-col, item cards shrink.
**Acceptance criteria:**
- [ ] `.coll-browser__body` → column; `.coll-section-nav` `width:100%` (its `overflow-y` retained); `.coll-topic-box-grid` → 1-col; `.coll-items-grid` min-track reduced (~150px) so cards don't overflow 360px.
- [ ] Level entry grid (`.level-block-grid`) fits; back buttons reachable.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): level → section → topic → items flow at 360/430px works, no overflow; 1280px unchanged.
**Dependencies:** Task 2.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** M.

#### Task 9: Flashcard Gate (vocab + collocation + library sub-modes)
**Description:** Make the flashcard arena fit narrow screens across all three review sub-modes (`.flip-card`, `.arena-*`, lobby).
**Acceptance criteria:**
- [ ] `.flip-card` / `.flip-card-inner` sized responsively (width 100% / max-width, no fixed overflow); review action buttons (again/hard/good/easy) reachable and tappable at 360px.
- [ ] Lobby + completion states readable; sub-tab switch (vocabulary/collocation) usable.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): run a flashcard review in each sub-mode at 360/430px; 1280px unchanged.
**Dependencies:** Task 2.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** M.

#### Task 10: Word Network Tree (react-flow, CSS-adapt + bottom-sheet)
**Description:** Adapt the Tree tab per A7: collapse the sidebar above a full-width fixed-height canvas, keep react-flow touch pan/zoom + MiniMap + fitView, convert the node-drawer to a bottom-sheet.
**Acceptance criteria:**
- [ ] `.vocab-tree-layout` → column; `.vocab-tree-sidebar` full-width collapsible/scrollable strip above the canvas; `.vocab-tree-canvas` full-width, fixed height (~60vh).
- [ ] `.vocab-tree-drawer` → bottom-sheet (`position:fixed/absolute; left:0; right:0; bottom:0; max-height:~55%`) overlaying the canvas, with reachable close button; canvas pan position preserved when it opens.
- [ ] react-flow Controls/MiniMap don't overlap the bottom-sheet; pinch-zoom + drag work on touch.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP, touch emulation): at 360/430px — canvas pans/zooms, tapping a node opens the bottom-sheet, close works; sidebar topic/codex-linker usable; 1280px unchanged.
**Dependencies:** Task 2.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** M.
**Risk note:** If touch pan/zoom proves unusable on real phones, flag a follow-up (do NOT rebuild as list this round) — see Risks.

#### Task 11: Shadow Duel / Word Family / Echo Chamber / Error Dungeon / Boss Battles tabs
**Description:** Collapse the multi-column grids and oversized fixed-width cards in the remaining gameplay tabs to single-column / fluid width.
**Acceptance criteria:**
- [ ] `.shadow-duel`, `.word-family-evolution`, `.echo-chamber` grids (`1fr 1fr` / `1.5fr 1fr` / `repeat(3–4,1fr)`) → 1-col where they overflow; cards with `min-width:320px` → `min-width:0` / `width:100%`.
- [ ] Error Dungeon + Boss Battles tab content readable; action buttons reachable; no overflow at 360px.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] Manual (DevTools MCP): each of the 5 tabs at 360/430px — no overflow, interactive elements usable; 1280px unchanged.
**Dependencies:** Task 2.
**Files likely touched:** `frontend/src/styles.css`.
**Estimated scope:** M.

### Checkpoint: Vocabulary
- [ ] `npm run build` clean.
- [ ] All 10 vocab tabs usable end-to-end at 360–430px via the tab-strip.
- [ ] Desktop unchanged.

### Phase 5: Full verification & close

#### Task 12: Full-device sweep + docs
**Description:** Run a complete DevTools-MCP screenshot sweep of every screen at all 5 test widths, confirm desktop parity at >=600px, and update docs.
**Acceptance criteria:**
- [ ] Every dashboard + overlay + vocab screen screenshotted at 360/375/390/412/430 with zero overflow/clipping findings (or findings filed as follow-ups).
- [ ] Side-by-side confirmation that >=600px (e.g. 1280px) is unchanged vs. pre-change.
**Verification:**
- [ ] `npm run build` succeeds.
- [ ] `docker compose up --build` runs; app reachable at `http://localhost:5173`.
- [ ] Docs updated: `docs/history/changelogs.md` (newest first), `docs/history/TEST_REPORT.md` (screenshot evidence), tasks moved to `tasks-done.md` with `Gap check: [x]`.
**Dependencies:** Tasks 1–11.
**Files likely touched:** `docs/history/changelogs.md`, `docs/history/TEST_REPORT.md`, `tasks-done.md`, `TASKS.md`.
**Estimated scope:** M.

### Checkpoint: Complete
- [ ] All acceptance criteria met across Tasks 1–12.
- [ ] No horizontal overflow at any test width; desktop pixel-stable.
- [ ] Ready for review.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| react-flow Tree pan/zoom unusable on real touch devices | Med | Keep canvas + MiniMap + fitView (Task 10). If verification fails on a real phone, file a follow-up task; do not rebuild as a list this round. |
| Full-screen overlay sheet causes double-scroll (sheet + inner panel) | Med | Single scroll container: body scrolls, header sticky; avoid nested `overflow:auto` inside the sheet. |
| A `<600` rule accidentally leaks to desktop (specificity/order) | High | All rules inside the one media block placed last in source; verify 1280px parity at every checkpoint. |
| Tab-strip hides that more tabs exist (11 tabs, scroll) | Low | Optional faded edge / partial-next-tab affordance; verify scrollability in DevTools. |
| Bottom-sheet covers react-flow Controls/MiniMap | Low | Position Controls top-left and cap sheet height (~55%) so Controls remain tappable (Task 10). |

## Open Questions

_None — all UX ambiguities resolved via grill-me (decisions A3–A7)._

## Session close (fill at end)
- Changed:
- Validated:
- Still open:
- Next session should read:
