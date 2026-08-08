#!/usr/bin/env python3
"""Regression tests for the cross-specification capability index."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


INDEX_PATH = Path(__file__).with_name("capability_index.py")
SPEC = importlib.util.spec_from_file_location("capability_index", INDEX_PATH)
assert SPEC is not None and SPEC.loader is not None
capability_index = importlib.util.module_from_spec(SPEC)
# Register before execution so the module's dataclasses can resolve their own
# module namespace during class creation.
sys.modules[SPEC.name] = capability_index
SPEC.loader.exec_module(capability_index)


SPEC_TEMPLATE = """\
# {slug}

## Active Slice

One slice.

## Cross-Specification Dependencies

Requires:

{requires}

Provides:

{provides}

## Tasks

{tasks}
"""

LEGACY_TEMPLATE = """\
# {slug}

## Active Slice

One slice.

## Tasks

{tasks}
"""


def requires_line(name: str, provider: str, provider_task: int, consumer_task: int) -> str:
    return (
        f"- `capability:{name}` — provider `specs/{provider}#Task {provider_task}` — "
        f"required before `Task {consumer_task}`."
    )


def provides_line(name: str, task: int) -> str:
    return f"- `capability:{name}` — ready after `Task {task}`."


def task_lines(*completion: bool) -> str:
    return "\n".join(
        f"- [{'x' if done else ' '}] Task {number} - Deliver outcome {number}."
        for number, done in enumerate(completion, start=1)
    )


class CapabilityIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "specs"
        self.root.mkdir()

    def write_spec(
        self,
        slug: str,
        *,
        requires: str = "- None.",
        provides: str = "- None.",
        tasks: str = task_lines(True),
    ) -> Path:
        directory = self.root / slug
        directory.mkdir()
        (directory / "tasks.md").write_text(
            SPEC_TEMPLATE.format(slug=slug, requires=requires, provides=provides, tasks=tasks),
            encoding="utf-8",
        )
        return directory

    def write_legacy_spec(self, slug: str, *, tasks: str = task_lines(True)) -> Path:
        directory = self.root / slug
        directory.mkdir()
        (directory / "tasks.md").write_text(
            LEGACY_TEMPLATE.format(slug=slug, tasks=tasks),
            encoding="utf-8",
        )
        return directory

    def index(self) -> tuple[dict[str, object], list[str]]:
        capabilities, problems = capability_index.build_index(
            capability_index.load_specs(self.root)
        )
        return {entry.name: entry for entry in capabilities}, problems

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INDEX_PATH), "--specs", str(self.root), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_resolves_provider_readiness_and_consumers(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 2), tasks=task_lines(True, True))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 2, 1),
            tasks=task_lines(False),
        )

        capabilities, problems = self.index()

        self.assertEqual([], problems)
        entry = capabilities["storage"]
        self.assertEqual("ready", entry.state)
        self.assertEqual("specs/05-provider#Task 2", entry.provider)
        self.assertEqual(
            ["specs/14-consumer#Task 1"],
            [requirement.consumer_reference for requirement in entry.consumers],
        )

    def test_provider_checkbox_drives_ready_versus_pending(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 2), tasks=task_lines(True, False))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 2, 1),
            tasks=task_lines(False),
        )

        capabilities, problems = self.index()

        self.assertEqual([], problems)
        self.assertEqual("pending", capabilities["storage"].state)

    def test_none_lists_declare_no_edges(self) -> None:
        self.write_spec("05-provider")

        specs = capability_index.load_specs(self.root)
        capabilities, problems = capability_index.build_index(specs)

        self.assertEqual([], problems)
        self.assertEqual([], capabilities)
        self.assertTrue(specs[0].adopted)
        self.assertEqual([], specs[0].requirements)
        self.assertEqual([], specs[0].provisions)

    def test_legacy_spec_without_capability_section_is_not_a_problem(self) -> None:
        self.write_legacy_spec("01-legacy")
        self.write_spec("05-provider", provides=provides_line("storage", 1))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 1, 1),
        )

        specs = capability_index.load_specs(self.root)
        _, problems = capability_index.build_index(specs)
        legacy = [spec for spec in specs if not spec.adopted]

        self.assertEqual([], problems)
        self.assertEqual(["specs/01-legacy"], [spec.reference for spec in legacy])
        self.assertEqual({"Task 1": True}, legacy[0].tasks)

        result = self.run_cli()
        self.assertEqual(0, result.returncode, result)
        self.assertIn("no capability section: specs/01-legacy", result.stdout)

    def test_required_capability_without_provider_is_missing(self) -> None:
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 2, 1),
        )

        capabilities, problems = self.index()

        self.assertEqual("missing", capabilities["storage"].state)
        self.assertIsNone(capabilities["storage"].provider)
        self.assertEqual(
            ["specs/14-consumer#Task 1: requires storage but no specification provides it"],
            problems,
        )
        self.assertEqual(1, self.run_cli().returncode)

    def test_two_providers_are_ambiguous(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 1))
        self.write_spec("06-provider", provides=provides_line("storage", 1))

        capabilities, problems = self.index()

        self.assertEqual("ambiguous", capabilities["storage"].state)
        self.assertIsNone(capabilities["storage"].provider)
        self.assertEqual(
            [
                "storage: provided by more than one specification: "
                "specs/05-provider#Task 1, specs/06-provider#Task 1"
            ],
            problems,
        )
        self.assertEqual(1, self.run_cli().returncode)

    def test_malformed_reference_is_reported_and_not_indexed(self) -> None:
        self.write_spec(
            "14-consumer",
            requires="- `capability:storage` — provider `specs/05-provider` — required before Task 1.",
            provides="- `capability:profile` ready after `Task 1`.",
        )

        capabilities, problems = self.index()

        self.assertEqual({}, capabilities)
        self.assertEqual(
            [
                "specs/14-consumer: malformed requires entry: - `capability:storage` — "
                "provider `specs/05-provider` — required before Task 1.",
                "specs/14-consumer: malformed provides entry: - `capability:profile` "
                "ready after `Task 1`.",
            ],
            problems,
        )
        self.assertEqual(1, self.run_cli().returncode)

    def test_stale_provider_reference_is_reported(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 2), tasks=task_lines(True, True))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 1, 1),
        )
        self.write_spec(
            "15-consumer",
            requires=requires_line("storage", "09-other", 2, 1),
        )
        self.write_spec("09-other", provides=provides_line("other", 1))

        _, problems = self.index()

        self.assertIn(
            "specs/14-consumer#Task 1: requires storage from specs/05-provider#Task 1 "
            "but it is ready after Task 2",
            problems,
        )
        self.assertIn(
            "specs/15-consumer#Task 1: requires storage from specs/09-other but "
            "specs/05-provider provides it",
            problems,
        )

    def test_provider_task_outside_the_task_plan_is_unresolved(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 9))

        capabilities, problems = self.index()

        self.assertEqual("unresolved", capabilities["storage"].state)
        self.assertEqual(
            ["specs/05-provider: provides storage from unknown Task 9"],
            problems,
        )

    def test_self_dependency_is_reported_without_an_edge(self) -> None:
        self.write_spec(
            "05-provider",
            requires=requires_line("storage", "05-provider", 1, 2),
            provides=provides_line("storage", 1),
            tasks=task_lines(True, False),
        )

        _, problems = self.index()

        self.assertEqual(
            ["specs/05-provider#Task 2: requires storage from itself"],
            problems,
        )

    def test_cycle_between_two_specifications_is_reported(self) -> None:
        self.write_spec(
            "05-alpha",
            requires=requires_line("beta", "06-beta", 1, 1),
            provides=provides_line("alpha", 1),
        )
        self.write_spec(
            "06-beta",
            requires=requires_line("alpha", "05-alpha", 1, 1),
            provides=provides_line("beta", 1),
        )

        _, problems = self.index()

        cycles = [problem for problem in problems if problem.startswith("capability cycle: ")]
        self.assertEqual(1, len(cycles), problems)
        self.assertIn("specs/05-alpha#Task 1", cycles[0])
        self.assertIn("specs/06-beta#Task 1", cycles[0])

        result = self.run_cli()
        self.assertEqual(1, result.returncode, result)
        self.assertIn("capability cycle: ", result.stderr)

    def test_acyclic_diamond_is_not_reported_as_a_cycle(self) -> None:
        self.write_spec("05-root", provides=provides_line("root", 1))
        self.write_spec(
            "06-left",
            requires=requires_line("root", "05-root", 1, 1),
            provides=provides_line("left", 1),
        )
        self.write_spec(
            "07-right",
            requires=requires_line("root", "05-root", 1, 1),
            provides=provides_line("right", 1),
        )
        self.write_spec(
            "08-join",
            requires="\n".join(
                (
                    requires_line("left", "06-left", 1, 1),
                    requires_line("right", "07-right", 1, 1),
                )
            ),
        )

        _, problems = self.index()

        self.assertEqual([], problems)
        self.assertEqual(0, self.run_cli().returncode)

    def test_capability_lookup_prints_provider_state_and_consumers(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 2), tasks=task_lines(True, True))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 2, 1),
        )

        result = self.run_cli("--capability", "storage")

        self.assertEqual(0, result.returncode, result)
        self.assertEqual(
            "capability  storage\n"
            "provider    specs/05-provider#Task 2\n"
            "state       ready\n"
            "consumers   specs/14-consumer#Task 1\n",
            result.stdout,
        )

    def test_capability_lookup_accepts_the_prefixed_name(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 1))

        result = self.run_cli("--capability", "capability:storage")

        self.assertEqual(0, result.returncode, result)
        self.assertIn("state       ready", result.stdout)
        self.assertIn("consumers   none", result.stdout)

    def test_unknown_capability_exits_nonzero(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 1))

        result = self.run_cli("--capability", "absent")

        self.assertEqual(2, result.returncode, result)
        self.assertEqual("", result.stdout)
        self.assertIn("unknown capability: absent", result.stderr)

    def test_capability_lookup_reports_only_its_own_problems(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 1))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 1, 1),
        )
        self.write_spec(
            "15-consumer",
            requires=requires_line("absent-elsewhere", "99-nowhere", 1, 1),
        )

        healthy = self.run_cli("--capability", "storage")
        broken = self.run_cli("--capability", "absent-elsewhere")

        self.assertEqual(0, healthy.returncode, healthy)
        self.assertIn("unrelated graph problems", healthy.stderr)
        self.assertEqual(1, broken.returncode, broken)
        self.assertIn("no specification provides it", broken.stderr)

    def test_missing_specs_directory_is_a_usage_error(self) -> None:
        result = subprocess.run(
            [sys.executable, str(INDEX_PATH), "--specs", str(self.root / "absent")],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(2, result.returncode, result)
        self.assertIn("is not a directory", result.stderr)

    def test_listing_is_one_line_per_capability_with_a_summary(self) -> None:
        self.write_spec("05-provider", provides=provides_line("storage", 2), tasks=task_lines(True, True))
        self.write_spec(
            "14-consumer",
            requires=requires_line("storage", "05-provider", 2, 1),
            provides=provides_line("profile", 1),
            tasks=task_lines(False),
        )

        result = self.run_cli()

        self.assertEqual(0, result.returncode, result)
        self.assertEqual(
            "ready      storage  provider=specs/05-provider#Task 2  "
            "consumers=specs/14-consumer#Task 1\n"
            "pending    profile  provider=specs/14-consumer#Task 1  consumers=none\n"
            "2 capabilities: 1 ready, 1 pending\n",
            "".join(sorted(result.stdout.splitlines(keepends=True), reverse=True)),
        )

    def test_directories_without_tasks_md_are_skipped(self) -> None:
        (self.root / "99-empty").mkdir()
        self.write_spec("05-provider", provides=provides_line("storage", 1))

        specs = capability_index.load_specs(self.root)

        self.assertEqual(["specs/05-provider"], [spec.reference for spec in specs])


if __name__ == "__main__":
    unittest.main()
