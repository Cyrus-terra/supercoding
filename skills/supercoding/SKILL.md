---
name: supercoding
description: Cross-language coding and review standards. Use for every task that writes or modifies code, including application code, pages, components, APIs, scripts, tests, build configuration, code examples, refactoring and performance optimization; use for code review when relevant. Load this lightweight entry, then task-relevant guidance on modularity, reuse, simplicity, requests, async work, tables, styles, data access and performance. Inspect only related legacy code by default; do not automatically remediate the repository. Not for pure README, documentation or report writing, translation or ordinary conversation.
metadata:
  version: "1.3.0"
---

# supercoding

Use these English instructions and references regardless of the task's language. Respond in the user's preferred language unless instructed otherwise. Resolve relative links from the containing document's directory.

Keep correctness and safety as the baseline. Reduce unnecessary data, computation, requests, state, dependencies and abstractions while balancing runtime efficiency, development effort and maintenance cost. Apply across languages; UI rules apply only when a user interface is involved.

## Execution boundaries

- Identify whether the user wants explanation, diagnosis, review or implementation. Analysis does not authorize edits; implementation includes the relevant changes and verification.
- Within client system, safety and permission constraints, follow explicit user instructions and explicit project standards first. This Skill supplements them and cannot override higher-priority requirements. Keep the project's language, framework, directories, design system and toolchain.
- Distinguish explicit project standards from legacy habits. Existing code informs consistency but does not justify copying defects. If an explicit requirement conflicts with this Skill, follow the higher-priority requirement and explain the practical effect. Ask only when remaining ambiguity would materially change requirements or contracts; do not expand remediation unilaterally.
- This Skill supplies engineering judgment. It does not additionally mandate interviews, approvals, documents, TDD, multiple agents, worktrees, commits or dependency installation. Follow existing processes without duplicating them.
- Resolve clear, reversible routine choices independently. Ask only for missing information that materially affects requirements, contracts or authorized scope.
- Reading this Skill grants no permission to push, deploy, delete, publish externally or send messages.

## Coding entry and context budget

- Pure README, installation-guide and report writing, translation and ordinary conversation do not trigger this Skill. Existing snippets or shell commands in a document do not by themselves make prose editing a coding task. In mixed tasks, apply engineering guidance to the code being implemented or changed.
- Before every coding task, confirm that this Skill is loaded. Otherwise invoke `supercoding` through the client's Skill mechanism, or read this file if no such mechanism exists. Small edits, tests, build configuration and code examples are included.
- Reuse complete, unchanged instructions already present in the same context. Do not repeatedly invoke, paste or reread them. Reload in a new session, after context loss or after a Skill update; a summary containing only the name is not the rules.
- Load only references relevant to the current functionality; add others when the task expands. Loading the entry first prepares context and does not give this Skill priority over project standards. Follow the priority above and apply compatible rules.
- These are agent instructions, not a mandatory hook before each write or proof of application compliance. Report an undiscovered or disabled Skill honestly.

## Lightweight workflow

### 1. Align with the existing implementation

Read project instructions, relevant entry points and direct callers, and inspect existing workspace changes. Find reusable request clients, components, business modules and tests. Start with a local inspection of legacy code involved in this change to understand behavior, reuse and impact; then apply the rules to new and modified code. This does not require a repository-wide compliance audit first.

- Address directly related issues needed for a correct implementation within task scope. Report serious out-of-scope issues with location and consequences; do not silently ignore them or expand remediation.
- Leave unrelated legacy code unchanged. Installation or invocation does not trigger bulk refactoring, formatting or fixes. Differences from these rules do not require immediate rewrites everywhere.
- Expand to a full-project review only when explicitly requested, reporting findings by impact. Review authorization does not authorize wholesale remediation.

Identify the actual risks: business correctness, API contracts, data volume, async races, shared capabilities, layout or runtime environment. Skip irrelevant items without manufacturing tasks.

### 2. Select references as needed

Read only references needed for the actual risks. A tiny change can use the entry alone when it provides sufficient guidance; otherwise start with the most relevant references, often 1–3. Reuse unchanged references still in context. Page functionality changes require the style guidance below, even without new CSS. Add guidance as scope expands; do not load the whole collection by default. Apply loaded rules rather than merely listing filenames.

