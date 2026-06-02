from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.cache import (
    AnalysisCacheError,
    CACHE_SCHEMA_VERSION,
    read_latest_analysis_cache,
)


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


if __name__ == "__main__":
    unittest.main()
