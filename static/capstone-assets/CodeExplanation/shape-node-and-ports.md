---
title: Shape Node and Ports Code Explanation
sidebar_position: 23
description: Explains how HyProNet shape nodes render, resolve ports, handle rotation, and hand node edits to modal, Redux, node cache, and save flows.
---

## Overview

The Shape Node area is the React Flow node renderer for model and subnetwork nodes on the canvas. `shape-node/index.tsx` renders the node body, the node toolbar modal, the React Flow resizer, rotation control, and the port handles used by custom edges.

This page documents current frontend behavior. Legacy CodeExplanation pages are useful for topic coverage only; the contracts below come from the current source files.

## Source Files

- `src/src/frontend/src/components/shape-node/index.tsx`: main React Flow node component, port source resolution, rotation, completion coloring, and modal callback wiring.
- `src/src/frontend/src/components/shape-node/port-handles.tsx`: converts `Port` records into positioned `PortHandle` children, derives subnetwork connection state, and fetches internal node names for wrapper tooltips.
- `src/src/frontend/src/components/shape-node/port-handle.tsx`: renders one React Flow `Handle`, decides source or target direction, lock state, connection color, tooltip text, and connectability.
- `src/src/frontend/src/components/shape-node/utils.ts`: static port coordinate maps, rotation helpers, React Flow handle bounds helper, and side-position calculation.
- `src/src/frontend/src/components/shape-node/rotation-button.tsx`: draggable rotation dot that snaps rotation to 90 degree quadrants.
- `src/src/frontend/src/components/shape-node/label.tsx`: standalone text input component for node labels. It is not the main label path in `ShapeNode`, which renders names through `Shape`.
- `src/src/frontend/src/components/shape-node/shape-node.css`: node label and port/error text styling.
- `src/src/frontend/src/components/shape-node/rotation-button.css`: rotation dot visual states.
- `src/src/frontend/src/components/modal/index.tsx`: `ShapeNodeModal` receives node edit callbacks from `ShapeNode`.
- `src/src/frontend/src/features/node/nodeCacheService.ts`: hook used by `ShapeNode` to read and update cached `ModelVersion` data.
- `src/src/frontend/src/features/node/nodeCacheSlice.ts`: Redux cache state, dirty tracking, and backend node save/load thunks.
- `src/src/frontend/src/features/domain/domainSelectors.ts`: `selectDomainModelMap`, used to resolve domain model ports and SVG shape data.
- `src/src/frontend/src/features/canvas/canvasSlice.ts`: node rotation, parent connection, node name, and node parameter Redux state.
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: later save handoff for canvas data, node cache diffs/full payloads, and incomplete-stream validation.

## Purpose and Responsibility

`ShapeNode` owns the canvas presentation and immediate React Flow state updates for a node. It does not own domain model definitions, backend node persistence, stream selection, or time-period persistence. Those are delegated to domain Redux state, `useNodeCache`, modal tabs, and the save flow.

The port rendering responsibility is split:

- `ShapeNode` resolves which `Port[]` to render.
- `PortHandles` maps each port to a rotated coordinate and connection state.
- `PortHandle` renders the actual React Flow handle and enforces connectability.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `id`, `selected`, `data` | React Flow `NodeProps<ShapeNode>` | Identifies the node, controls resizer/rotation visibility, and provides `data.model`, `data.color`, and `data.type`. |
| `data.model.node_id` | saved node model data | Preferred canonical node id for node cache lookups when present. |
| `data.model.portsMapping` | saved wrapper or legacy node data | Builds external wrapper ports and reconstructs ports when domain/cache port data is unavailable. |
| `domainModelMap.get(model.id)` | Redux `domain.data.models` through `selectDomainModelMap` | Supplies authoritative domain ports and SVG shape data when available. |
| `nodeCache.modelVersions[canonicalNodeId]` | Redux node cache through `useNodeCache` | Supplies `ports_var` for port fallback and required-value completion checks. |
| `canvas.parentConnections` | Redux canvas state | Marks wrapper/internal ports as connected or locked in subnetwork instance editors. |
| `calcType.type` | Redux calc type state | Decides which `PortVarObject` field makes a variable required. |

