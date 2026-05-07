---
title: Header Bar Code Explanation
sidebar_position: 11
description: Explains how the current HyProNet canvas header coordinates top-level navigation, secondary controls, save metadata, display filtering, run configuration, and computation-aware UI guards.
---

## Overview

The Header Bar is the fixed control surface above the React Flow canvas. It renders a primary toolbar, a contextual secondary row, save and autosave status, display filtering, navigation controls, and modals that are opened by header actions.

The main entry point is `src/src/frontend/src/components/header-bar/index.tsx`. The header receives canvas-shell callbacks and status values from `App.tsx`, reads Redux state for domain, calc type, save status, and computation guards, and delegates most feature-specific behavior to child button components.

## Source Files

- `src/src/frontend/src/components/header-bar/index.tsx`: header layout, active section state, secondary row branching, run config modal wiring, calc type confirmation, Multi-TP range detection, and save/autosave text.
- `src/src/frontend/src/components/header-bar/header-bar.css`: toolbar layout, button styling, responsive scaling, save status text, and header-specific modal/table sizing.
- `src/src/frontend/src/components/header-bar/header-buttons/display-button.tsx`: modal control for `all`, `normal`, and `subnetwork` node display filters.
- `src/src/frontend/src/utils/displayNodeFilter.ts`: display filter labels and node classification helper used by `App.tsx`.
- `src/src/frontend/src/utils/useComputingDisableRule.ts`: hook that maps computation state and diagram type to disabled/read-only decisions.
- `src/src/frontend/src/configs/computingDisableConfig.ts`: rule map for canvas, model, materials, costs, save, set-run, calc-type, MTP, system, and help controls.
- `src/src/frontend/src/features/canvas/canvasSlice.ts`: source of `isComputationProcessing`, diagram type, computation status, and other canvas state used by disable rules.
- `src/src/frontend/src/features/domain/domainSlice.ts`: source of `domain.data.runConfigs` used by the Set Run dropdowns.
- `src/src/frontend/src/features/saved/savedSlice.ts`: source of `isSaving`, `lastSavedAt`, and `lastSaveDurationMs` shown in the metadata area.
- `src/src/frontend/src/features/calcType/calcTypeSlice.ts`: source of `CALC_TYPES`, active `calcType`, and `updateCalcType(...)`.
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
- `src/src/frontend/src/components/header-bar/header-buttons/material-editor.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/metabase-button.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/create-diagram-modal.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/open-network-modal.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/import-diagram-modal.tsx`
- `src/src/frontend/src/components/header-bar/model-buttons/export-diagram-modal.tsx`
- `src/src/frontend/src/components/header-bar/run-buttons/run-config-modal.tsx`

## Purpose and Responsibility

`HeaderBar` owns navigation between header sections, the visible grouping of top-row and second-row controls, and high-level UI state such as the active section, calc type confirmation modal, run config modal, Multi-TP availability state, and save status text.

It does not own the implementation details of saving, computing, diagram creation/open/import/export, cost editing, TP editing, material editing, or result history. Those actions are delegated to child components. It also does not own React Flow node visibility; it receives `displayNodeFilter` and `setDisplayNodeFilter` from `App.tsx`, then passes them into `DisplayButton`.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `setMaterialEditor` | Parent `App.tsx` | Opens the top-level `MaterialEditor` modal rendered by the canvas shell. |
| `setSaveConfirm` | Parent `App.tsx` | Opens the save-confirm modal before leaving through the back button. |
| `remainingAutoSaveNodes` | Parent `App.tsx` autosave tracker | Shows how many unique node edits remain before autosave. |
| `autoSaveNodeThreshold` | Parent `App.tsx` constant | Shows the autosave threshold denominator. |
| `displayNodeFilter` | Parent `App.tsx` local state | Sets the selected Display modal value. |
| `setDisplayNodeFilter` | Parent `App.tsx` local setter | Emits Display modal changes back to the canvas shell. |
| `diagramId` | React Router params | Enables Multi-TP range detection through `/api/data/tpnodevers?diagramId=...`. |
| `state.domain.data.runConfigs` | Redux domain slice | Populates Solver and Algorithm dropdown items. |
| `state.calcType.type` | Redux calc type slice | Highlights the active calculation type and builds switch confirmation text. |
| `state.saved.isSaving` | Redux saved slice | Shows `Saving...` and disables save operations through the rule hook. |
| `state.saved.lastSavedAt` | Redux saved slice | Drives "Last saved ... ago" text and Multi-TP refresh dependency. |
| `state.saved.lastSaveDurationMs` | Redux saved slice | Shows "Last save took ..." when available. |
| `state.canvas.isComputationProcessing` | Redux canvas slice through `useComputingDisableRule` | Disables or makes controls read-only according to `ComputingDisableMap`. |
| `state.canvas.type` and `state.canvas.nodes` | Redux canvas slice through `useComputingDisableRule` | Keeps calc type buttons available for empty subnetwork diagrams. |

