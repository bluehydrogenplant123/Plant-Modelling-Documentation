# Dashboard Component (dashboard.tsx)

## Overview

The `Dashboard` is the main landing page after user authentication. It serves as the hub for:

- **Creating new diagrams** with a selected domain and calculation type
- **Managing existing diagrams** (verified, unverified, and subnetwork blueprints)
- **Importing/exporting diagrams** as JSON files
- **Handling diagram lifecycle** (load, delete, export)

**Location:** `src/src/frontend/src/pages/dashboard.tsx`

---

## 1. Component Purpose and Flow

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Dashboard Component                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────┐    ┌──────────────────────┐   │
│  │  Create New Diagram  │    │ Existing Diagrams    │   │
│  │  (Left Column)       │    │ (Right Column)       │   │
│  │                      │    │                      │   │
│  │ - Name input         │    │ - Verified list      │   │
│  │ - Domain selector    │    │ - Unverified list    │   │
│  │ - CalcType selector  │    │ - Blueprints         │   │
│  │ - Description        │    │                      │   │
│  │ - Create button      │    │ - Load, Export,      │   │
│  │ - Import button      │    │   Delete buttons     │   │
│  │ - Logout button      │    │                      │   │
│  └──────────────────────┘    └──────────────────────┘   │
│           │                           │                   │
│           └───────────┬───────────────┘                   │
│                       │                                   │
│                 Redux Dispatch                            │
│          (canvasSlice, alertsSlice)                       │
│                       │                                   │
│           ┌───────────┴───────────┐                       │
│           │                       │                       │
│           ▼                       ▼                        │
│       API Calls              Navigation                   │
│   - POST /diagrams       - /canvas/{domainId}            │
│   - GET /diagrams        - /diagram/{diagramId}          │
│   - GET /domains         - /                             │
│   - GET /subnetworks                                      │
│   - DELETE /diagrams                                      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 1.2 User Workflows

**Workflow 1: Create New Diagram**
```
1. User enters diagram name
   ↓ (validation: uniqueness)
2. User selects domain
   ↓ (loads domain models)
3. User selects calculation type
   ↓
4. User enters description
   ↓
5. Click "Create Diagram"
   ↓ (frontend validation, Redux dispatch, API call)
6. Navigate to /canvas/{domainId}
   ↓
7. Canvas editor opens with empty diagram
```

**Workflow 2: Load Existing Diagram**
```
1. User sees diagram list (Verified/Unverified/Blueprints)
   ↓
2. Click "Load" button
   ↓
3. Fetch diagram data from /api/data/diagrams/{diagramId}
   ↓
4. Redux state populated with diagram data
   ↓
5. Navigate to /diagram/{diagramId}
   ↓
6. Canvas editor opens with loaded diagram
```

**Workflow 3: Import Diagram from JSON**
```
1. User clicks "Import Diagram" button
   ↓
2. File dialog opens (hidden input)
   ↓
3. User selects .json file
   ↓
4. File parsed and validated
   ↓
5. POST to /api/data/diagrams with diagram data
   ↓
6. Optional: Verify if isVerified flag set
   ↓
7. Refresh diagram list
   ↓
8. Show success/error alert
```

**Workflow 4: Delete Diagram**
```
1. User clicks "Delete" button
   ↓
2. Fetch diagram to get node information
   ↓
3. Clean up modelNameMap and Redux nodeNames
   ↓
4. DELETE /api/data/diagrams/{diagramId}
   ↓
5. Refresh diagram list
   ↓
6. Show success/error alert
```

---

## 2. Component State

### 2.1 Local Component State

```typescript
// Form inputs for creating new diagram
const [canvasName, setCanvasName] = useState<string>('');
const [domain, setDomain] = useState<string>('');
const [description, setDescription] = useState<string>('');
const [type, setType] = useState<number>(0);  // 0=regular, 1=blueprint, 2=instance
const [calcType, setCalcType] = useState<string>(currentCalcType);

// Name validation state
const [nameError, setNameError] = useState<string>('');
const [nameTouched, setNameTouched] = useState<boolean>(false);

// Fetched data from backend
const [diagrams, setDiagrams] = useState<Diagram[]>([]);
const [domains, setDomains] = useState<Domain[]>([]);
const [blueprints, setBlueprints] = useState<SubnetworkBlueprint[]>([]);

// File import reference
const fileInputRef = useRef<HTMLInputElement | null>(null);
```

