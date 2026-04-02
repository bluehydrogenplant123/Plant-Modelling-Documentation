# Node Configuration & Data Flow Module

## System Overview

This module manages the lifecycle of node data within the application, from initialization and stream connection to user input and persistence. It handles the complex merging of "Base" domain definitions with "Calculated" rules and "Time Period" specific overrides.

**Data Flow Summary:**

1. **Initialization:** `modelVersionUtils` generates the initial data structure when a node is created or modified.
2. **Hydration:** `useNodeDataPrefetch` loads this data, fetches overrides (`TpChanges`) from the backend, and merges them for the UI.
3. **Display:** `SettingsTab` acts as the controller, passing data to `NodeVarsTab` which renders the list.
4. **Interaction:** `NodeVarInput` captures user edits and routes them to the correct storage destination (Node Definition vs. Time Period Override).

---

## 1. Data Utilities (`modelVersionUtils.ts`)

**Purpose:** The low-level logic layer for generating and maintaining the integrity of `ModelVersion` objects. It bridges the gap between static Domain definitions and dynamic runtime connectivity.

### Core Functions

* **`initModelVersionWithCalcType(domainModel, calcType, nodeId, connectedEdges)`**
* **Role:** The factory function for node data.
* **Logic:**
1. Creates a deep copy of the static `domainModel`.
2. Applies `calcType` rules (e.g., setting specific variables to "Fixed" or "Free").
3. Calls `updateModelVersionWithConnectedEdges` to inject stream data.




* **`findStreamKeyForPortVar(streamProperties, portVarName)`**
* **Role:** Fuzzy-matching algorithm to map Stream properties (e.g., `T`, `MF_kg_hr`) to Port variables.
* **Logic:** Handles exact matches, case-insensitive matches, and unit-suffix matching (e.g., mapping stream property `MF_kg_hr` to variable `MF`).



---

## 2. Data Loading Hook (`useNodeDataPrefetch.ts`)

**Purpose:** A React hook responsible for fetching, synchronizing, and merging node data before it is displayed in the settings panel. It ensures the UI reflects the true state of the database (Base + Overrides).

### Inputs

* `reactFlowNodeId`: The ID of the selected node.
* `baseVersion`: The default model configuration for the node.
* `timePeriods`: The list of active time periods for this node.
* `calcType`: The current calculation mode (`Simulation`, `Optimization`, `DataRec`, `ParamUpdt`).

### Core Logic

1. **Fetch Overrides:** Queries the backend for `TpChanges` (sparse overrides) specific to this node.
2. **Merge Strategy (`buildMergedModelVersion`):**
* Iterates through all time periods.
* For each period, overlays the fetched `TpChanges` onto the `baseVersion`.


3. **Redux Synchronization:** Dispatches `updateComputationResults` to ensure the global application state mirrors the merged local state.
4. **State Update:** Updates the local `timePeriods` state in `SettingsTab` with the fully resolved model versions.

---

## 3. Settings Container (`settings-tab.tsx`)

**Purpose:** The main view controller for node configuration. It manages the context (Base vs. Time Period) and orchestrates the sub-components.

### Core State

* `model`: The current resolved state of the node.
* `activeTimePeriodId`: Tracks which time period is currently selected in the dropdown (Base vs. Specific TP).
* `verified`: Boolean flag indicating if the node has been validated against the backend.

### Key Responsibilities

* **Context Switching:** When the user changes the Time Period dropdown, this component updates the `model` prop passed to child components to reflect that specific period's state.
* **Navigation:** Contains logic for "Go to Subnetwork" if the node represents a subnetwork instance.
* **Display Logic:** Toggles between "Verified" (Read-only/Result view) and "Unverified" (Edit view) layouts.

---

## 4. Variable List (`node-vars-tab.tsx`)

**Purpose:** Renders the list of variable inputs for the selected node. It acts as a filter and layout manager for the raw variable data.

### Props

* `model`: The full model object containing `ports_var`.
* `activeTimePeriodId`: used to determine if the view is "Base" or "Future".
* `handleChange`: The master change handler function.

### Core Logic

* **Filtering:** Filters `model.ports_var` to exclude internal variables or those hidden by the `hidden_by_default` flag (unless the "Show Hidden Variables" toggle is active).
* **Base vs. Override Detection:**
* Calculates `isBaseTP` (boolean).
* Passes this flag to inputs so they know whether to update the *Definition* (Base) or create a *Delta* (Override).


