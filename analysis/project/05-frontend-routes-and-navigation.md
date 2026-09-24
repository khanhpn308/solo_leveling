# 05 — Frontend routes and current navigation

Answers mission questions **5** (complete inventory of current frontend routes) and **6** (the
navigation that currently exists). Current state only; no proposals. Evidence convention and repo
state are in `README.md`.

---

## 1. Complete frontend route inventory

The router exists in exactly one place: `frontend/src/main.jsx:12-31`, using `react-router-dom`
`BrowserRouter` + `Routes`/`Route`. There are **four route entries total**, and one of them is a
catch-all:

| # | Path | Element | Guard | Renders | Evidence |
| --- | --- | --- | --- | --- | --- |
| R-1 | `/login` | `pages/Login.jsx` | none | Email + password form, Vietnamese copy, link to `/register` | `main.jsx:16`; `Login.jsx:33-66` |
| R-2 | `/register` | `pages/Register.jsx` | none | Email + password form (no name field), link to `/login` | `main.jsx:17`; `Register.jsx:33-66` |
| R-3 | `/onboarding` | `pages/Onboarding.jsx` | none (auth is implicit — the flow 401s without a token) | 5-step campaign wizard | `main.jsx:18`; `Onboarding.jsx:70-126` |
| R-4 | `/*` | `<ProtectedRoute><App /></ProtectedRoute>` | client-side only | The entire application shell | `main.jsx:19-27`; `ProtectedRoute.jsx:5-13` |

Every `navigate()`/`<Link>`/`<Navigate>` target in the codebase points at one of these four:

```
navigate('/')                 Login.jsx:20,22 · Register.jsx:20,22 · Onboarding.jsx:62
navigate('/login')            App.jsx:143,153
<Link to="/register">         Login.jsx:65
<Link to="/login">            Register.jsx:71
<Navigate to="/login">        ProtectedRoute.jsx:9
<Navigate to="/onboarding">   ProtectedRoute.jsx:11
```

Search evidence: `grep -rn "navigate('|navigate(\`|to=\"/" frontend/src --include="*.jsx"` returns
only the eleven sites above. Only four files can navigate at all
(`Login.jsx`, `Register.jsx`, `Onboarding.jsx`, `App.jsx` + `ProtectedRoute.jsx` render `<Navigate>`).

### 1.1 What is *not* a route

This is the single most consequential navigation fact in the app, so it is stated explicitly:

**Inside `R-4`, nothing changes the URL.** The dashboard, all four overlays, the full-screen
vocabulary workspace, the rank-exam screens and every sub-tab are driven by `useState` inside
`App.jsx`. There is no route, no query string and no hash for any of them:

- No `useSearchParams`, no `location.hash`, no `window.location` usage anywhere in `frontend/src`
  (verified: `grep -rn "location.hash|useSearchParams|window.location"` → no matches).
- The full-screen workspace switch is a state value: `const [currentView, setCurrentView] =
  useState('dashboard')` with `'dashboard' | 'vocabulary'` (`App.jsx:129`), swapped by
  `openVocabulary()` (`App.jsx:761-772`) and returned by the workspace's `onClose`
  (`App.jsx:790-793`).
- Overlay visibility is six independent booleans — `isNavOpen`, `isInboxOpen`, `isStatusOpen`,
  `isQuestOpen`, `isCertificateOpen`, `isBossOpen` (`App.jsx:105-110`) — deliberately kept mutually
  exclusive by each `open*()` helper (`App.jsx:712-772`).

Consequences that follow directly from that design, all verifiable from the code above:

1. **Browser Back does not close anything.** It exits to whatever preceded the SPA entry and, because
   `R-4` is a catch-all, re-entering lands on the dashboard regardless of what the user was doing.
2. **Nothing is linkable or shareable**, including the vocabulary workspace and an in-progress rank
   exam.
3. **A page reload resets all of it** to `dashboard` / all overlays closed — even mid-exam, since
   `RankExamScreen` keeps `answers` and `currentIdx` in component state
   (`RankExamScreen.jsx:34-35`).
4. **The exam timer is client-side only**: `useCountdown(expires_at)` ticks locally
   (`RankExamScreen.jsx:5-15`), though the server does persist `expires_at` and rejects late
   submissions (`main.py:1806-1813`).

---

## 2. Navigation that exists today

Navigation is a single level of overlays and mode switches. There is no persistent nav bar, no
breadcrumb, no tab bar in the DOM, and no footer nav.

