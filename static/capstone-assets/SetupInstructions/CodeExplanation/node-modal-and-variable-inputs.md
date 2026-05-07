---
title: Node Modal and Variable Inputs Code Explanation
sidebar_position: 22
description: Explains how the HyProNet node modal tabs edit node settings, stream variables, info variables, specs, time-period overrides, Redux state, and node cache data.
---

## Overview

The Node Modal area is the node-level editor shown through React Flow `NodeToolbar`. It contains Settings, Streams, Node Variables, and Specs tabs. It is the main UI for node name/model version changes, port variable edits, stream-derived component displays, required variable edits, time period selection, and subnetwork navigation.

This page documents the current modal and input behavior in `src/src/frontend/src/components/modal/`.

## Source Files

- `src/src/frontend/src/components/modal/index.tsx`: `ShapeNodeModal` container, active tab state, selected port state, shared time-period state, and base edit callback normalization.
- `src/src/frontend/src/components/modal/modal-header.tsx`: tab button renderer and tab names.
- `src/src/frontend/src/components/modal/useNodeDataPrefetch.ts`: prefetches TP changes, parent proxy streams, and merged model versions for modal display.
- `src/src/frontend/src/components/modal/utils.ts`: unit conversion helper.
- `src/src/frontend/src/components/modal/tabs/settings-tab.tsx`: node name/model version settings, TP dropdown, model metadata display, subnetwork navigation, and model version loading.
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`: non-info port variables, stream mode display, port selection, TP merge logic, TP draft writes, and subnetwork wrapper/internal metadata mapping.
- `src/src/frontend/src/components/modal/tabs/info-tab.tsx`: info-port variables for `port_type === 0`, TP merge logic, and TP draft writes.
- `src/src/frontend/src/components/modal/tabs/specs-tab.tsx`: required variable view, exposed wrapper-port filtering, TP merge logic, and TP draft writes.
- `src/src/frontend/src/components/modal/tabs/node-var-input.tsx`: atomic value/spec/bounds/unit input row, unit conversion, local edit state, Redux writes, and node cache writes.
- `src/src/frontend/src/components/modal/tabs/nodeVarInputUtils.ts`: numeric coercion and display formatting helpers.
- `src/src/frontend/src/components/modal/tabs/nodeVarsTabUtils.ts`: renderable-port filtering and base-only Redux display-cache lookup.
- `src/src/frontend/src/components/modal/tabs/tp-sync-utils.ts`: TP draft keys, comparable diffs, wrapper/internal mirror targets, and wrapper port mapping resolution.
- `src/src/frontend/src/components/modal/modal.css`: modal input, variable, stream, unit, and hidden/computed styling.
- `src/src/frontend/src/components/modal/ShapeNodeModal.css`: container, tabs, selected tab, info/specs scroll area, and variable-row styling.
- `src/src/frontend/src/features/node/nodeCacheService.ts`: node cache API used by the modal and inputs.
- `src/src/frontend/src/features/node/nodeCacheSlice.ts`: model version fetch/save, dirty tracking, and selectors.
- `src/src/frontend/src/features/canvas/canvasSlice.ts`: `nodeParameters`, `tpChangesDraft`, `parentConnections`, node name, verified, and diagram node state.
- `src/src/frontend/src/features/canvas/utils/nodeParametersUtils.ts`: rebuilds Redux node parameter entries after model version changes.
- `src/src/frontend/src/features/canvas/utils/nodeSettingsUtils.ts`: resolves TP baseline model versions and merges connected streams plus TP changes.
- `src/src/frontend/src/utils/modelVersionUtils.ts`: applies calc type, connected streams, and stream-property hydration to model versions.
- `src/src/frontend/src/utils/modelVersionState.ts`: resolves cached vs embedded model versions and base TP template model versions.
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: save-time node cache merge, diagram save, node save, and TP draft persistence.
- `src/src/backend/routes/dataRoutes.ts`: backend endpoints for node data, diagram saves, `tpnodevers`, and `tpchanges`.

## Purpose and Responsibility

`ShapeNodeModal` owns the tab shell and shared UI state for one selected node. Individual tabs own their own display and merge logic. `NodeVarInput` owns one row's local edit experience and delegates persistence decisions through callbacks, Redux, and node cache.

The modal does not directly own final diagram save or solver translation. It prepares in-memory state so the save flow can persist model versions, diagram canvas data, and TP changes.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `model` | `ShapeNode` node data | Node name, domain model id, selected model version id, subnetwork ids, ports mapping, and embedded model version fallback. |
| `nodeId` or `reactFlowNodeId` | `ShapeNode` | Cache key, Redux parameter key, backend node id, and TP draft node id. |
| `onModelFieldChange` | `ShapeNode` callback | Writes top-level model fields back into React Flow node data. |
| `onNodeVarFieldChange` | `ShapeNode` callback | Base TP variable edits flow back to node cache. |
| `onSelectTimePeriod` | `ShapeNode` callback | Keeps parent node model's active time period marker aligned. |
| `domain.data.models`, `domain.data.units`, `domain.data.streams` | Redux domain state | Ports, model versions, units, streams, and stream fractions. |
| `canvas.verified`, `canvas.nodeParameters`, `canvas.tpChangesDraft`, `canvas.parentConnections` | Redux canvas state | Tab branching, displayed values, pending TP overrides, and subnetwork mapping context. |
| `diagramId`, `domainId` | route params | Backend API context and Redux parameter metadata. |

| Output | Destination | Notes |
| --- | --- | --- |
| Model field changes | React Flow node data through `onModelFieldChange` | Node names, default model version id, and subnetwork diagram id updates. |
| Base TP model version changes | node cache through `updateNodeValue` | Values, bounds, unit, spec, and selected model version changes mark node cache dirty by default. |
| Display/runtime parameter changes | Redux `canvas.nodeParameters` | Composite keys use `{timePeriodId}-{nodeId}-{portVarId}`. |
| Non-base TP drafts | Redux `canvas.tpChangesDraft` | Sparse overrides persist on Save through `/api/data/tpchanges`. |
| Saved status | Redux saved slice | Most Redux actions mark the diagram unsaved through middleware; inputs also dispatch `updateSaved(false)`. |
| Backend reads | `/api/data/nodes`, `/api/data/tpnodevers`, `/api/data/tpchanges`, `/api/data/diagrams/{id}` | Used for lazy loading and display merges. |

## Core State and Data Structures

- `activeTab`: local `ShapeNodeModal` tab state: `settings`, `nodeVars`, `info`, or `specs`.
- `activeTimePeriodId`: shared modal time period state. Defaults to `BASE_TP`.
- `selectedPort`: selected non-info port location for Streams and Specs tabs. Defaults to the first non-info domain/model port.
- `nodeParameters`: Redux cache of displayed or edited values. It is merged incrementally by `updateComputationResults`.
- `tpChangesDraft`: Redux map of sparse TP overrides awaiting Save.
- `timePeriods`: tab-local list from `/api/data/tpnodevers`, with fallback `BASE_TP`.
- `mergedPortsVarByTP`: tab-local merged view of baseline model vars plus streams, backend TP changes, and drafts.
- `baselinePortsVarByTP` or `baseCalcPortsVarByTP`: comparison baseline used to decide whether a non-base TP edit is an override or a delete draft.
- `selectedWrapperPortMapping`: wrapper external port to internal node/port mapping from `model.portsMapping`.

## Main Components and Functions

- `ShapeNodeModal(...)`: renders `NodeToolbar`, `ModalHeader`, and active tab component. It normalizes input events and coordinates selected port/time period.
- `handleVarChange(...)`: converts input/select events into number, string, or undefined; updates base TP cache for `base_unit_default_value`; then calls `onNodeVarFieldChange`.
- `SettingsTab(...)`: loads the base model version, fetches TP node versions, updates node names, switches base model version, refreshes node parameters, and handles "Go to Subnetwork".
- `useNodeDataPrefetch(...)`: fetches all TP changes, builds parent proxy edges for mapped subnetwork ports, merges model versions per TP, and seeds Redux node parameters.
- `NodeVarsTab(...)`: filters variables for the selected port, supports stream mode, builds non-base TP merged variables, and upserts/delete-drafts TP overrides.
- `InfoTab(...)`: targets the info port, overlays Redux values, and uses the same non-base TP draft pattern as `NodeVarsTab`.
- `SpecsTab(...)`: shows required variables for the selected port, filters exposed wrapper ports, and applies internal mapped port metadata when editing wrapper ports.
- `NodeVarInput(...)`: manages value/spec/bounds/unit local state, commits edits on blur/change, updates Redux, updates node cache for Base TP, and disables spec edits in Simulation.
- `refreshNodeParametersAfterModelVersionChange(...)`: deletes and rebuilds Redux node parameter entries for one node/time period when model version context changes.
- `resolveTpMirrorTargets(...)`: creates wrapper-to-internal or internal-to-wrapper TP draft mirror targets for mapped ports.

## Rendered UI and Interaction Map

| Tab or Control | Source State or Props | Expected Result | State or API Effect |
| --- | --- | --- | --- |
| Settings tab | `canvas.verified`, model, domain model versions | Shows node/subnetwork name, base model version selector when unverified, TP selector and model metadata when verified. | May load model version, fetch `/tpnodevers`, update node names, refresh `nodeParameters`. |
| Streams tab button | `ModalHeader` tab name for `nodeVars` | Opens `NodeVarsTab`, labeled `Streams`. | Local `activeTab` changes only. |
| Node Variables tab button | `ModalHeader` tab name for `info` | Opens `InfoTab`. | Local `activeTab` changes only. |
| Specs tab | required vars and selected port | Shows only required variables for selected port; wrapper nodes show exposed ports only. | Edits write base cache or TP drafts. |
| Port dropdown | `domainModel.ports` and `selectedPort` | Changes visible port variables. | Local selected port state changes. |
| Time Period dropdown | tab-local `timePeriods` | Switches displayed values between Base TP and TP-specific merged values. | Calls shared `onTimePeriodSelect`; non-base tabs fetch/build merged vars. |
| Go to Stream | connected edge state | Switches `NodeVarsTab` from port variables to component flow/fraction display. | No backend write; display uses connected stream and node parameters. |
| Show Hidden Variables | `hidden_by_default` flags | Hidden variables become visible or hidden. | Local `showHiddenVars` state only. |
| Value input blur | `NodeVarInput` local state | Commits numeric/null value, highlights required or computed state. | Base TP: node cache and Redux. Non-base TP: parent tab writes Redux and TP draft. |
| Spec dropdown | `calcType` | Disabled in Simulation; otherwise commits `F`, `V`, `P`, `I`, `CALC`, or null. | Updates node cache/Redux for Base TP or TP draft for non-base TP. |
| Unit dropdown | domain units and dimension | Converts display unit and stores selected unit. | Updates node cache/Redux and calls parent change handler. |

## Component Contract

### `ShapeNodeModal`

Required props:

- `model: Model`
- `nodeId: string`
- `onModelFieldChange(field, value)`
- `onNodeVarFieldChange(portsVarId, timePeriodId, field, value)`
- `onSelectTimePeriod(timePeriodId)`

Important child props:

- `SettingsTab`: gets shared time period selection and node id.
- `NodeVarsTab`: gets selected port, port-change handler, active time period, and model field callback.
- `InfoTab`: gets canonical node id and active time period.
- `SpecsTab`: gets selected port, port-change handler, and active time period.

Hooks/effects:

- The selected port effect resets `selectedPort` when the domain/model port list changes and the old location is no longer present.
- `cachedModelVersion` is read after the event handler definition but used at runtime by `handleVarChange`; it must exist before a Base TP cache update can happen.

### `NodeVarInput`

Required behavior-relevant props include `portVarId`, `portVarName`, value/bounds/unit fields, `required`, `spec`, `isComputed`, `is_human_input`, `node_id`, `tpid`, `isBaseTP`, and `parameterDiagramId`.

`NodeVarInput` commits:

- Value, lower bound, and upper bound on blur.
- Spec on dropdown change.
- Selected unit on unit dropdown change.

It writes `is_human_input: true` and `is_computed: false` for user edits. Hidden variables are read-only/disabled and styled as hidden.

### Modal Tab Contracts

- Base TP changes must be able to update node cache so Save can persist the node model version.
- Non-base TP changes must create or delete sparse TP drafts instead of mutating the base model version.
- Tabs that fetch async data guard against missing ids and fall back to Base TP.
- Specs and NodeVars subnetwork wrapper views must resolve exposed wrapper ports and mapped internal metadata using `tp-sync-utils.ts`.

## Data Flow

### Base TP value edit

1. The user edits a `NodeVarInput` value and blurs the input.
2. `NodeVarInput.handleBlur` converts display value back to base unit when needed.
3. It calls the tab `handleChange`.
4. For Base TP, the tab calls `ShapeNodeModal.handleVarChange(..., 'BASE_TP')`.
5. `ShapeNodeModal.handleVarChange` updates the cached model version for `base_unit_default_value` and calls `onNodeVarFieldChange`.
6. `ShapeNode.onNodeVarFieldChange` updates the matching cached `ports_var` entry and calls `updateNodeValue(canonicalNodeId, updatedModelVersion)`.
7. `NodeVarInput` also dispatches `updateComputationResults` for the composite key.
8. Save later merges compatible `nodeParameters` into model versions, sends diagram `nodeCacheDiffs` or `nodeCacheFull`, and persists dirty node versions through `/api/data/nodes`.

### Non-base TP value/spec/bounds/unit edit

1. The user selects a non-base Time Period.
2. `NodeVarsTab`, `InfoTab`, or `SpecsTab` builds merged port variables from TP baseline, calc type, streams, backend `/tpchanges`, and current drafts.
3. The user edits a `NodeVarInput`.
4. The tab updates `mergedPortsVarByTP` optimistically.
5. The tab dispatches `updateComputationResults` for the non-base composite key.
6. The tab compares the edited values against the baseline values.
7. If values match the baseline, it dispatches `upsertTpChangeDraft` with `isDelete: true`.
8. If any field differs, it dispatches `upsertTpChangeDraft` with `portVarValue`, `lowerBound`, `upperBound`, `unit`, `spec`, `diagramId`, `nodeId`, `timePeriodId`, `portName`, `portVarName`, and `portLocation`.
9. `resolveTpMirrorTargets` adds wrapper/internal mirror drafts where needed.
10. Save persists drafts through `POST /api/data/tpchanges` or `DELETE /api/data/tpchanges`, then clears `tpChangesDraft`.

### Model version switch

1. In Settings, the user changes the base model version selector when the diagram is unverified and not a subnetwork.
2. `SettingsTab.handleModelVersionChange` resolves the selected domain model version.
3. It applies `initModelVersionWithCalcType` with connected edges to preserve stream-driven variables.
4. It writes the new model version to node cache and updates `model.defaultModelVersionId`.
5. It calls `refreshNodeParametersAfterModelVersionChange` for `BASE_TP`.

### Subnetwork navigation and mapped data

1. Settings detects a subnetwork model through `diagramId` on the model.
2. "Go to Subnetwork" either navigates to an existing instance or asks to save before creating/ensuring one.
3. `GET/POST /api/data/diagrams/{currentDiagramId}/subnetwork-instance` can be used to ensure an instance diagram.
4. Wrapper and internal TP edits use `resolveWrapperPortMappingTarget` and `resolveTpMirrorTargets` so exposed-port changes can mirror between parent wrapper and internal node contexts.

## Backend/Data-Flow Contract

- Base model version data is loaded with `GET /api/data/nodes/{nodeId}` and persisted by Save through diagram payloads plus node save calls.
- Time-period lists are loaded with `GET /api/data/tpnodevers`.
- TP overrides are read with `GET /api/data/tpchanges` or `GET /api/data/tpchanges/all`.
- Pending TP overrides are not posted immediately by modal tabs. They are stored in Redux `tpChangesDraft` and persisted by `save-util.tsx` on Save.
- Existing diagram saves use `PUT /api/data/diagrams/{diagramId}`; new diagram saves use `POST /api/data/diagrams`.
- Compute reads saved diagrams and persisted node cache/TP data. Modal runtime state that was not saved should not be assumed to reach compute.

## Side Effects

- Settings can dispatch `setVerified(true)` when `tpnodevers` exist and the current canvas is not verified.
- Settings updates node name lists with `addNodeName`, `removeNodeName`, `initializeNodeNames`, and `setDiagramNodes`.
- `NodeVarInput` prevents mouse wheel and arrow-key increments on number inputs by attaching DOM listeners and removing them on cleanup.
- Info and Specs tabs stop wheel events inside their scroll containers.
- `useNodeDataPrefetch` can dispatch `updateComputationResults` for many TP/node parameter entries after fetching TP changes.
- Most Redux writes mark the diagram unsaved through store middleware.

## Error Handling and Edge Cases

- If ids are missing, tabs fall back to Base TP display and skip backend fetches.
- If a cached model version is missing, Settings and Info attempt `loadModelVersion`.
- If `/tpnodevers` or `/tpchanges` fetches fail, tabs log and fall back to Base TP or empty change lists.
- If `domainUnits`, `dimension`, or unit definitions are missing, `convertToGivenUnit` returns the original value.
- Empty numeric input commits `null`.
- Invalid numeric input commits `null` when the value changed.
- `NodeVarInput` treats `null` Redux values as no computed override for Base TP display so base model values can still render.
- Specs only displays required variables and, for subnetwork instance wrapper nodes, only exposed ports.

## Port Mapping Cautions

- Wrapper external ports are selected by external `port_location`; internal metadata is resolved separately from `portsMapping`.
- Non-base TP drafts include `portLocation` to avoid collisions between ports with the same `portName` and `portVarName`.
- `resolveTpMirrorTargets` can produce wrapper-to-internal and internal-to-wrapper drafts. Keep both paths in sync when changing draft key shape.
- `NodeVarsTab` and `SpecsTab` apply mapped internal port metadata for wrapper ports so required/spec display can reflect the internal node. Do not remove this without verifying wrapper required fields.
- Parent proxy streams in `useNodeDataPrefetch` let internal subnetwork nodes display parent-connected stream data even when no local edge exists.

## Extension Points

- Add a new tab by extending `activeTab`, `ModalHeader`, and the conditional render block in `ShapeNodeModal`.
- Add a new editable field to `NodeVarInput` by updating Base TP node cache writes, Redux `ComputedNodeParameter`, non-base TP draft payloads, save merge logic, and backend `tpchanges` contract together.
- Change time-period merge rules by updating `NodeVarsTab`, `InfoTab`, `SpecsTab`, `nodeSettingsUtils.ts`, and backend translation expectations together.
- Change subnetwork wrapper editing by updating `tp-sync-utils.ts`, wrapper port filtering in Specs/NodeVars, and save-time mirror persistence.
- Change unit behavior by updating `convertToGivenUnit`, `NodeVarInput`, and manual unit conversion checks.

## Testing and Verification

Recommended source-level checks after code changes:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npm.cmd run build
```

