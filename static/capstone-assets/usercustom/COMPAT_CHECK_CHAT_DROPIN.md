# COMPAT_CHECK Chat Drop-In

If the local skill `plant-gui-compat-check` is installed, use it.
Otherwise read and execute `docs/Compatibility/COMPAT_CHECK.md` now.

If I did not already specify the mode, ask me exactly one compact question and
wait:

`Reply with 1N, 1Y, 2N, or 2Y.`

Meaning:

- `1` = development tweak/test
- `2` = ready for full compatibility
- `N` = compatibility patch only
- `Y` = also evaluate whether revert/rollback is the better path

If the answer ends with `Y`, also read:

- `docs/usercustom/developer-rollback-prompts.md`

Then continue and produce the default `summary table` from
`docs/Compatibility/COMPAT_CHECK.md`.

If I do not reply with a mode, do not block the whole check. Assume `1N`,
state that this was assumed, and still return the summary table first.

Classify the change before deep checks:

- `schema-only`
- `library-additive`
- `library-rename`
- `library-delete`
- `mixed`

If the change includes Excel/library updates, treat `compat-check` as required
before release or shared testing.

For any `library-*` or `mixed` result, if the old-data handling rule was not
already stated, ask one compact follow-up and get the developer decision:

- additive: explicit `library refresh` / `upgrade`
- delete or rename: warning + auto-unverify + manual reselection

For this repo's single compatibility version axis, recommend bumping
`CURRENT_SCHEMA_VERSION` for Excel/library changes that affect saved-diagram
compatibility, even when the persisted shape does not change.

When DB access is available, always do the baseline DB truth check that matches
the classification. Only expand to deeper diagram/TP inspection when the
classification or the evidence requires it. Do not force the widest possible DB
scan by default.

After the table, include an `Options` section that contains:

- 3-5 short action options with concrete operation names, with the recommended
  option first
- one option named `Show detailed compatibility table`
- one `Workflow shortcuts` line listing `1N`, `1Y`, `2N`, `2Y`
- include `D` = show the detailed table for the same pass
