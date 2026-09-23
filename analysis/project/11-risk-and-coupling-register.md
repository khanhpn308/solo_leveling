# 11 — Risk and coupling register

Answers mission question **14**: which current areas are structurally risky or tightly coupled.
Each entry states what the coupling **is**, what is coupled to it, what breaks together if one side
moves, how the coupling is **measurable** (with the actual counts and the command that produced
them), and whether it is **load-bearing or accidental**. Ranking is by consequence for a future
redesign, not by severity of the code.

Discovery only: no recommendations, no target design. Evidence convention in `README.md`.

## 0. How the measurements were taken

All counts below are mechanical over files that were read. The commands, once, so any number can be
reproduced:

| Measurement | Command |
| --- | --- |
| Module size | `wc -l backend/app/{main,services,seed}.py` → 2874 / 3267 / 2784 |
| Function fan-in | `grep -c "\b<name>\b" main.py services.py seed.py` per name |
| Write sites | `grep -c 'db.commit()'` and `db.flush()`; `grep -rn '<obj>\.<col> ='` per column |
| Route inventory | decorator + signature extraction (`07` §1) |
| Client field usage | `grep -rho "\bquest\.[a-z_]*" frontend/src` and the same for `profile.`/`skill.` |
| Component state | `grep -c "useState("` per component; `ls components/*.jsx \| wc -l` → 40 |
| Dead code | import-graph reachability (`05` §4) |
| Tracked artifacts | `git ls-files \| grep -c <pattern>` |

Module line counts: `main.py` **2874**, `services.py` **3267**, `seed.py` **2784**,
`models.py` **1559**, `dashboard-data.js` **817**, `styles.css` **6276**.

---

## 1. The register, ranked by consequence

### R-1 — Every derived value in the product is refreshed by a read, from one function (LOAD-BEARING)

**What it is.** `services.refresh_progress_state` (`services.py:804-816`) is the only thing that
brings quest status, weekly mission counters, skill state, badge unlocks and player counters up to
date, and it is called at the top of 8 plain GET routes plus 24 write routes plus startup (`08` §6.1).

**Measured.** 38 references: **34 in `main.py`** (1 import + **33 call sites**) and 4 in
`services.py` (1 definition + 3 internal calls). `refresh_progress_state` runs 5 recompute steps and
one `db.commit()` each time (`services.py:815`). Write sites overall: `db.commit()` × 35 in
`main.py`, × 37 in `services.py`.

**Coupled to.** Everything the dashboard shows. Changing any derivation rule means auditing 33 call
sites, of which 8 are reads a user performs by opening a page.

**Breaks together.** A change to one recompute step (say badge thresholds) and every route that
triggers it. Conversely, removing the GET-side calls changes when `quests.status`,
`quests.earned_xp`, badges and streak counters become accurate — `[UNRESOLVED]` U-32 on whether that
is observable.

**Load-bearing.** Yes. There is no scheduler (`01` §7), so if the GET-side refreshes stopped,
nothing else would refresh those columns.

---

### R-2 — One table of shared mutable progression state has six independent writers across two files (LOAD-BEARING, multiplicity ACCIDENTAL)

**What it is.** `campaign_skill_states` holds `xp`, `rank`, `level`, `confirmed_rank`, `pending_rank`
and `promotion_status` — the product's core progression row — and it is mutated from six functions:

| Owner | Mutation sites | Line anchors |
| --- | --- | --- |
| `services.recompute_skill_progress` | **13** | `services.py:743, 756-757, 761-762, 767-769, 790-791, 799-800` |
| `services.apply_rank_suggestion` | **5** | `services.py:1457, 1460-1461, 1464-1465` |
| `services.award_skill_xp` | 2 | `services.py:1411-1412` |
| `services.submit_vocabulary_boss_result` | 1 | `services.py:3015` |
| `main.submit_rank_exam` | **7** | `main.py:1828-1831, 1853, 1856, 1864` |
| `main.unlock_rank_exam`, `main.start_rank_exam` | 1 each | `main.py:1619`, `:1702` |

**Coupled to.** XP, rank, promotion gating, badges (read the same map), player XP (a mean of five of
these rows), and `SkillRankHistory`.

