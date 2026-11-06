#!/usr/bin/env python3
"""Emit a small, read-only SessionStart reminder for Claude Code, CodeBuddy and Gemini CLI."""

import json
from pathlib import Path


def build_output():
    skill = Path(__file__).resolve().parents[1] / "skills/supercoding/SKILL.md"
    if not skill.is_file():
        raise FileNotFoundError(f"supercoding entry not found: {skill}")
    context = (
        "Use supercoding for coding, including scripts, tests and build configuration. "
        "Skip pure README/document/report writing, translation and conversation. "
        "Reuse complete unchanged rules in context; otherwise invoke the available Skill "
        "(possibly supercoding:supercoding) or read the entry below. "
        "Load only needed references; tiny tasks may use the entry alone. "
        "Use shared English rules; respond in the user's preferred language. "
        "Within client constraints, explicit user requirements and project standards take priority. "
        "Inspect related code only; no automatic full-repository audit or remediation. "
        "This reminder grants no additional permissions. "
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
