# Issue Draft: Excel / Library Compatibility for Versioned Diagrams

> **Problem**: Diagram schema compatibility currently protects saved diagram structure, but it does not explicitly cover Excel-driven library changes such as model version renames, port/variable removals, or catalog updates. A diagram can pass schema migration and still fail to load, validate, or compute if its referenced model library entries changed in Excel and the database library state no longer matches the diagram's expectations.

---

## One-Line Summary

**Treat Excel compatibility as a separate layer from schema compatibility.**

Schema migration answers "can this saved diagram shape still be read?"
Excel/library compatibility answers "do the referenced models, model versions, ports, and variables still exist and mean the same thing?"

Both are needed.

---

## Why This Issue Exists

The current versioning work focuses on persisted diagram structure:

- `schemaVersion`
- diagram save/load/import/export migration
- backup and upgrade flow
- compatibility review against `SCHEMA_SNAPSHOT.md`

That protects the stored diagram format, but it does not fully protect runtime dependencies loaded from Excel-backed library data in Postgres.

If Excel changes:

- a `ModelVersion` name
- a node model's available variants
- a `PortVar`
- a port definition
- default flags or operational semantics

then an older diagram may still be structurally valid while becoming functionally incompatible.

---

## Concrete Risk Observed

Recent Excel comparison shows this is not theoretical.

Between `feb-15-2026.xlsx` and `mar-18-2026.xlsx`:

- `PSOURCE` and `PSINK` moved from `BASE` to `FLOW_FIXED` / `FLOW_FREE`
- related rows in `SYSNodeVariables` changed accordingly
- some older variable rows were removed

In the latest update to `mar-18-2026.xlsx`:

- `COMPR BASE` rows for `POSITIVE_SLACK` and `NEGATIVE_SLACK` were removed

This means a diagram may:

- survive schema upgrade
- still open as JSON/canvas
- but fail later because referenced library entries were renamed or removed

---

## Why Schema Compatibility Alone Is Not Enough

Schema compatibility and Excel compatibility protect different things.

| Layer | Protects | Example failure |
|-------|----------|-----------------|
| **Schema compatibility** | Persisted diagram/snapshot shape | old canvas field names no longer match current code |
| **Excel/library compatibility** | Runtime model catalog and node semantics | diagram references `PSOURCE / BASE`, but library now only has `FLOW_FIXED` / `FLOW_FREE` |

If only schema compatibility is checked, the team can incorrectly conclude:

> "migration passed, so compatibility is safe"

when the real risk is:

> "diagram structure is fine, but the referenced library contract changed"

---

## Additional Operational Risk

Excel import is currently a **manual** process, not an automatic startup migration.

The import script also uses a mix of:

- `ON CONFLICT DO UPDATE`
- `ON CONFLICT DO NOTHING`
- insert-if-missing behavior

This creates another compatibility risk:

- new Excel rows may be added successfully
- renamed or deleted Excel rows may leave stale Postgres data behind
- different environments may end up with different effective library state depending on whether the database was reset

So the problem is not only "what changed in Excel" but also "what data actually exists in the real database after import."

---

## Proposed Solution

Do **not** merge Excel compatibility into `SCHEMA_SNAPSHOT.md` itself.

Instead, define a second compatibility track alongside schema compatibility.

### 1. Keep Schema Compatibility Focused

`SCHEMA_SNAPSHOT.md` and schema migration review should continue to cover:

- persisted diagram structure
- snapshot/import/export format
- version bump rules
- migration and rollback safety

### 2. Add Excel / Library Compatibility Review

When Excel sheets change, run a separate review that asks:

- Did any sheet headers change?
- Were any models added, removed, or renamed?
- Were any `ModelVersion` keys added, removed, or renamed?
- Were any `PortVar` or port definitions added, removed, or renamed?
- Did any default flags or compute-relevant semantics change?

### 3. Add Stored-Data Impact Check

Before declaring the change safe, inspect whether existing diagrams reference:

- removed model names
- removed model versions
- removed port variable names
- renamed catalog entries that now require alias handling or migration

This should be checked against real DB state, not only code or Excel diff.

### 4. Define Recovery Paths by Change Type

Different Excel changes need different responses:

- **Additive change**: likely safe after re-import
- **Rename**: may need alias mapping or targeted migration
- **Deletion**: may require DB cleanup, compatibility aliasing, or diagram migration
- **Semantic change**: may require manual validation even if names did not change

### 5. Document When Version Bump Is Required

Not every Excel change should trigger a diagram schema version bump.

Suggested rule:

- **Schema version bump required** when persisted diagram format changes
- **Excel/library compatibility review required** when runtime catalog semantics change
- **Both required** when an Excel-driven change also forces persisted diagram content to be rewritten

---

## Proposed Workflow Addition

Extend compatibility review with a new section:

### Excel / Library Compatibility

Required when:

- files under `src/excel-sheets/` change
- import scripts under `src/excel-migration/` change
- code changes depend on renamed or removed library entries

At minimum, report:

- changed sheets
- changed headers, if any
- added/removed/renamed models
- added/removed/renamed model versions
- added/removed/renamed port variables
- whether real DB inspection is required
- whether stale imported DB rows are a risk
- whether a schema version bump is needed, not needed, or unclear

---

## Proposed Outcome

After this issue is addressed, the team should be able to answer two separate questions clearly:

1. **Can old saved diagrams still be structurally upgraded and read?**
2. **After the latest Excel import, do those diagrams still point to a valid runtime library contract?**

Right now the project answers the first question much better than the second.

---

## Non-Goals

This issue does **not** yet implement:

- Excel diff tooling
- DB cleanup tooling
- alias mapping for renamed model versions
- automatic migration of diagrams based on Excel renames

This issue is only for defining the problem, scope, and recommended solution direction.

---

## Suggested Acceptance Criteria for the Future Implementation

- Compatibility review explicitly distinguishes schema compatibility from Excel/library compatibility.
- Excel changes are no longer treated as implicitly covered by schema migration.
- The team has a documented rule for when Excel changes require DB inspection.
- The team has a documented rule for when Excel changes do or do not require a schema version bump.
- Real-server validation can state whether a failure is caused by schema mismatch, Excel/library mismatch, or stale imported DB state.
