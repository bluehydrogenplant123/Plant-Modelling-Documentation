---
title: Custom Edge and Stream Selection Code Explanation
sidebar_position: 21
description: Explains how HyProNet custom edges render orthogonal stream connections, validate stream selection, and hydrate connected node data.
---

## Overview

The Custom Edge area replaces default React Flow edges with stream-aware edges. It renders orthogonal paths, labels or selectors, incomplete-stream highlighting, editable waypoints, and the stream-to-node hydration flow that updates connected node model versions and Redux node parameters.

Current behavior is implemented in `src/src/frontend/src/components/custom-edge/`. Legacy edge documentation is historical reference only.

## Source Files

- `src/src/frontend/src/components/custom-edge/index.tsx`: main custom edge renderer, orthogonal path state, stream selection callbacks, node-data hydration, and edge visual state.
- `src/src/frontend/src/components/custom-edge/edge-label-selector.tsx`: selected-edge editor for Content, Instance, Stream Database Name, and edge stream name.
- `src/src/frontend/src/components/custom-edge/edge-label.tsx`: static edge name label when the selector is hidden.
- `src/src/frontend/src/components/custom-edge/connection-line.tsx`: orthogonal preview line while the user is creating a connection.
- `src/src/frontend/src/components/custom-edge/orthogonal-routing.ts`: orthogonal route candidate generation, scoring, simplification, and grid snapping.
- `src/src/frontend/src/components/custom-edge/utils.ts`: helper that removes stream-generated component variables from a model version for one port.
- `src/src/frontend/src/components/custom-edge/custom-edge.css`: selector, static label, and waypoint handle styling.
- `src/src/frontend/src/utils/streamValidation.ts`: complete/incomplete stream predicates, power-stream styling predicate, and duplicate instance detection helper.
- `src/src/frontend/src/utils/modelVersionUtils.ts`: stream property sanitization, stream-to-port-var matching, component variable generation, and stream hydration guards.
- `src/src/frontend/src/utils/connection-utils.ts`: finds a local edge connected to a selected node/port.
- `src/src/frontend/src/features/node/nodeCacheService.ts`: loads and updates cached connected-node model versions.
- `src/src/frontend/src/features/node/nodeCacheSlice.ts`: backend node version fetch/save thunks and dirty state.
- `src/src/frontend/src/features/canvas/canvasSlice.ts`: `updateComputationResults` and canvas state merged by stream hydration.
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: save-time incomplete-stream guard, edge-data cleanup, node cache persistence, and TP draft persistence.
- `src/src/backend/routes/computeRoutes.ts`: compute-time validation and translation handoff after saved diagrams are loaded.

## Purpose and Responsibility

`CustomEdge` owns user-facing connection rendering and stream selection for one edge. It does not own domain stream definitions, database persistence by itself, or final solver translation. Domain streams come from Redux `domain.data.streams`; persistence happens through save utilities and backend data routes; compute reads saved diagrams and node cache records.

The component is responsible for keeping edge data, connected node cache entries, and Redux node parameter mirrors consistent enough for the next save and compute.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `EdgeProps<Edge<CustomEdgeData>>` | React Flow | Edge id, endpoints, handle ids, selected state, marker, current label, stream data, waypoints, and incomplete flags. |
| `domain.data.streams` | Redux domain state | Selector options and stream property source. |
| `canvas.verified` | Redux canvas state | Hides selector and waypoint handles when the diagram is verified. |
| `canvas.nodeParameters` | Redux canvas state | Existing values used while hydrating or clearing stream-owned node parameters. |
| `diagramId` | React Router params | Backend node load context and `updateComputationResults` payload metadata. |
| `nodeCache` | Redux node cache service | Loads and writes connected endpoints' `ModelVersion` data. |
| Source and target nodes | React Flow `getNode` | Canonical node id resolution, measured dimensions, and port positions. |

| Output | Destination | Notes |
| --- | --- | --- |
| Edge data updates | React Flow `setEdges` | Writes selected stream, `label`, `sourceHandle`, `targetHandle`, `waypoints`, `forceConfigOpen`, and `highlightIncomplete`. |
| Connected node data updates | React Flow `setNodes` | Removes old stream components and keeps `model.modelVersion` aligned with cache when available. |
| Model version updates | node cache | `updateModelVersionWithDomainStream` generates component variables and stream-derived defaults for connected ports. |
| Node parameter updates | Redux `canvas.nodeParameters` | `BASE_TP-{nodeId}-{portVarId}` entries are created or cleared for stream-derived values. |
| Saved status updates | Redux saved middleware and explicit `updateSaved(false)` | Stream selection, name edits, and waypoint edits mark the diagram unsaved. |

