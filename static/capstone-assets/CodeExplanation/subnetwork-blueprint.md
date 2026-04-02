# Subnetwork Blueprint System

## Overview

A **Subnetwork Blueprint** is a reusable component that encapsulates a complex diagram into a single node that can be instantiated in other diagrams. This enables hierarchical composition of models, where internal components of one diagram can be abstracted and used as black-box nodes in parent diagrams.

---

## 1. How We Define a Subnetwork Blueprint

### 1.1 Data Structure

A Subnetwork Blueprint is defined by the `SubnetworkBlueprint` interface with the following structure:

```typescript
interface SubnetworkBlueprint {
  id: string;                                    // Unique identifier
  userId: string;                                // Owner of the blueprint
  blueprintDiagramId: string;                    // Reference to the blueprint diagram
  model_name: string;                            // Display name of the node in UI
  shape: string;                                 // SVG icon representation
  icon_width: number;                            // Icon dimensions
  icon_height: number;
  modelVersions: ModelVersion[];                 // Model versions with port information
  portsMapping: {                                // Maps external port numbers to internal nodes
    [exportPortLocation: string]: PortMapping;
  };
  rotationDirection: number;                     // Rotation metadata
}
```

### 1.2 PortMapping Definition

Each port in `portsMapping` connects an external port (on the wrapper node) to an internal node and its port:

```typescript
interface PortMapping {
  nodeId: string;              // ReactFlow node ID (internal node)
  portId: string;              // Domain port ID
  exportPortNumber: number;    // External port number on the wrapper node
  exportPortName: string;      // Name of the external port
  portType: number;            // 1=inlet, 2=outlet, 3=info, 4=electric
  portName: string;            // Internal port name
  portClass: string;           // Port classification (e.g., "inlet", "outlet")
  portLocation: number;        // Location number of the internal port
}
```

### 1.3 ModelVersion Structure

The `modelVersions` array stores the computational model of the subnetwork:

```typescript
interface ModelVersion {
  id: string;
  model_version_name: string;
  ports_var: PortVariable[];   // Variables for each port
  [otherFields: string]: unknown;
}

interface PortVariable {
  port_name: string;
  port_location: number;
  port_var_name: string;       // Variable name (e.g., "Cp", "Hex")
  internal_var_name?: string;
  port_class: string;
  model_var_object: [{        // Model variable with computed values
    base_unit_default_value?: number;
    selected_unit?: string;
    spec?: string;
    is_computed?: boolean;
    is_human_input?: boolean;
    upper_bound?: number;
    lower_bound?: number;
  }];
}
```

### 1.4 Creation and Storage

When a user creates a subnetwork blueprint:

1. **Frontend** (`save-as-subnetwork.tsx`):
   - User selects nodes and ports to expose
   - Creates a `SubnetworkBlueprint` object with port mappings
   - Sends POST request to `/api/data/subnetworks`

2. **Backend** (`dataRoutes.ts`):
   - Validates the blueprint diagram exists and belongs to the user
   - Creates the `SubnetworkBlueprint` record in MongoDB
   - Updates the diagram's `type` field to `1` (marking it as a blueprint)
   
```typescript
// Backend creation endpoint
router.post('/subnetworks', authenticateToken, async (req, res) => {
  const {
    blueprintDiagramId,
    model_name,
    shape,
    icon_width,
    icon_height,
    modelVersions,
    portsMapping,
  } = req.body;
  
  // Validate and create
  const subnetwork = await mongoClient.subnetworkBlueprint.create({
    data: {
      userId,
      blueprintDiagramId,
      model_name,
      shape,
      icon_width,
      icon_height,
      modelVersions,
      portsMapping,
    }
  });
});
```

### 1.5 Subnetwork Editor Auto‑Save

When the user clicks **Subnetwork Editor** from the header bar, the UI now performs an automatic save (if the diagram is not already saved) before opening the editor modal. This prevents stale blueprint data and guarantees the latest canvas state is persisted.

