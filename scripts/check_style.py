from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


TEXT_SUFFIXES = {
    "",
    ".gitignore",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class StyleIssue:
    path: Path
    message: str
    line_number: int | None = None

    def format(self, root: Path) -> str:
        relative_path = self.path.relative_to(root).as_posix()
        if self.line_number is None:
            return f"{relative_path}: {self.message}"
        return f"{relative_path}:{self.line_number}: {self.message}"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    issues = check_text_style(root, _tracked_files(root))
    if issues:
        for issue in issues:
            print(f"style: {issue.format(root)}", file=sys.stderr)
        return 1
    print("Estilo textual validado com sucesso.")
    return 0


def check_text_style(root: Path, paths: list[Path]) -> list[StyleIssue]:
    issues: list[StyleIssue] = []
    for path in paths:
        if not _is_text_candidate(path):
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            issues.append(StyleIssue(path, f"nao foi possivel ler arquivo: {exc}"))
            continue
        if not data:
            continue
        if b"\0" in data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if not text.endswith("\n"):
            issues.append(StyleIssue(path, "arquivo deve terminar com newline"))
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                issues.append(StyleIssue(path, "whitespace no fim da linha", line_number))
    return issues


def _tracked_files(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [root / line for line in completed.stdout.splitlines() if line]


def _is_text_candidate(path: Path) -> bool:
    if path.name == ".gitignore":
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


if __name__ == "__main__":
    raise SystemExit(main())
