from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Literal, Protocol
import tkinter as tk

from radar_transicao_energetica.app import AnalysisResult, run_analysis
from radar_transicao_energetica.baseline import BaselineComparison, BaselinePrediction
from radar_transicao_energetica.cli import DEFAULT_CACHE_PATH
from radar_transicao_energetica.data import GenerationDataError
from radar_transicao_energetica.domain import NON_RENEWABLE_SOURCES, RENEWABLE_SOURCES
from radar_transicao_energetica.ons import parse_ons_period
from radar_transicao_energetica.weather import (
    DEFAULT_WEATHER_FORECAST_DAYS,
    DEFAULT_WEATHER_LATITUDE,
    DEFAULT_WEATHER_LONGITUDE,
)


MAX_DESKTOP_BASELINE_POINTS = 8
DesktopStateLevel = Literal["info", "aviso", "erro"]


class CanvasLike(Protocol):
    def delete(self, *args: object) -> None: ...

    def winfo_width(self) -> int: ...

    def winfo_height(self) -> int: ...

    def create_text(self, *args: object, **kwargs: object) -> int: ...

    def create_rectangle(self, *args: object, **kwargs: object) -> int: ...

    def create_line(self, *args: object, **kwargs: object) -> int: ...

    def create_oval(self, *args: object, **kwargs: object) -> int: ...


@dataclass(frozen=True)
class DesktopAnalysisOptions:
    source_path: Path | None = None
    source: str = "exemplo"
    ons_year: int | None = None
    ons_month: int | None = None
    include_weather: bool = False
    weather_latitude: float = DEFAULT_WEATHER_LATITUDE
    weather_longitude: float = DEFAULT_WEATHER_LONGITUDE
    weather_forecast_days: int = DEFAULT_WEATHER_FORECAST_DAYS


@dataclass(frozen=True)
class DesktopMetric:
    label: str
    value: str


@dataclass(frozen=True)
class DesktopStateMessage:
    level: DesktopStateLevel
    title: str
    detail: str


@dataclass(frozen=True)
class DesktopGenerationRow:
    source: str
    generation_mw: str


@dataclass(frozen=True)
class DesktopGenerationChartBar:
    source: str
    generation_mw: float
    category: str


@dataclass(frozen=True)
class DesktopBaselineRow:
    period: str
    actual: str
    predicted: str
    error: str
    method: str


@dataclass(frozen=True)
class DesktopBaselineChartPoint:
    period: str
    actual_renewable_share: float
    predicted_renewable_share: float
    method: str


@dataclass(frozen=True)
class DesktopViewData:
    source: str
    period: str
    metrics: tuple[DesktopMetric, ...]
    state_messages: tuple[DesktopStateMessage, ...]
    generation_rows: tuple[DesktopGenerationRow, ...]
    generation_chart_bars: tuple[DesktopGenerationChartBar, ...]
    alert: str
    baseline_comparison: str
    baseline_rows: tuple[DesktopBaselineRow, ...]
    baseline_chart_points: tuple[DesktopBaselineChartPoint, ...]
    weather: str