| Output | Destination | Notes |
| --- | --- | --- |
| `activeSection` changes | Header local state | Selects which secondary button row branch is rendered. |
| `setMaterialEditor(true)` | Parent `App.tsx` | Opens the material editor modal; read-only enforcement is applied by the parent modal. |
| `setSaveConfirm(true)` | Parent `App.tsx` via `BackButton` | Opens save confirmation before navigation. |
| `updateCalcType(pendingCalcType)` | Redux calc type slice | Applies confirmed calc type switch. |
| `tpSpecsOpenSignal` increment | `TPSpecsButton` prop | Opens TP Specs after same-type click or confirmed calc type switch. |
| `setDisplayNodeFilter(...)` | Parent `App.tsx` | Causes canvas nodes and attached edges to hide/show. |
| `showRunConfigModal` and `selectedRunConfigType` | Header local state | Controls `RunConfigModal` when Set Run is active. |
| `networkHasMultiTp` | Header local state | Decides whether Multi-TP Economic cost editing is read-only. |

## Core State and Data Structures

- `activeSection`: local string state, default `Model`. Controls secondary row conditional rendering.
- `mainSections`: local array with `Model`, `Materials`, `Economic`, `Save`, `Calc Type`, `Analysis`, `Set Run`, `Run`, `Multi-TP`, `TP Analysis`, `System`, and `Help`. Current render slices skip `Save` and `Run` as section buttons; save and run are fixed controls instead.
- `showCalcTypeConfirm`: local boolean that renders the calc type confirmation modal.
- `pendingCalcType`: local calc type waiting for confirmation.
- `tpSpecsOpenSignal`: local counter passed to `TPSpecsButton`; incrementing it opens TP Specs.
- `showRunConfigModal` and `selectedRunConfigType`: local Set Run modal state.
- `networkHasMultiTp`: local boolean fetched from `tpnodevers` rows. It is true when any row has a non-base TP range other than `1-1`.
- `nowMs`: local clock updated once per second while `lastSavedAt` exists.
- `lastSavedText`: memoized display string derived from `lastSavedAt` and `nowMs`.
- `saveDurationText`: memoized display string derived from `lastSaveDurationMs`.
- `rule*` values: booleans returned by `useComputingDisableRule(...)` for named control groups.

## Main Functions and Components

- `HeaderBar(...)`: renders the top toolbar, secondary row, and calc type confirmation modal.
- `openTpSpecsPanel()`: increments `tpSpecsOpenSignal`.
- `handleCalcTypeClick(nextCalcType)`: returns early when calc type buttons are guarded, opens TP Specs directly for the current type, or opens the confirmation modal for a different type.
- `handleConfirmCalcTypeSwitch()`: dispatches `updateCalcType(pendingCalcType)`, opens TP Specs, clears pending state, and closes the modal.
- `handleOpenRunConfig(type)`: opens `RunConfigModal` and stores the chosen solver or algorithm key.
- `handleCloseRunConfig()`: closes `RunConfigModal` and clears the selected key.
- Multi-TP detection effect: calls `/api/data/tpnodevers?diagramId=${diagramId}`, treats rows outside `1-1` as Multi-TP, resets to false without a diagram ID or after an error, and uses a cancellation flag during cleanup.
- Save clock effect: starts a one-second interval only when `lastSavedAt` is present and clears it on cleanup.
- `DisplayButton`: renders the Display modal and calls `setDisplayNodeFilter` on Apply.
- `RunConfigModal`: receives `show`, `onHide`, `selectedType`, `runConfigs`, and `readOnly`.

