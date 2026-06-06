# Changelog

Newest first.

## [2026-06-06 12:05] Add glossary to repo-first prompt guides

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Clarify platform-level protocol vs repo workflow terms in the repo-first prompt guides

### 1. Summary

Added a short glossary to the repo-first English and Vietnamese prompt guides so future sessions can distinguish platform-level protocol, repo operating standard, skill, harness, orchestrator, and worker.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/current/prompt-en.md` | Modified | glossary section | Added a short terminology section for platform/runtime vs repo workflow concepts. |
| `docs/current/prompt-vi.md` | Modified | glossary section | Added the same glossary in Vietnamese. |
| `docs/history/TEST_REPORT.md` | Modified | top section | Added validation note for this documentation refinement. |
| `docs/history/AGENT_NOTES.md` | Modified | top section | Added a factual note about the glossary addition. |
| `docs/history/changelogs.md` | Modified | top entry | Added this implementation record. |

### 3. Features added

- [x] Glossary for platform-level protocol
- [x] Glossary for repo operating standard
- [x] Glossary for skill, harness, orchestrator, and worker

### 4. Bugs fixed

- [x] Reduced terminology ambiguity in the repo-first prompt guides.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only refinement.
Repo-first prompt guides now include a glossary for core runtime and workflow terms.
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- If needed later, add a short “who controls what” note for operators who are new to agent tooling.

### 10. User review checklist

- [ ] I reviewed the glossary additions.
- [ ] I confirmed the terminology is clear.
- [ ] I approved this task.

## [2026-06-06 11:55] Add minimum validation matrix to repo-first prompt guides

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Add task-specific minimum validation guidance to the repo-first Codex guides

### 1. Summary

Extended the repo-first prompt guides with a minimum validation matrix so future sessions know the smallest acceptable verification set for backend, migration, frontend, debugging, review-only, documentation-only, and session-close-only tasks.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/current/prompt-en.md` | Modified | validation/checklist section | Added a minimum validation matrix by task type in English. |
| `docs/current/prompt-vi.md` | Modified | validation/checklist section | Added the same minimum validation matrix in Vietnamese. |
| `docs/history/TEST_REPORT.md` | Modified | top section | Added validation note for this documentation refinement. |
| `docs/history/AGENT_NOTES.md` | Modified | top section | Added a factual note about the new validation matrix. |
| `docs/history/changelogs.md` | Modified | top entry | Added this implementation record. |

### 3. Features added

- [x] Minimum validation baseline for backend tasks
- [x] Minimum validation baseline for migration/database tasks
- [x] Minimum validation baseline for frontend tasks
- [x] Minimum validation baseline for debugging, review-only, documentation-only, and session-close-only tasks

### 4. Bugs fixed

- [x] Removed the remaining gap where the repo-first guides described workflow but not the minimum acceptable verification set per task type.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only refinement.
Repo-first guides now define:
- base load order
- task-specific context expansion
- minimum validation matrix by task type
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- If needed later, add one final refinement: a task-specific session-close matrix by task type.

### 10. User review checklist

- [ ] I reviewed the repo-first prompt guides.
- [ ] I checked the validation matrix additions.
- [ ] I approved this task.

## [2026-06-06 11:45] Expand repo-first prompt guides with task-specific context loading

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Add task-specific context-loading guidance to the repo-first Codex guides

### 1. Summary

