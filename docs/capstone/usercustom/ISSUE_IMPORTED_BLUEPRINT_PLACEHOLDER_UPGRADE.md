# Imported subnetwork blueprints from external snapshots are placeholders and cannot be independently upgraded

## Summary
When importing an old external `FullNetworkSnapshot`, the root diagram can be imported in compatibility mode and upgraded later, but imported subnetwork blueprint rows are not actually imported as full old blueprints.

For example, after importing `Blue_Hydrogen_Final_1_Plant_Network_4xdj2t.json`, the root network can show `Upgrade`, but the imported `FIREDH_NET` blueprint cannot be independently upgraded because the imported blueprint is only a placeholder record.

## Current behavior
- Root diagram import preserves the old snapshot version and can show `Upgrade`.
- Imported subnetwork blueprint rows appear in the `Subnetwork Blueprints` list.
- Those imported blueprint rows do not behave like real imported old blueprints.
- They cannot be independently upgraded from the dashboard.
- Loading them may only open a placeholder shell rather than a fully imported historical blueprint canvas.

## Expected behavior
One of these behaviors should be implemented consistently:

1. Preferred
- External snapshot import should carry full blueprint canvas data.
- Imported blueprint diagrams should preserve their original schema version.
- Imported blueprints should support manual `Upgrade` just like imported root diagrams and imported instance diagrams.
- Upgrade should still create backups.

2. Alternative
- If blueprint canvas data is not part of the snapshot contract, imported blueprint placeholders should not be presented as if they were fully imported editable blueprints.
- The UI and import flow should make it clear they are metadata placeholders only.

## Repro
1. Import an old external snapshot such as `Blue_Hydrogen_Final_1_Plant_Network_4xdj2t.json`.
2. Observe that the root network can require upgrade.
3. Observe that the imported `FIREDH_NET` row appears under `Subnetwork Blueprints`.
4. Observe that the blueprint does not have an independent upgrade path as a real imported old blueprint.

## Root cause
Current `FullNetworkSnapshot` export/import only carries blueprint metadata in `subnetworkBlueprints`:
- `model_name`
- `shape`
- `icon_width`
- `icon_height`
- `portsMapping`
- `modelVersions`
- `blueprintDiagramId`

It does **not** carry the blueprint diagram canvas itself.

During import, the backend creates a new blueprint diagram placeholder with an empty current-schema canvas and then creates the `subnetworkBlueprint` row against that placeholder.

Because of that:
- the imported blueprint is not a real historical blueprint diagram
- it has no preserved old canvas to upgrade
- it cannot behave like an independently imported old blueprint

## Suggested direction
- Extend snapshot export/import so blueprint diagrams can be serialized with their actual canvas and related records, not only metadata.
- Preserve imported blueprint schema version during compatibility import, similar to root and instance diagrams.
- Allow imported blueprint diagrams to participate in manual upgrade and backup flows.
- If full blueprint import is intentionally out of scope, adjust UI/wording so placeholders are not shown as equivalent to real imported blueprints.

## Acceptance criteria
- Importing an old external snapshot results in imported blueprint diagrams that are either:
  - real, loadable historical blueprint diagrams that can later be upgraded with backups, or
  - clearly marked placeholders that are not presented as normal imported blueprints.
- Dashboard behavior is consistent between root diagrams, instance diagrams, and imported blueprints.
- No false impression that a placeholder blueprint is a fully imported editable old blueprint.
