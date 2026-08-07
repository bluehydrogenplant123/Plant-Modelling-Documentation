---
title: Compute, Solver Callback, and Results Code Explanation
sidebar_position: 30
description: Explains how HyProNet binds active TP Spec versions and selected run inputs, starts computation tasks, dispatches solver requests, receives callbacks, and persists traceable results.
---

## Overview

The compute workflow starts from authenticated `/api/compute` routes, stores a MongoDB `computationTask`, dispatches a Bull queue job, sends the final solver request to the external solver engine, and records the solver callback into diagrams, nodes, time-period changes, and PostgreSQL computation-result rows.

The current source of truth is the TypeScript path from `computeRoutes.ts` through the worker, solver API service, callback route, reverse translation, and result storage. Generated JSON files such as `solve_request.json` are useful for read-only debugging only.

## Source Files

- `src/src/backend/routes/computeRoutes.ts`: authenticated compute API routes for start, chunk upload, selected-input resolution, details polling, history, result deletion, and abort.
- `src/src/backend/config/taskQueue/computationDispatchQueue.ts`: Bull queue instance named `computationDispatchQueue`.
- `src/src/backend/config/taskQueue/baseTaskQueue.ts`: Redis-backed Bull queue setup, Bull Board registration, and queue event logging.
- `src/src/backend/workers/computationDispatchWorker.ts`: queue consumer that builds and sends the solver request, updates task status, and waits for callback completion.
- `src/src/backend/services/computationTaskService.ts`: MongoDB task CRUD, Redis cache reads and invalidation, queue-position reporting, and run-configuration translation.
- `src/src/backend/services/solveInputTranslationService.ts`: resolves Optimization/DataRec selection ids against saved records and creates the queued-task selected-input snapshot.
- `src/src/backend/services/solverEngineApiService.ts`: builds the solver request, posts to `/solve/`, optionally writes `solve_request.json`, and posts `/kill/` for abort.
- `src/src/backend/routes/external/computeCallbackRoutes.ts`: gateway-authenticated callback endpoint for solver `success`, `failed`, and `timeout` statuses.
- `src/src/backend/services/computationTaskHandler.ts`: success-callback handler that applies reverse translation and persists callback side effects.
- `src/src/backend/utils/reverseTranslation.ts`: maps solver `results.tps_specs` back into parameters, node model versions, and computed TP changes.
- `src/src/backend/utils/storeComputationResultUtils.ts`: stores solver machine-generated values in PostgreSQL `ComputationResults`.
- `src/src/backend/utils/tpSpecVersionUtils.ts`: resolves active TP Spec version sets and logical tables by diagram, scope, and calculation type.
- `src/src/backend/prisma/mongodb/schema.prisma`: stores version ids, calculation type, and change source on computed `TpChanges`.
- `src/src/backend/prisma/postgres/schema.prisma`: stores TP Spec traceability fields on computation results.
- `src/src/backend/prisma/postgres/migrations/20260630000100_add_tp_spec_version_to_computation_results/migration.sql`: adds the PostgreSQL traceability columns.

## Purpose and Responsibility

The compute route layer owns request validation, user authorization, selected Optimization/DataRec input resolution, parameter generation, task creation, and polling responses. It does not directly call the solver. Solver dispatch belongs to the Bull worker, and callback processing belongs to the external callback route plus `handleComputationSuccess`.

The solver API service owns the external HTTP contract. It appends `/solve/`, `/kill/`, and `/compute/callback/` to configured base URLs. Environment values should therefore stay as base URLs, for example `BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api` and `BASE_EXTERNAL_URL=http://localhost:3000/api/external`.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `diagramId` | `/api/compute/start`, `/details/:diagramId`, `/history/:diagramId`, `/abort`, `/results` | Selects the diagram, task, result rows, and Redis cache key. |
| `maxComputationTime` | `/api/compute/start` body or upload metadata | Stored as `configuration.max_computation_time`; `/start` rejects values below `COMPUTATION_CONSTANTS.MINIMUM_COMPUTATION_TIME`. |
| `runName` | `/start`, `/upload/init`, `/results` | Stored on `computationTask` and used as part of the PostgreSQL result identity. |
| `solverName`, `algorithmName` | `/start` or upload metadata | Looked up in snapshot `runConfigs` and stored in task `configuration`. |
| `optimizationOptions` | `/start` body or upload metadata when the saved task type is Optimization | Selects mode, Objective Function Sets, and Additional Constraint Sets by id. |
| `dataRecOptions` | `/start` body or upload metadata when the saved task type is DataRec | Selects one Instrument Set, Plant Measurements, and Objective Function Sets by id. |
| TP Spec active context | Diagram TP mode, run calculation type, and MongoDB version metadata | Selects the Base patches or MTP changes used for translation and identifies the version in solve metadata. |
| `tpChanges` | Optional `/start` body plus active-version MongoDB changes | Merged before translation so explicit request overrides can affect `parameters.tps_specs`. |
| Chunk payload | `/upload/:sessionId/chunk` | Reassembled by `/upload/:sessionId/finalize` and queued as job metadata. |
| Solver callback | `/api/external/compute/callback` | Updates task status and, on success, persists solver results. |

