#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Pack = Join-Path (Split-Path -Parent $Root) "dup-agent-skills"
$Cards = Join-Path $Root "cards\dup-agent-skills"

if (-not (Test-Path (Join-Path $Pack "skills"))) {
  Write-Error "dup-agent-skills missing at $Pack"
  exit 2
}

Set-Location $Root
python -m pip install -e . -q
python -m pip install -e ..\dup-skills-eval -e ..\dup-skill-security-scan -e ..\dup-policy-gate -q

python -m skill_trust verify $Pack --out $Cards
$verifyExit = $LASTEXITCODE
python -m skill_trust check-install $Pack
$instExit = $LASTEXITCODE
Write-Host "verify_exit=$verifyExit check_install_exit=$instExit"
exit $instExit
