# User Tables Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the separate Materials and Economic header entries with a User Tables dropdown for base-period and Multi-TP table editors while preserving all existing editor, import, save, and persistence behavior.

**Architecture:** Add a pure option-model module and a focused `UserTablesMenu` React component. Extend `CostButtons` with a custom trigger renderer so the new menu can open the existing Economic panels without moving their state or data logic, then integrate base and Multi-TP instances into `HeaderBar`.

**Tech Stack:** React 18, TypeScript, React Bootstrap, Jest 29 with ts-jest, Vite 5.

## Global Constraints

- The menu order is exactly: `Material Properties`, `Cost and Revenue Data`, `Supply and Demand Data`.
- Base-period Material, Cost/Revenue, and Supply/Demand editors reuse their current implementations.
- Multi-TP Material Properties remains visible but disabled.
- Multi-TP Economic items remain unavailable until the graph is verified.
- Existing Economic modal titles, import/export formats, backend routes, Prisma schemas, storage contracts, base/Multi-TP save scopes, fast-save behavior, and computed-data-write behavior must not change.
- Existing unrelated worktree changes must not be staged or modified.

---

### Task 1: Define and test the User Tables option model

**Files:**
- Create: `src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu-options.ts`
- Test: `src/tests/frontend/userTablesMenuOptions.test.ts`

**Interfaces:**
- Produces: `UserTablesMode`, `UserTableMenuKey`, `UserTableMenuOption`, `getUserTableMenuOptions(options)`.
- `getUserTableMenuOptions` accepts `{ mode, materialDisabled, economicDisabled }` and returns the three ordered menu entries with final disabled states.

- [ ] **Step 1: Write the failing option-model tests**

```typescript
import { getUserTableMenuOptions } from '../../src/frontend/src/components/header-bar/header-buttons/user-tables-menu-options';

describe('User Tables menu options', () => {
  it('uses the confirmed labels in the confirmed order', () => {
    const options = getUserTableMenuOptions({
      mode: 'base',
      materialDisabled: false,
      economicDisabled: false,
    });

    expect(options.map(({ key, label }) => ({ key, label }))).toEqual([
      { key: 'materialProperties', label: 'Material Properties' },
      { key: 'costRevenue', label: 'Cost and Revenue Data' },
      { key: 'supplyDemand', label: 'Supply and Demand Data' },
    ]);
  });

  it('applies independent base-period disable rules', () => {
    expect(
      getUserTableMenuOptions({
        mode: 'base',
        materialDisabled: true,
        economicDisabled: false,
      }).map(({ disabled }) => disabled)
    ).toEqual([true, false, false]);

    expect(
      getUserTableMenuOptions({
        mode: 'base',
        materialDisabled: false,
        economicDisabled: true,
      }).map(({ disabled }) => disabled)
    ).toEqual([false, true, true]);
  });

  it('always disables Material Properties in Multi-TP mode', () => {
    expect(
      getUserTableMenuOptions({
        mode: 'mtp',
        materialDisabled: false,
        economicDisabled: false,
      }).map(({ disabled }) => disabled)
    ).toEqual([true, false, false]);
  });
});
```

- [ ] **Step 2: Run the test and verify RED**

Run from `src/`:

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/userTablesMenuOptions.test.ts --forceExit
```

Expected: FAIL because `user-tables-menu-options.ts` does not exist.

- [ ] **Step 3: Implement the option model**

```typescript
export type UserTablesMode = 'base' | 'mtp';

export type UserTableMenuKey =
  | 'materialProperties'
  | 'costRevenue'
  | 'supplyDemand';

export interface UserTableMenuOption {
  key: UserTableMenuKey;
  label: string;
  disabled: boolean;
}

interface GetUserTableMenuOptionsArgs {
  mode: UserTablesMode;
  materialDisabled: boolean;
  economicDisabled: boolean;
}