* **Rendering:** Maps the filtered variables to `NodeVarInput` components.

---

## 5. Input Component (`node-var-input.tsx`)

**Purpose:** The atomic interaction component. It manages the complex behavior of a scientific input field, including unit conversion, bounds checking, and "Computed" vs "User-Defined" states.

### Props

* `value`: The numeric value to display.
* `isComputed`: Boolean flag. If `true`, the value is a result from the solver (displayed in green).
* `isBaseTP`: Controls whether edits are structural or temporal overrides.
* `handleChange`: Callback to persist changes.

### Core Functions

* **`handleInputChange`**: Updates local temporary state for responsive typing.
* **`handleBlur`**: Commits the value. Triggers `handleChange`.
* **`formatDisplayValue`**: Formats high-precision numbers for readability (e.g., scientific notation handling).
* **Visual Feedback**: Applies CSS classes (`computed-value`, `user-override`) based on the source of the data.

### Calc Type Rules
* When `calcType === 'Simulation'`, spec edits are disabled at the input level to prevent changing solver spec flags in simulation mode.


---


---

## 5.5 Input Origin Flags (`is_human_input`, `is_computed`)

This module relies on two flags to determine whether values can be overwritten by solver output and whether they should be highlighted in the UI.

**Key rules:**
- Defaults and system-generated values start with `is_human_input = false`.
- Any user edit (value/spec/unit/bounds) forces `is_human_input = true` and `is_computed = false`.
- Solver output only applies when `is_human_input !== true`.

For the full lifecycle and state machine, see:
- `docs/CodeExplanation/human-input-flag.md`

## 6. TP Changes (Spec/Bounds/Unit 覆盖)

**目的：** 让非 Base TP 的变更以稀疏覆盖的形式持久化到 `tp_changes`，并在 UI 与求解侧正确生效。

**核心文件：**
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/node-var-input.tsx`
- `src/src/backend/utils/translation.ts`
- `src/src/backend/utils/translationTpsSpecsUtils.ts`

**关键点：**
1. `NodeVarInput` 在非 Base TP 的 spec/units 变化时，会把事件交给 `NodeVarsTab` 统一保存。
2. `NodeVarsTab` 会将 `portVarValue/spec/lowerBound/upperBound/unit` 与基线逐项对比，任意字段不同即 Upsert，否则 Delete。
3. Upsert 时会回填必要的 `spec/unit`（即使未改），避免首次保存为 `null`。
4. Backend 在 `translation` 阶段将 `tp_changes` 注入 `ModelVersion`，最终进入 `tps_specs`。

详细流程见：`docs/CodeExplanation/tpChanges.md`

---


---

## 6. TP Changes (Spec/Bounds/Unit Overrides)

**Purpose:** Persist non-Base TP changes as sparse overrides in `tp_changes`, and ensure they appear correctly in both UI and solver inputs.

**Core files:**
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/node-var-input.tsx`
- `src/src/backend/utils/translation.ts`
- `src/src/backend/utils/translationTpsSpecsUtils.ts`

**Key points:**
1. `NodeVarInput` routes non-Base TP edits (spec/units/bounds/value) to `NodeVarsTab` for persistence.
2. `NodeVarsTab` diffs `portVarValue/spec/lowerBound/upperBound/unit` against baseline. Any diff → Upsert; no diff → Delete.
3. Upsert fills in missing `spec/unit` using baseline values to avoid nulls on first save.
4. Backend `translation` injects `tp_changes` into the final `ModelVersion`, which then propagates into `tps_specs`.

See details: `docs/CodeExplanation/tpChanges.md`
---

## Usage Example (Hierarchy)

```tsx
/* 1. SettingsTab initializes the context */
<SettingsTab>
  {/* 2. Prefetch hook loads data & merges overrides */}
  { useNodeDataPrefetch(...) }

  {/* 3. NodeVarsTab receives resolved model */}
  <NodeVarsTab 
    model={resolvedModel} 
    activeTimePeriodId={currentTP}
  >
    {/* 4. NodeVarInput renders individual fields */}
    { variables.map(v => (
        <NodeVarInput 
           value={v.value} 
           isBaseTP={currentTP === 1}
        />
    ))}
  </NodeVarsTab>
</SettingsTab>

```
