# Phase 3A.1 — Read-only architecture & product audit

Coverage so far:

- **Pass 1 — mission sections 0 and 1** (a) baseline repository discovery, and (b) the current
  system architecture *as it actually is*.
- **Pass 2 — mission questions 1, 2, 5, 6, 7** what the product does for its users, who those users
  and roles are, every frontend route, the navigation that exists, and the domain/capability
  inventory.
- **Pass 3 — mission questions 8 and 9** every interface the product exposes (routes, auth levels,
  request/response shapes or their absence, client consumers, and the realtime finding), and traced
  data flows from datastore to rendering component, with duplicate fetches, recompute-on-read and
  client/server shape disagreements called out.
- **Pass 4 — mission question 10** the authentication and authorization system end to end: credential
  issuance, storage and verification; token format, lifetime and client storage; every
  refresh/expiry/silent-retry path and what the UI leaves behind when a session dies; the account
  lifecycle; what authorization is enforced per route; the unauthenticated surfaces with their two
  distinct reachability paths; and the trust boundary the client is assumed to hold.
- **Pass 5 — mission questions 11, 12, 13** the boundary map: server-owned behaviour that defines the
  product (progression, XP arithmetic, quest scheduling, exam grading, spaced repetition, seeding),
  the presentation layers that hold no authority (with the ones that only look replaceable because
  they are the sole implementation of a rule), and the interfaces that cannot move — declared and
  de-facto shapes, enum literals, the auth surface, configuration, and the places already drifted.
- **Pass 6 — mission questions 14 and 15** the risk and coupling register as measurement (sixteen
  ranked entries, each with what it is coupled to, what breaks together, the counts and the command
  that produced them, and whether the coupling is load-bearing or accidental), separated into what
  would break a redesign versus what merely makes the audit harder; plus the consolidation of the
  unknowns list into one register organised by whether a person, runtime evidence or something outside
  the repository can answer each question.
- **Errata pass (post-audit)** an independent re-run of this audit's own commands; the corrections,
  the cross-reference repairs and the canonical measurement IDs are in §Mission question coverage,
  §Canonical measured facts and §Errata log. This pass edited figures, references and indices only —
  no finding, analysis or trace was rewritten.

Everything here is strictly read-only: no source edits, no renames/moves, no installs, no
implementation, router, navigation, contract, dependency or Docker changes were made.

## Files in this deliverable

| File | Contents |
| --- | --- |
| `README.md` | This file: what was done, how claims are evidenced, limits of the passes. |
| `01-discovery-inventory.md` | Pass 1. Baseline discovery grounded in real files: manifests, entry points, apps, services, DB code, realtime, proxy, infra, auth, shared/generated code, tests, scripts, CI, external integrations. |
| `02-current-architecture.md` | Pass 1. Architecture as-is: client, runtimes, datastores, caches, brokers, proxies, external services, network/service boundaries, and where authentication sits. |
| `03-unresolved.md` | All passes, consolidated. The audit's open-question register, organised by **who can answer each question** — §1 a person (20), §2 runtime evidence (11), §3 outside the repository (7) — plus §4 for the four questions closed during the audit and §5 the absence-claims appendix. Stable `U-01`…`U-42` IDs, cited by the other documents. |
| `04-product-and-users.md` | Pass 2. What the product does for its user, the user/target profile, the role model that exists, the single-user lifecycle, onboarding asks, what the product is *not*, product language, and doc-vs-code contradictions. |
| `05-frontend-routes-and-navigation.md` | Pass 2. The 4 routes, why nothing else is a route, the 6-destination drawer, second-level tabs, the navigation graph, a reachability audit, and the UI that exists but is unreachable. |
| `06-domain-capability-inventory.md` | Pass 2. 20 product domains with a reachability label each (LIVE / HALF-WIRED / BACKEND-ONLY / DEAD UI), plus cross-cutting findings. |
| `07-api-contract-reference.md` | Pass 3. The full 121-path route inventory (method, path, auth level, request model, response model or its absence, client consumer), the 49 unconsumed paths and 2 calls to nonexistent routes, contract-shape observations, and the realtime finding with all refetch triggers. |
| `08-data-flow-traces.md` | Pass 3. The layer stack, the session precondition, ten traced read/write flows from table to component, the double-fetch inventory, what is recomputed or written on read, client/server shape and naming disagreements, and a per-datum ownership table. |
| `09-authentication-and-authorization.md` | Pass 4. Where auth lives, the credential lifecycle (password, JWT, refresh cookie), the full dependency chain from header to scoped data, every refresh/expiry/session-death path with the resulting UI state, the account lifecycle, the four auth levels with the three scoping patterns, the 14 unauthenticated paths and their reachability through the app versus curl, and the client-supplied values the server treats as authority. |
| `10-boundary-map.md` | Pass 5. What must survive (the recompute chain and every rule it owns, the XP ledger and vocabulary XP formula, quest scheduling, exam grading, spaced repetition, seeding/self-migration), the honest list of rules that live only in the client, the component/style/view-model layers that hold no authority, the screens that only look replaceable, the frozen contracts (declared vs consumed field sets, enum literals, auth surface, configuration) and the already-drifted list. |
| `11-risk-and-coupling-register.md` | Pass 6. Sixteen ranked risks, each with its couplings, its measured evidence (fan-in counts, write-site counts, line counts, tracked-artifact counts and the command behind each), and a load-bearing-versus-accidental verdict; then the separation into redesign-breaking versus audit-complicating, and the risks that need a running stack. |