### 2.1 Entry points to navigation

| Control | Location | Opens |
| --- | --- | --- |
| Menu button (hamburger + notification dot when claims are pending) | `HomeTopBar.jsx:20-25` | `NavigationDrawer` (`App.jsx:923-931`) |
| Avatar button (first letter of display name) | `HomeTopBar.jsx:33-35` | `StatusModal` (`App.jsx:933-952`) |
| Suggestion inbox toggle inside the top bar | `HomeTopBar.jsx:37-48` → `SuggestionInboxDropdown` | the inbox dropdown |
| "Vocabulary Today" support card | `App.jsx:886-899` | the vocabulary workspace |
| "Weekly Mission" support card | `App.jsx:901-916` | Quest overlay, `weekly` tab |

The menu button is the primary entry: `HomeTopBar.jsx:20-25` pairs it with
`hasPendingClaims={pendingClaimCount > 0}` (`App.jsx:849`), computed from
`pendingDailyClaims + pendingMainClaims + pendingWeeklyClaims` (`App.jsx:806-809`) — so the dot is a
claim reminder, not a general notification badge.

### 2.2 The `NavigationDrawer` (the only nav menu)

`frontend/src/components/NavigationDrawer.jsx` is a modal drawer (`role="dialog" aria-modal="true"`,
focus trap, close on outside click — `usePresenceLayer` options `:11-16`). It contains a header and
one flat action list with one sub-group (`:37-74`):

| Label shown | Sub-label shown | Group | Action |
| --- | --- | --- | --- |
| — | — | *Quest* | four sub-buttons: **Main**, **Daily**, **Weekly**, **Archive** (`:41-58`) |
| Lexical Awakening | "Codex Archive & Flashcard Gate" | — | `onOpenVocabulary` → switches `currentView` to `vocabulary` (`:63-66`) |
| Certificate | "IELTS / Aptis / TOEIC / TOEFL" | — | `onOpenCertificates` (`:67-70`) |
| Boss | "Current target + timeline" | — | `onOpenBoss` (`:71-74`) |

**Six destinations total.** There is no entry for check-ins, badges, the skill matrix, the exam
screens, trackers, or the individual vocabulary modules — those are reached from elsewhere or not at
all.

### 2.3 Second-level navigation inside overlays

| Container | Tabs / sub-navigation | Default | Evidence |
| --- | --- | --- | --- |
| Quest overlay | 4 tabs: Main, Daily, Weekly, Archive | `main` | `QuestOverlay.jsx:7-12` (tab list), `App.jsx:111` (default state) |
| Status modal | 4 collapsible `AuxSection` panels: Check-in editor, "Mục tiêu IELTS", Badge Wall, Recent Check-ins | all collapsed | `StatusModal.jsx:105-115` (the panel primitive), `:136-141` (state), `:205-338` (usages) |
| Vocabulary workspace | **10** sidebar nav buttons | `codex` | `VocabularyWorkspace.jsx:212` (default), `:531-604` (the 10 buttons) |
| Flashcard Gate tab | 3 sub-tabs: Vocabulary, Collocation, Vocab Library | `vocabulary` | `VocabularyWorkspace.jsx:227` (state), `:829-849` (buttons), `:851-1049` (branches) |
| Collocation tab | 3-layer drill-down: level → section → topic → items, plus a flashcard-add toggle | first level | `CollocationForge.jsx:110-202` |

The 10 vocabulary nav buttons, in DOM order, are: Codex Archive, Word Network Tree, Flashcard Gate,
Collocations, Vocabulary Library, Shadow Duel, Word Family, Echo Chamber, Error Dungeon, Boss Battles
(`VocabularyWorkspace.jsx:531-604`). Two of them carry a live count badge: Flashcard Gate
(`dueFlashcards.length`, `:553`) and Error Dungeon (`activeErrors.length`, `:596`).

### 2.4 The navigation graph, as a whole

