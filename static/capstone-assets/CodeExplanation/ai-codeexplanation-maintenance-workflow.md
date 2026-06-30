---
title: AI CodeExplanation Maintenance Workflow
sidebar_position: 2
description: Defines the subagent-based workflow for creating and updating HyProNet CodeExplanation documentation from current source code.
---

## Purpose

Use this workflow when an AI agent is asked to create new `CodeExplanation` pages or update existing ones for HyProNet. The goal is to keep the current documentation synchronized with the current source code, not with memory, issue summaries, or archived docs.

This is a repo-local workflow, not a global Codex skill. It depends on HyProNet paths, Docusaurus publishing rules, and the `CodeExplanation` standards in this repository.

## Required Inputs

Before any drafting starts, the coordinator must read:

- `docs/CodeExplanation/CODE_EXPLANATION_GUIDELINES.md`: page structure, style rules, source-file requirements, verification expectations, and generated-artifact cautions.
- `docs/CodeExplanation/code-explanation-index.md`: current coverage map, naming conventions, and the existing sidebar-visible reading order.
- `.github/workflows/sync-version6.1-docs-to-documentation-repo.yml`: current sync behavior from `HYPRONET-GUI/docs` to `Plant-Modelling-Documentation/docs/capstone`.
- The current source files under `src/src/backend` and `src/src/frontend` for the feature being documented.

Use `docs-archive/PreviousDoc/CodeExplanation/` only as historical reference. Never treat archive content as current behavior until the source code has been rechecked.

## Output Rules

Current documentation changes must use these paths:

```text
docs/CodeExplanation/<page-name>.md
docs/CodeExplanation/code-explanation-index.md
```

Create a new page when the source inventory finds a current feature, module, data flow, route, component group, or persistence workflow that is important and not already covered.

Update an existing page when the documented feature still exists but source behavior, inputs, outputs, state, persistence, solver payloads, verification commands, or extension points have changed.

Do not create duplicate pages for the same responsibility. If two pages overlap, choose one owner page and link to it from related pages.

## Coordinator Responsibilities

The coordinator owns scope, source-of-truth decisions, and final acceptance. Subagents collect evidence, draft bounded sections, and review; they do not decide that the workflow is complete.

Coordinator duties:

1. Work from a clean branch or isolated worktree based on the intended target branch.
2. Identify the comparison base:
   - For feature branch docs: compare the branch against the default branch.
   - For periodic documentation audits: scan the whole current source tree.
3. Split source reading across subagents by stable ownership areas.
4. Merge subagent dossiers into one documentation plan.
5. Assign drafting work with explicit file ownership.
6. Run multi-round review until there are no actionable findings at any severity.
7. Stage only documentation files that are in scope.
8. If publishing is requested, push to the default branch so the documentation sync action runs.

## Phase 1: Source Inventory With Subagents

Do not ask one agent to "read the whole repo" as an undifferentiated task. The coordinator creates a whole-repo inventory by dispatching focused subagents whose scopes cover the source tree.

Recommended inventory split:

| Subagent | Scope | Required Output |
| --- | --- | --- |
| Backend API and persistence reader | `src/src/backend/routes`, `src/src/backend/services`, Prisma schemas, workers, queue config | Route/service map, DB models touched, side effects, tests, undocumented or changed behavior |
| Frontend UI and state reader | `src/src/frontend/src/pages`, `components`, `features`, `hooks`, `utils`, `store.ts` | User-facing flows, component contracts, Redux state, route params, guards, existing docs mapping |
| Cross-layer workflow reader | save, import, compute, translation, solver callback, generated payload checks | End-to-end data flows, payload contracts, ownership boundaries, stale or missing docs |
| Documentation coverage reader | `docs/CodeExplanation`, `docs/Installation`, sync workflow | Existing coverage, duplicate topics, index gaps, broken links, sidebar/sync implications |

Each inventory subagent must return a dossier with this shape:

```text
Status: DONE | NEEDS_CONTEXT | BLOCKED

Scope read:
- exact files or directories read

Feature map:
- feature or workflow name
- source entry points
- existing documentation owner, if any
- current behavior summary grounded in source files

Documentation actions:
- CREATE docs/CodeExplanation/<name>.md because ...
- UPDATE docs/CodeExplanation/<name>.md because ...
- NO_CHANGE for <area> because ...

Evidence:
- source paths and symbols supporting each recommendation
- tests or verification commands that exist

Risks:
- stale archive content
- generated artifacts that must not be treated as source truth
- behavior that needs a human decision
```

