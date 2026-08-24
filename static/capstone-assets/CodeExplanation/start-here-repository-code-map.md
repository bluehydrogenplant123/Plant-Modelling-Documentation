---
title: "Start Here: Repository and GUI Code Map"
sidebar_position: 0
description: "The primary first-read guide that maps HyProNet GUI actions to frontend files, APIs, backend owners, and persistence boundaries."
---

# Start Here: Repository and GUI Code Map

> **This is the primary first-read code-navigation document for this repository.** Start here when you need to locate Login, User ID, Save, Import, Export, Duplicate, Verify, Run, or any other GUI action.

This guide maps user-visible features to their frontend component, HTTP boundary, backend implementation, and final data owner. It was checked against the source on **August 24, 2026**. Update it in the same pull request whenever a mapped feature changes.

## 1. How to use this guide

Trace a GUI feature in this order:

```text
GUI page, menu, or button
  -> React page or component
  -> Redux slice, hook, or frontend utility
  -> /api/... request
  -> backend/routes/index.ts mount point
  -> route handler
  -> service or backend utility
  -> MongoDB, PostgreSQL, Redis, or the Solver Engine
```

Status terms used below:

- **Implemented:** the frontend and required backend or local behavior are connected.
- **Frontend-only:** the action changes browser state or downloads a local file and does not immediately write to the backend.
- **Placeholder:** the control is disabled or has no handler.
- **Wiring gap:** the frontend sends a request for which the current backend has no route.

Search for API paths and component names rather than relying only on visible button text:

```bash
rg -n "diagrams/:diagramId/duplicate" src/src/backend/routes/dataRoutes.ts
rg -n "/api/data/diagrams/.*/verification" src/src/frontend/src
rg -n "Import Sys Materials|Import Node Definitions" src/src/frontend/src/components/header-bar
```

## 2. Repository layout

| Path | Purpose | Current source? |
| --- | --- | --- |
| `README.md` | Project overview and link to this guide. | Yes |
| `docs/CodeExplanation/` | Current developer-oriented code documentation. | Yes |
| `docs/Installation/` | Installation, startup, and real-server configuration. | Yes |
| `docs/UserGuide/` | End-user GUI instructions; this is not a code map. | Yes |
| `docs-archive/PreviousDoc/` | Historical documentation only. | No |
| `src/src/frontend/` | React, TypeScript, Vite, Redux, and React Flow frontend. | Yes |
| `src/src/backend/` | Express, Prisma, Bull, and Redis backend. | Yes |
| `src/src/shared/` | Pure TypeScript contracts and algorithms shared by both sides. | Yes |
| `src/tests/` | Frontend, backend, and integration tests. | Yes |
| `src/excel-migration/` | Imports system workbooks into PostgreSQL. | Yes |
| `src/excel-sheets/` | System-data workbooks and examples. | Input data |
| `src/generated/` | Generated Prisma clients; do not edit manually. | Generated |
| `src/dist/`, `src/coverage/`, `src/logs/` | Build output, coverage, and runtime logs. | Generated |
| `version6.1/` | An older release copy, not the active implementation. | No |

Primary runtime entry points:

- Frontend bootstrap: `src/src/frontend/src/main.tsx`
- Canvas application: `src/src/frontend/src/App.tsx`
- GUI menu assembly: `src/src/frontend/src/components/header-bar/index.tsx`
- Backend bootstrap: `src/src/backend/app.ts` and `src/src/backend/server.ts`
- API route assembly: `src/src/backend/routes/index.ts`
- Diagram and GUI-data API: `src/src/backend/routes/dataRoutes.ts`
- Computation API: `src/src/backend/routes/computeRoutes.ts`
- Data models: `src/src/backend/prisma/mongodb/schema.prisma` and `src/src/backend/prisma/postgres/schema.prisma`

## 3. Data ownership

| Data | Source of truth | Main code |
| --- | --- | --- |
| Users, refresh tokens, diagrams, node cache, TP changes, TP Spec versions, instrument sets, computation tasks, and subnetwork blueprints | MongoDB | `backend/prisma/mongodb/schema.prisma`, `backend/routes/dataRoutes.ts`, `backend/routes/userRoutes.ts` |
| Domains, model definitions, materials, streams, units, algorithms, system configuration, and computation result rows | PostgreSQL | `backend/prisma/postgres/schema.prisma`, `backend/routes/dataRoutes.ts`, `backend/services/storeComputationResultUtils.ts` |
| Temporary interaction state for the open page | React local state and Redux | `frontend/src/store.ts`, `frontend/src/features/**` |
| Browser copies of access and refresh tokens | `localStorage` | `frontend/src/AuthContext.tsx` |
| Waiting computation jobs | Redis and Bull | `backend/config/taskQueue/**`, `backend/workers/computationDispatchWorker.ts` |
| Solve execution | External Solver Engine | `backend/services/solverEngineApiService.ts`, `backend/routes/external/computeCallbackRoutes.ts` |
| Charts and TP Analysis dashboards | PostgreSQL bindings and the Metabase API | `dashboard-manager-button.tsx`, `metabase-button.tsx`, `dataRoutes.ts` |

