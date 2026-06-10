from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.charts import (
    render_baseline_comparison_chart,
    render_share_trend,
    render_source_chart,
)
from radar_transicao_energetica.data import DataSourceMetadata, GenerationDataError
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary
from radar_transicao_energetica.ons import parse_ons_period
from radar_transicao_energetica.serialization import analysis_payload
from radar_transicao_energetica.weather import (
    DEFAULT_WEATHER_FORECAST_DAYS,
    DEFAULT_WEATHER_LATITUDE,
    DEFAULT_WEATHER_LONGITUDE,
    WeatherSourceMetadata,
    WeatherSummary,
)


DEFAULT_CACHE_PATH = Path("data/cache/analises.sqlite")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        ons_year = None
        ons_month = None
        if args.ons_periodo:
            if args.fonte != "ons":
                raise ValueError("--ons-periodo so pode ser usado com --fonte ons.")
            ons_year, ons_month = parse_ons_period(args.ons_periodo)

        result = run_analysis(
            source_path=args.arquivo,
            cache_path=args.cache,
            write_cache=not args.sem_cache,
            source=args.fonte,
            ons_year=ons_year,
            ons_month=ons_month,
            prefer_cache=not args.sem_cache,
            include_weather=args.clima == "open-meteo",
            weather_latitude=args.clima_latitude,
            weather_longitude=args.clima_longitude,
            weather_forecast_days=args.clima_dias,
            ons_cache_max_age_days=args.ons_cache_max_age_dias,
        )
    except (GenerationDataError, ValueError) as exc:
        parser.exit(status=1, message=f"Erro: {exc}\n")

    if args.json:
        print(
            json.dumps(
                analysis_payload(
                    summary=result.summary,
                    period_summaries=result.period_summaries,
                    alert=result.alert,
                    baseline=result.baseline,
                    cache_path=result.cache_path,
                    data_source=result.data_source,
                    cache_hit=result.cache_hit,
                    weather_source=result.weather_source,
                    weather_summary=result.weather_summary,
                    weather_records=result.weather_records,
                    weather_error=result.weather_error,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(
            render_report(
                result.summary,
                result.period_summaries,
                result.alert.message,
                result.baseline,
                result.data_source,
                result.weather_summary,
                result.weather_source,
                result.weather_error,
            )
        )
        if result.cache_path:
            cache_action = "reutilizado" if result.cache_hit else "gravado"
            print(f"\nCache {cache_action} em: {result.cache_path}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="radar-transicao-energetica",
        description="Analisa participacao renovavel em dados de geracao eletrica.",
    )
    parser.add_argument(
        "--fonte",
        choices=("exemplo", "ons"),
        default="exemplo",
        help="Fonte de dados usada quando --arquivo nao for informado. Padrao: exemplo.",
    )
    parser.add_argument(
        "--ons-periodo",
        help="Periodo mensal da fonte ONS no formato YYYY-MM. Obrigatorio com --fonte ons.",
    )
    parser.add_argument(
        "--arquivo",
        help="CSV com colunas de periodo, fonte e geracao. Se omitido, usa exemplo embutido.",
    )
    parser.add_argument(
        "--cache",
        default=DEFAULT_CACHE_PATH,
        type=Path,
        help=f"Caminho do cache SQLite. Padrao: {DEFAULT_CACHE_PATH}",
    )
    parser.add_argument(
        "--sem-cache",
        action="store_true",
        help="Nao le nem grava cache local da ultima analise.",
    )
    parser.add_argument(
        "--ons-cache-max-age-dias",
        type=int,
        default=None,
        help=(
            "Idade maxima, em dias, para reutilizar registros ONS do cache. "
            "Se omitido, reutiliza o cache existente ate --sem-cache ser usado."
        ),
    )
    parser.add_argument(
        "--clima",
        choices=("nenhum", "open-meteo"),
        default="nenhum",
        help="Integra fonte climatica opcional. Padrao: nenhum.",
    )
    parser.add_argument(
        "--clima-latitude",
        type=float,
        default=DEFAULT_WEATHER_LATITUDE,
        help=f"Latitude usada no Open-Meteo. Padrao: {DEFAULT_WEATHER_LATITUDE}.",
    )
    parser.add_argument(
        "--clima-longitude",
        type=float,
        default=DEFAULT_WEATHER_LONGITUDE,
        help=f"Longitude usada no Open-Meteo. Padrao: {DEFAULT_WEATHER_LONGITUDE}.",
    )
    parser.add_argument(
        "--clima-dias",
        type=int,
        default=DEFAULT_WEATHER_FORECAST_DAYS,
        help=f"Dias de previsao climatica. Padrao: {DEFAULT_WEATHER_FORECAST_DAYS}.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime resultado resumido em JSON.",
    )
    return parser


def render_report(
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert_message: str,
    baseline: BaselinePrediction,
    data_source: DataSourceMetadata | None = None,
    weather_summary: WeatherSummary | None = None,
    weather_source: WeatherSourceMetadata | None = None,
    weather_error: str | None = None,
) -> str:
    share_text = "sem dados" if summary.renewable_share is None else f"{summary.renewable_share:.1%}"
    baseline_text = (
        "sem dados"
        if baseline.predicted_renewable_share is None
        else f"{baseline.predicted_renewable_share:.1%}"
    )
    if baseline.predicted_with_weather and baseline_text != "sem dados":
        baseline_text = f"{baseline_text} (com clima)"
    baseline_error_text = (
        "sem dados"
        if baseline.mean_absolute_error is None
        else f"{baseline.mean_absolute_error * 100:.1f} p.p."
    )
    baseline_rmse_text = (
        "sem dados"
        if baseline.root_mean_squared_error is None
        else f"{baseline.root_mean_squared_error * 100:.1f} p.p."
    )
    lines = [
        "Radar da Transicao Energetica",
        "=" * 31,
        f"Fonte: {_format_data_source(data_source)}",
        f"Periodo: {summary.period_start:%Y-%m-%d %H:%M} -> {summary.period_end:%Y-%m-%d %H:%M}",
        f"Geracao total: {summary.total_generation_mw:,.2f} MW",
        f"Geracao renovavel: {summary.renewable_generation_mw:,.2f} MW",
        f"Participacao renovavel: {share_text}",
        f"Baseline metodo: {baseline.method}",
        f"Baseline proxima janela: {baseline_text}",
        f"Baseline MAE: {baseline_error_text}",
        f"Baseline RMSE: {baseline_rmse_text}",
    ]
    if baseline.weather_adjusted_comparisons:
        lines.append(
            "Comparacoes com features climaticas: "
            f"{baseline.weather_adjusted_comparisons}/{baseline.evaluated_points}"
        )
    weather_lines = _format_weather_lines(
        weather_summary=weather_summary,
        weather_source=weather_source,
        weather_error=weather_error,
    )
    if weather_lines:
        lines.extend(weather_lines)
    latest_comparison = baseline.comparisons[-1] if baseline.comparisons else None
    if latest_comparison is not None:
        lines.append(
            "Ultima comparacao baseline: "
            f"real {latest_comparison.actual_renewable_share:.1%} vs "
            f"previsto {latest_comparison.predicted_renewable_share:.1%}"
            f"{' (com clima)' if latest_comparison.weather_adjusted else ''}"
        )
    if summary.unknown_sources:
        lines.append("Fontes nao classificadas na V0: " + ", ".join(summary.unknown_sources))
    lines.extend(
        [
            "",
            render_source_chart(summary),
            "",
            render_share_trend(period_summaries),
            "",
            render_baseline_comparison_chart(baseline.comparisons),
            "",
            f"Alerta: {alert_message}",
        ]
    )
    return "\n".join(lines)


def _format_data_source(data_source: DataSourceMetadata | None) -> str:
    if data_source is None:
        return "nao informada"
    if data_source.kind == "ons" and data_source.period:
        return f"{data_source.label} ({data_source.period})"
    if data_source.kind == "arquivo" and data_source.path:
        return f"{data_source.label}: {data_source.path}"
    return data_source.label


def _format_weather_lines(
    *,
    weather_summary: WeatherSummary | None,
    weather_source: WeatherSourceMetadata | None,
    weather_error: str | None,
) -> list[str]:
    if weather_source is None and weather_summary is None and weather_error is None:
        return []
    label = "Open-Meteo" if weather_source is None else weather_source.label
    if weather_error is not None:
        return [f"Clima: indisponivel ({label}): {weather_error}"]
    if weather_summary is None:
        return [f"Clima: sem dados ({label})"]
    return [
        (
            "Clima: "
            f"{label} "
            f"({weather_summary.period_start:%Y-%m-%d %H:%M} -> "
            f"{weather_summary.period_end:%Y-%m-%d %H:%M})"
        ),
        f"Temperatura media: {_format_optional_number(weather_summary.average_temperature_2m_c, 'C')}",
        f"Vento medio: {_format_optional_number(weather_summary.average_wind_speed_10m_kmh, 'km/h')}",
        (
            "Radiacao solar media: "
            f"{_format_optional_number(weather_summary.average_shortwave_radiation_w_m2, 'W/m2')}"
        ),
        (
            "Nebulosidade media: "
            f"{_format_optional_number(weather_summary.average_cloud_cover_percent, '%')}"
        ),
    ]


def _format_optional_number(value: float | None, unit: str) -> str:
    if value is None:
        return "sem dados"
    if unit == "%":
        return f"{value:.1f}%"
    return f"{value:.1f} {unit}"
