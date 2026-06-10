# Vocabulary Support Skill System Spec

_For IELTS Quest Dashboard / Solo-Leveling-inspired gamified learning system_

> **Last updated:** 2026-06-10 (session 8n+1 — gap-checked against code; all sections corrected to match actual implementation)
>
> **Implementation status:** Phases I1–I4 **complete**. All core modules exist in code. Remaining work is frontend visualization (Word Network Tree), UI polish for stub modules, and boss/error-dungeon completion.

---

## 0. Purpose

This document describes the **Vocabulary Support Skill** module for the IELTS Quest Dashboard. It is the living spec that agents and developers load to understand what exists, what the rules are, and what remains to build.

Target stack (actual, not proposed):

```text
Frontend: React 18 + Vite — raw JSX + src/styles.css (no TypeScript, no CSS framework)
Backend: FastAPI + SQLAlchemy 2 (sync sessions) + Alembic migrations
Database: MySQL 8.4 (port 3307 external / 3306 internal)
Runtime: Docker Compose — backend volume-mounts ./backend for hot-reload
Auth: JWT (access token in localStorage, refresh token in httpOnly cookie)
```

---

## 1. Source Grounding

### 1.1. Learning sources

This spec is grounded in two vocabulary-learning textbooks:

1. `effective-vocabulary-learning-pre-Intermediate.pdf`
2. `effective-vocabulary-learning-upper-Intermediate.pdf`

### 1.2. Source-based learning principles

Pre-intermediate supports:

- Build a daily and weekly revision routine.
- Learn actively: say words aloud, highlight, write down, write example sentences.
- Revise by covering meaning and testing memory.
- Use a vocabulary notebook.
- Organize words by topic.
- Add translation, English meaning, synonyms, opposites, word family, pronunciation, common word partners.
- Guess meaning first, then check with a dictionary.

Upper-intermediate supports:

- Learn words in phrases, not in isolation.
- Learn collocations, grammar characteristics, pronunciation, stress, and register.
- Group words by topic, grammar feature, word root, or meaning.
- Use diagrams, charts, tables, and network diagrams.
- Record synonyms, antonyms, word class, word family, stress, and typical learner errors.
- Use dictionary information: pronunciation, grammar pattern, synonym, antonym, collocation, register.
- Guess meaning from context using visual clues, surrounding words, grammar clues, background knowledge, prefixes/suffixes, and similarity to known words.

### 1.3. Mapping to implemented features

| Source idea | Implemented game feature |
|---|---|
| Vocabulary notebook | Codex Archive (`vocabulary_items`) |
| Cover meaning → recall → check | Flashcard Gate (tap-to-flip card, again/hard/good/easy) |
| Network / diagram | Word Network Tree (`vocabulary_topics/nodes/edges`) |
| Collocations | Collocation Forge (`collocation_*` tables, browser + flashcard) |
| Word family | Word Family Evolution (`vocabulary_relations`) |
| Synonym / antonym | Shadow Duel |
| Pronunciation / stress | Echo Chamber |
| Guess meaning from context | Context Hunt (not started) |
| Typical errors | Error Dungeon (`vocabulary_errors`) |
| Checkpoint test | Vocabulary Boss (`VocabularyBoss.jsx`) |

---

## 2. System Overview

### 2.1. System name

```text
Lexical Awakening System
```

### 2.2. Entry point

`VocabularyWorkspace` is a full-page view (`.vocab-shell`) launched from `App.jsx` via `currentView === 'vocabulary'`. It is **not** a route — it replaces the dashboard view state. Tabs within the workspace use local `activeTab` state (no React Router).

### 2.3. Module structure (actual)