The `userId` sent by the browser is not the authority for diagram ownership. Protected backend routes derive `req.user.id` from the verified JWT and use it when querying MongoDB.

## 4. Frontend map

In this section, `frontend/...` means `src/src/frontend/...` from the repository root.

### 4.1 Entry points, routes, and global state

| File | Responsibility |
| --- | --- |
| `frontend/src/main.tsx` | Mounts React, Redux, Router, and `AuthProvider`; declares `/login`, `/signup`, `/dashboard`, `/canvas/:domainId`, `/diagram/:diagramId`, and `/admin/config`. |
| `frontend/src/AuthContext.tsx` | Stores tokens, checks and refreshes authentication, retries one Axios 401, and exposes `userId`, `userData`, and `isAdmin`. |
| `frontend/src/routes/ProtectedRoute.tsx` | Redirects unauthenticated users to Login. |
| `frontend/src/routes/PublicRoute.tsx` | Redirects authenticated users away from Login and Signup. |
| `frontend/src/routes/AdminRoute.tsx` | Restricts System Configuration to `admin` and `owner` roles. |
| `frontend/src/pages/login.tsx` | Login form and `/api/auth/login` request. |
| `frontend/src/pages/signup.tsx` | Signup form and `/api/auth/signup` request. |
| `frontend/src/pages/dashboard.tsx` | Creates, opens, imports, exports, and deletes networks; manages blueprints and admin navigation. |
| `frontend/src/App.tsx` | React Flow canvas, loading, drag/drop, edge creation, deletion, display filters, computation polling, and auto-save triggers. |
| `frontend/src/store.ts` | Combines Redux slices. Most non-save actions mark the diagram as unsaved. |
| `frontend/src/react-flow-config.tsx` | Registers React Flow node and edge types and default settings. |

Important Redux slices:

| Slice | File | State owned |
| --- | --- | --- |
| `domain` | `features/domain/domainSlice.ts` | Current domain, model palette, streams/materials, run configuration, and subnetwork models. |
| `canvas` | `features/canvas/canvasSlice.ts` | Diagram ID/name/type, verification, TP mode, node names, parameters, computation status, and results. |
| `nodeCache` | `features/node/nodeCacheSlice.ts` | Detailed model versions per node, dirty flags, and MongoDB node-document mapping. |
| `saved` | `features/saved/savedSlice.ts` | Saved/saving state, last save time, and duration. |
| `equationWriting` | `features/equationWriting/equationWritingSlice.ts` | Equation Writing drafts and imported variables. |
| `constraintDrafts` | `features/constraint/constraintSlice.ts` | Set/collection drafts and SoluAlgo associations for `+Constr`. |
| `plantMeasurements` | `features/plantMeasurements/plantMeasurementSlice.ts` | Current Instrument Set and Plant Measurement editor drafts. |
| `alerts` | `features/alert/alertsSlice.ts` | Global notifications. |

### 4.2 Login, User ID, tokens, and authorization

| Feature | Frontend | API | Backend and persistence |
| --- | --- | --- | --- |
| Login | `pages/login.tsx` | `POST /api/auth/login` | `routes/userRoutes.ts` finds the MongoDB user, checks the bcrypt password, creates access/refresh JWTs, and stores the refresh token. |
| Obtain User ID | `AuthContext.tsx`, `checkAuthToken()` | `GET /api/auth/checktoken` | `userRoutes.ts` reads `userId` from the JWT and returns the user. The frontend stores `response.data.user.id` in `userId`; the Login response itself does not set it directly. |
| Refresh tokens | `AuthContext.tsx` | `POST /api/auth/token` | `userRoutes.ts` validates and rotates MongoDB refresh tokens; the Axios interceptor retries only once. |
| Signup | `pages/signup.tsx` | `POST /api/auth/signup` | `userRoutes.ts` hashes the password and creates the MongoDB user. |
| Logout | Dashboard and New Model call `AuthContext.logout()` | The current frontend does not call the logout API | `POST /api/auth/logout` exists, but the UI only clears browser tokens/state; the stored refresh token remains until expiry cleanup unless the API is called separately. |
| Page guards | `ProtectedRoute.tsx`, `PublicRoute.tsx` | None | Frontend guards are only for navigation UX; protected APIs still use `middleware/auth.ts`. |
| Admin access | `AdminRoute.tsx`, `pages/admin-config.tsx` | `/api/admin/**` | `middleware/auth.ts` supplies `requireAdmin`; admin route files enforce `admin` or `owner`. |

