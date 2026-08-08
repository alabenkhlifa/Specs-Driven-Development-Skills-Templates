#!/usr/bin/env python3
"""Answer cross-specification capability questions without opening a provider task plan.

The implement-spec preflight must confirm that each capability its active task
requires is available. Doing that by hand means reading whole provider tasks.md
files. This read-only index resolves every `## Cross-Specification Dependencies`
declaration under specs/ into one line per capability: provider, readiness, and
the consumers that require it.

Readiness follows the repository rule that a provided capability becomes
available only after its named provider task is checked complete. This tool
reports that checkbox state as a fast lookup. validate_spec.py remains the
authority for gate validation; a `ready` line here is a pointer, not approval.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


CAPABILITY_HEADING = "## Cross-Specification Dependencies"
TASKS_HEADING = "## Tasks"
CAPABILITY_SLUG_PATTERN = r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
CAPABILITY_NAME_PATTERN = rf"capability:{CAPABILITY_SLUG_PATTERN}"
SPEC_REFERENCE_PATTERN = rf"specs/{CAPABILITY_SLUG_PATTERN}"
REQUIREMENT_RE = re.compile(
    rf"^- `(?P<name>{CAPABILITY_NAME_PATTERN})` — "
    rf"provider `(?P<provider>{SPEC_REFERENCE_PATTERN})#(?P<provider_task>Task \d+)` — "
    r"required before `(?P<consumer_task>Task \d+)`\.$"
)
PROVISION_RE = re.compile(
    rf"^- `(?P<name>{CAPABILITY_NAME_PATTERN})` — ready after `(?P<task>Task \d+)`\.$"
)
TASK_RECORD_RE = re.compile(r"^- \[([ xX])\]\s+(.+)$")
TASK_LABEL_SPLIT_RE = re.compile(r"\s[—-]\s")
TASK_ID_RE = re.compile(r"^Task (\d+)$")

STATE_READY = "ready"
STATE_PENDING = "pending"
STATE_MISSING = "missing"
STATE_AMBIGUOUS = "ambiguous"
STATE_UNRESOLVED = "unresolved"
BLOCKING_STATES = frozenset({STATE_MISSING, STATE_AMBIGUOUS, STATE_UNRESOLVED})
STATE_WIDTH = len(STATE_AMBIGUOUS)


@dataclass(frozen=True)
class Requirement:
    """One `Requires:` entry declared by a consuming specification."""

    name: str
    declared_provider: str
    declared_provider_task: str
    consumer_spec: str
    consumer_task: str

    @property
    def consumer_reference(self) -> str:
        return f"{self.consumer_spec}#{self.consumer_task}"


@dataclass(frozen=True)
class Provision:
    """One `Provides:` entry declared by a providing specification."""

    name: str
    spec: str
    task: str

    @property
    def reference(self) -> str:
        return f"{self.spec}#{self.task}"


@dataclass
class Spec:
    """The capability contract and task checkbox state of one specification."""

    reference: str
    path: Path
    adopted: bool = False
    requirements: list[Requirement] = field(default_factory=list)
    provisions: list[Provision] = field(default_factory=list)
    tasks: dict[str, bool] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)


@dataclass
class Capability:
    """One capability resolved across every specification that names it."""

    name: str
    state: str
    provider: str | None
    consumers: list[Requirement] = field(default_factory=list)


def section_body(text: str, heading: str) -> str:
    """Return the lines between one H2 heading and the next."""
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


def task_sort_key(task: str) -> int:
    """Order task labels numerically instead of lexically."""
    match = TASK_ID_RE.match(task)
    return int(match.group(1)) if match else 0


def reference_sort_key(reference: str) -> tuple[str, int]:
    spec, _, task = reference.partition("#")
    return spec, task_sort_key(task)


def collect_task_completion(tasks_body: str) -> dict[str, bool]:
    """Map every stable task label to its checkbox completion state."""
    completion: dict[str, bool] = {}
    for line in tasks_body.splitlines():
        record = TASK_RECORD_RE.match(line)
        if record is None:
            continue
        label = TASK_LABEL_SPLIT_RE.split(record.group(2), maxsplit=1)[0].strip()
        if TASK_ID_RE.match(label) and label not in completion:
            completion[label] = record.group(1) in {"x", "X"}
    return completion


def parse_spec(reference: str, path: Path, tasks_text: str) -> Spec:
    """Parse one tasks.md into its capability contract and task checkbox state."""
    spec = Spec(reference=reference, path=path)
    spec.tasks = collect_task_completion(section_body(tasks_text, TASKS_HEADING))
    if CAPABILITY_HEADING not in tasks_text:
        return spec

    spec.adopted = True
    mode: str | None = None
    for line in section_body(tasks_text, CAPABILITY_HEADING).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"Requires:", "Provides:"}:
            mode = stripped[:-1].lower()
            continue
        if stripped == "- None.":
            continue
        if mode is None:
            spec.problems.append(
                f"{reference}: capability entry before Requires or Provides: {stripped}"
            )
            continue

        if mode == "requires":
            requirement = REQUIREMENT_RE.fullmatch(stripped)
            if requirement is None:
                spec.problems.append(f"{reference}: malformed requires entry: {stripped}")
                continue
            spec.requirements.append(
                Requirement(
                    name=requirement.group("name").removeprefix("capability:"),
                    declared_provider=requirement.group("provider"),
                    declared_provider_task=requirement.group("provider_task"),
                    consumer_spec=reference,
                    consumer_task=requirement.group("consumer_task"),
                )
            )
            continue

        provision = PROVISION_RE.fullmatch(stripped)
        if provision is None:
            spec.problems.append(f"{reference}: malformed provides entry: {stripped}")
            continue
        spec.provisions.append(
            Provision(
                name=provision.group("name").removeprefix("capability:"),
                spec=reference,
                task=provision.group("task"),
            )
        )

    return spec


def load_specs(specs_root: Path) -> list[Spec]:
    """Read every specification directory that has a tasks.md."""
    specs: list[Spec] = []
    for directory in sorted(path for path in specs_root.iterdir() if path.is_dir()):
        tasks_path = directory / "tasks.md"
        if not tasks_path.is_file():
            continue
        specs.append(
            parse_spec(
                f"specs/{directory.name}",
                tasks_path,
                tasks_path.read_text(encoding="utf-8"),
            )
        )
    return specs


def find_cycle(edges: dict[str, set[str]]) -> list[str] | None:
    """Return one provider-to-consumer cycle over spec#task nodes, if present."""
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            return stack[stack.index(node) :] + [node]
        if node in visited:
            return None

        visiting.add(node)
        stack.append(node)
        for neighbor in sorted(edges.get(node, set())):
            found = visit(neighbor)
            if found is not None:
                return found
        stack.pop()
        visiting.discard(node)
        visited.add(node)
        return None

    for node in sorted(edges):
        found = visit(node)
        if found is not None:
            return found
    return None


