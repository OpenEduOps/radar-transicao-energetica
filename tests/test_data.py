from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.data import (
    GenerationDataError,
    load_generation_csv,
    load_sample_generation,
    normalize_source,
)


class DataLoadingTest(unittest.TestCase):
    def test_load_sample_generation(self) -> None:
        records = load_sample_generation()

        self.assertEqual(len(records), 12)
        self.assertEqual(records[0].source, "hidraulica")
        self.assertEqual(records[0].generation_mw, 5200.0)

    def test_load_generation_csv_with_aliases(self) -> None:
        csv_text = "\n".join(
            [
                "din_instante;nom_tipousina;val_geracaomwmed",
                "01/01/2026 00:00;UHE;1.234,5",
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "geracao.csv"
            path.write_text(csv_text, encoding="utf-8")

            records = load_generation_csv(path)

        self.assertEqual(records[0].source, "hidraulica")
        self.assertEqual(records[0].generation_mw, 1234.5)

    def test_load_generation_csv_with_punctuated_header_and_en_number(self) -> None:
        csv_text = "\n".join(
            [
                "Data;Fonte;Val Geracao (MWmed)",
                "2026-01-01 00:00;Hidroeletrica;1,234.5",
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "geracao.csv"
            path.write_text(csv_text, encoding="utf-8")

            records = load_generation_csv(path)

        self.assertEqual(records[0].source, "hidraulica")
        self.assertEqual(records[0].generation_mw, 1234.5)

    def test_missing_generation_column_raises_error(self) -> None:
        csv_text = "period,source\n2026-01-01,hidraulica\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "geracao.csv"
            path.write_text(csv_text, encoding="utf-8")

            with self.assertRaises(GenerationDataError):
                load_generation_csv(path)

    def test_invalid_generation_value_raises_error(self) -> None:
        csv_text = "period,source,generation_mw\n2026-01-01,hidraulica,abc\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "geracao.csv"
            path.write_text(csv_text, encoding="utf-8")

            with self.assertRaises(GenerationDataError):
                load_generation_csv(path)

    def test_normalize_source(self) -> None:
        self.assertEqual(normalize_source("Hidrelétrica"), "hidraulica")
        self.assertEqual(normalize_source("Hidroeletrica"), "hidraulica")
        self.assertEqual(normalize_source("UFV"), "solar")


if __name__ == "__main__":
    unittest.main()
