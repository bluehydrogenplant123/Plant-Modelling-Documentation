# Minimal Subnetwork Ref Schema Plan

## Goal

Reduce drift between parent net and subnet mappings without doing a large database redesign first.

The current problem is that one logical subnetwork link is stored in too many aliases:

- `node.data.diagramId`
- `node.data.instanceDiagramId`
- `node.data.blueprintDiagramId`
- `node.data.model.diagramId`
- `node.data.model.instanceDiagramId`
- `node.data.model.blueprintDiagramId`
- `Diagram.parentConnections`

That duplication is the main reason upgrade, duplicate, import, rollback, and delete flows keep drifting out of sync.

## Canonical Shape

Keep the existing Mongo collections for now, but introduce one canonical forward reference on wrapper nodes:

```ts
node.data.subnetworkRef = {
  blueprintDiagramId?: string;
  instanceDiagramId?: string;
}
```

Canonical ownership after the refactor:

- Wrapper node forward link:
  - `node.data.subnetworkRef`
- Instance diagram reverse link:
  - `Diagram.parentConnections`
- Blueprint metadata:
  - `SubnetworkBlueprint`

`model.diagramId` should stop being treated as the canonical instance pointer. It remains a compatibility alias during transition only.

## Rollout

### Step 1: Compatibility Read + Dual Write

Purpose:

- old saves still load
- new saves begin writing `subnetworkRef`
- import/duplicate/remap paths keep `subnetworkRef` in sync

Concrete rules:

- Add helper readers that prefer `subnetworkRef`, then fall back to legacy aliases.
- Add helper writers that write:
  - `node.data.subnetworkRef`
  - legacy aliases still needed by current runtime
- Update the main wrapper read paths first:
  - save preparation
  - compute expansion
  - translation
  - runtime post-compute updates
  - dashboard/import/duplicate/remap paths that rewrite wrapper references

No destructive migration yet.

### Step 2: Save-Time Canonicalization

Purpose:

- all newly saved diagrams normalize wrapper refs into one consistent shape
- reduce alias drift in active data

Concrete rules:

- save payload always includes `subnetworkRef`
- keep legacy aliases only as compatibility mirrors
- add invariant checks before persist:
  - wrapper `instanceDiagramId` points to type `2`
  - wrapper `blueprintDiagramId` points to type `1`
  - instance `parentConnections.parentDiagramId` and `wrapperNodeId` remain resolvable

### Step 3: Final Compatibility Cleanup

Purpose:

- migration removes dependence on old aliases
- runtime stops reading scattered fallback fields

Concrete rules:

- add a real schema migration only when the structure is stable
- migrate old wrapper aliases into `subnetworkRef`
- remove code paths that treat `model.diagramId` or `node.data.diagramId` as canonical

## What Step 1 Must Touch

These are the minimum places that should understand `subnetworkRef` immediately:

- frontend wrapper creation and save normalization
- frontend wrapper navigation / subdiagram discovery
- backend wrapper extraction for export/import/upgrade/delete
- backend compute-time instance expansion
- backend translation subnetwork resolution
- backend computation result back-propagation
- backend import/duplicate blueprint remapping

## Why This Is The Minimal Version

This plan deliberately does not introduce a new Mongo collection yet.

It fixes the highest-cost issue first:

- too many aliases for the same relationship

while keeping the rest of the system operational and backward-compatible.

## Release Version Reset Plan

The current `6.3.0-alpha.2` line is being used as a testing line, not as the intended formal delivery version.

That is workable as long as two buckets are kept separate:

### Keep

- structural bug fixes
- delete / backup / rollback safety fixes
- mapping normalization helpers
- canonical `subnetworkRef` support

### Revert Or Squash Before Formal Delivery

- testing-only schema labels
- testing-only migration labels
- testing-only snapshot labels
- temporary test database contents

If formal delivery should still present as `6.0.0`, the later cleanup pass should:

- reset code labels such as `CURRENT_SCHEMA_VERSION`, `VERSION_ORDER`, save payload schema labels, and snapshot labels
- keep the mapping and robustness fixes
- use a clean test database or production seed, not the temporary alpha test saves

This is not especially hard if done in one explicit cleanup pass. The hard part is only if testing version labels and permanent runtime fixes get mixed into the same conceptual change and are no longer easy to separate.
