from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.cache import read_latest_analysis_cache
from radar_transicao_energetica.cli import render_report
from radar_transicao_energetica.data import GenerationRecord
from radar_transicao_energetica.weather import WeatherRecord


class CliTest(unittest.TestCase):
    def test_cli_runs_with_embedded_sample_json(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--json",
                "--sem-cache",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        payload = json.loads(result.stdout)

        self.assertIn("summary", payload)
        self.assertGreater(payload["summary"]["renewable_share"], 0)
        self.assertIn("alert", payload)
        self.assertIn("baseline", payload)
        self.assertIn("period_summaries", payload)
        self.assertEqual(payload["data_source"]["kind"], "exemplo")

    def test_cli_writes_cache_when_enabled(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--json",
                    "--cache",
                    str(cache_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = read_latest_analysis_cache(cache_path)

        self.assertIn("summary", payload)
        self.assertIn("alert", payload)
        self.assertEqual(payload["data_source"]["kind"], "exemplo")

    def test_cli_reuses_cached_ons_records_without_network(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"
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

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--fonte",
                    "ons",
                    "--ons-periodo",
                    "2026-01",
                    "--cache",
                    str(cache_path),
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(result.stdout)

        self.assertTrue(payload["cache_hit"])
        self.assertEqual(payload["data_source"]["kind"], "ons")
        self.assertEqual(payload["summary"]["renewable_share"], 0.8)

    def test_cli_json_includes_cache_path_when_cache_is_enabled(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--json",
                    "--cache",
                    str(cache_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(result.stdout)

        self.assertEqual(payload["cache_path"], str(cache_path))
        self.assertEqual(payload["data_source"]["kind"], "exemplo")

    def test_cli_can_compact_existing_cache(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"
            run_analysis(cache_path=cache_path)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--cache",
                    str(cache_path),
                    "--compactar-cache",
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            payload = read_latest_analysis_cache(cache_path)

        self.assertIn("Cache compactado em:", result.stdout)
        self.assertEqual(payload["data_source"]["kind"], "exemplo")

    def test_cli_compact_cache_reports_missing_file_without_creating_it(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--cache",
                    str(cache_path),
                    "--compactar-cache",
                ],
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertFalse(cache_path.exists())

        self.assertEqual(result.returncode, 1)
        self.assertIn("Cache nao encontrado", result.stderr)

    def test_cli_reports_invalid_file_with_nonzero_exit(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--arquivo",
                "arquivo-inexistente.csv",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Arquivo nao encontrado", result.stderr)

    def test_cli_reports_cache_write_failure_without_traceback(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--cache",
                    tmpdir,
                ],
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Nao foi possivel gravar o cache", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_reports_unknown_sources_in_text_output(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")
        csv_text = "\n".join(
            [
                "period,source,generation_mw",
                "2026-01-01 00:00,hidraulica,50",
                "2026-01-01 00:00,biomassa,25",
                "2026-01-01 00:00,termica,25",
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "geracao.csv"
            path.write_text(csv_text, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--arquivo",
                    str(path),
                    "--sem-cache",
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertIn("Fontes nao classificadas na V0: biomassa", result.stdout)
        self.assertIn("fontes ainda nao classificadas", result.stdout)
        self.assertIn("Fonte: CSV local", result.stdout)

    def test_cli_text_output_reports_baseline_metric_and_comparison(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--sem-cache",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertIn("Baseline MAE:", result.stdout)
        self.assertIn("Baseline RMSE:", result.stdout)
        self.assertIn("p.p.", result.stdout)
        self.assertIn("Ultima comparacao baseline:", result.stdout)
        self.assertIn("real", result.stdout)
        self.assertIn("previsto", result.stdout)
        self.assertIn("Comparacao real vs previsto por periodo:", result.stdout)
        self.assertIn("[media]", result.stdout)

    def test_cli_reports_missing_ons_period_without_network(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--fonte",
                "ons",
                "--sem-cache",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("--ons-periodo", result.stderr)

    def test_cli_rejects_ons_period_for_example_source(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--ons-periodo",
                "2026-01",
                "--sem-cache",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("--ons-periodo so pode ser usado", result.stderr)

    def test_cli_rejects_malformed_ons_period_without_network(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--fonte",
                "ons",
                "--ons-periodo",
                "2026-1",
                "--sem-cache",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("YYYY-MM", result.stderr)

    def test_cli_rejects_invalid_weather_options_without_network(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--clima",
                "open-meteo",
                "--clima-latitude",
                "91",
                "--sem-cache",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Latitude climatica", result.stderr)

    def test_render_report_includes_weather_summary_when_requested(self) -> None:
        result = run_analysis(
            write_cache=False,
            include_weather=True,
            weather_loader=lambda **_kwargs: [
                WeatherRecord(datetime(2026, 1, 1, 0), 22.0, 8.0, 0.0, 40.0),
                WeatherRecord(datetime(2026, 1, 1, 1), 24.0, 10.0, 120.0, 60.0),
                WeatherRecord(datetime(2026, 1, 1, 2), 23.0, 9.0, 60.0, 50.0),
                WeatherRecord(datetime(2026, 1, 1, 3), 23.0, 9.0, 60.0, 50.0),
            ],
        )

        report = render_report(
            result.summary,
            result.period_summaries,
            result.alert.message,
            result.baseline,
            result.data_source,
            result.weather_summary,
            result.weather_source,
            result.weather_error,
        )

        self.assertIn("Clima: Open-Meteo Forecast", report)
        self.assertIn("Temperatura media: 23.0 C", report)
        self.assertIn("Vento medio: 9.0 km/h", report)
        self.assertIn("Nebulosidade media: 50.0%", report)
        self.assertIn("Baseline metodo: media_movel_com_features_climaticas", report)
        self.assertIn("Baseline proxima janela:", report)
        self.assertIn("(com clima)", report)
        self.assertIn("Comparacoes com features climaticas:", report)

    def test_render_report_includes_weather_error_without_hiding_generation(self) -> None:
        result = run_analysis(write_cache=False)

        report = render_report(
            result.summary,
            result.period_summaries,
            result.alert.message,
            result.baseline,
            result.data_source,
            weather_error="fonte climatica indisponivel",
        )

        self.assertIn("Geracao total:", report)
        self.assertIn("Clima: indisponivel", report)
        self.assertIn("fonte climatica indisponivel", report)


if __name__ == "__main__":
    unittest.main()
