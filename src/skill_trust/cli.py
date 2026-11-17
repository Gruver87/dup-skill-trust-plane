"""CLI: verify / cards / check-install / serve / status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skill_trust import __version__
from skill_trust.models import GateResult, Verdict
from skill_trust.pipeline import verify_pack, write_cards
from skill_trust.server import serve


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dup-skill-trust",
        description=(
            "Fail-closed Agent Skills trust plane "
            "(eval + security + allowlist + sandbox profile + Skill Cards)."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Show tool version and gate import status")

    demo = sub.add_parser(
        "demo",
        help="Verify packaged fixture pack (no Desktop paths; gates optional)",
    )
    demo.add_argument("--out", type=Path, default=Path("cards/demo"))
    demo.add_argument(
        "--require-gates",
        action="store_true",
        help="Fail if sibling gates are not installed (default: best-effort)",
    )

    v = sub.add_parser("verify", help="Run full trust pipeline on a skills pack")
    v.add_argument("pack_root", type=Path)
    v.add_argument("--source", default="Gruver87/dup-agent-skills")
    v.add_argument("--skip-allowlist", action="store_true")
    v.add_argument("--no-policy", action="store_true")
    v.add_argument("--out", type=Path, default=None)
    v.add_argument("--json", action="store_true")

    c = sub.add_parser("cards", help="Verify and write Skill Cards")
    c.add_argument("pack_root", type=Path)
    c.add_argument("--source", default="Gruver87/dup-agent-skills")
    c.add_argument("--out", type=Path, default=Path("cards"))

    inst = sub.add_parser("check-install", help="ALLOW only when verdict is clean")
    inst.add_argument("pack_root", type=Path)
    inst.add_argument("--source", default="Gruver87/dup-agent-skills")

    srv = sub.add_parser("serve", help="Self-host HTTP trust API (local)")
    srv.add_argument("--host", default=None)
    srv.add_argument("--port", type=int, default=None)
    return p


def _print_summary(report) -> None:
    print(
        f"skill_trust {report.verdict.value.upper()} "
        f"ok={report.ok} n={report.skill_count} source={report.source}"
    )
    for name, gate in report.pack_gates.items():
        flag = "PASS" if gate.ok else ("MISS" if not gate.available else "FAIL")
        print(f" - pack/{name}: {flag} — {gate.detail}")
    for skill in report.skills:
        short = (skill.sha256 or "")[:12]
        print(f" - skill/{skill.name}: {skill.verdict.value} sha={short}")


def _import_status() -> dict:
    gates: dict[str, dict] = {}
    for label, mod in (
        ("static", "skills_eval"),
        ("security", "skill_security"),
        ("policy", "policy_gate"),
    ):
        try:
            __import__(mod)
            gates[label] = GateResult(label, True, True, f"{mod} import ok").to_dict()
        except ImportError as exc:
            gates[label] = GateResult(
                label, False, False, f"{mod} missing: {exc}"
            ).to_dict()
    return gates


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "status":
        print(
            json.dumps(
                {
                    "tool_version": __version__,
                    "gates": _import_status(),
                    "note": "control plane — not a marketplace; FUTURES_BLOCK via policy-gate",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.cmd == "demo":
        pack = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "good_pack"
        print(f"skill_trust DEMO pack={pack}")
        gates = _import_status()
        missing = [k for k, v in gates.items() if not v.get("available", True)]
        if missing:
            print(f"gates missing (optional for demo): {missing}")
        if args.require_gates and missing:
            print(f"FAIL: --require-gates and missing {missing}", file=sys.stderr)
            return 2
        if not gates.get("static", {}).get("available", False):
            print(
                "DEMO PARTIAL — install dup-skills-eval (+ security-scan, policy-gate) "
                "for full plane; status-only OK",
            )
            print(json.dumps({"tool_version": __version__, "gates": gates}, indent=2))
            return 0
        require_policy = gates.get("policy", {}).get("available", False)
        # Fixture skill name `no-futures-auto` is on the published allowlist.
        skip_al = not gates.get("security", {}).get("available", False)
        report = verify_pack(
            pack,
            source="Gruver87/dup-agent-skills",
            skip_allowlist=skip_al,
            require_policy=require_policy,
        )
        _print_summary(report)
        paths = write_cards(report, args.out)
        print(f"cards → {args.out} ({len(paths)} files)")
        if missing:
            print("DEMO PARTIAL (sibling gates missing) — cards written anyway")
            return 0
        return 0 if report.ok else 1

    if args.cmd == "serve":
        serve(host=args.host, port=args.port)
        return 0

    if args.cmd == "verify":
        report = verify_pack(
            args.pack_root,
            source=args.source,
            skip_allowlist=args.skip_allowlist,
            require_policy=not args.no_policy,
        )
        _print_summary(report)
        if args.out:
            paths = write_cards(report, args.out)
            print(f"wrote {len(paths)} files → {args.out}")
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return 0 if report.ok else 1

    if args.cmd == "cards":
        report = verify_pack(args.pack_root, source=args.source)
        paths = write_cards(report, args.out)
        _print_summary(report)
        print(f"cards → {args.out} ({len(paths)} files)")
        return 0 if report.ok else 1

    if args.cmd == "check-install":
        report = verify_pack(args.pack_root, source=args.source)
        _print_summary(report)
        if report.ok and report.verdict is Verdict.CLEAN:
            print("check-install ALLOW")
            return 0
        print("check-install REFUSE", file=sys.stderr)
        return 1

    print("unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
