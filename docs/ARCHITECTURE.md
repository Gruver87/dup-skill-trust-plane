# Architecture — dup-skill-trust-plane

**Org:** DUP Labs · **Role:** Agent Skills **trust / control plane** (not a marketplace)

## Why

Enterprises installing third-party Agent Skills need a fail-closed pipeline after
ClawHub-class supply-chain incidents. This product orchestrates:

```text
pack
  → static/honesty (dup-skills-eval)
  → security heuristics + allowlist (dup-skill-security-scan)
  → sandbox permission profile (this repo)
  → policy coherence probe (dup-policy-gate FUTURES_BLOCK)
  → Skill Card (dup.skill_card.v1) + optional HMAC
  → check-install ALLOW|REFUSE
```

## Verdicts

| Verdict | Meaning |
|---------|---------|
| `clean` | all required gates pass — installable |
| `suspicious` | warnings / review — not installable by default |
| `refused` | hard gate fail or missing sibling gate |
| `malicious` | security ERROR (secrets, download-exec, …) |

Missing sibling packages ⇒ **refuse** (`fail_if_gate_missing`).

## Self-host

```powershell
docker compose up --build
# POST http://127.0.0.1:8788/v1/verify  {"pack_root":"/packs/dup-agent-skills"}
```

## Related

- [`dup-skills-eval`](https://github.com/Gruver87/dup-skills-eval)
- [`dup-skill-security-scan`](https://github.com/Gruver87/dup-skill-security-scan)
- [`dup-policy-gate`](https://github.com/Gruver87/dup-policy-gate)
- [`dup-agent-skills`](https://github.com/Gruver87/dup-agent-skills)
