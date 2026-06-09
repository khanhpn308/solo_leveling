# Vocabulary Support Skill System Spec

_For IELTS Quest Dashboard / Solo-Leveling-inspired gamified learning system_

## 0. Purpose

This document describes the proposed **Vocabulary Support Skill** module for the IELTS Quest Dashboard. It is written so an agent code CLI can load context, ground the repository, lock the task contract, plan broad work, execute in small slices, verify changes, update docs/trackers, and close the session cleanly.

Target stack:

```text
Frontend: React
Backend: FastAPI
Database: MySQL
Runtime: Docker / Docker Compose
Theme: Solo-Leveling-inspired IELTS learning dashboard
```

---

## 1. Source Grounding

### 1.1. Learning sources

This spec is based on two vocabulary-learning sources:

1. `effective-vocabulary-learning-pre-Intermediate.pdf`
2. `effective-vocabulary-learning-upper-Intermediate.pdf`

### 1.2. Source-based learning principles

The pre-intermediate source supports these learning behaviours:

- Build a weekly routine for studying one unit.
- Build a daily routine for revision.
- Learn actively by saying words aloud, repeating silently, highlighting important words, writing words down, and writing example sentences.
- Revise by covering the meaning and testing memory.
- Use a vocabulary notebook.
- Organize words by topic.
- Add translation, English meaning, drawings, synonyms, opposites, word family, pronunciation, and common word partners.
- Guess meaning first, then check with a dictionary.
- Use diagrams to organize vocabulary.

The upper-intermediate source supports these learning behaviours:

- Learn words in phrases, not in isolation.
- Learn collocations, grammar characteristics, pronunciation, stress, and register.
- Group words by topic, grammar feature, word root, or meaning.
- Use pictures, charts, tables, and network diagrams.
- Record synonyms, antonyms, word class, word family, and stress.
- Record typical learner errors.
- Use dictionary information such as pronunciation, stress, grammar pattern, synonym, antonym, collocation, countable/uncountable, transitive/intransitive, and visual thesaurus.
- Guess meaning from context using visual clues, surrounding words, grammar clues, background knowledge, prefixes/suffixes, and similarity to known words.

### 1.3. Important interpretation

The sources do **not** directly use the word `flashcard`, but the pre-intermediate source describes the same mechanism:

```text
look at a word → cover the meaning → recall → check → review again later
```

Therefore, **Flashcard Gate** is a valid gamified version of the source-based active recall method.

The sources also support **tree / node / network** features through:

- diagrams;
- topic grouping;
- network diagrams;
- visual thesaurus;
- word family;
- synonyms/antonyms;
- collocation networks.

---

# 2. Overall Product Idea

## 2.1. Core idea

Vocabulary should be a true **Support Skill**, not just a word list. It should buff the main IELTS skills:

- Reading
- Listening
- Writing
- Speaking
- Collocation
- Grammar

## 2.2. Recommended system name

```text
Lexical Awakening System
```

## 2.3. Main module structure

```text
Vocabulary System Overlay
├── Codex Archive
├── Flashcard Gate
├── Word Network Tree
├── Collocation Forge
├── Word Family Evolution
├── Shadow Duel
├── Echo Chamber
├── Context Hunt
├── Error Dungeon
└── Boss: Lexical Awakening
```

## 2.4. Main game loop

```text
Discover word
→ Save to Codex
→ Add meaning / pronunciation / part of speech
→ Add example sentence
→ Add collocation / synonym / antonym / word family
→ Generate flashcards
→ Review in Flashcard Gate
→ Unlock node in Word Network Tree
→ Use word in Writing/Speaking
→ Defeat Error Dungeon monsters
→ Clear Boss Battle
→ Gain Vocabulary XP and rank up
```

## 2.5. Vocabulary rank system

Use the existing rank style:

```text
F → E → D → C → B → A → S
```

| Rank | Meaning |
|---|---|
| F | Word discovered, meaning not stable |
| E | Meaning known, but usage still weak |
| D | Meaning + part of speech + pronunciation known |
| C | Collocation or phrase usage known |
| B | Word family / synonym / antonym network created |
| A | Word used correctly in Writing or Speaking |
| S | Word reviewed repeatedly and used naturally |

---

# 3. Features to Add

## 3.1. Feature 1 — Codex Archive

### Concept

The **Codex Archive** is the gamified vocabulary notebook. It stores every word or phrase the learner discovers.

### Game UI language

```text
SYSTEM MODULE: CODEX ARCHIVE
Purpose: Store and awaken discovered lexical items.
```

### Main user actions

- Add a new word or phrase.
- Add English meaning.
- Add Vietnamese meaning.
- Add part of speech.
- Add pronunciation / IPA.
- Add word stress.
- Add personal example sentence.
- Add collocation.
- Add synonym / antonym.
- Add word family.
- Assign IELTS topic.
- Generate flashcards from the entry.

### XP rules

