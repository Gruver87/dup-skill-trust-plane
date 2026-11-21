# Start here (plain language)

**What is this?** A small local service that checks Agent Skills / MCP packages the way a careful company would: static checks, security heuristics, policy probes → a **Skill Card**.

**What it is not:** a marketplace, a paid audit firm, or a promise that “AI agents are safe forever.”

M8ven badge on the README means: the **publisher claimed** the public listing. That is identity/listing hygiene — **not** a full security audit and **not** a soak PASS.

---

## 5-minute demo (no API keys)

```powershell
cd dup-skill-trust-plane
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\scripts\demo.ps1
# or: make demo
```

You should see fixture cards printed / written without talking to KuCoin or any exchange.

---

## Full stack (optional)

If sibling repos sit next to this folder:

```powershell
python -m pip install -e ../dup-skills-eval -e ../dup-skill-security-scan -e ../dup-policy-gate
```

Easiest path for beginners: bootstrap everything from [`dup-lab`](https://github.com/Gruver87/dup-lab) (`.\scripts\bootstrap.ps1`).

---

## Self-host API (advanced)

See the main [README](../README.md) for Docker / `POST /v1/verify`.  
Do not put live trading keys into this service — it is a **trust plane**, not a broker.

---

## Russian summary

Это «проходная» для навыков ИИ: проверяет пакет → выдаёт карточку доверия.  
Бейдж M8ven = подтверждённый издатель в публичном индексе, не платная экспертиза.  
Демо без ключей: `.\scripts\demo.ps1`. Для новичка удобнее начать с `dup-lab`.
