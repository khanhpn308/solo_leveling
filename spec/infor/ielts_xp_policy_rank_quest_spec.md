# XP Policy Specification: Skill XP, Level Curve, Rank F–S

**Project:** IELTS Quest Dashboard
**Purpose:** Define the balanced XP, level-curve, and rank model for the 18-month IELTS gamified roadmap.
**Scope:** Skill XP, Skill Level/Rank, Player Level/Rank (derived), Daily Quests, Weekly Missions, Main Quests, Boss XP routing.
**Status:** CANONICAL. This file is the source of truth for all XP / level / rank values. Owner-approved 2026-06-09.

> **Reading order for implementers:** read this file first, then `quest.md` (lifecycle), then verify against `backend/app/services.py` + `backend/app/seed.py`.

---

## 1. Design Goal & Two-Layer Model

The XP system must be slow enough to keep the 18-month roadmap meaningful, but fast enough for the learner to feel weekly progress.

Two progression layers:

```text
Skill XP   = real learning progress per skill (the only thing that accrues XP)
Player XP  = DERIVED — the average of the 5 core skill XP values (no direct accrual)
```

### 1.1 Skill taxonomy (FINAL)

There are **5 SKILL MATRIX** entries. Only these have an independent rank and feed the player average:

```text
Listening
Reading
Writing
Speaking
Vocabulary
```

There are **2 SUPPORT SOURCES**. They have NO independent rank and do NOT feed the player average. They buff a matrix skill:

```text
Collocation  → buffs Vocabulary
Grammar      → buffs Writing
```

> The DB still seeds 7 `skills` rows (Listening, Reading, Writing, Speaking, Vocabulary, Collocation, Grammar) for categorisation, but only the 5 matrix skills carry a meaningful rank shown in the UI. Collocation/Grammar XP is *routed into* their buff target rather than tracked as a standalone rank.

> **UI presentation of support sources (FINAL — owner 2026-06-09):** the skill matrix renders exactly 5 tiles. Grammar/Collocation are **not** standalone tiles and have **no F–S rank/level**; they appear as a buff line inside their parent matrix card (Grammar → Writing card `+N XP from Grammar`; Collocation → Vocabulary card `+N XP from Collocation`). `/summary` carries a `support_breakdown:[{source,xp}]` per affected matrix skill so the UI can render the buff line without double-counting (the XP is already inside the parent skill `xp`). See `player_level.md` §2.A.

### 1.2 Player XP / Level / Rank (DERIVED — no direct accrual)

**The player never accrues XP directly.** Removed entirely: quest→player, mission→player, boss→player, check-in→player, vocab→player.

```text
player_xp    = round( mean( skill_xp[Listening, Reading, Writing, Speaking, Vocabulary] ) )
player_level = level_from_xp(player_xp)        # same curve as skill level
player_rank  = rank_from_level(player_level)   # 10 levels per rank
```

**Player RANK is the only player progression value shown on the UI.** Player level/XP are internal inputs to the rank; they are not surfaced as primary stats.

---

## 2. Level Curve & Rank Mapping (FINAL)

### 2.1 Level curve formula

```text
xp_to_reach(L) = round( 19 * (L^1.6 - 1) )     for L in 1..60
level_from_xp(xp) = highest L where xp_to_reach(L) <= xp   (clamped 1..60)
```

Properties: L1 = 0 XP; the per-level XP cost rises monotonically (≈39 XP for L2, ≈353 XP for L60); 60 levels total.

### 2.2 Rank mapping — 10 levels per rank

```text
rank_from_level(L):
    F if  1 <= L <= 10
    E if 11 <= L <= 20
    D if 21 <= L <= 30
    C if 31 <= L <= 40
    B if 41 <= L <= 50
    A if 51 <= L <= 59
    S if       L == 60
```

### 2.3 Rank threshold table (derived from the curve — DO NOT hand-edit; regenerate from §2.1)

