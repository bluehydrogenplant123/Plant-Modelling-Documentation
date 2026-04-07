# Compatibility: Gaps and Simple Fixes

Review of export/import, duplicate, subnetwork blueprints, and dashboard UX under the clean `6.0.0` baseline.

## 1. Export Version Bug

`Export` should record the actual diagram version, not blindly stamp the current version.

Status:
- Fixed by using the stored canvas version for export metadata.

## 2. Duplicate

`Duplicate` still runs through export plus import.

Status:
- Works with the clean baseline because export preserves the source version and import only upgrades supported legacy payloads.

## 3. Subnetwork Blueprints

Blueprints are still ordinary diagrams plus a `SubnetworkBlueprint` record.

Status:
- Backups are recovery copies only; the original blueprint remains the canonical linked record.

## 4. Nested Subnetwork Instances in Export

Nested `subnetworkInstances[].canvas` must stay aligned with the same migration rules as the root canvas.

Status:
- Fixed by running the same migration helper on nested canvases during snapshot migration.

## 5. Dashboard Upgrade UX

The dashboard should surface legacy diagrams before the user opens them.

Status:
- `GET /diagrams/version-status` and `POST /diagrams/bulk-upgrade` remain useful for supported legacy diagrams.
- Explicitly tagged unsupported versions should be rejected rather than bulk-upgraded.

## 6. User Feedback

Useful feedback remains:

- Upgrade toast after a supported legacy diagram is upgraded
- List badge for diagrams that still need upgrade
- Import feedback showing `migratedFrom` when a supported legacy snapshot was upgraded

## Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| 1 | Preserve actual export version | Low |
| 2 | Keep nested canvas migration aligned | Low |
| 3 | Surface version status in dashboard | Medium |
| 4 | Show upgrade feedback clearly | Low |
| 5 | Reject unsupported versions explicitly | Low |
