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


if __name__ == "__main__":
    unittest.main()
