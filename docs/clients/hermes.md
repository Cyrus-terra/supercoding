# Hermes Agent

**English** | [简体中文](hermes.zh-CN.md)

## Native plugin

The repository includes `.hermes-plugin/plugin.yaml` and a registration module. Install and enable it through Hermes:

```sh
hermes plugins install Cyrus-terra/supercoding --enable
hermes plugins list
hermes plugins update supercoding
```

The plugin registers `supercoding:supercoding` as an on-demand Skill. Start a new session after installation or update. Newer Hermes versions provide `hermes plugins doctor`; older versions can inspect `hermes plugins list` and startup diagnostics. The repository includes the adapter. To test locally, copy the checkout to the active profile's plugin directory only when the destination does not exist, then explicitly enable it; do not overwrite an installed plugin.

## Standalone alternative

Copy `skills/supercoding/` to `~/.hermes/skills/supercoding/` for the default profile, or the active profile's skills directory. Check with `hermes skills list`, start a new session or `/reset`, and invoke `/supercoding` with a coding task. Unlike plugin registration, standalone installation does not use the namespaced plugin name. The local manager can update a copy from a checked-out source:

```sh
python3 scripts/manage.py check --client hermes --source .
python3 scripts/manage.py update --client hermes --source . --dry-run
```

The plugin does not write state into its install tree and does not update itself during `pre_llm_call`. The installed CLI's update command pulls the installed source; no universally supported ref-pinning flag is claimed. Use a reviewed fixed checkout/standalone source when reproducibility is required.

## Evidence levels

**P:** fake-context registration and first-turn callback checks. **N/L/M:** native validation, live plugin lifecycle and model task not run. Fake context is not a Hermes session. See the [shared evidence matrix](../installation.md#verification-evidence).

Official reference: [Hermes plugin authoring and bundled Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins). Registration and first-turn behavior are covered by an isolated fake context; a real Hermes model session remains unverified.
