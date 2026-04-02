# canvasSlice (Redux)

## Overview

The `canvasSlice` is the central Redux slice that manages the entire diagram editing session state. It tracks:

- **Diagram metadata** (name, description, verification status, type)
- **Computation state** (status, processing flags, results)
- **Node data** (names, rotations, parameters, port mappings)
- **Subnetwork data** (parent connections, blueprint names)
- **User edits** (parameter values, specs, computed flags)

**Location:** `src/src/frontend/src/features/canvas/canvasSlice.ts`

---

## 1. State Shape

### 1.1 Complete State Structure

```typescript
interface CanvasState {
  // --- Diagram Metadata ---
  canvasName: string;                    // User-provided diagram name
  description: string;                   // Diagram description
  verified: boolean;                     // Diagram verification status
  type: number;                          // 0=regular, 1=subnetwork blueprint, 2=instance
  
  // --- Node Parameters ---
  nodeParameters: NodeParameters;        // Map of computed/edited port variable values
  streamParameters: StreamParameters;    // Stream-related computed values
  
  // --- Computation State ---
  computationStatus: 'idle' | 'waiting' | 'computing' | 'failed' | 'aborted' | 'timeout' | 'success';
  isComputationProcessing: boolean;      // Flag for ongoing computation
  lastUpdated?: number;                  // Timestamp of last computation result
  
  // --- Session Data ---
  currentDiagramId?: string;             // ID of currently open diagram
  nodes?: Node[];                        // List of nodes in current diagram
  nodeNames: string[];                   // Names of all nodes (for UI)
  nodeRotations: Record<string, number>; // Rotation states (0-3)
  
  // --- Subnetwork Data ---
  blueprintNames: string[];              // Names of saved blueprints
  portMappings: Record<string, PortMapping>;  // Port connectivity for subnetworks
  parentConnections: ParentConnections;  // Mapping to parent diagram for instances
}
```

### 1.2 Key Types

#### ComputedNodeParameter

```typescript
interface ComputedNodeParameter {
  value: number | null;           // The computed or user-entered value
  is_computed: boolean;           // True if value came from solver
  is_human_input: boolean;  // True if user edited it
  spec?: string | null;           // Specification (e.g., "<=100", ">=0")
  diagramId?: string;             // Diagram context (for multi-diagram scenarios)
  timerPeriodId?: string;         // Time period ID (for time-period-specific values)
  unit?: string;                  // Unit of measurement
}

// Example in nodeParameters:
// "BASE_TP-node-abc-portvar-1": {
//   value: 75.5,
//   is_computed: true,
//   is_human_input: false,
//   spec: "<=100",
//   unit: "kg/s"
// }
```

#### Node

```typescript
interface Node {
  node_id: string;       // ReactFlow node ID
  node_name: string;     // Display name in UI
  model_id: string;      // Model type ID (links to domain model)
  model_name: string;    // Model name for display
  modelVersion?: any;    // Base time period model version (for viewer)
  timePeriods?: any[];   // Multi-TP model versions (for viewer)
}
```

#### PortMapping

```typescript
interface PortMapping {
  nodeId: string;              // Internal node ID (for subnetwork)
  port_location: number;       // Port number (1, 2, 3, ...)
  port_type: number;           // 1=inlet, 2=outlet, 3=info, 4=electric
  port_class: string;          // Classification ("inlet", "outlet", etc.)
  isConnected?: boolean;       // Whether port has connections
  instance_port_id?: string;   // ID for instance diagram ports
}
```

#### ParentConnections

```typescript
interface ParentConnections {
  wrapperNodeId?: string;      // Wrapper node ID in parent diagram
  parentDiagramId?: string;    // Parent diagram ID
  externalPorts: {             // Mapping of wrapper ports to internal nodes
    [portLocation: string]: {
      isConnected: boolean;
      mapped?: {
        port_location?: number;
        port_type?: number;
        port_class?: string;
      };
    };
  };
  edges: Array<{               // Edges connected to wrapper externally
    id: string;
    source: string;
    target: string;
    sourceHandle?: string | number | null;
    targetHandle?: string | number | null;
  }>;
}
```

---

## 2. NodeParameters Key Format

### 2.1 Composite Key Structure

NodeParameters use a composite key format to uniquely identify each parameter:

```
${timePeriodId}-${nodeId}-${portVarId}
```

