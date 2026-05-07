---
title: Subnetwork Blueprint and Instance Flow Code Explanation
sidebar_position: 24
description: Explains how subnetwork blueprints are saved, how wrapper instances are persisted, and how instance node IDs and parent connections are remapped.
---

## Overview

The subnetwork flow lets a saved diagram become a reusable blueprint, then lets wrapper nodes in other diagrams point to isolated instance diagrams. Blueprint authoring starts in `SaveAsSubnetwork`; instance persistence happens during normal diagram save through `subnetworkInstances` in the diagram save payload.

This page focuses on blueprint save, instance save, parent connection persistence, and node ID remapping. It does not document solver execution or reverse translation.

## Source Files

- `src/src/frontend/src/components/header-bar/header-buttons/save-as-subnetwork.tsx`: Subnetwork Editor UI, port selection, blueprint request construction, and diagram type update.
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: creates `subnetworkInstances`, applies `createdSubnetworks`, and remaps subnetwork metadata after canonical node ID replacements.
- `src/src/frontend/src/features/node/nodeCacheService.ts`: preloads mapped node model versions used to build exposed port variables.
- `src/src/frontend/src/features/node/nodeCacheSlice.ts`: stores node cache data used by the editor and save workflow.
- `src/src/frontend/src/models/domain.ts`: frontend `SubnetworkBlueprint`, `PortMapping`, `ParentConnections`, and `Diagram` types.
- `src/src/backend/routes/dataRoutes.ts`: owns `/subnetworks`, `/diagrams/:diagramId/subnetwork-instance`, and diagram save-side instance processing.
- `src/src/backend/prisma/mongodb/schema.prisma`: defines `Diagram`, `Node`, and `SubnetworkBlueprint`.

## Purpose and Responsibility

`SaveAsSubnetwork` owns the user-facing editor for naming a blueprint, choosing an icon, and exposing selected internal ports. It sends a blueprint payload to the backend and then saves the diagram so the blueprint diagram and Node rows stay current.

The backend owns blueprint validation, `SubnetworkBlueprint` upsert, diagram `type` updates, instance diagram creation or reuse, node duplication, parent connection sanitization, and instance canvas remapping.

The normal save workflow owns wrapper instance persistence. A wrapper node is represented by a parent canvas node whose `data.blueprintDiagramId` points to the blueprint diagram while `data.model.diagramId` points to the instance diagram after save.

## Rendered UI and Interaction Map

| UI State or Action | Source State or Props | Expected Result |
| --- | --- | --- |
| Click `Subnetwork Editor` while saved | Redux `saved === true` | Opens the editor modal. |
| Click `Subnetwork Editor` with unsaved changes | Redux `saved === false` | Opens `NavigationSaveDiscardModal`; Save runs `useSaveDiagram(false, false, { showSuccessToast: false })`, Discard opens the editor without saving first. |
| Open editor on a diagram route | `location.pathname` starts with `/diagram/` | Loads blueprint names from `GET /api/data/subnetworks`. |
| Existing blueprint found | `GET /api/data/diagrams/:diagramId` and `/subnetworks` | Populates name, icon SVG, and saved port mappings. |
| Add port mapping | Local `portMappings` state and React Flow nodes/edges | Adds a row for selecting internal node, source port, external location, and external port name. |
| Save button disabled | Empty name, no mappings, duplicate name, or incomplete mapping row | Blocks invalid blueprint request before backend call. |

The icon upload accepts SVG, PNG, JPEG, and JPG only, with a 1 MB size limit.

## Component Contract

`SaveAsSubnetwork` receives:

```ts
{ disabled: boolean }
```

Important state and selectors:

- `diagramId`: parsed from `/diagram/:diagramId`.
- `saved` and `isSaving`: from Redux `saved` slice.
- `blueprintNames`: from Redux canvas slice, updated from `/api/data/subnetworks`.
- `domainModelMap`: used to resolve selected node port metadata.
- `getNodes()` / `getEdges()`: used to find selectable nodes and unconnected ports.
- `getCachedModelVersion(...)` and `preloadMultipleNodes(...)`: used to build `ports_var` from node cache or domain fallback data.

