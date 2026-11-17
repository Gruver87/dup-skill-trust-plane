from __future__ import annotations

from skill_trust.card import issue_card, sign_card, verify_signature
from skill_trust.models import GateResult, SkillTrust, Verdict


def test_sign_and_verify(monkeypatch) -> None:
    monkeypatch.setenv("TRUST_HMAC_SECRET", "test-secret-not-for-prod")
    body = {"skill": "x", "verdict": "clean"}
    signed = sign_card(body)
    assert signed["signature"]
    assert verify_signature(signed) is True
    signed["verdict"] = "tampered"
    assert verify_signature(signed) is False


def test_issue_card_structure() -> None:
    st = SkillTrust(
        name="no-futures-auto",
        sha256="abc",
        verdict=Verdict.CLEAN,
        gates={"static": GateResult("static", True)},
        permissions={"network": False},
    )
    card = issue_card(st, source="Gruver87/dup-agent-skills", pack_root="/tmp")
    assert card["schema"] == "dup.skill_card.v1"
    assert card["installable"] is True
