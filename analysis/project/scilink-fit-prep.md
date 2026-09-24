# Phase 3A.2 — Sci-Link reference fit preparation

## 1. Scope and evidence

This phase compares the current IELTS Quest Dashboard with the reverse-engineered Sci-Link visual system. It identifies visual and structural analogues only. It does **not** redesign information architecture, rename or add routes, settle navigation, alter API contracts, import Sci-Link business concepts, or prescribe a final design system.

### Evidence roots

- **Current product:** all twelve Phase 3A.1 documents in this directory, especially `04-product-and-users.md`, `05-frontend-routes-and-navigation.md`, `06-domain-capability-inventory.md`, `10-boundary-map.md`, and `11-risk-and-coupling-register.md`.
- **Sci-Link reference:** `../../../ui-clone-lab/site-inventory.md` and `../../../ui-clone-lab/analysis/pages/{app-shell,lessons,marketing,auth,utility-legal,live-classroom}.md`, supported by `../../../ui-clone-lab/references/` screenshots.
- **Excluded as an architecture source:** any cloned or inferred Sci-Link implementation. Only the reverse-engineering documentation and screenshots inform this comparison.

### Evidence status

- **VERIFIED** — explicitly established in the cited Phase 3A.1 audit or measured Sci-Link reference.
- **INFERRED** — compatibility judgement based on verified facts from both sides; not a claim of functional equivalence.
- **UNKNOWN** — unresolved by the static audit or by the available reference state.

### Fit classifications

- **STRONG VISUAL ANALOGUE** — the current goal and composition can naturally use a Sci-Link family while retaining current product semantics and behavior.
- **PARTIAL VISUAL ANALOGUE** — useful shell, hierarchy, or component patterns exist, but the workflow or state model needs a product-specific variant.
- **NO NATURAL ANALOGUE** — Sci-Link does not provide an honest pattern for the current workflow, or the current capability has no reachable UI to compare.

### Replacement-safety labels

- **SAFE PRESENTATION REPLACEMENT** — visual markup may be replaced if the same props, callbacks, accessibility contract, and state outputs remain intact.
- **PRESENTATION + LOGIC COUPLED** — the current UI owns local rules, navigation state, refresh triggers, or submission data that must be extracted or preserved.
- **HIGH-RISK REPLACEMENT** — replacing the surface wholesale can delete load-bearing client logic or change persisted outcomes.

### Current routing constraint

**VERIFIED:** The current frontend has exactly four route branches: `/login`, `/register`, `/onboarding`, and guarded `/*`. Dashboard, overlays, the vocabulary workspace, games, and rank-exam screens do not change the URL (`05-frontend-routes-and-navigation.md` §1). Any table row written as `/* — state: …` describes an in-app state, **not** a proposed route.

**VERIFIED:** Phase 3A.1 was static. Current runtime visuals, accessibility, partial-failure rendering, multi-account behavior, and several session behaviors remain unverified (`03-unresolved.md` U-03, U-04, U-25, U-26, U-34, U-37). This document preserves those uncertainties.

## 2. Sci-Link visual-family summary

| Family | Verified reference pattern | Natural use in the current product | Hard limit |
| --- | --- | --- | --- |
| **A. Auth** | Split desktop shell, equal visual/form columns, compact glass form card, shared fields/actions; brand panel disappears below 1024; Login/Register/Forgot are local form modes (`auth.md` §§Family conclusion, Auth page shell, Shared form system). | `/login` and `/register`; selected form primitives in onboarding. | Sci-Link's Forgot Password, school/telephone fields, email verification, and terms flow do not exist in the current backend. Its local mode-switch routing must not replace current routes. |
| **B. Authenticated app shell** | Dark glass frame, 216 px desktop sidebar, mobile drawer/app bar, independently scrolling main, 960 px content cap, shared search, cards, headings, overlays (`app-shell.md` §§Shared visual model, Shared shell measurements, Shared components). | Dashboard-level framing, top utilities, stat cards, section hierarchy, drawer treatment, and content-width candidates. | Current navigation is a modal drawer plus stateful overlays, not six Sci-Link routes. Shell adoption is an IA decision for Phase 3B, not a conclusion here. |
| **C. Marketing/public** | Long-form public landing page with fixed pill nav, hero, editorial sections, metrics, testimonials, CTA, form, and footer (`marketing.md` §§Design model, Global marketing shell). | No current reachable surface. | The current product has no public/marketing route or marketing content (`04-product-and-users.md` §3; `05` §1). Do not create one from the reference alone. |
| **D. Card/list/grid** | Stateful hierarchy browser with local search, breadcrumbs, Back/Home, responsive grids, collection/resource/recording variants, and drill-down that stays on one URL (`lessons.md` §§State model, Shared lessons shell, Card system). | Vocabulary library, collocation hierarchy, portions of Codex, collections, materials, and roadmap browsing. | Sci-Link's subject→instructor→year→module semantics, recording metadata, Telegram resources, and lesson route assumptions do not transfer. |
| **E. Utility/status** | Standalone dark public shell with legal, compact form, normal status, and warning status compositions; shared Auth primitives but distinct panels (`utility-legal.md` §§Family conclusion, Reuse analysis). | Empty/error/loading panels, account/session failure, completion/result summaries, and compact one-purpose forms. | Sci-Link reset/verification/rate-limit workflows are unsupported by the current account lifecycle. Status panels cannot substitute for product workflows or server state. |
| **F. Focused/live workspace** | Dedicated `100dvh` shell, primary work area plus optional 400 px side panel, stacked mobile regions, status presentation, internal scrolling (`live-classroom.md` §§Family conclusion, Page shell, Responsive behavior). | Rank exam, vocabulary boss, selected timed games, and graph/practice workspaces as a structural reference. | The current product has no realtime, stream, chat, moderation, or presence channel (`01-discovery-inventory.md` §7; `07-api-contract-reference.md` §7). Only the distraction-reduced workspace pattern transfers. |

**INFERRED:** Sci-Link offers a coherent visual vocabulary—Inter, near-black/navy surfaces, violet accent, white-alpha borders, glass panels, broad radius/spacing scales, and restrained state motion—but not a product model for quests, XP, ranks, exams, SRS, or game mechanics.

## 3. Current-product domain fit matrix

### Overview

