# Installation and activation

**English** | [简体中文](installation.zh-CN.md)

## Choose one installation method

Use the full plugin when you want a SessionStart coding reminder, or the standalone Skill for clients using standard Skill directories. Avoid installing both and creating duplicate entries/reminders.

This repository includes Claude Code and CodeBuddy manifests, not implemented integrations for Cursor, Codex or other clients. Hook JSON and configuration have been checked locally; actual discovery, trust confirmation and lifecycle behavior still need testing in each client.

## Load a local plugin for development

Run either client from your application project. Replace `<repo-root>` with the full repository path, retaining quotes:

```sh
codebuddy --plugin-dir "<repo-root>"
claude --plugin-dir "<repo-root>"
```

This loads the plugin for a session, not permanently. Follow client trust prompts without bypassing them. Start a new test session after updates.

Capabilities are discovered from `skills/` and `hooks/hooks.json`. The command uses `${CLAUDE_PLUGIN_ROOT}`; CodeBuddy's built-in documentation describes support for this alias. The hook emits only a short reminder and the entry path, not the full rules on every turn. It does not scan projects or write global files.

Python 3.9+ must be available as `python3`. If unavailable on Windows, use standalone mode. This version supplies no verified Windows launcher and does not claim universal plug-and-play support.

## Install the standalone Skill

Copy the complete `skills/supercoding/` directory into a client user- or project-level skills directory, keeping the name `supercoding`. Examples:

- CodeBuddy user level: `~/.codebuddy/skills/supercoding/`
- Claude Code user level: `~/.claude/skills/supercoding/`

These are destination layouts, not overwrite instructions. Inspect, compare and back up existing directories, symlinks or custom rules first. Copy only runtime files; do not put repository tests, scripts or docs inside the Skill.

Standalone mode does not include the session hook. Append the following to client-wide instructions or the chosen project's instructions, preserving existing content:

> Use supercoding before every task that writes or modifies code. Reuse the complete entry when unchanged and still in context; otherwise invoke the actual client-provided Skill name or read its SKILL.md. Load only task-relevant references and check styles for page changes. Respect client constraints, explicit user requirements and explicit project standards. Inspect related legacy code only by default, without automatic repository remediation. Do not trigger for ordinary conversation or non-coding file tasks.

Plugins may expose `supercoding:supercoding`; standalone mode usually exposes `supercoding`. Use the actual available name.

## Rule and response languages

[SKILL.md](../skills/supercoding/SKILL.md) and all eight references use one shared English rule set for every task language. The assistant responds in the user's preferred language; Chinese requests require no translated entry or language routing. Copy the complete runtime directory as provided.

README and installation instructions provide English/Chinese switches. Runtime rules, maintenance documentation, evaluation protocol and the single scenario set are maintained in English.

## Check that it works

1. In a new session, confirm the Skill is discoverable without duplicate versions.
2. In plugin mode, check the SessionStart reminder for Python, path or JSON errors.
3. Submit a small coding task and observe entry loading before coding, with only relevant references.
4. Continue similar work in the same session; confirm unchanged rules are reused.
5. Try ordinary translation and confirm no engineering workflow is triggered.
6. Try Chinese and English coding tasks in separate sessions; confirm both use the shared English rules while responses follow the user's preferred language.

These are real client behaviors requiring observation; structural and script tests cannot replace them.

## Troubleshooting

| Symptom | What to check and do |
| --- | --- |
| Skill does not appear | Confirm the path ends in `skills/supercoding/SKILL.md`, with the eight files in `references/` beside it. Avoid `supercoding/supercoding/SKILL.md` nesting or copying the repository root as the Skill. Start a new session and check whether the client has disabled the Skill. |
| Skill appears but is not used for every coding task | Discovery alone does not enforce use. Add the default coding instructions from the README to the appropriate user/project instruction file, preserving existing rules. Invoke the actual available Skill name to check that it is accessible. |
| Duplicate entries or repeated reminders | Check user-level and project-level installations, session plugin loading and symlinks. Choose one installation method and compare versions before removing a confirmed duplicate; do not blindly delete a shared symlink target. |
| Install command says the target already exists | The README commands intentionally stop without overwriting. Inspect the existing directory or symlink and compare it with the source. Preserve customizations and back up before an explicit update. |
| `python3` is missing, too old, or the hook fails | Plugin hooks require Python 3.9+ available to the client process as `python3`. Check `python3 --version` in the launch environment, plugin trust/hook permissions and client error output. Standalone mode does not require Python; Windows hook startup remains unverified. |
| Plugin is absent in a later session | Pass `--plugin-dir` again with the absolute repository-root path in quotes. The path must contain the plugin manifest, `skills/` and `hooks/`; passing only the runtime Skill directory does not load the full plugin. This option is session-scoped. |
| Hook reports a missing entry | Check that the plugin copy includes `skills/supercoding/SKILL.md` and has not been moved or partially copied. Restore the complete repository layout rather than editing the reported path blindly. |
| Source was updated but installed behavior is old | Copied standalone files do not update automatically. Compare and synchronize the installed runtime directory, retaining customizations, then start a new session. In plugin mode, confirm the loaded repository path and restart with `--plugin-dir`. |
| English rules or hook text appear during a Chinese task | English runtime rules and technical output are expected. Ask for Chinese responses if needed; no translated Skill installation is required. |

If the issue persists, record the client/version, operating system, installation method, directory layout, steps and exact error. Redact credentials and private data. A passing repository check can help identify packaging issues, but does not establish that the real client loaded the plugin or followed the rules.

## Commands, updates and existing versions

See the [README](../README.md) for first-install commands, global instruction paths and usage examples. No marketplace manifest is included; `--plugin-dir` is session loading, not permanent installation.

Copied standalone files do not follow source updates automatically. Compare source and installed directories, preserve customizations and synchronize explicitly. Restart plugin sessions with the loading argument after updating source.

Before switching modes, inspect existing directories and cross-client symlinks. Avoid duplicates and do not overwrite or delete a version in use. Removing a plugin does not remove manually added global instructions; maintain those separately.
