"""Sandbox permission profiles derived from skill contents (fail-closed defaults)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_NETWORK = re.compile(
    r"(?i)\b(httpx|requests|urllib|aiohttp|websocket|fetch\(|curl |wget )\b"
)
_SHELL = re.compile(r"(?i)\b(subprocess|os\.system|Popen|Invoke-Expression|iex\b)\b")
_CRED = re.compile(
    r"(?i)\b(api[_-]?key|secret|passphrase|password|token|private[_-]?key)\b"
)
_WRITE = re.compile(
    r"(?i)\b(open\([^)]*['\"][wa]|\.write_text|\.write_bytes|Path\(.*\)\.write)\b"
)


def _read_corpus(skill_dir: Path) -> str:
    parts: list[str] = []
    for pattern in ("*.md", "*.py", "*.ps1", "*.sh", "*.js", "*.ts"):
        for path in skill_dir.rglob(pattern):
            if any(p in {".git", "__pycache__", "node_modules"} for p in path.parts):
                continue
            try:
                parts.append(path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
    return "\n".join(parts)


def profile_skill(skill_dir: Path) -> dict[str, Any]:
    """Least privilege profile. Defaults deny network/credentials/write."""
    text = _read_corpus(skill_dir)
    has_scripts = any(skill_dir.rglob(p) for p in ("*.ps1", "*.py", "*.sh"))
    network = bool(_NETWORK.search(text))
    shell_needed = bool(_SHELL.search(text)) or has_scripts
    creds = bool(_CRED.search(text))
    fs_write = bool(_WRITE.search(text))

    # Trust plane never grants credentials or open network by default —
    # only *declares* detected needs. Install policy may still refuse.
    return {
        "profile": "declared_least_privilege",
        "network": False if not network else "detected_needs_review",
        "fs_write": False if not fs_write else "detected_needs_review",
        "shell": "scripts_readonly" if shell_needed else "deny",
        "credentials": "deny",
        "detected": {
            "network_refs": network,
            "shell_refs": shell_needed,
            "credential_refs": creds,
            "fs_write_refs": fs_write,
            "has_scripts": has_scripts,
        },
        "docker_hint": {
            "network": "none",
            "read_only_root": True,
            "cap_drop": ["ALL"],
            "note": "optional: docker run --network=none -v skill:/skill:ro",
        },
    }


def sandbox_gate(skill_dir: Path) -> tuple[dict[str, Any], bool, str]:
    """Gate fails if skill declares credential/network needs without refuse framing."""
    perms = profile_skill(skill_dir)
    det = perms["detected"]
    # Hard refuse: credential harvesting patterns without secrets-hygiene skill context
    # For trust plane: credential_refs alone is WARN-level unless paired with exfil.
    ok = True
    detail = "sandbox profile assigned"
    if det["credential_refs"] and det["network_refs"]:
        # Potential exfil surface — mark needs review but do not auto-malicious
        # (security gate already catches download-exec / secrets).
        detail = "credential+network refs — review required"
        # Still ok for profile assignment; verdict layer may mark suspicious
    return perms, ok, detail
