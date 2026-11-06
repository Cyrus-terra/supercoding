#!/usr/bin/env python3
"""Read-only validation for the English Skill and bilingual source documentation (Python 3.9+)."""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REFERENCES = {
    "architecture-and-reuse.md",
    "api-and-requests.md",
    "async-and-resources.md",
    "tables-and-forms.md",
    "styles-and-ui.md",
    "performance.md",
    "backend-and-data.md",
    "verification.md",
}


def inside(root, target):
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def translated(path):
    return path.with_name(path.stem + ".zh-CN" + path.suffix)


def read_entry(entry, root, errors):
    try:
        text = entry.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read {entry.name}: {exc}")
        return "", {}, {}
    lines = text.splitlines()
    if len(lines) >= 500:
        errors.append(f"Keep {entry.name} below 500 lines (authoring budget)")
    if not lines or lines[0] != "---":
        errors.append(f"{entry.name}: Missing opening YAML frontmatter delimiter")
        return text, {}, {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{entry.name}: Missing closing YAML frontmatter delimiter")
        return text, {}, {}
    fields, metadata = {}, {}
    in_metadata = False
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        prefix = f"{entry.name} line {number}"
        if line.startswith("  ") and in_metadata:
            match = re.fullmatch(r'  ([a-z][a-z0-9-]*): "([^"\n]*)"', line)
            if not match or match[1] in metadata:
                errors.append(f"{prefix}: invalid or duplicate metadata string")
            else:
                metadata[match[1]] = match[2]
            continue
        match = re.fullmatch(r"([a-z][a-z-]*):(?: (.+))?", line)
        if not match:
            errors.append(f"{prefix}: unsupported metadata syntax")
            continue
        key, value = match.groups()
        if key in fields:
            errors.append(f"{prefix}: duplicate field {key}")
        fields[key] = value or ""
        in_metadata = key == "metadata"
        if key not in {"name", "description", "metadata"}:
            errors.append(f"{prefix}: field {key} is outside this package schema")
        if key == "metadata" and value:
            errors.append(f"{prefix}: metadata must be a mapping")
    name = fields.get("name", "")
    if not NAME.fullmatch(name) or len(name) > 64 or name != root.name:
        errors.append(f"{entry.name}: name must be valid lowercase kebab-case and match the directory")
    if not 1 <= len(fields.get("description", "")) <= 1024:
        errors.append(f"{entry.name}: description must contain 1–1024 characters")
    if not "\n".join(lines[end + 1:]).strip():
        errors.append(f"{entry.name}: Missing instruction body")
    if not re.fullmatch(r"\d+\.\d+\.\d+", metadata.get("version", "")):
        errors.append(f"{entry.name}: invalid semantic version")
    return text, fields, metadata


def check_links(document, boundary, errors):
    targets = set()
    if not inside(boundary, document.resolve()):
        errors.append(f"Markdown resource escapes package: {document.name}")
        return targets
    try:
        source = document.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read {document.name}: {exc}")
        return targets
    for raw in LINK.findall(source):
        parsed = urlsplit(raw.strip().strip("<>"))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (document.parent / unquote(parsed.path)).resolve()
        if not inside(boundary, target):
            errors.append(f"{document.name}: link escapes package (missing or external link): {raw}")
        elif not target.exists():
            errors.append(f"{document.name}: missing linked file (missing or external link): {raw}")
        else:
            targets.add(target)
    return targets


def check_pair(english, chinese, links, errors):
    for document, counterpart in ((english, chinese), (chinese, english)):
        if counterpart.resolve() not in links.get(document, set()):
            errors.append(f"{document.name}: missing language switch to {counterpart.name}")


def read_cases(case_file, root, repository, name, errors):
    try:
        if not inside(repository, case_file.resolve()):
            raise ValueError("evals file escapes package")
        data = json.loads(case_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("evals root must be an object")
        if data.get("skill_name") != name or data.get("schema_version") != 1:
            errors.append(f"{case_file.name}: evals skill_name or schema_version mismatch")
        cases = data.get("evals")
        if not isinstance(cases, list) or not cases:
            raise ValueError("evals must be a non-empty array")
        seen, triggers, categories = set(), set(), set()
        allowed = {f"references/{n}" for n in REFERENCES}
        for index, case in enumerate(cases, 1):
            prefix = f"{case_file.name} eval {index}"
            if not isinstance(case, dict):
                errors.append(f"{prefix}: must be an object")
                continue
            case_id = case.get("id")
            if type(case_id) is not int or case_id < 1 or case_id in seen:
                errors.append(f"{prefix}: id must be unique positive integer")
            else:
                seen.add(case_id)
            for field in ("category", "prompt", "fixture", "expected_output"):
                if not isinstance(case.get(field), str) or not case[field].strip():
                    errors.append(f"{prefix}: missing non-empty {field}")
            if isinstance(case.get("category"), str):
                categories.add(case["category"])
            trigger = case.get("should_trigger")
            if type(trigger) is not bool:
                errors.append(f"{prefix}: should_trigger must be boolean")
            else:
                triggers.add(trigger)
            for field in ("files", "reference_files", "assertions"):
                values = case.get(field)
                if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
                    errors.append(f"{prefix}: {field} must be an array of non-empty strings")
            if not isinstance(case.get("assertions"), list) or not case["assertions"]:
                errors.append(f"{prefix}: assertions cannot be empty")
            if isinstance(case.get("reference_files"), list):
                for ref in case["reference_files"]:
                    if not isinstance(ref, str):
                        continue
                    target = (root / ref).resolve()
                    if ref not in allowed or not target.is_file() or not inside(root, target):
                        errors.append(f"{prefix}: invalid reference {ref}")
        if triggers != {True, False}:
            errors.append(f"{case_file.name}: Include both positive and negative trigger cases")
        required = {"ui-small-change", "request-race", "api-granularity", "reuse-boundary", "bounded-script", "cache-isolation", "style-isolation", "scope-review-only", "evidence-honesty"}
        if missing := required - categories:
            errors.append(f"{case_file.name}: Missing scenario categories: {', '.join(sorted(missing))}")
        return cases
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"Cannot validate evals {case_file.name}: {exc}")
        return []


def validate(root):
    root = root.resolve()
    repository = root if (root / "skills/supercoding").is_dir() else None
    root = repository / "skills/supercoding" if repository else root
    errors, stats = [], {}
    entry = root / "SKILL.md"
    if not entry.is_file():
        return ["Missing SKILL.md"], stats
    text, fields, metadata = read_entry(entry, root, errors)
    stats["entry_lines"] = len(text.splitlines())
    if set(root.rglob("SKILL.md")) != {entry}:
        errors.append("Keep exactly one discoverable SKILL.md")
    for forbidden in ("tests", "evals", "scripts"):
        if (root / forbidden).exists():
            errors.append(f"Development directory inside runtime Skill: {forbidden}")
    markdown = [entry] + sorted(root.glob("references/*.md"))
    expected_markdown = {entry, *(root / "references" / filename for filename in REFERENCES)}
    if set(root.rglob("*.md")) != expected_markdown:
        errors.append("Runtime must contain only SKILL.md and eight shared English references")
    links = {document: check_links(document, root, errors) for document in markdown}
    for filename in sorted(REFERENCES):
        resource = root / "references" / filename
        target = resource.resolve()
        if not inside(root, target) or not target.is_file():
            errors.append(f"Missing or external resource: {resource.relative_to(root)}")
        elif target not in links[entry]:
            errors.append(f"Resource is not directly linked from SKILL.md: {resource.relative_to(root)}")
    stats["reference_files"] = len(REFERENCES)
    if repository is None:
        return errors, stats
    name = fields.get("name", "")
    versions = set()
    for manifest_name in (".claude-plugin/plugin.json", ".codebuddy-plugin/plugin.json"):
        try:
            manifest = json.loads((repository / manifest_name).read_text(encoding="utf-8"))
            if not isinstance(manifest, dict) or manifest.get("name") != name:
                raise ValueError("manifest name mismatch")
            version = manifest.get("version")
            if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
                raise ValueError("invalid semantic version")
            versions.add(version)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"Invalid {manifest_name}: {exc}")
    if versions != {metadata.get("version")}:
        errors.append("Plugin and Skill versions must match")
    try:
        hook = json.loads((repository / "hooks/hooks.json").read_text(encoding="utf-8"))
        expected_hook = {"hooks": {"SessionStart": [{
            "matcher": "startup|resume|clear|compact",
            "hooks": [{"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.py"', "timeout": 10}],
        }]}}
        if hook != expected_hook or not (repository / "hooks/session-start.py").is_file():
            errors.append("SessionStart hook configuration or script is invalid")
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"Invalid hooks/hooks.json: {exc}")
    documents = [repository / n for n in ("README.md", "docs/installation.md")]
    documentation = {}
    for document in documents:
        counterpart = translated(document)
        for path in (document, counterpart):
            documentation[path] = check_links(path, repository, errors)
        check_pair(document, counterpart, documentation, errors)
    for document in (repository / "docs/development.md", repository / "tests/evals/protocol.md"):
        check_links(document, repository, errors)
    cases = read_cases(repository / "tests/evals/evals.json", root, repository, name, errors)
    stats["eval_cases"] = len(cases)
    return errors, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors, stats = validate(args.root)
    except OSError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    summary = f"PASS: structure; {stats['entry_lines']} entry lines; {stats['reference_files']} shared English references"
    if "eval_cases" in stats:
        summary += f"; {stats['eval_cases']} scenarios"
    print(summary)
    print("Behavior, trigger accuracy, code quality, translation equivalence and performance are NOT evaluated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