**Breaks together.** Changing what `xp` means touches 13 recompute sites and 9 hand-written mutation
sites; the recompute is also the mechanism that *undoes* manual writes, which is why
`main.py:1859-1866` applies the −50 XP exam penalty **after** a refresh (the comment says so).

**Load-bearing.** Yes — but note the asymmetry: 13 of the 30 sites are one function recomputing from
source, while 17 are direct writes that the next recompute can overwrite unless ordered carefully.
`[DERIVED]` Two of the direct writers already rely on that ordering (`apply_rank_suggestion` writes an
XP floor the recompute must respect, `services.py:1451-1452` and `:737-748`).

---

### R-3 — Two write paths for the same quest disagree about which account they recompute (ACCIDENTAL)

**What it is.** `complete_quest_instance` calls `refresh_progress_state(db)` with no arguments
(`services.py:863`), which falls back to `get_active_player(db)` = `db.query(Player).first()`
(`services.py:235-240`). The claim route on the same row passes both explicitly, with the comment
*"Pass player+campaign so recompute_player_progress targets the correct account"*
(`main.py:1132-1133`).

**Measured.** Of the 33 call sites, **3 pass `player=`/`campaign=` explicitly**; the other 30 either
run inside a request that already resolved the right rows (so the fallback is harmless) or resolve
globally. `get_active_player` fan-in: 5 references; `get_active_campaign`: 7.

**Coupled to.** Multi-account correctness (U-03) and every recompute-triggering route.

**Breaks together.** Any redesign that introduces a second account: the two paths stop agreeing, and
the divergence is invisible today because both resolve to the only player row.

**Load-bearing.** The rule is load-bearing; the inconsistency is accidental — and the code comment
shows awareness of it in one place only.

---

### R-4 — One 2874-line module owns every route, and the largest handlers are 105 lines (ACCIDENTAL)

**Measured.** `main.py`: 121 path decorators, 118 handler functions, 100 with `response_model`, 35
`db.commit()`, 12 `db.flush()`. Longest handlers: `submit_rank_exam` **105 lines**,
`start_rank_exam` **105**, `reset_database` **88**, `register` **76**, `get_collocation_levels` 68,
`get_summary` 67, `login` 64, `activate_campaign` 56.

**Coupled to.** Every contract in the product: there is no router package, no service interface, no
dependency-injection layer, so a change to any response shape, auth level or status literal is an
edit in this one file. Fan-in of the session concern alone: 121 decorators.

**Breaks together.** Any change to the auth dependency chain, since it is declared per handler rather
than globally (`main.py:208` has no `dependencies=[...]`) — 107 handlers opt in by hand and 14 do
not (`09` §7).

**Load-bearing.** The routes are load-bearing; the single-module shape is accidental accumulation.

---

### R-5 — Seeding reads curriculum content from files whose in-repo fallback is empty (LOAD-BEARING path, ACCIDENTAL file, CLOSES U-09)

**What it is.** `seed.material_file_path()` (`seed.py:557-579`) resolves the study plan from the
first candidate that **exists**, in this order:

1. `$MATERIAL_PLAN_PATH` — compose sets `/app/material.md`, a read-only mount of
   `material/material.md` (`docker-compose.yml:29`);
2. `<repo root>/material.md` — **does not exist** (the file lives at `material/material.md`);
3. `<repo>/backend/material.md` — **exists and is 0 bytes** (`wc -c` → 0; commit `05c92ab`)
   versus `material/material.md` at **238 258 bytes** (commit `d652133`);
4. `<cwd>/material.md`.

**Coupled to.** `parse_material_plan()` (`seed.py:596-650`) → `ensure_study_plan` (`:1125-1205`) →
`ensure_main_quest_instances` (`:1483`). `[DERIVED]` With zero bytes, `week_rows` and `session_rows`
are empty, so **study-plan weeks, study-plan sessions and main quests are all empty** while daily
quests and weekly missions still seed from `quest_template_seed` + quotas + `weekly_mission_patterns`.
`parse_start_date()` (`seed.py:2714-2718`) reads only `APP_START_DATE`, so the start date is
unaffected.

