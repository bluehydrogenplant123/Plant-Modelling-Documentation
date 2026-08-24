---
title: Component Template Lifecycle
sidebar_position: 18
description: Explains component-name templates from Excel catalog preflight through stream-driven expansion, cache cleanup, time periods, translation, and compute validation.
---

## Overview

Component templates let one catalog variable definition expand into one runtime variable per present stream component. The shared engine owns template parsing, deterministic identity, collision checks, reuse, and cleanup. Frontend and backend adapters add stream values and persistence behavior without redefining the template contract.

## Source Files

- `src/src/shared/componentTemplateCore.ts`: template grammar, deterministic expansion, reconciliation, issue codes, and unresolved-reference validation.
- `src/src/shared/streamComponentPresence.ts`: the null-versus-zero component-presence contract.
- `src/src/shared/componentMapping.ts`: canonicalizes user workbook component keys before they reach the lifecycle.
- `src/excel-migration/migrate.py`: validates canonical material MF/X pairs and atomically upgrades a compatible legacy catalog.
- `src/src/frontend/src/utils/modelVersionUtils.ts`: applies stream data and shared reconciliation to a node model version.
- `src/src/frontend/src/utils/componentTemplateCacheSyncUtils.ts`: loads or recovers model versions and commits changed cache and base-parameter state.
- `src/src/frontend/src/utils/componentTemplateLifecycleUtils.ts`: separates definitions, derived material values, and ordinary generated inputs.
- `src/src/frontend/src/utils/componentTemplateGlobalTpUtils.ts`: filters template-derived rows from Global TP snapshot and clone operations.
- `src/src/frontend/src/components/custom-edge/index.tsx`: invokes reconciliation on connect, reconnect, stream change, and disconnect.
- `src/src/backend/utils/componentTemplateBackendUtils.ts`: repeats reconciliation at translation time and derives canonical material values.
- `src/src/backend/utils/translationTpsSpecsUtils.ts`: merges Base/Multi-TP state with stream-driven component rows.
- `src/src/backend/routes/computeRoutes.ts` and `src/src/backend/services/solverEngineApiService.ts`: reject unresolved template references before solver dispatch.

## Responsibility Boundary

The lifecycle owns which component-derived variables exist and how they are identified. Component Mapping owns key canonicalization before canvas state changes. The connected material stream owns component fractions and flow properties. TP storage owns user overrides for eligible ordinary variables. The solver receives only a resolved model; it does not expand `{COMPNAME}`.

## Core Contracts

### Template Syntax

The only accepted tokens are case-sensitive `{COMPNAME}` and `{COMPNAME::SOURCEPORT}`. Both `internal_var_name` and `port_var_name` must contain exactly one token. Without `::SOURCEPORT`, the target port is also the component source. When both names specify a source port, they must agree and that port name must be unique.

Canonical material definitions are a complete pair:

```text
{COMPNAME}_MF
{COMPNAME}_X
```

The Excel preflight rejects partial pairs, duplicates, malformed internal names, and mixed canonical/legacy `compname_MF` or `compname_X` rows. A compatible legacy database is renamed across `SystemVariables`, `Ports`, `VarNames`, and `ModelVarMapping` in one transaction before normal port import.

### Presence and Values

| Stream value | Present? | Result |
| --- | --- | --- |
| JSON null or text `null` | No | No generated row for that key. |
| Numeric `0` or numeric text `0` | Yes | A generated row exists with a zero-derived value. |
| Empty text or invalid/non-finite text | Invalid/undefined | Never converted to zero; the import boundary rejects it. |

Component Mapping changes a key from `User Name` to `System Name` but preserves its value. Therefore a zero-valued alias remains present after canonicalization.

For canonical material rows, `{component}_X` is the component fraction. `{component}_MF` is `(MF0 or MF) * fraction`, or null when total flow is unavailable. Both are derived values with `required: false`, `spec: null`, `is_human_input: false`, and `send_to_calc: false`.

### Generated Identity

Each generated row records:

- `component_template_id` for its definition;
- `component_template_source_port` for the connected source;
- `component_template_component_key` for the original component key;
- `component_template_definition: false`.

The definition remains in the model with `component_template_definition: true` and is hidden/inert in normal variable selection. Generated IDs are deterministic UUIDs derived from definition, target port, location, canonical component identity, and nested object role. Reconnecting the same component therefore reuses compatible state instead of creating a random duplicate.

## Data Flow