| Rank | First Level | Min XP | Approx. week reached* |
|---|---:|---:|---:|
| F | L1  | 0      | week 0  |
| E | L11 | 862    | ~week 5  |
| D | L21 | 2,460  | ~week 14 |
| C | L31 | 4,604  | ~week 26 |
| B | L41 | 7,212  | ~week 41 |
| A | L51 | 10,234 | ~week 58 |
| S | L60 | 13,279 | ~week 75 |

\* Assumes ~177 skill XP/week (daily + weekly mission + full-XP main quest) and high consistency. S ≈ end of the 18-month (78-week) roadmap, as intended.

### 2.4 Full level→XP table

The full 60-row table is generated from §2.1. Seed it into `rank_xp_thresholds` (rank rows) and compute per-level XP in code. Representative values:

| L | XP | L | XP | L | XP | L | XP |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 16 | 1,586 | 31 | 4,604 | 46 | 8,674 |
| 2 | 39 | 17 | 1,749 | 32 | 4,845 | 47 | 8,978 |
| 3 | 91 | 18 | 1,918 | 33 | 5,090 | 48 | 9,286 |
| 5 | 231 | 20 | 2,274 | 35 | 5,595 | 50 | 9,915 |
| 10 | 737 | 21 | 2,460 | 41 | 7,212 | 51 | 10,234 |
| 11 | 862 | 30 | 4,368 | 45 | 8,374 | 60 | 13,279 |

---

## 3. Rank vs Confirmed Rank

```text
rank           = calculated rank from current skill XP (auto)
confirmed_rank = officially approved rank
```

`confirmed_rank` is raised by:
- **Certificate / manual score** → creates a rank suggestion → Apply → updates `confirmed_rank` directly (no boss).
- **Rank Boss pass** (for boss-gated skills only) → `confirmed_rank` updates after a ≥80% pass.

`rank` may sit above `confirmed_rank` (XP earned but not yet confirmed). XP must never drop `state.xp` below the `confirmed_rank` minimum.

### 3.1 Boss-gating per skill (FINAL)

| Skill | Boss-gated? | Promotion mechanism |
|---|---|---|
| Vocabulary | YES | Rank Boss exam (≥80%) |
| Reading | YES | Rank Boss exam |
| Listening | YES | Rank Boss exam |
| Grammar* | YES (MVP boss list) | Rank Boss exam |
| Collocation* | YES (MVP boss list) | Rank Boss exam |
| **Writing** | **NO** | `confirmed_rank = rank` directly from XP. No boss, no freeze. |
| **Speaking** | **NO** | `confirmed_rank = rank` directly from XP. No boss, no freeze. |

\* Grammar/Collocation keep their MVP Rank Boss exams for self-assessment, but since they are support sources they do not surface a matrix rank; treat their boss as optional/backlog UX.

**Writing/Speaking rule:** when `boss_gated = False`, `recompute_skill_progress` sets `confirmed_rank = rank`, `promotion_status = "none"`, never creates a `pending_rank`. This removes the "Boss required but no boss exists" dead-end.

> Implementation note: store `boss_gated` as a column on `skills` (preferred, avoids hard-code) or as a constant set keyed by skill name.

### 3.2 Rank Boss rules (boss-gated skills)

```text
XP reaches next rank threshold
  → pending_rank = next rank ONLY (no multi-rank jump)
  → promotion_status = boss_required
  → Rank Boss unlocks
  → pass score >= 80%
  → confirmed_rank updates only after pass
After clearing F->E, evaluate E->D later if XP still qualifies.
Retry: max 2 attempts/day. "day" = HOST/SERVER local timezone.
Time limit: 30 minutes per MVP Rank Boss exam.
```

---

## 4. XP Routing Rules (FINAL)

