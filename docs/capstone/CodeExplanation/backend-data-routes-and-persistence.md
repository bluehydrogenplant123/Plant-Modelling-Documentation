---
title: Backend Data Routes and Persistence Code Explanation
sidebar_position: 25
description: Explains how the Express data API is wired, authenticated, and persisted across MongoDB and PostgreSQL.
---

## Overview

The backend data API is mounted by `src/src/backend/app.ts` at `/api`, then by `src/src/backend/routes/index.ts` at `/api/data`. `src/src/backend/routes/dataRoutes.ts` is the main route file for domain catalog reads, user diagram persistence, node cache persistence, TP overrides, subnetwork blueprints, and full-network import/export.

All routes listed here use `authenticateToken`. The middleware accepts `Authorization: Bearer <token>` or a raw token, verifies it with `JWT_SECRET`, loads the MongoDB `User`, and attaches it to `req.user`. Token failures return 401, missing users return 404, and unexpected middleware errors continue to the global Express 500 handler.

## Purpose and Responsibility

`dataRoutes.ts` owns the backend contract for current domain/reference data and persisted user canvas data. It does not own authentication token creation, compute execution, external solver callbacks, or source-of-truth domain imports; those are handled by other route groups, services, or import tooling.

## Source Files

- `src/src/backend/app.ts`: Express app setup, CORS allow-list, JSON body limit, `/api` route mount, Bull Board mount, Swagger setup, global 500 handler, and refresh-token cleanup cron.
- `src/src/backend/routes/index.ts`: mounts `/data`, `/auth`, `/compute`, and `/external/compute` under `/api`.
- `src/src/backend/routes/dataRoutes.ts`: owns the data endpoints and most persistence helpers.
- `src/src/backend/middleware/auth.ts`: JWT authentication and `req.user` population.
- `src/src/backend/prisma/mongodb/schema.prisma`: MongoDB user-owned persistence models.
- `src/src/backend/prisma/postgres/schema.prisma`: PostgreSQL reference/catalog models.
- `src/src/backend/utils/canvasModelVersionUtils.ts`: model-version lookup and canvas attach/detach helpers.
- `src/src/backend/utils/schemaMigrations.ts`: current schema version, version checks, and snapshot/canvas migration hooks.

## Endpoint Map

All paths below include the `/api/data` prefix.

