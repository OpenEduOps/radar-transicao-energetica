from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from radar_transicao_energetica.alerts import RenewableAlert
from radar_transicao_energetica.baseline import BaselinePrediction
from radar_transicao_energetica.data import DataSourceMetadata, GenerationRecord
from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary
from radar_transicao_energetica.serialization import analysis_payload


class AnalysisCacheError(ValueError):
    """Raised when the local analysis cache cannot be written."""


def write_analysis_cache(
    path: str | Path,
    *,
    records: list[GenerationRecord],
    summary: RenewableSummary,
    period_summaries: list[PeriodRenewableSummary],
    alert: RenewableAlert,
    baseline: BaselinePrediction,
    data_source: DataSourceMetadata | None = None,
) -> Path:
    cache_path = Path(path)
    payload = analysis_payload(
        summary=summary,
        period_summaries=period_summaries,
        alert=alert,
        baseline=baseline,
        cache_path=cache_path,
        data_source=data_source,
    )

    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(str(cache_path))) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            _ensure_schema(connection)
            analysis_id = _insert_analysis(
                connection,
                payload=payload,
                summary=summary,
                data_source=data_source,
            )
            _insert_generation_records(connection, analysis_id=analysis_id, records=records)
            connection.commit()
    except (OSError, sqlite3.Error) as exc:
        raise AnalysisCacheError(f"Nao foi possivel gravar o cache em {cache_path}: {exc}") from exc
    return cache_path


def read_latest_analysis_cache(path: str | Path) -> dict[str, Any]:
    cache_path = Path(path)
    try:
        with closing(sqlite3.connect(str(cache_path))) as connection:
            _ensure_schema(connection)
            row = connection.execute(
                "SELECT payload_json FROM analyses ORDER BY id DESC LIMIT 1"
            ).fetchone()
    except (OSError, sqlite3.Error) as exc:
        raise AnalysisCacheError(f"Nao foi possivel ler o cache em {cache_path}: {exc}") from exc

    if row is None:
        raise AnalysisCacheError(f"Cache sem analises gravadas: {cache_path}")

    try:
        return json.loads(row[0])
    except json.JSONDecodeError as exc:
        raise AnalysisCacheError(f"Cache invalido em {cache_path}: {exc}") from exc


def read_latest_generation_records(path: str | Path) -> list[GenerationRecord]:
    cache_path = Path(path)
    try:
        with closing(sqlite3.connect(str(cache_path))) as connection:
            _ensure_schema(connection)
            latest = connection.execute("SELECT MAX(id) FROM analyses").fetchone()
            analysis_id = latest[0] if latest else None
            if analysis_id is None:
                raise AnalysisCacheError(f"Cache sem analises gravadas: {cache_path}")
            rows = connection.execute(
                """
                SELECT period, source, generation_mw
                FROM generation_records
                WHERE analysis_id = ?
                ORDER BY period, source
                """,
                (analysis_id,),
            ).fetchall()
    except AnalysisCacheError:
        raise
    except (OSError, sqlite3.Error) as exc:
        raise AnalysisCacheError(f"Nao foi possivel ler o cache em {cache_path}: {exc}") from exc

    return [
        GenerationRecord(
            period=datetime.fromisoformat(period),
            source=source,
            generation_mw=generation_mw,
        )
        for period, source, generation_mw in rows
    ]


def _ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            data_source_kind TEXT,
            data_source_label TEXT,
            data_source_period TEXT,
            data_source_path TEXT,
            data_source_dataset_url TEXT,
            data_source_resource_url TEXT,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            renewable_share REAL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS generation_records (
            analysis_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            source TEXT NOT NULL,
            generation_mw REAL NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_generation_records_analysis
        ON generation_records (analysis_id)
        """
    )


def _insert_analysis(
    connection: sqlite3.Connection,
    *,
    payload: dict[str, Any],
    summary: RenewableSummary,
    data_source: DataSourceMetadata | None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO analyses (
            created_at,
            payload_json,
            data_source_kind,
            data_source_label,
            data_source_period,
            data_source_path,
            data_source_dataset_url,
            data_source_resource_url,
            period_start,
            period_end,
            renewable_share
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            json.dumps(payload, ensure_ascii=False, indent=2),
            data_source.kind if data_source else None,
            data_source.label if data_source else None,
            data_source.period if data_source else None,
            data_source.path if data_source else None,
            data_source.dataset_url if data_source else None,
            data_source.resource_url if data_source else None,
            summary.period_start.isoformat(),
            summary.period_end.isoformat(),
            summary.renewable_share,
        ),
    )
    return int(cursor.lastrowid)


def _insert_generation_records(
    connection: sqlite3.Connection,
    *,
    analysis_id: int,
    records: list[GenerationRecord],
) -> None:
    connection.executemany(
        """
        INSERT INTO generation_records (analysis_id, period, source, generation_mw)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                analysis_id,
                record.period.isoformat(),
                record.source,
                record.generation_mw,
            )
            for record in records
        ],
    )