| Source | Routes to |
|---|---|
| Daily Quest (per quest) | the quest's own matrix skill |
| Daily Grammar quests (Review +5, Exercise +7) | **Writing** |
| Daily Collocation Forge (+5) | **Vocabulary** |
| Weekly Mission with target skill | that skill (Grammar mission → Writing; Collocation → Vocabulary) |
| Main Quest | **FULL XP to EVERY skill in the session** (see §6); Grammar component → Writing |
| Skill Boss | its skill |
| Phase / Overall Boss | distributed to the related skills (NOT the player) |
| Weekly Check-in | **streak only — NO XP** (shield is a separate countdown stat) |
| **Player** | **nothing — player_xp is the average of the 5 matrix skills** |

---

## 5. Daily Quest Structure

9 Daily Quests/day across 9 distinct slots (see `daily_quest.md` for the 9 `daily_slot_code` values):

```text
3 Vocabulary quests : Flashcard Gate, Codex Entry, Collocation Forge
4 Core skill quests : Listening, Reading, Writing, Speaking
2 Grammar quests    : Grammar Review, Grammar Exercise
```

### 5.1 Daily Quest XP

| Slot code | Quest | Skill XP | Routes to |
|---|---|---:|---|
| `vocab_flashcard` | Flashcard Gate | 4 | Vocabulary |
| `vocab_codex` | Codex Entry | 5 | Vocabulary |
| `vocab_collocation` | Collocation Forge | 5 | Vocabulary |
| `listening` | Listening Daily | 10 | Listening |
| `reading` | Reading Daily | 10 | Reading |
| `writing` | Writing Daily | 12 | Writing |
| `speaking` | Speaking Daily | 12 | Speaking |
| `grammar_review` | Grammar Review | 5 | Writing |
| `grammar_exercise` | Grammar Exercise | 7 | Writing |

Per-day routed totals: Vocabulary 14, Listening 10, Reading 10, Writing 12+12(grammar)=**24**, Speaking 12.

---

## 6. Main Quest XP Policy (FINAL — full-XP, tier by skill)

312 Main Quests = 78 weeks × 4 fixed sessions. Skill columns from `material/material.md`:

| Session | Skill column (material.md) | Matrix skills credited | Tier | XP |
|---|---|---|---|---:|
| S1 | Listening + Speaking | Listening, Speaking | standard | 35 |
| S2 | Reading + Vocabulary + Long sentence | Reading, Vocabulary | standard | 35 |
| S3 | Writing + Grammar | Writing (Grammar→Writing) | heavy_output | 45 |
| S4 | Review + Mini test + Error log | dominant skill of the week / mock | review 25 or mock 60 |

**Full-XP rule:** each session awards its full tier XP to **every** matrix skill it covers. Example: S2 (35 XP) credits Reading +35 **and** Vocabulary +35 (not split).

**Tier source:** the session's skill column (Writing/Speaking-heavy → 45; Listening/Reading → 35; Review/Error → 25; sectional/mock test → 60).

**Main Quest → Player:** none. The player rank rises only because the per-skill averages rise.

---

## 7. Weekly Mission XP Policy

| Mission | Completion rule | XP destination | XP |
|---|---|---|---:|
| Vocabulary Weekly | ≥15/21 vocab daily quests | Vocabulary | 55 |
| Listening Weekly | ≥5/7 listening quests | Listening | 40 |
| Reading Weekly | ≥5/7 reading quests | Reading | 40 |
| Writing Weekly | ≥4/7 writing quests | Writing | 45 |
| Speaking Weekly | ≥4/7 speaking quests | Speaking | 45 |
| Grammar Weekly | ≥10/14 grammar quests | **Writing** | 45 |
| Check-in Weekly | check-in ≥5 days/week | **streak only — NO XP** | — |

---

## 8. Vocabulary XP & Anti-Farm Cap (FINAL)

Vocabulary XP (`compute_vocabulary_xp`) feeds the Vocabulary matrix skill and aggregates:

