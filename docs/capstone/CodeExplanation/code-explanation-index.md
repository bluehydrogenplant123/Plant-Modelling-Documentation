---
title: Code Explanation Index
sidebar_position: 4
description: Current entry point for HyProNet CodeExplanation pages, grouped by source area and workflow.
---

## Overview

Use this page as the current entry point for HyProNet feature and workflow explanations. Current source `CodeExplanation` files live under:

```text
docs/CodeExplanation/
```

Current source setup and installation guides live under `docs/Installation/` and are linked from the Import/Runtime section when runtime context is needed.

In the published Docusaurus sidebar, the source folders appear as top-level groups: `Installation` and `CodeExplanation`. There is no extra visible wrapper menu above them.

The legacy archive at `docs-archive/PreviousDoc/CodeExplanation/` is historical reference only. Do not treat archive pages as current behavior unless the source code has been rechecked. Misplaced or generated CodeExplanation copies under `version6.1/`, including `version6.1/doc/docs/capstone/CodeExplanation/`, are intentionally not linked from this index.

## Standards

- [CodeExplanation Writing Standards](./CODE_EXPLANATION_GUIDELINES.md): placement rules, required structure, frontmatter expectations, source-file standards, verification expectations, and generated-artifact cautions for current CodeExplanation pages.
- [AI CodeExplanation Maintenance Workflow](./ai-codeexplanation-maintenance-workflow.md): subagent-based workflow for creating, updating, reviewing, and publishing current CodeExplanation documentation from source code.

## Orientation

- [Code Explanation Overview](./code-explanation-overview.md): high-level coverage, boundaries, recommended reading order, and page map for the current CodeExplanation set.

## Frontend/Core UI

- [Dashboard and Canvas Code Explanation](./dashboard-and-canvas.md): dashboard create/load/delete flows, canvas shell routing, React Flow setup, sidebar drag-and-drop, display filtering, and high-level edit guards.
- [Header Bar Code Explanation](./header-bar.md): top-level canvas navigation, secondary controls, Optimization/DataRec setup orchestration, shared-editor signals, save metadata, display filtering, run configuration entry points, and computation-aware UI guards.
- [Optimization and DataRec Setup and Selected Solve Inputs](./solve-request-selected-inputs.md): active Calc Type dropdowns, selection versus editing boundaries, Header-owned run state, authoritative backend resolution, queued snapshots, and `parameters.solve_inputs`.
- [Material Domain Editor Workflow Code Explanation](./material-domain-editor-workflow.md): User Tables entry, Domain + Port Class grouping, Generic/common materials, Properties/Fractions views, workbook import, API grouping, and solver sanitization boundaries.
- [Shape Node and Ports Code Explanation](./shape-node-and-ports.md): shape-node rendering, port resolution, rotation behavior, modal handoff, Redux updates, node cache updates, and save-flow integration.
- [Custom Edge and Stream Selection Code Explanation](./custom-edge-and-stream-selection.md): orthogonal stream edge rendering, stream-property selection, validation, connected-node hydration, and edge-level interaction contracts.
- [Node Modal and Variable Inputs Code Explanation](./node-modal-and-variable-inputs.md): node modal tabs, stream and info variables, specs, TP overrides, Redux state, and node-cache coordination.
- [Equation Writing Module Code Explanation](./equation-writing-module.md): equation authoring, tokenization, Add Variable metadata, Dimension/Unit conversion, Mongo persistence, and solver equation normalization.
- [Constraint Module Code Explanation](./constraint-module.md): `+Constr` set and collection layout, Redux draft cache, equation membership assignment, deletion guards, and Mongo persistence.
- [Solution Algorithm Library Module Code Explanation](./solution-algo-library-module.md): SoluAlgoLib table editing, PostgreSQL base rows, Mongo diagram selections, Algorithm dropdown integration, and solver configuration payload.

## Save/Subnetwork

- [Save Diagram and Node Cache Code Explanation](./save-diagram-and-node-cache.md): diagram save behavior, dirty-node persistence, node-cache diffs, canonical node ID remapping, save metadata, and exact request payloads.
- [Subnetwork Blueprint and Instance Flow Code Explanation](./subnetwork-blueprint-and-instance-flow.md): blueprint save flow, wrapper instance persistence, instance node ID remapping, parent connections, and subnetwork payload contracts.

## TP/Economic/Run

- [Time Period and Economic Flow Code Explanation](./time-period-and-economic-flow.md): base TP, global TP, Sliding Horizon UI and persistence, TP specs, economic panels, cost data ownership, and solver payload handoff.
- [TP Spec Version Management Code Explanation](./tp-spec-version-management.md): version identity, Base/MTP and calculation-type isolation, sparse MongoDB persistence, frontend operations, API contracts, active-version compute binding, callback scoping, and result traceability.
- [Run Config and Computation Start Code Explanation](./run-config-and-computation-start.md): solver configuration, SoluAlgoLib ownership, Optimization/DataRec selections, MTP-only Sliding Horizon handling, backend start behavior, and solver request boundaries.

## Backend/Data

- [Backend Data Routes and Persistence Code Explanation](./backend-data-routes-and-persistence.md): Express data API wiring, authentication, MongoDB and PostgreSQL boundaries, persistence helpers, and route-level fallback behavior.
- [System and User Table Reference](./system-and-user-table-reference.md): complete PostgreSQL system-table and MongoDB user-collection inventory, representative structures, purposes, and ownership rules.
- [Unit Conversion and Administration](./unit-conversion-and-administration.md): conversion formula, base-unit model, administration API, workbook path, and current offset-unit limitation.

## Compute/Translation

- [Compute, Solver Callback, and Results Code Explanation](./compute-solver-callback-and-results.md): selected-input snapshotting, compute task creation, Bull queue dispatch, solver request construction, external callback handling, reverse translation, and result persistence.
- [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md): solver-facing parameter construction, `parameters.tps_specs`, `parameters.costs`, stream/material data, reverse translation, and computed TP updates.
- [Calculation Server Payload Reference](./calculation-server-payload-reference.md): canonical final `/solve/` request shape, every assembled extension field, ownership, and normalization rules.

## Import/Runtime

- [Excel Import Pipeline Code Explanation](./excel-import-pipeline.md): system workbook import, workbook-to-CSV normalization, Prisma database setup, reference-data writes, and import verification boundaries.
- [Real Solver Quickstart](../Installation/REAL_SERVER_QUICKSTART.md): direct Microsoft Dev Tunnels CLI callback setup, route verification, compute acceptance, and failure classification without VS Code port forwarding.
- [HyProNet Installation Guide](../Installation/HYPRONET_INSTALLATION_GUIDE.md): current detailed setup, environment, workbook import, and real solver connectivity guide.
- [HyProNet Streamlined Guide](../Installation/STARTUP_GUIDE.md): concise current startup, shutdown, update, and real solver notes.

## Navigation Rule

For current feature documentation, start from the visible `CodeExplanation -> Code Explanation Index` page in Docusaurus, or from the source path `docs/CodeExplanation/` when editing files. Use `docs/Installation/` for install and runtime setup guides. Use `docs-archive/PreviousDoc/CodeExplanation/` only for historical comparison, and do not link new current docs to misplaced `version6.1/` CodeExplanation copies.