## Core Data Structures

MongoDB models:

| Model | Important Fields |
| --- | --- |
| `Diagram` | `canvas`, `parameters`, `snapshotId`, `type`, `parentConnections`, `duration`, `durationUnit`. `type` is `0` normal, `1` blueprint, `2` instance. |
| `Node` | `nodeId`, `diagramId`, `modelVersion`. `nodeId` is a string and may start as a React Flow ID before canonical remap. |
| `SubnetworkBlueprint` | `blueprintDiagramId` unique, `model_name` unique, `shape`, `icon_width`, `icon_height`, `portsMapping`, `modelVersions`. |

Frontend mapping types:

- `portsMapping`: map of external port location string to internal node and port metadata.
- `parentConnections`: instance diagram metadata with `wrapperNodeId`, `parentDiagramId`, `externalPorts`, and connected parent `edges`.
- `createdSubnetworks`: backend response map keyed by wrapper node ID.

## Exact Request Payloads

Blueprint save payload from `SaveAsSubnetwork`:

```ts
{
  blueprintDiagramId: diagramId,
  model_name: nodeName,
  shape: iconSvg,
  icon_width: 1,
  icon_height: 1,
  modelVersions: [
    {
      id,
      model_version_name: nodeName ?? 'Version 1',
      version_date: new Date().toISOString(),
      author: user ?? 'Unknown',
      eq_type_phase_1: '',
      eq_type_phase_2: '',
      calc_iteration_phase_1: '',
      calc_iteration_phase_2: '',
      calc_after_phase_1: '',
      calc_after_phase_2: '',
      ports_var: finalPortsVarArray,
    },
  ],
  portsMapping: {
    [exportPortNumber]: {
      nodeId: mapping.nodeId,
      port_location: sourcePortLocation,
      port_type: sourcePortType,
      port_class: sourcePortClass,
      port_name: mapping.exportPortName || mapping.portName || sourcePortName,
    },
  },
}
```

Create or upsert by blueprint diagram:

```ts
await axios.post('/api/data/subnetworks', newBlueprint);
```

Update by blueprint ID:

```ts
await axios.put(`/api/data/subnetworks/${id}`, newBlueprint);
```

After the blueprint request succeeds, `SaveAsSubnetwork` runs a normal diagram save and then marks the referenced diagram as a blueprint:

```ts
await saveDiagram();

await axios.put(`/api/data/diagrams/${diagramId}`, {
  name: nodeName,
  type: 1,
});
```

Subnetwork instance payload embedded in the normal diagram save request:

```ts
{
  nodeId: wrapperNode.id,
  nodeName: model.node_name,
  blueprintDiagramId,
  instanceDiagramId,
  parentConnections: {
    wrapperNodeId: wrapperNode.id,
    parentDiagramId,
    externalPorts: {
      [externalPortLocation]: {
        isConnected,
        mapped: {
          nodeId: internalNodeId,
          internalNodeId,
          instance_port_id,
          port_location,
          port_type,
          port_class,
        },
      },
    },
    edges: [
      {
        id,
        source,
        target,
        sourceHandle,
        targetHandle,
        data: {
          stream,
        },
      },
    ],
  },
}
```

On-demand instance creation endpoint:

```ts
await axios.post(`/api/data/diagrams/${diagramId}/subnetwork-instance`, {
  wrapperNodeId,
  blueprintDiagramId,
});
```

Response:

```ts
{
  instanceDiagramId,
  blueprintDiagramId,
}
```

## Data Flow

