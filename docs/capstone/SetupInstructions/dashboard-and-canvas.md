---
title: Dashboard and Canvas Code Explanation
sidebar_position: 10
description: Explains how the current dashboard creates and loads diagrams and how the React Flow canvas shell coordinates canvas state, sidebar drag-and-drop, navigation, and high-level UI guards.
---

## Overview

The Dashboard is the authenticated landing surface for creating, importing, exporting, loading, and deleting diagrams. After a user creates or loads a diagram, control moves to the React Flow canvas shell in `App.tsx`, which loads domain or diagram data, renders the canvas, wires the header bar and sidebar, and keeps high-level Redux state synchronized with route state.

This page covers the current frontend shell flow only. Backend CRUD route behavior, solver translation, save internals, and detailed node or edge renderers are delegated to their own source files.

## Source Files

- `src/src/frontend/src/pages/dashboard.tsx`: dashboard form, diagram lists, import/export/delete/load handlers, and navigation into the canvas routes.
- `src/src/frontend/src/pages/Dashboard.css`: dashboard card layout and list action spacing.
- `src/src/frontend/src/App.tsx`: React Flow canvas shell, route-driven diagram/domain loading, sidebar/header composition, display filtering, autosave counter wiring, and canvas edit guards.
- `src/src/frontend/src/components/sidebar/index.tsx`: domain-model palette rendering for drag-and-drop node creation.
- `src/src/frontend/src/components/sidebar/sidebar-item.tsx`: draggable model tile contract and blueprint self-drop guard.
- `src/src/frontend/src/components/sidebar/sidebar.css`: palette sizing, scroll behavior, and resolution-scale-aware styling.
- `src/src/frontend/src/components/header-bar/index.tsx`: canvas header contract consumed by `App.tsx`.
- `src/src/frontend/src/features/canvas/canvasSlice.ts`: canvas metadata, verification status, diagram type, node names, node parameters, computation status, parent connections, and diagram node cache state.
- `src/src/frontend/src/features/domain/domainSlice.ts`: domain-data loading, stream sanitization, and domain snapshot state used by the sidebar and run configuration UI.
- `src/src/frontend/src/features/saved/savedSlice.ts`: saved/unsaved status, active save flag, last save timestamp, and save duration state shown in the header.
- `src/src/frontend/src/store.ts`: Redux store wiring and middleware that marks most state-changing actions as unsaved.
- `src/src/frontend/src/utils/exportDownload.ts`: export filename normalization and browser download helper used by the dashboard.
- `src/src/frontend/src/utils/displayNodeFilter.ts`: canvas node display filter labels and subnetwork-wrapper detection used by `App.tsx` and the header Display button.

## Purpose and Responsibility

The Dashboard owns the first-step UI for choosing a diagram name, domain, calculation type, and description, plus list actions for existing diagrams and subnetwork blueprints. It does not render the canvas itself and it does not persist a newly created diagram immediately; it prepares Redux state and navigates to `/canvas/:domainId`.

`ReactFlowWrapper` and `ReactFlowCanvas` in `App.tsx` own the canvas shell. They load route-specific data, mount React Flow, place the sidebar and header inside React Flow panels, coordinate high-level edit guards, and keep canvas-level Redux state in sync with loaded backend data. They do not own the detailed implementation of save, computation, material editing, model modals, custom node rendering, or custom edge configuration.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `canvasName`, `domain`, `calcType`, `description` | Dashboard local form state | Prepares a new unsaved canvas session. |
| `diagrams` | `GET /api/data/diagrams` in `dashboard.tsx` | Populates verified and unverified diagram lists and duplicate-name checks. |
| `domains` | `GET /api/data/domains` in `dashboard.tsx` | Populates the domain selector. |
| `blueprints` | `GET /api/data/subnetworks` in `dashboard.tsx` | Populates the Subnetwork Blueprints list. |
| `domainId` | route param in `App.tsx` | Loads domain data for a new canvas route. |
| `diagramId` | route param in `App.tsx` | Loads an existing diagram and polls computation status. |
| `focusNodeId` | query string in `App.tsx` | Selects and fits the matching React Flow node once per diagram or domain. |
| `domain.data.models` | Redux domain slice | Drives the sidebar palette. |
| `canvas.verified` | Redux canvas slice | Hides the sidebar and blocks drops, new connections, and the custom delete-key listener. |
| `canvas.isComputationProcessing` | Redux canvas slice | Disables canvas editing, hides the sidebar, shows the computation notice, and dims the Leva panel. |
| `nodeCache.dirtyNodes` | node cache service consumed by `App.tsx` | Feeds the autosave threshold counter. |

