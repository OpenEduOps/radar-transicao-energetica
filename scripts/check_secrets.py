from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_FILE_BYTES = 1_000_000

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    "data/cache",
}

SECRET_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{30,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    pattern_name: str

    def format(self, root: Path) -> str:
        return f"{self.path.relative_to(root).as_posix()}:{self.line_number}: {self.pattern_name}"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = scan_for_secrets(root)
    if findings:
        for finding in findings:
            print(f"secret: {finding.format(root)}", file=sys.stderr)
        return 1
    print("Nenhum segredo de alta confianca encontrado.")
    return 0


def scan_for_secrets(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _candidate_files(root):
        text = _read_text_candidate(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern_name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(path.resolve(), line_number, pattern_name))
    return findings


def _candidate_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.stat().st_size <= MAX_FILE_BYTES
        and not _is_excluded(root, path)
    ]


def _is_excluded(root: Path, path: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    normalized = "/".join(relative_parts)
    return any(
        part in EXCLUDED_DIRS or normalized.startswith(f"{excluded}/")
        for part in relative_parts
        for excluded in EXCLUDED_DIRS
    )


def _read_text_candidate(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
