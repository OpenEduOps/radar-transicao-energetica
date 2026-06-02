from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from radar_transicao_energetica.alerts import build_renewable_alert
from radar_transicao_energetica.baseline import predict_next_renewable_share
from radar_transicao_energetica.cache import write_analysis_cache
from radar_transicao_energetica.charts import render_share_trend, render_source_chart
from radar_transicao_energetica.data import (
    GenerationDataError,
    load_generation_csv,
    load_sample_generation,
)
from radar_transicao_energetica.domain import summarize_by_period, summarize_generation


DEFAULT_CACHE_PATH = Path("data/cache/ultima-analise.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        records = load_generation_csv(args.arquivo) if args.arquivo else load_sample_generation()
        summary = summarize_generation(records)
        period_summaries = summarize_by_period(records)
        alert = build_renewable_alert(summary)
        baseline = predict_next_renewable_share(period_summaries)
    except (GenerationDataError, ValueError) as exc:
        parser.exit(status=2, message=f"Erro: {exc}\n")

    if args.json:
        print(
            json.dumps(
                {
                    "renewable_share": summary.renewable_share,
                    "total_generation_mw": summary.total_generation_mw,
                    "renewable_generation_mw": summary.renewable_generation_mw,
                    "alert": alert.level,
                    "baseline_prediction": baseline.predicted_renewable_share,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_report(summary, period_summaries, alert.message, baseline.predicted_renewable_share))

    if not args.sem_cache:
        cache_path = write_analysis_cache(
            args.cache,
            summary=summary,
            period_summaries=period_summaries,
            alert=alert,
            baseline=baseline,
        )
        if not args.json:
            print(f"\nCache gravado em: {cache_path}")

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
    summary,
    period_summaries,
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
