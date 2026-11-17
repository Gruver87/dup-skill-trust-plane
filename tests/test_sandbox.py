from __future__ import annotations

from pathlib import Path

from skill_trust.sandbox import profile_skill

FIXTURES = Path(__file__).parent / "fixtures"


def test_profile_defaults_deny_network() -> None:
    perms = profile_skill(FIXTURES / "good_pack" / "skills" / "no-futures-auto")
    assert perms["network"] is False
    assert perms["credentials"] == "deny"
