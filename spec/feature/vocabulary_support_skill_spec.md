# Vocabulary Support Skill System Spec

_For IELTS Quest Dashboard / Solo-Leveling-inspired gamified learning system_

> **Last updated:** 2026-06-10 (session 8n+2 — full code review of all 8 UI components; 6 modules upgraded from stub/partial to LIVE)
>
> **Implementation status:** Phases I1–I4 **complete**. All 9 implemented modules are LIVE. Only Context Hunt remains unstarted. Open gaps are gameplay depth items, not missing modules.

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

| Source idea | Game feature (project name) | Status |
|---|---|---|
| Vocabulary notebook | **Codex Archive** (`vocabulary_items`) | ✅ Live |
| Cover meaning → recall → check | **Flashcard Gate** (tap-to-flip, again/hard/good/easy) | ✅ Live |
| Network / diagram | **Lexical Network Map** (`vocabulary_topics/nodes/edges`, React Flow) | ✅ Live |
| Collocations | **Collocation Forge** (`collocation_*` tables, browser + flashcard) | ✅ Live |
| Word family | **Word Family Evolution** (`vocabulary_relations`, React Flow + quiz) | ✅ Live |
| Synonym / antonym | **Shadow Duel** (timed MCQ, 3 lives, streak) | ✅ Live |
| Pronunciation / stress | **Echo Chamber** (syllable stress + silent letter hunt, TTS) | ✅ Live |
| Typical errors | **Error Dungeon** (monster HP, correction battle) | ✅ Live |
| Checkpoint test | **Lexical Checkpoint Boss** (4 bosses, exam + submit flow) | ✅ Live |
| Guess meaning from context | **Context Hunt** | ❌ Not started |

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
├── Lexical Network Map        — WordNetworkTree.jsx (React Flow, drag/connect, node drawer)
├── Word Family Evolution      — WordFamilyEvolution.jsx (React Flow + inline quiz)
├── Shadow Duel                — ShadowDuel.jsx (timed MCQ, 3 lives, timer)
├── Echo Chamber               — EchoChamber.jsx (syllable stress + silent letter, TTS)
├── Error Dungeon              — ErrorDungeon.jsx (monster HP, correction battle)
└── Lexical Checkpoint Boss    — VocabularyBoss.jsx (4 bosses, exam + submit)
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
- Layer 2: Topic progress box grid (2 columns) — each box shows title, `%`, `done/total`, bottom-up fill animation, neon halo scaling with `--coll-ratio` (0→1)
- Layer 3: Collocation item cards (neon color = `effective_familiarity`), Add/Remove flashcard buttons
- Post-mutation refresh: both item list and topic progress counts update live

**Topic box neon system (`.coll-topic-box`):**

Each topic box carries two CSS custom properties set inline by `TopicProgressBox`:

| Property | Value | Purpose |
|---|---|---|
| `--coll-ratio` | `completed_count / item_count` (0.0 → 1.0) | Scales neon intensity |
| `--coll-pct` | `"${pct}%"` string | Drives the bottom-up fill span width |

The neon border and glow are computed entirely in CSS via `calc()` — no JavaScript animation:

```css
/* Border opacity: 0.10 at 0% → 0.55 at 100% */
border: 1px solid rgba(122,240,221, calc(0.10 + 0.45 * var(--coll-ratio, 0)));

/* Inner glow: blur 8px→26px, opacity 0.12→0.57 */
/* Outer glow: blur 16px→56px, opacity 0.05→0.30 */
box-shadow:
  0 0 calc(8px  + 18px * var(--coll-ratio, 0)) rgba(122,240,221, calc(0.12 + 0.45 * var(--coll-ratio, 0))),
  0 0 calc(16px + 40px * var(--coll-ratio, 0)) rgba(122,240,221, calc(0.05 + 0.25 * var(--coll-ratio, 0)));
```

State overrides:

| State | CSS class | Border | Box-shadow |
|---|---|---|---|
| Default (0–100%) | — | scales with `--coll-ratio` | scales with `--coll-ratio` |
| Hover | `:hover` | `rgba(122,240,221,0.55)` fixed | inherits ratio glow + translateY(-1px) |
| Active/selected | `.is-active` | `var(--cyan)` full | 14px + 34px + 64px fixed cyan glow |

The fill span (`.coll-topic-box__fill`) is absolutely positioned, bottom-anchored, height = `--coll-pct`, background gradient cyan→blue — provides the liquid fill visual separate from the neon border.

