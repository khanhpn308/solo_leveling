# Codex Session Playbook and Prompt Library

This file is the repo-first English guide for running effective Codex sessions in `IELTS Quest Dashboard`.

Use it when you want:

- a consistent session workflow
- better prompts
- correct skill selection
- clean handoff between sessions

## 1. Session Workflow

### Step 1. Load context in the correct order

For this repo, always start with:

1. `AGENTS.md`
2. `README.md`
3. `TASKS.md`
4. `DECISIONS.md`
5. `docs/current/CONTEXT_INDEX.md`

Then load only the docs and files relevant to the current task.

Do not start by reading:

- old changelog history
- long historical notes
- unrelated source trees

### Step 1A. Expand context by task type

After the base load order, load only the smallest additional context needed for the task.

#### For backend tasks

Load next:

- relevant backend entrypoints under `backend/app/`
- the matching service, schema, and model files
- `docs/current/DATABASE_SCHEMA.md` if behavior depends on stored state
- `docs/current/SCHEMA_SEMANTICS.md` if field meaning matters

Typical examples:

- endpoint change:
  - route file
  - service file
  - schema file
- state or data behavior change:
  - service file
  - model file
  - schema snapshot / semantics docs

#### For migration or database tasks

Load next:

- latest relevant Alembic revisions
- `backend/app/models.py`
- `docs/current/DATABASE_SCHEMA.md`
- `docs/current/SCHEMA_SEMANTICS.md`
- `docs/history/MIGRATION_HISTORY.md` if the task extends earlier rollout waves

Do not start writing a migration before checking:

- current invariants
- existing rollout pattern
- validation expectations

#### For frontend tasks

Load next:

- the target component
- directly related data/utility files
- one nearby component that shows the current visual and state pattern
- `docs/current/PROJECT_CONTEXT.md` when the task affects product presentation

If the task affects backend-fed UI state, also inspect the matching API consumer or view-model path.

#### For documentation tasks

Load next:

- the canonical doc that should become the source of truth
- the matching history docs only if needed for factual evidence
- `DECISIONS.md` if the change records a durable rule or workflow

Prefer updating canonical docs from current repo truth, not by copying old history logs.

#### For review tasks

Load next:

- the changed files or diff
- one adjacent file for pattern comparison if needed
- `TASKS.md` and `DECISIONS.md` when behavior intent is unclear
- `docs/history/TEST_REPORT.md` when validation claims must be checked

#### For debugging tasks

Load next:

- the failing code path
- the nearest relevant test, if it exists
- the exact runtime error or failing command output

Do not load broad history first. Reproduce and localize before widening context.

### Step 1B. Stop rules for context loading

Stop loading more files when all of these are true:

- you know the task type
- you know the likely files to touch
- you have one existing pattern to follow
- you can state the goal, constraints, and next step clearly

If you are still loading context after that point, you are probably adding noise instead of signal.

### Step 2. Ground in the repo

Before planning or coding, do a short grounding pass:

- confirm current task state in `TASKS.md`
- confirm latest accepted decisions in `DECISIONS.md`
- inspect only the relevant code paths
- confirm whether the task is:
  - planning
  - implementation
  - debugging
  - review
  - documentation
  - migration

### Step 3. Lock the task contract

State these explicitly:

- goal
- success criteria
- in scope
- out of scope
- constraints
- risks

If a high-impact ambiguity remains, stop and ask.

### Step 4. Plan before broad execution

Use a plan first when the task:

- touches multiple files
- changes backend behavior
- changes schema or API contracts
- affects migrations
- needs sequencing or validation strategy

Good plan outputs are:

- bounded
- decision complete
- testable
- small enough to implement in one focused session or one worker slice

### Step 5. Execute in a bounded slice

Implementation rule:

- touch only what the task needs
- follow existing project patterns
- avoid unrelated cleanup
- keep a single slice verifiable

### Step 6. Validate

Preferred order:

1. syntax / type checks
2. focused smoke checks
3. tests for changed behavior
4. review if the task is medium or high risk

Do not mark work complete without verification evidence.

### Step 7. Update docs and trackers

After meaningful implementation, update:

1. `TASKS.md`
2. `docs/history/TEST_REPORT.md`
3. `docs/history/AGENT_NOTES.md`
4. `docs/history/changelogs.md`
5. `DECISIONS.md` or an ADR if the decision is durable

### Step 8. Close the session cleanly

Before ending a session, record:

- what changed
- what passed validation
- what remains open
- what the next session should read first

The next session should not need to reconstruct state from raw chat history.

## 2. Skill Selection Matrix

Use the smallest useful set of skills.

### Session start / context reset

- Primary:
  - `context-engineering`
- Supporting:
  - `agent-skills:using-agent-skills`

Use when:

- starting a fresh session
- switching task domains
- output quality is drifting

### Planning

- Primary:
  - `agent-skills:planning-and-task-breakdown`
- Supporting:
  - `codex-orchestrator`