1. The user opens Subnetwork Editor. If the diagram is dirty, the save/discard modal appears before the editor.
2. The editor loads blueprint names from `GET /api/data/subnetworks` and, when editing an existing blueprint diagram, loads the matching blueprint by `blueprintDiagramId`.
3. The user selects internal nodes and unconnected ports. `getAvailableNodes()` excludes ports already used by current canvas edges.
4. Before save, the editor preloads missing mapped node model versions through `preloadMultipleNodes(...)`.
5. `finalPortsVarArray` is built from cached `modelVersion.ports_var`, matching source port variables by port location first, then normalized port name.
6. The editor sends `POST /api/data/subnetworks` or `PUT /api/data/subnetworks/:id`.
7. The backend validates ownership of `blueprintDiagramId`, rejects instance diagrams (`type === 2`) as blueprint sources, normalizes `portsMapping`, creates or updates `SubnetworkBlueprint`, and sets the blueprint diagram `type` to `1`.
8. The editor calls `saveDiagram()` so the diagram canvas and Node rows are current, then sends a focused `PUT /api/data/diagrams/:diagramId` with `name` and `type: 1`.
9. Later, when a parent diagram containing wrapper nodes is saved, `prepareSubnetworkInstances(...)` adds `subnetworkInstances` to the diagram save payload.
10. `processSubnetworkInstances(...)` reuses an existing instance when `instanceDiagramId` exists, belongs to the same user, and does not require replacement. It updates `parentConnections` and duration only when they changed.
11. If there is no reusable instance, the backend creates a new `Diagram` with `type: 2`, clones the blueprint snapshot if present, duplicates blueprint `Node` rows into the instance diagram, remaps the instance canvas to new canonical node IDs, and stores remapped `parentConnections`.
12. The backend returns `createdSubnetworks`; the frontend updates wrapper nodes so `data.blueprintDiagramId` remains the blueprint diagram and `data.model.diagramId` becomes the instance diagram.

## Remap and Second PUT Flow

Subnetwork remap happens in two places.

Backend instance creation remap:

- `duplicateBlueprintNodes(...)` clones `Node` rows from the blueprint diagram into the instance diagram.
- The created Mongo row ID becomes the canonical `nodeId`.
- `remapInstanceDiagramCanvas(...)` replaces internal canvas node IDs, `model.node_id`, edge endpoints, and nested `portsMapping` IDs.
- `remapParentConnectionsWithNodeIds(...)` updates `parentConnections.externalPorts[*].mapped.nodeId`, `internalNodeId`, and edge endpoints.
- `processSubnetworkInstances(...)` returns `nodeIdMapping` in `createdSubnetworks` so the wrapper's `portsMapping` can also be remapped.

Frontend post-node-save remap:

- `nodeCache.saveAllNodeChanges(currentDiagramId)` can return replacements after creating missing or non-canonical parent nodes.
- `save-util.tsx` maps `oldNodeId -> newNodeId`.
- It remaps wrapper `nodeId`, `parentConnections.wrapperNodeId`, parent edge `source` and `target`, generated edge IDs, `externalPorts[*].mapped.nodeId`, `externalPorts[*].mapped.internalNodeId`, canvas nodes, canvas edges, and wrapper `portsMapping`.
- It preserves `instanceDiagramId` so existing instances are updated instead of recreated.
- It sends the second `PUT /api/data/diagrams/${currentDiagramId}` with remapped `canvas`, empty `remappedNodeCacheDiffs` entries for canonical node IDs, empty `remappedNodeCacheFull`, and `finalSubnetworkInstances`.

## Backend and Database Boundaries

| Boundary | Write Behavior |
| --- | --- |
| `SubnetworkBlueprint` | `POST /subnetworks` creates or updates by `blueprintDiagramId`; `PUT /subnetworks/:id` updates by blueprint ID. `model_name` remains globally unique. |
| Blueprint `Diagram` | Backend sets `type: 1` after blueprint create/update. Frontend also sends a focused diagram `PUT` with `{ name, type: 1 }`. |
| Instance `Diagram` | Created with `type: 2`, cloned canvas and parameters, optional cloned snapshot, duration, duration unit, and `parentConnections`. |
| Instance `Node` rows | Cloned from the blueprint diagram into the instance diagram; each new Mongo row is normalized so `nodeId` equals the row `id`. |
| Parent `Diagram.canvas` | Wrapper nodes are updated with `blueprintDiagramId`, instance `model.diagramId`, remapped `portsMapping`, and optional `model.parentConnections`. |
| Internal node streams | `applySubnetworkStreamsToInternalNodes(...)` can copy stream payloads from parent connection edges into internal node model versions. |

