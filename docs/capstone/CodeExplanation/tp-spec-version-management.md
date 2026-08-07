---
title: TP Spec Version Management Code Explanation
sidebar_position: 13
description: Explains TP spec version identity, sparse persistence, frontend operations, active-version resolution, compute handoff, callback writes, and compatibility behavior.
---

## Overview

TP Spec version management lets one diagram keep independent specification variants without duplicating every materialized TP Specs row. A version is isolated by three keys:

```text
diagram + TP scope + calculation type
```

The TP scope is either Base TP (`BASE`) or Multi-TP (`MTP`). The calculation type is `Simulation`, `Optimization`, `DataRec`, or `ParamUpdt`. Each combination has its own version list and its own active version.

The implementation is intentionally split across layers:

- `TPSpecsButton` owns version selection, editing, and user actions.
- `dataRoutes.ts` materializes rows, persists sparse changes, and exposes the version API.
- `tpSpecVersionUtils.ts` owns version identity, default creation, naming, normalization, and active-context lookup.
- MongoDB stores version metadata plus sparse Base or MTP changes.
- `computeRoutes.ts` resolves the active version before translation and records its identity in the solve parameters.
- `computationTaskHandler.ts` scopes computed TP changes to an active version table.
- PostgreSQL computation results retain the version code and logical table name used by the run.

This page is the detailed maintenance reference. For the surrounding duration, Global TP, Sliding Horizon, and Economic flows, see [Time Period and Economic Flow](./time-period-and-economic-flow.md).

## Source Files

