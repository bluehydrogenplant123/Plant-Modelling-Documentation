# Structured Subnets: Current Implementation (Brief)

This note summarizes how structured subnetworks are implemented today in this codebase.

## 1. Compute-time expansion (supports nested subnetworks)

- Entry path: `src/src/backend/routes/computeRoutes.ts`
- `expandSubnetworkInstances(...)` recursively walks wrapper nodes (`diagramId` + `portsMapping`) and expands all reachable instance diagrams into one assembled canvas.
- While expanding, backend loads node documents for each involved diagram and stores:
  - `nodeId` (canvas id)
  - `documentId` (Mongo node id, used by solver)
  - `diagramId`
  - `modelVersion`

## 2. Wrapper port resolution to real internal nodes

- Entry path: `src/src/backend/utils/translation.ts`
- `buildSubnetworkPortMap(...)` resolves wrapper `portsMapping` recursively until a non-wrapper internal node is found.
- This recursion is not limited to 2 levels; it follows wrapper -> wrapper -> ... -> real node.
- If an edge uses a wrapper port that cannot be mapped, translation throws an error (fail fast).

## 3. How `net_name` is assigned

- Wrapper nodes are skipped from `parameters.nodes`.
- For real nodes:
  1. Use explicit `nodeData.net_name` if set.
  2. Else use diagram-to-net mapping derived from wrapper net names.
  3. Else fallback to root network name.
- `node_name` sent to solver uses node `documentId` when available (not temporary canvas id).

## 4. Keeping payload sections consistent

Current implementation keeps network naming aligned across payload sections:

- `nodes[].net_name`: resolved node network
- `tps_specs[].network`: copied from `node.net_name`
- `stream_connectivity.source_network` / `terminal_network`: resolved from endpoint mapping
- `global_params.network_config`: regenerated from used network names:
  - `&lt;net&gt; -&gt; null` for each used network
  - `&lt;root&gt; -&gt; &lt;childNet&gt;` links for non-root networks

## 5. Export / import / duplicate behavior for subnetworks

- Entry path: `src/src/backend/routes/dataRoutes.ts`
- Export includes:
  - `subnetworkBlueprints`
  - `subnetworkInstances` (canvas, nodes, tp data, `parentConnections`, snapshot)
- Import/duplicate creates new instance diagrams and remaps IDs in:
  - wrapper `portsMapping`
  - `parentConnections`
  - edges and TP records
- Duplicate also merges current instance nodes with snapshot nodes so nodes added later are preserved.

## 6. Practical rule in current design

- Network identity in solver payload is currently string-based (`net_name`).
- For copied/nested instances, each logical instance should have a distinct `net_name`; reusing old instance net names can cause ambiguity and wrong mapping.
