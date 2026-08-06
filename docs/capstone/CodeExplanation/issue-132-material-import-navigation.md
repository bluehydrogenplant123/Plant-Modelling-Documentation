# Issue #132 Material Import Navigation

Use this page to jump between the meeting evidence, the verified workbook
fixture, the implementation, and the regression tests for
[Issue #132](https://github.com/bluehydrogenplant123/HYPRONET-GUI/issues/132).
The implementation is tracked in
[PR #133](https://github.com/bluehydrogenplant123/HYPRONET-GUI/pull/133).

## Workbook source

Raunak Pandey sent the exact regression workbook to Muyao in Teams on
2026-07-30 at 17:39:

- Original filename: `material editor_ATR_Plant 2.xlsx`
- Size: `33,690` bytes
- SHA-256:
  `176AA2AEE025ECEBA83E540520BA61E42EBDE6CC6F9880BB014BFE319240D2FF`
- Sheets: `Stream Properties` (`121` data rows) and `Stream Contents` (`121`
  matching data rows)
- Port classes: `MES 119`, `Q 1`, and `ELF 1`

The unchanged workbook is now the browser regression fixture at
[`src/cypress/fixtures/material_editor_test.xlsx`](../../src/cypress/fixtures/material_editor_test.xlsx).
It replaces the stale fixture that lacked the row-level `Domain` and `Port
Class` metadata required by the production importer.

## Visual evidence

The
[Issue evidence comment](https://github.com/bluehydrogenplant123/HYPRONET-GUI/issues/132#issuecomment-5133344047)
contains the original meeting evidence. The
[Raunak workbook validation comment](https://github.com/bluehydrogenplant123/HYPRONET-GUI/issues/132#issuecomment-5195803141)
contains the exact before/after browser result.

### Original meeting recording

[Open the expected combined groups at full resolution](https://github.com/user-attachments/assets/636cf1a2-872b-480e-8c77-546e3fad9c07)

[![Expected combined groups](https://github.com/user-attachments/assets/636cf1a2-872b-480e-8c77-546e3fad9c07)](https://github.com/user-attachments/assets/636cf1a2-872b-480e-8c77-546e3fad9c07)

[Open the unexpected `Materials (119)` group at full resolution](https://github.com/user-attachments/assets/0cc257ac-7944-4719-ae08-2c1f13b36c9a)

[![Unexpected Materials 119 group](https://github.com/user-attachments/assets/0cc257ac-7944-4719-ae08-2c1f13b36c9a)](https://github.com/user-attachments/assets/0cc257ac-7944-4719-ae08-2c1f13b36c9a)

### Current branch validation

[Open the before-import screenshot at full resolution](https://github.com/user-attachments/assets/a85931de-def4-4d72-bade-2f89652e3dab)

[![Before exact Raunak import: 1 / 1 / 6](https://github.com/user-attachments/assets/a85931de-def4-4d72-bade-2f89652e3dab)](https://github.com/user-attachments/assets/a85931de-def4-4d72-bade-2f89652e3dab)

[Open the after-import screenshot at full resolution](https://github.com/user-attachments/assets/6ba79ee2-b67c-4458-abb4-da0f5aed8743)

[![After exact Raunak import: 2 / 2 / 125](https://github.com/user-attachments/assets/6ba79ee2-b67c-4458-abb4-da0f5aed8743)](https://github.com/user-attachments/assets/6ba79ee2-b67c-4458-abb4-da0f5aed8743)

### Import path

[Open the Draw.io flow at full resolution](https://github.com/user-attachments/assets/23eb0304-126b-428c-b36a-b590a4144d8e)

[![Issue 132 material import flow](https://github.com/user-attachments/assets/23eb0304-126b-428c-b36a-b590a4144d8e)](https://github.com/user-attachments/assets/23eb0304-126b-428c-b36a-b590a4144d8e)

## Code map

| Concern                                              | Code                                                                                                       |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Workbook entry point and strict metadata validation  | [`parsePortClassDatabaseMappingsWorkbook()`](../../src/src/frontend/src/utils/streamWorkbookUtils.ts#L593) |
| Read each resolved Properties sheet once             | [`propertySources`](../../src/src/frontend/src/utils/streamWorkbookUtils.ts#L650)                          |
| Assign shared-sheet rows to canonical material roles | [`propertySources.forEach()`](../../src/src/frontend/src/utils/streamWorkbookUtils.ts#L688)                |
| Stable stream identity matching                      | [`materialStreamsMatch()`](../../src/src/frontend/src/features/domain/domainSlice.ts#L69)                  |
| Merge user rows into Redux groups                    | [`updateOrAddStream`](../../src/src/frontend/src/features/domain/domainSlice.ts#L230)                      |
| Material Editor import and actionable errors         | [`handleImportStreams()`](../../src/src/frontend/src/components/material-editor/index.tsx#L494)            |
| Exact Raunak browser fixture                         | [`material_editor_test.xlsx`](../../src/cypress/fixtures/material_editor_test.xlsx)                        |
| Browser import, grouping, edge, and save regression  | [`canvas.cy.ts`](../../src/cypress/e2e/canvas/canvas.cy.ts#L50)                                            |
| Metadata-free rejection regression                   | [`streamWorkbookUtils.test.ts`](../../src/tests/frontend/streamWorkbookUtils.test.ts#L96)                  |
| Shared Hydrogen database `1 / 1 / 6` regression      | [`streamWorkbookUtils.test.ts`](../../src/tests/frontend/streamWorkbookUtils.test.ts#L221)                 |
| Random imported ID merge regression                  | [`domainSlice.test.ts`](../../src/tests/frontend/domainSlice.test.ts#L21)                                  |
| New row joins an existing combined group             | [`domainSlice.test.ts`](../../src/tests/frontend/domainSlice.test.ts#L91)                                  |

## Verified result

- Before import: three groups with `1 / 1 / 6` rows.
- After importing Raunak's exact workbook: the same three canonical groups with
  `2 / 2 / 125` rows.
- `P1`, `Q1`, and `S4A` are placed in the ELF, Q, and material groups,
  respectively.
- No fallback `Materials` group is created.
- Metadata-free workbooks stop with an actionable error.
- The targeted Cypress canvas import, edge-selection, and save flow passes.
- Docker/database cleanup cannot alter the grouping decision; isolated services
  were used only to exercise the complete browser flow.