```text
VocabularyWorkspace (full-page shell, App.jsx)
├── Codex Archive              — vocabulary_items CRUD + examples
├── Flashcard Gate             — activeTab === 'flashcard' in VocabularyWorkspace
│   ├── Vocabulary sub-tab     — due flashcards from flashcards table (SRS)
│   └── Collocation sub-tab    — collocation_flashcards table (familiarity model)
├── Collocation Forge          — CollocationForge.jsx, own tab
│   ├── Browser layer 1        — section accordion
│   ├── Browser layer 2        — topic progress boxes (neon % fill)
│   └── Browser layer 3        — collocation items + add/remove flashcard
├── Word Network Tree          — WordNetworkTree.jsx (backend live, UI stub)
├── Word Family Evolution      — WordFamilyEvolution.jsx (schema live, UI stub)
├── Shadow Duel                — ShadowDuel.jsx (backend partially live, UI stub)
├── Echo Chamber               — EchoChamber.jsx (backend stub, UI stub)
├── Error Dungeon              — ErrorDungeon.jsx (partially live)
└── Vocabulary Boss            — VocabularyBoss.jsx (backend partially live, UI thin)
```

### 2.4. Main game loop (implemented)

```text
Discover word
→ Add to Codex (vocabulary_items)
→ Add meaning / pronunciation / part of speech / example
→ Add to flashcard deck (auto-generates Flashcard row)
→ Review in Flashcard Gate (tap card → flip → grade again/hard/good/easy)
→ Vocabulary XP is recomputed from aggregate data — see §2.6
→ Browse Collocation Forge sections → add collocation flashcards
→ Review collocation flashcards (same flip UI, familiarity + decay)
→ 5 distinct collocation reviews/day → auto-complete "Collocation Forge" daily quest
  (daily_slot_code = "vocab_collocation")
→ Error Dungeon / Shadow Duel / Echo Chamber / Word Tree for depth
→ Vocabulary Boss for monthly checkpoint
```

### 2.5. Rank system

Uses the existing system-wide rank scale:

```text
F → E → D → C → B → A → S
```

XP thresholds (seeded in `rank_exam_pools.xp_threshold`):

| Target Rank | XP Required |
|---|---:|
| E | 500 |
| D | 1 200 |
| C | 2 500 |
| B | 4 500 |
| A | 7 000 |
| S | 10 000 |

### 2.6. Vocabulary XP model — recompute, not per-event

Vocabulary skill XP is **not** awarded per flashcard review. It is **recomputed** each time `refresh_progress_state()` is called, via `compute_vocabulary_xp()` in `services.py`.

The recompute aggregates:

| Source | XP formula |
|---|---|
| Each `vocabulary_item` | Base 2 XP + data-completeness XP (capped at 40) + mastery_score (capped at 50) |
| `player_collocation_progress` rows | 5 XP per completed collocation (legacy table) |
| `vocabulary_errors` logged | +1 XP per error logged |
| `vocabulary_errors` corrected | +5 XP per `defeated_count` tick |
| `vocabulary_errors` defeated | +20 XP per defeated error |
| Vocabulary skill confirmed rank | +60 XP if `confirmed_rank` ∈ {E–S} |
| Badge: Memory Streak Badge I | +80 XP |
| Badge: Writing Lexical Buff | +100 XP |
| Badge: Lexical Awakener | +200 XP |

**There is no per-review XP for flashcard grading (again/hard/good/easy).** Flashcard reviews affect `familiarity` state and `due_date` only. Vocabulary XP grows through adding words, enriching them, correcting errors, and earning badges — not through review repetition.

Quest claim XP (e.g. Collocation Forge daily) flows through the normal quest claim → `award_skill_xp` path and is additive on top of the recomputed base.

---

## 3. Feature Status

### 3.1. Codex Archive ✅ LIVE

**What exists:**
- `vocabulary_items` table: `word`, `normalized_word`, `part_of_speech`, `cefr_level`, `ielts_topic`, `meaning_en`, `meaning_vi`, `pronunciation_ipa`, `word_stress`, `source_type`, `source_reference`.
- `vocabulary_examples` table: linked to `vocabulary_item_id`.
- `flashcards` table: auto-created from vocabulary items; `card_type`, `front_text`, `back_text`, `hint`, `difficulty`, `status`.
- `vocabulary_relations` table: `source_word_id`, `target_word_id`, `target_text`, `relation_type` (`synonym/antonym/word_family/derived_form/related_meaning/register_alternative`). Backend CRUD API exists (see §6.1); no UI yet.
- CRUD API for items, examples, and relations (see §6.1).
- Frontend: tab "codex" in `VocabularyWorkspace.jsx` with search, add form, edit form, example list.

