#!/usr/bin/env python3
"""Validate one SDD specification or the complete cross-spec capability graph."""

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
    # Keep the current task plan compact. The append-only implementation
    # journal and proof receipts live beside it in progress.md.
    "progress.md": (),
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
TASK_ID_RE = re.compile(r"^Task \d+$")
DEPENDS_LINE_RE = re.compile(r"^\s*- Depends on:\s*(.+)$")
OWNS_LINE_RE = re.compile(r"^\s*- Owns:\s*(.+)$")
OWNS_TOKEN_RE = re.compile(r"^(AC-\d+|entity:[A-Za-z][A-Za-z0-9]*)$")
TRACEABILITY_CLASS_RE = re.compile(
    r"^- (Deferred|Release) (criteria|entities):\s*(.+)$",
    re.IGNORECASE,
)
CAPABILITY_HEADING = "## Cross-Specification Dependencies"
CAPABILITY_SLUG_PATTERN = r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
CAPABILITY_NAME_PATTERN = rf"capability:{CAPABILITY_SLUG_PATTERN}"
SPEC_REFERENCE_PATTERN = rf"specs/{CAPABILITY_SLUG_PATTERN}"
CAPABILITY_REQUIREMENT_RE = re.compile(
    rf"^- `(?P<name>{CAPABILITY_NAME_PATTERN})` — "
    rf"provider `(?P<provider>{SPEC_REFERENCE_PATTERN})#(?P<provider_task>Task \d+)` — "
    r"required before `(?P<consumer_task>Task \d+)`\.$"
)
CAPABILITY_PROVIDER_RE = re.compile(
    rf"^- `(?P<name>{CAPABILITY_NAME_PATTERN})` — ready after `(?P<task>Task \d+)`\.$"
)
TASK_RECORD_RE = re.compile(r"^- \[([ xX])\]\s+(.+)$")
SLICE_SIZE_HEADING = "## Slice Size Gate"
SLICE_SIZE_LINE_RE = re.compile(r"^- Slice size:\s*(.*)$")
SLICE_SIZE_EXCEPTION_RE = re.compile(r"^Exception — (?P<reason>.+)\.$")
TASK_SIZE_HEADING = "## Task Size Gate"
TASK_SIZE_LINE_RE = re.compile(r"^\s*- Size:\s*(.+)$")
TASK_SIZE_EXCEPTION_RE = re.compile(r"^Exception — (?P<reason>.+)\.$")
PROOF_SCOPE_HEADING = "## Proof Scope Gate"
PROOF_APPLIES_LINE_RE = re.compile(r"^- Applies to:\s*(.+)$")
PROOF_SCOPE_LINE_RE = re.compile(r"^\s*- Proof scope:\s*(.*)$")
PROOF_SCOPE_BROAD_RE = re.compile(r"^Broad — (?P<reason>.+)\.$")
PROOF_RECEIPT_RE = re.compile(
    r"^- Proof receipt: `(?P<task>Task \d+)` — "
    r"scope `(?P<scope>Focused|Broad)` — "
    r"command `(?P<command>[^`\n]+)` — exit `0`\.$"
)
SLICE_PROOF_RECEIPT_RE = re.compile(
    r"^- Proof receipt: slice — scope `Broad` — "
    r"command `(?P<command>[^`\n]+)` — exit `0`\.$"
)
PROGRESS_HEADING = "## Progress Log"
PROGRESS_FILENAME = "progress.md"
PROGRESS_POINTER = "See [progress.md](progress.md)."
PROGRESS_ENTRY_RE = re.compile(r"^### \S")


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


def progress_log_text(contents: dict[str, str]) -> str:
    """Return proof and readiness evidence from the separate progress journal.

    Legacy inline entries remain readable during migration so the validator
    reports the required split without also pretending that evidence vanished.
    """
    stored = contents.get(PROGRESS_FILENAME, "")
    if stored.strip():
        return stored
    return section_body(contents.get("tasks.md", ""), PROGRESS_HEADING)


