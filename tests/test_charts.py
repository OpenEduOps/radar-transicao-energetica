from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.baseline import BaselineComparison
from radar_transicao_energetica.charts import render_baseline_comparison_chart


class ChartTest(unittest.TestCase):
    def test_render_baseline_comparison_chart_marks_media_and_weather(self) -> None:
        chart = render_baseline_comparison_chart(
            (
                BaselineComparison(
                    period="2026-01-01T01:00:00",
                    actual_renewable_share=0.8,
                    predicted_renewable_share=0.5,
                    absolute_error=0.3,
                ),
                BaselineComparison(
                    period="2026-01-01T02:00:00",
                    actual_renewable_share=0.75,
                    predicted_renewable_share=0.78,
                    absolute_error=0.03,
                    method="media_movel_com_features_climaticas",
                    weather_adjusted=True,
                ),
            )
        )

        self.assertIn("Comparacao real vs previsto por periodo", chart)
        self.assertIn("Legenda: [media] media movel pura; [clima] analogia climatica.", chart)
        self.assertIn("[media]", chart)
        self.assertIn("[clima]", chart)
        self.assertIn("erro 30.0 p.p.", chart)

    def test_render_baseline_comparison_chart_handles_empty_input(self) -> None:
        chart = render_baseline_comparison_chart(())

        self.assertEqual(chart, "Sem comparacoes de baseline para exibir.")


if __name__ == "__main__":
    unittest.main()