| Action | XP |
|---|---:|
| Add new word | +2 |
| Add English/Vietnamese meaning | +2 |
| Add part of speech | +2 |
| Add pronunciation/stress | +3 |
| Add personal example | +5 |
| Add collocation | +5 |
| Add synonym/antonym | +3 |
| Add word family | +5 |
| Use word in Writing/Speaking task | +10 |

### Data needed

- `vocabulary_items`
- `vocabulary_examples`
- `vocabulary_collocations`
- `vocabulary_relations`
- `xp_transactions`

---

## 3.2. Feature 2 — Flashcard Gate

### Concept

The **Flashcard Gate** is the daily active recall battle system.

### Game UI language

```text
DAILY GATE: MEMORY RECALL
Mission: Review due cards before the gate closes.
```

### Card types

| Card Type | Purpose |
|---|---|
| `meaning_recall` | English word → recall meaning |
| `reverse_recall` | Vietnamese meaning → recall English word |
| `sentence_gap` | Fill word into sentence |
| `collocation` | Choose correct word partner |
| `pronunciation` | Identify pronunciation/stress |
| `register` | Choose formal/informal/neutral |
| `word_family` | Convert noun/verb/adjective forms |
| `synonym_antonym` | Choose synonym or opposite |

### Review buttons

```text
Again / Hard / Good / Easy
```

### Simple spaced repetition rule for MVP

| Result | Next Review |
|---|---|
| Again | Same day or next day |
| Hard | 1 day |
| Good | 3 days |
| Easy | 7 days |

### XP rules

| Review Result | XP |
|---|---:|
| Again | +0 |
| Hard | +1 |
| Good | +2 |
| Easy | +3 |
| Complete daily gate | +20 to +40 |

### Data needed

- `flashcards`
- `flashcard_reviews`
- `spaced_repetition_state`
- `xp_transactions`

---

## 3.3. Feature 3 — Word Network Tree

### Concept

The **Word Network Tree** is a graph-based vocabulary map. Each word, phrase, collocation, synonym, antonym, and word family item becomes a node.

### Recommended visualization

Use `React Flow` for the first implementation.

### Node statuses

| Status | Meaning |
|---|---|
| `locked` | Not available yet |
| `discovered` | Seen or added |
| `activated` | Meaning known |
| `stabilized` | Reviewed correctly |
| `mastered` | Used in a correct sentence |
| `awakened` | Used in IELTS Writing/Speaking or passed boss check |

### Node types

| Node Type | Example |
|---|---|
| `core` | education |
| `topic` | environment |
| `word` | significant |
| `collocation` | significant difference |
| `synonym` | important |
| `antonym` | insignificant |
| `word_family` | significance / significantly |
| `grammar_pattern` | suggest + clause |
| `register` | kids → informal, children → neutral/formal |

### Example tree

```text
Education
├── school
├── teacher
├── student
├── exam
├── assignment
├── scholarship
├── academic performance
└── higher education
```

### Unlock rule example

A node becomes `activated` when:

```text
meaning exists
AND part_of_speech exists
AND at least 1 example sentence exists
```

A node becomes `mastered` when:

```text
review_count >= 3
AND successful_review_rate >= 80%
AND at least 1 collocation exists
```

### Data needed

- `vocabulary_topics`
- `vocabulary_nodes`
- `vocabulary_edges`
- `vocabulary_items`
- `vocabulary_relations`

---

## 3.4. Feature 4 — Collocation Forge

### Concept

The **Collocation Forge** turns isolated words into usable phrases.

### Game UI language

```text
FORGE MODULE: COLLOCATION FORGE
Base word detected. Forge usable IELTS phrases.
```

### Gameplay

Learner matches or creates correct combinations:

```text
express + an opinion
make + a mistake
take + a break
gain + an advantage
strong + argument
significant + difference
```

### Collocation types

- adjective + noun
- verb + noun
- noun + preposition
- adjective + preposition
- fixed phrase
- IELTS phrase

### XP rules

| Action | XP |
|---|---:|
| Add collocation | +5 |
| Match collocation correctly | +3 |
| Write sentence with collocation | +7 |
| Use collocation in Writing/Speaking | +15 |

### Data needed

- `vocabulary_collocations`
- `vocabulary_examples`
- `xp_transactions`

---

## 3.5. Feature 5 — Word Family Evolution

### Concept

The **Word Family Evolution** feature lets a word evolve into related forms.

### Example

```text
communicate
├── communication
├── communicative
├── communicator
└── miscommunication
```

Another example:

```text
produce
├── product
├── production
├── productive
├── productivity
└── producer
```

### Gameplay

- Learner starts with a base word.
- Learner unlocks derived forms.
- Each derived form can become a new Codex item.
- Completing a family gives a bonus.

### XP rules

| Action | XP |
|---|---:|
| Add derived form | +4 |
| Identify correct word class | +3 |
| Complete word family set | +20 |

### Data needed

- `vocabulary_relations`
- `vocabulary_items`
- `xp_transactions`

---

## 3.6. Feature 6 — Shadow Duel

### Concept

The **Shadow Duel** is a synonym/antonym and register battle.

### Gameplay

