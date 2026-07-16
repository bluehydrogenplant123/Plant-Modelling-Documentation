# Remove Duplicate Header Save Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the left-hand duplicate `SaveAndRestore` render while preserving the right-side Save control and all existing save behavior.

**Architecture:** Keep the existing `SaveAndRestore` component and save pipeline unchanged. Add a focused source-level HeaderBar regression test, then remove only the older JSX instance from the main navigation group.

**Tech Stack:** React, TypeScript, Jest, ESLint

## Global Constraints

- Keep the right-side `SaveAndRestore` inside `header-toolbar-meta-actions` beside `CanvasNameEdit`.
- Preserve the `Refresh On/Off` toggle and the existing `ruleSaveOperations` disabled state.
- Do not modify save timing, fast-save behavior, computed-data writes, persistence, navigation, CSS, backend routes, or dependencies.
- Preserve all unrelated dirty-worktree files and do not upload or push the branch.

---

### Task 1: Remove the duplicate HeaderBar Save render

**Files:**
- Create: `src/tests/frontend/headerBarSavePlacement.test.ts`
- Modify: `src/src/frontend/src/components/header-bar/index.tsx:204-211`

**Interfaces:**
- Consumes: the `HeaderBar` source and its existing `SaveAndRestore` JSX component.
- Produces: exactly one `<SaveAndRestore>` render, retained inside `header-toolbar-meta-actions` with `disabled={ruleSaveOperations}`.

- [ ] **Step 1: Write the failing regression test**

Create `src/tests/frontend/headerBarSavePlacement.test.ts`:

```ts
import fs from 'fs';
import path from 'path';

describe('HeaderBar Save placement', () => {
  const headerSource = fs.readFileSync(
    path.resolve(__dirname, '../../src/frontend/src/components/header-bar/index.tsx'),
    'utf8'
  );

  it('renders SaveAndRestore once in the right-side meta actions', () => {
    const saveInstances = headerSource.match(/<SaveAndRestore\b/g) ?? [];
    const metaActionsStart = headerSource.indexOf(
      '<div className="header-toolbar-group header-toolbar-meta-actions">'
    );
    const metaActionsEnd = headerSource.indexOf('</div>', metaActionsStart);
    const metaActionsSource = headerSource.slice(metaActionsStart, metaActionsEnd);

    expect(saveInstances).toHaveLength(1);
    expect(metaActionsStart).toBeGreaterThan(-1);
    expect(metaActionsSource).toContain(
      '<SaveAndRestore disabled={ruleSaveOperations}></SaveAndRestore>'
    );
  });
});
```

- [ ] **Step 2: Run the test and verify the RED state**

Run from `src/`:

```powershell
npx jest tests/frontend/headerBarSavePlacement.test.ts --runInBand
```

Expected: FAIL because `saveInstances` has length `2` instead of `1`.

- [ ] **Step 3: Remove only the left-side JSX instance**

In `src/src/frontend/src/components/header-bar/index.tsx`, remove this line immediately after the base-period `UserTablesMenu`:

```tsx
<SaveAndRestore disabled={ruleSaveOperations}></SaveAndRestore>
```

Keep the `SaveAndRestore` import and the identical JSX instance inside `header-toolbar-meta-actions`.

- [ ] **Step 4: Run the focused tests and verify the GREEN state**

Run from `src/`:

```powershell
npx jest tests/frontend/headerBarSavePlacement.test.ts tests/frontend/headerBarUserTablesIntegration.test.ts --runInBand
```

Expected: PASS with `2` suites, `3` tests, and `0` failures.

- [ ] **Step 5: Run focused lint**

Run from `src/`:

```powershell
npx eslint src/frontend/src/components/header-bar/index.tsx tests/frontend/headerBarSavePlacement.test.ts
```

Expected: exit code `0` with no errors.

- [ ] **Step 6: Audit the final diff and protected paths**

Run from the repository root:

```powershell
git add -N -- src/tests/frontend/headerBarSavePlacement.test.ts
git diff --check -- src/src/frontend/src/components/header-bar/index.tsx src/tests/frontend/headerBarSavePlacement.test.ts
git diff -- src/src/frontend/src/components/header-bar/index.tsx src/tests/frontend/headerBarSavePlacement.test.ts
git status --short
```

Expected: the implementation diff contains only the new focused test and removal of the left-side `SaveAndRestore` line. Pre-existing dirty files remain unchanged and unstaged.

- [ ] **Step 7: Commit the implementation explicitly**

```powershell
git add -- src/src/frontend/src/components/header-bar/index.tsx src/tests/frontend/headerBarSavePlacement.test.ts
git commit -m "fix: remove duplicate header Save"
```
