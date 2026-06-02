from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.charts import render_share_trend, render_source_chart
from radar_transicao_energetica.data import GenerationDataError
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary


DEFAULT_CACHE_PATH = Path("data/cache/ultima-analise.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_analysis(
            source_path=args.arquivo,
            cache_path=args.cache,
            write_cache=not args.sem_cache,
        )
    except (GenerationDataError, ValueError) as exc:
        parser.exit(status=1, message=f"Erro: {exc}\n")

    if args.json:
        print(
            json.dumps(
                {
                    "renewable_share": result.summary.renewable_share,
                    "total_generation_mw": result.summary.total_generation_mw,
                    "renewable_generation_mw": result.summary.renewable_generation_mw,
                    "alert": result.alert.level,
                    "baseline_prediction": result.baseline.predicted_renewable_share,
                },
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
                result.baseline.predicted_renewable_share,
            )
        )
        if result.cache_path:
            print(f"\nCache gravado em: {result.cache_path}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="radar-transicao-energetica",
        description="Analisa participacao renovavel em dados locais de geracao eletrica.",
    )
    parser.add_argument(
        "--arquivo",
        help="CSV com colunas de periodo, fonte e geracao. Se omitido, usa exemplo embutido.",
    )
    parser.add_argument(
        "--cache",
        default=DEFAULT_CACHE_PATH,
        type=Path,
        help=f"Caminho do cache JSON. Padrao: {DEFAULT_CACHE_PATH}",
    )
    parser.add_argument(
        "--sem-cache",
        action="store_true",
        help="Nao grava cache local da ultima analise.",
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
    baseline_prediction: float | None,
) -> str:
    share_text = "sem dados" if summary.renewable_share is None else f"{summary.renewable_share:.1%}"
    baseline_text = (
        "sem dados"
        if baseline_prediction is None
        else f"{baseline_prediction:.1%}"
    )
    lines = [
        "Radar da Transicao Energetica",
        "=" * 31,
        f"Periodo: {summary.period_start:%Y-%m-%d %H:%M} -> {summary.period_end:%Y-%m-%d %H:%M}",
        f"Geracao total: {summary.total_generation_mw:,.2f} MW",
        f"Geracao renovavel: {summary.renewable_generation_mw:,.2f} MW",
        f"Participacao renovavel: {share_text}",
        f"Baseline proxima janela: {baseline_text}",
        "",
        render_source_chart(summary),
        "",
        render_share_trend(period_summaries),
        "",
        f"Alerta: {alert_message}",
    ]
    return "\n".join(lines)
