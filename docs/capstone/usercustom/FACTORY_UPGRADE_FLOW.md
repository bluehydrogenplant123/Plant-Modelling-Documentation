# Factory Test: Auto-Upgrade Flow for Old Diagrams

For factory delivery, diagrams (nets) opened in the app should auto-upgrade from older schema versions to the latest. This document describes the proposed flow and evaluation.

---

## Proposed Flow

```
User opens diagram (from DB or import)
        │
        ▼
┌───────────────────────────────┐
│ Detect version (schemaVersion  │
│ or version in snapshot)       │
└───────────────────────────────┘
        │
        ▼
   Version < CURRENT?
        │
   Yes  │  No
        │   └──► Load as-is
        ▼
┌───────────────────────────────┐
│ 1. Create backup: duplicate    │
│    diagram with name suffix    │
│    "_oldversion_6.0" (or       │
│    whatever the old version)   │
│ 2. Run migration chain        │
│    6.0 → 6.1 → ... → 6.5      │
│ 3. Save upgraded diagram      │
│ 4. Load upgraded diagram      │
└───────────────────────────────┘
```

**Key rule:** Same major version (6.x) can all upgrade to latest (e.g. 6.5). Different major (e.g. 5.x → 6.x) may need explicit handling.

---

## Backup Naming

Before upgrading, create a copy with a safe name:

- Original: `MyPlant_v1`
- Backup: `MyPlant_v1_oldversion_6.0`

If upgrade fails or corrupts data, the backup remains. User can revert manually.

---

## Evaluation

### Strengths

| Aspect | Benefit |
|--------|---------|
| **Non-destructive** | Original preserved; no data loss from failed upgrade |
| **Transparent** | User sees both old and new; can compare or rollback |
| **Factory-friendly** | Testers can open old exports without manual steps |
| **Same-major upgrade** | 6.0, 6.1, 6.2 → 6.5 is straightforward; one migration chain |

### Considerations

| Aspect | Note |
|--------|------|
| **Duplicate proliferation** | Each open creates a backup; may need cleanup policy (e.g. "keep last N backups" or "delete after successful upgrade") |
| **Name collision** | If `MyPlant_oldversion_6.0` already exists, need suffix (e.g. `_oldversion_6.0_2`) |
| **When to create backup** | Option A: Before migration (always). Option B: Only if migration fails (simpler, but no pre-failure backup) |

### Recommendation

- **Create backup before migration** — safest for factory test where reliability matters.
- **Consider auto-delete** of `_oldversion_*` copies after N days or after user confirms upgrade success, to avoid clutter. Can be a follow-up.

---

## Alternative Approaches

| Approach | Pros | Cons |
|----------|------|-----|
| **Backup before upgrade (proposed)** | Safe; reversible | Extra copy per open |
| **Upgrade in-place, no backup** | Simple | Risk of corruption with no rollback |
| **Prompt user: "Upgrade?" before opening** | User control | Friction for factory testers |
| **Read-only mode for old versions** | No risk of bad save | User cannot edit; poor UX |

The proposed flow (backup + auto-upgrade) balances safety and usability for factory delivery.

---

## Reusable Solutions (Research)

| Tool | Purpose | Fit for Plant-GUI? |
|------|---------|--------------------|
| **json-schema-migrate** | Migrates JSON Schema spec (draft-04 → draft-07) | No — we migrate app data, not schema specs |
| **Prisma migrate** | DB schema migrations (tables, columns) | Partial — we use it for Prisma; canvas/snapshot are Json fields, need custom logic |
| **Custom registry (current)** | Hand-written migration functions per version | Yes — explicit, testable, fits our structures |

**Conclusion:** No drop-in library for "migrate arbitrary JSON app data between versions." The current `schemaMigrations.ts` registry is appropriate. The backup-before-upgrade flow is application logic, not a generic library concern.

---

## Implementation Checklist

- [ ] On diagram load (GET /diagrams/:id): detect version from canvas or metadata
- [ ] If version is `&lt; CURRENT`: create backup diagram with `_oldversion_{version}` suffix
- [ ] Run `migrateCanvasIfNeeded` (already exists)
- [ ] Persist upgraded diagram (PUT) or return migrated data for display
- [ ] Ensure VERSION_ORDER includes all 6.x steps (6.0 → 6.1 → ... → 6.5) when applicable
