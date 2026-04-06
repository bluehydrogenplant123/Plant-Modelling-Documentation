# TP Duration, Base TP, and `solve_request.costs.duration`

## Overview
This document summarizes the TP duration feature set added across frontend and backend:
- TP range duration storage in `tp_node_vers`
- Diagram-level Base TP duration in `diagrams`
- Network/subnetwork inheritance rules
- Injection of duration data into solver payload under `parameters.costs.duration`

Key files:
- `src/src/backend/prisma/mongodb/schema.prisma`
- `src/src/backend/routes/dataRoutes.ts`
- `src/src/backend/routes/computeRoutes.ts`
- `src/src/backend/utils/translation.ts`
- `src/src/frontend/src/components/header-bar/header-buttons/base-tp-button.tsx`
- `src/src/frontend/src/components/header-bar/header-buttons/global-tp-button.tsx`

---

## 1. Database Model Changes

### 1.1 `tp_node_vers` (range-level duration)
`TpNodeVers` now stores:
- `duration` (`Float?`)
- `durationUnit` (`String?`)

These fields represent the duration assigned to each TP range (`fromTp` ~ `toTp`).

### 1.2 `diagrams` (Base TP duration)
`Diagram` now stores:
- `duration` (`Float?`, default `1`)
- `durationUnit` (`String?`, default `"hours"`)

This pair is treated as the diagram-level **Base TP duration default**.

---

## 2. Backend Duration Rules

### 2.1 Supported units
All duration write paths use one shared allowed set:
- `minutes`
- `hours`
- `days`
- `weeks`

Duration is normalized to:
- positive numeric value
- 6-decimal precision

### 2.2 Base TP update endpoint
New API:
- `PUT /api/data/diagrams/:diagramId/base-duration`

Input:
```json
{
  "duration": 1,
  "durationUnit": "hours"
}
```

Behavior:
1. Validate duration + unit.
2. Find all diagrams in the same network (main + linked subnetworks).
3. Update `duration` / `durationUnit` on all those diagrams.

This enforces shared Base TP duration across the full network graph.

### 2.3 Diagram create/update behavior
`POST /diagrams` and `PUT /diagrams/:diagramId` now accept/maintain diagram duration fields:
- If request provides valid duration fields, use them.
- Otherwise use existing/default diagram config (`1 hours` fallback).

### 2.4 Subnetwork inheritance behavior
When subnetwork instances are created (or reused with updates), instance diagrams inherit target duration config from parent/base context.

---

## 3. Frontend Behavior

### 3.1 Base TP panel
`Base TP` button is under **Model** section.

Panel fields:
- `Duration`
- `Duration Unit` (`minutes/hours/days/weeks`)

Features:
- Unit switch auto-converts duration value.
- Save calls `PUT /api/data/diagrams/:diagramId/base-duration`.
- Button is disabled once Multi-TP is already in use (non `1-1` TP ranges exist).

### 3.2 Global TP panel
Global TP now includes:
- range `duration`
- range `duration unit`

For newly created TP ranges:
- default value comes from diagram Base TP (`diagram.duration`, `diagram.durationUnit`).

This ensures Multi-TP defaults inherit Base TP settings.

---

## 4. `solve_request` Extension (`costs.duration`)

### 4.1 Target output shape
Duration is now added under `parameters.costs`, same level as `entities` and `mappings`:

```json
"costs": {
  "entities": [...],
  "mappings": [...],
  "duration": [
    {
      "From TP": 1,
      "To TP": 1,
      "Duration": 1,
      "DurationUnit": "hours"
    }
  ]
}
```

### 4.2 Generation location
- Build source data in `computeRoutes.ts` (`/api/compute/start`)
- Serialize into final payload in `translation.ts`

### 4.3 Base TP vs Multi TP rule
During compute request preparation:
1. Read all `tp_node_vers` rows for involved diagrams.
2. For the current diagram:
   - **If no TP rows**: use Base TP from `diagram.duration`, `diagram.durationUnit`, and emit one range `1-1`.
   - **If Multi TP exists**: use TP ranges from one representative node (all nodes are expected to share same TP segmentation) and emit one duration item per TP range.

### 4.4 Sanitization before output
`translation.ts` sanitizes outgoing `costs.duration`:
- normalizes TP bounds
- normalizes duration precision
- validates/fallbacks unit to `hours` when invalid

---

## 5. Practical Notes
- `costs.duration` is always generated as an array.
- Field names in final payload are currently:
  - `"From TP"`
  - `"To TP"`
  - `"Duration"`
  - `"DurationUnit"`
- The array can contain one item (base-only) or multiple items (multi-range TP).

---

## 6. Related Existing Docs
- `docs/CodeExplanation/global-tp.md`
- `docs/CodeExplanation/header-bar.md`
- `docs/CodeExplanation/timePeriodViewer.md`
- `docs/CodeExplanation/tpChanges.md`
