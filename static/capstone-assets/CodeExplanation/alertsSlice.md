# alertsSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/alert/alertsSlice.ts`
- Purpose: Manages transient alert messages with auto-dismiss behavior.

## State
- Array of alerts `{ id, type, msg }`, where `type` ∈ `['info','warn','error']`.

## Actions / Thunks
- `setAlert({ id, type, msg })` — push a new alert.
- `removeAlert(id)` — remove by id.
- `showAlertWithTimeout(type, msg)` — thunk that dispatches `setAlert` with a UUID and auto-removes after 5s.

## Notes
- Uses `uuidv4` for ids; adjust timeout in `showAlertWithTimeout` if UX requires longer/shorter display.

