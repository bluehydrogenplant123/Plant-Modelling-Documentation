# Global TP (Bulk Time Period Assignment)

## Overview
- **Location:** `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`
- **Purpose:** A bulk editor that applies a single, unified Time Period segmentation to **all nodes** (main diagram + subnetworks) in one operation. It is the fast-path alternative to per-node editing in `TimePeriodViewer`.
- **Visibility:** The button only renders after the diagram is verified (`state.canvas.verified === true`).
- **Dependencies:** React-Bootstrap (`Modal`, `Button`), React Flow (`useReactFlow`), Redux (selectors), Axios, and standard React hooks.

## Workflow
1. **Open modal** and fetch main/sub diagrams and `TpNodeVers` rows.
2. **Build Grid**
   - Users enter add/delete counts to set a target TP total.
   - The UI initializes a single canonical range `1..N`.
3. **Range builder**
   - Click **update** to stage a split for the selected range.
   - **Confirm Update** replaces the canonical range with head/staged/tail segments.
   - Validation enforces **continuous coverage** from `TP 1` to `TP N` (no gaps/overlaps).
4. **Apply to All Nodes**
   - Deletes all existing `TpNodeVers` rows for the nodes in scope.
   - Recreates rows for every node using the same range set.
   - Each range uses the node’s base model version (resolved by priority below).
5. **Persist**
   - Saves to `/api/data/tpnodevers` and triggers `saveDiagram()`.

## Model Version Resolution
For each node, the base model version is chosen in this order:
1. Existing `TpNodeVers` base row (`fromTp = 1`).
2. Node’s current `modelVersion`.
3. Snapshot model versions from the diagram payload.
4. Domain model versions.
5. Fallback: `FLOW_FIXED`.

Base versions are normalized with `initModelVersionWithCalcType(...)` and node edges when available.

## Styling
- Uses `tpeditor_style.css` for modal layout and table styling.
- **Build Grid** uses `.tp-build-grid-btn`, matching the main menu’s outline-primary colors and hover state.

## Related Components
- `TimePeriodViewer` (`TP Node - Model Version Control`) for fine-grained per-node edits.
- `header-bar/index.tsx` for placement under the **Multi-Time Period** section.