### 2.2 Redux State Integration

```typescript
// From calcType slice
const currentCalcType = useSelector(
  (state: RootState) => state.calcType.type
);

// From auth context
const { user, userId, logout } = useAuth();
const username = user;
const user_id = userId;
```

### 2.3 Data Types

```typescript
interface Domain {
  id: string;
  name: string;
  description: string;
}

interface Diagram {
  id: string;
  name: string;
  description: string;
  domainId: string;
  canvas: {
    nodes?: Array<{
      data?: {
        model?: {
          node_id?: string;
          node_name?: string;
          model_id?: string;
          model_name?: string;
        };
      };
    }>;
  };
  parameters?: Record<string, any>;
  isVerified?: boolean;
  type?: number;  // 0=regular, 1=blueprint
  userId?: string;
  snapshot?: {
    domainId: string;
    data: any;
  };
  parentConnections?: ParentConnections;
}

interface SubnetworkBlueprint {
  id: string;
  model_name: string;
  blueprintDiagramId: string;  // Link to associated diagram
  userId: string;
}
```

---

## 3. Key Functions

### 3.1 Initialization and Data Fetching

#### useEffect - Initialize on Mount

```typescript
useEffect(() => {
  dispatch(clearNodeNames());
  dispatch(clearDiagramNodes());
}, [dispatch]);

// Called once on component mount to clean Redux state
```

#### fetchDomains

```typescript
const fetchDomains = useCallback(async () => {
  try {
    const response = await axios.get<Domain[]>('/api/data/domains');
    setDomains((prev) => {
      // Only update if data actually changed (prevent infinite loops)
      if (JSON.stringify(prev) === JSON.stringify(response.data)) return prev;
      return response.data;
    });
  } catch (error) {
    console.error('Error fetching domains:', error);
  }
}, []);
```

**Purpose:** Fetch all available domains from backend
**Memoization:** Wrapped in `useCallback` to prevent deps array issues
**Deduplication:** Compares JSON before setState to prevent unnecessary re-renders

#### fetchDiagrams

```typescript
const fetchDiagrams = useCallback(async () => {
  try {
    const response = await axios.get<Diagram[]>('/api/data/diagrams');
    setDiagrams((prev) => {
      if (JSON.stringify(prev) === JSON.stringify(response.data)) return prev;
      return response.data;
    });
  } catch (error) {
    console.error('Error fetching diagrams:', error);
  }
}, []);
```

**Purpose:** Fetch all diagrams for current user
**Endpoint:** `GET /api/data/diagrams`
**Filtering:** Done in JSX (isVerified, type)

#### fetchBlueprints

```typescript
const fetchBlueprints = useCallback(async () => {
  try {
    const response = await axios.get<SubnetworkBlueprint[]>('/api/data/subnetworks');
    setBlueprints((prev) => {
      if (JSON.stringify(prev) === JSON.stringify(response.data)) return prev;
      return response.data;
    });
  } catch (error) {
    console.error('Error fetching blueprints:', error);
  }
}, []);
```

**Purpose:** Fetch all subnetwork blueprints
**Endpoint:** `GET /api/data/subnetworks`
**Usage:** Shown in third card (Subnetwork Blueprints)

#### useEffect - Trigger Fetches

```typescript
useEffect(() => {
  fetchDomains();
  fetchDiagrams();
  fetchBlueprints();
}, [fetchDomains, fetchDiagrams, fetchBlueprints]);

// Runs whenever any fetch function reference changes
```

---

### 3.2 Form Input Handlers

#### handleCanvasNameChange

```typescript
const handleCanvasNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const newName = e.target.value;
  setCanvasName(newName);
  setNameError('');  // Clear error on each keystroke
  if (domain) {
    // Store in localStorage as user types
    storeTemporaryData(domain, newName, description);
  }
};
```

**Behavior:**
- Updates local state as user types
- Clears validation error
- Stores temporary data to localStorage

#### handleCanvasNameBlur

```typescript
const handleCanvasNameBlur = () => {
  setNameTouched(true);
  // Check uniqueness only on blur (not on every keystroke)
  if (canvasName && diagrams.some((d) => d.name === canvasName)) {
    setNameError('Diagram name must be unique.');
    setCanvasName('');  // Clear the input
  } else {
    setNameError('');
  }
};
```