def build_desktop_view_data(result: AnalysisResult) -> DesktopViewData:
    summary = result.summary
    baseline = result.baseline
    latest_comparison = baseline.comparisons[-1] if baseline.comparisons else None

    metrics = (
        DesktopMetric("Participacao renovavel", _format_percent(summary.renewable_share)),
        DesktopMetric("Geracao total", _format_mw(summary.total_generation_mw)),
        DesktopMetric("Geracao renovavel", _format_mw(summary.renewable_generation_mw)),
        DesktopMetric("Baseline proxima janela", _format_baseline_prediction(baseline)),
        DesktopMetric("Baseline MAE", _format_points(baseline.mean_absolute_error)),
        DesktopMetric(
            "Comparacoes com clima",
            f"{baseline.weather_adjusted_comparisons}/{baseline.evaluated_points}",
        ),
    )
    state_messages = _build_state_messages(result)
    generation_rows = tuple(
        DesktopGenerationRow(source=source, generation_mw=_format_mw(generation))
        for source, generation in sorted(summary.generation_by_source.items())
    )
    generation_chart_bars = tuple(
        DesktopGenerationChartBar(
            source=source,
            generation_mw=generation,
            category=_source_category(source),
        )
        for source, generation in sorted(
            summary.generation_by_source.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )
    visible_comparisons = baseline.comparisons[-MAX_DESKTOP_BASELINE_POINTS:]
    baseline_rows = tuple(_comparison_to_desktop_row(item) for item in visible_comparisons)
    baseline_chart_points = tuple(
        DesktopBaselineChartPoint(
            period=_format_period_label(item.period),
            actual_renewable_share=item.actual_renewable_share,
            predicted_renewable_share=item.predicted_renewable_share,
            method=_comparison_method_label(item),
        )
        for item in visible_comparisons
    )
    return DesktopViewData(
        source=_format_data_source(result),
        period=f"{summary.period_start:%Y-%m-%d %H:%M} -> {summary.period_end:%Y-%m-%d %H:%M}",
        metrics=metrics,
        state_messages=state_messages,
        generation_rows=generation_rows,
        generation_chart_bars=generation_chart_bars,
        alert=f"{result.alert.level}: {result.alert.message}",
        baseline_comparison=_format_baseline_comparison(latest_comparison),
        baseline_rows=baseline_rows,
        baseline_chart_points=baseline_chart_points,
        weather=_format_weather(result),
    )


def build_desktop_error_view_data(message: str) -> DesktopViewData:
    state_message = _input_error_state_message(message)
    alert_level = "erro" if state_message.level == "erro" else "aviso"
    metrics = (
        DesktopMetric("Participacao renovavel", "sem dados"),
        DesktopMetric("Geracao total", "sem dados"),
        DesktopMetric("Geracao renovavel", "sem dados"),
        DesktopMetric("Baseline proxima janela", "sem dados"),
        DesktopMetric("Baseline MAE", "sem dados"),
        DesktopMetric("Comparacoes com clima", "0/0"),
    )
    return DesktopViewData(
        source="-",
        period="-",
        metrics=metrics,
        state_messages=(state_message,),
        generation_rows=(),
        generation_chart_bars=(),
        alert=f"{alert_level}: {message}",
        baseline_comparison="sem dados suficientes",
        baseline_rows=(),
        baseline_chart_points=(),
        weather="-",
    )


def build_desktop_analysis_options(
    *,
    source: str,
    csv_path: str = "",
    ons_period: str = "",
    include_weather: bool = False,
    weather_latitude: str = "",
    weather_longitude: str = "",
    weather_forecast_days: str = "",
) -> DesktopAnalysisOptions:
    weather_options = _parse_weather_options(
        include_weather=include_weather,
        weather_latitude=weather_latitude,
        weather_longitude=weather_longitude,
        weather_forecast_days=weather_forecast_days,
    )
    if source == "csv":
        path = csv_path.strip()
        if not path:
            raise ValueError("Selecione um arquivo CSV.")
        return DesktopAnalysisOptions(source_path=Path(path), **weather_options)

    if source == "ons":
        year, month = parse_ons_period(ons_period)
        return DesktopAnalysisOptions(
            source="ons",
            ons_year=year,
            ons_month=month,
            **weather_options,
        )

    if source == "exemplo":
        return DesktopAnalysisOptions(**weather_options)

    raise ValueError(f"Fonte de dados desconhecida: {source}")


def _parse_weather_options(
    *,
    include_weather: bool,
    weather_latitude: str,
    weather_longitude: str,
    weather_forecast_days: str,
) -> dict[str, float | int | bool]:
    if not include_weather:
        return {"include_weather": False}
    return {
        "include_weather": True,
        "weather_latitude": _parse_optional_float(
            weather_latitude,
            default=DEFAULT_WEATHER_LATITUDE,
            label="latitude climatica",
        ),
        "weather_longitude": _parse_optional_float(
            weather_longitude,
            default=DEFAULT_WEATHER_LONGITUDE,
            label="longitude climatica",
        ),
        "weather_forecast_days": _parse_optional_int(
            weather_forecast_days,
            default=DEFAULT_WEATHER_FORECAST_DAYS,
            label="dias de previsao climatica",
        ),
    }


def _parse_optional_float(value: str, *, default: float, label: str) -> float:
    text = value.strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"Informe um numero valido para {label}.") from exc