| ID | Current product area and user goal | Current route/page state | Best Sci-Link family | Fit | Replacement safety |
| --- | --- | --- | --- | --- | --- |
| D-01 | Identity/session — enter or create the local account | `/login`, `/register`; logout in `/*` status state | Auth | **STRONG VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-02 | Onboarding/campaign activation — establish goals and start the campaign | `/onboarding` five-step local wizard | Auth + Utility + Card | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-03 | Campaign/roadmap — understand the 78-week plan and current phase | `/*` dashboard + Quest Main state | App Shell + Card/List/Grid | **PARTIAL VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-04 | Skills/progression — read XP, level, rank, promotion, support routing | `/*` dashboard/top bar/status modal | App Shell cards/stats | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-05 | Daily quests — complete work, then claim the reward | `/*` Quest Daily state | Card/List/Grid | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-06 | Weekly missions — track objectives and claim completion | `/*` dashboard card + Quest Weekly state | App Shell cards/status | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-07 | Check-ins/streak/shield — record daily condition and view commitment state | `/*` status modal + dashboard stats | Utility form + App Shell stats | **PARTIAL VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-08 | Badges — inspect locked and unlocked achievements | `/*` status modal Badge Wall | Card/List/Grid + status badges | **PARTIAL VISUAL ANALOGUE** | **SAFE PRESENTATION REPLACEMENT** |
| D-09 | Trackers — record errors, writing, speaking, mock tests | No reachable UI; backend-only | None | **NO NATURAL ANALOGUE** | **HIGH-RISK REPLACEMENT** if activated |
| D-10 | Monthly bosses — view current boss/timeline and eventually claim | `/*` Boss overlay + dashboard card | Utility/status + Card | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-11 | Rank exams — unlock, start, answer, time, submit, inspect result | `/*` banner → exam → result states | Focused workspace + Utility/status | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-12 | Certificates/test records — record evidence that can create rank suggestions | `/*` Certificate overlay | Utility form + Card/List | **PARTIAL VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-13 | Rank/weakness suggestions — inspect, apply, or dismiss recommendations | `/*` suggestion inbox dropdown | App notifications + status cards | **PARTIAL VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-14 | Vocabulary Codex/tree/SRS/errors — curate and review vocabulary state | `/*` Vocabulary Workspace states | Card/List/Grid + Focused workspace | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-15 | Vocabulary practice games — complete interactive drills | `/*` Shadow Duel, Word Family, Echo Chamber | Focused workspace | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-16 | Vocabulary boss — take a gated challenge and receive progression consequences | `/*` Vocabulary Boss state | Focused workspace + status result | **PARTIAL VISUAL ANALOGUE** | **HIGH-RISK REPLACEMENT** |
| D-17 | Collocations — browse hierarchy, add/remove cards, review familiarity | `/*` Collocations + Flashcard Gate state | Card/List/Grid | **PARTIAL VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-18 | Vocabulary library — browse five layers, inspect words, manage review cards | `/*` Vocabulary Library + Flashcard Gate state | Card/List/Grid | **STRONG VISUAL ANALOGUE** | **PRESENTATION + LOGIC COUPLED** |
| D-19 | Materials/plan browsing — inspect source materials/templates | No reachable UI; backend-only | Card/List/Grid only if surfaced later | **NO NATURAL ANALOGUE** today | **UNKNOWN** |
| D-20 | Dev/maintenance utilities — reset, migrate, regenerate | No UI; curl-only | None | **NO NATURAL ANALOGUE** | **HIGH-RISK REPLACEMENT** / do not surface by analogy |

### Per-domain transfer boundaries

#### D-01 — Identity and sessions

- **Transferable:** Auth canvas, split desktop composition, compact form panel, form titles/descriptions, leading-icon fields, primary/secondary actions, responsive removal of the brand panel. **INFERRED.**
- **Must not transfer:** Forgot-password mode, email verification, school/telephone collection, Sci-Link's local Login/Register mode switching, or Sci-Link credential semantics. **VERIFIED:** current routes are `/login` and `/register`; no reset or verification endpoints exist (`06-domain-capability-inventory.md` D-01; `09-authentication-and-authorization.md` §§2–5). Sci-Link evidence: `auth.md` §§Family conclusion, Login, Forgot Password, Register.
- **Product-specific requirements:** Vietnamese copy currently exists; token persistence, silent refresh, lockout, `onboarding_completed`, and logout behavior remain unchanged.
- **Risk:** the form is visual, but success paths hydrate Auth context and route according to current rules. Session death behavior remains **UNKNOWN** at runtime (U-34/U-37).

#### D-02 — Onboarding and campaign activation

- **Transferable:** Auth/utility field primitives, centered panel foundations, step labels, progress indicators, card selection, confirmation summary. **INFERRED.**
- **Must not transfer:** Sci-Link registration fields or utility-status workflows; no Sci-Link family models a five-step campaign activation.
- **Product-specific requirements:** optional display name, five target bands, one hardcoded campaign choice, start date, confirmation, and the exact activation payload. Activation back-links evidence, creates the campaign, flips onboarding, and recomputes progression (`04-product-and-users.md` §2.4; `06` D-02).
- **Risk:** **HIGH-RISK REPLACEMENT** because `refreshAuth()` then `navigate('/')` is load-bearing (`10-boundary-map.md` §B4). Current `/onboarding` is publicly renderable but API-protected (`09` §6.4); do not infer a new guard here.

#### D-03 — Campaign and roadmap

- **Transferable:** App Shell content framing, Page/Section headers, responsive card grids, Lessons-style hierarchy/breadcrumb treatment for explicit drill-down, status badges, and compact metadata rows. **INFERRED.**
- **Must not transfer:** lesson subjects, instructors, recordings, or Sci-Link route hierarchy.
- **Product-specific requirements:** 78 weeks, five phases, study-plan sessions, main quests, current-week context, and current stateful overlay navigation (`06` D-03).
- **Risk:** phase metadata is duplicated client/server and labels already drift (`10` §§A9, C5; `11` R-8). A visual rewrite must preserve the existing source boundary until Phase 3B decides responsibility.

#### D-04 — Skills and progression

- **Transferable:** stat-card grids, compact badges, progress-bar anatomy, grouped cards, supporting metadata, chart-card substrate. **INFERRED.**
- **Must not transfer:** Sci-Link metrics, ranks, watch-time semantics, or palette-to-status mappings.
- **Product-specific requirements:** five matrix skills, Grammar→Writing and Collocation→Vocabulary support routing, two XP notions, ranks F–S, promotion states, confirmed/pending rank, and rank history (`06` D-04; `10` §A1).
- **Risk:** **HIGH-RISK REPLACEMENT**. Skill bar percentage and player level fraction are client-owned; the private skill ladder can disagree with server rank (`10` §§A9, B4; `11` R-7/R-8; U-30/U-31/U-41).

#### D-05 — Daily quests

- **Transferable:** collection-card shells, list/grid responsiveness, status pills, disabled/locked styling, empty/loading states, and compact filters. **INFERRED.**
- **Must not transfer:** lesson-card click-as-navigation behavior. A quest card is a stateful transaction surface.
- **Product-specific requirements:** nine daily slots, dates, skill roles, boss locks, expiry, and the COMPLETE → CLAIM → CLAIMED two-step loop (`04` §1.1; `06` D-05).
- **Risk:** **HIGH-RISK REPLACEMENT** because `getQuestActionMeta` is the sole action-affordance rule, and quest mutation triggers eleven broad reads (`10` §B4; `08` §§T-4/T-5, §5).

#### D-06 — Weekly missions

- **Transferable:** progress card, objective rows, completion badge, primary claim action, utility empty/error presentation. **INFERRED.**
- **Must not transfer:** Sci-Link maintenance/progress marketing section or learning-progress metrics as functional analogues.
- **Product-specific requirements:** server mission items, recomputed counters, skill-XP claim, and visible live-vs-fallback source identity (`06` D-06; `08` §7.4).
- **Risk:** **HIGH-RISK REPLACEMENT** because the UI fabricates a fallback mission from a different client table. Intent is **UNKNOWN** (U-40/U-41; `11` R-7/R-8).

#### D-07 — Check-ins, streak, and shield

- **Transferable:** compact utility form controls, stat cards, semantic icon tiles, collapsible detail sections, history-list styling. **INFERRED.**
- **Must not transfer:** Sci-Link profile metadata fields or public status semantics.
- **Product-specific requirements:** mood/energy/focus bounds, note, selected date, streak/best streak, two-shield cap, regen progress, and perfect-day relationship (`06` D-07; `10` §A1).
- **Risk:** UI draft plus browser-local `getTodayISO()` determines the submitted date; the server uses its own date elsewhere (`10` §§A9, B4; `11` R-11).

#### D-08 — Badges

- **Transferable:** responsive card/wall layout, locked/unlocked variants, icon tile, description, progress/requirement metadata, and badges/pills. **INFERRED.**
- **Must not transfer:** Sci-Link verified/student badges or their meanings.
- **Product-specific requirements:** fixed server thresholds and campaign-scoped unlock state (`06` D-08; `10` §A1).
- **Risk:** individual badge rendering is presentation-safe when props remain intact; do not reimplement unlock logic or fetch `/badges` merely because a standalone screen is designed.

