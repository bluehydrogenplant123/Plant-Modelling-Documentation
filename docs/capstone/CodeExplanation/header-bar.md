---
title: Header Bar Code Explanation
sidebar_position: 11
description: Explains how the current HyProNet canvas header coordinates navigation, calculation-type setup, run selections, shared editors, save metadata, display filtering, and computation-aware UI guards.
---

## Overview

The Header Bar is the fixed control surface above the React Flow canvas. It renders a primary toolbar, a contextual secondary row, save and autosave status, display filtering, navigation controls, and modals that are opened by header actions.

The main entry point is `src/src/frontend/src/components/header-bar/index.tsx`. The header receives canvas-shell callbacks and status values from `App.tsx`, reads Redux state for domain, calc type, Plant Measurements, save status, and computation guards, and delegates most feature-specific behavior to child button components. It also owns the in-memory Optimization and DataRec selections that are passed into the next computation.

## Source Files

- `src/src/frontend/src/components/header-bar/index.tsx`: header layout, active section state, secondary row branching, calc type confirmation, Optimization/DataRec run selections, shared-editor signals, run config modal wiring, User Tables wiring, and save/autosave text.
- `src/src/frontend/src/components/header-bar/header-bar.css`: toolbar layout, button styling, responsive scaling, save status text, and header-specific modal/table sizing.
- `src/src/frontend/src/components/header-bar/header-buttons/optimization-setup-menu.tsx`: active Optimization dropdown and Objective Function / Additional Constraint selectors.
- `src/src/frontend/src/components/header-bar/header-buttons/datarec-setup-menu.tsx`: active DataRec dropdown and Instrument Set / Plant Measurement / Objective Function selectors.
- `src/src/frontend/src/components/header-bar/header-buttons/optimization-types.ts`: Header-owned Optimization mode and selected-set contract.
- `src/src/frontend/src/components/header-bar/header-buttons/datarec-types.ts`: Header-to-computation DataRec selection contract.
- `src/src/frontend/src/components/header-bar/header-buttons/plant-measurements/plant-measurement-button.tsx`: shared editor opened from Analysis or from the DataRec dropdown through an open signal.
- `src/src/frontend/src/components/header-bar/header-buttons/constraint-module.tsx`: shared `+Constr` editor opened from Model or from setup dropdowns through an open signal.
- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`: receives Header-owned Optimization/DataRec options and sends the active type's identifier-only selection.
- `src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu.tsx`: shared base/Multi-TP **User Tables** dropdown and Material/Economic action routing.
- `src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu-options.ts`: labels, ordering, and availability rules for User Tables entries.
- `src/src/frontend/src/components/material-editor/index.tsx`: parent-rendered Material Editor opened by the User Tables callback.
- `src/src/frontend/src/components/header-bar/header-buttons/display-button.tsx`: modal control for `all`, `normal`, and `subnetwork` node display filters.
- `src/src/frontend/src/utils/displayNodeFilter.ts`: display filter labels and node classification helper used by `App.tsx`.
- `src/src/frontend/src/utils/useComputingDisableRule.ts`: hook that maps computation state and diagram type to disabled/read-only decisions.
- `src/src/frontend/src/configs/computingDisableConfig.ts`: rule map for canvas, model, materials, costs, save, set-run, calc-type, MTP, system, and help controls.
- `src/src/frontend/src/features/canvas/canvasSlice.ts`: source of `isComputationProcessing`, diagram type, computation status, and other canvas state used by disable rules.
- `src/src/frontend/src/features/domain/domainSlice.ts`: source of `domain.data.runConfigs` used by the Set Run dropdowns.
- `src/src/frontend/src/features/saved/savedSlice.ts`: source of `isSaving`, `lastSavedAt`, and `lastSaveDurationMs` shown in the metadata area.
- `src/src/frontend/src/features/calcType/calcTypeSlice.ts`: source of `CALC_TYPES`, active `calcType`, and `updateCalcType(...)`.
- `src/src/frontend/src/features/plantMeasurements/plantMeasurementSlice.ts`: source of the active DataRec Instrument Set and editor drafts.
- `src/src/frontend/src/App.tsx`: parent component that renders `HeaderBar` and owns material editor, save confirm, autosave counter, and display filter state.

Important delegated button components imported by `index.tsx` include:

- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/run-result-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/canvas-name-edit.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/back-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/back-to-parent-network.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/cost-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/base-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/tp-specs-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/time-period-viewer.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/save-as-copy.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/save-as-subnetwork.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/import-subnetwork.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/verify-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/metabase-button.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/create-diagram-modal.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/open-network-modal.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/import-diagram-modal.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/export-diagram-modal.tsx`
- `src/src/frontend/src/utils/verificationLifecycle.ts`: derives the next desired verification state and validates the canonical API response.
- `src/src/frontend/src/utils/diagramTransfer.ts`: shared Full Data export and current-format import contract used by Header and Dashboard.
- `src/src/frontend/src/components/header-bar/run-buttons/run-config-modal.tsx`