| Output | Destination | Notes |
| --- | --- | --- |
| `/canvas/:domainId` navigation | React Router | Starts a new canvas from domain data and temporary dashboard form data. |
| `/diagram/:diagramId` navigation | React Router | Opens an existing diagram route after the dashboard seeds minimal metadata. |
| `localStorage["temp_diagram_<domainId>"]` | Browser local storage | Stores in-progress dashboard name and description when a domain is selected. |
| `canvas` Redux state updates | `canvasSlice.ts` | Tracks metadata, verification, diagram type, node names, parent connections, computation status, and node parameters. |
| `domain` Redux state updates | `domainSlice.ts` | Stores fetched domain data or a loaded diagram snapshot. |
| `defaultNodes` / `defaultEdges` mutation | `initial-elements` arrays imported by `App.tsx` | Seeds React Flow default elements after existing diagram load and clears them on navigation cleanup. |
| Browser JSON download | `downloadJsonFile(...)` | Exports the full diagram snapshot returned by the backend. |

## Core State and Data Structures

- `canvasName`, `domain`, `description`: Dashboard local form fields. They are also written into temporary local storage only after a domain is selected.
- `calcType`: Dashboard local state initialized from `state.calcType.type`; on submit it dispatches `updateCalcType(calcType as CalcType)`.
- `type`: Dashboard local diagram type state defaults to `0`. Current JSX does not expose a selector for changing it, so normal dashboard creation uses type `0` unless future UI is added.
- `diagrams`, `domains`, `blueprints`: Dashboard-fetched arrays. Each fetch avoids a React state update when `JSON.stringify(prev) === JSON.stringify(response.data)`.
- `canvasSlice` state: includes `canvasName`, `description`, `verified`, `nodeParameters`, `tpChangesDraft`, `streamParameters`, `computationStatus`, `isComputationProcessing`, `currentDiagramId`, `nodeNames`, `nodeRotations`, `type`, `nodes`, `portMappings`, and `parentConnections`.
- `domainSlice` state: stores `data`, `status`, and `error`. `fetchDomainData(domainId)` loads `/api/data/domain/:domainId`; `setDomainData(...)` stores a loaded diagram snapshot after stream property sanitization.
- `displayNodeFilter`: React Flow canvas local state with values `all`, `normal`, and `subnetwork`. It controls which nodes and attached edges remain visible.
- `AUTO_SAVE_NODE_THRESHOLD`: constant value `3` in `App.tsx`. The header receives the remaining count but the actual save call is owned by `useSaveDiagram`.
- `modelNameMap`: `dashboard.tsx` has a local module-level map used during dashboard delete cleanup. `App.tsx` imports a separate `modelNameMap` from the settings tab module for canvas node naming and cleanup.
- `defaultNodes` and `defaultEdges`: imported mutable arrays used as React Flow defaults. `App.tsx` clears and repopulates them during route changes and existing diagram load.

## Main Functions and Components