**Data model — `CollocationItem` fields (actual columns):**

| Field | Type | Notes |
|---|---|---|
| `collocation` | `String(255)` | The phrase (e.g. "make a decision") |
| `pronunciation_us` | `String(255)` nullable | IPA for US pronunciation |
| `meaning_vi` | `Text` nullable | Vietnamese meaning |
| `example_en` | `Text` nullable | English example sentence |
| `example_vi` | `Text` nullable | Vietnamese translation of example |
| `collocation_type` | `String(100)` nullable | Grammatical pattern (e.g. "verb + noun") |
| `item_order` | `Integer` | Order within topic |

**Flashcard state — `CollocationFlashcard` fields:**

| Field | Type | Notes |
|---|---|---|
| `player_id` | FK → `players` | Scoped to player |
| `campaign_id` | FK → `campaigns` | Scoped to campaign |
| `collocation_item_id` | FK → `collocation_items` | Unique per player+campaign+item |
| `familiarity` | `String(10)` | `"again"` / `"hard"` / `"good"` / `"easy"` |
| `familiarity_set_at` | `DateTime` nullable | `None` until first review; set on each grade |

**Add/remove flashcard rules:**
- Add: creates row with `familiarity = "again"`, `familiarity_set_at = None`. Idempotent — if already exists, no-op (unless `easy` → resets to `"again"`).
- Re-add graduated (`easy`) card: resets `familiarity = "again"`, `familiarity_set_at = None`.
- Remove: hard-deletes the `CollocationFlashcard` row; item remains browsable in Forge.
- Guard: `familiarity == "easy"` items show no "Remove" button in UI — must re-add to reset.

**Completion % computation (backend, not frontend):**

`GET /api/collocations/topics` applies `effective_familiarity()` lazy decay per row on read:
```python
completed_count = count of rows where effective_familiarity(fam, set_at, now) in ("hard", "good", "easy")
```
This means a card that decayed from `good` back to `again` no longer counts toward `%` — the % can go *down* without any explicit player action.

**Collocation flashcard review flow (card arena in Flashcard Gate → Collocation sub-tab):**

1. Player picks a topic from topic picker (shows topics with ≥1 non-graduated card).
2. Cards loaded: `GET /api/collocations/flashcard/topics/{id}` — only non-graduated (`familiarity != "easy"`) cards, effective decay applied.
3. Flip card (tap anywhere) → see `collocation`, pronunciation, `collocation_type` on front; `meaning_vi`, `example_en`, `example_vi` on back.
4. Grade button → `POST /api/collocations/{item_id}/flashcard/review` with `{ result: "again"|"hard"|"good"|"easy" }`.
5. Backend sets `familiarity = result`, `familiarity_set_at = utcnow()`, then calls `try_autocomplete_collocation_forge()`.
6. If 5 distinct items reviewed today → quest `daily_slot_code = "vocab_collocation"` auto-completed.
7. Frontend advances to next card. After last card → "SESSION COMPLETE" screen.

**API endpoints (actual):**

```text
GET    /api/collocations/topics                       — all topics for campaign, with item_count + completed_count (decay-aware)
GET    /api/collocations/topics/{id}/items            — items in topic, with effective_familiarity + is_added
POST   /api/collocations/{item_id}/flashcard          — add to deck (familiarity=again, familiarity_set_at=None)
DELETE /api/collocations/{item_id}/flashcard          — remove from deck (hard-delete row)
POST   /api/collocations/{item_id}/flashcard/review   — grade (again/hard/good/easy), set familiarity_set_at, trigger autocomplete
GET    /api/collocations/flashcard/topics             — topics with ≥1 non-graduated card (for review picker)
GET    /api/collocations/flashcard/topics/{id}        — non-graduated cards in topic, effective decay applied
```

**Current browse terminology vs UI label:** the code hierarchy is `Collection → Section → Topic → Item`. In the sidebar, the accordion buttons (e.g. "Work and study") are **Sections** (`coll-section-btn`); the neon `--coll-ratio` boxes inside them are **Topics** (`TopicProgressBox`). When the user says "topic Work and Study", they mean the **Section** accordion row.

#### 3.3.x. Planned additions to Collocation Forge 🔵 PLANNED

> **Status:** Specified, not yet built. Two changes bring Collocation Forge to parity with the planned Vocabulary Library (§3.11).

**A. Add a Level (difficulty band) layer above Collection.**

