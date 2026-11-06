# OpenClaw

**English** | [简体中文](openclaw.zh-CN.md)

## Native plugin

The repository includes `openclaw.plugin.json` and a dependency-free `index.js`. Install from a Git source or local checkout:

```sh
openclaw plugins install git:github.com/Cyrus-terra/supercoding
openclaw plugins list
openclaw plugins inspect supercoding
openclaw plugins update supercoding
```

For local development, use `openclaw plugins install --link /absolute/path/to/supercoding` instead. Review trust prompts rather than bypassing them. The repository includes the packaging; local linked copies follow your checkout but do not fetch Git changes. The plugin exposes the shared `skills/` root. Changes apply to the Gateway according to its reload behavior; use `openclaw plugins inspect supercoding --runtime --json` and start a new chat when necessary. This repository is not claiming an npm or ClawHub publication.

## Standalone alternative

Copy `skills/supercoding/` to the active agent's `skills/supercoding/`, then inspect with `openclaw skills list` and `openclaw skills check`. For a checked-out source:

```sh
python3 scripts/manage.py check --client openclaw --source .
python3 scripts/manage.py update --client openclaw --source . --dry-run
```

Do not keep duplicate copies at managed, workspace and plugin paths without checking precedence. Newer hosts accept an explicit Git `@<tag-or-commit>` selector; inspect your installed version's help before relying on a newer syntax. The default manager path is `~/.openclaw/skills/supercoding`, not necessarily an individual agent's workspace.

## Evidence levels

**P:** manifest and dependency-free JS import checks. **N/L/M:** native validation, Gateway discovery and model task not run. Importing index.js does not test Gateway parsing/registration. See the [shared evidence matrix](../installation.md#verification-evidence).

Official references: [plugin install/update](https://docs.openclaw.ai/tools/plugin), [manifest](https://docs.openclaw.ai/plugins/manifest). The local host is 2026.5.7 and may differ from current docs. Plain metadata/long-description parsing and actual Gateway discovery remain version-sensitive; this package's JS entry/manifest checks are not a live Gateway test.