| Output | Destination | Notes |
| --- | --- | --- |
| React Flow node data updates | `setNodes` | Rotation, selected time period, model field edits, and calculated `model.complete` are written into the in-memory canvas node. |
| React Flow edge data updates | `setEdges` | Rotation touches connected edges with `updatedAt` to force path recalculation. |
| `setNodeRotation({ nodeId, rotation })` | `canvas.nodeRotations` | Stores snapped rotation direction in Redux. |
| `updateNodeValue(canonicalNodeId, modelVersion)` | node cache | Base TP variable edits and calcType-required synchronization mark cached model versions dirty by default. |
| `ShapeNodeModal` callbacks | modal tabs | User edits flow from modal rows back into `ShapeNode` callbacks. |

## Core State and Data Structures

- `canonicalNodeId`: `model.node_id` when present, otherwise the React Flow `id`. Cache reads and writes should use this id to avoid splitting a node across cache keys.
- `baseModelVersion`: cached `ModelVersion` from `useNodeCache`. It is the source for `ports_var` fallback and completion checking.
- `portsFromMapping`: ports reconstructed from `model.portsMapping`, including nested `mapped` entries.
- `portsFromCache`: ports reconstructed from `baseModelVersion.ports_var` and merged with `portsFromMapping` by `port_location`.
- `resolvedPorts`: final render input. Current precedence is domain model ports first, then cache ports, then mapping ports. Mapping names can override domain port names by matching `port_location`.
- `parentConnections`: normalized from Redux. Empty connection objects become `undefined` before passing to port rendering.
- `filledComplete`: calculated from required port vars and `base_unit_default_value`; `null` means the cache was unavailable and `model.complete` is used.

## Main Components and Functions

- `ShapeNode(...)`: top-level React Flow node renderer. It resolves ports, renders the shape, attaches modal and ports, and coordinates rotation and completion state.
- `useNodeDimensions(id)`: reads React Flow internal measurements so the shape, ports, and rotation button align to the measured node size.
- `onRotate(newRotation)`: snaps degrees to `rotationDirection` 0 through 3, updates the node model, refreshes connected edges, dispatches `setNodeRotation`, and calls `updateNodeInternals`.
- `onModelFieldChange(field, value)`: writes a top-level `Model` field into the React Flow node model.
- `onNodeVarFieldChange(portsVarId, timePeriodId, field, value)`: for `BASE_TP`, updates the cached `ModelVersion` port variable. Non-base TP edits are delegated to modal tabs and do not get written here.
- `PortHandles(...)`: positions each port with `portLocationMap`, `rotatePoint`, node dimensions, and `rotationDirection`.
- `PortHandle(...)`: renders one `Handle`, resolves locked/mapped state, tooltip text, border color, and source/target connectability.
- `getHandleBounds(node)`: computes React Flow handle bounds from `model.portsMapping`; it does not currently reconstruct bounds from `domainModel.ports`.

## Rendered UI and Interaction Map

| UI State or Action | Source State or Props | Expected Result | State or API Effect |
| --- | --- | --- | --- |
| Normal node renders | `domainModel.ports`, node dimensions, `model.rotationDirection` | Shape appears with domain SVG and rotated port handles. | No backend call. |
| Node is selected | `selected === true` | `NodeResizer` and rotation dot are visible. | Resize is handled by React Flow; rotation uses `onRotate`. |
| Mouse hovers node | `isHovered` local state | Rotation dot is visible while hovered. | No backend call. |
| User drags rotation dot | `RotationButton.onRotate` | Shape and ports snap to 0, 90, 180, or 270 degrees; connected edge paths refresh. | `setNodes`, `setEdges`, `setNodeRotation`, and `updateNodeInternals`. |
| Required variable has no value | cached `ports_var`, `calcType` | Shape stroke becomes red and gets a light red overlay. | `model.complete` is written back into React Flow node data when calculable. |
| Port is connected or mapped locked | `isConnected` or `isMappedInternalPort` | Handle background is gray. | No backend call. |
| Port is unconnected and unlocked | port metadata | Handle background is white with class-colored border. | No backend call. |

## Component Contract

### `ShapeNode`

Required inputs are React Flow `NodeProps<ShapeNode>`. `data.model` must be a `Model` shape with `id`, `model_name`, `rotationDirection`, and optionally `node_id`, `node_name`, `ports`, `portsMapping`, `diagramId`, and `complete`.

Important child props:

- `ShapeNodeModal`: receives `model`, `nodeId`, `onNodeVarFieldChange`, `onSelectTimePeriod`, and `onModelFieldChange`. The modal owns tab UI and calls back when the user edits values.
- `Shape`: receives shape type, dimensions, display name, fill/stroke state, domain SVG, rotation, node id, and React Flow setters.
- `PortHandles`: receives `resolvedPorts`, rotation direction, measured node size, `model`, `nodeId`, and normalized `parentConnections`.
- `RotationButton`: receives `onRotate`, current rotation in degrees, and measured dimensions.

