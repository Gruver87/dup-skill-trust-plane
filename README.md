# DUP Skill Trust Plane

[![ci](https://github.com/Gruver87/dup-skill-trust-plane/actions/workflows/ci.yml/badge.svg)](https://github.com/Gruver87/dup-skill-trust-plane/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/Gruver87/dup-skill-trust-plane?display_name=tag)](https://github.com/Gruver87/dup-skill-trust-plane/releases)
[![M8ven Score](https://m8ven.ai/badge/mcp/gruver87/dup-skill-trust-plane)](https://m8ven.ai/mcp/gruver87/dup-skill-trust-plane?s=readme)

**Org:** [DUP Labs](https://github.com/Gruver87) · **Author:** Uladzimir Dabranski  
**Version:** `0.1.0` · Fail-closed **Agent Skills control plane** (not a marketplace)

Universal trust plane for Agent Skills / MCP installs: compose static eval, security
allowlist, sandbox profile, and policy probes into Skill Cards. Domain-agnostic —
fintech, medicine-adjacent tooling, DevOps agents — crypto radar is the first stand.

Orchestrates the industrial gate chain companies need after skill-supply-chain attacks:

1. **Static / honesty** — [`dup-skills-eval`](https://github.com/Gruver87/dup-skills-eval)  
2. **Security + allowlist** — [`dup-skill-security-scan`](https://github.com/Gruver87/dup-skill-security-scan)  
3. **Sandbox profile** — least-privilege declaration (network/creds deny by default)  
4. **Policy probe** — [`dup-policy-gate`](https://github.com/Gruver87/dup-policy-gate) `FUTURES_BLOCK`  
5. **Skill Cards** — `dup.skill_card.v1` (+ optional HMAC)  

Self-host via Docker. No KuCoin keys. No soak.

## Quick demo (fixtures)

```bash
git clone https://github.com/Gruver87/dup-skill-trust-plane.git && cd dup-skill-trust-plane
python -m pip install -e ".[dev]"
# optional full plane:
# pip install -e ../dup-skills-eval -e ../dup-skill-security-scan -e ../dup-policy-gate
make demo
# or: python -m skill_trust demo
# Windows: .\scripts\demo.ps1
```

## Install (with sibling gates)

```bash
python -m pip install -e ".[dev]"
python -m pip install -e ../dup-skills-eval -e ../dup-skill-security-scan -e ../dup-policy-gate
make test   # or: .\scripts\test_all.ps1
```

## CLI

```bash
python -m skill_trust status
python -m skill_trust demo
python -m skill_trust verify ../dup-agent-skills --out ./cards
python -m skill_trust check-install ../dup-agent-skills
python -m skill_trust serve --host 127.0.0.1 --port 8788
```

`check-install` → exit `0` ALLOW only when pack verdict is **clean**.

## HTTP (self-host)

```bash
# Terminal A
python -m skill_trust serve --host 127.0.0.1 --port 8788

# Terminal B
curl -s -X POST http://127.0.0.1:8788/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"pack_root":"/path/to/dup-agent-skills"}'

# Docker
docker compose up --build
# POST http://127.0.0.1:8788/v1/verify
# {"pack_root":"/packs/dup-agent-skills","write_cards":true}
```

`GET /v1/health` — liveness. `POST /v1/verify` — full trust pipeline (fail-closed).

## Ecosystem

| Repo | Role |
|------|------|
| [`dup-agent-skills`](https://github.com/Gruver87/dup-agent-skills) | Pack under trust |
| [`dup-skills-eval`](https://github.com/Gruver87/dup-skills-eval) | Static / honesty gate |
| [`dup-skill-security-scan`](https://github.com/Gruver87/dup-skill-security-scan) | Heuristics + allowlist |
| [`dup-policy-gate`](https://github.com/Gruver87/dup-policy-gate) | FUTURES_BLOCK coherence |
| [`dup-evidence-graph`](https://github.com/Gruver87/dup-evidence-graph) | Evidence / claims map |

## License

MIT — [`LICENSE`](LICENSE).
