# supercoding

**English** | [简体中文](README.zh-CN.md)

**Engineering standards for AI coding assistants, with a focus on performance, reuse, simplicity, and UI quality.**

Use supercoding for feature development, bug fixes, refactoring, performance optimization, and code review across frontend, backend, scripts, tests, and build configuration. It follows your existing stack and loads relevant guidance as needed, balancing runtime efficiency, development effort, and maintenance cost.

`supercoding` is an Agent Skill with plugin entry points for Claude Code and CodeBuddy. It guides an assistant's implementation and verification through instructions; it is not a repository-wide automatic fixer or a code compliance scanner.

**Language:** You can describe tasks in English or Chinese. The assistant reads the same English rules and responds in your preferred language, unless you request otherwise. README and installation instructions are bilingual; runtime rules and maintenance/evaluation materials are English-only.

## Features

| Area | Guidance |
| --- | --- |
| Modularity and decoupling | Define boundaries by responsibility, keep dependency direction clear, and avoid circular dependencies; do not split files merely to meet a line limit |
| Reuse and shared components | Look for existing capabilities first, extract stable shared rules, and distinguish basic, domain, and page components without building universal components |
| Simpler code | Reduce duplicate conditions, dead branches, redundant state, and unnecessary wrappers while preserving readability and avoiding speculative abstractions |
| APIs and requests | Reuse the request layer, organize APIs by domain, paginate growing datasets, and balance aggregation with on-demand fields and detail endpoints |
| Async interactions | Scope loading indicators appropriately; handle errors, empty states, duplicate submissions, cancellation, stale responses, and resource cleanup |
| Tables and forms | Keep filters and pagination consistent; handle stable row keys, cross-page selection, batch operations, last-page deletion, validation, and imports/exports |
| UI and styles | Check existing layout, style scope, design tokens, long content, supported widths, overlays, and interaction states whenever a page gains functionality |
| Performance | Locate the bottleneck before choosing caching, lazy loading, virtualization, batching, streaming, or bounded concurrency; support claims with evidence |
| Backend and data | Address N+1 queries, data volume, transactions, idempotency, authorization boundaries, queue backpressure, and background jobs |
| Verification and delivery | Select tests, builds, and visual checks based on impact; distinguish observed results, static reasoning, and unverified behavior |

The rules are language- and framework-independent. The assistant must still respect project versions, dependencies, design systems, and deployment constraints. This does not mean every technology stack has been individually integrated or evaluated.

## How it works

```text
Receive a coding task
  → Load the lightweight entry, or reuse it if still available and unchanged
  → Read project constraints and relevant code; look for existing capabilities
  → Load the references needed for the task
  → Make the smallest complete change
  → Run relevant checks and report the results
```

For example:

- Add a filter: load table, request, and UI guidance.
- Fix out-of-order search results: load async and request guidance.
- Optimize a large-file script: load performance and resource-management guidance.
- Change a backend transaction: load backend/data and relevant verification guidance.

Start with the most relevant 1–3 references and add more as the task expands. Do not load the entire collection by default or repeatedly read unchanged content still present in context.

## Installation

Choose one method. **Use the standalone Skill for persistent installation, or the full plugin for session hooks.** Avoid installing both at once, which can create duplicate entries.

### 1. Get the source

Download and extract a ZIP from this GitHub repository, or clone it:

```sh
# Replace the placeholder with this repository's actual Git clone URL.
git clone "<repository-git-clone-url>" supercoding
cd supercoding
```

Run the installation commands below from the extracted or cloned `supercoding` repository root. Shell examples target common macOS / Linux shells.

### 2. Option A: Install the standalone Skill persistently

Install only `skills/supercoding/`. This method does not require Python and does not include the plugin session hook. Choose the client you use.

**Claude Code:**

```sh
if [ -e "$HOME/.claude/skills/supercoding" ] || [ -L "$HOME/.claude/skills/supercoding" ]; then
  printf '%s\n' 'Target already exists. Compare the existing installation first; nothing was overwritten.'
else
  mkdir -p "$HOME/.claude/skills" &&
  cp -R ./skills/supercoding "$HOME/.claude/skills/supercoding"
fi
```

**CodeBuddy:**

```sh
if [ -e "$HOME/.codebuddy/skills/supercoding" ] || [ -L "$HOME/.codebuddy/skills/supercoding" ]; then
  printf '%s\n' 'Target already exists. Compare the existing installation first; nothing was overwritten.'
else
  mkdir -p "$HOME/.codebuddy/skills" &&
  cp -R ./skills/supercoding "$HOME/.codebuddy/skills/supercoding"
fi
```