Use when:

- task is larger than one obvious edit
- work needs sequencing
- implementation should be delegated later

### Documentation and rationale capture

- Primary:
  - `agent-skills:documentation-and-adrs`

Use when:

- decisions should survive the session
- API, migration, or workflow behavior changes
- future agents need context

### Backend implementation

- Primary:
  - `backend-development`
- Supporting:
  - `fastapi-templates`
  - `agent-skills:api-and-interface-design`
  - `mysql` for schema, query, or migration work

### Frontend implementation

- Primary:
  - `frontend-design` or `agent-skills:frontend-ui-engineering`
- Supporting:
  - `web-design-guidelines`
  - `agent-skills:browser-testing-with-devtools`

### Debugging

- Primary:
  - `agent-skills:debugging-and-error-recovery`
- Supporting:
  - `agent-skills:test-driven-development`

### Review

- Primary:
  - `codex-reviewer`
- Supporting:
  - `agent-skills:code-review-and-quality`

### Migration / deprecation

- Primary:
  - `agent-skills:deprecation-and-migration`
- Supporting:
  - `mysql`
  - `backend-development`

### Session close

- Primary:
  - `agent-skills:documentation-and-adrs`
- Supporting:
  - `codex-orchestrator`

## 3. Prompt Templates

### A. Session start prompt

Use when starting a new session.

Skills:

- `context-engineering`
- `agent-skills:using-agent-skills`

Prompt:

```text
Use $context-engineering and $agent-skills:using-agent-skills.
Ground yourself in this repo before proposing changes.

Read in this order:
1. AGENTS.md
2. README.md
3. TASKS.md
4. DECISIONS.md
5. docs/current/CONTEXT_INDEX.md

Then inspect only the files relevant to this task: [insert task].

Return:
- current objective
- constraints
- files likely involved
- recommended skill stack
- next step
```

### B. Planning prompt

Use when the task is medium or high risk.

Skills:

- `agent-skills:planning-and-task-breakdown`
- `codex-orchestrator`

Prompt:

```text
Use $agent-skills:planning-and-task-breakdown and $codex-orchestrator.
Do a read-only exploration first, then produce a decision-complete plan for: [insert task].

Include:
- goal and success criteria
- assumptions
- implementation order
- validation steps
- docs/tracker updates required
```

### C. Backend implementation prompt

Skills:

- `backend-development`
- `fastapi-templates`
- `agent-skills:api-and-interface-design`
- `mysql` when needed

Prompt:

```text
Use $backend-development $fastapi-templates $agent-skills:api-and-interface-design.
If this task touches schema, queries, or migrations, also use $mysql.

Implement this bounded backend task: [insert task].

Requirements:
- follow existing backend patterns
- keep API response shapes stable unless explicitly requested
- run focused validation
- update TASKS.md, docs/history/TEST_REPORT.md, docs/history/AGENT_NOTES.md, and docs/history/changelogs.md
```

### D. Frontend implementation prompt

Skills:

- `frontend-design` or `$agent-skills:frontend-ui-engineering`
- `web-design-guidelines`

Prompt:

```text
Use $frontend-design and $web-design-guidelines.
Implement this bounded frontend task: [insert task].

Requirements:
- preserve the current visual language unless this task is a redesign
- verify responsive behavior
- avoid generic UI output
- update relevant docs/history files after implementation
```

### E. Debugging prompt

Skills:

- `agent-skills:debugging-and-error-recovery`
- `agent-skills:test-driven-development`

Prompt:

```text
Use $agent-skills:debugging-and-error-recovery and $agent-skills:test-driven-development.
Reproduce, localize, fix, and guard this issue: [insert bug].

Return:
- root cause
- minimal fix
- validation proof
- regression guard
```

### F. Review prompt

Skills:

- `codex-reviewer`
- `agent-skills:code-review-and-quality`

Prompt:

```text
Use $codex-reviewer and $agent-skills:code-review-and-quality.
Review this change in findings-first order.

Focus on:
- regressions
- logic bugs
- migration/data risks
- missing tests
- contract drift
```

### G. Documentation-only prompt

Skills:

- `agent-skills:documentation-and-adrs`

Prompt:

```text
Use $agent-skills:documentation-and-adrs.
Update repository documentation for this change: [insert change].

Requirements:
- capture decisions and rationale, not just edits
- keep canonical docs concise
- keep history docs factual
- preserve the root -> current -> history documentation model
```

### H. Session close prompt

Skills:

- `agent-skills:documentation-and-adrs`
- `codex-orchestrator`

Prompt:

```text
Use $agent-skills:documentation-and-adrs and $codex-orchestrator.
Close this session cleanly.

Do all of the following:
- summarize what changed
- record validation
- update TASKS.md
- update docs/history/TEST_REPORT.md
- update docs/history/AGENT_NOTES.md
- update docs/history/changelogs.md
- list the next best task
```

