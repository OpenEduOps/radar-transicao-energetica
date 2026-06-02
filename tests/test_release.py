from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.release import (  # noqa: E402
    ReleaseRequirement,
    evaluate_public_release_readiness,
    format_release_decision,
)
from scripts import build_exe  # noqa: E402


class ReleaseTest(unittest.TestCase):
    def test_current_release_gate_blocks_public_exe_release(self) -> None:
        decision = evaluate_public_release_readiness()

        self.assertEqual(decision.stage, "local-experimental")
        self.assertFalse(decision.can_publish)
        self.assertIn("ui-stable", {item.key for item in decision.missing_requirements})
        self.assertIn("formal-smoke-test", {item.key for item in decision.missing_requirements})
        self.assertIn("checksum", {item.key for item in decision.missing_requirements})
        self.assertIn("ci-artifact-build", {item.key for item in decision.missing_requirements})

    def test_public_release_is_allowed_only_when_all_requirements_are_satisfied(self) -> None:
        requirements = (
            ReleaseRequirement("ui-stable", "UI validada", True),
            ReleaseRequirement("formal-smoke-test", "Smoke test", True),
            ReleaseRequirement("checksum", "Checksum", True),
            ReleaseRequirement("ci-artifact-build", "Build CI", True),
            ReleaseRequirement("release-workflow", "Workflow", True),
        )

        decision = evaluate_public_release_readiness(requirements)

        self.assertTrue(decision.can_publish)
        self.assertEqual(decision.missing_requirements, ())

    def test_release_decision_format_lists_missing_requirements(self) -> None:
        decision = evaluate_public_release_readiness()

        message = format_release_decision(decision)

        self.assertIn("Estagio do executavel: local-experimental", message)
        self.assertIn("Release publica bloqueada.", message)
        self.assertIn("ui-stable", message)

    def test_build_script_public_release_flag_fails_before_pyinstaller(self) -> None:
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            exit_code = build_exe.main(["--public-release"])

        self.assertEqual(exit_code, 2)
        self.assertIn("Release publica bloqueada.", stderr.getvalue())

    def test_build_script_release_status_does_not_require_pyinstaller(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = build_exe.main(["--release-status"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Estagio do executavel: local-experimental", stdout.getvalue())
        self.assertIn("Release publica bloqueada.", stdout.getvalue())

    def test_build_script_command_keeps_local_experimental_exe_name(self) -> None:
        command = build_exe.build_pyinstaller_command()

        self.assertIn("--onefile", command)
        self.assertIn("--console", command)
        self.assertIn("radar-transicao-energetica", command)


if __name__ == "__main__":
    unittest.main()