1. Excel migration validates the complete canonical MF/X scope before importing dependent port rows.
2. Browser material import validates one complete Component Mapping snapshot and canonicalizes all component keys before committing Redux/canvas state.
3. An edge lifecycle event loads the node model version from cache, asynchronous storage, or recovery data.
4. `getPresentStreamComponentKeys(...)` removes null values but retains zero-valued keys.
5. `reconcileComponentTemplates(...)` resolves each definition, source port, component key, generated internal name, alias, and deterministic ID.
6. Existing compatible rows are reused. Missing rows are added. Rows whose source component or connection disappeared are removed. Legacy value sources can be merged into canonical rows.
7. If any syntax, binding, component, identity, internal-name, or alias issue exists, reconciliation returns the original model version unchanged.
8. The frontend commits a changed model version to the canonical node cache and mirrors node-ID aliases. Base derived values update node parameters only when their values changed.
9. Backend translation repeats reconciliation from connected streams, then applies TP overrides to eligible rows.
10. Compute and solver-service guards scan equations, sets, collections, and solution-algorithm structures. A remaining `{COMPNAME}`, plain `COMPNAME`, or legacy `compname_MF/X` reference stops dispatch; expressions must use concrete names such as `CH4_MF`.

## Base and Multi-Time-Period Behavior

Template definitions and derived material MF/X rows are not manual inputs and are excluded from Global TP snapshots, overlays, and clone payloads. Their values are recalculated from each connected stream. An ordinary generated template variable can participate in TP state when its fixed/required metadata makes it an eligible input.

When a connection or component disappears, edge lifecycle code removes obsolete generated rows and stages deletion of matching persisted TP changes. Save waits for pending cleanup requests, preventing a removed variable from returning on reload. If a generated identity is migrated, TP drafts are copied to the new identity and the old identity is marked for deletion.

## Errors and Atomicity

Shared issue codes include malformed/missing tokens, unknown or duplicate source ports, source-port conflicts, missing component metadata, normalized component collisions, duplicate generated identities, and internal-name or alias collisions. Any issue makes shared reconciliation all-or-nothing.

The Excel boundary is also all-or-nothing for the template upgrade. A workbook/database scope mismatch rolls back the rename transaction. An optional rollout manifest can additionally reject a wrong workbook SHA-256, filename, count, or scope digest before the database connection opens.

## Extension Points

- Add template grammar in `componentTemplateCore.ts`, then update both frontend and backend adapters.
- Add a new derived-variable family in the adapters, not by special-casing the shared identity engine.
- Add a new metadata key to `isIgnoredComponentMetadataKey(...)` only when it is never a chemical component.
- Keep Component Mapping before Redux and template expansion; do not add a second mapping layer in translation.

## Testing and Verification

From `src/`, run the passing translation and mapping suites adjacent to this lifecycle:

```powershell
./node_modules/.bin/jest.cmd --runTestsByPath tests/backend/utils/translationMaterialStreams.test.ts tests/frontend/componentMapping.test.ts tests/frontend/componentMappingCanvasIntegration.test.ts tests/frontend/componentMappingLifecycle.test.ts --runInBand --coverage=false
```

Some legacy assertions in `translationTpsSpecsUtils.test.ts` still expect a null-valued fraction to generate a component row. That expectation predates the current null-absent contract and should not be used as its source of truth until the test is updated.

For documentation changes, also run:

```powershell
git diff --check -- docs/CodeExplanation/component-template-lifecycle.md
```

Manual verification should connect a stream containing one normal fraction, numeric zero, and null. Confirm that normal and zero components expand, null does not, reconnect reuses IDs, and disconnect removes generated rows before save/reload.

## Known Cautions

- Null means absent; numeric zero means present. Do not use truthiness to select components.
- Keep legacy component-expansion tests aligned with the shared presence contract; a null-present assertion describes retired behavior.
- Do not expose template definitions as editable inputs or copy derived MF/X rows into Global TP data.
- Do not remove backend reconciliation. Saved diagrams and old caches can bypass the latest frontend edge event.
- Do not allow unresolved template tokens into equations or solver payloads.

## Related Pages

- [Excel Import Pipeline](./excel-import-pipeline.md)
- [Component Mapping Import Boundary](./component-mapping-import-boundary.md)
- [Separator and ASU Split Fractions](./separator-asu-split-fractions.md)
- [Custom Edge and Stream Selection](./custom-edge-and-stream-selection.md)
- [Translation and Reverse Translation](./translation-and-reverse-translation.md)
