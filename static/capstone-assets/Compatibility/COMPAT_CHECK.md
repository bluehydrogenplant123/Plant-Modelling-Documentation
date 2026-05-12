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
| `docs/Compatibility/RUNTIME_BASELINE.json` | Accepted Excel baseline for the current merged version | When a new workbook baseline is accepted |
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
If mode is missing, show 1N / 1Y / 2N / 2Y / DB / RC options and wait.
```

Shortcuts:

- `1N` = development tweak/test + compatibility patch only
- `1Y` = development tweak/test + include revert/rollback evaluation
- `2N` = ready for full compatibility + compatibility patch only
- `2Y` = ready for full compatibility + include revert/rollback evaluation
- `DB` = saved-diagram audit only; scan existing diagrams in the current
  database and do not mutate them
- `RC` = release/compute readiness; DB audit plus real-server upgrade and
  smoke-compute acceptance path

If no mode is supplied, do not start the review. Show a short option menu and
wait for the developer to choose `1N`, `1Y`, `2N`, `2Y`, `DB`, or `RC`.

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

### Step 0.75 - Decide Whether Saved-Diagram DB Audit Is In Scope

Saved-diagram DB audit is in scope when:

- the developer selects `DB`
- the developer asks about existing saved diagrams, old diagrams, or "all
  diagrams"
- the question is why missing or stale Excel/runtime items did not appear in a
  repo-only compatibility result
- a `2N` or `2Y` result would otherwise conclude saved-diagram safety without
  live database evidence

Rules:

- keep repo/worktree compatibility review separate from live DB saved-diagram
  audit
- do not claim that existing diagrams are clean unless this audit, or an
  equivalent live route smoke check, was actually run
- report the database/environment being scanned before interpreting results
- scan existing diagrams without mutation by default
- report counts for scanned diagrams, missing `runtimeBaselineRef`, stale
  `runtimeBaselineRef`, blocked compatibility issues, unscannable diagrams, and
  representative diagram IDs
- when blocked compatibility issues are found, produce a developer decision
  table before proposing migration or backfill code
- if DB access is unavailable, say `DB inspection not run` and keep old-diagram
  risk as `manual-review-required`

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

### Step 2.5 - Choose The Compatibility Version Bump

Use semantic compatibility versions as `major.minor.patch`.

Default rule for an accepted compatibility change:

- small persisted data-structure change: bump the last number
  (`6.1.0 -> 6.1.1`)
- accepted Excel/runtime baseline change: bump the last number, even when the
  persisted JSON shape is unchanged
- small migration/backfill policy change that affects saved-diagram safety:
  bump the last number
- large release-line change: bump the middle number and reset patch
  (`6.1.x -> 6.2.0`)

A large release-line change is indicated by explicit project evidence such as:

- the target/base branch name moves to a new stable line, for example
  `feature/stable-version6.2*`
- the issue/release plan states that the target is `6.2.x` instead of `6.1.x`
- the team accepts a broad runtime/library restructuring as the next minor
  compatibility line

Do not jump from `6.1.x` to `6.2.x` just because an Excel file changed. Excel
updates on the same stable line are patch bumps unless the branch/release plan
or domain-owner decision says this is a new minor line.

In `development tweak/test`, record the likely bump but do not change executable
version constants until the developer chooses a `2N` / `2Y` compatibility patch.

### Step 3 - Read Current Context

Always read:

- `src/src/backend/utils/schemaMigrations.ts`
- `docs/Compatibility/SCHEMA_SNAPSHOT.md`
- `docs/Compatibility/SCHEMA_HISTORY.md`
- `docs/usercustom/saved/AI_DEVELOPMENT_WORKFLOW.md`

When the classification is not `schema-only`, also inspect:

- `src/excel-migration/`
- `src/excel-migration/compare_excel_runtime.py` when workbook-vs-runtime
  drift must be checked directly
- `src/src/backend/routes/dataRoutes.ts`
- `src/src/backend/utils/diagramLibraryRefresh.ts`
- `src/src/backend/utils/diagramCompatibility.ts`
- current Postgres-backed runtime contract (`Models`, `ModelVersion`, `Ports`,
  `VarNames`, `SystemVariables`) when DB access is available

### Step 3.5 - Verify Runtime Baseline Evidence

Before concluding that saved diagrams are safe against Excel/runtime drift,
inspect the current runtime baseline evidence:

- prefer `src/excel-migration/logs/latest_import_metadata.json` when present
- otherwise inspect the newest import log under `src/excel-migration/logs/`
- compare that evidence against the runtime baseline recorded in
  `docs/Compatibility/RUNTIME_BASELINE.json`

Rules:

- do **not** treat "no new Excel diff in the current range" as proof that old
  saved diagrams are safe
- old diagrams may still reflect an older imported workbook even when the repo
  already defaults to a newer Excel/runtime baseline
- treat import metadata as provenance, not proof of live contract alignment
- if current import provenance is missing, or the history row uses a vague
  runtime baseline reference instead of a concrete workbook/runtime evidence
  pointer, mark the result as `manual-review-required`
- treat `docs/Compatibility/RUNTIME_BASELINE.json` as the lightweight
  repo-recorded source of truth for "which Excel workbook was accepted for this
  merged version"
- when diagram-level `runtimeBaselineRef` stamps are available, compare them to
  the current imported runtime baseline and call out any mismatch or missing
  stamp as `needs runtime review`

### Step 3.6 - Compare Workbook Contract vs Live Runtime When Needed

Use a direct workbook-vs-runtime comparison when:

- the user explicitly asks about real server / live runtime / Forbod drift
- files under `src/excel-sheets/` or `src/excel-migration/` changed and DB
  access is available
- you need to know whether the current runtime already matches the workbook
  under review instead of only comparing git diffs

Preferred commands:

- repo root local Python:
  `python src/excel-migration/compare_excel_runtime.py src/excel-sheets/<excel-file>.xlsx`
- from `src/`, container fallback when local Python is missing `openpyxl`:
  `docker compose run --rm python-runner python /app/compare_excel_runtime.py "/app/excel-sheets/<excel-file>.xlsx"`

Interpretation:

- `Excel-only` rows: workbook contains rows missing from runtime; import is
  missing, incomplete, or failed for those rows
- `Runtime-only` rows: runtime still has rows not present in workbook; stale
  imported rows likely remain from an older workbook
- `Value-mismatch` rows: same logical row exists on both sides but important
  attributes differ; mark as `manual-review-required`
- metadata mismatch by itself is provenance drift evidence, but not final proof
  of a runtime contract mismatch

### Step 3.65 - Scan Existing Saved Diagrams When DB Audit Is In Scope

When Step 0.75 is in scope, scan saved diagrams from the current database using
the same compatibility path that protects load/save/upgrade/compute flows.

Preferred evidence:

- current runtime baseline metadata from the server/runtime baseline reader
- Mongo saved-diagram truth, including canvas `runtimeBaselineRef`
- the stored-diagram compatibility scan used by the backend upgrade path
- representative blocked diagram IDs and issue summaries

Interpretation:

- missing or stale `runtimeBaselineRef` means `needs runtime review`
- missing runtime items, unscannable domain snapshots, or compatibility issues
  mean the diagram is blocked/manual-review until a developer or domain owner
  decides the handling
- `missing_required_value` should default to UI/manual repair: keep the diagram
  blocked, ask the user/developer to open the diagram from Dashboard, fill the
  affected node value, save, verify, and compute again
- do not invent or backfill default values for `missing_required_value` unless a
  domain owner approves the exact value and the decision is recorded
- stale saved variables may be cleaned up by migration/backfill only after the
  developer confirms that they are not approved rename/preserve cases
- preserve legacy/computed values by default. A cleanup may remove stale fields
  from the current compute contract only after the values are kept in a backup,
  audit record, or legacy section that is not used for current compute.
- a clean repo/worktree review does not override blocked live diagrams
- do not update diagram stamps or saved data during a `DB` audit
- if the user later requests a backfill, use Step 8.5 and run a dry-run first

### Step 3.66 - Ask For Developer Decisions After DB Audit

When Step 3.65 finds blocked diagrams, produce a **Saved-Diagram Decision
Table** before writing migration or backfill code.

Include:

| # | Issue Kind | Model / Version | Port / Variable | Affected Diagrams | Suggested Handling | Developer Decision |
|---|------------|-----------------|-----------------|-------------------|--------------------|--------------------|

Suggested handling rules:

- `missing_required_value`: `UI manual repair`; the diagram remains blocked
  until the user/developer opens it in Dashboard, fills the missing value,
  saves, verifies, and computes again.
- `stale_node_port_var` / `stale_tp_node_port_var`: ask whether to remove stale
  saved fields with `auto-unverify`, map to an approved replacement, preserve
  as legacy data, or leave blocked for manual reselection.
- `stale_tp_change`: ask whether to remove the stale override with
  `auto-unverify` or leave blocked for manual review.
- `missing_model_version` / `missing_domain_model` / unscannable diagrams:
  restore a usable domain snapshot, skip the diagram, or require manual repair.

Do not proceed to migration/backfill code until every non-auto-safe row has a
recorded developer decision.

### Step 3.67 - Plan Local Diagram Backfill

After developer decisions are recorded, design local diagram updates as a
dry-run first.

Classify each diagram:

- `safe-to-stamp`: no blocked compatibility issues; only missing/stale
  `runtimeBaselineRef` needs updating.
- `manual-ui-repair`: missing required values or domain choices. The user or
  developer should open the diagram from Dashboard, fill values, save, verify,
  and compute again.
- `developer-decision`: stale variables need an approved cleanup, mapping,
  preserve-as-legacy, or manual-reselection decision.
- `skip`: unscannable diagrams or unresolved manual review.

Backfill rules:

- never mutate without `--dry-run` evidence and explicit apply approval
- preserve legacy/computed values in backup/audit data before removing stale
  fields from the current compute path
- auto-unverify every diagram whose current compute inputs are changed
- stamp `runtimeBaselineRef` only after the diagram is clean or intentionally
  skipped with a recorded reason

### Step 3.68 - Check Release/Compute Readiness

Use this step when the developer selects `RC` or asks whether upgraded
diagrams can compute on the current real-server setup.

Acceptance requires all gates below:

1. DB audit is clean, or every blocker has an approved cleanup/manual-repair
   decision recorded.
2. The diagram has the current runtime baseline stamp.
3. Backend load/compatibility scan is clean.
4. Compute preflight passes, including subnetwork expansion and stream instance
   uniqueness.
5. The real solver accepts the job and the callback returns a terminal
   `success` status.

Real-server configuration checks:

- `PORT=3000`
- `ALLOWED_ORIGINS` includes `http://localhost:5173`
- `SAVE_JSON_FILES=true`
- `BASE_EXTERNAL_URL=<public-backend>/api/external`
- `BASE_SOLVER_ENGINE_URL=<real-solver>/api`
- local `http://localhost:3000/api` answers
- public `<public-backend>/api` answers; a 502 here is an infrastructure
  blocker, not a diagram compatibility failure