## Purpose and Responsibility

`HeaderBar` owns navigation between header sections, the visible grouping of top-row and second-row controls, and high-level UI state such as the active section, calc type confirmation modal, current Optimization/DataRec run selections, shared-editor open signals, run config modal, Multi-TP availability state, and save status text.

It does not own the persisted contents of Objective Function Sets, Constraint Sets, Instrument Sets, Plant Measurements, or TP Specs. Those records are owned by shared child editors and backend routes; Header only chooses which saved records belong to the next run. It also delegates saving, computation execution, diagram creation/open/import/export, cost editing, material editing, result history, and React Flow visibility changes.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `setMaterialEditor` | Parent `App.tsx` | Opens the top-level `MaterialEditor` modal rendered by the canvas shell. |
| `setSaveConfirm` | Parent `App.tsx` | Opens the save-confirm modal before leaving through the back button. |
| `theme` | Parent `App.tsx` | Passes the current light/dark theme to theme-aware delegated controls. |
| `remainingAutoSaveNodes` | Parent `App.tsx` autosave tracker | Shows how many unique node edits remain before autosave. |
| `autoSaveNodeThreshold` | Parent `App.tsx` constant | Shows the autosave threshold denominator. |
| `displayNodeFilter` | Parent `App.tsx` local state | Sets the selected Display modal value. |
| `setDisplayNodeFilter` | Parent `App.tsx` local setter | Emits Display modal changes back to the canvas shell. |
| `state.canvas.verified` | Redux canvas slice | Guards Multi-TP Economic entries in User Tables until the diagram is verified. |
| `state.domain.data.runConfigs` | Redux domain slice | Populates Solver dropdown items; the Algorithm dropdown delegates to SoluAlgoLib. |
| `state.calcType.type` | Redux calc type slice | Highlights the active calculation type and builds switch confirmation text. |
| `state.plantMeasurements.activeInstrumentSet` | Redux Plant Measurements slice | Supplies the active DataRec Instrument Set and scopes selectable measurements. |
| `state.saved.isSaving` | Redux saved slice | Shows `Saving…` and disables save operations through the rule hook. |
| `state.saved.lastSavedAt` | Redux saved slice | Drives the compact saved-age label and detailed tooltip timestamp. |
| `state.saved.lastSaveDurationMs` | Redux saved slice | Shows "Last save took ..." when available. |
| `state.canvas.isComputationProcessing` | Redux canvas slice through `useComputingDisableRule` | Disables or makes controls read-only according to `ComputingDisableMap`. |
| `state.canvas.type` and `state.canvas.nodes` | Redux canvas slice through `useComputingDisableRule` | Keeps calc type buttons available for empty subnetwork diagrams. |

| Output | Destination | Notes |
| --- | --- | --- |
| `activeSection` changes | Header local state | Selects which secondary button row branch is rendered. |
| `setMaterialEditor(true)` | Parent `App.tsx` | Opens the material editor modal; read-only enforcement is applied by the parent modal. |
| `setSaveConfirm(true)` | Parent `App.tsx` via `BackButton` | Opens save confirmation before navigation. |
| `updateCalcType(pendingCalcType)` | Redux calc type slice | Applies confirmed calc type switch. |
| `tpSpecsOpenSignal` increment | `TPSpecsButton` prop | Opens TP Specs after a Simulation/ParamUpdt same-type click, confirmed calc type switch, setup-menu Specification set action, or Multi-TP TP Specs action. |
| `constraintEditorOpenSignal` increment | `ConstraintModule` prop | Opens `+Constr` from Optimization/DataRec setup without duplicating the editor. |
| `plantMeasurementOpenSignal` and `plantMeasurementInitialTab` | `PlantMeasurementButton` props | Open the shared editor on the mappings or measurements tab. |
| `optimizationOptions` | `ComputationButton` prop | Supplies the next Optimization run's mode and selected sets. |
| `dataRecOptions` | `ComputationButton` prop | Supplies the active Instrument Set plus selected measurements and Objective Function Sets. |
| `setDisplayNodeFilter(...)` | Parent `App.tsx` | Causes canvas nodes and attached edges to hide/show. |
| `showRunConfigModal` and `selectedRunConfigType` | Header local state | Controls the selected Solver's `RunConfigModal` when Set Run is active. |

