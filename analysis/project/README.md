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
  only as strong as the search. The pass-1 absence claims are tabulated in `03-unresolved.md` §E.

**Additional methods introduced in pass 2** (all mechanical, over files that were read):

- **Import-graph reachability** — every component name was grepped across `frontend/src` excluding
  its own file, and the five `React.lazy` dynamic imports in `App.jsx:27-31` were checked
  separately, to separate renderable UI from dead UI (`05` §4.1).
- **Two-inventory comparison** — the client's API paths (62 normalised) were set-differenced against
  the server's routes (121 routes → 105 normalised templates). Because the client composes some
  paths from variables, this diff produces **false negatives**; every candidate gap was then checked
  by hand (`06` §4, `03` §F U-10).
- **Constant/string cross-checks** for wiring defects, e.g. the rank-exam `'mcq'` vs
  `'multiple_choice'` comparison was confirmed by grepping both string literals on both sides
  (`06` §D-11a).

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
  coupling claim (e.g. 33 `refresh_progress_state` call sites, 30 mutation sites on
  `campaign_skill_states` across 6 functions) rather than an impression of tightness.
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
- HEAD: `1b6def3 ui_mobile` (`git log --oneline -1`).
- Tracked files: 1741 (`git ls-files | wc -l`), of which **1533 are `frontend/node_modules/`**.
- Working tree at audit time contained **pre-existing, not-mine** changes: `docker-compose.yml`
  modified (see `01-discovery-inventory.md` §Infra) and an untracked `.freebuff/` directory.
  Nothing was reverted, staged, or touched.
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

## Out of scope so far

Mission sections 3+ (feature-by-feature analysis, data-model semantics, gap analysis, target-state
design). No proposal, recommendation or redesign language appears in these documents. The audit
deliberately maps the repo **on its own terms** and maps toward no external or separately
reverse-engineered reference UI. Product-intent documents (`spec/`, `docs/`, `TASKS.md`,
`DECISIONS.md`) were inventoried and are cited **only as claims to be checked against code**, never
as ground truth; where they disagree with the code, the disagreement is recorded rather than
resolved (`04` §5).
