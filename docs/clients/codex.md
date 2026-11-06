# Codex

**English** | [简体中文](codex.zh-CN.md)

## Native plugin

This repository includes `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. Add the repository marketplace, then install `supercoding` from `/plugins` or the client marketplace UI:

```text
codex plugin marketplace add Cyrus-terra/supercoding
codex plugin marketplace upgrade
codex
/plugins
```

The repository includes this packaging. For local testing, use `codex plugin marketplace add /absolute/path/to/supercoding`. This is a repository marketplace, not an official marketplace listing. Use `codex plugin marketplace upgrade supercoding` to refresh the source, then check the installed plugin in `/plugins`; refresh alone does not prove the installed copy changed.

## Standalone alternative

Copy `skills/supercoding/` to `~/.agents/skills/supercoding/` or `<project-root>/.agents/skills/supercoding/`. Use `/skills` or `$supercoding` to load it. The standalone manager can compare and update a local copy from a checked-out source:

```sh
python3 scripts/manage.py check --client codex --source .
python3 scripts/manage.py update --client codex --source . --dry-run
```

Codex marketplace refresh/update is host-managed. Start a new session after a plugin update. Do not confuse choosing a model with choosing the Skill installation path. To pin a source, use the host's `--ref <tag-or-commit>` marketplace option after a corresponding ref exists; do not assume the newest branch commit is a stable release.

## Evidence levels

**P:** deterministic manifest/marketplace contracts. **N/L/M:** not run; the incomplete local executable prevents native validation, discovery and model tasks. Launcher presence is not integration proof. See the [shared evidence matrix](../installation.md#verification-evidence).

Official references: [plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins.md), [Skill authoring](https://learn.chatgpt.com/docs/build-skills). Packaging is checked locally; the local Codex native executable is missing, so client discovery remains unverified.