**Measured.** 4 content files feed seeding: `material/material.md`, `backend/material.md`,
`material/vocabularies/pre-intermediate_intermediate/vocab.md`,
`material/collocation/English_Collocations_campaign1-3_3-6_polished.md`. `backend/material.md`
tracked as **0 bytes** by commit `05c92ab`.

**Load-bearing.** The markdown *is* the curriculum (`README`/`01` §materials) — the app stores no
lesson content. So the resolution order is load-bearing and the empty fallback file is accidental.

**This closes U-09** ("which copy is authoritative, and do they agree"): they do not agree, one is
empty, and the compose path never reaches it.

---

### R-6 — Startup is also the migration tool and the data loader (LOAD-BEARING, single point)

**What it is.** `@app.on_event("startup")` (`main.py:431-441`) runs: wait for the DB (30 retries ×
2 s, `database.py:23-35`) → `run_database_bootstrap` (either `create_all` + `alembic stamp head` on
an empty database, or `alembic upgrade head` on every boot, `database.py:39-57`) → `seed_database`
(**52 functions, 23 of them `ensure_*`**, `seed.py:2685-2707`) → `refresh_progress_state`.

**Measured.** `seed.py`: 2784 lines, 52 top-level functions, 23 `ensure_*`, **43 `db.flush()` calls,
1 `db.commit()`** — so an exception mid-seed rolls back the whole seed. 31 Alembic revisions exist.

**Coupled to.** Schema, reference data, all content, and the `material/*.md` files (R-5). Also to the
two unauthenticated dev routes that re-run parts of it at runtime (`main.py:1587`, `:1877`).

**Breaks together.** A markdown edit changes quests, XP and missions; a failed seeder prevents the
process from starting at all; and because seeding runs on every boot, a partially-converged database
is only detectable by starting the app.

**Load-bearing.** Yes — the product has no other migration or content path.

---

### R-7 — Thirteen rules have exactly one implementation and it is in the browser (LOAD-BEARING for the UI, ACCIDENTAL in origin)

**What it is.** `10` Part A9 lists them: the skill-bar percentage, the level-bar fraction, the weekly
fallback identity, the quest action affordance, the phase labels, the weakness-suggestion heuristics,
the review-session XP display, three games' scoring, the vocabulary-boss score, the exam timer, and
the client's notion of "today".

**Measured.** Three of them are backed by tables that exist nowhere on the server: `SKILL_XP_THRESHOLDS`
(`dashboard-data.js:4` — the values `1200`, `2500`, `4500` return **zero** matches in `backend/app/`),
`WEEKLY_MISSION_PATTERNS` (`:91-119`), `LEVEL_XP_FLOORS` (`:614-617`). Four of them are exercised by
`App.jsx` during every render (`view` memo at `App.jsx:227-230`).

**Coupled to.** The rendering of the dashboard, the vocabulary workspace, the games and the exam.
Nowhere else: no stored value depends on them except where they are sent back as input (R-11).

**Breaks together.** Replacing `dashboard-data.js` deletes these rules; keeping the server and
replacing the UI silently loses them. The reverse — replacing the server — does not restore them,
because there is no server-side equivalent.

**Load-bearing.** For the UI as shipped, yes. Origin: accidental, since four of them are duplicated
ideas that drifted (`R-8`).

---

### R-8 — Four tables of the same domain data exist on both sides, and two already disagree (ACCIDENTAL)

| Duplication | Server owner | Client owner | State |
| --- | --- | --- | --- |
| Player level curve `round(19*(L^1.6-1))` | `services.py:77` | `dashboard-data.js:614-617` | deliberately mirrored; **the frontend test asserts the mirror** (`dashboard-data.test.js`) |
| Phase boundaries and labels (weeks 13/26/39/52) | `seed.py:366-388` | `dashboard-data.js:53-90`, `:485-491` | same thresholds, **different label text** ("Months 1-3" vs "Month 1-3 / Foundation") |
| Weekly mission patterns | `seed.py:818-891` (6 per phase, items + `reward_xp`) | `dashboard-data.js:91-119` (3 patterns, sentence `lines`) | **different data sets**, not a copy (U-40) |
| Skill progress ladder | none exists | `dashboard-data.js:4`, `:461-467` | client-only; saturates at 10 000 while rank S needs 13 279 (`services.py:79-88`) |
| "Earned XP" of a quest | `earned_xp` column | `getQuestEarnedXp` reads `quest.xp` (`:412-414`) while `getQuestRewardValue` reads `earned_xp` (`:420-426`) | inconsistent within the client |