**What is NOT implemented:**
- Synonym/antonym/word-family CRUD from the Codex UI form (relations exist in DB + API, not wired to form).
- Word stress marking UI.
- CSV import.

---

### 3.2. Flashcard Gate ✅ LIVE

**What exists:**
- `flashcards` + `spaced_repetition_states` tables.
- SRS: grade → `interval_days` offset (`again`→0, `hard`→1, `good`→3, `easy`→7). No SM-2 ease factor in active use.
- Vocabulary sub-tab: tap anywhere on card to flip (two-way toggle); 4 grade buttons with `e.stopPropagation()`; no "Reveal"/"Recall" buttons.
- Card dimensions: `width: 100%` (fills main content panel, sidebar excluded) × `min(560px, 70vh)`.
- Collocation sub-tab: topic picker → `CollocationFlashcard` review with same flip UI and familiarity model.
- Familiarity decay: `effective_familiarity()` in `services.py` — one tier per 7 days (`easy` never decays).
- `easy` graduates from active deck (stays visible in browse as yellow neon).
- Re-adding a graduated card resets to `again`.

**Familiarity states:**

| State | Neon color | Counts as "completed" for % |
|---|---|---|
| `new` (not added) | none | No |
| `again` | grey | No |
| `hard` | cyan | Yes |
| `good` | blue | Yes |
| `easy` | gold | Yes (graduated) |

**Completion % rule (Collocation Forge topic boxes):**
`completed_count / item_count` where `completed_count` = flashcards with `effective_familiarity ∈ {hard, good, easy}`.

**Collocation auto-complete quest rule:**
Reviewing 5 **distinct** collocation items in one calendar day triggers `try_autocomplete_collocation_forge()`, which sets `completed=True` on today's quest where `daily_slot_code = "vocab_collocation"`. Reward claim remains manual.

**Card types (actual implemented):**

| Type | Where |
|---|---|
| `meaning_recall` | Vocabulary Flashcard Gate |
| Collocation phrase | Collocation Flashcard sub-tab |

Full multi-type card support (`reverse_recall`, `sentence_gap`, etc.) is **not yet implemented**.

**XP:** No per-review XP. See §2.6 for how Vocabulary XP is computed.

---

### 3.3. Collocation Forge ✅ LIVE

**What exists:**

**Database tables (actual names):**

| Table | Role |
|---|---|
| `collocation_collections` | A Cambridge book unit group (e.g. "Campaign 1–3 Month 3–6") |
| `collocation_sections` | Section within a collection — 10 sections; `section_order`, `title` |
| `collocation_topics` | Topic within a section — 60 topics per collection; `topic_order`, `topic_number` |
| `collocation_items` | Individual collocation entry — 1409 unique items (global dedup within collection) |
| `campaign_collocation_links` | Many-to-many: campaigns ↔ collections |
| `player_collocation_progress` | Legacy progress table (superseded by `collocation_flashcards` for review tracking) |
| `collocation_flashcards` | Per-player/campaign flashcard state: `familiarity`, `familiarity_set_at` |

**Seeding:**
- Source file: `material/vocabularies/month1-6/English_Collocations_campaign1-3_3-6_polished.md`
- Parser: `_Section: X_` → `CollocationSection`; `## N. Title` → `CollocationTopic`
- Global dedup per collection by phrase (cross-topic duplicates skipped; first occurrence wins)
- Volume mount: `./material/vocabularies:/app/material/vocabularies:ro`

**Browser UI (`CollocationForge.jsx`):**
- Layer 1: Section accordion (click to expand, chevron, topic count badge)
- Layer 2: Topic progress box grid (2 columns) — each box shows title, `%`, `done/total`, bottom-up fill animation, neon halo scaling with `--coll-ratio` (0→1), `cursor: pointer`
- Layer 3: Collocation item cards (neon color = `effective_familiarity`), Add/Remove flashcard buttons
- Post-mutation refresh: both item list and topic progress counts update live

