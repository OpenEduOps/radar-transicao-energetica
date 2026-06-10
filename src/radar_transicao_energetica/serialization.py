from __future__ import annotations

from pathlib import Path
from typing import Any

from radar_transicao_energetica.alerts import RenewableAlert
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.data import DataSourceMetadata
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary
from radar_transicao_energetica.features import weather_feature_to_dict
from radar_transicao_energetica.weather import (
    WeatherRecord,
    WeatherSourceMetadata,
    WeatherSummary,
)


def analysis_payload(
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert: RenewableAlert,
    baseline: BaselinePrediction,
    cache_path: str | Path | None = None,
    data_source: DataSourceMetadata | None = None,
    cache_hit: bool = False,
    weather_source: WeatherSourceMetadata | None = None,
    weather_summary: WeatherSummary | None = None,
    weather_records: list[WeatherRecord] | None = None,
    weather_error: str | None = None,
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
    payload["cache_hit"] = cache_hit
    if _has_weather_payload(
        weather_source=weather_source,
        weather_summary=weather_summary,
        weather_records=weather_records,
        weather_error=weather_error,
    ):
        payload["weather"] = weather_to_dict(
            weather_source=weather_source,
            weather_summary=weather_summary,
            weather_records=weather_records or [],
            weather_error=weather_error,
        )
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


def weather_to_dict(
    *,
    weather_source: WeatherSourceMetadata | None,
    weather_summary: WeatherSummary | None,
    weather_records: list[WeatherRecord],
    weather_error: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "summary": weather_summary_to_dict(weather_summary)
        if weather_summary is not None
        else None,
        "records": [weather_record_to_dict(record) for record in weather_records],
    }
    if weather_source is not None:
        payload["data_source"] = weather_source_to_dict(weather_source)
    if weather_error is not None:
        payload["error"] = weather_error
    return payload


def weather_source_to_dict(source: WeatherSourceMetadata) -> dict[str, Any]:
    return {
        "kind": source.kind,
        "label": source.label,
        "latitude": source.latitude,
        "longitude": source.longitude,
        "timezone": source.timezone,
        "forecast_days": source.forecast_days,
        "resource_url": source.resource_url,
    }


def weather_summary_to_dict(summary: WeatherSummary) -> dict[str, Any]:
    return {
        "period_start": summary.period_start.isoformat(),
        "period_end": summary.period_end.isoformat(),
        "record_count": summary.record_count,
        "average_temperature_2m_c": summary.average_temperature_2m_c,
        "average_wind_speed_10m_kmh": summary.average_wind_speed_10m_kmh,
        "average_shortwave_radiation_w_m2": summary.average_shortwave_radiation_w_m2,
        "average_cloud_cover_percent": summary.average_cloud_cover_percent,
    }


def weather_record_to_dict(record: WeatherRecord) -> dict[str, Any]:
    return {
        "period": record.period.isoformat(),
        "temperature_2m_c": record.temperature_2m_c,
        "wind_speed_10m_kmh": record.wind_speed_10m_kmh,
        "shortwave_radiation_w_m2": record.shortwave_radiation_w_m2,
        "cloud_cover_percent": record.cloud_cover_percent,
    }


def _has_weather_payload(
    *,
    weather_source: WeatherSourceMetadata | None,
    weather_summary: WeatherSummary | None,
    weather_records: list[WeatherRecord] | None,
    weather_error: str | None,
) -> bool:
    return (
        weather_source is not None
        or weather_summary is not None
        or bool(weather_records)
        or weather_error is not None
    )


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
        "predicted_with_weather": baseline.predicted_with_weather,
        "error_metric": baseline.error_metric,
        "mean_absolute_error": baseline.mean_absolute_error,
        "root_mean_squared_error": baseline.root_mean_squared_error,
        "evaluated_points": baseline.evaluated_points,
        "weather_feature_names": list(baseline.weather_feature_names),
        "weather_feature_periods": baseline.weather_feature_periods,
        "weather_adjusted_comparisons": baseline.weather_adjusted_comparisons,
        "next_weather_feature": weather_feature_to_dict(baseline.next_weather_feature)
        if baseline.next_weather_feature is not None
        else None,
        "comparisons": [
            {
                "period": item.period,
                "actual_renewable_share": item.actual_renewable_share,
                "predicted_renewable_share": item.predicted_renewable_share,
                "absolute_error": item.absolute_error,
                "method": item.method,
                "weather_adjusted": item.weather_adjusted,
                "weather_feature_count": item.weather_feature_count,
                "weather_distance": item.weather_distance,
                "weather_feature": weather_feature_to_dict(item.weather_feature)
                if item.weather_feature is not None
                else None,
            }
            for item in baseline.comparisons
        ],
    }