def _parse_optional_int(value: str, *, default: int, label: str) -> int:
    text = value.strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"Informe um numero inteiro valido para {label}.") from exc


def format_desktop_status(result: AnalysisResult) -> str:
    if result.cache_path is None:
        return "Analise atualizada"
    if result.cache_hit:
        return f"Analise atualizada; cache reutilizado: {result.cache_path}"
    return f"Analise atualizada; cache: {result.cache_path}"


def _build_state_messages(result: AnalysisResult) -> tuple[DesktopStateMessage, ...]:
    messages: list[DesktopStateMessage] = []
    if result.summary.renewable_share is None or result.summary.total_generation_mw <= 0:
        messages.append(
            DesktopStateMessage(
                level="aviso",
                title="Sem dados uteis",
                detail=(
                    "A geracao total do periodo esta zerada; indicadores percentuais "
                    "ficam indisponiveis."
                ),
            )
        )
    if result.weather_error is not None:
        messages.append(
            DesktopStateMessage(
                level="aviso",
                title="Clima indisponivel",
                detail=result.weather_error,
            )
        )
    if result.baseline.evaluated_points == 0:
        messages.append(
            DesktopStateMessage(
                level="aviso",
                title="Baseline sem pontos suficientes",
                detail=(
                    "Inclua pelo menos dois periodos com participacao renovavel "
                    "para comparar real vs previsto."
                ),
            )
        )
    if result.cache_hit:
        detail = "Registros normalizados foram reutilizados do cache local."
        if result.cache_path is not None:
            detail = f"{detail} Cache: {result.cache_path}"
        messages.append(
            DesktopStateMessage(
                level="info",
                title="Cache reutilizado",
                detail=detail,
            )
        )
    return tuple(messages)


def _input_error_state_message(message: str) -> DesktopStateMessage:
    normalized_message = message.lower()
    if "nao ha registros de geracao" in normalized_message:
        return DesktopStateMessage(
            level="aviso",
            title="Sem dados",
            detail=(
                "A fonte selecionada nao retornou registros de geracao "
                "para analisar."
            ),
        )
    return DesktopStateMessage(
        level="erro",
        title="Erro de entrada",
        detail=message,
    )


def _format_state_messages(messages: tuple[DesktopStateMessage, ...]) -> str:
    if not messages:
        return "Sem avisos"
    return "\n".join(
        f"{message.level.upper()} - {message.title}: {message.detail}"
        for message in messages
    )


class RadarDesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Radar da Transicao Energetica")
        self.root.minsize(980, 760)

        self.source_var = tk.StringVar(value="exemplo")
        self.csv_path_var = tk.StringVar()
        self.ons_period_var = tk.StringVar(value="2026-01")
        self.include_weather_var = tk.BooleanVar(value=False)
        self.weather_latitude_var = tk.StringVar(value=str(DEFAULT_WEATHER_LATITUDE))
        self.weather_longitude_var = tk.StringVar(value=str(DEFAULT_WEATHER_LONGITUDE))
        self.weather_forecast_days_var = tk.StringVar(value=str(DEFAULT_WEATHER_FORECAST_DAYS))
        self.status_var = tk.StringVar(value="Pronto")
        self.source_label_var = tk.StringVar(value="-")
        self.period_var = tk.StringVar(value="-")
        self.alert_var = tk.StringVar(value="-")
        self.baseline_comparison_var = tk.StringVar(value="-")
        self.weather_var = tk.StringVar(value="-")
        self.metric_vars: dict[str, tk.StringVar] = {}
        self.state_text_var = tk.StringVar(value="Sem avisos")
        self.generation_canvas: tk.Canvas | None = None
        self.baseline_canvas: tk.Canvas | None = None
        self.baseline_table: ttk.Treeview | None = None
        self.current_view_data: DesktopViewData | None = None

        self._build_layout()
        self.run_current_analysis()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.root, padding=12)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(5, weight=1)

        ttk.Label(controls, text="Fonte").grid(row=0, column=0, sticky="w")
        for index, (label, value) in enumerate(
            (("Exemplo", "exemplo"), ("CSV", "csv"), ("ONS", "ons")),
            start=1,
        ):
            ttk.Radiobutton(
                controls,
                text=label,
                value=value,
                variable=self.source_var,
                command=self._sync_control_state,
            ).grid(row=0, column=index, padx=(8, 0), sticky="w")

        ttk.Label(controls, text="CSV").grid(row=1, column=0, pady=(8, 0), sticky="w")
        self.csv_entry = ttk.Entry(controls, textvariable=self.csv_path_var)
        self.csv_entry.grid(row=1, column=1, columnspan=4, padx=(8, 0), pady=(8, 0), sticky="ew")
        self.csv_button = ttk.Button(controls, text="Selecionar", command=self._choose_csv)
        self.csv_button.grid(row=1, column=5, padx=(8, 0), pady=(8, 0), sticky="w")

        ttk.Label(controls, text="ONS").grid(row=2, column=0, pady=(8, 0), sticky="w")
        self.ons_entry = ttk.Entry(controls, textvariable=self.ons_period_var, width=12)
        self.ons_entry.grid(row=2, column=1, padx=(8, 0), pady=(8, 0), sticky="w")

        ttk.Checkbutton(
            controls,
            text="Clima Open-Meteo",
            variable=self.include_weather_var,
            command=self._sync_control_state,
        ).grid(row=3, column=0, pady=(8, 0), sticky="w")
        ttk.Label(controls, text="Lat").grid(row=3, column=1, padx=(8, 0), pady=(8, 0), sticky="e")
        self.weather_latitude_entry = ttk.Entry(
            controls,
            textvariable=self.weather_latitude_var,
            width=10,
        )
        self.weather_latitude_entry.grid(row=3, column=2, padx=(4, 0), pady=(8, 0), sticky="w")
        ttk.Label(controls, text="Lon").grid(row=3, column=3, padx=(8, 0), pady=(8, 0), sticky="e")
        self.weather_longitude_entry = ttk.Entry(
            controls,
            textvariable=self.weather_longitude_var,
            width=10,
        )
        self.weather_longitude_entry.grid(row=3, column=4, padx=(4, 0), pady=(8, 0), sticky="w")
        ttk.Label(controls, text="Dias").grid(row=3, column=5, padx=(8, 0), pady=(8, 0), sticky="e")
        self.weather_days_entry = ttk.Entry(
            controls,
            textvariable=self.weather_forecast_days_var,
            width=4,
        )
        self.weather_days_entry.grid(row=3, column=6, padx=(4, 0), pady=(8, 0), sticky="w")
        ttk.Button(controls, text="Executar", command=self.run_current_analysis).grid(
            row=3,
            column=7,
            padx=(8, 0),
            pady=(8, 0),
            sticky="e",
        )

        content = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)
        content.rowconfigure(3, weight=1)

        summary = ttk.LabelFrame(content, text="Resumo", padding=12)
        summary.grid(row=0, column=0, columnspan=2, sticky="ew")
        summary.columnconfigure(1, weight=1)
        ttk.Label(summary, text="Fonte").grid(row=0, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.source_label_var).grid(row=0, column=1, sticky="w")
        ttk.Label(summary, text="Periodo").grid(row=1, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.period_var).grid(row=1, column=1, sticky="w")

        metrics = ttk.Frame(summary)
        metrics.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="ew")
        for index, label in enumerate(
            (
                "Participacao renovavel",
                "Geracao total",
                "Geracao renovavel",
                "Baseline proxima janela",
                "Baseline MAE",
                "Comparacoes com clima",
            )
        ):
            metrics.columnconfigure(index, weight=1)
            self.metric_vars[label] = tk.StringVar(value="-")
            frame = ttk.Frame(metrics, padding=8)
            frame.grid(row=0, column=index, sticky="ew")
            ttk.Label(frame, text=label).grid(row=0, column=0, sticky="w")
            ttk.Label(frame, textvariable=self.metric_vars[label], font=("", 11, "bold")).grid(
                row=1,
                column=0,
                sticky="w",
            )

        states = ttk.LabelFrame(content, text="Estados", padding=12)
        states.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        states.columnconfigure(0, weight=1)
        ttk.Label(
            states,
            textvariable=self.state_text_var,
            wraplength=880,
            justify="left",
        ).grid(row=0, column=0, sticky="ew")

        generation = ttk.LabelFrame(content, text="Geracao por fonte", padding=12)
        generation.grid(row=2, column=0, sticky="nsew", pady=(12, 0), padx=(0, 6))
        generation.rowconfigure(0, weight=1)
        generation.columnconfigure(0, weight=1)
        self.generation_table = ttk.Treeview(
            generation,
            columns=("generation",),
            show="tree headings",
            height=8,
        )
        self.generation_table.heading("#0", text="Fonte")
        self.generation_table.heading("generation", text="Geracao")
        self.generation_table.column("#0", width=180, anchor="w")
        self.generation_table.column("generation", width=160, anchor="e")
        self.generation_table.grid(row=0, column=0, sticky="nsew")
        self.generation_canvas = tk.Canvas(
            generation,
            height=150,
            background="#ffffff",
            highlightthickness=1,
            highlightbackground="#d6d6d6",
        )
        self.generation_canvas.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self.generation_canvas.bind("<Configure>", lambda _event: self._redraw_charts())

        insights = ttk.LabelFrame(content, text="Alerta e baseline", padding=12)
        insights.grid(row=2, column=1, sticky="nsew", pady=(12, 0), padx=(6, 0))
        insights.columnconfigure(0, weight=1)
        ttk.Label(insights, text="Alerta").grid(row=0, column=0, sticky="w")
        ttk.Label(
            insights,
            textvariable=self.alert_var,
            wraplength=390,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(4, 16))
        ttk.Label(insights, text="Comparacao").grid(row=2, column=0, sticky="w")
        ttk.Label(
            insights,
            textvariable=self.baseline_comparison_var,
            wraplength=390,
            justify="left",
        ).grid(row=3, column=0, sticky="ew", pady=(4, 16))
        ttk.Label(insights, text="Clima").grid(row=4, column=0, sticky="w")
        ttk.Label(
            insights,
            textvariable=self.weather_var,
            wraplength=390,
            justify="left",
        ).grid(row=5, column=0, sticky="ew", pady=(4, 0))

        baseline = ttk.LabelFrame(content, text="Real vs previsto", padding=12)
        baseline.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        baseline.columnconfigure(0, weight=1)
        baseline.columnconfigure(1, weight=1)
        baseline.rowconfigure(0, weight=1)
        self.baseline_table = ttk.Treeview(
            baseline,
            columns=("actual", "predicted", "error", "method"),
            show="tree headings",
            height=5,
        )
        self.baseline_table.heading("#0", text="Periodo")
        self.baseline_table.heading("actual", text="Real")
        self.baseline_table.heading("predicted", text="Previsto")
        self.baseline_table.heading("error", text="Erro")
        self.baseline_table.heading("method", text="Metodo")
        self.baseline_table.column("#0", width=150, anchor="w")
        self.baseline_table.column("actual", width=90, anchor="e")
        self.baseline_table.column("predicted", width=90, anchor="e")
        self.baseline_table.column("error", width=90, anchor="e")
        self.baseline_table.column("method", width=110, anchor="w")
        self.baseline_table.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.baseline_canvas = tk.Canvas(
            baseline,
            height=190,
            background="#ffffff",
            highlightthickness=1,
            highlightbackground="#d6d6d6",
        )
        self.baseline_canvas.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.baseline_canvas.bind("<Configure>", lambda _event: self._redraw_charts())

        status = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        status.grid(row=2, column=0, sticky="ew")
        ttk.Label(status, textvariable=self.status_var).grid(row=0, column=0, sticky="w")

        self._sync_control_state()

    def _sync_control_state(self) -> None:
        source = self.source_var.get()
        csv_state = "normal" if source == "csv" else "disabled"
        ons_state = "normal" if source == "ons" else "disabled"
        weather_state = "normal" if self.include_weather_var.get() else "disabled"
        self.csv_entry.configure(state=csv_state)
        self.csv_button.configure(state=csv_state)
        self.ons_entry.configure(state=ons_state)
        self.weather_latitude_entry.configure(state=weather_state)
        self.weather_longitude_entry.configure(state=weather_state)
        self.weather_days_entry.configure(state=weather_state)

    def _choose_csv(self) -> None:
        selected = filedialog.askopenfilename(
            title="Selecionar CSV",
            filetypes=(("CSV", "*.csv"), ("Todos", "*.*")),
        )
        if selected:
            self.csv_path_var.set(selected)

    def run_current_analysis(self) -> None:
        self.status_var.set("Executando analise...")
        self.root.update_idletasks()
        try:
            result = self._run_selected_source()
        except (GenerationDataError, ValueError) as exc:
            self.status_var.set(f"Erro: {exc}")
            self._render_result(build_desktop_error_view_data(str(exc)))
            messagebox.showerror("Erro", str(exc))
            return
        self._render_result(build_desktop_view_data(result))
        self.status_var.set(format_desktop_status(result))

    def _run_selected_source(self) -> AnalysisResult:
        options = build_desktop_analysis_options(
            source=self.source_var.get(),
            csv_path=self.csv_path_var.get(),
            ons_period=self.ons_period_var.get(),
            include_weather=self.include_weather_var.get(),
            weather_latitude=self.weather_latitude_var.get(),
            weather_longitude=self.weather_longitude_var.get(),
            weather_forecast_days=self.weather_forecast_days_var.get(),
        )
        return run_analysis(
            source_path=options.source_path,
            source=options.source,
            ons_year=options.ons_year,
            ons_month=options.ons_month,
            cache_path=DEFAULT_CACHE_PATH,
            include_weather=options.include_weather,
            weather_latitude=options.weather_latitude,
            weather_longitude=options.weather_longitude,
            weather_forecast_days=options.weather_forecast_days,
        )

    def _render_result(self, data: DesktopViewData) -> None:
        self.current_view_data = data
        self.source_label_var.set(data.source)
        self.period_var.set(data.period)
        for metric in data.metrics:
            self.metric_vars[metric.label].set(metric.value)
        self.state_text_var.set(_format_state_messages(data.state_messages))
        self.alert_var.set(data.alert)
        self.baseline_comparison_var.set(data.baseline_comparison)
        self.weather_var.set(data.weather)
        for item in self.generation_table.get_children():
            self.generation_table.delete(item)
        for row in data.generation_rows:
            self.generation_table.insert("", "end", text=row.source, values=(row.generation_mw,))
        if self.baseline_table is not None:
            for item in self.baseline_table.get_children():
                self.baseline_table.delete(item)
            for row in data.baseline_rows:
                self.baseline_table.insert(
                    "",
                    "end",
                    text=row.period,
                    values=(row.actual, row.predicted, row.error, row.method),
                )
        self._redraw_charts()

    def _redraw_charts(self) -> None:
        if self.current_view_data is None:
            return
        if self.generation_canvas is not None:
            _draw_generation_chart(
                self.generation_canvas,
                self.current_view_data.generation_chart_bars,
            )
        if self.baseline_canvas is not None:
            _draw_baseline_chart(
                self.baseline_canvas,
                self.current_view_data.baseline_chart_points,
            )


