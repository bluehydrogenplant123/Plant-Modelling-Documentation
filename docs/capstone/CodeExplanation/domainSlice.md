# domainSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/domain/domainSlice.ts`
- Purpose: Holds domain-level data (models, streams, run configs, blueprints) fetched from backend.

## State
- `data: DomainData | null`
- `status: 'idle' | 'loading' | 'succeeded' | 'failed'`
- `error: string | null`

## Async Thunks
- `fetchDomainData(domainId)` → GET `/api/data/domain/{id}`; populates `data`, sets status flags.

## Helpers
- `convertBlueprintToDomainModel(blueprint)` — turns a `SubnetworkBlueprint` into a `DomainModel` with ports derived from `portsMapping`.
- `mergeBlueprintModels(domainData, blueprints)` — merges new blueprint-derived models into existing domain models (dedup by id).

## Reducers
- `setDomainData(domainData)` — replace entire domain data payload.
- `clearDomainData()` — reset to empty/idle.
- `clearStreams()` — empties `data.streams` if present.
- `updateOrAddStream({ stream })` — upsert by `stream_database_id`.
- `updateRunConfig({ type, updatedGroup })` — replace a runConfig group by key.
- `addBlueprints(blueprints)` — append blueprint models to `data.models`.

## Notes
- Run configs are stored as `runConfigs[type] = RunConfigGroup`; caller must supply correct `type` key.
- Streams use `stream_database_id` as the unique key for updates.

