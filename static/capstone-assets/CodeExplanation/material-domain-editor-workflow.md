---
title: Material Domain Editor Workflow Code Explanation
sidebar_position: 16
description: Explains how User Tables, the Material Editor, domain APIs, workbook import, and PostgreSQL mappings provide the Domain + Port Class material workflow.
---

## Overview

The Material Domain Editor workflow exposes material data through **User Tables -> Material Properties**. The frontend loads `streams` and `materialGroups` for the active domain, includes Generic/common mappings, groups rows by Port Class and mapped databases, and lets users inspect Properties or Stream Fractions.

The workflow crosses the stable7 header, Material Editor, Redux domain state, the `/api/data/domain/:domainId` route, PostgreSQL catalog tables, workbook-import tooling, and the solver translation boundary. It preserves legacy runtime and user-workbook fallbacks without restoring the obsolete system-workbook dependency on `SYS Stream Properties.csv` or `SYS Stream Fractions.csv`.

## Source Files

- `src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu.tsx`: renders **User Tables** and opens **Material Properties** in base-period mode.
- `src/src/frontend/src/components/header-bar/header-buttons/user-tables-menu-options.ts`: defines menu labels, order, base-period guards, and the Multi-TP material restriction.
- `src/src/frontend/src/components/material-editor/index.tsx`: renders the overlay, group tabs, detail views, import/export controls, clearing behavior, and the AgGrid table.
- `src/src/frontend/src/utils/streamWorkbookUtils.ts`: parses mapping-based and legacy two-sheet workbooks, normalizes Domain names, groups streams, and merges duplicate user material rows.
- `src/src/frontend/src/features/domain/domainSlice.ts`: owns hydrated `DomainData`, merges imported user streams, updates `materialGroups`, and clears stream state.
- `src/src/frontend/src/models/domain.ts`: defines the frontend `Stream`, `MaterialGroup`, and `DomainData` contracts.
- `src/src/frontend/src/components/header-bar/utils/save-util.tsx`: places current `domainData` in diagram `snapshotData` during Save.
- `src/src/backend/routes/dataRoutes.ts`: loads domain and Generic data, reads legacy stream mappings and normalized Port Class mappings, merges streams, and builds API `materialGroups`.
- `src/src/backend/models/dataRoutes.ts`: defines backend stream and material-group response shapes.
- `src/src/backend/prisma/postgres/schema.prisma`: defines `Streams`, `DomainStreamsMapping`, `PortClassDatabaseMapping`, `Domain`, and `PortClass` persistence boundaries.
- `src/excel-migration/excel_to_csv.py`: normalizes current mapping-sheet aliases and exports referenced material database sheets to CSV.
- `src/excel-migration/migrate.py`: imports `Port Classes Database Mapping` plus referenced `#Prop_*` / `#Comp_*` data into PostgreSQL.
- `src/src/backend/utils/translation.ts`: converts selected stream rows to solver material payloads, removes editor-only metadata, and applies the Port Class fractions rule.

Relevant regression coverage:

- `src/tests/frontend/userTablesMenuOptions.test.ts`
- `src/tests/frontend/streamWorkbookUtils.test.ts`
- `src/tests/frontend/domainSlice.test.ts`
- `src/tests/backend/routes/dataRoutes.test.ts`
- `src/tests/backend/utils/translation.test.ts`
- `src/excel-migration/tests/test_jul7_migration.py`
- `src/cypress/e2e/canvas/canvas.cy.ts`

## Purpose and Responsibility

This workflow owns:

- the base-period menu entry for material data;
- Domain + Port Class grouping in the Material Editor;
- Generic/common material inclusion;
- user workbook parsing and in-memory system/user merging;
- current system workbook normalization and PostgreSQL reference-data import;
- the API response contract for flat `streams` plus grouped `materialGroups`; and
- removal of editor-only metadata before solver requests.

