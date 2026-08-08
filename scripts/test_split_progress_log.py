#!/usr/bin/env python3
"""Regression tests for the progress-log split tool."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


TOOL_PATH = Path(__file__).with_name("split_progress_log.py")
SPEC = importlib.util.spec_from_file_location("split_progress_log", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
split_progress_log = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(split_progress_log)


POINTER = "See [progress.md](progress.md)."

ENTRY_NEW = """\
### 2026-08-04 - Branch work

- Completed: Delivered the branch outcome.
- Proof receipt: `Task 3` — scope `Focused` — command `mix test test/new_test.exs` — exit `0`.
"""

ENTRY_MIDDLE = """\
### 2026-08-02 - Second checkpoint

- Completed: Delivered the second outcome.
- Failed checks: None.

  Indented continuation with  double  spacing preserved.
"""

ENTRY_OLD = """\
### 2026-08-01 - First checkpoint

- Completed: Delivered the first outcome.
- Spec updates: None.
"""


def tasks_document(progress_body: str, *, title: str = "# Example Tasks") -> str:
    return f"""\
{title}

## Status

In Progress

## Tasks

- [x] Task 1 — Deliver one outcome.

## Progress Log

{progress_body}"""


class SplitProgressLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.spec = self.root / "specs" / "01-example"
        self.spec.mkdir(parents=True)
        self.tasks = self.spec / "tasks.md"
        self.progress = self.spec / "progress.md"

    def write_tasks(self, progress_body: str, *, title: str = "# Example Tasks") -> None:
        self.tasks.write_text(tasks_document(progress_body, title=title), encoding="utf-8")

    def split(self, *, check: bool = False) -> tuple[int, list[str]]:
        return split_progress_log.run([self.spec], check=check)

    def test_converts_legacy_inline_log(self) -> None:
        self.write_tasks(f"{ENTRY_NEW}\n{ENTRY_OLD}")
        changed, _ = self.split()
        self.assertEqual(2, changed)

        tasks_text = self.tasks.read_text(encoding="utf-8")
        self.assertTrue(tasks_text.endswith(f"## Progress Log\n\n{POINTER}\n"))
        self.assertNotIn("### ", tasks_text)
        self.assertEqual(
            f"# Example Progress Log\n\n{ENTRY_NEW}\n{ENTRY_OLD}",
            self.progress.read_text(encoding="utf-8"),
        )

    def test_preserves_entry_bytes_and_order(self) -> None:
        self.write_tasks(f"{ENTRY_NEW}\n{ENTRY_MIDDLE}\n{ENTRY_OLD}")
        original = self.tasks.read_text(encoding="utf-8")
        self.split()

        stored = self.progress.read_text(encoding="utf-8")
        for entry in (ENTRY_NEW, ENTRY_MIDDLE, ENTRY_OLD):
            self.assertIn(entry.rstrip("\n"), stored)
        headings = [line for line in stored.splitlines() if line.startswith("### ")]
        self.assertEqual(
            [
                entry.splitlines()[0]
                for entry in (ENTRY_NEW, ENTRY_MIDDLE, ENTRY_OLD)
            ],
            headings,
        )

        # No progress-log byte is lost: the log body moves under a new H1 and
        # the task plan keeps only the pointer line.
        moved = original.split("## Progress Log\n\n", 1)[1]
        self.assertEqual(f"# Example Progress Log\n\n{moved}", stored)

    def test_derives_title_from_the_task_plan_heading(self) -> None:
        self.write_tasks(ENTRY_OLD, title="# Repository Execution Profile Tasks")
        self.split()
        self.assertTrue(
            self.progress.read_text(encoding="utf-8").startswith(
                "# Repository Execution Profile Progress Log\n\n"
            )
        )

    def test_is_idempotent(self) -> None:
        self.write_tasks(f"{ENTRY_NEW}\n{ENTRY_OLD}")
        self.split()
        tasks_text = self.tasks.read_text(encoding="utf-8")
        progress_text = self.progress.read_text(encoding="utf-8")

        changed, reports = self.split()
        self.assertEqual(0, changed)
        self.assertEqual([], reports)
        self.assertEqual(tasks_text, self.tasks.read_text(encoding="utf-8"))
        self.assertEqual(progress_text, self.progress.read_text(encoding="utf-8"))

    def test_leaves_a_specification_without_a_progress_log_alone(self) -> None:
        self.tasks.write_text(
            "# Example Tasks\n\n## Tasks\n\n- [ ] Task 1 — Deliver one outcome.\n",
            encoding="utf-8",
        )
        original = self.tasks.read_text(encoding="utf-8")
        changed, _ = self.split()
        self.assertEqual(0, changed)
        self.assertFalse(self.progress.exists())
        self.assertEqual(original, self.tasks.read_text(encoding="utf-8"))

    def test_does_not_create_an_empty_progress_file(self) -> None:
        self.write_tasks(f"{POINTER}\n")
        changed, _ = self.split()
        self.assertEqual(0, changed)
        self.assertFalse(self.progress.exists())

    def test_merges_rebased_entries_without_duplicating_stored_entries(self) -> None:
        # The branch carries the full legacy log plus one newer entry, while
        # progress.md already stores the entries taken from the default branch.
        self.progress.write_text(
            f"# Example Progress Log\n\n{ENTRY_MIDDLE}\n{ENTRY_OLD}",
            encoding="utf-8",
        )
        self.write_tasks(f"{ENTRY_NEW}\n{ENTRY_MIDDLE}\n{ENTRY_OLD}")

        changed, _ = self.split()
        self.assertEqual(2, changed)

        stored = self.progress.read_text(encoding="utf-8")
        self.assertEqual(
            f"# Example Progress Log\n\n{ENTRY_NEW}\n{ENTRY_MIDDLE}\n{ENTRY_OLD}",
            stored,
        )
        headings = [line for line in stored.splitlines() if line.startswith("### ")]
        self.assertEqual(len(headings), len(set(headings)))

    def test_merge_keeps_entries_that_only_exist_in_the_stored_log(self) -> None:
        self.progress.write_text(
            f"# Example Progress Log\n\n{ENTRY_MIDDLE}\n{ENTRY_OLD}",
            encoding="utf-8",
        )
        self.write_tasks(f"{ENTRY_NEW}\n{ENTRY_OLD}")

        self.split()
        self.assertEqual(
            f"# Example Progress Log\n\n{ENTRY_NEW}\n{ENTRY_MIDDLE}\n{ENTRY_OLD}",
            self.progress.read_text(encoding="utf-8"),
        )

    def test_merge_keeps_the_stored_text_of_a_shared_entry(self) -> None:
        stored_entry = ENTRY_OLD.replace("Delivered", "Recorded")
        self.progress.write_text(
            f"# Example Progress Log\n\n{stored_entry}", encoding="utf-8"
        )
        self.write_tasks(ENTRY_OLD)

        self.split()
        self.assertEqual(
            f"# Example Progress Log\n\n{stored_entry}",
            self.progress.read_text(encoding="utf-8"),
        )

    def test_merge_appends_pointer_shaped_inline_entries(self) -> None:
        self.progress.write_text(
            f"# Example Progress Log\n\n{ENTRY_OLD}", encoding="utf-8"
        )
        self.write_tasks(f"{POINTER}\n\n{ENTRY_NEW}")

        self.split()
        self.assertEqual(
            f"# Example Progress Log\n\n{ENTRY_NEW}\n{ENTRY_OLD}",
            self.progress.read_text(encoding="utf-8"),
        )
        self.assertTrue(
            self.tasks.read_text(encoding="utf-8").endswith(
                f"## Progress Log\n\n{POINTER}\n"
            )
        )

    def test_preserves_sections_after_the_progress_log(self) -> None:
        self.tasks.write_text(
            "# Example Tasks\n\n## Tasks\n\n- [ ] Task 1 — Deliver.\n\n"
            f"## Progress Log\n\n{ENTRY_OLD}\n"
            "## Appendix\n\n- Trailing section.\n",
            encoding="utf-8",
        )
        self.split()
        self.assertEqual(
            "# Example Tasks\n\n## Tasks\n\n- [ ] Task 1 — Deliver.\n\n"
            f"## Progress Log\n\n{POINTER}\n\n"
            "## Appendix\n\n- Trailing section.\n",
            self.tasks.read_text(encoding="utf-8"),
        )

    def test_check_mode_reports_without_writing_and_exits_nonzero(self) -> None:
        self.write_tasks(f"{ENTRY_NEW}\n{ENTRY_OLD}")
        original = self.tasks.read_text(encoding="utf-8")

        changed, reports = self.split(check=True)
        self.assertEqual(2, changed)
        self.assertTrue(any("would create" in report for report in reports))
        self.assertTrue(any("would update" in report for report in reports))
        self.assertEqual(original, self.tasks.read_text(encoding="utf-8"))
        self.assertFalse(self.progress.exists())

        self.assertEqual(1, self.main(["--check"]))

        self.split()
        self.assertEqual(0, self.main(["--check"]))

    def main(self, extra: list[str]) -> int:
        argv = ["split_progress_log.py", str(self.spec), *extra]
        original_argv = split_progress_log.sys.argv
        split_progress_log.sys.argv = argv
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                return split_progress_log.main()
        finally:
            split_progress_log.sys.argv = original_argv

    def test_stops_on_unrecognized_progress_log_content(self) -> None:
        self.write_tasks(f"- Implementation has not started.\n\n{ENTRY_OLD}")
        with self.assertRaises(split_progress_log.SplitError) as raised:
            self.split()
        self.assertIn("unrecognized", str(raised.exception))
        self.assertFalse(self.progress.exists())
        self.assertEqual(2, self.main([]))

    def test_stops_on_duplicate_entry_headings(self) -> None:
        self.write_tasks(f"{ENTRY_OLD}\n{ENTRY_OLD}")
        with self.assertRaises(split_progress_log.SplitError) as raised:
            self.split()
        self.assertIn("duplicate entry heading", str(raised.exception))

    def test_stops_on_a_stored_log_without_an_h1(self) -> None:
        self.progress.write_text(f"{ENTRY_OLD}", encoding="utf-8")
        self.write_tasks(ENTRY_NEW)
        with self.assertRaises(split_progress_log.SplitError) as raised:
            self.split()
        self.assertIn("first line must be an H1 title", str(raised.exception))

    def test_processes_every_specification_under_a_root(self) -> None:
        second = self.root / "specs" / "02-example"
        second.mkdir()
        (second / "tasks.md").write_text(
            tasks_document(ENTRY_OLD, title="# Second Tasks"), encoding="utf-8"
        )
        self.write_tasks(ENTRY_NEW)

        changed, _ = split_progress_log.run([self.root / "specs"], check=False)
        self.assertEqual(4, changed)
        self.assertTrue((second / "progress.md").is_file())
        self.assertTrue(self.progress.is_file())


class MergeEntryTests(unittest.TestCase):
    def entries(self, *headings: str) -> list[object]:
        return [
            split_progress_log.Entry(f"### {heading}\n\n- Completed: {heading}.\n")
            for heading in headings
        ]

    def headings(self, entries: list[object]) -> list[str]:
        return [entry.heading for entry in entries]

    def test_new_entries_land_above_the_newest_shared_entry(self) -> None:
        merged = split_progress_log.merge_entries(
            self.entries("C", "B", "A"),
            self.entries("E", "D", "C", "B", "A"),
        )
        self.assertEqual(
            ["### E", "### D", "### C", "### B", "### A"], self.headings(merged)
        )

    def test_interleaved_new_entries_keep_both_orders(self) -> None:
        merged = split_progress_log.merge_entries(
            self.entries("C", "A"),
            self.entries("D", "C", "B", "A"),
        )
        self.assertEqual(
            ["### D", "### C", "### B", "### A"], self.headings(merged)
        )

    def test_disjoint_logs_concatenate_deterministically(self) -> None:
        merged = split_progress_log.merge_entries(
            self.entries("B", "A"),
            self.entries("D", "C"),
        )
        self.assertEqual(
            ["### D", "### C", "### B", "### A"], self.headings(merged)
        )

    def test_repeated_merges_are_stable(self) -> None:
        stored = self.entries("C", "B", "A")
        incoming = self.entries("E", "D", "C", "B", "A")
        once = split_progress_log.merge_entries(stored, incoming)
        twice = split_progress_log.merge_entries(once, incoming)
        self.assertEqual(self.headings(once), self.headings(twice))


if __name__ == "__main__":
    unittest.main()
