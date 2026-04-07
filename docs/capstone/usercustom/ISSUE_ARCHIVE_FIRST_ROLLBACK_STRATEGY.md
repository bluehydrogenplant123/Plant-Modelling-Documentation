# Issue Draft: Archive-First Rollback Strategy for Schema Upgrades

## Summary

Current diagram upgrade flow creates a pre-upgrade backup and then migrates directly
to the latest schema version. This supports restoring a saved backup graph, but it
does **not** support "revert one version" semantics such as:

- `6.3 -> 6.2`
- `6.2 -> 6.1`

when the original upgrade path may have been:

- `6.0 -> 6.3`

For now, we should **not** implement full version-targeted rollback. Instead, for a
small development team, we should explicitly adopt a simpler policy:

- keep archived old-version diagrams/backups
- restore or re-activate an archived graph when needed
- postpone true per-version revert / rollback design until it is clearly needed

## Problem

The current product language can imply that rollback means "go back one schema
version", but the actual system behavior is different:

- upgrade creates a backup of the pre-upgrade graph
- upgrade migrates directly to the latest schema
- restore activates a previous backup graph
- restore does not synthesize a new diagram at an intermediate schema version

This creates ambiguity for cases like:

- imported `6.0.0` diagram upgraded to `6.3.0-alpha.2`
- user later wants to return to `6.2.0`

There may be no diagram persisted at `6.2.0`, so "revert one version" is not
currently available.

## Proposed Near-Term Decision

Adopt an **archive-first rollback strategy**:

1. Treat rollback as "restore a previously archived graph", not "compute a prior
   schema revision".
2. Keep old-version backups/checkpoints available for manual re-activation.
3. Do not create or maintain a normal editable backup diagram for every migration
   hop.
4. Defer version-targeted rollback until the team has a stronger product need.

## Why This Is Simpler for a Small Team

This is likely the lowest-risk option for now because it avoids:

- per-hop backup explosion for `root + instance + blueprint + snapshot` graphs
- extra cleanup complexity after failed or repeated upgrades
- more shared-reference and orphan-data pollution risks
- the need to define and test reverse migrations for every schema step
- confusing UI semantics around "rollback", "revert", and "restore"

Instead, the team can rely on:

- one pre-upgrade archived graph
- explicit restore tooling
- forward migrations as the primary compatibility path

## What This Issue Should Clarify

This issue is a design/decision issue only. It should decide:

- whether "rollback" in product language means `restore archived backup`
- whether small-team workflow should prefer `archive + re-activate` over
  `version-by-version rollback`
- whether future version-targeted rollback should use separate immutable
  checkpoints instead of ordinary diagrams

## Out of Scope

This issue should **not** implement:

- full `6.3 -> 6.2 -> 6.1` revert flows
- reverse migrations for each schema hop
- automatic per-version backup creation
- rollback UI changes

## Suggested Follow-Up If We Need More Later

If the team later decides version-targeted rollback is necessary, a better long-term
path would be:

- explicit immutable checkpoints by selected schema version
- restore-from-checkpoint into a new active graph
- avoid treating every intermediate backup as a normal working diagram

## Acceptance Criteria

- Team agrees on the near-term rollback definition.
- Team agrees whether archive-first is the default compatibility recovery path.
- Team explicitly defers or schedules true version-targeted rollback separately.
