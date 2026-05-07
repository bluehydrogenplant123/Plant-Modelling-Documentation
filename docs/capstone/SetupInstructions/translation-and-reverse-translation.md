---
title: Translation and Reverse Translation Code Explanation
sidebar_position: 31
description: Explains how HyProNet builds solver-facing parameters and maps solver results back into diagrams, parameters, node model versions, and computed TP changes.
---

## Overview

Translation converts the current diagram, domain snapshot, stream data, time-period rows, TP overrides, and Economic cost data into the solver-facing `parameters` object. Reverse translation consumes callback `results.tps_specs` and pushes machine-generated values back into `parameters.tps_specs`, node model versions, and computed TP changes.

The solver request wrapper is built later by `solverEngineApiService.ts`; this page explains the `parameters` payload and the result-to-state mapping.

## Source Files

- `src/src/backend/utils/translation.ts`: builds `parameters`, including `parameters.tps_specs`, stream data, material data, and optional `parameters.costs`.
- `src/src/backend/utils/reverseTranslation.ts`: parses callback output specs, updates parameter values and node model versions, and returns generated computed TP changes.
- `src/src/backend/services/computationTaskHandler.ts`: calls reverse translation, merges subnetwork/wrapper updates, persists computed TP changes, and updates diagrams and nodes.
- `src/src/backend/utils/storeComputationResultUtils.ts`: stores callback machine-generated values in PostgreSQL result rows after reverse translation.
- `src/src/backend/routes/computeRoutes.ts`: gathers diagram, node, TP, stream, subnetwork, and cost inputs before calling `translation(...)`.
- `src/src/backend/utils/interfaces.ts`: declares the `tps_spec`, `stream_connect`, material, and global parameter interfaces.
- `src/tests/backend/utils/translation.test.ts`: verifies the general translation output format.
- `src/tests/backend/utils/translationCosts.test.ts`: verifies solver-facing Economic cost payloads.
- `src/tests/backend/utils/translationEmbeddedModelVersion.test.ts`: verifies embedded model-version fallback during translation.
- `src/tests/backend/utils/reverseTranslation.test.ts`: verifies reverse translation output updates.

## Purpose and Responsibility

`translation.ts` owns the shape of the solver-facing `parameters` object. It does not create tasks, call the solver, or persist results. It receives already loaded database records and returns a plain object that `computeRoutes.ts` writes to `diagram.parameters`.

`reverseTranslation.ts` owns conversion from solver callback output into in-memory diagram and parameter updates. It does not write MongoDB or PostgreSQL directly. Persistence is coordinated by `handleComputationSuccess(...)` in `computationTaskHandler.ts`.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `canvas` | MongoDB `diagram.canvas`, expanded with subnetwork instances by `computeRoutes.ts` | Source of nodes, edges, streams, handles, and embedded model data. |
| `name`, `description` | MongoDB diagram | Written into `parameters.global_params`. |
| `domainName`, `calcType` | Existing `diagram.parameters.global_params`, snapshot fallback, or default values | Selects solver domain and task type. |
| `domainModelMap` | Snapshot `models` | Resolves model versions, ports, model metadata, and port classes. |
| `nodeCacheData` | MongoDB `node` records plus expanded subnetwork nodes | Supplies persisted `modelVersion`, Mongo document ids, and diagram ids. |
| `subnetworkPortMap` | `buildSubnetworkPortMap(...)` | Resolves wrapper-node edge handles to internal nodes and ports. |
| `tpNodeVers` | MongoDB `tpNodeVers` | Builds TP ranges and model-version ranges. |
| `tpChanges` | MongoDB `tpChanges` merged with optional request TP changes | Supplies explicit non-computed human overrides. |
| `costsPayload` | Diagram Economic fields and TP durations | Builds optional `parameters.costs`. |
| `outputJson` | Solver callback `results` | Reverse-translated into updated parameters, canvas data, and computed TP changes. |