## Core State and Data Structures

- `CustomEdgeData.stream`: selected `Stream` or `null`. Complete stream selection requires either Content plus Instance or a Stream Database Name.
- `CustomEdgeData.sourceHandle` and `targetHandle`: numeric port locations stored as strings or numbers. They are preserved when changing stream labels.
- `CustomEdgeData.waypoints`: user-adjustable intermediate route points.
- `CustomEdgeData.controlPoints`: legacy route control points converted to waypoints when no `waypoints` array exists.
- `CustomEdgeData.forceConfigOpen`: transient UI flag that opens the selector for an incomplete edge.
- `CustomEdgeData.highlightIncomplete`: transient UI flag that renders a red incomplete edge during save validation.
- `Stream.properties`: sanitized before hydration so duplicate aliases such as matching `MF0`/`MFZ` style keys do not double-fill model variables.
- `Stream.stream_fractions`: source for generated component `_MF` and `_X` port variables.

## Main Components and Functions

- `CustomEdge(...)`: renders the SVG path, selector/static label, waypoint handles, and stream hydration callbacks.
- `getAbsolutePortPosition(node, portLocation)`: maps a numeric handle id to the rotated absolute canvas coordinate for a port.
- `setLabel(stream)`: clears previous node stream data, writes the selected stream into edge data, updates edge label and incomplete flags, marks connected nodes dirty, and hydrates node data when a stream is selected.
- `updateNodeData(stream)`: loads connected node model versions, removes old stream component vars, applies the selected domain stream to each connected endpoint, and dispatches Redux node parameter updates.
- `clearNodeData()`: removes generated component vars from each connected endpoint at the edge handles.
- `updateName(name)`: updates the current stream name nested under `edge.data.stream`.
- `updateWaypoints(nextWaypoints)`: simplifies and stores orthogonal waypoints in edge data.
- `EdgeLabelSelector(...)`: renders stream selection controls and validates duplicate names/instances.
- `isStreamSelectionComplete(stream)`: used for edge coloring, selector warnings, and save validation.
- `updateModelVersionWithDomainStream(...)`: generates component variables and fills only stream-owned non-human, non-required values.

## Rendered UI and Interaction Map

| UI State or Action | Source State or Props | Expected Result | State or API Effect |
| --- | --- | --- | --- |
| Edge has complete non-power stream | `isStreamSelectionComplete(stream) === true` | Black solid path with static name when not selected. | Edge data stores `stream` and `label`; node cache and Redux parameters are hydrated. |
| Edge has incomplete stream | Missing Content plus Instance and missing Stream Database Name | Orange dashed path; selector shows completion warning when selected. | Save later blocks and marks edge red through `highlightIncomplete`. |
| Save with incomplete custom edge | `save-util.tsx` calls `getIncompleteStreamEdges` | First incomplete edge is selected, red, and selector is forced open. | Save aborts before diagram or node backend writes. |
| Power stream | `isPowerStream(stream) === true` | Purple dashed path. | Same data flow as other complete streams. |
| Verified diagram | `canvas.verified === true` | Selector and waypoint handles are hidden; static label renders. | No stream edit can be made through this component. |
| Selected unverified edge | `selected === true` | Selector and segment drag handles render. | Edits update React Flow edge state and saved status. |
| Double-click selected edge path | unverified selected edge | New snapped waypoint appears at the nearest segment. | Edge `data.waypoints` updates and diagram becomes unsaved. |
| Drag segment handle | selected unverified edge | Orthogonal segment moves on grid. | Edge `data.waypoints` updates and diagram becomes unsaved on pointer up. |

## Component Contract

### `CustomEdge`

`CustomEdge` is a React Flow edge type. It expects `data.sourceHandle` and `data.targetHandle` to preserve port ids even when React Flow's top-level handle fields are missing or stale. `data.stream` may be `undefined`, `null`, or a `Stream`.

Important selectors and hooks:

- `useParams` supplies `diagramId`.
- `useSelector(state.canvas.verified)` controls editability.
- `useSelector(state.domain.data)` supplies stream options.
- `useSelector(state.canvas.nodeParameters)` supplies the mutable node parameter mirror.
- `useNodeCache()` loads and updates endpoint model versions.
- `useReactFlow()` supplies `getNode`, `getEdge`, `getEdges`, `setEdges`, `setNodes`, and `screenToFlowPosition`.

Cleanup and guards:

