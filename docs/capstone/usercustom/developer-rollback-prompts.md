# Developer Rollback Prompt Templates

This rollback flow is intentionally developer-only.

- It is not exposed in the dashboard.
- It currently supports only top-level normal diagrams (`type = 0`).
- It works by promoting an existing upgrade backup back to the active name, while archiving the current active graph as a new backup.

## 1. List rollback candidates

Use this prompt with the AI agent:

```text
Check rollback candidates for diagram "<diagram name or id>".

Use:
npm run dev:rollback:list -- "<diagram name or id>"

If the name is ambiguous, rerun with the diagram id.
Return a compact table with:
- backupId
- backupName
- sourceVersion
- schemaVersion
- createdAt

Then stop and ask me which backupId to activate.
```

If the diagram belongs to a different user account, add either:

```text
--user-id "<user id>"
```

or:

```text
--user-email "<user email>"
```

## 2. Dry-run a rollback

Use this before a real rollback:

```text
Dry-run a rollback for diagram "<diagram name or id>" to backup "<backup id>".

Use:
npm run dev:rollback:activate -- "<diagram name or id>" "<backup source version or backup id>" dry-run

Show me:
- which diagram will become the archived backup
- the archived backup name that will be created
- which backup will become active
- whether the restored diagram will still need schema upgrade afterwards
```

## 3. Execute the rollback

After confirming the backup id, use:

```text
Rollback diagram "<diagram name or id>" to backup "<backup id>".

Use:
npm run dev:rollback:activate -- "<diagram name or id>" "<backup source version or backup id>"

After it finishes, tell me:
- the archived backup name for the previous active diagram
- the promoted diagram id
- the promoted diagram schema version
- whether it will still open as read-only until upgraded
```

## Notes

- On this repo's Windows/npm setup, positional arguments are more reliable than `--diagram` style flags, so the examples above use positionals.
- Rollback does not rewrite the restored backup to the latest schema.
- If the promoted backup is an older schema like `6.2.0`, it will become the active diagram again, but the app will still open it in read-only mode until you upgrade it.
- This flow is aimed at development/debug recovery, not end-user self-service.
- Phase 2 rollback expects a self-contained full graph:
  - root net
  - nested subnetwork instances
  - referenced blueprint diagrams
- Older backups created before blueprint freezing may be rejected because they still point at live blueprint diagrams.
- If the active graph shares blueprint diagrams with other active nets, rollback is also blocked, because an in-place restore would mutate shared blueprint history.
