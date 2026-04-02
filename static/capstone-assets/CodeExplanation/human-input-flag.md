# Input Origin Flags (`is_human_input`, `is_computed`)

## Overview
These two flags drive how values are interpreted, updated, and highlighted across the app.

- `is_human_input` = **who owns the value** (user vs system)
- `is_computed` = **whether the UI should highlight it as computed**

This is the inverse of the old `is_machine_generated` field.

---

## Definitions

**`is_human_input`** (solver payload + UI semantics)
- `true`: value was manually set or edited by the user
- `false`: value is system-generated (defaults, stream-derived, or solver output)

**`is_computed`** (UI highlight only)
- `true`: show computed highlight
- `false`: do not highlight

---

## Lifecycle (State Machine)

Initial state (system default, not computed):
- `is_human_input = false`
- `is_computed = false`

After solver computation (only for non-human inputs):
- `is_human_input = false`
- `is_computed = true`

After any user edit (value/spec/unit/bounds):
- `is_human_input = true`
- `is_computed = false`

Once a user edits a value, **it remains user-owned** and **will not be overwritten by solver output**.

---

## Write Rules

### 1) Initialization (domain/model defaults)
- `is_human_input = false`
- `is_computed = false`

### 2) System/Generated Values
Examples: stream property injection, template expansions, solver output.
- Set or keep `is_human_input = false`
- Only set `is_computed = true` when the value is computed by solver

### 3) User Edits (any field)
Triggered by edits in the modal UI (`NodeVarInput`, TP overrides, spec/unit changes, etc.).
- Set `is_human_input = true`
- Set `is_computed = false`

### 4) Solver Results / Backprop
When processing solver output:
- **Only apply** to values where `is_human_input !== true`
- Set `is_computed = true` for those values
- Never flip `is_human_input` back to `false` once a user edits

---

## UI Highlight Rule

A value is highlighted as computed **only if**:
- `is_human_input === false`
- `is_computed === true`

If a user edits a computed value, highlighting is cleared by forcing:
- `is_human_input = true`
- `is_computed = false`

---

## Solver Payload

Solver inputs now include **only** `is_human_input` (no `is_machine_generated`).
This allows the backend to decide whether a value is eligible for solver-driven updates.

---

## Where This Is Enforced

Frontend:
- `src/src/frontend/src/components/modal/tabs/node-var-input.tsx`
- `src/src/frontend/src/components/modal/tabs/info-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/specs-tab.tsx`
- `src/src/frontend/src/components/modal/tabs/node-vars-tab.tsx`
- `src/src/frontend/src/components/custom-edge/index.tsx`

Backend:
- `src/src/backend/utils/translation.ts`
- `src/src/backend/utils/translationTpsSpecsUtils.ts`
- `src/src/backend/utils/reverseTranslation.ts`
- `src/src/backend/services/computationTaskHandler.ts`

---

## Common Pitfalls

- **Do not** default `is_human_input` to `true` on initialization.
- **Do not** re-enable `is_computed` after user edits.
- **Do not** overwrite user-owned values during solver backpropagation.

---

## Quick Reference (Pseudo Code)

```ts
// User edit
update(value) {
  is_human_input = true;
  is_computed = false;
}

// Solver output
applySolver(value) {
  if (is_human_input !== true) {
    set(value);
    is_computed = true;
    is_human_input = false;
  }
}
```