def main() -> int:
    root = tk.Tk()
    RadarDesktopApp(root)
    root.mainloop()
    return 0


def _format_data_source(result: AnalysisResult) -> str:
    data_source = result.data_source
    if data_source.kind == "ons" and data_source.period:
        return f"{data_source.label} ({data_source.period})"
    if data_source.kind == "arquivo" and data_source.path:
        return f"{data_source.label}: {data_source.path}"
    return data_source.label


def _format_mw(value: float) -> str:
    return f"{value:,.2f} MW"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "sem dados"
    return f"{value:.1%}"


def _format_points(value: float | None) -> str:
    if value is None:
        return "sem dados"
    return f"{value * 100:.1f} p.p."


def _format_baseline_prediction(baseline: BaselinePrediction) -> str:
    text = _format_percent(baseline.predicted_renewable_share)
    if text != "sem dados" and baseline.predicted_with_weather:
        return f"{text} (com clima)"
    return text


def _format_baseline_comparison(comparison: BaselineComparison | None) -> str:
    if comparison is None:
        return "sem dados suficientes"
    return (
        f"real {_format_percent(comparison.actual_renewable_share)} vs "
        f"previsto {_format_percent(comparison.predicted_renewable_share)}; "
        f"erro {_format_points(comparison.absolute_error)}"
        f"{'; com clima' if comparison.weather_adjusted else ''}"
    )


