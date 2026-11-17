#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python -m pip install -e ".[dev]" -q
# Best-effort sibling gates from Desktop
$Desktop = Split-Path $Root -Parent
foreach ($sib in @("dup-skills-eval", "dup-skill-security-scan", "dup-policy-gate")) {
  $path = Join-Path $Desktop $sib
  if (Test-Path $path) {
    python -m pip install -e $path -q
  }
}
python -m skill_trust demo
exit $LASTEXITCODE