- New top layer: **Level** (bí kíp / difficulty band), same concept as Vocabulary Library §3.11.1.
- The current seed (`Campaign 1–3 Month 3–6`, collection) is assigned to Level **Intermediate**.
- When the user opens Collocation Forge, the entry screen shows Level blocks first — a book/manual ("bí kíp võ công") card with a **horizontal progress bar** at the bottom (Level% = weighted completed items / total items), identical styling to Vocabulary Library §3.11.7.
- Clicking a Level drills into its Collections/Sections as today.
- New hierarchy: `Level → Collection → Section → Topic → Item`.

**B. Add neon progress wrapper to the Section accordion row.**

- Today the Section accordion button (`.coll-section-btn`, e.g. "Work and study") shows only title + topic-count badge — **no % and no neon**.
- Add a completion % and neon halo to the Section row, reusing the `--coll-ratio` neon system (§3.3 topic-box neon).
- Section% = weighted `completed_items / total_items` across all its topics (decay-aware, computed backend-side like topic %).
- The existing Topic boxes inside keep their current neon — this only adds the missing wrapper at the Section level.

**Completion % is weighted at every level** (completed items / total items counted at the Item leaf), consistent with §3.11.6 — never an average of child percentages.

---

### 3.4. Lexical Network Map ✅ LIVE

**What exists:**
- `vocabulary_topics`, `vocabulary_nodes`, `vocabulary_edges` tables in DB.
- Full backend CRUD API (see §6.3).
- `WordNetworkTree.jsx` — React Flow canvas with `CustomVocabNode` (status-based neon glow), `MiniMap`, `Controls`.
- Create/select topic visual maps from sidebar.
- Add Codex words to map as nodes; drag to reposition (position persisted via `PATCH /api/vocabulary/tree/nodes/{id}`).
- Draw edge between nodes via React Flow connect handle → `POST /api/vocabulary/tree/edges`.
- Delete edge via node drawer.
- Click node → drawer shows IPA, word stress, meanings, examples, collocations.
- `POST /api/vocabulary/tree/sync-all` syncs mastery states from flashcard data.

**Node status values:** `locked` / `discovered` / `activated` / `stabilized` / `mastered` / `awakened` (color-coded neon).

**What is NOT yet implemented:**
- Automatic node status transitions driven by backend mastery rules (status defaults to `discovered` on create; no enforce from flashcard mastery yet).

---

### 3.5. Word Family Evolution ✅ LIVE

**What exists:**
- `vocabulary_relations` table: `source_word_id`, `target_word_id`, `target_text`, `relation_type`.
- Backend API `GET /api/vocabulary/practice/word-family` — returns family groups with nodes + edges.
- `WordFamilyEvolution.jsx` — React Flow canvas with `CustomFamilyNode` (rank-based neon glow F→S).
- Family selector dropdown; root word at top, derived forms spread below.
- Inline quiz: sentence-gap MCQ (hardcoded for 3 seed families; dynamic "select derived form" for DB families).
- Correct answer → `POST /api/vocabulary/practice/record-success` with `xp_gained: 10`; `onXPUpdate` callback.

**What is NOT yet implemented:**
- UI to add `word_family` relation directly from the Codex word editor form.

---

### 3.6. Shadow Duel ✅ LIVE

**What exists:**
- `ShadowDuel.jsx` — full timed MCQ game loop.
- Questions from `GET /api/vocabulary/practice/shadow-duel` (relation-based + hardcoded fallback pool).
- 3 question types: `synonym`, `antonym`, `register` (informal → academic).
- 10-second countdown timer per question; timeout = wrong answer.
- 3 lives; game ends on 0 lives or last question.
- Score, streak, best streak tracking.
- End-game XP: synonym/antonym correct +2, register correct +3, best streak ≥10 +20.
- `POST /api/vocabulary/practice/record-success` on game end.

---

### 3.7. Echo Chamber ✅ LIVE

**What exists:**
- `EchoChamber.jsx` — 2-stage pronunciation gameplay.
- Questions from `GET /api/vocabulary/practice/echo-chamber`.
- Stage 1 — Stressed Syllable: click the syllable with primary stress from a split syllables array.
- Stage 2 — Silent Letter Hunt: click each character in the word that is a silent letter (only triggered if word has `silent_letters`).
- `window.speechSynthesis` TTS — auto-plays word on load and on "Listen" button.
- 3 lives, streak, best streak.
- End-game XP: word with silent letters +6, without +3, best streak ≥10 +20.
- `POST /api/vocabulary/practice/record-success` on game end.

