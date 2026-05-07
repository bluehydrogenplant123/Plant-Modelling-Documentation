---
title: Compute, Solver Callback, and Results Code Explanation
sidebar_position: 30
description: Explains how HyProNet starts computation tasks, dispatches solver requests, receives callbacks, and persists results.
---

## Overview

The compute workflow starts from authenticated `/api/compute` routes, stores a MongoDB `computationTask`, dispatches a Bull queue job, sends the final solver request to the external solver engine, and records the solver callback into diagrams, nodes, time-period changes, and PostgreSQL computation-result rows.

The current source of truth is the TypeScript path from `computeRoutes.ts` through the worker, solver API service, callback route, reverse translation, and result storage. Generated JSON files such as `solve_request.json` are useful for read-only debugging only.

## Source Files

- `src/src/backend/routes/computeRoutes.ts`: authenticated compute API routes for start, chunk upload, details polling, history, result deletion, and abort.
- `src/src/backend/config/taskQueue/computationDispatchQueue.ts`: Bull queue instance named `computationDispatchQueue`.
- `src/src/backend/config/taskQueue/baseTaskQueue.ts`: Redis-backed Bull queue setup, Bull Board registration, and queue event logging.
- `src/src/backend/workers/computationDispatchWorker.ts`: queue consumer that builds and sends the solver request, updates task status, and waits for callback completion.
- `src/src/backend/services/computationTaskService.ts`: MongoDB task CRUD, Redis cache reads and invalidation, queue-position reporting, and run-configuration translation.
- `src/src/backend/services/solverEngineApiService.ts`: builds the solver request, posts to `/solve/`, optionally writes `solve_request.json`, and posts `/kill/` for abort.
- `src/src/backend/routes/external/computeCallbackRoutes.ts`: gateway-authenticated callback endpoint for solver `success`, `failed`, and `timeout` statuses.
- `src/src/backend/services/computationTaskHandler.ts`: success-callback handler that applies reverse translation and persists callback side effects.
- `src/src/backend/utils/reverseTranslation.ts`: maps solver `results.tps_specs` back into parameters, node model versions, and computed TP changes.
- `src/src/backend/utils/storeComputationResultUtils.ts`: stores solver machine-generated values in PostgreSQL `ComputationResults`.

## Purpose and Responsibility

The compute route layer owns request validation, user authorization, parameter generation, task creation, and polling responses. It does not directly call the solver. Solver dispatch belongs to the Bull worker, and callback processing belongs to the external callback route plus `handleComputationSuccess`.

The solver API service owns the external HTTP contract. It appends `/solve/`, `/kill/`, and `/compute/callback/` to configured base URLs. Environment values should therefore stay as base URLs, for example `BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api` and `BASE_EXTERNAL_URL=http://localhost:3000/api/external`.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `diagramId` | `/api/compute/start`, `/details/:diagramId`, `/history/:diagramId`, `/abort`, `/results` | Selects the diagram, task, result rows, and Redis cache key. |
| `maxComputationTime` | `/api/compute/start` body or upload metadata | Stored as `configuration.max_computation_time`; `/start` rejects values below `COMPUTATION_CONSTANTS.MINIMUM_COMPUTATION_TIME`. |
| `runName` | `/start`, `/upload/init`, `/results` | Stored on `computationTask` and used as part of the PostgreSQL result identity. |
| `solverName`, `algorithmName` | `/start` or upload metadata | Looked up in snapshot `runConfigs` and stored in task `configuration`. |
| `tpChanges` | Optional `/start` body plus persisted MongoDB `tpChanges` | Merged before translation so explicit user overrides can affect `parameters.tps_specs`. |
| Chunk payload | `/upload/:sessionId/chunk` | Reassembled by `/upload/:sessionId/finalize` and queued as job metadata. |
| Solver callback | `/api/external/compute/callback` | Updates task status and, on success, persists solver results. |

