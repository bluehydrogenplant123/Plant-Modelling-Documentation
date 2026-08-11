---
sidebar_position: 13
title: Run Config and Computation Start
description: Explains how solver configuration, SoluAlgoLib, Optimization/DataRec selections, and MTP sliding-horizon data are collected, validated, and handed to compute start and the solver request.
---

# Run Config and Computation Start Code Explanation

## Overview

Run config and computation start are adjacent but separate flows. The current backend reads solver configuration definitions from the PostgreSQL `RunConfigs` table, groups them as `runConfigs`, and returns them with domain data. The frontend chooses a solver from that object, uses the diagram-specific SoluAlgoLib as the active algorithm, and sends task metadata plus mode-specific options to `/api/compute/start`.

Sliding Horizon is one of those mode-specific values. It is collected in Global TP, persisted with the canvas, and sent as `parameters.global_params.slidingHorizon` only for MTP runs. It is deliberately not part of solver `configuration`.

The frontend also contains a save path that attempts to post edited run config values to `/api/data/run-configs/import`. The current backend route file does not define that route, so this is an implementation gap, not a working backend persistence contract.

## Source Files

Current behavior was checked in these source files:

- `src/src/frontend/src/components/header-bar/index.tsx`
- `src/src/frontend/src/components/header-bar/run-buttons/run-config-modal.tsx`
- `src/src/frontend/src/components/header-bar/run-buttons/universal-runconfig-panel.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/optimization-setup-menu.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/datarec-setup-menu.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/solution-algo-library-module.tsx`
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`
- `src/src/frontend/src/features/canvas/canvasSlice.ts`
- `src/src/frontend/src/App.tsx`
- `src/src/backend/routes/computeRoutes.ts`
- `src/src/backend/services/computationTaskService.ts`
- `src/src/backend/services/solveInputTranslationService.ts`
- `src/src/backend/services/solverEngineApiService.ts`
- `src/src/backend/workers/computationDispatchWorker.ts`
- `src/src/backend/utils/economicCosts.ts`
- `src/src/backend/utils/tpSpecVersionUtils.ts`
- `src/src/backend/utils/translation.ts`
- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`
- `src/tests/backend/services/solveInputTranslationService.test.ts`
- `src/tests/backend/services/solverEngineApiService.test.ts`

For TP and Economic field ownership, see [Time Period and Economic Flow](./time-period-and-economic-flow.md). For active-version selection and metadata, see [TP Spec Version Management](./tp-spec-version-management.md).

## Purpose

Run config and computation start are separate responsibilities:

- Set Run opens stored solver configuration attributes, SoluAlgoLib, and Optimization mode options.
- Run selects the solver, fixed SoluAlgoLib algorithm, run name, and maximum computation time for a new task.
- Active Optimization/DataRec dropdowns own the next-run set, instrument, and measurement selections; Run reduces those selections to ids.
- Global TP owns the editable Sliding Horizon value; Run only reads that value and conditionally adds it to an MTP start request.
- The backend compute start route rebuilds solver parameters from the current diagram state and queues the computation task.

Run config does not own TP ranges, durations, Sliding Horizon, economic entities, economic mappings, or generated solver parameters. The computation configuration service also does not own Sliding Horizon; it remains a solver parameter throughout the start and dispatch flow.

## Field Ownership

| Field | Owner | Stored in | Used by compute start |
| --- | --- | --- | --- |
| `runConfigs` | Backend domain data route. | PostgreSQL `RunConfigs`, then Redux domain data. | Solver names are selected from keys that do not match `/algorithm/i`. |
| Solver config attributes | `RunConfigModal` and `UniversalRunConfigPanel`. | Currently loaded from `RunConfigs`; frontend save attempts `/api/data/run-configs/import`, but the backend route is missing. | `ComputationTaskService.translateComputationConfig` uses the selected solver name. |
| `solution_algo_library` | `SolutionAlgoLibraryModule`. | MongoDB `diagram.solualgolib`. | `buildSolveRequest(...)` normalizes saved rows into solver configuration. |
| `optimizationOptions` | Header Optimization setup plus **Set Run > Optimization Options**. | Header runtime state, then internal queued-task snapshot. | Selects deterministic/DRO mode and saved Objective Function / Constraint Sets. |
| `dataRecOptions` | Header DataRec setup. | Header/Redux runtime state, then internal queued-task snapshot. | Selects one Instrument Set, Plant Measurements, and Objective Function Sets. |
| `runName` | `ComputationButton`. | Computation task row. | Required in `/api/compute/start`. |
| `maxComputationTime` | `ComputationButton` UI, then backend route validation. | Computation configuration. | Passed to `translateComputationConfig`. |
| `slidingHorizon` | `GlobalTpButton`, then Redux canvas state. | `canvas.slidingHorizon`, default `1`. | For MTP only, sent and generated as `parameters.global_params.slidingHorizon`. Never added to `configuration`. |
| Active TP Spec context | TP Specs Apply action and backend version metadata. | MongoDB version set/table plus sparse Base or MTP changes. | Selects the changes used by translation and adds version identity to `global_params.task_config`. |
| `parameters.costs` | `computeRoutes.ts` and `translation.ts`. | `diagram.parameters.costs` after start. | Generated from `duration`, `durationUnit`, `tpNodeVers`, `costEntities`, and `costMappings`. |

