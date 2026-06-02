from __future__ import annotations

import json
from pathlib import Path

from radar_transicao_energetica.alerts import RenewableAlert
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary
from radar_transicao_energetica.serialization import analysis_payload


class AnalysisCacheError(ValueError):
    """Raised when the local analysis cache cannot be written."""


def write_analysis_cache(
    path: str | Path,
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert: RenewableAlert,
    baseline: BaselinePrediction,
) -> Path:
    cache_path = Path(path)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(
                analysis_payload(
                    summary=summary,
                    period_summaries=period_summaries,
                    alert=alert,
                    baseline=baseline,
                ),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError as exc:
        raise AnalysisCacheError(f"Nao foi possivel gravar o cache em {cache_path}: {exc}") from exc
    return cache_path
