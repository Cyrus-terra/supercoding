# Claude Code

**English** | [简体中文](claude-code.zh-CN.md)

## Recommended installation

Use the standalone Skill for a persistent, lightweight installation. Copy `skills/supercoding/` to `~/.claude/skills/supercoding/`, preserving the nine runtime files. The optional repository plugin is useful for a session reminder:

```sh
claude --plugin-dir "/absolute/path/to/supercoding"
```

For a persistent plugin, use these commands inside Claude Code (or replace `Cyrus-terra/supercoding` with the absolute local checkout path for testing):

```text
/plugin marketplace add Cyrus-terra/supercoding
/plugin install supercoding@supercoding
/plugin marketplace update supercoding
/plugin update supercoding@supercoding
```

The first two install; the last two refresh the marketplace and update the installed plugin. Automatic updating is controlled by Claude's marketplace settings, not this Skill. These operations do not remove a previous standalone copy; compare duplicates first.

## Update and verification

Standalone copies do not update automatically. Compare the source first, then use the shared manager from the repository:

```sh
python3 scripts/manage.py check --target "$HOME/.claude/skills/supercoding" --source .
python3 scripts/manage.py update --target "$HOME/.claude/skills/supercoding" --source . --dry-run
```

Run `claude plugin validate` for the plugin source when available, start a new session after changes, and do not overwrite a customized target without `--replace`.

## Limits

The hook is read-only and does not scan projects, fetch updates or change global instructions. For fixed sources, use a reviewed tag/commit checkout and a local marketplace rather than assuming a host-wide pin flag exists. This package's model behavior is not proven by packaging checks.

## Evidence levels

**P:** deterministic manifest/hook checks. **N:** native validation previously passed. **L:** namespaced discovery and SessionStart observed. **M:** no successful model task; API connection blocked. Historical host checks do not validate later edits. See the [shared evidence matrix](../installation.md#verification-evidence).

Official reference: [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference). Plugin/marketplace validation is available locally; previously observed model calls failed to connect.
