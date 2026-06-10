from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.cache import (
    AnalysisCacheError,
    read_latest_analysis_cache,
    read_latest_generation_records,
)
from radar_transicao_energetica.data import GenerationRecord
from radar_transicao_energetica.weather import WeatherDataError, WeatherRecord


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

    def test_run_analysis_revalidates_expired_ons_cache(self) -> None:
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
            expired_at = datetime.now(timezone.utc) - timedelta(days=3)
            with closing(sqlite3.connect(str(cache_path))) as connection:
                connection.execute(
                    "UPDATE analyses SET created_at = ?",
                    (expired_at.isoformat(timespec="seconds"),),
                )
                connection.commit()

            result = run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_cache_max_age_days=1,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 40.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 60.0),
                ],
            )

        self.assertFalse(result.cache_hit)
        self.assertEqual(result.summary.renewable_share, 0.4)

    def test_run_analysis_persists_weather_when_ons_records_are_reused_from_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.sqlite"
            run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 80.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 20.0),
                ],
            )

            result = run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=lambda _year, _month: [],
                include_weather=True,
                weather_loader=lambda **_kwargs: [
                    WeatherRecord(datetime(2026, 1, 1, 0), 22.0, 8.0, 0.0, 40.0),
                ],
            )
            cache_payload = read_latest_analysis_cache(cache_path)

        self.assertTrue(result.cache_hit)
        self.assertEqual(cache_payload["cache_hit"], True)
        self.assertEqual(cache_payload["weather"]["summary"]["record_count"], 1)
        self.assertEqual(cache_payload["summary"]["renewable_share"], 0.8)

    def test_run_analysis_requires_ons_period(self) -> None:
        with self.assertRaisesRegex(ValueError, "--ons-periodo"):
            run_analysis(source="ons")

    def test_run_analysis_rejects_negative_ons_cache_max_age(self) -> None:
        with self.assertRaisesRegex(ValueError, "--ons-cache-max-age-dias"):
            run_analysis(ons_cache_max_age_days=-1)

    def test_run_analysis_can_include_weather_with_fixture_loader(self) -> None:
        def fake_weather_loader(**kwargs: object) -> list[WeatherRecord]:
            self.assertEqual(kwargs["latitude"], -15.7939)
            self.assertEqual(kwargs["longitude"], -47.8828)
            self.assertEqual(kwargs["forecast_days"], 2)
            return [
                WeatherRecord(datetime(2026, 1, 1, 0), 22.0, 8.0, 0.0, 40.0),
                WeatherRecord(datetime(2026, 1, 1, 1), 24.0, 10.0, 120.0, 60.0),
            ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analise.sqlite"

            result = run_analysis(
                cache_path=cache_path,
                include_weather=True,
                weather_loader=fake_weather_loader,
            )
            cache_payload = read_latest_analysis_cache(cache_path)

        self.assertIsNotNone(result.weather_source)
        self.assertIsNotNone(result.weather_summary)
        self.assertIsNone(result.weather_error)
        assert result.weather_summary is not None
        self.assertEqual(result.weather_summary.record_count, 2)
        self.assertEqual(result.weather_summary.average_temperature_2m_c, 23.0)
        self.assertEqual(cache_payload["weather"]["summary"]["record_count"], 2)
        self.assertEqual(cache_payload["weather"]["data_source"]["kind"], "open-meteo")

    def test_run_analysis_keeps_generation_when_weather_loader_fails(self) -> None:
        def failing_weather_loader(**_kwargs: object) -> list[WeatherRecord]:
            raise WeatherDataError("fixture climatica indisponivel")

        result = run_analysis(
            write_cache=False,
            include_weather=True,
            weather_loader=failing_weather_loader,
        )

        self.assertGreater(len(result.records), 0)
        self.assertEqual(result.weather_records, [])
        self.assertEqual(result.weather_error, "fixture climatica indisponivel")
        self.assertIsNone(result.weather_summary)


if __name__ == "__main__":
    unittest.main()
