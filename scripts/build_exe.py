from __future__ import annotations

import argparse
import subprocess
import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from radar_transicao_energetica.release import (  # noqa: E402
    evaluate_public_release_readiness,
    format_release_decision,
)

EXE_NAME = "radar-transicao-energetica"


def build_pyinstaller_command() -> list[str]:
    return [
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera o executavel local experimental do Radar da Transicao Energetica.",
    )
    parser.add_argument(
        "--public-release",
        action="store_true",
        help="Falha enquanto os criterios de release publica nao estiverem completos.",
    )
    parser.add_argument(
        "--release-status",
        action="store_true",
        help="Mostra o estagio atual de release sem gerar executavel.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    release_decision = evaluate_public_release_readiness()

    if args.release_status:
        print(format_release_decision(release_decision))
        return 0

    if args.public_release and not release_decision.can_publish:
        print(format_release_decision(release_decision), file=sys.stderr)
        return 2

    if importlib.util.find_spec("PyInstaller") is None:
        print(
            'PyInstaller nao esta instalado. Execute: python -m pip install -e ".[dev]"',
            file=sys.stderr,
        )
        return 1

    print(format_release_decision(release_decision))
    print("Gerando executavel local experimental. Artefatos de release publica seguem adiados.")
    command = build_pyinstaller_command()
    subprocess.run(command, cwd=ROOT, check=True)

    exe_path = ROOT / "dist" / f"{EXE_NAME}.exe"
    if not exe_path.exists():
        print(f"Build finalizado sem encontrar o executavel esperado: {exe_path}", file=sys.stderr)
        return 1

    print(f"Executavel gerado em: {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
