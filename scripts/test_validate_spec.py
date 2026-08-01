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


def task_size_document(tasks: str, *, gate_after_boundary: bool = False) -> str:
    gate = """\
## Task Size Gate

- Standard tasks deliver one independently provable outcome in one task-boundary commit.
- Exceptions are allowed only when splitting creates an invalid intermediate state.
"""
    boundary = """\
## Implementation Boundary

- The example task-size contract.
"""
    ordered_sections = (
        f"{boundary}\n{gate}" if gate_after_boundary else f"{gate}\n{boundary}"
    )
    return f"""\
# Example Tasks

## Status

Not Started

## Active Slice

Deliver the example.

## Cross-Specification Dependencies

Requires:

- None.

Provides:

- None.

{ordered_sections}
## Tasks

{tasks}

## Verification Gate

- [ ] The example proof passes.

## Blocked Decisions

- None.

## Progress Log

- Implementation has not started.
"""


def slice_size_document(
    tasks: str,
    *,
    declaration: str | None = "- Slice size: Standard",
    duplicate_declaration: bool = False,
    gate_after_task_size: bool = False,
) -> str:
    declarations = "" if declaration is None else f"{declaration}\n"
    if duplicate_declaration and declaration is not None:
        declarations += f"{declaration}\n"
    slice_gate = f"""\
## Slice Size Gate

{declarations}"""
    task_gate = """\
## Task Size Gate

- Standard tasks deliver one independently provable outcome in one task-boundary commit.
- Exceptions are allowed only when splitting creates an invalid intermediate state.
"""
    ordered_gates = (
        f"{task_gate}\n{slice_gate}" if gate_after_task_size else f"{slice_gate}\n{task_gate}"
    )
    return f"""\
# Example Tasks

## Status

Not Started

## Active Slice

Deliver the example.

## Cross-Specification Dependencies

Requires:

- None.

Provides:

- None.

{ordered_gates}
## Implementation Boundary

- The example slice-size contract.

## Tasks

{tasks}

## Verification Gate

- [ ] The example proof passes.

## Blocked Decisions

- None.

## Progress Log

- Implementation has not started.
"""


def proof_scope_document(
    tasks: str,
    *,
    applies_to: str = "all tasks.",
    progress: str = "- Implementation has not started.",
    proof_gate_after_boundary: bool = False,
) -> str:
    size_gate = """\
## Task Size Gate

- Standard tasks deliver one independently provable outcome in one task-boundary commit.
- Exceptions are allowed only when splitting creates an invalid intermediate state.
"""
    proof_gate = f"""\
## Proof Scope Gate

- Applies to: {applies_to}
"""
    boundary = """\
## Implementation Boundary

- The example proof-scope contract.
"""
    ordered_sections = (
        f"{size_gate}\n{boundary}\n{proof_gate}"
        if proof_gate_after_boundary
        else f"{size_gate}\n{proof_gate}\n{boundary}"
    )
    return f"""\
# Example Tasks

## Status

Not Started

## Active Slice

Deliver the example.

{ordered_sections}
## Tasks

{tasks}

## Verification Gate

- [ ] The example proof passes.

## Blocked Decisions

- None.

## Progress Log

{progress}
"""


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


