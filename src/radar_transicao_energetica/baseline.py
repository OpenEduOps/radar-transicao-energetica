from __future__ import annotations

from dataclasses import dataclass

from radar_transicao_energetica.domain import PeriodRenewableSummary


@dataclass(frozen=True)
class BaselinePrediction:
    predicted_renewable_share: float | None
    points_used: int
    method: str


def predict_next_renewable_share(
    summaries: list[PeriodRenewableSummary],
    window: int = 3,
) -> BaselinePrediction:
    if window < 1:
        raise ValueError("A janela do baseline deve ser maior que zero.")

    usable_shares = [
        summary.renewable_share
        for summary in summaries
        if summary.renewable_share is not None
    ]
    if not usable_shares:
        return BaselinePrediction(
            predicted_renewable_share=None,
            points_used=0,
            method="media_movel",
        )

    window_values = usable_shares[-window:]
    return BaselinePrediction(
        predicted_renewable_share=sum(window_values) / len(window_values),
        points_used=len(window_values),
        method="media_movel",
    )