def validate_progress_log_split(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    """Require tasks.md to link to progress.md instead of carrying history."""
    errors: list[str] = []
    tasks_path = spec_dir / "tasks.md"
    tasks_text = contents.get("tasks.md", "")
    if PROGRESS_HEADING not in tasks_text:
        return errors

    lines = [
        line
        for line in section_body(tasks_text, PROGRESS_HEADING).splitlines()
        if line.strip()
    ]
    if any(PROGRESS_ENTRY_RE.match(line) for line in lines):
        errors.append(
            f"{tasks_path}: {PROGRESS_HEADING} still contains inline entries; "
            "run python3 .agents/scripts/split_progress_log.py to move them "
            f"into {PROGRESS_FILENAME}"
        )
        return errors

    if lines != [PROGRESS_POINTER]:
        errors.append(
            f"{tasks_path}: {PROGRESS_HEADING} body must be exactly "
            f"{PROGRESS_POINTER!r}"
        )
    return errors


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


def collect_task_dependency_lines(tasks_body: str) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """Collect each task label and its Depends on declarations."""
    tasks: list[tuple[str, list[str]]] = []
    structural_errors: list[str] = []
    current_index: int | None = None
    for line in tasks_body.splitlines():
        heading = TASK_HEADING_RE.match(line)
        if heading:
            label = re.split(r"\s[—-]\s", heading.group(1), maxsplit=1)[0].strip()
            tasks.append((label, []))
            current_index = len(tasks) - 1
            continue
        depends = DEPENDS_LINE_RE.match(line)
        if not depends:
            continue
        if current_index is None:
            structural_errors.append("Depends on line appears before the first task")
            continue
        tasks[current_index][1].append(depends.group(1).strip())
    return tasks, structural_errors


def validate_task_dependencies(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    """Validate stable task labels and backward-only dependencies when adopted."""
    errors: list[str] = []
    tasks_path = spec_dir / "tasks.md"
    tasks, structural_errors = collect_task_dependency_lines(
        section_body(contents["tasks.md"], "## Tasks")
    )
    for error in structural_errors:
        errors.append(f"{tasks_path}: {error}")

    # Opt-in: legacy specifications without Depends on declarations remain valid.
    if not any(lines for _, lines in tasks):
        return errors

    labels = [label for label, _ in tasks]
    positions: dict[str, int] = {}
    for position, label in enumerate(labels):
        if not TASK_ID_RE.fullmatch(label):
            errors.append(
                f"{tasks_path}: dependency-enabled task label {label!r} must be 'Task <n>'"
            )
        if label in positions:
            errors.append(f"{tasks_path}: duplicate task label {label}")
        else:
            positions[label] = position

    for position, (label, declarations) in enumerate(tasks):
        if len(declarations) == 0:
            errors.append(f"{tasks_path}: {label} is missing a Depends on line")
            continue
        if len(declarations) > 1:
            errors.append(f"{tasks_path}: {label} has multiple Depends on lines")
            continue

        content = declarations[0]
        if content.lower() in {"none", "none."}:
            continue

        dependencies = [raw.strip() for raw in content.split(",") if raw.strip()]
        if not dependencies:
            errors.append(f"{tasks_path}: {label} Depends on line is empty")
            continue
        seen: set[str] = set()
        for dependency in dependencies:
            if not TASK_ID_RE.fullmatch(dependency):
                errors.append(
                    f"{tasks_path}: {label} dependency {dependency!r} is not 'Task <n>' or 'none'"
                )
                continue
            if dependency in seen:
                errors.append(f"{tasks_path}: {label} repeats dependency {dependency}")
                continue
            seen.add(dependency)
            dependency_position = positions.get(dependency)
            if dependency_position is None:
                errors.append(f"{tasks_path}: {label} depends on unknown task {dependency}")
            elif dependency_position >= position:
                errors.append(
                    f"{tasks_path}: {label} depends on {dependency}, which is not an earlier task"
                )

    return errors


def collect_task_records(tasks_body: str) -> tuple[list[str], dict[str, dict[str, object]]]:
    """Collect task order, completion state, and the full task block."""
    order: list[str] = []
    records: dict[str, dict[str, object]] = {}
    current_label: str | None = None
    current_lines: list[str] = []

    def save_current() -> None:
        if current_label is not None and current_label not in records:
            records[current_label] = {
                "complete": current_lines[0].startswith("- [x] ")
                or current_lines[0].startswith("- [X] "),
                "body": "\n".join(current_lines),
            }

    for line in tasks_body.splitlines():
        heading = TASK_RECORD_RE.match(line)
        if heading:
            save_current()
            label = re.split(r"\s[—-]\s", heading.group(2), maxsplit=1)[0].strip()
            current_label = label
            current_lines = [line]
            order.append(label)
        elif current_label is not None:
            current_lines.append(line)

    save_current()
    return order, records


def task_ownership_counts(task_body: str) -> tuple[int, int]:
    """Count acceptance criteria and entities owned by one task."""
    acceptance_criteria: set[str] = set()
    entities: set[str] = set()
    for line in task_body.splitlines():
        owns = OWNS_LINE_RE.match(line)
        if owns is None:
            continue
        for raw in owns.group(1).split(","):
            token = raw.strip()
            if token.startswith("AC-") and OWNS_TOKEN_RE.fullmatch(token):
                acceptance_criteria.add(token)
            elif token.startswith("entity:") and OWNS_TOKEN_RE.fullmatch(token):
                entities.add(token)
    return len(acceptance_criteria), len(entities)


def valid_dependency_depth(tasks_body: str) -> int | None:
    """Return the longest valid dependency path, or None for an invalid graph.

    Dependency-shape errors remain owned by validate_task_dependencies so the
    slice-size gate does not report a second error for the same malformed edge.
    """
    tasks, structural_errors = collect_task_dependency_lines(tasks_body)
    if structural_errors or not tasks:
        return None

    labels = [label for label, _ in tasks]
    if any(not TASK_ID_RE.fullmatch(label) for label in labels):
        return None
    if len(set(labels)) != len(labels):
        return None

    positions = {label: position for position, label in enumerate(labels)}
    depths: dict[str, int] = {}
    for position, (label, declarations) in enumerate(tasks):
        if len(declarations) != 1:
            return None

        content = declarations[0]
        if content.lower() in {"none", "none."}:
            dependencies: list[str] = []
        else:
            dependencies = [raw.strip() for raw in content.split(",") if raw.strip()]
            if not dependencies or len(set(dependencies)) != len(dependencies):
                return None
            if any(not TASK_ID_RE.fullmatch(dependency) for dependency in dependencies):
                return None
            if any(
                dependency not in positions or positions[dependency] >= position
                for dependency in dependencies
            ):
                return None

        depths[label] = 1 + max(
            (depths[dependency] for dependency in dependencies),
            default=0,
        )

    return max(depths.values())


def validate_slice_size_gate(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    """Validate the optional prospective slice-size declaration and limits."""
    tasks_text = contents["tasks.md"]
    tasks_path = spec_dir / "tasks.md"
    if SLICE_SIZE_HEADING not in tasks_text:
        return []

    errors: list[str] = []
    capability_index = tasks_text.find(CAPABILITY_HEADING)
    slice_size_index = tasks_text.find(SLICE_SIZE_HEADING)
    task_size_index = tasks_text.find(TASK_SIZE_HEADING)
    if (
        capability_index == -1
        or task_size_index == -1
        or not (capability_index < slice_size_index < task_size_index)
    ):
        errors.append(
            f"{tasks_path}: {SLICE_SIZE_HEADING} must appear after "
            f"{CAPABILITY_HEADING} and before {TASK_SIZE_HEADING}"
        )

    gate_body = section_body(tasks_text, SLICE_SIZE_HEADING)
    declarations = [
        match.group(1).strip()
        for line in gate_body.splitlines()
        if (match := SLICE_SIZE_LINE_RE.fullmatch(line)) is not None
    ]
    if not declarations:
        errors.append(
            f"{tasks_path}: {SLICE_SIZE_HEADING} is missing a top-level "
            "'- Slice size:' declaration"
        )
        return errors
    if len(declarations) > 1:
        errors.append(
            f"{tasks_path}: {SLICE_SIZE_HEADING} has multiple top-level "
            "'- Slice size:' declarations"
        )
        return errors

    declaration = declarations[0]
    if declaration == "Standard":
        tasks_body = section_body(tasks_text, "## Tasks")
        tasks, _ = collect_task_dependency_lines(tasks_body)
        if len(tasks) > 12:
            errors.append(
                f"{tasks_path}: Standard slice has {len(tasks)} tasks; "
                "split it or record a justified Slice size exception"
            )

        longest_path = valid_dependency_depth(tasks_body)
        if longest_path is not None and longest_path > 8:
            errors.append(
                f"{tasks_path}: Standard slice has a longest dependency path of "
                f"{longest_path} tasks; split it or record a justified Slice size exception"
            )
        return errors

    exception = SLICE_SIZE_EXCEPTION_RE.fullmatch(declaration)
    if exception is not None:
        reason = exception.group("reason").strip()
        if (
            len(reason) >= 30
            and not re.search(r"<[^>\n]+>", reason)
            and reason.lower()
            not in {
                "cannot be split",
                "slice is complex",
                "too much work",
                "implementation convenience",
                "shared release milestone",
                "one pull request",
            }
        ):
            return errors

    errors.append(
        f"{tasks_path}: Slice size must be 'Standard' or a justified "
        "'Exception — <reason>.' that names the invalid boundary created by splitting"
    )
    return errors


def validate_task_size_gate(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    """Validate the opt-in task-size declaration and mechanical ownership limits."""
    tasks_text = contents["tasks.md"]
    tasks_path = spec_dir / "tasks.md"
    if TASK_SIZE_HEADING not in tasks_text:
        return []

    errors: list[str] = []
    previous_heading = (
        CAPABILITY_HEADING
        if CAPABILITY_HEADING in tasks_text
        else "## Active Slice"
    )
    previous_index = tasks_text.find(previous_heading)
    size_index = tasks_text.find(TASK_SIZE_HEADING)
    boundary_index = tasks_text.find("## Implementation Boundary")
    if not (previous_index < size_index < boundary_index):
        errors.append(
            f"{tasks_path}: {TASK_SIZE_HEADING} must appear after "
            f"{previous_heading} and before ## Implementation Boundary"
        )

    if len(meaningful_bullets(section_body(tasks_text, TASK_SIZE_HEADING))) < 2:
        errors.append(
            f"{tasks_path}: {TASK_SIZE_HEADING} must define the standard task "
            "and exception rules"
        )

    _, task_records = collect_task_records(section_body(tasks_text, "## Tasks"))
    for task, record in task_records.items():
        task_body = str(record["body"])
        declarations = [
            match.group(1).strip()
            for line in task_body.splitlines()
            if (match := TASK_SIZE_LINE_RE.match(line)) is not None
        ]
        if not declarations:
            errors.append(f"{tasks_path}: {task} is missing a Size line")
            continue
        if len(declarations) > 1:
            errors.append(f"{tasks_path}: {task} has multiple Size lines")
            continue

        declaration = declarations[0]
        if declaration == "Standard":
            criteria_count, entity_count = task_ownership_counts(task_body)
            if criteria_count > 3:
                errors.append(
                    f"{tasks_path}: {task} owns {criteria_count} acceptance criteria; "
                    "split it or record a justified Size exception"
                )
            if entity_count > 2:
                errors.append(
                    f"{tasks_path}: {task} owns {entity_count} entities; "
                    "split it or record a justified Size exception"
                )
            continue

        exception = TASK_SIZE_EXCEPTION_RE.fullmatch(declaration)
        if exception is None:
            errors.append(
                f"{tasks_path}: {task} Size must be 'Standard' or "
                "'Exception — <why splitting creates an invalid intermediate state>.'"
            )
            continue

        reason = exception.group("reason").strip()
        if (
            len(reason) < 30
            or re.search(r"<[^>\n]+>", reason)
            or reason.lower()
            in {
                "cannot be split",
                "task is complex",
                "too much work",
                "implementation convenience",
            }
        ):
            errors.append(
                f"{tasks_path}: {task} Size exception must explain the invalid "
                "intermediate state created by splitting"
            )

    return errors


def validate_proof_scope_gate(spec_dir: Path, contents: dict[str, str]) -> list[str]:
    """Validate opt-in task proof scopes and completed-task proof receipts."""
    tasks_text = contents["tasks.md"]
    tasks_path = spec_dir / "tasks.md"
    if PROOF_SCOPE_HEADING not in tasks_text:
        return []

    errors: list[str] = []
    size_index = tasks_text.find(TASK_SIZE_HEADING)
    proof_index = tasks_text.find(PROOF_SCOPE_HEADING)
    boundary_index = tasks_text.find("## Implementation Boundary")
    if size_index == -1 or not (size_index < proof_index < boundary_index):
        errors.append(
            f"{tasks_path}: {PROOF_SCOPE_HEADING} must appear after "
            f"{TASK_SIZE_HEADING} and before ## Implementation Boundary"
        )

    gate_body = section_body(tasks_text, PROOF_SCOPE_HEADING)
    applies_declarations = [
        match.group(1).strip()
        for line in gate_body.splitlines()
        if (match := PROOF_APPLIES_LINE_RE.fullmatch(line)) is not None
    ]
    if not applies_declarations:
        errors.append(
            f"{tasks_path}: {PROOF_SCOPE_HEADING} is missing a top-level "
            "'- Applies to:' declaration"
        )
        return errors
    if len(applies_declarations) > 1:
        errors.append(
            f"{tasks_path}: {PROOF_SCOPE_HEADING} has multiple top-level "
            "'- Applies to:' declarations"
        )
        return errors

    task_order, task_records = collect_task_records(section_body(tasks_text, "## Tasks"))
    applies_value = applies_declarations[0]
    applicable_tasks: list[str] = []
    if applies_value == "all tasks.":
        applicable_tasks = task_order
        for task in task_order:
            if not TASK_ID_RE.fullmatch(task):
                errors.append(
                    f"{tasks_path}: proof-scope task label {task!r} must be 'Task <n>'"
                )
    else:
        normalized_value = (
            applies_value[:-1] if applies_value.endswith(".") else applies_value
        )
        labels = [label.strip() for label in normalized_value.split(",")]
        if not labels or any(not label for label in labels):
            errors.append(
                f"{tasks_path}: Applies to must be 'all tasks.' or a comma-separated "
                "list of 'Task <n>' labels"
            )
            return errors
        seen_labels: set[str] = set()
        for label in labels:
            if not TASK_ID_RE.fullmatch(label):
                errors.append(
                    f"{tasks_path}: Applies to label {label!r} must be 'Task <n>'"
                )
                continue
            if label in seen_labels:
                errors.append(f"{tasks_path}: Applies to repeats task label {label}")
                continue
            seen_labels.add(label)
            if label not in task_records:
                errors.append(f"{tasks_path}: Applies to references unknown task {label}")
                continue
            applicable_tasks.append(label)

    receipts = [
        match.groupdict()
        for line in progress_log_text(contents).splitlines()
        if (match := PROOF_RECEIPT_RE.fullmatch(line.strip())) is not None
    ]

    for task in applicable_tasks:
        record = task_records.get(task)
        if record is None:
            # Unknown labels are reported while parsing an explicit applicability list.
            continue
        declarations = [
            match.group(1).strip()
            for line in str(record["body"]).splitlines()
            if (match := PROOF_SCOPE_LINE_RE.fullmatch(line)) is not None
        ]
        if not declarations:
            errors.append(f"{tasks_path}: {task} is missing a Proof scope line")
            continue
        if len(declarations) > 1:
            errors.append(f"{tasks_path}: {task} has multiple Proof scope lines")
            continue

        declaration = declarations[0]
        scope: str | None = None
        if declaration == "Focused":
            scope = "Focused"
        else:
            broad = PROOF_SCOPE_BROAD_RE.fullmatch(declaration)
            if broad is not None:
                reason = broad.group("reason").strip()
                if reason and not re.search(r"<[^>\n]+>", reason):
                    scope = "Broad"
        if scope is None:
            errors.append(
                f"{tasks_path}: {task} Proof scope must be 'Focused' or "
                "'Broad — <specific nonempty reason>.'"
            )
            continue

        if bool(record["complete"]) and not any(
            receipt["task"] == task and receipt["scope"] == scope
            for receipt in receipts
        ):
            errors.append(
                f"{tasks_path}: completed {task} requires a successful {scope} "
                f"Proof receipt in {PROGRESS_FILENAME}"
            )

    status_lines = section_body(tasks_text, "## Status").splitlines()
    status = status_lines[0].strip() if status_lines else ""
    if status == "Verified":
        incomplete_tasks = [
            task for task, record in task_records.items() if not bool(record["complete"])
        ]
        if incomplete_tasks:
            errors.append(
                f"{tasks_path}: Verified status requires every task complete; "
                f"incomplete: {', '.join(incomplete_tasks)}"
            )

        verification_lines = [
            line
            for line in section_body(tasks_text, "## Verification Gate").splitlines()
            if re.match(r"^- \[[ xX]\] ", line)
        ]
        if not verification_lines or any(not line.startswith("- [x]") and not line.startswith("- [X]") for line in verification_lines):
            errors.append(
                f"{tasks_path}: Verified status requires every Verification Gate item complete"
            )

        slice_receipts = [
            line
            for line in progress_log_text(contents).splitlines()
            if SLICE_PROOF_RECEIPT_RE.fullmatch(line.strip()) is not None
        ]
        if not slice_receipts:
            errors.append(
                f"{tasks_path}: Verified status requires a successful slice Proof receipt "
                f"in {PROGRESS_FILENAME}"
            )

    return errors


def parse_capability_dependencies(
    spec_dir: Path, tasks_text: str
) -> tuple[bool, list[dict[str, str]], list[dict[str, str]], list[str]]:
    """Parse the opt-in task-level cross-specification capability contract."""
    tasks_path = spec_dir / "tasks.md"
    if CAPABILITY_HEADING not in tasks_text:
        return False, [], [], []

    errors: list[str] = []
    active_index = tasks_text.find("## Active Slice")
    capability_index = tasks_text.find(CAPABILITY_HEADING)
    boundary_index = tasks_text.find("## Implementation Boundary")
    if not (active_index < capability_index < boundary_index):
        errors.append(
            f"{tasks_path}: {CAPABILITY_HEADING} must appear after "
            "## Active Slice and before ## Implementation Boundary"
        )

    body = section_body(tasks_text, CAPABILITY_HEADING)
    requirements: list[dict[str, str]] = []
    providers: list[dict[str, str]] = []
    modes_seen: list[str] = []
    none_seen: set[str] = set()
    mode: str | None = None

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"Requires:", "Provides:"}:
            mode = stripped[:-1].lower()
            modes_seen.append(mode)
            continue
        if not stripped.startswith("- "):
            errors.append(f"{tasks_path}: unexpected capability line {stripped!r}")
            continue
        if mode is None:
            errors.append(f"{tasks_path}: capability entry appears before Requires or Provides")
            continue
        if stripped == "- None.":
            none_seen.add(mode)
            continue

        match = (
            CAPABILITY_REQUIREMENT_RE.fullmatch(stripped)
            if mode == "requires"
            else CAPABILITY_PROVIDER_RE.fullmatch(stripped)
        )
        if match is None:
            expected = (
                "`capability:<name>` — provider `specs/<feature>#Task <n>` — "
                "required before `Task <n>`."
                if mode == "requires"
                else "`capability:<name>` — ready after `Task <n>`."
            )
            errors.append(
                f"{tasks_path}: malformed {mode} entry {stripped!r}; expected {expected}"
            )
            continue
        if mode == "requires":
            requirements.append(match.groupdict())
        else:
            providers.append({"name": match.group("name"), "task": match.group("task")})

    for required_mode in ("requires", "provides"):
        count = modes_seen.count(required_mode)
        if count == 0:
            errors.append(f"{tasks_path}: capability section is missing {required_mode.title()}:")
        elif count > 1:
            errors.append(
                f"{tasks_path}: capability section has multiple {required_mode.title()}: labels"
            )

    if "requires" in none_seen and requirements:
        errors.append(f"{tasks_path}: Requires cannot mix None with capability entries")
    if "provides" in none_seen and providers:
        errors.append(f"{tasks_path}: Provides cannot mix None with capability entries")
    if "requires" not in none_seen and not requirements:
        errors.append(f"{tasks_path}: Requires must declare a capability or None")
    if "provides" not in none_seen and not providers:
        errors.append(f"{tasks_path}: Provides must declare a capability or None")

    requirement_names: set[str] = set()
    for requirement in requirements:
        name = requirement["name"]
        if name in requirement_names:
            errors.append(f"{tasks_path}: duplicate required capability {name}")
        requirement_names.add(name)

    provider_names: set[str] = set()
    for provider in providers:
        name = provider["name"]
        if name in provider_names:
            errors.append(f"{tasks_path}: duplicate provided capability {name}")
        provider_names.add(name)

    _, task_records = collect_task_records(section_body(tasks_text, "## Tasks"))
    for requirement in requirements:
        consumer_task = requirement["consumer_task"]
        if consumer_task not in task_records:
            errors.append(
                f"{tasks_path}: required capability {requirement['name']} references "
                f"unknown consumer task {consumer_task}"
            )
    for provider in providers:
        task = provider["task"]
        if task not in task_records:
            errors.append(
                f"{tasks_path}: provided capability {provider['name']} references "
                f"unknown provider task {task}"
            )
            continue
        task_body = str(task_records[task]["body"])
        owned_surfaces = next(
            (
                line
                for line in task_body.splitlines()
                if line.strip().startswith("- Owned surfaces:")
            ),
            "",
        )
        if provider["name"] not in owned_surfaces:
            errors.append(
                f"{tasks_path}: {task} must name provided capability "
                f"{provider['name']} in its owned surfaces"
            )

    return True, requirements, providers, errors


def validate_capability_dependencies(
    spec_dir: Path, contents: dict[str, str]
) -> list[str]:
    """Validate one specification's capability syntax and local task ownership."""
    _, _, _, errors = parse_capability_dependencies(spec_dir, contents["tasks.md"])
    return errors


def spec_reference(spec_dir: Path) -> str:
    return f"specs/{spec_dir.name}"


def task_status(tasks_text: str) -> str:
    lines = section_body(tasks_text, "## Status").splitlines()
    return lines[0].strip() if lines else ""


def capability_cycle(edges: dict[str, set[str]]) -> list[str] | None:
    """Return one cycle in provider-to-consumer order, if present."""
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            index = stack.index(node)
            return stack[index:] + [node]
        if node in visited:
            return None

        visiting.add(node)
        stack.append(node)
        for neighbor in sorted(edges.get(node, set())):
            found = visit(neighbor)
            if found is not None:
                return found
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(edges):
        found = visit(node)
        if found is not None:
            return found
    return None


def validate_capability_graph(
    specs_root: Path, all_contents: dict[Path, dict[str, str]]
) -> list[str]:
    """Resolve capability providers, readiness, and cycles across specifications."""
    errors: list[str] = []
    parsed: dict[Path, dict[str, object]] = {}
    provider_index: dict[str, list[tuple[Path, str]]] = {}

    for spec_dir, contents in all_contents.items():
        adopted, requirements, providers, parse_errors = parse_capability_dependencies(
            spec_dir, contents["tasks.md"]
        )
        if not adopted or parse_errors:
            continue
        order, records = collect_task_records(
            section_body(contents["tasks.md"], "## Tasks")
        )
        parsed[spec_dir] = {
            "requirements": requirements,
            "providers": providers,
            "order": order,
            "records": records,
            "status": task_status(contents["tasks.md"]),
            "progress": progress_log_text(contents),
        }
        for provider in providers:
            provider_index.setdefault(provider["name"], []).append(
                (spec_dir, provider["task"])
            )

    for name, owners in sorted(provider_index.items()):
        if len(owners) > 1:
            rendered = ", ".join(
                f"{spec_reference(spec_dir)}#{task}" for spec_dir, task in owners
            )
            errors.append(
                f"{specs_root}: capability {name} has multiple providers: {rendered}"
            )

    for spec_dir, contract in parsed.items():
        records = contract["records"]
        progress = str(contract["progress"])
        for provider in contract["providers"]:
            provider_task = provider["task"]
            provider_record = records.get(provider_task)
            if (
                provider_record is not None
                and bool(provider_record["complete"])
                and provider["name"] not in progress
            ):
                errors.append(
                    f"{spec_dir / 'tasks.md'}: completed provider {provider_task} "
                    f"must record readiness for {provider['name']} in {PROGRESS_FILENAME}"
                )

    edges: dict[str, set[str]] = {}
    for spec_dir, contract in parsed.items():
        consumer_ref = spec_reference(spec_dir)
        records = contract["records"]
        order = contract["order"]
        first_incomplete = next(
            (
                label
                for label in order
                if label in records and not bool(records[label]["complete"])
            ),
            None,
        )

        for requirement in contract["requirements"]:
            name = requirement["name"]
            owners = provider_index.get(name, [])
            if not owners:
                errors.append(
                    f"{spec_dir / 'tasks.md'}: required capability {name} "
                    "has no declared provider"
                )
                continue
            if len(owners) > 1:
                continue

            provider_spec, provider_task = owners[0]
            expected_ref = requirement["provider"]
            expected_task = requirement["provider_task"]
            actual_ref = spec_reference(provider_spec)
            if expected_ref != actual_ref or expected_task != provider_task:
                errors.append(
                    f"{spec_dir / 'tasks.md'}: required capability {name} names "
                    f"{expected_ref}#{expected_task}, but its provider is "
                    f"{actual_ref}#{provider_task}"
                )
                continue
            if provider_spec == spec_dir:
                errors.append(
                    f"{spec_dir / 'tasks.md'}: capability {name} is a self-dependency; "
                    "use the task Depends on contract instead"
                )
                continue

            provider_contract = parsed.get(provider_spec)
            if provider_contract is None:
                continue
            provider_records = provider_contract["records"]
            provider_record = provider_records.get(provider_task)
            consumer_task = requirement["consumer_task"]
            consumer_record = records.get(consumer_task)
            if provider_record is None or consumer_record is None:
                continue

            provider_complete = bool(provider_record["complete"])
            consumer_complete = bool(consumer_record["complete"])
            if not provider_complete and consumer_complete:
                errors.append(
                    f"{spec_dir / 'tasks.md'}: completed consumer {consumer_task} "
                    f"requires unavailable {name} from {actual_ref}#{provider_task}"
                )
            if (
                not provider_complete
                and "Status: In Progress" in str(consumer_record["body"])
            ):
                errors.append(
                    f"{spec_dir / 'tasks.md'}: {consumer_task} cannot be In Progress "
                    f"while {name} is unavailable"
                )
            if not provider_complete and first_incomplete == consumer_task:
                if contract["status"] != "Blocked":
                    errors.append(
                        f"{spec_dir / 'tasks.md'}: next task {consumer_task} requires "
                        f"unavailable {name}; slice status must be Blocked"
                    )

            edges.setdefault(actual_ref, set()).add(consumer_ref)
            edges.setdefault(consumer_ref, set())

    cycle = capability_cycle(edges)
    if cycle is not None:
        errors.append(
            f"{specs_root}: cross-specification capability cycle: "
            + " -> ".join(cycle)
        )

    return errors


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


def validate_spec_directory(
    spec_dir: Path,
) -> tuple[dict[str, str], list[str]]:
    """Load and validate one specification directory."""
    errors: list[str] = []
    contents: dict[str, str] = {}
    for filename, headings in REQUIRED_FILES.items():
        path = spec_dir / filename
        if not path.is_file():
            hint = (
                "; run python3 .agents/scripts/split_progress_log.py"
                if filename == PROGRESS_FILENAME
                else ""
            )
            errors.append(f"{path}: required file is missing{hint}")
            continue
        contents[filename] = path.read_text(encoding="utf-8")
        errors.extend(validate_file(path, headings))

    if "tasks.md" in contents:
        errors.extend(validate_progress_log_split(spec_dir, contents))

    if len(contents) == len(REQUIRED_FILES):
        errors.extend(validate_cross_file(spec_dir, contents))
        errors.extend(validate_task_dependencies(spec_dir, contents))
        errors.extend(validate_traceability(spec_dir, contents))
        errors.extend(validate_capability_dependencies(spec_dir, contents))
        errors.extend(validate_slice_size_gate(spec_dir, contents))
        errors.extend(validate_task_size_gate(spec_dir, contents))
        errors.extend(validate_proof_scope_gate(spec_dir, contents))

    return contents, errors


def validate_all_specs(specs_root: Path) -> tuple[int, list[str]]:
    """Validate every specification plus the adopted capability graph."""
    spec_dirs = sorted(
        path
        for path in specs_root.iterdir()
        if path.is_dir() and any((path / filename).exists() for filename in REQUIRED_FILES)
    )
    if not spec_dirs:
        return 0, [f"{specs_root}: no specification directories found"]

    errors: list[str] = []
    all_contents: dict[Path, dict[str, str]] = {}
    for spec_dir in spec_dirs:
        contents, spec_errors = validate_spec_directory(spec_dir)
        errors.extend(spec_errors)
        if len(contents) == len(REQUIRED_FILES):
            all_contents[spec_dir] = contents
    errors.extend(validate_capability_graph(specs_root, all_contents))
    return len(spec_dirs), errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "spec_dir",
        nargs="?",
        type=Path,
        help="Directory containing requirements.md, design.md, and tasks.md",
    )
    parser.add_argument(
        "--all",
        dest="specs_root",
        type=Path,
        help="Validate every specification and the capability graph under this directory",
    )
    args = parser.parse_args()

    if (args.spec_dir is None) == (args.specs_root is None):
        parser.error("provide one spec_dir or --all SPECS_ROOT")

    if args.specs_root is not None:
        specs_root = args.specs_root
        if not specs_root.is_dir():
            print(
                f"Spec graph validation failed: {specs_root} is not a directory",
                file=sys.stderr,
            )
            return 1
        count, errors = validate_all_specs(specs_root)
        if errors:
            print(f"Spec graph validation failed: {specs_root}", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(
            f"Spec graph validation passed: {count} specifications under {specs_root}"
        )
        return 0

    spec_dir = args.spec_dir
    assert spec_dir is not None
    if not spec_dir.is_dir():
        print(f"Spec validation failed: {spec_dir} is not a directory", file=sys.stderr)
        return 1

    _, errors = validate_spec_directory(spec_dir)

    if errors:
        print(f"Spec validation failed: {spec_dir}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Spec validation passed: {spec_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