## Core State and Data Structures

- `activeSection`: local string state, default `Model`. Controls secondary row conditional rendering.
- `mainSections`: local array with `Model`, `Calc Type`, `Analysis`, `Set Run`, `Multi-TP`, `TP Analysis`, `System`, and `Help`. **User Tables**, computation, results, display, save, and navigation controls render separately from this section array.
- `showCalcTypeConfirm`: local boolean that renders the calc type confirmation modal.
- `pendingCalcType`: local calc type waiting for confirmation.
- `tpSpecsOpenSignal`: local counter passed to `TPSpecsButton`; incrementing it opens TP Specs.
- `optimizationOptions`: committed deterministic/DRO mode plus selected Objective Function and Constraint sets for the next Optimization run.
- `optimizationMode`, `wassersteinRadiusInput`, and `optimizationOptionsError`: draft state and validation for **Set Run > Optimization Options**.
- `dataRecObjectiveFunctions` and `dataRecMeasurements`: committed DataRec selections for the next run.
- `activeInstrumentSet`: Redux-owned DataRec Instrument Set; changing it invalidates the Header-owned measurement selection.
- `plantMeasurementOpenSignal` and `plantMeasurementInitialTab`: open the shared Plant Measurements editor on the requested tab.
- `constraintEditorOpenSignal`: opens the shared `+Constr` editor from a setup dropdown.
- `showRunConfigModal` and `selectedRunConfigType`: local Set Run modal state.
- `nowMs`: local clock updated once per second while `lastSavedAt` exists.
- `lastSavedText`: memoized display string derived from `lastSavedAt` and `nowMs`.
- `saveDurationText`: memoized display string derived from `lastSaveDurationMs`.
- `rule*` values: booleans returned by `useComputingDisableRule(...)` for named control groups.

## Main Functions and Components

- `HeaderBar(...)`: renders the top toolbar, secondary row, calculation-type setup controls, shared editor instances, and local modals.
- `openTpSpecsPanel()`: increments `tpSpecsOpenSignal`.
- `handleCalcTypeClick(nextCalcType)`: returns early when calc type buttons are guarded, opens TP Specs directly for the current plain active button, or opens the confirmation modal for a different type. Active Optimization/DataRec controls are dropdowns and do not call this handler.
- `handleConfirmCalcTypeSwitch()`: dispatches `updateCalcType(pendingCalcType)`, opens TP Specs, clears pending state, and closes the modal.
- `validateOptimizationOptions()`: commits deterministic mode directly or validates a non-negative finite Wasserstein radius for DRO.
- `handleObjectiveFunctionsChange(...)` and `handleAdditionalConstraintsChange(...)`: replace committed Optimization selections.
- `handleDataRecInstrumentSetChange(...)`: updates the active Instrument Set and clears measurements when the id changes.
- `openPlantMeasurementEditor(tab)`: chooses a shared editor tab and increments its open signal.
- `openConstraintEditor()`: increments the shared `+Constr` open signal.
- Diagram-change effects: clear all calculation-type run selections and the active Instrument Set so ids do not leak across networks.
- `handleOpenRunConfig(type)`: opens `RunConfigModal` and stores the chosen solver key.
- `handleCloseRunConfig()`: closes `RunConfigModal` and clears the selected key.
- Save clock effect: starts a one-second interval only when `lastSavedAt` is present and clears it on cleanup.
- `DisplayButton`: renders the Display modal and calls `setDisplayNodeFilter` on Apply.
- `RunConfigModal`: receives `show`, `onHide`, `selectedType`, `runConfigs`, and `readOnly`.

## Rendered UI / Interaction Map