## Rendered UI / Interaction Map

| UI State or Action | Source State or Props | Expected Result | Verification |
| --- | --- | --- | --- |
| Header initially renders | `activeSection` default `Model` | Top row shows Model, Materials, Economic, Calc Type, Analysis, Set Run, Computation, Run Result, Multi-TP, TP Analysis, System, Display, Help, save/name/back/status controls. Second row shows Model controls. | Open any canvas route and inspect initial header. |
| Click a section button | `activeSection` | Active button uses `deepblue`; secondary row changes to that section's controls. | Click Materials, Economic, Calc Type, Set Run, Multi-TP, System, Help. |
| Model section active | `activeSection === 'Model'`, disable rules | Shows create/open/save copy/save subnetwork/import subnetwork/verify/base TP/import/export plus `TPSpecsButton`. | Confirm Model secondary row contents. |
| Materials section active | `setMaterialEditor` prop | Shows MaterialEditor launcher; click opens parent material modal. | Click Materials, then Material Editor. |
| Economic section active | `ruleCostButtons` | Shows base `CostButtons` with read-only state from cost rule. | Open Economic during idle and during computation. |
| Calc Type section active | `CALC_TYPES`, `calcType`, `ruleCalcTypeButtons` | Shows Simulation, Optimization, DataRec, ParamUpdt; active calc type is primary. Same type opens TP Specs; different type opens confirmation. | Click active type and inactive type. |
| Confirm calc type switch | `pendingCalcType` | Modal closes, Redux calc type updates, and TP Specs opens. | Confirm a switch and check active button. |
| Cancel calc type switch | `showCalcTypeConfirm`, `pendingCalcType` | Modal closes without dispatching `updateCalcType`. | Open switch modal and cancel. |
| Set Run section active | `runConfigs` | Solver dropdown lists keys not matching `/algorithm/i`; Algorithm dropdown lists keys matching `/algorithm/i`; selecting one opens `RunConfigModal`. | Load a domain with run configs and select each dropdown. |
| Run config during computation | `ruleRunConfig` | `RunConfigModal` receives `readOnly=true` when the rule says ReadOnly and computation is processing. | Open Set Run while computation state is processing. |
| Computation button | `ComputationButton` child | Start/stop behavior is delegated to the child; it is always rendered in the primary row. | Use existing compute flow. |
| Run Result button | `RunResultButton` child | Result history behavior is delegated to the child; it is always rendered in the primary row. | Click Run Result on a diagram with history. |
| Display button | `displayNodeFilter`, `setDisplayNodeFilter` | Opens Display Nodes modal with radio options; Apply emits selected filter to parent. | Select Normal nodes, Apply, then inspect canvas visibility. |
| Multi-TP section active with no multi range | `networkHasMultiTp === false` | Multi-TP Economic dropdown is read-only; Time Horizon and View Time Periods are disabled; TP Node and Global TP controls render. | Open Multi-TP on a base-only diagram. |
| Multi-TP section active with multi range | `/api/data/tpnodevers` rows outside `1-1` | Multi-TP Economic dropdown can become editable unless cost rule also makes it read-only. | Add/save a non-base TP range, reopen Multi-TP. |
| TP Analysis section active | `activeSection === 'TP Analysis'` | Shows Metabase, Configure, and an Edit button linking to `http://localhost:3001/`. | Click TP Analysis and inspect buttons/link. |
| System section active | system disable rules | Shows Import Sys Materials and Import Node Definitions with computation-aware disabled state. | Toggle computation state and inspect disabled state. |
| Help section active | hardcoded disabled buttons | Shows disabled Documentation and Tutorials buttons. | Click Help and confirm buttons are disabled. |
| Save status renders | `isSaving`, `lastSavedAt`, `lastSaveDurationMs`, autosave props | Shows Not saved or Last saved age, autosave threshold text, optional save duration, and Saving... while a save is active. | Save a diagram and watch the age update. |
| Back button clicked | `setSaveConfirm` prop | Back navigation is delegated to `BackButton`; save-confirm modal is opened through parent setter when needed. | Click Back with unsaved changes. |