It does not own node Palette filtering, node Port Class definitions, saved-edge selection UI, computation dispatch, or external solver callbacks. A material group appearing in the editor proves that catalog data is available; it does not prove that a real computation server can solve that stream type.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| `domainId` | canvas route/domain selection | Calls `GET /api/data/domain/:domainId` and identifies the current domain. |
| `DomainStreamsMapping` rows | PostgreSQL legacy runtime mapping | Supplies compatible flat stream rows when normalized material mappings are missing or incomplete. |
| `PortClassDatabaseMapping` rows | PostgreSQL normalized mapping | Selects domain/Generic Port Classes and their Properties/Fractions databases. |
| `Streams` rows | PostgreSQL reference catalog | Supplies material identity, JSON Properties/Fractions, Port Class metadata, database names, and `source_type`. |
| User workbook | **Import Streams** file input | Adds or supplements user material rows for the current Domain/Generic mapping. |
| `readOnly` | `App.tsx` computation guard | Disables Delete/Import behavior and table interaction. |
| `detailView` | Material Editor local state | Selects `properties` or `stream_fractions` for columns and detail panels. |

| Output | Destination | Notes |
| --- | --- | --- |
| `streams` | API response and Redux `domain.data.streams` | Flat compatibility list used by existing stream selectors and consumers. |
| `materialGroups` | API response and Redux `domain.data.materialGroups` | Grouped view with mapping identity, scoped keys, Generic flag, and streams. |
| Imported user streams | Redux domain state | `source_type: user`; merge precedence lets user values supplement or override matching system values. |
| Diagram `snapshotData` | MongoDB diagram save payload | Save captures current `domainData`, including material state used by the diagram. |
| Export workbook | browser download | Contains `Properties` and `Fractions` sheets named `<domain>_materials_<timestamp>.xlsx`. |
| `material_properties` / `material_fractions` | solver request `parameters` | Contains sanitized material values for streams selected on edges, not editor mapping metadata. |

## Core State and Data Structures

### `Stream`

Important material fields are:

- `stream_database_id`, `content`, and `instance`: material identity and display values.
- `domain`: intrinsic or mapped domain label.
- `port_class_id` and `port_class_name`: normalized Port Class identity.
- `properties_database_name` and `fractions_database_name`: database scopes, including delimited shared-database names.
- `source_type`: normally `system` for the catalog and `user` for Material Editor imports.
- `properties`: dynamic material property JSON.
- `stream_fractions`: dynamic fraction/composition JSON.

### `MaterialGroup`

A group contains mapping identity plus the streams visible under that tab:

- `port_class_id` and `port_class_name`
- `properties_database_name` and `fractions_database_name`
- `property_keys` and `fraction_keys`
- `is_generic`
- `streams`

`property_keys` and `fraction_keys` prevent a shared stream row from displaying unrelated dynamic columns under the wrong mapped database.

### Merge Identity and Precedence

Backend, Redux, and workbook utilities use the same general identity order:

1. Port Class plus `stream_database_id` when a database ID exists.
2. Otherwise Port Class plus `content` and `instance`.
3. Internal record ID is a final fallback in backend/runtime collections.

When matching records are merged, a `source_type: user` record wins scalar conflicts. Properties and Fractions are merged by key so incoming user values can supplement existing system JSON instead of replacing the entire object.

## Main Functions and Components

### Header and Editor

- `getUserTableMenuOptions(...)`: returns **Material Properties**, **Cost and Revenue Data**, and **Supply and Demand Data** in fixed order. It always disables Material Properties for `mode === 'mtp'`.
- `UserTablesMenu`: ignores disabled selections, opens the parent Material Editor for `materialProperties`, and delegates Economic options to `CostButtons`.
- `MaterialEditor`: selects Redux domain data, derives group tabs and scoped keys, renders the table/detail panel, and owns import/export/clear handlers.
- `buildMaterialDetailKeyScopes(...)`: learns which dynamic keys belong to each database token, including shared property-database rows.
- `getScopedRecordEntries(...)`: limits displayed detail values to the active group's database scope.
- `handleImportStreams(...)`: reads the workbook with SheetJS, parses current-domain material rows, dispatches `updateOrAddStream(...)`, and reports the row count.
- `handleExportStreams()`: writes `Properties` and `Fractions` sheets for all current streams.
- `handleClearStreams()`: deletes all current React Flow edges, clears the edge state, and dispatches `clearStreams()`.