```
/login ──register──> /register
   │                     │
   └──── on success ─────┘
              │
      onboarding_completed?
        false ──> /onboarding  (5 wizard steps, no URL change)
        true  ──> /*
                    │
                App shell (dashboard view)          ── no URL ever changes below this line ──
                    ├── HomeTopBar
                    │     ├── menu  ──> NavigationDrawer
                    │     │              ├── Quest Main/Daily/Weekly/Archive ──> QuestOverlay
                    │     │              ├── Lexical Awakening ──> currentView='vocabulary'
                    │     │              ├── Certificate ──> CertificateOverlay
                    │     │              └── Boss ──> BossOverlay
                    │     ├── avatar ──> StatusModal  (targets · check-in · skills · badges · history · logout)
                    │     └── inbox ──> SuggestionInboxDropdown  (apply / dismiss)
                    ├── RoadmapHero (read-only)   + 4 support cards (2 of them navigate)
                    ├── RankBossNotif ──> RankExamScreen ──> RankExamResultScreen
                    └── currentView='vocabulary' ──> VocabularyWorkspace (10 tabs, flashcard 3 sub-tabs)

Logout is reachable from exactly two places: StatusModal.jsx:347-349 and the 401 handler in App.jsx:151-153.
```

---

## 3. Reachability audit — what each surface takes to reach

`[DERIVED]` from the code paths above. "Depth" counts user actions from a freshly loaded dashboard.

| Surface | Depth | Path | Notes |
| --- | --- | --- | --- |
| Dashboard / roadmap hero / stat cards | 0 | — | default view |
| Status (level, rank, XP bar, skills, badges, targets, history, check-in, logout) | 1 | avatar | Badge wall, targets, check-in editor and history each sit one collapse deeper (`StatusModal.jsx:294`, `:303`, `:208`, `:324`) |
| Suggestion inbox | 1 | top-bar inbox toggle | only place rank/weakness suggestions can be actioned |
| Quest board | 2 | menu → Quest sub-tab | 4 tabs inside |
| Boss battles | 2 | menu → Boss | hero + timeline |
| Certificate records | 2 | menu → Certificate | list + create form (one more click) |
| Vocabulary workspace | 1–2 | "Vocabulary Today" card, **or** menu → Lexical Awakening | two entry points |
| Rank exam (unlock/start/resume) | 0 | — | `RankBossNotif` renders inline on the dashboard whenever any skill has `promotion_status ∈ {eligible, boss_required, in_progress}` (`RankBossNotif.jsx:6-10`) |
| Weekly mission | 1–2 | support card → weekly tab, or menu → Weekly | also summarised in the support card itself |
| Check-in | 1 + 1 | avatar → "Check-in" toggle | |
| Collocation practice / review | 2 + 2 | workspace → Collocations, then level → section → topic | review lives inside the Flashcard Gate sub-tabs |
| Vocab flashcard review | 2 | workspace → Flashcard Gate | |

No surface is more than three actions deep, which is a direct consequence of the drawer-plus-overlay
design.

---

## 4. UI that exists in the codebase but is **unreachable from any navigation**

Reachability was determined by grepping every component name across `frontend/src` for references
outside its own file, then checking the five `React.lazy` call sites in `App.jsx:27-31`.

### 4.1 Dead components — imported by nothing, reachable by nothing

| Component | Size | What it would have shown | Evidence |
| --- | --- | --- | --- |
| `VocabularyOverlay.jsx` | 870 lines | A full vocabulary overlay duplicating the workspace: word CRUD, tree, flashcards, collocations, and 8 embedded gameplay modules | zero references to the identifier `VocabularyOverlay` anywhere outside the file; superseded by `VocabularyWorkspace.jsx` |
| `TrackersPanel.jsx` | 23 lines | The four tracker modules from `TRACKER_MODULES` (Error Log "Ready"; Writing / Speaking / Mock Test "Preparing") | zero references; `dashboard-data.js:24-49` |
| `SetupSummaryPanel.jsx` | 124 lines | Campaign setup summary + a `TEST_EVIDENCE` table + target editing | zero references; also contains Vietnamese copy |
| `CheckInPanel.jsx` | 71 lines | A standalone mood/energy/focus panel | zero references; superseded by the check-in editor inside `StatusModal` |
| `CampaignPanel.jsx` | 45 lines | Campaign & streak panel | zero references |
| `BadgeWallPanel.jsx` | 19 lines | Badge wall panel | zero references; badges are rendered inline in `StatusModal.jsx:303-322` |
| `WeeklyMissionPanel.jsx` | 37 lines | Weekly mission panel | zero references; superseded by `WeeklyMissionCard.jsx` (live) |
| `SuggestionInboxPanel.jsx` | 44 lines | Suggestion inbox panel | zero references; superseded by `SuggestionInboxDropdown.jsx` (live) |
| `CommandHeader.jsx` | 52 lines | Header with level block and date | zero references |