class SliceSizeValidationTests(unittest.TestCase):
    def errors(self, tasks: str) -> list[str]:
        return validate_spec.validate_slice_size_gate(
            Path("specs/example"),
            {"tasks.md": tasks},
        )

    def task(self, number: int, dependencies: str = "none") -> str:
        return f"""\
- [ ] Task {number} — Deliver outcome {number}.
  - Size: Standard
  - Owns: none (slice-size contract only).
  - Depends on: {dependencies}
  - Proof: The focused proof passes.
"""

    def graph(self, dependencies: list[str]) -> str:
        return "\n".join(
            self.task(number, dependency)
            for number, dependency in enumerate(dependencies, start=1)
        )

    def test_legacy_spec_without_gate_remains_valid(self) -> None:
        self.assertEqual(
            [],
            self.errors("# Tasks\n\n## Tasks\n\n" + self.task(1)),
        )

    def test_requires_gate_between_capability_and_task_size_sections(self) -> None:
        errors = self.errors(
            slice_size_document(self.task(1), gate_after_task_size=True)
        )
        self.assertTrue(any("must appear after" in error for error in errors))

    def test_requires_exactly_one_top_level_declaration(self) -> None:
        missing = slice_size_document(self.task(1), declaration=None)
        self.assertTrue(
            any("is missing a top-level" in error for error in self.errors(missing))
        )

        duplicate = slice_size_document(
            self.task(1),
            duplicate_declaration=True,
        )
        self.assertTrue(
            any("has multiple top-level" in error for error in self.errors(duplicate))
        )

    def test_rejects_malformed_declaration(self) -> None:
        malformed = slice_size_document(
            self.task(1),
            declaration="- Slice size: Exception —",
        )
        self.assertTrue(
            any("Slice size must be" in error for error in self.errors(malformed))
        )

    def test_accepts_exact_twelve_tasks_and_eight_task_path(self) -> None:
        dependencies = ["none"]
        dependencies.extend(f"Task {number}" for number in range(1, 8))
        dependencies.extend(["Task 1"] * 4)
        self.assertEqual(
            [],
            self.errors(slice_size_document(self.graph(dependencies))),
        )

    def test_rejects_thirteen_tasks(self) -> None:
        tasks = self.graph(["none"] + ["Task 1"] * 12)
        errors = self.errors(slice_size_document(tasks))
        self.assertTrue(any("Standard slice has 13 tasks" in error for error in errors))

    def test_rejects_nine_task_dependency_path(self) -> None:
        dependencies = ["none"]
        dependencies.extend(f"Task {number}" for number in range(1, 9))
        errors = self.errors(slice_size_document(self.graph(dependencies)))
        self.assertTrue(
            any("longest dependency path of 9 tasks" in error for error in errors)
        )

    def test_accepts_wide_parallel_graph_with_short_critical_path(self) -> None:
        tasks = self.graph(["none"] + ["Task 1"] * 11)
        self.assertEqual([], self.errors(slice_size_document(tasks)))

    def test_exception_bypasses_slice_limits_only(self) -> None:
        dependencies = ["none"]
        dependencies.extend(f"Task {number}" for number in range(1, 13))
        document = slice_size_document(
            self.graph(dependencies),
            declaration=(
                "- Slice size: Exception — Splitting the atomic rollout would "
                "leave consumers without a compatible provider."
            ),
        )
        self.assertEqual([], self.errors(document))

    def test_rejects_unjustified_slice_exception(self) -> None:
        document = slice_size_document(
            self.task(1),
            declaration="- Slice size: Exception — Implementation convenience.",
        )
        self.assertTrue(
            any("must be 'Standard' or a justified" in error for error in self.errors(document))
        )

    def test_malformed_dependencies_do_not_duplicate_path_errors(self) -> None:
        tasks = self.graph(["none", "Task 9"])
        document = slice_size_document(tasks)
        self.assertEqual([], self.errors(document))
        dependency_errors = validate_spec.validate_task_dependencies(
            Path("specs/example"),
            {"tasks.md": document},
        )
        self.assertEqual(1, len(dependency_errors))
        self.assertIn("depends on unknown task Task 9", dependency_errors[0])