| Area | Endpoint | Main behavior | DB boundary |
| --- | --- | --- | --- |
| Domain catalog | `GET /domains` | Returns non-`Generic` domains only. | Reads Postgres `Domain`. |
| Domain catalog | `GET /` | Returns all non-`Generic` domains with models, model versions, ports, streams, `colors`, and `units`, after merging `Generic` domain data. | Reads Postgres `Domain`, mappings, `Models`, `ModelVersion`, `Ports`, `VarNames`, `Streams`, `SystemVariables`, `Colors`, `UnitConversion`. |
| Domain catalog | `GET /domain/:domainId` | Returns one transformed domain plus `colors`, `units`, grouped `runConfigs`, and `costsConfig`. | Reads Postgres domain/catalog/config tables. |
| Domain catalog | `GET /tasktype` | Returns computation task types. | Reads Postgres `CompTaskTypes`. |
| Diagrams | `GET /diagrams` | Lists the authenticated user's diagrams, optional `?name=`, with schema metadata and backup flag. | Reads Mongo `Diagram`. |
| Diagrams | `GET /diagrams/version-status` | Returns schema upgrade status with `needsUpgradeCount: 0`; upgrade advertising is disabled. | No DB write. |
| Diagrams | `POST /diagrams/bulk-upgrade` | Returns all requested IDs as skipped with `schema_upgrade_disabled`. | No DB write. |
| Diagrams | `POST /diagrams` | Creates a diagram, optional domain snapshot, default costs, node rows, subnetwork instances, translated `parameters`, and ID remaps. | Writes Mongo `Diagram`, `DomainSnapshot`, `Node`, and sometimes child `Diagram` rows. Reads Postgres cost config. |
| Diagrams | `GET /diagrams/:diagramId` | Loads one authorized diagram with snapshot, strips `parameters` from the response, adds duration/calc/schema metadata. | Reads Mongo `Diagram` and `DomainSnapshot`. |
| Diagrams | `PUT /diagrams/:diagramId` | Updates diagram metadata/canvas/duration/type/parent connections, rebuilds node cache from diffs/full payload, refreshes translated `parameters`, updates snapshot data, and propagates some network-wide calc-type/port changes. | Reads/writes Mongo `Diagram`, `DomainSnapshot`, `Node`, `TpNodeVers`, `TpChanges`; may update related network diagrams. |
| Diagrams | `DELETE /diagrams/:diagramId` | Deletes a diagram through `deleteDiagramWithCleanup(...)`. | Deletes Mongo `ComputationTask`, `TpChanges`, `TpNodeVers`, `Node`, `SubnetworkBlueprint`, `Diagram`, and optional `DomainSnapshot`. |
| Diagrams | `PATCH /diagrams/:diagramId/verify` | Marks a diagram verified unless already verified. | Updates Mongo `Diagram.isVerified`. |
| Diagram settings | `PUT /diagrams/:diagramId/base-duration` | Validates duration/unit and updates the selected network graph's base duration. | Updates Mongo `Diagram.duration` and `durationUnit` for collected network diagrams. |
| Economic data | `PUT /diagrams/:diagramId/costs` | Sanitizes and stores Economic entities/mappings. | Updates Mongo `Diagram.costEntities` and `costMappings`. |
| Economic data | `POST /diagrams/:diagramId/costs/initialize-mtp` | Builds MTP Economic rows from base costs, or returns `initialized: false` with `reason: "base_missing"`. | Reads/writes Mongo diagram cost JSON; reads Postgres cost config only when seeding base rows. |
| Subnetwork instances | `POST /diagrams/:diagramId/subnetwork-instance` | Ensures one wrapper node has an instance diagram and writes the processed parent canvas. | Reads/writes Mongo `Diagram`; helper may create instance diagrams/nodes/snapshots. |
| Nodes | `GET /nodes/:nodeId` | Reads a node; optional `?diagramId=` avoids ambiguity. Multiple authorized matches return 409. | Reads Mongo `Node` and `Diagram`. |
| Nodes | `GET /nodes/diagram/:diagramId` | Reads all nodes for one authorized diagram. | Reads Mongo `Diagram` and `Node`. |
| Nodes | `POST /nodes` | Creates a node, then normalizes `nodeId` to the Mongo row `id`. | Writes Mongo `Node`; reads Mongo `Diagram` for ownership. |
| Nodes | `PUT /nodes/:nodeId` | Updates a node's `nodeId` and/or `modelVersion`; optional body `diagramId` avoids ambiguity. | Reads/writes Mongo `Node`; reads Mongo `Diagram`. |
| Nodes | `DELETE /nodes/:nodeId` | Deletes one authorized node; optional `?diagramId=` avoids ambiguity. | Deletes Mongo `Node`; reads Mongo `Diagram`. |
| Nodes | `DELETE /nodes/diagram/:diagramId` | Deletes all nodes for one authorized diagram. | Deletes Mongo `Node`; reads Mongo `Diagram`. |
| TP node versions | `POST /tpnodevers` | Creates rows for node model versions across time periods, with duration/unit validation. | Writes Mongo `TpNodeVers`. |
| TP node versions | `GET /tpnodevers` | Reads rows by required `diagramId` and optional `nodeId`; empty result returns 404. | Reads Mongo `TpNodeVers`. |
| TP node versions | `PUT /tpnodevers` | Updates one row by row id passed as `timePeriodId`. | Reads/writes Mongo `TpNodeVers`. |
| TP node versions | `DELETE /tpnodevers` | Deletes rows by `timePeriodIds`, which are row Mongo ids. | Deletes Mongo `TpNodeVers`. |
| TP changes | `POST /tpchanges` | Upserts a manual port override; resolves `BASE_TP` or TP ranges, falls back to existing override or node model default if creating without `portVarValue`, then mirrors wrapper overrides when possible. | Reads/writes Mongo `TpChanges`, reads Mongo `TpNodeVers` and `Node`, and may write mirrored `TpChanges`. |
| TP changes | `PUT /tpchanges` | Updates manual overrides matching diagram/node/time/port, preferring exact `portLocation` then `null`, and mirrors wrapper overrides when possible. | Reads/writes Mongo `TpChanges`. |
| TP changes | `DELETE /tpchanges` | Deletes matching overrides after resolving canonical time-period context, and mirrors wrapper delete when possible. | Deletes Mongo `TpChanges`; may read Mongo `TpNodeVers`. |
| TP changes | `GET /tpchanges` | Reads and dedupes overrides by required `diagramId` plus optional `nodeId`, `timePeriodId`, and `portLocation`; empty result returns 404. | Reads Mongo `TpChanges`. |
| TP changes | `GET /tpchanges/all` | Reads and dedupes all overrides for a required diagram/node pair. | Reads Mongo `TpChanges`. |
| TP spec versions | `GET /diagrams/:diagramId/tp-spec-versions` | Lists TP spec versions for the resolved scope and requested calculation type, creating V1 when missing. | Reads/writes Mongo `TpSpecVersionSet` and `TpSpecVersionTable`; may stamp legacy `TpChanges`. |
| TP spec versions | `POST /diagrams/:diagramId/tp-spec-versions` | Creates a new version for the current scope and calculation type only, copying sparse changes from the selected source version. | Writes Mongo `TpSpecVersionSet`, `TpSpecVersionTable`, `TpSpecBaseChange`, or version-scoped `TpChanges`. |
| TP spec versions | `PATCH /tp-spec-versions/:versionSetId` | Renames a version display name. | Updates Mongo `TpSpecVersionSet`. |
| TP spec versions | `POST /tp-spec-versions/:versionSetId/apply` | Makes one version active for its scope and calculation type. Other calculation types are not changed. | Updates Mongo `TpSpecVersionSet.isActive`. |
| TP spec versions | `DELETE /tp-spec-versions/:versionSetId` | Deletes a non-default version and falls back to V1 when the deleted version was active. | Deletes Mongo `TpSpecVersionSet`, `TpSpecVersionTable`, `TpSpecBaseChange`, and version-scoped `TpChanges`. |
| TP spec tables | `GET /diagrams/:diagramId/tp-spec-table` | Materializes one version table by overlaying sparse changes on model defaults and TP rows. | Reads Mongo `Diagram`, `Node`, `TpNodeVers`, `TpSpecBaseChange`, and `TpChanges`. |
| TP spec tables | `PUT /tp-spec-tables/:versionTableId/changes` | Saves sparse row changes for the selected Base TP or Multi-TP version table. | Writes Mongo `TpSpecBaseChange` for Base TP, or version-scoped `TpChanges` for Multi-TP. |
| Snapshot | `GET /diagrams/:diagramId/export` | Builds a full-network snapshot from the authorized diagram. | Reads Mongo `Diagram`, `DomainSnapshot`, `Node`, `TpNodeVers`, `TpChanges`, `SubnetworkBlueprint`. |
| Snapshot | `POST /diagrams/import` | Validates and migrates snapshot version, then recreates the network. | Writes Mongo `DomainSnapshot`, `Diagram`, `Node`, `TpNodeVers`, `TpChanges`, `SubnetworkBlueprint`. |
| Snapshot | `POST /diagrams/:diagramId/duplicate` | Exports the source network and imports it under a copy name. | Reads and writes the same Mongo data as export/import. |
| Subnetwork blueprints | `POST /subnetworks` | Creates or updates a blueprint for a diagram, normalizes `portsMapping`, prevents instance diagrams from becoming blueprints, and marks the diagram `type: 1`. | Reads/writes Mongo `SubnetworkBlueprint` and `Diagram`. |
| Subnetwork blueprints | `GET /subnetworks` | Lists user blueprints, normalizes legacy `portsMapping`, and adds schema metadata. | Reads/writes Mongo `SubnetworkBlueprint`; reads Mongo `Diagram`. |
| Subnetwork blueprints | `GET /subnetworks/:id` | Reads one authorized blueprint, normalizes legacy `portsMapping`, and adds schema metadata. | Reads/writes Mongo `SubnetworkBlueprint`; reads Mongo `Diagram`. |
| Subnetwork blueprints | `PUT /subnetworks/:id` | Updates one authorized blueprint and keeps the referenced diagram marked as `type: 1`. | Reads/writes Mongo `SubnetworkBlueprint` and `Diagram`. |
| Subnetwork blueprints | `DELETE /subnetworks/:id` | Deletes a blueprint and resets its blueprint diagram from `type: 1` to `type: 0` if still applicable. | Deletes Mongo `SubnetworkBlueprint`; updates Mongo `Diagram`. |

