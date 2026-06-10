from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import sqrt

from radar_transicao_energetica.domain import PeriodRenewableSummary
from radar_transicao_energetica.features import (
    WEATHER_FEATURE_NAMES,
    WeatherFeature,
    build_weather_features_by_period,
    find_next_weather_feature,
    normalize_feature_period,
    weather_feature_distance,
)
from radar_transicao_energetica.weather import WeatherRecord


@dataclass(frozen=True)
class BaselineComparison:
    period: str
    actual_renewable_share: float
    predicted_renewable_share: float
    absolute_error: float
    method: str = "media_movel"
    weather_adjusted: bool = False
    weather_feature_count: int = 0
    weather_distance: float | None = None
    weather_feature: WeatherFeature | None = None


@dataclass(frozen=True)
class BaselinePrediction:
    predicted_renewable_share: float | None
    points_used: int
    method: str
    window: int
    predicted_with_weather: bool = False
    error_metric: str = "mae"
    mean_absolute_error: float | None = None
    root_mean_squared_error: float | None = None
    evaluated_points: int = 0
    comparisons: tuple[BaselineComparison, ...] = ()
    weather_feature_names: tuple[str, ...] = ()
    weather_feature_periods: int = 0
    weather_adjusted_comparisons: int = 0
    next_weather_feature: WeatherFeature | None = None


