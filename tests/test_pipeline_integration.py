from __future__ import annotations

from pathlib import Path

import pytest

from skill_trust.pipeline import verify_pack

FIXTURES = Path(__file__).parent / "fixtures"
AGENT = Path(r"C:\Users\vovun\Desktop\dup-agent-skills")


def _gates_available() -> bool:
    try:
        import policy_gate  # noqa: F401
        import skill_security  # noqa: F401
        import skills_eval  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.mark.skipif(not _gates_available(), reason="sibling gates not installed")
def test_verify_agent_skills_clean() -> None:
    assert AGENT.is_dir()
    report = verify_pack(AGENT, source="Gruver87/dup-agent-skills")
    assert report.skill_count == 10
    assert report.ok is True
    assert report.verdict.value == "clean"
    assert all(s.card.get("schema") == "dup.skill_card.v1" for s in report.skills)


@pytest.mark.skipif(not _gates_available(), reason="sibling gates not installed")
def test_fixture_allowlisted_skill() -> None:
    # Fixture only has no-futures-auto which is on default allowlist
    report = verify_pack(
        FIXTURES / "good_pack",
        source="Gruver87/dup-agent-skills",
    )
    assert report.skill_count == 1
    assert report.skills[0].name == "no-futures-auto"
    assert report.ok is True