| UI State or Action | Source State or Props | Expected Result | Verification |
| --- | --- | --- | --- |
| Header initially renders | `activeSection` default `Model` | Top row shows Model, User Tables, Calc Type, Analysis, Set Run, Computation, Run Result, Multi-TP, TP Analysis, System, Display, Help, save/name/back/status controls. Second row shows Model controls. | Open any canvas route and inspect initial header. |
| Click a section button | `activeSection` | Active button uses `deepblue`; secondary row changes to that section's controls. | Click Calc Type, Analysis, Set Run, Multi-TP, TP Analysis, System, or Help. |
| Model section active | `activeSection === 'Model'`, disable rules | Shows create/open/save copy/save subnetwork/import subnetwork/root Verify-or-Unverify/base TP/import/export plus `TPSpecsButton`. | Confirm Model secondary row contents. |
| User Tables -> Material Properties | `ruleMaterialEditor`, `setMaterialEditor` | The base-period dropdown opens the parent Material Editor when enabled. | Open User Tables, then Material Properties. |
| User Tables -> Economic data | `ruleCostButtons` | Cost/Revenue and Supply/Demand entries open delegated Economic panels with the cost guard. | Open each User Tables Economic entry during idle and computation. |
| Multi-TP section active | `activeSection === 'Multi-TP'`, MTP guards | Shows User Tables, Time Period controls, Global TP, TP Specs, and TP Data. TP Specs opens the shared version-aware panel in MTP scope. | Open Multi-TP, click TP Specs, and confirm the MTP badge. |
| Multi-TP User Tables | `mode="mtp"`, `verified`, cost guard | Material Properties is disabled; Economic entries require the current availability guards. | Open Multi-TP, then inspect User Tables. |
| Calc Type section active | `CALC_TYPES`, `calcType`, `ruleCalcTypeButtons` | Shows Simulation, Optimization, DataRec, ParamUpdt. Active Optimization/DataRec render as setup dropdowns; other entries render as buttons. | Activate each calc type and inspect the secondary controls. |
| Active Optimization dropdown | `optimizationOptions`, diagram sets | Offers Objective function, Additional constraints, and Specification set. Set selectors load saved sets and commit only on Apply. | Select sets, cancel once, apply once, and reopen each panel. |
| Active DataRec dropdown | active Instrument Set, selected measurements/objective sets | Offers Define Instruments, Plant Measurements, Objective function, and Specification set. Editor actions open shared modules. | Select an Instrument Set, measurements, and Objective Function Sets. |
| Switch from inactive calc type | `pendingCalcType` | The plain inactive button opens confirmation; Confirm switches type and opens TP Specs. | Switch into Optimization or DataRec and confirm its control becomes a dropdown. |
| Confirm calc type switch | `pendingCalcType` | Modal closes, Redux calc type updates, and TP Specs opens. | Confirm a switch and check active button. |
| Cancel calc type switch | `showCalcTypeConfirm`, `pendingCalcType` | Modal closes without dispatching `updateCalcType`. | Open switch modal and cancel. |
| Set Run section active | `runConfigs` | Solver dropdown lists keys not matching `/algorithm/i`; Algorithm dropdown contains the `SoluAlgoLib` editor entry. | Load a domain, select a solver, then open Algorithm > SoluAlgoLib. |
| Optimization Options | `calcType === 'Optimization'`, `optimizationOptions` | Set Run shows deterministic/DRO mode; DRO requires a non-negative Wasserstein radius. | Save both modes and exercise blank, negative, and valid radius values. |
| Run config during computation | `ruleRunConfig` | `RunConfigModal` receives `readOnly=true` when the rule says ReadOnly and computation is processing. | Open Set Run while computation state is processing. |
| Computation button | `ComputationButton` child | Start/stop behavior is delegated to the child; it is always rendered in the primary row. | Use existing compute flow. |
| Run Result button | `RunResultButton` child | Result history behavior is delegated to the child; it is always rendered in the primary row. | Click Run Result on a diagram with history. |
| Display button | `displayNodeFilter`, `setDisplayNodeFilter` | Opens Display Nodes modal with radio options; Apply emits selected filter to parent. | Select Normal nodes, Apply, then inspect canvas visibility. |
| TP Analysis section active | `activeSection === 'TP Analysis'` | Shows Metabase, Configure, and an Edit button linking to `http://localhost:3001/`. | Click TP Analysis and inspect buttons/link. |
| System section active | system disable rules | Shows Import Sys Materials and Import Node Definitions with computation-aware disabled state. | Toggle computation state and inspect disabled state. |
| Help section active | hardcoded disabled buttons | Shows disabled Documentation and Tutorials buttons. | Click Help and confirm buttons are disabled. |
| Save status renders | `isSaving`, `lastSavedAt`, `lastSaveDurationMs`, autosave props | Shows a compact status pill; its tooltip contains the detailed timestamp, duration, and autosave threshold. | Save a diagram, hover the pill, and watch the compact age update. |
| Back button clicked | `setSaveConfirm` prop | Back navigation is delegated to `BackButton`; save-confirm modal is opened through parent setter when needed. | Click Back with unsaved changes. |

## Component Contract

`HeaderBarProps` are all required in current source:

| Prop | Type | Owner | Contract |
| --- | --- | --- | --- |
| `setMaterialEditor` | `Dispatch<SetStateAction<boolean>>` | `App.tsx` | Header calls it to open/close the parent material editor modal. |
| `setSaveConfirm` | `Dispatch<SetStateAction<boolean>>` | `App.tsx` | Passed to `BackButton` so navigation can trigger the parent save-confirm modal. |
| `remainingAutoSaveNodes` | `number` | `App.tsx` | Header displays how many unique node edits remain before autosave. |
| `autoSaveNodeThreshold` | `number` | `App.tsx` | Header displays the threshold denominator. |
| `theme` | `light` or `dark` | `App.tsx` | Passed to theme-aware delegated controls such as Extract Selection. |
| `displayNodeFilter` | `DisplayNodeFilter` | `App.tsx` | Header passes the current value to `DisplayButton`. |
| `setDisplayNodeFilter` | `Dispatch<SetStateAction<DisplayNodeFilter>>` | `App.tsx` | Header passes it to `DisplayButton` as `onChange`. |

Important child props:

- `SaveAndRestore` receives `disabled={ruleSaveOperations}`.
- `CanvasNameEdit` receives `disabled={ruleCanvasName}`.
- `BackButton` receives `setSaveConfirm`.
- `SaveAsSubnetwork`, `ImportSubnetwork`, and `VerifyButton` receive their matching model disable rules.
- Base `UserTablesMenu` receives `materialDisabled={ruleMaterialEditor}`, `economicDisabled={ruleCostButtons}`, and the parent Material Editor callback.
- Multi-TP `UserTablesMenu` disables Material Properties and receives `economicDisabled={ruleCostButtons || !verified}`.
- `UserTablesMenu` delegates its Economic entries to `CostButtons`; the parent `MaterialEditor` rendered in `App.tsx` receives the material read-only rule.
- Active `OptimizationSetupMenu` receives the current Objective Function / Constraint selections, `ruleCalcTypeButtons`, the combined TP Specs guard, and callbacks that open shared editors.
- Active `DataRecSetupMenu` receives the active Instrument Set, selected measurements / Objective Function Sets, the calc-type and Plant Measurement guards, the combined TP Specs guard, and shared-editor callbacks.
- `ComputationButton` always receives `optimizationOptions` and the derived `dataRecOptions`; the child sends only the option block matching the current calculation type.
- `ConstraintModule` receives `openSignal={constraintEditorOpenSignal}` and shows its own button only in Model.
- `PlantMeasurementButton` receives `openSignal`, `initialTab`, and an `onMeasurementsSaved` callback that clears stale DataRec measurement selections; it shows its own button only in Analysis.
- `RunConfigModal` receives `show`, `onHide`, `selectedType`, `runConfigs`, and `readOnly={ruleRunConfig}`.
- `TimePeriodViewer` receives `disabled={disableTpNodeButton || ruleModelVersionControl}`. `disableTpNodeButton` is currently hardcoded `false`.
- `TPSpecsButton` receives `readOnly={ruleSpecs || ruleMtpSpecs}`, `openSignal={tpSpecsOpenSignal}`, and `showButton={activeSection === 'Model'}`. The same hidden component instance also opens from Calc Type and Multi-TP through `openSignal`.
- `DisplayButton` receives `value={displayNodeFilter}` and `onChange={setDisplayNodeFilter}`.

Conditional rendering and cleanup:

- The secondary row remounts branch-specific controls when `activeSection` changes. Header-owned committed selections survive ordinary section switches.
- `RunConfigModal` is rendered only while `activeSection === 'Set Run'`.
- Calc type confirmation modal is always present but visible only when `showCalcTypeConfirm` is true.
- The shared `ConstraintModule`, `PlantMeasurementButton`, and `TPSpecsButton` instances stay rendered outside the section branches; `showButton` changes their visible triggers while signals allow cross-section opening.
- The save-age interval is created only after `lastSavedAt` exists and is cleared when dependencies change or the component unmounts.

## Data Flow

### Header Section Navigation

1. User clicks a primary section button.
2. `setActiveSection(section)` updates local state.
3. The clicked button switches to the `deepblue` variant.
4. The secondary row conditionally renders the controls for that section.
5. Child components receive disabled/read-only props based on the current computation rule state.

### User Tables Material Entry

1. Header renders `UserTablesMenu` directly in the top row with `mode="base"`.
2. `getUserTableMenuOptions(...)` applies the Material and Economic guards independently.
3. The user selects **Material Properties**.
4. `UserTablesMenu` ignores the selection if it is disabled; otherwise it calls `onOpenMaterialProperties()`.
5. Header calls `setMaterialEditor(true)`, and `App.tsx` renders the parent Material Editor with its current read-only rule.

### Calc Type Switch

