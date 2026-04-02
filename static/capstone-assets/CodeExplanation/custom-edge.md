# Custom Edge

## Overview
- Location: `src/src/frontend/src/components/custom-edge/index.tsx`
- Purpose: Replaces the default React Flow edge to support stream-aware labeling, validation, and node-model synchronization.
- Rendered as edge type `custom` with smooth-step paths and dynamic labels.

## Props (inputs/outputs)
- Inbound from React Flow via `EdgeProps<Edge<{ stream: Stream; sourceHandle: string; targetHandle: string }>>`:
  - `id`, `label`, `source`, `target`, `sourceX/Y`, `targetX/Y`, `sourcePosition`, `targetPosition`, `markerEnd`, `data`, `selected`.
- No explicit return value; renders a path and label renderer.

## Core Functions
- `getPortPosition(node, portLocation)` — params: measured node, portLocation; return: `{x,y}` absolute canvas coords; respects rotation.
- `getPortBorderPosition(node, portLocation)` — params: node, port; return: `Position` enum; uses rotation-aware helper.
- `getSmoothStepPath(...)` — from `@xyflow/react`; returns `[path, labelX, labelY]` used for rendering and label placement.
- `updateNodeData(stream?)` — params: selected `Stream`; return: Promise<void>; loads model versions (via `useNodeCache`), injects stream fractions/properties using `updateModelVersionWithDomainStream`, dispatches `canvas/updateComputationResults`, and updates node cache so nodes stay in sync.
- `setLabel(stream?)` — params: optional stream; return: void; clears existing node data, updates edge label/data handles, and triggers `updateNodeData` when a stream is chosen.
- `updateName(name)` — param: string | undefined; return: void; writes edited name into `edge.data.stream.name`.
- `clearNodeData()` — return: void; removes stream components from attached nodes via `deleteStreamComponent` and syncs cache.

## Composition
- Label editor: `EdgeLabelSelector` (shown when the edge is selected and the canvas is not verified).
- Static label: `EdgeLabel` (shown otherwise).
- Styling: `custom-edge.css` plus label-specific classes (`edge-label-renderer__custom-edge`, `edge-label-name__custom-edge`).

## Key Behavior
- Computes path via `getSmoothStepPath`, adjusting for rotated source/target ports (`getPortPositionWithRotation` and `portLocationMap`).
- Tracks `sourceHandle`/`targetHandle` to keep labels aligned with the correct ports even after edits.
- Streams:
  - Streams are loaded from Redux `domain.data.streams`.
  - Selecting a stream updates the edge label, persists the stream on `edge.data.stream`, and triggers `updateNodeData`.
- `updateNodeData` ensures model versions exist (canonical ids included) and writes new node parameters derived from stream fractions/properties before dispatching Redux updates.
- Stream-derived values are treated as system-generated (`is_human_input = false`) and are only applied when the current value is not human-owned.
- `clearNodeData` removes stream components from both endpoints when a label is cleared.
- Name editing: `EdgeLabelSelector` enforces unique stream names and can auto-generate defaults using `shortid`; `updateName` persists the edited value on the edge.

## Usage
```tsx
const edgeTypes = { custom: CustomEdge };
const defaultEdgeOptions = { type: 'custom', markerEnd: { type: MarkerType.ArrowClosed } };

<ReactFlow
  nodes={nodes}
  edges={edges}
  edgeTypes={edgeTypes}
  defaultEdgeOptions={defaultEdgeOptions}
/>
```

## Notes
- Verification lock: when `verified` is true, the selector is hidden and only the static label renders.
- Positioning respects node rotation; ensure node measurement is available (`node.measured`) for precise label placement.
- When adding new stream properties, extend the matching logic in `isStreamKeyAndPortVarNameMatching` to keep node parameters in sync.
