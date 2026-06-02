from __future__ import annotations

import re
from typing import Any, Callable
from urllib.request import Request, urlopen

from radar_transicao_energetica.data import (
    GenerationDataError,
    GenerationRecord,
    load_generation_csv_text,
)


ONS_GENERATION_BY_PLANT_DATASET_URL = "https://dados.ons.org.br/dataset/geracao-usina-2"
ONS_GENERATION_BY_PLANT_AWS_BASE_URL = (
    "https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/geracao_usina_2_ho"
)
ONS_USER_AGENT = "radar-transicao-energetica/0.1"
ONS_PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def parse_ons_period(value: str) -> tuple[int, int]:
    period = value.strip()
    if not ONS_PERIOD_PATTERN.fullmatch(period):
        raise ValueError("Periodo ONS invalido. Use o formato YYYY-MM.")

    year_text, month_text = period.split("-")
    year = int(year_text)
    month = int(month_text)
    _validate_ons_period(year, month)
    return year, month


def build_ons_generation_url(year: int, month: int) -> str:
    _validate_ons_period(year, month)
    return (
        f"{ONS_GENERATION_BY_PLANT_AWS_BASE_URL}/"
        f"GERACAO_USINA-2_{year}_{month:02d}.csv"
    )


def load_ons_generation(
    year: int,
    month: int,
    *,
    timeout: float = 30.0,
    opener: Callable[..., Any] = urlopen,
) -> list[GenerationRecord]:
    url = build_ons_generation_url(year, month)
    request = Request(url, headers={"User-Agent": ONS_USER_AGENT})

    try:
        response = opener(request, timeout=timeout)
        try:
            payload = response.read()
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
    except OSError as exc:
        raise GenerationDataError(
            f"Nao foi possivel baixar dados ONS para {year}-{month:02d}: {exc}"
        ) from exc

    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise GenerationDataError(
            f"Dados ONS para {year}-{month:02d} nao estao em UTF-8 valido."
        ) from exc

    try:
        return load_generation_csv_text(text)
    except GenerationDataError as exc:
        raise GenerationDataError(
            f"Dados ONS para {year}-{month:02d} nao puderam ser normalizados: {exc}"
        ) from exc


def _validate_ons_period(year: int, month: int) -> None:
    if year < 2022:
        raise ValueError("A fonte ONS V0 aceita arquivos mensais de 2022 em diante.")
    if month < 1 or month > 12:
        raise ValueError("Mes ONS invalido. Use um valor entre 1 e 12.")
