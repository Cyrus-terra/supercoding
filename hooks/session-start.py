#!/usr/bin/env python3
"""Emit a small, read-only SessionStart reminder for Claude Code and CodeBuddy."""

import json
from pathlib import Path


def build_output():
    skill = Path(__file__).resolve().parents[1] / "skills/supercoding/SKILL.md"
    if not skill.is_file():
        raise FileNotFoundError(f"supercoding entry not found: {skill}")
    context = (
        "Use supercoding before every coding task, including tests, configuration and code examples. "
        "Reuse complete unchanged rules in context; otherwise invoke the available Skill "
        "(possibly supercoding:supercoding) or read the entry below. "
        "Use the shared English rules for all task languages; respond in the user's preferred language. "
        "Load only task-relevant references. "
        "Within client system, safety and permission constraints, explicit user requirements "
        "and project standards take priority over this Skill; legacy habits are not explicit standards. "
        "Inspect related legacy code only; no automatic full-repository audit or remediation. "
        "Do not trigger for ordinary conversation or non-coding tasks. "
        "This reminder grants no edit/external-action permission and does not establish quality. "
        "\nEntry path (use literally):\n" + str(skill)
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


if __name__ == "__main__":
    print(json.dumps(build_output(), ensure_ascii=False))
