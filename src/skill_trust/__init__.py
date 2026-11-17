"""DUP Skill Trust Plane — fail-closed control plane for Agent Skills."""

from __future__ import annotations

__version__ = "0.1.0"

from skill_trust.pipeline import TrustReport, verify_pack

__all__ = ["__version__", "TrustReport", "verify_pack"]
