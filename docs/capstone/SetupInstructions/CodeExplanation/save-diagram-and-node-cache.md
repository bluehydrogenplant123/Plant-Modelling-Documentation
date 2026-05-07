---
title: Save Diagram and Node Cache Code Explanation
sidebar_position: 20
description: Explains how diagram save, dirty-node persistence, node cache diffs, canonical node ID remapping, and save metadata work.
---

## Overview

The save workflow persists the React Flow canvas, diagram metadata, subnetwork instance references, and dirty node `modelVersion` data. The main frontend entry point is `useSaveDiagram` in `src/src/frontend/src/components/header-bar/utils/save-util.tsx`; the main backend entry points are `POST /api/data/diagrams`, `PUT /api/data/diagrams/:diagramId`, and the node routes in `src/src/backend/routes/dataRoutes.ts`.

This page documents the current source behavior. Legacy CodeExplanation pages were used only as a density reference.

## Source Files

- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: builds the save payload, sends the diagram save request, saves dirty node cache entries, handles canonical node ID replacements, and writes save metadata.
- `src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx`: renders the Save button and persists the auto-reload preference.
- `src/src/frontend/src/features/node/nodeCacheService.ts`: exposes the hook wrapper around node cache selectors and thunks.
- `src/src/frontend/src/features/node/nodeCacheSlice.ts`: owns cached node `modelVersion` data, dirty tracking, node save thunks, and node ID replacement handling.
- `src/src/backend/routes/dataRoutes.ts`: rebuilds node cache from diffs, creates or updates diagrams, upserts and prunes `Node` rows, processes subnetwork instances, and translates the saved canvas into persisted parameters.
- `src/src/backend/prisma/mongodb/schema.prisma`: defines the MongoDB `Diagram`, `Node`, and `SubnetworkBlueprint` persistence models.

## Purpose and Responsibility

The save workflow owns user-triggered persistence for the active diagram and dirty node `modelVersion` changes. It also maintains the consistency boundary between temporary React Flow node IDs and canonical MongoDB node IDs.

The frontend owns the canvas snapshot, dirty-node selection, local `nodeCacheDiffs` and `nodeCacheFull` construction, localStorage metadata, and UI feedback. The backend owns authorization, MongoDB writes, diff application, node table coverage, subnetwork instance creation or reuse, translation, parameter persistence, and snapshot persistence.

The save workflow does not own solver execution and must not use generated solver artifacts such as `src/src/backend/services/solve_request.json` as source of truth.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `diagramId` | React Router params | Chooses `PUT /api/data/diagrams/:diagramId` for an existing diagram or `POST /api/data/diagrams` for a new diagram. |
| `domainData.id` and `domainData` | Redux `domain.data` | Required domain guard, `domainId`, and `snapshotData`. |
| `canvasName`, `description`, `diagramType`, `parentConnectionsState`, `nodeParameters`, `tpChangesDraft` | Redux `canvas` state | Diagram metadata, save type, subnetwork instance metadata, dirty value merge, and TP draft persistence. |
| `calcType` | Redux `calcType.type` | Stored on the request and used by backend translation. |
| `nodeCache.modelVersions`, `nodeCache.dirtyNodes`, `nodeCache.originalModelVersions` | Redux `nodeCache` state | Dirty-node payload, JSON patch diff base, and full payload fallback. |
| React Flow `toObject()` and `getEdges()` | `@xyflow/react` hooks | Serialized lightweight canvas and stream completeness validation. |

| Output | Destination | Notes |
| --- | --- | --- |
| Lightweight `canvas` | `Diagram.canvas` | Excludes embedded `modelVersion` and `timePeriods`; includes `schemaVersion: "6.0.0"`. |
| `parameters` | `Diagram.parameters` | Built server-side through `translation(...)` from the saved canvas and node cache. |
| `nodeCacheDiffs` / `nodeCacheFull` | Backend request body | Used to rebuild dirty node `modelVersion` state without sending every cached node. |
| Dirty node rows | MongoDB `Node` collection | Written by both diagram route helpers and `POST/PUT /api/data/nodes`. |
| `createdSubnetworks` | Diagram save response | Tells the frontend which wrapper nodes now point to which instance diagrams. |
| `parentNodeUpdates` | Diagram save response | Updates parent wrapper node cache after instance-to-parent propagation. |
| Save metadata | `localStorage` and Redux `saved` slice | Stores last save time, duration, and saved status. |