**Validation Strategy:**
- Only validate on blur (better UX)
- Check against existing diagram names
- Clear input if duplicate detected
- Show error message

#### handleDomainChange

```typescript
const handleDomainChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
  const newDomain = e.target.value;
  setDomain(newDomain);
  if (newDomain) {
    // Store in localStorage
    storeTemporaryData(newDomain, canvasName, description);
  }
};
```

#### handleDescriptionChange

```typescript
const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  const newDescription = e.target.value;
  setDescription(newDescription);
  if (domain) {
    storeTemporaryData(domain, canvasName, newDescription);
  }
};
```

#### storeTemporaryData

```typescript
const storeTemporaryData = (
  domainId: string,
  canvasName: string,
  description: string
) => {
  const tempData = {
    canvasName,
    description,
    timestamp: Date.now()
  };
  console.log('Dashboard: Storing temporary data:', {
    key: `temp_diagram_${domainId}`,
    data: tempData
  });
  localStorage.setItem(`temp_diagram_${domainId}`, JSON.stringify(tempData));
};
```

**Purpose:** Persist form data to localStorage during editing
**Key Format:** `temp_diagram_${domainId}`
**Use Case:** Recover form data if user navigates away

---

### 3.3 Diagram Creation

#### handleSubmit

```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();

  setNameTouched(true);
  // Validate uniqueness before submit
  if (diagrams.some((d) => d.name === canvasName)) {
    setNameError('Diagram name must be unique.');
    return;
  }

  // Clear any previous state
  dispatch(clearNodeNames());
  dispatch(clearDiagramNodes());

  if (canvasName && domain && calcType) {
    // Clear previous diagram Redux state
    dispatch(clearComputationResults());
    dispatch(clearCurrentDiagramId());
    dispatch(clearCanvasName());
    dispatch(clearDescription());
    
    // Set new diagram state
    dispatch(setCurrentDiagramId(domain));
    dispatch(fetchDomainData(domain));
    dispatch(updateCalcType(calcType as CalcType));
    dispatch(updateCanvasName(canvasName));
    dispatch(updateDescription(description));
    dispatch(setVerified(false));
    dispatch(setDiagramType(type));

    // Navigate to canvas
    navigate(`/canvas/${domain}`);
  } else {
    dispatch(
      showAlertWithTimeout(
        'error',
        'Please provide canvas name, domain, and calculation type.'
      )
    );
  }
};
```

**Validation Flow:**
1. Prevent default form submission
2. Set `nameTouched` to trigger validation UI
3. Check for duplicate names
4. Return early if duplicate found

**Redux Dispatch Chain:**
1. Clear old diagram state (computation results, canvas name, nodes)
2. Set new diagram metadata (name, description, type)
3. Fetch domain data (models, ports)
4. Update calculation type
5. Navigate to canvas editor

**Navigation:** `/canvas/${domain}`

---

### 3.4 Diagram Loading

#### handleLoadDiagram

```typescript
const handleLoadDiagram = async (diagramId: string) => {
  // Clear Redux state for fresh load
  dispatch(clearComputationResults());
  dispatch(clearCurrentDiagramId());
  dispatch(clearCanvasName());
  dispatch(clearDescription());
  dispatch(clearDiagramNodes());
  dispatch(clearParentConnections());
  dispatch(clearNodeNames());

  try {
    // Fetch diagram data
    const response = await axios.get<Diagram>(`/api/data/diagrams/${diagramId}`);
    const diagramData = response.data;
    
    console.log('diagramdata in dashboard', diagramData);

    // Extract node names from canvas
    const nodeNames = diagramData.canvas.nodes?.map(
      (node: any) => node?.data?.model?.node_name
    )
      .filter(Boolean) || [];
    
    // Get parent connections (for instances)
    const parentConnections = diagramData.parentConnections;

    // Update Redux state
    dispatch(initializeNodeNames(nodeNames));
    dispatch(setCurrentDiagramId(diagramId));
    dispatch(setDiagramType(diagramData.type || 0));
    dispatch(setParentConnections(parentConnections));

    // Navigate to diagram editor
    navigate(`/diagram/${diagramId}`);
  } catch (error) {
    console.error('Error loading diagram:', error);
    dispatch(showAlertWithTimeout('error', 'Failed to load diagram.'));
  }
};
```

