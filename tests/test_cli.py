from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTest(unittest.TestCase):
    def test_cli_runs_with_embedded_sample_json(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "radar_transicao_energetica",
                "--json",
                "--sem-cache",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        payload = json.loads(result.stdout)

        self.assertIn("renewable_share", payload)
        self.assertGreater(payload["renewable_share"], 0)
        self.assertIn("alert", payload)

    def test_cli_writes_cache_when_enabled(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.json"

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radar_transicao_energetica",
                    "--json",
                    "--cache",
                    str(cache_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(cache_path.read_text(encoding="utf-8"))

        self.assertIn("summary", payload)
        self.assertIn("alert", payload)


if __name__ == "__main__":
    unittest.main()
