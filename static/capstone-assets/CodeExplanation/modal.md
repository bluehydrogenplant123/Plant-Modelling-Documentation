# Shape Node Modal

## Overview
- Location: `src/src/frontend/src/components/modal/index.tsx`
- Purpose: Provides the node-level modal used in React Flow to edit model metadata, stream variables, info, and specs for a selected node.
- UI: Renders inside `@xyflow/react` `NodeToolbar`, with tabbed content controlled by `ModalHeader`.

## Props (inputs/outputs)
- `model: Model` — required; current model bound to the node.
- `onModelFieldChange(field: keyof Model, value: Model[K]) => void` — required; no return, pushes top-level model edits upward.
- `onNodeVarFieldChange(portsVarId: string, timePeriodId: string | undefined, field: keyof PortVarObject, value: PortVarObject[K]) => void` — required; no return, propagates variable edits with time-period context.
- `onSelectTimePeriod(timePeriodId?: string) => void` — optional id; no return, parent can load different versions.
- `nodeId: string` — required; React Flow node id for cache lookups.

## Core Functions
- `handleTabChange(tab)` — param: tab union; return: void; updates `activeTab` to show the right tab component.
- `updateTimePeriodPortVar({ model, timePeriodId, portVarId, newValue })` — params: `Model`, target time period id, variable id, numeric value; return: void; mutates the matching port var inside the selected time period in memory (currently uses `BASE_TP` placeholder).
- `handleVarChange(portsVarId, key, event)` — params: variable id, model var key, input/select event; return: void; normalizes number/string, updates cached modelVersion when editing `base_unit_default_value`, calls `onNodeVarFieldChange`, and syncs node cache for downstream consumers.
- `handlePortChange(event)` — param: select change; return: void; sets `selectedPort` for Node Vars tab (defaults from Redux domain model).
- `nodeCache.getCachedModelVersion(nodeId)` — used to seed and update cached versions; edits are persisted via `nodeCache.updateNodeValue`.

## Tabs (files in `modal/tabs`)
- `settings-tab.tsx`
  - Props: `model`, `onModelFieldChange(field,value)`, `nameChangeSummaries`, `onSelectTimePeriod`, `reactFlowNodeId`.
  - Core: loads/syncs modelVersion via `useNodeCache`; validates unique node names (Redux `nodeNames` + `modelNameMap`); allows base model version switch with `initModelVersionWithCalcType` and refreshes node parameters via `refreshNodeParametersAfterModelVersionChange`; supports “Go to Subnetwork” save-and-navigate using `useSaveDiagram`; shows model version metadata; blocks edits when verified.
  - Returns JSX only; side effects update Redux (names, nodes, nodeParameters) and node cache.
- `node-vars-tab.tsx`
  - Props: `model`, `handleChange(portsVarId,key,event)`, `handlePortChange`, `selectedPort`, `reactFlowNodeId`, `onModelFieldChange`.
  - Core: merges port variables per time period from snapshot/domain/streams (`initModelVersionWithCalcType`) and tpchanges (REST). Handles stream mode (shows stream fractions), time-period selection and splitting, port selection, and TP-specific writes via `handleChangeWithTpLogic` (posts/puts/deletes tpchanges, then rebuilds merged ports). Uses `NodeVarInput` for numeric/spec/unit edits and propagates to Redux/node cache.
  - Outputs JSX; side effects: tpchanges API, Redux `nodeParameters`, node cache updates.
- `info-tab.tsx`
  - Props: `model`, `handleChange`, `nodeId`.
  - Core: targets the info port (`port_type=0`), loads cached modelVersion if missing, overlays Redux overrides per composite key (`tpid-nodeId-portVarId`), and renders `NodeVarInput` rows with width sizing. Uses time period selection from `model.defaultTimePeriodId`.
  - Returns JSX only; mutations flow through `handleChange`.
- `specs-tab.tsx`
  - Props: `model`, `handleChange`, `reactFlowNodeId`.
  - Core: filters required vars from cached modelVersion (or TP model_version), overlays Redux overrides for BASE_TP, and renders `NodeVarInput` with width heuristics. Time-period label shown; scroll wheel suppressed in container.
  - Returns JSX; mutations handled via `handleChange` → parent.
- `node-var-input.tsx`
  - Props: detailed numeric/spec/unit editors (`portVarId`, bounds, dimension, units, spec, flags, `node_id`, `tpid`, etc.).
  - Core: manages display vs stored values, converts units with `convertToGivenUnit`, syncs Redux `nodeParameters` and node cache on blur/change, updates specs dropdown (F/V/P/I), and prevents accidental scroll/arrow increments. Uses `updateComputationResults` and `updateSaved` for Redux writes.
  - Calc Type: when `calcType === 'Simulation'`, spec edits are disabled to keep Simulation mode read-only for spec flags.
  - Input origin flags: any user edit forces `is_human_input = true` and `is_computed = false`; computed highlighting only applies when `is_human_input = false`.
  - Returns a row of inputs/selects; no explicit return data.

## Key Behavior
- User edits always flip `is_human_input = true` and clear `is_computed`; solver results only highlight non-human inputs. See `docs/CodeExplanation/human-input-flag.md`.
- Manages `activeTab` (`settings` | `nodeVars` | `info` | `specs`) and routes renders to `SettingsTab`, `NodeVarsTab`, `InfoTab`, or `SpecsTab`.
- Uses `ModalHeader` for tab buttons; selection is lifted to parent via `onTabChange`.
- Lazily pulls cached model versions via `useNodeCache`; updates are written back to cache to keep the canvas state consistent.
- `handleVarChange` normalizes number/string input, forwards updates to `onNodeVarFieldChange`, and mutates cached model versions when editing `base_unit_default_value`.
- Time-period mutations currently assume a placeholder id `BASE_TP` (see `updateTimePeriodPortVar`); adjust when multi-time-period editing is wired.
- Port selection for the Node Vars tab is tracked with `selectedPort` and uses domain data from Redux (`selectDomainModelMap`) to seed defaults.

## Usage
```tsx
<NodeToolbar className="nodrag" offset={32}>
  <ShapeNodeModal
    model={model}
    nodeId={node.id}
    onModelFieldChange={handleModelChange}
    onNodeVarFieldChange={handleVarChangeWithTP}
    onSelectTimePeriod={setActiveTimePeriod}
  />
</NodeToolbar>
```

## Notes
- `nameChangeSummaries` is tracked via `useRef` for auditing name edits in `SettingsTab`.
- When integrating multi-time-period support, replace the hard-coded `BASE_TP` usages with the actual selected time period id.
- Styling is defined in `modal.css` and `ShapeNodeModal.css`.