Hook dependencies that matter:

- `updateNodeInternals` runs when `rotation` changes.
- Port resolution uses `useMemo` for `portsFromMapping`, `portsFromCache`, and `resolvedPorts`.
- Completion status writes back to node data when `filledComplete` becomes known and differs from `model.complete`.
- `useEffectDebugger("SyncCalcTypeToPortVars", ...)` updates cached `required` and `spec` fields when calc type changes.

### `PortHandles`

`PortHandles` expects a `Port[]`, a rotation direction, measured node width/height, and optional model/subnetwork context. It derives `portsMapping` from `model.portsMapping`, fetches internal node names with `GET /api/data/diagrams/{diagramId}` only when a wrapper model has mapping data, and cleans up the async name-load effect with an `isActive` flag.

### `PortHandle`

`PortHandle` receives one normalized port plus mapping context. It sets:

- `Handle.type` to `target` when `portType % 2 !== 0`, otherwise `source`.
- `Handle.id` to `String(portLocation)`.
- `isConnectableStart` to false for locked ports and inlet ports (`portType === 1`).
- `isConnectableEnd` to false for locked ports and outlet ports (`portType === 2`).

## Data Flow

### Port rendering

1. `ShapeNode` receives a React Flow node with `data.model`.
2. It resolves `canonicalNodeId` from `model.node_id` or `id`.
3. It reads the cached model version with `getCachedModelVersion(canonicalNodeId)`.
4. It builds `portsFromMapping` from `model.portsMapping`, accepting both direct records and nested `mapped` records.
5. It builds `portsFromCache` from `baseModelVersion.ports_var`, keyed by `port_location`, and merges mapping names/classes when present.
6. It builds `resolvedPorts`: domain model ports win when present, cache ports are next, mapping ports are last.
7. `PortHandles` converts each port's location to node-local coordinates, rotates around the node center, and passes the result to `PortHandle`.
8. `PortHandle` renders the React Flow handle, tooltip, source/target direction, class border color, and connection/locked state.

### Node variable edit to persistence handoff

1. The user edits a value in a modal tab.
2. `ShapeNodeModal` normalizes the event and calls `ShapeNode.onNodeVarFieldChange`.
3. For `BASE_TP`, `ShapeNode` updates the cached model version and calls `updateNodeValue(canonicalNodeId, updatedModelVersion)`.
4. `nodeCacheSlice.updateModelVersion` marks that node dirty and stores the original version for later diffing.
5. `save-util.tsx` later gathers dirty node cache entries, merges compatible Redux `canvas.nodeParameters`, sends diagram payloads with `nodeCacheDiffs` and `nodeCacheFull`, then calls `saveAllNodeChanges`.
6. `nodeCacheSlice.saveAllChanges` persists dirty node model versions to `/api/data/nodes/{nodeId}` or creates nodes through `/api/data/nodes`.

### Rotation and canvas handoff

1. The user drags the rotation dot.
2. `RotationButton` maps pointer quadrant to a snapped rotation.
3. `ShapeNode.onRotate` updates `model.rotationDirection` in React Flow node data.
4. It updates connected edge data with `updatedAt` so custom edges rerender with new handle positions.
5. It dispatches `setNodeRotation`; the full canvas is later included in the diagram save payload.

## Side Effects

- `PortHandles` may call `GET /api/data/diagrams/{diagramId}` to resolve wrapper tooltip names.
- `ShapeNode` writes React Flow node and edge state through `setNodes` and `setEdges`.
- `ShapeNode` writes Redux node cache through `updateNodeValue`, which marks nodes dirty unless `markDirty: false` is passed.
- `ShapeNode` writes `canvas.nodeRotations` with `setNodeRotation`.
- `ShapeNodeModal` opens inside React Flow `NodeToolbar`; edits are not persisted to backend immediately unless a child tab explicitly calls an API. Base model-version persistence happens on Save.

## Error Handling and Edge Cases

- If `portsMapping` is missing or malformed, mapping-derived ports are ignored.
- If `baseModelVersion` is unavailable, cache-derived ports are skipped and completion state falls back to saved `model.complete`.
- If a port location is not in `portLocationMap`, `PortHandles` returns `null` for that port.
- If a mapping entry has a non-numeric external key, `ShapeNode` skips it.
- If `PortHandles` fails to fetch internal node names, it clears `internalNodeNameById` and still renders ports.
- If a required value is `null`, `undefined`, empty string, or non-finite number, completion treats it as missing.

