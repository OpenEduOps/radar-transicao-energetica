from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.alerts import build_renewable_alert
from radar_transicao_energetica.baseline import predict_next_renewable_share
from radar_transicao_energetica.data import GenerationRecord
from radar_transicao_energetica.domain import summarize_by_period, summarize_generation


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
        self.assertAlmostEqual(prediction.predicted_renewable_share or 0, 0.65)


if __name__ == "__main__":
    unittest.main()