| Output | Destination | Notes |
| --- | --- | --- |
| `parameters` | MongoDB `diagram.parameters`; later solver request body | Contains exact solver-facing fields. |
| `parameters.tps_specs` | Solver and reverse translation | Main variable-spec contract between request and callback. |
| `parameters.costs` | Solver | Optional Economic payload with entities, mappings, and durations. |
| `canvasJson` | `handleComputationSuccess(...)` persistence | Updated with base-period computed values. |
| `generatedTpChanges` | `handleComputationSuccess(...)` persistence | Computed non-base TP values stored with `isComputed: true`. |
| `updatedNodeIds`, `updatedDocumentIds` | `handleComputationSuccess(...)` persistence | Identify MongoDB node records that need `modelVersion` updates. |

## Solver-Facing Parameters Contract

`translation(...)` returns this top-level shape:

```ts
{
  global_params: {
    domain: string,
    project_name: string,
    project_description: string,
    task_config: {
      task_name: string,
      ntp: number,
      task_type: string
    },
    network_config: Array<{
      parent_net: string,
      child_net: string | null
    }>
  },
  models: Array<{
    model_name: string,
    model_version: string,
    phase1: object,
    calc_after_phase1: string,
    phase2: object,
    calc_after_phase2: string
  }>,
  nodes: Array<{
    net_name: string,
    node_name: string,
    model_name: string,
    model_versions: Record<string, string>
  }>,
  tps_specs: Array<TpSpec>,
  stream_connectivity: Array<StreamConnect>,
  material_properties: Array<object>,
  material_fractions: Array<object>,
  costs?: {
    entities: object[],
    mappings: object[],
    duration: object[]
  }
}
```

`node_name` is usually the MongoDB node document id when `nodeCacheData[nodeId].documentId` exists. It falls back to the React Flow node id when no document id is available. The callback path depends on this id mapping when translating results back.

## `parameters.tps_specs`

Every generated TP spec uses these exact fields:

| Field | Source or Rule |
| --- | --- |
| `from_tp`, `to_tp` | Model-version range derived from `tpNodeVers`, defaulting to base range when no split exists. |
| `task` | Current calculation type, usually from `global_params.task_config.task_type`. |
| `network` | Diagram name passed into `translation(...)`. |
| `node_name` | Solver node name, preferably MongoDB node document id. |
| `model_name` | Canvas node model name. |
| `model_version` | Resolved model version name for the TP range. |
| `port` | Port name from the resolved model version. |
| `port_var_name` | Port variable name from the resolved model version. |
| `value` | `base_unit_default_value` coerced by `coerceTpSpecNumericValue(...)`. |
| `spec` | Model var `spec`, except raw `"P"` is sent as `"F"`. |
| `unit` | Model var `base_unit` or an empty string. |
| `var_type` | Model var `var_type`, falling back to `type`, or `null`. |
| `lower_bound`, `upper_bound` | Bounds coerced by `coerceTpSpecNumericValue(...)`. |
| `is_human_input` | Model var flag or `DEFAULT_IS_HUMAN_INPUT_FLAG`. |

`coerceTpSpecNumericValue(...)` returns a finite number for numeric values or numeric strings. It returns `null` for `null`, `undefined`, empty strings, nonnumeric strings, nonfinite numbers, and unsupported types.

Ignored variables are not sent to the solver when they are component aggregate names, derived component variables ending in `_MF` or `_X`, or metadata marks them with `send_to_calc` false.

## `parameters.costs`

`computeRoutes.ts` builds `costsPayload` from:

- `diagram.costEntities`
- `diagram.costMappings`
- `buildCostDurationPayload(diagram, diagramId, tpNodeVers)`

`translation.ts` sanitizes that payload into:

```ts
parameters.costs = {
  entities: object[],
  mappings: object[],
  duration: object[]
}
```

`parameters.costs.entities` has two modes:

- Base-only Economic data stays as rows shaped like `{ name, cost, unit, type }`.
- Multi-TP Economic data or Multi-TP duration data is grouped by lowercased `name`, `unit`, and `type`, then each entity receives sorted `timePeriodCosts` rows shaped like `{ "From TP", "To TP", cost, uncertainty }`.

`parameters.costs.mappings` rows are sanitized to:

```ts
{ network: string, node: string, port: string, var: string, entity: string }
```

`parameters.costs.duration` rows are sanitized to:

```ts
{ "From TP": number, "To TP": number, Duration: number, DurationUnit: string }
```

Durations default to `1`, are rounded to six decimal places, and accept only `minutes`, `hours`, `days`, or `weeks`; unsupported units become `hours`.

## Stream and Material Data

`translation.ts` builds `stream_connectivity` from canvas edges after resolving source and target handles. Subnetwork wrapper nodes are skipped as ordinary solver nodes, but their used edge ports can resolve to internal nodes through `subnetworkPortMap`.

`material_properties` comes from edge stream properties. Runtime stream properties are sanitized, then formatted with normalized numeric fields:

```ts
T0, P0, Cp, H0, MF0, Rho
```

Material property lookup is case-insensitive and can fall back to zero-suffixed keys for names that do not already end in a digit. `material_fractions` filters spreadsheet artifact keys such as `Unnamed`, stream database metadata, and instruction/header text before sending fractions to the solver.

## Data Flow

1. `computeRoutes.ts` loads diagram, snapshot, node rows, TP rows, TP changes, cost data, and subnetwork information.
2. `expandSubnetworkInstances(...)` adds instance diagram nodes to the canvas and node cache.
3. `buildSubnetworkPortMap(...)` resolves wrapper external port locations to internal nodes and ports.
4. `translation(...)` initializes `global_params`, computes `ntp`, and prepares maps for models, ports, and solver node names.
5. It skips subnetwork instance wrapper nodes while still allowing their used edge ports to resolve to internal nodes.
6. It creates solver `models` and `nodes`, including TP model-version ranges.
7. It converts edges to `stream_connectivity`, `material_properties`, and `material_fractions`.
8. It reconstructs each node state from a clean model definition, connected-stream hydration, persisted explicit human overrides, and current request overrides.
9. It emits `parameters.tps_specs`.
10. It appends sanitized `parameters.costs` when a `costsPayload` is present.

## Reverse Translation Contract

The callback result path expects `results.tps_specs` entries with these fields:

```ts
{
  network: string,
  node: string,
  port: string,
  port_var: string,
  machine_generated_values: number[] | Record<string, number> | number
}
```

`reverseTranslation.ts` normalizes callback values as follows:

- Arrays map index `0` to TP `1`, index `1` to TP `2`, and so on.
- Objects use range keys such as `"1"`, `"1-1"`, or `"2-5"`.
- Scalar values become a single-value array.
- Legacy `*_MFZ` and `*_XZ` output rows are skipped when canonical `*_MF` or `*_X` rows exist for the same node and port.

Reverse translation updates two surfaces:

- `parameterJson.tps_specs`: matching specs receive computed `value` updates when they are not protected human inputs.
- Canvas/node model versions: base TP values update `base_unit_default_value` and set `is_computed = true` when the target model var is not protected as human input.

For non-base TP ranges, reverse translation generates computed TP changes instead of mutating base model defaults. Each generated change carries:

```ts
{
  diagramId: string,
  nodeId: string,
  timePeriodId: string,
  portName: string,
  portVarName: string,
  portLocation: number | null,
  portVarValue: number,
  spec: string,
  lowerBound: number,
  upperBound: number,
  unit: string,
  fromTp: number,
  toTp: number,
  isComputed: true
}
```

If an output variable has no matching input `parameters.tps_specs` row, the fallback path can still generate computed TP changes from `machine_generated_values`. Base `1-1` fallback values are not stored as TP changes because base values belong on the node model version.