Example synonym duel:

```text
Word: pleased
Choose synonym:
A. glad
B. cold
C. narrow
D. heavy
```

Example antonym duel:

```text
Word: urban
Choose opposite:
A. rural
B. modern
C. formal
D. crowded
```

Example register duel:

```text
Word: guys
Register: informal
Better IELTS Writing option: people / individuals
```

### XP rules

| Action | XP |
|---|---:|
| Correct synonym | +2 |
| Correct antonym | +2 |
| Correct register | +3 |
| 10-duel win streak | +20 |

### Data needed

- `vocabulary_relations`
- `vocabulary_items`
- `flashcards`
- `xp_transactions`

---

## 3.7. Feature 7 — Echo Chamber

### Concept

The **Echo Chamber** trains pronunciation, IPA, silent letters, and stress.

### Gameplay

- Choose correct stress.
- Identify silent letter.
- Listen and choose word.
- Mark syllables.
- Optional later: record pronunciation.

### Example

```text
record
Noun: REcord
Verb: reCORD
```

### XP rules

| Action | XP |
|---|---:|
| Mark stress correctly | +3 |
| Identify silent letter | +3 |
| Listen and choose word | +5 |
| Record pronunciation attempt | +10 |

### Data needed

- `vocabulary_items`
- `flashcards`
- `flashcard_reviews`
- optional future: `pronunciation_attempts`

---

## 3.8. Feature 8 — Context Hunt

### Concept

The **Context Hunt** trains learners to guess meaning before checking the dictionary.

### Gameplay

```text
Read sentence
→ Guess meaning
→ Select clue type
→ Check dictionary result
→ Save to Codex
```

### Clue types

- visual clue
- background knowledge
- surrounding words
- grammar clue
- prefix/suffix
- similarity to known word
- similarity to another language
- false friend warning

### Example

```text
Sentence:
The number of students increased significantly after the new policy.

Target word:
significantly

Guess:
noticeably / importantly
```

### XP rules

| Action | XP |
|---|---:|
| Guess before dictionary | +3 |
| Correct guess | +5 |
| Identify clue type | +3 |
| Save word to Codex | +2 |

### Data needed

- `context_hunt_attempts`
- `vocabulary_items`
- `xp_transactions`

---

## 3.9. Feature 9 — Dictionary Scanner

### Concept

The **Dictionary Scanner** is a checklist-based scanner for new words.

### Scanner checklist

```text
[ ] Meaning
[ ] Vietnamese meaning
[ ] Part of speech
[ ] Pronunciation / IPA
[ ] Word stress
[ ] Example sentence
[ ] Collocation
[ ] Synonym
[ ] Antonym
[ ] Word family
[ ] Register
[ ] Grammar pattern
[ ] Countable/uncountable
[ ] Transitive/intransitive
```

### Rank calculation idea

| Completed Fields | Suggested Rank |
|---|---|
| meaning only | F |
| meaning + example | E |
| + pronunciation + part of speech | D |
| + collocation | C |
| + word family/synonym/antonym | B |
| + used in writing/speaking | A |
| + repeated correct reviews | S |

### Data needed

- `vocabulary_items`
- `vocabulary_examples`
- `vocabulary_collocations`
- `vocabulary_relations`

---

## 3.10. Feature 10 — Error Dungeon

### Concept

The **Error Dungeon** stores recurring vocabulary mistakes as monsters.

### Monster types

| Monster Type | Example |
|---|---|
| `wrong_collocation` | make homework → do homework |
| `wrong_meaning` | use word with wrong meaning |
| `wrong_register` | guys in formal Writing |
| `wrong_word_form` | success vs successful |
| `wrong_preposition` | depend of → depend on |
| `wrong_grammar_pattern` | suggest to do → suggest doing / suggest that |

### Defeat rule

A monster is defeated when the learner corrects it successfully multiple times.

Example:

```text
corrected_count >= 3
AND last_mistake_at older than 7 days
```

### XP rules

| Action | XP |
|---|---:|
| Log error | +1 |
| Correct error | +5 |
| Defeat monster | +20 |
| Clear 10 monsters | Badge unlock |

### Data needed

- `vocabulary_errors`
- `xp_transactions`

---

# 4. Integration with Current UI

The current UI already contains:

- Mission Gates
- Boss Battles
- Quest Board
- Skill Matrix
- Rank F → S
- XP
- Daily / Weekly / Archive tabs
- Boss Timeline
- Streak / Shield
- Main Quest / Daily Quest / Weekly Quest
- Badge Wall

## 4.1. Add to Mission Gates

Add a new section:

```text
Vocabulary System
├── Codex
├── Flashcard Gate
├── Word Tree
├── Collocation Forge
├── Context Hunt
└── Error Dungeon
```

## 4.2. Add to Skill Matrix

Vocabulary already exists as a Support Skill. Expand it to show:

```text
SUPPORT SKILL
Vocabulary
Level: Lv.2
Rank: E
XP: 145 / 250

Current Buff:
+5% Reading comprehension
+3% Writing lexical resource
+3% Speaking lexical range
```

