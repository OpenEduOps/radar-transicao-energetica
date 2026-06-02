from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseRequirement:
    key: str
    description: str
    satisfied: bool


@dataclass(frozen=True)
class ReleaseDecision:
    stage: str
    can_publish: bool
    requirements: tuple[ReleaseRequirement, ...]

    @property
    def missing_requirements(self) -> tuple[ReleaseRequirement, ...]:
        return tuple(requirement for requirement in self.requirements if not requirement.satisfied)


CURRENT_RELEASE_STAGE = "local-experimental"

CURRENT_RELEASE_REQUIREMENTS = (
    ReleaseRequirement(
        key="ui-stable",
        description="Interface desktop inicial estavel e validada manualmente",
        satisfied=False,
    ),
    ReleaseRequirement(
        key="formal-smoke-test",
        description="Smoke test formal do executavel definido e automatizavel",
        satisfied=False,
    ),
    ReleaseRequirement(
        key="checksum",
        description="Checksum do artefato definido no fluxo de release",
        satisfied=False,
    ),
    ReleaseRequirement(
        key="ci-artifact-build",
        description="Build automatico de artefato configurado na CI",
        satisfied=False,
    ),
    ReleaseRequirement(
        key="release-workflow",
        description="Workflow de release publica documentado e aprovado",
        satisfied=False,
    ),
)


def evaluate_public_release_readiness(
    requirements: tuple[ReleaseRequirement, ...] = CURRENT_RELEASE_REQUIREMENTS,
) -> ReleaseDecision:
    missing = tuple(requirement for requirement in requirements if not requirement.satisfied)
    return ReleaseDecision(
        stage=CURRENT_RELEASE_STAGE,
        can_publish=not missing,
        requirements=requirements,
    )


def format_release_decision(decision: ReleaseDecision) -> str:
    lines = [f"Estagio do executavel: {decision.stage}"]
    if decision.can_publish:
        lines.append("Release publica permitida.")
        return "\n".join(lines)

    lines.append("Release publica bloqueada.")
    lines.append("Pendencias:")
    lines.extend(f"- {item.key}: {item.description}" for item in decision.missing_requirements)
    return "\n".join(lines)
