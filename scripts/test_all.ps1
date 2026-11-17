#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Assert-NativeExit {
  param([Parameter(Mandatory)][string]$Label)
  if ($null -eq $LASTEXITCODE) { return }
  if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit $LASTEXITCODE" }
}

Write-Host "== install trust-plane + sibling gates =="
python -m pip install -e ".[dev]" -q
Assert-NativeExit "pip-self"
$siblings = @(
  (Join-Path (Split-Path -Parent $Root) "dup-skills-eval"),
  (Join-Path (Split-Path -Parent $Root) "dup-skill-security-scan"),
  (Join-Path (Split-Path -Parent $Root) "dup-policy-gate")
)
foreach ($s in $siblings) {
  if (Test-Path $s) {
    python -m pip install -e $s -q
    Assert-NativeExit "pip-$([IO.Path]::GetFileName($s))"
  }
}

python -m ruff check src tests
Assert-NativeExit "ruff"
python -m pytest -q
Assert-NativeExit "pytest"
Write-Host "test_all PASS"
exit 0