**API endpoints (actual):**

```text
GET    /api/collocations/topics                       — all topics with item_count + completed_count
GET    /api/collocations/topics/{id}/items            — items with effective_familiarity + is_added
POST   /api/collocations/{item_id}/flashcard          — add to deck (familiarity_set_at=None)
DELETE /api/collocations/{item_id}/flashcard          — remove from deck
POST   /api/collocations/{item_id}/flashcard/review   — grade (again/hard/good/easy) + autocomplete check
GET    /api/collocations/flashcard/topics             — topics with non-graduated cards (for review picker)
GET    /api/collocations/flashcard/topics/{id}        — cards for a topic (non-graduated only)
```

---

### 3.4. Word Network Tree ⚠️ BACKEND LIVE / UI STUB

**What exists:**
- `vocabulary_topics`, `vocabulary_nodes`, `vocabulary_edges` tables in DB.
- Full backend CRUD API (see §6.3).
- `WordNetworkTree.jsx` component (stub/early implementation — no React Flow).

**What is NOT implemented:**
- React Flow visualization in the frontend.
- Node unlock rules enforced end-to-end.

---

### 3.5. Word Family Evolution ⚠️ SCHEMA ONLY / UI STUB

**What exists:**
- `vocabulary_relations` table with CRUD API (see §6.1).
- `WordFamilyEvolution.jsx` component (stub).

**What is NOT implemented:**
- UI for adding/browsing word families from Codex.
- Dedicated API surface for relation browsing (reuses `/api/vocabulary/relations`).

---

### 3.6. Shadow Duel ⚠️ BACKEND PARTIALLY LIVE / UI STUB

**What exists:**
- `ShadowDuel.jsx` component (stub).
- `GET /api/vocabulary/practice/shadow-duel` — returns question set generated from `vocabulary_relations` + fallback hardcoded pool.
- `POST /api/vocabulary/practice/record-success` — records a correct answer.

**What is NOT implemented:**
- Full scoring flow wired to frontend.
- XP award for shadow duel completion.

---

### 3.7. Echo Chamber ⚠️ BACKEND STUB / UI STUB

**What exists:**
- `EchoChamber.jsx` component (stub).
- `GET /api/vocabulary/practice/echo-chamber` — returns minimal response.

**What is NOT implemented:**
- Pronunciation data, stress-marking gameplay, scoring.

---

### 3.8. Error Dungeon ⚠️ PARTIALLY LIVE

**What exists:**
- `vocabulary_errors` table: `error_type`, `wrong_text`, `corrected_text`, `explanation`, `status` (`active`/`defeated`), `defeated_count`.
- `ErrorDungeon.jsx` component.
- Full CRUD API including defeat endpoint (see §6.4).
- `defeat_vocabulary_error()` service in `services.py`.

**What is NOT implemented:**
- Monster defeat animation / UI flow in `ErrorDungeon.jsx`.
- Correction counter UI (tracking `defeated_count` increments).

---

### 3.9. Vocabulary Boss ⚠️ BACKEND PARTIALLY LIVE / UI THIN

**What exists:**
- `VocabularyBoss.jsx` component.
- `GET /api/vocabulary/boss/status` — returns boss status list (locked/unlocked per boss ID).
- `POST /api/vocabulary/boss/{boss_id}/challenge` — returns `VocabularyBossExam` question set.
- `POST /api/vocabulary/boss/{boss_id}/submit` — accepts `score_pct`, runs `submit_vocabulary_boss_result()`.
- 4 boss IDs supported (1–4).

**What is NOT implemented:**
- Boss requirements computed from real gameplay data (currently stub conditions).
- Full reward + badge unlock flow wired to frontend.

---

### 3.10. Context Hunt ❌ NOT STARTED

Planned future feature. No DB table, no component, no API. Low priority.

---

## 4. Architecture Decisions (Actual)

### 4.1. Auth scope — Account/Player/Campaign, not user_id

