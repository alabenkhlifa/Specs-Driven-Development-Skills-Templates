#!/usr/bin/env python3
"""Validate required files and synchronized SDD starter-kit resources."""

from __future__ import annotations

import re
import subprocess
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
    "scripts/validate_spec.py",
    "scripts/test_validate_spec.py",
    "commands/add-spec.md",
    "commands/update-spec.md",
    "commands/implement-spec.md",
    "commands/review-spec.md",
    ".claude/commands/add-spec.md",
    ".claude/commands/update-spec.md",
    ".claude/commands/implement-spec.md",
    ".claude/commands/review-spec.md",
]

SKILLS = ("add-spec", "update-spec", "implement-spec", "review-spec")
TEMPLATES = ("requirements.md", "design.md", "tasks.md")


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def compare_files(errors: list[str], first: str, second: str, message: str) -> None:
    if (ROOT / first).is_file() and (ROOT / second).is_file() and read(first) != read(second):
        errors.append(message)


def run_check(errors: list[str], script: str, *args: str) -> None:
    path = ROOT / script
    if not path.is_file():
        return
    result = subprocess.run(
        [sys.executable, str(path), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        errors.append(f"{script} failed:\n{output}")


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")

    for skill in SKILLS:
        skill_file = ROOT / "skills" / skill / "SKILL.md"
        metadata_file = ROOT / "skills" / skill / "agents" / "openai.yaml"
        command_file = ROOT / "commands" / f"{skill}.md"
        link = ROOT / ".claude" / "skills" / skill

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

        if command_file.is_file() and command_file.read_text(encoding="utf-8") != content:
            errors.append(f"command mirror is out of sync: commands/{skill}.md")

        if not link.is_symlink():
            errors.append(f"missing Claude skill link: .claude/skills/{skill}")
        elif not link.exists():
            errors.append(f"broken Claude skill link: .claude/skills/{skill}")
        elif link.resolve() != skill_file.parent.resolve():
            errors.append(f"Claude skill link targets the wrong folder: .claude/skills/{skill}")

    for template in TEMPLATES:
        compare_files(
            errors,
            f"templates/feature-spec/{template}",
            f"skills/add-spec/assets/{template}",
            f"bundled template is out of sync: {template}",
        )

    for command in SKILLS:
        adapter_path = f".claude/commands/{command}.md"
        if (ROOT / adapter_path).is_file():
            adapter = read(adapter_path)
            if f"commands/{command}.md" not in adapter:
                errors.append(f"Claude adapter does not reference commands/{command}.md")

    placeholder = re.compile(r"<[^>]+>")
    for example in (ROOT / "examples").rglob("*.md"):
        if placeholder.search(example.read_text(encoding="utf-8")):
            errors.append(f"example contains an unresolved placeholder: {example.relative_to(ROOT)}")

    compare_files(
        errors,
        "templates/AGENTS.md",
        "templates/CLAUDE.md",
        "templates/AGENTS.md and templates/CLAUDE.md are out of sync",
    )
    compare_files(
        errors,
        "AGENTS.md",
        "CLAUDE.md",
        "root AGENTS.md and CLAUDE.md are out of sync",
    )

    run_check(errors, "scripts/test_validate_spec.py")
    if (ROOT / "examples" / "training-request").is_dir():
        run_check(errors, "scripts/validate_spec.py", "examples/training-request")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed.")
    print(
        f"Checked {len(REQUIRED_FILES)} required files, {len(SKILLS)} skills, "
        f"{len(TEMPLATES)} bundled templates, and the completed example."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