**Examples:**
- `BASE_TP-node-abc-portvar-1` - Base time period, node abc, port var 1
- `TP-2024-Dec-node-abc-portvar-1` - Custom time period, node abc, port var 1
- `1-node-xyz-portvar-5` - Time period 1, node xyz, port var 5

### 2.2 Key Components

| Component | Purpose | Example |
|-----------|---------|---------|
| `timePeriodId` | Identifies time period | `BASE_TP`, `1`, `TP-2024-Dec` |
| `nodeId` | ReactFlow node ID | `node-abc`, `node-xyz` |
| `portVarId` | Port variable ID | `portvar-1`, `portvar-5` |

### 2.3 Usage in Code

```typescript
// Setting a parameter after user edits
dispatch(updateComputationResults({
  nodeParameters: {
    'BASE_TP-node-abc-portvar-1': {
      value: 50,
      is_computed: false,
      is_human_input: true,
      spec: '<=100'
    }
  },
  streamParameters: {},
  diagramId: 'diagram-xyz',
  node_id: 'node-abc'
}));

// Deleting parameters for a specific node/time period
dispatch(deleteNodeParametersByTpIdNodeId({
  node_id: 'node-abc',
  tpId: 'BASE_TP'
}));
```

---

## 3. Computation Status Lifecycle

### 3.1 Status Values

```
'idle'       → No computation running
   ↓
'waiting'    → Queued, waiting for computation server
   ↓
'computing'  → Currently computing
   ↓
'success'    ✓ Computation completed successfully
'failed'     ✗ Computation failed with error
'aborted'    ✗ User killed the computation
'timeout'    ✗ Exceeded max computation time
```

### 3.2 Status Transitions

```typescript
// User initiates computation
dispatch(setComputationStatus('waiting'));
dispatch(setIsComputationProcessing(true));

// Server starts computing
dispatch(setComputationStatus('computing'));

// Computation finishes
dispatch(updateComputationResults({
  nodeParameters: { /* results */ },
  streamParameters: {},
  diagramId: 'diagram-id',
  node_id: 'node-id'
}));
dispatch(setComputationStatus('success'));
dispatch(setIsComputationProcessing(false));
```

### 3.3 Status-Dependent UI

Components check `computationStatus` to:
- **Disable save button** during `'waiting'` or `'computing'`
- **Show loading spinner** during `'computing'`
- **Display result message** for `'success'` or `'failed'`
- **Show error details** for `'aborted'` or `'timeout'`

---

## 4. Actions (Synchronous Reducers)

### 4.1 Diagram Metadata

```typescript
// Update diagram name
dispatch(updateCanvasName('New Diagram Name'));

// Update diagram description
dispatch(updateDescription('This is a detailed description'));

// Set verification status
dispatch(setVerified(true));

// Mark as subnetwork blueprint
dispatch(setDiagramType(1));

// Clear all metadata
dispatch(clearCanvasName());
dispatch(clearDescription());
```

### 4.2 Computation State

```typescript
// Set computation status
dispatch(setComputationStatus('computing'));

// Flag that computation is actively running
dispatch(setIsComputationProcessing(true));

// Clear all computation results
dispatch(clearComputationResults());
```

### 4.3 Node Names

```typescript
// Add a single node name
dispatch(addNodeName('Pump'));
dispatch(addNodeName('Heat Exchanger'));

// Remove a node name
dispatch(removeNodeName('Pump'));

// Initialize from array (deduplicates automatically)
dispatch(initializeNodeNames(['Pump', 'Mixer', 'Pump'])); // Results in ['Pump', 'Mixer']

// Clear all names
dispatch(clearNodeNames());
```

### 4.4 Node Rotations

```typescript
// Set rotation for a specific node (0-3)
dispatch(setNodeRotation({ nodeId: 'node-abc', rotation: 1 }));
dispatch(setNodeRotation({ nodeId: 'node-xyz', rotation: 2 }));

// Clear rotation for a node
dispatch(clearNodeRotation('node-abc'));

// Clear all rotations
dispatch(clearAllNodeRotations());
```

### 4.5 Diagram Nodes

```typescript
// Set the nodes for the current diagram
dispatch(setDiagramNodes([
  {
    node_id: 'node-1',
    node_name: 'Pump',
    model_id: 'pump-model',
    model_name: 'Centrifugal Pump'
  },
  {
    node_id: 'node-2',
    node_name: 'Mixer',
    model_id: 'mixer-model',
    model_name: 'Static Mixer'
  }
]));

// Clear nodes
dispatch(clearDiagramNodes());
```

