---
title: Code Explanation Overview
sidebar_position: 5
description: Overview of current HyProNet CodeExplanation coverage, reading order, and documentation boundaries.
---

## Overview

This page explains what the current HyProNet `CodeExplanation` set covers and how contributors should read it. The active source documentation parent is:

```text
docs/
```

Within that source parent, current `CodeExplanation` pages live under `docs/CodeExplanation/`, and current setup guides live under `docs/Installation/`.

In the published Docusaurus sidebar, the source folders appear as top-level groups: `Installation` and `CodeExplanation`. Contributors should not expect or create another visible wrapper menu above them.

These pages form a maintenance map for the main application flows: dashboard and canvas entry, header controls, node and edge editing, diagram save and node cache persistence, subnetwork persistence, TP and Economic data, run configuration, backend data routes, compute dispatch, solver callbacks, translation, reverse translation, and Excel import setup.

Use this overview for orientation, then use the [Code Explanation Index](./code-explanation-index.md) as the complete current link entry point.

## What This Documentation Represents

The current `CodeExplanation` set represents the core source areas a contributor is most likely to touch when maintaining HyProNet.

- It maps the primary frontend editing path from dashboard load to React Flow canvas interaction.
- It follows important state handoffs between React components, Redux slices, backend routes, MongoDB diagrams and nodes, PostgreSQL reference data, and local storage.
- It explains the main persistence flows for saved diagrams, dirty node cache data, subnetwork blueprints, subnetwork instances, TP changes, and computation results.
- It documents the solver-facing boundary: compute start, Bull queue dispatch, solver request construction, callback handling, reverse translation, and result storage.
- It documents the import boundary that turns system Excel workbooks into normalized CSV contracts and PostgreSQL catalog data.

The set is intentionally workflow-oriented. It explains how important features work across files and layers so future changes can start from the correct owner, data shape, and side-effect boundary.

## What This Documentation Does Not Represent

This set is not a full API reference, exhaustive source listing, or complete catalog of every route, helper, prop, field, test, and UI branch in the repository.

- It does not replace reading the current source code before changing behavior.
- It does not document every internal helper when that helper is not a maintenance entry point.
- It does not list every backend endpoint as an API specification.
- It does not treat generated files, runtime logs, or solver debug artifacts as source-of-truth documentation.
- It does not make legacy archive pages current again.

If a feature is not covered here, inspect the source, then add or update a focused `CodeExplanation` page when the area becomes a maintenance surface.

## Current Surface and Legacy References

Current `CodeExplanation` source files live in `docs/CodeExplanation/`. In the published sidebar, they appear under `CodeExplanation`. Contributors should start with the current pages in this folder and follow current links only. Installation and startup guides live in `docs/Installation/`.

The legacy archive at `docs-archive/PreviousDoc/CodeExplanation/` is historical reference only. It can help with topic discovery or older context, but current behavior, API contracts, data ownership, and verification commands must come from the current source code and current docs.

Ignore misplaced or generated `CodeExplanation` copies under `version6.1/`, including `version6.1/doc/docs/capstone/CodeExplanation/`, when deciding current placement, sidebar order, or documentation coverage.

## Recommended Reading Order

1. Start with [CodeExplanation Writing Standards](./CODE_EXPLANATION_GUIDELINES.md) to understand placement, page structure, generated-artifact rules, and verification expectations.
2. Use the [Code Explanation Index](./code-explanation-index.md) to locate the current page for a feature or workflow.
3. Read [Dashboard and Canvas Code Explanation](./dashboard-and-canvas.md), then [Header Bar Code Explanation](./header-bar.md), to understand the main frontend shell.
4. Read [Shape Node and Ports Code Explanation](./shape-node-and-ports.md), [Custom Edge and Stream Selection Code Explanation](./custom-edge-and-stream-selection.md), and [Node Modal and Variable Inputs Code Explanation](./node-modal-and-variable-inputs.md) for canvas element editing.
5. Read [Save Diagram and Node Cache Code Explanation](./save-diagram-and-node-cache.md) before changing persistence, save metadata, dirty node cache behavior, or canonical node ID remapping.
6. Read [Subnetwork Blueprint and Instance Flow Code Explanation](./subnetwork-blueprint-and-instance-flow.md) before changing reusable blueprint or wrapper-instance behavior.
7. Read [Time Period and Economic Flow](./time-period-and-economic-flow.md) and [Run Config and Computation Start](./run-config-and-computation-start.md) before changing run setup, TP data, Economic data, or compute-start handoff.
8. Read [Backend Data Routes and Persistence Code Explanation](./backend-data-routes-and-persistence.md) before changing Express data routes, authentication behavior, MongoDB diagram/node persistence, or PostgreSQL catalog reads.
9. Read [Compute, Solver Callback, and Results Code Explanation](./compute-solver-callback-and-results.md) and [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md) before changing solver request shape, queue behavior, callbacks, generated parameters, or result persistence.
10. Read [Excel Import Pipeline Code Explanation](./excel-import-pipeline.md) before changing workbook normalization, importer scripts, Prisma setup, or reference-data loading.

