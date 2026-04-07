# Compatibility Check Workflow

Purpose: define the operational workflow for compatibility review in Plant-GUI.
This file is the active procedure for AI-assisted checks, developer reviews,
and final compatibility patches.

This file is intentionally shorter and more procedural than the earlier
prompt-heavy version. The goal is to make the workflow easier to audit, easier
to turn into a skill, and safer to explain to the team.

---

## Active Compatibility Doc Set

Use these files together:

| File | Role | Update Frequency |
|------|------|------------------|
| `docs/Compatibility/COMPAT_CHECK.md` | Operational workflow and output contract | When the process changes |
| `docs/Compatibility/SCHEMA_SNAPSHOT.md` | Current persisted compatibility baseline; the judge for drift | When the compatibility version is bumped |
| `docs/Compatibility/SCHEMA_HISTORY.md` | Version-to-version map plus integrated decision summary | When the compatibility version is bumped |
| `docs/Compatibility/COMPAT_VISUAL_DECK.md` | Slide-style walkthrough for team review and onboarding | When the workflow or mental model changes |

Historical analysis notes live in `docs/Compatibility/archive/`.

---

## Decision Log Policy

For the current team size, a separate `DECISION_LOG.md` is not required.

Instead:

- record per-version migration and library decisions in
  `docs/Compatibility/SCHEMA_HISTORY.md`
- keep `SCHEMA_HISTORY.md` compact, but include the decision summary that
  explains *why* a version bump happened and *how* the change should be handled
- only split out a dedicated decision log later if one version regularly needs
  more than a few bullets, or if ownership/approval tracking becomes complex

What must be recorded somewhere for each released compatibility version:

- version and previous version
- migration key(s)
- runtime baseline reference
- change classification
- changed persistence/runtime layers
- decision summary
- evidence pointers

Important: the raw Excel file already exists in the repo. What the history must
capture is not the workbook contents themselves, but the *compatibility
decision* made from those workbook changes.

---

## Team Rule: Do Not Invent Domain Semantics

Compatibility tooling may detect changes. It must not silently invent
chemical-engineering meaning.

Default rule:

- additive change: auto-refresh is acceptable only when the change is clearly
  additive and low-risk
- delete change: do not silently remap by guesswork
- rename/replace change: do not infer mappings from string similarity alone
- semantic/default-value change: treat as domain-owner review unless the rule
  was already explicitly approved and recorded

If a change requires a domain decision, the developer/assistant must:

1. mark it as `manual-review-required` or `domain-owner-decision-required`
2. avoid presenting an inferred mapping as fact
3. record the final decision in `SCHEMA_HISTORY.md` when the version is bumped

---

## Recommended Entry Points

Preferred skill-style entry:

```text
Run Plant-GUI compat-check in 1N mode for the current unreleased compatibility scope.
```

Fallback chat entry:

```text
Read and execute docs/Compatibility/COMPAT_CHECK.md now.
If mode is missing, ask for 1N / 1Y / 2N / 2Y.
```

Shortcuts:

- `1N` = development tweak/test + compatibility patch only
- `1Y` = development tweak/test + include revert/rollback evaluation
- `2N` = ready for full compatibility + compatibility patch only
- `2Y` = ready for full compatibility + include revert/rollback evaluation

If no mode is supplied and the review can still proceed, assume `1N` and say so
explicitly.

---

## Workflow

### Step 0 - Determine Workflow State

Decide whether the pass is:

- `development tweak/test`
- `ready for full compatibility`

Rules:

- `development tweak/test` means the developer is still iterating, validating,
  or debugging
- in `development tweak/test`, do not bump compatibility version, do not edit
  `VERSION_ORDER`, and do not add migrations in the same change
- `ready for full compatibility` means the change set is stable and the
  developer wants the actual compatibility patch now

### Step 0.5 - Decide Whether Revert / Rollback Evaluation Is In Scope

If requested, compare:

- patch forward with compatibility updates
- git/code revert
- diagram backup rollback/restore

Never conflate them:

- git revert does not restore already-upgraded diagram data
- diagram rollback does not revert repository code

If revert/rollback evaluation is in scope, also read:

- `docs/usercustom/developer-rollback-prompts.md`

### Step 1 - Determine Review Scope

Define two scopes:

1. `diff under review`
2. `unreleased compatibility scope`

Rules:

- use the exact pasted diff/range if the user supplied one
- otherwise, if the worktree is dirty, use `git diff HEAD` as the local overlay
- determine the `unreleased compatibility scope` from the last accepted
  compatibility baseline up to current `HEAD`
- do not limit compatibility scope to only the current author's commits
- if the worktree is dirty, treat uncommitted changes as an overlay on top of
  the unreleased compatibility scope, not as the whole compatibility event

Baseline anchors:

- `docs/Compatibility/SCHEMA_SNAPSHOT.md`
- `docs/Compatibility/SCHEMA_HISTORY.md`
- `src/src/backend/utils/schemaMigrations.ts`

If library/runtime changes are in scope, also include git history touching:

- `src/excel-sheets/`
- `src/excel-migration/`
- `src/src/backend/routes/dataRoutes.ts`
- `src/src/backend/utils/diagramLibraryRefresh.ts`
- `src/src/backend/utils/diagramCompatibility.ts`

### Step 2 - Classify The Change

Classify the unreleased compatibility scope into exactly one bucket:

- `schema-only`
- `library-additive`
- `library-rename`
- `library-delete`
- `mixed`

Definitions:

- `schema-only`: persisted diagram/snapshot/database shape changed, but the
  runtime library contract did not
- `library-additive`: workbook/runtime catalog added optional or additive items
- `library-rename`: workbook/runtime catalog changed identifiers or names
- `library-delete`: workbook/runtime catalog removed items or made them vanish
  from the accepted live baseline
- `mixed`: both persisted shape and runtime library contract changed

This repo currently uses a single compatibility version axis. In a `2N` or
`2Y` pass, any `library-*` or `mixed` result that changes saved-diagram
compatibility normally advances `CURRENT_SCHEMA_VERSION`, even when the
persisted JSON shape is unchanged.

### Step 3 - Read Current Context

Always read:

- `src/src/backend/utils/schemaMigrations.ts`
- `docs/Compatibility/SCHEMA_SNAPSHOT.md`
- `docs/Compatibility/SCHEMA_HISTORY.md`
- `docs/usercustom/saved/AI_DEVELOPMENT_WORKFLOW.md`

When the classification is not `schema-only`, also inspect:

- `src/excel-migration/`
- `src/src/backend/routes/dataRoutes.ts`
- `src/src/backend/utils/diagramLibraryRefresh.ts`
- `src/src/backend/utils/diagramCompatibility.ts`
- current Postgres-backed runtime contract (`Models`, `ModelVersion`, `Ports`,
  `VarNames`, `SystemVariables`) when DB access is available

### Step 4 - Compare Live Code vs Snapshot

Principle: `SCHEMA_SNAPSHOT.md` is the judge for current persisted structure.

Compare current code against the snapshot for:

- save payload shape
- `FullNetworkSnapshot`
- Prisma MongoDB models
- canvas node and edge stored shape

Keep these questions separate:

1. does the current diff change persisted structure?
2. does the unreleased compatibility scope change persisted structure or the
   runtime library contract?
3. does the current repo diverge from `SCHEMA_SNAPSHOT.md`?

### Step 5 - Inspect Runtime Library Impact

When classification is `library-*` or `mixed`, determine:

- what model/model-version/port/variable/default changed
- whether the change is additive, delete, rename, or semantic
- whether stored diagrams can be refreshed automatically
- whether compute/verify should be blocked
- whether old values should be preserved, removed, or explicitly remapped

Use DB truth checks that match the classification. Do not default to the
widest possible scan if a smaller targeted inspection is sufficient.

#### Step 5.1 - Excel Change Triage

When Excel / migrate.py changes are detected, produce an **Excel Change
Triage Table** before proceeding to the decision summary. For each detected
change, list:

| # | Model | Item Changed | Change Type | Affected Saved Diagrams | Recommended Handling | Status |
|---|-------|-------------|-------------|------------------------|---------------------|--------|

Change Type values: `var-added`, `var-removed`, `var-renamed`,
`var-default-changed`, `port-added`, `port-removed`, `model-added`,
`model-removed`, `model-renamed`, `version-added`, `version-removed`,
`uuid-regenerated`.

Recommended Handling values:
- `auto-refresh` — safe to merge additively on next open/save
- `auto-unverify` — clear verification; user re-checks manually
- `block-compute` — block computation until user resolves
- `silent-ok` — no user-facing impact
- `needs-developer-decision` — present options and wait for answer

After producing the table, **ask the developer** for each row marked
`needs-developer-decision`:

```
Excel change triage found N items requiring your decision:
  1. MODEL_X / VAR_Y was removed. Options:
     a) Treat as stale → auto-unverify + let user re-select
     b) Map to VAR_Z (renamed) → add migration mapping
     c) Preserve old value as-is (domain owner approved)
  Which option? (or describe a different handling)
```

Do not proceed to Step 6 until all `needs-developer-decision` rows have
a recorded answer. Record all answers in the decision summary.

### Step 6 - Produce A Decision Summary

Every compatibility pass must produce a `decision summary`, even in `1N`.

The summary must say:

- what changed
- what the system can safely do automatically
- what still requires a human decision
- what must be recorded later in `SCHEMA_HISTORY.md`

Use these decision statuses:

| Status | Meaning |
|--------|---------|
| `auto-safe` | Safe to perform automatically under the existing rule set |
| `manual-review-required` | The system can detect the issue but should not decide the fix |
| `domain-owner-decision-required` | A model writer / chemical engineer must decide the handling |

Decision rules by classification:

| Classification | Default Handling |
|----------------|------------------|
| `schema-only` | migration-driven; no workbook semantic decision required |
| `library-additive` | additive refresh allowed if clearly low-risk; flag required/new semantic values for review |
| `library-rename` | require explicit mapping; do not guess |
| `library-delete` | default to warning + auto-unverify + manual reselection unless a documented removal rule exists |
| `mixed` | combine the schema patch with the strictest required library decision path |

### Step 7 - Decide Patch Forward vs Revert / Rollback

Only do this when revert/rollback evaluation is in scope.

Recommend revert/rollback only when it is clearly safer, faster, or less risky
than patching forward.

### Step 8 - Apply The Compatibility Patch In `2N` / `2Y`

When the user wants the full compatibility patch now, update all affected
artifacts together:

- `CURRENT_SCHEMA_VERSION`
- `VERSION_ORDER`
- migration registry
- frontend compatibility/version constant if applicable
- `docs/Compatibility/SCHEMA_SNAPSHOT.md`
- `docs/Compatibility/SCHEMA_HISTORY.md`
- tests and fixtures

Do not bump the version without updating both snapshot and history.

---

## What To Record In `SCHEMA_HISTORY.md`

For each released compatibility version, record:

- version
- previous version
- migration key(s)
- runtime baseline reference
- classification
- changed layers
- decision summary
- main evidence

Record the compatibility decision, not the full workbook contents.

Good examples:

- "Added `MCP_OUT1/MCP_OUT2` to `MIXER/FLOW_MIX`; additive refresh allowed;
  missing required values remain manual review"
- "Removed `FLOW_FREE`; auto-unverify + manual reselection required; no
  automatic rename mapping approved"

Bad examples:

- "Excel changed"
- "Used a newer workbook"

---

## Output Contract For Each Run

### Compact Result Table

Return a compact table that includes at least:

- workflow state
- compatibility scope used
- diff / overlay used
- classification
- repo vs snapshot drift
- affected layers
- DB inspection status
- recommended action
- residual risk

### Required Narrative After The Table

After the table, include:

1. a short `decision summary`
2. a short `open questions / assumptions` block when needed
3. an `Options` section with concrete next actions

### Options Section

Include:

- 3-5 short action options
- the recommended option first
- one option named `Show detailed compatibility table`
- one `Workflow shortcuts` line listing `1N`, `1Y`, `2N`, `2Y`
- include `D` = show the detailed table for the same pass

---

## Minimal Prompt For Humans / Skills

Use this instead of pasting a giant custom prompt:

```text
You are the Plant-GUI compatibility checker.
Read and execute docs/Compatibility/COMPAT_CHECK.md.
Use docs/Compatibility/SCHEMA_SNAPSHOT.md as the current baseline.
Use docs/Compatibility/SCHEMA_HISTORY.md as the version-to-version map and integrated decision log.
If the mode is missing, ask for 1N / 1Y / 2N / 2Y, or assume 1N if the review can still proceed.
Produce the compact result table first, then the decision summary, assumptions, and options.
Do not invent chemical-engineering mappings without explicit owner approval.
```

---

## Maintenance Rules

- keep this file process-focused
- keep `SCHEMA_SNAPSHOT.md` structure-focused
- keep `SCHEMA_HISTORY.md` version-and-decision-focused
- keep historical assessments in `docs/Compatibility/archive/`
- if the procedure grows again, move examples and long checklists into
  reference docs instead of re-expanding this file into another giant prompt