## 4.3. Add Vocabulary Panel to Dashboard

Recommended dashboard cards:

```text
Vocabulary Today
- Due cards: 20
- New words: 5
- Weak words: 8
- Active errors: 3
- Current tree: Education
```

```text
Lexical Mastery
- Total words: 320
- Mastered words: 75
- Active nodes: 180
- Awakened nodes: 12
```

## 4.4. Add Quest Board vocabulary integration

Daily tab should include:

```text
Daily Vocabulary Gate
- Review due cards
- Add new words
- Forge collocations
- Write example sentences
```

Weekly tab should include:

```text
Weekly Lexical Expansion
- Complete one topic tree
- Master 30 words
- Defeat 10 error monsters
```

Archive tab should preserve completed vocabulary quests for review.

---

# 5. Daily Quest Samples for Vocabulary

## 5.1. Daily Quest — Memory Gate

```text
Daily Quest: Memory Gate

Tasks:
1. Review 20 due flashcards.
2. Add 5 new words to Codex.
3. Write 3 personal example sentences.
4. Forge 3 collocations.
5. Unlock 1 node in Word Network Tree.

Reward:
+40 Vocabulary XP
+10 Reading XP
+1 Streak Point
```

## 5.2. Daily Quest — Collocation Forge

```text
Daily Quest: Collocation Forge

Tasks:
1. Select 5 base words from Codex.
2. Add 2 collocations for each base word.
3. Write 3 IELTS-style sentences.
4. Review 10 collocation cards.

Reward:
+45 Vocabulary XP
+15 Writing XP
Badge progress: Collocation Hunter
```

## 5.3. Daily Quest — Context Hunt

```text
Daily Quest: Context Hunt

Tasks:
1. Read 1 short paragraph.
2. Guess meaning of 5 unknown words.
3. Identify clue type for each word.
4. Check dictionary after guessing.
5. Save useful words to Codex.

Reward:
+35 Vocabulary XP
+15 Reading XP
```

## 5.4. Daily Quest — Error Dungeon

```text
Daily Quest: Error Dungeon

Tasks:
1. Review 3 active error monsters.
2. Correct each wrong sentence.
3. Write a new correct sentence.
4. Mark defeated progress.

Reward:
+30 Vocabulary XP
+10 Grammar XP
```

---

# 6. Boss Battle for Vocabulary

## 6.1. Boss 01 — Foundation Scan

Designed for Month 1–3.

```text
Boss 01: Foundation Scan

Requirements:
- 100 words in Codex
- 60 flashcards reviewed
- 30 example sentences
- 20 collocations
- 5 topic nodes unlocked

Boss Test:
- 20 meaning recall questions
- 10 collocation questions
- 5 synonym/antonym questions
- 5 sentence completion questions

Reward:
+60 Vocabulary XP
Unlock:
Vocabulary Rank E
```

## 6.2. Boss 02 — Monthly Checkpoint

```text
Boss 02: Monthly Checkpoint

Requirements:
- 150 words in Codex
- 100 flashcard reviews
- 30 words stabilized
- 10 error monsters corrected

Boss Test:
- Due card accuracy >= 75%
- Sentence completion accuracy >= 70%
- Collocation accuracy >= 70%

Reward:
+80 Vocabulary XP
Unlock:
Memory Streak Badge I
```

## 6.3. Boss 03 — Collocation Hunter

```text
Boss 03: Collocation Hunter

Requirements:
- 150 collocations forged
- 30 fixed phrases learned
- 20 IELTS topic words used in sentences

Boss Test:
- Match 30 collocations
- Write 10 sentences using collocations
- Identify 10 wrong collocations

Reward:
+100 Vocabulary XP
+30 Writing XP
Unlock:
Writing Lexical Buff
```

## 6.4. Boss 04 — Lexical Awakening

```text
Boss 04: Lexical Awakening

Requirements:
- 500 words in Codex
- 250 mastered words
- 100 collocations
- 50 word family relations
- 30 error monsters defeated

Boss Test:
- 50 mixed flashcards
- 20 collocation questions
- 10 context guessing questions
- 1 short IELTS-style paragraph using target vocabulary

Reward:
+200 Vocabulary XP
Badge:
Lexical Awakener
```

---

# 7. Database Proposal

## 7.1. `vocabulary_items`

