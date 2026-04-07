# Issue 82: Gap Analysis & Test Strategy

## 1. Potential Gaps (遗漏) Identified

### 1.1 Old Versions in Database — Do They Exist?

| Question | Answer |
|----------|--------|
| **Are old-version diagrams stored in DB?** | Yes. Diagrams without `schemaVersion` in canvas are treated as legacy `1.0.0`. They remain in DB until loaded or bulk-upgraded. |
| **Where are they?** | `Diagram` table; `canvas` JSON may lack `schemaVersion` or have `schemaVersion: '1.0.0'`. |
| **How to verify?** | Query: `db.diagram.find({ "canvas.schemaVersion": { $exists: false } })` or `{ "canvas.schemaVersion": "1.0.0" }`. |

**Status:** ✅ Old versions can exist. The upgrade flow handles them on load.

---

### 1.2 Backup — Should It Create Independent Instances? (Gap)

| Question | Answer |
|----------|--------|
| **Design intent** | Backup **should** create independent instance diagrams (like Duplicate does). Backup and original **should not** share instances. |
| **Current implementation** | `performDiagramUpgrade` only copies the parent diagram. It does **not** deep-copy instance diagrams. The backup's canvas references the **same** `instanceDiagramId` values → backup and original **share** instances. |
| **Is this correct?** | **No.** This is a **gap**. For true rollback isolation, backup must create new instance diagrams and remap wrapper refs (same pattern as Duplicate/Import). |

**Code reference** (`dataRoutes.ts` ~99–109) — current behavior:

```ts
const backupDiagram = await mongoClient.diagram.create({
  data: {
    canvas: diagram.canvas,  // Same canvas, same instanceDiagramId refs — shares instances
    ...
  },
});
// Only copies: Node, TpNodeVers, TpChanges where diagramId = parent
// Instance diagrams are NOT copied — GAP
```

**Recommendation:** Extend `performDiagramUpgrade` to:
1. Extract `instanceDiagramIds` from canvas (reuse `extractInstanceDiagramIdsFromCanvasPayload`)
2. For each instance diagram: create a copy (like import does), remap IDs
3. Update backup canvas so wrapper nodes point to the new instance diagram IDs

---

### 1.3 New Version — Does It Create Independent Instances?

| Context | Creates Independent Instances? |
|---------|-------------------------------|
| **Upgrade (performDiagramUpgrade)** | **No** — gap. Should create independent instances. |
| **Duplicate** (`POST /diagrams/:id/duplicate`) | **Yes.** Export → migrateToLatest → import creates new parent + new instance diagrams with remapped IDs. |
| **Import** (`POST /diagrams/import`) | **Yes.** Creates new diagrams from snapshot; instances are recreated from `subnetworkInstances`. |

**Conclusion:** Duplicate and Import create independent instances. **Upgrade/backup currently does not** — this is a gap that should be fixed.

---

### 1.4 Instance Diagram Upgrade

| Question | Answer |
|----------|--------|
| **When are instance diagrams upgraded?** | When loaded individually (e.g. user opens instance). `performDiagramUpgrade` is called per diagram. |
| **If parent is upgraded, are instances upgraded?** | No. Parent upgrade only touches the parent. Instance diagrams are upgraded on their own load. |
| **Bulk-upgrade** | `POST /bulk-upgrade` loops over diagrams from `version-status`. It only includes diagrams that need upgrade. Instance diagrams are separate Diagram records, so they would be in the list if they need upgrade. |

---

## 2. Issue 82 Test Strategy

### 2.1 What Issue 82 Implements

- schemaVersion in save/export
- Load: backup → migrate → return
- Import: migrateToLatest before insert
- Bulk-upgrade from dashboard
- Version-status API

### 2.2 Issue 83 (from `git log --grep="83"`)