### 4.6 Current Diagram Context

```typescript
// Track which diagram is currently open
dispatch(setCurrentDiagramId('diagram-12345'));

// Clear the current diagram context
dispatch(clearCurrentDiagramId());
```

### 4.7 Blueprint Management

```typescript
// Set all known blueprint names
dispatch(setBlueprintNames(['Pump Subsystem', 'Heat Exchanger Pack']));

// Add a new blueprint name
dispatch(addBlueprintName('New Blueprint'));

// Remove a blueprint
dispatch(deleteBlueprintName('Old Blueprint'));

// Clear all blueprints
dispatch(clearBlueprintNames());
```

### 4.8 Port and Parent Mappings

```typescript
// Set port mappings for subnetwork nodes
dispatch(setPortMappings({
  'external-port-1': {
    nodeId: 'internal-node-1',
    port_location: 2,
    port_type: 1,
    port_class: 'inlet',
    isConnected: true
  },
  'external-port-2': {
    nodeId: 'internal-node-2',
    port_location: 3,
    port_type: 2,
    port_class: 'outlet'
  }
}));

// Set parent connections (for instance diagrams)
dispatch(setParentConnections({
  wrapperNodeId: 'wrapper-node-1',
  parentDiagramId: 'parent-diagram-1',
  externalPorts: {
    '1': { isConnected: true, mapped: { port_location: 2 } }
  },
  edges: []
}));

// Clear port mappings
dispatch(clearPortMappings());
dispatch(clearParentConnections());
```

### 4.9 Node ID Renaming

This is a complex action that updates **all references** to a node ID:

```typescript
dispatch(renameNodeId({
  oldNodeId: 'temp-node-1',
  newNodeId: '550e8400-e29b-41d4-a716-446655440000'
}));

// What gets updated:
// 1. nodeParameters keys: 'BASE_TP-temp-node-1-*' → 'BASE_TP-550e8400-*'
// 2. nodeRotations: nodeRotations['temp-node-1'] → nodeRotations['550e8400-*']
// 3. nodes list: node.node_id = 'temp-node-1' → 'tail550e8400-*'
// 4. portMappings: portMappings['temp-node-1'] → portMappings['550e8400-*']
```

**Implementation Details:**

```typescript
renameNodeId: (state, action: PayloadAction<{ oldNodeId: string; newNodeId: string }>) => {
  const { oldNodeId, newNodeId } = action.payload;

  if (!oldNodeId || !newNodeId || oldNodeId === newNodeId) {
    return;
  }

  // 1. Update nodeParameters keys
  const updatedParameters: Record<string, any> = {};
  Object.entries(state.nodeParameters).forEach(([key, value]) => {
    const segments = key.split('-');
    if (segments.length >= 3 && segments[1] === oldNodeId) {
      segments[1] = newNodeId;  // Replace node ID in composite key
      updatedParameters[segments.join('-')] = value;
    } else {
      updatedParameters[key] = value;
    }
  });
  state.nodeParameters = updatedParameters;

  // 2. Update nodeRotations
  if (state.nodeRotations[oldNodeId] !== undefined) {
    state.nodeRotations[newNodeId] = state.nodeRotations[oldNodeId];
    delete state.nodeRotations[oldNodeId];
  }

  // 3. Update nodes list
  state.nodes = state.nodes?.map((node) =>
    node.node_id === oldNodeId ? { ...node, node_id: newNodeId } : node
  );

  // 4. Update portMappings keys
  if (state.portMappings[oldNodeId]) {
    state.portMappings[newNodeId] = state.portMappings[oldNodeId];
    delete state.portMappings[oldNodeId];
  }
}
```

---

## 5. Extra Actions (Async/Complex)

### 5.1 updateComputationResults

Called when solver finishes successfully:

```typescript
export const updateComputationResults = createAction<{
  nodeParameters: Record<string, ComputedNodeParameter>;
  streamParameters: any;
  diagramId: string;
  node_id: string;
}>('canvas/updateComputationResults');

// Usage:
dispatch(updateComputationResults({
  nodeParameters: {
    'BASE_TP-node-1-portvar-1': {
      value: 75.5,
      is_computed: true,
      is_human_input: false,
      spec: '<=100'
    },
    'BASE_TP-node-1-portvar-2': {
      value: 50.0,
      is_computed: true,
      is_human_input: false
    }
  },
  streamParameters: {
    'stream-1': { density: 1000, viscosity: 0.001 }
  },
  diagramId: 'diagram-123',
  node_id: 'node-1'
}));
```

