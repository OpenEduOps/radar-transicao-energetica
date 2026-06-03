from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.alerts import build_renewable_alert
from radar_transicao_energetica.baseline import (
    evaluate_moving_average_baseline,
    predict_next_renewable_share,
)
from radar_transicao_energetica.data import GenerationRecord
from radar_transicao_energetica.domain import summarize_by_period, summarize_generation
from radar_transicao_energetica.weather import WeatherRecord


class DomainTest(unittest.TestCase):
    def test_summarize_generation_calculates_renewable_share(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "eolica", 25.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 25.0),
        ]

        summary = summarize_generation(records)

        self.assertEqual(summary.total_generation_mw, 100.0)
        self.assertEqual(summary.renewable_generation_mw, 75.0)
        self.assertEqual(summary.renewable_share, 0.75)

    def test_summarize_generation_handles_zero_total(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 0.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 0.0),
        ]

        summary = summarize_generation(records)

        self.assertIsNone(summary.renewable_share)

    def test_summarize_generation_exposes_unknown_sources(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "biomassa", 25.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 25.0),
        ]

        summary = summarize_generation(records)

        self.assertEqual(summary.unknown_sources, ("biomassa",))
        self.assertEqual(summary.renewable_share, 0.5)

    def test_summarize_by_period_sorts_periods(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 40.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "solar", 50.0),
        ]

        summaries = summarize_by_period(records)

        self.assertEqual([item.period.hour for item in summaries], [0, 1])
        self.assertEqual(summaries[0].renewable_share, 0.5)
        self.assertEqual(summaries[1].renewable_share, 1.0)
        self.assertEqual(summaries[0].unknown_sources, ())

    def test_alert_levels_are_interpretable(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 40.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 60.0),
        ]

        alert = build_renewable_alert(summarize_generation(records))

        self.assertEqual(alert.level, "pressao_termica")
        self.assertIn("pressao termica", alert.message)

    def test_baseline_uses_moving_average(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 80.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "termica", 20.0),
        ]

        prediction = predict_next_renewable_share(summarize_by_period(records), window=2)

        self.assertEqual(prediction.method, "media_movel")
        self.assertEqual(prediction.points_used, 2)
        self.assertEqual(prediction.window, 2)
        self.assertEqual(prediction.error_metric, "mae")
        self.assertAlmostEqual(prediction.predicted_renewable_share or 0, 0.65)
        self.assertEqual(prediction.evaluated_points, 1)
        self.assertAlmostEqual(prediction.mean_absolute_error or 0, 0.3)
        self.assertEqual(prediction.comparisons[0].period, "2026-01-01T01:00:00")
        self.assertAlmostEqual(prediction.comparisons[0].actual_renewable_share, 0.8)
        self.assertAlmostEqual(prediction.comparisons[0].predicted_renewable_share, 0.5)

    def test_baseline_evaluates_walk_forward_comparisons(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 80.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "termica", 20.0),
            GenerationRecord(datetime(2026, 1, 1, 2), "hidraulica", 40.0),
            GenerationRecord(datetime(2026, 1, 1, 2), "termica", 60.0),
        ]

        comparisons = evaluate_moving_average_baseline(summarize_by_period(records), window=2)

        self.assertEqual(len(comparisons), 2)
        self.assertAlmostEqual(comparisons[0].predicted_renewable_share, 0.5)
        self.assertAlmostEqual(comparisons[0].absolute_error, 0.3)
        self.assertAlmostEqual(comparisons[1].predicted_renewable_share, 0.65)
        self.assertAlmostEqual(comparisons[1].absolute_error, 0.25)

    def test_baseline_ignores_periods_without_renewable_share_in_evaluation(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 0.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "termica", 0.0),
            GenerationRecord(datetime(2026, 1, 1, 2), "hidraulica", 75.0),
            GenerationRecord(datetime(2026, 1, 1, 2), "termica", 25.0),
        ]

        prediction = predict_next_renewable_share(summarize_by_period(records), window=2)

        self.assertEqual(prediction.evaluated_points, 1)
        self.assertAlmostEqual(prediction.comparisons[0].predicted_renewable_share, 0.5)
        self.assertAlmostEqual(prediction.comparisons[0].actual_renewable_share, 0.75)
        self.assertAlmostEqual(prediction.mean_absolute_error or 0, 0.25)

    def test_baseline_rejects_invalid_window(self) -> None:
        with self.assertRaises(ValueError):
            predict_next_renewable_share([], window=0)

    def test_baseline_uses_weather_features_for_walk_forward_comparisons(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 20.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 80.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 80.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "termica", 20.0),
            GenerationRecord(datetime(2026, 1, 1, 2), "hidraulica", 25.0),
            GenerationRecord(datetime(2026, 1, 1, 2), "termica", 75.0),
            GenerationRecord(datetime(2026, 1, 1, 3), "hidraulica", 75.0),
            GenerationRecord(datetime(2026, 1, 1, 3), "termica", 25.0),
        ]
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 0), 20.0, 5.0, 100.0, 80.0),
            WeatherRecord(datetime(2026, 1, 1, 1), 28.0, 25.0, 900.0, 10.0),
            WeatherRecord(datetime(2026, 1, 1, 2), 21.0, 6.0, 110.0, 78.0),
            WeatherRecord(datetime(2026, 1, 1, 3), 27.0, 24.0, 880.0, 12.0),
        ]

        prediction = predict_next_renewable_share(
            summarize_by_period(records),
            window=1,
            weather_records=weather,
        )

        self.assertEqual(prediction.method, "media_movel_com_features_climaticas")
        self.assertEqual(prediction.weather_feature_periods, 4)
        self.assertEqual(prediction.weather_adjusted_comparisons, 3)
        self.assertEqual(prediction.comparisons[2].period, "2026-01-01T03:00:00")
        self.assertTrue(prediction.comparisons[2].weather_adjusted)
        self.assertAlmostEqual(prediction.comparisons[2].predicted_renewable_share, 0.8)
        self.assertAlmostEqual(prediction.comparisons[2].actual_renewable_share, 0.75)

    def test_baseline_uses_future_weather_feature_for_next_prediction(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 20.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 80.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 80.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "termica", 20.0),
        ]
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 0), 20.0, 5.0, 100.0, 80.0),
            WeatherRecord(datetime(2026, 1, 1, 1), 28.0, 25.0, 900.0, 10.0),
            WeatherRecord(datetime(2026, 1, 1, 2), 27.5, 24.0, 880.0, 12.0),
        ]

        prediction = predict_next_renewable_share(
            summarize_by_period(records),
            window=1,
            weather_records=weather,
        )

        self.assertEqual(prediction.method, "media_movel_com_features_climaticas")
        self.assertEqual(prediction.points_used, 1)
        self.assertTrue(prediction.predicted_with_weather)
        self.assertIsNotNone(prediction.next_weather_feature)
        self.assertAlmostEqual(prediction.predicted_renewable_share or 0, 0.8)

    def test_baseline_reports_only_available_weather_feature_names(self) -> None:
        records = [
            GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 75.0),
            GenerationRecord(datetime(2026, 1, 1, 1), "termica", 25.0),
        ]
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 0), 20.0, 5.0, None, None),
            WeatherRecord(datetime(2026, 1, 1, 1), 22.0, 7.0, None, None),
        ]

        prediction = predict_next_renewable_share(
            summarize_by_period(records),
            window=1,
            weather_records=weather,
        )

        self.assertEqual(
            prediction.weather_feature_names,
            ("temperature_2m_c", "wind_speed_10m_kmh"),
        )


if __name__ == "__main__":
    unittest.main()
