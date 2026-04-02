# nodeCacheSlice (Redux)

## Overview
- Location: `src/src/frontend/src/features/node/nodeCacheSlice.ts`
- Purpose: Client cache for node `modelVersion` objects, tracking dirty nodes and coordinating save/load to backend.

## State
- `modelVersions: Record<nodeId, ModelVersion>`
- `dirtyNodes: string[]`
- `loading: Record<nodeId, boolean>`
- `error: string | null`

## Async Thunks
- `fetchModelVersion(nodeId)` — GET `/api/data/nodes/{nodeId}`; stores returned `modelVersion`.
- `saveAllChanges(diagramId)` — saves all dirty nodes; PUT when nodeId looks canonical (24-hex), otherwise POST to create and possibly remap ids; returns `{ savedCount, replacements }`.
- `saveNode(nodeId)` — PUT single `modelVersion` for nodeId.

## Actions
- Cache set/update: `setModelVersion`, `updateModelVersion` (marks dirty), `updateNodeProperty(propertyPath,value)` (deep update + dirty).
- Dirty tracking: `markClean(nodeId)`.
- Housekeeping: `clearCache`, `clearError`, `preloadNodes(nodeIds)` (marks loading true for uncached ids).
- `renameNodeCacheEntry({ oldNodeId, newNodeId, modelVersion })` — remaps cache/dirties/loading entries when backend creates new ids.

## Notes
- `saveAllChanges` attempts PUT first for hex ids; on 404 or non-hex, POST creates a node and may trigger `renameNodeCacheEntry` to keep cache aligned.
- Selectors provided: `selectModelVersion`, `selectDirtyNodes`, `selectHasUnsavedChanges`, `selectIsLoading`, `selectCacheError`, `selectCacheInfo` (counts/estimatedMemory).