On Windows, manually copy the `skills/supercoding` folder into your client's user-level skills directory. The resulting path should end in `skills/supercoding/SKILL.md`, without an extra nested `supercoding` folder.

Start a new client session and confirm that `supercoding` appears in the skills list. For project-only use, copy it into the project's `.claude/skills/` or `.codebuddy/skills/` instead. Avoid duplicate user-level and project-level installations.

**Apply it to every coding task:**

A standalone installation lets the client discover the Skill based on the task. To explicitly require it for all coding tasks, append the following instructions to the appropriate file while preserving existing content:

| Scope | Claude Code | CodeBuddy |
| --- | --- | --- |
| User-level, across projects | `~/.claude/CLAUDE.md` | `~/.codebuddy/CODEBUDDY.md` |
| Current project only | `CLAUDE.md` in the project root | `CODEBUDDY.md` in the project root |

```markdown
## supercoding

Use supercoding before every task that writes or modifies code, including application code, pages, components, APIs, scripts, tests, build configuration, code examples, bug fixes, refactoring, and performance optimization.
If the complete entry is already available in the current context and unchanged, reuse it. Otherwise invoke the Skill by its actual client-provided name, or read the installed supercoding/SKILL.md.
Load only references relevant to the current functionality. Page changes must include style and layout checks.
Respect client system, safety, and permission constraints. Explicit user requirements and project standards take priority over this Skill; existing coding habits are not automatically explicit standards.
By default, inspect only legacy code relevant to the current change. Do not automatically audit or refactor the entire repository. Do not trigger for ordinary conversation, translation, or non-coding file tasks.
```

These are agent instructions, not a write-time enforcement mechanism. Installation does not edit your global instruction files; append the rules yourself.

### 3. Option B: Load the full plugin for a session

Install the relevant client and **Python 3.9+**, available through the `python3` command. Check it with:

```sh
python3 --version
```

From the repository root, start either client:

```sh
# Claude Code
claude --plugin-dir "$PWD"

# CodeBuddy
codebuddy --plugin-dir "$PWD"
```

To work directly in an application project, run the client from that project's directory and pass the absolute path to this repository:

```sh
claude --plugin-dir "/absolute/path/to/supercoding"
# Or:
codebuddy --plugin-dir "/absolute/path/to/supercoding"
```

Replace the example path and follow the client's trust prompts. `--plugin-dir` loads the plugin **for that session**; it is not a permanent installation command. Supply the argument again for later sessions. This repository does not currently provide a marketplace manifest, so no marketplace installation command is documented.

The plugin's `SessionStart` hook provides a short reminder and entry path on startup, resume, clear, or context compaction. Coding tasks then load guidance as needed. The hook does not scan application projects, write application files, or modify global instructions.

The plugin Skill may appear as `supercoding:supercoding`; use the name exposed by your client. Standalone installations typically expose `supercoding`. Other clients may adapt the standard Skill directory, but this repository does not implement their plugin integrations.

See the [installation guide](docs/installation.md) for more details on installation, updates, and troubleshooting.

## Usage

Once default coding instructions are configured or the full plugin is loaded, describe your task normally. You can also request supercoding explicitly.

**Add a feature:**

```text
Use supercoding to add a status filter to the orders page.
Reuse the existing request layer and components, handle pagination, loading and errors,
and check how the new controls fit the existing page layout.
```

**Optimize performance:**

```text
Use supercoding to investigate this slow list.
Separate database, transfer and rendering costs before making evidence-based changes.
Do not claim percentage improvements without measurements.
```

**Reuse and simplify:**

```text
Use supercoding to simplify these repeated business conditions.
Preserve behavior and change only the relevant modules.
```

**Review an existing project:**

```text
Review this project against supercoding.
Report issue locations, triggering conditions and impact. Do not modify code yet.
```

Clients with slash-command support may expose `/supercoding`, or `/supercoding:supercoding` for plugins. Check the client menu; no single invocation syntax is required across all clients.

## Existing projects and instruction priority