That is **9 of 40 components (22%)** — 1285 JSX lines — that no code path can render (**MF-19**). `PanelFrame.jsx`
is *not* in this list: it is used by three live components (`MainQuestMapPanel`, `DailyQuestPanel`,
`BossTimelinePanel`).

### 4.2 Dead API wrappers

Exported from `frontend/src/api/` and referenced by no component:

| Wrapper | Calls | Note |
| --- | --- | --- |
| `postManualCertificate` (`api/auth.js:29-34`) | `POST /certificates/manual` | The live certificate UI writes through `POST /test-records` instead (`App.jsx:695-705`), so `/api/certificates/manual` and `GET /api/certificates` are both unreferenced |
| `refreshTokens` (`api/auth.js:64-66`) | `POST /auth/refresh` | refresh is performed internally by `client.js:17-31`, not through this wrapper |
| `getOnboardingStatus` (`api/auth.js:25-27`) | `GET /onboarding/status` | `Onboarding.jsx` reads `me.account.onboarding_completed` from the context instead (`AuthProvider.jsx:23-25, 41-42`) |
| `getRankExamStatus` (`api/rankExam.js:12-14`) | `GET /rank-exams/status/{skill_id}` | the "review remaining daily attempts" endpoint is never called; the UI shows no attempt counter |
| `getRankExamAttempt` (`api/rankExam.js:16-18`) | `GET /rank-exams/{attempt_id}` | the resume path is never used — see §4.3 |

The five entries above were found by grepping each exported wrapper name across `frontend/src` and
excluding its own module (`postManualCertificate`, `refreshTokens`, `getOnboardingStatus`,
`getRankExamStatus`, `getRankExamAttempt` → 0 references each).

### 4.3 A half-wired flow: resuming an exam

`RankBossNotif.jsx` renders a third banner for skills with `promotion_status === 'in_progress'`
labelled **"Exam in progress — resume before time runs out"** with a **"Resume Exam"** button
(`RankBossNotif.jsx:72-87`). That button calls `handleStart` → `onStartExam` → `startRankExam(skill.id)`
(`RankBossNotif.jsx:22-30`; `App.jsx:665-676`), i.e. it starts a **new** attempt rather than resuming.
`getRankExamAttempt` exists for exactly that purpose and is never called. `[DERIVED]` Whether the
server tolerates the extra start is bounded by the 2-per-day cap it enforces
(`main.py:1641-1648`), so a user who reloads mid-exam and presses "Resume Exam" consumes one of their
two daily attempts and loses the original answers.

### 4.4 A capability with a backend and no UI at all

`TRACKER_MODULES` (`dashboard-data.js:24-49`) declares four tracker surfaces with their own status
labels — Error Log `Ready`, Writing/Speaking/Mock Test `Preparing`. The backend implements all four
(`main.py:1383-1400` error logs, `:1402-1420` writing, `:1421-1439` speaking, `:1440-1461` mock
tests), and the only component that renders them is the dead `TrackersPanel`. `[DERIVED]` So the
in-app status labels themselves are unrenderable: nothing in the shipped UI can tell a user whether
Error Log is "Ready" or "Preparing". This is carried into `06-domain-capability-inventory.md` §3 D-09.

---

## 5. Accessibility / interaction facts relevant to navigation

Recorded because they are the mechanism by which navigation works, not as a review:

- Every overlay uses the same hook, which supplies Escape-to-close, a Tab focus trap, outside-click
  close and focus restoration to the previously focused element
  (`usePresenceLayer.jsx:16-17` for the opt-in flags, `:60-68` for focus restore, `:78-99` for
  Escape and Tab trapping).
- Overlays are `role="dialog" aria-modal="true"` with `aria-labelledby` and optional
  `aria-describedby` (`OverlayFrame.jsx:22-30`); the drawer is the same (`NavigationDrawer.jsx:21`).
- Icon-only buttons carry `aria-label`s (`HomeTopBar.jsx:22`, `:33`; `OverlayFrame.jsx:44`).
- The suggestion inbox is a dropdown with `onToggle`/`onClose` but rendered inside the top bar
  rather than a portal (`HomeTopBar.jsx:37-48`), so its stacking is handled by CSS, not by the DOM.
- Only one `@media (prefers-reduced-motion: reduce)` concern exists per motion block
  (`styles.css:586, 931, 2561`) and four width breakpoints are in use:
  `1220px`, `980px`, `640px`, `599.98px` (`styles.css:2585, 2609, 2677, 5652`).