The complete User ID path is:

1. MongoDB `User.id` is the canonical user ID.
2. `userRoutes.ts` places it in the JWT payload as `userId`.
3. `middleware/auth.ts` verifies the JWT, reloads the user, and sets `req.user`.
4. Backend business routes use `req.user.id` for ownership filters.
5. `AuthContext.tsx` obtains the same ID through `/checktoken` and exposes `useAuth().userId` to the frontend.
6. `backend/types/express.d.ts` provides the Express type extension for `req.user`.

### 4.3 Dashboard and Canvas actions

| GUI action | Frontend owner | API / backend owner | Status and side effect |
| --- | --- | --- | --- |
| Dashboard: Create Diagram | `pages/dashboard.tsx` | No API at creation; first Save calls `POST /api/data/diagrams` | **Frontend-only until Save.** Initializes Redux and `temp_diagram_<domainId>`, then opens `/canvas/:domainId`. |
| Dashboard: Load | `pages/dashboard.tsx` | `GET /api/data/diagrams/:diagramId` in `dataRoutes.ts` | **Implemented.** Opens `/diagram/:diagramId`. |
| Dashboard: Import Diagram | `pages/dashboard.tsx`, `utils/diagramTransfer.ts` | Current format: `POST /api/data/diagrams/import`; legacy format: `POST /api/data/diagrams` | **Implemented.** The current snapshot path includes schema migration and owned related data. |
| Dashboard: Export | `pages/dashboard.tsx`, `utils/diagramTransfer.ts` | `GET /api/data/diagrams/:diagramId/export` | **Implemented.** Downloads a full snapshot and can preserve verification or export an unverified copy without changing the source. |
| Dashboard: Delete diagram | `pages/dashboard.tsx` | `DELETE /api/data/diagrams/:diagramId`, then `deleteDiagramWithCleanup()` | **Implemented and destructive.** Removes the diagram and related node/TP/task/subnetwork data. |
| Dashboard: Delete blueprint | `pages/dashboard.tsx` | `DELETE /api/data/subnetworks/:id`, followed by blueprint diagram deletion | **Implemented and destructive.** |
| Dashboard: System Configuration | `pages/dashboard.tsx` | Navigates to `/admin/config` | Visible only when `isAdmin` is true. |
| Load Canvas | `App.tsx` | `GET /api/data/diagrams/:diagramId`, plus node APIs on demand | **Implemented.** Base canvas loads first; node model versions use the node cache. |
| Add/connect/delete Canvas items | `App.tsx`, `sidebar/**`, `custom-edge/**` | Mostly React Flow/Redux until Save | Structural editing is restricted for a verified diagram. |
| Display | `header-buttons/display-button.tsx`, `App.tsx` | No dedicated persistence endpoint | **Frontend-only.** Filters and displays node labels, streams, parameters, and results. |

### 4.4 Header and Model menu actions

`frontend/src/components/header-bar/index.tsx` is the authoritative assembly point for top-level menus, visibility, modal state, selected items, and disabled/read-only rules.