## Persistence Boundary

`updateCanvasAndParametersFromOutput(...)` returns updated JSON and IDs, but it does not write to the database. `handleComputationSuccess(...)` persists the returned state:

- It writes computed MongoDB `tpChanges` with `isComputed: true`.
- It updates existing computed TP changes before creating missing ones.
- It never overwrites manual user TP changes with computed results.
- It applies wrapper and subnetwork propagation before final diagram and node writes.
- It writes node `modelVersion` updates and diagram `canvas` / `parameters` updates with bounded concurrency.
- It calls `storeComputationResults(...)` to upsert PostgreSQL result rows.

## Error Handling and Edge Cases

- `translation(...)` returns empty arrays when `canvas.nodes` is missing or not an array.
- Missing cached or embedded model versions cause nodes to be skipped in translation.
- Missing edge source, target, or handle data causes the edge to be skipped.
- Missing subnetwork port mappings are logged and prevent that edge endpoint from contributing to solver connectivity.
- Computed `tpChanges` from previous runs are filtered out of translation inputs, so old computed values do not become new user constraints.
- Human-input values are protected from computed overwrite in both parameter updates and node model-version updates.
- Reverse translation logs missing `TpNodeVer` matches and missing `portLocation` information instead of inventing a database target.

## Extension Points

- Add a new solver parameter by updating `translation.ts`, the `parameters` contract in this page, and a focused translation test.
- Add a new TP spec field by updating the `tps_spec` interface, translation generation, reverse matching if needed, and callback result storage metadata.
- Add a new Economic cost field by updating cost UI persistence, `computeRoutes.ts` cost payload assembly, `translation.ts` cost sanitizers, and `translationCosts.test.ts`.
- Add a new callback output format by updating `OutputSpec`, value normalization, and `reverseTranslation.test.ts`.
- Change computed TP persistence in `computationTaskHandler.ts`, not in `reverseTranslation.ts`, because reverse translation returns data but does not write it.

## Testing and Verification

Existing backend utility tests for this area:

- `src/tests/backend/utils/translation.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`
- `src/tests/backend/utils/translationEmbeddedModelVersion.test.ts`
- `src/tests/backend/utils/reverseTranslation.test.ts`
- `src/tests/backend/utils/economicCosts.test.ts`

Focused command:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npx.cmd jest tests/backend/utils/translation.test.ts tests/backend/utils/translationCosts.test.ts tests/backend/utils/translationEmbeddedModelVersion.test.ts tests/backend/utils/reverseTranslation.test.ts --runInBand --coverage=false
```

Manual payload inspection:

1. Run compute from the UI.
2. Inspect `diagram.parameters` or, only when `SAVE_JSON_FILES === 'true'`, read `src/src/backend/services/solve_request.json`.
3. Confirm `parameters.tps_specs` contains the expected TP ranges, bounds, specs, and human-input flags.
4. Confirm `parameters.costs.entities`, `parameters.costs.mappings`, and `parameters.costs.duration` exist when Economic data is present.
5. After callback success, confirm base TP values changed on node model versions and non-base values became computed TP changes.

## Known Cautions

- `src/src/backend/services/solve_request.json` is a runtime diagnostic written by `solverEngineApiService.ts`; it is not the source of truth for translation behavior.
- `src/src/backend/routes/external/callback_response.json` can be stale and should not be trusted without checking its modification time and the current task.
- `src/tests/backend/utils/paramResult.json` can be overwritten by `handleComputationSuccess(...)` and should not be edited as an implementation file.
- Prefer source-level tests and direct source inspection before using generated JSON as confirmation.

## Related Pages

- `docs/SetupInstructions/compute-solver-callback-and-results.md`
- `docs/SetupInstructions/save-diagram-and-node-cache.md`
- `docs/SetupInstructions/subnetwork-blueprint-and-instance-flow.md`