**Dependency:** requires words seeded with `syllables`, `stressed_index`, and optionally `silent_letters` in the backend echo-chamber response.

---

### 3.8. Error Dungeon ✅ LIVE

**What exists:**
- `vocabulary_errors` table: `error_type`, `wrong_text`, `corrected_text`, `explanation`, `status` (`active`/`defeated`), `defeated_count`.
- Full CRUD API including defeat endpoint (see §6.4).
- `ErrorDungeon.jsx` — monster lobby grid + battle arena.
- Monster cards: HP bar (`3 - defeated_count / 3`), type-based icon/name/description.
- Battle: player types the corrected text → exact-match compare → `POST /api/vocabulary/errors/{id}/defeat`.
- Feedback: "HP reduced (N/3 attempts)" or "fully defeated and banished".
- 6 monster types: `wrong_collocation`, `wrong_meaning`, `wrong_register`, `wrong_word_form`, `wrong_preposition`, `wrong_grammar_pattern`.

---

### 3.9. Lexical Checkpoint Boss ✅ LIVE

**What exists:**
- `VocabularyBoss.jsx` — boss lobby + exam arena.
- `GET /api/vocabulary/boss/status` — returns 4 bosses with `id`, `title`, `stage`, `goal`, `status` (locked/ready/cleared), `requirements` (met/unmet with current/target values), `reward_xp`.
- `POST /api/vocabulary/boss/{id}/challenge` — returns question set.
- Exam: multiple-choice per question, progress indicator, "Flee Battle" escape.
- Submit: calculates `score_pct` client-side → `POST /api/vocabulary/boss/{id}/submit` → shows pass/fail, score, reward XP.
- Pass threshold: 75%.

**What is NOT yet implemented:**
- Boss requirements populated from real gameplay data (backend `get_vocabulary_boss_status` currently returns stub/placeholder conditions).

---

### 3.10. Context Hunt ❌ NOT STARTED

Planned future feature. No DB table, no component, no API. Low priority.

---

### 3.11. Vocabulary Library (Codex Archive reorganization) 🔵 PLANNED

> **Status:** Specified, not yet built. This is the next planned change — reorganize Codex Archive into a multi-level curriculum browser that mirrors the Collocation Forge pattern. Confirmed business rules below.

**Motivation:** Today the Codex Archive only holds user-entered words (free-form CRUD). We are adding a **curriculum-seeded vocabulary library** sourced from leveled textbooks, browsable through a fixed hierarchy and reviewable with the same flashcard/familiarity engine as Collocation Forge.

#### 3.11.1. The 5-level hierarchy

