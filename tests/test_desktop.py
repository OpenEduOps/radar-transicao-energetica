from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.desktop import (
    build_desktop_analysis_options,
    build_desktop_view_data,
)


class DesktopTest(unittest.TestCase):
    def test_build_desktop_view_data_exposes_core_metrics(self) -> None:
        result = run_analysis(write_cache=False)

        view_data = build_desktop_view_data(result)
        metrics = {metric.label: metric.value for metric in view_data.metrics}

        self.assertEqual(view_data.source, "Exemplo embutido")
        self.assertIn("2026-01-01 00:00", view_data.period)
        self.assertEqual(metrics["Participacao renovavel"], "79.0%")
        self.assertIn("MW", metrics["Geracao total"])
        self.assertIn("p.p.", metrics["Baseline MAE"])
        self.assertIn("boa_janela_renovavel", view_data.alert)
        self.assertIn("real", view_data.baseline_comparison)
        self.assertIn("previsto", view_data.baseline_comparison)

    def test_build_desktop_view_data_sorts_generation_rows_by_source(self) -> None:
        result = run_analysis(write_cache=False)

        view_data = build_desktop_view_data(result)

        self.assertEqual(
            [row.source for row in view_data.generation_rows],
            ["eolica", "hidraulica", "solar", "termica"],
        )

    def test_build_desktop_analysis_options_accepts_csv_source(self) -> None:
        options = build_desktop_analysis_options(source="csv", csv_path=" examples/dados.csv ")

        self.assertEqual(str(options.source_path), "examples\\dados.csv")
        self.assertEqual(options.source, "exemplo")

    def test_build_desktop_analysis_options_parses_ons_source(self) -> None:
        options = build_desktop_analysis_options(source="ons", ons_period="2026-01")

        self.assertEqual(options.source, "ons")
        self.assertEqual(options.ons_year, 2026)
        self.assertEqual(options.ons_month, 1)

    def test_build_desktop_analysis_options_rejects_unknown_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "Fonte de dados desconhecida"):
            build_desktop_analysis_options(source="invalida")


if __name__ == "__main__":
    unittest.main()
