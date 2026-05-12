# Codex Skill Setup

## What This Branch Provides

This branch stores the repo copy of the `plant-gui-compat-check` skill at:

- `.codex/skills/plant-gui-compat-check/`

That makes the skill versioned with the repo and easy to review in pull
requests.

## Important Limitation

`git pull` alone does not make Codex auto-discover a repo skill.

In the current Codex setup, installed skills are loaded from the user's local
Codex home, typically:

- `~/.codex/skills/`
- or `$CODEX_HOME/skills/`

So teammates still need one install step after pulling the branch.

## Simplest Path

If teammates normally start the app from `src` with:

```bash
npm run dev
```

this branch now runs a best-effort Codex skill sync first.

That means the usual development startup also attempts to install or refresh:

- `plant-gui-compat-check`

Rules:

- if the installed local skill already matches the repo copy, nothing changes
- if the repo copy changed, the older local version is backed up first
- if the Codex sync fails, app startup still continues

This makes `npm run dev` the easiest path for most teammates.

## Manual Install

Run this from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-codex-skill.ps1
```

The script copies the repo skill into the user's Codex skill directory. If an
older local copy already exists, it is moved aside into a timestamped backup
folder first.

From `src`, there is also a direct npm command:

```bash
npm run codex:skill
```

After the script finishes:

1. restart Codex
2. invoke the skill by name, for example:

```text
Use $plant-gui-compat-check for a 1N pass on the current branch.
```

## Fallback If The Skill Is Not Installed

If someone has not installed the local skill yet, they can still use the repo
workflow prompt in:

- `docs/usercustom/COMPAT_CHECK_CHAT_DROPIN.md`
