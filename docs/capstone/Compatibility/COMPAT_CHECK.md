# Compatibility Check Prompt

Use this prompt with an AI assistant (Cursor, ChatGPT, etc.) when making
changes that might affect stored data. Paste or reference your git diff.

---

## Prompt Template

```
You are a schema compatibility checker for the Plant-GUI project.

### Step 1 — Read Project Context

Before analyzing, read these files from the codebase:

1. src/src/backend/utils/schemaMigrations.ts
   → Find CURRENT_SCHEMA_VERSION and VERSION_ORDER
2. docs/Compatibility/SCHEMA_SNAPSHOT.md
   → This is the last-known data structure baseline, recorded at the
     version noted at the top of that file

### Step 2 — Compare Live Code vs Snapshot (Snapshot Is the Judge)

**Principle:** Use SCHEMA_SNAPSHOT.md as the source of truth. Version numbers
are labels; structural divergence from the snapshot is what matters.

Compare current code structures against the snapshot:

- save-util.tsx payload fields
- FullNetworkSnapshot interface in dataRoutes.ts
- Prisma MongoDB schema (Diagram, Node, SubnetworkBlueprint,
  TpNodeVers, TpChanges)
- Canvas node/edge data shape

If ANY structure has diverged from the snapshot (do not rely on version
numbers; the snapshot comparison is the judge), then:

1. Ask the user: "Data structures have changed but version was not bumped.
   Update version?"
2. If the user answers Yes:
   - Bump CURRENT_SCHEMA_VERSION in schemaMigrations.ts
   - Append the new version to VERSION_ORDER
   - Add migration entries (migrations / canvasMigrations) if needed
   - Update docs/Compatibility/SCHEMA_SNAPSHOT.md with the current
     structure (read live code and write the new snapshot)
   - Update schemaVersion in save-util.tsx payload to match
3. If the user answers No: remind them to do it manually later.

### Step 3 — Analyze the Git Diff

For the provided diff, determine:

1. Does it modify any stored data structure (save payload, export
   snapshot, Prisma schema, canvas node/edge fields)?
   - If NO → reply "This change does not affect compatibility." and stop.
   - If YES → continue.

2. Classify the change:
   - Additive (new optional field with default) → no migration needed
   - Rename / restructure → migration needed
   - Destructive (field removed, type changed) → migration needed,
     possibly incompatible

3. If migration is needed, generate a migration function for
   schemaMigrations.ts (both the snapshot-level `migrations` registry
   and the canvas-level `canvasMigrations` registry as appropriate).
   Include the new version in VERSION_ORDER.

4. Recommend version bump: minor (6.0 → 6.1) or major (6.x → 7.0).

5. If the change is fundamentally incompatible (no migration path),
   state this clearly and recommend documenting it as a breaking change.

### Input
Paste the git diff below:
```

---

## When To Use

- Before merging a PR that touches save/load, export/import, or DB schema
- During code review when unsure if a change is breaking
- When adding new fields to canvas nodes or edges
- Periodically, to verify snapshot is still in sync with code

## Version Bump Quick Reference

| Change Type | Bump | Migration? |
|-------------|------|------------|
| New optional field with default | None | No |
| Field renamed | Minor | Yes |
| Field type changed | Minor | Yes |
| Field removed | Minor or Major | Yes |
| Data model restructured | Major | Yes |
| No migration path possible | Major | Document as breaking |

## Key File Paths

| File | Role |
|------|------|
| `src/src/backend/utils/schemaMigrations.ts` | Version constant + migration registry |
| `docs/Compatibility/SCHEMA_SNAPSHOT.md` | Baseline structure — **the judge** for "needs version bump" |
| `src/src/frontend/src/components/header-bar/utils/save-util.tsx` | Save payload definition |
| `src/src/backend/routes/dataRoutes.ts` | FullNetworkSnapshot + export/import |
| `src/src/backend/prisma/mongodb/schema.prisma` | MongoDB data models |

---

## Prompt vs Code-Based Check: Evaluation

### Is the Prompt Professional Enough?

The prompt is structured and actionable: it defines steps, file paths, and decision rules. For human-in-the-loop workflows (e.g. before merging a PR), it is sufficient. It does not, however, enforce consistency automatically—it relies on the developer to run it and follow the instructions.

### Would Code Be More Efficient?

| Approach | Pros | Cons |
|----------|------|------|
| **Prompt only** | No extra tooling; works with any AI; flexible for ad-hoc checks | Manual; easy to forget; no CI integration |
| **Code-based check** | Automatable; can run in CI; deterministic; catches drift before merge | Requires maintenance; snapshot must be machine-parseable; limited to what the script can detect |
| **Hybrid** | Script detects drift → prompts for migration generation | Best of both; more setup |

### Recommendation

- **Keep the prompt** for migration generation and human judgment (e.g. "is this additive or breaking?"). AI is better at interpreting diffs and writing migration code.
- **Add a lightweight script** (e.g. `npm run compat-check`) that:
  - Compares key structure locations (payload keys, Prisma model fields) against a machine-readable baseline (e.g. JSON derived from SCHEMA_SNAPSHOT)
  - Exits with code 1 if drift is detected
  - Can be run in CI or pre-commit
- **Use the script for detection**, the **prompt for remediation**. The script answers "did something change?"; the prompt answers "how do we fix it?"