1. User opens the Calc Type section.
2. `CALC_TYPES.map(...)` renders the active Optimization/DataRec type as a setup dropdown; all other types render as buttons.
3. Clicking the current Simulation or ParamUpdt button calls `openTpSpecsPanel()` directly.
4. Clicking a different plain button stores `pendingCalcType` and opens the confirmation modal.
5. Confirm dispatches `updateCalcType(pendingCalcType)`, increments `tpSpecsOpenSignal`, clears pending state, and closes the modal.
6. `TPSpecsButton` opens, and the next render turns active Optimization/DataRec into its dropdown.

### Optimization and DataRec Setup

1. The active setup dropdown opens a selector for saved sets, Instrument Sets, or Plant Measurements.
2. The child menu keeps checkbox/radio changes in modal-local draft ids.
3. **Apply** sends the freshly resolved selected objects to Header callbacks.
4. Header stores the committed selections in `optimizationOptions`, `dataRecObjectiveFunctions`, `dataRecMeasurements`, or Redux `activeInstrumentSet`.
5. Editor footer actions close the selector, then increment the `ConstraintModule` or `PlantMeasurementButton` signal.
6. Specification set increments `tpSpecsOpenSignal` and uses the one shared TP Specs instance.
7. A diagram-id change clears all committed selections; an Instrument Set change additionally clears measurements.

### Selected-Input Compute Handoff

1. Header derives `dataRecOptions` from the active Instrument Set and committed DataRec arrays.
2. Header passes `optimizationOptions` and `dataRecOptions` into `ComputationButton` on every render.
3. When Start is confirmed, `ComputationButton` includes only the option block matching `state.calcType.type`.
4. The child converts selected records into id arrays before `POST /api/compute/start`; Header objects are never treated as authoritative backend content.
5. Backend resolution and solver normalization are documented in [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md).

### Set Run

1. Header reads `runConfigs` from `state.domain.data.runConfigs`.
2. Solver dropdown includes run config keys whose names do not match `/algorithm/i`.
3. Selecting a solver calls `handleOpenRunConfig(key)` and opens `RunConfigModal` with the full `runConfigs` object.
4. Algorithm dropdown delegates its only active entry to `SolutionAlgoLibraryModule`.
5. When Optimization is active, Set Run also shows **Optimization Options** for deterministic/DRO mode.
6. `ruleRunConfig` decides whether the run-config modal is editable or read-only during computation.

### Multi-TP User Tables Guard

1. Header renders a second `UserTablesMenu` inside the Multi-TP secondary row with `mode="mtp"`.
2. Material Properties is disabled unconditionally for that mode.
3. `economicDisabled={ruleCostButtons || !verified}` guards the Economic entries.
4. `UserTablesMenu` delegates enabled Economic selections to `CostButtons`.

### Display Filter

1. User clicks Display.
2. `DisplayButton` opens a local modal and copies the current prop into `pendingValue`.
3. User chooses `All nodes`, `Normal nodes`, or `Subnetwork nodes`.
4. Apply calls `setDisplayNodeFilter(pendingValue)`.
5. `App.tsx` applies the filter to React Flow nodes and attached edges.

### Save Metadata

1. `App.tsx` and save utilities update `savedSlice` with `isSaving`, `lastSavedAt`, and `lastSaveDurationMs`.
2. Header reads those values through selectors.
3. If `lastSavedAt` exists, Header starts a one-second interval to refresh relative time text.
4. Header renders a compact Not saved / Saving / Saved-age pill and puts the absolute/relative timestamp, optional duration, and autosave threshold in its tooltip.

## Side Effects

- Header dispatches `updateCalcType(...)` only after calc type switch confirmation.
- Header opens local modals for calc type confirmation, Optimization Options, and run configuration.
- Header updates in-memory Optimization/DataRec run selections when setup modal **Apply** actions invoke callbacks.
- Header dispatches `setActiveInstrumentSet(...)`; that Redux action clears Plant Measurement editor drafts.
- Header resets run selections on diagram changes and resets DataRec measurements on Instrument Set changes or successful measurement saves.
- Header increments signals that open the existing `+Constr`, Plant Measurements, and TP Specs components.
- Header calls parent setters to open the material editor and save-confirm modal.
- Header emits display filter changes to the parent canvas shell.
- Header starts and clears a one-second timer for relative save-age text.
- Header does not directly save diagrams, start computations, delete results, edit costs, or import/export diagrams; those side effects are delegated to child components.

## Error Handling and Edge Cases

