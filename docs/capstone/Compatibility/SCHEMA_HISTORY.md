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

## Current History

| Version | Previous | Migration Key(s) | Runtime Baseline | Classification | Changed Layers | Decision Summary | Evidence |
|---------|----------|------------------|------------------|----------------|----------------|------------------|----------|
| `1.0.0` | n/a | n/a | legacy baseline | legacy | legacy persisted data | Missing version is treated as `1.0.0`; runtime fallbacks still support older shapes. | `schemaMigrations.ts` |
| `6.0.0` | `1.0.0` | `1.0.0->6.0.0` | `feature/stable-version6.1` code baseline | `schema-only` | save/export/import snapshot contract; current stable persisted model | This branch intentionally resets the live executable compatibility axis back to clean `6.0.0`. Experimental `6.1/6.2/6.3` schema labels and migrations were removed; only low-risk version-agnostic fixes such as `model_name`-based UUID reconciliation were retained. | `schemaMigrations.ts`; `dataRoutes.ts`; compatibility docs |

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
