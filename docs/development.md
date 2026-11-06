# Repository maintenance

## Separate runtime and development material

- `skills/supercoding/` contains one English entry and eight English runtime references, and can be copied independently.
- `scripts/` contains validation, standalone management and opt-in evaluation tools; none are required context for normal coding.
- `tests/` contains deterministic tests, evaluation scenarios and two intentionally defective runnable fixtures under `tests/evals/examples/`. Scenario prompts are test data, not instructions for the current task; fixture failures are expected until a client implements the requested fix.
- `hooks/` contains the lightweight plugin reminder, without application scanning or write interception.
- `.claude-plugin/`, `.codebuddy-plugin/`, `.codex-plugin/`, `.hermes-plugin/`, `gemini-extension.json` and `openclaw.plugin.json` contain client manifests; other capabilities live at repository root.
- `docs/` serves installers and maintainers. Do not create unused assets, agents, commands, adapters or dependencies just to imitate another repository.

## Content, language and versions

Keep entries lean and reference modules directly reachable in one step. Use document-relative Markdown links; runtime files cannot depend on outer repository files, so standalone copies remain complete.

Keep one English `SKILL.md` and eight English references for every task language. Do not maintain translated runtime entries or reference collections. Responses follow the user's preferred language without changing instruction priority or authorized scope.

Only README and installation instructions are bilingual, with reciprocal links between `.md` and `.zh-CN.md`. Keep these pairs synchronized. Maintenance documentation, evaluation protocol, scenario data and runtime rules are maintained in English only.

`evals.json` contains 20 scenarios and 72 assertions, with `reference_files` pointing to shared English rules. Maintain one scenario set rather than translated copies. Additional language-specific evaluation is optional when a concrete need arises.

Rules follow project language/framework constraints without forcing abstractions or legacy rewrites as best practice. Loading order does not establish instruction priority.

Version metadata lives in the entry and every client manifest; synchronize all declarations when releasing a version change. `scripts/manage.py` only manages standalone copies; native plugin updates remain host-managed. Do not invent repository URLs, authors, licenses or compatibility claims. The maintainer decides licensing and distribution channels before publication.

## Checks

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 -B scripts/manage.py --help
```

To validate an installed standalone directory:

```sh
python3 -B scripts/validate_skill.py "<installed-skill-root>"
```

The validator supports the simple YAML subset used here; it is not a general YAML parser or official certification. Tests cover valid/invalid inputs, English runtime completeness, bilingual README/installation links and scenario validity, hook output, scope and path behavior.

Use `python3 -B scripts/run_examples.py` to reproduce the two fixture baselines without model requests. Client mode is an explicit opt-in; see the [evaluation protocol](../tests/evals/protocol.md) for requirements, quotas, retained traces and evidence boundaries. Passing automated tests establishes structure and script behavior, not automatic usage, better generated code or improved performance. Those require actual client runs and runnable business fixtures.

## Releases and standalone updates

The runtime stays dependency-free; `scripts/manage.py` is an optional Python 3.9+ source-checkout tool. Its check/preview path is read-only, including disabling bytecode-cache writes. `install`, `update` and `rollback` use a sibling `.supercoding-state/`, an OS-released advisory lock, full-directory backups and a transaction journal. Do not claim the two directory renames are a single crash-atomic operation. Keep backups until an operator explicitly archives them; do not put state inside plugin install trees or the Skill.

For releases, synchronize the entry, all client manifests and any marketplace version fields, run all deterministic checks, then review the diff and obtain separate authorization for commit/push/tag/publication. Publish a stable GitHub Release tagged `vX.Y.Z` with matching runtime metadata. The manager accepts only stable numeric versions, resolves the release tag to a full commit, and reads the nine permitted files from that immutable archive. No Release means failure with a local `--source` alternative, never a default-branch fallback. HTTPS, byte/member/expanded-size limits and path/link checks are transport/package protections, not cryptographic author signatures. Hash receipts detect subsequent local changes, not a malicious publisher.

Run updater tests against temporary directories and fixed responses; never use the actual user Skill directory as a fixture. Actual plugin discovery requires separate client observation. Native plugin managers own their update caches, refresh behavior and permission prompts.

## Relationship to Superpowers

The directory separation is inspired by Superpowers: runtime Skills in `skills`, development checks in `tests`, session entry in `hooks`, and tools/guides in `scripts`/`docs`. Its source code, brand, contribution policies and development process were not copied. This repository need not inherit all its adapters or historical documents.