**Key Steps:**
1. Clear Redux state (fresh slate)
2. Fetch diagram from `/api/data/diagrams/{diagramId}`
3. Extract node names from canvas.nodes
4. Extract parent connections (for subnetwork instances)
5. Populate Redux state
6. Navigate to `/diagram/{diagramId}`

**Why Clear State First:**
- Prevents stale data from previous diagram
- Ensures clean editor experience

---

### 3.5 Diagram Deletion

#### handleDeleteDiagram

```typescript
const handleDeleteDiagram = async (diagramId: string) => {
  try {
    // 1. Fetch diagram to get node info
    const response = await axios.get<{
      canvas?: {
        nodes?: Array<{
          data?: {
            model?: {
              node_id?: string;
              node_name?: string;
            };
          };
        }>;
      };
    }>(`/api/data/diagrams/${diagramId}`);
    const diagramData = response.data;
    
    // 2. Clean up node names from modelNameMap and Redux
    if (diagramData.canvas?.nodes) {
      diagramData.canvas.nodes.forEach((node) => {
        if (node.data?.model?.node_id) {
          modelNameMap.delete(node.data.model.node_id);
        }
        if (node.data?.model?.node_name) {
          dispatch(removeNodeName(node.data.model.node_name));
        }
      });
    }

    // 3. Delete the diagram
    await axios.delete(`/api/data/diagrams/${diagramId}`);
    
    // 4. Refresh list
    await fetchDiagrams();
    
    dispatch(showAlertWithTimeout('info', 'Diagram deleted successfully!'));
  } catch (error) {
    console.error('Error deleting diagram:', error);
    dispatch(showAlertWithTimeout('error', 'Failed to delete diagram.'));
  }
};
```

**Deletion Strategy:**
1. Fetch diagram first (to get node data)
2. Clean up modelNameMap (module-level map)
3. Dispatch Redux removeNodeName for each node
4. DELETE diagram from database
5. Refresh diagram list to reflect deletion
6. Show success/error alert

**Why Cleanup:**
- modelNameMap is global and tracks node name→ID mappings
- Redux nodeNames array needs to stay in sync
- Prevents stale references after deletion

#### handleDeleteSubnetwork

```typescript
const handleDeleteSubnetwork = async (blueprintId: string) => {
  try {
    // Get blueprint data
    const response = await axios.get<SubnetworkBlueprint>(
      `/api/data/subnetworks/${blueprintId}`
    );
    const blueprintData = response.data;

    // Delete subnetwork blueprint
    await axios.delete(`/api/data/subnetworks/${blueprintId}`);
    
    // Also delete associated diagram
    await handleDeleteDiagram(blueprintData.blueprintDiagramId);
    
    // Refresh blueprint list
    await fetchBlueprints();
    
    dispatch(showAlertWithTimeout('info', 'Subnetwork blueprint deleted successfully!'));
  } catch (error) {
    console.error('Error deleting subnetwork blueprint:', error);
    dispatch(showAlertWithTimeout('error', 'Failed to delete subnetwork blueprint.'));
  }
};
```

**Blueprint Deletion:**
1. Fetch blueprint metadata
2. Delete blueprint entry
3. **Also delete** associated diagram (blueprintDiagramId)
4. Refresh blueprint list

**Why Delete Associated Diagram:**
- Blueprints link to an internal diagram (blueprintDiagramId)
- Without cleanup, orphaned diagrams would accumulate in database

---

### 3.6 Diagram Export

#### handleExportDiagram

```typescript
const handleExportDiagram = async (diagramId: string, diagramName?: string) => {
  try {
    // Use full export endpoint (includes subnetwork data)
    const response = await axios.get(`/api/data/diagrams/${diagramId}/export`);
    const snapshotData = response.data;

    // Create filename
    const filename = `${(snapshotData.metadata?.name || diagramName || diagramId).replace(/\\s+/g, '_')}.json`;

    // Convert snapshot JSON blob
    const blob = new Blob([JSON.stringify(snapshotData, null, 2)], {
      type: 'application/json'
    });

    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    dispatch(showAlertWithTimeout('info', 'Diagram exported successfully with all data!'));
  } catch (error) {
    console.error('Error exporting diagram:', error);
    dispatch(showAlertWithTimeout('error', 'Failed to export diagram.'));
  }
};
```

