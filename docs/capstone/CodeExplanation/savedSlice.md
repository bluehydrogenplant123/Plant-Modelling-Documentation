# savedSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/saved/savedSlice.ts`
- Purpose: Tracks whether the current diagram state is saved.

## State
- `saved: boolean` (default `false`).

## Actions
- `updateSaved(boolean)` — set saved flag.

## Notes
- Other features (e.g., modal/tab edits) dispatch `updateSaved(false)` when mutating node data; ensure save flows set it back to true after persistence.