class TaskSizeValidationTests(unittest.TestCase):
    def errors(self, tasks: str) -> list[str]:
        return validate_spec.validate_task_size_gate(
            Path("specs/example"),
            {"tasks.md": tasks},
        )

    def standard_task(self, owns: str = "AC-01, entity:Example") -> str:
        return f"""\
- [ ] Task 1 — Deliver one outcome.
  - Size: Standard
  - Owned surfaces: One coherent behavior.
  - Owns: {owns}
  - Depends on: none
  - Proof: The focused proof passes.
"""

    def test_legacy_spec_without_gate_remains_valid(self) -> None:
        self.assertEqual([], self.errors("# Tasks\n\n## Tasks\n\n" + self.standard_task()))

    def test_accepts_standard_task_within_mechanical_limits(self) -> None:
        self.assertEqual([], self.errors(task_size_document(self.standard_task())))

    def test_requires_gate_before_implementation_boundary(self) -> None:
        errors = self.errors(
            task_size_document(self.standard_task(), gate_after_boundary=True)
        )
        self.assertTrue(any("must appear after" in error for error in errors))

    def test_requires_one_size_line_per_task(self) -> None:
        tasks = self.standard_task().replace("  - Size: Standard\n", "")
        self.assertTrue(
            any("Task 1 is missing a Size line" in error for error in self.errors(task_size_document(tasks)))
        )

    def test_rejects_multiple_size_lines(self) -> None:
        tasks = self.standard_task().replace(
            "  - Size: Standard\n",
            "  - Size: Standard\n  - Size: Standard\n",
        )
        self.assertTrue(
            any("Task 1 has multiple Size lines" in error for error in self.errors(task_size_document(tasks)))
        )

    def test_standard_task_owns_at_most_three_acceptance_criteria(self) -> None:
        tasks = self.standard_task("AC-01, AC-02, AC-03, AC-04")
        self.assertTrue(
            any("owns 4 acceptance criteria" in error for error in self.errors(task_size_document(tasks)))
        )

    def test_standard_task_owns_at_most_two_entities(self) -> None:
        tasks = self.standard_task("entity:First, entity:Second, entity:Third")
        self.assertTrue(
            any("owns 3 entities" in error for error in self.errors(task_size_document(tasks)))
        )

    def test_accepts_justified_atomic_exception(self) -> None:
        tasks = self.standard_task(
            "AC-01, AC-02, AC-03, AC-04, entity:First, entity:Second, entity:Third"
        ).replace(
            "  - Size: Standard",
            "  - Size: Exception — Splitting the migration from its backfill would expose records without a valid owner.",
        )
        self.assertEqual([], self.errors(task_size_document(tasks)))

    def test_rejects_unexplained_exception(self) -> None:
        tasks = self.standard_task().replace(
            "  - Size: Standard",
            "  - Size: Exception — Cannot be split.",
        )
        self.assertTrue(
            any("must explain the invalid intermediate state" in error for error in self.errors(task_size_document(tasks)))
        )