- `Dashboard`: renders the landing page, fetches list data, dispatches Redux setup actions, and routes to the canvas.
- `handleSubmit(e)`: validates duplicate names and required form fields, clears old canvas state, fetches domain data, writes new diagram metadata to Redux, marks the new diagram unverified, sets diagram type, and navigates to `/canvas/${domain}`.
- `handleLoadDiagram(diagramId)`: clears stale canvas state, fetches the diagram once, initializes node names, current diagram ID, diagram type, and parent connections, then navigates to `/diagram/${diagramId}`.
- `handleDeleteDiagram(diagramId)`: fetches the diagram to remove node names from dashboard cleanup state, deletes the backend diagram, refreshes the list, and shows an alert.
- `handleDeleteSubnetwork(blueprintId)`: deletes the subnetwork blueprint, refreshes blueprint data, shows a blueprint success alert, and then calls `handleDeleteDiagram` for the associated `blueprintDiagramId`.
- `handleExportDiagram(diagramId, diagramName)`: prompts for an export name, calls `/api/data/diagrams/:id/export`, normalizes the final filename, and downloads the snapshot JSON.
- `handleImportDiagram(file)`: parses a selected JSON file, posts current snapshot formats to `/api/data/diagrams/import`, falls back to the legacy `/api/data/diagrams` path, optionally verifies legacy imports, refreshes the list, and clears the hidden file input.
- `ReactFlowWrapper`: owns route cleanup, domain load, existing diagram load, computation polling, loading-state rendering, and the outer `ReactFlowProvider`.
- `ReactFlowCanvas`: owns React Flow event handlers, header/sidebar panels, material editor modal, save confirm modal, display filtering, autosave threshold tracking, custom delete-key handling, and canvas edit guards.
- `Sidebar`: reads `state.domain.data.models` and renders draggable `SidebarItem` entries.
- `SidebarItem`: writes `application/reactflow` and serialized `model` data into `dataTransfer`; it prevents dragging a subnetwork blueprint into its own diagram.

## Rendered UI / Interaction Map

| UI State or Action | Source State or Props | Expected Result | Verification |
| --- | --- | --- | --- |
| Dashboard opens | Auth context `user`, fetched domains, diagrams, and blueprints | Shows the signed-in user's welcome message, a Create New Network card, Verified Networks, Unverified Networks, and Subnetwork Blueprints. | Start app, log in, open the dashboard route. |
| Type a diagram name | `canvasName`, `nameError`, `diagrams` | Input updates; duplicate error is cleared while typing. On blur, an exact duplicate name clears the field and shows "Diagram name must be unique.". | Type an existing diagram name, blur the field. |
| Select a domain after entering form data | `domain`, `canvasName`, `description` | Temporary data is written to `localStorage` under `temp_diagram_<domainId>`. | Inspect browser local storage after changing the selector. |
| Click Create Diagram with valid fields | Dashboard local state and Redux dispatches | Old canvas state is cleared, domain data fetch starts, name/description/calc type are stored, `verified` becomes `false`, and route changes to `/canvas/<domainId>`. | Create a network and confirm the canvas route opens. |
| Click Create Diagram with missing fields | Required inputs and submit guard | Browser required-field validation may block submit; if the handler runs without required state, an error alert is dispatched. | Try submitting with a missing domain or calculation type. |
| Click Load on an existing diagram | `diagrams` list item ID | Dashboard clears stale state, fetches the diagram, seeds node names/type/parent connections, and navigates to `/diagram/<diagramId>`. | Click Load and watch route plus loaded canvas state. |
| Export a diagram | `handleExportDiagram` prompt and export endpoint | A browser prompt asks for the base filename; Cancel stops export. Confirm downloads a normalized `.json` snapshot. | Click Export, test both Cancel and confirmed names with spaces. |
| Import a current snapshot | Hidden file input, JSON `version` of `1.0.0` or `6.0.0`, `metadata` | Posts `{ snapshot }` to `/api/data/diagrams/import`, shows success, may mention migration, refreshes diagram list, and updates local `calcType` if metadata provides one. | Import a known current-format export and check alert/list refresh. |
| Import a legacy snapshot | JSON without current snapshot metadata | Builds a legacy diagram payload, appends a random suffix for duplicate names, posts to `/api/data/diagrams`, optionally calls verify, and refreshes the list. | Import a legacy JSON with and without duplicate name. |
| Delete a diagram | Diagram list action | Fetches node metadata, removes node names from cleanup state, deletes the backend diagram, refreshes the list, and shows an info alert. | Delete a test diagram and confirm it disappears after refresh. |
| Delete a subnetwork blueprint | Blueprint list action | Deletes blueprint, refreshes blueprints, shows blueprint success alert, then deletes the associated diagram through `handleDeleteDiagram`. | Delete a disposable blueprint and confirm both list changes. |
| Canvas opens for new domain | `domainId` route and `domain.status` | Shows loading/preparing messages while domain data loads, then renders React Flow with header and sidebar if not verified or computing. | Create a diagram from the dashboard and observe route and palette. |
| Canvas opens for existing diagram | `diagramId` route | Shows "Loading existing diagram...", fetches the diagram, restores metadata, nodes, edges, node names, verification, calc type, domain snapshot or domain fallback, and saved state. | Load an existing diagram and confirm nodes and metadata appear. |
| Drag a sidebar model onto canvas | `SidebarItem` `dataTransfer`, React Flow `onDrop` | Creates a selected shape node, stores modelVersion in node cache, stores a slim model in the canvas node, marks unsaved, and refreshes base TP parameters. | Drag a normal model from the palette and inspect the new node. |
| Try to drag a blueprint into its own diagram | `model.diagramId` and current route ID | Drag start is prevented and no node is dropped. | Open a blueprint diagram and try dragging its own blueprint model. |
| Connect ports | React Flow connection event, domain model port metadata | Duplicate connections are selected instead of recreated; new connections require source port type `2`, target port type `1`, matching handle data, and create a custom edge with `forceConfigOpen: true`. | Connect valid ports, then repeat the same connection. |
| Select Display filter | Header `DisplayButton` updates `displayNodeFilter` | Non-matching nodes are hidden and deselected; edges attached to hidden nodes are hidden and deselected. | Apply "Subnetwork nodes" then "All nodes". |
| `focusNodeId` query param exists | URL query and current nodes | Matching React Flow node ID or `data.model.node_id` is selected and fit into view once for the current route. | Open `/diagram/<id>?focusNodeId=<nodeId>`. |
| Computation is processing | `canvas.isComputationProcessing` | React Flow edit handlers are disabled, nodes cannot be dragged or connected, sidebar is hidden, a warning panel appears, and Leva is dimmed and non-interactive. | Start or mock a running computation and observe canvas guards. |
| Diagram is verified | `canvas.verified` | Sidebar is hidden, drops and new connections are blocked, and the custom Delete/Backspace listener is not attached. | Load a verified diagram and try palette drop/delete-key actions. |

