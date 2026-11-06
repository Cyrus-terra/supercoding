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
- The scenario set contains 22 cases and 83 assertions. All cases reference the same English rules; do not count translated variants as independent coverage.

The debugging and review-feedback cases now have lightweight runnable Python fixtures. Refactoring has a Python analogue of the Kotlin scenario; passing it is not Kotlin verification. For debugging, retain the pre-fix reproduction and the experiment that distinguishes competing causes. For review feedback, retain the relevant freshness/authorization requirements and check each accepted or rejected suggestion against them. For refactoring, compare the same behavior and observable side effects before/after; UI cases need an integrated user journey, and performance cases need comparable measurements. These additions remain behavior-unverified until actual client runs provide evidence.

## Behavior evaluation procedure

1. Prepare a minimal runnable fixture isolated from production, using the stack specified by the case. Verbal advice without a fixture is not successful implementation.
2. Run each case in separate contexts with and without the Skill, keeping the model, project, task and checks identical. Do not let one run's edits influence another.
3. Distinguish standalone-only, standalone plus global instructions, and full plugin plus SessionStart configurations. Preserve metadata discovery for automatic loading rather than only injecting instructions; load global rules for that configuration and let the client execute plugin hooks. Check entry use before coding, no full-rule loading for ordinary non-coding work, and reuse of unchanged context.
4. Collect assertion outcomes, correctness, unrelated diffs, reference volume, tool calls and, when available, token usage and measured performance.
5. Actually control completion order for races, failures and concurrency, and render representative widths/states for style cases.
6. Record pass, fail or not evaluated for each assertion, with evidence. Repeat nondeterministic behavior; do not weaken assertions to improve scores.
7. If a language-specific behavior needs evaluation, run a targeted variant in a fresh context and record its language. Confirm responses follow the user's preferred language without translated rule loading; additional languages are not mandatory for every case.

Store results in a test workspace outside the Skill and application repository. Report only actual execution; mark unrun checks as not evaluated.

## Runnable examples

Five fixtures are bundled under `examples/`, with independent correct implementations under `controls/`. Controls are never copied into the model workspace. Four originals contain intentional defects; refactoring starts from valid behavior.

- `search-race/`: a framework-independent JavaScript search controller, with four checks controlling response completion order, stale errors and loading ownership. It has no DOM; it does not evaluate React integration, visual layout or cancellation support.
- `streaming/`: a Python CSV transformer, with checks for a bounded input-to-output window, ordered output, worker limits, timeout forwarding, failure propagation and closed files. The transform callback owns enforcing its downstream I/O timeout. These checks do not measure throughput or prove a constant-memory bound for arbitrary row sizes.

- `debugging/`: seven input rows lose a partial final batch; full/empty batches and storage failures are neighboring cases. A passing fix alone does not prove that the model performed the discriminating experiment.
- `refactoring/`: a passing Python characterization baseline covers serialization, zero/null values, error behavior and audit calls. A control simplifies duplication while retaining those observations; it is not Kotlin execution or an automatic readability score.
- `review-feedback/`: expose filter-key collisions, preserve five-second freshness and separate read/export permissions. Checks establish these behaviors, while the explanation of accepted/rejected suggestions needs trace review.

Streaming checks explicitly force a later row to finish before the first row. No check here measures a production speedup or verifies arbitrary-input memory bounds.

From the repository root:

```sh
# No model requests: validate known original outcomes and all correct controls.
python3 -B scripts/run_examples.py

# Opt in to real model requests using your existing client/account.
python3 -B scripts/run_examples.py --client claude
# Or:
python3 -B scripts/run_examples.py --client codebuddy

# Select one case and an explicit model; client mode is still opt-in.
python3 -B scripts/run_examples.py --client claude --case debugging --model YOUR_MODEL --max-budget-usd 1 --client-timeout 180

# Prepare identical neutral tasks only; no client starts and isolation is NOT established.
python3 -B scripts/run_examples.py --prepare-comparison
```

Requires Python 3.9+ and Node.js 18+. Client mode additionally requires the chosen authenticated client and may consume account quota or incur charges. Each case runs in a fresh temporary directory with the repository plugin, project-only settings, no MCP servers, and only Read/Edit/Skill/Glob/Grep tools allowed. No application repository or installed Skill is modified. The evaluator runs checks externally and saves JSON output and patches outside the repository. Claude mode requests a per-case $1 budget ceiling; CodeBuddy mode caps each case at 16 turns without a monetary ceiling. Both have a 180-second process timeout, and the runner stops after a client error. These controls are not a total-run cost guarantee.