### Workbook and Redux

- `parsePortClassDatabaseMappingsWorkbook(...)`: accepts mapping-sheet aliases, filters mappings to the current domain plus Generic, reads referenced database sheets, and falls back to a two-sheet import when no mapping sheet exists.
- `buildMaterialStreamsFromWorkbookRows(...)`: builds dynamic `properties` JSON and filters explicit Domain rows to the active domain or Generic.
- `mergeStreamFractionRows(...)`: attaches Fractions to rows by `stream_database_id`, then Content/Instance fallback.
- `updateOrAddStream(...)`: updates the flat Redux list and matching `materialGroups`, applying user-over-system merge precedence.
- `clearStreams()`: clears both `streams` and `materialGroups` in Redux domain state.

### Backend and System Import

- `fetchPortClassDatabaseMappings(...)`: returns Generic mappings plus rows matching `domain_id`, normalized domain name, or the `Generic` domain label.
- `fetchStreamsForMaterialMappings(...)`: reads metadata-aware `Streams` rows and filters them against compatible mapping/domain rules.
- `streamMatchesMaterialMapping(...)`: requires mapped database agreement when the mapping specifies a database and prevents material, heat, and electric roles from being mixed.
- `buildMaterialGroups(...)`: starts from mappings, attaches compatible merged streams, scopes dynamic keys, merges equivalent shared-database groups, sorts Generic first, and returns the API group list.
- `transformData(...)`: merges legacy domain streams with mapping-selected streams and returns both `streams` and `materialGroups`.
- `process_port_class_material_streams(...)`: imports the current mapping CSV, stores normalized mapping rows, reads each shared Properties database once, merges referenced Fractions databases, and upserts system streams.
- `process_streams(...)`: invokes the current Port Class material importer and skips stream import when no valid mapping contract is available.
- `transformStreamToMaterialProperty(...)`: removes Port Class/database/source metadata before building the solver property row.
- `translation(...)`: emits a material property row only when the selected stream has at least one usable property value, and emits fractions only when a connected port has both `compname_MF` and `compname_X` templates.
- `shouldIncludeMaterialFractionsForPortClass(...)`: additionally omits fraction rows when the active Port Class mapping explicitly has no Fractions database.

## Rendered UI / Interaction Map

| UI State or Action | Source State or Props | Expected Result | Verification |
| --- | --- | --- | --- |
| Base-period **User Tables** | `mode="base"` | Dropdown includes enabled/guarded **Material Properties**. | Open a base-period canvas and inspect the dropdown. |
| Multi-TP **User Tables** | `mode="mtp"` | **Material Properties** is always disabled. | Open the Multi-TP secondary row. |
| Editor opens | `domain.data`, `isOpen` | Header shows Domain and active Class; Generic badge appears for Generic mappings. | Open Material Properties for a domain with Generic data. |
| Multiple groups | `materialGroups` with more than one non-empty group | Tabs show group labels and stream counts; Generic sorts first. | Load a mapping workbook with Generic plus domain groups. |
| One non-empty group | derived `streamGroups.length === 1` | No tab strip; the single group becomes active. | Load a single-group material set. |
| Switch Detail View | `detailView` local state | Dynamic table columns and **View (N)** counts switch between Properties and Stream Fractions. | Toggle the selector and inspect one row. |
| Open detail panel | `selectedDetail` local state | Side panel shows scoped non-empty key/value rows for one stream. | Click an enabled **View (N)** button. |
| Import workbook | `readOnly === false` | Mapping rows for the current domain/Generic merge into Redux and a row-count alert appears. | Import a focused fixture workbook. |
| Read-only editor | `readOnly === true` | Delete and Import are disabled; direct table interaction is suppressed. Export remains available. | Toggle the computation guard while the editor is open. |
| Delete All Streams | current React Flow edges and Redux streams | All current edges are deleted and the material lists are cleared. | Use a disposable diagram and check both canvas and editor. |

