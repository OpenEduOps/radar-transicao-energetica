from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from radar_transicao_energetica.alerts import RenewableAlert, build_renewable_alert
from radar_transicao_energetica.baseline import BaselinePrediction, predict_next_renewable_share
from radar_transicao_energetica.cache import (
    find_generation_records_by_source_period,
    write_analysis_cache,
)
from radar_transicao_energetica.data import (
    DataSourceMetadata,
    GenerationRecord,
    load_generation_csv,
    load_sample_generation,
)
from radar_transicao_energetica.domain import (
    PeriodRenewableSummary,
    RenewableSummary,
    summarize_by_period,
    summarize_generation,
)
from radar_transicao_energetica.ons import load_ons_generation, ons_generation_source_metadata
from radar_transicao_energetica.weather import (
    DEFAULT_WEATHER_FORECAST_DAYS,
    DEFAULT_WEATHER_LATITUDE,
    DEFAULT_WEATHER_LONGITUDE,
    WeatherDataError,
    WeatherRecord,
    WeatherSourceMetadata,
    WeatherSummary,
    load_open_meteo_weather,
    open_meteo_source_metadata,
    summarize_weather,
)


@dataclass(frozen=True)
class AnalysisResult:
    records: list[GenerationRecord]
    data_source: DataSourceMetadata
    summary: RenewableSummary
    period_summaries: list[PeriodRenewableSummary]
    alert: RenewableAlert
    baseline: BaselinePrediction
    cache_path: Path | None
    cache_hit: bool = False
    weather_records: list[WeatherRecord] | None = None
    weather_source: WeatherSourceMetadata | None = None
    weather_summary: WeatherSummary | None = None
    weather_error: str | None = None


def run_analysis(
    source_path: str | Path | None = None,
    cache_path: str | Path | None = None,
    write_cache: bool = True,
    source: str = "exemplo",
    ons_year: int | None = None,
    ons_month: int | None = None,
    ons_loader: Callable[[int, int], list[GenerationRecord]] | None = None,
    prefer_cache: bool = True,
    include_weather: bool = False,
    weather_latitude: float = DEFAULT_WEATHER_LATITUDE,
    weather_longitude: float = DEFAULT_WEATHER_LONGITUDE,
    weather_forecast_days: int = DEFAULT_WEATHER_FORECAST_DAYS,
    weather_loader: Callable[..., list[WeatherRecord]] | None = None,
    ons_cache_max_age_days: int | None = None,
) -> AnalysisResult:
    if ons_cache_max_age_days is not None and ons_cache_max_age_days < 0:
        raise ValueError("--ons-cache-max-age-dias deve ser maior ou igual a zero.")

    records, data_source, cache_hit = _load_records(
        source_path=source_path,
        source=source,
        ons_year=ons_year,
        ons_month=ons_month,
        ons_loader=ons_loader,
        cache_path=cache_path,
        prefer_cache=prefer_cache,
        ons_cache_max_age_days=ons_cache_max_age_days,
    )
    summary = summarize_generation(records)
    period_summaries = summarize_by_period(records)
    alert = build_renewable_alert(summary)
    weather_records: list[WeatherRecord] | None = None
    weather_source: WeatherSourceMetadata | None = None
    weather_summary: WeatherSummary | None = None
    weather_error: str | None = None

    if include_weather:
        weather_source = open_meteo_source_metadata(
            latitude=weather_latitude,
            longitude=weather_longitude,
            forecast_days=weather_forecast_days,
        )
        loader = weather_loader or load_open_meteo_weather
        try:
            weather_records = loader(
                latitude=weather_latitude,
                longitude=weather_longitude,
                forecast_days=weather_forecast_days,
            )
        except WeatherDataError as exc:
            weather_error = str(exc)
            weather_records = []
        weather_summary = summarize_weather(weather_records)
    baseline = predict_next_renewable_share(period_summaries, weather_records=weather_records)

    written_cache_path = None
    should_write_cache = write_cache and cache_path is not None and (
        not cache_hit or include_weather
    )
    if should_write_cache:
        written_cache_path = write_analysis_cache(
            cache_path,
            records=records,
            summary=summary,
            period_summaries=period_summaries,
            alert=alert,
            baseline=baseline,
            data_source=data_source,
            cache_hit=cache_hit,
            weather_source=weather_source,
            weather_summary=weather_summary,
            weather_records=weather_records,
            weather_error=weather_error,
        )
    elif cache_hit:
        written_cache_path = Path(cache_path) if cache_path is not None else None

    return AnalysisResult(
        records=records,
        data_source=data_source,
        summary=summary,
        period_summaries=period_summaries,
        alert=alert,
        baseline=baseline,
        cache_path=written_cache_path,
        cache_hit=cache_hit,
        weather_records=weather_records,
        weather_source=weather_source,
        weather_summary=weather_summary,
        weather_error=weather_error,
    )


def _load_records(
    *,
    source_path: str | Path | None,
    source: str,
    ons_year: int | None,
    ons_month: int | None,
    ons_loader: Callable[[int, int], list[GenerationRecord]] | None,
    cache_path: str | Path | None,
    prefer_cache: bool,
    ons_cache_max_age_days: int | None,
) -> tuple[list[GenerationRecord], DataSourceMetadata, bool]:
    if source_path is not None:
        if source != "exemplo":
            raise ValueError("--arquivo nao pode ser combinado com --fonte ons.")
        csv_path = Path(source_path)
        return load_generation_csv(csv_path), DataSourceMetadata(
            kind="arquivo",
            label="CSV local",
            path=str(csv_path),
        ), False

    if source == "exemplo":
        return load_sample_generation(), DataSourceMetadata(
            kind="exemplo",
            label="Exemplo embutido",
        ), False

    if source == "ons":
        if ons_year is None or ons_month is None:
            raise ValueError("--ons-periodo e obrigatorio quando --fonte ons.")
        metadata = ons_generation_source_metadata(ons_year, ons_month)
        if prefer_cache and cache_path is not None and metadata.period is not None:
            cached_records = find_generation_records_by_source_period(
                cache_path,
                source_kind=metadata.kind,
                source_period=metadata.period,
                max_age_days=ons_cache_max_age_days,
            )
            if cached_records:
                return cached_records, metadata, True
        loader = ons_loader or load_ons_generation
        return loader(ons_year, ons_month), metadata, False

    raise ValueError(f"Fonte de dados desconhecida: {source}")