## Component Contract

`HeaderBarProps` are all required in current source:

| Prop | Type | Owner | Contract |
| --- | --- | --- | --- |
| `setMaterialEditor` | `Dispatch<SetStateAction<boolean>>` | `App.tsx` | Header calls it to open/close the parent material editor modal. |
| `setSaveConfirm` | `Dispatch<SetStateAction<boolean>>` | `App.tsx` | Passed to `BackButton` so navigation can trigger the parent save-confirm modal. |
| `remainingAutoSaveNodes` | `number` | `App.tsx` | Header displays how many unique node edits remain before autosave. |
| `autoSaveNodeThreshold` | `number` | `App.tsx` | Header displays the threshold denominator. |
| `displayNodeFilter` | `DisplayNodeFilter` | `App.tsx` | Header passes the current value to `DisplayButton`. |
| `setDisplayNodeFilter` | `Dispatch<SetStateAction<DisplayNodeFilter>>` | `App.tsx` | Header passes it to `DisplayButton` as `onChange`. |

Important child props:

- `SaveAndRestore` receives `disabled={ruleSaveOperations}`.
- `CanvasNameEdit` receives `disabled={ruleCanvasName}`.
- `BackButton` receives `setSaveConfirm`.
- `SaveAsSubnetwork`, `ImportSubnetwork`, and `VerifyButton` receive their matching model disable rules.
- Header `MaterialEditor` receives `setMaterialEditor`; the read-only state is handled by the parent `MaterialEditor` modal rendered in `App.tsx`.
- Base Economic `CostButtons` receives `readOnly={ruleCostButtons}`.
- Multi-TP Economic `CostButtons` receives `readOnly={ruleCostButtons || !networkHasMultiTp}`, `showTpRanges`, `triggerMode="dropdown"`, and `dropdownLabel="Economic"`.
- `RunConfigModal` receives `show`, `onHide`, `selectedType`, `runConfigs`, and `readOnly={ruleRunConfig}`.
- `TimePeriodViewer` receives `disabled={disableTpNodeButton || ruleModelVersionControl}`. `disableTpNodeButton` is currently hardcoded `false`.
- `TPSpecsButton` receives `readOnly={ruleSpecs}`, `openSignal={tpSpecsOpenSignal}`, and `showButton={activeSection === 'Model'}`.
- `DisplayButton` receives `value={displayNodeFilter}` and `onChange={setDisplayNodeFilter}`.

Conditional rendering and cleanup:

- The secondary row remounts branch-specific controls when `activeSection` changes.
- `RunConfigModal` is rendered only while `activeSection === 'Set Run'`.
- Calc type confirmation modal is always present but visible only when `showCalcTypeConfirm` is true.
- The Multi-TP detection effect cleans up with a `cancelled` flag so a late API response does not update unmounted state.
- The save-age interval is created only after `lastSavedAt` exists and is cleared when dependencies change or the component unmounts.

## Data Flow

### Header Section Navigation

1. User clicks a primary section button.
2. `setActiveSection(section)` updates local state.
3. The clicked button switches to the `deepblue` variant.
4. The secondary row conditionally renders the controls for that section.
5. Child components receive disabled/read-only props based on the current computation rule state.

### Calc Type Switch

1. User opens the Calc Type section.
2. `CALC_TYPES.map(...)` renders one button per calc type.
3. Clicking the current type calls `openTpSpecsPanel()` directly.
4. Clicking a different type stores `pendingCalcType` and opens the confirmation modal.
5. Confirm dispatches `updateCalcType(pendingCalcType)`, increments `tpSpecsOpenSignal`, clears pending state, and closes the modal.
6. `TPSpecsButton` receives the changed `openSignal` and opens its panel.

### Set Run

