---
sidebar_position: 12
title: Time Period and Economic Flow
description: Explains how base time period, multi-time-period ranges, sliding horizon, TP Spec versions, economic costs, and compute-start parameters are edited and persisted.
---

# Time Period and Economic Flow Code Explanation

## Overview

The TP and Economic flow owns diagram-level duration, Multi-TP ranges, the MTP sliding-horizon value, TP Spec version selection, node model-version ranges, cost entities, and cost mappings. User edits are saved to diagram fields or TP rows first; compute start later converts those persisted fields into solver-facing parameters.

The important boundary is that `canvas.slidingHorizon` is the editable persistence source for Sliding Horizon, while `parameters.global_params.slidingHorizon` is the MTP solver-facing value generated at compute start. Similarly, `parameters.costs` is generated runtime state rather than the editing source of truth for Base TP, Global TP, Base Economic, or Multi-TP Economic behavior.

This page keeps the cross-feature view. For version identity, sparse storage, endpoint contracts, Base overlays, MTP compatibility, and callback/result behavior, use [TP Spec Version Management](./tp-spec-version-management.md) as the detailed maintenance reference.

## Source Files

Current behavior was checked in these source files:

- `src/src/frontend/src/components/header-bar/header-buttons/base-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/time-period-viewer.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/tp-specs-button.tsx`
- `src/src/frontend/src/components/modal/tabs/info-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/specs-tab.tsx`
- `src/src/frontend/src/components/modal/useNodeDataPrefetch.ts`
- `src/src/frontend/src/components/header-bar/header-buttons/cost-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/cost-button-utils.ts`
- `src/src/frontend/src/components/header-bar/index.tsx`
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`
- `src/src/frontend/src/features/canvas/canvasSlice.ts`
- `src/src/frontend/src/App.tsx`
- `src/src/backend/routes/dataRoutes.ts`
- `src/src/backend/routes/computeRoutes.ts`
- `src/src/backend/services/solverEngineApiService.ts`
- `src/src/backend/workers/computationDispatchWorker.ts`
- `src/src/backend/utils/tpSpecVersionUtils.ts`
- `src/src/backend/utils/economicCosts.ts`
- `src/src/backend/utils/translation.ts`
- `src/src/backend/utils/storeComputationResultUtils.ts`
- `src/src/backend/prisma/mongodb/schema.prisma`
- `src/src/backend/prisma/postgres/schema.prisma`
- `src/src/backend/prisma/postgres/migrations/20260630000100_add_tp_spec_version_to_computation_results/migration.sql`
- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/storeComputationResultUtils.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`

Legacy docs were used only as historical density references:

- `docs-archive/PreviousDoc/CodeExplanation/global-tp.md`
- `docs-archive/PreviousDoc/CodeExplanation/tp-duration-base-and-solve-request.md`
- `docs-archive/PreviousDoc/CodeExplanation/tp-specs-panel.md`
- `docs-archive/PreviousDoc/CodeExplanation/timePeriodViewer.md`

## Purpose

The TP and Economic flow owns four related data surfaces:

- Time structure and duration, stored on the diagram for the base period and on `tpNodeVers` rows for multi-time-period ranges.
- The MTP sliding-horizon size, edited in Global TP, stored with the canvas, and copied into solver-facing global parameters only for MTP computations.
- TP Spec versions, stored as version metadata plus sparse Base or MTP changes and bound to computation by the active version.
- Economic cost definitions and mappings, stored on the diagram and converted into solver-facing `parameters.costs` only when computation starts.

The UI does not edit solver-facing `parameters` directly. The backend start route rebuilds `parameters.costs` from the current diagram, TP rows, and economic rows, and separately attaches the normalized Sliding Horizon value after translation.

## Field Ownership

