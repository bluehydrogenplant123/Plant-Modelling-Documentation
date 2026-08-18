---
title: Optimization and DataRec Setup and Selected Solve Inputs
sidebar_position: 15
description: Explains how the active Optimization and DataRec dropdowns collect run selections, open shared editors, and produce authoritative solver inputs.
---

## Overview

The active **Optimization** and **DataRec** calculation types become dropdown menus in the Header Bar's **Calc Type** section. These menus do two related jobs:

1. They open existing editors for TP specifications, equation sets, instrument mappings, and plant measurements.
2. They let the user select which saved records belong to the next computation.

Editing and selecting are deliberately separate. Saving an Objective Function Set, Constraint Set, Instrument Set, or Plant Measurement makes it available for selection, but it does not automatically include that record in a run. The dropdown's **Apply** action updates an in-memory run selection, and `ComputationButton` sends only the selected identifiers when the matching calculation type is active.

The backend does not trust browser-supplied record contents. It resolves the identifiers against saved records, validates ownership and relationships, stores an authoritative snapshot on the queued computation task, and later emits the normalized selection under `parameters.solve_inputs`.

## Source Files

### Frontend orchestration and menus

- `src/src/frontend/src/components/header-bar/index.tsx`: renders the active calculation-type dropdown, owns Optimization/DataRec selections, opens shared editors through signals, clears diagram-specific selections, and passes the current options into `ComputationButton`.
- `src/src/frontend/src/components/header-bar/header-buttons/optimization-setup-menu.tsx`: Optimization dropdown, saved-set loading, Objective Function and Additional Constraint selection modals, and shared-editor entry points.
- `src/src/frontend/src/components/header-bar/header-buttons/optimization-setup-menu.css`: scrollable Optimization selection-list styling.
- `src/src/frontend/src/components/header-bar/header-buttons/datarec-setup-menu.tsx`: DataRec dropdown, Instrument Set, Plant Measurement, and Objective Function selection modals, plus shared-editor entry points.
- `src/src/frontend/src/components/header-bar/header-buttons/datarec-setup-menu.css`: DataRec selection context, list, option, and metadata styling.
- `src/src/frontend/src/components/header-bar/header-buttons/optimization-types.ts`: `OptimizationOptions` and selected set shapes.
- `src/src/frontend/src/components/header-bar/header-buttons/datarec-types.ts`: `DataRecOptions` shape.
- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`: converts selected objects to identifier-only request fields and adds only the active calculation type's options to `POST /api/compute/start`.

### Shared editors and persisted selection sources

- `src/src/frontend/src/components/header-bar/header-buttons/constraint-module.tsx`: shared `+Constr` editor that persists Objective Function and Constraint sets on `diagram.sets`.
- `src/src/frontend/src/components/header-bar/header-buttons/plant-measurements/plant-measurement-button.tsx`: shared editor for Instrument Sets, variable-to-instrument mappings, and Plant Measurements.
- `src/src/frontend/src/components/header-bar/header-buttons/tp-specs-button.tsx`: shared Specification Set / TP Specs panel opened through `tpSpecsOpenSignal`.
- `src/src/frontend/src/features/plantMeasurements/plantMeasurementApi.ts`: Instrument Set, mapping, measurement-import, and measurement API calls.
- `src/src/frontend/src/features/plantMeasurements/plantMeasurementSlice.ts`: owns the active Instrument Set and clears mapping/import drafts when that set changes.
- `src/src/frontend/src/features/plantMeasurements/plantMeasurementTypes.ts`: editor and API DTOs.

### Backend resolution and solver handoff

- `src/src/backend/routes/computeRoutes.ts`: receives selection identifiers, derives the saved calculation type, translates selections before queueing, and stores the snapshot in `configuration.selected_inputs`.
- `src/src/backend/services/solveInputTranslationService.ts`: validates selected set, Instrument Set, and measurement identifiers and builds the authoritative Optimization or DataRec snapshot.
- `src/src/backend/services/computationTaskService.ts`: persists the computation configuration, including the internal selected-input snapshot, on the MongoDB computation task.
- `src/src/backend/workers/computationDispatchWorker.ts`: reloads the queued task and diagram, then passes saved equations, collections, SoluAlgoLib rows, and selected inputs into the solve-request builder.
- `src/src/backend/services/solverEngineApiService.ts`: removes stale parameter copies, converts selected set equation objects to equation-id references, moves selected inputs into `parameters.solve_inputs`, and builds the final solver request.

## Purpose and Responsibility

This workflow owns the selection boundary between reusable saved editor data and one computation run. It decides which saved sets and measurements are selected, which active Instrument Set provides DataRec mappings, and which Optimization mode is sent.

It does not own the contents of those records:

- Equation Writing owns equation definitions.
- `+Constr` owns Objective Function and Constraint set membership.
- Plant Measurements owns Instrument Sets, mappings, and measurement rows.
- TP Specs owns calculation-type-specific variable specifications.
- The compute route and solver builder own validation, snapshotting, and final payload normalization.

## Rendered UI and Interaction Map

The specialized dropdown is rendered only for the active calculation type. Inactive types remain ordinary buttons so the existing confirmation flow can switch calculation type first.

| Calc Type state | Secondary control | Behavior |
| --- | --- | --- |
| Optimization inactive | Outline **Optimization** button | Opens **Switch Calc Type**. Confirming the switch updates Redux and opens TP Specs. |
| Optimization active | Primary **Optimization** dropdown | Opens Objective Function, Additional Constraints, or Specification Set setup. |
| DataRec inactive | Outline **DataRec** button | Opens **Switch Calc Type**. Confirming the switch updates Redux and opens TP Specs. |
| DataRec active | Primary **DataRec** dropdown | Opens Define Instruments, Plant Measurements, Objective Function, or Specification Set setup. |

### Optimization dropdown

| Menu item | Selection source | Result |
| --- | --- | --- |
| **Objective function** | Saved `diagram.sets` with type `Objective Function` | Multi-select modal; **Apply** replaces `optimizationOptions.objectiveFunctions`. |
| **Additional constraints** | Saved `diagram.sets` with type `Constraint` | Multi-select modal; **Apply** replaces `optimizationOptions.additionalConstraints`. |
| **Specification set** | Shared `TPSpecsButton` | Increments `tpSpecsOpenSignal` and opens TP Specs. |
| **Edit Objective Functions** | Shared `ConstraintModule` | Closes the selector and increments `constraintEditorOpenSignal`. |
| **Edit Constraints** | Shared `ConstraintModule` | Closes the selector and opens the same `+Constr` editor. |

The set selector fetches `GET /api/data/diagrams/:diagramId` whenever either selection modal opens. `normalizeOptimizationSets(...)` keeps only records with a non-empty id and a recognized set type. Draft checkbox state is isolated inside the modal until **Apply** is clicked; **Cancel** leaves the committed Header Bar selection unchanged.

### DataRec dropdown

| Menu item | Selection source | Result |
| --- | --- | --- |
| **Define Instruments** | `GET /api/data/diagrams/:diagramId/instrument-sets` | Single-select radio modal; **Apply** sets the active Instrument Set. |
| **Plant Measurements** | `GET /api/data/instrument-sets/:instrumentSetId/measurements` | Multi-select modal for measurements saved under the active Instrument Set. |
| **Objective function** | Saved `diagram.sets` with type `Objective Function` | Multi-select modal; **Apply** replaces `dataRecObjectiveFunctions`. |
| **Specification set** | Shared `TPSpecsButton` | Increments `tpSpecsOpenSignal` and opens TP Specs. |
| **Edit Instruments** | Shared `PlantMeasurementButton` | Applies the selected Instrument Set, closes the selector, and opens the `mappings` tab. |
| **Edit Measurements** | Shared `PlantMeasurementButton` | Closes the selector and opens the `measurements` tab. |
| **Edit Objective Functions** | Shared `ConstraintModule` | Closes the selector and opens `+Constr`. |

Plant Measurements cannot be selected until an Instrument Set is active. Measurement options without a persisted non-empty `id` are excluded because they cannot be resolved safely at compute start.

### Optimization mode

The **Optimization > Optimization Options** dropdown entry controls a separate part of `OptimizationOptions`:

- `deterministic` stores no Wasserstein radius.
- `dro` requires a finite `wassersteinRadius` greater than or equal to zero and a `wassersteinNorm` of `L1`, `L2`, or `L∞`.
- The DRO defaults are radius `1.0` and norm `L1`.
- Closing or cancelling restores the last committed mode, radius, and norm.
- Saving a mode change preserves the currently selected Objective Function and Constraint sets.

## Frontend State and Component Contracts

### Header-owned committed state

| State | Type | Meaning |
| --- | --- | --- |
| `optimizationOptions` | `OptimizationOptions` | Committed mode, Objective Function Sets, and Additional Constraint Sets for the next Optimization run. |
| `dataRecObjectiveFunctions` | `OptimizationObjectiveFunctionSet[]` | Committed Objective Function Sets for the next DataRec run. |
| `dataRecMeasurements` | `PlantMeasurementDto[]` | Committed saved measurements for the next DataRec run. |
| `activeInstrumentSet` | Redux `InstrumentSetDto \| null` | Current DataRec Instrument Set and source of all mapping records. |
| `plantMeasurementOpenSignal` | `number` | Opens the shared Plant Measurements modal from the DataRec dropdown. |
| `plantMeasurementInitialTab` | `'mappings' \| 'measurements'` | Chooses which shared editor tab opens. |
| `constraintEditorOpenSignal` | `number` | Opens the shared `+Constr` modal without its Model-section button. |
| `tpSpecsOpenSignal` | `number` | Opens the shared TP Specs panel from either dropdown. |

### Menu-local draft state

The selection menus keep temporary ids rather than mutating committed Header state immediately:

- Optimization uses `draftSelectedIds` plus `selectionPanel`.
- DataRec uses `draftInstrumentSetId`, `draftMeasurementIds`, and `draftObjectiveFunctionIds`.
- Each panel also owns loading and error state for its current API request.
- **Apply** resolves draft ids against the freshly loaded option objects before invoking the parent callback.

This draft/committed split makes modal cancellation non-destructive.

### Reset rules

- When `diagramId` changes, Header clears both Optimization set lists, all DataRec selections, and the active Instrument Set.
- When the active Instrument Set id changes, Header clears the selected DataRec measurements.
- When the Plant Measurements editor reports a successful measurement save, Header clears the selected DataRec measurements so the user must reselect from current persisted rows.
- Changing an Instrument Set through Redux also clears mapping and imported-measurement editor drafts in `plantMeasurementSlice`.

These selections are run-setup state, not saved diagram configuration. A Header Bar remount or network change resets them.

## Selection Boundary at Compute Start

`ComputationButton` receives full selected objects because the menus need labels and metadata. Immediately before `POST /api/compute/start`, it reduces them to ids.

Optimization request fields:

```json
{
  "optimizationOptions": {
    "mode": "dro",
    "wassersteinRadius": 0.25,
    "wassersteinNorm": "L2",
    "objectiveFunctionSetIds": ["objective-set-1"],
    "additionalConstraintSetIds": ["constraint-set-1"]
  }
}
```

DataRec request fields:

```json
{
  "dataRecOptions": {
    "instrumentSetId": "64b000000000000000000003",
    "measurementIds": ["64b000000000000000000005"],
    "objectiveFunctionSetIds": ["objective-set-1"]
  }
}
```

Only the active type is added:

- `calcType === 'Optimization'` adds `optimizationOptions` and omits `dataRecOptions`.
- `calcType === 'DataRec'` adds `dataRecOptions` and omits `optimizationOptions`.
- Simulation and ParamUpdt omit both fields.

The route derives its calculation type from the saved `diagram.parameters.global_params.task_config.task_type`. The normal computation workflow prompts users to save first; direct API callers must also keep the saved task type consistent with the option block they send.

## Backend Resolution and Snapshot Rules

`translateSolveInputSelection(...)` is the trust boundary. Explicit id arrays take precedence over older object-array fields, duplicate ids are removed, and display names are never used as persistent linkage.

### Optimization resolution

1. Normalize saved `diagram.sets` into id, name, type, and equation arrays.
2. Resolve `objectiveFunctionSetIds` only against `Objective Function` sets.
3. Resolve `additionalConstraintSetIds` only against `Constraint` sets.
4. Reject a missing id or a set with the wrong type.
5. Default the mode to `deterministic` unless it is exactly `dro`.
6. Reject DRO when the radius is missing, non-numeric, or negative.
7. Copy the saved set names and equation objects into the queued snapshot.

### DataRec resolution

1. Resolve selected Objective Function Set ids from saved `diagram.sets`.
2. If no Instrument Set is selected, reject any non-empty measurement selection; otherwise return an empty instrument/measurement selection.
3. Require the Instrument Set and measurement ids to be MongoDB ObjectId-shaped strings.
4. Require the Instrument Set to belong to both the authenticated user and the current diagram.
5. Load every saved variable-to-instrument mapping in the selected Instrument Set. These become `instruments` even when no measurement is selected for a mapping.
6. Load only the selected measurement ids from that Instrument Set.
7. Reject missing measurements, measurements with saved `rowErrors`, invalid numeric plant values, or measurements whose mapping no longer exists.
8. Join each measurement to authoritative mapping weight, accuracy, bounds, and model-path data.

The translated snapshot is attached to `configuration.selected_inputs` before the task is inserted. This freezes selected set names/membership and expanded DataRec values for the queued run. One boundary remains separate: the worker reloads the top-level Equation Writing catalog from `diagram.equations` at dispatch time.

## Solver-Facing Contract

At dispatch, `buildSolveRequest(...)` removes the internal `selected_inputs` field from solver configuration and writes the normalized form to `parameters.solve_inputs`.

For selected equation sets, the queued snapshot temporarily contains full persisted equation objects. The final solver payload reduces each nested set's `equations` array to equation ids. The full normalized Equation Writing catalog remains separately available in top-level `parameters.equations`.

Optimization selection example:

```json
{
  "parameters": {
    "equations": [
      {
        "id": "equation-objective-1",
        "name": "Minimize fuel",
        "belong_to": "Main Network",
        "equation_type": "Objective Function",
        "eq_type": "Minimize",
        "expression": "Main Network.Heater.OUT.Duty[t]",
        "tokens": []
      },
      {
        "id": "equation-constraint-1",
        "name": "Duty cap",
        "belong_to": "Main Network",
        "equation_type": "Constraint",
        "eq_type": "Inequality",
        "expression": "Main Network.Heater.OUT.Duty[t] <= 100",
        "tokens": []
      }
    ],
    "solve_inputs": {
      "calculation_type": "Optimization",
      "optimization": {
        "mode": "deterministic",
        "wasserstein_radius": null,
        "wasserstein_norm": null,
        "objective_functions": [
          {
            "set_id": "objective-set-1",
            "name": "Fuel objective",
            "equations": ["equation-objective-1"]
          }
        ],
        "additional_constraints": [
          {
            "set_id": "constraint-set-1",
            "name": "Operating limits",
            "equations": ["equation-constraint-1"]
          }
        ]
      }
    }
  }
}
```

DataRec selection example:

```json
{
  "parameters": {
    "solve_inputs": {
      "calculation_type": "DataRec",
      "data_reconciliation": {
        "instrument_set": {
          "id": "64b000000000000000000003",
          "network": "Main Network",
          "instr_set": "VARINSTRMAP"
        },
        "instruments": [
          {
            "id": "64b000000000000000000004",
            "instrument_name": "TI-101",
            "units": "C",
            "weight": 2,
            "accuracy": {
              "absolute_accuracy": 0.5,
              "percent_accuracy": null
            },
            "bounds": {
              "lower_bound": 0,
              "upper_bound": 500
            },
            "model_path": {
              "network": "Main Network",
              "subnetwork": "none",
              "sub_subnetwork": "none",
              "node_id": "heater-node-1",
              "node_name": "Heater",
              "port": "OUT",
              "variable": "Temperature"
            }
          }
        ],
        "measurements": [
          {
            "id": "64b000000000000000000005",
            "mapping_id": "64b000000000000000000004",
            "instrument_name": "TI-101",
            "plant_value": 325.5,
            "units": "C",
            "date": "2026-07-20",
            "time": "10:30:00",
            "sample_number": "3",
            "measurement_weight": 1.5,
            "mapping_weight": 2,
            "accuracy": {
              "absolute_accuracy": 0.5,
              "percent_accuracy": null
            },
            "bounds": {
              "lower_bound": 0,
              "upper_bound": 500
            },
            "model_path": {
              "network": "Main Network",
              "subnetwork": "none",
              "sub_subnetwork": "none",
              "node_id": "heater-node-1",
              "node_name": "Heater",
              "port": "OUT",
              "variable": "Temperature"
            }
          }
        ],
        "objective_functions": []
      }
    }
  }
}
```

All normal translated model, TP, stream, material, and economic parameters remain alongside these fields.

### Stale parameter cleanup versus the equation catalog

`removeIndependentSolveInputParameters(...)` removes legacy selection-like fields already embedded in `diagram.parameters`, including old equation, set, constraint, instrument, measurement, Optimization, and DataRec keys. It then attaches the current `solve_inputs` snapshot.

This cleanup does not eliminate the authoritative Equation Writing catalog. The worker separately passes `diagram.equations` to `buildSolveRequest(...)`, which normalizes that saved catalog and recreates top-level `parameters.equations`. The two fields have different responsibilities:

- `parameters.equations` contains normalized saved equation definitions.
- `parameters.solve_inputs.*.objective_functions[].equations` and `additional_constraints[].equations` contain ids that select equations within named sets for this run.

Do not remove either path without updating the solver contract and focused tests.

## End-to-End Data Flow

1. The user saves reusable definitions in TP Specs, `+Constr`, or Plant Measurements.
2. The user opens **Calc Type** and activates Optimization or DataRec through the existing switch-confirmation flow.
3. The active type renders its dropdown instead of a plain button.
4. Opening a selection item reloads the current saved options from the backend.
5. **Apply** commits selected objects to Header-owned run state; editor entry buttons open shared modules through incrementing signals.
6. `ComputationButton` reduces the committed objects to ids and sends only the active type's option block.
7. `computeRoutes.ts` resolves ids against saved diagram and measurement data and rejects stale or unauthorized selections.
8. The route stores the authoritative snapshot in the queued task's `configuration.selected_inputs`.
9. The Bull worker reloads the task and diagram.
10. `buildSolveRequest(...)` removes stale parameter copies, normalizes selected set equation references to ids, moves the snapshot to `parameters.solve_inputs`, and adds the independent normalized equation catalog.
11. The solver receives the final request through `${BASE_SOLVER_ENGINE_URL}/solve/`.

## Side Effects

- Opening a set selector fetches the full diagram record.
- Opening Define Instruments or Plant Measurements reads persisted Instrument Set or measurement data.
- **Apply** changes run-selection state only; it does not persist the selected combination to the diagram.
- Editor entry buttons can open `+Constr`, Plant Measurements, or TP Specs, whose own save actions persist data.
- Changing the active Instrument Set clears measurement selection and Plant Measurement draft rows.
- Starting computation writes a selected-input snapshot to the MongoDB computation task.
- Solver dispatch strips that internal snapshot from `configuration` and exposes its normalized copy under `parameters.solve_inputs`.

## Error Handling and Edge Cases

- An unsaved network cannot load diagram sets or Instrument Sets; the selectors show a save-first error.
- A loading or request error disables **Apply** in the affected selection modal.
- Empty saved lists show a non-destructive message and an editor entry point.
- Plant Measurements shows a select-Instrument-Set message until an Instrument Set is active.
- Switching Instrument Sets invalidates selected measurements because measurement ids are scoped to one set.
- A selected set deleted or changed to the wrong type before compute start causes a `400` selection error.
- A stale, unauthorized, or cross-diagram Instrument Set causes a `400` selection error.
- Missing measurements, measurements with validation errors, invalid values, and missing mapping joins are rejected before queueing.
- DataRec may run with no Instrument Set only when no measurements are selected; its solver snapshot then contains `instrument_set: null`, empty `instruments`, and empty `measurements`.
- The editor-level Plant Measurement `include` field does not decide run inclusion. Only dropdown-selected measurement ids do.
- The UI validates DRO radius, and the backend repeats that validation so direct API calls cannot bypass it.

## Extension Points

- Add a new Optimization selection category by updating `OptimizationOptions`, `OptimizationSetupMenu`, the identifier-only frontend builder, `translateOptimizationSelection(...)`, `normalizeSelectedSolveInputs(...)`, and backend tests together.
- Add a new DataRec selection category by updating `DataRecOptions`, `DataRecSetupMenu`, `buildDataRecSelectionRequest(...)`, the DataRec translator, solver normalization, and tests together.
- Persist run selections across remounts only after defining their ownership and invalidation model; current selections intentionally live in Header/Redux runtime state.
- Change shared-editor navigation through the signal props instead of creating duplicate editor instances in either dropdown.
- Change set or measurement id formats only with frontend normalization, backend validation, MongoDB schema, and stale-id errors in mind.
- If the solver needs full equation objects nested inside selected sets, change `normalizeSelectedEquationSets(...)` and the solver contract deliberately; current nested references are id-only.

## Testing and Verification

Focused backend tests:

- `src/tests/backend/services/solveInputTranslationService.test.ts`
- `src/tests/backend/services/solverEngineApiService.test.ts`
- `src/tests/backend/workers/computationDispatchWorker.test.ts`

Run from `src/`:

```bash
npx jest tests/backend/services/solveInputTranslationService.test.ts tests/backend/services/solverEngineApiService.test.ts tests/backend/workers/computationDispatchWorker.test.ts --runInBand --coverage=false
```

Frontend build check from `src/src/frontend/`:

```bash
npm run build
```

Manual verification matrix:

| Scenario | Expected result |
| --- | --- |
| Switch from Simulation to Optimization | Confirmation appears; after confirm, TP Specs opens and Optimization renders as a dropdown. |
| Select Objective Function and Constraint sets | Reopening each selector shows the committed checks; Cancel does not change them. |
| Open either Optimization edit action | The selection modal closes and the shared `+Constr` editor opens. |
| Switch from Optimization to DataRec | DataRec renders as a dropdown; Optimization returns to a plain button. |
| Open Plant Measurements without an Instrument Set | Selector asks for an Instrument Set and does not enable Apply. |
| Change Instrument Set | Existing selected measurements clear. |
| Save Plant Measurements through the editor | Existing dropdown measurement selection clears and must be reapplied. |
| Start an Optimization run | Request includes `optimizationOptions`, omits `dataRecOptions`, and solver payload contains Optimization `solve_inputs`. |
| Start a DataRec run | Request includes `dataRecOptions`, omits `optimizationOptions`, and only selected measurement ids are expanded. |
| Delete a selected saved record before starting | Backend rejects the stale selection instead of silently substituting a record. |
| Select DRO with a blank or negative radius | UI blocks Save; direct invalid requests are also rejected by the backend. |

## Known Cautions

- Dropdown **Apply** is not a persistence action. It commits the next-run selection only.
- Selection objects are kept for display, but only ids cross the frontend/backend trust boundary.
- Set and equation display names are not unique. Keep id-based linkage throughout the workflow.
- The active Instrument Set is Redux state, while selected measurements and DataRec Objective Functions are Header-local state. Preserve the reset effects when moving ownership.
- Backend selection uses the saved calculation type from `diagram.parameters`; direct clients must not assume that merely sending `optimizationOptions` or `dataRecOptions` changes the calculation type.
- All mappings from a selected Instrument Set become DataRec `instruments`; only the measurement list is individually selected.
- `configuration.selected_inputs` is an internal queued-task snapshot and must not be sent as a solver configuration field.
- Top-level `parameters.equations` and nested equation-id selections serve different purposes. The stale-parameter cleanup happens before the authoritative equation catalog is added back.
- The selected set snapshot freezes equation membership ids, but the worker reloads the full `diagram.equations` definitions at dispatch. Editing or deleting an equation while a task is waiting can therefore change or break the catalog referenced by that queued selection.
- Generated `src/src/backend/services/solve_request.json` is runtime evidence only and may be stale.

## Related Pages

- [Header Bar Code Explanation](./header-bar.md)
- [Constraint Module Code Explanation](./constraint-module.md)
- [Equation Writing Module Code Explanation](./equation-writing-module.md)
- [Run Config and Computation Start Code Explanation](./run-config-and-computation-start.md)
- [Compute, Solver Callback, and Results Code Explanation](./compute-solver-callback-and-results.md)
- [TP Spec Version Management Code Explanation](./tp-spec-version-management.md)
