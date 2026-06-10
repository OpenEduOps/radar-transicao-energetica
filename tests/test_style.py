from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_style import check_text_style  # noqa: E402


class StyleValidationTest(unittest.TestCase):
    def test_check_text_style_accepts_clean_text_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "README.md"
            path.write_text("# Titulo\n\nTexto limpo.\n", encoding="utf-8")

            issues = check_text_style(root, [path])

        self.assertEqual(issues, [])

    def test_check_text_style_reports_trailing_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "README.md"
            path.write_text("# Titulo \n", encoding="utf-8")

            issues = check_text_style(root, [path])

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 1)

    def test_check_text_style_reports_missing_final_newline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "README.md"
            path.write_text("# Titulo", encoding="utf-8")

            issues = check_text_style(root, [path])

        self.assertEqual(len(issues), 1)
        self.assertIn("newline", issues[0].message)


if __name__ == "__main__":
    unittest.main()
