#!/usr/bin/env python3
"""Tests for the focused and slice proof command runner."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("run_proof.py")


class RunProofTests(unittest.TestCase):
    def run_proof(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def make_executable(self, directory: Path, body: str, name: str = "fixture-command") -> Path:
        executable = directory / name
        executable.write_text(
            "#!/usr/bin/env python3\n" + textwrap.dedent(body),
            encoding="utf-8",
        )
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        return executable

    def assert_rejected(self, *command: str) -> None:
        result = self.run_proof("task", "--task", "35", "--", *command)
        self.assertEqual(2, result.returncode, result)
        self.assertIn("task proof rejects", result.stderr)
        self.assertNotIn("Proof receipt", result.stdout)

    def test_task_scope_allows_focused_mix_test_paths_and_selectors(self) -> None:
        allowed_commands = (
            ("mix", "test", "test/example_test.exs"),
            ("mix", "test", "test/example_test.exs:42"),
            ("mix", "test", "--only", "integration"),
            ("mix", "test", "--only=integration"),
            ("mix", "test", "--failed"),
            ("mix", "test", "--stale"),
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            self.make_executable(temporary_path, "raise SystemExit(0)\n", name="mix")
            environment_path = f"PATH={temporary_directory}{os.pathsep}{os.environ.get('PATH', '')}"
            for command in allowed_commands:
                with self.subTest(command=command):
                    result = self.run_proof(
                        "task",
                        "--task",
                        "35",
                        "--",
                        environment_path,
                        *command,
                    )
                    self.assertEqual(0, result.returncode, result)
                    self.assertIn("scope `Focused`", result.stdout)

    def test_task_scope_rejects_unscoped_mix_test(self) -> None:
        self.assert_rejected("mix", "test")
        self.assert_rejected("/usr/local/bin/mix", "test")
        self.assert_rejected("mix", "test", "--warnings-as-errors")
        self.assert_rejected("mix", "test", "--seed", "0")
        self.assert_rejected("mix", "test", "--only")

    def test_task_scope_rejects_broad_mix_gates(self) -> None:
        for mix_task in ("check", "credo", "dialyzer", "deps.audit", "sobelow"):
            with self.subTest(mix_task=mix_task):
                self.assert_rejected("mix", mix_task)

    def test_task_scope_rejects_shell_env_and_mix_do_wrappers(self) -> None:
        for command in (
            ("/bin/sh", "-c", "mix test"),
            ("bash", "-c", "mix check"),
            ("zsh", "-c", "mix dialyzer"),
            ("fish", "-c", "mix deps.audit"),
            ("env", "MIX_ENV=prod", "mix", "release"),
            ("mix", "do", "test", ",", "dialyzer"),
        ):
            with self.subTest(command=command):
                self.assert_rejected(*command)

    def test_task_scope_rejects_package_installation_commands(self) -> None:
        for command in (
            ("npm", "ci"),
            ("npm", "install"),
            ("pnpm", "install"),
            ("pnpm", "ci"),
            ("yarn", "install"),
            ("npm", "--prefix", "assets", "ci"),
        ):
            with self.subTest(command=command):
                self.assert_rejected(*command)

    def test_task_scope_rejects_unscoped_e2e_and_allows_selector_arguments(self) -> None:
        self.assert_rejected("npm", "--prefix", "assets", "run", "test:e2e")
        self.assert_rejected("pnpm", "run", "test:e2e", "--")
        for operational_arguments in (
            ("--project", "chromium"),
            ("--headed",),
            ("--workers", "1"),
            ("--reporter=list",),
            ("--grep",),
            ("--grep", "--headed"),
            ("--grep=",),
        ):
            with self.subTest(operational_arguments=operational_arguments):
                self.assert_rejected(
                    "npm",
                    "--prefix",
                    "assets",
                    "run",
                    "test:e2e",
                    "--",
                    *operational_arguments,
                )

        with tempfile.TemporaryDirectory() as temporary_directory:
            self.make_executable(Path(temporary_directory), "raise SystemExit(0)\n", name="npm")
            environment_path = f"PATH={temporary_directory}{os.pathsep}{os.environ.get('PATH', '')}"
            focused_selectors = (
                ("--grep", "@task-35"),
                ("--grep=@task-35",),
                ("--last-failed",),
                ("test/e2e/task_35.spec.ts",),
            )
            for selectors in focused_selectors:
                with self.subTest(selectors=selectors):
                    result = self.run_proof(
                        "task",
                        "--task",
                        "35",
                        "--",
                        environment_path,
                        "npm",
                        "--prefix",
                        "assets",
                        "run",
                        "test:e2e",
                        "--",
                        *selectors,
                    )
                    self.assertEqual(0, result.returncode, result)
                    self.assertIn("scope `Focused`", result.stdout)

    def test_task_scope_rejects_production_asset_and_release_gates(self) -> None:
        self.assert_rejected("MIX_ENV=prod", "mix", "assets.deploy")
        self.assert_rejected("MIX_ENV=prod", "mix", "release")

        inherited_environment = os.environ.copy()
        inherited_environment["MIX_ENV"] = "prod"
        result = self.run_proof(
            "task",
            "--task",
            "35",
            "--",
            "mix",
            "release",
            environment=inherited_environment,
        )
        self.assertEqual(2, result.returncode, result)
        self.assertIn("task proof rejects", result.stderr)

    def test_environment_assignments_are_passed_without_a_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_executable(
                Path(temporary_directory),
                """
                import os
                import sys
                print(os.environ["PROOF_VALUE"])
                print(sys.argv[1])
                """,
            )
            result = self.run_proof(
                "task",
                "--task",
                "7",
                "--",
                "PROOF_VALUE=kept verbatim",
                str(executable),
                "$(printf not-a-shell)",
            )

        self.assertEqual(0, result.returncode, result)
        lines = result.stdout.splitlines()
        self.assertEqual("kept verbatim", lines[0])
        self.assertEqual("$(printf not-a-shell)", lines[1])
        self.assertEqual(
            "- Proof receipt: `Task 7` — scope `Focused` — "
            f"command `'PROOF_VALUE=kept verbatim' {executable} '$(printf not-a-shell)'` — exit `0`.",
            lines[2],
        )

    def test_success_prints_exact_task_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_executable(Path(temporary_directory), "raise SystemExit(0)\n")
            result = self.run_proof("task", "--task", "35", "--", str(executable), "proof arg")

        self.assertEqual(0, result.returncode, result)
        self.assertEqual(
            "- Proof receipt: `Task 35` — scope `Focused` — "
            f"command `{executable} 'proof arg'` — exit `0`.\n",
            result.stdout,
        )
        self.assertEqual("", result.stderr)

    def test_explicit_broad_task_scope_permits_full_gate_and_marks_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            self.make_executable(Path(temporary_directory), "raise SystemExit(0)\n", name="mix")
            environment_path = f"PATH={temporary_directory}{os.pathsep}{os.environ.get('PATH', '')}"
            result = self.run_proof(
                "task",
                "--task",
                "35",
                "--broad",
                "--",
                environment_path,
                "mix",
                "test",
            )

        self.assertEqual(0, result.returncode, result)
        self.assertEqual(
            "- Proof receipt: `Task 35` — scope `Broad` — "
            f"command `'{environment_path}' mix test` — exit `0`.\n",
            result.stdout,
        )

    def test_slice_scope_permits_broad_commands_and_prints_exact_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            self.make_executable(Path(temporary_directory), "raise SystemExit(0)\n", name="mix")
            environment_path = f"PATH={temporary_directory}{os.pathsep}{os.environ.get('PATH', '')}"
            result = self.run_proof("slice", "--", environment_path, "mix", "test")

        self.assertEqual(0, result.returncode, result)
        self.assertEqual(
            "- Proof receipt: slice — scope `Broad` — "
            f"command `'{environment_path}' mix test` — exit `0`.\n",
            result.stdout,
        )

    def test_failure_preserves_exit_status_and_prints_no_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_executable(
                Path(temporary_directory),
                """
                import sys
                print("fixture failed")
                raise SystemExit(23)
                """,
            )
            result = self.run_proof("task", "--task", "9", "--", str(executable))

        self.assertEqual(23, result.returncode, result)
        self.assertEqual("fixture failed\n", result.stdout)
        self.assertNotIn("Proof receipt", result.stdout)

    def test_missing_executable_returns_127_without_receipt(self) -> None:
        result = self.run_proof("slice", "--", "definitely-not-a-proof-command")
        self.assertEqual(127, result.returncode, result)
        self.assertIn("proof command not found", result.stderr)
        self.assertNotIn("Proof receipt", result.stdout)

    def test_missing_command_and_invalid_task_number_are_usage_errors(self) -> None:
        missing = self.run_proof("task", "--task", "3", "--", "ONLY_ENV=value")
        invalid = self.run_proof("task", "--task", "0", "--", "true")
        self.assertEqual(2, missing.returncode, missing)
        self.assertEqual(2, invalid.returncode, invalid)
        self.assertNotIn("Proof receipt", missing.stdout)
        self.assertNotIn("Proof receipt", invalid.stdout)


if __name__ == "__main__":
    unittest.main()
