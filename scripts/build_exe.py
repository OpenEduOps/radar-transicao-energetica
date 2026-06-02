from __future__ import annotations

import subprocess
import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXE_NAME = "radar-transicao-energetica"


def main() -> int:
    if importlib.util.find_spec("PyInstaller") is None:
        print(
            "PyInstaller nao esta instalado. Execute: python -m pip install pyinstaller",
            file=sys.stderr,
        )
        return 1

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
    if not exe_path.exists():
        print(f"Build finalizado sem encontrar o executavel esperado: {exe_path}", file=sys.stderr)
        return 1

    print(f"Executavel gerado em: {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
