# Implementation Plan: Phase 4 — Collocation Browser + Flashcard System (I4-1 → I4-7)

## Background

Tasks I4-2 → I4-7 are the only remaining incomplete tasks in TASKS.md.
Task I4-1 has been **partially completed** by a previous session:
- Migration `20260609_20_add_collocation_flashcards.py` ✅ exists  
- `CollocationFlashcard` model ✅ in `models.py` (line 1406)  
- Backend endpoints ❌ not implemented  
- Frontend ❌ not implemented

## Summary of Changes

Transform the existing "Collocation Forge" MCQ quiz into a full **Collocations browser + collocation flashcard** system (I4-2 → I4-7), and fix the vocabulary flashcard one-way flip bug (I4-6).

---

## Proposed Changes

### Phase A — Backend (I4-2 + I4-7)

#### [MODIFY] services.py
New helpers and service functions:
- `effective_familiarity(stored: str, set_at: datetime | None, now: datetime) -> str`  
  Drops one tier per 7-day window: `good→hard→again`; `easy` never decays; floored `again`.
- `try_autocomplete_collocation_forge(db, player_id, campaign_id, today)` —  
  Count `DISTINCT collocation_item_id` where `DATE(familiarity_set_at)=today`; if ≥5, find `vocab_collocation` daily quest and call `complete_quest_instance`.

#### [MODIFY] schemas.py
New Pydantic schemas:
- `CollocationTopicOut` — `id`, `title`, `topic_order`, `section_title`
- `CollocationItemOut` — all `CollocationItem` fields + `effective_familiarity` + `is_added`
- `CollocationFlashcardTopicOut` — `id`, `title`, `card_count` (non-graduated)
- `CollocationFlashcardItemOut` — item fields + `effective_familiarity`
- `CollocationReviewIn` — `result: str` (again/hard/good/easy)