The spec originally proposed `user_id` as the root FK on all tables. **Actual implementation** uses a 3-level hierarchy:

```text
Account → Player → Campaign
```

- `accounts` = auth entity (email, JWT)
- `players` = study profile (XP, level, streaks)
- `campaigns` = active study run (all gameplay scoped here)

All vocabulary and collocation data is scoped to `player_id` + `campaign_id`. The `vocabulary_items` and `flashcards` tables use `player_id` as FK (not `user_id`).

### 4.2. Migrations — Alembic, not raw SQL

All schema changes go through Alembic (`backend/alembic/versions/`). Naming: `YYYYMMDD_NN_description.py`. Do **not** write raw `CREATE TABLE` DDL directly.

### 4.3. Spaced repetition — simple familiarity + interval, not SM-2

The original spec proposed SM-2 ease factor. **Actual implementation** uses two parallel tracking mechanisms:

**Vocabulary flashcards** (`spaced_repetition_states`):

| Grade | `interval_days` | `status` |
|---|---|---|
| again | 0 | `reviewing` |
| hard | 1 | `active` |
| good | 3 | `active` |
| easy | 7 | `active` |

**Collocation flashcards** (`collocation_flashcards.familiarity`):

| Grade | Familiarity stored | Decay rule |
|---|---|---|
| again | `again` | no decay (already worst) |
| hard | `hard` | decays to `again` after 7 days |
| good | `good` | decays to `hard` after 7 days |
| easy | `easy` | never decays; graduates from active deck |

`effective_familiarity(stored, set_at, now)` is a pure function in `services.py` — decay is computed on read, never stored back.

### 4.4. Collocation progress — CollocationFlashcard, not PlayerCollocationProgress

`player_collocation_progress` exists in DB but is **superseded** by `collocation_flashcards` for tracking review state. The `completed_count` for topic progress boxes reads from `collocation_flashcards.familiarity`. The legacy table still accumulates writes from the old `/api/collocation-items/{id}/progress` endpoint but is not used for any UI computation.

### 4.5. Frontend routing — view state, not React Router

No `react-router-dom`. Navigation is `currentView` state in `App.jsx`. `VocabularyWorkspace` is mounted when `currentView === 'vocabulary'`. Tabs within the workspace use local state (`activeTab`).

### 4.6. Flashcard flip UX — tap-to-flip, no Reveal/Recall buttons

Original spec proposed "Show Answer" button. **Actual implementation**: click anywhere on the card flips it (toggle both ways). Grade buttons use `e.stopPropagation()`. No "Reveal"/"Recall" button exists. Card width fills full main content panel (sidebar excluded).

### 4.7. Vocabulary XP — recompute model, not per-event transactions

Vocabulary skill XP is not written via `award_skill_xp` on each flashcard review. It is recomputed from aggregate data by `compute_vocabulary_xp()` every time `refresh_progress_state()` is called. See §2.6 for the full formula.

---

## 5. Database: Actual Tables

### 5.1. Vocabulary system tables (live)

```text
vocabulary_items          — word, meanings, pronunciation, source info
vocabulary_examples       — personal example sentences per word
vocabulary_relations      — synonym/antonym/word_family/derived_form links
vocabulary_settings       — per-campaign vocabulary preferences
vocabulary_topics         — topic nodes for Word Network Tree
vocabulary_nodes          — graph nodes (backend CRUD live, UI stub)
vocabulary_edges          — graph edges (backend CRUD live, UI stub)
vocabulary_errors         — Error Dungeon monsters
flashcards                — vocabulary flashcard decks
spaced_repetition_states  — SRS state per flashcard
```

### 5.2. Collocation system tables (live)

```text
collocation_collections      — book/unit groupings
collocation_sections         — 10 sections per collection
collocation_topics           — 60 topics per collection
collocation_items            — 1409 unique collocation entries
campaign_collocation_links   — campaign ↔ collection many-to-many
player_collocation_progress  — legacy (superseded for review tracking)
collocation_flashcards       — per-player/campaign flashcard state
```

---

## 6. API Contracts (Actual Implemented)

### 6.1. Vocabulary Codex + Relations

