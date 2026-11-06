# Gemini CLI

**English** | [简体中文](gemini-cli.zh-CN.md)

## Native extension

The repository includes `gemini-extension.json`; Gemini discovers the shared `skills/` directory. Install from the repository or a published source:

```sh
gemini extensions install https://github.com/Cyrus-terra/supercoding
# For a Git source, add --auto-update when automatic refresh is desired.
gemini extensions update supercoding
```

Updates take effect after restarting the Gemini CLI session. Use `/extensions list` to inspect the extension. A workspace must be trusted before workspace-local activation.

## Standalone alternative

Copy `skills/supercoding/` to `~/.gemini/skills/supercoding/` or a trusted project skills directory. Use `/skills list` and `/skills reload` after a change. To compare a checked-out source:

```sh
python3 scripts/manage.py check --client gemini --source .
python3 scripts/manage.py update --client gemini --source . --dry-run
```

The shared SessionStart hook only emits a short coding reminder. It never performs extension updates; Gemini's manager owns source copies and updates. Use `gemini extensions install /absolute/path/to/supercoding` to test a local checkout before its changes are pushed. No global context file or permissions are installed. Use `--ref <tag-or-commit>` when you want a fixed source; `--auto-update` is optional and should be an explicit user choice.

Official reference: [extension format and lifecycle](https://geminicli.com/docs/extensions/reference/). Gemini CLI is unavailable locally; shell/configuration checks do not replace a real activation test.
