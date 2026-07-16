# User Tables Menu Design

## Goal

Replace the separate top-level **Materials** and **Economic** entries with a single **User Tables** dropdown that reuses the existing Material and Economic editors for base-period and Multi-TP data.

## Confirmed Menu Labels

The menu items appear in this order:

1. **Material Properties**
2. **Cost and Revenue Data**
3. **Supply and Demand Data**

The labels apply to menu entries only. Existing editor titles, table columns, import formats, and persisted data shapes remain unchanged.

## User Experience

### Base period

- The top toolbar contains one **User Tables** dropdown in place of the current **Materials** and **Economic** buttons.
- **Material Properties** opens the existing Material Editor.
- **Cost and Revenue Data** opens the existing base-period Economic cost-and-revenue panel.
- **Supply and Demand Data** opens the existing base-period Economic demand-and-supply panel.
- Each editor retains its current default system data, Import, Export, and Save behavior.

### Multi-TP

- The current **Economic** dropdown inside the **Multi-TP** secondary toolbar is replaced by a **User Tables** dropdown.
- **Material Properties** remains visible but is disabled and visually greyed out.
- **Cost and Revenue Data** opens the existing Multi-TP cost-and-revenue panel.
- **Supply and Demand Data** opens the existing Multi-TP demand-and-supply panel.
- The existing requirement that the graph be verified before Multi-TP Economic editing remains enforced.

## Architecture

### `UserTablesMenu`

Create a focused `UserTablesMenu` component under the header-bar button directory. It owns only dropdown presentation and routing:

- accepts `mode: 'base' | 'mtp'`;
- accepts independent Material and Economic disabled states;
- accepts the existing Material Editor open callback;
- renders the three confirmed menu entries in a stable order;
- routes Economic selections through the existing `CostButtons` modal controller.

The component does not fetch, transform, import, save, or persist table data.

### Economic editor integration

Extend `CostButtons` with a custom trigger-rendering interface. `CostButtons` continues to own Economic panel state and supplies an `openPanel(panelType)` callback to `UserTablesMenu`. Existing button and dropdown trigger modes remain supported for backward compatibility.

This keeps Material routing outside the Economic component and avoids moving the large, established Economic editor implementation.

### Menu option model

Create a small TypeScript menu-option module containing:

- the menu item keys and labels;
- the base/Multi-TP disabled-state calculation;
- the stable option ordering.

The React component consumes this model, and Jest tests exercise it without requiring a browser DOM environment.

## Disable Rules

- Base **Material Properties** follows the existing `Materials.MaterialEditor` computing-disable rule.
- Both Economic items follow the existing `Costs.CostButtons` computing-disable rule.
- Multi-TP **Material Properties** is always disabled.
- Multi-TP Economic items are disabled when either `Costs.CostButtons` is disabled or the graph is not verified.
- The dropdown toggle remains available so disabled items can still be seen; individual items enforce availability.

## Data and Performance Boundaries

- No backend routes, Prisma schemas, request payloads, workbook formats, or storage contracts change.
- Existing Material and Economic import code is reused without modification to its data semantics.
- Existing scoped base/Multi-TP Economic save behavior remains unchanged.
- No additional save calls, computed-data writes, or background fetches are introduced. Economic data continues to load only when an Economic panel opens.

## Testing

1. Add Jest tests for exact labels, stable ordering, base-period availability, Multi-TP Material disabling, and independent Economic disabling.
2. Add a focused header integration/source assertion that the obsolete top-level **Materials** and **Economic** buttons are removed, the base `UserTablesMenu` is present, and the Multi-TP Economic entry uses `UserTablesMenu`.
3. Run the focused Jest tests.
4. Run the frontend TypeScript/Vite build to validate the TSX integration.
5. Inspect the final diff to confirm that unrelated dirty-worktree files and protected save paths were not modified.

## Out of Scope

- Redesigning the Material or Economic tables.
- Renaming existing Economic modal titles or changing Cost/Revenue grouping.
- Adding Material Properties support for Multi-TP.
- Changing import/export formats or backend persistence.
- Refactoring unrelated header controls.