Manual UI verification matrix:

| Scenario | Steps | Expected Visual Result | Expected State or Backend Handoff | Regression Risk |
| --- | --- | --- | --- | --- |
| Normal Base TP value edit | Open a normal node, go to Streams or Specs, edit a value, blur, then save. | Input keeps the edited value; required styling updates. | Node cache dirty entry updates, Redux `BASE_TP-{nodeId}-{portVarId}` updates, Save persists node model version. | Edits show in UI but are not saved. |
| Normal non-base TP edit | Select a non-base Time Period, edit value/spec/bounds/unit, then save. | Edited value remains while switching within the modal. | Redux `nodeParameters` updates and `tpChangesDraft` persists to `/api/data/tpchanges` on Save. | TP override is lost or written into Base TP. |
| Settings model version switch | In unverified normal node, switch base model version. | Model metadata changes and variables refresh. | Node cache receives new version and `refreshNodeParametersAfterModelVersionChange` rebuilds Base TP parameters. | Stale variables after model version switch. |
| Subnetwork wrapper ports | Open wrapper node Specs. | Port dropdown shows exposed ports only and displays wrapper notice. | Required/spec metadata can be resolved from mapped internal node data. | Hidden internal ports leak into wrapper UI. |
| Internal mapped ports | Enter subnetwork instance from Settings and inspect mapped internal node. | Mapped stream values can appear through parent proxy data; mapped locked ports remain consistent with canvas port rendering. | Parent connection and mirror draft logic connect internal edits to parent wrapper context on Save. | Internal edits fail to mirror or use wrong port location. |
| Incomplete stream edge plus modal | Create an incomplete stream edge, open connected node modal, then save. | Edge save validation highlights incomplete stream; modal values should not imply the stream is complete. | Save aborts before backend writes until edge stream selection is complete. | Node UI masks incomplete stream data. |
| Hidden variables | Use a port with `hidden_by_default` variables and toggle Show Hidden Variables. | Hidden rows appear gray/read-only; visible rows remain editable. | Hidden rows do not commit user edits. | Hidden fields become editable unintentionally. |
| Simulation spec guard | Set calc type to Simulation and open `NodeVarInput` spec dropdown. | Spec dropdown is disabled/gray. | Spec changes are blocked in input handler. | Users change specs in Simulation mode. |
| Unit conversion | Edit value after changing display unit. | Display value uses selected unit; committed base value is converted back. | Node cache and Redux store base-unit value plus selected unit. | Saved value uses display unit as base. |

## Known Cautions

- `NodeVarInput` writes both local display state and shared Redux/cache state. Avoid adding new writes that bypass `handleChange`.
- Base TP and non-base TP have different persistence paths. A fix for one path can leave the other stale.
- `getDisplayCachedNodeParameter` intentionally ignores Redux cache for non-base TP display; non-base tabs rely on merged TP data instead.
- `tpChangesDraft` persists only on Save. Closing the page before saving loses pending TP edits.
- `ShapeNodeModal` tab labels do not match internal tab ids exactly: `nodeVars` renders the visible `Streams` tab and `info` renders the visible `Node Variables` tab.
- Generated runtime artifacts are not the source of truth for modal behavior.

## Related Pages

- `docs/SetupInstructions/CodeExplanation/shape-node-and-ports.md`
- `docs/SetupInstructions/CodeExplanation/custom-edge-and-stream-selection.md`