#### D-09 — Trackers

- **Transferable:** no current mapping. Sci-Link cards/forms may later supply primitives, but not a workflow analogue. **UNKNOWN** until product intent is settled.
- **Must not transfer:** arbitrary dashboard cards that imply the capability is usable.
- **Product-specific requirements:** error, writing, speaking, and mock-test entry models plus quest linkage (`06` D-09).
- **Risk:** backend exists, reachable UI does not. `TrackersPanel` is dead and labels are stale. Whether to revive or remove it is **UNKNOWN** (U-24). Phase 3B must decide product presence before Phase 3C designs it.

#### D-10 — Monthly bosses

- **Transferable:** status hero, timeline/list card, semantic cleared/locked states, result/status panel. **INFERRED.**
- **Must not transfer:** Sci-Link live/offline semantics or classroom framing.
- **Product-specific requirements:** monthly sequence, cleared state, claim eligibility, idempotent reward, and deliberate skill-XP-only award (`06` D-10; `10` §A3).
- **Risk:** claim endpoint is complete but no UI action exists. Whether omission is intentional is **UNKNOWN** (U-23). A redesign must not invent or omit the action as if decided.

#### D-11 — Rank exams

- **Transferable:** focused full-height shell, dominant question workspace, secondary navigator/status panel, compact classroom-like header, mobile panel stacking, and utility result state. **INFERRED.**
- **Must not transfer:** streaming, chat, moderated/slow-mode status, or Sci-Link's immediate panel toggle behavior.
- **Product-specific requirements:** unlock/start/resume, 2/day attempts, server expiry, question navigation, answer map, auto-submit, scoring, penalty, and rank result (`06` D-11; `08` T-8).
- **Risk:** **HIGH-RISK REPLACEMENT**. Timer and answers are client state; resume is broken; `'mcq'` vs `'multiple_choice'` makes the current UI unpassable. Preserve the defect as unresolved, not as desired behavior (U-21; `10` §B4/C5; `11` R-13).

#### D-12 — Certificates and test records

- **Transferable:** utility form, collection/list cards, empty state, result metadata, primary/secondary actions. **INFERRED.**
- **Must not transfer:** Sci-Link profile upload or verification flows.
- **Product-specific requirements:** four certificate types, test score fields, `/test-records` create/list path, and resulting suggestion generation (`06` D-12).
- **Risk:** the visible “certificate” form uses test-record endpoints, while certificate endpoints are unused. Preserve contracts and terminology ambiguity until Phase 3B adjudicates responsibility.

#### D-13 — Rank and weakness suggestions

- **Transferable:** Sci-Link notification-item hierarchy, unread/count badge treatment, detail summary, and action grouping. **INFERRED.**
- **Must not transfer:** passive notification semantics or route-based feed assumptions; current items cause domain mutations.
- **Product-specific requirements:** two suggestion types merged into one inbox, Apply/Dismiss actions, rank-floor XP consequence, and subsequent refetch (`06` D-13; `08` §7.2).
- **Risk:** **PRESENTATION + LOGIC COUPLED**. Applying a rank suggestion changes confirmed rank and raises XP; do not model it as a harmless dismissible notice (`10` §A8; `11` R-11).

#### D-14 — Vocabulary Codex, tree, SRS, and errors

- **Transferable:** App/Focused workspace shell, Lessons collection grids, local search, tabs, breadcrumbs for true hierarchy, form panels, card/list states, and status/empty panels. **INFERRED.**
- **Must not transfer:** a single uniform card family across graph editing, CRUD, review, and dungeon gameplay.
- **Product-specific requirements:** ten workspace modes, Codex CRUD, automatic card creation, React Flow tree editing, active error state, three review mechanisms, and refresh callbacks (`06` D-14; `08` T-9/T-10).
- **Risk:** **HIGH-RISK REPLACEMENT**. `VocabularyWorkspace.jsx` owns 30 local state values, review cursors, refresh triggers, an unbacked XP readout, and forge acknowledgement (`10` §§B1, B4).

#### D-15 — Vocabulary practice games

- **Transferable:** focused workspace framing, status HUD primitives, icon buttons, result panel, responsive single-task layout. **INFERRED.**
- **Must not transfer:** classroom/video/chat structure or generic content cards as the interaction model.
- **Product-specific requirements:** each game's timer, stage, lives/selections, score, and posted word list (`06` D-15).
- **Risk:** **HIGH-RISK REPLACEMENT** because scoring exists only in the client; the server receives the consequence-driving word list (`10` §§A9, B4; `11` R-7/R-11).

#### D-16 — Vocabulary boss

- **Transferable:** focused challenge shell, progression/status banner, question stage, side navigator, result panel, and warning/success variants. **INFERRED.**
- **Must not transfer:** Sci-Link live-state semantics or a generic status page in place of the exam.
- **Product-specific requirements:** boss catalogue, requirements, question types, 75% threshold, badges, and rank consequence (`06` D-16).
- **Risk:** **HIGH-RISK REPLACEMENT** because grading is client-side, correct answers are returned, and the server accepts `score_pct` to mutate rank (`09` §8; `11` R-11; U-39).

#### D-17 — Collocations

- **Transferable:** Lessons-style progressive drill-down, breadcrumbs, search/filter, collection cards, item list, and responsive grid; Form/Status primitives for add/remove/review feedback. **INFERRED.**
- **Must not transfer:** subject/instructor/year terminology or recording/resource cards.
- **Product-specific requirements:** level→section→topic→items, familiarity, card toggle, topic review, auto-complete acknowledgement, and support-XP routing (`06` D-17; `08` T-9).
- **Risk:** live UI does not implement Codex-word attachment; two phantom calls live only in dead UI. Do not import that dead flow into a new design (`10` §C5; U-24).

#### D-18 — Vocabulary library

- **Transferable:** hierarchy browser shell, breadcrumb state, Back/Home controls, local search, responsive collection grid, locked/empty cards, and internal-vs-page scrolling strategy. **INFERRED; strongest non-Auth analogue.**
- **Must not transfer:** Sci-Link entity names, recording metadata, Telegram resources, or external-classroom transition.
- **Product-specific requirements:** five layers (level→topic→unit→section→word), campaign links, locked empty levels, card add/remove, due review, familiarity decay, and mastery state (`06` D-18).
- **Risk:** hierarchy presentation is replaceable, but endpoint id spaces and review logic are not (`08` §§T-9, 7.5). Three empty levels are intentional status **UNKNOWN** (U-22).

#### D-19 — Study materials and plan browsing

- **Transferable:** only a future reference possibility: Lessons collection/resource hierarchy. **UNKNOWN** because no current UI exists.
- **Must not transfer:** inventing a material browser, route, or information architecture from Sci-Link.
- **Product-specific requirements:** markdown-seeded materials, quest templates, and study-plan relationships (`06` D-19; `11` R-5/R-6).
- **Risk:** current curriculum is a runtime file dependency. Phase 3B must first decide whether this becomes user-facing.

#### D-20 — Dev and maintenance utilities

- **Transferable:** none.
- **Must not transfer:** public utility panels, links, buttons, or discoverability for reset/migrate/regenerate actions.
- **Product-specific requirements:** development-only operational behavior, not a learner workflow.
- **Risk:** unauthenticated reset can delete all data (`09` §7; `11` R-15). This is not a design opportunity.

## 4. Page-by-page fit matrix

The route column preserves the four current route branches. Rows beneath `/*` are named states only.