## LocalStorage Keys

| Key | Writer | Value |
| --- | --- | --- |
| `save_auto_reload_enabled` | `SaveAndRestore` | String `"true"` or `"false"`; missing means auto reload defaults to enabled. |
| `temp_diagram_${domainId}` | `useSaveDiagram` | JSON object `{ canvasName, description, timestamp }` written before save and removed after the main create/update branch succeeds. |
| `diagram_save_meta_${diagramId}` | `useSaveDiagram` | JSON object `{ lastSavedAt, lastSaveDurationMs }` written after successful save finalization. |

## Core State and Data Structures

- `nodeCache.modelVersions`: map of `nodeId -> ModelVersion` in Redux.
- `nodeCache.dirtyNodes`: array of node IDs with unsaved cache edits.
- `nodeCache.originalModelVersions`: baseline versions captured before the first dirty edit; used to build JSON patch operations.
- `NodeIdReplacement`: `{ oldNodeId, newNodeId }`, returned when a non-canonical or missing node is created as a MongoDB row and receives a canonical ID.
- `NodeCacheDiffs`: `Record<string, Operation[]>`, generated with `fast-json-patch.compare(base, current)`.
- `NodeCacheFull`: `Record<string, ModelVersion>`, used when the frontend has no baseline for a dirty node.
- `CreatedSubnetworksResponse`: map keyed by wrapper node ID, containing `instanceDiagramId`, `blueprintDiagramId`, optional `nodeIdMapping`, and optional `parentConnections`.

## Main Functions and Components

- `SaveAndRestore`: renders the Save button, blocks save when `disabled`, and persists the auto-reload toggle.
- `useSaveDiagram(saveAsCopy, autoReload, options)`: coordinates the full frontend save operation.
- `flushPendingInputEdits()`: blurs the active element before snapshotting so blur handlers can stage pending Redux/cache changes.
- `prepareSubnetworkInstances(canvas, parentDiagramId)`: scans wrapper nodes and connected edges, then builds `subnetworkInstances` for backend instance persistence.
- `gatherNodeCachePayload(...)`: includes dirty nodes only, loads missing cached model versions, and merges explicit Redux node parameter edits into `modelVersion`.
- `saveAllChanges(diagramId)`: saves dirty nodes through node routes and returns node ID replacements.
- `buildNodeCacheRecordFromDiffs(...)`: backend helper that fetches existing `Node` rows, applies patches, and combines `nodeCacheDiffs` with `nodeCacheFull`.
- `upsertDiagramNodesFromCacheAndCanvas(...)`: backend helper that writes model versions into the `Node` collection for the current diagram.
- `pruneDiagramNodes(...)`: deletes `Node` rows no longer represented by the saved canvas or node cache record.

## Exact Request Payloads

Primary diagram save payload from `useSaveDiagram`:

```ts
{
  name: canvasName,
  canvas,
  description,
  domainId: domainData.id,
  calcType,
  snapshotData: domainData,
  type: diagramType,
  nodeCacheDiffs,
  nodeCacheFull,
  subnetworkInstances,
  clientTiming: {
    snapshotDataMs: Math.round(snapshotMs),
    nodeCacheDataMs: Math.round(nodeCacheMs),
  },
  schemaVersion: '6.0.0',
}
```

Existing diagrams use:

```ts
await axios.put(`/api/data/diagrams/${diagramId}`, payload);
```

New diagrams use:

```ts
await axios.post('/api/data/diagrams', payload);
```

The remap repair request is sent only when `saveAllNodeChanges(...)` returns replacements:

```ts
await axios.put(`/api/data/diagrams/${currentDiagramId}`, {
  name: canvasName,
  description,
  domainId: domainData.id,
  calcType,
  canvas,
  nodeCacheDiffs: remappedNodeCacheDiffs,
  nodeCacheFull: remappedNodeCacheFull,
  subnetworkInstances: finalSubnetworkInstances,
});
```

Node cache route payloads:

