from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.data import GenerationDataError
from radar_transicao_energetica.ons import (
    build_ons_generation_url,
    load_ons_generation,
    parse_ons_period,
)


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.closed = False

    def read(self) -> bytes:
        return self.payload

    def close(self) -> None:
        self.closed = True


class OnsLoadingTest(unittest.TestCase):
    def test_parse_ons_period_requires_year_month_format(self) -> None:
        self.assertEqual(parse_ons_period("2026-01"), (2026, 1))

        with self.assertRaisesRegex(ValueError, "YYYY-MM"):
            parse_ons_period("2026")

        with self.assertRaisesRegex(ValueError, "YYYY-MM"):
            parse_ons_period("2026-1")

        with self.assertRaisesRegex(ValueError, "Mes ONS invalido"):
            parse_ons_period("2026-13")

    def test_build_ons_generation_url_uses_monthly_public_csv_path(self) -> None:
        url = build_ons_generation_url(2026, 1)

        self.assertEqual(
            url,
            "https://ons-aws-prod-opendata.s3.amazonaws.com/"
            "dataset/geracao_usina_2_ho/GERACAO_USINA-2_2026_01.csv",
        )

    def test_build_ons_generation_url_rejects_older_yearly_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "2022 em diante"):
            build_ons_generation_url(2021, 12)

    def test_build_ons_generation_url_rejects_invalid_month(self) -> None:
        with self.assertRaisesRegex(ValueError, "Mes ONS invalido"):
            build_ons_generation_url(2026, 13)

    def test_load_ons_generation_normalizes_public_csv_fixture(self) -> None:
        csv_text = "\n".join(
            [
                "din_instante;nom_tipousina;val_geracaomwmed",
                "2026-01-01 00:00:00;HIDROELÉTRICA;1.000,5",
                "2026-01-01 00:00:00;EOLIELÉTRICA;200,25",
                "2026-01-01 00:00:00;SOLAR FOTOVOLTAICA;50",
                "2026-01-01 00:00:00;TERMOELÉTRICA;300",
            ]
        )
        response = FakeResponse(csv_text.encode("utf-8-sig"))
        captured_urls: list[str] = []

        def fake_opener(request, timeout):
            captured_urls.append(request.full_url)
            self.assertEqual(timeout, 30.0)
            return response

        records = load_ons_generation(2026, 1, opener=fake_opener)

        self.assertTrue(response.closed)
        self.assertEqual(
            captured_urls,
            [
                "https://ons-aws-prod-opendata.s3.amazonaws.com/"
                "dataset/geracao_usina_2_ho/GERACAO_USINA-2_2026_01.csv"
            ],
        )
        self.assertEqual(
            [record.source for record in records],
            ["hidraulica", "eolica", "solar", "termica"],
        )
        self.assertEqual(sum(record.generation_mw for record in records), 1550.75)

    def test_load_ons_generation_reports_download_error_cleanly(self) -> None:
        def failing_opener(request, timeout):
            raise OSError("offline")

        with self.assertRaisesRegex(GenerationDataError, "Nao foi possivel baixar dados ONS"):
            load_ons_generation(2026, 1, opener=failing_opener)


if __name__ == "__main__":
    unittest.main()
