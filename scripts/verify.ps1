# Run all available FamilyShield checks from the repository root.
# Requires backend Python dependencies and frontend npm dependencies to be installed.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "== Backend tests ==" -ForegroundColor Cyan
python -m pytest backend/tests -q
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }

Write-Host "== ML training ==" -ForegroundColor Cyan
python -m ml.train_model
if ($LASTEXITCODE -ne 0) { throw "ML training failed" }

Write-Host "== ML evaluation ==" -ForegroundColor Cyan
python -m ml.evaluate
if ($LASTEXITCODE -ne 0) { throw "ML evaluation failed" }

Write-Host "== Frontend production build ==" -ForegroundColor Cyan
Push-Location (Join-Path $root "frontend")
cmd /c "npm run build"
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Frontend build failed" }
Pop-Location

Write-Host "All checks passed." -ForegroundColor Green