## Mission question coverage

The Phase 3A.1 mission posed fifteen numbered questions plus a section-0 baseline. The mission text
itself is **not in this repository** (searched: `grep -rn "3A\.1\|Phase 3A\|mission question"` over
every `*.md`/`*.txt`/`*.json` outside `analysis/` → 0 matches), so the labels below are reconstructed
from the pass briefs that named the question numbers, and the last column records what the deliverable
actually contains for each.

| Q | Question (as the pass briefs state it) | Answering document, by section | Coverage |
| --- | --- | --- | --- |
| **0** | Baseline repository discovery, and the current architecture as it actually is | `01` (all); `02` (all) | Answered |
| **1** | What the product does for its users | `04` §1, §3; capability labels in `06` §2–§3 | Answered |
| **2** | Who the users and roles are | `04` §2 (target user, the one role, the five lifecycle states) | Answered |
| **3** | **Frontend structure** (framework, entry points, routing model, component/state organisation, styles, client derivation layer) | `01` §3–§4, §12; `05` §1; `06` §1; `10` §B1–B3 | **Attributed here only** — see note below |
| **4** | **Backend structure** (framework, entry point, module layout, layering, schema/seed composition) | `01` §3, §5–§6; `02` §1–§5; `07` §1; `10` Part A | **Attributed here only** — see note below |
| **5** | Complete inventory of current frontend routes | `05` §1 (the four route branches, and §1.1 for what is *not* a route) | Answered |
| **6** | The navigation that currently exists | `05` §2 (drawer, second-level tabs, graph) and §3 (reachability) | Answered |
| **7** | Product domains / capabilities that currently exist | `06` §2–§3 (20 domains, labelled LIVE / HALF-WIRED / BACKEND-ONLY / DEAD UI) and §4 | Answered |
| **8** | Every interface the product exposes, and every realtime mechanism | `07` §1–§6 (all 121 paths) and §7 (the no-realtime finding, freshness mechanisms, refetch triggers) | Answered |
| **9** | Traced data flow from datastore through the service layer to the endpoint, then into the rendering component | `08` (all; ten traces, double-fetch inventory, recompute-on-read, ownership table) | Answered |
| **10** | How authentication and authorization work | `09` (all) | Answered |
| **11** | Business logic that must survive a UI redesign | `10` Part A (plus the CLIENT-ONLY list in §A9) | Answered |
| **12** | Frontend presentation layers safe to replace | `10` Part B (§B4 for the ones that only look replaceable) | Answered |
| **13** | Contracts that must not be broken | `10` Part C (§C5 for the already-drifted set) | Answered |
| **14** | Structurally risky or tightly coupled areas | `11` §1 (register), §2 (load-bearing vs accidental), §3 (redesign-breaking vs audit-complicating) | Answered |
| **15** | Consolidation of what remains unknown | `03` (all; §1 person, §2 runtime, §3 outside the repo, §4 closed, §5 absence claims) | Answered |

