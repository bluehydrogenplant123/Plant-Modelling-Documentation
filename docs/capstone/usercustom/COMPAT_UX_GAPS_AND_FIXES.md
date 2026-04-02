# Compatibility: Gaps and Simple Fixes

Review of export/import, duplicate, subnetwork blueprints, and dashboard UX.

---

## 1. Export Version Bug — FIXED

**Issue:** Export always set `version: CURRENT_SCHEMA_VERSION` even when the diagram canvas was old.

**Fix applied:** Export and duplicate now use `getCanvasVersion(diagram.canvas)` so the snapshot reflects the actual data version. Duplicate also runs `migrateToLatest` before import so the copy is upgraded.

---

## 2. Duplicate

**Status:** Duplicate uses export → import. After fixing export version (above), duplicate will work correctly: source diagram version is preserved in the snapshot, and import runs migration.

**No extra change needed.**

---

## 3. Subnetwork Blueprints

**Status:** Blueprints are diagrams (type 1) with a `SubnetworkBlueprint` record. Our upgrade flow (GET /diagrams/:id) runs on any diagram. When a blueprint is opened, we create a backup and upgrade it. We do **not** copy the `SubnetworkBlueprint` record for the backup—the backup is for recovery only. The original blueprint diagram is upgraded and keeps its `SubnetworkBlueprint` link.

**No extra change needed.** Backup diagrams are not meant to be full blueprints; they are raw data backups.

---

## 4. Subnetwork Instances in Export — FIXED

**Issue:** Nested `subnetworkInstances[].canvas` were not migrated.

**Fix applied:** `migrateToLatest` now recursively migrates each `subnetworkInstances[].canvas` via `migrateCanvasIfNeeded`.

---

## 5. Dashboard: Proactive Upgrade — FIXED

**Issue:** If a diagram is not opened for a long time, it may need many migration steps (e.g. 1.0 → 6.0 → 6.1 → … → 6.5). Long chains increase the risk of failure. Upgrading when entering the dashboard would keep diagrams up to date.

**Fix applied:** Added `GET /diagrams/version-status` and `POST /diagrams/bulk-upgrade`. Dashboard fetches version-status on load, shows banner when `needsUpgradeCount > 0`, and "Upgrade All" button calls bulk-upgrade. Backend uses shared `performDiagramUpgrade()` for both single-load and bulk-upgrade.

---

## 6. Other Small UX Tweaks — FIXED

| Item | Status |
|------|--------|
| **Upgrade toast** | After opening an upgraded diagram (dashboard, open-network-modal, or App direct load), show: "Diagram upgraded from X to current. Backup saved as Y." |
| **List badge** | GET /diagrams returns `schemaVersion` and `needsUpgrade` per diagram; dashboard shows "Upgrade" badge for diagrams needing upgrade. |
| **Import feedback** | Import endpoint returns `migratedFrom` when migration occurred; dashboard and import-diagram-modal show "File was version X. Upgraded to current version." |

---

## Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| 1 | Export version fix | ~5 min |
| 2 | Recursive migrate for subnetworkInstances | ~10 min |
| 3 | GET /diagrams/version-status + POST /diagrams/bulk-upgrade | ~30 min |
| 4 | Upgrade toast on load | ~5 min |
| 5 | List badge (optional) | ~15 min |