| Field | Owner | Stored in | Computation handoff |
| --- | --- | --- | --- |
| `duration` | Base TP owns diagram-level base duration. Global TP owns TP-row duration. | `diagram.duration`; `tpNodeVers.duration` | `computeRoutes.ts` builds `parameters.costs.duration`. |
| `durationUnit` | Base TP owns diagram-level base unit. Global TP owns TP-row unit. | `diagram.durationUnit`; `tpNodeVers.durationUnit` | `computeRoutes.ts` normalizes to `DurationUnit`. |
| Base TP spec versions | The TP Specs panel in Base TP mode. | `tp_spec_version_sets`, `tp_spec_version_tables`, and sparse `tp_spec_base_changes`. | `computeRoutes.ts` resolves the active Base TP version for the current calculation type before translation. |
| Multi-TP spec versions | The TP Specs panel in Multi-TP mode. | `tp_spec_version_sets`, `tp_spec_version_tables`, and version-scoped `tp_changes`. | `computeRoutes.ts` resolves the active MTP version for the current calculation type before translation. |
| `slidingHorizon` | `GlobalTpButton` and Redux canvas state. | `canvas.slidingHorizon`; default `1`. Older locations are read only as compatibility fallbacks. | Sent and retained as `parameters.global_params.slidingHorizon` only in MTP mode. |
| `costEntities` | Base Economic and Multi-TP Economic panels. Backend MTP initialization may seed or stretch rows. | `diagram.costEntities` | `translation.ts` sanitizes into `parameters.costs.entities`. |
| `costMappings` | Base Economic and Multi-TP Economic panels. Backend MTP initialization may stretch rows. | `diagram.costMappings` | `translation.ts` sanitizes into `parameters.costs.mappings`. |
| `parameters.costs` | Backend compute start route and translation layer. | `diagram.parameters.costs` after `/api/compute/start` | Solver-facing payload. Not the source of truth for editing. |

## Data Flow

1. Base TP edits save `duration` and `durationUnit` to the diagram through `/api/data/diagrams/:diagramId/base-duration`.
2. Global TP edits read and write `tpNodeVers` rows for the current network, including TP ranges, durations, units, and model versions.
3. The same Global TP modal validates Sliding Horizon, stores it in Redux, and triggers the diagram save path so it is persisted as `canvas.slidingHorizon`.
4. TP Specs edits are stored as versioned sparse changes. Base TP specs use `tp_spec_base_changes`; Multi-TP specs use version-scoped `tp_changes`.
5. Applying a TP spec version marks that version active only for its scope and calculation type.
6. Base Economic and Multi-TP Economic edits save `costEntities` and `costMappings` to the diagram through `/api/data/diagrams/:diagramId/costs`.
7. Multi-TP initialization or range changes may call `/api/data/diagrams/:diagramId/costs/initialize-mtp` so economic rows match the current TP structure.
8. When an MTP run starts, `ComputationButton` sends the Redux value as `parameters.global_params.slidingHorizon`. Base TP requests omit this request field.
9. `computeRoutes.ts` loads the diagram, TP rows, active TP spec version, cost entities, and cost mappings, then independently validates and resolves Sliding Horizon.
10. `computeRoutes.ts` builds `costsPayload` from persisted diagram fields plus `buildCostDurationPayload(...)`.
11. `translation.ts` sanitizes that payload and writes solver-facing `parameters.costs`.
12. After translation, the route attaches TP-spec metadata and the MTP-only Sliding Horizon field, saves the generated `parameters` back to the diagram, and queues the computation task.

Saved economic entity rows use this storage shape:

```ts
{
  generatedBy,
  scope,
  fromTp,
  toTp,
  name,
  cost,
  uncertainty,
  unit,
  type
}
```

Saved economic mapping rows use this storage shape:

```ts
{
  scope,
  fromTp,
  toTp,
  network,
  node,
  port,
  var,
  entity
}
```

`scope` is intentionally backward-compatible:

- A row with `scope: "base"` is a base-period row.
- A legacy unscoped `1-1` row is also treated as base.
- A row with `scope: "mtp"` is a Multi-TP row, even when its range is `1-1`.
- A legacy unscoped row outside `1-1` is treated as Multi-TP.

## Base TP

`BaseTpButton` edits the base duration for a saved diagram.

The modal reads `diagram.duration` and `diagram.durationUnit` from `GET /api/data/diagrams/:diagramId`. Missing or invalid values fall back to `1 hours`.

On save it calls:

```http
PUT /api/data/diagrams/:diagramId/base-duration
```

with:

```json
{
  "duration": 1,
  "durationUnit": "hours"
}
```

The backend validates that duration is positive and the unit is one of `minutes`, `hours`, `days`, or `weeks`. It then updates the current diagram and related network diagrams so subnetworks use the same base duration.

Base TP is guarded against accidental use after Multi-TP ranges exist. The button is disabled when there is no `diagramId`, or when `/api/data/tpnodevers?diagramId=...` contains any range other than `1-1`. If the guard fetch fails, the component logs the error and leaves the button available instead of blocking the user.