def _comparison_to_desktop_row(comparison: BaselineComparison) -> DesktopBaselineRow:
    return DesktopBaselineRow(
        period=_format_period_label(comparison.period),
        actual=_format_percent(comparison.actual_renewable_share),
        predicted=_format_percent(comparison.predicted_renewable_share),
        error=_format_points(comparison.absolute_error),
        method=_comparison_method_label(comparison),
    )


def _format_period_label(period: str) -> str:
    return period.replace("T", " ")[:16]


def _comparison_method_label(comparison: BaselineComparison) -> str:
    return "clima" if comparison.weather_adjusted else "media movel"


def _source_category(source: str) -> str:
    normalized_source = source.lower()
    if normalized_source in RENEWABLE_SOURCES:
        return "renovavel"
    if normalized_source in NON_RENEWABLE_SOURCES:
        return "nao renovavel"
    return "desconhecida"


def _draw_generation_chart(
    canvas: CanvasLike,
    bars: tuple[DesktopGenerationChartBar, ...],
) -> None:
    canvas.delete("all")
    width = _canvas_size(canvas.winfo_width(), fallback=420)
    height = _canvas_size(canvas.winfo_height(), fallback=150)
    if not bars:
        _draw_empty_canvas(canvas, width, height, "Sem dados de geracao")
        return

    max_generation = max(bar.generation_mw for bar in bars)
    if max_generation <= 0:
        _draw_empty_canvas(canvas, width, height, "Geracao sem valor positivo")
        return

    left = 96
    right = 16
    top = 16
    bottom = 16
    available_height = max(1, height - top - bottom)
    row_height = available_height / len(bars)
    bar_height = max(4.0, min(18.0, row_height * 0.65))
    chart_width = max(40, width - left - right)

    for index, bar in enumerate(bars):
        y = top + index * row_height + row_height / 2
        bar_width = round((bar.generation_mw / max_generation) * chart_width)
        color = _generation_color(bar.category)
        canvas.create_text(8, y, text=bar.source[:13], anchor="w", fill="#263238")
        canvas.create_rectangle(
            left,
            y - bar_height / 2,
            left + bar_width,
            y + bar_height / 2,
            fill=color,
            outline=color,
        )
        canvas.create_text(
            left + min(bar_width + 6, chart_width - 8),
            y,
            text=f"{bar.generation_mw:,.0f}",
            anchor="w",
            fill="#37474f",
        )