Extended the repo-first prompt guides so they do more than list the base file load order. They now tell future agents exactly what extra context to load for backend, migration, frontend, documentation, review, and debugging tasks, and when to stop loading more files to avoid context noise.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/current/prompt-en.md` | Modified | Step 1 section | Added task-specific context expansion rules and context stop rules in English. |
| `docs/current/prompt-vi.md` | Modified | Bước 1 section | Added the same repo-first context expansion rules and stop rules in Vietnamese. |
| `docs/history/TEST_REPORT.md` | Modified | top section | Added validation note for this documentation refinement. |
| `docs/history/AGENT_NOTES.md` | Modified | top section | Added a factual note about the new task-specific context-loading rules. |
| `docs/history/changelogs.md` | Modified | top entry | Added this implementation record. |

### 3. Features added

- [x] Task-specific context-loading guidance for repo-first backend work
- [x] Task-specific context-loading guidance for migration/database work
- [x] Task-specific context-loading guidance for frontend, docs, review, and debugging work
- [x] Context stop rules to prevent overloading sessions

### 4. Bugs fixed

- [x] Removed the gap where the repo-first guides only defined the base load order but not the next files by task type.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only refinement.
Repo-first prompt guides now define both:
- base load order
- task-specific context expansion rules
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Add one more refinement later if needed: task-specific “minimum validation set” per task type.

### 10. User review checklist

- [ ] I reviewed the repo-first prompt guides.
- [ ] I checked the added task-specific loading rules.
- [ ] I checked the stop rules.
- [ ] I approved this task.

## [2026-06-06 11:35] Split generic Codex playbooks from repo-first playbooks

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Add a generic Codex workflow layer without replacing the existing repo-first guides

### 1. Summary

Added a second layer of Codex guidance for cross-repo use. The repository now has both generic and repo-first prompt playbooks. The generic files are reusable across projects, while the original `prompt-en.md` and `prompt-vi.md` remain the local operator guides for `IELTS Quest Dashboard`.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/current/prompt-generic-en.md` | Added | full file | Added a generic English Codex session playbook and prompt library for reuse across repositories. |
| `docs/current/prompt-generic-vi.md` | Added | full file | Added a generic Vietnamese Codex session playbook and prompt library. |
| `README.md` | Modified | canonical docs map + Codex workflow section | Added links to the generic guides and clarified generic vs repo-first usage. |
| `AGENTS.md` | Modified | current canonical docs list | Added the generic guides to the canonical docs map. |
| `docs/current/CONTEXT_INDEX.md` | Modified | canonical docs list | Added load guidance that distinguishes generic vs repo-first prompt docs. |
| `DECISIONS.md` | Modified | prompt-playbook decision | Clarified that both generic and repo-first prompt playbooks are maintained. |
| `TASKS.md` | Modified | session resume + tracker + references | Recorded the generic guides as completed documentation work. |
| `docs/history/TEST_REPORT.md` | Modified | top section | Added validation result for the generic split and rerun link scan counts. |
| `docs/history/AGENT_NOTES.md` | Modified | top section | Added a factual note about the new generic layer. |
| `docs/history/changelogs.md` | Modified | top entry | Added this task record. |

### 3. Features added

- [x] Generic English Codex playbook
- [x] Generic Vietnamese Codex playbook
- [x] Clear separation between generic and repo-first operator guidance

### 4. Bugs fixed

- [x] Removed ambiguity about whether the existing prompt guides were generic or repo-specific.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 docs/current/prompt-en.md
Get-Content -Encoding UTF8 docs/current/prompt-vi.md
Get-Content -Encoding UTF8 README.md
Get-Content -Encoding UTF8 docs/current/CONTEXT_INDEX.md
python - <local markdown link scan>
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Added generic prompt guides successfully.
Kept repo-first guides intact.
local markdown links checked: 89
broken local links: 0
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Use the generic guides as a reusable baseline and the repo-first guides for actual work inside this repository.

### 10. User review checklist

- [ ] I reviewed the generic guides.
- [ ] I checked the separation between generic and repo-first docs.
- [ ] I checked the updated links.
- [ ] I approved this task.

## [2026-06-06 11:20] Add bilingual Codex prompt playbooks

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Implement the repo-first Codex session playbook and prompt library in Vietnamese and English

### 1. Summary

