from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.cache import (
    AnalysisCacheError,
    read_latest_analysis_cache,
)


class CacheTest(unittest.TestCase):
    def test_read_latest_analysis_cache_does_not_create_missing_database(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.sqlite"

            with self.assertRaisesRegex(AnalysisCacheError, "Cache nao encontrado"):
                read_latest_analysis_cache(cache_path)

            self.assertFalse(cache_path.exists())


if __name__ == "__main__":
    unittest.main()
