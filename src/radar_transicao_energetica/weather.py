from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from collections.abc import Iterable
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_USER_AGENT = "radar-transicao-energetica/0.1"
OPEN_METEO_MAX_DOWNLOAD_BYTES = 5 * 1024 * 1024
DEFAULT_WEATHER_LATITUDE = -15.7939
DEFAULT_WEATHER_LONGITUDE = -47.8828
DEFAULT_WEATHER_FORECAST_DAYS = 2
DEFAULT_WEATHER_TIMEZONE = "America/Sao_Paulo"
OPEN_METEO_HOURLY_VARIABLES = (
    "temperature_2m",
    "wind_speed_10m",
    "shortwave_radiation",
    "cloud_cover",
)


class WeatherDataError(ValueError):
    """Raised when weather data cannot be loaded or normalized."""


@dataclass(frozen=True)
class WeatherRecord:
    period: datetime
    temperature_2m_c: float | None
    wind_speed_10m_kmh: float | None
    shortwave_radiation_w_m2: float | None
    cloud_cover_percent: float | None


@dataclass(frozen=True)
class WeatherSourceMetadata:
    kind: str
    label: str
    latitude: float
    longitude: float
    timezone: str
    forecast_days: int
    resource_url: str


@dataclass(frozen=True)
class WeatherSummary:
    period_start: datetime
    period_end: datetime
    record_count: int
    average_temperature_2m_c: float | None
    average_wind_speed_10m_kmh: float | None
    average_shortwave_radiation_w_m2: float | None
    average_cloud_cover_percent: float | None


def build_open_meteo_url(
    *,
    latitude: float = DEFAULT_WEATHER_LATITUDE,
    longitude: float = DEFAULT_WEATHER_LONGITUDE,
    forecast_days: int = DEFAULT_WEATHER_FORECAST_DAYS,
    timezone: str = DEFAULT_WEATHER_TIMEZONE,
) -> str:
    _validate_coordinates(latitude=latitude, longitude=longitude)
    _validate_forecast_days(forecast_days)
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(OPEN_METEO_HOURLY_VARIABLES),
            "forecast_days": forecast_days,
            "timezone": timezone,
        }
    )
    return f"{OPEN_METEO_FORECAST_URL}?{query}"


def open_meteo_source_metadata(
    *,
    latitude: float = DEFAULT_WEATHER_LATITUDE,
    longitude: float = DEFAULT_WEATHER_LONGITUDE,
    forecast_days: int = DEFAULT_WEATHER_FORECAST_DAYS,
    timezone: str = DEFAULT_WEATHER_TIMEZONE,
) -> WeatherSourceMetadata:
    return WeatherSourceMetadata(
        kind="open-meteo",
        label="Open-Meteo Forecast",
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        forecast_days=forecast_days,
        resource_url=build_open_meteo_url(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            timezone=timezone,
        ),
    )


def load_open_meteo_weather(
    *,
    latitude: float = DEFAULT_WEATHER_LATITUDE,
    longitude: float = DEFAULT_WEATHER_LONGITUDE,
    forecast_days: int = DEFAULT_WEATHER_FORECAST_DAYS,
    timezone: str = DEFAULT_WEATHER_TIMEZONE,
    timeout: float = 30.0,
    max_bytes: int = OPEN_METEO_MAX_DOWNLOAD_BYTES,
    opener: Callable[..., Any] = urlopen,
) -> list[WeatherRecord]:
    url = build_open_meteo_url(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        timezone=timezone,
    )
    request = Request(url, headers={"User-Agent": OPEN_METEO_USER_AGENT})
    try:
        response = opener(request, timeout=timeout)
        try:
            payload = _read_limited_payload(response, max_bytes=max_bytes)
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
    except OSError as exc:
        raise WeatherDataError(f"Nao foi possivel baixar dados climaticos: {exc}") from exc

    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WeatherDataError("Dados climaticos nao estao em JSON UTF-8 valido.") from exc

    return parse_open_meteo_weather(data)


def parse_open_meteo_weather(payload: dict[str, Any]) -> list[WeatherRecord]:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise WeatherDataError("Resposta climatica sem bloco hourly.")

    times = hourly.get("time")
    if not isinstance(times, list) or not times:
        raise WeatherDataError("Resposta climatica sem horarios.")

    variables = {
        "temperature_2m": hourly.get("temperature_2m"),
        "wind_speed_10m": hourly.get("wind_speed_10m"),
        "shortwave_radiation": hourly.get("shortwave_radiation"),
        "cloud_cover": hourly.get("cloud_cover"),
    }
    for name, values in variables.items():
        if values is not None and (not isinstance(values, list) or len(values) != len(times)):
            raise WeatherDataError(f"Variavel climatica invalida ou desalinhada: {name}.")

    records: list[WeatherRecord] = []
    for index, raw_period in enumerate(times):
        if not isinstance(raw_period, str):
            raise WeatherDataError("Horario climatico invalido.")
        records.append(
            WeatherRecord(
                period=_parse_period(raw_period),
                temperature_2m_c=_optional_float(variables["temperature_2m"], index),
                wind_speed_10m_kmh=_optional_float(variables["wind_speed_10m"], index),
                shortwave_radiation_w_m2=_optional_float(
                    variables["shortwave_radiation"], index
                ),
                cloud_cover_percent=_optional_float(variables["cloud_cover"], index),
            )
        )
    return records


def summarize_weather(records: list[WeatherRecord]) -> WeatherSummary | None:
    if not records:
        return None
    periods = [record.period for record in records]
    return WeatherSummary(
        period_start=min(periods),
        period_end=max(periods),
        record_count=len(records),
        average_temperature_2m_c=_average(
            record.temperature_2m_c for record in records
        ),
        average_wind_speed_10m_kmh=_average(
            record.wind_speed_10m_kmh for record in records
        ),
        average_shortwave_radiation_w_m2=_average(
            record.shortwave_radiation_w_m2 for record in records
        ),
        average_cloud_cover_percent=_average(
            record.cloud_cover_percent for record in records
        ),
    )


def _validate_coordinates(*, latitude: float, longitude: float) -> None:
    if latitude < -90 or latitude > 90:
        raise WeatherDataError("Latitude climatica deve estar entre -90 e 90.")
    if longitude < -180 or longitude > 180:
        raise WeatherDataError("Longitude climatica deve estar entre -180 e 180.")


def _validate_forecast_days(value: int) -> None:
    if value < 1 or value > 16:
        raise WeatherDataError("Dias de previsao climatica devem ficar entre 1 e 16.")


def _read_limited_payload(response: Any, *, max_bytes: int) -> bytes:
    if max_bytes < 1:
        raise ValueError("max_bytes deve ser maior que zero.")
    payload = response.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise WeatherDataError("Resposta climatica excede o limite de download da V0.")
    return payload


def _parse_period(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WeatherDataError(f"Horario climatico invalido: {value}") from exc


def _optional_float(values: Any, index: int) -> float | None:
    if values is None:
        return None
    value = values[index]
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise WeatherDataError(f"Valor climatico invalido: {value}") from exc


def _average(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present) / len(present)