def build_index(specs: list[Spec]) -> tuple[list[Capability], list[str]]:
    """Resolve providers, readiness, consumers, and graph problems."""
    problems: list[str] = []
    for spec in specs:
        problems.extend(spec.problems)

    by_reference = {spec.reference: spec for spec in specs}
    provisions: dict[str, list[Provision]] = {}
    for spec in specs:
        for provision in spec.provisions:
            provisions.setdefault(provision.name, []).append(provision)

    consumers: dict[str, list[Requirement]] = {}
    for spec in specs:
        for requirement in spec.requirements:
            consumers.setdefault(requirement.name, []).append(requirement)

    capabilities: list[Capability] = []
    edges: dict[str, set[str]] = {}
    for name in sorted(set(provisions) | set(consumers)):
        owners = provisions.get(name, [])
        required_by = sorted(
            consumers.get(name, []), key=lambda item: reference_sort_key(item.consumer_reference)
        )

        if not owners:
            state = STATE_MISSING
            provider_reference: str | None = None
            for requirement in required_by:
                problems.append(
                    f"{requirement.consumer_reference}: requires {name} but no "
                    "specification provides it"
                )
        elif len(owners) > 1:
            state = STATE_AMBIGUOUS
            provider_reference = None
            rendered = ", ".join(sorted(owner.reference for owner in owners))
            problems.append(f"{name}: provided by more than one specification: {rendered}")
        else:
            owner = owners[0]
            provider_reference = owner.reference
            provider_spec = by_reference[owner.spec]
            if owner.task not in provider_spec.tasks:
                state = STATE_UNRESOLVED
                problems.append(
                    f"{owner.spec}: provides {name} from unknown {owner.task}"
                )
            else:
                state = STATE_READY if provider_spec.tasks[owner.task] else STATE_PENDING

            for requirement in required_by:
                if requirement.declared_provider != owner.spec:
                    problems.append(
                        f"{requirement.consumer_reference}: requires {name} from "
                        f"{requirement.declared_provider} but {owner.spec} provides it"
                    )
                elif requirement.declared_provider_task != owner.task:
                    problems.append(
                        f"{requirement.consumer_reference}: requires {name} from "
                        f"{requirement.declared_provider}#{requirement.declared_provider_task} "
                        f"but it is ready after {owner.task}"
                    )
                if requirement.consumer_spec == owner.spec:
                    problems.append(
                        f"{requirement.consumer_reference}: requires {name} from itself"
                    )
                    continue
                edges.setdefault(owner.reference, set()).add(requirement.consumer_reference)
                edges.setdefault(requirement.consumer_reference, set())

        capabilities.append(
            Capability(
                name=name,
                state=state,
                provider=provider_reference,
                consumers=required_by,
            )
        )

    cycle = find_cycle(edges)
    if cycle is not None:
        problems.append("capability cycle: " + " -> ".join(cycle))

    return capabilities, problems