**On questions 3 and 4.** No pass in this audit was labelled with questions 3 or 4 — passes 1–6 claim
questions 0–1, 1/2/5/6/7, 8–9, 10, 11–13 and 14–15 respectively — so before this table the numbering
gap was ambiguous: a reader could not tell whether frontend and backend structure had been dropped,
deferred, or folded into another question. They were **covered, but never attributed**: frontend
structure is the subject of `01` §4 (the 53-file `frontend/src` surface, entry point, router, API
layer, styles, build config) and of `05`/`06`/`10` Part B; backend structure is the subject of `01`
§5–§6 (the eight modules, route declaration style, DB and seeding code) and of `02` §1–§5 and `07`
§1. Both are also answered implicitly by their questions' documents. The rows above supply the
attribution; no re-reading was done to produce them, and neither row is claimed as a complete
structural survey of the kind a pass of its own would have produced. `[DERIVED]`

Two numbering systems appear in the briefs and they are not the same axis: **mission sections** (pass 1
covered sections 0 and 1; "sections 3+" are out of scope per §Out of scope so far) and the **fifteen
numbered questions** above. The question rows are what this table attributes; the section boundaries
say only how the mission was carved up for delivery.

---

## Canonical measured facts

Every count that more than one document states is owned **here** and cited elsewhere by its `MF-nn`
ID. Other documents name the ID instead of re-deriving the number, so a correction has exactly one
home. All values were produced by the commands shown, re-run against the tree at the HEAD recorded
under §Repo state; where a figure has two legitimate values, the definition is stated rather than one
number being picked.

**Terminology, stated once, because three different counts are routinely confused in this domain:**

| Term | Definition |
| --- | --- |
| **decorator line / route decorator** | one line matching `^@app.<method>("…")` in `backend/app/main.py`; three handlers carry two, so this equals the count of distinct `(method, path)` pairs |
| **handler function** | one `def` reached from one or more route decorators |
| **path template** | a distinct path string, ignoring which method(s) decorate it |
| **model / table** | one `class` in `models.py` with a `__tablename__` (the three counts below coincide) |