## 4. Bad Prompt -> Better Prompt

### Example 1. Vague bug fix

Bad:

```text
Fix backend bug.
```

Better:

```text
Use $agent-skills:debugging-and-error-recovery and $agent-skills:test-driven-development.
Investigate why `/api/checkins` returns inconsistent results after recent migration work.

First reproduce and isolate the cause.
Then implement the smallest safe fix.
Run focused validation and update the repo history docs.
```

### Example 2. Unbounded backend change

Bad:

```text
Refactor the backend.
```

Better:

```text
Use $backend-development $fastapi-templates $agent-skills:api-and-interface-design.
Refactor only the quest completion flow so typed tracker writes are easier to maintain.

Constraints:
- no API response shape changes
- no schema changes
- keep current behavior intact
- run focused smoke checks
```

### Example 3. Risky migration request

Bad:

```text
Update the database.
```

Better:

```text
Use $mysql $backend-development $agent-skills:planning-and-task-breakdown.
Explore the current schema and write a decision-complete migration plan for: [insert migration goal].

Do not implement yet.
Include:
- data risks
- ordering
- rollback expectations
- validation checklist
```

### Example 4. Docs-only cleanup

Bad:

```text
Update docs.
```

Better:

```text
Use $agent-skills:documentation-and-adrs.
Update the canonical docs to reflect the new backend behavior for [insert feature].

Keep:
- source-of-truth docs concise
- rationale explicit
- history docs updated separately
```

## 5. Session Checklists

### Start checklist

- read root entrypoints
- load only relevant canonical docs
- identify task type
- choose skill stack
- state assumptions

### Execution checklist

- keep scope bounded
- verify against current patterns
- validate before claiming completion
- update trackers immediately after major progress

### Close checklist

- update `TASKS.md`
- update `docs/history/TEST_REPORT.md`
- update `docs/history/AGENT_NOTES.md`
- update `docs/history/changelogs.md`
- record next best task

## 6. Minimum Validation Matrix By Task Type

Use this as the minimum acceptable validation set before calling a task complete.

### Backend task

Minimum:

- syntax check for touched backend files
- one focused API or service smoke check for the changed behavior
- update `docs/history/TEST_REPORT.md`

Add more when applicable:

- schema-aware checks if response shape or state interpretation changed
- targeted regression test if the same bug could easily return

### Migration or database task

Minimum:

- syntax check for the migration file and touched backend files
- migration upgrade on the local target database
- SQL or schema inspection proving the intended structural change
- one post-migration smoke check for the affected behavior
- update `docs/history/TEST_REPORT.md`

Add more when applicable:

- duplicate/null audits before hardening
- downgrade verification if rollback safety is part of the task

### Frontend task

Minimum:

- build or syntax validation for touched frontend code
- one runtime or visual verification of the affected surface
- update `docs/history/TEST_REPORT.md`

Add more when applicable:

- browser walkthrough for layout or interaction changes
- targeted component or view-model test if the repo has one

### Debugging task

Minimum:

- reproduce the issue or identify a clear failing condition
- validate that the fix removes the failure
- validate one nearby path that could regress
- update `docs/history/TEST_REPORT.md`

### Review-only task

Minimum:

- inspect the diff or changed files directly
- verify stated validation evidence if it is central to the review
- produce findings-first output

### Documentation-only task

Minimum:

- verify the changed docs reflect current repo truth
- verify links or references if paths changed
- update `docs/history/changelogs.md`

### Session-close-only task

Minimum:

- `TASKS.md` reflects current state
- validation notes are current
- change log is updated
- next recommended step is explicit

## 7. Glossary

### Platform-level protocol

Rules enforced by the agent platform or runtime itself.

Examples:

- which channels exist
- when tools can be called
- approval or sandbox rules
- tool input/output constraints
- plan-mode vs execution-mode restrictions

Project docs can explain these, but they do not control them.

### Repo operating standard

The workflow standard used inside this repository.

Examples in this repo:

- which docs to read first
- which tracker files must be updated
- which prompt guide to use
- how sessions are closed and documented

This is project-level guidance, not platform-level enforcement.

### Skill

A reusable workflow or instruction bundle for a task type.

Examples:

- `context-engineering`
- `backend-development`
- `mysql`
- `agent-skills:documentation-and-adrs`

### Harness

The surrounding agent execution environment that provides tools, modes, channels, and runtime controls.

### Orchestrator

The coordinating agent that:

- reads context
- decides scope
- creates plans
- delegates or sequences work
- checks completion

### Worker

The implementation-focused agent or session slice that executes one bounded task.

## 8. Recommended Defaults For This Repo

- Use a plan first for backend, migration, or multi-file work.
- Use `mysql` whenever a task touches schema, indexes, or migration safety.
- Use `documentation-and-adrs` whenever the change would confuse a future session if left undocumented.
- Prefer small bounded implementation slices over broad “fix everything” prompts.
- Keep canonical docs current and history docs factual.
