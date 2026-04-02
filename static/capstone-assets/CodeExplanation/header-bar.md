# Header Bar

## Overview
- Location: `src/src/frontend/src/components/header-bar/index.tsx`
- Purpose: Top-level navigation and action bar for the React Flow canvas, organized into primary sections with contextual secondary controls (including Run Result history access).
- Dependencies: React-Bootstrap (`Navbar`, `Button`, `Dropdown`), Redux selectors (`RootState`), and multiple child button components (run/config/save/model actions).

## Props (inputs/outputs)
- `setMaterialEditor: Dispatch<SetStateAction<boolean>>` — required; toggles the material editor modal; returns void.
- `setSaveConfirm: Dispatch<SetStateAction<boolean>>` — required; opens/closes the save-confirm modal before leaving; returns void.

## Core State
- `activeSection: string | null` — drives which secondary row is visible; defaults to `Model`.
- `showRunConfigModal: boolean` / `selectedRunConfigType: string | null` — governs the shared Run Config modal.
- `runConfigs` — read from Redux `domain.data.runConfigs`; maps solver/algorithm keys to config definitions.
- `calcType` — active calculation mode (`Simulation`, `Optimization`, `DataRec`, `ParamUpdt`) from Redux.
- Disable flags from `useComputingDisableRule` gate many buttons while computations run.

## Core Functions
- `handleOpenRunConfig(type: string)` — param: solver/algorithm key; return: void; opens modal and stores selected key.
- `handleCloseRunConfig()` — return: void; hides run-config modal and clears selection.
- `handleCalcTypeClick(nextCalcType)` — confirms switching calc type; if same type, opens TP Specs directly.
- `handleConfirmCalcTypeSwitch()` — updates Redux `calcType` and opens TP Specs panel.
- `setActiveSection(section)` — param: section label; return: void; switches visible secondary button group.
- Rendering pipeline returns a `Navbar` with two button rows: primary row (all sections + core actions) and secondary row (contextual actions based on `activeSection`).

## Section Behavior (secondary row)
- `Model`: create/open/import/export diagram, save as copy/subnetwork, verify, TP specs.
- `Materials`: opens `MaterialEditor`; view/import material placeholders.
- `Calc Type`: renders 4 buttons (Simulation / Optimization / DataRec / ParamUpdt). Clicking opens a confirmation modal if switching types.
- `Set Run`: solver/algorithm dropdowns populated from `runConfigs`; selecting triggers `handleOpenRunConfig` and shows `RunConfigModal`.
- `Run`: `ComputationButton` handles start/stop and exposes a display-only RunConfig modal. `Run Result` opens a history modal for prior runs, with delete actions for stored results.
- `Multi-Time Period`: `TimePeriodViewer` (TP Node - Model Version Control) and `Global TP` for bulk time-period assignment; both are only visible after the diagram is verified. TP specs/data remain placeholders.
- `Advanced Analysis`: `MetabaseButton`, Configure/Edit stubs.
- `System`: import sys materials and node definitions (respect disable rules).
- `Help`: documentation/tutorial placeholders.

## Usage
```tsx
<HeaderBar
  setMaterialEditor={setMaterialEditorOpen}
  setSaveConfirm={setSaveConfirmOpen}
/>
```

## Notes
- Styling in `header-bar.css`; many child buttons have their own styles.
- Disable rules from `useComputingDisableRule` should align with backend policy so UI and allowed actions stay consistent.
- Logging of run configs is present for debugging; remove or guard for production.
- `BackToParentNetwork` now uses the same `outline-primary` color scheme as the main menu buttons for visual consistency.

## Run Result History

Run history and deletion are surfaced via the `Run Result` button in the primary row, next to `Run`.

Key files:
- `src/src/frontend/src/components/header-bar/header-buttons/run-result-button.tsx`
- `src/src/backend/routes/computeRoutes.ts`

Behavior:
1. Clicking `Run Result` fetches `/api/compute/history/:diagramId` and shows a modal table.
2. Each row displays `runName`, `status`, and `runAt` (start time if present, else creation time).
3. Delete triggers `/api/compute/results` and removes both PostgreSQL `ComputationResults` and MongoDB `computationTask` entries, then closes the modal.
