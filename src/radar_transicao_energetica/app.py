from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from radar_transicao_energetica.alerts import RenewableAlert, build_renewable_alert
from radar_transicao_energetica.baseline import BaselinePrediction, predict_next_renewable_share
from radar_transicao_energetica.cache import write_analysis_cache
from radar_transicao_energetica.data import GenerationRecord, load_generation_csv, load_sample_generation
from radar_transicao_energetica.domain import (
    PeriodRenewableSummary,
    RenewableSummary,
    summarize_by_period,
    summarize_generation,
)


@dataclass(frozen=True)
class AnalysisResult:
    records: list[GenerationRecord]
    summary: RenewableSummary
    period_summaries: list[PeriodRenewableSummary]
    alert: RenewableAlert
    baseline: BaselinePrediction
    cache_path: Path | None


def run_analysis(
    source_path: str | Path | None = None,
    cache_path: str | Path | None = None,
    write_cache: bool = True,
) -> AnalysisResult:
    records = load_generation_csv(source_path) if source_path else load_sample_generation()
    summary = summarize_generation(records)
    period_summaries = summarize_by_period(records)
    alert = build_renewable_alert(summary)
    baseline = predict_next_renewable_share(period_summaries)

    written_cache_path = None
    if write_cache and cache_path is not None:
        written_cache_path = write_analysis_cache(
            cache_path,
            summary=summary,
            period_summaries=period_summaries,
            alert=alert,
            baseline=baseline,
        )

    return AnalysisResult(
        records=records,
        summary=summary,
        period_summaries=period_summaries,
        alert=alert,
        baseline=baseline,
        cache_path=written_cache_path,
    )