def render_listing(capabilities: list[Capability], specs: list[Spec]) -> list[str]:
    """Render one grep-friendly line per capability plus a summary."""
    lines: list[str] = []
    for capability in capabilities:
        provider = capability.provider or "none"
        consumers = (
            ",".join(requirement.consumer_reference for requirement in capability.consumers)
            or "none"
        )
        lines.append(
            f"{capability.state:<{STATE_WIDTH}}  {capability.name}  "
            f"provider={provider}  consumers={consumers}"
        )

    counts = {state: 0 for state in (STATE_READY, STATE_PENDING, *sorted(BLOCKING_STATES))}
    for capability in capabilities:
        counts[capability.state] += 1
    summary = ", ".join(f"{count} {state}" for state, count in counts.items() if count)
    lines.append(f"{len(capabilities)} capabilities: {summary or 'none'}")

    legacy = [spec.reference for spec in specs if not spec.adopted]
    if legacy:
        lines.append(f"no capability section: {', '.join(legacy)}")
    return lines


def render_capability(capability: Capability) -> list[str]:
    """Render the single-capability answer the preflight needs."""
    lines = [
        f"capability  {capability.name}",
        f"provider    {capability.provider or 'none'}",
        f"state       {capability.state}",
    ]
    if not capability.consumers:
        return [*lines, "consumers   none"]

    label = "consumers  "
    for requirement in capability.consumers:
        lines.append(f"{label} {requirement.consumer_reference}")
        label = " " * len(label)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--specs",
        dest="specs_root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "specs",
        help="Specifications directory to index (default: the repository specs/ tree)",
    )
    parser.add_argument(
        "--capability",
        help="Report one capability instead of the whole index; accepts capability:<name>",
    )
    args = parser.parse_args()

    specs_root = args.specs_root
    if not specs_root.is_dir():
        print(f"capability index failed: {specs_root} is not a directory", file=sys.stderr)
        return 2

    specs = load_specs(specs_root)
    capabilities, problems = build_index(specs)

    if args.capability is None:
        for line in render_listing(capabilities, specs):
            print(line)
        if problems:
            print(f"capability graph problems: {len(problems)}", file=sys.stderr)
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        return 0

    wanted = args.capability.removeprefix("capability:")
    match = next((entry for entry in capabilities if entry.name == wanted), None)
    if match is None:
        print(f"unknown capability: {wanted}", file=sys.stderr)
        return 2

    for line in render_capability(match):
        print(line)

    references = {match.provider, *(item.consumer_reference for item in match.consumers)}
    related = [
        problem
        for problem in problems
        if wanted in problem
        or (
            problem.startswith("capability cycle: ")
            and any(reference and reference in problem for reference in references)
        )
    ]
    if related:
        for problem in related:
            print(f"- {problem}", file=sys.stderr)
        return 1
    if problems:
        print(
            f"note: {len(problems)} unrelated graph problems; run without --capability",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
