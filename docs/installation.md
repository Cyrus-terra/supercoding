# Installation and activation

**English** | [简体中文](installation.zh-CN.md)

## Choose one installation method

Install a native plugin/extension when you want the client's install and update management. Use the standalone Skill when you only need portable rules, without a hook or runtime dependency. Keep one discovered installation per client; shared `.agents/skills` directories can be visible to multiple clients.

Clone `https://github.com/Cyrus-terra/supercoding.git` or extract its ZIP. Commands in this guide run from the repository root. The repository contains the client packaging; no official marketplace, npm or ClawHub publication is claimed.

## Client compatibility

Official formats checked on **2026-11-06**. Each client has separate installation, invocation, update and troubleshooting instructions:

| Client | Native packaging in this repository | Guide |
| --- | --- | --- |
| Claude Code | `.claude-plugin/` and marketplace | [Claude Code](clients/claude-code.md) |
| CodeBuddy | `.codebuddy-plugin/` and marketplace | [CodeBuddy](clients/codebuddy.md) |
| Codex | `.codex-plugin/` and `.agents/plugins/marketplace.json` | [Codex](clients/codex.md) |
| Gemini CLI | `gemini-extension.json` | [Gemini CLI](clients/gemini-cli.md) |
| Hermes Agent | `.hermes-plugin/` registration and manifest | [Hermes](clients/hermes.md) |
| OpenClaw | `openclaw.plugin.json`, `package.json`, `index.js` | [OpenClaw](clients/openclaw.md) |

All six load the same [English runtime Skill](../skills/supercoding/SKILL.md). Model choice, including using DeepSeek through a host, does not change the installation format. A package/adapter check is not proof of model compliance; see [observed results and limits](../tests/evals/protocol.md). Codex's local executable is incomplete and Gemini CLI is absent; those clients' live integration remains unverified.

## Verification evidence

Do not collapse these independent levels: **P** (package/adapter tests), **N** (native validator), **L** (real discovery/lifecycle), and **M** (successful model task). The current local evidence is:

| Client | P | N | L | M |
| --- | --- | --- | --- | --- |
| Claude Code | Manifest, hook output and POSIX expansion | Previously passed | Namespaced discovery + hook observed | API connection blocked |
| CodeBuddy | Manifest, hook output and POSIX expansion | Previously passed | Not scored | Headless tool permissions blocked |
| Codex | Manifest/marketplace contracts | Not run | Not run: incomplete local executable | Not run |
| Gemini CLI | Manifest + simulated substitution | Not run | Not run: CLI unavailable | Not run |
| Hermes Agent | Fake-context registration/first turn | Not run | Real plugin session not run | Not run |
| OpenClaw | Manifest + dependency-free JS import | Not run | Gateway discovery not run | Not run |

Historical native/client observations are not revalidation of later source changes. Deterministic adapter checks are not host execution. Windows hook startup, remote CI results, and automatic-trigger/model improvement claims need separate evidence. See the [protocol and historical records](../tests/evals/protocol.md).

## Install the standalone Skill

Copy the complete `skills/supercoding/` directory, including its eight references, into the client's skills root. Preserve existing directories and symlinks. On Windows, manual copying needs no Python. The final layout is `skills/supercoding/SKILL.md`, without an extra nested repository directory.

| Client argument | Default user destination |
| --- | --- |
| `claude` | `~/.claude/skills/supercoding` |
| `codebuddy` | `~/.codebuddy/skills/supercoding` |
| `codex` | `~/.agents/skills/supercoding` |
| `gemini` | `~/.gemini/skills/supercoding` |
| `hermes` | `~/.hermes/skills/supercoding` |
| `openclaw` | `~/.openclaw/skills/supercoding` |

With Python 3.9+, the management tool provides guarded installation and records file hashes outside the runtime folder. Choose **one** client:

```sh
python3 -B scripts/manage.py install --client codex --source .
```

For custom profiles, project-only use, remote hosts or containers, pass an explicit target where the agent runs:

```sh
python3 -B scripts/manage.py install --target "/absolute/project/.agents/skills/supercoding" --source .
```

Install stops if the target exists. It does not change global instructions, trust settings or plugin caches. Symlink targets and symlinked ancestors are refused: compare and update the actual shared source separately. On macOS, use canonical `/private/...` paths if a temporary location is exposed through the OS `/var` symlink. The manager itself refuses the system `/tmp` alias for this safety check; a canonical temporary path is required.

## Optional session plugin

For Claude Code and CodeBuddy, local session loading remains available:

```sh
claude --plugin-dir "/absolute/path/to/supercoding"
codebuddy --plugin-dir "/absolute/path/to/supercoding"
```

This lasts for the session, not a permanent installation. The short SessionStart reminder reads local files and emits JSON; it does not fetch updates or scan projects. Gemini uses the same reminder through its extension hook; Hermes uses its own registration hook. Codex and OpenClaw load the rules through their native Skill registration without this shell reminder.

Hooks require `python3` (Python 3.9+) and a compatible shell. Windows hook startup has not been verified; use standalone files if unavailable. Follow client trust prompts.