Key files:
- `src/src/frontend/src/components/header-bar/header-buttons/save-as-subnetwork.tsx`
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`

Behavior:
- If `saved === false`, the editor triggers `useSaveDiagram(false, false, { successMessage: 'saved automaticly' })`.
- After the auto‑save completes (or if already saved), the Subnetwork Editor modal opens.

---

## 2. Subnetwork Instance Name Persistence (Bug Fix)

When a user edits a **Subnetwork Name** on a wrapper node and saves the diagram, the instance diagram name must be updated in MongoDB **and** its computation results must reflect the new subnetwork name. This is handled during `PUT /api/data/diagrams/:diagramId` when `subnetworkInstances` are processed.

Key file:
- `src/src/backend/routes/dataRoutes.ts`

Behavior:
1. `processSubnetworkInstances` receives `nodeName` for each wrapper node.
2. If an instance diagram already exists:
   - Compare `nodeName` (trimmed) with `existingInstanceDiagram.name`.
   - If different, update the instance diagram's `name`.
   - Call `syncComputationResultsNames` with `diagramType: 2` to update `ComputationResults.subnetwork_name` for all rows belonging to the instance.

This ensures the backend is consistent with the UI label shown on the canvas and historical computation results.

## 3. How We Translate the Subnetwork Node

### 3.1 Translation Overview

When a diagram containing subnetwork nodes is translated for computation, the translation process:

1. **Identifies** subnetwork instance nodes (nodes with `diagramId` and `portsMapping`)
2. **Expands** them by resolving their internal structure
3. **Maps** external ports to internal nodes
4. **Generates** solver parameters for the internal network

### 3.2 Subnetwork Detection

A node is identified as a subnetwork instance if it has:

```typescript
const isSubnetworkInstanceNode = (node: CanvasNode): boolean => {
  const nodeData = node.data as Record<string, unknown> | undefined;
  const model = nodeData?.model as Record<string, unknown> | undefined;

  if (!model) return false;

  // Has a diagramId (references an instance diagram)
  const diagramIdCandidate =
    (typeof nodeData?.diagramId === 'string' && nodeData.diagramId.trim().length > 0) ||
    (typeof model.diagramId === 'string' && (model.diagramId as string).trim().length > 0);

  // Has portsMapping (maps external to internal ports)
  const hasPortsMapping =
    model.portsMapping && typeof model.portsMapping === 'object' && 
    Object.keys(model.portsMapping as object).length > 0;

  return Boolean(diagramIdCandidate && hasPortsMapping);
};
```

### 3.3 Building the Subnetwork Port Map

Before translation, the `buildSubnetworkPortMap` function creates a mapping of wrapper node ports to internal nodes:

```typescript
export const buildSubnetworkPortMap = async (
  canvas: unknown,
  domainModelMap: Map<string, DomainModel>,
  nodeCacheData?: NodeCacheMap
): Promise<SubnetworkPortMap> => {
  // Returns: { [wrapperNodeId]: { [portLocation]: SubnetworkResolvedPortInfo } }
  // Where SubnetworkResolvedPortInfo contains:
  // - internalNodeId: the internal node's ReactFlow ID
  // - internalNodeName: the internal node's document ID (for solver)
  // - internalModelName: the model name
  // - internalDiagramId: the instance diagram ID
  // - internalPortLocation: the port location inside the internal node
  // - portName: the port name
  // - portClass: classification
  // - portType: port type (inlet/outlet/etc)
}
```

### 3.4 Edge Resolution with Subnetworks

During edge processing in translation, edges connected to subnetwork nodes are resolved to their internal nodes:

```typescript
const resolveEndpoint = (nodeId: string, handle: string | number) => {
  const portLocation = Number(handle);

  // If this is a subnetwork node, resolve to internal node
  if (skippedSubnetworkNodes.has(nodeId)) {
    const mappedPorts = subnetworkPortMap[nodeId];
    const resolved = mappedPorts ? mappedPorts[portLocation] : undefined;
    
    if (!resolved) {
      logger.warn(`Missing subnetwork port mapping for node ${nodeId}`);
      return null;
    }
    
    return {
      ...resolved,
      nodeName: resolved.internalNodeName,  // Document ID used by solver
      portName: resolved.portName,
    };
  }

  // Regular node resolution...
  const nodeName = map_models[nodeId];
  const portEntry = map_ports[nodeId]?.[portLocation];
  
  return { nodeName, portName: portEntry[0], ... };
};
```

### 2.5 Translation Parameter Generation

When generating TPS specs (translation parameters) for subnetwork nodes, the translation system:

1. **Skips** creating explicit nodes for subnetwork wrappers in the solver output
2. **Resolves** all edges through the subnetwork port map to connect directly to internal nodes
3. **Generates** stream connectivity that connects external edges to internal nodes
4. **Propagates** all port variables from internal nodes to the solver

Example edge processing:

```typescript
for (let i = 0; i < canvasEdges.length; i++) {
  const edge = canvasEdges[i];
  const sourceId = edge?.source;
  const targetId = edge?.target;
  const sourceHandle = edge?.sourceHandle;
  const targetHandle = edge?.targetHandle;

  // Both resolveEndpoint calls handle subnetwork expansion
  const sourceResolved = resolveEndpoint(sourceId, sourceHandle);
  const targetResolved = resolveEndpoint(targetId, targetHandle);

  if (!sourceResolved || !targetResolved) continue;

  // Create stream connectivity using the resolved (internal) endpoints
  const stream_connect_entry: stream_connect = {
    source_node: sourceResolved.nodeName,      // Internal node
    terminal_node: targetResolved.nodeName,    // Internal node
    source_port: sourceResolved.portName,
    terminal_port: targetResolved.portName,
    // ... other fields
  };
  
  stream_connectivity.push(stream_connect_entry);
}
```

### 2.6 Complete Translation Flow

```
User Diagram with Subnetwork Node
    ↓
