---
title: Large Model Performance and Recovery
sidebar_position: 12
description: Explains how the canvas limits work during movement, loads detailed node data on demand, narrows panel subscriptions, and recovers legacy model versions.
---

## Overview

Large diagrams can contain many nodes, edges, handles, labels, and cached model variables. The current frontend reduces the amount of work performed while the viewport moves, when a feature panel is closed, and when a diagram first opens. It also provides a guarded recovery path for older node records whose saved model version is incomplete.

These optimizations cover browser rendering and frontend data loading. They do not measure solver speed or guarantee a fixed maximum diagram size.

## Source Files

- `src/src/frontend/src/App.tsx`: tracks viewport movement, suppresses movement-only UI, and loads a diagram without embedding every node model version in the canvas.
- `src/src/frontend/src/react-flow.css`: hides expensive canvas details while the viewport is moving.
- `src/src/frontend/src/utils/viewportMovementTracker.ts`: normalizes XYFlow move start, move, and move end events with a fallback timer.
- `src/src/frontend/src/utils/flowPanelSubscriptionUtils.ts`: prevents closed panels from subscribing to full React Flow node and edge arrays.
- `src/src/frontend/src/components/shape-node/index.tsx`: subscribes each rendered node only to its own node-cache entry.
- `src/src/frontend/src/features/node/nodeCacheService.ts`: loads, caches, updates, and persists model versions outside the lightweight canvas record.
- `src/src/frontend/src/components/modal/useNodeDataPrefetch.ts`: loads TP changes and builds detailed node values when the node settings workflow needs them.
- `src/src/frontend/src/utils/modelVersionUtils.ts`: validates and recovers incomplete legacy model versions.
- `src/src/frontend/src/components/custom-edge/index.tsx`: loads or recovers endpoint model versions before stream-component updates.
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: saves only the required node-cache data and recovers an unusable dirty-node version before persistence.

## Purpose and Responsibility

This code keeps canvas interaction responsive without removing model information. It separates lightweight graph rendering from detailed model-version data, narrows subscriptions to the UI that is currently open, and temporarily removes nonessential visual work during viewport movement.

It does not change solver request semantics. Save and compute paths still require a usable model version and must preserve human-entered values.

## Performance Controls

| Control | Trigger | Current behavior |
| --- | --- | --- |
| Viewport movement mode | Pan, zoom, or scroll movement | Adds `react-flow--moving`, disables node pointer events, hides handles, fixed labels, rotation dots, and the minimap, and does not render the port tooltip. |
| Movement fallback | XYFlow omits a move-end event | `createViewportMovementTracker(...)` clears movement mode after 200 ms without another move event. |
| Per-node cache subscription | One node model version changes | `ShapeNode` reads only that node's cache entry instead of making every node react to the full cache. |
| Closed-panel subscription guard | Equation Writing or Plant Measurements is closed | The panel selector returns a stable empty array instead of subscribing to all current flow items. |
| Lightweight initial diagram load | An existing diagram opens | The canvas loads basic graph and node identity data first; node model versions stay in the separate cache path. |
| On-demand detailed loading | A node modal, stream update, or open feature panel needs model data | The relevant path loads the required model version and TP changes rather than expanding all node details during initial render. |

## Main Functions and Components

- `createViewportMovementTracker(onMovingChange, fallbackDelayMs)`: emits movement state only when it changes, refreshes the fallback timer on every move, and cleans up the timer on disposal.
- `selectFlowItemsWhenPanelOpen(items, isPanelOpen)`: returns the current flow array only while the panel is open; otherwise it returns one stable empty array.
- `useNodeCacheEntry(nodeId)`: gives `ShapeNode` a node-specific cache subscription and update function.
- `useNodeDataPrefetch(...)`: loads TP changes for the active node, combines local and parent-proxy edges, builds time-period model versions, and updates the node parameter state needed by the modal.
- `isUsableModelVersion(value)`: accepts only object values with a `ports_var` array.
- `recoverModelVersionFromDomain(...)`: keeps a usable version unchanged; otherwise it selects the preferred, default, or first domain version and initializes it for the current calculation type and connections.

## Data Flow

### Viewport movement