| Output | Destination | Notes |
| --- | --- | --- |
| `diagram.parameters` | MongoDB `diagram` | `/start` writes freshly translated base parameters; selected inputs and saved equation/collection data are added later during dispatch. |
| `computationTask` | MongoDB | Created as `waiting`, updated to `computing`, then terminal `success`, `failed`, `timeout`, or `aborted`. |
| `configuration.selected_inputs` | MongoDB computation task | Internal authoritative snapshot resolved before queueing; removed from solver configuration during request assembly. |
| `computationTask:${diagramId}` | Redis | Cached by `getLatestComputationTask` for 5 minutes and invalidated on task insert/update/delete. |
| Bull job | Redis-backed `computationDispatchQueue` | Contains `diagramId`, names, user metadata, and `canvasWithModelVersions`. |
| Solver request | External solver `${BASE_SOLVER_ENGINE_URL}/solve/` | Contains `callback_url`, `configuration`, and `parameters`, including normalized equations/collections and optional `parameters.solve_inputs`. |
| `ComputationResults` rows | PostgreSQL | Upserted in batches from callback `results.tps_specs`, including calculation type and applied TP Spec metadata. |
| Diagram, node, and TP change updates | MongoDB | Applied during success callback processing; computed MTP rows are scoped to a TP Spec version table when context resolution succeeds. |

## Solver-Facing Payload Contract

The worker calls:

```ts
buildSolveRequest(
  computationTask.configuration,
  diagram.parameters,
  diagram.equations,
  diagram.collections,
  diagram.solualgolib,
  unitConversions
)
```

The returned object sent to the solver has this high-level shape:

```ts
{
  callback_url: `${BASE_EXTERNAL_URL}/compute/callback/`,
  configuration: {
    max_computation_time: number | null,
    solver: object | null,
    algorithm: "SoluAlgoLib" | null,
    solution_algo_library: object[]
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
    },
    equations?: object[],
    equation_collections?: Array<{
      id: string,
      name: string,
      sets: string[]
    }>,
    solve_inputs?: {
      calculation_type: "Optimization" | "DataRec",
      optimization?: object,
      data_reconciliation?: object
    }
  }
}
```

Important exact fields:

- `parameters` is the translated diagram payload stored on `diagram.parameters` before queue dispatch.
- `parameters.tps_specs` is the main variable-spec array consumed by the solver and later matched against callback results.
- `parameters.costs` is present when `computeRoutes.ts` passes a `costsPayload` into `translation(...)`; it contains sanitized `entities`, `mappings`, and `duration`.
- `parameters.global_params.task_config` identifies the active TP Spec context with `tp_spec_scope`, `tp_spec_version`, `tp_spec_version_name`, `active_tp_spec_table`, `active_tp_spec_version_set_id`, and `active_tp_spec_version_table_id`.
- `configuration.solution_algo_library` contains normalized SoluAlgoLib rows whose set/collection links are ids.
- `parameters.equations` is rebuilt from saved `diagram.equations`; variable token bounds are converted to base units for the solver copy.
- `parameters.equation_collections` is rebuilt from saved collections with id-only set references.
- `parameters.solve_inputs` comes from the queued task's internal `configuration.selected_inputs`. Selected sets contain equation-id references; DataRec contains the selected Instrument Set, all mappings from that set, selected measurements, and selected Objective Function Sets.
- Before those fields are attached, `removeIndependentSolveInputParameters(...)` removes stale equation/set/constraint/instrument/measurement/Optimization/DataRec copies from saved `diagram.parameters`.

The worker loads the task and diagram from MongoDB when processing the queue job. The queued `canvasWithModelVersions` is not the final solver payload in the current worker implementation. The exact selected-input shapes and their editor-to-solver boundary are documented in [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md).

## Core State and Data Structures

