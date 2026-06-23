# domainSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/domain/domainSlice.ts`
- Purpose: Holds domain-level data (models, streams, run configs, blueprints) fetched from backend.

## State
- `data: DomainData | null`
- `status: 'idle' | 'loading' | 'succeeded' | 'failed'`
- `error: string | null`

## Async Thunks
- `fetchDomainData(domainId)` 鈫?GET `/api/data/domain/{id}`; populates `data`, sets status flags.

## Helpers
- `convertBlueprintToDomainModel(blueprint)` 鈥?turns a `SubnetworkBlueprint` into a `DomainModel` with ports derived from `portsMapping`.
- `mergeBlueprintModels(domainData, blueprints)` 鈥?merges new blueprint-derived models into existing domain models (dedup by id).

## Reducers
- `setDomainData(domainData)` 鈥?replace entire domain data payload.
- `clearDomainData()` 鈥?reset to empty/idle.
- `clearStreams()` 鈥?empties `data.streams` if present.
- `updateOrAddStream({ stream })` 鈥?upsert by `stream_database_id`.
- `updateRunConfig({ type, updatedGroup })` 鈥?replace a runConfig group by key.
- `addBlueprints(blueprints)` 鈥?append blueprint models to `data.models`.

## Notes
- Run configs are stored as `runConfigs[type] = RunConfigGroup`; caller must supply correct `type` key.
- Streams use `stream_database_id` as the unique key for updates.