export const getUserTableMenuOptions = ({
  mode,
  materialDisabled,
  economicDisabled,
}: GetUserTableMenuOptionsArgs): UserTableMenuOption[] => [
  {
    key: 'materialProperties',
    label: 'Material Properties',
    disabled: mode === 'mtp' || materialDisabled,
  },
  {
    key: 'costRevenue',
    label: 'Cost and Revenue Data',
    disabled: economicDisabled,
  },
  {
    key: 'supplyDemand',
    label: 'Supply and Demand Data',
    disabled: economicDisabled,
  },
];
```

- [ ] **Step 4: Run the test and verify GREEN**

Run the Step 2 command again.

Expected: PASS, 3 tests passed.

- [ ] **Step 5: Commit the tested option model**

```powershell
git add -- src/tests/frontend/userTablesMenuOptions.test.ts src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu-options.ts
git commit -m "feat: define User Tables menu options"
```

---

### Task 2: Add a custom Economic trigger interface

**Files:**
- Modify: `src/src/frontend/src/components/header-bar/header-buttons/cost-button.tsx:47-52,188-193,1681-1720`
- Test: `src/tests/frontend/costButtonCustomTrigger.test.ts`

**Interfaces:**
- Produces: exported `EconomicPanelOpener = (panelType: EconomicPanelType) => void`.
- Extends `CostButtonsProps` with `renderTrigger?: (openPanel: EconomicPanelOpener) => React.ReactNode`.
- Preserves existing `buttons` and `dropdown` trigger behavior when `renderTrigger` is absent.

- [ ] **Step 1: Write the failing custom-trigger contract test**

```typescript
import fs from 'fs';
import path from 'path';

describe('CostButtons custom trigger contract', () => {
  it('exposes the existing panel opener without replacing legacy triggers', () => {
    const source = fs.readFileSync(
      path.resolve(
        __dirname,
        '../../src/frontend/src/components/header-bar/header-buttons/cost-button.tsx'
      ),
      'utf8'
    );

    expect(source).toContain(
      'export type EconomicPanelOpener = (panelType: EconomicPanelType) => void;'
    );
    expect(source).toContain(
      'renderTrigger?: (openPanel: EconomicPanelOpener) => React.ReactNode;'
    );
    expect(source).toContain('renderTrigger ? renderTrigger(openPanel)');
    expect(source).toContain("triggerMode === 'dropdown'");
  });
});
```

- [ ] **Step 2: Run the test and verify RED**

Run from `src/`:

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/costButtonCustomTrigger.test.ts --forceExit
```

Expected: FAIL because the custom trigger contract is absent.

- [ ] **Step 3: Add the custom trigger prop**

Add the exported type and prop immediately before/inside `CostButtonsProps`:

```typescript
export type EconomicPanelOpener = (panelType: EconomicPanelType) => void;

interface CostButtonsProps {
  readOnly?: boolean;
  showTpRanges?: boolean;
  triggerMode?: 'buttons' | 'dropdown';
  dropdownLabel?: string;
  renderTrigger?: (openPanel: EconomicPanelOpener) => React.ReactNode;
}
```

Destructure the new prop:

```typescript
const CostButton: React.FC<CostButtonsProps> = ({
  readOnly = false,
  showTpRanges = false,
  triggerMode = 'buttons',
  dropdownLabel = 'Economic',
  renderTrigger,
}) => {
```

Wrap the existing trigger expression without changing either legacy branch:

```tsx
{renderTrigger ? renderTrigger(openPanel) : triggerMode === 'dropdown' ? (
  <Dropdown onSelect={(eventKey) => openPanel(eventKey as EconomicPanelType | null)}>
    <Dropdown.Toggle
      variant="outline-primary"
      id="economic-dropdown"
      disabled={readOnly}
      className="text-nowrap"
    >
      {dropdownLabel}
    </Dropdown.Toggle>
    <Dropdown.Menu>
      {ECONOMIC_PANEL_OPTIONS.map((option) => (
        <Dropdown.Item
          key={option.key}
          eventKey={option.key}
        >
          {option.title}
        </Dropdown.Item>
      ))}
    </Dropdown.Menu>
  </Dropdown>
) : (
  ECONOMIC_PANEL_OPTIONS.map((option) => (
    <Button
      key={option.key}
      type="button"
      variant="outline-primary"
      onClick={(event) => {
        event.currentTarget.blur();
        openPanel(option.key);
      }}
      disabled={readOnly}
      className="text-nowrap"
    >
      {option.title}
    </Button>
  ))
)}
```