- `ComputationStatus.waiting`: task exists and is queued but has not received a solver `task_id`.
- `ComputationStatus.computing`: solver accepted the request and returned `task_id`.
- `ComputationStatus.success`: callback succeeded and `handleComputationSuccess` completed.
- `ComputationStatus.failed`: dispatch failed or the solver callback returned `failed`.
- `ComputationStatus.timeout`: solver callback returned `timeout`.
- `ComputationStatus.aborted`: user abort succeeded or solver reported the task was already terminated.
- `SolveInputSnapshot`: Optimization or DataRec selection values resolved from persisted data before the task enters the queue.
- `configuration.selected_inputs`: internal task-only location for that snapshot. `buildSolveRequest(...)` removes it from configuration and emits normalized `parameters.solve_inputs`.
- `computeUploadSessions`: in-memory upload session map with 30-minute TTL cleanup.
- `computationTask:${diagramId}`: Redis cache key for the latest computation task.
- `computationDispatchQueue`: Bull queue backed by Redis `TASK_QUEUE_REDIS_DB` or DB `1`, with `removeOnComplete` and `removeOnFail`.

## Main Functions and Routes

- `POST /api/compute/start`: validates request fields, expands subnetwork instances, resolves selected run inputs and active TP Spec contexts, loads node model versions and version-scoped TP rows, builds `parameters`, writes `diagram.parameters`, creates a waiting task, and enqueues dispatch.
- `POST /api/compute/upload/init`: creates an in-memory chunk upload session after diagram ownership checks.
- `POST /api/compute/upload/:sessionId/chunk`: stores a string chunk in the upload session.
- `POST /api/compute/upload/:sessionId/finalize`: reassembles uploaded JSON, creates a waiting task, and enqueues dispatch.
- `GET /api/compute/details/:diagramId`: returns status-specific polling information and queue-position details for waiting tasks.
- `GET /api/compute/history/:diagramId`: returns task history for the diagram.
- `DELETE /api/compute/results`: deletes PostgreSQL result rows and matching MongoDB tasks for a `diagramId` and `runName`.
- `POST /api/compute/abort`: calls solver `/kill/` when `taskId` exists and marks the MongoDB task as `aborted`.
- `ComputationTaskService.translateComputationConfig(...)`: reads snapshot `runConfigs` and builds the stored solver and algorithm configuration blocks.
- `translateSolveInputSelection(...)`: reloads selected set/instrument/measurement records, enforces type and ownership constraints, and returns a queue-safe snapshot for Optimization or DataRec.
- `buildSolveRequest(...)`: strips stale parameter copies, removes internal `selected_inputs` from configuration, adds `parameters.solve_inputs`, and normalizes equations, collections, and SoluAlgoLib rows.
- `createComputationTask(...)`: posts the solve request to `${BASE_SOLVER_ENGINE_URL}/solve/` and expects `status` plus `task_id`.
- `killComputationTask(...)`: posts `{ task_id }` to `${BASE_SOLVER_ENGINE_URL}/kill/` and treats solver `404` or `409` as already terminated.
- `handleComputationSuccess(...)`: applies reverse translation, writes computed TP changes, persists node and diagram updates, stores PostgreSQL result rows, and updates the task.

## Data Flow

1. The frontend calls `POST /api/compute/start` with `diagramId`, timing/run fields, solver/algorithm names, and the active calculation type's identifier-only `optimizationOptions` or `dataRecOptions`.
2. `computeRoutes.ts` loads the diagram and derives the calculation type from saved `diagram.parameters.global_params.task_config.task_type`.
3. `translateSolveInputSelection(...)` resolves selected ids against saved diagram sets and, for DataRec, MongoDB Instrument Set, mapping, and measurement records.
4. The route keeps the authoritative result as `configuration.selected_inputs`; invalid or stale selections return a `400` before queueing.
5. The route loads snapshot data, nodes, TP rows, cost entities, and cost mappings, then resolves the active TP Spec set/table for the main and related diagrams.
6. The route loads only active-table MTP changes, with fully unversioned compatibility rows, or converts active Base patches into translation overrides.
7. `translation(...)` builds the solver-facing base `parameters`, including `parameters.tps_specs` and optional `parameters.costs`.
8. The route attaches the main diagram's active TP Spec metadata and writes the final base `parameters` back to the MongoDB diagram record.
9. `ComputationTaskService.insertComputationTask(...)` creates a MongoDB task with status `waiting`, including the selected-input snapshot, and invalidates the Redis task cache.
10. `computationDispatchQueue.add(...)` stores a Bull job in Redis.
11. `computationDispatchWorker.ts` consumes one job at a time and reloads the task and diagram.
12. `buildSolveRequest(...)` combines base parameters with selected inputs, saved equations, collections, SoluAlgoLib configuration, callback URL, and unit conversions.
13. The solver returns `task_id`; the worker stores it on the MongoDB task and changes status to `computing`.
14. The worker loops until the task changes away from a processing status.
15. The solver posts to `/api/external/compute/callback`.
16. The callback route updates failed or timeout tasks directly; success callbacks call `handleComputationSuccess(...)`.
17. Success handling reverse-translates results, writes version-scoped computed TP changes, upserts traceable PostgreSQL result rows, writes diagram/node state, and marks the task `success`.

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
- Tagging computed TP changes with the resolved version set/table ids, calculation type, and `changeSource: "COMPUTED"` without overwriting manual rows.
- Updating parent, subnetwork instance, and wrapper-node diagrams when subnetwork mappings are present.
- Upserting PostgreSQL `ComputationResults` rows from `results.tps_specs`.
- Updating the MongoDB `computationTask` with terminal status and callback timestamps.