The coordinator must reject dossiers that do not name exact source files.

## Phase 2: Documentation Plan

The coordinator converts the dossiers into a documentation plan before editing files.

The plan must list:

- New pages to create.
- Existing pages to update.
- Pages that should not be touched.
- Source files each page must cite in its `Source Files` section.
- Index or overview updates required.
- Verification commands and manual checks available for each page.
- Subagent writer assignments with disjoint file ownership.

Acceptance criteria for the plan:

- Every planned page has one clear responsibility.
- No two pages claim ownership of the same primary source area.
- Every new page name follows the file naming rules in `CODE_EXPLANATION_GUIDELINES.md`.
- Existing pages are preferred over new pages when the current page already owns the code area.
- The plan includes `code-explanation-index.md` updates whenever a visible current page is created, renamed, or removed.

## Phase 3: Drafting With Writer Subagents

Dispatch writer subagents only after the plan is complete.

Writer subagents must receive:

- The exact page path they own.
- The exact source files they must read.
- The relevant excerpt or link target from `CODE_EXPLANATION_GUIDELINES.md`.
- Any existing page they are updating.
- A strict instruction not to edit files outside their assigned page unless the coordinator explicitly assigns the index update.

Writer subagents must produce pages that include the sections required by `CODE_EXPLANATION_GUIDELINES.md`.

For frontend pages, they must cover:

- Rendered UI and interaction map.
- Component contracts.
- Props passed to behavior-relevant child components.
- Route params, selectors, local state, hooks, effects, cleanup.
- Conditional rendering and disabled/readOnly guards.
- Manual UI verification matrix.

For backend or cross-layer pages, they must cover:

- Request and response contracts.
- Exact important fields such as `parameters`, `parameters.tps_specs`, and `parameters.costs` when relevant.
- Field ownership and source.
- Fallback, sanitization, validation, and legacy compatibility rules.
- DB read/write boundaries.
- Queue, solver, callback, and result persistence boundaries when relevant.

## Phase 4: Integration Pass

The coordinator performs the integration pass after writer subagents finish.

Required integration checks:

1. Frontmatter exists and has `title`, `sidebar_position`, and `description`.
2. `Source Files` lists exact current source paths and one-sentence roles.
3. `Data Flow`, `Testing and Verification`, and `Known Cautions` are present.
4. New current pages are linked from `docs/CodeExplanation/code-explanation-index.md`.
5. Related pages link only to current docs or explicitly labeled historical archive references.
6. No page treats generated files as source truth.
7. No page adds `docs/SetupInstructions` or another duplicate wrapper.
8. No changes are made under `docs-archive/` or `version6.1/` unless the user explicitly requested archive or legacy site edits.

## Phase 5: Multi-Round Subagent Verification

Verification is not complete after one review. The coordinator must run independent review rounds and repair findings between rounds.

### Round 1: Source Accuracy Review

Dispatch at least one reviewer per changed page group. Reviewers must read the changed docs and the cited source files.

Reviewer prompt:

```text
Review these changed CodeExplanation docs for source accuracy.

You must verify every behavior claim against current source files.
Do not rely on archived docs, generated artifacts, or the writer's summary.
Return PASS only if there are no actionable inaccuracies, missing source boundaries, or unsupported claims.

Output:
- PASS or FAIL
- findings with file path, section, source evidence, and suggested fix
- source files read
```

The coordinator fixes every actionable finding before moving to Round 2.

### Round 2: Standards and Navigation Review

Dispatch a separate reviewer that did not write the pages and did not perform Round 1 for the same page.

Reviewer prompt:

```text
Review these CodeExplanation docs against CODE_EXPLANATION_GUIDELINES.md and code-explanation-index.md.

Check frontmatter, required sections, source-file roles, data flow, verification commands, known cautions, link targets, index placement, duplicate topics, and Docusaurus sidebar implications.
Return PASS only if there are no actionable standards or navigation issues.

Output:
- PASS or FAIL
- findings with file path, section, rule violated, and suggested fix
- links or files checked
```

The coordinator fixes every actionable finding before moving to Round 3.