**Export Flow:**
1. Call `GET /api/data/diagrams/{id}/export`
2. Receive `FullNetworkSnapshot` payload
3. Create filename (metadata name fallback to diagram name/id)
4. Create Blob from JSON
5. Create temporary download link
6. Trigger browser download
7. Clean up resources (revoke ObjectURL)

**Snapshot Coverage:**
- Root diagram canvas + nodes + TP records
- `subnetworkBlueprints`
- `subnetworkInstances` (instance canvas/nodes/TP/parentConnections/snapshot)

**Browser Download Technique:**
- Create invisible `<a>` element
- Set href to blob ObjectURL
- Set download attribute to filename
- Programmatically click the link
- Clean up by removing link and revoking URL

---

### 3.7 Diagram Import

#### handleImportDiagram

```typescript
const handleImportDiagram = async (file: File | null) => {
  if (!file) {
    dispatch(showAlertWithTimeout('error', 'No file selected for import.'));
    return;
  }

  try {
    // 1. Read and parse JSON
    const text = await file.text();
    const snapshotData = JSON.parse(text);
    const isNewFormat = snapshotData.version === '1.0.0' && snapshotData.metadata;

    if (isNewFormat) {
      // New snapshot import endpoint
      await axios.post('/api/data/diagrams/import', {
        snapshot: snapshotData,
      });

      if (snapshotData.metadata.isVerified) {
        dispatch(setVerified(true));
        dispatch(showAlertWithTimeout('info', 'Diagram imported and verified!'));
      } else {
        dispatch(showAlertWithTimeout('info', 'Diagram imported successfully with all data!'));
      }
    } else {
      // Legacy import fallback
      const diagramPayload: any = {
        name: snapshotData.name,
        canvas: snapshotData.canvas,
        description: snapshotData.description,
        domainId: snapshotData.snapshot?.domainId,
        calcType: calcType || undefined,
        snapshotData: snapshotData.snapshot?.data,
        isVerified: !!snapshotData.isVerified,
        parameters: snapshotData.parameters,
        type: snapshotData.type,
        userId: snapshotData.userId,
      };

      Object.keys(diagramPayload).forEach((k) => {
        if (diagramPayload[k] === undefined) delete diagramPayload[k];
      });

      if (diagrams.some((d) => d.name === diagramPayload.name)) {
        const randomSuffix = Math.random().toString(36).substring(2, 8);
        diagramPayload.name = `${diagramPayload.name}_${randomSuffix}`;
      }

      const resp = await axios.post('/api/data/diagrams', diagramPayload);
      const respData = resp.data as { diagram: { id: string } };
      const createdId = respData.diagram.id;

      if (diagramPayload.isVerified && createdId) {
        try {
          await axios.patch(`/api/data/diagrams/${createdId}/verify`);
          dispatch(setVerified(true));
          dispatch(showAlertWithTimeout('info', 'Diagram imported and verified!'));
        } catch (err: any) {
          const status = err?.response?.status;
          if (status === 403 || status === 401) {
            dispatch(showAlertWithTimeout(
              'warn',
              'Diagram imported but verification failed: you may not have permission to verify diagrams.'
            ));
          } else {
            dispatch(showAlertWithTimeout('warn', 'Diagram imported but verification attempt failed.'));
          }
        }
      } else {
        dispatch(showAlertWithTimeout('info', 'Diagram imported successfully!'));
      }
    }

    // Refresh diagram list
    await fetchDiagrams();

  } catch (err) {
    console.error('Error importing diagram:', err);
    dispatch(showAlertWithTimeout(
      'error',
      'Failed to import diagram. Check console for details.'
    ));
  } finally {
    // Clear file input
    if (fileInputRef.current) fileInputRef.current.value = '';
  }
};
```

**Import Flow:**
1. Validate file exists
2. Read file as text
3. Parse JSON
4. Detect format:
   - New snapshot format (`version: 1.0.0`) -> `POST /api/data/diagrams/import`
   - Legacy format -> `POST /api/data/diagrams` (+ optional verify)
5. Handle success/warning/error alert
6. Refresh diagram list
7. Clear file input

**Legacy Duplicate Name Handling:**
```
Original: "My Diagram"
Conflict: append "_" + random 6 chars
Result: "My Diagram_abc123"
```

**Verification Logic:**
- New snapshot import keeps `metadata.isVerified` on the import path.
- Legacy import may require a follow-up verify call.