## Component Contract

### Dashboard

`Dashboard` receives no props. It depends on:

- Auth context: `user`, `userId`, and `logout`.
- Redux dispatch from `useAppDispatch`.
- Redux selector: `state.calcType.type`.
- React Router navigation from `useNavigate`.
- Backend endpoints under `/api/data`.

Important child and DOM contracts:

- The Create New Network form requires `Diagram Name`, `Select Domain`, `Calculation Type`, and `Description`.
- The import control is a hidden `<input type="file" accept=".json,application/json">` triggered by the visible Import Diagram button.
- The Verified and Unverified list branches only show the empty message when `diagrams.length === 0`, not when a specific filtered list is empty.
- Blueprint list items currently render every fetched blueprint in `blueprints`; `user_id` is read from auth context but not used as a client-side filter.

### ReactFlowWrapper

`ReactFlowWrapper` receives no props. It depends on route params:

- `domainId`: new canvas flow.
- `diagramId`: existing diagram flow and computation polling.

It provides `ReactFlowCanvas` with:

| Prop | Source | Contract |
| --- | --- | --- |
| `theme`, `snapToGrid`, `panOnScroll`, `zoomOnDoubleClick` | Leva `useControls` | Passed directly into React Flow options. |
| `disabled` | `state.canvas.isComputationProcessing` | Disables canvas edit handlers and visual interaction while a computation is processing. |
| `nodeCache` | `useNodeCache()` | Used for dropped-node modelVersion storage, dirty-node tracking, node delete cleanup, and autosave threshold tracking. |
| `resolutionScale` | window size calculation | Drives header/sidebar responsive sizing through CSS variables and child props. |

### ReactFlowCanvas

`ReactFlowCanvas` assumes it is rendered inside `ReactFlowProvider`. Its behavior-relevant dependencies are:

- React Flow hooks: `screenToFlowPosition`, `setNodes`, `getNodes`, `setEdges`, `getEdges`, `getNode`, `deleteElements`, `fitView`.
- Redux selectors: `canvas.verified`, `saved.lastSavedAt`, `saved.isSaving`, `canvas.nodeParameters`, `canvas.nodes`, `domain.data`, `calcType.type`.
- Route params: `diagramId` and `domainId`.
- Child props sent to `HeaderBar`: `setMaterialEditor`, `setSaveConfirm`, `remainingAutoSaveNodes`, `autoSaveNodeThreshold`, `displayNodeFilter`, and `setDisplayNodeFilter`.
- Child props sent to `Sidebar`: `resolutionScale`.