def _draw_baseline_chart(
    canvas: CanvasLike,
    points: tuple[DesktopBaselineChartPoint, ...],
) -> None:
    canvas.delete("all")
    width = _canvas_size(canvas.winfo_width(), fallback=420)
    height = _canvas_size(canvas.winfo_height(), fallback=190)
    if not points:
        _draw_empty_canvas(canvas, width, height, "Sem comparacoes de baseline")
        return

    left = 42
    right = 18
    top = 34
    bottom = 34
    plot_width = max(40, width - left - right)
    plot_height = max(40, height - top - bottom)

    canvas.create_line(left, top, left, top + plot_height, fill="#b0bec5")
    canvas.create_line(left, top + plot_height, left + plot_width, top + plot_height, fill="#b0bec5")
    canvas.create_text(left - 8, top, text="100%", anchor="e", fill="#607d8b")
    canvas.create_text(left - 8, top + plot_height, text="0%", anchor="e", fill="#607d8b")
    _draw_baseline_legend(canvas, left, 14)

    actual_coordinates: list[tuple[int, int]] = []
    predicted_coordinates: list[tuple[int, int]] = []
    for index, point in enumerate(points):
        x = _chart_x(index, len(points), left, plot_width)
        actual_y = _share_y(point.actual_renewable_share, top, plot_height)
        predicted_y = _share_y(point.predicted_renewable_share, top, plot_height)
        actual_coordinates.append((x, actual_y))
        predicted_coordinates.append((x, predicted_y))

    _draw_line(canvas, actual_coordinates, color="#2e7d32")
    _draw_line(canvas, predicted_coordinates, color="#546e7a", dash=(4, 3))

    for index, point in enumerate(points):
        x = _chart_x(index, len(points), left, plot_width)
        actual_y = _share_y(point.actual_renewable_share, top, plot_height)
        predicted_y = _share_y(point.predicted_renewable_share, top, plot_height)
        predicted_color = "#ef6c00" if point.method == "clima" else "#1565c0"
        canvas.create_oval(x - 4, actual_y - 4, x + 4, actual_y + 4, fill="#2e7d32", outline="")
        canvas.create_oval(
            x - 4,
            predicted_y - 4,
            x + 4,
            predicted_y + 4,
            fill=predicted_color,
            outline="",
        )
        if len(points) <= 6 or index in (0, len(points) - 1):
            canvas.create_text(
                x,
                top + plot_height + 14,
                text=point.period[-5:],
                anchor="n",
                fill="#607d8b",
            )


