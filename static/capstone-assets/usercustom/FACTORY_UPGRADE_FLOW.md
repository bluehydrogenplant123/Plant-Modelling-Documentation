# Factory Test: Auto-Upgrade Flow for Old Diagrams

For factory delivery, diagrams opened in the app should follow one clear rule:

- Legacy or missing version metadata may be upgraded to `6.0.0`.
- Diagrams tagged with unsupported newer versions must be rejected explicitly.

## Proposed Flow

1. User opens a diagram from DB or imports a snapshot.
2. Backend reads the stored `schemaVersion` or snapshot `version`.
3. If the version is legacy or missing, create a backup copy with an `_oldversion_{version}` suffix.
4. Run the supported migration chain `1.0.0 -> 6.0.0`.
5. Save and return the upgraded diagram.
6. If the version is unsupported, stop and return an explicit error instead of attempting a partial upgrade.

## Backup Naming

- Original: `MyPlant_v1`
- Backup: `MyPlant_v1_oldversion_1.0.0`

If upgrade fails or corrupts data, the backup remains available for manual recovery.

## Evaluation

| Aspect | Benefit |
|--------|---------|
| `Non-destructive` | Original data is preserved before upgrade |
| `Transparent` | User can compare backup and upgraded copy |
| `Factory-friendly` | Old exports can still be opened without hand edits |
| `Bounded upgrade path` | Only `1.0.0 -> 6.0.0` is supported, which keeps risk low |

## Considerations

| Aspect | Note |
|--------|------|
| `Duplicate proliferation` | Backup copies may accumulate and need cleanup policy |
| `Name collision` | Repeated backup names need suffix handling |
| `Unsupported newer tags` | `6.1/6.2/6.3` test artifacts must fail fast, not auto-upgrade |

## Recommendation

- Create the backup before migration.
- Keep the executable compatibility axis narrow and explicit.
- Reject unsupported versions instead of guessing how to migrate them.

## Reusable Solutions

| Tool | Purpose | Fit for Plant-GUI? |
|------|---------|--------------------|
| `json-schema-migrate` | Migrates JSON Schema drafts | No; we migrate app data, not schema specs |
| `Prisma migrate` | Migrates DB schema | Partial; JSON canvas/snapshot data still needs custom logic |
| `Custom registry` | Hand-written migration functions | Yes; explicit, testable, and matches our structures |

## Implementation Checklist

- [ ] On diagram load/import, detect version from canvas or snapshot metadata
- [ ] If version is legacy, create a backup with `_oldversion_{version}`
- [ ] Run `migrateCanvasIfNeeded` / `migrateToLatest`
- [ ] Persist the upgraded `6.0.0` data
- [ ] Reject unsupported versions with a clear error response
- [ ] Keep `VERSION_ORDER` limited to supported steps only
