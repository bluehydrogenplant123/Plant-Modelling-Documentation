# Schema Snapshot - v6.0.0

> IMPORTANT: This file is the baseline reference for compatibility checks.
> When `CURRENT_SCHEMA_VERSION` is bumped, update this file to reflect the
> live compatibility baseline. If the bump is library-only, keep the structure
> sections accurate and note that the persisted shape did not change.
> Version-to-version decision summaries belong in
> `docs/Compatibility/SCHEMA_HISTORY.md`, not here.

Last updated at version: `6.0.0`
Source of truth: `src/src/backend/utils/schemaMigrations.ts` -> `CURRENT_SCHEMA_VERSION`

Note: the active compatibility axis has been reset to a clean `v6.0.0`
baseline on top of the `feature/stable-version6.1` code branch. Older
experimental `6.1/6.2/6.3` schema labels are not part of the live executable
history anymore.

---

## 1. Save Payload (Frontend -> Backend)

Source: `src/src/frontend/src/components/header-bar/utils/save-util.tsx`

```txt
payload {
  name: string
  canvas: {
    schemaVersion: string         // "6.0.0"
    nodes: [...]
    edges: [...]
    parentConnections?: ParentConnections
  }
  description: string
  domainId: string
  calcType: string
  snapshotData: object
  type: number                    // 0: normal, 1: blueprint, 2: instance
  nodeCacheDiffs: Record<nodeId, Operation[]>
  nodeCacheFull: Record<nodeId, ModelVersion>
  subnetworkInstances: Array<{
    nodeId: string
    nodeName?: string
    blueprintDiagramId: string
    instanceDiagramId?: string
    parentConnections?: ParentConnections
  }>
  clientTiming: { snapshotDataMs, nodeCacheDataMs }
  schemaVersion: string           // "6.0.0"
}
```

## 2. Export Snapshot (FullNetworkSnapshot)

Source: `src/src/backend/routes/dataRoutes.ts` -> `interface FullNetworkSnapshot`

```txt
FullNetworkSnapshot {
  version: string                 // "6.0.0"
  metadata: {
    name: string
    description: string
    type: number
    isVerified: boolean
    duration?: number
    durationUnit?: string
    domainId?: string
    calcType?: string
    createdAt?: string
  }
  canvas: Json
  parentConnections?: Json
  nodes: Array<{ nodeId: string, modelVersion: Json }>
  tpNodeVers: Array<{
    nodeId, timePeriodId, fromTp, toTp,
    duration?, durationUnit?, modelVersion
  }>
  tpChanges: Array<{
    nodeId, timePeriodId, fromTp, toTp,
    portName, portVarName, portVarValue,
    spec?, lowerBound?, upperBound?, unit?, isComputed?
  }>
  subnetworkBlueprints?: Array<{
    model_name, shape, icon_width, icon_height,
    portsMapping: Json, modelVersions: Json,
    blueprintDiagramId
  }>
  subnetworkInstances?: Array<{
    instanceDiagramId, blueprintDiagramId,
    name, description,
    duration?: number, durationUnit?: string,
    canvas: Json,
    parentConnections?: Json,
    nodes: Array<{ nodeId, modelVersion }>,
    tpNodeVers: Array<{...}>,
    tpChanges: Array<{...}>,
    snapshot?: { domainId, data }
  }>
  snapshot?: { domainId: string, data: Json }
}
```

## 3. Prisma MongoDB Models

Source: `src/src/backend/prisma/mongodb/schema.prisma`

```txt
Diagram {
  id: ObjectId, userId: ObjectId,
  name: String, description: String,
  canvas: Json, parameters: Json,
  costEntities?: Json, costMappings?: Json,
  snapshotId?: ObjectId, isVerified: Boolean,
  type: Int (default 0), duration?: Int,
  durationUnit?: String,
  parentConnections?: Json
}

Node {
  id: ObjectId, nodeId: String,
  diagramId: ObjectId, modelVersion: Json
}

SubnetworkBlueprint {
  id: ObjectId, userId: ObjectId,
  blueprintDiagramId: ObjectId (unique),
  model_name: String (unique),
  shape: String, icon_width: Float, icon_height: Float,
  portsMapping: Json, modelVersions: Json
}

TpNodeVers {
  id: ObjectId, diagramId: ObjectId,
  nodeId: String, timePeriodId: String,
  fromTp: Int, toTp: Int,
  duration?: Int, durationUnit?: String,
  modelVersion: String
}

TpChanges {
  id: ObjectId, diagramId: ObjectId,
  nodeId: String, timePeriodId: String,
  fromTp: Int, toTp: Int,
  portName: String, portVarName: String,
  portLocation?: Int,
  portVarValue: Float,
  spec?: String, lowerBound?: Float,
  upperBound?: Float, unit?: String,
  isComputed?: Boolean
}
```

## 4. Canvas JSON Structure

Stored in `Diagram.canvas` (MongoDB Json field).

```txt
StreamPayload {
  id?: string
  name?: string
  stream_database_id?: string
  content?: string
  instance?: string
  propertyValues: Record<string, number | null>
  composition: {
    fractions: Record<string, number | null>
  }
  meta: {
    label?: string
    sourceKind: string
  }
  ...legacy passthrough fields
}

ParentConnections {
  wrapperNodeId?: string
  parentDiagramId?: string
  externalPorts: Record<location, {
    isConnected: boolean
    mapped?: {
      nodeId?: string
      internalNodeId?: string
      instance_port_id?: string
      port_location?: number
      port_type?: number
      port_class?: string
    }
  }>
  edges: Array<{
    id: string
    source: string
    target: string
    sourceHandle?: string | number | null
    targetHandle?: string | number | null
    data?: {
      stream?: StreamPayload
    }
  }>
}

canvas {
  schemaVersion: string           // "6.0.0"
  nodes: Array<{
    id: string
    type: string
    position: { x, y }
    data: {
      subnetworkRef?: {
        blueprintDiagramId?: string
        instanceDiagramId?: string
      }
      model: {
        node_id: string
        node_name: string
        model_id: number
        model_name: string
        rotationDirection: 0 | 1 | 2 | 3
        ports: Array<{ port_location, port_type, port_class }>
        portsMapping?: Record<location, {
          nodeId, internalNodeId,
          port_location, port_type, port_class,
          instance_port_id?
        }>
        diagramId?: string
        instanceDiagramId?: string
        blueprintDiagramId?: string
      }
      blueprintDiagramId?: string
      instanceDiagramId?: string
      diagramId?: string
    }
  }>
  edges: Array<{
    id: string
    type: "custom"
    source: string
    target: string
    sourceHandle: number | string
    targetHandle: number | string
    data: {
      sourceHandle: number | string
      targetHandle: number | string
      direction: { source: number, target: number }
      stream?: StreamPayload
    }
    style: { strokeWidth: number }
  }>
  parentConnections?: ParentConnections
}
```