## Component Contract

`MaterialEditorProps`:

| Prop | Type | Contract |
| --- | --- | --- |
| `isOpen` | `boolean` | Returns `null` when false; renders the portal when true. |
| `onClose` | `() => void` | Closes the overlay without changing material state. |
| `container` | `HTMLElement` optional | Portal target; defaults to `document.body`. |
| `readOnly` | `boolean` optional | Defaults to false and controls destructive/import interactions. |

State and dependencies:

- Redux selector: `state.domain.data` supplies `streams`, `materialGroups`, Domain identity, and mapped database metadata.
- React Flow: `getEdges`, `deleteElements`, and `setEdges` implement clear/import edge side effects.
- Local state: `selectedGroupKey`, `selectedDetail`, and `detailView` control group and detail presentation.
- `useMemo`: derives stream groups, active group, scoped keys, column definitions, and row data from current domain state.
- File API and SheetJS: `FileReader` loads `.xlsx`/`.xls`; `XLSX.read` parses; `XLSX.writeFile` downloads export data.
- `AgGridReact`: receives active-group rows and dynamic columns. Current code does not provide a cell-edit persistence handler, so import is the supported way to change material row data.

## Data Flow

### Domain load to grouped editor

1. `fetchDomainData(domainId)` calls `GET /api/data/domain/:domainId`.
2. `dataRoutes.ts` loads the selected domain and calls `mergeGenericDomain(...)` so Generic models and legacy stream mappings remain available.
3. `transformData(...)` builds legacy flat streams, fetches normalized Port Class mappings for the domain plus Generic, and fetches metadata-aware streams compatible with those mappings.
4. `mergeMaterialStreams(...)` deduplicates system/user records by material identity.
5. `buildMaterialGroups(...)` attaches streams to Domain + Port Class/database groups, scopes dynamic keys, merges equivalent shared-database groups, and sorts Generic first.
6. The route returns flat `streams` and grouped `materialGroups` in the same domain response.
7. `domainSlice` sanitizes dynamic stream properties and stores both collections.
8. `MaterialEditor` prefers backend `materialGroups`; if they are absent, it derives groups from flat streams.

### User workbook import and save

1. The user selects **Import Streams** and chooses an `.xlsx` or `.xls` file.
2. `parsePortClassDatabaseMappingsWorkbook(...)` looks for a mapping-sheet alias.
3. With a mapping sheet, it keeps mappings for the current domain plus Generic and reads the referenced Properties/Fractions sheets.
4. Without a mapping sheet, it treats the first sheet as Properties and the optional second sheet as Fractions.
5. Parsed rows receive `source_type: user` and are deduplicated by material identity.
6. `updateOrAddStream(...)` merges each row into flat streams and the matching group; user scalar/JSON values take precedence over matching system data.
7. A later diagram Save includes current `domainData` as `snapshotData`.

### System workbook to PostgreSQL

1. `excel_to_csv.py` recognizes **Port Classes Database Mapping** aliases and preserves referenced `#Prop_*` / `#Comp_*` sheet names.
2. `migrate.py` writes normalized `PortClassDatabaseMapping` rows.
3. Shared Properties databases are read once; referenced Fractions databases are merged into the same material records.
4. Intrinsic row Domain/Port Class metadata wins when present; mapping values provide fallback context.
5. The importer upserts `Streams` and their `DomainStreamsMapping` links.
6. `System Variables` continues through its own active import path. The stream importer does not read `SYS Stream Properties.csv` or `SYS Stream Fractions.csv`.