| Output | Destination | Notes |
| --- | --- | --- |
| `diagram.parameters` | MongoDB `diagram` | `/start` writes the freshly translated solver-facing `parameters`. |
| `computationTask` | MongoDB | Created as `waiting`, updated to `computing`, then terminal `success`, `failed`, `timeout`, or `aborted`. |
| `computationTask:${diagramId}` | Redis | Cached by `getLatestComputationTask` for 5 minutes and invalidated on task insert/update/delete. |
| Bull job | Redis-backed `computationDispatchQueue` | Contains `diagramId`, names, user metadata, and `canvasWithModelVersions`. |
| Solver request | External solver `${BASE_SOLVER_ENGINE_URL}/solve/` | Contains `callback_url`, `configuration`, and `parameters`. |
| `ComputationResults` rows | PostgreSQL | Upserted in batches from callback `results.tps_specs`. |
| Diagram, node, and TP change updates | MongoDB | Applied during success callback processing. |

## Solver-Facing Payload Contract

`buildSolveRequest(configuration, parameters)` returns the object sent to the solver:

```ts
{
  callback_url: `${BASE_EXTERNAL_URL}/compute/callback/`,
  configuration: {
    max_computation_time: number | null,
    solver: {
      solver_name: string,
      attributes: Array<{ attribute_name: string; value: string | number | null }>
    } | null,
    algorithm: {
      algorithm_name: string,
      attributes: Array<{ attribute_name: string; value: string | number | null }>
    } | null
  },
  parameters: {
    global_params: object,
    models: object[],
    nodes: object[],
    tps_specs: object[],
    stream_connectivity: object[],
    material_properties: object[],
    material_fractions: object[],
    costs?: {
      entities: object[],
      mappings: object[],
      duration: object[]
    }
  }
}
```

Important exact fields:

- `parameters` is the translated diagram payload stored on `diagram.parameters` before queue dispatch.
- `parameters.tps_specs` is the main variable-spec array consumed by the solver and later matched against callback results.
- `parameters.costs` is present when `computeRoutes.ts` passes a `costsPayload` into `translation(...)`; it contains sanitized `entities`, `mappings`, and `duration`.

The worker loads `diagram.parameters` from MongoDB when processing the queue job. The queued `canvasWithModelVersions` is not the final solver payload in the current worker implementation.

## Core State and Data Structures

- `ComputationStatus.waiting`: task exists and is queued but has not received a solver `task_id`.
- `ComputationStatus.computing`: solver accepted the request and returned `task_id`.
- `ComputationStatus.success`: callback succeeded and `handleComputationSuccess` completed.
- `ComputationStatus.failed`: dispatch failed or the solver callback returned `failed`.
- `ComputationStatus.timeout`: solver callback returned `timeout`.
- `ComputationStatus.aborted`: user abort succeeded or solver reported the task was already terminated.
- `computeUploadSessions`: in-memory upload session map with 30-minute TTL cleanup.
- `computationTask:${diagramId}`: Redis cache key for the latest computation task.
- `computationDispatchQueue`: Bull queue backed by Redis `TASK_QUEUE_REDIS_DB` or DB `1`, with `removeOnComplete` and `removeOnFail`.

## Main Functions and Routes

- `POST /api/compute/start`: validates request fields, expands subnetwork instances, loads node model versions and TP rows, builds `parameters`, writes `diagram.parameters`, creates a waiting task, and enqueues dispatch.
- `POST /api/compute/upload/init`: creates an in-memory chunk upload session after diagram ownership checks.
- `POST /api/compute/upload/:sessionId/chunk`: stores a string chunk in the upload session.
- `POST /api/compute/upload/:sessionId/finalize`: reassembles uploaded JSON, creates a waiting task, and enqueues dispatch.
- `GET /api/compute/details/:diagramId`: returns status-specific polling information and queue-position details for waiting tasks.
- `GET /api/compute/history/:diagramId`: returns task history for the diagram.
- `DELETE /api/compute/results`: deletes PostgreSQL result rows and matching MongoDB tasks for a `diagramId` and `runName`.
- `POST /api/compute/abort`: calls solver `/kill/` when `taskId` exists and marks the MongoDB task as `aborted`.
- `ComputationTaskService.translateComputationConfig(...)`: reads snapshot `runConfigs` and builds the stored solver and algorithm configuration blocks.
- `createComputationTask(...)`: posts the solve request to `${BASE_SOLVER_ENGINE_URL}/solve/` and expects `status` plus `task_id`.
- `killComputationTask(...)`: posts `{ task_id }` to `${BASE_SOLVER_ENGINE_URL}/kill/` and treats solver `404` or `409` as already terminated.
- `handleComputationSuccess(...)`: applies reverse translation, writes computed TP changes, persists node and diagram updates, stores PostgreSQL result rows, and updates the task.

