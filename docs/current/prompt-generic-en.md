# Generic Codex Session Playbook and Prompt Library

This file is the generic English version of the Codex session workflow.

Use it when:

- you want a reusable Codex workflow across repositories
- the repo does not yet have strong local documentation
- you want a neutral prompt template before adapting it to a project

Use the repo-first guide instead when a repository already has a well-defined local workflow.

## 1. Generic Session Workflow

### Step 1. Load rules first

Start with the highest-priority project instructions:

1. repository rules file
2. README or project overview
3. active tracker or issue/task document
4. decision log or architecture notes
5. only then task-specific files

If the repo has no clear rules file, say that explicitly and proceed carefully.

### Step 2. Ground in the codebase

Before planning or coding:

- identify the subsystem involved
- inspect the relevant files
- find one existing pattern to follow
- confirm whether the task is planning, implementation, debugging, review, documentation, or migration

### Step 3. Lock the task contract

State:

- goal
- success criteria
- scope
- constraints
- risks

Do not silently invent missing requirements.

### Step 4. Plan when the task is not trivial

Create a plan first when the task:

- spans multiple files
- changes behavior
- changes APIs or schemas
- requires ordering
- has non-trivial validation

### Step 5. Execute in bounded slices

- keep the slice small
- avoid unrelated changes
- preserve existing conventions
- validate each slice before claiming completion

### Step 6. Validate

Preferred validation order:

1. syntax or type checks
2. focused tests or smoke checks
3. broader review only if the risk warrants it

### Step 7. Record context for the next session

Update the repo’s task tracker, validation notes, and change log according to the local documentation model.

### Step 8. Close the session cleanly

Record:

- what changed
- validation outcome
- remaining issues
- next recommended step

## 2. Generic Skill Selection Matrix

### Session start

- `context-engineering`
- `agent-skills:using-agent-skills`

### Planning

- `agent-skills:planning-and-task-breakdown`
- `codex-orchestrator`

### Backend work

- `backend-development`
- `fastapi-templates` when FastAPI is involved
- `agent-skills:api-and-interface-design` for public contracts
- `mysql` for MySQL schema/query work

### Frontend work

- `frontend-design`
- `agent-skills:frontend-ui-engineering`
- `web-design-guidelines`

### Debugging

- `agent-skills:debugging-and-error-recovery`
- `agent-skills:test-driven-development`

### Review

- `codex-reviewer`
- `agent-skills:code-review-and-quality`

### Documentation

- `agent-skills:documentation-and-adrs`

### Migration / deprecation

- `agent-skills:deprecation-and-migration`
- `mysql`
- `backend-development`

## 3. Generic Prompt Templates

### A. Generic session start

```text
Use $context-engineering and $agent-skills:using-agent-skills.
Ground yourself in this repository before proposing changes.

Read the repository rules, README, active task tracker, and decision log first.
Then inspect only the files relevant to this task: [insert task].

Return:
- current objective
- key constraints
- likely files involved
- recommended skill stack
- next step
```

### B. Generic planning prompt

```text
Use $agent-skills:planning-and-task-breakdown and $codex-orchestrator.
Do a read-only exploration first, then write a decision-complete plan for: [insert task].

Include:
- goal
- success criteria
- assumptions
- implementation order
- validation plan
```

### C. Generic implementation prompt

```text
Use the skills best matched to this task.
Implement this bounded change: [insert task].

Requirements:
- follow existing project patterns
- keep scope tight
- validate the changed behavior
- update the local task and documentation files before closing
```

### D. Generic review prompt

```text
Use $codex-reviewer and $agent-skills:code-review-and-quality.
Review this change in findings-first order.

Focus on:
- regressions
- behavior bugs
- missing validation
- contract drift
```

### E. Generic closeout prompt

```text
Use $agent-skills:documentation-and-adrs.
Close this session cleanly.

Record:
- what changed
- validation
- remaining issues
- next recommended step
```

## 4. Bad Prompt -> Better Prompt

Bad:

```text
Fix it.
```

Better:

```text
Use the skills that match this task.
First inspect the relevant code and identify the root issue for: [insert bug].
Then implement the smallest safe fix, validate it, and update the repo docs/tracker.
```

Bad:

```text
Refactor everything.
```

Better:

```text
Refactor only [insert subsystem] to improve [insert concrete goal].

Constraints:
- no unrelated cleanup
- no public contract changes unless explicitly approved
- run focused validation
```

## 5. Generic Checklists

### Start

- read project rules
- inspect only relevant files
- identify task type
- select skill stack
- state assumptions

### Execute

- keep scope bounded
- follow project patterns
- validate changes

### Close

- update task tracking
- update validation notes
- update changelog/history
- record next step