A successful offline runner exit requires exact known failure identities/counts for the four defective originals, a passing refactoring original, and five passing correct controls. Syntax/import errors, missing executables, unexpected test failures and timeouts are not successful reproductions. Client runs must change only the implementation and pass trusted checks. Before any post-check, recursive file/type/content inventory rejects check edits, deletion, extra directories/files and links. The evaluator builds its check directory from held fixture bytes, not candidate checks. This is integrity protection, not an OS sandbox: evaluate candidate code only in an appropriately isolated environment. Inspect the saved tool trace for Skill discovery, entry/reference use and unrelated changes; passing code checks alone does not establish these. The client is explicitly asked to use the Skill, so these examples do not measure automatic triggering or establish a with/without-Skill comparison. Retain sanitized results only; raw client logs may contain local paths or account metadata.

## Comparison preparation and isolation

`--prepare-comparison` produces separate `with-skill`/`without-skill` directories containing identical neutral TASK.txt prompts and originals, plus a `prepared_not_evaluated` manifest. It never starts a client or copies the correct controls. Use proven independent client profiles with the same model, limits and task. Enable the Skill only in the treatment profile. Audit user/global Skills, SessionStart hooks, parent instruction files, workspace trust and MCP exposure before either run. Changing HOME alone does not demonstrate isolation; if contamination cannot be excluded, mark the control invalid and do not report an improvement.

The forced-client mode explicitly invokes the Skill and does not establish automatic loading. It does not grant shell/network tools, so a model's unexecuted debugging experiment remains **not evaluated**, even when the evaluator later verifies the fix. Inspect tool traces for reasoning, selective loading and feedback decisions. Record per-assertion pass/fail/not-evaluated manually with evidence; fixture pass counts are not scenario assertion scores.

## Current offline evidence

Five original/control pairs are executable offline. Runner regression tests cover expected outcomes, infrastructure errors, timeout, recursive tampering/deletion/links, invalid client results, selection and neutral preparation. These deterministic checks do not supply real-model results. Remote CI, actual published-release upgrading and successful real-client tasks are separate unverified layers.

## Observed local results (2026-11-06)

The following records describe earlier runs and their then-current scenario/test counts, not verification of later rule or scenario additions.

| Check | Observed result | Limit |
| --- | --- | --- |
| Repository validation | Passed: 96 entry lines, eight references, 20 scenarios / 72 assertions; 28 deterministic tests passed. | Package/script coverage, not model compliance. |
| Documented installation | Ten shell blocks parsed by sh/bash/zsh; 60 isolated install cases preserved existing directories, files and valid/dangling symlinks. | No network clone or interactive trust flow tested. |
| Search baseline | Three race checks failed; current failure/recovery passed. | Intentional defect reproduced, not a successful fix. |
| CSV baseline | Output-window check failed; failure propagation/file closure passed. | Intentional buffering defect reproduced. |
| Claude Code plugin | Discovered `supercoding:supercoding`; SessionStart hook exited 0. Both model calls returned `API Error: Unable to connect to API (ECONNREFUSED)`. | No implementation edits; model behavior not evaluated. |
| CodeBuddy client attempt | Model tool requests encountered non-interactive permission denial; runner timed out after 180 seconds and stopped. | No implementation edits; no permission-bypass retry. Plugin lifecycle not scored. |

Raw JSON/tool traces and empty implementation patches were retained in temporary evaluation workspaces outside the repository. They are local diagnostic evidence, not published artifacts or durable benchmark data. CodeBuddy's restricted headless invocation did not authorize tools in the tested configuration; the runner does not bypass permissions. Future authorized client runs are still required to complete the model evaluations; the suite now contains five fixtures. No automatic-trigger rate, with/without-Skill improvement, visual regression result or speedup was measured.

## Acceptance priorities

- Correct positive triggering and absence of false triggering on negative tasks.
- Correct behavior with bounded data, concurrency, state and resources.
- Small changes stay small without forced abstractions, documents, dependencies or multiple agents.
- Added page functionality checks existing layout and style scope.
- Reports distinguish measured results, static reasoning and unverified behavior.
- Tasks apply the shared English rules and responses follow the user's preferred language.

Rerun affected scenarios after rule changes. Before releases, cover triggering, frontend, backend, scripts, resistance to overengineering and evidence honesty. Without actual benchmarks, promise no fixed speedup or token-saving percentage.
