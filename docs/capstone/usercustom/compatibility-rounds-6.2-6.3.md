# Compatibility Update Plan for 6.2 and 6.3

This document describes what should be changed in round `6.2` and round `6.3`
under a simulated real-development workflow:

1. Make the raw structure change first.
2. Allow iterative tweak-and-test passes while the target shape is still being
   stabilized.
3. Do not bump schema version or add migrations during those WIP passes.
4. Once the structure is stable, run the compatibility-check prompt and add one
   final compatibility patch for the whole unreleased change set.
5. Test the result in the dashboard and with the real server.

## Current Baseline

Round 1 has already introduced one structure-only change:

- add optional `stream.meta`

Scope:

- `canvas.edges[*].data.stream`
- `parentConnections.edges[*].data.stream`

Current stream shape after round 1:

```ts
stream = {
  stream_database_id: "...",
  content: "...",
  instance: "...",
  properties: { ... },
  stream_fractions: { ... },
  meta: {
    label?: string,
    sourceKind?: string
  }
}
```

Important rule for the next two rounds:

- no Prisma schema change
- no top-level `Node` document change
- no version bump in the structure-only or WIP tweak changes
- no migration code in the structure-only or WIP tweak changes

## Round 6.2

### Goal

Rename:

- `stream.properties`

to:

- `stream.propertyValues`

### Scope

Apply the change in both persisted locations:

- `canvas.edges[*].data.stream`
- `parentConnections.edges[*].data.stream`

### Shape Change

Before:

```ts
stream = {
  stream_database_id: "...",
  content: "...",
  instance: "...",
  properties: { ... },
  stream_fractions: { ... },
  meta: {
    label?: string,
    sourceKind?: string
  }
}
```

After:

```ts
stream = {
  stream_database_id: "...",
  content: "...",
  instance: "...",
  propertyValues: { ... },
  stream_fractions: { ... },
  meta: {
    label?: string,
    sourceKind?: string
  }
}
```

### Diagram

```text
stream
|- stream_database_id
|- content
|- instance
|- properties          -> removed in 6.2 structure update
|- propertyValues      -> added in 6.2 structure update
|- stream_fractions
`- meta
   |- label?
   `- sourceKind?
```

### What the Structure-Only Change Should Do

- update write paths so newly saved nets use `propertyValues`
- update in-memory types/helpers so the app works with `propertyValues`
- keep `meta`
- keep `stream_fractions`

### What the Structure-Only Change Should Not Do

- do not add `6.1 -> 6.2` migration logic
- do not bump schema version in the same change
- do not add fallback code that upgrades old `properties` payloads during load

### What the Compatibility Agent Should Add Later

- version bump from `6.1` to `6.2`
- migration from `properties` to `propertyValues`
- compatibility coverage for:
  - load/open
  - dashboard `version-status`
  - `bulk-upgrade`
  - import/export

### Manual Validation After Compatibility Patch

Use these graphs:

- `t1`
- `f1`
- `f1 (Copy)`
- `f1 (Copy)_zydd2s`

Checks:

- old `6.1` graphs can be detected and upgraded
- `t1` opens and computes
- `f1` survives upgrade and computes with subnetwork connections intact
- `f1 (Copy)` and `f1 (Copy)_zydd2s` do not regress
- export-rename still works

## Round 6.3

### Goal

Move:

- `stream.stream_fractions`

to:

- `stream.composition.fractions`

### Scope

Apply the change in both persisted locations:

- `canvas.edges[*].data.stream`
- `parentConnections.edges[*].data.stream`

### Real-Dev Simulation Rule

Treat round `6.3` as one unreleased structural change set that may span
multiple commits and several test/fix loops.

That means:

- the branch may go through several `development tweak/test` passes
- each pass may fix one more reader, writer, or runtime consumer
- do not create a new schema version for every tweak
- do one final version bump only when the `6.3` shape is stable and ready for
  the compatibility patch

### Final 6.3 Target Shape

Before:

```ts
stream = {
  stream_database_id: "...",
  content: "...",
  instance: "...",
  propertyValues: { ... },
  stream_fractions: { ... },
  meta: {
    label?: string,
    sourceKind?: string
  }
}
```

After:

```ts
stream = {
  stream_database_id: "...",
  content: "...",
  instance: "...",
  propertyValues: { ... },
  composition: {
    fractions: { ... }
  },
  meta: {
    label?: string,
    sourceKind?: string
  }
}
```

### Final 6.3 Diagram