Hook and cleanup contracts:

- The autosave requestAnimationFrame is cancelled on unmount and when a save starts.
- Header panel height is measured with `ResizeObserver`; the CSS variable `--header-panel-height` is updated and the observer/listener are cleaned up.
- The custom Delete/Backspace listener is attached only when the diagram is not verified and is removed on cleanup.
- The computation status interval is cleaned up on effect cleanup and stops early when backend status says processing is false or when `/api/compute/details/:diagramId` returns 404.
- Route and before-unload cleanup clear domain data, canvas name, node naming maps, `defaultNodes`, `defaultEdges`, and node cache state.

## Data Flow

### Create New Diagram

1. User fills Dashboard form fields.
2. `handleSubmit` prevents default submit and checks `diagrams.some((d) => d.name === canvasName)`.
3. Dashboard clears node names and diagram nodes.
4. If name, domain, and calc type are present, Dashboard clears old computation, current diagram ID, canvas name, and description.
5. Dashboard dispatches `fetchDomainData(domain)`, `updateCalcType(...)`, `updateCanvasName(...)`, `updateDescription(...)`, `setVerified(false)`, and `setDiagramType(type)`.
6. Dashboard navigates to `/canvas/${domain}`.
7. `ReactFlowWrapper` sees `domainId`, fetches domain data when `domain.status === 'idle'`, restores any `temp_diagram_<domainId>` values into Redux, and renders the canvas once loading states clear.
8. The user edits the unsaved canvas; persistence happens later through save controls, not during Dashboard submit.

### Load Existing Diagram

1. User clicks a Dashboard Load button.
2. `handleLoadDiagram` clears prior canvas metadata, computation results, diagram nodes, parent connections, and node names.
3. Dashboard fetches `/api/data/diagrams/${diagramId}` and seeds node names, `currentDiagramId`, diagram type, and parent connections.
4. Dashboard navigates to `/diagram/${diagramId}`.
5. `ReactFlowWrapper` fetches the same diagram again for full canvas hydration.
6. `App.tsx` restores save metadata from `diagram_save_meta_<diagramId>`, sets current diagram ID, caches basic diagram node info, updates name/description, parent connections, type, verification, and calc type.
7. `App.tsx` writes loaded nodes and edges into `defaultNodes` and `defaultEdges`.
8. If the diagram contains a domain snapshot, `setDomainData(snapshot.data)` hydrates Redux; otherwise `fetchDomainData(res.data.domainId)` is used.
9. `updateSaved(true)` marks the loaded diagram as saved.

### Drag, Connect, Delete

1. `Sidebar` renders `domain.data.models` as `SidebarItem` entries.
2. `SidebarItem` writes shape type and serialized model data into `dataTransfer` on drag start.
3. `ReactFlowCanvas.onDrop` converts screen coordinates to flow coordinates, creates a timestamp-based node ID, creates a generated default node name, initializes modelVersion for the active calc type, stores modelVersion in node cache, and adds a selected React Flow node.
4. `onConnect` validates handles, avoids duplicates, checks source and target port metadata, and adds a selected custom edge.
5. Deleting edges removes stream-generated component values for affected ports and updates computation results.
6. Deleting nodes clears naming/cache state, removes base TP parameters for deleted nodes, resets machine-generated values on connected nodes, updates diagram nodes, removes attached edges, and marks the canvas unsaved.

### Display Filter

1. Header `DisplayButton` calls `setDisplayNodeFilter`.
2. `App.tsx` computes visible node IDs using `nodeMatchesDisplayFilter(...)`.
3. Matching nodes remain visible; non-matching nodes are set to `hidden: true` and deselected.
4. Edges are hidden and deselected if either endpoint node is hidden.

## Side Effects