buildSubnetworkPortMap()
    ↓ (builds internal resolution map)
Process Canvas Nodes
    ↓
isSubnetworkInstanceNode() → Skip wrapper (mark in skippedSubnetworkNodes)
    ↓
Process Canvas Edges
    ↓
resolveEndpoint() → Uses subnetworkPortMap to find internal nodes
    ↓
Generate Stream Connectivity for Internal Nodes
    ↓
Generate TPS Specs (only for regular + internal nodes)
    ↓
Output Parameters (for solver)
```

---

## 3. How We Reverse-Translate Results During Computation

### 3.1 Computation Result Flow

After the solver computes, results are returned containing computed values for nodes. The reverse-translation process must:

1. **Update** internal nodes with their computed values
2. **Backpropagate** values from internal nodes to wrapper nodes
3. **Persist** updates to both instance and parent diagrams

### 3.2 Result Structure

Results from the solver contain `tps_specs` array:

```typescript
interface SolverResult {
  tps_specs: [{
    network: string;           // Network name
    node: string;              // Node name (document ID)
    port: string;              // Port name
    port_var_name: string;     // Variable name (e.g., "Cp")
    machine_generated_values: number[] | Record<string, number>;
    from_tp: number;
    to_tp: number;
    value?: number;            // For single TP
  }];
}
```

### 3.3 Reverse Translation Function

The `updateCanvasAndParametersFromOutput` function processes solver results:

```typescript
export function updateCanvasAndParametersFromOutput(
  canvasJson: AnyDict,
  parameterJson: AnyDict,
  outputJson: AnyDict,
  nodeCacheData?: Record<string, NodeCacheEntry>,
  tpNodeVers: TpNodeVer[] = []
): {
  canvasJson: AnyDict;
  parameterJson: AnyDict;
  updatedNodeIds: string[];
  updatedDocumentIds: string[];
  generatedTpChanges: TpChange[];
} {
  // 1. Parse output specs
  const outputSpecs: OutputSpec[] = outputJson["tps_specs"].map(
    (spec) => new OutputSpec(spec)
  );

  // 2. For each result, resolve node and update values
  for (const spec of outputSpecs) {
    const values = spec.machine_generated_values;

    // Update parameterJson's tps_specs with computed values
    updateParameterValue(spec.node, spec.port, spec.port_var, values, tpsSpecs);

    // Update canvasJson's nodes with computed values
    updateCanvasValue(
      spec.node,
      spec.port,
      spec.port_var,
      values,
      nodes,
      nodeCacheData,
      tpNodeVers,
      generatedTpChanges,
      updatedNodeIds,
      documentIdToNodeId,
      nodeIdToDocumentId,
      updatedDocumentIds
    );
  }

  return {
    canvasJson,
    parameterJson,
    updatedNodeIds: Array.from(updatedNodeIdSet),
    updatedDocumentIds: Array.from(updatedDocumentIdSet),
    generatedTpChanges
  };
}
```

### 3.4 Updating Canvas Values

The `updateCanvasValue` function updates node model versions with computed values:

```typescript
function updateCanvasValue(
  node_name: string,           // From solver result (document ID)
  port_name: string,
  port_var_name: string,
  values: MachineGeneratedValues,
  nodes: AnyDict[],
  nodeCacheData: Record<string, NodeCacheEntry>,
  tpNodeVers: TpNodeVer[]
) {
  // 1. Resolve document ID to ReactFlow node ID
  let resolvedNodeKey = documentIdToNodeId?.get(node_name) ?? node_name;

  // 2. Find matching node in canvas
  const targetNode = nodes.find(n => n.id === resolvedNodeKey);
  if (!targetNode) return;

  // 3. Update port variable values
  const portVar = targetNode.data.model.modelVersion.ports_var.find(
    pv => pv.port_name === port_name && pv.port_var_name === port_var_name
  );

  if (portVar?.model_var_object?.[0]) {
    portVar.model_var_object[0].base_unit_default_value = values[0];
    portVar.model_var_object[0].is_computed = true;
  }
}
```

### 3.5 Backpropagation from Instance to Parent

The critical step for subnetworks is **backpropagation**: after the instance diagram is computed, values must propagate back to the wrapper node:

```typescript
const backpropagateFromInstanceToParent = (
  instanceDiagramId: string,
  parentConnections: AnyDict | undefined,
  instanceCanvas: AnyDict,
  parentCanvas: AnyDict,
  nodeCacheData: NodeCacheMap
) => {
  if (!parentConnections?.wrapperNodeId) {
    logger.warn(`No parentConnections for instance ${instanceDiagramId}`);
    return;
  }

  const wrapperNodeId = parentConnections.wrapperNodeId;
  const externalPorts = parentConnections.externalPorts;

  // Get wrapper node's model version from cache
  const wrapperModelVersion = getCachedModelVersion(wrapperNodeId, nodeCacheData);
  if (!wrapperModelVersion?.ports_var) return;

  // For each external port mapping
  Object.entries(externalPorts).forEach(([externalPortLocationStr, portInfo]) => {
    const internalNodeId = portInfo.mapped?.internalNodeId;
    const internalPortLocation = portInfo.mapped?.port_location;
    const externalPortLocation = Number(externalPortLocationStr);

    if (!internalNodeId || !internalPortLocation) return;

    // Get internal node's computed values
    const internalModelVersion = getCachedModelVersion(internalNodeId, nodeCacheData);
    const internalPortVars = internalModelVersion?.ports_var?.filter(
      (pv) => pv.port_location === internalPortLocation
    ) || [];

    // Find wrapper node's corresponding port vars
    const externalPortVars = wrapperModelVersion.ports_var.filter(
      (pv) => pv.port_location === externalPortLocation
    );

    // Copy computed values from internal to wrapper
    internalPortVars.forEach((internalPortVar) => {
      const internalModelVarObject = internalPortVar?.model_var_object?.[0];
      if (!internalModelVarObject) return;

      const matchingExternalPortVar = externalPortVars.find(
        (epv) => epv.port_var_name === internalPortVar.port_var_name
      ) ?? externalPortVars[0];

      const externalModelVarObject = matchingExternalPortVar?.model_var_object?.[0];
      if (!externalModelVarObject) return;

      // Copy all computed fields
      copyPortVarValues(externalModelVarObject, internalModelVarObject);

      logger.info(
        `Backpropagated ${internalPortVar.port_var_name} from ` +
        `internal node ${internalNodeId} to wrapper ${wrapperNodeId}`
      );

      nodesToPersist.add(wrapperNodeId);
    });
  });
};
```

### 3.6 Complete Reverse-Translation Flow

```
Computation Result from Solver
    ↓
