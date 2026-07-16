# Save and Auto Refresh Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the oversized combined Save/checkbox button with a compact, accessible two-segment Save and Auto refresh control.

**Architecture:** Keep the current `SaveAndRestore` state, local-storage key, and `useSaveDiagram` integration. Change only the rendered controls and their header-scoped CSS, with a source-contract Jest test that protects the separate-button semantics and selected visual states.

**Tech Stack:** React 18, TypeScript, React Bootstrap, react-bootstrap-icons, CSS, Jest/ts-jest

## Global Constraints

- Do not change the `save_auto_reload_enabled` local-storage key or its default value of `true`.
- Do not change `useSaveDiagram(false, autoReloadEnabled)` or the existing save behavior.
- Render Save and Auto refresh as two separate native buttons with no nested interactive elements.
- Do not push the branch to GitHub.
- Preserve all unrelated working-tree changes and stage only files named in this plan.

---

## File structure

- `src/tests/frontend/saveAndRestoreControl.test.ts`: source-contract coverage for separate actions, accessibility state, icon/status UI, and removal of the checkbox pattern.
- `src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx`: keeps persistence and save behavior while rendering the connected two-button group.
- `src/src/frontend/src/components/header-bar/header-bar.css`: owns the connected border, segment states, status dot, hover/focus behavior, and responsive sizing.

### Task 1: Connected Save and Auto refresh control

**Files:**
- Create: `src/tests/frontend/saveAndRestoreControl.test.ts`
- Modify: `src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx`
- Modify: `src/src/frontend/src/components/header-bar/header-bar.css`

**Interfaces:**
- Consumes: `useSaveDiagram(false, autoReloadEnabled)`, `Button` from `react-bootstrap`, `ArrowRepeat` from `react-bootstrap-icons`, and local storage key `save_auto_reload_enabled`.
- Produces: a `role="group"` control containing `.save-control-save-button` and `.save-auto-refresh-button`; the second button exposes `aria-pressed={autoReloadEnabled}` and toggles the existing boolean state.

- [x] **Step 1: Write the failing source-contract test**

Create `src/tests/frontend/saveAndRestoreControl.test.ts`:

```ts
import fs from 'fs';
import path from 'path';

describe('SaveAndRestore connected control', () => {
  const componentSource = fs.readFileSync(
    path.resolve(
      __dirname,
      '../../src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx'
    ),
    'utf8'
  );
  const cssSource = fs.readFileSync(
    path.resolve(__dirname, '../../src/frontend/src/components/header-bar/header-bar.css'),
    'utf8'
  );

  it('renders separate Save and Auto refresh buttons without a nested checkbox', () => {
    expect(componentSource.match(/<Button\b/g) ?? []).toHaveLength(2);
    expect(componentSource).toContain("className='save-control-segment save-control-save-button'");
    expect(componentSource).toContain('save-auto-refresh-button');
    expect(componentSource).toContain('Auto refresh');
    expect(componentSource).not.toContain("type='checkbox'");
    expect(componentSource).not.toContain('<label');
  });

  it('exposes and toggles the auto-refresh pressed state', () => {
    expect(componentSource).toContain('aria-pressed={autoReloadEnabled}');
    expect(componentSource).toContain(
      'onClick={() => setAutoReloadEnabled((enabled) => !enabled)}'
    );
    expect(componentSource).toContain("const SAVE_AUTO_RELOAD_KEY = 'save_auto_reload_enabled'");
    expect(componentSource).toContain('useSaveDiagram(false, autoReloadEnabled)');
  });

  it('styles enabled and disabled refresh states within one connected group', () => {
    expect(cssSource).toContain('.save-control-container:focus-within');
    expect(cssSource).toContain('.save-auto-refresh-button.is-enabled');
    expect(cssSource).toContain('.save-auto-refresh-button.is-disabled');
    expect(cssSource).toContain('.save-auto-refresh-status');
  });
});
```

- [x] **Step 2: Run the focused test and verify RED**

Run from `src/`:

```powershell
npx jest tests/frontend/saveAndRestoreControl.test.ts --runInBand --coverage=false
```

Expected: FAIL because the current component renders one `Button`, a nested checkbox/label, and none of the new segment classes.

- [x] **Step 3: Replace the nested checkbox with two button segments**

Replace `save-and-restore.tsx` with:

```tsx
import { useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';
import { ArrowRepeat } from 'react-bootstrap-icons';
import { useSaveDiagram } from '../utils/save-util.tsx';

interface SaveAndRestoreProps {
  disabled?: boolean;
}

const SAVE_AUTO_RELOAD_KEY = 'save_auto_reload_enabled';

const readAutoReloadPreference = (): boolean => {
  try {
    const storedPreference = localStorage.getItem(SAVE_AUTO_RELOAD_KEY);
    if (storedPreference === null) {
      return true;
    }
    return storedPreference === 'true';
  } catch (error) {
    console.warn('[Save]Failed to read save auto-reload preference:', error);
    return true;
  }
};

export default function SaveAndRestore({ disabled = false }: SaveAndRestoreProps) {
  const [autoReloadEnabled, setAutoReloadEnabled] = useState<boolean>(readAutoReloadPreference);
  const onSave = useSaveDiagram(false, autoReloadEnabled);

  useEffect(() => {
    try {
      localStorage.setItem(SAVE_AUTO_RELOAD_KEY, String(autoReloadEnabled));
    } catch (error) {
      console.warn('[Save]Failed to persist save auto-reload preference:', error);
    }
  }, [autoReloadEnabled]);

  const handleSave = async () => {
    if (disabled) return;

    await onSave();
  };

  const autoRefreshStateLabel = autoReloadEnabled ? 'on' : 'off';

  return (
    <div
      className='button-container save-control-container'
      role='group'
      aria-label='Save and auto refresh'
    >
      <Button
        onClick={handleSave}
        disabled={disabled}
        variant='outline-primary'
        className='save-control-segment save-control-save-button'
      >
        Save
      </Button>
      <Button
        onClick={() => setAutoReloadEnabled((enabled) => !enabled)}
        disabled={disabled}
        variant='outline-primary'
        className={`save-control-segment save-auto-refresh-button ${
          autoReloadEnabled ? 'is-enabled' : 'is-disabled'
        }`}
        aria-pressed={autoReloadEnabled}
        aria-label={`Auto refresh ${autoRefreshStateLabel}`}
        title={`Auto refresh is ${autoRefreshStateLabel}`}
      >
        <ArrowRepeat className='save-auto-refresh-icon' aria-hidden='true' />
        <span>Auto refresh</span>
        <span className='save-auto-refresh-status' aria-hidden='true' />
      </Button>
    </div>
  );
}
```

- [x] **Step 4: Replace the old checkbox styles with connected-control styles**

In `header-bar.css`, remove the rules for `.save-button-inline-toggle`, `.save-button-label`, `.save-reload-toggle`, and its checkbox/span descendants. Keep `.save-control-container`, but replace its body and add:

```css
.save-control-container {
  display: inline-flex;
  align-items: stretch;
  gap: 0;
  overflow: hidden;
  border: 1px solid #003366;
  border-radius: 6px;
  background-color: #ffffff;
  box-shadow: 0 1px 2px rgba(0, 51, 102, 0.08);
}

.save-control-container:focus-within {
  box-shadow: 0 0 0 2px rgba(0, 51, 102, 0.22);
}

.header-navbar .save-control-segment {
  margin: 0;
  border: 0 !important;
  border-radius: 0 !important;
  transform: none !important;
}

.header-navbar .save-control-segment + .save-control-segment {
  border-left: 1px solid #a9bfd3 !important;
}

.header-navbar .save-auto-refresh-button {
  gap: 0.4rem;
}

.header-navbar .save-auto-refresh-button.is-enabled {
  background-color: #eaf2f8 !important;
  color: #003366 !important;
}

.header-navbar .save-auto-refresh-button.is-disabled {
  background-color: #ffffff !important;
  color: #52697d !important;
}

.header-navbar .save-control-segment:hover:not(:disabled),
.header-navbar .save-control-segment:focus-visible {
  background-color: #001f3f !important;
  color: #ffffff !important;
}

.header-navbar .save-control-segment:disabled {
  background-color: #f0f0f0 !important;
  color: #6c757d !important;
  opacity: 0.7;
}

.save-auto-refresh-icon {
  width: 14px !important;
  height: 14px !important;
  flex: 0 0 auto;
}

.save-auto-refresh-status {
  width: 7px;
  height: 7px;
  flex: 0 0 auto;
  border-radius: 50%;
  background-color: #95a1ac;
}

.save-auto-refresh-button.is-enabled .save-auto-refresh-status {
  background-color: #23845c;
  box-shadow: 0 0 0 3px rgba(35, 132, 92, 0.12);
}

@media (max-width: 992px) {
  .header-navbar .save-control-container,
  .header-navbar .save-control-container .save-control-segment {
    width: auto;
  }
}
```

- [x] **Step 5: Run the focused tests and verify GREEN**

Run from `src/`:

```powershell
npx jest tests/frontend/saveAndRestoreControl.test.ts tests/frontend/headerBarSavePlacement.test.ts --runInBand --coverage=false
```

Expected: 2 suites pass; the connected-control suite has 3 passing tests and the placement suite remains green.

- [x] **Step 6: Run targeted lint and the production build**

Run from `src/src/frontend/`:

```powershell
npx eslint src/components/header-bar/header-buttons/save-and-restore.tsx
npm run build
```

Expected: ESLint exits 0; TypeScript and Vite production build exit 0.

Actual baseline note: targeted ESLint and `npx vite build` pass. The repository's existing `tsc -b` project build remains blocked by pre-existing TypeScript and project-reference errors; `npx tsc -p tsconfig.app.json --noEmit --pretty false` reports no error for `save-and-restore.tsx`.

- [x] **Step 7: Verify the real header visually**

Open the running frontend, confirm the connected control matches the approved direction, click only the Auto refresh segment, and verify:

- the status dot and background change without triggering Save;
- the stored value for `save_auto_reload_enabled` changes between `true` and `false`;
- Save remains independently clickable;
- both segments show visible keyboard focus;
- the control stays aligned with Canvas Name and neighboring header controls.

- [x] **Step 8: Commit only the implementation files**

```powershell
git add -- src/tests/frontend/saveAndRestoreControl.test.ts src/src/frontend/src/components/header-bar/header-buttons/save-and-restore.tsx src/src/frontend/src/components/header-bar/header-bar.css
git diff --cached --check
git commit -m "feat: redesign save auto-refresh control"
```