- Dashboard reads `/api/data/domains`, `/api/data/diagrams`, and `/api/data/subnetworks` on mount.
- Dashboard creates imports through `/api/data/diagrams/import` for current snapshot payloads and `/api/data/diagrams` for legacy payloads.
- Dashboard may call `PATCH /api/data/diagrams/:id/verify` for verified legacy imports.
- Dashboard deletes diagrams through `DELETE /api/data/diagrams/:id` and deletes blueprints through `DELETE /api/data/subnetworks/:id`.
- Dashboard exports through `GET /api/data/diagrams/:id/export` and triggers a browser download.
- Dashboard writes temporary form data to `localStorage`.
- `App.tsx` reads `localStorage` keys `temp_diagram_<domainId>` and `diagram_save_meta_<diagramId>`.
- `App.tsx` calls `/api/data/diagrams/:diagramId` for existing diagram load and `/api/compute/details/:diagramId` for computation status polling.
- React Flow node/edge edits update local React Flow state, Redux canvas state, node cache state, saved status, and sometimes node parameters.
- Store middleware in `store.ts` marks most Redux actions as unsaved by dispatching `updateSaved(false)` unless the action is save or alert bookkeeping.

## Error Handling and Edge Cases

- Duplicate dashboard diagram names are exact string matches. On blur, a duplicate clears the input and shows inline feedback; on submit, a duplicate returns early.
- Dashboard submit with missing state dispatches `Please provide canvas name, domain, and calculation type.` if browser required-field validation does not stop it first.
- `fetchDomains`, `fetchDiagrams`, and `fetchBlueprints` log errors to the console but do not show user alerts.
- Import with no selected file shows `No file selected for import.`.
- Import parse, schema, or API failures show `Failed to import diagram. Check console for details.` and clear the hidden file input.
- Legacy import duplicate names receive a random six-character suffix.
- Legacy verify treats `400` responses containing `already verified` as success; `401` and `403` become a warning about permission.
- Export prompt cancel exits before calling the backend.
- Existing diagram load errors in Dashboard show `Failed to load diagram.`; existing diagram load errors in `App.tsx` are logged and clear the loading flag.
- Domain load failure in `domainSlice` leads `ReactFlowWrapper` to render `Error loading domain data`.
- If computation detail polling returns 404, `App.tsx` treats computation as idle and stops polling.
- `isValidConnection` and `onConnect` do not enforce exactly the same rules: `isValidConnection` checks same `port_class` and broad port-type compatibility, while `onConnect` finally requires source `port_type === 2` and target `port_type === 1`.
- Verified diagrams hide the sidebar and block drops/new connections/delete-key handling, but `verified` is separate from the computation `disabled` prop.
- Blueprint self-drag prevention is client-side and compares `model.diagramId` with the current route's last path segment.

## Extension Points

- Add a visible diagram type selector in `dashboard.tsx` by wiring an input to the existing `type` state and checking every downstream consumer of `canvas.type`.
- Change Dashboard list filtering in `dashboard.tsx`; if filtering blueprints by owner is required, use `blueprint.userId` and the existing `user_id` auth value intentionally.
- Add import format support in `handleImportDiagram`, then update backend import validation and manual import verification together.
- Change export naming by updating `handleExportDiagram` and `src/src/frontend/src/utils/exportDownload.ts` together.
- Add new domain data fields by updating `DomainData` in `models/domain.ts`, `domainSlice.ts` sanitization if needed, and any sidebar/header consumers.
- Change React Flow connection rules by updating both `isValidConnection` and `onConnect` in `App.tsx`; otherwise the preview and final edge creation can disagree.
- Extend display filtering by updating `DisplayNodeFilter`, `DISPLAY_NODE_FILTER_LABELS`, and `nodeMatchesDisplayFilter(...)`, then confirm `App.tsx` hides both nodes and attached edges correctly.
- Change autosave behavior in `App.tsx` and `useSaveDiagram` together; the header only displays the threshold state.
- Add canvas edit guards by using both React Flow option guards and event-handler guards, since `verified` and `disabled` protect different paths.

## Testing and Verification

Automated checks for code changes should be run from the repository's `src/` package when the implementation changes:

```powershell
cd C:\Users\19612\Desktop\Project\HYPRONET-GUI\src
npm.cmd run build
```

For a full browser flow, run the app from the same working directory:

```powershell
npm.cmd run dev
```

This page is documentation-only. When editing this page, verify source references and Markdown whitespace from the repository root:

```powershell
git diff --check -- docs/SetupInstructions/dashboard-and-canvas.md
```

