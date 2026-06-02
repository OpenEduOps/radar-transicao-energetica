from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.cache import AnalysisCacheError


class AppTest(unittest.TestCase):
    def test_run_analysis_reuses_core_flow_and_writes_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.json"

            result = run_analysis(cache_path=cache_path)

            cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))

        self.assertGreater(len(result.records), 0)
        self.assertIsNotNone(result.summary.renewable_share)
        self.assertEqual(result.cache_path, cache_path)
        self.assertIn("summary", cache_payload)

    def test_run_analysis_can_skip_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.json"

            result = run_analysis(cache_path=cache_path, write_cache=False)

        self.assertIsNone(result.cache_path)
        self.assertFalse(cache_path.exists())

    def test_run_analysis_reports_cache_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(AnalysisCacheError):
                run_analysis(cache_path=Path(tmpdir))


if __name__ == "__main__":
    unittest.main()
