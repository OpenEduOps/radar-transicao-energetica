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
    MAX_DESKTOP_BASELINE_POINTS,
    DesktopBaselineChartPoint,
    DesktopGenerationChartBar,
    DesktopStateMessage,
    RadarDesktopApp,
    build_desktop_analysis_options,
    build_desktop_error_view_data,
    build_desktop_view_data,
    format_desktop_status,
    _draw_baseline_chart,
    _draw_generation_chart,
    _format_state_messages,
)
from radar_transicao_energetica.weather import WeatherDataError, WeatherRecord


class FakeCanvas:
    def __init__(self, width: int = 420, height: int = 190) -> None:
        self.width = width
        self.height = height
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def delete(self, *args: object) -> None:
        self.calls.append(("delete", args, {}))

    def winfo_width(self) -> int:
        return self.width

    def winfo_height(self) -> int:
        return self.height

    def create_text(self, *args: object, **kwargs: object) -> int:
        self.calls.append(("create_text", args, kwargs))
        return len(self.calls)

    def create_rectangle(self, *args: object, **kwargs: object) -> int:
        self.calls.append(("create_rectangle", args, kwargs))
        return len(self.calls)

    def create_line(self, *args: object, **kwargs: object) -> int:
        self.calls.append(("create_line", args, kwargs))
        return len(self.calls)

    def create_oval(self, *args: object, **kwargs: object) -> int:
        self.calls.append(("create_oval", args, kwargs))
        return len(self.calls)

    def create_polygon(self, *args: object, **kwargs: object) -> int:
        self.calls.append(("create_polygon", args, kwargs))
        return len(self.calls)

    def calls_named(self, name: str) -> list[tuple[tuple[object, ...], dict[str, object]]]:
        return [(args, kwargs) for call_name, args, kwargs in self.calls if call_name == name]

    def text_values(self) -> list[str]:
        texts: list[str] = []
        for _args, kwargs in self.calls_named("create_text"):
            text = kwargs.get("text")
            if isinstance(text, str):
                texts.append(text)
        return texts

    def fill_values(self, call_name: str) -> list[object]:
        return [kwargs.get("fill") for _args, kwargs in self.calls_named(call_name)]

    def rectangle_coordinates(self) -> list[tuple[float, float, float, float]]:
        coordinates = []
        for args, _kwargs in self.calls_named("create_rectangle"):
            x1, y1, x2, y2 = args
            coordinates.append((float(x1), float(y1), float(x2), float(y2)))
        return coordinates


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
        self.assertEqual(view_data.state_messages, ())
        self.assertGreater(len(view_data.baseline_rows), 0)
        self.assertGreater(len(view_data.baseline_chart_points), 0)
        self.assertEqual(view_data.baseline_rows[-1].method, "media movel")

    def test_build_desktop_view_data_sorts_generation_rows_by_source(self) -> None:
        result = run_analysis(write_cache=False)

        view_data = build_desktop_view_data(result)

        self.assertEqual(
            [row.source for row in view_data.generation_rows],
            ["eolica", "hidraulica", "solar", "termica"],
        )

    def test_build_desktop_view_data_orders_generation_chart_by_volume(self) -> None:
        result = run_analysis(write_cache=False)

        view_data = build_desktop_view_data(result)
        chart_by_source = {bar.source: bar for bar in view_data.generation_chart_bars}

        self.assertEqual(view_data.generation_chart_bars[0].source, "hidraulica")
        self.assertEqual(view_data.generation_chart_bars[0].category, "renovavel")
        self.assertEqual(chart_by_source["termica"].category, "nao renovavel")
        self.assertEqual(
            [bar.generation_mw for bar in view_data.generation_chart_bars],
            sorted(
                (bar.generation_mw for bar in view_data.generation_chart_bars),
                reverse=True,
            ),
        )

    def test_build_desktop_view_data_limits_baseline_points_for_first_screen(self) -> None:
        records = []
        for hour in range(10):
            records.extend(
                [
                    GenerationRecord(datetime(2026, 1, 1, hour), "hidraulica", 50.0 + hour),
                    GenerationRecord(datetime(2026, 1, 1, hour), "termica", 50.0 - hour),
                ]
            )

        result = run_analysis(
            write_cache=False,
            source="ons",
            ons_year=2026,
            ons_month=1,
            ons_loader=lambda _year, _month: records,
        )

        view_data = build_desktop_view_data(result)

        self.assertGreater(result.baseline.evaluated_points, MAX_DESKTOP_BASELINE_POINTS)
        self.assertEqual(len(view_data.baseline_rows), MAX_DESKTOP_BASELINE_POINTS)
        self.assertEqual(len(view_data.baseline_chart_points), MAX_DESKTOP_BASELINE_POINTS)
        self.assertEqual(view_data.baseline_rows[0].period, "2026-01-01 02:00")

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
                WeatherRecord(datetime(2026, 1, 1, 2), 23.0, 9.0, 60.0, 50.0),
                WeatherRecord(datetime(2026, 1, 1, 3), 23.0, 9.0, 60.0, 50.0),
            ],
        )

        view_data = build_desktop_view_data(result)
        metrics = {metric.label: metric.value for metric in view_data.metrics}

        self.assertIn("Open-Meteo Forecast", view_data.weather)
        self.assertIn("temperatura media 23.0 C", view_data.weather)
        self.assertIn("nebulosidade 50.0%", view_data.weather)
        self.assertIn("com clima", metrics["Baseline proxima janela"])
        self.assertIn("/", metrics["Comparacoes com clima"])
        self.assertIn("com clima", view_data.baseline_comparison)
        self.assertEqual(view_data.baseline_rows[-1].method, "clima")
        self.assertEqual(view_data.baseline_chart_points[-1].method, "clima")

    def test_build_desktop_view_data_reports_weather_unavailable_state(self) -> None:
        def failing_weather_loader(**_kwargs: object) -> list[WeatherRecord]:
            raise WeatherDataError("servico fora do ar")

        result = run_analysis(
            write_cache=False,
            include_weather=True,
            weather_loader=failing_weather_loader,
        )

        view_data = build_desktop_view_data(result)
        messages_by_title = {message.title: message for message in view_data.state_messages}

        self.assertIn("Clima indisponivel", messages_by_title)
        self.assertEqual(messages_by_title["Clima indisponivel"].level, "aviso")
        self.assertIn("servico fora do ar", messages_by_title["Clima indisponivel"].detail)
        self.assertIn("indisponivel", view_data.weather)

    def test_build_desktop_view_data_reports_baseline_without_enough_points(self) -> None:
        result = run_analysis(
            write_cache=False,
            source="ons",
            ons_year=2026,
            ons_month=1,
            ons_loader=lambda _year, _month: [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 80.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 20.0),
            ],
        )

        view_data = build_desktop_view_data(result)
        titles = [message.title for message in view_data.state_messages]

        self.assertEqual(result.baseline.evaluated_points, 0)
        self.assertIn("Baseline sem pontos suficientes", titles)
        self.assertEqual(view_data.baseline_rows, ())
        self.assertEqual(view_data.baseline_chart_points, ())

    def test_build_desktop_view_data_reports_no_useful_generation_state(self) -> None:
        result = run_analysis(
            write_cache=False,
            source="ons",
            ons_year=2026,
            ons_month=1,
            ons_loader=lambda _year, _month: [
                GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 0.0),
                GenerationRecord(datetime(2026, 1, 1, 0), "termica", 0.0),
            ],
        )

        view_data = build_desktop_view_data(result)
        metrics = {metric.label: metric.value for metric in view_data.metrics}
        titles = [message.title for message in view_data.state_messages]

        self.assertEqual(metrics["Participacao renovavel"], "sem dados")
        self.assertIn("Sem dados uteis", titles)
        self.assertIn("Baseline sem pontos suficientes", titles)

    def test_build_desktop_view_data_reports_cache_reused_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "analises.sqlite"
            run_analysis(
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

        view_data = build_desktop_view_data(result)
        messages_by_title = {message.title: message for message in view_data.state_messages}

        self.assertIn("Cache reutilizado", messages_by_title)
        self.assertEqual(messages_by_title["Cache reutilizado"].level, "info")
        self.assertIn(str(cache_path), messages_by_title["Cache reutilizado"].detail)

    def test_build_desktop_error_view_data_clears_results_and_reports_error(self) -> None:
        view_data = build_desktop_error_view_data("Periodo ONS invalido")
        metrics = {metric.label: metric.value for metric in view_data.metrics}

        self.assertEqual(view_data.source, "-")
        self.assertEqual(view_data.period, "-")
        self.assertEqual(metrics["Participacao renovavel"], "sem dados")
        self.assertEqual(view_data.generation_rows, ())
        self.assertEqual(view_data.generation_chart_bars, ())
        self.assertEqual(view_data.baseline_rows, ())
        self.assertEqual(view_data.baseline_chart_points, ())
        self.assertEqual(view_data.state_messages[0].level, "erro")
        self.assertEqual(view_data.state_messages[0].title, "Erro de entrada")
        self.assertIn("Periodo ONS invalido", view_data.state_messages[0].detail)

    def test_build_desktop_error_view_data_reports_no_data_state(self) -> None:
        view_data = build_desktop_error_view_data("Nao ha registros de geracao para analisar.")

        self.assertEqual(view_data.state_messages[0].level, "aviso")
        self.assertEqual(view_data.state_messages[0].title, "Sem dados")
        self.assertIn("nao retornou registros", view_data.state_messages[0].detail)
        self.assertIn("aviso", view_data.alert)

    def test_format_state_messages_exposes_level_title_and_detail(self) -> None:
        text = _format_state_messages(
            (
                DesktopStateMessage("aviso", "Clima indisponivel", "sem conexao"),
                DesktopStateMessage("info", "Cache reutilizado", "cache local"),
            )
        )

        self.assertIn("ATENCAO - Clima indisponivel: sem conexao", text)
        self.assertIn("INFO - Cache reutilizado: cache local", text)

    def test_format_state_messages_reports_no_warnings(self) -> None:
        self.assertEqual(_format_state_messages(()), "Sem avisos")

    def test_generation_chart_draws_source_bars_without_tk_window(self) -> None:
        canvas = FakeCanvas(width=520, height=160)

        _draw_generation_chart(
            canvas,
            (
                DesktopGenerationChartBar("hidraulica", 100.0, "renovavel"),
                DesktopGenerationChartBar("termica", 40.0, "nao renovavel"),
                DesktopGenerationChartBar("biomassa", 10.0, "desconhecida"),
            ),
        )

        self.assertEqual(canvas.calls[0][0], "delete")
        self.assertIn("hidraulica (renovavel)", canvas.text_values())
        self.assertEqual(len(canvas.calls_named("create_rectangle")), 3)
        self.assertEqual(
            canvas.fill_values("create_rectangle"),
            ["#166534", "#991b1b", "#374151"],
        )
        self.assertIn("100 MW", canvas.text_values())

    def test_generation_chart_draws_empty_state_without_tk_window(self) -> None:
        canvas = FakeCanvas(width=520, height=160)

        _draw_generation_chart(canvas, ())

        self.assertIn("Sem dados de geracao", canvas.text_values())
        self.assertEqual(canvas.calls_named("create_rectangle"), [])

    def test_generation_chart_draws_zero_generation_state_without_tk_window(self) -> None:
        canvas = FakeCanvas(width=520, height=160)

        _draw_generation_chart(
            canvas,
            (
                DesktopGenerationChartBar("hidraulica", 0.0, "renovavel"),
                DesktopGenerationChartBar("termica", 0.0, "nao renovavel"),
            ),
        )

        self.assertIn("Geracao sem valor positivo", canvas.text_values())
        self.assertEqual(canvas.calls_named("create_rectangle"), [])

    def test_generation_chart_keeps_many_bars_inside_canvas_without_tk_window(self) -> None:
        canvas = FakeCanvas(width=520, height=160)

        _draw_generation_chart(
            canvas,
            tuple(
                DesktopGenerationChartBar(f"fonte_{index}", float(20 - index), "desconhecida")
                for index in range(20)
            ),
        )

        rectangles = canvas.rectangle_coordinates()

        self.assertEqual(len(rectangles), 20)
        self.assertTrue(all(y1 >= 16 for _x1, y1, _x2, _y2 in rectangles))
        self.assertTrue(all(y2 <= 144 for _x1, _y1, _x2, y2 in rectangles))

    def test_baseline_chart_draws_legend_and_weather_markers_without_tk_window(self) -> None:
        canvas = FakeCanvas(width=520, height=220)

        _draw_baseline_chart(
            canvas,
            (
                DesktopBaselineChartPoint("2026-01-01 01:00", 0.8, 0.7, "media movel"),
                DesktopBaselineChartPoint("2026-01-01 02:00", 0.75, 0.78, "clima"),
            ),
        )

        self.assertIn("Real", canvas.text_values())
        self.assertIn("Prev. media", canvas.text_values())
        self.assertIn("Prev. clima", canvas.text_values())
        self.assertIn("100%", canvas.text_values())
        self.assertIn("0%", canvas.text_values())
        self.assertEqual(
            canvas.fill_values("create_oval"),
            ["#166534", "#166534", "#166534"],
        )
        self.assertEqual(
            canvas.fill_values("create_rectangle"),
            ["#1d4ed8", "#1d4ed8"],
        )
        self.assertEqual(
            canvas.fill_values("create_polygon"),
            ["#9a3412", "#9a3412"],
        )
        self.assertGreaterEqual(len(canvas.calls_named("create_line")), 3)

    def test_baseline_chart_draws_empty_state_without_tk_window(self) -> None:
        canvas = FakeCanvas(width=520, height=220)

        _draw_baseline_chart(canvas, ())

        self.assertIn("Sem comparacoes de baseline", canvas.text_values())
        self.assertEqual(canvas.calls_named("create_oval"), [])

    def test_baseline_chart_draws_single_point_without_series_line(self) -> None:
        canvas = FakeCanvas(width=520, height=220)

        _draw_baseline_chart(
            canvas,
            (DesktopBaselineChartPoint("2026-01-01 01:00", 0.8, 0.7, "media movel"),),
        )

        data_lines = [
            kwargs
            for _args, kwargs in canvas.calls_named("create_line")
            if kwargs.get("width") == 2
        ]

        self.assertEqual(data_lines, [])
        self.assertEqual(len(canvas.calls_named("create_oval")), 2)
        self.assertEqual(len(canvas.calls_named("create_rectangle")), 2)
        self.assertEqual(len(canvas.calls_named("create_polygon")), 1)

    def test_desktop_redraw_charts_uses_last_view_data_without_tk_window(self) -> None:
        result = run_analysis(write_cache=False)
        view_data = build_desktop_view_data(result)
        generation_canvas = FakeCanvas(width=520, height=160)
        baseline_canvas = FakeCanvas(width=520, height=220)
        app = object.__new__(RadarDesktopApp)
        app.current_view_data = view_data
        app.generation_canvas = generation_canvas
        app.baseline_canvas = baseline_canvas

        RadarDesktopApp._redraw_charts(app)

        self.assertGreater(len(generation_canvas.calls_named("create_rectangle")), 0)
        self.assertGreater(len(baseline_canvas.calls_named("create_oval")), 0)

    def test_run_from_keyboard_executes_analysis_and_stops_event(self) -> None:
        app = object.__new__(RadarDesktopApp)
        calls: list[str] = []

        def fake_run_current_analysis() -> None:
            calls.append("run")

        app.run_current_analysis = fake_run_current_analysis

        result = RadarDesktopApp._run_from_keyboard(app, object())

        self.assertEqual(calls, ["run"])
        self.assertEqual(result, "break")

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
