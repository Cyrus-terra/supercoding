# Architecture, reuse and simplicity

## Required: define boundaries by responsibility

- Inspect existing boundaries and callers first. Organize code by business responsibility, reasons for change and lifetime, not line counts or a fixed number of layers.
- Presentation composes and renders; business rules and orchestration stay clear; data access has explicit entry points. Small features may keep a little code together without empty wrappers solely for layering.
- Use public interfaces across modules. Avoid accessing private state, reverse dependencies and cycles. Introduce dependency injection only to replace a boundary, isolate side effects or enable actual reuse.
- Make inputs, outputs, errors and side effects understandable through the project's types, data structures or contracts. Do not impose identical patterns across languages.
- Search direct callers before changing a shared interface. Preserve contracts for errors, ordering, nulls, time units and serialization even during an internal refactor.

## Required: reuse before adding

1. Search existing components, utilities, business services and standard-library capabilities.
2. Check that semantics, constraints and extension points match; similar names alone do not justify reuse.
3. Use a suitable implementation directly; consider existing callers when extending it.
4. Extract the smallest shared capability when several places own the same stable rule. Keep module-only capabilities local first.

Repetition signals possible extraction; counts are not a mechanical threshold. Stable rules such as authorization, monetary calculations or state transitions may need one explicit entry even with few callers. Similar appearance does not justify coupling business flows that change for different reasons.

## Conditional: extract components and functions

- Basic components handle general interactions; domain components handle a clear business area; page-local components serve the current page.
- Shared components accept explicit data and events. Avoid hidden dependencies on page routes, specific global stores, implicit selectors or private page requests.
- A defined business-data component may fetch data if its source, lifetime, refresh and error contracts are explicit. Do not force every component to be presentational.
- Prefer composition and a few stable extension points. Reconsider boundaries when flags, special cases and parameters keep growing.
- Preserve focus, authorization, loading, errors and keyboard interaction when extracting components.

## Required: reduce complexity, not line count

- Remove dead branches, unused variables/imports, duplicate computation and obsolete implementations introduced or directly affected by this change. Check dynamic use and external contracts before removal.
- Avoid storing duplicate state reliably derived from existing data. Cache expensive computation only when measurement and usage justify it.
- Use clear names, guard clauses and focused responsibilities to reduce nesting while retaining validation, business meaning and error context.
- Do not trade readable code for complex one-liners, excessive metaprogramming, generic layers or forwarding wrappers.
- Do not add factories, plugin systems, configurable layers or cross-language bridges for speculative future reuse.
- Do not format or rewrite unrelated files to unify style.

## Required: preserve behavior during refactoring

- Name the observable behavior that must stay unchanged. Use existing tests and representative inputs before restructuring; add focused characterization checks only for relevant uncovered risks.
- Compare the same cases before and after: outputs, valid zero/empty/null values, errors, ordering, serialization, and the number/order of observable side effects. Representative callers and UI interactions matter as well as the extracted helper.
- Keep structural changes separate from requested behavior changes so each is reviewable. Do not silently fix a business rule while claiming a behavior-preserving refactor; report an unrelated defect instead of expanding scope.

## Examples

Do: reuse a domain money formatter across two lists; keep separate orchestration for pages with different approval flows.

Avoid: a universal orders-and-employees table with dozens of options, or a separate file for every one-line forwarding function.

## Verification signals

Check direct callers, dependency direction, original behavior and the diff. Explain which rule an extraction centralizes and which callers it affects. Shorter files alone do not establish better quality.
