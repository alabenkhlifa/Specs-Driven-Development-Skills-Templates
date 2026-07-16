#!/usr/bin/env python3
"""Validate required files and synchronized SDD starter-kit resources."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "AGENTS.md",
    "CLAUDE.md",
    "templates/AGENTS.md",
    "templates/CLAUDE.md",
    "templates/feature-spec/requirements.md",
    "templates/feature-spec/design.md",
    "templates/feature-spec/tasks.md",
    "commands/add-spec.md",
    "commands/update-spec.md",
    "commands/implement-spec.md",
    ".claude/commands/add-spec.md",
    ".claude/commands/update-spec.md",
    ".claude/commands/implement-spec.md",
]

SKILLS = ("add-spec", "update-spec", "implement-spec")
TEMPLATES = ("requirements.md", "design.md", "tasks.md")


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")

    for skill in SKILLS:
        skill_file = ROOT / "skills" / skill / "SKILL.md"
        metadata_file = ROOT / "skills" / skill / "agents" / "openai.yaml"
        if not skill_file.is_file():
            errors.append(f"missing skill file: skills/{skill}/SKILL.md")
            continue
        if not metadata_file.is_file():
            errors.append(f"missing skill metadata: skills/{skill}/agents/openai.yaml")

        content = skill_file.read_text(encoding="utf-8")
        match = re.match(r"^---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n", content)
        if not match:
            errors.append(f"invalid skill frontmatter: skills/{skill}/SKILL.md")
        elif match.group(1) != skill:
            errors.append(f"skill name mismatch: {skill} != {match.group(1)}")

    for template in TEMPLATES:
        canonical = read(f"templates/feature-spec/{template}")
        bundled = read(f"skills/add-spec/assets/{template}")
        if canonical != bundled:
            errors.append(f"bundled template is out of sync: {template}")

    for command in SKILLS:
        adapter = read(f".claude/commands/{command}.md")
        if f"commands/{command}.md" not in adapter:
            errors.append(f"Claude adapter does not reference commands/{command}.md")

    placeholder = re.compile(r"<[^>]+>")
    for example in (ROOT / "examples").rglob("*.md"):
        if placeholder.search(example.read_text(encoding="utf-8")):
            errors.append(f"example contains an unresolved placeholder: {example.relative_to(ROOT)}")

    if read("templates/AGENTS.md") != read("templates/CLAUDE.md"):
        errors.append("templates/AGENTS.md and templates/CLAUDE.md are out of sync")

    if read("AGENTS.md") != read("CLAUDE.md"):
        errors.append("root AGENTS.md and CLAUDE.md are out of sync")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed.")
    print(f"Checked {len(REQUIRED_FILES)} required files, {len(SKILLS)} skills, and {len(TEMPLATES)} bundled templates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