- `src/src/frontend/src/components/header-bar/header-buttons/tp-specs-button.tsx`: shared Base/MTP grid, calculation-type tabs, version actions, sparse-change save call, active Base node-cache synchronization, and read-only behavior.
- `src/src/frontend/src/components/header-bar/index.tsx`: opens the shared panel from Model, Calc Type, and Multi-TP controls and combines the Base and MTP computation-disable rules.
- `src/src/frontend/src/components/modal/tabs/info-tab.tsx`: includes `calcType` when reading TP changes for a node modal.
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`: includes `calcType` in scoped TP-change reads.
- `src/src/frontend/src/components/modal/tabs/specs-tab.tsx`: includes `calcType` in scoped TP-change reads.
- `src/src/frontend/src/components/modal/useNodeDataPrefetch.ts`: prefetches TP changes for the current calculation type.
- `src/src/backend/utils/tpSpecVersionUtils.ts`: version types, normalization, logical naming, V1 creation, legacy claiming, list helpers, and active/selected context resolution.
- `src/src/backend/routes/dataRoutes.ts`: TP Spec version/table endpoints, row materialization, sparse save behavior, active Base overlay, and version-aware TP-change routes.
- `src/src/backend/routes/computeRoutes.ts`: resolves active version contexts for the full network, selects version-scoped input changes, and adds TP Spec metadata to generated parameters.
- `src/src/backend/services/computationTaskHandler.ts`: tags computed `TpChanges` with version identifiers, calculation type, and `changeSource: "COMPUTED"`.
- `src/src/backend/utils/storeComputationResultUtils.ts`: copies calculation-type and TP Spec metadata from solve parameters into PostgreSQL result rows.
- `src/src/backend/prisma/mongodb/schema.prisma`: `TpSpecVersionSet`, `TpSpecVersionTable`, `TpSpecBaseChange`, and version fields on `TpChanges`.
- `src/src/backend/prisma/postgres/schema.prisma`: traceability fields on `ComputationResults`.
- `src/src/backend/prisma/postgres/migrations/20260630000100_add_tp_spec_version_to_computation_results/migration.sql`: adds the result traceability columns.
- `src/tests/backend/utils/storeComputationResultUtils.test.ts`: current result-storage coverage; it exercises row persistence but does not yet assert TP Spec metadata.

## Responsibility Boundary

This feature owns:

- Version identity and display names.
- Independent active versions for each scope and calculation type.
- Copy, rename, apply, and delete behavior.
- Materialization of a full grid from model defaults, TP ranges, and sparse changes.
- Selection of the active version during diagram reads and computation.
- Run-result traceability to a version code and logical table.

It does not own:

- Base duration or Multi-TP range structure.
- Model-version selection for each TP range.
- Calculation-type definitions outside the supported four-value TP Spec set.
- Solver interpretation of `F`, `V`, `P`, `I`, or `CALC`.
- Run-history UI filtering by the stored version metadata.

## Version Identity

The supported axes are:

| Axis | Values | Effect |
| --- | --- | --- |
| Diagram | MongoDB diagram id | Versions never cross diagram boundaries. |
| Scope | `BASE`, `MTP` | Base and Multi-TP versions are separate families and use different sparse stores. |
| Calculation type | `Simulation`, `Optimization`, `DataRec`, `ParamUpdt` | Each calculation type has an independent version list and active selection. |
| Version number | `1`, `2`, `3`, ... | New uses one greater than the current maximum. Gaps below the maximum are not filled; deleting the highest version allows that number to be generated again later. |

The practical state space for one diagram is therefore:

| Scope | Simulation | Optimization | DataRec | ParamUpdt |
| --- | --- | --- | --- | --- |
| Base TP | Independent list and active version | Independent list and active version | Independent list and active version | Independent list and active version |
| Multi-TP | Independent list and active version | Independent list and active version | Independent list and active version | Independent list and active version |

Creating Simulation V2 does not create Optimization V2. Applying Base Simulation V2 does not activate MTP Simulation V2 or any other calculation type.

### Canonical Values and Aliases

`normalizeTpSpecScope(...)` accepts case-insensitive `BASE` and `MTP` strings. `normalizeTpSpecCalcType(...)` returns one of the four canonical calculation types and accepts aliases such as `dr`, `data_rec`, `pe`, `param_est`, and case/spacing/hyphen variations supported by the helper.

Invalid or missing calculation types usually fall back to the diagram's persisted `global_params.task_config.task_type`, then to `Simulation`. Callers should still send `calcType` explicitly because the intended version family is otherwise coupled to persisted diagram state.

## Logical Naming

`buildTpSpecLogicalName(...)` generates the logical table identifier. Version code and display name are separate:

- `code` is the stable generated code such as `V1` or `V2`.
- `displayName` is the user-editable label shown in the menu.
- `logicalName` identifies the scope/calculation-type/version combination.

Naming patterns:

| Scope | Calculation type | Pattern | V1 example |
| --- | --- | --- | --- |
| Base | Simulation | `TPSPECV{n}` | `TPSPECV1` |
| Base | Optimization | `TPSPECOPTV{n}` | `TPSPECOPTV1` |
| Base | DataRec | `TPSPECDRV{n}` | `TPSPECDRV1` |
| Base | ParamUpdt | `TPSPECPEV{n}` | `TPSPECPEV1` |
| Multi-TP | Simulation | `MTPSPECV{n}` | `MTPSPECV1` |
| Multi-TP | Optimization | `MTPSPECOPTV{n}` | `MTPSPECOPTV1` |
| Multi-TP | DataRec | `MTPSPECDRV{n}` | `MTPSPECDRV1` |
| Multi-TP | ParamUpdt | `MTPSPECPEV{n}` | `MTPSPECPEV1` |

Renaming a version changes only `displayName`. It does not change `code`, `versionNo`, `logicalName`, sparse-change ownership, or computation result identity.

These logical names are metadata identifiers. The implementation does not create separate physical MongoDB collections named `TPSPECV1`, `MTPSPECV2`, and so on; all version-table metadata lives in `tp_spec_version_tables`, while sparse values live in the Base or MTP change collections.

## MongoDB Data Model

### `TpSpecVersionSet`

One row represents one version in one diagram/scope/calculation-type family.

```ts
{
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
```

The schema enforces uniqueness on `(diagramId, scope, calcType, versionNo)`. `sourceVersionSetId` records the version selected when a new version was copied.

### `TpSpecVersionTable`

The table row provides the logical table identity used by sparse changes and solve metadata.

```ts
{
  diagramId,
  versionSetId,
  scope,
  calcType,
  logicalName,
  createdAt,
  updatedAt
}
```

The current UI creates one calculation-type table for each calculation-type-specific version set. The API response still exposes `tables` as an array, and the helpers tolerate legacy shapes, so consumers must choose the table matching the requested calculation type instead of assuming `tables[0]` is always correct.

### `TpSpecBaseChange`

Base versions use sparse JSON patches rather than duplicate node model versions:

```ts
{
  diagramId,
  versionSetId,
  versionTableId,
  nodeId,
  portName,
  portVarName,
  portLocation,
  portLocationKey,
  modelVarId,
  patch
}
```

The unique row identity is `(versionTableId, nodeId, portName, portVarName, portLocationKey)`. `portLocationKey` uses the normalized location string or `"na"`, preventing same-named variables on different port locations from sharing one patch.

The patch may contain `value`, `spec`, `lower_bound`, `upper_bound`, `unit`, and `type`. A field is stored only when it differs from the materialized baseline.

### Version-Scoped `TpChanges`

MTP versions reuse `TpChanges`. Version-aware rows add:

```ts
{
  tpSpecVersionSetId,
  tpSpecVersionTableId,
  calcType,
  changeSource // "USER" or "COMPUTED"
}
```

Manual and computed rows intentionally coexist in this collection. Save and copy paths restrict their queries to manual rows where required; callback persistence scopes computed rows to the active table and does not overwrite manual rows.

## Default V1 and Compatibility Adoption

Defaults are created lazily. Listing versions or resolving an active context calls `ensureDefaultTpSpecVersionSet(...)`.

For one diagram/scope/calculation-type family, the helper:

1. Claims eligible legacy version sets whose `calcType` is null.
2. Finds or creates version number `1` with code `V1`, display name `V1 Default`, `isDefault: true`, and `isActive: true`.
3. Makes V1 active if the family currently has no active version.
4. Ensures the matching logical table exists.
5. For MTP, attaches fully unversioned, non-computed `TpChanges` to the V1 set/table and marks them as `USER` changes.

Legacy claiming is migration behavior, not a normal version operation. A legacy set with a null calculation type is assigned to the first compatible calculation-type family that claims its version number. Stale tables for other calculation types, along with their sparse changes, are removed during that cleanup. Changes to this logic require migration-specific tests and production-data review.

The database does not have a unique constraint that guarantees exactly one active row per family. The Apply route enforces the invariant by clearing `isActive` for the family before activating the selected version. Direct database writes can violate it; active lookup then uses the first active row returned by the ordered version list.

## Row Materialization

The grid is derived data. Neither Base nor MTP stores a complete table.

### Baseline Row Selection

`buildBaseTpSpecRowsFromNodes(...)` reads MongoDB `Node.modelVersion.ports_var` rows and:

1. Selects the first `model_var_object` for each port variable.
2. Reads the field named by the requested calculation type, falling back to `modelVarObject.spec`.
3. Includes only effective specs in `F`, `V`, `P`, `I`, or `CALC`.
4. Hides non-exposed internal subnetwork ports by checking canvas `portsMapping`, mapped names, and port locations.
5. Emits a Base row with TP range `1-1` and `timePeriodId: "BASE_TP"`.

The row key combines:

```text
nodeId + timePeriodId + portLocation + portName + portVariableName
```

### Base Materialization

`materializeBaseTpSpecRows(...)` builds baseline rows from node model versions, then overlays `TpSpecBaseChange` patches for the selected version table. An overlay marks the row `isChanged: true`.

The active Base version is also overlaid when the regular node APIs return node data:

```http
GET /api/data/nodes/:nodeId
GET /api/data/nodes/diagram/:diagramId
```

This read overlay applies only while the diagram is in Base mode. It returns a cloned, derived `modelVersion`; the sparse patch remains the persisted source of the version difference.

### MTP Materialization

`materializeMtpTpSpecRows(...)` starts with the same model-version baseline, expands each node row across that node's `TpNodeVers` ranges, then overlays `TpChanges` belonging to the selected version table. MTP requires TP ranges to exist; otherwise the table is empty.

Rows indicate both `isChanged` and `isComputed`. Computed values may be displayed, but new version creation copies only non-computed source changes.

## Frontend State and Interaction

`TPSpecsButton` is one shared component. It derives the scope from `state.canvas.tpMode`, while its local state owns:

- `selectedCalcType`
- `versions`
- `selectedVersionId`
- `versionTable`
- materialized `rowData`
- loading and saving states
- the create/rename dialog state

The selected version and active version are different concepts:

- Selecting changes which rows the grid loads and edits.
- Applying changes which version the network and next solve use.
- The menu appends `(active)` to the active version.
- Apply is disabled when the selected version is already active.

The panel can open from three places:

- Model -> Specs for Base TP work.
- Calc Type buttons, which can switch calculation type and open the panel.
- Multi-TP -> TP Specs for MTP work.

Changing calculation-type tabs clears the selected version, table, rows, and empty-state message before loading that family's active version. The panel also resets when the global Redux calculation type changes or a new `openSignal` arrives.

During computation, `HeaderBar` combines `Model.Specs` and `MTP.TPSpecs` disable rules and passes the result as `readOnly`. Read-only mode still permits inspection and refresh, but disables version mutations and grid edits.

## Version Operations

### Select

Selecting a menu item loads its materialized table. It does not modify active state.

### Save

Save stops grid editing, sends all displayed rows to the selected `versionTable`, and lets the backend calculate sparse differences against an unmodified baseline.

- For Base, an empty patch deletes the existing `TpSpecBaseChange`; a non-empty patch is inserted or updated.
- For MTP, an empty patch deletes the matching manual `TpChanges` row for that table; a non-empty patch inserts or updates a manual version-scoped row.
- Saving an inactive version never activates it.
- Saving the active Base version triggers a calculation-type-only diagram update and synchronizes the refreshed Base rows into frontend node cache without marking those cache entries dirty.
- Saving an inactive Base version does not update node cache or current computation-result state.

### New

New creates the next version number using `max(versionNo) + 1`. The optional display name defaults to the generated code.

The selected version is the copy source:

- Base copies its sparse `TpSpecBaseChange` rows.
- MTP copies only non-computed source `TpChanges` and rewrites their set/table ids with `changeSource: "USER"`.
- The new version starts inactive.
- The frontend selects and loads the new version after creation.

Because only sparse changes are copied, unchanged cells continue to inherit the current materialized baseline. A later change to node model defaults can therefore affect unchanged cells in multiple versions.

### Rename

Rename requires a non-empty display name and updates only `TpSpecVersionSet.displayName`.

### Apply

Apply clears active state for the exact diagram/scope/calculation-type family, activates the selected version, persists the selected calculation type across the network through the diagram update route, reloads the table, and synchronizes Base rows into frontend node cache when the panel is in Base mode.

The backend Apply endpoint changes version metadata only. The additional calculation-type update and frontend cache synchronization are performed by `TPSpecsButton`. API clients that bypass the UI must account for that distinction.

### Delete

V1 is protected when either `isDefault` is true or `versionNo === 1`. Deleting another version removes its Base patches, MTP version-scoped changes, table metadata, and version-set metadata.

If the deleted version was active, the backend makes V1 active for the same scope and calculation type. The frontend reloads V1 and, for Base mode, synchronizes the fallback rows into node cache.

## API Contract

All paths include `/api/data` and require authentication.

| Method and path | Important input | Main response or side effect |
| --- | --- | --- |
| `GET /diagrams/:diagramId/tp-spec-versions` | Query: optional `scope`, `calcType` | Resolves scope/calc type, lazily ensures V1, and returns `activeVersionSetId` plus ordered versions. |
| `POST /diagrams/:diagramId/tp-spec-versions` | Body: optional `scope`, `calcType`, `sourceVersionSetId`, `displayName` | Creates an inactive version and copies the source version's sparse manual changes. |
| `PATCH /tp-spec-versions/:versionSetId` | Body: required non-empty `displayName` | Renames the version. |
| `POST /tp-spec-versions/:versionSetId/apply` | Body: optional `calcType` | Makes the version active only in its resolved family. |
| `DELETE /tp-spec-versions/:versionSetId` | Version-set id | Rejects V1, deletes version-owned data, and activates V1 if necessary. |
| `GET /diagrams/:diagramId/tp-spec-table` | Query: optional `scope`, `calcType`, `versionSetId` | Resolves the selected or active context and returns its materialized rows and table metadata. |
| `PUT /tp-spec-tables/:versionTableId/changes` | Body: non-empty `specs` array | Recomputes sparse differences and reports `upserted` and `deleted` counts. |

Scope defaults to the diagram's resolved TP mode. Calculation type defaults to the diagram's persisted task type and then Simulation. Explicit values are safer for non-UI API clients.

The version endpoints call `authorizeTpSpecDiagram(...)`, validate the MongoDB diagram id, and verify `Diagram.userId`. Invalid ids return through the shared validation path, missing diagrams return `404`, and ownership failures return `403`.

## Version-Aware Direct TP-Change Reads and Writes

The node modal still uses the general `/tpchanges` and `/tpchanges/all` routes for MTP editing. Those calls now include `calcType` so the backend can resolve the active MTP context.

Active MTP reads accept all of these compatibility shapes:

1. Rows with the active `tpSpecVersionTableId`.
2. Legacy rows with no table id but the active `tpSpecVersionSetId`.
3. Fully unversioned rows retained for backward compatibility.

Read results are ordered newest first and deduplicated by node, time period, port location, port, and variable, so the newest accepted row wins when compatibility shapes overlap. Manual POST/PUT writes are stamped with the active set id, table id, calculation type, and `changeSource: "USER"`. The frontend files listed in Source Files pass the current calculation type to prevent one tab from displaying another tab's MTP changes.

The dedicated TP Specs table endpoint should be used for version-grid saves. The older `/tp-specs/bulk-update` route mutates node model versions directly and is not the version-aware save contract.

## Compute-Start Handoff

`POST /api/compute/start` binds a run to the active version before translation.

1. Resolve diagram TP mode to `BASE` or `MTP`.
2. Normalize the run calculation type.
3. Resolve an active version context for the main diagram and each related network/subnetwork diagram.
4. For MTP, load changes from active table ids plus fully unversioned compatibility rows.
5. For Base, load active `TpSpecBaseChange` rows and convert their JSON patches into the TP-change-shaped input expected by translation.
6. Merge request-body `tpChanges` over persisted changes when the request supplies them.
7. Call `translation(...)` to create `parameters.tps_specs`.
8. Add the main diagram's active-version metadata to `parameters.global_params.task_config`.
9. Save the final parameters to the diagram before queue dispatch.

Metadata fields:

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

`tp_spec_version` is the stable code such as `V2`; `tp_spec_version_name` is the editable label. IDs are retained for exact internal identity, while `active_tp_spec_table` provides the readable logical name.

If an active context cannot be resolved for a related subnetwork diagram, compute start logs a warning and continues without that subnetwork context. Failure to resolve the main diagram context is fatal because the final request metadata requires it.

## Callback and Result Traceability

On successful callback, `handleComputationSuccess(...)` resolves a TP Spec context for each target diagram and tags computed `TpChanges` with:

```ts
{
  tpSpecVersionSetId,
  tpSpecVersionTableId,
  calcType,
  changeSource: "COMPUTED"
}
```

Computed update matching requires `isComputed: true` and includes the active table id. Writes preserve the reverse-translated `isComputed` value and default it to `true`; manual rows are not overwritten.

`storeComputationResults(...)` reads metadata from the first parameter source whose task configuration contains calculation-type or TP Spec fields. PostgreSQL `ComputationResults` stores:

| Column | Source |
| --- | --- |
| `calc_type` | `task_config.task_type` |
| `tp_spec_scope` | `task_config.tp_spec_scope` |
| `tp_spec_version` | `task_config.tp_spec_version` |
| `tp_spec_table` | `task_config.active_tp_spec_table` |

The result upsert updates these columns on conflict, so a stored run row remains traceable to the version metadata present in its parameter source.

The callback handler resolves the currently active set/table rather than reading the saved version ids back from task metadata. The UI makes TP Specs read-only during computation, which protects the normal flow. A direct API client should not apply another version while a task is running unless callback scoping is deliberately redesigned.

## Error and Fallback Behavior

- An unsaved diagram cannot load versions; the panel displays `Save the diagram first to load TP Specs.`
- A Base diagram with no eligible model variables returns an empty table message.
- An MTP diagram with no `TpNodeVers` rows returns `No Multi-TP spec rows found. Create time periods first.`
- Version/table load and save failures are logged in the browser and shown through panel messages or global alerts.
- Creating with an unknown `sourceVersionSetId` returns `404`.
- Renaming with an empty display name returns `400`.
- Saving without a non-empty `specs` array returns `400`.
- Applying, renaming, deleting, and table writes verify diagram ownership through their referenced version metadata.
- Missing active state falls back to V1; missing V1 causes it to be created.
- Legacy unversioned MTP rows remain readable so older diagrams do not silently lose TP overrides.

## Extension Points

### Add a Calculation Type

Update all of these together:

1. `TpSpecCalcType`, `TP_SPEC_CALC_TYPES`, aliases, and table suffixes in `tpSpecVersionUtils.ts`.
2. Frontend `CalcType` and `CALC_TYPES` definitions.
3. Source model-variable fields and import contracts.
4. Version API validation and logical-name expectations.
5. User guides, manual verification matrix, and tests.

### Add a Versioned Field

Update:

1. `TPSpec` and grid columns.
2. `TpSpecRow` and `getComparableTpSpecFields(...)`.
3. Base patch application to rows and model versions.
4. MTP `TpChanges` schema if the field cannot fit an existing column.
5. Translation and result metadata if the solver consumes or returns it.

### Change Version Copy Semantics

Decide explicitly whether the new version should copy sparse deltas or a fully materialized snapshot. The current sparse-copy design preserves inheritance from model defaults and excludes computed MTP rows. Changing it affects storage volume, behavior after model-version updates, and migration requirements.

### Add Run-History Filtering

The PostgreSQL fields already preserve calculation type, scope, version code, and table name. A new filter must update the result query route and Run Result UI while preserving old rows whose metadata columns are null.

## Testing and Verification

There are currently no focused automated tests for `tpSpecVersionUtils.ts`, the seven version/table endpoints, or `TPSpecsButton` version actions. `src/tests/backend/utils/storeComputationResultUtils.test.ts` also does not assert the four TP Spec result fields. Treat this as a test-coverage gap.

Recommended automated coverage:

- Logical-name and alias normalization for every scope/calculation-type pair.
- Lazy V1 creation and one-active-version behavior.
- Legacy version-set claiming and unversioned MTP row adoption.
- Base and MTP materialization with sparse overlays.
- New version copy excluding computed MTP rows.
- Save-to-inactive versus Apply behavior.
- Delete-active fallback to V1.
- Compute selection of active table ids across subnetworks.
- Callback computed-row scoping and manual-row protection.
- PostgreSQL result metadata extraction and upsert values.

Manual verification matrix:

| Scenario | Action | Expected result |
| --- | --- | --- |
| Lazy default | Open Base Simulation Specs on a saved diagram with no version rows. | `V1 Default` appears active and uses `TPSPECV1`. |
| Scope isolation | Create Base Simulation V2, switch to MTP Simulation. | MTP retains its own V1 list; Base V2 is absent. |
| Calculation isolation | Create Simulation V2, switch to Optimization. | Optimization retains its own V1 list and active state. |
| Inactive save | Select V2, edit, Save, but do not Apply. | Reopening V2 shows the edit; active nodes and next solve still use the prior active version. |
| Apply | Apply V2. | V2 shows `(active)`; refreshed nodes/table and the next solve use V2. |
| Base overlay | Apply a Base version and reload diagram nodes. | Node API responses contain the active Base patch for the persisted calculation type. |
| MTP copy | Create a new version after a run generated computed values. | Manual source edits are copied; computed callback rows are not copied. |
| Active delete | Delete an active non-default version. | Version-owned rows disappear and V1 becomes active for that family. |
| Result traceability | Run computation with a non-default version active. | Solve task config and PostgreSQL result rows contain the expected scope, version code, and logical table. |
| Legacy MTP | Open an older diagram containing unversioned manual `TpChanges`. | V1 is created and legacy manual rows remain visible under the adopted active context. |

Documentation verification from the repository root:

```bash
git diff --check -- docs/CodeExplanation docs/UserGuide
```

For source changes, also run the relevant backend tests and builds from `src/`, plus the frontend build from `src/src/frontend/`.

## Known Cautions

- Treat `selected` and `active` as different states. Only active versions affect ordinary node reads and compute start.
- Always carry diagram, scope, and calculation type through version operations. Version code alone is not globally unique.
- Do not rename logical tables when changing a display label.
- Do not persist Base version patches in `TpChanges`; do not persist MTP version rows in `TpSpecBaseChange`.
- Do not copy computed MTP rows when creating a user-editable version.
- Sparse versions inherit unchanged values from node model defaults; they are not immutable full snapshots.
- Base node overlay depends on the diagram's persisted calculation type. The UI Apply path updates it, but a raw Apply API call does not perform that separate diagram update.
- `ensureDefaultTpSpecVersionSet(...)` and version listing can write migration/default data. They are not read-only helpers.
- The active-version invariant is enforced in route logic, not by a database uniqueness constraint.
- Keep legacy unversioned-row fallbacks until a verified migration proves all supported diagrams have version ids.
- The callback uses the active context at callback time. Keep version actions read-only while computation is in progress.
- Do not use generated `solve_request.json` or callback JSON artifacts as the source of truth; inspect current TypeScript and persisted records.

## Related Pages

- [Time Period and Economic Flow](./time-period-and-economic-flow.md)
- [Backend Data Routes and Persistence](./backend-data-routes-and-persistence.md)
- [Run Config and Computation Start](./run-config-and-computation-start.md)
- [Compute, Solver Callback, and Results](./compute-solver-callback-and-results.md)
- [Translation and Reverse Translation](./translation-and-reverse-translation.md)
- [Header Bar](./header-bar.md)
- [Base Specs User Guide](../UserGuide/primary-menus/model/specs.mdx)
- [Multi-TP Specs User Guide](../UserGuide/primary-menus/multi-tp/tp-specs.mdx)