- [ ] **Step 4: Run focused verification and verify GREEN**

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/costButtonCustomTrigger.test.ts tests/frontend/costButtonUtils.test.ts --forceExit
```

Expected: PASS for both suites.

- [ ] **Step 5: Commit the custom trigger**

```powershell
git add -- src/tests/frontend/costButtonCustomTrigger.test.ts src/src/frontend/src/components/header-bar/header-buttons/cost-button.tsx
git commit -m "feat: support custom Economic panel triggers"
```

---

### Task 3: Build the focused User Tables dropdown component

**Files:**
- Create: `src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu.tsx`
- Test: `src/tests/frontend/userTablesMenuComponent.test.ts`

**Interfaces:**
- Consumes: `getUserTableMenuOptions`, `UserTablesMode`, `EconomicPanelOpener`.
- Produces: default `UserTablesMenu` component with props `{ mode, materialDisabled, economicDisabled, onOpenMaterialProperties }`.
- Routes `costRevenue` to Economic panel `cost` and `supplyDemand` to `demandSupply`.

- [ ] **Step 1: Write the failing component integration test**

```typescript
import fs from 'fs';
import path from 'path';

describe('UserTablesMenu component', () => {
  it('routes the three menu entries through existing editors', () => {
    const componentPath = path.resolve(
      __dirname,
      '../../src/frontend/src/components/header-bar/header-buttons/user-tables-menu.tsx'
    );

    expect(fs.existsSync(componentPath)).toBe(true);

    const source = fs.readFileSync(componentPath, 'utf8');
    expect(source).toContain("costRevenue: 'cost'");
    expect(source).toContain("supplyDemand: 'demandSupply'");
    expect(source).toContain('onOpenMaterialProperties();');
    expect(source).toContain('openEconomicPanel(economicPanel);');
    expect(source).toContain('disabled={option.disabled}');
    expect(source).toContain('renderTrigger={(openEconomicPanel) =>');
  });
});
```

- [ ] **Step 2: Run the test and verify RED**

Run from `src/`:

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/userTablesMenuComponent.test.ts --forceExit
```

Expected: FAIL because `user-tables-menu.tsx` does not exist.

- [ ] **Step 3: Implement `UserTablesMenu`**

```tsx
import React from 'react';
import { Dropdown } from 'react-bootstrap';
import CostButtons from './cost-button';
import type { EconomicPanelType } from './cost-button-utils';
import {
  getUserTableMenuOptions,
  type UserTableMenuKey,
  type UserTablesMode,
} from './user-tables-menu-options';

interface UserTablesMenuProps {
  mode: UserTablesMode;
  materialDisabled: boolean;
  economicDisabled: boolean;
  onOpenMaterialProperties: () => void;
}

const ECONOMIC_PANEL_BY_KEY: Partial<
  Record<UserTableMenuKey, EconomicPanelType>
> = {
  costRevenue: 'cost',
  supplyDemand: 'demandSupply',
};

const UserTablesMenu: React.FC<UserTablesMenuProps> = ({
  mode,
  materialDisabled,
  economicDisabled,
  onOpenMaterialProperties,
}) => {
  const options = getUserTableMenuOptions({
    mode,
    materialDisabled,
    economicDisabled,
  });

  return (
    <CostButtons
      readOnly={economicDisabled}
      showTpRanges={mode === 'mtp'}
      renderTrigger={(openEconomicPanel) => (
        <Dropdown
          onSelect={(eventKey) => {
            const option = options.find(({ key }) => key === eventKey);
            if (!option || option.disabled) {
              return;
            }
            if (option.key === 'materialProperties') {
              onOpenMaterialProperties();
              return;
            }
            const economicPanel = ECONOMIC_PANEL_BY_KEY[option.key];
            if (economicPanel) {
              openEconomicPanel(economicPanel);
            }
          }}
        >
          <Dropdown.Toggle
            variant="outline-primary"
            id={`user-tables-${mode}-dropdown`}
            className="text-nowrap"
          >
            User Tables
          </Dropdown.Toggle>
          <Dropdown.Menu>
            {options.map((option) => (
              <Dropdown.Item
                key={option.key}
                eventKey={option.key}
                disabled={option.disabled}
              >
                {option.label}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      )}
    />
  );
};

export default UserTablesMenu;
```

