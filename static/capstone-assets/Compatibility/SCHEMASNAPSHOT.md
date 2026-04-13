# Schema Snapshot — v6.0.0

> **IMPORTANT:** This file is the baseline reference for compatibility checks.
> When `CURRENT_SCHEMA_VERSION` is bumped, update this file to reflect the
> new structure. The compatibility prompt compares live code against this
> snapshot to detect undocumented changes.

Last updated at version: `6.0.0`
Source of truth: `src/src/backend/utils/schemaMigrations.ts` → `CURRENT_SCHEMA_VERSION`

---

## 1. Save Payload (Frontend → Backend)

Source: `src/src/frontend/src/components/header-bar/utils/save-util.tsx`

```
payload {
  name: string
  canvas: { nodes: [...], edges: [...] }
  description: string
  domainId: string
  calcType: string
  snapshotData: object
  type: number                     // 0: normal, 1: blueprint, 2: instance
  nodeCacheDiffs: Record<nodeId, Operation[]>
  nodeCacheFull: Record<nodeId, ModelVersion>
  subnetworkInstances: SubnetworkInstanceRequest[]
  clientTiming: { snapshotDataMs, nodeCacheDataMs }
  schemaVersion: string            // "6.0.0"
}
```

## 2. Export Snapshot (FullNetworkSnapshot)

Source: `src/src/backend/routes/dataRoutes.ts` → `interface FullNetworkSnapshot`

```
FullNetworkSnapshot {
  version: string
  metadata: {
    name: string
    description: string
    type: number
    isVerified: boolean
    domainId?: string
    calcType?: string
    createdAt?: string
  }
  canvas: Json
  parentConnections?: Json
  nodes: Array<{ nodeId: string, modelVersion: Json }>
  tpNodeVers: Array<{
    nodeId, timePeriodId, fromTp, toTp, modelVersion
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
    name, description, canvas: Json,
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

```
Diagram {
  id: ObjectId, userId: ObjectId,
  name: String, description: String,
  canvas: Json, parameters: Json,
  snapshotId?: ObjectId, isVerified: Boolean,
  type: Int (default 0),
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
  fromTp: Int, toTp: Int, modelVersion: String
}

TpChanges {
  id: ObjectId, diagramId: ObjectId,
  nodeId: String, timePeriodId: String,
  fromTp: Int, toTp: Int,
  portName: String, portVarName: String,
  portVarValue: Float,
  spec?: String, lowerBound?: Float,
  upperBound?: Float, unit?: String,
  isComputed?: Boolean
}
```

## 4. Canvas JSON Structure

Stored in `Diagram.canvas` (MongoDB Json field).

```
canvas {
  nodes: Array<{
    id: string
    type: string
    position: { x, y }
    data: {
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
        diagramId?: string       // instance diagram ID
      }
      blueprintDiagramId?: string
    }
  }>
  edges: Array<{
    id: string
    type: "custom"
    source: string
    target: string
    sourceHandle: number
    targetHandle: number
    data: {
      sourceHandle: number
      targetHandle: number
      direction: { source: number, target: number }
      stream?: object
    }
    style: { strokeWidth: number }
  }>
}
```
