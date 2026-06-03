from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.serialization import analysis_payload
from radar_transicao_energetica.weather import WeatherRecord


class SerializationTest(unittest.TestCase):
    def test_analysis_payload_keeps_cache_and_cli_contract_consistent(self) -> None:
        result = run_analysis(write_cache=False)

        payload = analysis_payload(
            summary=result.summary,
            period_summaries=result.period_summaries,
            alert=result.alert,
            baseline=result.baseline,
            cache_path="data/cache/analises.sqlite",
            data_source=result.data_source,
        )

        self.assertIn("summary", payload)
        self.assertIn("period_summaries", payload)
        self.assertIn("alert", payload)
        self.assertIn("baseline", payload)
        self.assertIn("data_source", payload)
        self.assertEqual(payload["data_source"]["kind"], "exemplo")
        self.assertEqual(payload["cache_path"], "data/cache/analises.sqlite")
        self.assertIn("mean_absolute_error", payload["baseline"])
        self.assertEqual(payload["baseline"]["error_metric"], "mae")
        self.assertEqual(payload["baseline"]["window"], 3)
        self.assertIn("evaluated_points", payload["baseline"])
        self.assertIn("comparisons", payload["baseline"])
        self.assertGreater(payload["baseline"]["evaluated_points"], 0)
        self.assertIn("renewable_share", payload["summary"])
        self.assertIn("unknown_sources", payload["summary"])
        self.assertIn("unknown_sources", payload["period_summaries"][0])
        self.assertIn("message", payload["alert"])

    def test_analysis_payload_includes_optional_weather_contract(self) -> None:
        result = run_analysis(
            write_cache=False,
            include_weather=True,
            weather_loader=lambda **_kwargs: [
                WeatherRecord(datetime(2026, 1, 1, 0), 22.0, 8.0, 0.0, 40.0),
                WeatherRecord(datetime(2026, 1, 1, 1), 24.0, 10.0, 120.0, 60.0),
            ],
        )

        payload = analysis_payload(
            summary=result.summary,
            period_summaries=result.period_summaries,
            alert=result.alert,
            baseline=result.baseline,
            data_source=result.data_source,
            weather_source=result.weather_source,
            weather_summary=result.weather_summary,
            weather_records=result.weather_records,
            weather_error=result.weather_error,
        )

        self.assertIn("weather", payload)
        self.assertEqual(payload["weather"]["data_source"]["kind"], "open-meteo")
        self.assertEqual(payload["weather"]["summary"]["record_count"], 2)
        self.assertEqual(payload["weather"]["summary"]["average_temperature_2m_c"], 23.0)
        self.assertEqual(len(payload["weather"]["records"]), 2)
        self.assertEqual(payload["weather"]["records"][1]["wind_speed_10m_kmh"], 10.0)


if __name__ == "__main__":
    unittest.main()