```text
POST   /api/vocabulary                        — create item
GET    /api/vocabulary                        — list items (player-scoped)
GET    /api/vocabulary/{id}                   — get single item
PUT    /api/vocabulary/{id}                   — update item
DELETE /api/vocabulary/{id}                   — delete item
POST   /api/vocabulary/{id}/examples          — add example sentence
DELETE /api/vocabulary/examples/{id}          — delete example
POST   /api/vocabulary/relations              — create relation (synonym/antonym/word_family/…)
DELETE /api/vocabulary/relations/{id}         — delete relation
```

### 6.2. Vocabulary Flashcard Gate

```text
GET    /api/flashcards                        — list all flashcards
POST   /api/flashcards                        — create flashcard manually
GET    /api/flashcards/due                    — due cards for today's review session
POST   /api/flashcards/{id}/review            — grade a card (again/hard/good/easy)
```

**Note:** These endpoints use the prefix `/api/flashcards/`, NOT `/api/vocabulary/flashcards/`.

### 6.3. Word Network Tree

```text
GET    /api/vocabulary/tree/topics            — list topics
POST   /api/vocabulary/tree/topics            — create topic
GET    /api/vocabulary/tree/{topic_id}        — get tree (nodes + edges) for topic
POST   /api/vocabulary/tree/nodes             — create node
PATCH  /api/vocabulary/tree/nodes/{id}        — update node
POST   /api/vocabulary/tree/edges             — create edge
DELETE /api/vocabulary/tree/edges/{id}        — delete edge
POST   /api/vocabulary/tree/sync-all          — sync all vocabulary items to nodes
```

### 6.4. Error Dungeon

```text
POST   /api/vocabulary/errors                 — log a new error
GET    /api/vocabulary/errors/active          — active monsters
GET    /api/vocabulary/errors                 — all errors
PATCH  /api/vocabulary/errors/{id}            — update error
POST   /api/vocabulary/errors/{id}/defeat     — defeat monster (increments defeated_count, sets status=defeated)
```

### 6.5. Vocabulary Boss

```text
GET    /api/vocabulary/boss/status            — boss list with lock status
POST   /api/vocabulary/boss/{id}/challenge    — start boss exam (returns question set)
POST   /api/vocabulary/boss/{id}/submit       — submit score_pct, trigger result + reward
```

### 6.6. Practice endpoints

```text
GET    /api/vocabulary/practice/collocations       — collocation practice set (legacy)
GET    /api/vocabulary/practice/shadow-duel        — shadow duel question set
GET    /api/vocabulary/practice/word-family        — word family practice set
GET    /api/vocabulary/practice/echo-chamber       — echo chamber practice set
POST   /api/vocabulary/practice/record-success     — record a correct practice answer
```

### 6.7. Collocation Forge + Flashcard

```text
GET    /api/collocations/topics                       — all topics with item_count + completed_count
GET    /api/collocations/topics/{id}/items            — items with effective_familiarity + is_added
POST   /api/collocations/{item_id}/flashcard          — add to deck
DELETE /api/collocations/{item_id}/flashcard          — remove from deck
POST   /api/collocations/{item_id}/flashcard/review   — grade (triggers autocomplete check)
GET    /api/collocations/flashcard/topics             — topics with active cards (for review)
GET    /api/collocations/flashcard/topics/{id}        — cards in a topic for review
```

---

## 7. Frontend: Actual Components

| Component | File | Status |
|---|---|---|
| VocabularyWorkspace (shell + Codex + Flashcard tabs) | `VocabularyWorkspace.jsx` | ✅ Live |
| CollocationForge (browser 2-layer + flashcard sub-tab) | `CollocationForge.jsx` | ✅ Live |
| WordNetworkTree | `WordNetworkTree.jsx` | ⚠️ Stub (backend live) |
| WordFamilyEvolution | `WordFamilyEvolution.jsx` | ⚠️ Stub |
| ShadowDuel | `ShadowDuel.jsx` | ⚠️ Stub (backend partial) |
| EchoChamber | `EchoChamber.jsx` | ⚠️ Stub |
| ErrorDungeon | `ErrorDungeon.jsx` | ⚠️ Partial (defeat API exists, UI incomplete) |
| VocabularyBoss | `VocabularyBoss.jsx` | ⚠️ Partial (challenge/submit API exists, UI thin) |

