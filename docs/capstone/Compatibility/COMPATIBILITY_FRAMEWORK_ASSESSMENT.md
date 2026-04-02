# Compatibility Framework Assessment

**Purpose:** Evaluate data structure complexity, historical changes, and whether a comprehensive compatibility framework is necessary or difficult.

---

## 1. Data Structure Complexity

### 1.1 Layers of Data (Overview)

| Layer | Location | Complexity | Notes |
|-------|----------|------------|-------|
| **Save Payload** | save-util.tsx | Medium | canvas, nodeCacheDiffs, nodeCacheFull, subnetworkInstances, schemaVersion |
| **FullNetworkSnapshot** | dataRoutes.ts | High | version, metadata, canvas, nodes, tpNodeVers, tpChanges, subnetworkBlueprints, subnetworkInstances |
| **Canvas JSON** | Diagram.canvas | High | nodes (data.model, portsMapping, diagramId), edges (data.stream) |
| **Node Table** | MongoDB Node | Medium | nodeId, modelVersion (deep JSON) |
| **ModelVersion** | interfaces.ts | High | ports_var → model_var_object (many fields) |
| **Translation** | translation.ts | Very High | canvas → solver parameters (800+ lines) |
| **Reverse Translation** | reverseTranslation.ts | Very High | output → canvas/parameters (600+ lines) |

### 1.2 Structural Hotspots

| Area | Complexity | Reason |
|------|------------|--------|
| **Node identity** | High | `nodeId` vs `documentId` (MongoDB Node.id vs ReactFlow node.id); used in translation, reverseTranslation, nodeCache |
| **portsMapping** | Medium | `internalNodeId` vs `nodeId` fallback; `instance_port_id` optional |
| **NodeCacheEntry** | Medium | Two shapes: `ModelVersion` directly or `{ nodeId, diagramId, documentId?, modelVersion }` |
| **Port var names** | Medium | Legacy `MFZ`/`_MFZ`/`_XZ` vs canonical `MF`/`_MF`/`_X` |
| **TpNodeVer / TpChange** | Medium | `fromTp`/`toTp` vs `from_tp`/`to_tp`; `nodeId` vs `node_id`; `diagramId` vs `diagram_id` |
| **Subnetwork** | High | Blueprint + instance; nested canvas; parentConnections |

---

## 2. Historical Schema Changes

### 2.1 Version History

| Version | Status | Migration |
|---------|--------|-----------|
| **1.0.0** | Legacy | Treated as baseline; no schemaVersion in canvas |
| **6.0.0** | Current | modelVersion moved out of canvas → Node table; FullNetworkSnapshot with metadata |

### 2.2 Key Change: 1.0.0 → 6.0.0

- **modelVersion location:** Was embedded in `node.data.model`; now in separate Node table (node cache)
- **Backward compatibility:** Code supports both:
  - `extractModelVersionFromCanvasNode` for embedded modelVersion (legacy)
  - Node cache / Node table for new format
- **Migration function:** `1.0.0->6.0.0` is **identity** (`return data`) — no structural transform
- **canvasMigrations:** Empty — no canvas-level migrations implemented yet

### 2.3 Implicit Compatibility (Defensive Fallbacks)

The codebase already handles many legacy shapes via fallbacks:

```ts
// reverseTranslation.ts - TpNodeVer field resolution
timePeriodId: r.timePeriodId || r.time_period_id || r.tpid || r.id
nodeId: r.nodeId || r.node_id
fromTp: r.fromTp ?? r.from_tp ?? r.fromTP
toTp: r.toTp ?? r.to_tp ?? r.toTP

// portsMapping - internalNodeId vs nodeId
internalNodeId ?? nodeId

// NodeCacheEntry - documentId optional
documentId in cacheEntry ? documentId : nodeId
```

---

## 3. Is a Comprehensive Compatibility Framework Necessary?

### 3.1 Current State (What You Have)