#### [MODIFY] main.py
New route group `/api/collocations`:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/collocations/topics` | Browse: all topics in campaign-linked collections |
| `GET` | `/api/collocations/topics/{topic_id}/items` | Browse: items + `effective_familiarity` + `is_added` |
| `POST` | `/api/collocations/{item_id}/flashcard` | Add/re-add flashcard (idempotent; re-add graduated resets to `again`) |
| `DELETE` | `/api/collocations/{item_id}/flashcard` | Remove flashcard |
| `POST` | `/api/collocations/{item_id}/flashcard/review` | Set familiarity + trigger auto-complete check |
| `GET` | `/api/collocations/flashcard/topics` | Flashcard: topics with ≥1 non-graduated card |
| `GET` | `/api/collocations/flashcard/topics/{topic_id}` | Flashcard: non-graduated cards in topic |

All endpoints scoped to `current_player` + `current_campaign` (same pattern as other vocab endpoints).

Also update `reset_database` to wipe `CollocationFlashcard` rows (add to delete list before `CollocationItem`).

#### [MODIFY] test_backend.py
New test class `TestCollocationFlashcards`:
- `test_effective_familiarity_decay` — decay table: good@0d→good, good@8d→hard, good@15d→again, hard@8d→again, again stays, easy stays
- `test_add_flashcard_idempotent` — 2nd POST same item → no duplicate
- `test_add_graduated_resets_to_again` — POST on `easy` card resets to `again`
- `test_review_easy_graduates` — card excluded from flashcard/topics after `easy`
- `test_autocomplete_collocation_forge_5_distinct` — 5 distinct → quest completed
- `test_autocomplete_collocation_forge_same_card_no_complete` — 1 card × 5 → not completed

---

### Phase B — Frontend (I4-3, I4-4, I4-5, I4-6)

#### [MODIFY] CollocationForge.jsx → repurpose as `CollocationBrowser.jsx`
Completely rewrite to a browse UI:
- On mount: `GET /api/collocations/topics` → topic list
- Click topic → `GET /api/collocations/topics/{id}/items` → item cards
- **Card layout** (hide null rows): `collocation` (largest h2) → `pronunciation_us` → `meaning_vi` → `example_en` → `example_vi` → `collocation_type` tag
- **Neon border** by `effective_familiarity`: `again` → grey (no glow), `hard` → faint light-green, `good` → soft blue, `easy` → strong yellow
- **Add/remove**: not-added → "Add to flashcard" button; added+again → "✓ Đã thêm" badge + remove button
- Remove all MCQ quiz code

#### [MODIFY] VocabularyWorkspace.jsx
Two changes:
1. **Tab rename + component swap**: "Collocation Forge" (`forge`) tab → "Collocations" (`collocations`); render `CollocationBrowser` instead of old `CollocationForge` (I4-3)
2. **Flashcard tab sub-tabs** (I4-4): add `flashSubTab` state (`'vocabulary' | 'collocation'`); when `activeTab === 'flashcard'`:
   - Show sub-tab buttons: `Vocabulary | Collocation`
   - `Vocabulary` sub-tab = existing review loop (unchanged)
   - `Collocation` sub-tab = new `CollocationFlashcardReview` inline component:
     - `GET /api/collocations/flashcard/topics` → topic list
     - Click topic → review loop using same duel flip UI
     - 4 buttons → `POST .../flashcard/review`; `easy` removes card from loop
     - Card border matches `effective_familiarity` (same neon CSS)
3. **Dead code removal** (I4-5): remove "+ Forge Collocation" button, `handleAddCollocation`, `handleDeleteCollocation`, dead `item.collocations` block in codex card
4. **Two-way flip** (I4-6): on the flashcard BACK face, add a "↩ Recall Meaning" button that calls `setShowAnswer(false)`

#### [MODIFY] styles.css
New CSS rules:
- `.neon-again` — grey border, no glow
- `.neon-hard` — `border: 1px solid #4ade80; box-shadow: 0 0 4px rgba(74,222,128,0.2)`
- `.neon-good` — `border: 1px solid #60a5fa; box-shadow: 0 0 8px rgba(96,165,250,0.3)`
- `.neon-easy` — `border: 1px solid #fde68a; box-shadow: 0 0 14px rgba(253,230,138,0.5)`
- `.collocation-browser`, `.collocation-topic-list`, `.collocation-item-card`, `.coll-add-badge`, `.flashcard-subtabs`

---

## Dependency Order

```
I4-1 (done) → I4-2 backend (services + endpoints + tests)
                    ↓
         I4-5 (remove dead code, independent)
         I4-6 (two-way flip, independent)
                    ↓
         I4-3 (CollocationBrowser component)
                    ↓
         I4-4 (Flashcard sub-tabs + collocation review loop)
                    ↓
         I4-7 (autocomplete, wired in I4-2 review endpoint)
```

I4-5 and I4-6 can be done independently of I4-2; I'll do them early to clean up the frontend before adding new UI.

---

## Verification Plan

### Automated Tests (backend)
```bash
# From backend container or local venv
pytest backend/app/test_backend.py -k "collocation_flashcard" -v
# Full suite must remain ≥ 61/1/0
pytest backend/app/test_backend.py -v
```

### Build Check
```bash
npm run build  # must succeed: 0 errors
```

### Manual Browser Smoke
1. `/api/dev/reset` → open Vocabulary Workspace → "Collocations" tab
2. Browse topics → click one → cards render with grey border + "Add to flashcard"
3. Add 3 cards → browse shows "✓ Đã thêm" badges
4. "Flashcard Gate" → Collocation sub-tab → topic appears → review loop runs
5. Press "good" → card shows blue border in browse
6. Press "easy" on another card → disappears from flashcard loop, stays yellow in browse
7. Review 5 distinct → Collocation Forge daily quest auto-completed (claim-ready state)
8. Vocabulary sub-tab: review a card → flip shows back; "↩ Recall Meaning" flips back to front

---

## Open Questions

> None — all decided in grill session 8l. Full owner model is documented in TASKS.md Phase 4 header.