| ID | Fact | Value | Command that produces it |
| --- | --- | --- | --- |
| **MF-01** | Route decorator lines = distinct `(method, path)` pairs | **121** | `grep -cE "^@app\\.(get\|post\|put\|patch\|delete)" backend/app/main.py` |
| **MF-02** | Route handler functions | **118** | `awk '/^@app\\.(get\|post\|put\|patch\|delete)\\(/ {dec=1; next} dec && /^(async )?def / {n++; dec=0} END {print n}' backend/app/main.py` |
| **MF-03** | Distinct path templates | **105** | `grep -oE "^@app\\.(get\|post\|put\|patch\|delete)\\(\"[^\"]+\"" backend/app/main.py \\| sed -E 's/.*\\(\"//; s/\"$//' \\| sort -u \\| wc -l` |
| **MF-04** | Route decorators by method | GET **59**, POST **51**, PATCH **3**, PUT **1**, DELETE **7** (=121) | `grep -oE "^@app\\.(get\|post\|put\|patch\|delete)\\(\"" backend/app/main.py \\| sed 's/^@app\\.//; s/(\"//' \\| sort \\| uniq -c` |
| **MF-05** | Routes with **no** auth dependency | **14** | signature scan of each decorator+handler block for `get_current_player`/`get_current_account`/`get_current_campaign`/`Depends(security)`; the 14 are listed in `02` §6.3 and `09` §7 |
| **MF-06** | Authenticated routes | **107** of 121 `(method, path)` pairs = **104** of 118 handler functions | 121 − 14 (MF-01, MF-05), and 118 − 14 (MF-02, MF-05) |
| **MF-07** | Routes by most restrictive auth dependency | `none` **14**, `account` **3**, `player` **37**, `campaign` **67** (=121) | classification of the MF-05 signature scan; raw dependency counts: `grep -oE "Depends\\([a-zA-Z_]+" backend/app/main.py \\| sort \\| uniq -c` |
| **MF-08** | Routes declaring no `response_model` | **21** (100 declare one) | `grep -c "response_model=" backend/app/main.py` → 100; MF-01 − 100 |
| **MF-09** | `models.py` model/table count | **72** (`class` = `__tablename__` = `Base` subclass = 72) | `grep -c "__tablename__" backend/app/models.py`; `grep -c "^class " backend/app/models.py` |
| **MF-10** | `schemas.py` Pydantic classes | **119** | `grep -c "^class " backend/app/schemas.py` |
| **MF-11** | Module sizes (lines) | `main.py` **2874**, `services.py` **3267**, `seed.py` **2784**, `models.py` **1559**, `schemas.py` **1272**, `database.py` **67**, `auth_utils.py` **74** | `wc -l backend/app/*.py` |
| **MF-12** | `refresh_progress_state` references / call sites | **38** references (**34** in `main.py` = 1 import + **33** call sites; 4 in `services.py`) | `grep -c refresh_progress_state backend/app/main.py` → 34; `grep -c refresh_progress_state backend/app/services.py` → 4 |
| **MF-13** | Route sites that call `refresh_progress_state` | **32** = **8 GET** + 24 write (16 POST, 3 PATCH, 1 PUT, 4 DELETE), plus 1 startup call = the 33 of MF-12 | per-handler body scan; the 8 GETs are `/api/summary`, `/api/profile`, `/api/skills`, `/api/main-quests`, `/api/quests`, `/api/quests/today`, `/api/badges`, `/api/weakness-suggestions` |
| **MF-14** | Attribute-write sites on `campaign_skill_states` (the six progression columns `xp`, `rank`, `level`, `confirmed_rank`, `pending_rank`, `promotion_status`) | **32** across **7** functions: `recompute_skill_progress` 12, `apply_rank_suggestion` 8, `submit_rank_exam` 7, `award_skill_xp` 2, `unlock_rank_exam` 1, `start_rank_exam` 1, `submit_vocabulary_boss_result` 1 | `grep -hoE '\\.(xp\|rank\|level\|confirmed_rank\|pending_rank\|promotion_status) *[+*-]?=' backend/app/main.py backend/app/services.py \\| wc -l` → 32; attributed to enclosing `def` by line scan |
| **MF-15** | `db.commit()` / `db.flush()` per module | `main.py` **35 / 12**, `services.py` **37 / 10**, `seed.py` **1 / 43** | `grep -c 'db.commit()'` and `grep -c 'db.flush()'` per file |
| **MF-16** | `seed.py` top-level functions / `ensure_*` functions | **52** / **23** | `grep -c "^def " backend/app/seed.py`; `grep -c "^def ensure_" backend/app/seed.py` |
| **MF-17** | Alembic revisions | **31** | `ls backend/alembic/versions/*.py \\| wc -l` |
| **MF-18** | Backend tests (read, never executed here) | **68** tests across **11** classes | `grep -c "def test_" backend/app/test_backend.py` → 68; `grep -c "^class .*Test"` → 11 |
| **MF-19** | Frontend components / stateless / unreachable | **40** components; **21** call `useState` zero times; **9** (**1285** JSX lines) are reachable from no code path | `ls frontend/src/components/*.jsx \\| wc -l`; `grep -c "useState("` per file; import-graph reachability (`05` §4.1) |
| **MF-20** | Client derivation layer and stylesheet | `dashboard-data.js` **817** lines, **25** exported functions (**35** top-level `function` declarations); `styles.css` **6276** lines | `wc -l frontend/src/dashboard-data.js frontend/src/styles.css`; `grep -cE "^(export )?function" frontend/src/dashboard-data.js` |
| **MF-21** | Client API paths vs server path templates vs unconsumed | **62** normalised client paths (64 raw); **105** server templates (MF-03); **49** paths with no client consumer | two-inventory comparison (`07` §1, §4; method in §Evidence convention above) |
| **MF-22** | `frontend/src` files | **53** | `find frontend/src -type f \\| wc -l` |
| **MF-23** | Tracked files at HEAD `3fc4261` | **1754** = `frontend/node_modules/` **1533** + `analysis/project/` **12** + `frontend/dist/` **11** (9 of them under `dist/assets/`) + `__pycache__` **35** + **163** other | `git -c safe.directory='*' ls-files \\| wc -l`, filtered per prefix |

