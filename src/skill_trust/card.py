"""Skill Card issuer — NVIDIA-style trust artifact (local HMAC optional)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any

from skill_trust import __version__
from skill_trust.models import SkillTrust, Verdict


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sign_card(body: dict[str, Any], secret: str | None = None) -> dict[str, Any]:
    secret = secret if secret is not None else os.environ.get("TRUST_HMAC_SECRET")
    out = dict(body)
    if not secret:
        out["signature"] = None
        out["signature_alg"] = None
        return out
    digest = hmac.new(secret.encode("utf-8"), _canonical(body), hashlib.sha256).hexdigest()
    out["signature"] = digest
    out["signature_alg"] = "hmac-sha256"
    return out


def verify_signature(card: dict[str, Any], secret: str | None = None) -> bool:
    secret = secret if secret is not None else os.environ.get("TRUST_HMAC_SECRET")
    if not secret or not card.get("signature"):
        return False
    body = {k: v for k, v in card.items() if k not in {"signature", "signature_alg"}}
    expected = hmac.new(
        secret.encode("utf-8"), _canonical(body), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, str(card["signature"]))


def issue_card(skill: SkillTrust, *, source: str, pack_root: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "schema": "dup.skill_card.v1",
        "issuer": "dup-skill-trust-plane",
        "tool_version": __version__,
        "issued_at_ms": int(time.time() * 1000),
        "skill": skill.name,
        "sha256": skill.sha256,
        "source": source,
        "pack_root": pack_root,
        "verdict": skill.verdict.value,
        "gates": {k: v.to_dict() for k, v in skill.gates.items()},
        "permissions": dict(skill.permissions),
        "installable": skill.verdict is Verdict.CLEAN,
        "note": "fail-closed trust card — not a marketplace approval",
    }
    return sign_card(body)
