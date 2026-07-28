#!/usr/bin/env python3
"""Regression tests for the SDD specification validator."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).with_name("validate_spec.py")
SPEC = importlib.util.spec_from_file_location("validate_spec", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
validate_spec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_spec)


REQUIREMENTS = """\
# Example

## Acceptance Criteria

- [AC-01] Active behavior works.
- [AC-02] Release behavior works.
- [AC-03] Deferred behavior works.
"""

DESIGN = """\
# Example Design

## Data and Access Boundaries

- `TrainingRequest`: active-slice record.
- `ReleaseReceipt`: release-only record.
- `FutureAudit`: deferred record.
"""

BOUNDARY = """\
## Implementation Boundary

Traceability:

- Deferred criteria: AC-03
- Release criteria: AC-02
- Deferred entities: entity:FutureAudit
- Release entities: entity:ReleaseReceipt
"""

TASKS = """\
## Tasks

- [ ] Task 1 — Implement active behavior.
  - Owns: AC-01, entity:TrainingRequest

- [ ] Task 2 — Run integration proof.
  - Owns: none (integration only).
"""

DEPENDENCY_TASKS = """\
## Tasks

- [ ] Task 1 — Establish the baseline.
  - Depends on: none

- [ ] Task 2 — Deliver the workflow.
  - Depends on: Task 1

- [ ] Task 3 — Verify integration.
  - Depends on: Task 1, Task 2
"""


def capability_tasks(
    *,
    status: str,
    requires: str,
    provides: str,
    tasks: str,
    progress: str = "- Implementation has not started.",
) -> str:
    return f"""\
# Example Tasks

## Status

{status}

## Active Slice

Deliver the example capability contract.

## Cross-Specification Dependencies

Requires:

{requires}

Provides:

{provides}

## Implementation Boundary

Included:

- The example capability contract.

## Tasks

{tasks}

## Verification Gate

- [ ] The example proof passes.

## Blocked Decisions

- None.

## Progress Log

{progress}
"""


def provider_task(capability: str, *, complete: bool = False) -> str:
    checkbox = "x" if complete else " "
    return f"""\
- [{checkbox}] Task 1 — Deliver the provider contract.
  - Owned surfaces: {capability} readiness write-back.
  - Owns: none (provider contract only).
  - Depends on: none
  - Proof: The provider contract passes.
"""


def consumer_task(*, complete: bool = False, in_progress: bool = False) -> str:
    checkbox = "x" if complete else " "
    status = "\n  - Status: In Progress" if in_progress else ""
    return f"""\
- [{checkbox}] Task 1 — Consume the provider contract.{status}
  - Owned surfaces: Consumer behavior.
  - Owns: none (consumer contract only).
  - Depends on: none
  - Proof: The consumer contract passes.
