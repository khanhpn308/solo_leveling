# Player Level & Skill Level Mechanics

This document describes how the system computes and uses Player Level/Rank and Skill Level/Rank in the IELTS Quest Dashboard.

> **Canonical XP/level/rank values live in [`ielts_xp_policy_rank_quest_spec.md`](ielts_xp_policy_rank_quest_spec.md).** This file describes mechanics; it must not redefine values.
>
> **STALE WARNING (pre-redesign):** earlier versions of this file said the player accrues XP directly (`player_xp = quest_xp + mission_xp + boss_xp + vocab_xp`) and used the old 7-step rank table (3500=S … 200=E). Both are **removed**. The model below is the owner-approved redesign (2026-06-09).

---

## 1. Player Level/Rank — DERIVED, no direct accrual

**The player never earns XP directly.** All player-XP routing (quest→player, mission→player, boss→player, vocab→player, check-in→player) is removed.

```text
player_xp    = round( mean( skill_xp of the 5 matrix skills ) )
             = round( (Listening + Reading + Writing + Speaking + Vocabulary) / 5 )
player_level = level_from_xp(player_xp)
player_rank  = rank_from_level(player_level)
```

- The 5 **matrix skills** are the only inputs. Collocation and Grammar are support sources (see §3) and are excluded from the average.
- `player_xp` / `player_level` are internal inputs only.
- **Player RANK is the only player progression value surfaced on the UI** (Top Bar, Roadmap Hero, Status Modal).

### 1.A Level curve & rank mapping

Both player and skill use the same curve and mapping defined canonically in the XP policy spec §2:

```text
xp_to_reach(L) = round( 19 * (L^1.6 - 1) )     L in 1..60
rank_from_level: F=L1-10  E=L11-20  D=L21-30  C=L31-40  B=L41-50  A=L51-59  S=L60
Rank min XP    : F=0  E=862  D=2460  C=4604  B=7212  A=10234  S=13279
```

### 1.B No level-gating

There is **no** feature gate based on player level/rank (e.g. no "Level 5 to fight Boss"). Unlocking of study sections and bosses is driven purely by `study_plan_weeks` and `roadmap_phases`.

---

## 2. Display & UX

- Exposed via `/summary` and `/profile`.
- Top Bar / Roadmap Hero / Status Modal show **player rank** (with streak and shield).
- **Player rank vs Skill rank must be visually distinct** — both use the F–S scale, so the UI must label them clearly (e.g. "Overall Rank C" vs "Listening · Rank D") to avoid confusion.
- `rank` vs `confirmed_rank`: when `rank > confirmed_rank` (XP earned, not yet confirmed) the UI must show a locked/"Boss required" state for boss-gated skills, not the higher rank as if achieved.

### 2.A Support sources in the UI (FINAL — owner decision 2026-06-09)

The skill matrix shows **exactly 5 tiles** (Listening, Reading, Writing, Speaking, Vocabulary). Grammar and Collocation are **not** standalone tiles and have **no F–S rank/level** on the UI. Instead they render as a **buff line inside their parent matrix card**:

- **Writing card** → secondary line `+N XP from Grammar`.
- **Vocabulary card** → secondary line `+N XP from Collocation`.

`/summary` exposes, on each affected matrix skill entry, a `support_breakdown` array `[{ source, xp }]` carrying the routed support XP (already folded into the parent skill `xp` — do not double-count). The buff line is informational only; rank/level belong solely to the parent matrix skill. If a support XP is 0 (e.g. collocations not yet imported), show a muted/empty buff line rather than hiding it, so the learner still sees the source exists.

---

## 3. Skill Level/Skill XP & support sources

Each of the 5 matrix skills (`CampaignSkillState`) has its own `xp`, `level`, `rank`, `confirmed_rank`.

### 3.A Skill XP formula

```text
skill_xp = sum(earned_xp of claimed quests routed to this skill) + routed support XP (+ vocab activity for Vocabulary)
```

Routing (canonical in XP policy spec §4):
- **Grammar** support source → adds to **Writing** XP (daily Grammar Review/Exercise + S3 main quest Grammar component + Grammar weekly mission).
- **Collocation** support source → adds to **Vocabulary** XP (Collocation Forge daily + collocations learned via `PlayerCollocationProgress`, +5 each).

### 3.B Skill Level — fine-grained (60 levels)

Skill level is **fine-grained**: it advances on the same 60-level curve, so a learner levels up frequently (every few hundred XP) while rank changes only every 10 levels. This gives steady weekly feedback while keeping rank meaningful.

### 3.C Vocabulary XP detail & cap

`compute_vocabulary_xp` aggregates word data-entry, examples, relations, error-dungeon, collocations-learned, and vocab boss/badges. **Data-entry XP per word is capped at 40** (mastery_score +50 counted separately). See XP policy spec §8 for the full breakdown and the anti-farm rationale.

### 3.D Writing/Speaking confirmed rank

Writing and Speaking are **not boss-gated**: `confirmed_rank = rank` directly from XP. They never freeze waiting for a boss that does not exist. The 5 boss-gated skills (Vocabulary, Reading, Listening, Grammar, Collocation) keep the Rank Boss flow.