## Global TP

`GlobalTpButton` owns the editable Multi-TP structure. It reads the current diagram, subnetwork diagrams, nodes, and all `tpNodeVers` rows for the network.

Each saved row can include:

```ts
{
  diagramId,
  nodeId,
  timePeriodId,
  fromTp,
  toTp,
  duration,
  durationUnit,
  modelVersion
}
```

The range validator enforces these rules:

- Ranges must start at `1`.
- Ranges must be continuous.
- Ranges must not overlap.
- The last `toTp` must match the total TP count.
- Every range must have a positive duration.
- `durationUnit` must be `minutes`, `hours`, `days`, or `weeks`.

On apply, the component builds add, update, and delete sets for `/api/data/tpnodevers`. Structural changes can clear TP-specific values, computation results, and cache state. When new ranges are added, the component can clone existing base or first-period TP changes into the new ranges.

Global TP also prepares economic data for the new TP ranges. It calls:

```http
POST /api/data/diagrams/:diagramId/costs/initialize-mtp
```

when the network is converted to Multi-TP, ranges are appended, ranges are reduced, or existing ranges change. If base cost data is missing during base-to-MTP expansion, the UI warns that base-period cost data does not exist and the user should upload Multi-TP cost data.

### Sliding Horizon UI and State

The Global TP modal renders Sliding Horizon as one inline row above the TP count controls:

- A `Sliding Horizon:` label.
- A number input named `slidingHorizon`, with `min={1}` and `step={1}`.
- A `Save Sliding Horizon` button using the same primary button style as `Build Grid`.
- An inline validation message when the current input cannot be normalized.

The initial value is `1`. When an existing diagram is opened, both `App.tsx` and `GlobalTpButton` restore the first available value in this compatibility order:

1. `canvas.slidingHorizon`, the current editable persistence location.
2. `parameters.global_params.slidingHorizon`, the current solver-facing location.
3. `parameters.global_params.task_config.slidingHorizon`, the legacy location.
4. Default value `1`.

`slidingHorizonInput` is local string state so the input can represent an incomplete edit. A valid save dispatches `setSlidingHorizon(value)` to `state.canvas.slidingHorizon`. `useSaveDiagram` includes that Redux value in every saved canvas:

```json
{
  "canvas": {
    "tpMode": "MTP",
    "slidingHorizon": 1
  }
}
```

The standalone save action is visible before the TP range grid is built. It stores the value, closes the modal, and triggers the normal diagram save hook. After the range grid is built, `Apply to All Nodes` validates and stores Sliding Horizon together with the TP range operation; the separate save button is no longer shown.

### Sliding Horizon Validation

The frontend uses the same normalization rule when loading, saving, applying TP changes, and constructing the compute request:

1. Convert the input with `Number(...)`.
2. Reject non-finite values and values below `1`.
3. Normalize accepted values with `Math.trunc(...)`.
4. Fall back to `1` only on diagram load or compute-payload normalization; direct UI save and apply actions remain blocked while the input is invalid.

An invalid Global TP input displays `Sliding Horizon must be a positive integer.` The standalone save button and `Apply to All Nodes` are disabled, and active TP apply work also disables the input. The backend repeats the finite-and-positive check for MTP requests and returns HTTP `400` for an explicitly supplied invalid value.

Because the current helper uses `Math.trunc`, a fractional value at or above `1` is truncated rather than rejected. Contributors who change this to strict integer validation must update the UI, frontend payload normalization, backend validation, migration behavior, and tests together.

## Time Period Viewer

`TimePeriodViewer` is currently a model-version viewer/editor, not the owner of range structure or duration. The source has:

```ts
const TP_STRUCTURE_EDITING_ENABLED = false;
```

With that flag disabled, the modal tells the user that TP range editing is temporarily disabled. It still reads `tpNodeVers`, diagrams, and nodes, and it can save model-version updates, but it does not expose active duration or range-structure editing controls.

The button renders only after verification state allows it. The header keeps the button available and relies on this component to control the detailed editing surface.

## TP Specs

`TPSpecsButton` edits node model variable specs and values, not TP range duration. It is version-aware and works in two separate scopes:

- Base TP scope for single-period specs.
- Multi-TP scope for time-period-specific specs.

