# Issue 82: Schema Versioning for Diagram Save/Load — Implementation Report

> **Problem**: No `schemaVersion` in save/export; old diagrams and exported JSON can break when the data format changes. Need backward compatibility without heavy migration tooling.

---

## One-Line Summary

**Stamp every diagram with a version; auto-upgrade old ones on load.** Backup first, migrate in place, and let users bulk-upgrade from the dashboard.

```
┌──────────────────────────────────────────────────────────────────┐
│                    Version-Aware Flow                              │
├──────────────────────────────────────────────────────────────────┤
│  Save/Export   │ schemaVersion: '6.0.0' on every payload/snapshot  │
│  Load          │ needsUpgrade? → backup → migrate → return         │
│  Import        │ migrateToLatest(snapshot) before insert           │
│  Dashboard     │ version-status → "X need upgrade" → bulk-upgrade  │
└──────────────────────────────────────────────────────────────────┘
```

---

## How It Works

| Feature | One-liner | What the code does |
|---------|-----------|--------------------|
| **Save** | "Stamp the version" | Add `schemaVersion: '6.0.0'` to canvas in save payload |
| **Export** | "Carry real version" | Use `getCanvasVersion(diagram.canvas)` instead of hardcoded version |
| **Load** | "Backup before upgrade" | If `needsUpgrade()` → create backup `{name}_oldversion_{version}` → copy Diagram/Nodes/TP → migrate canvas → update original |
| **Import** | "Migrate then insert" | Validate schema, run `migrateToLatest()` on snapshot, then create records |
| **Bulk upgrade** | "Upgrade all at once" | `GET /version-status` → banner → `POST /bulk-upgrade` loops over each diagram |

---

## Code Entry Points

| Feature | Backend | Frontend |
|---------|---------|----------|
| Version status | `GET /api/data/diagrams/version-status` | Dashboard fetches on load |
| Bulk upgrade | `POST /api/data/diagrams/bulk-upgrade` | Dashboard "Upgrade All" button |
| Single load | `GET /api/data/diagrams/:id` (headers `X-Diagram-Upgraded-From`, `X-Diagram-Backup-Name`) | Dashboard, Open Network Modal, App |
| Import feedback | `POST /api/data/diagrams/import` (returns `migratedFrom`) | Dashboard, Import button |

---

## Key Implementation Details

1. **schemaMigrations.ts**: `CURRENT_SCHEMA_VERSION`, `VERSION_ORDER`, `migrations`, `canvasMigrations`; `migrateToLatest()` for snapshots, `migrateCanvasIfNeeded()` for stored canvas.
2. **performDiagramUpgrade()**: Shared helper for backup + upgrade; used by single load and bulk-upgrade.
3. **List badge**: GET /diagrams returns `schemaVersion` and `needsUpgrade` per diagram; Dashboard shows "Upgrade" badge.
4. **Upgrade toast**: After opening an upgraded diagram, show "Diagram upgraded from X to current. Backup saved as Y."
5. **Import feedback**: When `migratedFrom` is returned, show "File was version X. Upgraded to current version."

---

## Acceptance Checklist

| Criterion | Status |
|-----------|--------|
| schemaVersion in save payload and export snapshot | ✅ |
| Old diagrams (no schemaVersion) load as legacy | ✅ |
| Exported JSON from previous versions imports correctly | ✅ |
| AI prompt template (COMPAT_CHECK_PROMPT.md) | ✅ |
| Migration registry with example | ✅ |