Generated solver request artifacts are not part of this boundary and should not be edited or used as authoring source.

## Error Handling and Edge Cases

- `SaveAsSubnetwork` blocks save when the name is empty, duplicate, or any mapping row lacks node, port, or export port number.
- Blueprint icon upload rejects files over 1 MB and non-SVG/PNG/JPEG/JPG types.
- `POST /subnetworks` and `PUT /subnetworks/:id` require `blueprintDiagramId`, `model_name`, `modelVersions`, and `portsMapping`.
- The backend returns `404` when the blueprint diagram does not exist.
- The backend returns `403` when the diagram or blueprint belongs to another user.
- `POST /subnetworks` returns `400` when trying to save an instance diagram (`type === 2`) as a blueprint. The current `PUT /subnetworks/:id` path validates ownership and payload shape but does not repeat that specific type guard.
- `normalizeBlueprintPortsMapping(...)` drops invalid mapping entries and rejects an empty normalized mapping.
- Existing instance diagrams are reused only when they exist and belong to the same user; otherwise the backend creates a new instance from the blueprint.
- Existing instances with non-canonical internal mappings can trigger remap using blueprint canvas, instance canvas, node names, and legacy port-location hints.

## Testing and Verification

Existing targeted tests that touch subnetwork instance and parent connection behavior:

```powershell
# Working directory: src
npx.cmd jest tests/backend/routes/dataRoutes.recursiveSubnetwork.test.ts --runInBand --coverage=false
```

Node cache remap error coverage:

```powershell
# Working directory: src
npx.cmd jest tests/frontend/nodeCacheSlice.test.ts --runInBand --coverage=false
```

Manual verification matrix:

| Scenario | Expected State or API Change | Regression Risk |
| --- | --- | --- |
| Create blueprint from normal diagram | `/api/data/subnetworks` creates or updates a blueprint; diagram becomes `type: 1`. | Saving a stale diagram if the follow-up `saveDiagram()` fails. |
| Edit existing blueprint | `PUT /api/data/subnetworks/:id` keeps the same blueprint record and updates name/icon/mappings. | Name conflict with another blueprint. |
| Save parent diagram with wrapper | Primary diagram save includes `subnetworkInstances`; wrapper `model.diagramId` becomes instance diagram ID. | Recreating instance diagrams on every save. |
| Save after new parent node IDs are created | Replacement flow sends second `PUT` with remapped `subnetworkInstances`. | `parentConnections` or `portsMapping` still referencing old wrapper/internal IDs. |
| Save copy with wrappers | Copy payload clears `instanceDiagramId` so copied wrappers can receive new instance diagrams. | Accidentally sharing old instance diagrams across copies. |

## Known Cautions

- Do not use legacy blueprint docs as behavior source. Current behavior is defined by `save-as-subnetwork.tsx`, `save-util.tsx`, and `dataRoutes.ts`.
- `portsMapping` is normalized on backend create, update, and read. Future fields must be added to `normalizeBlueprintPortMappingEntry(...)` or they may be dropped.
- `instanceDiagramId` is the reuse signal. Clearing it forces new instance creation; preserving it updates existing instance metadata.
- `parentConnections.edges` carries wrapper edge context and optional `data.stream`. Dropping this data can break internal stream propagation.
- Subnetwork Editor depends on node cache coverage for exposed port variables. If mapped nodes are not cached and domain fallback data is insufficient, save fails with `No port variables found after loading node data`.
- The normal save remap and the backend instance remap must stay aligned. Any new ID-bearing field in `portsMapping`, `parentConnections`, or edge data needs remap support in both places when applicable.
- Some current backend and frontend paths contain local diagnostic `fetch('http://127.0.0.1:7242/ingest/...')` calls. Treat them as debug side effects, not as part of the persistence contract.
- `npm.cmd test` enables coverage by default in `src/package.json`; use targeted Jest commands with `--coverage=false` when documenting or running focused verification.

## Related Pages

- `docs/SetupInstructions/CodeExplanation/save-diagram-and-node-cache.md`
- `docs/SetupInstructions/CodeExplanation/CODE_EXPLANATION_GUIDELINES.md`
