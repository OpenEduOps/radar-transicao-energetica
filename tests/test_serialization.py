from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar_transicao_energetica.app import run_analysis
from radar_transicao_energetica.serialization import analysis_payload


class SerializationTest(unittest.TestCase):
    def test_analysis_payload_keeps_cache_and_cli_contract_consistent(self) -> None:
        result = run_analysis(write_cache=False)

        payload = analysis_payload(
            summary=result.summary,
            period_summaries=result.period_summaries,
            alert=result.alert,
            baseline=result.baseline,
            cache_path="data/cache/analises.sqlite",
            data_source=result.data_source,
        )

        self.assertIn("summary", payload)
        self.assertIn("period_summaries", payload)
        self.assertIn("alert", payload)
        self.assertIn("baseline", payload)
        self.assertIn("data_source", payload)
        self.assertEqual(payload["data_source"]["kind"], "exemplo")
        self.assertEqual(payload["cache_path"], "data/cache/analises.sqlite")
        self.assertIn("mean_absolute_error", payload["baseline"])
        self.assertIn("evaluated_points", payload["baseline"])
        self.assertIn("comparisons", payload["baseline"])
        self.assertGreater(payload["baseline"]["evaluated_points"], 0)
        self.assertIn("renewable_share", payload["summary"])
        self.assertIn("unknown_sources", payload["summary"])
        self.assertIn("unknown_sources", payload["period_summaries"][0])
        self.assertIn("message", payload["alert"])


if __name__ == "__main__":
    unittest.main()