"""


def requires(capability: str, provider: str, provider_task: int = 1, consumer_task: int = 1) -> str:
    return (
        f"- `{capability}` — provider `{provider}#Task {provider_task}` — "
        f"required before `Task {consumer_task}`."
    )


def provides(capability: str, task: int = 1) -> str:
    return f"- `{capability}` — ready after `Task {task}`."


class TraceabilityValidationTests(unittest.TestCase):
    def errors(self, boundary: str = BOUNDARY, tasks: str = TASKS) -> list[str]:
        contents = {
            "requirements.md": REQUIREMENTS,
            "design.md": DESIGN,
            "tasks.md": f"# Example Tasks\n\n{boundary}\n\n{tasks}",
        }
        return validate_spec.validate_traceability(Path("specs/example"), contents)

    def test_accepts_task_owned_deferred_and_release_coverage(self) -> None:
        self.assertEqual([], self.errors())

    def test_requires_exactly_one_owns_line_per_task(self) -> None:
        tasks = TASKS.replace("  - Owns: none (integration only).\n", "")
        self.assertTrue(any("Task 2 is missing an Owns line" in error for error in self.errors(tasks=tasks)))

    def test_rejects_uncovered_criterion(self) -> None:
        boundary = BOUNDARY.replace("- Release criteria: AC-02", "- Release criteria: none")
        self.assertTrue(any("AC-02 has no coverage" in error for error in self.errors(boundary=boundary)))

    def test_rejects_task_owned_and_classified_criterion(self) -> None:
        tasks = TASKS.replace("AC-01, entity:TrainingRequest", "AC-01, AC-02, entity:TrainingRequest")
        self.assertTrue(any("AC-02 is both task-owned and classified release" in error for error in self.errors(tasks=tasks)))

    def test_rejects_multiple_criterion_owners(self) -> None:
        tasks = TASKS.replace("Owns: none (integration only).", "Owns: AC-01")
        self.assertTrue(any("AC-01 is owned by multiple tasks" in error for error in self.errors(tasks=tasks)))

    def test_allows_multiple_active_entity_owners(self) -> None:
        tasks = TASKS.replace("Owns: none (integration only).", "Owns: entity:TrainingRequest")
        self.assertEqual([], self.errors(tasks=tasks))

    def test_rejects_malformed_classification_token(self) -> None:
        boundary = BOUNDARY.replace(
            "- Release entities: entity:ReleaseReceipt",
            "- Release entities: ReleaseReceipt",
        )
        errors = self.errors(boundary=boundary)
        self.assertTrue(any("release entities token 'ReleaseReceipt' has the wrong format" in error for error in errors))


class TaskDependencyValidationTests(unittest.TestCase):
    def errors(self, tasks: str = DEPENDENCY_TASKS) -> list[str]:
        contents = {
            "requirements.md": REQUIREMENTS,
            "design.md": DESIGN,
            "tasks.md": f"# Example Tasks\n\n{tasks}",
        }
        return validate_spec.validate_task_dependencies(Path("specs/example"), contents)

    def test_accepts_backward_dependencies(self) -> None:
        self.assertEqual([], self.errors())

    def test_requires_one_dependency_line_per_task_after_opt_in(self) -> None:
        tasks = DEPENDENCY_TASKS.replace("  - Depends on: Task 1\n", "", 1)
        self.assertTrue(any("Task 2 is missing a Depends on line" in error for error in self.errors(tasks)))

    def test_rejects_forward_dependency(self) -> None:
        tasks = DEPENDENCY_TASKS.replace("  - Depends on: none", "  - Depends on: Task 2")
        self.assertTrue(
            any("Task 1 depends on Task 2, which is not an earlier task" in error for error in self.errors(tasks))
        )

    def test_rejects_unknown_dependency(self) -> None:
        tasks = DEPENDENCY_TASKS.replace("  - Depends on: Task 1\n", "  - Depends on: Task 9\n", 1)
        self.assertTrue(any("Task 2 depends on unknown task Task 9" in error for error in self.errors(tasks)))

    def test_rejects_multiple_dependency_lines(self) -> None:
        tasks = DEPENDENCY_TASKS.replace(
            "  - Depends on: Task 1\n",
            "  - Depends on: Task 1\n  - Depends on: none\n",
            1,
        )
        self.assertTrue(any("Task 2 has multiple Depends on lines" in error for error in self.errors(tasks)))

    def test_rejects_duplicate_task_labels(self) -> None:
        tasks = DEPENDENCY_TASKS.replace("Task 3 — Verify", "Task 2 — Verify")
        self.assertTrue(any("duplicate task label Task 2" in error for error in self.errors(tasks)))

    def test_rejects_unstable_task_label(self) -> None:
        tasks = DEPENDENCY_TASKS.replace("Task 2 — Deliver", "Deliver workflow — Deliver")
        self.assertTrue(
            any("dependency-enabled task label 'Deliver workflow' must be 'Task <n>'" in error for error in self.errors(tasks))
        )


class CapabilityDependencyValidationTests(unittest.TestCase):
    capability = "capability:example-contract"

    def errors(self, tasks: str) -> list[str]:
        return validate_spec.validate_capability_dependencies(
            Path("specs/example"),
            {"tasks.md": tasks},
        )

    def valid_tasks(self) -> str:
        tasks = f"""\
- [ ] Task 1 — Consume the provider contract.
  - Owned surfaces: Consumer behavior.
  - Depends on: none

- [ ] Task 2 — Deliver the example contract.
  - Owned surfaces: {self.capability} readiness write-back.
  - Depends on: Task 1
