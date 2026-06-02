from __future__ import annotations

from dataclasses import dataclass

from radar_transicao_energetica.domain import PeriodRenewableSummary


@dataclass(frozen=True)
class BaselineComparison:
    period: str
    actual_renewable_share: float
    predicted_renewable_share: float
    absolute_error: float


@dataclass(frozen=True)
class BaselinePrediction:
    predicted_renewable_share: float | None
    points_used: int
    method: str
    window: int
    error_metric: str = "mae"
    mean_absolute_error: float | None = None
    evaluated_points: int = 0
    comparisons: tuple[BaselineComparison, ...] = ()


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
    comparisons = evaluate_moving_average_baseline(summaries, window=window)
    mean_absolute_error = _mean_absolute_error(comparisons)
    if not usable_shares:
        return BaselinePrediction(
            predicted_renewable_share=None,
            points_used=0,
            method="media_movel",
            window=window,
            mean_absolute_error=mean_absolute_error,
            evaluated_points=len(comparisons),
            comparisons=tuple(comparisons),
        )

    window_values = usable_shares[-window:]
    return BaselinePrediction(
        predicted_renewable_share=sum(window_values) / len(window_values),
        points_used=len(window_values),
        method="media_movel",
        window=window,
        mean_absolute_error=mean_absolute_error,
        evaluated_points=len(comparisons),
        comparisons=tuple(comparisons),
    )


def evaluate_moving_average_baseline(
    summaries: list[PeriodRenewableSummary],
    window: int = 3,
) -> list[BaselineComparison]:
    if window < 1:
        raise ValueError("A janela do baseline deve ser maior que zero.")

    previous_shares: list[float] = []
    comparisons: list[BaselineComparison] = []
    for summary in summaries:
        actual = summary.renewable_share
        if actual is None:
            continue

        if previous_shares:
            window_values = previous_shares[-window:]
            predicted = sum(window_values) / len(window_values)
            comparisons.append(
                BaselineComparison(
                    period=summary.period.isoformat(),
                    actual_renewable_share=actual,
                    predicted_renewable_share=predicted,
                    absolute_error=abs(actual - predicted),
                )
            )

        previous_shares.append(actual)
    return comparisons


def _mean_absolute_error(comparisons: list[BaselineComparison]) -> float | None:
    if not comparisons:
        return None
    return sum(item.absolute_error for item in comparisons) / len(comparisons)
