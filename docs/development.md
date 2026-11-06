# Repository maintenance

## Separate runtime and development material

- `skills/supercoding/` contains one English entry and eight English runtime references, and can be copied independently.
- `scripts/` contains read-only maintenance tools, not required context for normal coding.
- `tests/` contains deterministic tests and evaluation scenarios. Scenario prompts are test data, not instructions for the current task.
- `hooks/` contains the lightweight plugin reminder, without application scanning or write interception.
- `.claude-plugin/` and `.codebuddy-plugin/` contain manifests; other capabilities live at repository root.
- `docs/` serves installers and maintainers. Do not create unused assets, agents, commands, adapters or dependencies just to imitate another repository.

## Content, language and versions

Keep entries lean and reference modules directly reachable in one step. Use document-relative Markdown links; runtime files cannot depend on outer repository files, so standalone copies remain complete.

Keep one English `SKILL.md` and eight English references for every task language. Do not maintain translated runtime entries or reference collections. Responses follow the user's preferred language without changing instruction priority or authorized scope.

Only README and installation instructions are bilingual, with reciprocal links between `.md` and `.zh-CN.md`. Keep these pairs synchronized. Maintenance documentation, evaluation protocol, scenario data and runtime rules are maintained in English only.

`evals.json` contains 19 scenarios and 69 assertions, with `reference_files` pointing to shared English rules. Maintain one scenario set rather than translated copies. Additional language-specific evaluation is optional when a concrete need arises.

Rules follow project language/framework constraints without forcing abstractions or legacy rewrites as best practice. Loading order does not establish instruction priority.

Version metadata lives in the entry and both plugin manifests; synchronize all three when releasing a version change. Do not invent repository URLs, authors, licenses or compatibility claims. The maintainer decides licensing and distribution channels before publication.

## Checks

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

To validate an installed standalone directory:

```sh
python3 -B scripts/validate_skill.py "<installed-skill-root>"
```

The validator supports the simple YAML subset used here; it is not a general YAML parser or official certification. Tests cover valid/invalid inputs, English runtime completeness, bilingual README/installation links and scenario validity, hook output, scope and path behavior.

See the [evaluation protocol](../tests/evals/protocol.md). Passing automated tests establishes structure and script behavior, not automatic usage, better generated code or improved performance. Those require actual client runs and runnable business fixtures.

## Relationship to Superpowers

The directory separation is inspired by Superpowers: runtime Skills in `skills`, development checks in `tests`, session entry in `hooks`, and tools/guides in `scripts`/`docs`. Its source code, brand, contribution policies and development process were not copied. This repository need not inherit all its adapters or historical documents.
