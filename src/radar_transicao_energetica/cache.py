from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from radar_transicao_energetica.alerts import RenewableAlert
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary


def write_analysis_cache(
    path: str | Path,
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert: RenewableAlert,
    baseline: BaselinePrediction,
) -> Path:
    cache_path = Path(path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {
                "summary": _summary_to_dict(summary),
                "period_summaries": [_period_summary_to_dict(item) for item in period_summaries],
                "alert": {
                    "level": alert.level,
                    "message": alert.message,
                },
                "baseline": {
                    "method": baseline.method,
                    "points_used": baseline.points_used,
                    "predicted_renewable_share": baseline.predicted_renewable_share,
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return cache_path


def _summary_to_dict(summary: RenewableSummary) -> dict[str, Any]:
    return {
        "period_start": summary.period_start.isoformat(),
        "period_end": summary.period_end.isoformat(),
        "total_generation_mw": summary.total_generation_mw,
        "renewable_generation_mw": summary.renewable_generation_mw,
        "renewable_share": summary.renewable_share,
        "generation_by_source": summary.generation_by_source,
    }


def _period_summary_to_dict(summary: PeriodRenewableSummary) -> dict[str, Any]:
    return {
        "period": summary.period.isoformat(),
        "total_generation_mw": summary.total_generation_mw,
        "renewable_generation_mw": summary.renewable_generation_mw,
        "renewable_share": summary.renewable_share,
    }