Each scope is also separated by calculation type. Simulation, Optimization, DataRec, and ParamUpdt each have their own version list and active version. Creating `V2` while the Simulation tab is selected creates only the Simulation version table; it does not create matching V2 tables for the other calculation types.

The complete code-level explanation is in [TP Spec Version Management](./tp-spec-version-management.md). The summary below defines the boundaries that matter when changing adjacent TP or Economic code.

Default Base TP logical table names are:

| Calculation type | Table name |
| --- | --- |
| Simulation | `TPSPECV1` |
| Optimization | `TPSPECOPTV1` |
| DataRec | `TPSPECDRV1` |
| ParamUpdt | `TPSPECPEV1` |

Default Multi-TP logical table names use the same suffixes with an `M` prefix:

| Calculation type | Table name |
| --- | --- |
| Simulation | `MTPSPECV1` |
| Optimization | `MTPSPECOPTV1` |
| DataRec | `MTPSPECDRV1` |
| ParamUpdt | `MTPSPECPEV1` |

The version metadata is stored in MongoDB:

```ts
TpSpecVersionSet {
  diagramId,
  scope,
  calcType,
  versionNo,
  code,
  displayName,
  isDefault,
  isActive,
  sourceVersionSetId,
  createdAt,
  updatedAt
}

TpSpecVersionTable {
  diagramId,
  versionSetId,
  scope,
  calcType,
  logicalName,
  createdAt,
  updatedAt
}
```

Large TP spec tables are not duplicated in full. The backend stores only sparse user changes:

- Base TP changes are stored in `TpSpecBaseChange` with a JSON patch for value, spec, bounds, unit, and type fields.
- Multi-TP changes are stored in `TpChanges` with `tpSpecVersionSetId`, `tpSpecVersionTableId`, `calcType`, and `changeSource`.

The table shown in the UI is materialized on demand. Base starts from node model-version defaults and overlays the selected Base patch set. MTP expands those defaults across `TpNodeVers` ranges and overlays the selected table's `TpChanges`. Creating a version copies sparse manual changes, not a frozen full-table snapshot; computed MTP rows are not copied.

The frontend uses these version endpoints:

```http
GET /api/data/diagrams/:diagramId/tp-spec-versions
POST /api/data/diagrams/:diagramId/tp-spec-versions
PATCH /api/data/tp-spec-versions/:versionSetId
POST /api/data/tp-spec-versions/:versionSetId/apply
DELETE /api/data/tp-spec-versions/:versionSetId
GET /api/data/diagrams/:diagramId/tp-spec-table
PUT /api/data/tp-spec-tables/:versionTableId/changes
```

`Save` and `Apply` are intentionally different:

- Selecting a version changes which table is displayed and edited; it does not change the network's active version.
- `Save` persists edits to the selected version table. Saving a non-active version does not change the network.
- `Apply` marks the selected version active for the current scope and calculation type, refreshes the TP Specs panel, and updates the values used by the network and the next solve request.
- `V1 Default` is created automatically and cannot be deleted. If an active non-default version is deleted, that scope and calculation type fall back to V1.

In Base mode, ordinary node reads overlay the active Base patch set for the diagram's persisted calculation type. The UI Apply path also performs a calculation-type-only diagram update and refreshes frontend node cache. The backend Apply endpoint itself only toggles version metadata, so non-UI API clients must preserve the calculation-type handoff explicitly.

For MTP, node-modal `/tpchanges` reads and writes are scoped to the active version context. The Info, Node Vars, Specs, and prefetch paths pass `calcType` so one calculation-type tab does not read another tab's changes. Legacy unversioned MTP rows remain readable and are adopted by default-version compatibility logic.

At compute start, `computeRoutes.ts` resolves the active TP spec context with `getActiveTpSpecContext(...)`, overlays the active sparse changes, and attaches version metadata to `parameters.global_params.task_config`:

```ts
{
  tp_spec_scope,
  tp_spec_version,
  tp_spec_version_name,
  active_tp_spec_table,
  active_tp_spec_version_set_id,
  active_tp_spec_version_table_id
}
```

Callback result storage copies this metadata into PostgreSQL `ComputationResults` columns `calc_type`, `tp_spec_scope`, `tp_spec_version`, and `tp_spec_table` so stored rows can be traced back to the version used for the solve. These columns provide a backend traceability contract; a result UI must opt in before users can filter or display every field.

