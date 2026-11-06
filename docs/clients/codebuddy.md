# CodeBuddy

**English** | [简体中文](codebuddy.zh-CN.md)

## Recommended installation

Copy `skills/supercoding/` to `~/.codebuddy/skills/supercoding/` for a persistent standalone Skill. For a session reminder, load the repository plugin:

```sh
codebuddy --plugin-dir "/absolute/path/to/supercoding"
```

For a persistent plugin, run these inside CodeBuddy, or add the absolute checkout path for local testing:

```text
/plugin marketplace add Cyrus-terra/supercoding
/plugin install supercoding@supercoding
/plugin marketplace update supercoding
/plugin update supercoding@supercoding
```

The last two commands refresh metadata and update the installed copy separately. Automatic update behavior belongs to CodeBuddy's settings; the hook never downloads code. Avoid a second standalone installation.

## Update and verification

Standalone files are snapshots. Compare and preview before updating:

```sh
python3 scripts/manage.py check --target "$HOME/.codebuddy/skills/supercoding" --source .
python3 scripts/manage.py update --target "$HOME/.codebuddy/skills/supercoding" --source . --dry-run
```

Use `codebuddy plugin validate` when available. Start a new session after an update. A modified or unmanaged target requires explicit `--replace`; symlink targets are refused.

## Limits

The plugin reminder is read-only. It does not grant permissions, audit the repository, or silently update installations. For fixed sources, use a reviewed tag/commit checkout with a local marketplace. The manifest/marketplace passed the installed client's validator; previous headless implementation attempts were blocked by tool permissions, not completed model evaluations.

## Evidence levels

**P:** deterministic manifest/hook checks. **N:** native validation previously passed. **L:** lifecycle not scored. **M:** no successful task; headless tool permission denial/timeout. No bypass retry is implied. See the [shared evidence matrix](../installation.md#verification-evidence).

The command and manifest contract was checked against CodeBuddy's bundled plugin and marketplace documentation. Use the installed client's help if your version differs.