class ProofScopeValidationTests(unittest.TestCase):
    def errors(self, tasks: str) -> list[str]:
        return validate_spec.validate_proof_scope_gate(
            Path("specs/example"),
            {"tasks.md": tasks},
        )

    def task(
        self,
        number: int,
        *,
        complete: bool = False,
        proof_scope: str | None = "Focused",
        duplicate_scope: bool = False,
    ) -> str:
        checkbox = "x" if complete else " "
        scope_lines = ""
        if proof_scope is not None:
            scope_lines = f"  - Proof scope: {proof_scope}\n"
            if duplicate_scope:
                scope_lines += f"  - Proof scope: {proof_scope}\n"
        return f"""\
- [{checkbox}] Task {number} — Deliver one outcome.
  - Size: Standard
{scope_lines}  - Owns: none (proof contract only).
  - Depends on: none
  - Proof: The declared proof passes.
"""

    def receipt(
        self,
        task: int,
        *,
        scope: str = "Focused",
        command: str = "mix test test/example_test.exs",
    ) -> str:
        return (
            f"- Proof receipt: `Task {task}` — scope `{scope}` — "
            f"command `{command}` — exit `0`."
        )

    def test_legacy_spec_without_gate_remains_valid(self) -> None:
        self.assertEqual(
            [],
            self.errors("# Tasks\n\n## Tasks\n\n" + self.task(1)),
        )

    def test_accepts_prospective_task_list_without_rewriting_earlier_tasks(self) -> None:
        tasks = self.task(1, complete=True, proof_scope=None) + "\n" + self.task(2)
        self.assertEqual(
            [],
            self.errors(proof_scope_document(tasks, applies_to="Task 2.")),
        )

    def test_accepts_completed_focused_task_with_exact_receipt(self) -> None:
        document = proof_scope_document(
            self.task(1, complete=True),
            progress=self.receipt(1),
        )
        self.assertEqual([], self.errors(document))

    def test_accepts_completed_broad_task_with_reason_and_broad_receipt(self) -> None:
        document = proof_scope_document(
            self.task(
                1,
                complete=True,
                proof_scope=(
                    "Broad — This task owns the repository-wide dependency "
                    "validation invariant."
                ),
            ),
            progress=self.receipt(1, scope="Broad", command="mix test"),
        )
        self.assertEqual([], self.errors(document))

    def test_requires_gate_between_task_size_and_implementation_boundary(self) -> None:
        errors = self.errors(
            proof_scope_document(self.task(1), proof_gate_after_boundary=True)
        )
        self.assertTrue(any("must appear after" in error for error in errors))

    def test_requires_exactly_one_top_level_applies_to_declaration(self) -> None:
        missing = proof_scope_document(self.task(1)).replace(
            "- Applies to: all tasks.\n",
            "Applies to all tasks.\n",
        )
        self.assertTrue(any("is missing a top-level" in error for error in self.errors(missing)))

        duplicate = proof_scope_document(self.task(1)).replace(
            "- Applies to: all tasks.\n",
            "- Applies to: all tasks.\n- Applies to: Task 1.\n",
        )
        self.assertTrue(any("has multiple top-level" in error for error in self.errors(duplicate)))

    def test_rejects_malformed_and_unknown_applicability_labels(self) -> None:
        malformed = proof_scope_document(self.task(1), applies_to="First task.")
        self.assertTrue(any("must be 'Task <n>'" in error for error in self.errors(malformed)))

        unknown = proof_scope_document(self.task(1), applies_to="Task 1, Task 9.")
        self.assertTrue(any("unknown task Task 9" in error for error in self.errors(unknown)))

    def test_requires_exactly_one_scope_for_each_applicable_task(self) -> None:
        missing = proof_scope_document(self.task(1, proof_scope=None))
        self.assertTrue(any("Task 1 is missing a Proof scope line" in error for error in self.errors(missing)))

        duplicate = proof_scope_document(self.task(1, duplicate_scope=True))
        self.assertTrue(any("Task 1 has multiple Proof scope lines" in error for error in self.errors(duplicate)))

    def test_rejects_malformed_scope_declarations(self) -> None:
        malformed_focused = proof_scope_document(self.task(1, proof_scope="focused"))
        self.assertTrue(any("Proof scope must be" in error for error in self.errors(malformed_focused)))

        empty_broad = proof_scope_document(self.task(1, proof_scope="Broad — ."))
        self.assertTrue(any("Proof scope must be" in error for error in self.errors(empty_broad)))

    def test_incomplete_task_does_not_require_receipt(self) -> None:
        self.assertEqual([], self.errors(proof_scope_document(self.task(1))))

    def test_completed_task_requires_matching_exact_receipt(self) -> None:
        missing = proof_scope_document(self.task(1, complete=True))
        self.assertTrue(any("requires a successful Focused" in error for error in self.errors(missing)))

        wrong_scope = proof_scope_document(
            self.task(1, complete=True),
            progress=self.receipt(1, scope="Broad"),
        )
        self.assertTrue(any("requires a successful Focused" in error for error in self.errors(wrong_scope)))

        malformed = proof_scope_document(
            self.task(1, complete=True),
            progress=self.receipt(1).replace(" — exit `0`.", " — exit 0."),
        )
        self.assertTrue(any("requires a successful Focused" in error for error in self.errors(malformed)))

    def test_verified_status_requires_complete_tasks_gate_and_slice_receipt(self) -> None:
        document = proof_scope_document(self.task(1)).replace(
            "Not Started",
            "Verified",
            1,
        )
        errors = self.errors(document)
        self.assertTrue(any("requires every task complete" in error for error in errors))
        self.assertTrue(any("requires every Verification Gate item complete" in error for error in errors))
        self.assertTrue(any("requires a successful slice Proof receipt" in error for error in errors))

    def test_accepts_verified_status_with_complete_evidence(self) -> None:
        progress = "\n".join(
            (
                self.receipt(1),
                "- Proof receipt: slice — scope `Broad` — command `mix check` — exit `0`.",
            )
        )
        document = proof_scope_document(
            self.task(1, complete=True),
            progress=progress,
        ).replace("Not Started", "Verified", 1).replace(
            "- [ ] The example proof passes.",
            "- [x] The example proof passes.",
        )
        self.assertEqual([], self.errors(document))


if __name__ == "__main__":
    unittest.main()
