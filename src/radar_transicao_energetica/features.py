from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from radar_transicao_energetica.domain import PeriodRenewableSummary
from radar_transicao_energetica.weather import WeatherRecord


WEATHER_FEATURE_NAMES = (
    "temperature_2m_c",
    "wind_speed_10m_kmh",
    "shortwave_radiation_w_m2",
    "cloud_cover_percent",
)

WEATHER_FEATURE_SCALES = {
    "temperature_2m_c": 20.0,
    "wind_speed_10m_kmh": 40.0,
    "shortwave_radiation_w_m2": 1000.0,
    "cloud_cover_percent": 100.0,
}


@dataclass(frozen=True)
class WeatherFeature:
    period: datetime
    temperature_2m_c: float | None
    wind_speed_10m_kmh: float | None
    shortwave_radiation_w_m2: float | None
    cloud_cover_percent: float | None

    @property
    def available_feature_count(self) -> int:
        return sum(1 for value in self.values_by_name().values() if value is not None)

    def values_by_name(self) -> dict[str, float | None]:
        return {
            "temperature_2m_c": self.temperature_2m_c,
            "wind_speed_10m_kmh": self.wind_speed_10m_kmh,
            "shortwave_radiation_w_m2": self.shortwave_radiation_w_m2,
            "cloud_cover_percent": self.cloud_cover_percent,
        }


def build_weather_features_by_period(
    summaries: list[PeriodRenewableSummary],
    weather_records: list[WeatherRecord] | None,
) -> dict[datetime, WeatherFeature]:
    if not weather_records:
        return {}

    summary_periods = {normalize_feature_period(summary.period) for summary in summaries}
    grouped_records: dict[datetime, list[WeatherRecord]] = {}
    for record in weather_records:
        key = normalize_feature_period(record.period)
        if key in summary_periods:
            grouped_records.setdefault(key, []).append(record)

    return {
        period: WeatherFeature(
            period=period,
            temperature_2m_c=_average(record.temperature_2m_c for record in records),
            wind_speed_10m_kmh=_average(record.wind_speed_10m_kmh for record in records),
            shortwave_radiation_w_m2=_average(
                record.shortwave_radiation_w_m2 for record in records
            ),
            cloud_cover_percent=_average(record.cloud_cover_percent for record in records),
        )
        for period, records in grouped_records.items()
    }


def find_next_weather_feature(
    summaries: list[PeriodRenewableSummary],
    weather_records: list[WeatherRecord] | None,
) -> WeatherFeature | None:
    if not summaries or not weather_records:
        return None
    latest_period = max(normalize_feature_period(summary.period) for summary in summaries)
    future_records = [
        record
        for record in weather_records
        if normalize_feature_period(record.period) > latest_period
    ]
    if not future_records:
        return None
    next_period = min(normalize_feature_period(record.period) for record in future_records)
    records = [
        record
        for record in future_records
        if normalize_feature_period(record.period) == next_period
    ]
    return WeatherFeature(
        period=next_period,
        temperature_2m_c=_average(record.temperature_2m_c for record in records),
        wind_speed_10m_kmh=_average(record.wind_speed_10m_kmh for record in records),
        shortwave_radiation_w_m2=_average(
            record.shortwave_radiation_w_m2 for record in records
        ),
        cloud_cover_percent=_average(record.cloud_cover_percent for record in records),
    )


def weather_feature_distance(
    left: WeatherFeature,
    right: WeatherFeature,
) -> float | None:
    distances = []
    left_values = left.values_by_name()
    right_values = right.values_by_name()
    for name in WEATHER_FEATURE_NAMES:
        left_value = left_values[name]
        right_value = right_values[name]
        if left_value is None or right_value is None:
            continue
        distances.append(abs(left_value - right_value) / WEATHER_FEATURE_SCALES[name])
    if not distances:
        return None
    return sum(distances) / len(distances)


def weather_feature_to_dict(feature: WeatherFeature) -> dict[str, float | str | int | None]:
    return {
        "period": feature.period.isoformat(),
        "temperature_2m_c": feature.temperature_2m_c,
        "wind_speed_10m_kmh": feature.wind_speed_10m_kmh,
        "shortwave_radiation_w_m2": feature.shortwave_radiation_w_m2,
        "cloud_cover_percent": feature.cloud_cover_percent,
        "available_feature_count": feature.available_feature_count,
    }


def normalize_feature_period(value: datetime) -> datetime:
    return value.replace(minute=0, second=0, microsecond=0, tzinfo=None)


def _average(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present) / len(present)
