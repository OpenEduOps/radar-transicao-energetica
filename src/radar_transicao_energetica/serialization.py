from __future__ import annotations

from pathlib import Path
from typing import Any

from radar_transicao_energetica.alerts import RenewableAlert
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary


def analysis_payload(
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert: RenewableAlert,
    baseline: BaselinePrediction,
    cache_path: str | Path | None = None,
) -> dict[str, Any]:
    payload = {
        "summary": summary_to_dict(summary),
        "period_summaries": [period_summary_to_dict(item) for item in period_summaries],
        "alert": alert_to_dict(alert),
        "baseline": baseline_to_dict(baseline),
    }
    if cache_path is not None:
        payload["cache_path"] = str(cache_path)
    return payload


def summary_to_dict(summary: RenewableSummary) -> dict[str, Any]:
    return {
        "period_start": summary.period_start.isoformat(),
        "period_end": summary.period_end.isoformat(),
        "total_generation_mw": summary.total_generation_mw,
        "renewable_generation_mw": summary.renewable_generation_mw,
        "renewable_share": summary.renewable_share,
        "generation_by_source": summary.generation_by_source,
    }


def period_summary_to_dict(summary: PeriodRenewableSummary) -> dict[str, Any]:
    return {
        "period": summary.period.isoformat(),
        "total_generation_mw": summary.total_generation_mw,
        "renewable_generation_mw": summary.renewable_generation_mw,
        "renewable_share": summary.renewable_share,
    }


def alert_to_dict(alert: RenewableAlert) -> dict[str, str]:
    return {
        "level": alert.level,
        "message": alert.message,
    }


def baseline_to_dict(baseline: BaselinePrediction) -> dict[str, float | int | str | None]:
    return {
        "method": baseline.method,
        "points_used": baseline.points_used,
        "predicted_renewable_share": baseline.predicted_renewable_share,
    }