| GUI action | Frontend file | API / backend owner | Status |
| --- | --- | --- | --- |
| Model: New Model | `model-buttons/create-diagram-modal.tsx` | First Save creates the diagram | **Frontend-only until Save.** |
| Model: Open | `model-buttons/open-network-modal.tsx` | Diagram list/detail routes in `dataRoutes.ts` | **Implemented.** |
| Model: Duplicate | `model-buttons/save-as-copy.tsx` | `POST /api/data/diagrams/:diagramId/duplicate` | **Implemented.** Uses a client `requestId`; the copy is always unverified. |
| Model: Extract | `model-buttons/extract-selection-button.tsx` | Subnetwork/diagram routes in `dataRoutes.ts` | **Implemented.** Extracts selected nodes to a network or blueprint. |
| Model: Save as Subnetwork | `model-buttons/save-as-subnetwork-button.tsx` | Subnetwork routes in `dataRoutes.ts` | **Implemented.** |
| Model: Equation Writing | `model-buttons/equation-writing-button.tsx`, `equation-writing-modal/**` | Saved through diagram state and computation inputs | **Implemented.** |
| Model: +Constr | `model-buttons/constraint-button.tsx`, `constraint-editor/**` | Constraint drafts flow into the save/computation payload | **Implemented.** |
| Model: Verify / Unverify | `model-buttons/verify-button.tsx` | `PATCH /api/data/diagrams/:diagramId/verification` | **Implemented.** Persists the canonical state and updates Redux. |
| Model: Base TP | `model-buttons/base-tp-button.tsx` | TP routes in `dataRoutes.ts` | **Implemented.** |
| Model: TP Specs | `header-buttons/tp-specs-button.tsx`, `tp-specs/**` | TP Spec version routes in `dataRoutes.ts` | **Implemented.** |
| Model: Import / Export | `model-buttons/import-export-model-button.tsx`, `import-export-modal.tsx`, `utils/diagramTransfer.ts` | `/diagrams/import` and `/diagrams/:id/export` | **Implemented** for Full Data snapshots; solver/algorithm run-config export has a wiring gap described below. |
| Model: Save and Restore | `header-buttons/save-and-restore.tsx`, `utils/save-util.tsx` | Diagram POST/PUT and node/TP routes | **Implemented.** This is the main manual save entry. |

Important import/export distinctions:

- Dashboard Export and Model > Export > Full Data use the full-network snapshot route.
- Open Network contains an export path that downloads the normal diagram GET response, which is not the same artifact as a full snapshot.
- New Model retains a legacy import path for older diagram JSON.
- Solver/Algorithm export calls `GET /api/data/run-configs/export`; no matching Express route exists in the current source.

### 4.5 User Tables, calculation type, and Run

| GUI action | Frontend file | API / backend owner | Status |
| --- | --- | --- | --- |
| User Tables | `header-buttons/user-tables-button.tsx`, `user-tables/**` | Material/domain endpoints in `dataRoutes.ts` | **Implemented.** Reads and edits user-owned material-domain data, including workbook import. |
| Calculation Type | `header-buttons/calc-type-button.tsx`, `calc-type/**` | Stored with diagram/run state; consumed by computation translation | **Implemented.** Controls Simulation, Optimization, or Data Reconciliation inputs. |
| Run | `header-buttons/computation-button.tsx` | `POST /api/compute/start` in `computeRoutes.ts` | **Implemented.** Validates selections, creates a task, and queues solver work. |
| Run status | `App.tsx`, computation hooks/components | `GET /api/compute/details/:diagramId` | **Implemented.** Polls waiting, computing, processing, success, and failure phases. |
| Run Result | `header-buttons/run-result-button.tsx` and result components | `/api/compute/history/:diagramId` and result endpoints | **Implemented.** Reads stored history and result data. |
| Cancel computation | computation status UI | Compute cancellation endpoint in `computeRoutes.ts` | **Implemented.** Cancels or marks the active task as appropriate to its phase. |

The central disable contract is `frontend/src/components/header-bar/computingDisableConfig.ts`. Any new header action must define whether it is allowed while a task is waiting, computing, or processing results.

### 4.6 Analysis, Multi-TP, TP Analysis, System, and Help

| Menu/action | Frontend owner | Backend owner | Status |
| --- | --- | --- | --- |
| Analysis: Instrument Set | `instrument-set/**` and Plant Measurement components | Instrument-set routes in `dataRoutes.ts` | **Implemented.** |
| Analysis: Expenses, Objective Function, Revenues | `header-bar/index.tsx` | None | **Placeholder.** Disabled controls. |
| Multi-TP: Economic | `economic/**` | Economic/TP routes in `dataRoutes.ts` | **Implemented** with verification guards. |
| Multi-TP: Global TP | `global-tp/**` | TP routes in `dataRoutes.ts` | **Implemented** with verification guards. |
| Multi-TP: Time Horizon, View Time Periods | `header-bar/index.tsx` | None | **Placeholder.** Disabled controls. |
| Multi-TP: TP Data | `header-bar/index.tsx` | None | **Placeholder.** Visible control without an action handler. |
| TP Analysis: Dashboard Manager | `header-buttons/dashboard-manager-button.tsx` | Dashboard binding routes in `dataRoutes.ts` and Metabase integration | **Implemented.** |
| TP Analysis: View Dashboard | `header-buttons/metabase-button.tsx` | Metabase API and stored bindings | **Implemented.** |
| System: Import Sys Materials | `header-bar/index.tsx` | No GUI route | **Placeholder.** No handler. |
| System: Import Node Definitions | `header-bar/index.tsx` | No GUI route | **Placeholder.** No handler. |
| Help: Documentation, Tutorial | `header-bar/index.tsx` | None | **Placeholder.** Disabled controls. |

