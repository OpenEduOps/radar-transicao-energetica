from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_docs import _find_broken_local_links, _validate_test_plan  # noqa: E402


class DocsValidationTest(unittest.TestCase):
    def test_find_broken_local_links_accepts_existing_markdown_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (root / "README.md").write_text(
                "[Arquitetura](docs/arquitetura.md)\n",
                encoding="utf-8",
            )
            (docs_dir / "arquitetura.md").write_text("# Arquitetura\n", encoding="utf-8")

            errors = _find_broken_local_links(root)

        self.assertEqual(errors, [])

    def test_find_broken_local_links_reports_missing_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("[Ausente](docs/ausente.md)\n", encoding="utf-8")

            errors = _find_broken_local_links(root)

        self.assertEqual(len(errors), 1)
        self.assertIn("link local quebrado", errors[0])

    def test_validate_test_plan_requires_core_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_plan = Path(tmpdir) / "testes.md"
            test_plan.write_text("# Plano de Testes\n", encoding="utf-8")

            errors = _validate_test_plan(test_plan)

        self.assertGreaterEqual(len(errors), 1)
        self.assertIn("## Guardrails", errors[0])


if __name__ == "__main__":
    unittest.main()
