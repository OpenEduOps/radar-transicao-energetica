from __future__ import annotations

from dataclasses import dataclass

from radar_transicao_energetica.domain import RenewableSummary


@dataclass(frozen=True)
class RenewableAlert:
    level: str
    message: str


def build_renewable_alert(summary: RenewableSummary) -> RenewableAlert:
    share = summary.renewable_share
    if share is None:
        return RenewableAlert(
            level="dados_insuficientes",
            message="Dados insuficientes para calcular participacao renovavel.",
        )

    unknown_suffix = ""
    if summary.unknown_sources:
        unknown_suffix = (
            " A analise contem fontes ainda nao classificadas na V0: "
            + ", ".join(summary.unknown_sources)
            + "."
        )

    if share >= 0.75:
        return RenewableAlert(
            level="boa_janela_renovavel",
            message=(
                "Boa janela renovavel: a maior parte da geracao analisada veio de fontes renovaveis."
                + unknown_suffix
            ),
        )

    if share >= 0.55:
        return RenewableAlert(
            level="atencao_moderada",
            message=(
                "Atencao moderada: a participacao renovavel esta positiva, mas ha espaco para maior dependencia termica."
                + unknown_suffix
            ),
        )

    return RenewableAlert(
        level="pressao_termica",
        message=(
            "Maior pressao termica: a participacao renovavel ficou abaixo do patamar desejado para esta analise."
            + unknown_suffix
        ),
    )