### 4.7 System Configuration

Most administrator UI is concentrated in `frontend/src/pages/admin-config.tsx`. The backend is intentionally split by domain:

| Backend file | Responsibility |
| --- | --- |
| `routes/adminRoutes.ts` | Admin route assembly and shared configuration operations. |
| `routes/adminReferenceRoutes.ts` | Reference-data administration. |
| `routes/adminMetadataRoutes.ts` | Metadata administration. |
| `routes/adminDimensionRoutes.ts` | Dimension administration. |
| `routes/adminConstraintRoutes.ts` | Constraint administration. |
| `routes/adminDomainDiagramRoutes.ts` | Domain-diagram administration. |
| `middleware/auth.ts` | JWT authentication and `requireAdmin` authorization. |

## 5. Backend map

In this section, `backend/...` means `src/src/backend/...` from the repository root.

### 5.1 Startup and route mounting

| File | Responsibility |
| --- | --- |
| `backend/server.ts` | Starts the HTTP server and runtime infrastructure. |
| `backend/app.ts` | Builds the Express app, middleware, error handling, and API mount points. |
| `backend/routes/index.ts` | Mounts authentication, data, computation, admin, external callback, and other route groups. |
| `backend/middleware/auth.ts` | Verifies access JWTs, populates `req.user`, and enforces admin roles. |
| `backend/types/express.d.ts` | Types the authenticated Express request user. |

### 5.2 Main route files

| Route file | Main responsibilities |
| --- | --- |
| `routes/userRoutes.ts` | Signup, login, token refresh/rotation, token check, logout, and user lookup. |
| `routes/dataRoutes.ts` | Diagrams, nodes, save/load/delete, duplicate, verification, import/export, subnetworks, TP data, instrument sets, dashboards, materials, domains, and much of the GUI data API. |
| `routes/computeRoutes.ts` | Computation start, validation, task creation, status, history, results, and cancellation. |
| `routes/external/computeCallbackRoutes.ts` | Receives Solver Engine success/failure callbacks. |
| `routes/dashboardRoutes.ts` | Dashboard-related endpoints that are separate from the main data router. |
| `routes/admin*Routes.ts` | Protected System Configuration APIs. |
| `routes/versionRoutes.ts` | Version information. |

`dataRoutes.ts` is large. Search it by exact endpoint, helper name, or Prisma model before editing it. New independent domains should use a focused route/service rather than automatically expanding this file.

### 5.3 Backend services

| Service | Responsibility |
| --- | --- |
| `services/solverEngineApiService.ts` | Sends solve requests to the external Solver Engine. |
| `services/solveInputTranslationService.ts` | Resolves and translates selected computation inputs. |
| `services/computationTaskHandler.ts` | Handles successful and failed solver results and updates task state. |
| `services/storeComputationResultUtils.ts` | Stores normalized computation result rows in PostgreSQL. |
| `services/reverseTranslation.ts` | Converts solver output back to diagram, node, and TP structures. |
| `services/dashboardService.ts` | Dashboard and Metabase-related business logic. |
| `services/subnetworkService.ts` | Subnetwork business logic shared by routes. |

`backend/services/solve_request.json` is optional diagnostic output, not an API contract or source file.

### 5.4 Important backend utilities and models