**Import Safety for Subnetworks:**
- New import path may return `400` with `missingInstanceIds` when wrappers reference missing `subnetworkInstances`.
- This fail-fast behavior prevents broken partial imports.

#### onImportFileChange

```typescript
const onImportFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0] ?? null;
  handleImportDiagram(file);
};
```

**Purpose:** Hidden file input change handler

#### openImportDialog

```typescript
const openImportDialog = () => {
  if (fileInputRef.current) fileInputRef.current.click();
};
```

**Purpose:** Programmatically trigger hidden file input click

---

### 3.8 Logout

#### handleLogout

```typescript
const handleLogout = () => {
  dispatch(clearNodeNames());
  logout();
};
```

**Behavior:**
1. Clear Redux nodeNames
2. Call auth context logout (clears tokens, redirects to login)

---

## 4. UI Layout

### 4.1 Left Column: Create New Diagram

**Card Components:**
- **Diagram Name Input** - Text field with uniqueness validation
- **Domain Selector** - Dropdown with available domains
- **Calculation Type Selector** - Dropdown with CALC_TYPES
- **Description Textarea** - Multi-line description input
- **Create Diagram Button** - Triggers handleSubmit
- **Import Diagram Button** - Opens file dialog
- **Logout Button** - Triggers handleLogout

### 4.2 Right Column: Existing Diagrams

**Three Card Sections:**

1. **Verified Networks**
   - Lists diagrams with `isVerified=true` and `type=0`
   - Scrollable with max-height 300px
   - Actions: Load, Export, Delete

2. **Unverified Networks**
   - Lists diagrams with `isVerified=false` and `type=0`
   - Same actions as verified

3. **Subnetwork Blueprints**
   - Lists blueprints owned by current user
   - Filtered: `blueprint.userId === user_id`
   - Actions: Load, Delete

---

## 5. Redux Integration

### 5.1 canvasSlice Actions Used

```typescript
// Clearing state
dispatch(clearNodeNames());
dispatch(clearDiagramNodes());
dispatch(clearComputationResults());
dispatch(clearCurrentDiagramId());
dispatch(clearCanvasName());
dispatch(clearDescription());
dispatch(clearParentConnections());

// Setting new diagram state
dispatch(setCurrentDiagramId(diagramId));
dispatch(initializeNodeNames(nodeNames));
dispatch(setDiagramType(type));
dispatch(setParentConnections(parentConnections));
dispatch(updateCanvasName(canvasName));
dispatch(updateDescription(description));
dispatch(setVerified(isVerified));

// Removing individual items
dispatch(removeNodeName(nodeName));
```

### 5.2 Other Slices

**calcTypeSlice:**
```typescript
const currentCalcType = useSelector(
  (state: RootState) => state.calcType.type
);
dispatch(updateCalcType(calcType));
```

**domainSlice:**
```typescript
dispatch(fetchDomainData(domain));
// Async thunk that loads domain models/ports
```

**alertsSlice:**
```typescript
dispatch(showAlertWithTimeout(type, message));
// Shows toast notification with auto-dismiss
```

---

## 6. API Endpoints

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| GET | `/api/data/domains` | List all domains | - | `Domain[]` |
| GET | `/api/data/diagrams` | List user's diagrams | - | `Diagram[]` |
| GET | `/api/data/diagrams/{id}` | Get single diagram | - | `Diagram` |
| GET | `/api/data/diagrams/{id}/export` | Export full snapshot | - | `FullNetworkSnapshot` |
| POST | `/api/data/diagrams` | Create new diagram | `DiagramPayload` | `{ diagram: { id } }` |
| POST | `/api/data/diagrams/import` | Import full snapshot | `{ snapshot }` | `{ diagram: { id, name } }` |
| DELETE | `/api/data/diagrams/{id}` | Delete diagram | - | - |
| PATCH | `/api/data/diagrams/{id}/verify` | Verify diagram | - | - |
| GET | `/api/data/subnetworks` | List blueprints | - | `SubnetworkBlueprint[]` |
| GET | `/api/data/subnetworks/{id}` | Get blueprint | - | `SubnetworkBlueprint` |
| DELETE | `/api/data/subnetworks/{id}` | Delete blueprint | - | - |

---

## 7. Data Flow Patterns

### 7.1 Creating a New Diagram