"""
        return capability_tasks(
            status="Blocked",
            requires=requires(self.capability, "specs/provider"),
            provides=provides(self.capability, 2),
            tasks=tasks,
        )

    def test_accepts_exact_capability_contract(self) -> None:
        self.assertEqual([], self.errors(self.valid_tasks()))

    def test_rejects_malformed_requirement(self) -> None:
        tasks = self.valid_tasks().replace(
            "required before `Task 1`.",
            "required before Task 1.",
        )
        self.assertTrue(
            any("malformed requires entry" in error for error in self.errors(tasks))
        )

    def test_rejects_unknown_consumer_task(self) -> None:
        tasks = self.valid_tasks().replace(
            "required before `Task 1`.",
            "required before `Task 9`.",
        )
        self.assertTrue(
            any("references unknown consumer task Task 9" in error for error in self.errors(tasks))
        )

    def test_provider_task_must_own_readiness_write_back(self) -> None:
        tasks = self.valid_tasks().replace(
            f"Owned surfaces: {self.capability} readiness write-back.",
            f"Purpose: Mention {self.capability} without owning its readiness write-back.\n"
            "  - Owned surfaces: Provider implementation.",
        )
        self.assertTrue(
            any("must name provided capability" in error for error in self.errors(tasks))
        )

    def test_rejects_none_mixed_with_capability(self) -> None:
        tasks = self.valid_tasks().replace(
            "Requires:\n\n",
            "Requires:\n\n- None.\n",
        )
        self.assertTrue(
            any("Requires cannot mix None" in error for error in self.errors(tasks))
        )


class CapabilityGraphValidationTests(unittest.TestCase):
    capability = "capability:shared-contract"

    def provider(
        self,
        *,
        spec: str = "provider",
        complete: bool = False,
        progress: str = "- Implementation has not started.",
    ) -> tuple[Path, dict[str, str]]:
        return Path(f"specs/{spec}"), {
            "tasks.md": capability_tasks(
                status="Not Started",
                requires="- None.",
                provides=provides(self.capability),
                tasks=provider_task(self.capability, complete=complete),
                progress=progress,
            )
        }

    def consumer(
        self,
        *,
        provider: str = "specs/provider",
        status: str = "Blocked",
        complete: bool = False,
        in_progress: bool = False,
        provided_capability: str | None = None,
    ) -> tuple[Path, dict[str, str]]:
        capability_provision = (
            provides(provided_capability)
            if provided_capability is not None
            else "- None."
        )
        task = consumer_task(complete=complete, in_progress=in_progress)
        if provided_capability is not None:
            task = task.replace(
                "Owned surfaces: Consumer behavior.",
                f"Owned surfaces: Consumer behavior and {provided_capability} readiness write-back.",
            )
        return Path("specs/consumer"), {
            "tasks.md": capability_tasks(
                status=status,
                requires=requires(self.capability, provider),
                provides=capability_provision,
                tasks=task,
            )
        }

    def errors(self, *specs: tuple[Path, dict[str, str]]) -> list[str]:
        return validate_spec.validate_capability_graph(
            Path("specs"),
            dict(specs),
        )

    def test_accepts_blocked_consumer_until_provider_is_ready(self) -> None:
        self.assertEqual([], self.errors(self.provider(), self.consumer()))

    def test_accepts_available_provider_and_unblocked_consumer(self) -> None:
        provider = self.provider(
            complete=True,
            progress=f"- Task 1 completed; {self.capability} is ready.",
        )
        consumer = self.consumer(status="Not Started")
        self.assertEqual([], self.errors(provider, consumer))

    def test_rejects_missing_provider(self) -> None:
        self.assertTrue(
            any("has no declared provider" in error for error in self.errors(self.consumer()))
        )

    def test_rejects_ambiguous_provider(self) -> None:
        self.assertTrue(
            any(
                "has multiple providers" in error
                for error in self.errors(
                    self.provider(spec="provider"),
                    self.provider(spec="other-provider"),
                    self.consumer(),
                )
            )
        )

    def test_rejects_incorrect_named_provider(self) -> None:
        self.assertTrue(
            any(
                "but its provider is specs/provider#Task 1" in error
                for error in self.errors(
                    self.provider(),
                    self.consumer(provider="specs/wrong-provider"),
                )
            )
        )

    def test_completed_provider_requires_readiness_write_back(self) -> None:
        self.assertTrue(
            any(
                "must record readiness" in error
                for error in self.errors(self.provider(complete=True))
            )
        )

    def test_rejects_completed_consumer_with_unavailable_provider(self) -> None:
        self.assertTrue(
            any(
                "completed consumer Task 1 requires unavailable" in error
                for error in self.errors(
                    self.provider(),
                    self.consumer(complete=True, status="Not Started"),
                )
            )
        )

    def test_next_blocked_consumer_requires_blocked_slice_status(self) -> None:
        self.assertTrue(
            any(
                "slice status must be Blocked" in error
                for error in self.errors(
                    self.provider(),
                    self.consumer(status="Not Started"),
                )
            )
        )

    def test_unavailable_consumer_cannot_be_in_progress(self) -> None:
        self.assertTrue(
            any(
                "cannot be In Progress" in error
                for error in self.errors(
                    self.provider(),
                    self.consumer(in_progress=True),
                )
            )
        )

    def test_rejects_cross_specification_cycle(self) -> None:
        first_capability = "capability:first"
        second_capability = "capability:second"
        first = Path("specs/first"), {
            "tasks.md": capability_tasks(
                status="Blocked",
                requires=requires(second_capability, "specs/second"),
                provides=provides(first_capability),
                tasks=provider_task(first_capability),
            )
        }
        second = Path("specs/second"), {
            "tasks.md": capability_tasks(
                status="Blocked",
                requires=requires(first_capability, "specs/first"),
                provides=provides(second_capability),
                tasks=provider_task(second_capability),
            )
        }
        self.assertTrue(
            any(
                "cross-specification capability cycle" in error
                for error in self.errors(first, second)
            )
        )


if __name__ == "__main__":
    unittest.main()
