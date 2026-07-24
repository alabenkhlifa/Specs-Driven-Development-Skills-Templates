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


if __name__ == "__main__":
    unittest.main()
