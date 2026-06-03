from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.cache import (
    AnalysisCacheError,
    read_latest_analysis_cache,
    read_latest_generation_records,
)
from radar_transicao_energetica.data import GenerationRecord


class AppTest(unittest.TestCase):
    def test_run_analysis_reuses_core_flow_and_writes_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.sqlite"

            result = run_analysis(cache_path=cache_path)

            cache_payload = read_latest_analysis_cache(cache_path)
            cached_records = read_latest_generation_records(cache_path)

        self.assertGreater(len(result.records), 0)
        self.assertIsNotNone(result.summary.renewable_share)
        self.assertEqual(result.cache_path, cache_path)
        self.assertEqual(result.data_source.kind, "exemplo")
        self.assertIn("summary", cache_payload)
        self.assertEqual(cache_payload["data_source"]["kind"], "exemplo")
        self.assertEqual(cache_payload["cache_path"], str(cache_path))
        self.assertEqual(len(cached_records), len(result.records))
        self.assertEqual(cached_records[0].source, "eolica")

    def test_run_analysis_can_skip_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.sqlite"

            result = run_analysis(cache_path=cache_path, write_cache=False)

        self.assertIsNone(result.cache_path)
        self.assertFalse(cache_path.exists())

    def test_run_analysis_reports_cache_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(AnalysisCacheError):
                run_analysis(cache_path=Path(tmpdir))

    def test_run_analysis_can_use_ons_loader(self) -> None:
        def fake_ons_loader(year: int, month: int) -> list[GenerationRecord]:
            self.assertEqual((year, month), (2026, 1))
            return [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 75.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 25.0),
            ]

        result = run_analysis(
            source="ons",
            ons_year=2026,
            ons_month=1,
            write_cache=False,
            ons_loader=fake_ons_loader,
        )

        self.assertEqual(result.summary.renewable_share, 0.75)
        self.assertEqual(result.data_source.kind, "ons")
        self.assertEqual(result.data_source.period, "2026-01")
        self.assertIn("GERACAO_USINA-2_2026_01.csv", result.data_source.resource_url or "")

    def test_run_analysis_reuses_cached_ons_records_by_period(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.sqlite"
            run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 75.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 25.0),
                ],
            )

            def failing_loader(_year: int, _month: int) -> list[GenerationRecord]:
                raise AssertionError("ONS loader should not be called on cache hit")

            result = run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=failing_loader,
            )

        self.assertTrue(result.cache_hit)
        self.assertEqual(result.cache_path, cache_path)
        self.assertEqual(result.summary.renewable_share, 0.75)

    def test_run_analysis_can_bypass_cached_ons_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.sqlite"
            run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 75.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 25.0),
                ],
            )

            result = run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                prefer_cache=False,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
                ],
            )

        self.assertFalse(result.cache_hit)
        self.assertEqual(result.summary.renewable_share, 0.5)

    def test_run_analysis_requires_ons_period(self) -> None:
        with self.assertRaisesRegex(ValueError, "--ons-periodo"):
            run_analysis(source="ons")


if __name__ == "__main__":
    unittest.main()
