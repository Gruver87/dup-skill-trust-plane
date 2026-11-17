"""Trust pipeline orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skill_trust import __version__
from skill_trust.card import issue_card
from skill_trust.gates import (
    list_skills,
    run_policy_sanity,
    run_security_scan,
    run_skills_eval,
)
from skill_trust.models import GateResult, SkillTrust, TrustReport, Verdict
from skill_trust.sandbox import sandbox_gate

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PACKAGE_ROOT / "configs" / "default_trust.json"


def load_trust_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_CONFIG
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _skill_verdict(
    *,
    pack_static: GateResult,
    security: GateResult,
    allowlist: GateResult,
    sandbox: GateResult,
    skill_security_findings: list[dict[str, Any]],
) -> Verdict:
    if not security.available or not pack_static.available:
        return Verdict.REFUSED
    if any(f.get("code") in {
        "download_exec",
        "sk_live_token",
        "private_key_block",
        "hidden_exfil",
        "eval_obfuscation",
    } for f in skill_security_findings):
        return Verdict.MALICIOUS
    if not security.ok:
        return Verdict.MALICIOUS if skill_security_findings else Verdict.REFUSED
    if not pack_static.ok or not allowlist.ok or not sandbox.ok:
        return Verdict.REFUSED
    return Verdict.CLEAN


def verify_pack(
    pack_root: Path,
    *,
    source: str = "Gruver87/dup-agent-skills",
    skip_allowlist: bool = False,
    require_policy: bool = True,
) -> TrustReport:
    pack_root = pack_root.resolve()
    pack_gates: dict[str, GateResult] = {}

    static = run_skills_eval(pack_root)
    pack_gates["static"] = static

    security, allowlist, hashes = run_security_scan(
        pack_root, source=source, skip_allowlist=skip_allowlist
    )
    pack_gates["security"] = security
    pack_gates["allowlist"] = allowlist

    if require_policy:
        pack_gates["policy"] = run_policy_sanity()

    skills_out: list[SkillTrust] = []
    for skill_dir in list_skills(pack_root):
        name = skill_dir.name
        perms, sb_ok, sb_detail = sandbox_gate(skill_dir)
        sb = GateResult(
            name="sandbox_profile",
            ok=sb_ok,
            available=True,
            detail=sb_detail,
        )
        # Per-skill security findings filtered by skill name
        skill_findings = [
            f
            for f in security.findings
            if isinstance(f, dict) and f.get("skill") == name
        ]
        # Allowlist deny for this skill
        al_skill_ok = allowlist.ok or not any(
            isinstance(f, dict) and f.get("skill") == name for f in allowlist.findings
        )
        if not allowlist.ok:
            al_skill_ok = not any(
                isinstance(f, dict) and f.get("skill") == name for f in allowlist.findings
            )

        gates = {
            "static": static,
            "security": GateResult(
                name="security",
                ok=len(skill_findings) == 0 and security.available,
                available=security.available,
                detail=security.detail,
                findings=skill_findings,
            ),
            "allowlist": GateResult(
                name="allowlist",
                ok=al_skill_ok and allowlist.available,
                available=allowlist.available,
                detail=allowlist.detail,
                findings=[
                    f
                    for f in allowlist.findings
                    if isinstance(f, dict) and f.get("skill") == name
                ],
            ),
            "sandbox_profile": sb,
        }
        verdict = _skill_verdict(
            pack_static=static,
            security=gates["security"],
            allowlist=gates["allowlist"],
            sandbox=sb,
            skill_security_findings=skill_findings,
        )
        # Pack-level static failure refuses all
        if not static.ok or not static.available:
            verdict = Verdict.REFUSED
        if require_policy and not pack_gates.get("policy", GateResult("policy", True)).ok:
            if not pack_gates["policy"].available:
                verdict = Verdict.REFUSED

        st = SkillTrust(
            name=name,
            sha256=hashes.get(name),
            verdict=verdict,
            gates=gates,
            permissions=perms,
        )
        st.card = issue_card(st, source=source, pack_root=str(pack_root))
        skills_out.append(st)

    # Pack verdict
    if any(not g.available for g in pack_gates.values()):
        pack_verdict = Verdict.REFUSED
    elif any(s.verdict is Verdict.MALICIOUS for s in skills_out):
        pack_verdict = Verdict.MALICIOUS
    elif skills_out and all(s.verdict is Verdict.CLEAN for s in skills_out) and all(
        g.ok for g in pack_gates.values() if g.name != "policy" or require_policy
    ):
        # policy must pass when required
        if require_policy and not pack_gates["policy"].ok:
            pack_verdict = Verdict.REFUSED
        else:
            pack_verdict = Verdict.CLEAN
    elif any(s.verdict is Verdict.SUSPICIOUS for s in skills_out):
        pack_verdict = Verdict.SUSPICIOUS
    else:
        pack_verdict = Verdict.REFUSED

    ok = pack_verdict is Verdict.CLEAN
    return TrustReport(
        pack_root=str(pack_root),
        skill_count=len(skills_out),
        ok=ok,
        verdict=pack_verdict,
        skills=skills_out,
        pack_gates=pack_gates,
        tool_version=__version__,
        source=source,
    )


def write_cards(report: TrustReport, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for skill in report.skills:
        path = out_dir / f"{skill.name}.skillcard.json"
        path.write_text(
            json.dumps(skill.card, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    summary = out_dir / "pack.trust.json"
    summary.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    paths.append(summary)
    return paths