- `handleCalcTypeClick` returns immediately when `ruleCalcTypeButtons` is true.
- If `handleConfirmCalcTypeSwitch` runs without `pendingCalcType`, it closes the modal and makes no Redux update.
- Active Optimization/DataRec are dropdown toggles, so clicking them does not call the same-type TP Specs shortcut; Specification set is an explicit dropdown item.
- DRO Save is rejected when the radius is blank, non-finite, or negative. Closing the modal restores the last committed mode and radius.
- DataRec measurement selection is intentionally cleared after an Instrument Set change or measurement save to prevent stale ids reaching compute start.
- Setup-menu loading and persistence errors are owned by the child menus and shared editors, not by Header.
- `lastSavedText` returns `Not saved` when `lastSavedAt` is missing and clamps negative time differences to zero.
- `saveDurationText` is hidden when `lastSaveDurationMs` is null or negative.
- Empty `runConfigs` results in an empty Solver menu; Algorithm still exposes `SoluAlgoLib` through its delegated module.
- **User Tables** is not part of `mainSections`; it renders directly between Model and Calc Type.
- Several controls are intentionally disabled placeholders in current source: Analysis secondary buttons, Multi-TP Time Horizon, Multi-TP View Time Periods, Help Documentation, and Help Tutorials.

## Extension Points

- Add a new primary section by updating `mainSections`, the render slices, and the secondary-row conditional branch in `index.tsx` together.
- Add a new direct top-row dropdown by placing it deliberately among the rendered toolbar groups instead of assuming it belongs in `mainSections`.
- Add a new computation guard by extending `ComputingDisableMap`, then consume it through `useComputingDisableRule(...)` in `index.tsx` or the delegated child.
- Add a new calculation-type setup item by updating the menu component, Header-owned committed state/callbacks, `ComputationButton` request reduction, and backend selected-input translation together.
- Keep shared editor entry points signal-driven. Do not mount a second `ConstraintModule`, `PlantMeasurementButton`, or `TPSpecsButton` inside a dropdown modal.
- Add a new run config category by changing the Solver filter or the delegated Algorithm module deliberately; the two menus no longer share one generic key split.
- Add a new display filter by updating `DisplayNodeFilter`, `DISPLAY_NODE_FILTER_LABELS`, `DisplayButton`, and the filtering effect in `App.tsx`.
- Change Multi-TP User Tables availability by updating the header props, `user-tables-menu-options.ts`, and its focused tests together.
- Add new save metadata by extending `savedSlice.ts`, updating save utilities, and rendering the new field in the header metadata area.
- Add or enable placeholder controls only after wiring the child behavior and manual verification path; avoid leaving enabled buttons with no side effect.

## Testing and Verification

For implementation changes in the header or its child components, run the frontend build from the frontend package:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src\src\frontend
npm.cmd run build
```

For a broader repository build, run from `src/`:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npm.cmd run build
```

For documentation-only edits to this page, verify source references and Markdown whitespace from the repository root:

```powershell
git diff --check -- docs/CodeExplanation/header-bar.md
```

### Frontend Manual Verification Matrix