```text
stream
|- stream_database_id
|- content
|- instance
|- propertyValues
|- stream_fractions       -> removed in final 6.3 shape
|- composition            -> added in final 6.3 shape
|  `- fractions
`- meta
   |- label?
   `- sourceKind?
```

### Continuous Tweak Development Plan

#### Tweak A - First WIP Structure Change

Goal:

- switch new writes to `composition.fractions`

What this pass should do:

- update write/save paths so newly saved nets use `composition.fractions`
- update primary in-memory types so active editing uses `composition.fractions`
- keep `meta`
- keep `propertyValues`

What this pass should not do:

- do not add `6.2 -> 6.3` migration logic yet
- do not bump schema version yet
- do not claim compatibility is complete yet

#### Tweak B - Reader Alignment Pass

Goal:

- make app readers consistently consume `composition.fractions`

What this pass should do:

- update helper utilities and normalization code
- update any UI/runtime reader still looking for `stream_fractions`
- verify that normal edges and parent-connection edges both behave correctly

What this pass should not do:

- do not create another schema version just because this is a second tweak
- do not append a new entry to `VERSION_ORDER` yet

#### Tweak C - Downstream Runtime Audit

Goal:

- catch consumers outside the obvious save/load path

Check at minimum:

- compute translation / solver payload building
- export/import
- dashboard `version-status`
- `bulk-upgrade`
- duplicate/clone flows

Rule:

- if one of these still reads `stream_fractions`, fix it in the same unreleased
  `6.3` change set
- this is still not a new schema round; it is part of the same `6.3`
  development cycle

#### Final Compatibility Pass

Only after the structure is stable and runtime behavior is verified:

- bump version from `6.2` to `6.3`
- add migration from `stream_fractions` to `composition.fractions`
- update `SCHEMA_SNAPSHOT.md`
- update save payload `schemaVersion`
- add compatibility tests and upgraded-diagram validation

### What the Development Tweaks Should Do

- move toward the final `composition.fractions` shape incrementally
- allow several commits of testing and bug-fixing before the compatibility bump
- keep all changes inside the same unreleased `6.3` target schema

### What the Development Tweaks Should Not Do

- do not add `6.2 -> 6.3` migration logic during WIP passes
- do not bump schema version for each tweak
- do not create `6.4` or another follow-up version just because the first `6.3`
  attempt needed more fixes
- do not mark the work complete until the final compatibility pass is done

### What the Final Compatibility Agent Should Add

- version bump from `6.2` to `6.3`
- migration from `stream_fractions` to `composition.fractions`
- snapshot refresh to the final `6.3` structure
- compatibility coverage for:
  - load/open
  - dashboard `version-status`
  - `bulk-upgrade`
  - import/export
  - compute translation / solver payload building
  - duplicate/clone flows

### Example Real-Dev Timeline

Example branch history:

1. Commit 1: save paths start writing `composition.fractions`
2. Commit 2: UI helpers and edge readers are updated
3. Commit 3: compute/export/import readers are fixed after testing
4. Commit 4: final compatibility patch bumps `6.2 -> 6.3` and adds migration

Important interpretation:

- commits 1 to 3 are still one unreleased schema change set
- only commit 4 should finalize the compatibility versioning work

### Manual Validation After Final Compatibility Patch

Use these graphs:

- `t1`
- `f1`
- `f1 (Copy)`
- `f1 (Copy)_zydd2s`

Checks:

- old `6.2` graphs can be detected and upgraded
- `t1` opens and computes
- `f1` survives upgrade and computes with subnetwork connections intact
- `f1 (Copy)` and `f1 (Copy)_zydd2s` do not regress
- composition data is preserved in both normal edges and subnetwork wrapper
  edges
- export-rename still works

## Recommended Sequence

### For 6.2

1. Make the structure-only change from `properties` to `propertyValues`.
2. Run the compatibility-check prompt in a separate agent.
3. Review the generated compatibility patch.
4. Test dashboard compatibility.
5. Test real-server compute.

### For 6.3

1. Start the `6.3` structure change from `stream_fractions` to
   `composition.fractions`.
2. Iterate through one or more `development tweak/test` passes until save/load,
   helpers, and downstream runtime readers are stable.
3. Run the compatibility-check prompt in `ready for full compatibility` mode.
4. Review the generated compatibility patch.
5. Test dashboard compatibility.
6. Test real-server compute.

## Notes

- export-rename is a separate feature and should remain working across both
  rounds
- these two rounds are focused on persisted stream payload compatibility only
- if later you want to test Prisma-level or `Node` collection compatibility,
  that should be planned as a separate track