**Handler (in extraReducers):**

```typescript
builder.addCase(updateComputationResults, (state, action) => {
  // Merge new parameters with existing ones
  state.nodeParameters = {
    ...state.nodeParameters,
    ...action.payload.nodeParameters  // Overwrites matching keys
  };
  state.streamParameters = {
    ...state.streamParameters,
    ...action.payload.streamParameters
  };
  state.lastUpdated = Date.now();  // Track when results arrived
});
```

### 5.2 deleteNodeParametersByTpIdNodeId

Called when removing time periods or nodes:

```typescript
export const deleteNodeParametersByTpIdNodeId = createAction<{
  node_id?: string;
  tpId?: string;
}>('canvas/deleteNodeParametersByTpIdNodeId');

// Usage: Remove all parameters for node-abc in BASE_TP
dispatch(deleteNodeParametersByTpIdNodeId({
  node_id: 'node-abc',
  tpId: 'BASE_TP'
}));

// This deletes all keys matching pattern: 'BASE_TP-node-abc-*'
```

**Handler (in extraReducers):**

```typescript
builder.addCase(deleteNodeParametersByTpIdNodeId, (state, action) => {
  const { node_id, tpId } = action.payload;

  if (!node_id || !tpId) return;

  const prefix = `${tpId}-${node_id}-`;
  const beforeKeys = Object.keys(state.nodeParameters).length;

  // Delete all keys starting with the prefix
  for (const key of Object.keys(state.nodeParameters)) {
    if (key.includes(prefix)) {
      delete state.nodeParameters[key];
    }
  }

  const afterKeys = Object.keys(state.nodeParameters).length;
  console.log(`Removed ${beforeKeys - afterKeys} parameters for node ${node_id}`);
});
```

---

## 6. Selectors

Selectors are memoized functions that extract data from Redux state:

```typescript
// Get all diagram nodes
const diagramNodes = useSelector(selectDiagramNodes);
// Result: Node[]

// Get all node names
const nodeNames = useSelector(selectNodeNames);
// Result: string[]

// Get all node rotations
const rotations = useSelector(selectNodeRotations);
// Result: Record<string, number>

// Get rotation for a specific node
const nodeRotation = useSelector((state) => selectNodeRotation(state, 'node-abc'));
// Result: number (0-3)
```

---

## 7. Usage Examples

### 7.1 User Edits a Port Variable

```typescript
// User changes a port variable value in the modal
function handlePortVarChange(nodeId: string, portVarId: string, newValue: number) {
  const tpId = 'BASE_TP';
  const paramKey = `${tpId}-${nodeId}-${portVarId}`;
  
  dispatch(updateComputationResults({
    nodeParameters: {
      [paramKey]: {
        value: newValue,
        is_computed: false,        // User edited, not from solver
        is_human_input: true, // User is now "responsible" for this value
        spec: currentSpec,
        unit: 'kg/s'
      }
    },
    streamParameters: {},
    diagramId: currentDiagramId,
    node_id: nodeId
  }));
}
```

### 7.2 Computation Completes

```typescript
// Results arrive from solver callback
function handleComputationSuccess(results) {
  // Build nodeParameters from results
  const nodeParams = {};
  results.tps_specs.forEach(spec => {
    const key = `${spec.from_tp}-${spec.node_id}-${spec.port_var_id}`;
    nodeParams[key] = {
      value: spec.value,
      is_computed: true,
      is_human_input: false,
      spec: spec.spec,
      unit: spec.unit
    };
  });
  
  // Dispatch to Redux
  dispatch(updateComputationResults({
    nodeParameters: nodeParams,
    streamParameters: {},
    diagramId: diagramId,
    node_id: spec.node_id
  }));
  
  dispatch(setComputationStatus('success'));
  dispatch(setIsComputationProcessing(false));
}
```

### 7.3 Handling Node ID Replacements