## Page Map by Functional Domain

| Functional domain | Read first | Main boundary explained |
| --- | --- | --- |
| Documentation standards | [CodeExplanation Writing Standards](./CODE_EXPLANATION_GUIDELINES.md), [Code Explanation Index](./code-explanation-index.md) | Current docs placement, page shape, verification expectations, and link entry points. |
| Frontend shell | [Dashboard and Canvas Code Explanation](./dashboard-and-canvas.md), [Header Bar Code Explanation](./header-bar.md) | Dashboard actions, canvas route state, React Flow shell, header controls, and high-level edit guards. |
| Canvas element editing | [Shape Node and Ports Code Explanation](./shape-node-and-ports.md), [Custom Edge and Stream Selection Code Explanation](./custom-edge-and-stream-selection.md), [Node Modal and Variable Inputs Code Explanation](./node-modal-and-variable-inputs.md) | Node rendering, port resolution, stream edge selection, modal edits, Redux updates, and node cache handoff. |
| Save and subnetworks | [Save Diagram and Node Cache Code Explanation](./save-diagram-and-node-cache.md), [Subnetwork Blueprint and Instance Flow Code Explanation](./subnetwork-blueprint-and-instance-flow.md) | Diagram save payloads, dirty node persistence, canonical ID remapping, blueprint save, wrapper instances, and MongoDB persistence. |
| TP, Economic, and run setup | [Time Period and Economic Flow](./time-period-and-economic-flow.md), [Run Config and Computation Start](./run-config-and-computation-start.md) | Base TP, Multi-TP data, Economic cost ownership, run config selection, compute-start payload inputs, and generated parameter handoff. |
| Backend data API | [Backend Data Routes and Persistence Code Explanation](./backend-data-routes-and-persistence.md) | Express route mounting, authentication, MongoDB user data, PostgreSQL reference data, and route fallback behavior. |
| Compute and solver | [Compute, Solver Callback, and Results Code Explanation](./compute-solver-callback-and-results.md), [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md) | Task creation, queue dispatch, solver request construction, callback status, reverse translation, and result persistence. |
| Import and setup boundary | [Excel Import Pipeline Code Explanation](./excel-import-pipeline.md), [HyProNet Installation Guide](../Installation/HYPRONET_INSTALLATION_GUIDE.md), [HyProNet Streamlined Guide](../Installation/STARTUP_GUIDE.md) | Workbook-to-CSV normalization, Prisma setup, Docker services, PostgreSQL catalog writes, and local runtime setup. |

## Boundary Map

Use the page set as a boundary map when choosing where to make a change.

- Data and API boundary: start from [Backend Data Routes and Persistence Code Explanation](./backend-data-routes-and-persistence.md), then move to the feature page that owns the frontend or workflow input.
- Persistence boundary: start from [Save Diagram and Node Cache Code Explanation](./save-diagram-and-node-cache.md) for diagram and node cache writes, or [Subnetwork Blueprint and Instance Flow Code Explanation](./subnetwork-blueprint-and-instance-flow.md) for blueprint and instance persistence.
- Solver boundary: start from [Run Config and Computation Start](./run-config-and-computation-start.md), then follow [Compute, Solver Callback, and Results Code Explanation](./compute-solver-callback-and-results.md) and [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md).
- Import boundary: start from [Excel Import Pipeline Code Explanation](./excel-import-pipeline.md), then use the setup guides only for local environment and execution context.
- Frontend interaction boundary: start from [Dashboard and Canvas Code Explanation](./dashboard-and-canvas.md) and [Header Bar Code Explanation](./header-bar.md), then follow the specific node, edge, modal, TP, Economic, or save page.

## Common Maintenance Paths

For a UI bug in canvas editing, read the frontend shell pages first, then the node, edge, or modal page that owns the interaction.

For a saved-data bug, read the save page first, then the backend data page, and only then inspect the feature page that created the saved field.

For a solver payload or result bug, read the run configuration page, compute page, and translation page together. Generated files such as `src/src/backend/services/solve_request.json` can confirm runtime behavior, but they are read-only debugging output, not the source contract.

For an importer or catalog-data bug, read the Excel import page first, then inspect the backend data page for how imported PostgreSQL data is read by the application.

## Related Pages

- [CodeExplanation Writing Standards](./CODE_EXPLANATION_GUIDELINES.md)
- [Code Explanation Index](./code-explanation-index.md)
