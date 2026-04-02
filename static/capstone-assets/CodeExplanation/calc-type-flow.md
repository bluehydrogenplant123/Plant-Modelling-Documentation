# Calc Type Flow (Network-Level)

## Overview
- Purpose: Define how calculation type is selected, persisted, rehydrated, and enforced across a network and its subnetworks.
- Scope: New calc types `Simulation`, `Optimization`, `DataRec`, `ParamUpdt`.
- Key files:
  - Frontend: `src/src/frontend/src/features/calcType/calcTypeSlice.ts`, `src/src/frontend/src/components/header-bar/index.tsx`, `src/src/frontend/src/components/header-bar/header-buttons/tp-specs-button.tsx`, `src/src/frontend/src/components/modal/tabs/node-var-input.tsx`
  - Backend: `src/src/backend/routes/dataRoutes.ts`

## Source of Truth
- The persisted source of truth is `diagram.parameters.global_params.task_config.task_type`.
- `GET /api/data/diagrams/:id` derives `calcType` from `parameters` and returns it at the top level for frontend rehydration.
- The frontend stores the active value in Redux `calcType.type`.

## Creation Flow
1. The “Create Diagram” modal presents the calc type dropdown using `CALC_TYPES`.
2. On create, the selected calc type is passed to `translation` and persisted in `parameters.global_params.task_config.task_type`.

## Switch Flow (Header Bar)
1. Header “Calc Type” section renders four buttons: Simulation / Optimization / DataRec / ParamUpdt.
2. Clicking the current calc type opens the TP Specs panel immediately.
3. Clicking a different calc type shows a confirmation modal (“Switch from X to Y?”).
4. Confirm:
   - Updates Redux `calcType`.
   - Opens TP Specs panel (same component as Model → Specs).
5. TP Specs “Save” triggers:
   - `/api/data/tp-specs/bulk-update` (spec value persistence).
   - `PUT /api/data/diagrams/:id` with `calcType` to persist network-level calc type.

## Simulation Mode Restrictions
- When `calcType === 'Simulation'`:
  - TP Specs grid “Spec” column is read-only.
  - Node spec input in `NodeVarInput` is disabled.

## Network-Wide Sync (Parent + Subnetworks)
When `PUT /api/data/diagrams/:id` includes a calc type:
1. Backend re-translates parameters for the current diagram.
2. Backend locates the network root by walking `parentConnections.parentDiagramId`.
3. It collects all diagrams in the same network tree (parent + all children).
4. For each related diagram, it updates:
   - `parameters.global_params.task_config.task_type`
   - `parameters.tps_specs[*].task` (if present)

This keeps parent and subnetwork calc types consistent after any single change.

## Computation Input
- `translation(...)` receives `calcType` and injects it into solver parameters.
- The computation request uses the latest confirmed network calc type (after switching).
