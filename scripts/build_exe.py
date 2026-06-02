from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXE_NAME = "radar-transicao-energetica"


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--console",
        "--name",
        EXE_NAME,
        "--paths",
        str(ROOT / "src"),
        str(ROOT / "src" / "radar_transicao_energetica" / "__main__.py"),
    ]
    subprocess.run(command, cwd=ROOT, check=True)

    exe_path = ROOT / "dist" / f"{EXE_NAME}.exe"
    print(f"Executavel gerado em: {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