- [ ] **Step 4: Run focused tests and verify GREEN**

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/userTablesMenuOptions.test.ts tests/frontend/costButtonCustomTrigger.test.ts tests/frontend/userTablesMenuComponent.test.ts --forceExit
```

Expected: PASS, 3 suites passed.

- [ ] **Step 5: Commit the component**

```powershell
git add -- src/tests/frontend/userTablesMenuComponent.test.ts src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu.tsx
git commit -m "feat: add User Tables dropdown"
```

---

### Task 4: Replace the header entries and preserve Multi-TP gating

**Files:**
- Modify: `src/src/frontend/src/components/header-bar/index.tsx:14,31,68-71,86-100,190-259,294-326,421-465`
- Modify: `src/tests/frontend/headerBarEconomicAvailability.test.ts:4-22`
- Create: `src/tests/frontend/headerBarUserTablesIntegration.test.ts`
- Delete: `src/src/frontend/src/components/header-bar/header-buttons/material-editor.tsx`

**Interfaces:**
- Consumes: `UserTablesMenu` and the existing `setMaterialEditor` callback.
- Produces: base User Tables top-level dropdown and Multi-TP User Tables secondary dropdown.
- Preserves: `ruleCostButtons || !verified` gating for Multi-TP Economic items.

- [ ] **Step 1: Write the failing header integration tests**

Create `headerBarUserTablesIntegration.test.ts`:

```typescript
import fs from 'fs';
import path from 'path';

describe('HeaderBar User Tables integration', () => {
  const headerSource = fs.readFileSync(
    path.resolve(__dirname, '../../src/frontend/src/components/header-bar/index.tsx'),
    'utf8'
  );

  it('replaces the top-level Materials and Economic sections', () => {
    expect(headerSource).toContain(
      "import UserTablesMenu from './header-buttons/user-tables-menu.tsx';"
    );
    expect(headerSource).toContain('mode="base"');
    expect(headerSource).not.toContain("activeSection === 'Materials'");
    expect(headerSource).not.toContain("activeSection === 'Economic'");
    expect(headerSource).not.toContain(
      "import MaterialEditor from './header-buttons/material-editor.tsx';"
    );
  });

  it('uses User Tables with per-item Multi-TP availability', () => {
    const multiTpBlock = headerSource.slice(
      headerSource.indexOf("activeSection === 'Multi-TP'"),
      headerSource.indexOf("activeSection === 'TP Analysis'")
    );

    expect(multiTpBlock).toContain('<UserTablesMenu');
    expect(multiTpBlock).toContain('mode="mtp"');
    expect(multiTpBlock).toContain('materialDisabled');
    expect(multiTpBlock).toContain(
      'economicDisabled={ruleCostButtons || !verified}'
    );
    expect(multiTpBlock).not.toContain('dropdownLabel="Economic"');
  });
});
```

Update `headerBarEconomicAvailability.test.ts` so the first test expects the new gating prop:

```typescript
expect(headerSource).toContain(
  'economicDisabled={ruleCostButtons || !verified}'
);
```

Remove its obsolete expectation for `readOnly={ruleCostButtons || !verified}` and retain the dimension-metadata test unchanged.

- [ ] **Step 2: Run the tests and verify RED**

Run from `src/`:

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/headerBarUserTablesIntegration.test.ts tests/frontend/headerBarEconomicAvailability.test.ts --forceExit
```

Expected: FAIL because `HeaderBar` still renders Materials/Economic and the old Multi-TP Economic dropdown.

- [ ] **Step 3: Integrate the new component into `HeaderBar`**

Replace the direct Cost/Material button imports with:

```typescript
import UserTablesMenu from './header-buttons/user-tables-menu.tsx';
```

Change the indexed section list to remove obsolete entries:

```typescript
const mainSections = [
  'Model', 'Calc Type', 'Analysis', 'Set Run',
  'Multi-TP', 'TP Analysis', 'System', 'Help'
];
```

Add the Material disable rule alongside the existing Cost rule:

```typescript
const ruleMaterialEditor = useComputingDisableRule("Materials.MaterialEditor");
const ruleCostButtons = useComputingDisableRule("Costs.CostButtons");
```

Render the base dropdown between Model and Save:

```tsx
{mainSections.slice(0, 1).map((section) => (
  <Button
    key={section}
    variant={activeSection === section ? 'deepblue' : 'outline-primary'}
    onClick={() => setActiveSection(section)}
    className="text-nowrap"
  >
    {section}
  </Button>
))}
<UserTablesMenu
  mode="base"
  materialDisabled={ruleMaterialEditor}
  economicDisabled={ruleCostButtons}
  onOpenMaterialProperties={() => setMaterialEditor(true)}
/>
<SaveAndRestore disabled={ruleSaveOperations}></SaveAndRestore>
{mainSections.slice(1, 3).map((section) => (
  <Button
    key={section}
    variant={activeSection === section ? 'deepblue' : 'outline-primary'}
    onClick={() => setActiveSection(section)}
    className="text-nowrap"
  >
    {section}
  </Button>
))}
```