Two facts whose apparent disagreement is definitional, so both are recorded: `frontend/dist/` holds
**11** tracked files of which **9** are bundles under `assets/` (MF-23) — documents say either number;
and `models.py` has **72** classes/tables (MF-09) — the pass-6 documents said 57, corrected in §Errata
log.

## Evidence convention

Every non-trivial claim is followed by a file reference, and the audit distinguishes what was
actually opened from what was only inferred:

- `path:line` — a path that was **opened and read** during this pass. Line numbers refer to the
  working-tree state described in §Repo state below.
- `[DERIVED]` — a conclusion produced by a mechanical scan over files that were read (e.g. a route
  inventory extracted with `grep`/`sed`/`awk` over `backend/app/main.py`). The command is stated
  where it matters.
- `[UNRESOLVED]` — asserted only as an open question; it is also listed in `03-unresolved.md`.
- Absence claims ("there is no X") are stated with the exact search that failed, because absence is
  only as strong as the search. The pass-1 absence claims are tabulated in `03-unresolved.md` §5.

**Additional methods introduced in pass 2** (all mechanical, over files that were read):

- **Import-graph reachability** — every component name was grepped across `frontend/src` excluding
  its own file, and the five `React.lazy` dynamic imports in `App.jsx:27-31` were checked
  separately, to separate renderable UI from dead UI (`05` §4.1).
- **Two-inventory comparison** — the client's API paths (62 normalised) were set-differenced against
  the server's routes (121 routes → 105 normalised templates). Because the client composes some
  paths from variables, this diff produces **false negatives**; every candidate gap was then checked
  by hand (`06` §4, `03` §4 U-10).
- **Constant/string cross-checks** for wiring defects, e.g. the rank-exam `'mcq'` vs
  `'multiple_choice'` comparison was confirmed by grepping both string literals on both sides
  (`06` §3 D-11 item (a)).

**Additional methods introduced in pass 3** (all mechanical, over files that were read):

- **Decorator/signature extraction** — every `@app.<method>` decorator, its handler signature and its
  `response_model` were dumped and classified, producing the 121-path / 118-function inventory and
  the auth-level distribution (`07` §1–§2).
- **Call-site dump** — every `api(` / `apiFetch(` hit in `frontend/src` was read, with dynamically
  composed paths resolved by hand, to decide each route's consumer column and to find calls with no
  matching route (`07` §§3–5).