## Data Ownership and DB Boundary

Postgres is treated as the read-side catalog for imported domain knowledge: domains, model mappings, stream mappings, model/version/port/var metadata, system variable bounds/types, unit conversions, colors, task types, run config rows, and cost entity defaults. `dataRoutes.ts` reads this data through `postgresClient` and transforms it for the frontend; it does not write Postgres data.

MongoDB is the user-state store. `Diagram` owns canvas JSON, translated `parameters`, optional Economic cost JSON, snapshot relation, verification state, type, parent connections, and base duration. `Node` owns persisted node `modelVersion` cache by diagram. `TpNodeVers` owns MTP model-version rows. `TpChanges` owns Multi-TP manual/computed per-port overrides and, for TP spec versions, stores version-scoped Multi-TP sparse changes. `TpSpecVersionSet` and `TpSpecVersionTable` own TP spec version metadata. `TpSpecBaseChange` owns sparse Base TP spec patches. `DomainSnapshot` freezes the domain payload used when a diagram was saved. `SubnetworkBlueprint` owns reusable blueprint metadata and `portsMapping`.

PostgreSQL also stores computation result metadata for applied TP spec versions. `ComputationResults` includes `calc_type`, `tp_spec_scope`, `tp_spec_version`, and `tp_spec_table` so a stored run can be traced back to the applied version table.