- the solver API is reachable enough to accept `/solve/` requests

Smoke-test order:

1. one clean simple diagram
2. one representative subnetwork diagram
3. one large Blue Hydrogen diagram after the first two pass

Keep manual work bounded. If many diagrams share the same stale variable
signature, group it once in the decision table and request one batch decision
such as `approve cleanup`, `preserve`, `map`, `manual UI repair`, or `skip`.
Do not ask the user to manually edit dozens of identical stale fields unless no
safe developer cleanup exists.

### Step 3.7 - Infer Candidate Source Workbook For Unstamped Diagrams

Use candidate-source inference when a saved diagram:

- has no `runtimeBaselineRef`
- has a stale or mismatched `runtimeBaselineRef`
- fails compatibility scan with missing runtime items
- was imported from a Teams/shared-folder export whose original Excel baseline
  is not recorded

Preferred command for a whole saved diagram export:

```bash
python src/excel-migration/infer_diagram_runtime_baseline.py \
  --excel-dir src/excel-sheets \
  --diagram "<path-to-saved-diagram.json>"
```

Targeted command for one missing compatibility issue:

```bash
python src/excel-migration/infer_diagram_runtime_baseline.py \
  --excel-dir src/excel-sheets \
  --model HEATER \
  --model-version T_OUT_SPEC \
  --port INFO \
  --var HEAT_VAPORIZATION
```