| Area | Files | Responsibility |
| --- | --- | --- |
| Save/delete | `utils/saveDiagramUtils.ts`, `utils/deleteDiagramUtils.ts` | Persists diagrams and performs related-data cleanup. |
| Translation | `utils/translation.ts`, `services/solveInputTranslationService.ts` | Builds the solver-facing graph and parameters. |
| Callback filtering | `utils/callbackResultFiltering.ts` | Prevents inappropriate material-component results from being written back. |
| Graph assembly | `utils/edgesProcessor.ts`, `utils/globalParamsBuilder.ts` | Builds stream connectivity and global parameters. |
| Node cache | `utils/canvasModelVersionUtils.ts` | Attaches, detaches, and merges canvas nodes with separate model-version cache documents. |
| Full snapshots | `models/fullNetworkSnapshot.ts`, `utils/fullNetworkSnapshotUtils.ts` | Defines snapshot types, ID remapping, and owned-state cloning for import/export/duplicate. |
| Schema compatibility | `utils/schemaMigrations.ts` | Defines the current snapshot version and migration chain. |
| Component templates | `utils/componentTemplateBackendUtils.ts`, `shared/componentTemplateCore.ts` | Expands and validates material component templates. |
| Split fractions | `shared/splitFractionModel.ts`, `utils/translationTpsSpecsUtils.ts` | Handles SEPARATOR/ASU runtime identity and pre-computation checks. |
| Stream validation | `utils/streamInstanceValidation.ts`, `utils/streamComponentReferenceValidation.ts`, `utils/streamPropertySanitization.ts` | Validates names, equation references, and stream properties. |
| Computed writeback | `utils/computedWritebackProtection.ts` | Protects manual parameter and TP inputs from callback overwrites. |
| TP metadata | `utils/tpChangeMetadataUtils.ts`, `utils/tpChangeReadUtils.ts`, `utils/tpSpecVersionUtils.ts` | Writes metadata, deduplicates reads, and resolves TP Spec version context. |
| System metadata | `utils/systemVariableMetadataUtils.ts` | Resolves domain-scoped system variables. |
| Infrastructure | `utils/constants.ts`, `utils/dateUtils.ts`, `utils/logger.ts`, `utils/chunkUploadUtils.ts` | Constants, dates, logging, and large-payload chunking. |

### 5.5 Queue, worker, and solver callback

| File | Responsibility |
| --- | --- |
| `config/taskQueue/baseTaskQueue.ts` | Creates Bull queues, configures Redis, and connects logging/Bull Board. |
| `config/taskQueue/computationDispatchQueue.ts` | Defines `computationDispatchQueue` and its job payload. |
| `workers/computationDispatchWorker.ts` | Consumes waiting tasks in FIFO order, builds solve requests, calls the Solver Engine, and tracks terminal state. |
| `routes/external/computeCallbackRoutes.ts` | Receives callbacks, records result-processing timing, and invokes success/failure handling. |
| `shared/computationPhaseProgress.ts` | Shared computation phase and timing calculations used by both sides. |

`routes/external/callback_response.json` stores the most recent callback only when diagnostics are enabled. It is not the source of the callback contract. Also note that `authenticateGateway.ts` currently logs and calls `next()` without validating a shared secret; it must not be treated as a completed security boundary.

### 5.6 Prisma and databases

| File or directory | Responsibility |
| --- | --- |
| `backend/prisma/mongodb/schema.prisma` | Current MongoDB collections and relations for user-owned operational state. |
| `backend/prisma/postgres/schema.prisma` | Current PostgreSQL tables and relations for system catalogs and result data. |
| `backend/prisma/postgres/migrations/` | PostgreSQL migration history. Use the current schema as the final authority. |
| `generated/mongodb-client/`, `generated/postgres-client/` | Generated Prisma clients; regenerate through package scripts, never edit directly. |

For a fuller inventory, read [System and User Table Reference](./system-and-user-table-reference.md).

### 5.7 System Excel import

The System menu import controls are not wired. The actual system-data import path is:

| File | Responsibility |
| --- | --- |
| `src/run-all.sh` | Initializes/starts databases and invokes workbook migration. |
| `src/excel-migration/excel_to_csv.py` | Normalizes Excel sheets into migration input. |
| `src/excel-migration/migrate.py` | Writes normalized records to PostgreSQL. |
| `src/excel-migration/schema_contract.py` | Defines sheet/column contracts and validation. |
| `src/excel-migration/economic_contract.py` | Defines Economic sheet rules and disabled behavior. |
| `src/scripts/select-latest-versioned-workbook.cjs` | Selects the latest dated/versioned workbook. |

Read [Excel Import Pipeline](./excel-import-pipeline.md) before changing system-table import behavior.

## 6. Key end-to-end flows

### 6.1 Save

1. The user selects Save and Restore, which enters `useSaveDiagram()`.
2. `header-bar/utils/save-util.tsx` collects React Flow nodes/edges, Redux canvas/domain/calculation-type state, node cache, TP changes, and subnetwork information.
3. A new diagram uses `POST /api/data/diagrams`; an existing diagram uses `PUT /api/data/diagrams/:diagramId`.
4. `dataRoutes.ts` checks `req.user.id` and processes node IDs, node cache, subnetwork instances, and snapshot-related state.
5. Diagram and node/TP data are stored in MongoDB, then the frontend updates `savedSlice` and local save metadata.

See [Save Diagram and Node Cache](./save-diagram-and-node-cache.md).

### 6.2 Duplicate