## Data Flow

1. `app.ts` accepts JSON requests, applies CORS, and sends `/api/*` traffic to `routes/index.ts`.
2. `routes/index.ts` sends `/api/data/*` traffic into `dataRoutes.ts`.
3. `authenticateToken` validates the request and loads the Mongo `User`.
4. Catalog endpoints read Postgres, normalize rows into frontend domain/config payloads, and return JSON without writing Postgres.
5. Persistence endpoints validate ownership, read/write Mongo user-state rows, run helper transforms such as node-cache rebuild or `translation(...)`, then return the updated diagram/node/TP/subnetwork payload.

## Main Helpers

- `transformData(...)`, `transformModel(...)`, `transformModelVersion(...)`, `buildFullStreams(...)`, `mergeGenericDomain(...)`, and `getAllUnits(...)`: build frontend domain payloads from Postgres rows and normalize stream/property/unit data.
- `buildRunConfigs(...)`, `parseDefaultValue(...)`, `parseOptions(...)`, and `buildCostsConfig(...)`: transform Postgres config tables into frontend run and Economic config shapes.
- `buildNodeCacheRecordFromDiffs(...)`, `ensureNodeCacheCoverage(...)`, `remapCanvasWithNodeCache(...)`, `upsertDiagramNodesFromCacheAndCanvas(...)`, and `pruneDiagramNodes(...)`: keep canvas node IDs, Mongo `Node` rows, and cached `modelVersion` payloads consistent during save.
- `getCachedModelVersion(...)`: reads a model version from a node cache map and falls back from document id to stored `nodeId` when callers pass the wrong identifier.
- `translation(...)` and `buildSubnetworkPortMap(...)`: turn saved canvas, domain models, node cache, TP rows, TP changes, and subnetwork mappings into persisted diagram `parameters`.
- `getActiveTpSpecContext(...)`, `listTpSpecVersionSets(...)`, and `getTpSpecContextByVersionSet(...)`: resolve TP spec versions by diagram, scope, and calculation type; create V1 defaults; and return the active version table used by the network and solve request.
- `processSubnetworkInstances(...)`, `duplicateBlueprintNodes(...)`, `applySubnetworkStreamsToInternalNodes(...)`, `propagateSubnetworkPortValuesFromNodeCache(...)`, and `propagateInstancePortValuesToParent(...)`: create/reuse subnetwork instance diagrams and keep parent/child port values aligned.
- `buildFullNetworkSnapshotFromDiagram(...)` and `importFullNetworkSnapshotInternal(...)`: export/import complete networks, including recursive subnetwork data.
- `normalizeBlueprintPortsMapping(...)`, `migrateToLatest(...)`, `migrateCanvasIfNeeded(...)`, and `getCanvasVersion(...)`: keep blueprint mappings and snapshot/canvas schema metadata compatible.