```ts
// Load a node modelVersion, with diagram scope when available.
axios.get(`/api/data/nodes/${nodeId}`, {
  params: diagramId ? { diagramId } : undefined,
});

// Update an existing canonical node.
axios.put(`/api/data/nodes/${nodeId}`, {
  modelVersion,
  diagramId,
});

// Create a missing or non-canonical node.
axios.post('/api/data/nodes', {
  nodeId,
  diagramId,
  modelVersion,
});
```

Pending TP drafts are persisted after the diagram has a usable diagram ID:

```ts
// Create or update a TP change draft.
axios.post('/api/data/tpchanges', {
  ...draftFields,
  nodeId: resolvedNodeId,
  diagramId: targetDiagramId,
});

// Delete a TP change draft.
axios.delete('/api/data/tpchanges', {
  data: {
    ...draftFields,
    nodeId: resolvedNodeId,
    diagramId: targetDiagramId,
  },
});
```

## Data Flow

1. The user clicks Save in `SaveAndRestore`, or another component calls `useSaveDiagram`.
2. The hook blocks duplicate saves with `saveInFlightRef`, `globalSaveInFlight`, Redux `isSaving`, and a 3-second create dedupe key of `${domainId}:${canvasName}`.
3. The hook blurs the active input, reads latest canvas Redux state, validates `domainData.id`, stores `temp_diagram_${domainId}`, and aborts if `getIncompleteStreamEdges(getEdges())` finds incomplete streams.
4. `toObject()` is deep copied into a lightweight `canvas`; embedded `modelVersion` and `timePeriods` are removed from node data, edge UI-only fields are stripped, and `schemaVersion` is set to `"6.0.0"`.
5. For instance diagrams (`diagramType === 2`), `canvas.parentConnections` is sanitized from Redux `parentConnectionsState`.
6. `prepareSubnetworkInstances(...)` gathers wrapper node `blueprintDiagramId`, optional `instanceDiagramId`, external port mappings, connected edge metadata, and stream payloads.
7. `gatherNodeCachePayload(...)` includes dirty nodes only, merges explicit Redux parameter edits, and preserves propagated values on exposed ports unless there is an explicit human override.
8. The frontend builds `nodeCacheDiffs` for nodes with an original baseline and `nodeCacheFull` for nodes without one.
9. The frontend sends the primary `POST /api/data/diagrams` or `PUT /api/data/diagrams/:diagramId` request.
10. The backend optionally processes `subnetworkInstances`, rebuilds node cache from `nodeCacheDiffs` and `nodeCacheFull`, ensures node cache coverage, remaps canvas IDs from node cache records, propagates subnetwork port values when needed, runs translation, and writes `Diagram`.
11. The backend upserts and prunes `Node` rows when the request contains canvas or node cache data.
12. The frontend applies `createdSubnetworks` to wrapper nodes, updates parent node cache from `parentNodeUpdates`, pushes merged model versions back into Redux, and calls `nodeCache.saveAllNodeChanges(currentDiagramId)`.
13. If `saveAllNodeChanges` returns replacements, the frontend remaps React Flow nodes, edges, canvas nodes, `portsMapping`, `parentConnections`, `subnetworkInstances`, `modelNameMap`, and canvas Redux node IDs, then sends the second `PUT`.
14. The hook writes `diagram_save_meta_${diagramId}`, marks the diagram saved in Redux, optionally navigates to a new diagram route, and optionally reloads after an update save.

## Backend and Database Boundaries

| Boundary | MongoDB Model | Save Behavior |
| --- | --- | --- |
| Diagram document | `Diagram` | `POST /diagrams` creates a diagram with `canvas`, `parameters`, default costs, optional snapshot, `type`, `duration`, `durationUnit`, and `parentConnections`. `PUT /diagrams/:diagramId` updates the current document after translation. |
| Node model versions | `Node` | `nodeId` is a string, not an ObjectId field type. Routes and helper functions create, update, upsert, and prune rows by `diagramId` and `nodeId`. |
| Blueprint metadata | `SubnetworkBlueprint` | Read indirectly when save creates or reuses subnetwork instances. Blueprint creation is documented in the subnetwork page. |
| Domain snapshot | `DomainSnapshot` | New diagram save creates a snapshot from `snapshotData`; update save updates the existing snapshot when `snapshotData` is provided. |
| TP state | `TpNodeVers`, `TpChanges` | Update save reads both tables for translation. The frontend separately writes pending `tpChangesDraft` entries through `/api/data/tpchanges`. |