## Result Persistence

`storeComputationResults(...)` reads `results.tps_specs`. Each output spec may carry `machine_generated_values` as an array, an object keyed by TP range such as `"1-3"`, or a scalar. The utility normalizes those values into result rows.

Rows are keyed by:

```text
diagram_id, run_name, node_id, port_name, port_var_name, from_tp, to_tp
```

The insert uses PostgreSQL `ON CONFLICT` to update value, bounds, spec, unit, type, solver, algorithm, network, subnetwork, node name, calculation type, TP Spec scope, TP Spec version code, and TP Spec logical table. Writes are batched with `COMPUTATION_RESULTS_BATCH_SIZE = 1000`.

`storeComputationResults(...)` extracts traceability metadata from the first parameter source whose `global_params.task_config` contains calculation-type or TP Spec fields:

| Result column | Task-config source |
| --- | --- |
| `calc_type` | `task_type` |
| `tp_spec_scope` | `tp_spec_scope` |
| `tp_spec_version` | `tp_spec_version` |
| `tp_spec_table` | `active_tp_spec_table` |

MongoDB persistence happens in `handleComputationSuccess(...)`, not in `storeComputationResults(...)`. The handler updates node `modelVersion`, diagram `canvas`, diagram `parameters`, computed `tpChanges`, and the task status.

## Error Handling and Edge Cases

- `/start` rejects missing required fields and `maxComputationTime` below the configured minimum.
- `/start` and upload finalize reject stale or wrong-type selected equation sets, invalid DRO radius, cross-user/cross-diagram Instrument Sets, missing selected measurements, measurements with validation errors, invalid plant values, and broken measurement-to-mapping joins.
- DataRec measurement ids cannot be supplied without an Instrument Set id.
- `/start` rejects diagrams with missing persisted node model versions, duplicate stream instances after subnetwork expansion, or missing domain model definitions.
- `/start` and upload finalize reject users who already have a processing task.
- Upload finalize deletes the in-memory upload session after parse errors, authorization errors, missing diagrams, duplicate processing tasks, and successful queueing.
- The worker marks the task `failed` if solver dispatch throws after a task id is available locally.
- `/details/:diagramId` reports `waiting`, `computing`, `failed`, `aborted`, `timeout`, and `success` with different polling behavior.
- `/abort` returns an error if the latest task is not processing; if the solver says the task is already terminated, the route still marks the local task as aborted.
- Callback requests for already terminal tasks return `409` and do not reprocess results.
- Compute start logs and skips an unresolved related-diagram TP Spec context, but the main diagram context must resolve before metadata can be attached.

## Extension Points

- Add a new compute route in `computeRoutes.ts`, then decide whether it should create a MongoDB task, enqueue a Bull job, or only read status.
- Add a new solver configuration field by updating snapshot `runConfigs`, `ComputationTaskService.translateComputationConfig(...)`, and callback/result documentation together.
- Add a new solver payload field by updating `translation.ts`, verifying the final `parameters` shape, and extending tests under `src/tests/backend/utils/`.
- Add or change Optimization/DataRec run selections by updating the frontend identifier builder, `solveInputTranslationService.ts`, `ComputationConfiguration.selected_inputs`, `normalizeSelectedSolveInputs(...)`, and focused service/worker tests together.
- Add a new callback status by updating `CallbackStatus`, `callbackToComputationStatusMap`, `isComputationProcessing` if needed, and `/details/:diagramId` response handling.
- Change result storage only with `storeComputationResultUtils.ts`, PostgreSQL schema constraints, and result-history UI expectations in mind.
- Change TP Spec version binding only with `computeRoutes.ts`, `computationTaskHandler.ts`, result metadata, legacy unversioned rows, and the read-only-during-computation guard in mind.