## Data Flow

1. The domain data route reads PostgreSQL `RunConfigs` through `buildRunConfigs()` and returns the grouped `runConfigs` object with the rest of the domain payload.
2. The frontend stores `runConfigs` in Redux domain state and filters non-algorithm keys into the Solver menu.
3. `Set Run` opens `RunConfigModal` for a selected solver. Editable saves currently attempt `/api/data/run-configs/import`; because the backend route is not present, treat that call as frontend intent that still needs backend implementation.
4. Set Run's Algorithm menu opens `SolutionAlgoLibraryModule`, and active Optimization additionally exposes deterministic/DRO options.
5. Active Optimization/DataRec dropdowns collect next-run selections independently of their shared editors.
6. `Run` opens `ComputationButton`, which chooses one solver and uses `SoluAlgoLib` as the algorithm.
7. The frontend posts `/api/compute/start` with task fields plus the active type's identifier-only `optimizationOptions` or `dataRecOptions`. MTP requests additionally contain `parameters.global_params.slidingHorizon`; Base TP requests omit it.
8. The backend resolves selected ids into an authoritative queued snapshot, resolves TP mode, validates and normalizes Sliding Horizon for MTP, and rebuilds the rest of the diagram parameters.
9. The route attaches the normalized horizon as a sibling of `global_params.task_config`, saves the generated parameters, and uses `ComputationTaskService.translateComputationConfig(...)` to build the separate solver configuration.
10. A waiting computation task is created and queued. The dispatch worker passes task selection, saved diagram parameters, equations, collections, and SoluAlgoLib rows to `buildSolveRequest(...)`.

## Header Handoff

`HeaderBar` reads `state.domain.data.runConfigs || {}` and exposes these connected surfaces:

- `Calc Type` for Optimization/DataRec next-run selection.
- `Set Run` for solver attributes, SoluAlgoLib, and Optimization mode.
- `Run` through `ComputationButton` for starting a computation.

In `Set Run`, keys that do not match `/algorithm/i` are shown under the Solver dropdown. The Algorithm dropdown no longer lists generic run-config keys; its active entry is `SoluAlgoLib`, which opens the diagram-specific solution algorithm library.

The same computing-disable rule is passed as `readOnly` to `RunConfigModal`. In read-only mode, the modal renders the config values but does not expose save/cancel actions.

## Run Config Modal

`RunConfigModal` receives:

```ts
{
  show,
  onHide,
  selectedType,
  runConfigs,
  readOnly
}
```

The current Header path opens this modal for solver groups. The modal still derives `exportType` with `/algorithm/i` for compatibility, then passes the selected group's `attributes` to `UniversalRunConfigPanel`.

`UniversalRunConfigPanel` renders attributes as:

- A 1D table when `attributeName` does not contain `_`.
- A 2D table when `attributeName` contains `_`.

On save, numeric-looking strings are converted to numbers. Empty numeric strings become `null`. The panel returns a map keyed by `attributeName`.

`RunConfigModal` then creates an updated run config group where each attribute receives the new `defaultValue`. It posts:

```http
POST /api/data/run-configs/import
```

Current frontend payload shape:

```json
{
  "exportType": "<solver-or-algorithm-from-selectedType>",
  "diagramId": "...",
  "runConfigs": {
    "<selectedType>": {
      "attributes": []
    }
  }
}
```

`exportType` is derived from `selectedType`: `/algorithm/i.test(selectedType)` produces `algorithm`; every other selected type produces `solver`.

Current caution: the frontend call exists, but the current backend only reads `RunConfigs` from PostgreSQL and returns them with domain data. `dataRoutes.ts` does not currently define `POST /api/data/run-configs/import`, so edited values do not have a confirmed backend persistence route until that gap is implemented.

