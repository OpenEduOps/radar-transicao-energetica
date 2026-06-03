from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from radar_transicao_energetica.app import AnalysisResult, run_analysis
from radar_transicao_energetica.baseline import BaselineComparison
from radar_transicao_energetica.cli import DEFAULT_CACHE_PATH
from radar_transicao_energetica.data import GenerationDataError
from radar_transicao_energetica.ons import parse_ons_period


@dataclass(frozen=True)
class DesktopAnalysisOptions:
    source_path: Path | None = None
    source: str = "exemplo"
    ons_year: int | None = None
    ons_month: int | None = None


@dataclass(frozen=True)
class DesktopMetric:
    label: str
    value: str


@dataclass(frozen=True)
class DesktopGenerationRow:
    source: str
    generation_mw: str


@dataclass(frozen=True)
class DesktopViewData:
    source: str
    period: str
    metrics: tuple[DesktopMetric, ...]
    generation_rows: tuple[DesktopGenerationRow, ...]
    alert: str
    baseline_comparison: str


def build_desktop_view_data(result: AnalysisResult) -> DesktopViewData:
    summary = result.summary
    baseline = result.baseline
    latest_comparison = baseline.comparisons[-1] if baseline.comparisons else None

    metrics = (
        DesktopMetric("Participacao renovavel", _format_percent(summary.renewable_share)),
        DesktopMetric("Geracao total", _format_mw(summary.total_generation_mw)),
        DesktopMetric("Geracao renovavel", _format_mw(summary.renewable_generation_mw)),
        DesktopMetric("Baseline proxima janela", _format_percent(baseline.predicted_renewable_share)),
        DesktopMetric("Baseline MAE", _format_points(baseline.mean_absolute_error)),
    )
    generation_rows = tuple(
        DesktopGenerationRow(source=source, generation_mw=_format_mw(generation))
        for source, generation in sorted(summary.generation_by_source.items())
    )
    return DesktopViewData(
        source=_format_data_source(result),
        period=f"{summary.period_start:%Y-%m-%d %H:%M} -> {summary.period_end:%Y-%m-%d %H:%M}",
        metrics=metrics,
        generation_rows=generation_rows,
        alert=f"{result.alert.level}: {result.alert.message}",
        baseline_comparison=_format_baseline_comparison(latest_comparison),
    )


def build_desktop_analysis_options(
    *,
    source: str,
    csv_path: str = "",
    ons_period: str = "",
) -> DesktopAnalysisOptions:
    if source == "csv":
        path = csv_path.strip()
        if not path:
            raise ValueError("Selecione um arquivo CSV.")
        return DesktopAnalysisOptions(source_path=Path(path))

    if source == "ons":
        year, month = parse_ons_period(ons_period)
        return DesktopAnalysisOptions(source="ons", ons_year=year, ons_month=month)

    if source == "exemplo":
        return DesktopAnalysisOptions()

    raise ValueError(f"Fonte de dados desconhecida: {source}")


def format_desktop_status(result: AnalysisResult) -> str:
    if result.cache_path is None:
        return "Analise atualizada"
    if result.cache_hit:
        return f"Analise atualizada; cache reutilizado: {result.cache_path}"
    return f"Analise atualizada; cache: {result.cache_path}"


class RadarDesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Radar da Transicao Energetica")
        self.root.minsize(900, 620)

        self.source_var = tk.StringVar(value="exemplo")
        self.csv_path_var = tk.StringVar()
        self.ons_period_var = tk.StringVar(value="2026-01")
        self.status_var = tk.StringVar(value="Pronto")
        self.source_label_var = tk.StringVar(value="-")
        self.period_var = tk.StringVar(value="-")
        self.alert_var = tk.StringVar(value="-")
        self.baseline_comparison_var = tk.StringVar(value="-")
        self.metric_vars: dict[str, tk.StringVar] = {}

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
        ttk.Button(controls, text="Executar", command=self.run_current_analysis).grid(
            row=2,
            column=5,
            padx=(8, 0),
            pady=(8, 0),
            sticky="e",
        )

        content = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(1, weight=1)

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

        generation = ttk.LabelFrame(content, text="Geracao por fonte", padding=12)
        generation.grid(row=1, column=0, sticky="nsew", pady=(12, 0), padx=(0, 6))
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

        insights = ttk.LabelFrame(content, text="Alerta e baseline", padding=12)
        insights.grid(row=1, column=1, sticky="nsew", pady=(12, 0), padx=(6, 0))
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
        ).grid(row=3, column=0, sticky="ew", pady=(4, 0))

        status = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        status.grid(row=2, column=0, sticky="ew")
        ttk.Label(status, textvariable=self.status_var).grid(row=0, column=0, sticky="w")

        self._sync_control_state()

    def _sync_control_state(self) -> None:
        source = self.source_var.get()
        csv_state = "normal" if source == "csv" else "disabled"
        ons_state = "normal" if source == "ons" else "disabled"
        self.csv_entry.configure(state=csv_state)
        self.csv_button.configure(state=csv_state)
        self.ons_entry.configure(state=ons_state)

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
            messagebox.showerror("Erro", str(exc))
            return
        self._render_result(build_desktop_view_data(result))
        self.status_var.set(format_desktop_status(result))

    def _run_selected_source(self) -> AnalysisResult:
        options = build_desktop_analysis_options(
            source=self.source_var.get(),
            csv_path=self.csv_path_var.get(),
            ons_period=self.ons_period_var.get(),
        )
        return run_analysis(
            source_path=options.source_path,
            source=options.source,
            ons_year=options.ons_year,
            ons_month=options.ons_month,
            cache_path=DEFAULT_CACHE_PATH,
        )

    def _render_result(self, data: DesktopViewData) -> None:
        self.source_label_var.set(data.source)
        self.period_var.set(data.period)
        for metric in data.metrics:
            self.metric_vars[metric.label].set(metric.value)
        self.alert_var.set(data.alert)
        self.baseline_comparison_var.set(data.baseline_comparison)
        for item in self.generation_table.get_children():
            self.generation_table.delete(item)
        for row in data.generation_rows:
            self.generation_table.insert("", "end", text=row.source, values=(row.generation_mw,))


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


def _format_baseline_comparison(comparison: BaselineComparison | None) -> str:
    if comparison is None:
        return "sem dados suficientes"
    return (
        f"real {_format_percent(comparison.actual_renewable_share)} vs "
        f"previsto {_format_percent(comparison.predicted_renewable_share)}; "
        f"erro {_format_points(comparison.absolute_error)}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
