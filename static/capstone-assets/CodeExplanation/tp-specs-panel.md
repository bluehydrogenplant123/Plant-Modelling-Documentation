# TP Specs Panel

## Overview
- Location: `src/src/frontend/src/components/header-bar/header-buttons/tp-specs-button.tsx`
- Purpose: Display and edit TP Specs (spec, bounds, value, unit) in a grid view.
- UI: AG Grid modal opened from Header Bar or after calc type confirmation.

## Data Sources
1. `GET /api/data/diagrams/:id`  
   - Loads canvas for node listing and diagram metadata.
2. `GET /api/data/nodes/:nodeId`  
   - Fetches each node’s `modelVersion.ports_var` to build grid rows.

## Save Flow
1. Collect current grid rows with `gridApi.forEachNode(...)`.
2. `PUT /api/data/tp-specs/bulk-update` to persist the specs.
3. `PUT /api/data/diagrams/:id` with `calcType` to persist the network-level calc type.
4. Show toast “TP Specs updated successfully!” and refresh.

## Calc Type Rules
- When `calcType === 'Simulation'`, the **Spec** column is read-only.
- This matches `NodeVarInput` behavior (spec edits disabled in Simulation mode).

## Column Behavior (Highlights)
- `Node` / `Port` / `Port Var` use select editors seeded by live node data.
- Changing `Node` cascades to update `Port`, `Port Var`, and default values.
- `Unit` change triggers automatic value conversion using unit families.

## Notes
- The panel is reused for both initial access and calc type switching.
- Calc type confirmation only opens the panel; the actual persistence happens on Save.