- Segment drag listeners are registered on `window` and removed on pointer up or pointer cancel.
- The waypoint orthogonalization effect exits when verified or when stored waypoints already exist.
- `ensureModelVersionLoaded` returns `null` if no node id is available or the backend/cache cannot provide a version.

### `EdgeLabelSelector`

Required props include edge id, label coordinates, current label, stream list, current stream, name, and callback functions for label/name/node-data changes.

The selector emits:

- `onLabelChange(undefined)` when Content changes, clearing stream selection.
- `onLabelChange(updatedStream)` when Instance or Stream Database Name changes.
- `updateName(newName)` while editing the stream name.
- `clearNodeData()` when the parent Content selection changes.
- `updateNodeData(updatedStream)` in several selection/name flows.

Current caution: selecting an instance or database id can call `updateNodeData` both through `onLabelChange` and directly from `EdgeLabelSelector`. The hydration path must stay idempotent.

## Data Flow

### Stream selection to edge data and node cache

1. The user selects a Content, Instance, or Stream Database Name in `EdgeLabelSelector`.
2. `EdgeLabelSelector` validates duplicate stream instances against other custom edges.
3. The selector creates `updatedStream` and calls `onLabelChange(updatedStream)`.
4. `CustomEdge.setLabel` sanitizes stream properties, calls `clearNodeData`, and writes `data.stream`, `label`, handles, and completion flags into the current edge.
5. `markConnectedNodesDirty` ensures source and target model versions are loaded and synchronized into node cache.
6. `updateNodeData` loads endpoint model versions, then iterates React Flow nodes.
7. For each endpoint at the matching handle, `deleteStreamComponent` removes previous generated component variables for that port.
8. `getConnectionInfo` confirms the current edge is the local edge attached to that node and selected port.
9. `updateModelVersionWithDomainStream` generates component `_MF` and `_X` vars from `stream_fractions` and fills stream-owned matching properties.
10. `syncCachedModelVersion` writes updated model versions under both React Flow id and canonical `model.node_id` when they differ.
11. `updateComputationResults` writes or clears `BASE_TP-{node.id}-{portVar.id}` entries in `canvas.nodeParameters`.
12. A later Save sends canvas edge data and node cache diffs/full payloads to backend data routes and then saves dirty node model versions.

### Incomplete stream validation

1. `isStreamSelectionComplete` returns true only when Content plus Instance exists or `stream_database_id` exists.
2. `CustomEdge` uses that result for black or orange edge styling.
3. `save-util.tsx` calls `getIncompleteStreamEdges(getEdges())` before building the save payload.
4. If any incomplete custom edge exists, save marks them red, sets `forceConfigOpen` on the first one, shows an alert, and aborts backend persistence.
5. `save-util.tsx` strips `forceConfigOpen` and `highlightIncomplete` from edge data before a successful save payload is built.

### Backend handoff after save and compute

1. Save builds a lightweight canvas that includes edge stream data.
2. Save gathers node cache data, merges compatible `canvas.nodeParameters`, and sends `nodeCacheDiffs` and `nodeCacheFull` in the diagram payload.
3. Save persists dirty node model versions through `nodeCache.saveAllNodeChanges`.
4. Compute later loads the saved diagram, expands subnetwork data, attaches saved model versions, validates duplicate stream instances, loads `tpChanges`, and calls `translation(...)`.
5. The final solver request is built from saved canvas edges, persisted node model versions, domain snapshot data, and TP overrides. `solve_request.json` is a runtime artifact and should not be used as authoring source.

## Side Effects

- Reads cached or backend model versions through `nodeCache.loadModelVersion`, which calls `GET /api/data/nodes/{nodeId}` with `diagramId` when supplied.
- Writes edge state through `setEdges`.
- Writes node state through `setNodes`.
- Writes node cache through `updateNodeValue`, marking model versions dirty by default.
- Dispatches `canvas/updateComputationResults` to merge node parameter updates.
- Dispatches `updateSaved(false)` through explicit calls and the store middleware.
- Uses `window` pointer listeners while dragging route segments.

## Error Handling and Edge Cases

- If no stream or no domain data exists, `updateNodeData` returns without changing nodes.
- If the selected stream is not found in `domainData.streams` or lacks `stream_fractions`, hydration returns early.
- If a connected endpoint model version cannot be loaded, that endpoint is skipped.
- If component templates `compname_MF` and `compname_X` are missing for the connected port, `updateModelVersionWithDomainStream` warns and returns the original model version.
- Required or human-input port variables are not populated from stream properties.
- Non-human, non-computed port variables may be cleared when a previously stored value no longer has a matching stream property.
- Duplicate stream instances are blocked in the selector UI and also checked by backend compute after subnetwork expansion.

