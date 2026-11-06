# supercoding

**English** | [简体中文](README.zh-CN.md)

**Engineering judgment for AI coding assistants. Reuse what exists. Keep changes focused. Verify what matters.**

supercoding is a cross-language **Agent Skill**, with native plugin/extension packaging for six clients. It helps assistants handle stale search results, oversized API responses, shared business rules, loading states and page layouts using your project's stack. It is not an MCP server or a mandatory development methodology.

One lightweight entry, eight references loaded only when relevant. Pure README/document writing, translation and ordinary conversation do not trigger it.

[How it works](#how-it-works) · [Installation](#installation) · [First use](#first-use) · [What's inside](#whats-inside) · [Updates](#updates) · [Verification and contributing](#verification-and-contributing)

## How it works

1. **Understand the existing implementation.** Read project constraints, related code and callers; find suitable components, request clients and tests before adding new ones.
2. **Load guidance for the actual risk.** UI work needs layout checks; async work needs state ownership; optimization needs bottleneck evidence. Reuse complete, unchanged rules already in context. Tiny changes can use the entry alone.
3. **Make the smallest complete change.** Preserve contracts, bound growing work and cover relevant failure paths. Do not turn a small feature into a framework or an unrelated cleanup.
4. **Verify before claiming success.** Test the reported trigger and affected behavior. Separate measured results, static reasoning and checks that could not run.

For a slow list, that means locating query, transfer or rendering costs—not automatically adding a cache. For similar tables, it means sharing stable business rules—not forcing both pages into a universal component. For a bug, it means testing a cause—not stacking guesses.

supercoding adds no mandatory interviews, design documents, TDD, multi-agent, worktree or approval workflow. Follow your project's existing process.

## Installation

Choose **one** native plugin/extension or standalone Skill per client. All six share the same runtime rules; model choice, including DeepSeek through a supported host, does not change the installation format.

| Client | Available installation | Instructions |
| --- | --- | --- |
| Claude Code | Marketplace plugin, local session plugin, standalone | [Claude Code](docs/clients/claude-code.md) |
| CodeBuddy | Marketplace plugin, local session plugin, standalone | [CodeBuddy](docs/clients/codebuddy.md) |
| Codex | Repository marketplace plugin, standalone | [Codex](docs/clients/codex.md) |
| Gemini CLI | Native extension, standalone | [Gemini CLI](docs/clients/gemini-cli.md) |
| Hermes Agent | Native plugin, standalone | [Hermes](docs/clients/hermes.md) |
| OpenClaw | Native plugin, standalone | [OpenClaw](docs/clients/openclaw.md) |

For a managed standalone copy, get the source and install with Python 3.9+. This example targets Codex:

```sh
git clone https://github.com/Cyrus-terra/supercoding.git
cd supercoding
python3 -B scripts/manage.py install --client codex --source .
```

Without Python, copy `skills/supercoding/` to your client's skills directory without overwriting an existing installation. See the [shared installation guide](docs/installation.md) for paths, Windows, project scope and troubleshooting. Plugin/extension packaging is available in this repository; no official marketplace, npm or ClawHub listing is claimed. Live-client verification limits are recorded in the client guides.

## First use

Start a new client session, confirm `supercoding` or `supercoding:supercoding` is available, and try:

```text
Use supercoding to add a status filter to the orders page.
Reuse the existing request layer and components. Handle pagination, loading
and errors, and check the controls against the existing page layout.
```

Discovery alone does not ensure use on every coding task. For default use, add the [coding instructions](docs/installation.md#use-for-every-coding-task) to the context file your client actually loads. English and Chinese tasks use the same English rules; responses follow your preferred language.

## What's inside

The [runtime entry](skills/supercoding/SKILL.md) routes tasks directly to eight focused references. These are guidance modules, not eight independently installed Skills.

| Reference | What it helps the assistant decide |
| --- | --- |
| [Architecture and reuse](skills/supercoding/references/architecture-and-reuse.md) | Where responsibilities belong, what is genuinely reusable, and how to simplify while preserving behavior and side effects. |
| [APIs and requests](skills/supercoding/references/api-and-requests.md) | How much data to return, when to split or aggregate endpoints, and how to reuse request/error handling. |
| [Async work and resources](skills/supercoding/references/async-and-resources.md) | Who owns loading and results, how to prevent stale writes or duplicate submissions, and when resources are released. |
| [Tables and forms](skills/supercoding/references/tables-and-forms.md) | How filtering, pagination, selection, validation, batch actions and exports stay consistent. |
| [Styles and UI](skills/supercoding/references/styles-and-ui.md) | How new functionality fits the existing layout, supported widths, accessibility and complete user journey. |
| [Performance](skills/supercoding/references/performance.md) | Where the bottleneck is, how to bound data/concurrency, when caching or lazy loading helps, and whether measurements justify the change. |
| [Backend and data](skills/supercoding/references/backend-and-data.md) | How queries, transactions, authorization, idempotency and background work preserve correctness at scale. |
| [Verification and review](skills/supercoding/references/verification.md) | How to test debugging hypotheses, assess review feedback, choose relevant checks and report evidence honestly. |

## Existing projects and boundaries

Explicit user requirements and project standards take priority over general Skill guidance, within client system, safety and permission constraints. Keep the existing stack, request layer and design system; legacy defects are not standards to copy.

Opening a project does not trigger an audit. Coding tasks inspect related legacy code and apply guidance to new or modified parts. A full review requires an explicit request, and review alone does not authorize fixes. Loading the Skill grants no permission to push, deploy or publish.

## Updates

Native plugins/extensions update through their client; automatic updates depend on its settings. Session hooks never fetch or install updates.

Managed standalone copies support read-only checks/previews, full-directory backups, local-change protection and rollback. For example, from the source checkout:

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
```

Online check/update requires a matching stable GitHub Release. Before one is published, or offline, add `--source .` to use a trusted local checkout. Review [update and recovery instructions](docs/installation.md#version-checks-updates-and-rollback) before applying changes; customized installations require explicit replacement, and symlink targets are refused.

## Verification and contributing

From the repository root:

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Deterministic checks cover packaging, local links, adapters and standalone update/recovery behavior. They do **not** establish automatic triggering, model compliance, visual correctness or performance gains. Real-client integration and model behavior require separate evidence; see [evaluation scenarios, runnable examples and observed limits](tests/evals/protocol.md).

Improvements should address a concrete failure, include an observable evaluation case, and preserve selective loading. See the [maintenance guide](docs/development.md) for checks and release requirements. README and installation guides are bilingual; runtime, maintenance and evaluation materials stay English-only.

## License

[MIT](LICENSE). Commercial use, modification and distribution are permitted with the required copyright and permission notices. Provided without warranty.