## Data Flow

1. The frontend calls `POST /api/compute/start` with `diagramId`, `maxComputationTime`, `runName`, `solverName`, and `algorithmName`.
2. `computeRoutes.ts` loads the diagram, snapshot data, nodes, TP rows, persisted TP changes, cost entities, and cost mappings.
3. `translation(...)` builds the solver-facing `parameters`, including `parameters.tps_specs` and optional `parameters.costs`.
4. The route writes `parameters` back to the MongoDB diagram record.
5. `ComputationTaskService.insertComputationTask(...)` creates a MongoDB task with status `waiting` and invalidates the Redis task cache.
6. `computationDispatchQueue.add(...)` stores a Bull job in Redis.
7. `computationDispatchWorker.ts` consumes one job at a time, reloads the task and diagram, wraps `diagram.parameters` with `callback_url` and `configuration`, then posts the request to the solver.
8. The solver returns `task_id`; the worker stores it on the MongoDB task and changes status to `computing`.
9. The worker loops until the task changes away from a processing status.
10. The solver posts to `/api/external/compute/callback`.
11. The callback route updates failed or timeout tasks directly; success callbacks call `handleComputationSuccess(...)`.
12. Success handling reverse-translates results, upserts PostgreSQL result rows, writes MongoDB diagram/node/TP changes, and marks the task `success`.

## Queue and Redis Boundaries

Bull queue state and task status are separate:

- Bull tracks whether a job is waiting, active, completed, failed, or stalled in Redis.
- MongoDB `computationTask.status` is the application-visible compute status.
- `getTasksAhead(diagramId)` reads Bull active and waiting jobs, sorts by enqueue timestamp, and then checks each job's MongoDB task status.
- `getLatestComputationTask(diagramId)` first checks Redis cache, then MongoDB, and caches the task for 5 minutes.
- Task insert, update, and result deletion delete the Redis cache key so polling does not keep a stale status.

`COMPUTATION_CONSTANTS.MAX_CONCURRENT_WORKERS` is `1`, so the current worker is intentionally serialized. The worker also holds the active job while the solver task is still `waiting` or `computing`.

## Callback, Status, and Result Flow

The external callback route is mounted as:

```text
POST /api/external/compute/callback
```

It passes through the `authenticateGateway` middleware. In the current source, that middleware logs the request and immediately calls `next()`; it does not validate `GATEWAY_SECRET` or reject missing `x-gateway-secret` headers. The Swagger metadata still documents a gateway secret header, but secret validation should be treated as intended hardening rather than current runtime behavior.

Callback body:

```ts
{
  task_id: string,
  status: "success" | "failed" | "timeout",
  results?: Record<string, unknown>,
  start_time?: Date,
  end_time?: Date,
  message?: string
}
```

Current implementation details:

- `task_id` and `status` are required.
- `status` must be one of `success`, `failed`, or `timeout`.
- `results` is required only when `status` is `success`.
- `message` is stored as `errorMessage` for failed or timeout callbacks when it is a string; the implementation does not reject a failed or timeout callback that omits `message`.
- If the task is already terminal, including `aborted`, the callback returns `409` and does not overwrite the terminal state.
- A successful callback calls `handleComputationSuccess(results, diagramId, computationTaskId, updates)`.

Successful callback persistence includes:

- Updating `parameters.tps_specs` values from callback machine-generated values.
- Updating base-period node `modelVersion` values and `is_computed`.
- Creating or updating computed MongoDB `tpChanges` for non-base time periods.
- Updating parent, subnetwork instance, and wrapper-node diagrams when subnetwork mappings are present.
- Upserting PostgreSQL `ComputationResults` rows from `results.tps_specs`.
- Updating the MongoDB `computationTask` with terminal status and callback timestamps.

## Result Persistence

`storeComputationResults(...)` reads `results.tps_specs`. Each output spec may carry `machine_generated_values` as an array, an object keyed by TP range such as `"1-3"`, or a scalar. The utility normalizes those values into result rows.

Rows are keyed by:

```text
diagram_id, run_name, node_id, port_name, port_var_name, from_tp, to_tp
```

The insert uses PostgreSQL `ON CONFLICT` to update value, bounds, spec, unit, type, solver, algorithm, network, subnetwork, and node name. Writes are batched with `COMPUTATION_RESULTS_BATCH_SIZE = 1000`.

MongoDB persistence happens in `handleComputationSuccess(...)`, not in `storeComputationResults(...)`. The handler updates node `modelVersion`, diagram `canvas`, diagram `parameters`, computed `tpChanges`, and the task status.

## Error Handling and Edge Cases

- `/start` rejects missing required fields and `maxComputationTime` below the configured minimum.
- `/start` rejects diagrams with missing persisted node model versions, duplicate stream instances after subnetwork expansion, or missing domain model definitions.
- `/start` and upload finalize reject users who already have a processing task.
- Upload finalize deletes the in-memory upload session after parse errors, authorization errors, missing diagrams, duplicate processing tasks, and successful queueing.
- The worker marks the task `failed` if solver dispatch throws after a task id is available locally.
- `/details/:diagramId` reports `waiting`, `computing`, `failed`, `aborted`, `timeout`, and `success` with different polling behavior.
- `/abort` returns an error if the latest task is not processing; if the solver says the task is already terminated, the route still marks the local task as aborted.
- Callback requests for already terminal tasks return `409` and do not reprocess results.

## Extension Points

- Add a new compute route in `computeRoutes.ts`, then decide whether it should create a MongoDB task, enqueue a Bull job, or only read status.
- Add a new solver configuration field by updating snapshot `runConfigs`, `ComputationTaskService.translateComputationConfig(...)`, and callback/result documentation together.
- Add a new solver payload field by updating `translation.ts`, verifying the final `parameters` shape, and extending tests under `src/tests/backend/utils/`.
- Add a new callback status by updating `CallbackStatus`, `callbackToComputationStatusMap`, `isComputationProcessing` if needed, and `/details/:diagramId` response handling.
- Change result storage only with `storeComputationResultUtils.ts`, PostgreSQL schema constraints, and result-history UI expectations in mind.

## Testing and Verification

Existing related backend utility tests are under:

- `src/tests/backend/utils/translation.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`
- `src/tests/backend/utils/translationEmbeddedModelVersion.test.ts`
- `src/tests/backend/utils/reverseTranslation.test.ts`
- `src/tests/backend/utils/economicCosts.test.ts`

Focused verification for payload and reverse-translation changes:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npx.cmd jest tests/backend/utils/translation.test.ts tests/backend/utils/translationCosts.test.ts tests/backend/utils/translationEmbeddedModelVersion.test.ts tests/backend/utils/reverseTranslation.test.ts --runInBand --coverage=false
```

Manual integration check:

1. Start the backend, Redis, MongoDB, PostgreSQL, and solver engine.
2. Run `/api/compute/start` from the UI.
3. Poll `/api/compute/details/:diagramId`.
4. Confirm the solver receives `callback_url`, `configuration`, and `parameters`.
5. Confirm callback success produces updated diagram parameters plus PostgreSQL `ComputationResults` rows.

There is no dedicated route or worker test in `src/tests/backend/utils/`; route, queue, and callback changes need either a focused integration test or a manual end-to-end check.

## Known Cautions

- `src/src/backend/services/solve_request.json` is written only when `SAVE_JSON_FILES === 'true'`. It mirrors one local runtime request and may be stale.
- `src/src/backend/routes/external/callback_response.json` is also optional and can represent an older callback.
- `src/tests/backend/utils/paramResult.json` can be overwritten by `handleComputationSuccess(...)` during runtime callback processing.
- Do not hand-edit these files to define behavior. Use source files and tests as the source of truth, then use generated artifacts only for read-only confirmation.
- Do not commit generated solver or callback JSON unless a task explicitly asks for a fixture update.
- Current `authenticateGateway` behavior is pass-through logging. Enforcing `x-gateway-secret` would require a code change and should be documented separately when implemented.

## Related Pages

- `docs/CodeExplanation/translation-and-reverse-translation.md`
- `docs/CodeExplanation/save-diagram-and-node-cache.md`
- `docs/CodeExplanation/subnetwork-blueprint-and-instance-flow.md`