**Coupled to.** Any change to progression presentation or to mission definitions has to be made in two
places or acknowledged as one-sided.

**Breaks together.** Because the only frontend test asserts the level-curve mirror, the test suite
**enforces** that one duplication and says nothing about the other three.

---

### R-9 — The only automated test that runs here locks in a duplication, and the larger suite cannot run (ACCIDENTAL, worsens every risk above)

**Measured.** Frontend: **1 test file** (`frontend/src/dashboard-data.test.js`), 6 tests, all passing
(`README` §verified). Its assertions cover `getQuestStatus`, `getCompletionMode`, `getQuestEarnedXp`,
`getPlayerXpProgress`, `getCalendarDayDiff` — i.e. four of the CLIENT-ONLY rules of R-7 and the
duplicated level curve of R-8. Backend: **68 tests across 11 classes** in `test_backend.py`, **read
but never executed** here (no Python interpreter; U-04), and they run on in-memory SQLite, so they
cannot validate the MySQL path or the 31 Alembic revisions either.

**Coupled to.** Confidence in every other entry in this register.

**Breaks together.** Nothing at runtime; but as a change-enabler, the regression net covers the
client-side derivations (the part a redesign would replace) and not the server-side rules (the part it
must keep).

---

### R-10 — Auth is a chain of single points that every route depends on (LOAD-BEARING)

**Measured.** 118 authenticated paths depend on `get_current_account`, which depends on
`decode_jwt` (`auth_utils.py:32-55`, signature + `exp` only) and on the **`JWT_SECRET_KEY`
fallback literal** (`auth_utils.py:8`) that is absent from `.env.example` and `docker-compose.yml`
(`09` §2.3). Refresh rotation replaces the stored hash in place (`main.py:637-639`) with no grace
window while the client fires up to 13 parallel requests on boot (`08` §3 T-1). On session death the
client returns `undefined` instead of throwing (`App.jsx:152-155`).

**Coupled to.** Every route, the client's loader error handling, and the "logged in" state of the SPA.

**Breaks together.** A token-format or cookie change breaks all 118 routes and the silent-retry path
at once; a second account breaks nothing today (U-03) but the rotation race might (U-37).

**Load-bearing.** Entirely. This is the densest single point in the repository.

---

### R-11 — The client is the authority for scheduling inputs while the server is the authority for consequences (LOAD-BEARING split, ACCIDENTAL boundary)

**What it is.** Scored or scheduled inputs arrive from the browser and are used server-side:
`score_pct: float` sets `confirmed_rank` (`services.py:2999, 3015`); game `words` drive
`mastery_score += 2` (`services.py:2216`) which feeds the vocabulary XP formula (`services.py:553-646`);
test records and certificates drive rank suggestions, and applying one **raises `state.xp` to the rank
floor** (`services.py:1451-1452`). Conversely the client's `getTodayISO()` decides which quests are
"today" while the server uses its own `date.today()` (`dashboard-data.js:184-190` vs `main.py:767`).

**Measured.** 8 client-supplied values in `09` §8; 2 independent "today" functions; 1 of them
(`xp_gained`, `schemas.py:820`) accepted and ignored.

**Coupled to.** XP, rank, mastery, templates and the daily board.

**Breaks together.** A redesign that stops sending these fields (or renames them) changes stored
progression, because the server does not compute them from anything else.

**Load-bearing.** The split is a product decision (a manual tracker); where the boundary falls is
accidental and inconsistent — the rank-exam path in the same codebase does the opposite
(`08` §T-8).

---

### R-12 — Generated artifacts and dead code are committed beside live code, with no `.gitignore` (makes the audit harder; one part changes behaviour if deleted)

**Measured.** Tracked: **1533 files under `frontend/node_modules/`, 11 under `frontend/dist/`,
35 `__pycache__` files**; there is no `.gitignore` in the repository root. Dead code: **9 of 40
components (1285 lines)** unreachable by any code path (`05` §4.1), **5 exported API wrappers** with
zero references (§4.2), **49 of 121 routes** with no client consumer (`07` §4), and the four tracker
domains with full server CRUD and no renderer (`06` §D-09).

