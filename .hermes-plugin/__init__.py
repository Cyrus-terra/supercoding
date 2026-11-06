"""Hermes adapter for the shared supercoding Skill."""

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = next((root for root in (HERE.parent, HERE) if (root / "skills/supercoding/SKILL.md").is_file()), HERE.parent)
ENTRY = ROOT / "skills" / "supercoding" / "SKILL.md"
MARKER = "supercoding coding reminder"


def _description() -> str:
    text = ENTRY.read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else "Cross-language coding standards"


def register(ctx):
    if not ENTRY.is_file():
        raise RuntimeError(f"supercoding entry not found: {ENTRY}")
    ctx.register_skill("supercoding", ENTRY, description=_description())

    def pre_llm_call(is_first_turn=None, platform=None, **kwargs):
        if is_first_turn and platform != "subagent":
            return {
                "context": (
                    f"{MARKER}: use supercoding for coding tasks, including tests and build configuration; "
                    "skip pure documentation, translation and conversation; load only relevant references; "
                    "explicit user requirements and project standards take priority. "
                    "Load the Skill with skill_view(\"supercoding:supercoding\") when needed."
                )
            }
        return None

    ctx.register_hook("pre_llm_call", pre_llm_call)