### Selected stream to solver payload

1. Edge selection stores a chosen stream record on the canvas edge.
2. `translation.ts` resolves both connected ports and builds stream connectivity for every supported stream class.
3. `transformStreamToMaterialProperty(...)` copies dynamic `properties` while removing editor-only mapping metadata; empty/all-invalid property records are not sent to the solver.
4. Fractions are normalized and included only when they are non-empty, at least one endpoint has both component templates (`compname_MF` and `compname_X`), and the active Port Class mapping does not explicitly disable a Fractions database.
5. Internal matching `key` fields are removed from final `parameters.material_properties` and `parameters.material_fractions` records.

## Backend/Data-Flow Contract

`GET /api/data/domain/:domainId` remains backward compatible by returning:

- `streams`: the existing flat stream list;
- `materialGroups`: the Domain + Port Class/database view;
- the other existing domain models, colors, units, run configs, equation types, solution algorithms, and cost configuration.

The normalized `PortClassDatabaseMapping` table is preferred when available. If it is absent or returns no mappings, `transformData(...)` still returns `DomainStreamsMapping` streams and `buildMaterialGroups(...)` falls back to stream metadata/name grouping.

The Material Editor import is a frontend state operation. It does not write the system PostgreSQL catalog. System workbook migration is a separate deployment/setup workflow.

## Side Effects

- Opening a domain calls `GET /api/data/domain/:domainId` through the Redux thunk.
- Import reads a local workbook and mutates Redux domain state; it does not upload the workbook.
- Save can persist the resulting domain material state inside diagram `snapshotData`.
- Export initiates a browser download and does not change Redux or backend data.
- Delete All Streams deletes every current React Flow edge and clears Redux `streams`/`materialGroups`.
- The system importer writes PostgreSQL mapping, stream, and domain-link rows; it is not invoked by the Material Editor.
- Solver translation reads only streams selected on edges and emits sanitized request records.

## Error Handling and Edge Cases

- A missing mapping sheet in a user workbook activates the compatible first-sheet/second-sheet fallback.
- A missing first worksheet returns no imported rows.
- Mapping rows are filtered to the current domain, normalized Petroleum Refinery spelling, and Generic mappings.
- Missing referenced Properties sheets produce no user rows for that mapping; an optional missing Fractions sheet leaves the material without imported fractions.
- The backend checks whether `PortClassDatabaseMapping` and optional `Streams` metadata columns exist before reading them.
- When no normalized mapping is available, legacy `DomainStreamsMapping` rows still populate flat streams and fallback groups.
- Group labels fall back from Port Class to Properties database, Fractions database, then `Materials`.
- Material/heat/electric role checks prevent compatible database-name matching from mixing those stream categories.
- Shared database names can be delimited by semicolons, commas, or pipes; detail-key scoping separates the visible dynamic columns.
- `Delete All Streams` is intentionally global to the current canvas. There is no per-group delete action.

## Extension Points

- Add a new workbook mapping alias in `streamWorkbookUtils.ts` and `excel_to_csv.py`, then update both frontend and Python migration tests.
- Add material identity fields by updating frontend/backend models, Prisma schema, importer SQL, API merge keys, Redux merge keys, export columns, and solver sanitization together.
- Change group matching in `streamMatchesMaterialMapping(...)` and verify shared database, Generic, heat, electric, and material cases in `dataRoutes.test.ts`.
- Change database-scoped detail columns in both backend and frontend `buildMaterialDetailKeyScopes(...)`; they intentionally mirror each other.
- Add direct cell editing only with an explicit Redux update/persistence contract and AgGrid edit-request handling.
- Add node Palette Port Class filtering in the Palette/sidebar area, not in this Material Editor grouping code.
- Change solver material metadata only through `translation.ts` tests; do not expose editor database names in the external solver payload by accident.
- Keep current system migration mapping-based. Do not restore obsolete reads of `SYS Stream Properties.csv` or `SYS Stream Fractions.csv`.

