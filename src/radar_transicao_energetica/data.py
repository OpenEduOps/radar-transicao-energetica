from __future__ import annotations

import csv
import io
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SAMPLE_GENERATION_CSV = """period,source,generation_mw
2026-01-01 00:00,hidraulica,5200
2026-01-01 00:00,eolica,1800
2026-01-01 00:00,solar,200
2026-01-01 00:00,termica,1600
2026-01-01 01:00,hidraulica,5000
2026-01-01 01:00,eolica,2100
2026-01-01 01:00,solar,100
2026-01-01 01:00,termica,1900
2026-01-01 02:00,hidraulica,4700
2026-01-01 02:00,eolica,2300
2026-01-01 02:00,solar,80
2026-01-01 02:00,termica,2200
"""


PERIOD_COLUMNS = ("period", "periodo", "timestamp", "data", "din_instante")
SOURCE_COLUMNS = ("source", "fonte", "tipo_fonte", "nom_tipousina", "nom_tipocombustivel")
GENERATION_COLUMNS = (
    "generation_mw",
    "geracao_mw",
    "geracao",
    "val_geracao",
    "val_geracaomwmed",
    "val_geracaomw",
    "val_geracao_mwmed",
    "mwmed",
)

SOURCE_ALIASES = {
    "hidraulica": "hidraulica",
    "hidreletrica": "hidraulica",
    "hidroeletrica": "hidraulica",
    "hidro": "hidraulica",
    "uhe": "hidraulica",
    "eolica": "eolica",
    "eol": "eolica",
    "solar": "solar",
    "fotovoltaica": "solar",
    "ufv": "solar",
    "termica": "termica",
    "termeletrica": "termica",
    "ute": "termica",
}


class GenerationDataError(ValueError):
    """Raised when generation data cannot be loaded or normalized."""


@dataclass(frozen=True)
class GenerationRecord:
    period: datetime
    source: str
    generation_mw: float


def load_sample_generation() -> list[GenerationRecord]:
    return _load_generation_from_text(SAMPLE_GENERATION_CSV)


def load_generation_csv(path: str | Path) -> list[GenerationRecord]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise GenerationDataError(f"Arquivo nao encontrado: {csv_path}")

    return _load_generation_from_text(csv_path.read_text(encoding="utf-8-sig"))


def normalize_source(value: str) -> str:
    normalized = _normalize_key(value)
    return SOURCE_ALIASES.get(normalized, normalized)


def _load_generation_from_text(text: str) -> list[GenerationRecord]:
    if not text.strip():
        raise GenerationDataError("Arquivo CSV vazio.")

    reader = csv.DictReader(io.StringIO(text), dialect=_detect_dialect(text))
    if not reader.fieldnames:
        raise GenerationDataError("CSV sem cabecalho.")

    normalized_fieldnames = {_normalize_key(name): name for name in reader.fieldnames}
    period_column = _find_column(normalized_fieldnames, PERIOD_COLUMNS, "periodo")
    source_column = _find_column(normalized_fieldnames, SOURCE_COLUMNS, "fonte")
    generation_column = _find_column(normalized_fieldnames, GENERATION_COLUMNS, "geracao")

    records: list[GenerationRecord] = []
    for line_number, row in enumerate(reader, start=2):
        try:
            period = _parse_period(row.get(period_column, ""))
            source = normalize_source(row.get(source_column, ""))
            generation_mw = _parse_float(row.get(generation_column, ""))
        except GenerationDataError as exc:
            raise GenerationDataError(f"Linha {line_number}: {exc}") from exc

        if not source:
            raise GenerationDataError(f"Linha {line_number}: fonte ausente.")
        if generation_mw < 0:
            raise GenerationDataError(f"Linha {line_number}: geracao negativa.")

        records.append(
            GenerationRecord(
                period=period,
                source=source,
                generation_mw=generation_mw,
            )
        )

    if not records:
        raise GenerationDataError("CSV sem registros de geracao.")
    return records


def _find_column(
    normalized_fieldnames: dict[str, str],
    candidates: tuple[str, ...],
    label: str,
) -> str:
    for candidate in candidates:
        column = normalized_fieldnames.get(_normalize_key(candidate))
        if column:
            return column

    available = ", ".join(sorted(normalized_fieldnames.values()))
    raise GenerationDataError(
        f"Coluna de {label} nao encontrada. Colunas disponiveis: {available}"
    )


def _parse_period(value: str | None) -> datetime:
    raw = (value or "").strip()
    if not raw:
        raise GenerationDataError("periodo ausente.")

    normalized = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        pass

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    )
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise GenerationDataError(f"periodo invalido: {raw}")


def _parse_float(value: str | None) -> float:
    raw = (value or "").strip()
    if not raw:
        raise GenerationDataError("valor de geracao ausente.")

    normalized = raw.replace(" ", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized and "." not in normalized:
        normalized = normalized.replace(",", ".")

    try:
        return float(normalized)
    except ValueError as exc:
        raise GenerationDataError(f"valor de geracao invalido: {raw}") from exc


def _normalize_key(value: str | None) -> str:
    raw = (value or "").strip().lower()
    decomposed = unicodedata.normalize("NFD", raw)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    normalized = "".join(char if char.isalnum() else "_" for char in without_accents)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def _detect_dialect(text: str) -> csv.Dialect:
    sample = text[:2048]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if ";" in first_line:
            dialect = csv.excel()
            dialect.delimiter = ";"
            return dialect
        return csv.excel
