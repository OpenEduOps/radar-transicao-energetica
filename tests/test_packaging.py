from __future__ import annotations

import sys
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class PackagingTest(unittest.TestCase):
    def test_pyproject_exposes_desktop_entry_point(self) -> None:
        pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        scripts = pyproject["project"]["scripts"]

        self.assertEqual(
            scripts["radar-transicao-energetica-ui"],
            "radar_transicao_energetica.desktop:main",
        )

    def test_ci_does_not_build_or_upload_exe_artifacts_yet(self) -> None:
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8").lower()

        self.assertNotIn("scripts/build_exe.py", workflow)
        self.assertNotIn("actions/upload-artifact", workflow)
        self.assertNotIn("checksum", workflow)

    def test_gitignore_keeps_local_exe_artifacts_out_of_git(self) -> None:
        ignored_patterns = set(Path(".gitignore").read_text(encoding="utf-8").splitlines())

        self.assertIn("build/", ignored_patterns)
        self.assertIn("dist/", ignored_patterns)
        self.assertIn("*.spec", ignored_patterns)


if __name__ == "__main__":
    unittest.main()