## Economic Panels

`CostButtons` is used in two modes:

- Base Economic uses `showTpRanges={false}` from the `Economic` header section.
- Multi-TP Economic uses `showTpRanges` from the `Multi-TP` header section.

The Multi-TP version is read-only when the header cannot detect a Multi-TP network, or when the computing-disable rule for cost buttons is active.

The component loads `diagram.costEntities` and `diagram.costMappings`. In Multi-TP mode it also loads `tpNodeVers` to discover the available ranges and maximum TP. If existing saved economic rows do not match the current TP ranges, the component can initialize Multi-TP data through `/api/data/diagrams/:diagramId/costs/initialize-mtp`.

Save validates that all entity and mapping ranges are finite, start at TP `1` or later, and have `toTp >= fromTp`. It then merges rows with normalized ranges, inferred scope, trimmed names, and deduplication keys before calling:

```http
PUT /api/data/diagrams/:diagramId/costs
```

The `Apply Base Economic` action copies base economic rows into all available Multi-TP ranges with `scope: "mtp"`. Base rows remain base rows, and generated MTP rows are saved separately.

## Backend Economic Normalization

`economicCosts.ts` is the storage-normalization boundary for economic rows.

It accepts TP aliases such as `fromTp`, `fromTP`, `from_tp`, and `From TP`, and the matching `toTp` aliases. It rejects invalid ranges. It defaults missing row ranges to `1-1`.

`buildMtpEconomicDataFromBase` preserves base rows and stretches Multi-TP rows to the requested ranges. It is careful not to treat explicit `scope: "mtp"` rows as base rows just because they happen to be `1-1`.

## Compute Start Handoff

### Sliding Horizon

`ComputationButton` reads `state.canvas.tpMode` and `state.canvas.slidingHorizon`. It adds a `parameters` object to the start request only when `tpMode === "MTP"`:

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

A Base TP request omits `parameters.global_params.slidingHorizon` entirely. The field is not placed in `configuration`.

The backend determines the effective TP mode from `diagram.tpMode`, then `diagram.canvas.tpMode`, and finally from whether TP rows exist. For MTP, Sliding Horizon precedence is:

1. Explicit request value at `req.body.parameters.global_params.slidingHorizon`.
2. Persisted `diagram.parameters.global_params.slidingHorizon`.
3. Persisted `diagram.canvas.slidingHorizon`.
4. Legacy `diagram.parameters.global_params.task_config.slidingHorizon`.
5. Default value `1`.

`attachSlidingHorizonGlobalParam(...)` runs after `translation(...)` and TP-spec metadata attachment. This ordering matters because translation rebuilds the runtime parameters object. The helper writes the normalized value to `parameters.global_params.slidingHorizon` for MTP and removes both the current field and any legacy `task_config.slidingHorizon` value for Base TP.

The diagram's generated `parameters` are saved before the computation is queued. `buildSolveRequest(...)` later forwards those diagram parameters into the final solver request. The relevant MTP excerpt is:

```json
{
  "parameters": {
    "global_params": {
      "slidingHorizon": 1
    }
  }
}
```

The existing top-level `configuration` object is built separately and remains unchanged by this field. Only parameter collection and transport are implemented here. No frontend component, compute route, or request builder performs sliding-horizon solver iterations.

### Economic Data

When `/api/compute/start` runs, `computeRoutes.ts` resolves the active TP spec version, then builds:

```ts
const costsPayload = {
  entities: cloneCostEntityFields(diagram.costEntities),
  mappings: Array.isArray(diagram.costMappings) ? diagram.costMappings : [],
  duration: buildCostDurationPayload(diagram, diagramId, tpNodeVersRows)
};
```

`buildCostDurationPayload` uses TP rows for the current network when valid rows exist. It falls back to `diagram.duration` and `diagram.durationUnit` as `1-1` when no valid TP rows exist.

`translation.ts` then writes solver-facing costs into `parameters.costs`:

- `entities` stay in the legacy single-period shape when there are no Multi-TP entities and no Multi-TP duration.
- Multi-TP entities are grouped with `timePeriodCosts`.
- `mappings` drop `scope`, `fromTp`, and `toTp`; the solver receives network/node/port/var/entity only.
- `duration` is emitted as an array with `From TP`, `To TP`, `Duration`, and `DurationUnit`.

