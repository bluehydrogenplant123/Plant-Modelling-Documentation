# Global TP (Bulk TP + Duration Assignment)

## Overview
- **Location:** `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`
- **Purpose:** A bulk editor that applies one unified TP segmentation to all nodes (main diagram + subnetworks), and now also manages **duration** metadata per TP range.
- **Visibility:** The button renders only after diagram verification (`state.canvas.verified === true`).
- **Primary storage target:** MongoDB `tp_node_vers` (`duration`, `durationUnit` per TP range row).

## What Changed
The Global TP panel now includes two additional editable columns:
- `Duration`
- `Duration Unit`

Supported units:
- `minutes`
- `hours`
- `days`
- `weeks`

When users switch unit, the numeric duration is converted automatically (value-preserving conversion, rounded to 6 decimals). Decimal durations are supported.

## Data Flow
1. Open modal:
   - Fetch main diagram + subnetwork diagrams.
   - Fetch `TpNodeVers` rows from all related diagrams.
   - Fetch diagram-level Base TP duration (`diagram.duration`, `diagram.durationUnit`).
2. Build Grid:
   - User enters add/delete TP counts.
   - System builds canonical TP ranges.
3. Edit ranges:
   - Split/confirm/cancel range rows.
   - Edit `from tp`, `to tp`, `duration`, `duration unit`.
4. Validate:
   - Range coverage must be continuous and complete.
   - Every range must have valid positive `duration`.
5. Apply to All Nodes:
   - Rewrites node TP ranges into `tp_node_vers`.
   - Persists `duration` + `durationUnit` with each TP range row.

## Default Duration Behavior
For new TP ranges created from Global TP:
- default duration comes from diagram-level **Base TP** duration (`diagram.duration`, `diagram.durationUnit`)
- not from hardcoded null values anymore

This keeps newly created multi-TP ranges aligned with Base TP settings.

## Unit Conversion Rules
- Conversion base internally uses hour-equivalent factors.
- Conversion happens whenever `Duration Unit` changes.
- Unsupported/invalid units fallback to `hours`.
- Invalid/non-positive durations are rejected in validation.

## Backend Compatibility
Global TP depends on backend APIs that now accept and persist duration fields:
- `POST /api/data/tpnodevers`
- `PUT /api/data/tpnodevers`
- `GET /api/data/tpnodevers`

`durationUnit` validation now enforces the same allowed set:
- `minutes`, `hours`, `days`, `weeks`

## Related Components
- `TimePeriodViewer` for per-node TP/model-version editing.
- `Base TP` panel for diagram-level default duration management.
- `header-bar/index.tsx` for button placement under **Multi-Time Period**.
