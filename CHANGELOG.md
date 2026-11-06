# Changelog

Changes are recorded here before release. **Unreleased is not a published version.** Runtime and manifest metadata remain 1.3.0 until a release is prepared; use commit IDs and file hashes to distinguish source revisions with identical metadata.

## Unreleased

### Engineering guidance

- Diagnose falsifiable causes before patching; verify incoming review suggestions against actual contracts.
- Preserve serialization, errors and observable side effects during refactoring.
- Keep performance changes attributable and compare repeated measurements when noise matters.
- Verify complete page journeys and existing controls, not just new widgets.
- Add concrete decision contrasts and cooperate with relevant available specialist Skills without installing or enabling them automatically.

### Evaluation and compatibility evidence

- Provide five runnable fixtures: search races, bounded CSV streaming, partial-batch debugging, behavior-preserving refactoring, and mixed review feedback.
- Keep independent correct implementations outside model workspaces; require known failure identities and passing controls.
- Reject recursive workspace tampering before trusted post-checks. Support selected cases, explicit model/run limits, and neutral comparison-workspace preparation without claiming profile isolation.
- Add offline Linux/macOS/Windows CI and Python 3.9 coverage. Configuring CI is not evidence that the remote matrix passed.
- Separate package checks, native validation, lifecycle discovery and successful model tasks in bilingual installation documentation.

### Packaging and updates

- Provide six client wrappers around one English runtime and optional guarded standalone install/check/update/rollback management.
- Resolve stable GitHub Releases to immutable commits, preserve full backups, and detect local changes and interrupted replacements.
- Add mocked release lifecycle coverage and an explicit-version published-release smoke tool restricted to temporary targets.

### Evidence limits

No public release, successful real-model comparison, automatic-trigger rate, visual result or performance gain is established by these changes. See the [evaluation protocol](tests/evals/protocol.md) and [release checklist](docs/development.md#release-checklist).
