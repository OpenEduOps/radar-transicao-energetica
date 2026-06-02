from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from radar_transicao_energetica.alerts import RenewableAlert, build_renewable_alert
from radar_transicao_energetica.baseline import BaselinePrediction, predict_next_renewable_share
from radar_transicao_energetica.cache import write_analysis_cache
from radar_transicao_energetica.data import (
    DataSourceMetadata,
    GenerationRecord,
    load_generation_csv,
    load_sample_generation,
)
from radar_transicao_energetica.domain import (
    PeriodRenewableSummary,
    RenewableSummary,
    summarize_by_period,
    summarize_generation,
)
from radar_transicao_energetica.ons import load_ons_generation, ons_generation_source_metadata


@dataclass(frozen=True)
class AnalysisResult:
    records: list[GenerationRecord]
    data_source: DataSourceMetadata
    summary: RenewableSummary
    period_summaries: list[PeriodRenewableSummary]
    alert: RenewableAlert
    baseline: BaselinePrediction
    cache_path: Path | None


def run_analysis(
    source_path: str | Path | None = None,
    cache_path: str | Path | None = None,
    write_cache: bool = True,
    source: str = "exemplo",
    ons_year: int | None = None,
    ons_month: int | None = None,
    ons_loader: Callable[[int, int], list[GenerationRecord]] | None = None,
) -> AnalysisResult:
    records, data_source = _load_records(
        source_path=source_path,
        source=source,
        ons_year=ons_year,
        ons_month=ons_month,
        ons_loader=ons_loader,
    )
    summary = summarize_generation(records)
    period_summaries = summarize_by_period(records)
    alert = build_renewable_alert(summary)
    baseline = predict_next_renewable_share(period_summaries)

    written_cache_path = None
    if write_cache and cache_path is not None:
        written_cache_path = write_analysis_cache(
            cache_path,
            records=records,
            summary=summary,
            period_summaries=period_summaries,
            alert=alert,
            baseline=baseline,
            data_source=data_source,
        )

    return AnalysisResult(
        records=records,
        data_source=data_source,
        summary=summary,
        period_summaries=period_summaries,
        alert=alert,
        baseline=baseline,
        cache_path=written_cache_path,
    )


def _load_records(
    *,
    source_path: str | Path | None,
    source: str,
    ons_year: int | None,
    ons_month: int | None,
    ons_loader: Callable[[int, int], list[GenerationRecord]] | None,
) -> tuple[list[GenerationRecord], DataSourceMetadata]:
    if source_path is not None:
        if source != "exemplo":
            raise ValueError("--arquivo nao pode ser combinado com --fonte ons.")
        csv_path = Path(source_path)
        return load_generation_csv(csv_path), DataSourceMetadata(
            kind="arquivo",
            label="CSV local",
            path=str(csv_path),
        )

    if source == "exemplo":
        return load_sample_generation(), DataSourceMetadata(
            kind="exemplo",
            label="Exemplo embutido",
        )

    if source == "ons":
        if ons_year is None or ons_month is None:
            raise ValueError("--ons-periodo e obrigatorio quando --fonte ons.")
        loader = ons_loader or load_ons_generation
        return loader(ons_year, ons_month), ons_generation_source_metadata(ons_year, ons_month)

    raise ValueError(f"Fonte de dados desconhecida: {source}")