1. Header reads `runConfigs` from `state.domain.data.runConfigs`.
2. Solver dropdown includes run config keys whose names do not match `/algorithm/i`.
3. Algorithm dropdown includes run config keys whose names match `/algorithm/i`.
4. Selecting any item calls `handleOpenRunConfig(key)`.
5. `RunConfigModal` opens with the selected key and the full `runConfigs` object.
6. `ruleRunConfig` decides whether the modal is editable or read-only during computation.

### Multi-TP Economic Guard

1. Header effect runs when `diagramId`, `lastSavedAt`, or `activeSection` changes.
2. If no `diagramId` exists, `networkHasMultiTp` becomes false.
3. Otherwise the effect calls `/api/data/tpnodevers?diagramId=<diagramId>`.
4. Rows are inspected for `fromTp/fromTP` and `toTp/toTP`.
5. Any finite range other than `1-1` sets `networkHasMultiTp` true.
6. The Multi-TP Economic dropdown stays read-only when `networkHasMultiTp` is false or the cost disable rule is active.

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
4. Header renders Not saved, Last saved age, autosave threshold progress, and optional save duration.

## Side Effects

- Header calls `/api/data/tpnodevers?diagramId=...` to detect whether the current diagram has Multi-TP ranges.
- Header dispatches `updateCalcType(...)` only after calc type switch confirmation.
- Header opens local modals for calc type confirmation and run configuration.
- Header calls parent setters to open the material editor and save-confirm modal.
- Header emits display filter changes to the parent canvas shell.
- Header starts and clears a one-second timer for relative save-age text.
- Header does not directly save diagrams, start computations, delete results, edit costs, or import/export diagrams; those side effects are delegated to child components.

## Error Handling and Edge Cases

- `handleCalcTypeClick` returns immediately when `ruleCalcTypeButtons` is true.
- If `handleConfirmCalcTypeSwitch` runs without `pendingCalcType`, it closes the modal and makes no Redux update.
- If Multi-TP detection runs without a `diagramId`, `networkHasMultiTp` is reset to false.
- If the Multi-TP detection request fails, the error is logged and `networkHasMultiTp` is reset to false, which makes Multi-TP Economic editing read-only.
- `lastSavedText` returns `Not saved` when `lastSavedAt` is missing and clamps negative time differences to zero.
- `saveDurationText` is hidden when `lastSaveDurationMs` is null or negative.
- Empty `runConfigs` results in empty Solver and Algorithm dropdown menus; the dropdowns still render.
- `mainSections` includes `Save` and `Run`, but current render slices do not render them as section buttons.
- Several controls are intentionally disabled placeholders in current source: Analysis secondary buttons, Multi-TP Time Horizon, Multi-TP View Time Periods, Help Documentation, and Help Tutorials.
- `ruleImportUsrMaterials`, `ruleTimeHorizon`, `ruleTPsSpecs`, and `ruleTPData` are defined in `index.tsx`, but the corresponding current JSX either does not pass them to a child or has unresolved developer notes.

## Extension Points