## Port Mapping Cautions

- `portsMapping` keys are external wrapper port locations. The value may be a direct mapping or may contain a nested `mapped` record. Current code supports both.
- Do not assume `port_location` alone uniquely identifies a mapped internal port. `PortHandle` locks a mapped internal port only after matching node id, port location, optional port type, and optional port class.
- Wrapper-node ports and internal mapped ports use different connection signals. Wrapper nodes use `portsMapping` or `parentConnections.externalPorts`; internal nodes use `parentConnections.externalPorts[*].mapped`.
- The visible port class color is the border color in `PortHandle`, not the fill. Unconnected unlocked handles have `backgroundColor: 'white'`; connected or locked handles have gray background.
- The border color map is hardcoded for `MES`, `ELF`, and `Q` inlet/outlet keys plus `info`. For `portType === 1` or `portType === 2`, an unknown `port_class` produces no mapped border color; `colors.info` is used only when `portType` is neither `1` nor `2`.
- `getHandleBounds` currently reconstructs handles from `model.portsMapping`. If connection behavior differs between normal domain ports and wrapper ports, check both `resolvedPorts` rendering and the static bounds helper.
- Saved diagrams can omit embedded `ports` or `portsMapping`. In that case, current rendering depends on domain data and the node cache path.

## Extension Points

- Add a new port color by updating the `colors` map in `port-handle.tsx` and manually checking connected, unconnected, inlet, outlet, and info ports.
- Change port placement by updating `portLocationMap`, `getPortPosition`, and `getHandleBounds` together.
- Change completion coloring by updating the `filledComplete` logic in `shape-node/index.tsx` and verifying required fields across calc types.
- Change subnetwork port mapping by updating `PortHandles`, `PortHandle`, and modal `tp-sync-utils.ts` together. Wrapper and internal editors must stay consistent.
- Change node edit persistence by checking `ShapeNodeModal`, `nodeCacheService`, `nodeCacheSlice`, and `save-util.tsx` together.

## Testing and Verification

Recommended source-level checks after code changes:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npm.cmd run build
```

Manual UI verification matrix:

| Scenario | Steps | Expected Visual Result | Expected State or Backend Handoff | Regression Risk |
| --- | --- | --- | --- | --- |
| Normal node ports | Open a normal diagram node with domain ports. Rotate it through all four quadrants. | Ports stay attached to the correct sides, edge paths recalculate, and tooltips show port name/class. | React Flow node `model.rotationDirection` and Redux `nodeRotations` update; no immediate backend call. | Port coordinate regressions, stale edges. |
| Required missing value | Use a calc type where a visible port variable is required and clear its value. | Node outline/overlay turns red and the modal input shows required styling. | Cached model version and `model.complete` update; Save later sends node cache diff/full payload. | False complete status, missed required field. |
| Subnetwork wrapper ports | Select a wrapper node with `portsMapping`. Hover external ports. | External tooltip shows external and internal mapping lines; only exposed wrapper ports render. | `PortHandles` may fetch the instance diagram to resolve internal node names. | Wrong external/internal labels, missing wrapper handles. |
| Internal mapped ports | Enter a subnetwork instance diagram and inspect the mapped internal node port. | Exact mapped internal port is gray/locked and tooltip includes external port status. | Lock is derived from `canvas.parentConnections`; no immediate backend call. | Over-locking unrelated nodes at same `port_location`. |
| Unknown port class | Render an inlet or outlet port class not in the hardcoded color map. | Handle still renders, but the inlet/outlet border may have no mapped class color. Only non-1/2 port types use the `info` color. | No backend call. | New imported port class appears uncolored or misleading. |
| Incomplete stream connected to port | Connect an edge but leave stream selection incomplete, then save. | Save flow highlights incomplete edge red and opens the first selector. | `save-util.tsx` blocks save before backend write. | Users save diagrams with incomplete stream edge data. |

## Known Cautions

- `ShapeNode` contains console debug effects for domain model and parent connections. Do not treat console output as the source of truth for documentation.
- Base TP edits are dirty-node cached; non-base TP edits are primarily handled by modal tabs through `tpChangesDraft`.
- The node cache can be keyed by both React Flow id and canonical `model.node_id`. New logic must preserve the canonical-id fallback.
- Generated runtime files, including `src/src/backend/services/solve_request.json`, are not source documentation for this area.

## Related Pages

- `docs/CodeExplanation/custom-edge-and-stream-selection.md`
- `docs/CodeExplanation/node-modal-and-variable-inputs.md`