1. `save-as-copy.tsx` validates the new name and creates a client `requestId`.
2. It calls `POST /api/data/diagrams/:diagramId/duplicate`.
3. `dataRoutes.ts` deduplicates retries by `userId + diagramId + requestId`.
4. The backend builds a full snapshot, forces the root diagram to unverified, and imports the cloned owned state with remapped IDs.
5. The response returns the new diagram ID; the frontend navigates to it and reloads.

### 6.3 Full export and import

1. `diagramTransfer.ts` requests `/diagrams/:id/export`.
2. `buildFullNetworkSnapshotFromDiagram()` in `dataRoutes.ts` collects the root diagram, embedded subnetworks, node cache, TP data, TP Specs, instruments, and other owned records.
3. `exportDownload.ts` downloads the JSON in the browser.
4. Import validates the artifact with `isCurrentFullNetworkSnapshot()` and posts it to `/diagrams/import`.
5. `schemaMigrations.ts` upgrades supported older snapshots. The import remaps database IDs and business references and compensates by deleting created records if the operation fails.

### 6.4 Verify and Unverify

1. `verify-button.tsx` derives the requested state from Redux `canvas.verified`.
2. It sends `{ isVerified: boolean }` to `PATCH /diagrams/:id/verification`.
3. `persistDiagramVerificationState()` checks diagram ownership and performs an idempotent MongoDB update.
4. The frontend stores the canonical state returned by the backend.
5. `App.tsx` and child components use the state to hide the palette or block editing. Multi-TP Economic and Global TP also apply verified guards.

See [Diagram Verification Lifecycle](./diagram-verification-lifecycle.md).

### 6.5 Run, solver callback, and results

1. `computation-button.tsx` collects solver, algorithm, run name, timeout, and Optimization/Data Reconciliation selections, then calls `/api/compute/start`.
2. `computeRoutes.ts` checks ownership and graph/equation/stream data; expands subnetworks; and loads node cache, TP values, costs, and the domain snapshot.
3. `translation.ts` and related utilities build `Diagram.parameters`; `solveInputTranslationService.ts` resolves selected inputs.
4. The backend creates a MongoDB `ComputationTask` and adds a Bull job.
5. `computationDispatchWorker.ts` reads required units from PostgreSQL, calls `buildSolveRequest()`, and sends the request to the Solver Engine.
6. The solver posts to `/api/external/compute/callback`.
7. `computationTaskHandler.ts` and `reverseTranslation.ts` write results back to diagram/node/TP state; `storeComputationResultUtils.ts` writes PostgreSQL result rows.
8. The frontend polls `/api/compute/details/:diagramId`; Run Result reads `/history/:diagramId` and related result endpoints.

Continue with [Run Config and Computation Start](./run-config-and-computation-start.md), [Compute, Solver Callback, and Results](./compute-solver-callback-and-results.md), and [Translation and Reverse Translation](./translation-and-reverse-translation.md).

## 7. What to change when extending a feature

### Add a GUI menu action

1. Add the entry in `components/header-bar/index.tsx` with correct visibility and disabled rules.
2. Create or reuse a component under `header-buttons/**` or `model-buttons/**`.
3. If it changes editable state, verify the saved-state middleware behavior in `store.ts`.
4. If persistence is required, add an endpoint to the appropriate route file and move domain logic into a service when useful.
5. Protect backend access with `authenticateToken` and ownership checks based on `req.user.id`.
6. Update schemas/migrations if needed, add frontend/backend tests, and update the User Guide and this map.

### Add a diagram field

Check at least:

- the relevant frontend type or interface;
- `frontend/src/features/canvas/canvasSlice.ts` or the owning slice;
- `header-bar/utils/save-util.tsx` serialization;
- diagram POST/PUT/GET handlers in `backend/routes/dataRoutes.ts`;
- `backend/models/fullNetworkSnapshot.ts` and full import/export clone/remap logic;
- `backend/routes/computeRoutes.ts` and `utils/translation.ts` if the solver needs the field;
- save, snapshot, route, and translation tests.

### Add a computation input

Check:

- the GUI editor and header-owned run state;
- request reduction/assembly in `computation-button.tsx`;
- `solveInputTranslationService.ts` for selection-based inputs;
- `translation.ts` for graph, domain, or TP inputs;
- the final request in `solverEngineApiService.ts`;
- callback and reverse translation if the solver returns a related value.

## 8. Tests and verification

The backend working directory is `HYPRONET-GUI/src/`:

```bash
npm test
npm run lint
npm run typecheck
```