## Port Mapping Cautions

- Custom edge hydration uses the edge source/target handle ids as port locations. Keep `sourceHandle`, `targetHandle`, `data.sourceHandle`, and `data.targetHandle` aligned.
- Rotated node path endpoints are calculated from `portLocationMap` and `model.rotationDirection`; changing port locations requires updating shape-node and custom-edge utilities together.
- Local `getConnectionInfo` only finds edges in the current React Flow graph. Internal subnetwork views may need parent proxy stream data handled by modal prefetch logic rather than by `CustomEdge` alone.
- Wrapper ports and internal mapped ports can share numeric locations. Use node id plus port location when applying node cache or TP changes.
- Save-time edge cleanup removes transient UI flags, not selected stream data.

## Extension Points

- Add a new edge visual state by updating `edgeStroke`, `edgeDash`, and the manual save validation expectations.
- Add a new stream completeness rule in `streamValidation.ts` and update `EdgeLabelSelector`, save validation, and compute validation docs together.
- Add a new stream property matching rule in `modelVersionUtils.ts`; verify both generated component vars and standard stream-owned variables.
- Change route behavior in `orthogonal-routing.ts` and verify stored waypoints, legacy `controlPoints`, double-click insert, and segment drag.
- Change subnetwork stream propagation by checking `CustomEdge`, modal `useNodeDataPrefetch`, `tp-sync-utils.ts`, and backend compute expansion together.

## Testing and Verification

Recommended source-level checks after code changes:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npm.cmd run build
```

Manual UI verification matrix:

| Scenario | Steps | Expected Visual Result | Expected State or Backend Handoff | Regression Risk |
| --- | --- | --- | --- | --- |
| Normal complete stream | Connect two normal node ports, select Content and Instance, enter a unique name, then deselect. | Edge is black with static label. | Edge data has `stream`, `label`, handles; connected node cache and `canvas.nodeParameters` contain stream-derived updates. | Stream selection does not hydrate endpoints. |
| Stream Database Name path | Select a Stream Database Name without using Content/Instance. | Completion warning disappears and edge becomes complete. | `isStreamSelectionComplete` accepts `stream_database_id`; save can proceed. | Database-name-only streams falsely blocked. |
| Incomplete stream | Connect ports and leave stream selection blank, then save. | Edge becomes red, first incomplete selector opens, alert explains incomplete stream selection. | Save aborts before `/api/data/diagrams` or node save calls. | Invalid stream edge persists. |
| Duplicate instance | Give two edges the same stream instance. | Selector shows duplicate instance error. | Backend compute also checks duplicate stream instances after expansion. | Duplicate stream instances reach solver translation. |
| Rotated normal nodes | Rotate source/target nodes and inspect edge endpoints. | Orthogonal path starts and ends at rotated handle positions. | Edge data remains on same handle ids. | Edge starts at old unrotated side. |
| Subnetwork wrapper port | Select a stream on an edge connected to a wrapper exposed port, then save. | Wrapper edge behaves like a complete custom edge. | Edge stream data saves in parent canvas; node cache merge preserves exposed-port propagation unless explicit human override exists. | Wrapper values overwritten by automatic merge. |
| Internal mapped port | Enter subnetwork instance with parent-connected stream and open node variables. | Edge may not exist locally, but modal stream display can still use parent proxy stream data. | Verify modal prefetch path rather than `CustomEdge` only. | Internal mapped variables appear disconnected. |
| Waypoint editing | Select edge, double-click path, then drag segment handle. | Waypoints remain orthogonal and snap to grid. | Edge `data.waypoints` updates and diagram becomes unsaved. | Route saves diagonal or jittery points. |

## Known Cautions

- `EdgeLabelSelector` can call `updateNodeData` more than once for one user selection. Keep stream hydration idempotent.
- Stream selection should not fill required/user-table fields. `shouldPopulatePortVarFromStream` blocks `required` and `is_human_input` rows.
- `sanitizeStreamPropertiesForHydration` removes duplicate alias keys only when the canonical and alias values match.
- Generated stream component variables depend on `compname_MF` and `compname_X` templates at the connected port.
- The source currently contains diagnostic `fetch('http://127.0.0.1:7242/ingest/...')` calls in some paths. Do not treat diagnostic side channels as app contracts.
- Do not hand-edit `src/src/backend/services/solve_request.json` to explain edge behavior.

## Related Pages

- `docs/SetupInstructions/CodeExplanation/shape-node-and-ports.md`
- `docs/SetupInstructions/CodeExplanation/node-modal-and-variable-inputs.md`