## Testing and Verification

Terminal: **PowerShell**

Working directory:

```text
HYPRONET-GUI/src/
```

Run the focused TypeScript regressions:

```powershell
npx.cmd jest tests/frontend/userTablesMenuOptions.test.ts tests/frontend/streamWorkbookUtils.test.ts tests/frontend/domainSlice.test.ts tests/backend/routes/dataRoutes.test.ts tests/backend/utils/translation.test.ts --runInBand
```

Run the repository TypeScript build:

```powershell
npm.cmd run build
```

Run the Python migration regression in the same container path used by CI:

```powershell
docker compose run --rm python-runner python -m unittest discover -s tests -p "test_*.py"
```

For documentation-only changes, run from the repository root:

```powershell
git diff --check -- docs/CodeExplanation/material-domain-editor-workflow.md
```

### Frontend Manual Verification Matrix

| Scenario | Action | Expected Visual Result | Expected State or API Effect | Regression Risk |
| --- | --- | --- | --- | --- |
| Generic plus domain groups | Open Material Properties for a mapped domain. | Generic is first; domain-specific classes follow; counts and database names match. | One domain API request returns flat and grouped data. | High: wrong grouping mixes incompatible material rows. |
| Properties scope | Choose a shared-database group and select Properties. | Only keys belonging to the active Properties database appear. | No write; derived columns use `property_keys`. | High: cross-database keys can mislead users and solver selection. |
| Fractions scope | Select Stream Fractions for a class with/without a Fractions database. | Mapped fraction columns appear; a no-fractions group shows zero fraction columns. | No write; derived columns use `fraction_keys`. | High: composition can leak into an incompatible Port Class. |
| User override | Import a workbook row matching a system material. | One merged row remains; user values appear and Source is user. | Redux merges scalar and JSON values using user precedence. | High: duplicate or reversed precedence changes model inputs. |
| Legacy user workbook | Import a two-sheet workbook with no mapping sheet. | Rows load in the compatible fallback group. | First sheet becomes Properties; optional second becomes Fractions. | Medium: older user files must remain usable. |
| Read-only guard | Open or keep the editor open while the material rule is read-only. | Delete/Import are disabled; Export is available. | No destructive/import mutation is allowed. | High: computation-time edits can desynchronize state. |
| Clear all | Use a disposable diagram and click Delete All Streams. | Material rows disappear and every canvas edge is removed. | React Flow edges and Redux material state clear. | High: this action is intentionally destructive. |

## Known Cautions

- The current header entry is **User Tables -> Material Properties**, not a separate **Materials -> Material Editor** section.
- Direct AgGrid cell editing is not a supported persistence path; use workbook import for material row changes.
- Export creates a two-sheet material workbook, not the full system mapping workbook.
- A selected material group does not filter node models in the Palette.
- Catalog/API/payload tests do not establish successful real-server computation for every Port Class. Keep external solver callback validation separate.
- Diagram snapshots can retain imported material state. Check both current PostgreSQL catalog data and saved `snapshotData` when diagnosing stale rows.
- Generic data is intentionally merged into selected domains. Do not remove it as an apparent duplicate without checking mapping identity and `is_generic`.
- Generated migration logs, CSV output, runtime JSON, and solver request artifacts are verification aids only and must not be edited or committed as source documentation.

## Related Pages

- [Material Editor User Guide](../UserGuide/primary-menus/materials/material-editor.mdx)
- [Header Bar Code Explanation](./header-bar.md)
- [Custom Edge and Stream Selection Code Explanation](./custom-edge-and-stream-selection.md)
- [Backend Data Routes and Persistence Code Explanation](./backend-data-routes-and-persistence.md)
- [Excel Import Pipeline Code Explanation](./excel-import-pipeline.md)
- [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md)