Interpretation:

- `high` confidence means most saved model/version/port/variable signatures
  exist in the same workbook rows; it is strong evidence for the source
  workbook, but still not permission to auto-remap deleted or renamed domain
  items.
- `medium` or `low` confidence means the workbook may be related, but a human
  should review the unmatched/conflicting samples before stamping a baseline.
- `none` means no workbook has enough same-row evidence. Treat the diagram or
  issue as internally inconsistent, imported from an unknown external workbook,
  or affected by an old save/import bug.

This inference step is evidence collection only. Do not automatically set
`runtimeBaselineRef`, remove saved variables, or create rename mappings from
the inference result unless the confidence is high and the decision is recorded
or a domain owner approves the handling.

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

Use the Step 2.5 rule when choosing the next version:

- same stable line: next patch version
- new stable branch/release line: next minor version with patch `0`

Do not bump the version without updating both snapshot and history.

### Step 8.5 - Offer Developer/Admin Database Backfill

After schema/migration code and compatibility docs are updated in a `2N` or
`2Y` pass, ask the developer whether to update existing database diagrams from
inside the developer workflow instead of requiring every end user to click
Upgrade in the UI.

This is an optional developer/admin backfill. "Bypass the user" means bypassing
ordinary user-side Upgrade clicks. It does **not** mean bypassing safety gates.

