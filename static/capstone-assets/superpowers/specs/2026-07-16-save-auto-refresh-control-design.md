# Save and Auto Refresh Control Design

## Goal

Replace the oversized `Save / Refresh On` control in the header toolbar with a compact connected control that matches HYPRONET's existing navy outlined buttons.

## Selected direction

Use two connected button segments inside one visual group:

- The left segment is labelled `Save` and keeps the existing save behavior.
- The right segment contains a refresh icon, the label `Auto refresh`, and a small status dot.
- The segments share one outer navy border and rounded outer corners, while a divider keeps the actions visually and semantically distinct.

## States

- When auto refresh is enabled, the right segment uses a light navy background and a green status dot.
- When auto refresh is disabled, the right segment uses a white background and a neutral gray status dot.
- Hover and focus states follow the existing header toolbar's navy color system.

## Interaction and accessibility

- `Save` and `Auto refresh` are separate native buttons; interactive elements are not nested.
- The auto-refresh button exposes its state with `aria-pressed` and a state-specific accessible label.
- Both actions remain keyboard accessible and have visible focus treatment.
- The current `save_auto_reload_enabled` local-storage key and save behavior remain unchanged.

## Scope

The implementation is limited to the existing Save/Restore header component, its toolbar styles, and focused frontend tests. It does not change diagram persistence, restore behavior, canvas naming, or other header controls.
