# supercoding

**English** | [简体中文](README.zh-CN.md)

**Cross-language engineering standards for AI coding assistants. Build with reuse, clear boundaries and performance in mind.**

supercoding is an **Agent Skill** that guides coding decisions across architecture, APIs, async state, UI, backend data and verification. It helps assistants consider how a change fits the existing project, behaves under failure and scales with more data—not just whether the new code runs.

**One lightweight entry. Eight references loaded as needed. Your existing stack and conventions.** Native plugin/extension packaging is included for Claude Code, CodeBuddy, Codex, Gemini CLI, Hermes Agent and OpenClaw.

[Core capabilities](#core-capabilities) · [A feature from request to verification](#a-feature-from-request-to-verification) · [Quick start](#quick-start) · [Eight focused references](#eight-focused-references) · [Updates](#updates) · [Verification](#verification)

## Core capabilities

The rules address decisions that can turn a working feature into a maintenance, correctness or performance problem:

| When development runs into… | What supercoding guides the assistant to do |
| --- | --- |
| Duplicated business logic, tangled modules or growing shared components | Find existing capabilities, split by responsibility, share stable rules and preserve caller contracts. Keep abstractions proportional to actual reuse. |
| Slow lists, oversized responses or too many small requests | Locate query, transfer and rendering costs; use server pagination and necessary fields; choose endpoint splitting, aggregation or bounded batches by usage and cost. |
| Stale results, stuck loading or duplicate submissions | Define operation ownership for data, loading and errors; guard against out-of-order completion; handle cancellation, duplicate prevention and cleanup. |
| A new control that crowds or breaks an existing page | Reuse the design system and local styles; check wrapping, long content, overlays, focus and failure/retry through the affected user journey. |
| Large files, unbounded jobs or caches with incorrect results | Bound submitted work and output buffers, stream end to end, define cache keys and expiry, and preserve tenant/permission boundaries. |
| Guess-based fixes, risky refactors or conflicting review advice | Test falsifiable causes, preserve observable behavior and side effects, verify feedback against contracts, and report the evidence actually obtained. |

These are conditional engineering decisions: caching, lazy loading, component extraction and API splitting need a concrete reason. They are not changes to apply mechanically to every task.

## A feature from request to verification

**Task: add a status filter to an existing orders page.**

The guidance connects several parts of that change:

1. **Reuse the project.** Inspect the current filters, request client, table and API before creating another component or request wrapper.
2. **Keep query behavior consistent.** Coordinate the selected status with pagination and applicable selection rules; check that the backend filters and paginates the requested data.
3. **Protect current state.** Rapid filter changes must not let an older response replace current results, show an obsolete error or clear a newer request's loading state.
4. **Control data cost.** Return list-summary fields, load large details when opened, and check directly affected queries for per-row calls or unnecessary work.
5. **Fit the existing page.** Check the new filter beside current actions, including long labels, the narrowest supported width, loading, empty results and retry feedback.
6. **Verify the complete journey.** Change filters quickly, move between pages, reproduce a failure and retry, and confirm existing controls still behave correctly.

This illustrates the rules' intended coverage, not a measured model result. Apply the checks relevant to the requested scope; identify backend work outside a frontend-only task rather than silently expanding it.

The same approach applies beyond pages: a CSV job needs bounded work and ordered output; a shared helper needs caller and side-effect checks; a database change needs consistency and deployment considerations.

## Built for everyday development

- **Selective context:** load the entry, then references for the actual task. Reuse complete unchanged instructions already in context; tiny changes can use the entry alone.
- **Project-aware reuse:** follow the existing language, framework, request infrastructure and design system. Inspect related legacy code and apply guidance to new or modified parts.
- **Focused changes:** simplify responsibilities and duplication while preserving contracts. Keep unrelated cleanup and speculative frameworks outside the task.
- **Evidence-led verification:** use checks appropriate to the risk. Separate measured performance, passing behavior checks, static reasoning and unverified results.
- **Composable guidance:** combine relevant available specialist Skills without duplicating their workflows. English rules serve tasks in any language; responses follow the user's preference.

Pure README/document writing, translation and ordinary conversation do not trigger the Skill. It adds no mandatory interviews, design documents, TDD, agents, worktrees or approval workflow; follow your project's existing process.

## Quick start

Choose **one** native plugin/extension or standalone installation per client. All clients share the same runtime rules. Model choice, including DeepSeek through a supported host, does not change the installation format.

### Install

For a managed standalone copy, get the source and install with Python 3.9+. This example targets Codex:

```sh
git clone https://github.com/Cyrus-terra/supercoding.git
cd supercoding
python3 -B scripts/manage.py install --client codex --source .
```

Without Python, copy the complete `skills/supercoding/` directory into your client's skills root, preserving existing installations. Client-specific plugin and standalone instructions:

| Client | Available installation | Guide |
| --- | --- | --- |
| Claude Code | Marketplace plugin, local session plugin, standalone | [Claude Code](docs/clients/claude-code.md) |
| CodeBuddy | Marketplace plugin, local session plugin, standalone | [CodeBuddy](docs/clients/codebuddy.md) |
| Codex | Repository marketplace plugin, standalone | [Codex](docs/clients/codex.md) |
| Gemini CLI | Native extension, standalone | [Gemini CLI](docs/clients/gemini-cli.md) |
| Hermes Agent | Native plugin, standalone | [Hermes](docs/clients/hermes.md) |
| OpenClaw | Native plugin, standalone | [OpenClaw](docs/clients/openclaw.md) |

See the [shared installation guide](docs/installation.md) for default paths, Windows, project scope and troubleshooting. Packaging is provided in this repository; no official marketplace, npm or ClawHub listing is claimed. Check the [client verification matrix](docs/installation.md#verification-evidence) for observed integration evidence and limits.

### Use it

Start a new client session, confirm `supercoding` or `supercoding:supercoding` is available, and try:

```text
Use supercoding to add a status filter to the existing orders page.
Follow the project's conventions and verify the affected behavior and layout.
```

Other task examples:

- “Investigate why search results sometimes revert after changing filters.”
- “Refactor this duplicated business logic while preserving behavior and side effects.”
- “Review this API change for unnecessary data, query cost and caller compatibility.”
- “Make this large-file job process data with bounded memory and concurrency.”

Discovery alone does not ensure use on every coding task. For default use, add the [coding instructions](docs/installation.md#use-for-every-coding-task) to the context file your client actually loads.

## Eight focused references

The [runtime entry](skills/supercoding/SKILL.md) routes directly to eight guidance modules. They are references within one Skill, not eight separate installations.

| Reference | Decisions and failure paths covered |
| --- | --- |
| [Architecture and reuse](skills/supercoding/references/architecture-and-reuse.md) | Responsibilities and dependency direction; existing capability discovery; shared business rules; component extraction; simpler control flow; behavior-preserving refactoring, including errors, serialization and side-effect order. |
| [APIs and requests](skills/supercoding/references/api-and-requests.md) | Server pagination and deterministic ordering; summary/detail fields; endpoint splitting and aggregation; shared transport/domain APIs; timeouts, cancellation, normalized errors and bounded idempotent retries. |
| [Async work and resources](skills/supercoding/references/async-and-resources.md) | Local loading and recovery states; latest-request ownership; stale successes/errors/finalizers; duplicate submissions; optimistic rollback; bounded concurrency, backpressure and resource lifetimes. |
| [Tables and forms](skills/supercoding/references/tables-and-forms.md) | Filters and pagination; row identity and selection scope; batch actions and exports; validation, submission feedback and retained input; long content and state consistency. |
| [Styles and UI](skills/supercoding/references/styles-and-ui.md) | Existing tokens and components; scoped styles; supported widths, long labels and wrapping; overlay clipping and stacking; keyboard/focus behavior; loading/error states and integrated page regression. |
| [Performance](skills/supercoding/references/performance.md) | Bottleneck attribution and comparable baselines; bounded data, work and buffers; cache keys, isolation and invalidation; on-demand loading, virtualization and prefetch tradeoffs; measured benefits and resource costs. |
| [Backend and data](skills/supercoding/references/backend-and-data.md) | N+1 reads, field selection and query plans; parameterized queries; server authorization and tenant boundaries; transaction scope, idempotency and conflicts; background jobs, migration impact and bounded diagnostic logs. |
| [Verification and review](skills/supercoding/references/verification.md) | Falsifiable debugging hypotheses; discriminating experiments; evidence-backed review findings and feedback decisions; risk-based tests; dependency/runtime compatibility; honest completion and performance claims. |

## Existing projects and scope

Within client system, safety and permission constraints, explicit user requirements and project standards take priority over general Skill guidance. Existing code informs consistency; existing defects are not standards to copy.

Opening a project does not trigger an audit. Coding tasks inspect related code; a full review needs an explicit request, and review alone does not authorize fixes. The Skill is not an MCP server and grants no permission to install dependencies, push, deploy or publish.

## Updates

Native plugins/extensions update through their client; automatic updates depend on its settings. Session hooks only provide local reminders and never fetch updates.

Managed standalone copies support read-only checks/previews, full-directory backups, local-change protection and rollback. From the source checkout:

```sh
python3 -B scripts/manage.py check --client codex
python3 -B scripts/manage.py update --client codex --dry-run
```

Online checks require a matching stable GitHub Release. If unavailable or offline, add `--source .` to use a trusted local checkout. Read the [update and recovery guide](docs/installation.md#version-checks-updates-and-rollback) before applying changes.

See [CHANGELOG](CHANGELOG.md) for rule and tooling changes. Before release, source revisions can share version metadata; compare commit IDs and changed files as well as the version label.

## Verification

The repository includes deterministic package/update tests and five runnable fixture/control pairs: search races, bounded CSV streaming, partial-batch debugging, behavior-preserving refactoring and mixed review feedback.

From the repository root:

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 -B scripts/run_examples.py
```

These checks establish package and evaluator behavior, not automatic triggering, improved model output, visual correctness or performance gains. Successful real-model comparisons, remote CI and Windows hook startup remain unverified. See the [client evidence matrix](docs/installation.md#verification-evidence) and [evaluation protocol with observed results](tests/evals/protocol.md).

Contributions should address a concrete failure, include observable evaluation evidence and preserve selective loading. See the [maintenance guide](docs/development.md). README and installation guides are bilingual; runtime, maintenance and evaluation materials stay English-only.

## License

[MIT](LICENSE). Commercial use, modification and distribution are permitted with the required copyright and permission notices. Provided without warranty.