- **Budget/curve cross-checks** — numeric constants used for progression were grepped on both sides
  of the wire (e.g. `1200`/`2500`/`4500` return zero matches in `backend/app/`, establishing that the
  client's skill ladder has no server counterpart — `08` §7.1).
- **Call-graph tracing** — each flow in `08` was traced as a chain of explicit `path:line` hops
  (table → model → service → route → schema → client → component), so any hop can be re-verified on
  its own.

**Additional methods introduced in pass 4** (all mechanical, over files that were read):

- **Value-set enumeration for lifecycle states** — every write of a status-like column was grepped
  on both the application and seeder sides (e.g. `Account.status` yields exactly `"active"` and
  `"locked"`), so the documented state machine is the observed one rather than an assumed one.
- **Key-name reconciliation across configuration surfaces** — a variable's presence was checked in
  `auth_utils.py`, `.env.example` and `docker-compose.yml` *together*, which is how the
  `JWT_SECRET_KEY` fallback was shown to be live in the shipped composition (`09` §2.3).
- **Sentence-level tracing of the client error path** — the 401 branch in `App.jsx:146-158` was read
  as executable control flow (including that the bare `return` suppresses the rethrow) and then
  matched against each loader's `catch`/`finally`, producing the failure-state table in `09` §4.4.

**Additional methods introduced in pass 5** (all mechanical, over files that were read):

- **De-facto vs declared contract measurement** — property accesses in the client
  (`grep -rho "\bquest\.[a-z_]*"` and the same for `profile.`/`skill.`) were counted and set against
  the declared `response_model` width, which is how `QuestOut`'s 40 declared fields were narrowed to
  21 consumed ones (`10` §C1).
- **Both-owner pairing** — every duplicated rule was pinned by naming the server file *and* the
  client file together, which is what distinguishes a deliberate mirror (the level curve, asserted by
  a test) from two independent implementations of the same idea (the weekly mission patterns).
- **State-surface census** — each component was counted for `useState` calls and line length, giving
  the 21-stateless / 19-stateful split and the per-component table in `10` §B1, so "presentation
  only" is a measurement rather than a judgement.

**Additional methods introduced in pass 6** (all mechanical, over files that were read):

- **Fan-in counting** — each shared function's references were counted per file
  (`grep -c "\b<name>\b" main.py services.py seed.py`), producing the call-site numbers behind every
  coupling claim (e.g. 33 `refresh_progress_state` call sites — MF-12 — and 32 attribute-write sites on
  `campaign_skill_states` across 7 functions — MF-14) rather than an impression of tightness.
- **Write-site attribution** — for each mutable column the assignment was grepped and attributed to
  its enclosing function with `awk`, which is how the single-writer columns (all `players.*` except
  `player_xp`) were separated from the six-writer progression row.
- **Resolution-order tracing** — the seeder's file-resolution candidates were read in order *and*
  each candidate checked for existence and size, which is how `backend/material.md` was found to be
  0 bytes while the mounted copy is 238 258 bytes (this closed U-09 and produced risk `11` R-5).
- **Config-presence sweep** — tracked filenames were filtered for tooling patterns and 13 conventional
  CI paths were probed at once, producing the two absence claims in `03` §5 (no lint/type config, no
  CI) as exhaustive rather than inspection-based.

No claim in this deliverable is inferred from a folder name. Where a name is suggestive but the
contents were not read, it is marked `[UNRESOLVED]` instead of described.

## Secrets handling

Secret **values** are not reproduced anywhere in this deliverable. Environment variable **key
names** are listed for `.env.example` only; other credential-bearing literals found in tracked
files are reported by location and nature, not by value. See §Notable security observations in
`01-discovery-inventory.md`.

## Repo state this audit was taken against

- Branch: `main` (`git branch --show-current`).
- HEAD at audit time: `1b6def3 ui_mobile`. **HEAD at the errata pass: `3fc4261 add_analysis`**, which
  committed these twelve documents together with the two pre-existing working-tree changes below.
  No file the deliverable describes changed between the two commits
  (`git -c safe.directory='*' diff --stat 1b6def3 3fc4261 -- . ':(exclude)analysis'` →
  `.freebuff/project-id` added, `docker-compose.yml` 1 insertion / 1 deletion), and the working tree
  is clean at the errata pass.
- Tracked files: **1741** at audit time (`git ls-files | wc -l`), of which **1533 are
  `frontend/node_modules/`**; **1754** at the errata pass (MF-23), the difference being the 12
  documents in `analysis/project/` plus `.freebuff/project-id`.
- The two **pre-existing, not-mine** working-tree changes present at audit time were left untouched:
  `docker-compose.yml` modified (one line — `VITE_API_URL` from a public IP to
  `http://localhost:8000/api`; see `01-discovery-inventory.md` §8, `docker-compose.yml:48`) and an untracked `.freebuff/`
  directory. Both were committed by `3fc4261`. No claim in the deliverable depended on the superseded
  value: `10` §C4 records the `localhost` value, which is what the working tree held while the audit
  read it.
- `git` required an inline `-c safe.directory='*'` because the checkout is reached through a
  `\\wsl.localhost\...` UNC path; no git config was modified.
- Tooling actually available in the audit shell: `node v24.19.0`, `npm 11.17.0`. **No working
  Python interpreter**, so no backend code was executed. `rg` was unavailable; `grep`/`sed`/`awk`
  were used instead.

## What was actually verified by execution

- `frontend/src/dashboard-data.test.js` was run with `node --test`: **6 tests, 6 pass, 0 fail**.
  (`npm run test:dashboard-data` itself cannot run here — `npm` shells out through `cmd.exe`,
  which rejects the UNC working directory. The equivalent direct invocation was used.)
- Nothing else was executed in either pass. No dev server was started, no container was built or
  run, no port was probed, and no browser session was opened. Backend tests were **read, not run**
  — see `03-unresolved.md` U-04. Everything in this deliverable is therefore a **static**
  description of the code; runtime behaviour is asserted only where the code path is unambiguous,
  and is otherwise deferred to `03-unresolved.md`.

## Errata log (post-audit corrections)

An independent pass re-ran the commands behind this audit's numbers and found four defect classes.
Each is recorded here with the evidence that corrects it, the `MF-nn` ID that now owns the number, and
the sites changed. Nothing else in the twelve documents was edited; the audit's findings stand.

| # | Defect | Correction | Evidence / owner | Sites changed |
| --- | --- | --- | --- | --- |
| E-1 | Four documents said `models.py` holds **57 models**, contradicting `02` §5 in the same document, which said 72 | **72** classes/tables | `grep -c "__tablename__" backend/app/models.py` → **72**; `grep -c "^class "` → **72** (MF-09) | `01` §5, `02` §6.3, `06` §3 D-20, `08` §1 |
| E-2 | **118** was used as a *path* count in four places. 118 is the **handler-function** count (MF-02), not a path count; the authenticated path count is 121 − 14 = **107** (MF-06) | authenticated `(method, path)` pairs = **107**; authenticated handler functions = **104**; 118 retains its own meaning as handlers | MF-01, MF-02, MF-05, MF-06; the unauthenticated 14 are listed in `02` §6.3 and `09` §7 | `09` §10, `11` R-4, `11` R-10 (×2), `11` §3 |
| E-3 | `11` R-2's writer table undercounted `apply_rank_suggestion` (5, was 8) and overcounted `recompute_skill_progress` (13, was 12), giving 30 sites across "six functions" when the total is **32 across seven** | writer table re-measured; derived totals in R-2, §2, §3 and §5 corrected (20 direct writes vs 12 recompute) | `grep -hoE '\\.(xp\|rank\|level\|confirmed_rank\|pending_rank\|promotion_status) *[+*-]?=' backend/app/main.py backend/app/services.py \\| wc -l` → **32**, attributed to enclosing `def` (MF-14) | `11` R-2, §2, §3, §5 |
| E-4 | Six cross-references still pointed at the pre-consolidation section labels of `03-unresolved.md` (`§E`/`§F`/`§G`/`§H`), and five citations used `06 §D-11a`, which is an inline label at `06:393–394`, not a section | `§E`→`§5`, `§F`→`§4`, `§G`→`§4`, `§H`→`§1`/`§3` as applicable; `06 §D-11a`→`06` §3 D-11 item (a) | `03-unresolved.md` headings (`§1`–`§5`); `06` §3 D-11's items are labelled (a)/(b)/(c) at `06:220`, `:234` | `04` §2.2, `04` §3, `08` §9, `09` §11, `README` §Evidence convention, `03` §1, `06` §4, `10` Part C |

Two further figures that were **stale rather than wrong** are corrected in place: the `dashboard-data.js`
function count in `02` §7 ("31 pure builder functions" → **25 exported functions / 35 top-level
`function` declarations**, MF-20) and `11` R-4's longest-handler list, re-measured with a stated
definition (span from the `def` line through the last non-blank body line: `submit_rank_exam` and
`start_rank_exam` **103**, `reset_database` **86**, `register` **74**, `get_collocation_levels` **66**,
`get_summary` **65**, `login` **62**, `activate_campaign` **54**). Repo-state drift found while
re-running the commands — HEAD has moved and these documents are now committed — is recorded under
§Repo state.

## Out of scope so far

Mission sections 3+ (feature-by-feature analysis, data-model semantics, gap analysis, target-state
design). No proposal, recommendation or redesign language appears in these documents. The audit
deliberately maps the repo **on its own terms** and maps toward no external or separately
reverse-engineered reference UI. Product-intent documents (`spec/`, `docs/`, `TASKS.md`,
`DECISIONS.md`) were inventoried and are cited **only as claims to be checked against code**, never
as ground truth; where they disagree with the code, the disagreement is recorded rather than
resolved (`04` §5).