- Per word created: +2; +2 meaning_en; +2 meaning_vi; +2 part_of_speech; +3 pronunciation_ipa; +mastery_score (capped +50/word).
- **NEW data-entry cap:** the sum of *data-entry* XP for a single word (create + meaning_en + meaning_vi + part_of_speech + pronunciation_ipa + its examples + its relations) is capped at **40 XP/word**. The mastery_score (+50 max) is counted **separately**, on top of the 40 cap.
- Examples: +5 each (subject to the 40/word cap). Collocation learned (`PlayerCollocationProgress` status in learning/practiced/mastered): +5 each → Vocabulary. Synonym/antonym: +3; word_family: +5 (subject to cap). Error Dungeon: log +1, defeat +5, destroyed +20. Vocabulary Boss/badges: +60/+80/+100/+200.

**"Collocation XP not rising" root cause & fix:** the routing (+5 → Vocabulary) is correct and intended. The skill stays flat only because `collocation_items` is empty. Fix = **import the collocation source file** (see §9); once learners progress collocations, Vocabulary XP rises.

---

## 9. Collocation Import (design only — seed in implementation phase)

Source: `material/vocabularies/month1-6/English_Collocations_campaign1-3_3-6.md` (~1,467 collocations, 60 sections). The schema already supports it — **no migration needed**.

Parser mapping:

```text
File                         → DB
1 collection (file)          → CollocationCollection ("English Collocations in Use Intermediate")
"## N. <name>"               → CollocationSection (section_order = N)
"_Section: <group>_"         → CollocationTopic
table row                    → CollocationItem
    col1 collocation         → collocation
    col2 phiên âm (US)       → pronunciation_us
    col3 nghĩa               → meaning_vi
    col4 ví dụ               → example_en
    col5 nghĩa VN của ví dụ  → example_vi
link to campaign             → CampaignCollocationLink
```

Parser robustness requirements: tolerate noisy IPA (e.g. `breed /kraɪm/`, `heavy /snoʊ/`) without failing; allow duplicate collocations across sections; `meaning_en` is null (file has none); idempotent on `(collection, section_order, item_order, collocation)`; `daily_collocation_target = 3` already drives the Collocation Forge daily quest.

---

## 10. Recommended DB Policy Tables (avoid hard-coding)

```text
rank_xp_thresholds          -- F..S min_xp + level→rank (regenerated from §2 curve)
quest_xp_policies           -- daily quest activity → skill_code → xp
weekly_mission_xp_policies  -- mission_type → reward_target/skill → xp
main_quest_xp_policies      -- tier (light/standard/heavy/review/mock) → xp
```

`quest_xp_policies` seed reflects §5.1. `main_quest_xp_policies` seed reflects §6 (light_intro 25, standard 35, heavy_output 45, review_error_logging 25, sectional_test_mock_part 60). `weekly_mission_xp_policies` seed reflects §7 (note Grammar reward_target skill = Writing).

---

## 11. Final Values Summary

```text
Level curve : xp(L) = round(19 * (L^1.6 - 1)), L in 1..60, 10 levels/rank
Rank min XP : F=0 E=862 D=2460 C=4604 B=7212 A=10234 S=13279
Player      : rank = rank_from_level( level_from_xp( mean(5 matrix skill xp) ) ); rank-only on UI
Daily XP    : Vocab 14 | Listening 10 | Reading 10 | Writing 12 | Speaking 12 | Grammar 12→Writing
Weekly XP   : Vocab 55 | L 40 | R 40 | W 45 | S 45 | Grammar 45→Writing | Check-in streak-only
Main Quest  : full XP to every matrix skill in session; tier by skill (25/35/45/60)
Boss        : skill boss→skill; phase/overall→related skills; never player
Vocab cap   : 40 XP/word data-entry (+ mastery 50 separate)
Collocation : support source → Vocabulary; import 1467-item file to activate
Grammar     : support source → Writing
```

---

## 12. Notes for Future Tuning

These are initial balancing values. Tune only after collecting real data: actual completion rate, quests/week, Rank Boss pass rate, per-skill speed, whether Writing/Speaking boss exams are added later. Do not tune XP randomly.
