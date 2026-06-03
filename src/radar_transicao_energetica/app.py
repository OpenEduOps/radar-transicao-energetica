from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from radar_transicao_energetica.alerts import RenewableAlert, build_renewable_alert
from radar_transicao_energetica.baseline import BaselinePrediction, predict_next_renewable_share
from radar_transicao_energetica.cache import (
    find_generation_records_by_source_period,
    write_analysis_cache,
)
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
    cache_hit: bool = False


def run_analysis(
    source_path: str | Path | None = None,
    cache_path: str | Path | None = None,
    write_cache: bool = True,
    source: str = "exemplo",
    ons_year: int | None = None,
    ons_month: int | None = None,
    ons_loader: Callable[[int, int], list[GenerationRecord]] | None = None,
    prefer_cache: bool = True,
) -> AnalysisResult:
    records, data_source, cache_hit = _load_records(
        source_path=source_path,
        source=source,
        ons_year=ons_year,
        ons_month=ons_month,
        ons_loader=ons_loader,
        cache_path=cache_path,
        prefer_cache=prefer_cache,
    )
    summary = summarize_generation(records)
    period_summaries = summarize_by_period(records)
    alert = build_renewable_alert(summary)
    baseline = predict_next_renewable_share(period_summaries)

    written_cache_path = None
    if cache_hit:
        written_cache_path = Path(cache_path) if cache_path is not None else None
    elif write_cache and cache_path is not None:
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
        cache_hit=cache_hit,
    )


def _load_records(
    *,
    source_path: str | Path | None,
    source: str,
    ons_year: int | None,
    ons_month: int | None,
    ons_loader: Callable[[int, int], list[GenerationRecord]] | None,
    cache_path: str | Path | None,
    prefer_cache: bool,
) -> tuple[list[GenerationRecord], DataSourceMetadata, bool]:
    if source_path is not None:
        if source != "exemplo":
            raise ValueError("--arquivo nao pode ser combinado com --fonte ons.")
        csv_path = Path(source_path)
        return load_generation_csv(csv_path), DataSourceMetadata(
            kind="arquivo",
            label="CSV local",
            path=str(csv_path),
        ), False

    if source == "exemplo":
        return load_sample_generation(), DataSourceMetadata(
            kind="exemplo",
            label="Exemplo embutido",
        ), False

    if source == "ons":
        if ons_year is None or ons_month is None:
            raise ValueError("--ons-periodo e obrigatorio quando --fonte ons.")
        metadata = ons_generation_source_metadata(ons_year, ons_month)
        if prefer_cache and cache_path is not None and metadata.period is not None:
            cached_records = find_generation_records_by_source_period(
                cache_path,
                source_kind=metadata.kind,
                source_period=metadata.period,
            )
            if cached_records:
                return cached_records, metadata, True
        loader = ons_loader or load_ons_generation
        return loader(ons_year, ons_month), metadata, False

    raise ValueError(f"Fonte de dados desconhecida: {source}")