| Current route/page | Primary user goal | Domain | Best Sci-Link family | Fit | Reusable shell | Reusable component patterns | Major mismatch | New pattern? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/login` | Authenticate | D-01 | Auth | Strong | Auth split shell candidate | Form panel, fields, primary/link actions | Current token/refresh/lockout behavior; Vietnamese copy | No |
| `/register` | Create account | D-01 | Auth | Strong | Auth split shell candidate | Form panel, fields, account switch | Current form has email/password and optional display name, not Sci-Link's five fields | No |
| `/onboarding` | Activate campaign and targets | D-02 | Auth + Utility | Partial | Centered/split shell candidate | Step header, form fields, selection cards, confirmation | Five-step campaign workflow has no Sci-Link equivalent | **Yes** |
| `/*` — dashboard | See today's plan, progression, roadmap, and alerts | D-03/D-04/D-06/D-07 | Authenticated App Shell | Partial | App frame candidate, pending Phase 3B | Top bar, page/section headers, stat/card/chart primitives | Dense game progression and mixed action/state ownership | **Yes** |
| `/*` — Navigation Drawer | Open six current destinations | Cross-cutting | App Shell mobile drawer | Partial | Drawer behavior candidate | Scrim, focusable nav rows, active/hover styles | Sci-Link drawer mirrors routed sidebar; current actions open overlays/mode switches | Yes |
| `/*` — Status modal | Inspect/edit profile, targets, skills, badges, history; logout | D-04/D-07/D-08 | App Profile + Utility | Partial | Dialog overlay | Metadata cards, inline edit, collapsible sections, danger action | Current composition mixes profile, progression, check-in, and logout | Yes |
| `/*` — Suggestion Inbox | Apply/dismiss rank and weakness suggestions | D-13 | App Notifications | Partial | Dropdown/detail surface | Feed item, count badge, action group | Items mutate rank/XP and are not passive notifications | Yes |
| `/*` — Quest Main tab | Browse roadmap sessions and main quests | D-03 | Lessons | Partial | Hierarchy panel | Breadcrumbs, collection cards, responsive grid | Time/phase map and quest state replace lesson hierarchy | Yes |
| `/*` — Quest Daily tab | Complete/claim daily quests | D-05 | Card/List/Grid | Partial | Collection panel | Filter, state cards, badges, empty state | Two-step transactional card actions | **Yes** |
| `/*` — Quest Weekly tab | Track/claim weekly mission | D-06 | App cards + Utility/status | Partial | Card panel | Progress card, objective list, CTA | Dual client/server mission identity | **Yes** |
| `/*` — Quest Archive tab | Inspect prior quest states | D-03/D-05 | Card/List/Grid | Partial | Collection panel | Filters, list/card states, status badges | Expired/claimed/completed semantics are product-specific | Yes |
| `/*` — Certificate overlay | List and create test evidence | D-12 | Utility form + list | Partial | Dialog/utility panel | Form fields, list cards, empty state | Record creation can trigger rank suggestions | Yes |
| `/*` — Boss overlay | Inspect monthly target and timeline | D-10 | Utility/status + cards | Partial | Dialog/status panel | Hero status, timeline cards, badges | Claim path is currently unwired and unresolved | Yes |
| `/*` — RankBossNotif | Respond to promotion eligibility/state | D-11 | Status banner | Partial | Inline status strip | Badge, warning copy, action button | State machine and broken resume semantics | Yes |
| `/*` — RankExamScreen | Complete timed promotion exam | D-11 | Focused workspace | Partial | Dedicated focused shell candidate | Header, dominant pane, side navigator, status, composer-like input | No Sci-Link question/timer/attempt pattern | **Yes** |
| `/*` — RankExamResultScreen | Understand pass/fail and rank consequence | D-11 | Utility/status | Partial | Centered status composition | Status icon, metrics, primary/secondary actions | Score, accuracy, penalty, and new-rank semantics | Yes |
| `/*` — Vocabulary Workspace shell | Switch among ten vocabulary capabilities | D-14–D-18 | App Shell + Focused workspace | Partial | Dedicated workspace shell candidate | Side navigation, top bar, responsive drawer, section container | Ten heterogeneous tools and heavy local state | **Yes** |
| `/*` — Codex Archive | Search/filter/create/edit vocabulary | D-14 | Card/List/Grid + Auth form | Partial | Workspace content shell | Search, filter, cards, form fields, empty state | CRUD creates flashcards and drives XP formula | Yes |
| `/*` — Word Network Tree | Edit vocabulary graph | D-14 | Focused workspace | None | Only low-level shell tokens | Side panel, icon buttons, status chips | Graph canvas/node/edge editing has no Sci-Link analogue | **Yes** |
| `/*` — Flashcard Gate | Review three card systems | D-14/D-17/D-18 | Focused workspace + tabs | Partial | Focused review shell candidate | Tabs, status, progress, actions | Three incompatible scheduling/id-space models | **Yes** |
| `/*` — Collocations | Drill level→section→topic→items | D-17 | Lessons | Strong structurally | Hierarchy browser candidate | Breadcrumbs, grid/cards, Back/Home, search | Familiarity, flashcard toggles, and auto-completion | Yes |
| `/*` — Vocabulary Library | Drill five layers and manage cards | D-18 | Lessons | Strong | Hierarchy browser candidate | Breadcrumbs, responsive grid, locked/empty cards | Mastery/familiarity and empty seeded levels | Yes |
| `/*` — Shadow Duel | Timed practice game | D-15 | Focused workspace | Partial | Focused shell only | HUD/status, actions, result panel | Game loop and scoring are client-only | **Yes** |
| `/*` — Word Family | Complete node-placement game | D-15 | Focused workspace | Partial | Focused shell only | Workspace, side status, result panel | Interactive graph/game mechanics | **Yes** |
| `/*` — Echo Chamber | Complete audio-supported drill | D-15 | Focused workspace | Partial | Focused shell only | Prompt panel, status, result | Speech synthesis and game scoring | **Yes** |
| `/*` — Error Dungeon | Defeat active vocabulary errors | D-14 | Focused workspace + cards | Partial | Focused shell only | Encounter card, progress/status, result | Error lifecycle and dungeon progression | **Yes** |
| `/*` — Vocabulary Boss Battles | Take gated vocabulary challenge | D-16 | Focused workspace + Utility result | Partial | Focused shell candidate | Status header, question pane, result panel | Client grading mutates rank | **Yes** |

**VERIFIED:** Dead components and backend-only surfaces are not added to this page matrix because no current navigation path can render them (`05-frontend-routes-and-navigation.md` §4). D-09, D-19, and D-20 remain in the domain matrix so their absence is explicit.

## 5. Component-pattern transfer matrix

| Sci-Link pattern | Classification | Fit and constraints |
| --- | --- | --- |
| `AppShell` / framed dark canvas | **TRANSFERABLE WITH VARIANT** | Useful for dashboard/workspace framing; must not assume Sci-Link routes, six-item nav, term block, global search, footer, or persistent sidebar. |
| Desktop `Sidebar` | **REFERENCE ONLY** | A viable treatment only if Phase 3B chooses persistent navigation. Current navigation is a modal drawer and state switches. |
| `SidebarNavItem` | **TRANSFERABLE WITH VARIANT** | Icon/label/active/hover anatomy transfers; destination semantics and active-state source differ. |
| Mobile `Drawer` + scrim | **DIRECTLY TRANSFERABLE** visually | Current product already uses a modal drawer. Preserve its focus trap, Escape/outside close, and callback behavior from `usePresenceLayer` (`05` §5). |
| `TopBar` | **TRANSFERABLE WITH VARIANT** | Header spacing, utility buttons, avatar, and count badge fit; term/search content and route behavior do not. |
| `SearchField` | **TRANSFERABLE WITH VARIANT** | Visual and focus system transfers. Search scope, query ownership, and actual filtering must be defined per current surface; Sci-Link global search appeared inert. |
| `PageHeader` | **DIRECTLY TRANSFERABLE** | Title/support/action structure is generic when product terminology remains current. |
| `SectionHeader` | **DIRECTLY TRANSFERABLE** | Useful for dashboard, status, quest, and workspace sections. |
| `GlassCard` / base `Card` | **DIRECTLY TRANSFERABLE** | Substrate, border, radius, padding, and shadow can become visual primitives. Interactive semantics stay outside the card. |
| `StatCard` | **TRANSFERABLE WITH VARIANT** | Layout transfers; XP, streak, shield, attempts, ranks, and their semantic colors require domain variants. |
| `CollectionCard` | **TRANSFERABLE WITH VARIANT** | Strong for vocabulary/collocation hierarchy; add locked, mastery, due-count, and action-bearing variants without importing lesson labels. |
| `ResourceCard` / `RecordingCard` | **REFERENCE ONLY** | Media/resource anatomy can inspire future materials, but current product has no comparable recording surface. |
| `ChartCard` | **TRANSFERABLE WITH VARIANT** | Visual frame transfers to roadmap/progress analytics; chart semantics and data density are product-specific. |
| `StatusPanel` | **TRANSFERABLE WITH VARIANT** | Good for exam result, empty/error, and gated states; success/failure/locked semantics need product tokens. |
| `FormField` | **DIRECTLY TRANSFERABLE** visually | Field anatomy and focus behavior fit Auth/utility forms. Preserve current field names, validation, payloads, and accessibility. |
| `PrimaryButton` / `SecondaryButton` / `IconButton` | **DIRECTLY TRANSFERABLE** visually | Reusable appearance and states; destructive, claim, submit, review, and disabled meanings require semantic variants. |
| `Badge` / `StatusChip` | **TRANSFERABLE WITH VARIANT** | Base pill transfers; rank, quest, mastery, boss, attempts, locked/unlocked, and due states need explicit mappings. |
| `EmptyState` | **TRANSFERABLE WITH VARIANT** | Shared hierarchy transfers; action availability and cause-specific copy are product-owned. |
| `LoadingState` | **TRANSFERABLE WITH VARIANT** | Sci-Link syncing/status language is reference only; current loaders and broad refetch behavior remain. |
| `ErrorState` | **TRANSFERABLE WITH VARIANT** | Utility warning composition transfers; 401, network, contract, exam, and validation states need separate behaviors. |
| `Breadcrumb` + Back/Home | **TRANSFERABLE WITH VARIANT** | Strong for collocation/vocab drill-down and perhaps roadmap hierarchy. Do not introduce globally or copy Sci-Link's clipped mobile crumbs. |
| `Tabs` | **TRANSFERABLE WITH VARIANT** | Visual treatment transfers; current tabs own local state and often gate distinct API/workflow behavior. |
| `DialogOverlay` / `OverlayPanel` | **DIRECTLY TRANSFERABLE** visually | Keep current modal semantics, focus trap, focus restore, Escape/outside close, and lazy-loading boundary. |
| `SidePanel` | **REFERENCE ONLY** | Useful for exam navigator, graph inspector, or review queue; not a universal secondary panel. |
| `InlineEdit` | **TRANSFERABLE WITH VARIANT** | Fits targets/profile-like edits; current save payloads and drafts remain authoritative. |
| `ProgressBar` / `ProgressRing` | **TRANSFERABLE WITH VARIANT** | Geometry transfers; percentage ownership must remain explicit because several current values are client-only or divergent. |
| `NotificationItem` | **TRANSFERABLE WITH VARIANT** | Fits suggestion hierarchy, but Apply/Dismiss effects distinguish it from a passive feed. |
| `FocusedWorkspaceShell` | **TRANSFERABLE WITH VARIANT** | Useful for exam, games, graph, and boss experiences. Only layout transfers; no live/chat semantics. |
| `LiveChatPanel`, moderation, stream status | **IRRELEVANT** | Current product has no realtime or chat surface. |
| Marketing hero/testimonials/CTA/footer | **IRRELEVANT** today | No current public marketing surface. Retain only low-level primitives if another current page independently needs them. |
| Legal document panel | **IRRELEVANT** today | No current legal route is documented. Do not add one by analogy. |

## 6. Design-token compatibility

| Token family | Classification | Compatibility judgement |
| --- | --- | --- |
| Typography family and basic hierarchy | **SAFE TO ADOPT GENERALLY** | Inter and a coherent heading/body/label scale fit both app and focused surfaces. Exact editorial marketing sizes should stay marketing-only if a public surface is ever approved. |
| Spacing scale | **SAFE TO ADOPT GENERALLY** | Sci-Link's repeated 4/8/12/16/24/32/40/48 family and compact equivalents can unify rhythm. Workflow layouts may add task-specific gaps. |
| Border system | **SAFE TO ADOPT GENERALLY** | White-alpha 5%/10%/20% tiers are useful for dark surfaces and focus hierarchy. Contrast must be validated against current content density. |
| Radius scale | **ADOPT WITH DOMAIN VARIANTS** | Small controls, medium cards, large panels, and pills form a useful system; exam/game HUDs and dense quest lists may need tighter variants. |
| Neutral colors | **SAFE TO ADOPT GENERALLY** | `#050505`, `#0B0E14`, `#151923`, off-white, and gray text roles align with the current hardcoded dark direction (`10-boundary-map.md` §B2). |
| Primary accent | **ADOPT WITH DOMAIN VARIANTS** | Violet/fuchsia can serve brand and primary actions. It must not automatically mean XP, rank, success, boss, or mastery. |
| Semantic colors | **DO NOT STANDARDIZE YET** | Current states include success/failure, COMPLETE/CLAIM/CLAIMED, expired, boss-locked, promotion states, due review, mastery tiers, streak/shield, and exam timing. Phase 3C must map meaning before color. |
| Glass/translucency | **ADOPT WITH DOMAIN VARIANTS** | Useful for shells, overlays, and status panels. Dense data lists, form readability, and long sessions may need more opaque surfaces. |
| Shadows/glows | **ADOPT WITH DOMAIN VARIANTS** | Sci-Link neutral elevation and violet glow are reusable. Strong glow should identify hierarchy/action, not every gamified state. |
| Information density | **ADOPT WITH DOMAIN VARIANTS** | Sci-Link app shell is moderately spacious; daily quests, exams, and ten-mode vocabulary tools require denser task variants. |
| Content widths | **ADOPT WITH DOMAIN VARIANTS** | A 960 px reading/dashboard cap is a good candidate; graph, exam, roadmap, and focused workspaces may need full-width shells. |
| Breakpoints | **DO NOT STANDARDIZE YET** | Current CSS uses 1220, 980, 640, and 599.98 px (`05` §5). Sci-Link uses material changes at 1280/1024/980/768/640 depending on family. Validate content, not names. |
| 12 px root at ≥1024 | **DO NOT STANDARDIZE YET** | It is a measured Sci-Link fidelity quirk causing a one-pixel scale discontinuity. It is not automatically a good product token (`app-shell.md` §Responsive system; `auth.md` §Responsive behavior). |
| Motion/transitions | **ADOPT WITH DOMAIN VARIANTS** | 150 ms field/hover, 300 ms controls/drawers, and restrained panel motion are useful. Timed games/exams must not obscure state; reduced motion is required. |

### Semantic-state guardrail

**VERIFIED:** Sci-Link semantic colors cover generic success/info/warning/danger, but not the current product's exact state machines (`app-shell.md` §Design tokens; current `10-boundary-map.md` §§A1, C2). Therefore Phase 3C must define separate tokens for at least:

- player/skill XP and progression;
- ranks F–S and pending/confirmed rank;
- quest pending, complete, claimable, claimed, expired, and boss-locked;
- promotion `none`, `eligible`, `boss_required`, `in_progress`, and `passed`;
- mastery/familiarity `again`, `hard`, `good`, `easy` plus locked/unlocked;
- exam normal, warning, timed-out, passed, and failed;
- streak/shield/perfect-day state;
- suggestion pending/applied/dismissed;
- backend error, session expiry, and offline/network failure.

## 7. Interaction-pattern compatibility

| Pattern | Verdict | Current-product fit |
| --- | --- | --- |
| Sidebar navigation | **NEEDS ADAPTATION** | Visual treatment fits, but persistent navigation would change current drawer/overlay IA. Phase 3B decides; this phase does not. |
| Mobile drawer | **CAN TRANSFER** | Current product already has a modal drawer. Preserve focus trap, Escape/outside click, and restore behavior. |
| Tabs | **NEEDS ADAPTATION** | Current Quest and Vocabulary tabs drive different data and local state; keep semantics and state ownership explicit. |
| Breadcrumb drill-down | **CAN TRANSFER** in hierarchical modules | Strong for Collocations and Vocabulary Library; not a global app navigation pattern. |
| Search/filter | **NEEDS ADAPTATION** | Fits Codex and collections. Each scope needs real behavior; do not copy the inert Sci-Link global search. |
| Card click → deeper collection | **CAN TRANSFER** | Strong for hierarchy browsing. Not suitable for quest actions, exams, or mutating suggestion cards. |
| COMPLETE/CLAIM card actions | **SHOULD NOT TRANSFER** from Sci-Link | No Sci-Link analogue. Preserve current action-state logic and design a product-specific pattern later. |
| Expand/collapse | **CAN TRANSFER** | Useful for status/history/secondary detail; keep accessibility and current drafts intact. |
| Side panel | **NEEDS ADAPTATION** | Useful in focused workflows; responsive ownership and task content differ from chat. |
| Modal/overlay | **CAN TRANSFER** visually | Current app already relies on overlays. Preserve `usePresenceLayer` behavior and state callbacks. |
| Inline edit | **CAN TRANSFER** | Fits targets and account-like data; save/cancel/error semantics remain current-product concerns. |
| Loading/sync | **NEEDS ADAPTATION** | Sci-Link has explicit syncing/connecting states; current app has `SYSTEM LOADING`, API-error, and broad refetches. Do not imply realtime synchronization. |
| Empty state | **CAN TRANSFER** | Copy/actions must distinguish no data, locked content, due-empty, unavailable backend-only feature, and errors. |
| Error/warning status | **CAN TRANSFER** with variants | Utility family is a strong visual base; session, network, exam, and validation behaviors remain distinct. |
| Success feedback | **NEEDS ADAPTATION** | Current toasts, reward animation, result screens, and rank changes have different persistence and consequence. |
| Realtime/live status | **SHOULD NOT TRANSFER** | Current product has no realtime channel. Local timers are not realtime data. |
| Show/hide secondary panel | **NEEDS ADAPTATION** | Structurally useful in focused workspaces, but Sci-Link's panel mounts instantly and its mobile offline content clips; do not copy those quirks. |
| Hover lift/tilt/zoom | **NEEDS ADAPTATION** | Suitable for browse cards, not dense quest/actions, keyboard-critical exams, or touch-only game controls. |
| Route-local mode switch without URL change | **NEEDS ADAPTATION** | Current app already has extensive local state, but Sci-Link Auth mode behavior must not erase `/login` vs `/register` route semantics. |

## 8. Responsive-pattern compatibility

| Pattern | Classification | Fit by current area |
| --- | --- | --- |
| Desktop sidebar + independent main scroll | **NEEDS VALIDATION** | Good structural candidate for dashboard/workspace, but adoption depends on Phase 3B navigation grouping and current 980/1220 behavior. |
| Mobile drawer over content | **GOOD CANDIDATE** | Closely matches the current drawer interaction; preserve modal accessibility. |
| 960 px max-width content | **GOOD CANDIDATE** | Appropriate for dashboard, forms, lists, status, and quest summaries; not for graph/exam/game workspaces. |
| Responsive collection grid | **GOOD CANDIDATE** | Strong for badges, Codex, Collocations, Vocabulary Library, certificates, and archive cards. |
| One-column card stacking | **GOOD CANDIDATE** | Natural for mobile browse/content views; action density still needs testing. |
| 400 px desktop side panel → mobile vertical stack | **NEEDS VALIDATION** | Candidate for exam navigator or graph inspector, but exact 50/50 stacking and internal scrolling may not fit task content. |
| Typography scaling by root switch | **POOR FIT** as-is | Sci-Link's 1024 jump is visually verified but abrupt. Current content and existing breakpoints must drive scaling. |
| Utility-page centered panel | **GOOD CANDIDATE** | Fits login/register/result/error and compact one-purpose forms, not long quest or vocabulary workflows. |
| Auth brand panel hidden below 1024 | **GOOD CANDIDATE** | Likely fit for `/login` and `/register`; onboarding may require a different density due to five steps. |
| Internal desktop list scroll; page scroll on mobile | **NEEDS VALIDATION** | Useful for long hierarchy/workspace panes, but current overlay height, focus, and game state must be tested. |
| Stable DOM order during reflow | **GOOD CANDIDATE** | Matches accessible responsive behavior; avoid visual-only reordering unless Phase 3C proves a need. |
| Sci-Link 1024/768/640 thresholds | **NEEDS VALIDATION** | They are measured reference breakpoints, not target-product requirements. Current CSS already uses 1220/980/640/599.98. |

**VERIFIED:** Sci-Link itself does not use one universal responsive system: the app shell changes at 1024/768/1280, marketing at 1024/980/768/640, Auth at 1024/768, and Live at 1024/768/640. Phase 3C should validate components against content rather than import one breakpoint table.

## 9. Patterns that must NOT be imported

1. **Sci-Link business hierarchy:** subject, instructor, year, program, unit, module, recording, Telegram resource, term, watch-time, classroom, moderated chat, or student-account metadata.
2. **Sci-Link routes or routing architecture:** `/dashboard`, `/lessons`, `/analytics`, `/notices`, `/notifications`, `/profile`, `/live`, `/terms`, `/reset-password`, `/verify-email`, and `/rate-limited` are reference routes only. Current routes remain `/login`, `/register`, `/onboarding`, and `/*`.
3. **Sci-Link navigation labels or final shell:** no six-link student sidebar, global lessons search, term block, appearance controls, profile summary, or developer footer should be imported without Phase 3B product decisions.
4. **Sci-Link Auth mode semantics:** do not collapse current `/login` and `/register` into one in-place mode merely because the reference can; do not add Forgot Password, verification, reset, or rate-limit flows unsupported by current contracts.
5. **Public marketing IA:** the current product has no public landing page. Do not create a hero, testimonial, subject, metrics, CTA, email, or social/footer surface by analogy.
6. **Live-classroom semantics:** no stream, online/offline broadcast, chat, moderation, slow mode, messages, composer, or live presence exists in the current product.
7. **Sci-Link content assumptions:** lesson media, external Telegram/YouTube actions, instructor portraits, video duration/views/dates, and classroom connection stages do not describe the current material tracker.
8. **Reference semantic color mapping:** violet, green, blue, orange, pink, and red must not be assigned to XP, rank, quest, mastery, exam, or lock states solely because Sci-Link uses them elsewhere.
9. **The 12 px desktop root-size discontinuity:** measured fidelity behavior is not automatically a desirable target.
10. **Known responsive quirks:** clipped deep lesson breadcrumbs; mobile live panel centering that puts content above the scrollport; abrupt root-scale changes; immediate chat geometry despite transition classes.
11. **Known reference inconsistencies:** inert tested global search, unusual notification-overlay containing block, profile view/edit subject mismatch, and third-party Telegram embed variability (`site-inventory.md` §Exploration notes; `app-shell.md` §Reconstruction cautions).
12. **Decorative motion as workflow state:** marketing marquee, orbit canvas, counters, reveal animations, and strong hover tilt must not appear in timed, high-stakes, or dense task surfaces by default.
13. **Visual similarity as functional equivalence:** Sci-Link Dashboard is not the current Dashboard; Sci-Link notifications are not rank suggestions; Live Classroom is not a rank exam; Lessons is not vocabulary business logic.
14. **Source, API, or business assumptions from Sci-Link:** no source structure, component implementation, auth contract, persistence model, API shape, or feature logic is an input to later architecture.

## 10. Product areas requiring new patterns

| Area | Why Sci-Link is insufficient | New pattern eventually required — not designed here |
| --- | --- | --- |
| XP/progression overview | Sci-Link stats/charts provide framing but not mean-vs-ledger XP, skill support routing, level fraction, confirmed/pending rank, or drift warnings. | Product-specific progression summary and semantic model. |
| Quest COMPLETE→CLAIM loop | Sci-Link cards navigate or open content; they do not model completion followed by explicit reward banking, expiry, locks, or idempotency. | Transactional quest card/action-state pattern. |
| Weekly mission dual source | No reference pattern communicates server state versus fabricated fallback identity. | Mission-source, objective, and claim pattern after product intent is settled. |
| 78-week roadmap | Lessons drill-down is hierarchical, not temporal/phase-based with sessions and main quests. | Campaign timeline/roadmap pattern. |
| Rank promotion | Generic badges/status panels do not explain eligible→boss_required→in_progress→passed/none. | Promotion-state pattern spanning banner, action, and history. |
| Rank exam | Live workspace supplies only shell geometry; attempts, expiry, question types, auto-submit, result, penalty, and resume need an exam system. | Timed assessment workspace and persistence pattern. |
| Check-in/streak/shield | Stat cards do not encode daily input, replay, shield consumption/regen, and perfect-day conditions. | Commitment-state and daily check-in pattern. |
| Vocabulary SRS | Three current review engines have different due/familiarity/id models. Sci-Link offers no SRS workflow. | Review queue/card/session pattern with explicit mechanism variants. |
| Vocabulary graph | No Sci-Link family covers node/edge editing and inspector state. | Graph workspace, selection, edit, and mobile fallback pattern. |
| Practice games | Focused shell is only a frame; lives, stages, timers, interactions, score, and mastery consequences are unique. | Game HUD, interaction, and result patterns. |
| Vocabulary boss | Generic exam/status framing does not cover client grading and rank consequence. | Boss challenge and result pattern after trust-boundary decisions. |
| Error Dungeon | Neither status cards nor Lessons represent error encounters and defeat progression. | Error-review/encounter pattern. |
| Suggestions | Sci-Link notifications are passive; current Apply can change rank and XP. | Consequential recommendation pattern with confirmation/effect disclosure. |
| Certificates/test evidence | Generic forms/lists do not show downstream inferred rank suggestions or overlapping contracts. | Evidence-record pattern with consequence visibility. |
| Tracker surfaces | No reachable current UI and no Sci-Link analogue settle how four tracker families should work. | Product decision first, then tracker entry/history patterns. |
| Mixed-language product | Sci-Link is not evidence for English/Vietnamese policy. | Localization/content-language rules after Phase 3B decides terminology. |

## 11. Business-logic replacement risks

Cross-check: `10-boundary-map.md` and `11-risk-and-coupling-register.md` are authoritative here.

| Current surface | Safety label | Logic/state that must survive | Sci-Link use allowed |
| --- | --- | --- | --- |
| Pure card/panel markup receiving finished props | **SAFE PRESENTATION REPLACEMENT** | Prop shape, callbacks, accessible naming | Card, typography, spacing, radius, shadow, responsive grid |
| `HomeTopBar`, `OverlayFrame`, `PanelFrame`, presentational result/badge renderers | **SAFE PRESENTATION REPLACEMENT** conditionally | `aria-*`, focus trap/restore, action callback, count source | Shell/control styling and layout only |
| Auth Login/Register forms | **PRESENTATION + LOGIC COUPLED** | token write, `getMe`, context hydration, onboarding redirect, lockout/error rendering | Auth shell and form primitives |
| `/onboarding` | **HIGH-RISK REPLACEMENT** | five-step draft/payload, campaign activation, `refreshAuth`, redirect | Form/step visuals only |
| `App.jsx` shell/dashboard orchestration | **HIGH-RISK REPLACEMENT** | ~30 states, six mount loaders, 13 initial requests, open/close helpers, refetch triggers, 401 behavior | Visual frame only; do not wholesale replace |
| `dashboard-data.js` | **HIGH-RISK REPLACEMENT** | thirteen client-only rules, view builders, private ladders, fallback mission, action affordances | No direct Sci-Link substitution |
| Daily Quest board | **HIGH-RISK REPLACEMENT** | `getQuestActionMeta`, pending state, mutation, COMPLETE/CLAIM ordering, broad refetch | Card/list visuals only |
| Weekly Mission card/panel | **HIGH-RISK REPLACEMENT** | fallback identity, live merge, source label, claim/refetch | Progress/objective visuals only |
| Skill/level progress visuals | **HIGH-RISK REPLACEMENT** | private skill ladder and mirrored level fraction | Stat/progress visuals only |
| Status modal/check-in | **PRESENTATION + LOGIC COUPLED** | drafts, local today, target save, section state, logout | Dialog, fields, cards, collapsibles |
| Suggestion inbox | **PRESENTATION + LOGIC COUPLED** | dynamic endpoint, apply/dismiss, rank/XP effects, reloads | Notification-item hierarchy only |
| Rank exam screen and banner | **HIGH-RISK REPLACEMENT** | unlock/start/submit, answers, timer/auto-submit, daily cap, broken resume, type mismatch | Focused shell/status visuals only |
| Vocabulary workspace root | **HIGH-RISK REPLACEMENT** | 30 local states, tab selection, CRUD drafts, review cursors, `onLoadData` refresh triggers | Workspace shell and generic primitives only |
| Shadow Duel / Echo Chamber / Word Family | **HIGH-RISK REPLACEMENT** | client-only scoring and posted words | Focused layout/HUD visuals only |
| Vocabulary Boss | **HIGH-RISK REPLACEMENT** | local grading, posted `score_pct`, rank consequence | Challenge/result visual shell only |
| Collocation and Vocabulary Library hierarchy | **PRESENTATION + LOGIC COUPLED** | endpoint-specific ids, add/remove/review actions, familiarity decay acknowledgement, drill state | Lessons-style hierarchy/grid patterns |
| Word Network Tree | **PRESENTATION + LOGIC COUPLED** | node/edge mutations, selection/drag drafts, sync-all | Generic shell/side panel/buttons only |
| Dead components/API wrappers | **HIGH-RISK REPLACEMENT** if deleted | may be sole evidence of intended endpoints/features; intent U-24 unresolved | None until adjudicated |
| CSS-only visual rules | **SAFE PRESENTATION REPLACEMENT** in isolation | interaction affordance, focus visibility, reduced motion, layout hooks used by logic | Tokens and visual primitives |

### Load-bearing boundaries that visual work must not cross

1. **VERIFIED:** `refresh_progress_state` and its 33 call sites own progression freshness; eight GETs write (`10` §A1; `11` R-1).
2. **VERIFIED:** `campaign_skill_states` has 32 writes across seven functions; UI must not write or recompute authoritative progression (`11` R-2).
3. **VERIFIED:** curriculum and quest generation come from markdown/seeding, not a client collection (`10` §§A3/A7; `11` R-5/R-6).
4. **VERIFIED:** thirteen client-only rules disappear if `dashboard-data.js` or stateful components are replaced (`10` §A9; `11` R-7).
5. **VERIFIED:** current API paths, response shapes, enum strings, auth storage/cookie behavior, and configuration are contracts (`10` Part C).
6. **VERIFIED:** several client inputs cause stored consequences—words, scores, dates, evidence, suggestion actions (`09` §8; `11` R-11).
7. **UNKNOWN:** runtime behavior of backend tests, concurrent refresh, rejected loaders, multi-account scoping, and live accessibility remains unresolved (U-03/U-04/U-25/U-26/U-37).

## 12. Inputs for Phase 3B

Phase 3B must make these **product/information-architecture decisions**. This phase deliberately does not answer them.

1. Should the authenticated experience keep the current drawer/overlay model, introduce persistent navigation, or use a hybrid—and which existing destinations belong in it?
2. Which current stateful surfaces should remain overlays/workspace modes, and which, if any, should later become addressable pages? Current routes remain unchanged until that decision is approved.
3. What is the dashboard's primary responsibility: today's action queue, campaign roadmap, progression summary, alerts, or a defined combination?
4. How should Quest Main/Daily/Weekly/Archive responsibilities and entry points be grouped without changing their rules?
5. How should the ten Vocabulary Workspace modes be grouped, named, and prioritized? Are Codex, review, hierarchy browsing, games, errors, and bosses one domain or several user-facing groups?
6. Should profile/status, check-in, targets, skills, badges, history, and logout remain one modal responsibility?
7. Are Trackers user-facing product capabilities, deferred capabilities, or intentionally absent? U-24 and D-09 must be adjudicated first.
8. Should Materials/Quest Templates become browsable, or remain backend inputs only?
9. What is the intended monthly-boss claim experience (U-23), and what is the intended resume/attempt experience for rank exams (U-21)?
10. Which certificate/test-record terminology and workflow is canonical, given the live UI uses `/test-records` while certificate endpoints remain unused?
11. What terminology is canonical for the three XP concepts, skill progress, ranks, mastery, and weekly missions (U-30/U-31/U-40/U-41)?
12. What is the product language policy: English, Vietnamese, or a defined bilingual mode?
13. Is a public/marketing surface required at all? No current route supplies evidence that it is.
14. Which dead UI is superseded versus future scope (U-24), and which backend-only capabilities belong in the eventual product?

## 13. Inputs for Phase 3C

After Phase 3B settles product structure, Phase 3C must make these **design-system decisions**. No decision is made here.

1. Whether to adopt an Auth split shell and how onboarding varies from Login/Register.
2. Whether an authenticated App Shell, focused workspace shell, or both are needed, and which surfaces receive each.
3. Whether persistent sidebar, mobile drawer, top bar, content caps, and internal scroll regions fit the approved IA.
4. The final typography family/scale, density tiers, spacing scale, radius hierarchy, borders, shadows, blur, and neutral palette.
5. Whether violet/fuchsia remains brand-only or also serves primary action, and the complete semantic color map for progression, quests, mastery, locks, exams, suggestions, errors, and success.
6. Breakpoints based on current content, reconciling existing 1220/980/640/599.98 behavior with the reference's component-specific thresholds; whether to reject the Sci-Link 12 px root switch.
7. Card variants: stat, collection, transactional quest, mission, achievement, suggestion, evidence, hierarchy, game/result, and status.
8. Hierarchy-browser behavior for Collocations/Vocabulary Library: breadcrumbs, Back/Home, search, locked/empty states, scroll ownership, and mobile overflow.
9. Overlay/dialog variants and their focus, Escape, outside-click, restore, loading, and failure behavior.
10. Focused workspace variants for rank exams, bosses, graph editing, SRS, and games—including side-panel behavior and mobile stacking.
11. Product-specific progress, roadmap, quest action, promotion, attempts/timer, SRS, game HUD, and consequence-disclosure patterns absent from Sci-Link.
12. Motion tokens and reduced-motion rules; decorative motion must be separated from time-critical or state-significant motion.
13. Loading, empty, locked, offline/network, validation, session-expired, success, failed, timed-out, and partial-data states.
14. Accessibility and touch validation for current dense workflows, because current runtime accessibility remains U-26.

## 14. Unresolved questions

### Preserved Phase 3A.1 uncertainty

- **UNKNOWN — U-03/U-28:** multi-account isolation and full unscoped-handler set. Do not design account switching or multi-user affordances.
- **UNKNOWN — U-04:** backend behavior is statically read but tests were not executed.
- **UNKNOWN — U-11:** cross-tab/device freshness is a product requirement or not; no push exists.
- **UNKNOWN — U-20:** preferences are written and unread; theme/locale/notification settings intent is unresolved.
- **UNKNOWN — U-21:** rank-exam question-type mismatch intent; do not style the defect into permanence.
- **UNKNOWN — U-22:** empty vocabulary levels are intended locked content or unfinished material.
- **UNKNOWN — U-23:** monthly boss claim omission is intentional or incomplete.
- **UNKNOWN — U-24:** dead components are abandoned, alternate, or future scope.
- **UNKNOWN — U-25/U-34:** actual failed-loader and expired-session experience.
- **UNKNOWN — U-26:** current runtime accessibility.
- **UNKNOWN — U-30/U-31/U-33:** XP terminology, private skill ladder, and unbacked review XP intent.
- **UNKNOWN — U-37:** concurrent refresh behavior.
- **UNKNOWN — U-39:** client-supplied grading/authority is deliberate.
- **UNKNOWN — U-40/U-41:** weekly fallback and client-only progression values are intended and user-relevant.
- **UNKNOWN — U-42:** intended de-facto contract width.

### Questions introduced by reference fit

1. Which Sci-Link visual traits are desired brand attributes versus incidental reference details?
2. Is a persistent authenticated shell compatible with the product's intended focus, or should the current overlay/workspace model remain dominant?
3. Which current surfaces require dense operational layouts rather than Sci-Link's spacious card rhythm?
4. Should browse hierarchies share one visual system while retaining separate data/action adapters for Codex, Collocations, and Vocabulary Library?
5. Which focused workflows need a secondary side panel, and what content earns that space?
6. Which semantic states must be visually comparable across quests, progression, mastery, and exams, and which must remain distinct?
7. Which current responsive behavior is intentional versus accumulated CSS, given no current runtime visual audit is part of Phase 3A.1?

### Concise handoff summary

1. **Strongest Sci-Link visual analogues:** Auth for `/login` and `/register`; Lessons hierarchy for Vocabulary Library and Collocations; low-level App Shell cards, fields, buttons, overlays, and responsive drawer.
2. **Partial analogues:** dashboard framing, roadmap, status modal, suggestions, quests, weekly mission, check-in, certificates, vocabulary workspace, exams, bosses, and games. Their visual shells transfer; workflow/state semantics do not.
3. **No analogue:** graph editing, the transactional quest claim loop, three SRS models, product-specific progression/rank semantics, backend-only Trackers/Materials, and dev utilities. Marketing and live chat are irrelevant to the current product.
4. **Highest-risk replacements:** `App.jsx`, `dashboard-data.js`, onboarding, daily/weekly quest surfaces, skill progress, rank exam, Vocabulary Workspace, practice games, and Vocabulary Boss.
5. **Phase 3B must decide:** IA, navigation grouping, page responsibilities, overlay-versus-page boundaries, vocabulary grouping, trackers/materials inclusion, canonical terminology, and language policy.
6. **Phase 3C must decide:** shell variants, card system, token/semantic adaptation, breakpoints, responsive scroll/panel rules, component variants, accessibility/motion, and the new product-specific patterns Sci-Link does not supply.

Phase 3A.2 stops here. No Phase 3B or Phase 3C decision has been made, and no UI implementation is included.
