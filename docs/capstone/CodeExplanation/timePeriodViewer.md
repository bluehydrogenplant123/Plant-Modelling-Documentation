# Time Period Viewer (TP Node - Model Version Control)

## Overview
- **Location:** `src/src/frontend/src/components/header-bar/header-buttons/time-period-viewer.tsx`
- **Purpose:** Per-node Time Period editor that drives the `TpNodeVers` table. It lets users split time ranges, assign model versions to those ranges, and persist changes across the main diagram and all subnetworks.
- **Visibility:** The button only renders after the diagram is verified (`state.canvas.verified === true`).
- **Dependencies:** React-Bootstrap (`Modal`, `Button`), React Flow (`useReactFlow`), Redux (selectors + dispatch), Axios, and standard React hooks.

## Data Flow (fetch/build)
1. **Fetch main diagram** via `GET /api/data/diagrams/:diagramId`.
2. **Discover subnetworks** by scanning dummy nodes with `blueprintDiagramId` and `model.diagramId`.
3. **Fetch sub-diagrams** and collect all nodes + edges (main + sub) into `allNodesContext`.
4. **Fetch TpNodeVers rows** for every diagram via `GET /api/data/tpnodevers?diagramId=...`.
5. **Build in-memory maps** (`timePeriodsMap`, `recordRows`) and synthesize missing base rows using snapshot/domain model versions.
6. **Hide dummy subnetwork wrapper nodes** in the grid while still retaining their data.

## UI Workflow
- **Step 1: Build Grid**
  - Users enter add/delete counts to adjust total TP count, then click **Build Grid**.
  - The component rebuilds per-node ranges to cover `1..N` for all nodes.
- **Step 2: Per-node range editing**
  - Grid columns: network, node name, model name, model version, from TP, to TP.
  - Ticking **update** creates a staged row (red outline) that represents a split.
  - **Confirm Update** splits the canonical row into head / staged / tail segments.
  - Filters allow narrowing by network, node, model, model version, and TP range.

## Save Behavior
- Changes are grouped **per diagram** and persisted via:
  - `POST /api/data/tpnodevers` for adds
  - `PUT /api/data/tpnodevers` for updates
  - `DELETE /api/data/tpnodevers` for deletes
- Base TP (fromTP = 1) is normalized with `initModelVersionWithCalcType(...)` using connected edges.
- Main-diagram nodes are refreshed in Redux (`setDiagramNodes` + `refreshNodeParametersAfterModelVersionChange`).
- A final `saveDiagram()` persists the canvas snapshot.

## Styling
- Uses `tpeditor_style.css` for table layout and modal sizing.
- **Build Grid** uses the `.tp-build-grid-btn` class to match main-menu colors and hover behavior.

## Notes
- `TpNodeVers` is treated as the source of truth; node objects do not store Time Periods directly.
- Subnetwork nodes are written to the database but do not trigger Redux refresh (only main diagram nodes are live in the store).