Update the other indexed groups to match the new list:

```tsx
{mainSections.slice(3, 4).map((section) => (
  <Button
    key={section}
    variant={activeSection === section ? 'deepblue' : 'outline-primary'}
    onClick={() => setActiveSection(section)}
    className="text-nowrap"
  >
    {section}
  </Button>
))}

{mainSections.slice(4, 7).map((section) => (
  <Button
    key={section}
    variant={activeSection === section ? 'deepblue' : 'outline-primary'}
    onClick={() => setActiveSection(section)}
    className="text-nowrap"
  >
    {section}
  </Button>
))}

{mainSections.slice(7).map((section) => (
  <Button
    key={section}
    variant={activeSection === section ? 'deepblue' : 'outline-primary'}
    onClick={() => setActiveSection(section)}
    className="text-nowrap"
  >
    {section}
  </Button>
))}
```

Delete the obsolete `activeSection === 'Materials'` and `activeSection === 'Economic'` secondary-toolbar blocks.

Replace the Multi-TP `CostButtons` instance with:

```tsx
<UserTablesMenu
  mode="mtp"
  materialDisabled
  economicDisabled={ruleCostButtons || !verified}
  onOpenMaterialProperties={() => setMaterialEditor(true)}
/>
```

Delete the now-unused `header-buttons/material-editor.tsx` wrapper. Do not modify the full Material Editor mounted in `App.tsx`.

- [ ] **Step 4: Run focused tests and verify GREEN**

```powershell
npx jest --runInBand --runTestsByPath tests/frontend/headerBarUserTablesIntegration.test.ts tests/frontend/headerBarEconomicAvailability.test.ts tests/frontend/userTablesMenuOptions.test.ts tests/frontend/costButtonCustomTrigger.test.ts tests/frontend/userTablesMenuComponent.test.ts tests/frontend/costButtonUtils.test.ts --forceExit
```

Expected: PASS, 6 suites passed.

- [ ] **Step 5: Run the frontend build**

Run from `src/src/frontend/`:

```powershell
npm run build
```

Expected: TypeScript project build and Vite production build exit with code 0.

- [ ] **Step 6: Commit the header integration**

```powershell
git add -- src/tests/frontend/headerBarUserTablesIntegration.test.ts src/tests/frontend/headerBarEconomicAvailability.test.ts src/src/frontend/src/components/header-bar/index.tsx src/src/frontend/src/components/header-bar/header-buttons/material-editor.tsx
git commit -m "feat: replace Materials and Economic with User Tables"
```

---

### Task 5: Final regression and scope verification

**Files:**
- Verify only; no planned production edits.

**Interfaces:**
- Confirms the complete feature contract and protects existing Economic helper, save-scope, and frontend compilation behavior.

- [ ] **Step 1: Run all relevant frontend Jest tests**

Run from `src/`:

```powershell
npx jest --runInBand --testPathPattern="tests/frontend" --forceExit
```

Expected: all frontend suites pass. If an unrelated pre-existing test fails, record the exact suite and error instead of modifying unrelated code.

- [ ] **Step 2: Run the production frontend build again**

Run from `src/src/frontend/`:

```powershell
npm run build
```

Expected: exit code 0.

- [ ] **Step 3: Inspect scope and protected paths**

Run from the repository root:

```powershell
git status --short
git diff --check 679651c^..HEAD
git diff --stat 679651c^..HEAD
git diff 679651c^..HEAD -- src/src/frontend/src/components/header-bar src/tests/frontend
```

Confirm:

- no backend, Prisma, import-format, save utility, or computed-data-write file changed;
- unrelated dirty-worktree files remain unstaged and unmodified by this feature;
- no debug logging or temporary code remains;
- the implementation commits contain only the design, plan, User Tables code, and focused tests.

- [ ] **Step 4: Record the verified result**

Report the exact test-suite count, build exit status, commit range, changed files, and any residual manual UI verification requirement.
