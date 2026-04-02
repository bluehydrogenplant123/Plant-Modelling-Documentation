# TP Changes (Multi-Time Period Overrides)

## Overview

`tp_changes` is a sparse override table used for Multi-Time Periods (non-Base TP). It stores deltas relative to the baseline so each time period can override node port variables.

Supported fields (used by UI display and solver input):
- `portVarValue`: numeric value (base_unit_default_value)
- `spec`: F / V / P / I (or empty)
- `lowerBound` / `upperBound`
- `unit`
- `fromTp` / `toTp` / `timePeriodId` / `nodeId` / `diagramId` / `portName` / `portVarName`

This table is only used for non-Base TP; Base TP still writes to `NodeCache/Node`.

---

## Frontend Write Path

Entry components:
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/node-var-input.tsx`

### 1) Trigger Flow

1. `NodeVarInput` captures user edits (value, spec, bounds, unit).
2. For non-Base TP, the event is forwarded to `NodeVarsTab.handleChangeWithTpLogic`.
3. `handleChangeWithTpLogic` compares against baseline and decides:
   - Diff exists → `POST /api/data/tpchanges` (Upsert)
   - No diff → `DELETE /api/data/tpchanges`

### 2) Diff Rules

Each field is compared to the baseline:
- `portVarValue`
- `spec`
- `lowerBound`
- `upperBound`
- `unit`

If any field differs, it triggers an Upsert. If all fields match, it deletes the entry.

### 3) Upsert Payload (Null-Safe)

Upsert writes not only the changed fields, but also necessary context values:
- `portVarValue`: if not modified but other fields changed, baseline value is used as fallback
- `spec` / `unit`: if not modified but other fields changed, baseline values are used as fallback
- `lowerBound` / `upperBound`: written only when changed, otherwise `null`

---

## Frontend Read & Merge

Entry function:
- `buildMergedPortsVarForTP` in `node-vars-tab.tsx`

Merge logic:
1. Fetch `tp_changes` for the TP:
   - `GET /api/data/tpchanges?diagramId&nodeId&timePeriodId`
2. Apply overrides to variables:
   - `base_unit_default_value`
   - `lower_bound` / `upper_bound`
   - `spec`
   - `selected_unit`
3. If an override does not exist in the baseline (e.g., dynamic component vars), append it to the list.

---

## Backend Solver Integration

Core files:
- `src/src/backend/utils/translation.ts`
- `src/src/backend/utils/translationTpsSpecsUtils.ts`

Data flow:
1. `translation.ts` builds `VariableOverride` from `tp_changes`:
   - `value` / `spec` / `lowerBound` / `upperBound` / `unit`
2. `resolveNodeState` injects overrides into `ModelVersion.model_var_object`:
   - overrides value/spec/bounds/unit
3. Generated `tps_specs` includes these fields.

---

## Common Issues & Protections

1) Bounds-only changes were not saved  
Fixed by diffing each field rather than relying on value changes.

2) Initial spec/unit saved as null  
Fixed by adding baseline fallback on Upsert.

---

## Related Docs

- `docs/CodeExplanation/portVariableDataLogic.md`
- `docs/CodeExplanation/timePeriodViewer.md`
