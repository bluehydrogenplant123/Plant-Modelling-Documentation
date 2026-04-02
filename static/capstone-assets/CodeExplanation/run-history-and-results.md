# Run History & Result Management

## Overview

This document describes the run history UI, server APIs, and result deletion flow added around computation tasks. It also covers run‑name uniqueness checks in the Computation Panel.

Key files:
- `src/src/frontend/src/components/header-bar/header-buttons/run-result-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/computation-button.tsx`
- `src/src/backend/routes/computeRoutes.ts`

---

## 1. Run Result History Modal (UI)

**Component:** `RunResultButton`

Behavior:
1. Clicking `Run Result` opens a modal and fetches `GET /api/compute/history/:diagramId`.
2. The table renders `runName`, `status`, and `runAt` (derived from task start time or creation time).
3. Clicking **Delete** calls `DELETE /api/compute/results` with `{ diagramId, runName }`.
4. On success, the modal closes automatically and a success alert is shown.

Implementation highlights:
- Fetch is only executed when the modal is open.
- Delete uses `axios.delete` with a `data` body to pass JSON.

---

## 2. Run Name Uniqueness Validation (UI)

**Component:** `ComputationButton` (Computation Panel)

When the panel is opened:
1. `GET /api/compute/history/:diagramId` is called.
2. All `runName` values are collected and stored locally.

Validation logic:
- `runName` is trimmed and compared case‑insensitively.
- If a duplicate exists, a red warning text is shown and **Start Computation** is disabled.
- The backend still remains the source of truth, but the UI blocks obvious duplicates.

---

## 3. Backend APIs

### 3.1 Get Run History
`GET /api/compute/history/:diagramId`

Responsibilities:
- Validates diagram ownership.
- Returns a list of computation tasks for the diagram, newest first.
- Each item includes: `id`, `runName`, `status`, and `runAt`.

### 3.2 Delete Run Results
`DELETE /api/compute/results`

Request body:
```json
{ "diagramId": "<id>", "runName": "<name>" }
```

Responsibilities:
- Validates diagram ownership.
- Deletes **PostgreSQL** rows from `ComputationResults` for `(diagram_id, run_name)`.
- Deletes **MongoDB** rows from `computationTask` with the same `(diagramId, runName, userId)`.
- Clears Redis cache for `computationTask:<diagramId>`.
- Returns counts for deleted results and tasks.

---

## 4. Notes and Edge Cases

- Run history is scoped to a **single diagram**.
- Deleting results does **not** delete the diagram itself.
- If multiple tasks share the same `runName`, all matching tasks for that diagram are removed.
- The modal currently closes after a delete to avoid stale history views.