The frontend working directory is `HYPRONET-GUI/src/src/frontend/`:

```bash
npm test
npm run lint
npm run build
```

Useful feature-focused test areas:

| Feature | Test location or search term |
| --- | --- |
| Authentication | `src/tests/backend`, search `login`, `token`, and `auth` |
| Save/node cache | `src/tests/backend`, search `saveDiagram` and `canvasModelVersion` |
| Duplicate | `src/tests/backend`, search `duplicate` and `fullNetworkSnapshot` |
| Import/export | `src/tests/backend` and `src/tests/frontend`, search `snapshot`, `diagramTransfer`, and `schemaMigration` |
| Verification | route/service tests plus frontend `verify` tests |
| Computation | `src/tests/backend`, search `compute`, `translation`, `callback`, and `result` |
| TP Specs | backend TP Spec tests and `src/tests/frontend/tpSpec*` |

Minimum manual checks:

| Scenario | Expected UI | Expected network/data change |
| --- | --- | --- |
| Successful Login | Opens Dashboard and displays the user | `/login` is followed by `/checktoken`; `AuthContext.userId` is set. |
| Create diagram | Opens `/canvas/:domainId` | MongoDB has no new diagram before Save; first Save returns a diagram ID. |
| Duplicate | Opens one new diagram | Exactly one copy is created and it is unverified. |
| Verify | Button changes to Unverify and editing is restricted | `/verification` returns `isVerified: true`. |
| Full Export then Import | JSON downloads and imports successfully | Owned node, TP, subnetwork, instrument, and related snapshot data are restored. |
| Run | Displays waiting/computing/progress state | MongoDB task is created, worker dispatches it, and callback results are written back. |
| Placeholder control | Does not imply completed behavior | System, Help, and the identified Analysis/Multi-TP items produce no API side effect. |

## 9. Known cautions and source gaps

- **There are multiple import/export paths with different artifacts.** Dashboard and Model > Import/Export > Full Data use the complete snapshot. Open Network export uses the normal diagram response. New Model also retains legacy import.
- **Solver/Algorithm Export has no backend route.** The frontend calls `/api/data/run-configs/export`, but the current Express source does not implement it.
- **Frontend Logout only clears the browser.** `/api/auth/logout` exists, but the current UI does not call it to revoke the MongoDB refresh token.
- **Gateway callback authentication does not currently validate a secret.** `authenticateGateway.ts` logs and continues; do not rely on it as an implemented security boundary.
- **Create Diagram does not immediately write to MongoDB.** The first Save creates the persistent diagram.
- **Duplicate always produces an unverified copy.** Never carry a source diagram's verified state into the duplicate.
- **Verification is not authorization.** It is a business/editing-lifecycle state. JWT validation plus `req.user.id` ownership checks enforce access.
- **MongoDB and PostgreSQL are not interchangeable.** User diagram state normally belongs to MongoDB; system catalogs and computation result rows normally belong to PostgreSQL.
- **`dataRoutes.ts` is very large.** Search by endpoint/helper/model and prefer a focused module for a new independent domain.
- **Do not edit generated or diagnostic artifacts.** `generated/`, `dist/`, `coverage/`, `solve_request.json`, and `callback_response.json` are not business-source files.
- **Do not infer current behavior from archives.** Verify anything in `docs-archive/` or `version6.1/` against the active `src/src/` code.
- **Computation-time disabling is a separate contract.** New buttons must account for `computingDisableConfig.ts` and backend rules for processing state.

## 10. Continue reading

- [Code Explanation Index](./code-explanation-index.md): index of all current technical guides.
- [Dashboard and Canvas](./dashboard-and-canvas.md): Dashboard, React Flow Canvas, and sidebar.
- [Header Bar](./header-bar.md): menu assembly, disabled/read-only guards, and modal orchestration.
- [Backend Data Routes and Persistence](./backend-data-routes-and-persistence.md): Express data APIs and MongoDB/PostgreSQL boundaries.
- [Subnetwork Blueprint and Instance Flow](./subnetwork-blueprint-and-instance-flow.md): blueprint and instance lifecycle.
- [Material Domain Editor Workflow](./material-domain-editor-workflow.md): User Tables and workbook import.
- [Time Period and Economic Flow](./time-period-and-economic-flow.md): Base TP, Multi-TP, and Economic behavior.
- [System and User Table Reference](./system-and-user-table-reference.md): database table and collection inventory.
- [CodeExplanation Writing Standards](./CODE_EXPLANATION_GUIDELINES.md): maintenance standards for this guide and future documentation.
