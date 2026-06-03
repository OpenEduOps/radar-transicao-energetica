from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.data import GenerationRecord
from radar_transicao_energetica.domain import summarize_by_period
from radar_transicao_energetica.features import (
    build_weather_features_by_period,
    find_next_weather_feature,
    weather_feature_distance,
)
from radar_transicao_energetica.weather import WeatherRecord


class FeaturesTest(unittest.TestCase):
    def test_build_weather_features_aligns_weather_to_generation_periods(self) -> None:
        summaries = summarize_by_period(
            [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 80.0),
                GenerationRecord(datetime(2026, 1, 1, 1), "termica", 20.0),
            ]
        )
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 0, 10), 22.0, 8.0, 100.0, 40.0),
            WeatherRecord(datetime(2026, 1, 1, 0, 30), 24.0, 10.0, 120.0, 60.0),
            WeatherRecord(datetime(2026, 1, 1, 3), 30.0, 2.0, 900.0, 10.0),
        ]

        features = build_weather_features_by_period(summaries, weather)

        self.assertEqual(len(features), 1)
        feature = features[datetime(2026, 1, 1, 0)]
        self.assertEqual(feature.available_feature_count, 4)
        self.assertEqual(feature.temperature_2m_c, 23.0)
        self.assertEqual(feature.wind_speed_10m_kmh, 9.0)
        self.assertEqual(feature.shortwave_radiation_w_m2, 110.0)
        self.assertEqual(feature.cloud_cover_percent, 50.0)

    def test_find_next_weather_feature_returns_first_future_period(self) -> None:
        summaries = summarize_by_period(
            [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            ]
        )
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 0), 22.0, 8.0, 100.0, 40.0),
            WeatherRecord(datetime(2026, 1, 1, 1), 24.0, 10.0, 120.0, 60.0),
            WeatherRecord(datetime(2026, 1, 1, 2), 26.0, 12.0, 140.0, 70.0),
        ]

        feature = find_next_weather_feature(summaries, weather)

        self.assertIsNotNone(feature)
        assert feature is not None
        self.assertEqual(feature.period, datetime(2026, 1, 1, 1))
        self.assertEqual(feature.temperature_2m_c, 24.0)

    def test_weather_features_ignore_periods_without_any_available_value(self) -> None:
        summaries = summarize_by_period(
            [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            ]
        )
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 0), None, None, None, None),
        ]

        features = build_weather_features_by_period(summaries, weather)

        self.assertEqual(features, {})

    def test_find_next_weather_feature_skips_empty_future_periods(self) -> None:
        summaries = summarize_by_period(
            [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
            ]
        )
        weather = [
            WeatherRecord(datetime(2026, 1, 1, 1), None, None, None, None),
            WeatherRecord(datetime(2026, 1, 1, 2), 26.0, 12.0, 140.0, 70.0),
        ]

        feature = find_next_weather_feature(summaries, weather)

        self.assertIsNotNone(feature)
        assert feature is not None
        self.assertEqual(feature.period, datetime(2026, 1, 1, 2))
        self.assertEqual(feature.available_feature_count, 4)

    def test_weather_feature_distance_uses_available_common_values(self) -> None:
        summaries = summarize_by_period(
            [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 50.0),
                GenerationRecord(datetime(2026, 1, 1, 1), "hidraulica", 80.0),
                GenerationRecord(datetime(2026, 1, 1, 1), "termica", 20.0),
            ]
        )
        features = build_weather_features_by_period(
            summaries,
            [
                WeatherRecord(datetime(2026, 1, 1, 0), 20.0, 10.0, None, None),
                WeatherRecord(datetime(2026, 1, 1, 1), 24.0, 18.0, 800.0, 60.0),
            ],
        )

        distance = weather_feature_distance(
            features[datetime(2026, 1, 1, 0)],
            features[datetime(2026, 1, 1, 1)],
        )

        self.assertIsNotNone(distance)
        assert distance is not None
        self.assertAlmostEqual(distance, 0.2)


if __name__ == "__main__":
    unittest.main()