| Area | Setup | Action | Expected Visual Result | Expected API or State Change | Regression Risk |
| --- | --- | --- | --- | --- | --- |
| Initial header | Open any canvas route | Observe top and second rows | Model is active; save/name/back/status controls render; Model secondary controls render | No API call besides parent load effects | Medium: missing controls block common workflows. |
| Section switching | Canvas loaded | Click Calc Type, Analysis, Set Run, Multi-TP, TP Analysis, System, Help | Active button turns deep blue; secondary row swaps controls | Local `activeSection` updates | Medium: wrong branch can hide feature controls. |
| User Tables material entry | Base-period canvas loaded | Open User Tables, then select Material Properties | Parent Material Editor opens when the material rule allows it | `setMaterialEditor(true)` is called | High: wrong routing hides the material workflow. |
| Simulation/ParamUpdt same click | Calc Type section open with either type active | Click the currently active plain button | No confirm modal; TP Specs opens | `tpSpecsOpenSignal` increments; no `updateCalcType` dispatch | Medium: accidental dispatch changes solver mode. |
| Active Optimization setup | Optimization calc type active | Open dropdown, select Objective/Constraint sets, Apply | Selected checks are retained when panels reopen | Header `optimizationOptions` changes; editor records are not rewritten | High: wrong selections change solve scope. |
| Active DataRec setup | DataRec calc type active | Select Instrument Set, measurements, and Objective Functions | Each modal reflects the committed selection | Active set updates Redux; other selections update Header state | High: stale ids cause invalid reconciliation input. |
| Shared editor handoff | Either setup dropdown active | Click an Edit action | Selector closes and the existing editor opens on the correct view | Matching open signal increments | Medium: duplicate editor instances can diverge. |
| Instrument Set invalidation | DataRec measurements selected | Change Instrument Set | Previously selected measurements clear | `setDataRecMeasurements([])` runs | High: measurements must remain scoped to one set. |
| Optimization Options | Optimization active, Set Run open | Save deterministic; then save valid DRO; try invalid radius | Committed mode survives reopening; invalid radius shows an error | `optimizationOptions` changes only after valid Save | High: mode/radius are solver inputs. |
| Calc type switch confirm | Calc Type section open | Click different type, Confirm | Modal closes; new type button becomes active; TP Specs opens | `updateCalcType` dispatches once | High: calc type controls model parameter semantics. |
| Calc type switch cancel | Confirmation modal open | Click Cancel or close | Modal closes; active type stays unchanged | No `updateCalcType` dispatch | Medium: cancel must be non-destructive. |
| Set Run dropdowns | Domain has run config keys | Open Solver and Algorithm dropdowns | Solver lists non-algorithm run configs; Algorithm exposes SoluAlgoLib | Solver opens `RunConfigModal`; algorithm opens its module | Medium: wrong routing hides run configuration. |
| Multi-TP User Tables | Open an unverified, then verified diagram | Open Multi-TP and inspect User Tables | Material Properties stays disabled; Economic entries require verification and the cost rule | Reads `verified` and computation guard state; no range-detection API call | High: unverified Multi-TP Economic editing must remain guarded. |
| Display filter | Canvas has normal and subnetwork nodes | Click Display, choose Subnetwork nodes, Apply | Only subnetwork nodes remain visible; attached normal edges hide | Parent `displayNodeFilter` updates | Medium: display filtering must not delete nodes. |
| Save status | Diagram just saved | Watch and hover the status pill | Shows Saved just now, then compact seconds/minutes; tooltip shows absolute time, duration, and autosave progress | `saved.lastSavedAt` and `lastSaveDurationMs` drive text | Low: stale text misleads but does not mutate data. |
| Computation guard | Computation processing true | Inspect header controls | Guarded controls disabled/read-only according to map; run controls still visible | `useComputingDisableRule` reads `isComputationProcessing` | High: editing while compute runs can corrupt results. |
| Back/save confirm | Unsaved canvas | Click Back | Parent save confirm modal opens when BackButton requests it | `setSaveConfirm` parent setter is invoked | High: unsaved work can be lost. |

## Known Cautions

- Do not infer all top-row behavior from `mainSections`. User Tables, computation, results, display, save, and navigation controls are rendered separately.
- Active Optimization/DataRec controls are not plain buttons. Any refactor of `CALC_TYPES.map(...)` must preserve the dropdown substitution and inactive-type switch confirmation.
- Optimization/DataRec selections are not saved diagram fields. They survive section switching but reset on Header remount or diagram change.
- `ComputationButton` receives selection objects for UI convenience and reduces them to ids. Do not send the full objects as authoritative request content.
- Changing the active Instrument Set must continue clearing selected measurements and Plant Measurement drafts.
- Cross-menu editor access depends on monotonically increasing open signals. Boolean props can fail to reopen an already mounted shared component without an additional reset protocol.
- `RunConfigModal` is rendered only inside the Set Run branch. Changing active section while it is open can unmount that modal.
- Multi-TP Material Properties is intentionally unavailable; its User Tables entry is always disabled in `mode="mtp"`.
- The User Tables entry uses `ruleMaterialEditor` as its disabled state; the parent `MaterialEditor` modal in `App.tsx` receives the same material read-only rule.
- The save metadata area is display-only. The autosave threshold is tracked in `App.tsx`, not in the header.
- `useComputingDisableRule` treats empty subnetwork diagrams specially for `CalcType.CalcTypeButtons`; preserve this exception if refactoring computation guards.
- TP Specs combines the `Model.Specs` and `MTP.TPSpecs` read-only rules because one shared component serves both scopes. Do not wire only one guard when changing its placement.
- Generated runtime files such as `src/src/backend/services/solve_request.json` are not a source for header behavior and should not be edited for this documentation workflow.

## Related Pages

- [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md)
- [Dashboard and Canvas Code Explanation](./dashboard-and-canvas.md)
- [Constraint Module Code Explanation](./constraint-module.md)
- [Run Config and Computation Start Code Explanation](./run-config-and-computation-start.md)
- [Material Domain Editor Workflow Code Explanation](./material-domain-editor-workflow.md)
- [TP Spec Version Management Code Explanation](./tp-spec-version-management.md)
- [CodeExplanation Writing Standards](./CODE_EXPLANATION_GUIDELINES.md)