def predict_next_renewable_share(
    summaries: list[PeriodRenewableSummary],
    window: int = 3,
    weather_records: list[WeatherRecord] | None = None,
) -> BaselinePrediction:
    if window < 1:
        raise ValueError("A janela do baseline deve ser maior que zero.")

    usable_shares = [
        summary.renewable_share
        for summary in summaries
        if summary.renewable_share is not None
    ]
    weather_features = build_weather_features_by_period(summaries, weather_records)
    next_weather_feature = find_next_weather_feature(summaries, weather_records)
    comparisons = evaluate_weather_aware_baseline(
        summaries,
        weather_records=weather_records,
        window=window,
    )
    mean_absolute_error = _mean_absolute_error(comparisons)
    root_mean_squared_error = _root_mean_squared_error(comparisons)
    weather_adjusted_comparisons = sum(1 for item in comparisons if item.weather_adjusted)
    method = (
        "media_movel_com_features_climaticas"
        if weather_adjusted_comparisons > 0
        else "media_movel"
    )
    weather_feature_names = _weather_feature_names_used(weather_features)
    if not usable_shares:
        return BaselinePrediction(
            predicted_renewable_share=None,
            points_used=0,
            method=method,
            window=window,
            mean_absolute_error=mean_absolute_error,
            root_mean_squared_error=root_mean_squared_error,
            evaluated_points=len(comparisons),
            comparisons=tuple(comparisons),
            weather_feature_names=weather_feature_names,
            weather_feature_periods=len(weather_features),
            weather_adjusted_comparisons=weather_adjusted_comparisons,
            next_weather_feature=next_weather_feature,
        )

    window_values = usable_shares[-window:]
    predicted_share = sum(window_values) / len(window_values)
    points_used = len(window_values)
    weather_prediction = _predict_next_with_weather_features(
        summaries=summaries,
        next_weather_feature=next_weather_feature,
        window=window,
        weather_features=weather_features,
    )
    predicted_with_weather = False
    if weather_prediction is not None:
        predicted_share, points_used = weather_prediction
        method = "media_movel_com_features_climaticas"
        predicted_with_weather = True

    return BaselinePrediction(
        predicted_renewable_share=predicted_share,
        points_used=points_used,
        method=method,
        window=window,
        predicted_with_weather=predicted_with_weather,
        mean_absolute_error=mean_absolute_error,
        root_mean_squared_error=root_mean_squared_error,
        evaluated_points=len(comparisons),
        comparisons=tuple(comparisons),
        weather_feature_names=weather_feature_names,
        weather_feature_periods=len(weather_features),
        weather_adjusted_comparisons=weather_adjusted_comparisons,
        next_weather_feature=next_weather_feature,
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


def evaluate_weather_aware_baseline(
    summaries: list[PeriodRenewableSummary],
    weather_records: list[WeatherRecord] | None,
    window: int = 3,
) -> list[BaselineComparison]:
    if window < 1:
        raise ValueError("A janela do baseline deve ser maior que zero.")
    weather_features = build_weather_features_by_period(summaries, weather_records)
    if not weather_features:
        return evaluate_moving_average_baseline(summaries, window=window)

    previous_shares: list[float] = []
    previous_featured_periods: list[tuple[float, WeatherFeature]] = []
    comparisons: list[BaselineComparison] = []
    for summary in summaries:
        actual = summary.renewable_share
        if actual is None:
            continue

        feature = weather_features.get(normalize_feature_period(summary.period))
        weather_prediction = _predict_from_weather_analogues(
            previous_featured_periods,
            feature,
            window=window,
        )
        if weather_prediction is not None:
            predicted, _points_used, distance = weather_prediction
            comparisons.append(
                BaselineComparison(
                    period=summary.period.isoformat(),
                    actual_renewable_share=actual,
                    predicted_renewable_share=predicted,
                    absolute_error=abs(actual - predicted),
                    method="media_movel_com_features_climaticas",
                    weather_adjusted=True,
                    weather_feature_count=feature.available_feature_count
                    if feature is not None
                    else 0,
                    weather_distance=distance,
                    weather_feature=feature,
                )
            )
        elif previous_shares:
            window_values = previous_shares[-window:]
            predicted = sum(window_values) / len(window_values)
            comparisons.append(
                BaselineComparison(
                    period=summary.period.isoformat(),
                    actual_renewable_share=actual,
                    predicted_renewable_share=predicted,
                    absolute_error=abs(actual - predicted),
                    weather_feature_count=feature.available_feature_count
                    if feature is not None
                    else 0,
                    weather_feature=feature,
                )
            )

        previous_shares.append(actual)
        if feature is not None and feature.available_feature_count > 0:
            previous_featured_periods.append((actual, feature))
    return comparisons


def _predict_next_with_weather_features(
    *,
    summaries: list[PeriodRenewableSummary],
    next_weather_feature: WeatherFeature | None,
    window: int,
    weather_features: dict[datetime, WeatherFeature],
) -> tuple[float, int] | None:
    history: list[tuple[float, WeatherFeature]] = []
    for summary in summaries:
        actual = summary.renewable_share
        feature = weather_features.get(normalize_feature_period(summary.period))
        if actual is not None and feature is not None and feature.available_feature_count > 0:
            history.append((actual, feature))
    prediction = _predict_from_weather_analogues(
        history,
        next_weather_feature,
        window=window,
    )
    if prediction is None:
        return None
    predicted_share, points_used, _distance = prediction
    return predicted_share, points_used


def _predict_from_weather_analogues(
    history: list[tuple[float, WeatherFeature]],
    target_feature: WeatherFeature | None,
    *,
    window: int,
) -> tuple[float, int, float] | None:
    if target_feature is None or target_feature.available_feature_count == 0:
        return None
    candidates = []
    for renewable_share, feature in history:
        distance = weather_feature_distance(target_feature, feature)
        if distance is not None:
            candidates.append((distance, renewable_share))
    if not candidates:
        return None
    selected = sorted(candidates, key=lambda item: item[0])[:window]
    predicted_share = sum(share for _distance, share in selected) / len(selected)
    average_distance = sum(distance for distance, _share in selected) / len(selected)
    return predicted_share, len(selected), average_distance


def _weather_feature_names_used(
    weather_features: dict[datetime, WeatherFeature],
) -> tuple[str, ...]:
    if not weather_features:
        return ()
    return tuple(
        name
        for name in WEATHER_FEATURE_NAMES
        if any(feature.values_by_name()[name] is not None for feature in weather_features.values())
    )


def _mean_absolute_error(comparisons: list[BaselineComparison]) -> float | None:
    if not comparisons:
        return None
    return sum(item.absolute_error for item in comparisons) / len(comparisons)


def _root_mean_squared_error(comparisons: list[BaselineComparison]) -> float | None:
    if not comparisons:
        return None
    mean_squared_error = sum(item.absolute_error**2 for item in comparisons) / len(comparisons)
    return sqrt(mean_squared_error)