## Version checks, updates and rollback

**Native plugins:** use the client-specific guide. Marketplace refresh and updating an installed plugin may be separate operations. Automatic updates depend on the host's settings; supercoding never pulls code at session startup.

**Standalone copies:** use `scripts/manage.py` from a trusted source checkout. `check` and `--dry-run` do not write local files. Both query the latest stable GitHub Release unless you supply `--source`:

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
python3 -B scripts/manage.py update --client codex
```

The release must be published with a `vX.Y.Z` tag matching the entry's version. The tool resolves the tag to an immutable commit and reads only the nine runtime files from its bounded archive. No published Release means a clear error, without silently falling back to a branch. Network/rate-limit errors also fail explicitly. To compare and update offline from a checkout:

```sh
python3 -B scripts/manage.py check --client codex --source .
python3 -B scripts/manage.py update --client codex --source . --dry-run
python3 -B scripts/manage.py update --client codex --source .
```

Use `--version X.Y.Z` instead of `--source` to choose a specific published stable Release. Updates reject downgrades; restore a retained backup to go back.

A first migration from a manual copy, or local changes since the previous managed installation, requires explicit acceptance. Review the preview, then use:

```sh
python3 -B scripts/manage.py update --client codex --source . --replace
python3 -B scripts/manage.py rollback --client codex
```

`--replace` does not merge custom rules: it preserves the **entire** old directory as a backup and installs the new canonical files. Keep customizations separately if you want to reapply them. Files with links, special types or excessive size are refused rather than followed or discarded.

The sibling `.supercoding-state/` directory holds receipts, backups, lock and transaction journal. Keep it for rollback and do not copy it inside the Skill. Backups are retained until you intentionally archive or remove them. Rollback verifies their file hashes and preserves the displaced installation; an unmanaged backup stays unmanaged. Start a new session after changing rules.

### Interrupted operations

A normal failure attempts to restore the previous installation. A process interruption between directory renames may leave an unfinished `transaction.json`; operations detect that journal. Run `rollback` to restore the recorded verified backup, including when the target is temporarily absent. The OS releases the management lock when the process exits; do not delete lock/state files to bypass a live operation.

This is a journaled replacement, not a claim of crash-proof or power-loss-atomic filesystem transactions. If initial installation was interrupted before any backup existed, or state/backup validation fails, inspect the printed `.supercoding-state/` paths and restore manually; the tool refuses to guess or destroy data.

## Use for every coding task

Discovery does not enforce default use. Add the following to the instruction file your client actually loads, preserving existing content. Installation does not modify it:

| Client | User/project instructions |
| --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` or project `CLAUDE.md` |
| CodeBuddy | `~/.codebuddy/CODEBUDDY.md` or project `CODEBUDDY.md` |
| Codex | `AGENTS.md` in the applicable scope |
| Gemini CLI | `GEMINI.md` in the applicable scope |
| Hermes / OpenClaw | The active workspace/profile's supported context file |

```markdown
## supercoding

Use supercoding before writing or modifying code, including scripts, tests, build configuration and runnable examples; use for code review when relevant.
Reuse complete unchanged rules already in context; otherwise invoke the actual available Skill name or read its SKILL.md.
Load only relevant references; tiny tasks can use the entry alone. Page functionality changes need style guidance, reusing it if already loaded.
Within client constraints, explicit user requirements and project standards take priority. Inspect related legacy code only; no automatic repository-wide audit or remediation.
Skip pure README/document/report writing, translation and conversation. In mixed tasks, apply coding guidance only to the code portion.
```

Plugins may expose `supercoding:supercoding`; standalone usually exposes `supercoding`. Use the actual available name. These are agent instructions, not write interception or additional tool permissions.

## Languages and verification

Runtime rules and references are English; responses follow the user's language. README and installation guides are bilingual, while maintenance/evaluation content stays English.

In a new session, confirm one discoverable entry, try a small coding task, and observe only relevant references loading. Continue similar work to check context reuse; try prose-only editing and translation to check exclusion. These model behaviors require observation, beyond deterministic package tests.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Missing Skill | Check the complete runtime layout, active profile/workspace, allowlists and disabled entries; restart/reload as the client requires. |
| Duplicate rules/reminders | Compare standalone, project, plugin and shared installations before removing confirmed duplicates. |
| Target already exists | Use `check`/`update --dry-run`; never treat first-install commands as upgrades. |
| Unmanaged or modified target | Review changed files, then explicitly use `update --replace` to keep a full backup. |
| Symlink refusal | Inspect the shared source and its users; update it separately, without replacing the symlink. |
| No stable release / offline | Use a trusted local checkout with `--source`; no silent branch fallback exists. |
| Lock / unfinished journal | Let the active operation finish; after a process interruption use verified rollback, without deleting state. |
| Old behavior | Verify the loaded path, use the appropriate client updater or standalone tool, then start a new session. |
| Hook fails | Check Python, shell, trust and path expansion; standalone requires no hook. |

When reporting an issue, include client/version, OS, installation mode, relevant paths, steps and exact error, without credentials or private content.