---

## 8. Daily Quests (Actual Integration)

The quest seed in `seed.py` creates these daily quest types:

| Quest display name | `daily_slot_code` | Completion trigger |
|---|---|---|
| Vocabulary Codex daily | _(manual)_ | Honor system (manual claim) |
| Collocation Forge daily | `vocab_collocation` | **Auto-complete**: 5 distinct collocation reviews in one calendar day |

Quest XP for collocation forge: seeded value in `quest.base_xp` / `quest.xp` (check `seed.py` for exact value). XP flows through the normal quest claim → `award_skill_xp` path.

---

## 9. What Remains to Build

### Priority 1 — Frontend for existing backend

- **Word Network Tree** — wire `/api/vocabulary/tree/*` to React Flow visualization; implement node status transitions in UI.
- **Word Family Evolution** — add UI to browse/add word family relations from Codex.

### Priority 2 — Complete partial features

- **Error Dungeon defeat UI** — wire `POST /api/vocabulary/errors/{id}/defeat`; monster defeat animation; correction counter display.
- **Vocabulary Boss full flow** — boss requirements from real data; reward + badge unlock UI.
- **Shadow Duel scoring** — wire question set to frontend; XP award on completion.

### Priority 3 — New features

- **Reverse flashcard / sentence gap types** — extend flashcard generation to `reverse_recall`, `sentence_gap` card types.
- **Relation CRUD in Codex UI** — synonym/antonym/word family form in the Codex word editor.
- **Context Hunt** — DB table `context_hunt_attempts`, component, API.
- **Echo Chamber gameplay** — pronunciation / stress marking, scoring.

---

## 10. Agent Workflow

### 10.1. Context load order

```text
1. AGENTS.md
2. README.md
3. TASKS.md
4. DECISIONS.md
5. docs/current/CONTEXT_INDEX.md
```

Then load only what the task needs:
- Schema changes → `docs/current/DATABASE_SCHEMA.md` + `docs/current/SCHEMA_SEMANTICS.md`
- Business logic → `docs/current/BUSINESS_RULES.md`
- This spec → `spec/feature/vocabulary_support_skill_spec.md`

### 10.2. Task contract format

Before editing, define:

```text
Goal:
Completion Criteria:
In Scope:
Out of Scope:
Constraints:
Risks:
```

### 10.3. Implementation constraints

- Follow existing repo patterns before introducing new ones.
- All schema changes go through Alembic (`backend/alembic/versions/`).
- Do not use `user_id` as FK — use `player_id` + `campaign_id`.
- Do not introduce React Router, Tailwind, or new CSS frameworks.
- Keep frontend CSS in `frontend/src/styles.css`; use existing CSS variable tokens (`--cyan`, `--line`, `--text`, etc.).
- Keep the app runnable with `docker compose up --build`.
- Do not remove existing features unless explicitly requested.
- Validate with `npm run build` (frontend) and `python -m pytest` (backend) after every meaningful change.

### 10.4. Session close format

```text
- Changed:
- Validated:
- Still open:
- Next session should read:
```

---

## 11. Open Decisions

| # | Decision | Status |
|---|---|---|
| 1 | Should `player_collocation_progress` be removed or kept as legacy? | Open — keep for now, no active writes post-I4 |
| 2 | Should Word Network Tree use React Flow or a simpler SVG/canvas approach? | Open — React Flow was the original proposal; backend ready |
| 3 | Should Context Hunt be a standalone tab or part of Codex? | Open |
| 4 | Should Shadow Duel questions be generated from vocabulary_relations or seeded manually? | Open — backend already uses relation-based generation + fallback pool |
| 5 | Should `compute_vocabulary_xp` eventually be replaced with event-driven XP transactions? | Open — current recompute model is simple but may drift from intent as features grow |