Generated solver request files are outside this boundary. Do not hand-edit or document behavior from `src/src/backend/services/solve_request.json`.

## Error Handling and Edge Cases

- Missing `domainData.id` aborts save with `No domain selected`.
- Incomplete stream edges are highlighted and save aborts before any diagram request.
- Missing `name`, `canvas`, or `description` on `POST /diagrams` returns `400`.
- `PUT /diagrams/:diagramId` requires at least one normal updatable field such as `name`, `canvas`, `description`, `domainId`, `snapshotData`, `calcType`, `type`, `parentConnections`, or duration fields.
- `nodeCache.saveAllChanges` rejects if a dirty node has no cached `modelVersion`.
- `PUT /api/data/nodes/:nodeId` can return `409` if the same `nodeId` exists in multiple diagrams and the request does not include `diagramId`.
- If the second remap `PUT` fails, the frontend keeps the original save but warns that node IDs may be outdated and asks the user to save again.
- LocalStorage reads and writes are guarded with `try/catch`; failures log warnings but do not abort save.

## Testing and Verification

Existing targeted tests that touch this area:

```powershell
# Working directory: src
npx.cmd jest tests/frontend/nodeCacheSlice.test.ts --runInBand --coverage=false
npx.cmd jest tests/backend/routes/dataRoutes.recursiveSubnetwork.test.ts --runInBand --coverage=false
```

Build check:

```powershell
# Working directory: src
npm.cmd run build
```

Manual verification matrix:

| Scenario | Expected State or API Change | Regression Risk |
| --- | --- | --- |
| Save existing clean canvas | `PUT /api/data/diagrams/:diagramId` succeeds; save metadata updates; reload follows `save_auto_reload_enabled`. | Accidentally reloading during non-manual saves. |
| Save with dirty node cache | Payload contains dirty `nodeCacheDiffs` or `nodeCacheFull`; `Node.modelVersion` is updated. | Dropping dirty changes if `dirtyNodes` and cache keys diverge. |
| Save new diagram with temporary node IDs | `POST /api/data/diagrams` creates a diagram, node route creates canonical IDs, replacement flow sends second `PUT`. | Canvas edges or `portsMapping` still pointing at temporary IDs. |
| Save diagram containing subnetwork wrappers | `subnetworkInstances` is included; response may include `createdSubnetworks`; wrapper `model.diagramId` becomes the instance diagram ID. | Recreating instances instead of preserving `instanceDiagramId`. |
| Save with incomplete stream edge | No diagram request is sent; edge is highlighted and an error alert appears. | Persisting incomplete stream data. |

## Known Cautions

- `nodeCacheDiffs` depends on `originalModelVersions`; if no baseline exists, the frontend must use `nodeCacheFull`.
- The backend can rebuild patches against an empty base when a node is missing, but that is a fallback. Prefer sending `nodeCacheFull` for nodes without a reliable base.
- Dirty-node persistence is intentionally narrow. Do not change it to send every cached node unless the save-performance tradeoff is explicitly accepted.
- The second `PUT` is part of the canonical node ID contract. Any change that creates nodes with new IDs must keep the remap of canvas nodes, edges, `portsMapping`, `parentConnections`, and `subnetworkInstances`.
- `saveAllChanges.fulfilled` clears all dirty nodes. If a later remap or TP draft step fails, the UI may need a new save to repair related diagram metadata.
- `saveAsCopy` currently contains local diagnostic `fetch('http://127.0.0.1:7242/ingest/...')` calls in the source. Treat those as debug side effects, not as persistence contract.
- The package `npm.cmd test` script enables coverage. Use explicit `--coverage=false` for targeted Jest commands when coverage output is not desired.

## Related Pages

- `docs/SetupInstructions/CodeExplanation/subnetwork-blueprint-and-instance-flow.md`
- `docs/SetupInstructions/CodeExplanation/CODE_EXPLANATION_GUIDELINES.md`
