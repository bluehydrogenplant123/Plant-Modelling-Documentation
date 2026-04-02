# calcTypeSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/calcType/calcTypeSlice.ts`
- Purpose: Stores the active calculation type for the canvas/session.

## State
- `type: CalcType` where `CalcType` ∈ `['Simulation', 'Optimization', 'DataRec', 'ParamUpdt']` (default `'Simulation'`).

## Actions
- `updateCalcType(type)` — sets state when payload is in `CALC_TYPES`; logs a warning otherwise.

## Notes
- Use the exported `CALC_TYPES` for validation in UI controls.
- The active calc type is persisted at the diagram (network) level and rehydrated on load from the backend response.