| Situation | Default behavior |
| --- | --- |
| Open or start an existing project | Do not automatically audit the repository or rewrite legacy code |
| Add a feature to an existing project | Read relevant implementations and reuse opportunities; apply guidance to new and modified code |
| Find an issue directly related to the task | Address it within the authorized scope while preserving intended behavior and contracts |
| Find unrelated legacy code that differs from the rules | Do not automatically refactor it; report serious out-of-scope issues when discovered |
| Receive an explicit request for a full review | Expand the review and report findings; review authorization does not authorize fixes |
| Project standards differ from the Skill | Within client constraints, follow explicit user requirements and project standards, then apply compatible general guidance |

Keep the project's language, directory conventions, naming, component library, request client, and compatibility targets. Existing defects do not become standards merely for the sake of consistency.

## Confirm it is working

1. Start a new session and confirm the Skill is discoverable. In plugin mode, check for Python or hook errors.
2. Submit a small coding task and observe whether the entry loads before coding, followed only by relevant references.
3. Continue a similar task in the same session and confirm the entire collection is not loaded again.
4. Try a simple translation request and confirm it does not trigger the engineering workflow.

If it does not work, check directory nesting, whether the client was restarted, whether the Skill is disabled, and whether multiple versions are installed. In plugin mode, also check `python3` and hook execution. Further troubleshooting is available in the [installation guide](docs/installation.md).

## Repository layout

```text
supercoding/
├── .claude-plugin/plugin.json
├── .codebuddy-plugin/plugin.json
├── skills/
│   └── supercoding/
│       ├── SKILL.md                # Shared English entry
│       └── references/             # 8 on-demand English rule modules
├── hooks/                         # Plugin session reminder
├── scripts/                       # Read-only maintenance checks
├── tests/
│   ├── test_repository.py
│   └── evals/                     # Evaluation data, excluded from runtime Skill
├── docs/                          # Installation and maintenance guides
├── README.md                      # English, default
└── README.zh-CN.md                 # Simplified Chinese
```

**Copy only [skills/supercoding](skills/supercoding) for standalone installation; load the repository root for the full plugin.** The runtime entry does not depend on outer documentation, tests, or scripts, keeping development materials out of normal coding context.

## Local verification

From the repository root, with Python 3.9+ and no third-party Python dependencies:

```sh
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

- Structure checks cover metadata, relative links, version consistency, runtime isolation, and evaluation data format.
- Automated tests cover valid and malformed inputs, plugin hook output, paths containing Chinese characters and spaces, and standalone Skill completeness.
- The [19 scenarios and 69 assertions](tests/evals/evals.json) support behavior evaluation. Follow the [evaluation protocol](tests/evals/protocol.md); having scenarios does not mean live model evaluation has been completed.

## Support status and limitations

Current version: **1.2.0**. Local structure checks, YAML checks, and 28 automated tests have passed. Claude Code and CodeBuddy manifests and hook output have been checked against their documented formats. **Actual client plugin-loading and model behavior evaluations have not been completed.** No automatic-trigger rate, code-quality outcome, or performance improvement is guaranteed by these checks.

The standalone Skill has no programming-language runtime dependency. Plugin hooks and maintenance tools require Python. Windows hook startup has not been verified, and this version has no dedicated Windows launcher.

The runtime [SKILL.md](skills/supercoding/SKILL.md) and all eight reference modules use one shared English rule set for tasks in any language. The assistant responds in the user's preferred language; Chinese requests do not require Chinese rule files. Only README and installation instructions are available in English and Simplified Chinese. Maintenance documentation, evaluation protocol and the single set of 19 scenarios with 69 assertions are maintained in English.

`supercoding` does not replace linting, type checks, tests, performance measurements, or human review. It does not automatically install application dependencies, push code, deploy, or publish. It does not impose TDD, multiple agents, worktrees, or requirements-approval workflows; existing project processes still apply.

The repository organization is inspired by Superpowers, while the scope remains engineering standards rather than its full development workflow. See the [maintenance guide](docs/development.md).

## Updates and removal

- After downloading or pulling updated source, compare and synchronize standalone runtime files. A copied installation does not automatically follow source updates.
- In plugin mode, restart a session with `--plugin-dir` after updating the source.
- When removing a standalone installation, remove only the confirmed Skill directory and the `supercoding` instruction block you added. Preserve other configuration and check whether the directory is a shared symlink.
- A session-loaded plugin stops loading when you omit `--plugin-dir`; manually added global instructions must be handled separately.

## License

No license is currently included. Uploading the repository to GitHub does not itself grant an open-source license or redistribution permission. The maintainer should choose the licensing terms and add the corresponding license file before public distribution.