### Frontend Manual Verification Matrix

| Area | Setup | Action | Expected Visual Result | Expected API or State Change | Regression Risk |
| --- | --- | --- | --- | --- | --- |
| New canvas creation | Dashboard with at least one domain | Enter unique name, select domain and calc type, enter description, click Create Diagram | Canvas route opens with header and palette | Redux name/description/calc type update; `fetchDomainData` runs; route is `/canvas/<domainId>` | High: wrong state causes later save to use stale metadata. |
| Duplicate name guard | Dashboard has an existing diagram name | Enter the exact same name and blur | Input clears and invalid feedback appears | No navigation; `nameError` is set | Medium: duplicate diagrams confuse import/export lists. |
| Existing diagram load | Dashboard has a saved diagram | Click Load | Loading message then diagram canvas appears | Dashboard and `App.tsx` both fetch diagram; Redux current ID/type/names/parent connections update | High: stale state can leak between diagrams. |
| Import current snapshot | Valid export JSON with version `1.0.0` or `6.0.0` | Click Import Diagram and select file | Success alert; list refreshes | `POST /api/data/diagrams/import`; optional local calc type update | High: import format drift can break recovery workflows. |
| Export cancel | Any listed diagram | Click Export and cancel prompt | No download | No export API call should be made | Low: avoids unexpected downloads. |
| Delete diagram | Disposable diagram | Click Delete | Diagram disappears after refresh; info alert appears | `GET /diagrams/:id`, `DELETE /diagrams/:id`, node names removed from cleanup state | High: wrong delete can remove saved work. |
| Sidebar drag | New unverified, not computing canvas | Drag a palette item onto canvas | New selected shape appears | Node cache receives modelVersion; canvas marked unsaved; node parameters refreshed | High: node creation is a core authoring path. |
| Invalid connection | Two incompatible ports | Drag a connection | Edge is not created | No edge added; saved state should not change for rejected final connect | Medium: invalid streams pollute solver input. |
| Duplicate connection | Existing valid edge | Connect same handles again | Existing edge becomes selected | No duplicate edge ID is added; existing edge data may set `forceConfigOpen` | Medium: duplicate edges corrupt stream ownership. |
| Display filter | Canvas with normal and subnetwork nodes | Use Display to show only one type | Hidden node type disappears; attached edges disappear | React Flow nodes/edges get `hidden`; hidden selections clear | Medium: hidden state must not delete data. |
| Computation processing guard | Existing diagram with processing status | Poll or set processing true | Warning panel appears; palette hidden; Leva dimmed | `isComputationProcessing` true; React Flow edit props disabled | High: editing during compute can invalidate results. |
| Verified guard | Verified diagram | Try palette drop and Delete key | Palette is hidden; Delete key does not delete | `verified` blocks drop/connect/delete-key handler | High: verified networks should not be accidentally mutated. |

## Known Cautions

- Do not treat legacy `docs-archive/PreviousDoc/CodeExplanation/dashboard.md` as current behavior. It describes a visible diagram type selector and blueprint user filtering that are not present in current `dashboard.tsx`.
- Dashboard creation prepares an unsaved canvas; it does not call a create-diagram endpoint during `handleSubmit`.
- Dashboard load performs an initial diagram fetch, and `App.tsx` fetches the same diagram again after navigation. Keep this double-load behavior in mind before adding expensive work to either path.
- Current Dashboard blueprint rendering does not filter by `userId` on the client side.
- The empty-list message for Verified and Unverified Networks depends on total `diagrams.length`, not the filtered list length.
- `modelNameMap` in `dashboard.tsx` is not the same map imported by `App.tsx`; do not assume dashboard delete cleanup updates the canvas map.
- `defaultNodes` and `defaultEdges` are mutable module-level arrays. Route cleanup and load ordering matter.
- `store.ts` marks most Redux actions unsaved. Adding high-frequency UI state to Redux can cause unexpected unsaved transitions.
- Generated runtime files such as `src/src/backend/services/solve_request.json` are not source of truth for this page and should not be edited for this documentation workflow.

## Related Pages

- `docs/SetupInstructions/header-bar.md`
- `docs/SetupInstructions/CODE_EXPLANATION_GUIDELINES.md`
