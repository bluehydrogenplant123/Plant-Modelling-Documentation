# Time Period Viewer (TP Node - Model Version Control)

## Overview
- **Location:** `src/src/frontend/src/components/header-bar/header-buttons/time-period-viewer.tsx`
- **Purpose:** Per-node Time Period panel backed by `TpNodeVers`. In the current release, it is in a temporary frontend-safe mode: users can view TP ranges and update model versions, while TP range structure editing is disabled in UI.
- **Visibility:** The button only renders after the diagram is verified (`state.canvas.verified === true`).
- **Dependencies:** React-Bootstrap (`Modal`, `Button`), React Flow (`useReactFlow`), Redux (selectors + dispatch), Axios, and standard React hooks.
- **Feature Toggle:** `TP_STRUCTURE_EDITING_ENABLED` (currently `false`) controls whether TP structure editing UI is enabled.

## Data Flow (fetch/build)
1. **Fetch main diagram** via `GET /api/data/diagrams/:diagramId`.
2. **Discover subnetworks** by scanning dummy nodes with `blueprintDiagramId` and `model.diagramId`.
3. **Fetch sub-diagrams** and collect all nodes + edges (main + sub) into `allNodesContext`.
4. **Fetch TpNodeVers rows** for every diagram via `GET /api/data/tpnodevers?diagramId=...`.
5. **Build in-memory maps** (`timePeriodsMap`, `recordRows`) and synthesize missing base rows using snapshot/domain model versions.
6. **Hide dummy subnetwork wrapper nodes** in the grid while still retaining their data.

## UI Workflow
- **Current mode (temporary): TP structure editing disabled**
  - The modal opens directly to the grid view.
  - `from tp` / `to tp` are display-only (read-only text in table).
  - `model version` remains editable.
  - `update` and `confirm` columns are hidden.
  - Add/Delete TP inputs and **Build Grid** entry flow are hidden.
  - Filters (network/node/model/model version/TP range) remain available.
- **When toggle is re-enabled (`TP_STRUCTURE_EDITING_ENABLED = true`)**
  - Build-grid flow and staged split/update controls become available again.
  - Existing split/confirm/cancel code path is still preserved.

## Save Behavior
- Save pipeline remains grouped **per diagram** and persists through:
  - `POST /api/data/tpnodevers` for adds
  - `PUT /api/data/tpnodevers` for updates
  - `DELETE /api/data/tpnodevers` for deletes
- In current temporary mode, user-driven TP structure operations are blocked by frontend UI, so effective user edits are model-version changes only.
- Base TP (fromTP = 1) is normalized with `initModelVersionWithCalcType(...)` using connected edges.
- Main-diagram nodes are refreshed in Redux (`setDiagramNodes` + `refreshNodeParametersAfterModelVersionChange`).
- A final `saveDiagram()` persists the canvas snapshot.

## Styling
- Uses `tpeditor_style.css` for table layout and modal sizing.
- **Build Grid** uses the `.tp-build-grid-btn` class to match main-menu colors and hover behavior.

## Notes
- `TpNodeVers` is treated as the source of truth; node objects do not store Time Periods directly.
- Subnetwork nodes are written to the database but do not trigger Redux refresh (only main diagram nodes are live in the store).
- Backend TP routes and data logic are intentionally preserved; this change is frontend-only gating.