**Coupled to.** Nothing at runtime — except two things that matter. `VocabularyOverlay.jsx:142,
:161` are the **only written record of two endpoints that do not exist**, i.e. the only evidence of an
intended feature (`07` §5); and `frontend/dist/` is committed, so a stale bundle can be served
alongside current source (U-02).

**Breaks together.** Deleting the dead UI removes that evidence; trusting `dist/` misrepresents the
current source.

**Load-bearing.** No for the shipped product; yes for the audit's completeness. This is the entry
that most inflates the size of everything else: 1533 of 1741 tracked files are `node_modules`.

---

### R-13 — Contract drift already exists in fourteen places (ACCIDENTAL)

**Measured.** Enumerated in `10` §C5. The subset that would break a redesign if inherited as truth:
rank-exam questions unanswerable (`RankExamScreen.jsx:162` tests `'mcq'` vs the backend's
`'multiple_choice'`), the dual `card.id` id space across three review endpoints, the monthly boss
claim endpoint with no caller (`main.py:1246-1267`), the review XP display with no award
(`VocabularyWorkspace.jsx:861`), the unreachable `uncomplete` route by construction (`main.py:1078`),
**21 paths with no `response_model`** and `SummaryOut.player: dict` (`07` §6.1-6.2).

**Coupled to.** The client's expectations and any redesign that starts from observed behaviour.

**Breaks together.** The two phantom endpoints and the four dead wrappers disappear with the dead UI
(R-12); the response-model gaps would silently re-shape if someone tightened them.

**Load-bearing.** No — but they make current behaviour an unreliable specification.

---

### R-14 — The read/write fan-out amplifies any new field (ACCIDENTAL)

**Measured.** One quest completion = **1 write + 11 reads**; a cold boot issues **13 loader requests**
plus `/auth/me`; the `loadWeeklyMission` loader has 3 call sites; 8 GETs write (`08` §5, §6.1).

**Coupled to.** Every screen that renders quest, summary or mission data — because adding a field means
deciding which of the 11 loaders refetches it.

**Breaks together.** Nothing immediately; the cost is change amplification, and the staleness
patterns already documented (boss battles are fetched only at mount, `07` §7.2).

**Load-bearing.** No. Accidental.

---

### R-15 — The dev surface is unauthenticated and destructive (ACCIDENTAL as a production path)

**Measured.** `POST /api/dev/reset` (`main.py:1498-1583`, 88-line handler) disables foreign-key
checks, nulls `Players.active_campaign_id`/`account_id` and `Campaigns.campaign_template_id`, then
deletes across the model list (including `AccountSession`, `main.py:1523`) and reseeds — with **no auth
dependency and no environment gate**. `/api/dev/run_migrations` and `/api/dev/regenerate-quests` are
likewise open, and the third resolves `Player.first()` via `get_player_or_404` (`main.py:1880`). Total:
**3 of the 14 unauthenticated routes.**

**Coupled to.** The whole database; and the seeding path (R-6), since reset re-runs it.

**Breaks together.** One request removes all data. Reachability is by curl, not by any UI path
(`09` §7).

**Load-bearing.** For the development workflow, plausibly; as an exposed surface, accidental.

---

### R-16 — Session state and cross-tab assumptions (ACCIDENTAL)

**Measured.** The access token lives in `localStorage` (`client.js:3`); there is no `storage`
listener; the refresh cookie is scoped `path=/api/auth`; `error.sessionExpired` is set and never read
(`client.js:71`); the exported `refreshTokens` wrapper is dead while `client.js` refreshes internally.

**Coupled to.** R-10 (session lifetime) and R-14 (parallel requests).

**Breaks together.** A second tab neither learns about a logout nor shares a refresh; two parallel
401s can end a session (U-37).

**Load-bearing.** No.

---

## 2. Load-bearing versus accidental

