---
title: Unit Conversion and Administration
sidebar_position: 19
description: Explains the shared UnitConversion data model, conversion formula, and current process for adding or changing units.
---

# Unit Conversion and Administration

## Overview

HyProNet stores conversions in PostgreSQL `UnitConversion` and exposes them to the frontend as a map grouped by dimension. A dimension has exactly one conceptual base unit; every row defines a target unit relative to it.

```ts
// One UnitConversion row
{
  dimension: 'Temperature',
  base_unit: 'K',
  target_unit: 'C',
  multiplier: 1,
  formula_offset: -273.15,
  formula_note: 'C = K - 273.15'
}
```

The domain endpoint groups rows into this runtime structure:

```ts
{
  Temperature: {
    base_unit: 'K',
    units: {
      C: { multiplier: 1, offset: -273.15 }
    }
  }
}
```

## Conversion Rule

The stored definition means:

```text
target value = base value × multiplier + offset
base value   = (target value - offset) / multiplier
```

For example, with K as base and C as target, `300 K` displays as `26.85 C`; `26.85 C` converts back to `300 K` for solver bounds. The frontend helper is `components/modal/utils.ts`; Equation Writing applies the same direction before solver dispatch in `solverEngineApiService.ts`.

Only convert within the same dimension. Changing an Equation Writing variable's dimension clears its bounds because reusing values across dimensions would be invalid.

## Adding a Unit

System administrators add units through the protected `/api/admin/units` API, or through the system workbook/import process when catalog data is managed as a workbook. There is currently no user-facing unit-administration screen.

1. Choose an existing dimension and its canonical base unit, or define both for a new dimension.
2. Add one row for each non-base target unit. Repeat the same `dimension` and `base_unit` on every row in that dimension.
3. Calculate `multiplier` and `formula_offset` using the formula above.
4. Reload domain data or restart the relevant client session, then verify a value can make a round trip: base → target → base.
5. Run a computation and verify Equation Writing bounds are sent in the base unit.

Example request for a multiplicative conversion:

```http
POST /api/admin/units
Content-Type: application/json

{
  "dimension": "Pressure",
  "base_unit": "Pa",
  "target_unit": "kPa",
  "multiplier": 0.001
}
```

The API requires an authenticated administrator. `GET /api/admin/units`, `PATCH /api/admin/units/:id`, and `DELETE /api/admin/units/:id` list, change, and remove rows.

## Current Limitation for Offset-Based Units

The schema and runtime support `formula_offset` and `formula_note`; the admin route currently does not accept or update those two fields. Therefore use the workbook/import path (or a controlled database migration) for an offset-based unit such as Celsius/Fahrenheit until the admin route is extended. Do not create an offset conversion through the current POST/PATCH API and assume it is correct.

## Data Integrity Requirements

- Keep `base_unit` consistent for all rows in a dimension. The runtime map uses the rows it reads and cannot safely resolve conflicting base-unit definitions.
- Do not create duplicate target units within a dimension. The current schema does not enforce that uniqueness, and duplicate rows can overwrite one another in the runtime map.
- Use a non-zero finite multiplier.
- Renaming/removing a unit can invalidate saved display units in equations, node values, cost rows, and measurements. Migrate existing records first.
- The base unit itself need not be a `target_unit` row; the code recognizes `base_unit` directly.

## Verification

1. Call `GET /api/admin/units` as an administrator and confirm the row.
2. Reload domain data and confirm the dimension/unit appears in Equation Writing or the node variable editor.
3. Enter an easily checked value, switch units, and switch back without losing the original value (allowing normal floating-point rounding).
4. With `SAVE_JSON_FILES=true` only in a safe development environment, inspect the generated request and confirm equation token bounds and `units` use the base unit.

## Source Files

- `src/src/backend/prisma/postgres/schema.prisma`
- `src/src/backend/routes/adminUnitRoutes.ts`
- `src/src/backend/routes/dataRoutes.ts` (`getAllUnits`)
- `src/src/frontend/src/components/modal/utils.ts`
- `src/src/frontend/src/components/header-bar/header-buttons/equation-writing-module.tsx`
- `src/src/backend/services/solverEngineApiService.ts`

## Related Pages

- [Equation Writing Module Code Explanation](./equation-writing-module.md)
- [System and User Table Reference](./system-and-user-table-reference.md)
- [Calculation Server Payload Reference](./calculation-server-payload-reference.md)