| Commit | Description |
|--------|--------------|
| `4b9f2a2` | **Dev/replace aspen id#54 (#83)** — Migration: `aspen_id` → `stream_database_id` in domain API, stream selection, material editor, translation |
| `a8eab83` | Docs/Added the system tests for most of the NFRs (#83) |

**Issue 83 scope:** Rename `aspen_id` to `stream_database_id` in PostgreSQL Streams table, translation, edgesProcessor, domain slice, material editor. Affects edge/stream data in canvas and parameters.

### 2.3 Can Issue 82 Be Tested Using Issue 83's Fix?

**Yes.** Issue 83's change (aspen_id → stream_database_id) creates a concrete migration scenario:

| Test approach | How |
|---------------|-----|
| **Old data with aspen_id** | If canvas/edge `stream` objects or parameters contain `aspen_id`, add a migration step in `canvasMigrations` or `migrations` to rename → `stream_database_id`. Then test: load/import old diagram → verify `stream_database_id` present. |
| **Schema migration chain** | Issue 83 defines a real field rename. Use it to validate that `migrateToLatest` / `migrateCanvasIfNeeded` correctly transform persisted data. |
| **Duplicate/Import** | Duplicate uses export → migrateToLatest → import. If export includes stream data with old field names, migration can normalize them. |

### 2.4 Can Issue 82 Be Tested Using Duplicate-Import Flow?

| Test Path | Exercises Issue 82? | Notes |
|-----------|--------------------|-------|
| **Duplicate** (export → migrateToLatest → import) | Partially | `migrateToLatest` is called during import. But export typically returns 6.0.0 already, so migration may be no-op. |
| **Import of old JSON** (1.0.0 snapshot) | ✅ Yes | Best way to test `migrateToLatest`. Use a fixture or manually create 1.0.0 export. |
| **Load old diagram from DB** | ✅ Yes | Have legacy diagram in DB → open it → triggers backup + migrate. |
| **Bulk-upgrade** | ✅ Yes | Dashboard "Upgrade All" → exercises backup + migrate for each. |

### 2.5 Recommended Test Matrix for Issue 82

| # | Scenario | How to Test | Validates |
|---|----------|-------------|-----------|
| 1 | Old diagram in DB (no schemaVersion) | Create diagram with old format, save to DB, then load | Backup created, migrate runs, toast shown |
| 2 | Import 1.0.0 JSON | Use fixture or strip schemaVersion from export, import | migrateToLatest, "File was version X" message |
| 3 | Bulk-upgrade | Have multiple old diagrams, click "Upgrade All" | All upgraded, backups exist |
| 4 | Duplicate with subnetwork | Duplicate diagram with instances | migrateToLatest in import path; new independent instances |
| 5 | Export round-trip | Export 6.0.0 → import | schemaVersion preserved, no regression |

### 2.6 Using Duplicate/Import (Issue 28 Flow) to Test Issue 82

**Yes, with caveats:**

1. **Duplicate path:** Export → `migrateToLatest` → Import. So the migration path is exercised. If the exported snapshot is already 6.0.0, `migrateToLatest` returns early (no-op). To test migration, you need a 1.0.0 snapshot in the import payload.

2. **How to test migration via import:**
   - Export a diagram to JSON.
   - Edit the JSON: set `version: "1.0.0"` (or remove it), remove `schemaVersion` from canvas if present.
   - Import the modified JSON.
   - Expected: Import succeeds, response includes `migratedFrom: "1.0.0"`, diagram works.

3. **Duplicate with subnetwork** validates:
   - Export includes subnetworkInstances.
   - Import creates new instance diagrams (independent copies).
   - `migrateToLatest` recurses into `subnetworkInstances[].canvas` (see schemaMigrations.ts:87–92).

---

## 3. Summary of Gaps & Recommendations

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| Backup shares instance diagrams | **Medium** | **Fix:** Extend `performDiagramUpgrade` to deep-copy instance diagrams and remap wrapper refs (same pattern as Duplicate). Backup and original should NOT share instances. |
| No explicit "old version in DB" test | Low | Add a test that seeds a 1.0.0 diagram and verifies load/upgrade. |
| Import 1.0.0 fixture | Low | Add a 1.0.0 export fixture for import tests. |

---

## 4. Quick Test Checklist for Issue 82

- [ ] Create diagram, manually set canvas without schemaVersion in DB, load → backup created, upgrade toast
- [ ] Import JSON with `version: "1.0.0"` → success, `migratedFrom` in response
- [ ] Bulk-upgrade multiple old diagrams → all upgraded
- [ ] Duplicate diagram with subnetwork instances → new independent instances, no shared refs
- [ ] Export 6.0.0 → import → schemaVersion preserved