```typescript
// After saving, backend returns old → new ID mappings
function handleNodeIdReplacements(replacements) {
  replacements.forEach(({ oldNodeId, newNodeId }) => {
    dispatch(renameNodeId({ oldNodeId, newNodeId }));
    // This updates nodeParameters, rotations, nodes, and portMappings
  });
}
```

### 7.4 Switching to a New Diagram

```typescript
function handleOpenDiagram(diagramId) {
  // Clear previous diagram state
  dispatch(clearComputationResults());
  dispatch(clearCurrentDiagramId());
  dispatch(clearDiagramNodes());
  dispatch(clearNodeNames());
  
  // Set new diagram
  dispatch(setCurrentDiagramId(diagramId));
  dispatch(setDiagramNodes(loadedNodes));
  dispatch(initializeNodeNames(loadedNodes.map(n => n.node_name)));
}
```

---

## 8. State Dependencies and Relationships

### 8.1 nodeParameters ↔ nodeCache

- **nodeParameters**: Redux state, user edits + computation results
- **nodeCache**: Separate Redux slice, stores ModelVersion objects

When saving:
1. Read `nodeParameters` from canvas slice
2. Load `ModelVersion` from `nodeCache` 
3. **Merge** parameters into ModelVersion
4. Save combined ModelVersion to backend

```typescript
// In save-util.tsx
const reduxParam = nodeParameters[paramKey];
if (reduxParam) {
  // Merge Redux value into modelVersion
  modelVersion.ports_var[i].model_var_object[0].value = reduxParam.value;
  modelVersion.ports_var[i].model_var_object[0].is_computed = reduxParam.is_computed;
}
```

### 8.2 parentConnections ↔ Instance Diagrams

- **parentConnections**: Stored in canvas slice for instance diagrams
- **Links**: Wrapper node in parent → internal nodes in instance

Used during:
- **Save**: Sending parentConnections to backend to create instance diagram
- **Computation**: Backpropagating results from instance to parent wrapper node
- **Display**: Showing which external ports connect to which internal nodes

---

## 9. Debugging and Logging

The slice includes logging in several reducers:

```typescript
// In setComputationStatus reducer
console.log('[canvasSlice] setComputationStatus called with:', action.payload);

// In setIsComputationProcessing reducer
console.log('[canvasSlice] setIsComputationProcessing called with:', action.payload);

// In deleteNodeParametersByTpIdNodeId
console.log(`[Redux] Deleting nodeParameters for node_id=${node_id}, tpId=${tpId}`);
console.log(`[Redux] Removed ${beforeKeys - afterKeys} parameters for node ${node_id}`);
```

Enable/disable by searching for `console.log` calls in the slice.

---

## 10. Common Patterns and Best Practices

### 10.1 Deduplication

When adding items to arrays, deduplication is automatic:

```typescript
addNodeName: (state, action) => {
  const newNames = [...new Set([...state.nodeNames, action.payload])];
  state.nodeNames = newNames;  // Duplicates removed
}
```

### 10.2 Safe Key Updates

When renaming node IDs, always check that IDs aren't identical:

```typescript
if (!oldNodeId || !newNodeId || oldNodeId === newNodeId) {
  return;  // Exit early if no-op
}
```

### 10.3 Composite Key Parsing

When working with nodeParameters keys, split by `-`:

```typescript
const [tpId, nodeId, ...portVarIdParts] = key.split('-');
const portVarId = portVarIdParts.join('-');  // Port var ID might contain dashes
```

### 10.4 Merging vs Replacing

- `updateComputationResults`: **Merges** (spread operator)
- `setDiagramNodes`: **Replaces** (direct assignment)
- `updateCanvasName`: **Replaces** (direct assignment)

---

## 11. Related Slices

| Slice | Purpose | Integration |
|-------|---------|-------------|
| `nodeCacheSlice` | Stores ModelVersion objects | Merge during save |
| `domainSlice` | Domain models and metadata | Model lookups |
| `alertsSlice` | User alerts/messages | Status notifications |
| `savedSlice` | Save/unsaved state | Tracks changes |

---

## 12. Files Using canvasSlice

| File | Usage |
|------|-------|
| `save-util.tsx` | Read nodeParameters for saving |
| `modal/tabs/node-tab.tsx` | Update nodeParameters on edit |
| `modal/tabs/time-period-tab.tsx` | Manage time-period-specific parameters |
| `computation/compute-service.ts` | Update results on computation finish |
| `node/nodeCacheService.ts` | Coordinate with nodeCache |


