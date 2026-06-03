from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.charts import render_share_trend, render_source_chart
from radar_transicao_energetica.data import DataSourceMetadata, GenerationDataError
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary
from radar_transicao_energetica.ons import parse_ons_period
from radar_transicao_energetica.serialization import analysis_payload


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
) -> str:
    share_text = "sem dados" if summary.renewable_share is None else f"{summary.renewable_share:.1%}"
    baseline_text = (
        "sem dados"
        if baseline.predicted_renewable_share is None
        else f"{baseline.predicted_renewable_share:.1%}"
    )
    baseline_error_text = (
        "sem dados"
        if baseline.mean_absolute_error is None
        else f"{baseline.mean_absolute_error * 100:.1f} p.p."
    )
    lines = [
        "Radar da Transicao Energetica",
        "=" * 31,
        f"Fonte: {_format_data_source(data_source)}",
        f"Periodo: {summary.period_start:%Y-%m-%d %H:%M} -> {summary.period_end:%Y-%m-%d %H:%M}",
        f"Geracao total: {summary.total_generation_mw:,.2f} MW",
        f"Geracao renovavel: {summary.renewable_generation_mw:,.2f} MW",
        f"Participacao renovavel: {share_text}",
        f"Baseline proxima janela: {baseline_text}",
        f"Baseline MAE: {baseline_error_text}",
    ]
    latest_comparison = baseline.comparisons[-1] if baseline.comparisons else None
    if latest_comparison is not None:
        lines.append(
            "Ultima comparacao baseline: "
            f"real {latest_comparison.actual_renewable_share:.1%} vs "
            f"previsto {latest_comparison.predicted_renewable_share:.1%}"
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
