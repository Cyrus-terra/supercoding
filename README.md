# supercoding

**English** | [简体中文](README.zh-CN.md)

**Coding standards for AI assistants: reuse what exists, keep changes focused, and check performance and UI quality.**

An Agent Skill for frontend, backend, scripts, tests and build configuration. It helps assistants handle real engineering details—stale search results, oversized API responses, reusable business rules, loading states and page layouts—using your project's stack.

One lightweight entry, eight references loaded only when relevant. Reuse unchanged rules already in context; tiny changes can use the entry alone. Pure README/document writing, translation and ordinary conversation do not trigger it.

## Install for your client

Choose **one** native plugin/extension or standalone Skill per client. All six share the same runtime rules; model choice, including DeepSeek through a supported host, does not change the installation format.

| Client | Available installation | Instructions |
| --- | --- | --- |
| Claude Code | Marketplace plugin, local session plugin, standalone | [Claude Code](docs/clients/claude-code.md) |
| CodeBuddy | Marketplace plugin, local session plugin, standalone | [CodeBuddy](docs/clients/codebuddy.md) |
| Codex | Repository marketplace plugin, standalone | [Codex](docs/clients/codex.md) |
| Gemini CLI | Native extension, standalone | [Gemini CLI](docs/clients/gemini-cli.md) |
| Hermes Agent | Native plugin, standalone | [Hermes](docs/clients/hermes.md) |
| OpenClaw | Native plugin, standalone | [OpenClaw](docs/clients/openclaw.md) |

Get the source for local installation, testing or standalone management:

```sh
git clone https://github.com/Cyrus-terra/supercoding.git
cd supercoding
```

For example, install a managed standalone copy for Codex with Python 3.9+:

```sh
python3 -B scripts/manage.py install --client codex --source .
```

No Python? Copy `skills/supercoding/` to your client's skills directory, preserving existing installations; see the [shared installation guide](docs/installation.md) for paths, Windows, project scope and default activation. Native plugins are managed by each client. New packaging must be pushed before remote install commands can retrieve it; this repository does not claim an official marketplace, npm or ClawHub listing.

## First use

Start a new client session, confirm `supercoding` or `supercoding:supercoding` is available, and try:

```text
Use supercoding to add a status filter to the orders page.
Reuse the existing request layer and components. Handle pagination, loading
and errors, and check the controls against the existing page layout.
```

Discovery alone does not require use on every coding task. For default use, add the [coding instructions](docs/installation.md#use-for-every-coding-task) to the context file your client actually loads. English and Chinese tasks use the same English rules; responses follow your preferred language.

## Updates without silent overwrites

Native plugin/extension updates belong to the client; automatic updates depend on its settings. Session hooks never fetch or install updates.

Standalone copies support read-only checking and previews, validated updates with full backups, local-change protection and rollback:

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
python3 -B scripts/manage.py update --client codex
python3 -B scripts/manage.py rollback --client codex
```

These commands require a matching stable GitHub Release. Before one is published, or offline, add `--source .` to check/update from a trusted local checkout. Manual or customized installations require explicit `update --replace` after review; symlinks are refused. See [updates and recovery](docs/installation.md#version-checks-updates-and-rollback).

## What it covers

| Area | Practical guidance |
| --- | --- |
| Reuse and simpler code | Find existing capabilities; extract stable shared rules; keep responsibility boundaries clear without universal components or speculative abstractions. |
| APIs and data | Reuse request clients; paginate at the data source; load necessary fields; consider N+1 queries, transactions, idempotency and authorization. |
| Async work and interactions | Scope loading and errors; protect against stale responses and duplicate submissions; keep filters, pagination and selection consistent. |
| UI quality | Check layout, style scope, design tokens, long content, supported widths, focus and interaction states whenever page functionality changes. |
| Performance and verification | Bound data and concurrency; choose streaming, caching or lazy loading when justified; support results with relevant checks and measurements. |

The [runtime entry](skills/supercoding/SKILL.md) links directly to all eight reference modules. The assistant reads project constraints and related code, loads the necessary guidance, makes the smallest complete change, then verifies it. There is no mandatory TDD, multi-agent, worktree or approval workflow added by this Skill.

## Existing projects

Explicit user requirements and project standards take priority over general Skill guidance, within client system, safety and permission constraints. Keep the existing stack, request layer and design system; legacy defects are not standards to copy.

Opening a project does not trigger an audit. Coding tasks inspect related legacy code and apply guidance to new or modified parts. A full review requires an explicit request, and review alone does not authorize fixes.

## Evidence and development

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Deterministic checks cover packaging, local links, shared runtime completeness, adapters and standalone update/recovery behavior. They do not establish model compliance or performance gains. Claude plugin discovery/hook execution was observed previously, but API connection failure blocked implementation; a CodeBuddy example was blocked by headless permissions. Codex's local executable is incomplete and Gemini CLI is absent; their live integration remains unverified. Windows hook startup remains unverified.

Two [runnable examples and recorded results](tests/evals/protocol.md) cover search races and bounded CSV processing. See the [maintenance guide](docs/development.md) for release and verification details. README and installation guides are bilingual; runtime, maintenance and evaluation materials stay English-only.

## License

[MIT](LICENSE). Commercial use, modification and distribution are permitted with the required copyright and permission notices. Provided without warranty.
