from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from radar_transicao_energetica.data import GenerationRecord


RENEWABLE_SOURCES = frozenset({"hidraulica", "eolica", "solar"})


@dataclass(frozen=True)
class RenewableSummary:
    period_start: datetime
    period_end: datetime
    total_generation_mw: float
    renewable_generation_mw: float
    renewable_share: float | None
    generation_by_source: dict[str, float]


@dataclass(frozen=True)
class PeriodRenewableSummary:
    period: datetime
    total_generation_mw: float
    renewable_generation_mw: float
    renewable_share: float | None


def summarize_generation(records: list[GenerationRecord]) -> RenewableSummary:
    if not records:
        raise ValueError("Nao ha registros de geracao para analisar.")

    generation_by_source: dict[str, float] = defaultdict(float)
    for record in records:
        generation_by_source[record.source] += record.generation_mw

    total_generation_mw = sum(generation_by_source.values())
    renewable_generation_mw = sum(
        generation
        for source, generation in generation_by_source.items()
        if source in RENEWABLE_SOURCES
    )
    renewable_share = (
        renewable_generation_mw / total_generation_mw if total_generation_mw > 0 else None
    )

    periods = [record.period for record in records]
    return RenewableSummary(
        period_start=min(periods),
        period_end=max(periods),
        total_generation_mw=total_generation_mw,
        renewable_generation_mw=renewable_generation_mw,
        renewable_share=renewable_share,
        generation_by_source=dict(sorted(generation_by_source.items())),
    )


def summarize_by_period(records: list[GenerationRecord]) -> list[PeriodRenewableSummary]:
    records_by_period: dict[datetime, list[GenerationRecord]] = defaultdict(list)
    for record in records:
        records_by_period[record.period].append(record)

    summaries: list[PeriodRenewableSummary] = []
    for period, period_records in sorted(records_by_period.items()):
        summary = summarize_generation(period_records)
        summaries.append(
            PeriodRenewableSummary(
                period=period,
                total_generation_mw=summary.total_generation_mw,
                renewable_generation_mw=summary.renewable_generation_mw,
                renewable_share=summary.renewable_share,
            )
        )
    return summaries