| Component | Status | Role |
|-----------|--------|------|
| **schemaMigrations.ts** | ✅ Exists | Version constant, VERSION_ORDER, migrations + canvasMigrations registries |
| **COMPAT_CHECK.md** | ✅ Exists | Human-in-the-loop prompt for PR review |
| **SCHEMA_SNAPSHOT.md** | ✅ Exists | Baseline structure reference |
| **performDiagramUpgrade** | ✅ Exists | Backup + upgrade flow in dataRoutes |
| **version-status API** | ✅ Exists | Dashboard shows diagrams needing upgrade |
| **Machine check** | ❌ Missing | No automated drift detection |
| **Real migrations** | ⚠️ Minimal | 1.0.0→6.0.0 is identity; canvasMigrations empty |

### 3.2 Assessment

| Question | Answer |
|----------|--------|
| **Necessary for factory test?** | **No.** Current setup is sufficient. You support 1.0.0 and 6.0.0; migration is trivial. |
| **Necessary for future?** | **Yes, incrementally.** When you add 6.1.0 with real structural changes, you will need canvas migrations. |
| **Overkill right now?** | A *full* framework (e.g. JSON Schema validation, multi-version migration chains) would be overkill. A *lightweight* script is enough. |

### 3.3 Recommendation

- **Keep:** schemaMigrations, COMPAT_CHECK prompt, SCHEMA_SNAPSHOT
- **Add:** `npm run compat-check` — a small script that compares key field names against a machine-readable baseline and exits 1 on drift
- **Defer:** Heavy migration framework until you have a concrete 6.1.0 change that requires non-identity migrations

---

## 4. Is It Difficult?

### 4.1 Difficulty by Task

| Task | Difficulty | Effort | Notes |
|------|------------|--------|-------|
| **Lightweight compat script** | Low | 0.5–1 day | Compare payload keys, Prisma fields, canvas node shape vs JSON baseline |
| **Add 6.1.0 canvas migration** | Medium | 1–2 days | Write migration fn; add to canvasMigrations; test with old fixtures |
| **Full migration chain (3+ versions)** | Medium–High | 2–5 days | Chain migrations; handle edge cases; regression tests |
| **JSON Schema validation** | Medium | 1–2 days | Define schemas; validate on load/save; good for strict contracts |
| **Automated snapshot sync** | Medium | 1 day | Script to regenerate SCHEMA_SNAPSHOT from live code |

### 4.2 Main Challenges

1. **Scattered structure definitions:** Interfaces live in interfaces.ts, dataRoutes models, Prisma schema, save-util, domain.ts — no single source of truth.
2. **Deep nesting:** ModelVersion.ports_var[].model_var_object[] — migrations must traverse carefully.
3. **Dual identity (nodeId/documentId):** Any migration touching node references must handle both.
4. **Subnetwork nesting:** subnetworkInstances[].canvas must be migrated recursively.

### 4.3 Summary

| Aspect | Verdict |
|--------|---------|
| **Current framework adequate?** | Yes for factory test |
| **Comprehensive framework necessary?** | Not yet; add when you have real breaking changes |
| **Difficulty of lightweight script?** | Low |
| **Difficulty of full framework?** | Medium — manageable if done incrementally |

---

## 5. Action Items (Prioritized)

| Priority | Action | When |
|----------|--------|------|
| 1 | Keep using COMPAT_CHECK prompt before schema-touching PRs | Now |
| 2 | Add `npm run compat-check` script (optional, 0.5 day) | Before factory handoff if time permits |
| 3 | When adding 6.1.0 with structural changes: implement canvas migration, bump version, update SCHEMA_SNAPSHOT | When needed |
| 4 | Consider JSON Schema for FullNetworkSnapshot if you want strict validation | Later |

---

*Assessment based on codebase review of schemaMigrations, translation, reverseTranslation, dataRoutes, save-util, and SCHEMA_SNAPSHOT.*