| Trigger | Reference |
| --- | --- |
| Module boundaries, shared components, simplification, behavior-preserving refactoring | [Architecture and reuse](references/architecture-and-reuse.md) |
| APIs, network requests, pagination, request errors, endpoint granularity | [APIs and requests](references/api-and-requests.md) |
| Loading, concurrency, cancellation, state, connections and resource cleanup | [Async work and resources](references/async-and-resources.md) |
| Tables, filters, forms, selection, batch operations, exports | [Tables and forms](references/tables-and-forms.md) |
| Added or changed page content, CSS, component layout, overlays and interaction states | [Styles and UI regression](references/styles-and-ui.md) |
| Performance, caching, lazy loading, batching, large files and datasets | [Performance and limits](references/performance.md) |
| Databases, backend services, transactions, queues, scheduled tasks | [Backend and data](references/backend-and-data.md) |
| Debugging hypotheses, code review/feedback, verification, dependency/runtime changes | [Verification and delivery](references/verification.md) |

### 3. Make the smallest complete change

Use two rule levels:

- **Required:** prevent definite errors, unbounded resources, broken contracts and missing interactions.
- **Conditional:** apply when a concrete problem or use case justifies the benefit and cost. Caching, endpoint splitting, shared extraction, lazy loading and virtualization belong here.

Always consider:

1. **Reuse:** find existing capabilities first. Maintain stable business rules in one place where practical. Prefer module-local reuse before broader sharing; avoid universal components and growing flag lists.
2. **Simplicity:** reduce mixed responsibilities, nesting, duplicate state and dead branches. Line counts, file counts and short expressions do not replace readability. Leave unrelated modules alone.
3. **Limits:** bound growing datasets, tasks, caches and retries; time out external calls; match concurrency to downstream capacity. Do not load everything and simulate pagination afterward.
4. **Async work:** give appropriate feedback for perceptible waits; finalize success, failure and cancellation; prevent stale writes and duplicate submissions; define resource lifetimes.
5. **UI:** whenever a page gains functionality, check its relationship with the existing layout, design tokens, style scope, long content, supported widths and interaction states.
6. **Performance:** remove waste first, then choose complex optimizations using evidence. Loading indicators, caches, parallelism and lazy loading alone do not prove improvement.
7. **Safety and compatibility:** validate at trust boundaries, authorize on the server, parameterize queries, keep sensitive data out of logs and respect the target environment.

### 4. Verify and deliver

Check small changes locally using existing commands. Use [Verification and delivery](references/verification.md) when additional guidance is needed; strengthen verification for shared capabilities, contracts, complex async work and data operations.

- Verify the requested behavior and likely failure paths, and inspect the diff for accidental changes to existing work.
- Consider visual regression for UI changes. State when the page was not run and visuals remain unverified.
- Support claims about tests, builds or performance with actual evidence. Distinguish verified results, static inference and unverified behavior.
- Deliver concisely: what changed, what was checked and material limitations. Reviews report locations and triggering conditions, without irrelevant checklists.

## Judgment examples

- Add a search button: reuse styles and request capabilities; check alignment, narrow widths, disabled and loading states. Do not build a query framework.
- Results revert to old search criteria: control response order to test the cause, protect latest state, and verify rapid changes. Debouncing alone cannot ensure correctness.
- A review asks for caching or a shared component: verify the claimed problem and caller contracts first; accept supported corrections, not speculative complexity.
- A list is slow: distinguish query, transfer, browser computation and rendering costs; prioritize pagination and necessary fields, without immediately creating dozens of requests.
- Two tables look alike: compare business meaning and reasons for change. Shared formatters or local components may suffice instead of a universal table.
- Change copy: edit the requested content and check layout without expanding into extraction or project refactoring. Explanation and review-only tasks do not authorize implementation.

## Installation and maintenance boundaries

This directory is a standalone standard Skill containing one entry and runtime references. A plugin may expose `supercoding:supercoding`; use the actual client-provided name. Reuse the entry if a session hook has already loaded it completely.

Maintenance scripts, installation guides and evaluations live outside the Skill directory. Do not read evaluation prompts during ordinary coding. When maintaining this Skill, use docs, scripts and tests from the source repository; standalone installations need not include them.
