from __future__ import annotations

from radar_transicao_energetica.domain import PeriodRenewableSummary, RenewableSummary


def render_source_chart(summary: RenewableSummary, width: int = 32) -> str:
    if not summary.generation_by_source:
        return "Sem dados de fonte para exibir."

    max_generation = max(summary.generation_by_source.values())
    lines = ["Geracao por fonte:"]
    for source, generation in summary.generation_by_source.items():
        bar = _bar(generation, max_generation, width)
        lines.append(f"- {source:<12} {bar} {generation:,.2f} MW")
    return "\n".join(lines)


def render_share_trend(summaries: list[PeriodRenewableSummary], width: int = 24) -> str:
    if not summaries:
        return "Sem periodos para exibir."

    lines = ["Tendencia de participacao renovavel:"]
    for summary in summaries:
        share = summary.renewable_share
        if share is None:
            lines.append(f"- {summary.period:%Y-%m-%d %H:%M} sem dados")
            continue
        bar = _bar(share, 1.0, width)
        lines.append(f"- {summary.period:%Y-%m-%d %H:%M} {bar} {share:.1%}")
    return "\n".join(lines)


def _bar(value: float, max_value: float, width: int) -> str:
    if max_value <= 0:
        filled = 0
    else:
        filled = round((value / max_value) * width)
    filled = max(0, min(width, filled))
    return "#" * filled + "." * (width - filled)
