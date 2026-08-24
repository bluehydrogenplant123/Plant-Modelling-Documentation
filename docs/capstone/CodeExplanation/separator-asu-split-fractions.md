---
title: Separator and ASU Split Fractions
sidebar_position: 19
description: Explains SEPARATOR and ASU SPLT_FRAC templates, stream-driven component rows, Base and Multi-TP persistence, UI allocation, and compute validation.
---

## Overview

`SEPARATOR` and `ASU` nodes can expose one split-fraction input per active inlet component. The `SPLT_FRAC` model version uses the component-template lifecycle to create `SF`, `SF1`, `SF2`, or later numbered families, then validates every active value before computation.

## Source Files

- `src/src/shared/splitFractionModel.ts`: supported model/version names and SF-family parsing.
- `src/src/shared/streamComponentPresence.ts`: null-absent and zero-present selection.
- `src/src/frontend/src/utils/separatorSplitFractionUtils.ts`: port binding, active-component resolution, reconciliation, and UI eligibility.
- `src/src/frontend/src/utils/separatorSplitFractionPresentation.ts`: compact split rows and original-node-variable grouping.
- `src/src/frontend/src/utils/separatorSplitFractionAllocation.ts`: two-outlet percentage/amount conversion.
- `src/src/frontend/src/components/modal/tabs/info-tab.tsx`: Time Period selector and `Component Split Fractions` panel.
- `src/src/frontend/src/components/modal/tabs/separator-split-allocation.tsx`: graphical OUT1/OUT2 editor.
- `src/src/frontend/src/utils/separatorSplitFractionTpCleanup.ts`: TP deletion/migration drafts and save-time cleanup flushing.
- `src/src/frontend/src/components/custom-edge/index.tsx`: connect, reconnect, stream-change, and disconnect reconciliation.
- `src/src/backend/utils/translationTpsSpecsUtils.ts`: backend Base/Multi-TP resolution and strict compute validation.

## Applicability and Catalog Contract

Model names are normalized to uppercase and must be `SEPARATOR` or `ASU`. The calculation workflow applies only when `model_version_name` is `SPLT_FRAC`.

Template internal names use this grammar:

```text
SF_{COMPNAME::IN}
SF1_{COMPNAME::IN}
SF2_{COMPNAME::IN}
```

At runtime they become `SF_CH4`, `SF1_CH4`, and `SF2_CH4`. `SF`, `SF1`, `SF2`, and later `SF<number>` families are supported. Every family must resolve to the same unique source and target ports, and one family cannot be declared twice.

For a legacy static catalog with no templates, the model must contain exactly one `IN` and one `INFO` port. Static INFO names such as `SF_CH4` determine the available families; if none can be inferred, the fallback family is `SF`.

## Component and Value Rules

- The material stream must be connected to the resolved source port, normally `IN`.
- JSON/text null is absent and creates no active split row.
- Numeric zero is a present inlet component and does create an active split row.
- Metadata keys such as `DOMAIN`, `INSTANCE`, `FRACTIONS`, and unnamed spreadsheet columns are ignored.
- Component keys are compared case-insensitively; two raw keys that normalize to one component are a blocking collision.
- Every present inlet component must have exactly one INFO mapping in every declared SF family.
- Each active split value must be a finite number from `0` through `1`, inclusive. Zero and one are valid.

An active mapped row is a human input. It becomes `send_to_calc: true` only when all active mapped values are valid. Inactive rows are cleared to null and disabled for calculation.

## Data Flow

