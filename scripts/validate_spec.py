#!/usr/bin/env python3
"""Validate the mechanical structure of one SDD feature specification."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FILES = {
    "requirements.md": (
        "## Status",
        "## Outcome",
        "## Users",
        "## In Scope",
        "## Out of Scope",
        "## Business Rules",
        "## Acceptance Criteria",
        "## Open Questions",
    ),
    "design.md": (
        "## Context",
        "## Proposed Approach",
        "## Components Affected",
        "## Data and Access Boundaries",
        "## Interfaces",
        "## Decisions and Tradeoffs",
        "## Risks",
        "## Open Questions",
    ),
    "tasks.md": (
        "## Status",
        "## Active Slice",
        "## Implementation Boundary",
        "## Tasks",
        "## Verification Gate",
        "## Blocked Decisions",
        "## Progress Log",
    ),
}

ALLOWED_STATUSES = {
    "requirements.md": {"Draft", "Approved", "Implementing", "Verified"},
    "tasks.md": {"Not Started", "In Progress", "Blocked", "Verified"},
}

PLACEHOLDER_PATTERNS = (
    re.compile(r"<[^>\n]+>"),
    re.compile(r"Draft \| Approved \| Implementing \| Verified"),
    re.compile(r"Not Started \| In Progress \| Blocked \| Verified"),
)

# Traceability coverage: a spec opts in by giving its acceptance criteria stable
# [AC-<n>] IDs. Once opted in, every active criterion must be owned by exactly
# one task and every active data entity by at least one. Deferred and release
# coverage is classified explicitly in the implementation boundary.
ACCEPTANCE_ID_RE = re.compile(r"^\[(AC-\d+)\]\s+\S")
ENTITY_DEFINITION_RE = re.compile(r"^- `([A-Za-z][A-Za-z0-9]*)`:", re.MULTILINE)
TASK_HEADING_RE = re.compile(r"^- \[[ xX]\]\s+(.+)$")
OWNS_LINE_RE = re.compile(r"^\s*- Owns:\s*(.+)$")
OWNS_TOKEN_RE = re.compile(r"^(AC-\d+|entity:[A-Za-z][A-Za-z0-9]*)$")
TRACEABILITY_CLASS_RE = re.compile(
    r"^- (Deferred|Release) (criteria|entities):\s*(.+)$",
    re.IGNORECASE,
)


def section_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return ""

    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


def validate_file(path: Path, headings: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    if not text.strip():
        return [f"{path}: file is empty"]
    if not text.startswith("# "):
        errors.append(f"{path}: first line must be an H1 title")

    for heading in headings:
        if heading not in text:
            errors.append(f"{path}: missing required heading {heading!r}")

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.rstrip() != line:
            errors.append(f"{path}:{line_number}: trailing whitespace")

    for pattern in PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"{path}: unresolved template placeholder {match.group(0)!r}")

    allowed = ALLOWED_STATUSES.get(path.name)
    if allowed is not None:
        status = section_body(text, "## Status").splitlines()
        value = status[0].strip() if status else ""
        if value not in allowed:
            expected = ", ".join(sorted(allowed))
            errors.append(f"{path}: invalid status {value!r}; expected one of {expected}")

    return errors


def meaningful_bullets(body: str) -> list[str]:
    return [
        line.strip()[2:].strip()
        for line in body.splitlines()
        if line.strip().startswith("- ")
        and line.strip()[2:].strip().lower() not in {"none", "none."}
    ]


def validate_cross_file(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    errors: list[str] = []
    requirements = contents["requirements.md"]
    tasks = contents["tasks.md"]

    if not meaningful_bullets(section_body(requirements, "## Acceptance Criteria")):
        errors.append(f"{spec_dir / 'requirements.md'}: acceptance criteria must contain at least one bullet")

    if not re.search(r"^- \[[ xX]\] ", section_body(tasks, "## Tasks"), re.MULTILINE):
        errors.append(f"{spec_dir / 'tasks.md'}: tasks must contain at least one checkbox")

    requirements_status_lines = section_body(requirements, "## Status").splitlines()
    requirements_status = requirements_status_lines[0].strip() if requirements_status_lines else ""
    open_questions = meaningful_bullets(section_body(requirements, "## Open Questions"))
    if requirements_status in {"Approved", "Implementing", "Verified"} and open_questions:
        errors.append(
            f"{spec_dir / 'requirements.md'}: status {requirements_status!r} is incompatible with unresolved open questions"
        )

    task_status_lines = section_body(tasks, "## Status").splitlines()
    task_status = task_status_lines[0].strip() if task_status_lines else ""
    blocked_decisions = meaningful_bullets(section_body(tasks, "## Blocked Decisions"))
    if task_status == "Blocked" and not blocked_decisions:
        errors.append(f"{spec_dir / 'tasks.md'}: Blocked status requires at least one blocked decision")

    return errors


def top_level_bullets(body: str) -> list[str]:
    return [line[2:].strip() for line in body.splitlines() if line.startswith("- ")]


def collect_task_owners(
    tasks_body: str,
) -> tuple[dict[str, list[str]], list[tuple[str, str]], list[tuple[str, int]], list[str]]:
    """Map owned tokens and record whether every task declares one Owns line."""
    owners: dict[str, list[str]] = {}
    malformed: list[tuple[str, str]] = []
    tasks: list[dict[str, str | int]] = []
    structural_errors: list[str] = []
    current: dict[str, str | int] | None = None
    for line in tasks_body.splitlines():
        heading = TASK_HEADING_RE.match(line)
        if heading:
            label = re.split(r"\s[—-]\s", heading.group(1), maxsplit=1)[0].strip()
            current = {"label": label, "owns_count": 0}
            tasks.append(current)
            continue
        owns = OWNS_LINE_RE.match(line)
        if not owns:
            continue
        if current is None:
            structural_errors.append("Owns line appears before the first task")
            continue
        current["owns_count"] = int(current["owns_count"]) + 1
        current_label = str(current["label"])
        content = owns.group(1).strip()
        # An `Owns: none ...` line marks a task that owns no criterion or entity.
        if content.lower().startswith("none"):
            continue
        for raw in content.split(","):
            token = raw.strip()
            if not token or token.lower() in {"none", "none."}:
                continue
            if OWNS_TOKEN_RE.match(token):
                owners.setdefault(token, []).append(current_label)
            else:
                malformed.append((current_label, token))
    task_counts = [(str(task["label"]), int(task["owns_count"])) for task in tasks]
    return owners, malformed, task_counts, structural_errors


def collect_traceability_classes(
    boundary_body: str,
) -> tuple[dict[str, list[str]], list[tuple[str, str]]]:
    """Map deferred and release tokens to their declared readiness class."""
    classes: dict[str, list[str]] = {}
    malformed: list[tuple[str, str]] = []
    for line in boundary_body.splitlines():
        match = TRACEABILITY_CLASS_RE.match(line)
        if not match:
            continue
        readiness = match.group(1).lower()
        token_type = match.group(2).lower()
        content = match.group(3).strip()
        if content.lower().startswith("none"):
            continue
        for raw in content.split(","):
            token = raw.strip()
            expected = (
                re.fullmatch(r"AC-\d+", token)
                if token_type == "criteria"
                else re.fullmatch(r"entity:[A-Za-z][A-Za-z0-9]*", token)
            )
            if expected:
                classes.setdefault(token, []).append(readiness)
            else:
                malformed.append((f"{readiness} {token_type}", token))
    return classes, malformed


def validate_traceability(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    """Enforce AC/entity ownership coverage once a spec adopts [AC-<n>] IDs."""
    errors: list[str] = []
    req_path = spec_dir / "requirements.md"
    design_path = spec_dir / "design.md"
    tasks_path = spec_dir / "tasks.md"

    ac_bullets = top_level_bullets(section_body(contents["requirements.md"], "## Acceptance Criteria"))
    defined_acs: list[str] = []
    for bullet in ac_bullets:
        match = ACCEPTANCE_ID_RE.match(bullet)
        if match:
            defined_acs.append(match.group(1))

    # Opt-in: a spec without any [AC-<n>] ID keeps the legacy structural checks only.
    if not defined_acs:
        return errors

    for bullet in ac_bullets:
        if not ACCEPTANCE_ID_RE.match(bullet):
            errors.append(f"{req_path}: acceptance criterion missing [AC-<n>] ID: {bullet[:60]!r}")

    seen: set[str] = set()
    for ac in defined_acs:
        if ac in seen:
            errors.append(f"{req_path}: duplicate acceptance-criterion ID {ac}")
        seen.add(ac)
    ac_ids = set(defined_acs)

    entities = ENTITY_DEFINITION_RE.findall(section_body(contents["design.md"], "## Data and Access Boundaries"))
    entity_ids = set(entities)

    owners, malformed, task_counts, structural_errors = collect_task_owners(
        section_body(contents["tasks.md"], "## Tasks")
    )
    classes, malformed_classes = collect_traceability_classes(
        section_body(contents["tasks.md"], "## Implementation Boundary")
    )
    for error in structural_errors:
        errors.append(f"{tasks_path}: {error}")
    for task_label, count in task_counts:
        if count == 0:
            errors.append(f"{tasks_path}: {task_label} is missing an Owns line")
        elif count > 1:
            errors.append(f"{tasks_path}: {task_label} has multiple Owns lines")
    for task_label, token in malformed:
        errors.append(f"{tasks_path}: {task_label} Owns token {token!r} is not 'AC-<n>' or 'entity:<Name>'")
    for classification, token in malformed_classes:
        errors.append(
            f"{tasks_path}: {classification} token {token!r} has the wrong format"
        )

    for token, owning_tasks in owners.items():
        if token.startswith("entity:"):
            name = token.split(":", 1)[1]
            if name not in entity_ids:
                where = ", ".join(sorted(set(owning_tasks)))
                errors.append(f"{tasks_path}: Owns references unknown entity {name!r} ({where})")
        elif token not in ac_ids:
            where = ", ".join(sorted(set(owning_tasks)))
            errors.append(f"{tasks_path}: Owns references unknown acceptance criterion {token} ({where})")

    for token, readiness_classes in classes.items():
        if token.startswith("entity:"):
            name = token.split(":", 1)[1]
            if name not in entity_ids:
                errors.append(
                    f"{tasks_path}: traceability references unknown entity {name!r}"
                )
        elif token not in ac_ids:
            errors.append(
                f"{tasks_path}: traceability references unknown acceptance criterion {token}"
            )
        if len(readiness_classes) > 1:
            errors.append(
                f"{tasks_path}: {token} has multiple readiness classifications: "
                f"{', '.join(readiness_classes)}"
            )

    for ac in sorted(ac_ids):
        claimants = owners.get(ac, [])
        readiness_classes = classes.get(ac, [])
        if claimants and readiness_classes:
            errors.append(
                f"{req_path}: {ac} is both task-owned and classified "
                f"{readiness_classes[0]}"
            )
        elif not claimants and not readiness_classes:
            errors.append(
                f"{req_path}: {ac} has no coverage; assign one task or classify it deferred or release"
            )
        elif len(claimants) > 1:
            errors.append(f"{req_path}: {ac} is owned by multiple tasks: {', '.join(claimants)}")

    for name in sorted(entity_ids):
        token = f"entity:{name}"
        claimants = owners.get(token, [])
        readiness_classes = classes.get(token, [])
        if claimants and readiness_classes:
            errors.append(
                f"{design_path}: entity {name!r} is both task-owned and classified "
                f"{readiness_classes[0]}"
            )
        elif not claimants and not readiness_classes:
            errors.append(
                f"{design_path}: entity {name!r} has no coverage; assign a task or classify it deferred or release"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_dir", type=Path, help="Directory containing requirements.md, design.md, and tasks.md")
    args = parser.parse_args()
    spec_dir = args.spec_dir

    if not spec_dir.is_dir():
        print(f"Spec validation failed: {spec_dir} is not a directory", file=sys.stderr)
        return 1

    errors: list[str] = []
    contents: dict[str, str] = {}
    for filename, headings in REQUIRED_FILES.items():
        path = spec_dir / filename
        if not path.is_file():
            errors.append(f"{path}: required file is missing")
            continue
        contents[filename] = path.read_text(encoding="utf-8")
        errors.extend(validate_file(path, headings))

    if len(contents) == len(REQUIRED_FILES):
        errors.extend(validate_cross_file(spec_dir, contents))
        errors.extend(validate_traceability(spec_dir, contents))

    if errors:
        print(f"Spec validation failed: {spec_dir}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Spec validation passed: {spec_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