| Load-bearing (removing it changes what the product does) | Accidental (removing it changes only how the code is arranged) |
| --- | --- |
| R-1 recompute-on-read and its 33 call sites | R-1's *frequency* (8 of them being GETs) |
| R-2 `campaign_skill_states` writers as a set | R-2's *multiplicity* (17 direct writes vs 1 recompute) |
| R-3 the recompute rules | R-3's *inconsistency* about which account |
| R-4 the routes and auth per handler | R-4's single-module shape |
| R-5 the markdown curriculum as the content source | R-5's resolution order landing on an empty file |
| R-6 startup migration + seeding | R-6 running on every boot |
| R-7 the thirteen client-only rules | R-7's *location* (they could live either side) |
| R-8 the level curve being mirrored | R-8's other three duplications |
| R-10 the whole auth chain | R-10's secret fallback and no-grace rotation |
| R-11 the input/consequence split | R-11 where the boundary falls per endpoint |
| R-12 dead UI being dead | R-12 committed `node_modules`/`dist`/`__pycache__` and no `.gitignore` |
| — | R-9's coverage shape, R-13 the drift, R-14 the fan-out, R-15 the dev surface, R-16 session state |

---

## 3. What would break a redesign versus what only makes the audit harder

**Would break a redesign if not honoured** (these are load-bearing couplings with measured fan-in):

1. **R-1 + R-2 + R-3** — 33 recompute call sites and 30 mutation sites on the progression row. A
   redesign that writes progression directly will be overwritten by the next read.
2. **R-5 + R-6** — the curriculum is file content parsed at boot; a redesign that assumes content
   lives in the database will seed an empty plan.
3. **R-7** — thirteen rules exist only in the browser; a UI replacement deletes them.
4. **R-10** — 118 routes depend on one token chain, a public fallback secret, and a rotation rule
   with no grace window.
5. **R-11** — the server stores progression derived from client-posted values; a client that stops
   sending them changes the data.
6. **R-13** — the drift set: a redesign built on observed behaviour inherits four broken flows.

**Only makes the audit harder** (no runtime consequence):

1. **R-12** — dead UI, dead wrappers, 49 unconsumed routes, and 1579 tracked generated files with no
   `.gitignore`; also the `dist/` vs source question (U-02) and the two phantom endpoints whose only
   record is dead code.
2. **R-8** — the four duplicated tables: they confuse ownership but only two of them currently change
   behaviour (the level mirror is asserted by the only test; the weekly fallback is only reachable
   when `/weekly-mission/current` has not resolved).
3. **R-9** — the test boundary: it explains why the duplication is safe to keep, and it is why the
   server rules have no executable check here.
4. **R-14** — the read fan-out: it multiplies work, and it is the mechanism behind the staleness
   already documented.
5. **R-16** — session/tab behaviour: unobservable without a running browser.

---

## 4. Risks that cannot be settled without running the stack

`[UNRESOLVED]` — all of these are recorded in `03-unresolved.md`:

| Risk | Open question | ID |
| --- | --- | --- |
| R-1 | does removing the 8 GET-side refreshes change any observable value | U-32 |
| R-2/R-3 | can two writers race on `campaign_skill_states` | U-19 |
| R-3 | does a second account get an isolated campaign, or `Player.first()`'s | U-03 |
| R-5 | does a non-Docker boot actually resolve to the empty file and seed no plan | U-04 (needs a run) |
| R-9 | do the 68 backend tests pass, and against MySQL | U-04 |
| R-10 | is `JWT_SECRET_KEY` set anywhere real; is the host reachable over TLS | U-35, U-36 |
| R-10 | do two parallel refreshes kill a session | U-37 |
| R-10/R-16 | what a user actually sees when a session dies | U-34, U-25 |
| R-13 | the shape of the 21 routes with no `response_model` | U-29 |

---

## 5. What this register could not establish

- **No risk was observed at runtime.** Every entry is a static reading: the couplings are counts of
  call sites and writers, not measurements of failure. R-9 is the reason — the backend suite cannot
  run in this environment (U-04).
- **Nothing about performance.** The 1-write/11-read pattern (R-14), the 548-day streak replay
  (`services.py:519-551`) and the per-word vocabulary XP loop are described structurally; their cost
  was not measured.
- **Nothing about deployment topology** beyond the compose file (U-01, U-36), so R-15's real
  exposure and R-10's real key are bounded by what the repository shows.
- **Concurrency is wholly untested.** R-2's 30 mutation sites and R-10's rotation both raise racing
  questions that static reading cannot answer (U-19, U-37).
