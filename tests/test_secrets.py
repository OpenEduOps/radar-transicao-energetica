from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_secrets import scan_for_secrets  # noqa: E402


SAMPLE_GITHUB_TOKEN = "ghp_" + "1234567890abcdefghijklmnopqrstuvwx"


class SecretsValidationTest(unittest.TestCase):
    def test_scan_for_secrets_reports_high_confidence_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text(
                f"token = {SAMPLE_GITHUB_TOKEN}\n",
                encoding="utf-8",
            )

            findings = scan_for_secrets(root)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].pattern_name, "github-token")
        self.assertEqual(findings[0].line_number, 1)

    def test_scan_for_secrets_ignores_binary_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "sample.bin").write_bytes(b"\0" + SAMPLE_GITHUB_TOKEN.encode("utf-8"))

            findings = scan_for_secrets(root)

        self.assertEqual(findings, [])

    def test_scan_for_secrets_ignores_generated_artifact_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dist = root / "dist"
            dist.mkdir()
            (dist / "artifact.txt").write_text(
                f"token = {SAMPLE_GITHUB_TOKEN}\n",
                encoding="utf-8",
            )

            findings = scan_for_secrets(root)

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