1. XYFlow calls `onMoveStart`, `onMove`, and `onMoveEnd` in `App.tsx`.
2. `viewportMovementTracker` updates `isViewportMoving` and maintains the fallback timer.
3. `App.tsx` applies `react-flow--moving` and omits the port tooltip while movement is active.
4. `react-flow.css` hides nonessential details and disables node pointer events.
5. A real move-end event, or the fallback timer, restores the normal canvas.

### Detailed node data

1. The diagram route loads the saved canvas and basic node identities.
2. Detailed model versions remain in `nodeCacheService` rather than inside every React Flow node.
3. A node modal or edge workflow requests the model version it needs.
4. The cache returns a usable version or loads it from the backend.
5. Modal prefetch loads TP changes only for the active node and builds the visible time-period values.

### Legacy recovery

1. An edge or save path receives a missing or malformed model version.
2. `recoverModelVersionFromDomain(...)` selects the matching preferred version, the domain default, or the first usable domain version.
3. `initModelVersionWithCalcType(...)` rebuilds the node-specific version using the current calculation type and connected streams.
4. The recovered version is placed in the cache and the original operation continues.
5. If no usable domain version exists, the operation stops instead of saving incomplete node data.

## Side Effects

- Viewport movement changes only temporary render state; it does not change graph data.
- Opening a detailed node workflow can fetch TP changes and populate Redux node parameters.
- Recovery can add a rebuilt version to the node cache before an edge update or save.
- Save still uses dirty-node tracking and narrow node-cache payloads; these performance protections must remain intact.

## Error Handling and Edge Cases

- The movement tracker uses a fallback because a single-wheel XYFlow path can omit `onMoveEnd`.
- Closing or unmounting the canvas disposes the tracker timer.
- Closed panels receive a stable empty array, so they do not recompute against changing graph arrays.
- A valid cached model version is never replaced by the recovery helper.
- If neither the cache nor the domain catalog provides a usable model version, edge hydration returns no update and save reports that the node has no usable model version.
- A saved snapshot without usable palette models falls back to fresh domain data when the diagram has a resolvable domain id.

## Extension Points

- Add another movement-only visual suppression in `react-flow.css` under `.react-flow--moving`; do not hide data that must remain interactive after movement ends.
- Use `selectFlowItemsWhenPanelOpen(...)` for another modal only when an explicit open state exists and a stable empty array is safe for the closed state.
- Keep node rendering subscribed through `useNodeCacheEntry(...)`; a whole-cache selector can make one node update rerender the full diagram.
- Extend legacy recovery in `modelVersionUtils.ts`, then verify the edge and save callers together.

## Testing and Verification

Terminal: **PowerShell**

Working directory:

```text
HYPRONET-GUI/src/
```

Run the existing recovery regression test:

```powershell
.\node_modules\.bin\jest.cmd tests/frontend/modelVersionRecovery.test.ts --runInBand --coverage=false
```

Run the application build:

```powershell
npm.cmd run build
```

Manual verification:

| Scenario | Action | Expected result |
| --- | --- | --- |
| Large canvas movement | Pan and zoom a diagram with many nodes and edges. | Handles, fixed labels, rotation dots, minimap, and port tooltip are suppressed only during movement and return afterward. |
| Closed feature panels | Keep Equation Writing and Plant Measurements closed while moving or editing nodes. | The panels remain closed and do not react to graph-array changes. |
| Lazy node details | Open a saved diagram, then open one node. | The canvas appears before all node details are expanded; the selected node's values load when required. |
| Legacy node version | Open and save a diagram containing an incomplete legacy model version. | A usable domain version is recovered, or save stops with a clear missing-version failure. |

## Known Cautions

- Do not reattach full model versions to every canvas node. The lightweight canvas and node cache are deliberate performance boundaries.
- Do not broaden dirty-node save payloads to every cached node; that would regress the fast-save path.
- The CSS movement mode is temporary. Leaving the class active would make handles and controls appear missing.
- Recovery must preserve an already valid cached version and human-entered split or input values.
- Performance claims should be verified with a representative saved diagram. This page documents the mechanisms, not a fixed timing result.

## Related Pages

- [Dashboard and Canvas Code Explanation](./dashboard-and-canvas.md)
- [Node Modal and Variable Inputs Code Explanation](./node-modal-and-variable-inputs.md)
- [Save Diagram and Node Cache Code Explanation](./save-diagram-and-node-cache.md)
- [Custom Edge and Stream Selection Code Explanation](./custom-edge-and-stream-selection.md)
