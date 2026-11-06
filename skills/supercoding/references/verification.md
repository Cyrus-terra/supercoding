# Verification, compatibility and delivery

## Choose checks by risk

| Change | Priority checks |
| --- | --- |
| Copy or a single local style | Relevant content, actual layout/states and necessary existing checks |
| Business logic or bug fix | Key behavior, reproduction path, relevant tests or targeted regression |
| Shared component or utility | Representative callers, existing contracts, necessary integration checks |
| API or data structure | Inputs/outputs, authorization, callers, pagination, errors and compatibility |
| Async work, caching or submission | Response order, failure, cancellation, duplicates, invalidation and cleanup |
| Database, batch writes or migration | Consistency, rollback, scale and release constraints in an isolated environment |
| Dedicated performance work | Comparable baseline, target metrics, correctness and resource tradeoffs |
| Dependencies, build or runtime | Types/compilation/build, relevant integration and target compatibility |

Use existing project commands and tools. Start locally and expand by impact; run full checks when required by the project. Do not repeatedly rerun identical checks without new changes or unresolved risks.

## Required: valuable tests and truthful results

- Follow the project's testing process. This Skill neither mandates test-first for every edit nor exempts existing requirements.
- Prefer tests for real business behavior, historical defects and high-risk boundaries. Do not test language built-ins, only mock calls or mirrored implementation details.
- Use appropriate substitutes at external boundaries while checking real core behavior where possible. Do not add unrelated production switches for testing convenience.
- Inspect the diff, unused content and pre-existing workspace changes to avoid overwriting others' work or mixing unrelated changes.
- Compilation, lint, tests and builds establish different things. A build does not prove interaction, visual correctness or production performance.
- State when commands were not run, tools/environments are missing or checks failed. Distinguish pre-existing failures from introduced ones without hiding either.

## Required: respect the actual runtime

- Check language versions, runtimes, frameworks, databases and browsers before using new syntax, APIs or libraries.
- Require concrete value from new dependencies. Compare existing packages and the standard library; assess size, maintenance, licensing and compatibility without adding a large library for a small feature.
- Respect lockfiles and package managers. Do not arbitrarily upgrade, downgrade or replace global toolchains.
- Dependency additions, installations and network operations follow current client authorization; this Skill does not relax it.
- Combine enabled compatibility Skills without duplicating workflows. When a tool is unsupported, use an available equivalent check and explain its limits.

## Keep delivery concise

For implementation, report:

- Completed behavior and key changes, with useful source locations.
- Checks actually executed and their results.
- Material unverified areas, real blockers or necessary follow-up, without invented disclaimers.

For review or diagnosis, provide evidence: location, triggering conditions, consequences and necessary recommendations. Distinguish established issues from hypotheses. Do not implement unrequested fixes.

For performance work, also report measurement conditions, before/after metrics and tradeoffs; without measurements, report only the measures taken.

If a UI change was not run, state that visual verification is incomplete. A current-browser check cannot stand in for an unavailable target device.

## Quality boundaries of this Skill

Structural checks establish only that package structure and evaluation data meet this package's checks. Representative scenarios and actual client evaluation are needed to establish code quality, triggering accuracy and acceptable overhead. Never describe static scenario inspection as passed model behavior evaluation.