def _draw_baseline_legend(canvas: CanvasLike, left: int, y: int) -> None:
    legend_items = (
        ("real", "#2e7d32"),
        ("prev media", "#1565c0"),
        ("prev clima", "#ef6c00"),
    )
    x = left
    for label, color in legend_items:
        canvas.create_oval(x, y - 4, x + 8, y + 4, fill=color, outline="")
        canvas.create_text(x + 14, y, text=label, anchor="w", fill="#37474f")
        x += 92


def _draw_line(
    canvas: CanvasLike,
    coordinates: list[tuple[int, int]],
    *,
    color: str,
    dash: tuple[int, int] | None = None,
) -> None:
    if len(coordinates) < 2:
        return
    flattened = [value for coordinate in coordinates for value in coordinate]
    canvas.create_line(*flattened, fill=color, width=2, dash=dash)


def _chart_x(index: int, total: int, left: int, plot_width: int) -> int:
    if total <= 1:
        return left + plot_width // 2
    return left + round((index / (total - 1)) * plot_width)


def _share_y(value: float, top: int, plot_height: int) -> int:
    clamped = max(0.0, min(1.0, value))
    return top + round((1 - clamped) * plot_height)


def _generation_color(category: str) -> str:
    if category == "renovavel":
        return "#2e7d32"
    if category == "nao renovavel":
        return "#c62828"
    return "#607d8b"


def _canvas_size(value: int, *, fallback: int) -> int:
    return value if value > 10 else fallback


def _draw_empty_canvas(canvas: CanvasLike, width: int, height: int, text: str) -> None:
    canvas.create_text(width // 2, height // 2, text=text, fill="#607d8b")


def _format_weather(result: AnalysisResult) -> str:
    if (
        result.weather_source is None
        and result.weather_summary is None
        and result.weather_error is None
    ):
        return "nao solicitado"
    label = "Open-Meteo" if result.weather_source is None else result.weather_source.label
    if result.weather_error is not None:
        return f"indisponivel ({label}): {result.weather_error}"
    if result.weather_summary is None:
        return f"sem dados ({label})"
    summary = result.weather_summary
    return (
        f"{label}: temperatura media {_format_plain_number(summary.average_temperature_2m_c)} C; "
        f"vento {_format_plain_number(summary.average_wind_speed_10m_kmh)} km/h; "
        f"radiacao {_format_plain_number(summary.average_shortwave_radiation_w_m2)} W/m2; "
        f"nebulosidade {_format_plain_number(summary.average_cloud_cover_percent)}%"
    )


def _format_plain_number(value: float | None) -> str:
    if value is None:
        return "sem dados"
    return f"{value:.1f}"


if __name__ == "__main__":
    raise SystemExit(main())