```
User Form Inputs
    ↓
Local State (canvasName, domain, description)
    ↓ (localStorage stored)
    ↓
handleSubmit() triggered
    ↓
Frontend Validation (name uniqueness, required fields)
    ↓
Redux State Cleared (old diagram state)
    ↓
Redux State Set (new diagram metadata)
    ↓
fetchDomainData() dispatched (loads domain models)
    ↓
Navigate to /canvas/{domainId}
    ↓
Canvas component loads from Redux state
```

### 7.2 Loading Existing Diagram

```
Diagram List (from fetchDiagrams())
    ↓
User clicks "Load"
    ↓
handleLoadDiagram(diagramId)
    ↓
GET /api/data/diagrams/{diagramId}
    ↓
Extract canvas.nodes and parentConnections
    ↓
Redux State Cleared
    ↓
Redux State Populated
    ↓
Navigate to /diagram/{diagramId}
    ↓
Canvas component loads from Redux + database
```

### 7.3 Importing Diagram from JSON

```
User selects .json file
    ↓
handleImportDiagram(file)
    ↓
Parse JSON
    ↓
Check snapshot format
    ↓
If new (`version=1.0.0`):
  POST /api/data/diagrams/import
Else (legacy):
  POST /api/data/diagrams
  optional PATCH /diagrams/{id}/verify
    ↓
fetchDiagrams() to refresh list
    ↓
Show alert (success/warning/error)
```

---

## 8. localStorage Integration

### 8.1 Temporary Data Storage

```typescript
const tempData = {
  canvasName: string,
  description: string,
  timestamp: number
};

// Stored with key: `temp_diagram_${domainId}`
// Stored at: localStorage.setItem()
// Cleared at: Navigate to canvas (not shown in this file)
```

**Use Case:** If user navigates away from dashboard, form data is persisted and can be recovered on return.

**Not Implemented Here:** Code to retrieve and restore this data.

---

## 9. Module-Level State

### 9.1 modelNameMap

```typescript
const modelNameMap = new Map<string, string>();
```

**Purpose:** Global map tracking node_id → node_name relationships

**Used In:**
- `handleDeleteDiagram()` - Cleanup on deletion
- Canvas component (unclear from this file)

**Why Global:**
- Coordinates name mappings across multiple diagrams
- Centralized source of truth for node naming

---

## 10. Error Handling and Alerts

### 10.1 Error Types

| Scenario | Handler | Alert Message |
|----------|---------|-------|
| Duplicate diagram name | `handleCanvasNameBlur()` | "Diagram name must be unique." |
| Missing required fields | `handleSubmit()` | "Please provide canvas name, domain, and calculation type." |
| Failed diagram load | `handleLoadDiagram()` | "Failed to load diagram." |
| Failed diagram delete | `handleDeleteDiagram()` | "Failed to delete diagram." |
| Failed subnetwork delete | `handleDeleteSubnetwork()` | "Failed to delete subnetwork blueprint." |
| Failed diagram export | `handleExportDiagram()` | "Failed to export diagram." |
| Failed import | `handleImportDiagram()` | "Failed to import diagram. Check console for details." |
| Verification denied | `handleImportDiagram()` | "Diagram imported but verification failed: you may not have permission." |

### 10.2 Alert Dispatch

```typescript
dispatch(showAlertWithTimeout(
  type,    // 'error' | 'warn' | 'info'
  message  // string
));

// Automatically dismisses after timeout (default 5s)
```

---

## 11. File Input Handling

### 11.1 Hidden File Input Pattern

```tsx
// Define ref
const fileInputRef = useRef<HTMLInputElement | null>(null);

// Render hidden input
<input
  ref={fileInputRef}
  type="file"
  accept=".json,application/json"
  style={{ display: 'none' }}
  onChange={onImportFileChange}
/>

// Trigger with button
<Button onClick={openImportDialog} variant='primary'>
  Import Diagram
</Button>

// Functions to manage
const openImportDialog = () => {
  if (fileInputRef.current) fileInputRef.current.click();
};

const onImportFileChange = (e) => {
  const file = e.target.files?.[0] ?? null;
  handleImportDiagram(file);
};
```

**Rationale:**
- Browser file input unstyled and hard to customize
- Hidden input + custom button provides better UX
- Click on button triggers file dialog

---

## 12. Performance Optimizations

