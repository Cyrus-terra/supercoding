# supercoding evaluation protocol

Use only when maintaining or evaluating the Skill, not during every application task. [evals.json](evals.json) is this package's scenario format, with no claimed platform compatibility. Maintain this protocol and the single scenario set in English.

## Three verification levels

1. **Structural validation:** run `scripts/validate_skill.py` to check metadata, entry links, resources and scenario structure. This establishes static structure only.
2. **Static scenario inspection:** check that rules cover each prompt, expected reference and assertion. This does not establish actual model compliance.
3. **Client behavior evaluation:** run tasks with a real client in isolated fixtures/project copies; retain prompts, diffs, tool records and actual checks before scoring assertions.

Passing the first two levels is not passed behavior evaluation. Skill maintenance does not authorize paid services, subagents, publication or edits to real application repositories.

## Use the scenario set

- `should_trigger` indicates expected automatic loading. Negative cases such as ordinary translation should not trigger; still honor explicit named invocation and determine actual scope.
- `files` identifies fixture paths the evaluator must prepare, not bundled files or paths available on the current machine.
- `reference_files` identifies supporting resources relative to the Skill root, not a rigid exact read set. Reasonable equivalent routing is acceptable.
- `assertions` score observable behavior, code results and honest reporting, not similarity of wording.
- The scenario set contains 19 cases and 69 assertions. All cases reference the same English rules; do not count translated variants as independent coverage.

## Behavior evaluation procedure

1. Prepare a minimal runnable fixture isolated from production, using the stack specified by the case. Verbal advice without a fixture is not successful implementation.
2. Run each case in separate contexts with and without the Skill, keeping the model, project, task and checks identical. Do not let one run's edits influence another.
3. Distinguish standalone-only, standalone plus global instructions, and full plugin plus SessionStart configurations. Preserve metadata discovery for automatic loading rather than only injecting instructions; load global rules for that configuration and let the client execute plugin hooks. Check entry use before coding, no full-rule loading for ordinary non-coding work, and reuse of unchanged context.
4. Collect assertion outcomes, correctness, unrelated diffs, reference volume, tool calls and, when available, token usage and measured performance.
5. Actually control completion order for races, failures and concurrency, and render representative widths/states for style cases.
6. Record pass, fail or not evaluated for each assertion, with evidence. Repeat nondeterministic behavior; do not weaken assertions to improve scores.
7. If a language-specific behavior needs evaluation, run a targeted variant in a fresh context and record its language. Confirm responses follow the user's preferred language without translated rule loading; additional languages are not mandatory for every case.

Store results in a test workspace outside the Skill and application repository. Report only actual execution; mark unrun checks as not evaluated.

## Acceptance priorities

- Correct positive triggering and absence of false triggering on negative tasks.
- Correct behavior with bounded data, concurrency, state and resources.
- Small changes stay small without forced abstractions, documents, dependencies or multiple agents.
- Added page functionality checks existing layout and style scope.
- Reports distinguish measured results, static reasoning and unverified behavior.
- Tasks apply the shared English rules and responses follow the user's preferred language.

Rerun affected scenarios after rule changes. Before releases, cover triggering, frontend, backend, scripts, resistance to overengineering and evidence honesty. Without actual benchmarks, promise no fixed speedup or token-saving percentage.
