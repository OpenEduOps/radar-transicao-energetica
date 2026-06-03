from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.data import GenerationRecord
from radar_transicao_energetica.desktop import (
    build_desktop_analysis_options,
    build_desktop_view_data,
    format_desktop_status,
)
from radar_transicao_energetica.weather import WeatherRecord


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
        self.assertEqual(view_data.weather, "nao solicitado")

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

    def test_build_desktop_analysis_options_parses_weather_controls(self) -> None:
        options = build_desktop_analysis_options(
            source="exemplo",
            include_weather=True,
            weather_latitude=" -22.9 ",
            weather_longitude=" -43.2 ",
            weather_forecast_days="3",
        )

        self.assertTrue(options.include_weather)
        self.assertEqual(options.weather_latitude, -22.9)
        self.assertEqual(options.weather_longitude, -43.2)
        self.assertEqual(options.weather_forecast_days, 3)

    def test_build_desktop_analysis_options_rejects_invalid_weather_controls(self) -> None:
        with self.assertRaisesRegex(ValueError, "latitude climatica"):
            build_desktop_analysis_options(
                source="exemplo",
                include_weather=True,
                weather_latitude="invalida",
            )

    def test_build_desktop_view_data_exposes_weather_summary(self) -> None:
        result = run_analysis(
            write_cache=False,
            include_weather=True,
            weather_loader=lambda **_kwargs: [
                WeatherRecord(datetime(2026, 1, 1, 0), 22.0, 8.0, 0.0, 40.0),
                WeatherRecord(datetime(2026, 1, 1, 1), 24.0, 10.0, 120.0, 60.0),
            ],
        )

        view_data = build_desktop_view_data(result)

        self.assertIn("Open-Meteo Forecast", view_data.weather)
        self.assertIn("temperatura media 23.0 C", view_data.weather)
        self.assertIn("nebulosidade 50.0%", view_data.weather)

    def test_build_desktop_analysis_options_rejects_unknown_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "Fonte de dados desconhecida"):
            build_desktop_analysis_options(source="invalida")

    def test_format_desktop_status_includes_cache_path_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analises.sqlite"
            result = run_analysis(cache_path=cache_path)

        self.assertEqual(format_desktop_status(result), f"Analise atualizada; cache: {cache_path}")

    def test_format_desktop_status_reports_cache_hit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analises.sqlite"
            first_result = run_analysis(
                cache_path=cache_path,
                source="ons",
                ons_year=2026,
                ons_month=1,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 90.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 10.0),
                ],
            )
            result = run_analysis(
                cache_path=cache_path,
                source="ons",
                ons_year=2026,
                ons_month=1,
                ons_loader=lambda _year, _month: [],
            )

        self.assertFalse(first_result.cache_hit)
        self.assertTrue(result.cache_hit)
        self.assertEqual(
            format_desktop_status(result),
            f"Analise atualizada; cache reutilizado: {cache_path}",
        )


if __name__ == "__main__":
    unittest.main()