The same compute-start pass writes TP spec version metadata into `parameters.global_params.task_config`. For MTP, `slidingHorizon` is a sibling of `task_config` under `parameters.global_params`; it is not nested inside `task_config`. The solver request therefore identifies the calculation type, applied TP spec table, and MTP horizon size. The callback storage path persists TP-spec metadata with computation results for traceability and possible result filtering.

## Testing

Relevant backend tests are present at:

- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/storeComputationResultUtils.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`

Focused backend validation commands, run from `src/`:

```bash
npx jest tests/backend/utils/economicCosts.test.ts tests/backend/utils/translationCosts.test.ts tests/backend/utils/storeComputationResultUtils.test.ts --runInBand --coverage=false
npm run build
```

Frontend lint, run from `src/src/frontend/`:

```bash
npm run lint -- --quiet
```

There is no dedicated automated Sliding Horizon test in the current repository. Use this manual verification matrix for changes to this path:

| Mode and state | Action | Expected UI or saved state | Expected compute request/result |
| --- | --- | --- | --- |
| New diagram | Open Global TP | Input displays `1`. | No request until Run is clicked. |
| Valid input | Enter `3` and click `Save Sliding Horizon` before building the grid. | Modal closes; Redux and saved `canvas.slidingHorizon` become `3`. | A later MTP run sends `parameters.global_params.slidingHorizon: 3`. |
| Invalid input | Clear the field or enter a value below `1`. | Inline error appears; save/apply controls remain disabled. | No compute request should be started from this invalid UI state. |
| Existing legacy diagram | Open a diagram with only `parameters.global_params.task_config.slidingHorizon`. | The legacy value is displayed and is moved to `canvas.slidingHorizon` on the next save. | MTP compute writes the current location and removes the legacy nested copy. |
| Base TP run | Start computation with `tpMode === "BASE"`. | Saved canvas may still retain the editable value. | Start request omits the field; backend removes it from generated solver parameters. |
| MTP run | Start computation with `tpMode === "MTP"`. | Existing Run behavior is unchanged. | Request and final solver payload contain `parameters.global_params.slidingHorizon`. |

There are also no focused automated tests for TP Spec version utilities, version/table routes, or frontend version actions. At minimum, manually verify scope isolation, calculation-type isolation, inactive Save, Apply, active-version deletion fallback, MTP copy excluding computed rows, and solve/result metadata. The detailed matrix is in [TP Spec Version Management](./tp-spec-version-management.md#testing-and-verification).

## Known Cautions

- Do not use generated runtime artifacts as the source of truth for TP or cost behavior.
- `parameters.costs` is regenerated by compute start; edit diagram-level fields or TP rows instead.
- `canvas.slidingHorizon` is editable saved state; `parameters.global_params.slidingHorizon` is rebuilt solver-facing state.
- Sliding Horizon belongs under `parameters.global_params`, never under solver `configuration` or current `task_config`.
- Base TP computation intentionally removes the solver-facing Sliding Horizon field even if the saved canvas still contains the user's value.
- Current numeric helpers truncate fractional values. Do not document or test the behavior as strict `Number.isInteger(...)` validation unless the implementation is changed.
- This feature transports a value only. Sliding-horizon solver behavior remains outside this frontend and API integration.
- Base TP is intentionally blocked once real Multi-TP ranges exist.
- `TimePeriodViewer` contains save code for TP rows, but the current UI disables TP structure editing with `TP_STRUCTURE_EDITING_ENABLED = false`.
- Legacy unscoped `1-1` cost rows are base rows for compatibility. New Multi-TP rows should use explicit `scope: "mtp"`.
- Do not treat a saved TP spec version as applied unless `isActive` is true for that exact scope and calculation type.
- Saving a non-active TP spec version is allowed, but it must not update node cache, active `tp_changes`, or solve request metadata until the user clicks `Apply`.
- TP Spec versions are sparse overlays, not immutable table snapshots. Unchanged cells continue to inherit node model-version defaults.
- Keep TP Spec actions read-only during computation. Callback persistence resolves the active context when results are handled.

## Related Pages

- [TP Spec Version Management](./tp-spec-version-management.md)
- [Run Config and Computation Start](./run-config-and-computation-start.md)
- [Backend Data Routes and Persistence](./backend-data-routes-and-persistence.md)
- [Compute, Solver Callback, and Results](./compute-solver-callback-and-results.md)
