# Save Diagram Workflow (Current Implementation)

This document reflects the current save logic in:
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx`

## 1. Entry Points

### 1.1 Main Save Button (manual save)

`SaveAndRestore` now controls `autoReload` via a checkbox and passes it into `useSaveDiagram`:

```typescript
const [autoReloadEnabled, setAutoReloadEnabled] = useState<boolean>(readAutoReloadPreference);
const onSave = useSaveDiagram(false, autoReloadEnabled);
```

- Checkbox checked: save with refresh enabled.
- Checkbox unchecked: save without refresh.
- Preference is persisted in `localStorage` key: `save_auto_reload_enabled`.
- Button text is dynamic: `Save (Refresh On)` / `Save (Refresh Off)`.

### 1.2 Other callers

- `App.tsx` autosave uses `useSaveDiagram(false, false, { showSuccessToast: false })` (no refresh).
- Some other flows still call `useSaveDiagram()` and inherit `autoReload = true` by default.

## 2. Hook Signature and Options

```typescript
export function useSaveDiagram(
  saveAsCopy: boolean = false,
  autoReload: boolean = true,
  options?: {
    successMessage?: string;
    showSuccessToast?: boolean;
    showTimingToast?: boolean;
  }
)
```

- `saveAsCopy`: create a copy flow after main save.
- `autoReload`: controls post-save page reload behavior (applies to update path).
- `showSuccessToast`: default true.
- `showTimingToast`: optional debug timing toast.

## 3. Guards and Early Validation

Before saving:

1. Global/in-hook dedupe:
- Skip if `saveInFlightRef`, `globalSaveInFlight`, or Redux `isSaving` is true.

2. New-diagram dedupe window:
- For unsaved diagrams (`!diagramId`), skip duplicate create requests within 3 seconds using key:
  `${domainId}:${canvasName}`.

3. Required domain check:
- If no `domainData.id`, abort with error alert.

4. Incomplete stream check:
- `getIncompleteStreamEdges(getEdges())` must be empty.
- Incomplete edges are highlighted and save aborts.

Temporary data (`canvasName`, `description`) is written to:
- `localStorage["temp_diagram_${domainId}"]`

## 4. Canvas and Payload Preparation

### 4.1 Canvas serialization

- `toObject()` output is deep-copied and normalized.
- Node `modelVersion`/`timePeriods` are stripped from canvas.
- `blueprintDiagramId` is preserved.
- `rotationDirection` is normalized to 0..3.
- Edges are processed via `processEdges`.

For instance diagram (`diagramType === 2`):
- `canvas.parentConnections` is sanitized with `sanitizeParentConnectionsPayload`.

### 4.2 Subnetwork extraction

- `prepareSubnetworkInstances(canvas, diagramId)` returns:
  - updated `canvas`
  - `subnetworkInstances` metadata sent to backend

### 4.3 Node cache payload

`gatherNodeCachePayload()`:
- Processes dirty nodes only (`nodeCache.dirtyNodes`).
- Loads cached/base modelVersion when needed.
- Merges Redux `nodeParameters` into `modelVersion` for non-exposed ports.
- Skips merge on exposed ports mapped by `portsMapping`.

Then frontend builds:
- `nodeCacheDiffs: Record<string, Operation[]>` using `fast-json-patch.compare(...)`.
- `nodeCacheFull: Record<string, ModelVersion>` for nodes without original baseline.

### 4.4 Request payload

Current save payload sent to `/api/data/diagrams` or `/api/data/diagrams/:id`:

```typescript
{
  name,
  canvas,
  description,
  domainId,
  calcType,
  snapshotData,
  type,
  nodeCacheDiffs,
  nodeCacheFull,
  subnetworkInstances,
  clientTiming,
}
```

## 5. Create vs Update Branch

### 5.1 Update existing diagram (`PUT`)

- Endpoint: `PUT /api/data/diagrams/${diagramId}`
- Applies backend response:
  - `createdSubnetworks`
  - `parentNodeUpdates`
- Cleans temp localStorage.
- Sets:
  - `shouldReloadAfterSave = autoReload`

### 5.2 Create new diagram (`POST`)

- Endpoint: `POST /api/data/diagrams`
- Saves `recentCreateRequest` for dedupe.
- Applies `createdSubnetworks` + `parentNodeUpdates`.
- Sets `currentDiagramId = response.data.diagram.id`.
- Updates subnetwork parent IDs to the new diagram.
- If `saveAsCopy === true`, posts a copy payload with:
  - random suffix name
  - `instanceDiagramId: undefined` for copy instances
- Cleans temp localStorage.
- Sets `navigateAfterSave = currentDiagramId`.

## 6. Node Table Persistence and TP Draft Persistence

After diagram save:

1. Push merged versions into Redux cache (`nodeCache.updateNodeValue`).
2. Persist to Node table:
- `nodeCache.saveAllNodeChanges(currentDiagramId)`
- If failed: alert and return early.
3. Persist multi-TP drafts (`tpChangesDraft`) via:
- `POST /api/data/tpchanges`
- `DELETE /api/data/tpchanges` for delete drafts
- On success: `clearTpChangeDrafts()`

## 7. Canonical Node ID Remap

If `saveAllNodeChanges` returns `replacements`:

- Build `idMap` from `{ oldNodeId -> newNodeId }`.
- Remap:
  - ReactFlow nodes and edges
  - canvas nodes and edges
  - `portsMapping`
  - `parentConnections` (including edges and external port mappings)
  - `subnetworkInstances`
- Dispatch Redux `renameNodeId(...)`.
- Issue a second `PUT /api/data/diagrams/${currentDiagramId}` with remapped data.
- If second PUT fails, show warning: ids may be outdated and ask user to save again.

## 8. Finalization

At the end of successful save:

1. Navigate if this is a newly created diagram:
- `navigate("/diagram/${navigateAfterSave}")`

2. Save metadata:
- `localStorage["diagram_save_meta_${diagramId}"] = { lastSavedAt, lastSaveDurationMs }`

3. Redux save status:
- `updateSaved(true)`
- `setLastSavedAt(...)`
- `setLastSaveDurationMs(...)`

4. Optional timing toast:
- shown when `showTimingToast` is true or `VITE_SAVE_TIMING_TOAST === "true"`.

5. Optional reload:
- If `shouldReloadAfterSave` is true, run `window.location.reload()` after 1 second.
- In current implementation, this flag is set in the update branch only.

In `finally` block:
- clear in-flight flags
- set `isSaving(false)`

## 9. Refresh Behavior Summary (UI + Logic)

### 9.1 What controls refresh

- Hook-level switch: `autoReload` parameter in `useSaveDiagram`.
- Manual Save button now exposes that switch via checkbox.

### 9.2 User-facing behavior

- Checked: `Save (Refresh On)` and label `Auto refresh after save`.
- Unchecked: `Save (Refresh Off)` and label `Stay on page after save`.
- Preference persists in localStorage (`save_auto_reload_enabled`).

### 9.3 Important nuance

- Refresh is tied to update save path (`PUT`) via `shouldReloadAfterSave`.
- New diagram create path navigates to new route; it does not set `shouldReloadAfterSave`.

## 10. Quick Flow Diagram

```text
Click Save
  -> dedupe/in-flight guard
  -> validate domain + stream completeness
  -> build lightweight canvas + subnetworkInstances
  -> gather nodeCache payload
  -> build nodeCacheDiffs/nodeCacheFull
  -> PUT(existing) or POST(new)
  -> apply createdSubnetworks + parentNodeUpdates
  -> saveAllNodeChanges (Node table)
  -> persist tpChanges drafts
  -> if replacements: remap ids + second PUT
  -> update saved state + save metadata
  -> navigate(new) or reload(update + autoReload=true)
```

## 11. Key Files

| File | Responsibility |
|---|---|
| `src/src/frontend/src/components/header-bar/utils/save-util.tsx` | Core save hook and data remap logic |
| `src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx` | Save button UI + refresh toggle preference |
| `src/src/frontend/src/features/node/nodeCacheService.ts` | Node modelVersion cache and persistence |
| `src/src/frontend/src/features/saved/savedSlice.ts` | Save state (`saved`, `isSaving`, timestamps) |
| `src/src/backend/routes/dataRoutes.ts` | Backend diagram save/update processing |