Implemented the Codex session playbook and prompt library as two repo-first operator guides: an English canonical version and a Vietnamese working version. The new guides define the full session lifecycle from context loading through planning, execution, validation, documentation, and session close, and include skill-mapped prompt templates for common task types.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/current/prompt-en.md` | Added | full file | Added the canonical English session playbook, skill matrix, prompt templates, bad-vs-better examples, and session checklists. |
| `docs/current/prompt-vi.md` | Added | full file | Added the Vietnamese operator version of the same workflow and prompt library. |
| `README.md` | Modified | canonical docs map + Codex workflow section | Added links to the new prompt guides and a short “Working With Codex” section. |
| `AGENTS.md` | Modified | current canonical docs list | Added both prompt guides to the canonical repo docs map. |
| `docs/current/CONTEXT_INDEX.md` | Modified | canonical docs list | Added load guidance for `prompt-en.md` and `prompt-vi.md`. |
| `DECISIONS.md` | Modified | accepted decisions | Added the decision that prompt playbooks are the standard Codex session guidance for this repo. |
| `TASKS.md` | Modified | session resume + documentation tracker + references | Recorded the new prompt playbooks as complete documentation work and added them to the “read more” section. |
| `docs/history/TEST_REPORT.md` | Modified | top section | Added documentation validation note for the new prompt guides. |
| `docs/history/AGENT_NOTES.md` | Modified | top section | Added a factual note about the bilingual prompt playbooks. |
| `docs/history/changelogs.md` | Modified | top entry | Added this implementation record. |

### 3. Features added

- [x] English Codex session playbook for this repo
- [x] Vietnamese Codex session playbook for this repo
- [x] Skill-to-task prompt matrix using installed local skills
- [x] Start / plan / implement / validate / document / close prompt templates

### 4. Bugs fixed

- [x] Reduced future session ambiguity around how to prompt Codex effectively in this repo.
- [x] Added a stable place to document skill usage by task type.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
Get-Content -Encoding UTF8 README.md
Get-Content -Encoding UTF8 AGENTS.md
Get-Content -Encoding UTF8 docs/current/CONTEXT_INDEX.md
Get-Content -Encoding UTF8 DECISIONS.md
Get-Content -Encoding UTF8 TASKS.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\context-engineering\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\agent-skills\skills\documentation-and-adrs\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\agent-skills\skills\planning-and-task-breakdown\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\codex-orchestrator\SKILL.md
Get-Content -Encoding UTF8 C:\Users\Admin\.agents\skills\agent-skills\skills\using-agent-skills\SKILL.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only change.
Bilingual prompt guides added successfully.
Canonical docs map updated.
No repo-managed markdown links were broken by the change.
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Use the new prompt playbooks to drive the next backend-test planning and implementation session.

### 10. User review checklist

- [ ] I reviewed the new prompt guides.
- [ ] I checked the skill mappings.
- [ ] I checked the updated canonical doc links.
- [ ] I approved this task.

## [2026-06-06 10:45] Repository-wide stale-link scan after documentation reorganization

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Verify repo-wide documentation links after the `docs/current` / `docs/history` restructure

### 1. Summary

Confirmed that the environment can run an automated repo-wide stale-link scan and used it to validate the reorganized documentation layout. Parsed all local markdown links in repo-managed docs, resolved each relative path from its source file, and verified target existence. No broken local markdown links were found.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `docs/history/TEST_REPORT.md` | Modified | top section | Added the stale-link scan validation snapshot and exact scan counts. |
| `docs/history/AGENT_NOTES.md` | Modified | top section | Added a short factual note for the automated stale-link scan result. |
| `docs/history/changelogs.md` | Modified | top entry | Added this validation record. |

### 3. Features added

- [x] Automated repo-wide markdown stale-link verification for the reorganized docs layout.

### 4. Bugs fixed

- [x] Confirmed there are no broken local markdown links left by the documentation move.

### 5. Code removed

- [ ] None

### 6. Commands run

```bash
rg -n "AGENT_NOTES\.md|TEST_REPORT\.md|changelogs\.md|docs/PROJECT_CONTEXT\.md|docs/MVP_BUSINESS_RULES\.md|docs/DATABASE_SCHEMA\.md|docs/FRONTEND_PLAN\.md|docs/history/changelogs\.md|docs/history/TEST_REPORT\.md|docs/history/AGENT_NOTES\.md|docs/current/PROJECT_CONTEXT\.md|docs/current/BUSINESS_RULES\.md|docs/current/DATABASE_SCHEMA\.md|docs/current/SCHEMA_SEMANTICS\.md" -g "*.md" .
rg -n "\]\(([^)]+)\)" -g "*.md" .
python - <markdown-link existence scan>
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
markdown files scanned: 18
local markdown links checked: 69
broken local links: 0
```

### 8. Remaining issues

- [ ] Browser visual walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Move on to automated backend tests, since documentation link integrity is now verified.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the validation counts.
- [ ] I confirmed the documentation links are clean.
- [ ] I approved this task.

## [2026-06-06 10:30] Documentation and context reorganization

**Agent:** coder-gpt54  
**Status:** Done  
**Related task:** Reorganize repository documentation for low-noise context loading

### 1. Summary

Reworked the repository documentation layout so future sessions can load context quickly without reading large historical dumps first. Reduced root documentation to entrypoint files, created clear canonical and history layers under `docs/current/` and `docs/history/`, rewrote the root docs in English, added schema semantics and a documentation ADR, and reordered changelog history to newest-first.

### 2. Files changed

| File | Change type | Changed lines / area | What changed |
| --- | --- | --- | --- |
| `README.md` | Modified | full file | Rewrote as a concise project entrypoint with docs map and context load order. |
| `AGENTS.md` | Modified | full file | Rewrote repo agent guide, added official load order, and required newest-first changelog rule. |
| `TASKS.md` | Modified | full file | Compressed into an active tracker and recorded the documentation reorganization as completed. |
| `DECISIONS.md` | Modified | full file | Rebuilt as a short decision ledger with links to migration history and the new ADR. |
| `docs/current/CONTEXT_INDEX.md` | Added | full file | Added canonical context-loading map. |
| `docs/current/PROJECT_CONTEXT.md` | Added | full file | Added current product and user context summary. |
| `docs/current/BUSINESS_RULES.md` | Added | full file | Added English business-rule summary for progression and quest behavior. |
| `docs/current/DATABASE_SCHEMA.md` | Added | full file | Added current schema snapshot summary after Wave E. |
| `docs/current/SCHEMA_SEMANTICS.md` | Added | full file | Added field-semantics reference for rank, quest role, scope, and related state meanings. |
| `docs/current/decisions/ADR-001-documentation-layout-and-context-loading.md` | Added | full file | Recorded the documentation split and context-loading decision. |
| `docs/history/AGENT_NOTES.md` | Added | full file | Rebuilt as newest-first short factual history notes. |
| `docs/history/TEST_REPORT.md` | Added | full file | Rebuilt as newest-first validation snapshots. |
| `docs/history/changelogs.md` | Added | full file | Rebuilt changelog as newest-first recent history. |
| `docs/history/MIGRATION_HISTORY.md` | Added | full file | Added condensed Wave A-E migration summary. |
| `docs/history/FRONTEND_PLAN.md` | Added | full file | Added historical note for the earlier frontend plan. |
| `AGENT_NOTES.md` | Deleted | full file | Removed root history file after moving history to `docs/history/`. |
| `TEST_REPORT.md` | Deleted | full file | Removed root history file after moving history to `docs/history/`. |
| `changelogs.md` | Deleted | full file | Removed root history file after moving history to `docs/history/`. |
| `docs/PROJECT_CONTEXT.md` | Deleted | full file | Removed old location after canonical doc split. |
| `docs/MVP_BUSINESS_RULES.md` | Deleted | full file | Removed old location after canonical doc split. |
| `docs/DATABASE_SCHEMA.md` | Deleted | full file | Removed old location after canonical doc split. |
| `docs/FRONTEND_PLAN.md` | Deleted | full file | Removed old location after history doc split. |

### 3. Features added

- [x] Official root-first context load order
- [x] Canonical current-doc layer
- [x] History-doc layer
- [x] Schema semantics reference
- [x] Documentation ADR

### 4. Bugs fixed

- [x] Removed historical noise from `TASKS.md`.
- [x] Removed mixed-purpose root documentation layout.
- [x] Fixed changelog ordering so new entries are at the top.

### 5. Code removed

- [x] Removed old root history files.
- [x] Removed superseded doc locations under `docs/`.

### 6. Commands run

```bash
Get-Content -Encoding UTF8 TASKS.md
Get-Content -Encoding UTF8 AGENT_NOTES.md
Get-Content -Encoding UTF8 changelogs.md
Get-Content -Encoding UTF8 README.md
Get-Content -Encoding UTF8 DECISIONS.md
Get-Content -Encoding UTF8 docs/PROJECT_CONTEXT.md
Get-Content -Encoding UTF8 docs/MVP_BUSINESS_RULES.md
```

### 7. Validation result

- [x] Passed
- [ ] Failed
- [ ] Not run

Details:

```text
Documentation-only change.
Root entrypoint rewrite complete.
Canonical/history split complete.
Changelog ordering normalized to newest-first.
```

### 8. Remaining issues

- [ ] Browser walkthrough is still pending.
- [ ] Automated backend tests are still pending.

### 9. Suggested next step

- Add automated backend tests for the post-migration backend behavior, then return to deferred legacy cleanup planning.

### 10. User review checklist

- [ ] I reviewed the changed files.
- [ ] I checked the changed areas.
- [ ] I checked the documentation layout.
- [ ] I checked the validation notes.
- [ ] I approved this task.

## [2026-06-06 00:23] Wave E constraint hardening

Status: `Done`

- Hardened write paths before DDL.
- Applied fail-fast migration `20260606_08_wave_e_constraint_hardening.py`.
- Enforced `NOT NULL` campaign scope on target tables.
- Added composite uniqueness for check-ins and daily quest slots.

## [2026-06-05 23:57] TASKS cleanup after Wave D

Status: `Done`

- Removed stale wave-start markers.
- Narrowed open work to real remaining backend/documentation items.

## [2026-06-05 23:38] Wave D backend cutover

Status: `Done`

- Cut skill progression over to `campaign_skill_states`.
- Cut badge reads over to `badge_unlocks`.
- Scoped campaign-facing reads and typed quest completion writes.

## [2026-06-05 22:30] Wave C data backfill

Status: `Done`

- Backfilled campaign scope and typed-link fields.
- Seeded campaign-scoped mutable state rows.

## [2026-06-05 22:01] Wave B additive state tables

Status: `Done`

- Added `campaign_skill_states`.
- Added `badge_unlocks`.
- Synced backend seed-facing English copy.

## [2026-06-05 21:24] Wave A scope and typed-link foundation

Status: `Done`

- Added nullable campaign columns and typed-link columns.
- Applied migration and validated the schema upgrade locally.