If a matching backend route is added and returns success, the frontend dispatches `updateRunConfig`, refreshes domain data when `domainId` exists, alerts success, and closes the modal.

## Computation Button

`ComputationButton` reads the same `runConfigs` object. When configs load, it defaults:

- `selectedSolver` to the first key that does not match `/algorithm/i`.
- `selectedAlgorithm` to the fixed compatibility name `SoluAlgoLib`.

The computation modal lets the user choose run name, maximum computation time, solver, fixed SoluAlgoLib algorithm, and log level. It can also open a read-only `RunConfigModal` view for the selected solver.

Before posting a start request, the frontend guards against:

- Unsaved diagrams.
- Incomplete stream edges.
- Missing or duplicate stream connection names; repeated Excel/material instances are allowed when non-empty names differ.
- Blank run name.
- Duplicate run name.
- Missing selected solver.
- Missing selected algorithm.
- Double-submit while a start request is already in progress.

The common Base TP start body is:

```json
{
  "runName": "Run 1",
  "solverName": "Selected Solver",
  "algorithmName": "SoluAlgoLib",
  "logLevel": "development",
  "maxComputationTime": 50,
  "diagramId": "..."
}
```

When Optimization is active, the request also contains selected set ids and mode:

```json
{
  "optimizationOptions": {
    "mode": "deterministic",
    "objectiveFunctionSetIds": ["objective-set-1"],
    "additionalConstraintSetIds": ["constraint-set-1"]
  }
}
```

When DataRec is active, the request instead contains selected Instrument Set, measurement, and Objective Function Set ids:

```json
{
  "dataRecOptions": {
    "instrumentSetId": "64b000000000000000000003",
    "measurementIds": ["64b000000000000000000005"],
    "objectiveFunctionSetIds": ["objective-set-1"]
  }
}
```

The full editor objects do not cross the trust boundary. See [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md) for authoritative resolution and solver shapes.

When `state.canvas.tpMode === "MTP"`, `ComputationButton` adds the normalized Redux value without changing the existing request fields:

```json
{
  "runName": "Run 1",
  "solverName": "Selected Solver",
  "algorithmName": "SoluAlgoLib",
  "logLevel": "development",
  "maxComputationTime": 50,
  "diagramId": "...",
  "parameters": {
    "global_params": {
      "slidingHorizon": 1
    }
  }
}
```

The `parameters` branch is omitted when the frontend TP mode is `BASE`. Sliding Horizon does not alter the `configuration` request or the selected solver/algorithm structure.

The frontend computes `maxComputationTime` from the UI value and selected unit before sending. The backend treats it as the numeric value used to build the computation configuration and enforces its minimum allowed value.

## Backend Start Route

`POST /api/compute/start` validates:

- `diagramId`
- `maxComputationTime`
- `runName`
- `solverName`
- `algorithmName`

The route rejects missing required fields and computation times below the backend minimum.

After validation, the route:

1. Loads the diagram with snapshot data.
2. Checks that the user can access the diagram.
3. Loads node documents and cache data.
4. Expands subnetwork nodes into the assembled canvas.
5. Checks for missing model versions.
6. Checks for missing or duplicate stream connection names after subnetwork expansion.
7. Reads calculation type from `diagram.parameters.global_params.task_config.task_type`, falling back to `Simulation`.
8. Resolves the active type's `optimizationOptions` or `dataRecOptions` against saved sets, Instrument Sets, mappings, and measurements.
9. Loads network `tpNodeVers` rows and persisted TP changes.
10. Resolves Base versus MTP mode and resolves the MTP Sliding Horizon value.
11. Merges request-body TP changes over persisted TP changes when supplied.
12. Builds `costsPayload`.
13. Calls `translation(...)`.
14. Attaches active TP Spec metadata and the mode-specific Sliding Horizon field. Version selection is isolated by diagram, TP scope, and calculation type.
15. Writes the returned parameters back to the diagram.
16. Builds the computation configuration from the selected solver and SoluAlgoLib indicator, then attaches the internal selected-input snapshot.
17. Creates a waiting computation task.

The compute route does not read solver parameters from the run config modal state directly. It receives the selected solver and algorithm names and delegates the configuration shell to `ComputationTaskService.translateComputationConfig`. Sliding Horizon follows the separate base `parameters` path. Optimization/DataRec selections follow a third path: an internal `configuration.selected_inputs` snapshot that `buildSolveRequest(...)` later moves to `parameters.solve_inputs`.