Vocabulary content is organized into **5 nested levels** (one more level than Collocation's 3):

```text
Level (difficulty band)          e.g. Elementary, pre-intermediate_intermediate, Upper Intermediate, Advanced
└── Topic                        e.g. "The World Around Us", "People"
    └── Unit                     e.g. "Unit 5: Country, nationality and language"
        └── Section              e.g. "A. Who speaks what where?"
            └── Word (vocab item)  ← vocabulary entries live ONLY at the Section leaf
```

- **Level** = difficulty band. When the user opens Codex Archive, they first see the list of vocabulary sets ordered by ascending difficulty: `Elementary → pre-intermediate_intermediate → Upper Intermediate → Advanced`.
- Clicking a Level reveals its Topics; clicking a Topic reveals its Units; clicking a Unit reveals its Sections; clicking a Section reveals the vocabulary words.
- **Words are displayed only at the deepest Section node** — never at Level/Topic/Unit nodes.
- Example navigation path: `pre-intermediate_intermediate` → Topic `The World Around Us` → Unit `Country, nationality and language` → Section `A. Who speaks what where?` → word list.

(Compare: Collocation Forge is `Collection → Section → Topic → Item`, 3 browse levels with items at the leaf. Vocabulary is `Level → Topic → Unit → Section → Word`, 4 browse levels with words at the leaf.)

#### 3.11.2. Seed source format

Source file (first set): `material/vocabularies/pre-intermediate_intermediate/vocab.md`.

Markdown parsing rules (derived from the actual file):

| Markdown pattern | Maps to |
|---|---|
| `# Topic: <name>` or `# Vocabulary Topic: <name>` | Topic |
| `## Unit N: <name>` | Unit |
| `### <Letter>. <name>` (e.g. `### A. Who speaks what where?`) | Section |
| Pipe table with header `collocation / từ vựng \| từ loại \| phiên âm (US) \| nghĩa \| ví dụ \| nghĩa tiếng việt của ví dụ` | One vocabulary Word per row |

The Level is **not** in the file body — it is inferred from the folder name (`pre-intermediate_intermediate`), assigned at seed time.

**Word row → fields:**

| Table column (the standard table) | Source |
|---|---|
| `word` / collocation phrase | `collocation / từ vựng` |
| `part_of_speech` | `từ loại` (e.g. noun, verb, adjective, noun phrase, phrasal verb) |
| `pronunciation` (US IPA) | `phiên âm (US)` |
| `meaning_vi` | `nghĩa` |
| `example_en` | `ví dụ` |
| `example_vi` | `nghĩa tiếng việt của ví dụ` |

#### 3.11.3. Special-table handling decision

Some sections (e.g. `A. Who speaks what where?`) contain a **second, non-standard table** with columns `Country / Nationality / Language` (3 paired phonetic columns). **Decision: skip these special tables.** Only parse tables that match the standard 6-column shape above. The Country/Nationality/Language reference table is ignored at seed time.

#### 3.11.4. Seed vs user-CRUD separation

**Decision: curriculum-seeded vocabulary and user-entered words are separate sources** — mirroring how Collocation Forge keeps the seeded `collocation_items` browse catalog separate from review state.

- The seeded library is a **fixed browse catalog** (read-only reference content shared across players, like `collocation_collections`).
- User browses the library and **adds words to their flashcard deck** (per-player/campaign review state, like `collocation_flashcards`).
- Free-form user-entered words (existing Codex CRUD) remain a **separate area** — seed content does NOT pour into each user's `vocabulary_items`. This keeps curriculum updatable centrally without touching user data.

#### 3.11.5. Learning mechanics — identical to Collocation Forge

**Decision: reuse the Collocation Forge engine wholesale.** The vocabulary library gets the exact same review mechanics:

- Per-word flashcard with `familiarity` ∈ {`again`, `hard`, `good`, `easy`}.
- `effective_familiarity()` lazy decay — 1 tier per 7 days, `easy` never decays, `easy` graduates.
- A word "counts as 1 point" toward completion when its **effective** familiarity ∈ {hard, good, easy} — i.e. any state other than `again` and not-yet-added.
- Neon progress boxes with `--coll-ratio`-style scaling (see §3.3 neon system).
- Add/remove flashcard, re-add graduated resets to `again`.
- Same tap-to-flip card UI.

**Implication for new schema:** new tables paralleling the Collocation set will be needed (e.g. `vocab_levels`, `vocab_topics`, `vocab_units`, `vocab_sections`, `vocab_library_items`, `vocab_library_flashcards`) — final names TBD at planning time. These are distinct from the existing `vocabulary_*` tables (which back the user-CRUD Codex and the network/family/error features). See Open Decision #6.

#### 3.11.6. Completion % shown at every level (weighted count, not average)

Every node at every level (Level, Topic, Unit, Section) displays its own completion %. The % is **always computed by counting words at the leaf** — never by averaging child percentages.

**Decision: weighted (total completed words / total words), consistent with Collocation Forge.**

For any node, regardless of depth:
```
node_completion_% = (count of words under node with effective_familiarity ∈ {hard, good, easy})
                  / (total count of words under node)
```

- **Section%** = completed words in section / total words in section.
- **Unit%** = completed words across ALL its sections / total words across ALL its sections.
- **Topic%** = completed words across ALL its units / total words across ALL its units.
- **Level%** = completed words across ALL its topics / total words across ALL its topics.

This is weighted, not a simple average of children — a section with 8 words influences its Unit% four times more than a section with 2 words. Example: Section A = 2/2 (100%) + Section B = 2/8 (25%) → Unit% = 4/10 = **40%** (not the 62.5% a naive average of percentages would give).

**Implementation note:** backend computes all level %s from a single decay-aware count over leaf flashcards (same approach as `GET /api/collocations/topics`), aggregated by the hierarchy — there is no stored "% per node".

#### 3.11.7. Difficulty-band selection UI (Level blocks)

When the user opens Codex Archive, the entry screen shows the difficulty bands as a row/grid of **blocks**, ordered by ascending difficulty:

```text
Elementary  →  pre-intermediate_intermediate  →  Upper Intermediate  →  Advanced
```

Each Level block is a "martial-arts manual" (bí kíp võ công) card:

| Element | Spec |
|---|---|
| Icon | A book/tome icon (📖 / 📕) — themed as a secret-technique manual |
| Title | Level name |
| Progress bar | A **horizontal progress bar** at the bottom of the block, filling left→right to Level% (weighted per §3.11.6). This is a flat horizontal bar — NOT the vertical bottom-up neon fill used by Collocation topic boxes. |
| State | Locked/dim if the level has no linked content yet; active if seeded |

Clicking a Level block drills into its Topics.

#### 3.11.8. Drill-level UI (Topic / Unit / Section) — reuse Collocation neon boxes

Below the Level blocks, the Topic → Unit → Section drill levels reuse the **Collocation Forge neon box pattern** (§3.3 neon system), NOT the horizontal bar:

- Each Topic / Unit / Section is a neon box with vertical bottom-up fill (`--coll-pct`) and neon halo scaling with `--coll-ratio`.
- Each box shows its title, weighted completion %, and `done/total` word count.
- Clicking drills one level deeper; the Section leaf reveals the word list (with add-to-flashcard + tap-to-flip review).

**Summary of the two visual styles:**

| Level | Visual |
|---|---|
| Level (difficulty band) | Book/manual block + **horizontal progress bar** |
| Topic / Unit / Section | Collocation-style **neon box, vertical bottom-up fill** |

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

| Game name | File | Status |
|---|---|---|
| Codex Archive + Flashcard Gate (shell) | `VocabularyWorkspace.jsx` | ✅ Live |
| Collocation Forge (browser + flashcard) | `CollocationForge.jsx` | ✅ Live |
| Lexical Network Map | `WordNetworkTree.jsx` | ✅ Live (React Flow, drag/connect) |
| Word Family Evolution | `WordFamilyEvolution.jsx` | ✅ Live (React Flow + quiz) |
| Shadow Duel | `ShadowDuel.jsx` | ✅ Live (timed MCQ, 3 lives) |
| Echo Chamber | `EchoChamber.jsx` | ✅ Live (stress + silent letters, TTS) |
| Error Dungeon | `ErrorDungeon.jsx` | ✅ Live (monster HP, correction battle) |
| Lexical Checkpoint Boss | `VocabularyBoss.jsx` | ✅ Live (exam + submit, 4 bosses) |
| Context Hunt | _(not started)_ | ❌ Not started |

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

### Priority 1 — Gameplay depth for live features

- **Lexical Network Map — node auto-status transitions** — backend enforce: node status progresses `discovered → activated → stabilized → mastered → awakened` based on flashcard mastery level, not just manual `sync-all`.
- **Lexical Checkpoint Boss — real requirements** — `get_vocabulary_boss_status()` in `services.py` returns stub/placeholder requirements; replace with real data computed from `vocabulary_items`, `collocation_flashcards`, `vocabulary_errors`, etc.
- **Word Family Evolution — Codex relation editor** — add `word_family` relation directly from the Codex word form UI; currently must go through the API directly.

### Priority 2 — New features

- **Reverse flashcard / sentence gap types** — extend flashcard generation to support `reverse_recall`, `sentence_gap` card types.
- **Context Hunt** — DB table `context_hunt_attempts`, component, API. No prior work exists.

### Priority 3 — Polish

- **Shadow Duel question depth** — hardcoded fallback pool is small; grow `vocabulary_relations` data to reduce fallback reliance.
- **Echo Chamber data coverage** — words need `syllables`, `stressed_index`, and `silent_letters` fields populated in the backend response; coverage depends on seeded/entered data quality.

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
| 2 | Should Lexical Network Map node status transitions be auto-driven by flashcard mastery, or remain manual via sync-all? | Open — current: manual sync-all only |
| 3 | Should Context Hunt be a standalone tab or part of Codex? | Open |
| 4 | Should Lexical Checkpoint Boss requirements be computed live or cached/snapshotted? | Open — currently stub; real data needed |
| 5 | Should `compute_vocabulary_xp` eventually be replaced with event-driven XP transactions? | Open — current recompute model is simple but may drift from intent as features grow |
| 6 | New table names for the Vocabulary Library (§3.11) — reuse/extend existing `vocabulary_topics` or create a fresh `vocab_*` table family? | Open — recommend fresh family to avoid colliding with Word Network Tree's `vocabulary_topics`; decide at planning |
| 7 | Does the seeded Vocabulary Library award XP on review (like the recompute model), or stay XP-neutral like collocation review? | Open — collocation review awards no direct XP; library should likely match |
