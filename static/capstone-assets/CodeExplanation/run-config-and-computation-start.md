---
sidebar_position: 13
title: Run Config and Computation Start
description: Explains how run configuration and MTP sliding-horizon data are collected, validated, and handed to compute start and the solver request.
---

# Run Config and Computation Start Code Explanation

## Overview

Run config and computation start are adjacent but separate flows. The current backend reads run configuration definitions from the PostgreSQL `RunConfigs` table, groups them as `runConfigs`, and returns them with domain data. The frontend lets users select solver and algorithm groups from that object, then sends the chosen names, task metadata, and mode-specific options to `/api/compute/start`.

Sliding Horizon is one of those mode-specific values. It is collected in Global TP, persisted with the canvas, and sent as `parameters.global_params.slidingHorizon` only for MTP runs. It is deliberately not part of solver `configuration`.

The frontend also contains a save path that attempts to post edited run config values to `/api/data/run-configs/import`. The current backend route file does not define that route, so this is an implementation gap, not a working backend persistence contract.

## Source Files

Current behavior was checked in these source files:

- `src/src/frontend/src/components/header-bar/index.tsx`
- `src/src/frontend/src/components/header-bar/run-buttons/run-config-modal.tsx`
- `src/src/frontend/src/components/header-bar/run-buttons/universal-runconfig-panel.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`
- `src/src/frontend/src/features/canvas/canvasSlice.ts`
- `src/src/frontend/src/App.tsx`
- `src/src/backend/routes/computeRoutes.ts`
- `src/src/backend/services/computationTaskService.ts`
- `src/src/backend/services/solverEngineApiService.ts`
- `src/src/backend/workers/computationDispatchWorker.ts`
- `src/src/backend/utils/economicCosts.ts`
- `src/src/backend/utils/translation.ts`
- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`

For TP and Economic field ownership, see `time-period-and-economic-flow.md`.

## Purpose

Run config and computation start are separate responsibilities:

- Set Run edits stored solver and algorithm configuration attributes.
- Run selects the solver, algorithm, run name, and maximum computation time for a new task.
- Global TP owns the editable Sliding Horizon value; Run only reads that value and conditionally adds it to an MTP start request.
- The backend compute start route rebuilds solver parameters from the current diagram state and queues the computation task.

Run config does not own TP ranges, durations, Sliding Horizon, economic entities, economic mappings, or generated solver parameters. The computation configuration service also does not own Sliding Horizon; it remains a solver parameter throughout the start and dispatch flow.

## Field Ownership

| Field | Owner | Stored in | Used by compute start |
| --- | --- | --- | --- |
| `runConfigs` | Backend domain data route. | PostgreSQL `RunConfigs`, then Redux domain data. | Solver and algorithm names are selected from these keys. |
| Solver config attributes | `RunConfigModal` and `UniversalRunConfigPanel`. | Currently loaded from `RunConfigs`; frontend save attempts `/api/data/run-configs/import`, but the backend route is missing. | `ComputationTaskService.translateComputationConfig` uses the selected solver name. |
| Algorithm config attributes | `RunConfigModal` and `UniversalRunConfigPanel`. | Currently loaded from `RunConfigs`; frontend save attempts `/api/data/run-configs/import`, but the backend route is missing. | `ComputationTaskService.translateComputationConfig` uses the selected algorithm name. |
| `runName` | `ComputationButton`. | Computation task row. | Required in `/api/compute/start`. |
| `maxComputationTime` | `ComputationButton` UI, then backend route validation. | Computation configuration. | Passed to `translateComputationConfig`. |
| `slidingHorizon` | `GlobalTpButton`, then Redux canvas state. | `canvas.slidingHorizon`, default `1`. | For MTP only, sent and generated as `parameters.global_params.slidingHorizon`. Never added to `configuration`. |
| `parameters.costs` | `computeRoutes.ts` and `translation.ts`. | `diagram.parameters.costs` after start. | Generated from `duration`, `durationUnit`, `tpNodeVers`, `costEntities`, and `costMappings`. |

## Data Flow

1. The domain data route reads PostgreSQL `RunConfigs` through `buildRunConfigs()` and returns the grouped `runConfigs` object with the rest of the domain payload.
2. The frontend stores `runConfigs` in Redux domain state and `HeaderBar` splits keys into solver and algorithm groups with `/algorithm/i`.
3. `Set Run` opens `RunConfigModal` for the selected group. Editable saves currently attempt `/api/data/run-configs/import`; because the backend route is not present, treat that call as frontend intent that still needs backend implementation.
4. `Run` opens `ComputationButton`, which chooses one solver key and one algorithm key from the same `runConfigs` object.
5. The frontend posts `/api/compute/start` with `runName`, `solverName`, `algorithmName`, `maxComputationTime`, and `diagramId`. MTP requests additionally contain `parameters.global_params.slidingHorizon`; Base TP requests omit it.
6. The backend start route resolves TP mode, validates and normalizes Sliding Horizon for MTP, and rebuilds the rest of the diagram parameters.
7. The route attaches the normalized horizon as a sibling of `global_params.task_config`, saves the generated parameters, and uses `ComputationTaskService.translateComputationConfig(...)` to build the separate solver configuration.
8. A waiting computation task is created and queued. The dispatch worker passes the saved diagram parameters to `buildSolveRequest(...)`, which preserves `global_params.slidingHorizon` in the solver request.

## Header Handoff

`HeaderBar` reads `state.domain.data.runConfigs || {}` and exposes two user-facing sections:

- `Set Run` for editing config attributes.
- `Run` through `ComputationButton` for starting a computation.

In `Set Run`, keys that do not match `/algorithm/i` are shown under the Solver dropdown. Keys that match `/algorithm/i` are shown under the Algorithm dropdown. Selecting either key opens `RunConfigModal` with the selected config group.

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

It determines whether the selected group is a solver or algorithm group by checking `/algorithm/i`. The modal then passes the selected group's `attributes` to `UniversalRunConfigPanel`.

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
- `selectedAlgorithm` to the first key that matches `/algorithm/i`.

The computation modal lets the user choose run name, maximum computation time, solver, and algorithm. It can also open read-only `RunConfigModal` views for the selected solver or algorithm.

Before posting a start request, the frontend guards against:

- Unsaved diagrams.
- Incomplete stream edges.
- Duplicate stream-instance edges.
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
  "algorithmName": "Selected Algorithm",
  "maxComputationTime": 50,
  "diagramId": "..."
}
```