### 12.1 useCallback Memoization

```typescript
const fetchDomains = useCallback(async () => {
  // ... fetch logic
}, []);
```

**Benefit:** Prevents unnecessary re-creation of fetch functions, reducing dependency array churn

### 12.2 JSON Comparison for setState

```typescript
setDiagrams((prev) => {
  if (JSON.stringify(prev) === JSON.stringify(response.data)) return prev;
  return response.data;
});
```

**Benefit:** Prevents re-renders when data hasn't actually changed

**Cost:** O(n) JSON serialization, but typically less than 10 ms for diagram arrays

### 12.3 Conditional localStorage Updates

```typescript
if (domain) {
  storeTemporaryData(domain, canvasName, description);
}
```

**Benefit:** Only stores data when domain is selected

---

## 13. Integration with Other Pages

### 13.1 Dependencies

```
Dashboard
  ↓
Canvas (/canvas/{domainId}) ← Created new diagram
  ↓
DiagramEditor (/diagram/{diagramId}) ← Loaded existing diagram
```

**Data Passed via Redux:**
- `canvasSlice.canvasName`
- `canvasSlice.description`
- `canvasSlice.currentDiagramId`
- `canvasSlice.nodeNames`
- `canvasSlice.parentConnections`
- `calcTypeSlice.type`

---

## 14. Security Considerations

### 14.1 User Isolation

```typescript
// Blueprint filtering by user
blueprints.filter(blueprint => blueprint.userId === user_id)
```

**Ensures:** Users can only see their own blueprints

### 14.2 File Import Validation

```typescript
const filename = `${(diagramName || diagramId).replace(/\\s+/g, '_')}.json`;
```

**Note:** No schema validation shown here. Backend should validate:
- Canvas structure
- Node references
- Port IDs
- Domain ID matches allowed domains

### 14.3 Duplicate Name Prevention

```typescript
if (diagrams.some((d) => d.name === diagramPayload.name)) {
  const randomSuffix = Math.random().toString(36).substring(2, 8);
  diagramPayload.name = `${diagramPayload.name}_${randomSuffix}`;
}
```

**Strategy:** Append random suffix to prevent collisions (weak but pragmatic)

---

## 15. Common Issues and Debugging

### 15.1 Diagram List Not Updating

**Symptom:** Created or deleted diagram doesn't appear/disappear

**Causes:**
- `fetchDiagrams()` not called after mutation
- Backend returned different format
- JSON comparison check failed

**Solution:**
```typescript
await fetchDiagrams();  // Always call after CRUD
```

### 15.2 Form Data Lost on Navigation

**Symptom:** User fills form but navigates away, data is lost

**Current State:** localStorage saves data but no restore logic shown

**Needed:** Add useEffect to restore from localStorage:
```typescript
useEffect(() => {
  if (domain) {
    const saved = localStorage.getItem(`temp_diagram_${domain}`);
    if (saved) {
      const { canvasName, description } = JSON.parse(saved);
      setCanvasName(canvasName);
      setDescription(description);
    }
  }
}, [domain]);
```

### 15.3 Import Fails with Verification Error

**Symptom:** "Diagram imported but verification failed"

**Causes:**
- Legacy-format import triggered verify flow
- User does not have verification permission

**Solution:** Check user roles/permissions before attempting import with verification

### 15.4 Import Fails with Missing Subnetwork Instances

**Symptom:** Import returns `400` and response includes `missingInstanceIds`

**Cause:**
- Wrapper nodes in imported snapshot reference instance diagrams that are not present in `subnetworkInstances`

**Solution:**
- Re-export from source using `GET /api/data/diagrams/{id}/export`
- Re-import the unmodified snapshot payload
- Avoid manually removing `subnetworkInstances` entries from export JSON

---

## 16. Related Files

| File | Relationship |
|------|-------------|
| `canvas.tsx` | Opens after "Create Diagram" |
| `diagram-editor.tsx` | Opens after "Load Diagram" |
| `canvasSlice.ts` | Redux state for canvas/diagram |
| `calcTypeSlice.ts` | Calculation type state |
| `domainSlice.ts` | Domain models/ports |
| `alertsSlice.ts` | Alert notifications |
| `AuthContext.tsx` | User authentication |
| `save-util.tsx` | Diagram save logic |
| `dataRoutes.ts` (backend) | Diagram CRUD endpoints |
