from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


REQUIRED_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/arquitetura.md",
    "docs/checklists.md",
    "docs/ci.md",
    "docs/matriz-issues.md",
    "docs/planejamento-inicial.md",
    "docs/plano-implementacao.md",
    "docs/qa-ui.md",
    "docs/requisitos.md",
    "docs/testes.md",
)

REQUIRED_TEST_PLAN_MARKERS = (
    "## Guardrails",
    "## Critérios de Aceite Gerais",
    "## Matriz de Cobertura",
    "## Checklist de QA Manual da UI",
)

LOCAL_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.is_file():
            errors.append(f"Documento obrigatorio ausente: {relative_path}")

    errors.extend(_find_broken_local_links(root))
    errors.extend(_validate_test_plan(root / "docs" / "testes.md"))

    if errors:
        for error in errors:
            print(f"docs: {error}", file=sys.stderr)
        return 1
    print("Documentacao validada com sucesso.")
    return 0


def _find_broken_local_links(root: Path) -> list[str]:
    errors: list[str] = []
    for markdown_path in _markdown_files(root):
        text = markdown_path.read_text(encoding="utf-8")
        for match in LOCAL_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if _is_external_or_anchor(target):
                continue
            target_path = _link_target_path(markdown_path, target)
            if not target_path.exists():
                relative_markdown = markdown_path.relative_to(root).as_posix()
                relative_target = _display_path(root, target_path)
                errors.append(
                    f"link local quebrado em {relative_markdown}: {target} -> {relative_target}"
                )
    return errors


def _markdown_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*.md")
        if ".git" not in path.parts and ".venv" not in path.parts
    ]


def _is_external_or_anchor(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or target.startswith("#")
    )


def _link_target_path(markdown_path: Path, target: str) -> Path:
    path_part = target.split("#", maxsplit=1)[0]
    return (markdown_path.parent / unquote(path_part)).resolve()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _validate_test_plan(test_plan_path: Path) -> list[str]:
    if not test_plan_path.is_file():
        return []
    text = test_plan_path.read_text(encoding="utf-8")
    return [
        f"marcador obrigatorio ausente em docs/testes.md: {marker}"
        for marker in REQUIRED_TEST_PLAN_MARKERS
        if marker not in text
    ]


if __name__ == "__main__":
    raise SystemExit(main())