When `state.canvas.tpMode === "MTP"`, `ComputationButton` adds the normalized Redux value without changing the existing request fields:

```json
{
  "runName": "Run 1",
  "solverName": "Selected Solver",
  "algorithmName": "Selected Algorithm",
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
6. Checks duplicate stream instances.
7. Reads calculation type from `diagram.parameters.global_params.task_config.task_type`, falling back to `Simulation`.
8. Loads network `tpNodeVers` rows and persisted TP changes.
9. Resolves Base versus MTP mode and resolves the MTP Sliding Horizon value.
10. Merges request-body TP changes over persisted TP changes when supplied.
11. Builds `costsPayload`.
12. Calls `translation(...)`.
13. Attaches active TP-spec metadata and the mode-specific Sliding Horizon field.
14. Writes the returned parameters back to the diagram.
15. Builds the computation configuration from the selected solver and algorithm.
16. Creates a waiting computation task.

The compute route does not read solver parameters from the run config modal state directly. It receives the selected solver and algorithm names and delegates configuration construction to `ComputationTaskService.translateComputationConfig`. Sliding Horizon follows the separate `parameters` path and is not passed into that service.

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

- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`

Focused backend validation commands, run from `src/`:

```bash
npx jest tests/backend/utils/economicCosts.test.ts tests/backend/utils/translationCosts.test.ts --runInBand --coverage=false
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
| Existing Run options | Includes Optimization or DataRec options as before. | Existing parameter translation and configuration remain unchanged. | Adding the horizon branch must not drop sibling request fields. |

## Known Cautions

- Solver and algorithm grouping depends on the config key name matching `/algorithm/i`.
- `UniversalRunConfigPanel` converts numeric-looking strings on save, but deeper semantic validation belongs to the missing run config import/backend path.
- The current frontend attempts `POST /api/data/run-configs/import`; the current backend does not define that route and only reads `RunConfigs` into domain data.
- `parameters.costs` is produced at compute start from persisted diagram fields. It should not be treated as a manual editing surface.
- `canvas.slidingHorizon` is the editable saved value; `parameters.global_params.slidingHorizon` is generated for MTP solver transport.
- Do not add Sliding Horizon to `ComputationConfiguration` or `translateComputationConfig(...)`; that would change the established separation between `configuration` and `parameters`.
- Base TP intentionally omits the frontend request field and removes any stale generated value on the backend.
- The current numeric normalizers truncate positive fractions. Strict-integer behavior requires a coordinated frontend and backend change.
- No solver iteration logic is implemented by this feature.
- `src/src/backend/services/solve_request.json` is not the current source of truth for this flow.
