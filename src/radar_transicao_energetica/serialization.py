from __future__ import annotations

from pathlib import Path
from typing import Any

from radar_transicao_energetica.alerts import RenewableAlert
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.data import DataSourceMetadata
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary


def analysis_payload(
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert: RenewableAlert,
    baseline: BaselinePrediction,
    cache_path: str | Path | None = None,
    data_source: DataSourceMetadata | None = None,
) -> dict[str, Any]:
    payload = {
        "summary": summary_to_dict(summary),
        "period_summaries": [period_summary_to_dict(item) for item in period_summaries],
        "alert": alert_to_dict(alert),
        "baseline": baseline_to_dict(baseline),
    }
    if data_source is not None:
        payload["data_source"] = data_source_to_dict(data_source)
    if cache_path is not None:
        payload["cache_path"] = str(cache_path)
    return payload


def data_source_to_dict(data_source: DataSourceMetadata) -> dict[str, str]:
    payload = {
        "kind": data_source.kind,
        "label": data_source.label,
    }
    optional_fields = {
        "period": data_source.period,
        "path": data_source.path,
        "dataset_url": data_source.dataset_url,
        "resource_url": data_source.resource_url,
    }
    for key, value in optional_fields.items():
        if value is not None:
            payload[key] = value
    return payload


def summary_to_dict(summary: RenewableSummary) -> dict[str, Any]:
    return {
        "period_start": summary.period_start.isoformat(),
        "period_end": summary.period_end.isoformat(),
        "total_generation_mw": summary.total_generation_mw,
        "renewable_generation_mw": summary.renewable_generation_mw,
        "renewable_share": summary.renewable_share,
        "generation_by_source": summary.generation_by_source,
        "unknown_sources": list(summary.unknown_sources),
    }


def period_summary_to_dict(summary: PeriodRenewableSummary) -> dict[str, Any]:
    return {
        "period": summary.period.isoformat(),
        "total_generation_mw": summary.total_generation_mw,
        "renewable_generation_mw": summary.renewable_generation_mw,
        "renewable_share": summary.renewable_share,
        "unknown_sources": list(summary.unknown_sources),
    }


def alert_to_dict(alert: RenewableAlert) -> dict[str, str]:
    return {
        "level": alert.level,
        "message": alert.message,
    }


def baseline_to_dict(baseline: BaselinePrediction) -> dict[str, Any]:
    return {
        "method": baseline.method,
        "points_used": baseline.points_used,
        "window": baseline.window,
        "predicted_renewable_share": baseline.predicted_renewable_share,
        "error_metric": baseline.error_metric,
        "mean_absolute_error": baseline.mean_absolute_error,
        "evaluated_points": baseline.evaluated_points,
        "comparisons": [
            {
                "period": item.period,
                "actual_renewable_share": item.actual_renewable_share,
                "predicted_renewable_share": item.predicted_renewable_share,
                "absolute_error": item.absolute_error,
            }
            for item in baseline.comparisons
        ],
    }
