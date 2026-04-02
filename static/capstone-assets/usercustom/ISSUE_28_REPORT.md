# Issue 28: Duplicate & Import & Export — Implementation Report

> **Problem**: In the old design, `canvas` held full network data. In the new design, `canvas` stores layout only; node details live in the `nodes` collection. Duplicate/Import/Export broke and did not support TP (Time Period) or Subnetwork structures.

---

## One-Line Summary

**Package the entire network into a single JSON snapshot**: layout + node configs + time periods + subnetworks. Export, Import, and Duplicate all operate on this snapshot.

```
┌─────────────────────────────────────────────────────────┐
│              Full Network Snapshot (single JSON)          │
├─────────────────────────────────────────────────────────┤
│  metadata     │ name, description, type, calcType...      │
│  canvas       │ Layout: nodes + edges (from diagrams)     │
│  nodes        │ Node details: modelVersion (from nodes)   │
│  tpNodeVers   │ Time period versions                      │
│  tpChanges    │ Time period changes                       │
│  subnetwork*  │ Blueprints + instances (nested canvas/TP)  │
│  snapshot     │ Domain snapshot (optional)                │
└─────────────────────────────────────────────────────────┘
```

---

## How the Three Features Work

| Feature | One-liner | What the code does |
|---------|-----------|--------------------|
| **Export** | "Take a snapshot" | Query diagram + nodes + tpNodeVers + tpChanges + subnetwork data, assemble into `FullNetworkSnapshot` JSON |
| **Import** | "Develop the snapshot" | Parse JSON → create diagram, nodes, TP records, subnetworks → remap nodeIds and edge source/target |
| **Duplicate** | "Snapshot then develop" | `Export(diagramId)` → `Import(snapshot)`, return new diagramId |

---

## Code Entry Points

| Feature | Backend route | Frontend |
|---------|---------------|----------|
| Export | `GET /api/data/diagrams/:id/export` | Dashboard export, Export button |
| Import | `POST /api/data/diagrams/import` | Dashboard import, Import button |
| Duplicate | `POST /api/data/diagrams/:id/duplicate` | Save-as-copy button |

---

## Key Implementation Details

1. **ID remapping**: Import generates new nodeIds; canvas edges' source/target are updated to the new IDs.
2. **Subnetwork recursion**: Subnetwork instances include their own `canvas`, `nodes`, `tpNodeVers`, `tpChanges`; import recreates them recursively.
3. **Blueprint references**: Subnetwork nodes reference blueprintDiagramId; import builds blueprintDiagramId → new ID mapping.
4. **Version compatibility**: Snapshot carries a `version` field; import uses `schemaMigrations.migrateToLatest()` for migration.

---

## Acceptance Checklist

| Criterion | Status |
|-----------|--------|
| Duplicate creates a new network that is fully editable and computable | ✅ |
| Export produces a single JSON importable into a clean database | ✅ |
| Import restores node configs, TP behavior, and subnetwork structures correctly | ✅ |
