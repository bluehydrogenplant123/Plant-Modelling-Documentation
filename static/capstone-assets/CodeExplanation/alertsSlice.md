# alertsSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/alert/alertsSlice.ts`
- Purpose: Manages transient alert messages with auto-dismiss behavior.

## State
- Array of alerts `{ id, type, msg }`, where `type` 鈭?`['info','warn','error']`.

## Actions / Thunks
- `setAlert({ id, type, msg })` 鈥?push a new alert.
- `removeAlert(id)` 鈥?remove by id.
- `showAlertWithTimeout(type, msg)` 鈥?thunk that dispatches `setAlert` with a UUID and auto-removes after 5s.

## Notes
- Uses `uuidv4` for ids; adjust timeout in `showAlertWithTimeout` if UX requires longer/shorter display.