```sql
CREATE TABLE vocabulary_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    word VARCHAR(255) NOT NULL,
    normalized_word VARCHAR(255),
    part_of_speech VARCHAR(50),
    cefr_level VARCHAR(10),
    ielts_topic VARCHAR(100),
    meaning_en TEXT,
    meaning_vi TEXT,
    register_label VARCHAR(50),
    grammar_note TEXT,
    pronunciation_ipa VARCHAR(255),
    word_stress VARCHAR(255),
    source_type VARCHAR(50),
    source_reference VARCHAR(255),
    mastery_rank VARCHAR(5) DEFAULT 'F',
    mastery_score INT DEFAULT 0,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

Recommended indexes:

```sql
CREATE INDEX idx_vocabulary_items_user_id ON vocabulary_items(user_id);
CREATE INDEX idx_vocabulary_items_topic ON vocabulary_items(ielts_topic);
CREATE INDEX idx_vocabulary_items_rank ON vocabulary_items(mastery_rank);
CREATE INDEX idx_vocabulary_items_word ON vocabulary_items(normalized_word);
```

## 7.2. `vocabulary_examples`

```sql
CREATE TABLE vocabulary_examples (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    vocabulary_item_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    example_sentence TEXT NOT NULL,
    example_type VARCHAR(50),
    is_corrected BOOLEAN DEFAULT FALSE,
    correction_note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 7.3. `vocabulary_collocations`

```sql
CREATE TABLE vocabulary_collocations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    vocabulary_item_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    collocation VARCHAR(255) NOT NULL,
    collocation_type VARCHAR(100),
    example_sentence TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 7.4. `vocabulary_relations`

```sql
CREATE TABLE vocabulary_relations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    source_word_id BIGINT NOT NULL,
    target_word_id BIGINT NULL,
    target_text VARCHAR(255),
    relation_type VARCHAR(50),
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `relation_type` values:

```text
synonym
antonym
word_family
derived_form
related_meaning
register_alternative
```

## 7.5. `vocabulary_topics`

```sql
CREATE TABLE vocabulary_topics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    parent_topic_id BIGINT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 7.6. `vocabulary_nodes`

```sql
CREATE TABLE vocabulary_nodes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    topic_id BIGINT NOT NULL,
    vocabulary_item_id BIGINT NULL,
    node_label VARCHAR(255) NOT NULL,
    node_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'locked',
    x_position FLOAT,
    y_position FLOAT,
    unlock_requirement TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `node_type` values:

```text
core
topic
word
collocation
synonym
antonym
word_family
grammar_pattern
register
```

Allowed `status` values:

```text
locked
discovered
activated
stabilized
mastered
awakened
```

## 7.7. `vocabulary_edges`

```sql
CREATE TABLE vocabulary_edges (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    source_node_id BIGINT NOT NULL,
    target_node_id BIGINT NOT NULL,
    edge_type VARCHAR(50),
    strength INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `edge_type` values:

```text
topic_link
synonym_link
antonym_link
family_link
collocation_link
grammar_link
register_link
```

## 7.8. `flashcards`

```sql
CREATE TABLE flashcards (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    vocabulary_item_id BIGINT NOT NULL,
    card_type VARCHAR(50),
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    hint TEXT,
    difficulty INT DEFAULT 1,
    status VARCHAR(50) DEFAULT 'new',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `card_type` values:

```text
meaning_recall
reverse_recall
sentence_gap
collocation
pronunciation
register
word_family
synonym_antonym
```

## 7.9. `flashcard_reviews`

```sql
CREATE TABLE flashcard_reviews (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    flashcard_id BIGINT NOT NULL,
    result VARCHAR(50),
    response_time_ms INT,
    reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `result` values:

```text
again
hard
good
easy
```

## 7.10. `spaced_repetition_state`

```sql
CREATE TABLE spaced_repetition_state (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    flashcard_id BIGINT NOT NULL,
    ease_factor FLOAT DEFAULT 2.5,
    interval_days INT DEFAULT 0,
    repetition_count INT DEFAULT 0,
    due_date DATE,
    last_reviewed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 7.11. `vocabulary_errors`

```sql
CREATE TABLE vocabulary_errors (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    vocabulary_item_id BIGINT NULL,
    error_type VARCHAR(100),
    wrong_text TEXT,
    corrected_text TEXT,
    explanation TEXT,
    status VARCHAR(50) DEFAULT 'active',
    defeated_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `error_type` values:

```text
wrong_collocation
wrong_meaning
wrong_register
wrong_word_form
wrong_preposition
wrong_grammar_pattern
```

## 7.12. `context_hunt_attempts`

```sql
CREATE TABLE context_hunt_attempts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    vocabulary_item_id BIGINT NULL,
    sentence TEXT NOT NULL,
    target_word VARCHAR(255) NOT NULL,
    guessed_meaning TEXT,
    correct_meaning TEXT,
    clue_type VARCHAR(100),
    is_correct BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `clue_type` values:

```text
visual_clue
background_knowledge
surrounding_words
grammar_clue
prefix_suffix
known_word_similarity
other_language_similarity
false_friend
```

## 7.13. `xp_transactions`

```sql
CREATE TABLE xp_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    skill_name VARCHAR(100),
    source_type VARCHAR(100),
    source_id BIGINT,
    xp_amount INT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `skill_name` values should reuse the current system if it already exists:

```text
listening
reading
writing
speaking
vocabulary
collocation
grammar
```

---

# 8. Backend FastAPI Contract

## 8.1. Vocabulary Codex API

```text
POST   /api/vocabulary/items
GET    /api/vocabulary/items
GET    /api/vocabulary/items/{id}
PATCH  /api/vocabulary/items/{id}
DELETE /api/vocabulary/items/{id}
```

### Create item request

```json
{
  "word": "significant",
  "part_of_speech": "adjective",
  "meaning_en": "important or large enough to be noticed",
  "meaning_vi": "quan trọng, đáng kể",
  "ielts_topic": "education",
  "register_label": "neutral",
  "pronunciation_ipa": "/sɪɡˈnɪfɪkənt/",
  "word_stress": "sig-NIF-i-cant"
}
```

## 8.2. Example API

```text
POST   /api/vocabulary/items/{id}/examples
GET    /api/vocabulary/items/{id}/examples
PATCH  /api/vocabulary/examples/{example_id}
DELETE /api/vocabulary/examples/{example_id}
```

## 8.3. Collocation API

```text
POST   /api/vocabulary/items/{id}/collocations
GET    /api/vocabulary/items/{id}/collocations
PATCH  /api/vocabulary/collocations/{collocation_id}
DELETE /api/vocabulary/collocations/{collocation_id}
POST   /api/vocabulary/collocations/practice
```

## 8.4. Relation API

```text
POST   /api/vocabulary/items/{id}/relations
GET    /api/vocabulary/items/{id}/relations
DELETE /api/vocabulary/relations/{relation_id}
```

## 8.5. Flashcard API

```text
POST /api/flashcards/generate/{vocabulary_item_id}
GET  /api/flashcards/due
POST /api/flashcards/{id}/review
GET  /api/flashcards/stats
```

### Review request

```json
{
  "result": "good",
  "response_time_ms": 2400
}
```

### Review response

```json
{
  "flashcard_id": 123,
  "result": "good",
  "next_due_date": "2026-06-09",
  "xp_awarded": 2,
  "vocabulary_rank_changed": false
}
```

## 8.6. Word Tree API

```text
GET    /api/vocabulary/tree/topics
POST   /api/vocabulary/tree/topics
GET    /api/vocabulary/tree/{topic_id}
POST   /api/vocabulary/tree/nodes
PATCH  /api/vocabulary/tree/nodes/{id}
POST   /api/vocabulary/tree/edges
DELETE /api/vocabulary/tree/edges/{id}
PATCH  /api/vocabulary/tree/nodes/{id}/unlock
```

## 8.7. Context Hunt API

```text
POST /api/vocabulary/context-hunt/attempts
GET  /api/vocabulary/context-hunt/history
```

## 8.8. Error Dungeon API

```text
POST  /api/vocabulary/errors
GET   /api/vocabulary/errors/active
GET   /api/vocabulary/errors
PATCH /api/vocabulary/errors/{id}
POST  /api/vocabulary/errors/{id}/defeat
```

## 8.9. XP / Skill Progress API

Reuse current XP system if it already exists.

Suggested endpoints if missing:

```text
POST /api/xp/award
GET  /api/skills/vocabulary/progress
GET  /api/skills/support/progress
```

---

# 9. Frontend React Screens

## 9.1. Vocabulary Dashboard

Purpose: overview of Vocabulary Support Skill.

Cards:

```text
Vocabulary Level
Rank F → S
Total words
Words mastered
Flashcards due today
Weakest word type
Current topic tree
Active error monsters
Current buff to IELTS skills
```

Recommended components:

```text
VocabularyDashboard
VocabularyStatsPanel
VocabularyBuffCard
VocabularyDueReviewCard
VocabularyWeaknessPanel
```

## 9.2. Codex Archive Screen

Purpose: manage vocabulary notebook.

Table columns:

```text
Word | Meaning | Topic | Part of Speech | Rank | Due Review | Actions
```

Filters:

```text
Topic
Rank
Part of speech
IELTS topic
Due today
Weak words
Archived
```

Recommended components:

```text
VocabularyCodexPage
VocabularyItemTable
VocabularyItemDrawer
VocabularyItemForm
VocabularyScannerChecklist
```

## 9.3. Flashcard Gate Screen

Purpose: active recall review battle.

UI style:

```text
Memory Gate
Card 1 / 20
HP: 20
Combo: 4
XP reward: +30
```

Controls:

```text
Show Answer
Again / Hard / Good / Easy
Skip
End Gate
```

Recommended components:

```text
FlashcardGatePage
FlashcardBattleCard
FlashcardReviewControls
FlashcardSessionSummary
```

## 9.4. Word Network Tree Screen

Purpose: visual node/tree learning.

Recommended library:

```text
React Flow
```

Node display:

```text
Node label
Node type
Status
Rank
Mastery score
Connections
```

Recommended components:

```text
WordNetworkTreePage
VocabularyNode
VocabularyEdge
NodeDetailPanel
TopicTreeSelector
```

## 9.5. Collocation Forge Screen

Purpose: train word combinations.

Gameplay variants:

```text
Drag and match
Multiple choice
Fill missing partner
Write sentence
```

Recommended components:

```text
CollocationForgePage
CollocationMatchGame
CollocationInputForm
CollocationResultPanel
```

## 9.6. Word Family Evolution Screen

Recommended components:

```text
WordFamilyEvolutionPage
WordFamilyTree
WordClassBadge
DerivedFormCard
```

## 9.7. Shadow Duel Screen

Recommended components:

```text
ShadowDuelPage
SynonymDuelCard
AntonymDuelCard
RegisterDuelCard
```

## 9.8. Echo Chamber Screen

Recommended components:

```text
EchoChamberPage
PronunciationCard
StressMarkerGame
SilentLetterQuiz
```

## 9.9. Context Hunt Screen

Recommended components:

```text
ContextHuntPage
ContextSentenceCard
ClueTypeSelector
GuessMeaningForm
ContextHuntResult
```

## 9.10. Error Dungeon Screen

Recommended components:

```text
ErrorDungeonPage
ErrorMonsterCard
ErrorCorrectionForm
ErrorDefeatProgress
```

---

# 10. MVP Plan

Do **not** implement all features at once.

## 10.1. Phase 1 — Core Vocabulary System

Build first:

1. Vocabulary Codex
2. Flashcard Gate
3. Simple spaced repetition
4. Vocabulary XP transactions
5. Daily Vocabulary Quest summary

### Phase 1 Definition of Done

- User can add vocabulary items.
- User can add examples and collocations.
- User can generate flashcards.
- User can review due cards.
- Review result updates next due date.
- XP is awarded to Vocabulary Support Skill.
- UI shows Vocabulary progress.

## 10.2. Phase 2 — Word Network Tree

Build second:

1. Topic nodes
2. Vocabulary nodes
3. Node status
4. Node edges
5. React Flow visualization

### Phase 2 Definition of Done

- User can create topic tree.
- User can see vocabulary nodes.
- User can connect words by relation.
- Node status changes based on learning progress.

## 10.3. Phase 3 — IELTS Advanced Vocabulary

Build third:

1. Collocation Forge
2. Word Family Evolution
3. Synonym/Antonym Shadow Duel
4. Register Checker

### Phase 3 Definition of Done

- User can practice collocation matching.
- User can add and review word families.
- User can practice synonym/antonym/register cards.
- Writing/Speaking lexical buff can read from vocabulary progress.

## 10.4. Phase 4 — Boss and Error System

Build fourth:

1. Monthly Vocabulary Boss
2. Error Dungeon
3. Boss timeline integration
4. Badge unlocks

### Phase 4 Definition of Done

- User can start and complete Vocabulary Boss Battle.
- Boss requirements are computed from actual data.
- Error monsters can be logged, corrected, and defeated.
- Badge progress updates.

---

# 11. Best Final System Design

The best system for this dashboard is not “flashcards only”.

The strongest design is:

```text
Codex Archive
+ Flashcard Gate
+ Word Network Tree
+ Collocation Forge
+ Error Dungeon
```

Why:

| Source idea | Game feature |
|---|---|
| Vocabulary notebook | Codex Archive |
| Cover meaning and test yourself | Flashcard Gate |
| Diagrams / network diagram | Word Network Tree |
| Collocations | Collocation Forge |
| Word family | Word Family Evolution |
| Synonym / antonym | Shadow Duel |
| Pronunciation / stress | Echo Chamber |
| Guess meaning from context | Context Hunt |
| Typical errors | Error Dungeon |
| Weekly/daily revision | Daily Gate / Weekly Mission |
| Checkpoint test | Boss Battle |

Recommended dashboard path:

```text
Mission Gates
→ Vocabulary System
→ Codex / Flashcard Gate / Word Tree / Forge / Dungeon
```

---

# 12. Agent Workflow for Implementation

This section adapts the current project workflow for implementing Vocabulary Support Skill.

## 12.1. Ground repo before doing work

Before coding, the agent must read in this order:

```text
1. AGENTS.md
2. README.md
3. TASKS.md
4. DECISIONS.md
5. docs/current/CONTEXT_INDEX.md
```

Stop loading context only when all four conditions are met:

```text
- Task type is identified.
- Files likely to be modified are identified.
- Existing pattern to follow is identified.
- Goal, constraints, and next steps are clear.
```

## 12.2. Lock task contract before implementation

Before touching files, define:

```text
Goal:
Completion Criteria:
In Scope:
Out of Scope:
Constraints:
Risks:
```

Example contract for Phase 1:

```text
Goal:
Add the MVP Vocabulary Codex and Flashcard Gate.

Completion Criteria:
- Vocabulary item CRUD works.
- Flashcards can be generated from vocabulary items.
- Due flashcards can be reviewed.
- Review updates spaced repetition state.
- Vocabulary XP increases after valid reviews.
- Frontend has Codex and Flashcard Gate screens.
- Basic smoke checks pass.

In Scope:
- Backend models/schemas/routes/services for vocabulary and flashcards.
- MySQL migration or schema update.
- Frontend pages/components for Codex and Flashcard Gate.
- XP integration if existing pattern is clear.

Out of Scope:
- Word Network Tree.
- Collocation Forge game UI.
- Error Dungeon.
- Boss Battle.
- Voice pronunciation recording.
- AI dictionary auto-fill.

Constraints:
- Follow existing repo patterns.
- Do not rewrite unrelated dashboard code.
- Keep slices small and verifiable.
- Reuse existing XP/quest systems if available.

Risks:
- Schema may conflict with existing skill/XP tables.
- Frontend routing may already have a different pattern.
- Spaced repetition logic can become too complex.
```

## 12.3. Plan before broad tasks

Plan first if the task:

```text
- touches multiple files;
- changes backend behavior;
- changes schema or API contract;
- involves migrations;
- requires clear sequencing or validation.
```

A good plan must be:

```text
- bounded;
- decision-complete;
- testable;
- small enough for one focused session or worker slice.
```

## 12.4. Execute in small slices

Recommended slices for Phase 1:

```text
Slice 1: Backend database models/migration
Slice 2: Pydantic schemas and service layer
Slice 3: Vocabulary Codex API
Slice 4: Flashcard generation and review API
Slice 5: XP integration
Slice 6: Frontend Codex page
Slice 7: Frontend Flashcard Gate page
Slice 8: Smoke tests and docs update
```

Each slice must be independently verifiable.

## 12.5. Verification priority

Tasks are not done without evidence.

Verify in this order:

```text
1. Syntax / type checks
2. Focused smoke checks
3. Tests for changed behavior
4. Review for medium/high-risk tasks
```

Suggested checks:

### Backend

```bash
python -m pytest
python -m compileall .
```

or repo-specific commands if documented.

### Frontend

```bash
npm run lint
npm run build
```

or repo-specific commands if documented.

### Docker

```bash
docker compose up --build
```

only if appropriate for the task and repo workflow.

## 12.6. Documentation and tracker updates

After meaningful changes, update:

```text
TASKS.md
docs/history/TEST_REPORT.md
docs/history/AGENT_NOTES.md
docs/history/changelogs.md
DECISIONS.md or ADR if there is a long-term decision
```

## 12.7. Session close format

At the end of each session, output:

```text
What changed:
- ...

What was validated:
- ...

What is still open:
- ...

Next session should read first:
- ...
```

---

# 13. Ready-to-use Prompt for Code Agent

Use this prompt when assigning the feature to a coding agent:

```text
You are working on the IELTS Quest Dashboard.

Task:
Implement the Vocabulary Support Skill MVP based on docs/current/vocabulary_support_skill_spec.md.

Before coding:
1. Ground the repo by reading:
   - AGENTS.md
   - README.md
   - TASKS.md
   - DECISIONS.md
   - docs/current/CONTEXT_INDEX.md
2. Stop loading context when:
   - task type is identified;
   - files likely to be modified are identified;
   - existing pattern to follow is identified;
   - goal, constraints, and next steps are clear.
3. Lock the task contract:
   - Goal
   - Completion Criteria
   - In Scope
   - Out of Scope
   - Constraints
   - Risks

Implementation rule:
- Do not implement every feature at once.
- Start with Phase 1 only:
  - Vocabulary Codex
  - Flashcard Gate
  - Simple spaced repetition
  - Vocabulary XP integration
  - Daily vocabulary quest summary if it fits existing patterns.
- Follow existing repo patterns.
- Touch only necessary files.
- Execute in small verifiable slices.
- Validate after each meaningful slice.
- Update docs and tracker files after meaningful changes.
- End the session with:
  - what changed;
  - what was validated;
  - what is still open;
  - what to read first next session.
```

---

# 14. Implementation Notes

## 14.1. Keep MVP simple

Avoid adding complex AI dictionary auto-fill at first.

For MVP, allow manual entry:

```text
word
meaning
part of speech
example
collocation
flashcard generation
review result
next due date
XP
```

## 14.2. Do not overbuild the graph first

The Word Network Tree is valuable, but it should be Phase 2.

Phase 1 should focus on the learning loop:

```text
Codex → Flashcard → Review → XP → Progress
```

## 14.3. Integrate with existing gamification

Do not create a separate XP universe if the dashboard already has XP/skill tables.

Prefer:

```text
Use existing user / skill / XP / quest models
```

Only add tables needed for vocabulary-specific data.

## 14.4. Naming consistency

Use these names consistently:

```text
Vocabulary Support Skill
Codex Archive
Flashcard Gate
Word Network Tree
Collocation Forge
Error Dungeon
Lexical Awakening System
```

---

# 15. Open Decisions for Agent

Before implementation, inspect the repo and decide:

```text
1. Does the project already have user_id/auth?
2. Does the project already have skill XP tables?
3. Does the project already have quest tables?
4. Is database migration handled by Alembic, raw SQL, or init scripts?
5. What frontend router is used?
6. What UI component pattern is used?
7. Is React Query, Zustand, Redux, or plain fetch used?
8. Is there an existing API client layer?
9. Where should docs/current/vocabulary_support_skill_spec.md live?
10. Should Phase 1 include only manual vocabulary input, or also CSV/import?
```

Until these are grounded in the repo, do not assume implementation details.
