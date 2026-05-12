# Compatibility History And Decision Summary

Purpose: keep a compact version-to-version map of compatibility changes, while
also recording the small amount of decision context that future developers will
need.

This file is intentionally lightweight. It does **not** replace:

- `docs/Compatibility/SCHEMA_SNAPSHOT.md` as the current baseline
- `src/src/backend/utils/schemaMigrations.ts` as the executable migration chain
- Git as the full raw change history

For this project, this file also serves as the integrated decision log. A
separate `DECISION_LOG.md` is not needed yet.

---

## What Belongs Here

For each released compatibility version, record:

- version
- previous version
- migration key(s)
- runtime baseline reference
- classification
- changed layers
- decision summary
- evidence

Do **not** record every commit, refactor, or UI-only change.

---

## Version Numbering Policy

Use `major.minor.patch` for the compatibility axis.

For accepted changes on the same stable line, bump the patch number:

- small persisted data-structure changes
- accepted Excel/runtime baseline updates
- migration/backfill policy changes that affect saved-diagram safety

Example: while the target branch is still `feature/stable-version6.1-*`, the
next accepted compatibility boundary after `6.1.0` should be `6.1.1`.

Bump the minor number only when project evidence says the team has moved to a
new compatibility line, for example:

- the target/base branch name moves from `stable-version6.1*` to
  `stable-version6.2*`
- the issue/release plan explicitly targets `6.2.x`
- the team accepts a broad runtime/library restructuring as the next minor line

An Excel update alone is not a reason to jump from `6.1.x` to `6.2.x`; it is a
patch bump unless the branch/release plan says otherwise.

---

## Current History

| Version | Previous | Migration Key(s) | Runtime Baseline | Classification | Changed Layers | Decision Summary | Evidence |
|---------|----------|------------------|------------------|----------------|----------------|------------------|----------|
| `1.0.0` | n/a | n/a | legacy baseline | legacy | legacy persisted data | Missing version is treated as `1.0.0`; runtime fallbacks still support older shapes. | `schemaMigrations.ts` |
| `6.0.0` | `1.0.0` | `1.0.0->6.0.0` | `src/excel-sheets/apr-6-2026.xlsx` accepted with the stable-version6.1 reset | `schema-only` | save/export/import snapshot contract; current stable persisted model; optional runtime baseline stamps on `canvas` | This branch intentionally resets the live executable compatibility axis back to clean `6.0.0`. Experimental `6.1/6.2/6.3` schema labels and migrations were removed; only low-risk version-agnostic fixes such as `model_name`-based UUID reconciliation and optional `runtimeBaselineRef`/`runtimeBaselineImportedAt` canvas stamps were retained. The 2026-05-07 `2N` pass did not find a new accepted workbook or persisted-shape change requiring a version bump; diagrams with missing or stale runtime baselines remain blocked/manual-review paths rather than automatic domain remaps. | `schemaMigrations.ts`; `dataRoutes.ts`; `runtimeBaseline.ts`; `diagramCompatibility.ts`; `RUNTIME_BASELINE.json`; `latest_import_metadata.json`; compatibility docs; import evidence |
| `6.1.0` | `6.0.0` | `6.0.0->6.1.0` | `src/excel-sheets/apr-6-2026.xlsx` / `apr-6-2026.xlsx#c03c1f87c78f158ff6b2099f4d082cdf92fa8da5e0db1be2b5d80f2fe092edf9` | `schema-only` | version boundary only; persisted save/export/import shape unchanged; current target for local saved-diagram upgrade/backfill work | The team accepted `6.1.0` as the current compatibility target for Issue 82/83 old-diagram upgrade work. The `6.0.0->6.1.0` migration is intentionally no-op for persisted structure; old diagrams still require runtime compatibility review. No automatic domain remaps or default missing values are approved: stale saved variables require developer cleanup decisions, missing required values remain UI/manual repair, and unscannable diagrams are skipped or repaired before backfill. | `schemaMigrations.ts`; `SCHEMA_SNAPSHOT.md`; `audit_saved_diagrams.ts`; `reconcile_legacy_diagrams.ts` dry-run report under local usercustom/backup notes |

---

## How To Use This File

Use this file when you need a quick answer to:

- which version introduced this compatibility boundary?
- which migration key should handle it?
- was this a schema change, a library change, or both?
- what decision was made about old saved data?
- what workbook/runtime baseline was accepted for that version?

Do **not** use this file as the judge for current structure drift. For that,
always use `SCHEMA_SNAPSHOT.md`.

---

## Version Entry Template

Use this template when adding a new compatibility version:

| Version | Previous | Migration Key(s) | Runtime Baseline | Classification | Changed Layers | Decision Summary | Evidence |
|---------|----------|------------------|------------------|----------------|----------------|------------------|----------|
| `x.y.z` | `prev` | `prev->x.y.z` | `path/to/workbook.xlsx` or `n/a` | `schema-only` / `library-additive` / `library-rename` / `library-delete` / `mixed` | short layer list | 1-2 sentences describing what was decided for old saved data | migrations/tests/docs |

Write the decision summary so a future developer can understand the policy
without replaying the entire Git history.

Good:

- "Removed `FLOW_FREE`; auto-unverify + manual reselection required; no
  automatic rename mapping approved."
- "Added `MCP_OUT1/MCP_OUT2`; additive refresh allowed; required-value handling
  remains manual review."

Bad:

- "Excel changed."
- "Compatibility updated."

---

## When To Split Out A Separate Decision Log

Create a dedicated decision log only if one or more of these becomes true:

- version entries regularly exceed a few bullets
- multiple owners/approvers must be recorded for each release
- the team starts maintaining several parallel compatibility tracks
- the history table becomes hard to scan because decisions are too dense

Until then, keeping the decision summary inside `SCHEMA_HISTORY.md` is the
cleaner option for this team.
