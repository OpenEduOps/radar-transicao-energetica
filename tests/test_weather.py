from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.weather import (
    DEFAULT_WEATHER_LATITUDE,
    DEFAULT_WEATHER_LONGITUDE,
    OPEN_METEO_FORECAST_URL,
    WeatherDataError,
    build_open_meteo_url,
    load_open_meteo_weather,
    open_meteo_source_metadata,
    parse_open_meteo_weather,
    summarize_weather,
)


class FakeWeatherResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.closed = False

    def read(self, _size: int) -> bytes:
        return self.payload

    def close(self) -> None:
        self.closed = True


def weather_payload() -> dict[str, object]:
    return {
        "hourly": {
            "time": ["2026-01-01T00:00", "2026-01-01T01:00"],
            "temperature_2m": [22.0, 24.0],
            "wind_speed_10m": [8.0, 10.0],
            "shortwave_radiation": [0.0, 120.0],
            "cloud_cover": [40.0, 60.0],
        }
    }


class WeatherTest(unittest.TestCase):
    def test_build_open_meteo_url_uses_expected_endpoint_and_hourly_variables(self) -> None:
        url = build_open_meteo_url()

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        self.assertEqual(f"{parsed.scheme}://{parsed.netloc}{parsed.path}", OPEN_METEO_FORECAST_URL)
        self.assertEqual(query["latitude"], [str(DEFAULT_WEATHER_LATITUDE)])
        self.assertEqual(query["longitude"], [str(DEFAULT_WEATHER_LONGITUDE)])
        self.assertEqual(query["forecast_days"], ["2"])
        self.assertEqual(query["timezone"], ["America/Sao_Paulo"])
        self.assertEqual(
            query["hourly"],
            ["temperature_2m,wind_speed_10m,shortwave_radiation,cloud_cover"],
        )

    def test_open_meteo_metadata_tracks_coordinates_and_resource_url(self) -> None:
        metadata = open_meteo_source_metadata(latitude=-22.9, longitude=-43.2, forecast_days=1)

        self.assertEqual(metadata.kind, "open-meteo")
        self.assertEqual(metadata.latitude, -22.9)
        self.assertEqual(metadata.longitude, -43.2)
        self.assertIn("latitude=-22.9", metadata.resource_url)
        self.assertIn("forecast_days=1", metadata.resource_url)

    def test_parse_open_meteo_weather_normalizes_hourly_records(self) -> None:
        records = parse_open_meteo_weather(weather_payload())

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].period.isoformat(), "2026-01-01T00:00:00")
        self.assertEqual(records[1].temperature_2m_c, 24.0)
        self.assertEqual(records[1].wind_speed_10m_kmh, 10.0)
        self.assertEqual(records[1].shortwave_radiation_w_m2, 120.0)
        self.assertEqual(records[1].cloud_cover_percent, 60.0)

    def test_summarize_weather_calculates_average_values(self) -> None:
        summary = summarize_weather(parse_open_meteo_weather(weather_payload()))

        self.assertIsNotNone(summary)
        assert summary is not None
        self.assertEqual(summary.record_count, 2)
        self.assertEqual(summary.average_temperature_2m_c, 23.0)
        self.assertEqual(summary.average_wind_speed_10m_kmh, 9.0)
        self.assertEqual(summary.average_shortwave_radiation_w_m2, 60.0)
        self.assertEqual(summary.average_cloud_cover_percent, 50.0)

    def test_load_open_meteo_weather_uses_injected_opener_without_network(self) -> None:
        response = FakeWeatherResponse(json.dumps(weather_payload()).encode("utf-8"))

        def fake_opener(request: object, timeout: float) -> FakeWeatherResponse:
            self.assertEqual(timeout, 30.0)
            self.assertEqual(
                getattr(request, "get_header")("User-agent"),
                "radar-transicao-energetica/0.1",
            )
            return response

        records = load_open_meteo_weather(opener=fake_opener)

        self.assertTrue(response.closed)
        self.assertEqual(len(records), 2)

    def test_parse_open_meteo_weather_rejects_misaligned_hourly_arrays(self) -> None:
        payload = weather_payload()
        hourly = payload["hourly"]
        assert isinstance(hourly, dict)
        hourly["wind_speed_10m"] = [8.0]

        with self.assertRaisesRegex(WeatherDataError, "desalinhada"):
            parse_open_meteo_weather(payload)

    def test_open_meteo_validation_rejects_invalid_coordinates_and_days(self) -> None:
        with self.assertRaisesRegex(WeatherDataError, "Latitude"):
            build_open_meteo_url(latitude=91.0)

        with self.assertRaisesRegex(WeatherDataError, "Longitude"):
            build_open_meteo_url(longitude=-181.0)

        with self.assertRaisesRegex(WeatherDataError, "Dias"):
            build_open_meteo_url(forecast_days=0)

    def test_load_open_meteo_weather_rejects_large_or_invalid_payloads(self) -> None:
        large_response = FakeWeatherResponse(b"{}")

        with self.assertRaisesRegex(WeatherDataError, "excede"):
            load_open_meteo_weather(opener=lambda *_args, **_kwargs: large_response, max_bytes=1)

        invalid_response = FakeWeatherResponse(b"{")

        with self.assertRaisesRegex(WeatherDataError, "JSON UTF-8"):
            load_open_meteo_weather(opener=lambda *_args, **_kwargs: invalid_response)


if __name__ == "__main__":
    unittest.main()