## Testing and Verification

Existing related backend utility tests are under:

- `src/tests/backend/services/solveInputTranslationService.test.ts`
- `src/tests/backend/services/solverEngineApiService.test.ts`
- `src/tests/backend/workers/computationDispatchWorker.test.ts`
- `src/tests/backend/utils/translation.test.ts`
- `src/tests/backend/utils/translationCosts.test.ts`
- `src/tests/backend/utils/translationEmbeddedModelVersion.test.ts`
- `src/tests/backend/utils/reverseTranslation.test.ts`
- `src/tests/backend/utils/economicCosts.test.ts`
- `src/tests/backend/utils/storeComputationResultUtils.test.ts`

Focused verification for payload and reverse-translation changes:

```bash
cd src
npx jest tests/backend/services/solveInputTranslationService.test.ts tests/backend/services/solverEngineApiService.test.ts tests/backend/workers/computationDispatchWorker.test.ts tests/backend/utils/translation.test.ts tests/backend/utils/translationCosts.test.ts tests/backend/utils/translationEmbeddedModelVersion.test.ts tests/backend/utils/reverseTranslation.test.ts tests/backend/utils/storeComputationResultUtils.test.ts --runInBand --coverage=false
```

Manual integration check:

1. Start the backend, Redis, MongoDB, PostgreSQL, and solver engine.
2. Run `/api/compute/start` from the UI.
3. Poll `/api/compute/details/:diagramId`.
4. Confirm the solver receives `callback_url`, `configuration`, and `parameters`.
5. For Optimization/DataRec, confirm the matching `parameters.solve_inputs` exists and `configuration.selected_inputs` does not reach the solver.
6. Confirm `parameters.equations` contains the normalized equation catalog while selected sets use equation ids.
7. Confirm `parameters.global_params.task_config` identifies the active TP Spec version used by the run.
8. Confirm callback success produces version-scoped computed TP changes plus PostgreSQL `ComputationResults` rows carrying the expected `calc_type`, `tp_spec_scope`, `tp_spec_version`, and `tp_spec_table`.

Selected-input translation, solver assembly, and worker argument handoff have focused tests. Full compute-route, queue, and callback behavior still needs either a focused integration test or a manual end-to-end check. The existing result-storage test also does not assert the four TP Spec metadata values, so that remains a focused coverage gap.

## Known Cautions

- `src/src/backend/services/solve_request.json` is written only when `SAVE_JSON_FILES === 'true'`. It mirrors one local runtime request and may be stale.
- `src/src/backend/routes/external/callback_response.json` is also optional and can represent an older callback.
- `src/tests/backend/utils/paramResult.json` can be overwritten by `handleComputationSuccess(...)` during runtime callback processing.
- Do not hand-edit these files to define behavior. Use source files and tests as the source of truth, then use generated artifacts only for read-only confirmation.
- Do not commit generated solver or callback JSON unless a task explicitly asks for a fixture update.
- `configuration.selected_inputs` is an internal queued snapshot. It must be stripped before solver dispatch and must not be confused with persisted base `diagram.parameters`.
- `removeIndependentSolveInputParameters(...)` removes stale parameter copies, after which `buildSolveRequest(...)` deliberately adds the authoritative saved equation catalog back as `parameters.equations`.
- Selected set membership is snapshotted before queueing, but the worker reloads full top-level equation definitions from `diagram.equations` at dispatch. Avoid editing equations while an older task is waiting.
- Current `authenticateGateway` behavior is pass-through logging. Enforcing `x-gateway-secret` would require a code change and should be documented separately when implemented.
- The callback handler resolves the active TP Spec context at callback time. The normal UI keeps version actions read-only while computation is active; direct API clients should not switch the active version mid-run.
- Older PostgreSQL result rows can have null TP Spec metadata. New result queries and filters must preserve compatibility with those rows.

## Related Pages

- [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md)
- [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md)
- [TP Spec Version Management Code Explanation](./tp-spec-version-management.md)
- [Save Diagram and Node Cache Code Explanation](./save-diagram-and-node-cache.md)
- [Subnetwork Blueprint and Instance Flow Code Explanation](./subnetwork-blueprint-and-instance-flow.md)