Offer concise choices:

```text
Database backfill options:
1. Skip DB backfill for now
2. Dry-run only: scan existing diagrams and report what would change
3. Backfill current user's diagrams after dry-run passes
4. Backfill all diagrams in this database after dry-run passes
```

Rules:

- never mutate diagrams unless the developer explicitly selects a backfill
  target
- before mutation, confirm the target database/environment and record whether
  it is local/dev/staging/production
- create or point to a backup/export of affected diagrams before mutation
- run a dry-run first and report counts: safe, changed, skipped, blocked,
  failed
- do not update diagrams with `manual-review-required`,
  `domain-owner-decision-required`, missing source workbook, unknown runtime
  baseline, or unresolved compatibility issues
- do not silently remove, rename, or map domain-library items without a recorded
  owner-approved rule
- after mutation, verify a sample and report final counts plus any failed
  diagram IDs

Preferred implementation shape:

- use an existing migration/backfill script when one exists
- if no script exists, add a narrowly scoped developer script or admin-only
  endpoint with `--dry-run` as the default behavior
- keep the backfill operation idempotent where possible
- keep user-facing Upgrade available as the fallback path for diagrams skipped
  by the developer/admin backfill

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
- workbook vs runtime contract status when Step 3.6 was run
- saved-diagram DB audit status when Step 0.75 was in scope
- release/compute readiness status when Step 3.68 was run
- affected layers
- DB inspection status
- recommended action
- residual risk

### Required Narrative After The Table

After the table, include:

1. a `Saved-Diagram Decision Table` when DB audit found blocked diagrams
2. a short `decision summary`
3. a `Release/Compute Readiness` block when `RC` or real-server testing was
   requested
4. a developer/admin database-backfill choice when a `2N` or `2Y` patch
   updated schema/migration code
5. a short `open questions / assumptions` block when needed
6. an `Options` section with concrete next actions

### Options Section

Include:

- 3-5 short action options
- the recommended option first
- one option named `Show detailed compatibility table`
- one option named `Record developer decisions` when DB audit found unresolved
  blocked diagram rows
- one option named `Run real-server smoke compute` when `RC` gates are ready
- one option named `Fix infrastructure blocker` when public callback or solver
  reachability fails
- when Step 8.5 applies, include one option named `Dry-run database backfill`
- one option named `Run saved-diagram DB audit` when live saved diagrams were
  not scanned
- one `Workflow shortcuts` line listing `1N`, `1Y`, `2N`, `2Y`, `DB`, `RC`
- include `D` = show the issue decision table for the same pass. `D` must group
  findings by problem kind, model/version, port/variable, affected count, and
  representative diagrams; say whether each row is stale, missing, or
  unscannable; give suggested handling; and ask for developer decisions on
  high-risk rows. Do not answer `D` with a field glossary. Use per-diagram rows
  only as supporting detail when requested.

---

## Minimal Prompt For Humans / Skills

Use this instead of pasting a giant custom prompt:

```text
You are the Plant-GUI compatibility checker.
Read and execute docs/Compatibility/COMPAT_CHECK.md.
Use docs/Compatibility/SCHEMA_SNAPSHOT.md as the current baseline.
Use docs/Compatibility/SCHEMA_HISTORY.md as the version-to-version map and integrated decision log.
If the mode is missing, show a short 1N / 1Y / 2N / 2Y / DB / RC option menu and wait.
Produce the compact result table first, then any Saved-Diagram Decision Table, Release/Compute Readiness block, the decision summary, any developer/admin database-backfill choice, assumptions, and options.
Do not invent chemical-engineering mappings without explicit owner approval.
When real-server workbook drift is the question, compare the workbook against the live Postgres runtime contract.
When existing saved diagrams are the question, run the DB saved-diagram audit or explicitly report that DB inspection was not run.
For missing required values, recommend UI/manual repair unless an approved domain default is provided.
Keep compatibility output concise: summary counts first, decision rows next, details only on `D` or in a usercustom note.
When the user replies `D`, show grouped issue decision rows, not field definitions.
```

---

## Maintenance Rules

- keep this file process-focused
- keep `SCHEMA_SNAPSHOT.md` structure-focused
- keep `SCHEMA_HISTORY.md` version-and-decision-focused
- keep historical assessments in `docs/Compatibility/archive/`
- if the procedure grows again, move examples and long checklists into
  reference docs instead of re-expanding this file into another giant prompt
