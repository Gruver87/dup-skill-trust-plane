"""Adapters to sibling DUP gates — fail-closed if missing."""

from __future__ import annotations

from pathlib import Path

from skill_trust.models import GateResult


def run_skills_eval(pack_root: Path) -> GateResult:
    try:
        from skills_eval.runner import evaluate_pack
    except ImportError:
        return GateResult(
            name="static",
            ok=False,
            available=False,
            detail="dup-skills-eval not installed (pip install -e ../dup-skills-eval)",
        )
    report = evaluate_pack(pack_root)
    findings = [f.to_dict() for f in report.errors]
    return GateResult(
        name="static",
        ok=report.ok,
        available=True,
        detail=(
            f"skills_eval errors={len(report.errors)} "
            f"warns={len(report.warnings)} pin={report.pin}"
        ),
        findings=findings,
    )


def run_security_scan(
    pack_root: Path,
    *,
    source: str,
    skip_allowlist: bool = False,
) -> tuple[GateResult, GateResult, dict[str, str]]:
    """Return (security_gate, allowlist_gate, skill_hashes)."""
    try:
        from skill_security.allowlist import apply_allowlist, load_allowlist
        from skill_security.models import Severity
        from skill_security.scanner import list_skill_dirs, resolve_skills_root, scan_pack
    except ImportError:
        missing = GateResult(
            name="security",
            ok=False,
            available=False,
            detail="dup-skill-security-scan not installed",
        )
        al = GateResult(
            name="allowlist",
            ok=False,
            available=False,
            detail="dup-skill-security-scan not installed",
        )
        return missing, al, {}

    report = scan_pack(pack_root)
    pure_errors = [f for f in report.findings if f.severity is Severity.ERROR]
    sec = GateResult(
        name="security",
        ok=len(pure_errors) == 0,
        available=True,
        detail=f"heuristic errors={len(pure_errors)} skills={report.skill_count}",
        findings=[f.to_dict() for f in pure_errors],
    )

    if skip_allowlist:
        al = GateResult(name="allowlist", ok=True, available=True, detail="skipped")
        return sec, al, report.skill_hashes

    allowlist = load_allowlist()
    skills_root = resolve_skills_root(pack_root)
    names = [d.name for d in list_skill_dirs(skills_root)]
    denied = apply_allowlist(
        names, allowlist, source=source, hashes=report.skill_hashes
    )
    al = GateResult(
        name="allowlist",
        ok=len(denied) == 0,
        available=True,
        detail=f"denied={len(denied)}" if denied else "all allowlisted",
        findings=[{"skill": n, "reason": r} for n, r in denied],
    )
    return sec, al, report.skill_hashes


def run_policy_sanity() -> GateResult:
    """Confirm policy-gate FUTURES_BLOCK is available (ecosystem coherence)."""
    try:
        from policy_gate.engine import evaluate_intent
        from policy_gate.models import OrderIntent
    except ImportError:
        return GateResult(
            name="policy",
            ok=False,
            available=False,
            detail="dup-policy-gate not installed",
        )
    d = evaluate_intent(
        OrderIntent(
            symbol="BTCUSDT",
            side="buy",
            market="futures",
            dry_run=True,
        ),
        keys_present=False,
    )
    ok = (not d.allowed) and any("FUTURES" in r for r in d.reasons)
    return GateResult(
        name="policy",
        ok=ok,
        available=True,
        detail="FUTURES_BLOCK probe " + ("ok" if ok else "FAILED"),
        findings=[] if ok else [{"reasons": list(d.reasons)}],
    )


def list_skills(pack_root: Path) -> list[Path]:
    skills = pack_root / "skills"
    if not skills.is_dir():
        return []
    return sorted(
        p for p in skills.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