## Sliding Horizon Handoff

### Canonical Contract

Sliding Horizon is one scalar positive numeric value. The current editable and API names are:

| Boundary | Canonical field |
| --- | --- |
| Redux | `state.canvas.slidingHorizon` |
| Saved diagram canvas | `canvas.slidingHorizon` |
| MTP compute request | `parameters.global_params.slidingHorizon` |
| Generated diagram parameters | `parameters.global_params.slidingHorizon` |
| Final solver request | `parameters.global_params.slidingHorizon` |

The corrected implementation does not use `globalTimePeriods`, `slidingHorizonStart`, `slidingHorizonEnd`, a `"Sliding Horizon"` object, or `configuration.slidingHorizon`. The backend reads `parameters.global_params.task_config.slidingHorizon` only as a legacy fallback and removes that nested copy when rebuilding parameters.

### Frontend Ownership and Persistence

`GlobalTpButton` presents one number input and a `Save Sliding Horizon` button. The default is `1`. A valid value is placed in `state.canvas.slidingHorizon` with `setSlidingHorizon(...)`, and `useSaveDiagram` writes it to `canvas.slidingHorizon` on the diagram.

When a diagram is loaded, the frontend reads the first available value in this order:

1. `canvas.slidingHorizon`.
2. `parameters.global_params.slidingHorizon`.
3. Legacy `parameters.global_params.task_config.slidingHorizon`.
4. Default `1`.

The Global TP UI rejects non-finite values and values below `1`, displays `Sliding Horizon must be a positive integer.`, and disables save/apply actions while invalid. The current normalizer applies `Math.trunc`, so fractional positive values are truncated rather than rejected.

### Backend Resolution

`computeRoutes.ts` resolves the effective diagram TP mode from these sources:

1. `diagram.tpMode`.
2. `diagram.canvas.tpMode`.
3. Presence of `tpNodeVers` rows as a legacy fallback.

Only MTP mode consumes the request value. For MTP, the winning value is selected in this order:

1. `req.body.parameters.global_params.slidingHorizon`.
2. Persisted `diagram.parameters.global_params.slidingHorizon`.
3. Persisted `diagram.canvas.slidingHorizon`.
4. Legacy `diagram.parameters.global_params.task_config.slidingHorizon`.
5. Default `1`.

If an MTP request explicitly supplies an invalid value, the route returns HTTP `400` with `Sliding Horizon must be a positive integer`. If the request omits the field, a persisted value or the default keeps older clients compatible.

After `translation(...)` rebuilds the runtime parameters and TP-spec metadata is attached, `attachSlidingHorizonGlobalParam(...)` performs the final placement:

- MTP: sets `parameters.global_params.slidingHorizon`.
- Base TP: removes `parameters.global_params.slidingHorizon`.
- Both modes: removes the legacy `parameters.global_params.task_config.slidingHorizon` copy when a `task_config` object exists.

This final attachment prevents translation from discarding the value and ensures stale MTP data cannot leak into a Base TP solver request.

### Solver Request Boundary

The compute route saves the generated parameter object on the diagram before queue dispatch. `computationDispatchWorker.ts` later reads `diagram.parameters`, and `buildSolveRequest(...)` spreads those parameters into the outbound request. The relevant MTP excerpt is:

```json
{
  "parameters": {
    "global_params": {
      "slidingHorizon": 1
    }
  }
}
```

Existing solver configuration fields remain in the separate top-level `configuration` object. This integration only collects, persists, validates, and transports Sliding Horizon; it does not implement solver-side sliding-horizon behavior.

## TP and Economic Handoff

The cost payload assembled by compute start is:

```ts
{
  entities: cloneCostEntityFields(diagram.costEntities),
  mappings: Array.isArray(diagram.costMappings) ? diagram.costMappings : [],
  duration: buildCostDurationPayload(diagram, diagramId, tpNodeVersRows)
}
```

`buildCostDurationPayload` uses valid `tpNodeVers` ranges for the current network. If there are no valid TP rows, it falls back to:

```ts
{
  fromTp: 1,
  toTp: 1,
  duration: diagram.duration || 1,
  durationUnit: diagram.durationUnit || "hours"
}
```

`translation.ts` then writes `parameters.costs`:

- `entities` are normalized and may be grouped into `timePeriodCosts`.
- `mappings` are normalized to network/node/port/var/entity.
- `duration` is normalized to solver keys `From TP`, `To TP`, `Duration`, and `DurationUnit`.