1. Connecting or changing the IN stream collects only present component keys; zero is retained and null is removed.
2. The shared component-template engine expands the SF-family definitions into deterministic per-component rows on INFO.
3. `resolveSeparatorInfoPortContent(...)` checks source/target binding, component collisions, missing mappings, and duplicates. It returns `disconnected`, `empty`, `unsupported`, or `ready`.
4. `reconcileSeparatorSplitFractions(...)` preserves valid existing values, activates current mappings, clears inactive rows, and calculates solver eligibility.
5. Selecting the node opens its toolbar. The **Node Variables** tab renders `Component Split Fractions` separately from `Original Node Variables` and shares the modal's **Time Period** selector.
6. Backend `resolveNodeState(...)` rebuilds the same component set from the connected stream, applies Base or TP overrides only to active mappings, and optionally runs strict validation.
7. A disconnected input, empty component set, unsupported/duplicate mapping, missing value/spec, wrong input metadata, or value outside `[0, 1]` raises `SeparatorSplitFractionValidationError` before solver dispatch.

## Base and Multi-Time-Period Persistence

For Base TP, edits update the node's cached model version and Base node parameters. For another selected Time Period, the panel merges the model baseline with persisted TP changes and local drafts, then writes a TP-specific draft rather than changing the Base value.

When a component disappears or an edge disconnects, the removed SF rows are marked inactive and persisted TP rows with the same port name, variable name, and location are staged as deletes. Generation counters cancel a stale delete if the component is reactivated before cleanup finishes. Diagram save calls `flushPendingSeparatorSplitFractionCleanups(...)` before persistence.

## Graphical Allocation

Only `SEPARATOR` exposes the **Graphical View** toggle. It represents a two-outlet split:

```text
OUT1 = stored split fraction
OUT2 = 1 - OUT1
```

Users can edit either percentage or drag the slider; OUT1 and OUT2 always total 100%. Amount editing is enabled only when the inlet component amount can be calculated from a positive `MF0`/`MF`. The amount uses the resolved mass-flow unit. `ASU` uses the traditional 0-to-1 fields and does not show this two-outlet control.

## Errors and UI Outcomes

| Status | UI outcome |
| --- | --- |
| No source stream | `Connect a material stream to the <model> IN port.` |
| No present components | `The connected IN stream has no active components.` |
| Bad binding/mapping/collision | Red `split fractions cannot be configured` list. |
| Ready but incomplete/out of range | Warning lists variables that need a value from 0 to 1. |
| Ready and valid | Active rows are eligible for calculation. |

The frontend messages guide editing, but backend strict validation remains authoritative at compute time.

## Extension Points

- Add another family with the existing `SF<number>` grammar; do not create family-specific branches.
- Add a model name in `splitFractionModel.ts` only after its port and solver semantics match this contract.
- Keep graphical allocation restricted to a proven two-outlet model. A multi-outlet or multi-family display needs an explicit allocation model.

## Testing and Verification

From `src/`:

```powershell
./node_modules/.bin/jest.cmd --runTestsByPath tests/frontend/separatorSplitFractionTpCleanup.test.ts tests/frontend/separatorSplitFractionCanvasCleanup.test.ts --runInBand --coverage=false
```

The null/zero behavior must also be checked manually against the shared contract below. Some legacy assertions in `separatorSplitFractionUtils.test.ts`, `separatorSplitFractionPresentation.test.ts`, `translationSeparatorSplitFraction.test.ts`, and `translationTpsSpecsUtils.test.ts` still treat null-valued fractions as active components. That is older behavior and does not match the current null-absent implementation.

Manual verification should cover Base and one non-Base Time Period, null and zero inlet values, connect/disconnect/reconnect, `0`, `1`, and an invalid value, plus save/reload after removing a component.

## Known Cautions

- Do not treat zero as an absent component or an invalid split fraction.
- Do not treat legacy null-present test assertions as the current component-selection contract.
- INFO display can identify split-shaped rows for supported model names, but solver eligibility is restricted to `SPLT_FRAC`.
- Do not allow inactive TP overrides to reactivate removed component rows during backend merge.
- Do not describe ASU as having the SEPARATOR two-outlet graphical control.

## Related Pages

- [Component Template Lifecycle](./component-template-lifecycle.md)
- [Excel Import Pipeline](./excel-import-pipeline.md)
- [Node Modal and Variable Inputs](./node-modal-and-variable-inputs.md)
- [Translation and Reverse Translation](./translation-and-reverse-translation.md)