## Error and Fallback Behavior

- Authentication failures are returned before route handlers run: missing token 401, invalid/expired token 401 with a code, missing user 404.
- Most route validation errors return 400, missing records return 404, ownership failures return 403, duplicate subnetwork names return 409, and uncaught route errors flow to the global app handler as `{ message: "Internal Server Error" }`.
- CORS accepts requests with no `Origin`, or origins listed in `ALLOWED_ORIGINS`; other origins are rejected before route handling.
- Debug ingest calls to `http://127.0.0.1:7242/ingest/...` are suppressed by a local fetch wrapper unless `DEBUG_INGEST=true`; they are diagnostics, not persistence.
- Schema upgrade endpoints currently report no pending upgrades and skip bulk upgrades. Import still rejects unknown snapshot versions and calls `migrateToLatest(...)` for known older versions.
- TP change creation can recover a missing `portVarValue` from an existing manual override or the node model default; if no value can be resolved, creation returns 400.
- TP spec version reads create V1 defaults automatically. V1 cannot be deleted. Saving a non-active version persists sparse changes but does not change the active network state until the version is applied.
- Subnetwork blueprint reads normalize legacy `portsMapping` and write the normalized JSON back when migration is detected.

## Known Cautions

- `dataRoutes.ts` is a monolith: catalog reads, save translation, node cache sync, TP override mirroring, subnetwork recursion, import/export, and debug logging live in one file. Keep route changes narrow and verify the helper chain that the route calls.
- `authenticateToken` is applied everywhere, but ownership checks are not uniform. Diagram and node routes generally check `Diagram.userId`; several TP routes validate object ids but do not re-check that the requested `diagramId` belongs to `req.user`.
- `DELETE /diagrams/:diagramId` sends a 403 for unauthorized diagrams but does not return before calling cleanup in the current source. Treat that as a source caution before changing or relying on delete behavior.
- Node routes can be ambiguous because `nodeId` is not globally unique across diagrams. Pass `diagramId` when reading, updating, or deleting a node.
- Save endpoints are performance-sensitive. `nodeCacheDiffs`/`nodeCacheFull`, `ensureNodeCacheCoverage`, and selective node upserts are used to avoid rewriting every node model version on every save.
- TP spec versions are scoped by both TP mode and calculation type. A query or update that omits `calcType` can accidentally read or mutate the wrong version family.
- Base TP spec version data and Multi-TP spec version data use different sparse stores. Do not move Base TP patches into `TpChanges`, and do not store Multi-TP version rows in `TpSpecBaseChange`.
- Do not document behavior from `src/src/backend/services/solve_request.json`; it is a generated runtime artifact and is outside this persistence API source of truth.

## Testing and Verification

For documentation-only edits to this page, run from `C:\Users\19612\Desktop\Project\HYPRONET-GUI`:

```powershell
git diff --check -- docs/CodeExplanation/backend-data-routes-and-persistence.md
```