This is the key boundary: TP and Economic UI fields are persisted before start, and compute start converts those persisted fields into `parameters.costs`.

## Generated Parameters

`translation.ts` rebuilds the runtime parameter object. It also rebuilds `tps_specs` from:

- Clean model definitions.
- Connected stream values.
- Current calculation type.
- Explicit TP/spec overrides.

This means `diagram.parameters` after a run start is generated state. Do not use generated runtime files or stale parameter snapshots as the source of truth for TP or Economic editing behavior.

## Testing

Relevant backend tests are present at:

- `src/tests/backend/services/solveInputTranslationService.test.ts`
- `src/tests/backend/services/solverEngineApiService.test.ts`
- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`

Focused backend validation commands, run from `src/`:

```bash
npx jest tests/backend/services/solveInputTranslationService.test.ts tests/backend/services/solverEngineApiService.test.ts tests/backend/utils/economicCosts.test.ts tests/backend/utils/translationCosts.test.ts --runInBand --coverage=false
npm run build
```

Frontend lint, run from `src/src/frontend/`:

```bash
npm run lint -- --quiet
```

For documentation-only edits, also run:

```bash
git diff --check -- docs/CodeExplanation/time-period-and-economic-flow.md docs/CodeExplanation/run-config-and-computation-start.md
```

There is no dedicated automated Sliding Horizon request test in the current repository. Manually verify the behavior at the request and generated-parameter boundaries:

| Scenario | Frontend request | Backend/generated parameters | Regression to watch |
| --- | --- | --- | --- |
| MTP with value `3` | Contains `parameters.global_params.slidingHorizon: 3`. | Retains the same normalized value under `global_params`. | Field must not move into `configuration` or `task_config`. |
| MTP with request field omitted | Older/manual client sends no horizon field. | Uses persisted current value, saved canvas value, legacy value, or default `1` in that order. | Older clients must remain runnable. |
| MTP with invalid explicit value | Contains a non-finite value or value below `1`. | Returns HTTP `400`; no task is queued. | Invalid request must not silently overwrite saved state. |
| Base TP after an earlier MTP run | Omits the field. | Removes current and legacy solver-facing horizon fields. | Stale MTP horizon must not reach the Base TP solver request. |
| Optimization run | Includes `optimizationOptions` id arrays and mode. | Queued snapshot becomes Optimization `parameters.solve_inputs`. | Sliding Horizon or run-config changes must not drop selected sets. |
| DataRec run | Includes `dataRecOptions` ids. | Queued snapshot expands authoritative mappings and selected measurements. | Sliding Horizon or run-config changes must not drop DataRec selections. |

## Known Cautions

- Solver grouping depends on config key names not matching `/algorithm/i`; the active algorithm path is now the separate diagram-specific SoluAlgoLib module.
- `UniversalRunConfigPanel` converts numeric-looking strings on save, but deeper semantic validation belongs to the missing run config import/backend path.
- The current frontend attempts `POST /api/data/run-configs/import`; the current backend does not define that route and only reads `RunConfigs` into domain data.
- `parameters.costs` is produced at compute start from persisted diagram fields. It should not be treated as a manual editing surface.
- `canvas.slidingHorizon` is the editable saved value; `parameters.global_params.slidingHorizon` is generated for MTP solver transport.
- Do not add Sliding Horizon to `ComputationConfiguration` or `translateComputationConfig(...)`; that would change the established separation between `configuration` and `parameters`.
- `configuration.selected_inputs` is an intentional internal snapshot for selected set membership and expanded DataRec values. `buildSolveRequest(...)` removes it from configuration and emits `parameters.solve_inputs`; full equation definitions are still reloaded from the diagram at dispatch.
- Optimization/DataRec dropdown **Apply** updates runtime selection only. Saving an editor record and selecting it for a run are separate actions.
- Base TP intentionally omits the frontend request field and removes any stale generated value on the backend.
- The current numeric normalizers truncate positive fractions. Strict-integer behavior requires a coordinated frontend and backend change.
- No solver iteration logic is implemented by this feature.
- Saving an inactive TP Spec version does not affect compute start. Only the active version for the resolved scope and calculation type is selected.
- `src/src/backend/services/solve_request.json` is not the current source of truth for this flow.

## Related Pages

- [Time Period and Economic Flow](./time-period-and-economic-flow.md)
- [TP Spec Version Management](./tp-spec-version-management.md)
- [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md)
- [Compute, Solver Callback, and Results](./compute-solver-callback-and-results.md)