- Add a new primary section by updating `mainSections`, the render slices, and the secondary-row conditional branch in `index.tsx` together.
- Convert `Save` or `Run` into active sections only after deciding how they should coexist with the fixed `SaveAndRestore`, `ComputationButton`, and `RunResultButton` controls.
- Add a new computation guard by extending `ComputingDisableMap`, then consume it through `useComputingDisableRule(...)` in `index.tsx` or the delegated child.
- Add a new run config category by changing the Solver/Algorithm key filter logic if the backend introduces keys that do not fit the current `/algorithm/i` split.
- Add a new display filter by updating `DisplayNodeFilter`, `DISPLAY_NODE_FILTER_LABELS`, `DisplayButton`, and the filtering effect in `App.tsx`.
- Change Multi-TP Economic availability by updating the `tpnodevers` range detection and the `CostButtons` `readOnly` expression together.
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
git diff --check -- docs/SetupInstructions/CodeExplanation/header-bar.md
```

### Frontend Manual Verification Matrix

| Area | Setup | Action | Expected Visual Result | Expected API or State Change | Regression Risk |
| --- | --- | --- | --- | --- | --- |
| Initial header | Open any canvas route | Observe top and second rows | Model is active; save/name/back/status controls render; Model secondary controls render | No API call besides parent load effects | Medium: missing controls block common workflows. |
| Section switching | Canvas loaded | Click Materials, Economic, Calc Type, Set Run, Multi-TP, System, Help | Active button turns deep blue; secondary row swaps controls | Local `activeSection` updates | Medium: wrong branch can hide feature controls. |
| Calc type same click | Calc Type section open | Click currently active calc type | No confirm modal; TP Specs opens | `tpSpecsOpenSignal` increments; no `updateCalcType` dispatch | Medium: accidental dispatch changes solver mode. |
| Calc type switch confirm | Calc Type section open | Click different type, Confirm | Modal closes; new type button becomes active; TP Specs opens | `updateCalcType` dispatches once | High: calc type controls model parameter semantics. |
| Calc type switch cancel | Confirmation modal open | Click Cancel or close | Modal closes; active type stays unchanged | No `updateCalcType` dispatch | Medium: cancel must be non-destructive. |
| Set Run dropdowns | Domain has run config keys | Open Solver and Algorithm dropdowns | Solver excludes algorithm-like keys; Algorithm includes them | Selecting a key opens `RunConfigModal` | Medium: wrong split hides run configuration. |
| Multi-TP base-only diagram | Existing diagram has only `1-1` TP rows | Open Multi-TP section | Economic dropdown is read-only; other Multi-TP controls render | `/api/data/tpnodevers?diagramId=...` returns base-only rows; `networkHasMultiTp=false` | High: cost editing must not target missing TP ranges. |
| Multi-TP ranged diagram | Existing diagram has non-`1-1` TP row | Open Multi-TP section after save | Economic dropdown becomes available unless computation rule is active | TP range request sets `networkHasMultiTp=true` | High: range-level cost editing depends on this guard. |
| Display filter | Canvas has normal and subnetwork nodes | Click Display, choose Subnetwork nodes, Apply | Only subnetwork nodes remain visible; attached normal edges hide | Parent `displayNodeFilter` updates | Medium: display filtering must not delete nodes. |
| Save status | Diagram just saved | Watch header for 60 seconds | Shows Last saved just now, then seconds/minutes; save duration appears if available | `saved.lastSavedAt` and `lastSaveDurationMs` drive text | Low: stale text misleads but does not mutate data. |
| Computation guard | Computation processing true | Inspect header controls | Guarded controls disabled/read-only according to map; run controls still visible | `useComputingDisableRule` reads `isComputationProcessing` | High: editing while compute runs can corrupt results. |
| Back/save confirm | Unsaved canvas | Click Back | Parent save confirm modal opens when BackButton requests it | `setSaveConfirm` parent setter is invoked | High: unsaved work can be lost. |

## Known Cautions

- Do not infer section behavior from the `mainSections` array alone. `Save` and `Run` exist in the array but are not rendered as active section buttons in the current JSX.
- `RunConfigModal` is rendered only inside the Set Run branch. Changing active section while it is open can unmount that modal.
- Multi-TP range detection depends on `/api/data/tpnodevers` and is refreshed on `diagramId`, `lastSavedAt`, and `activeSection`; unsaved TP changes may not affect `networkHasMultiTp`.
- Multi-TP Economic editing is read-only unless a non-`1-1` TP range is detected.
- Header MaterialEditor button does not receive `ruleImportUsrMaterials`; the parent `MaterialEditor` modal in `App.tsx` receives the material editor read-only rule.
- Several rule variables are currently defined but not wired to active controls. Check JSX before assuming a rule affects the UI.
- The save metadata area is display-only. The autosave threshold is tracked in `App.tsx`, not in the header.
- `useComputingDisableRule` treats empty subnetwork diagrams specially for `CalcType.CalcTypeButtons`; preserve this exception if refactoring computation guards.
- Generated runtime files such as `src/src/backend/services/solve_request.json` are not a source for header behavior and should not be edited for this documentation workflow.

## Related Pages

- `docs/SetupInstructions/CodeExplanation/dashboard-and-canvas.md`
- `docs/SetupInstructions/CodeExplanation/CODE_EXPLANATION_GUIDELINES.md`
