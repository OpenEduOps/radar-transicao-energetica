from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.cache import (
    AnalysisCacheError,
    CACHE_SCHEMA_VERSION,
    find_generation_records_by_source_period,
    read_latest_analysis_cache,
)
from radar_transicao_energetica.data import GenerationRecord


class CacheTest(unittest.TestCase):
    def test_read_latest_analysis_cache_does_not_create_missing_database(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            with self.assertRaisesRegex(AnalysisCacheError, "Cache nao encontrado"):
                read_latest_analysis_cache(cache_path)

            self.assertFalse(cache_path.exists())

    def test_sqlite_cache_stores_metadata_and_normalized_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            result = run_analysis(cache_path=cache_path)

            with closing(sqlite3.connect(str(cache_path))) as connection:
                analysis_row = connection.execute(
                    """
                    SELECT data_source_kind, data_source_label, renewable_share
                    FROM analyses
                    """
                ).fetchone()
                record_count = connection.execute(
                    "SELECT COUNT(*) FROM generation_records"
                ).fetchone()[0]
                schema_version = connection.execute(
                    """
                    SELECT value
                    FROM cache_metadata
                    WHERE key = 'schema_version'
                    """
                ).fetchone()[0]

        self.assertEqual(analysis_row[0], "exemplo")
        self.assertEqual(analysis_row[1], "Exemplo embutido")
        self.assertEqual(analysis_row[2], result.summary.renewable_share)
        self.assertEqual(record_count, len(result.records))
        self.assertEqual(schema_version, CACHE_SCHEMA_VERSION)

    def test_cache_finds_generation_records_by_source_and_period(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"
            run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 90.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 10.0),
                ],
            )

            cached_records = find_generation_records_by_source_period(
                cache_path,
                source_kind="ons",
                source_period="2026-01",
            )
            missing_records = find_generation_records_by_source_period(
                cache_path,
                source_kind="ons",
                source_period="2026-02",
            )

        self.assertIsNotNone(cached_records)
        self.assertEqual(len(cached_records or []), 2)
        self.assertEqual((cached_records or [])[0].source, "hidraulica")
        self.assertIsNone(missing_records)

    def test_cache_ignores_expired_generation_records_by_source_and_period(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"
            run_analysis(
                source="ons",
                ons_year=2026,
                ons_month=1,
                cache_path=cache_path,
                ons_loader=lambda _year, _month: [
                    GenerationRecord(datetime(2026, 1, 1, 0), "hidraulica", 90.0),
                    GenerationRecord(datetime(2026, 1, 1, 0), "termica", 10.0),
                ],
            )
            expired_at = datetime.now(timezone.utc) - timedelta(days=2)
            with closing(sqlite3.connect(str(cache_path))) as connection:
                connection.execute(
                    "UPDATE analyses SET created_at = ?",
                    (expired_at.isoformat(timespec="seconds"),),
                )
                connection.commit()

            cached_records = find_generation_records_by_source_period(
                cache_path,
                source_kind="ons",
                source_period="2026-01",
                max_age_days=1,
            )
            fresh_without_policy = find_generation_records_by_source_period(
                cache_path,
                source_kind="ons",
                source_period="2026-01",
            )

        self.assertIsNone(cached_records)
        self.assertIsNotNone(fresh_without_policy)

    def test_cache_rejects_negative_max_age_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            with self.assertRaisesRegex(ValueError, "max_age_days"):
                find_generation_records_by_source_period(
                    cache_path,
                    source_kind="ons",
                    source_period="2026-01",
                    max_age_days=-1,
                )


if __name__ == "__main__":
    unittest.main()
