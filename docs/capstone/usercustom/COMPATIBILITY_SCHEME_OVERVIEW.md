# Compatibility Scheme Overview

A brief, objective overview of the Plant-GUI schema compatibility approach.

---

## What It Is

```
┌─────────────────────────────────────────────────────────────────┐
│                    Compatibility Scheme                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [Save]          [Load]           [Export]        [Import]      │
│   payload ──►     canvas ◄──       snapshot ◀──►  snapshot     │
│   +schemaVersion  migrateCanvas    +version       migrateToLatest│
│                   IfNeeded()                      ()             │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  schemaMigrations.ts                                     │  │
│   │  • CURRENT_SCHEMA_VERSION                                │  │
│   │  • VERSION_ORDER (version chain)                         │  │
│   │  • migrations{} — snapshot-level transforms              │  │
│   │  • canvasMigrations{} — canvas-level transforms           │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  SCHEMA_SNAPSHOT.md — baseline structure at last bump    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Core idea:** Every stored diagram and exported file carries a version. On load/import, we run a small migration chain to bring old data up to the current format. The snapshot file records what the structure looked like at the last version bump, so we can detect when someone changed the structure but forgot to bump the version.

---

## Why This Approach?

### 1. Not every change needs compatibility work

Most code changes (UI, business logic, new features) do not touch stored data. A full compatibility system would be idle most of the time. A lightweight scheme that only activates when data structures change is enough.

### 2. Team size and iteration speed

With a small team (e.g. 5 people) and active development, the priority is to ship features. A heavy migration framework would add overhead without clear payoff. A simple version field plus a small registry of migration functions keeps the cost low.

### 3. Migration logic is case-specific

Each breaking change is different: sometimes a field rename, sometimes a structural change, sometimes a default value. A generic engine that infers migrations from schema diffs is complex and brittle. Hand-written (or generated) migration functions are explicit and easier to reason about.

---

## Why Not "Let the Agent Handle It Every Time"?

| Approach | Pros | Cons |
|----------|------|------|
| **On-demand, per change** | No upfront design; agent writes migration when needed | No baseline to compare against; easy to forget version bump; no shared convention |
| **Current scheme** | Snapshot + version chain; clear baseline; prompts can remind about bumps | Requires discipline to update snapshot when bumping |

The problem with "agent does it every time" is that there is no persistent record of what the structure *was*. The agent sees only the current code. Without a snapshot, it cannot reliably detect "structure changed but version not bumped." The snapshot file provides that baseline.

The prompt is a *checklist and convention*, not the main logic. The real logic lives in `schemaMigrations.ts` and the load/import paths. The prompt helps humans (or tools) follow the convention and avoid forgetting version bumps.

---

## Does This Really Have Advantages?

**Yes, in context:**

- **Low maintenance:** One small file (`schemaMigrations.ts`), one snapshot doc, and a few hooks in load/import. No separate migration engine.
- **Explicit:** Each migration is a named function. Easy to read, test, and debug.
- **Traceable:** Version is stored with data. You can see which diagrams came from which schema.
- **Extensible:** New versions are added by appending to `VERSION_ORDER` and registering a function. No refactor of the core system.

**Limitations:**

- Migrations are manual (or generated with help). Someone must write or review them.
- The snapshot can drift if people forget to update it. The prompt helps reduce that risk.
- No automatic detection of breaking changes; that still relies on process (e.g. running the compatibility check before merge).

---

## Why Not a Comprehensive Universal Compatibility System?

A "universal" system would typically:

- Parse schema definitions (TypeScript interfaces, Prisma, etc.)
- Diff old vs new schema
- Auto-generate migrations
- Support arbitrary nested structures and type changes

**Why we don't do that:**

1. **Complexity:** Our stored data is JSON with nested objects, arrays, and optional fields. Inferring safe migrations from schema diffs is hard. Renames, type changes, and structural changes need human judgment.
2. **Cost vs benefit:** We have a few main structures (save payload, export snapshot, canvas, Prisma models). A generic engine would be a large investment for a small number of migration scenarios.
3. **Overkill for our pace:** We don't change the schema every week. Occasional, targeted migrations are sufficient.
4. **Maintainability:** A custom engine becomes another piece of infrastructure to maintain, document, and debug. A simple registry of functions is easier for a small team to own.

---

## Summary

| Question | Answer |
|----------|--------|
| What is it? | Version field + migration registry + structure snapshot. Load/import run migrations when data is older than current. |
| Why not agent-only? | Need a baseline (snapshot) to detect "changed but not bumped." Agent helps follow the convention, not replace it. |
| Real advantage? | Low overhead, explicit migrations, fits a small team and occasional schema changes. |
| Why not universal? | High complexity and maintenance cost for limited benefit; hand-written migrations are sufficient. |

The scheme is intentionally minimal. It solves the concrete problem—old diagrams and exports must still work—without building a general-purpose migration platform.
