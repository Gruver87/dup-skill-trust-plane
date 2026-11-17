"""Trust report / Skill Card types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Verdict(StrEnum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    REFUSED = "refused"
    MALICIOUS = "malicious"


@dataclass
class GateResult:
    name: str
    ok: bool
    available: bool = True
    detail: str = ""
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillTrust:
    name: str
    sha256: str | None
    verdict: Verdict
    gates: dict[str, GateResult]
    permissions: dict[str, Any]
    card: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "sha256": self.sha256,
            "verdict": self.verdict.value,
            "gates": {k: v.to_dict() for k, v in self.gates.items()},
            "permissions": dict(self.permissions),
            "card": dict(self.card),
        }


@dataclass
class TrustReport:
    pack_root: str
    skill_count: int
    ok: bool
    verdict: Verdict
    skills: list[SkillTrust] = field(default_factory=list)
    pack_gates: dict[str, GateResult] = field(default_factory=dict)
    tool_version: str = "0.1.0"
    source: str = "Gruver87/dup-agent-skills"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_version": self.tool_version,
            "pack_root": self.pack_root,
            "source": self.source,
            "skill_count": self.skill_count,
            "ok": self.ok,
            "verdict": self.verdict.value,
            "pack_gates": {k: v.to_dict() for k, v in self.pack_gates.items()},
            "skills": [s.to_dict() for s in self.skills],
            "note": (
                "trust plane only — not a marketplace; "
                "not financial advice; FUTURES_BLOCK unchanged"
            ),
        }