### Round 3: Sync and Release Readiness Review

Run this round when the docs are intended to publish to the documentation site.

Reviewer prompt:

```text
Review this documentation diff for HYPRONET-GUI docs sync readiness.

Check that the diff is limited to intended docs paths, that default-branch sync rules are understood, that no duplicate top-level docs wrapper was introduced, and that Plant-Modelling-Documentation will receive the expected paths under docs/capstone.
Return PASS only if this is safe to commit and push.
```

The coordinator must not push until Round 3 is PASS.

### Stop Condition

The stop condition is:

```text
PASS = no actionable findings at any severity across all active review rounds.
```

If any reviewer returns findings, repair them and rerun the relevant round. Do not downgrade findings to "notes" unless the coordinator can point to source evidence showing the reviewer is wrong.

## Phase 6: Local Verification

Run these checks before committing:

```powershell
git diff --check -- docs/CodeExplanation
rg -n "^(<<<<<<<|=======|>>>>>>>)" docs/CodeExplanation
```

If docs outside `CodeExplanation` changed, include them in the same checks.

For link checks, verify that every relative markdown link points to an existing file in the source tree. At minimum, inspect:

- links from new or updated pages
- links from `docs/CodeExplanation/code-explanation-index.md`
- links to `docs/Installation`

If the documentation site is being published, verify the sync workflow rules:

- The source branch must be the repository default branch for automatic sync.
- `docs/<top-level-dir>` syncs to `Plant-Modelling-Documentation/docs/capstone/<top-level-dir>`.
- `Installation` and `CodeExplanation` are sidebar-visible in the generated site.
- Deleted top-level source docs directories are removed from the target site by the sync workflow.

## Phase 7: Commit, Push, and Publish

Stage only the intended documentation files:

```powershell
git add -- docs/CodeExplanation
```

If other docs paths are intentionally changed, stage those paths explicitly. Do not use `git add -A` in a mixed worktree.

Before pushing, inspect:

```powershell
git diff --cached --name-status
git diff --cached --check
```

For documentation site publication:

1. Push the docs commit to the HYPRONET-GUI default branch.
2. Confirm `Plant-Modelling-Documentation` receives a commit like `Sync docs/ from <branch> (<sha>)`.
3. Confirm the documentation repository's GitHub Pages deploy succeeds.
4. Spot-check the published pages with HTTP 200 responses.

## Common Failure Modes

| Failure | Cause | Fix |
| --- | --- | --- |
| New docs are written from archive content | The writer treated `docs-archive` as current behavior | Re-read current source and rewrite unsupported claims |
| A new page duplicates an existing owner page | Inventory did not map existing docs first | Merge the new content into the owner page and update links |
| The page lists files but does not explain behavior | Writer summarized imports instead of code responsibility | Add purpose, data flow, side effects, and cautions |
| Frontend docs miss user-facing guards | Writer only read JSX structure | Add rendered UI map, disabled/readOnly conditions, state, and manual verification |
| Backend docs miss payload ownership | Writer only read routes | Trace service utilities, DB models, queue workers, solver/callback boundaries |
| Docs do not appear on the site | Changes were pushed to a non-default branch or an unlisted sidebar group | Push to default for sync and place visible pages under `CodeExplanation` or `Installation` |
| Review stops after one PASS | Coordinator treated one reviewer as enough | Run source accuracy, standards/navigation, and sync readiness rounds |

## Minimal Subagent Set

Small doc update:

1. One source inventory subagent.
2. One writer subagent.
3. One source accuracy reviewer.
4. One standards/navigation reviewer.

Large feature or periodic audit:

1. Backend inventory subagent.
2. Frontend inventory subagent.
3. Cross-layer workflow inventory subagent.
4. Documentation coverage subagent.
5. One writer subagent per page or page group.
6. Source accuracy reviewers split by page group.
7. Standards/navigation reviewer.
8. Sync readiness reviewer.

Do not let the same subagent write and approve the same page.

## Final Report Format

The coordinator's final report should include:

- Pages created.
- Pages updated.
- Source areas inspected.
- Subagent rounds completed and their PASS/FAIL outcomes.
- Verification commands run.
- Whether the docs were synced to `Plant-Modelling-Documentation`.
- Published URLs, if deployed.
- Any residual risks or source areas intentionally left undocumented.