handleComputationSuccess()
    ↓
Collect instance diagram IDs from base canvas
    ↓ (subnetwork nodes reference instance diagrams)
Load instance + parent diagram data
    ↓
updateCanvasAndParametersFromOutput()
    ↓ (for base diagram)
Update internal nodes with computed values
    ↓
Load instance diagram caches + parentConnections
    ↓
For each instance diagram:
    ├─ updateCanvasAndParametersFromOutput() [instance canvas]
    │   ↓
    │   Update instance nodes
    ├─ backpropagateFromInstanceToParent()
    │   ↓
    │   Copy values from internal → wrapper node in parent
    ↓
Load parent diagrams (if hierarchy exists)
    ↓
Repeat backpropagation for parent's wrapper nodes
    ↓
Persist all updated nodes to database
```

### 3.7 ParentConnections Metadata

Each instance diagram stores `parentConnections` for backpropagation:

```typescript
interface ParentConnections {
  wrapperNodeId: string;           // The wrapper node ID in parent diagram
  parentDiagramId: string;         // The parent diagram ID
  externalPorts: {
    [portLocation: string]: {
      isConnected: boolean;
      mapped?: {
        internalNodeId: string;    // Which internal node provides this port
        port_location: number;     // Port location on internal node
        port_type: number;
        port_class: string;
      };
    };
  };
}
```

This metadata is automatically populated when instance diagrams are created and enables the system to know:
- Where to find the wrapper node in the parent
- How each port on the wrapper maps to internal nodes
- How to propagate computed values back up the hierarchy

---

## 4. Key Design Patterns

### 4.1 Port Mapping Pattern
- **External Interface**: Ports on wrapper node (port_location 1, 2, 3, ...)
- **Internal Resolution**: Each external port maps to a specific (nodeId, port_location) on an internal node
- **Solver Translation**: External ports are resolved to internal nodes before sending to solver

### 4.2 Document ID vs ReactFlow ID
- **ReactFlow ID**: Used in UI canvas for node identification
- **Document ID**: Used in solver and database persistence
- **Resolution**: `documentIdToNodeId` map bridges the two

### 4.3 Hierarchical Computation
- Subnetwork nodes are **expanded** during translation (not included in solver as wrapper)
- Internal networks are computed with their own TPS specs
- Values **backpropagate** from computed internal nodes to wrapper nodes

### 4.4 Caching Strategy
- `NodeCacheMap` stores all node information for quick lookup
- Prevents repeated database queries during translation/reverse-translation
- Includes ReactFlow ID → Document ID → ModelVersion mappings

---

## 5. Example Workflow

**User creates a subnetwork blueprint:**
1. User selects nodes in a diagram (e.g., Pump, Mixer, Heat Exchanger)
2. User exposes 3 external ports (inlet, outlet, thermal)
3. System creates `PortMapping` array linking external ports to internal nodes
4. Creates `SubnetworkBlueprint` with these mappings and the diagram as `blueprintDiagramId`

**User adds subnetwork instance to parent diagram:**
1. Creates a node with `data.model.diagramId` = instance diagram ID
2. Sets `data.model.portsMapping` = the blueprint's port mappings
3. Connects edges to external ports on the wrapper node

**During computation:**
1. `buildSubnetworkPortMap` resolves all external→internal port mappings
2. `translation()` expands subnetwork edges to internal nodes
3. Solver computes with only internal nodes (no wrapper)
4. `handleComputationSuccess()` processes results
5. `updateCanvasAndParametersFromOutput()` updates instance diagrams
6. `backpropagateFromInstanceToParent()` copies values to wrapper nodes
7. Database persists all updated diagrams

---

## 6. Duplicate / Export / Import Behavior (Issue 28)

### 6.1 Export Snapshot Contract

Subnetwork-aware export uses `GET /api/data/diagrams/:diagramId/export` and returns a `FullNetworkSnapshot` payload.

For subnetworks, the payload includes:
- `subnetworkBlueprints` (referenced blueprint metadata)
- `subnetworkInstances` (instance diagram data used by wrappers), including:
  - instance canvas
  - instance nodes
  - `tpNodeVers` and `tpChanges`
  - `parentConnections`
  - optional instance snapshot

This is the data required to rebuild wrapper-instance links during import/duplicate.

### 6.2 Import Restore Rules

Import uses `POST /api/data/diagrams/import` and restores:
1. Parent diagram and node IDs (with remap)
2. TP data (with remap)
3. Subnetwork instances from `snapshot.subnetworkInstances`
4. Wrapper node `diagramId` references to new instance IDs

Safety guard:
- If a wrapper references an instance ID that is missing from `subnetworkInstances`, import returns `400` with `missingInstanceIds`.
- This avoids silent partial import with broken wrapper links.

### 6.3 Duplicate Isolation Rules

Duplicate uses `POST /api/data/diagrams/:diagramId/duplicate`.

Current behavior:
1. Build snapshot-like data from source diagram.
2. Recreate parent diagram with remapped IDs.
3. For each wrapper node, create a fresh instance diagram (no shared old instance reference).
4. Prefer cloning from exported `subnetworkInstances` data when available.
5. Fallback to blueprint-based instance creation when instance payload is unavailable.
6. Remap wrapper `portsMapping` and instance `parentConnections`.
7. Preserve nodes that were added inside instance diagrams after original snapshot creation.

Result:
- Copied wrappers point to copied instances.
- Parent and instance mappings stay compute-ready after duplication.

---

## 7. Files Involved

| File | Role |
|------|------|
| `frontend/src/components/header-bar/header-buttons/save-as-subnetwork.tsx` | Create/update blueprints |
| `backend/routes/dataRoutes.ts` | CRUD endpoints for blueprints |
| `backend/utils/translation.ts` | Port mapping + edge expansion |
| `backend/utils/reverseTranslation.ts` | Update canvas from results |
| `backend/services/computationTaskHandler.ts` | Backpropagation logic |
| `frontend/src/models/domain.ts` | Type definitions |
