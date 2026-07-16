# Remove Duplicate Header Save Design

## Goal

Remove the left-hand duplicate **Save** control from the main header while preserving the right-hand **Save** control and all existing save behavior.

## Confirmed Behavior

- `HeaderBar` renders `SaveAndRestore` only once.
- The retained instance stays in the right-side `header-toolbar-meta-actions` group beside `CanvasNameEdit`.
- The retained control keeps its **Refresh On/Off** toggle and existing disabled-state rule.
- Save execution, auto-reload preference, persistence, and navigation behavior remain unchanged.

## Implementation

Delete only the older `SaveAndRestore` JSX instance rendered in the left/main navigation group of `header-bar/index.tsx`.

Keep the `SaveAndRestore` import because the right-side instance still uses it. Do not modify `save-and-restore.tsx`, `save-util.tsx`, CSS, backend routes, or persistence code.

## Testing

- Add a focused HeaderBar regression assertion that `SaveAndRestore` is rendered exactly once.
- Assert that the remaining instance is still inside `header-toolbar-meta-actions`.
- Run the focused frontend Jest test and inspect the final diff.

## Boundaries

- No visual redesign or toolbar reordering.
- No changes to save timing, fast-save behavior, computed-data writes, or auto-reload behavior.
- No unrelated cleanup or formatting changes.
