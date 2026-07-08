$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m PyInstaller ".\packaging\medbis_price_intelligence.spec" --clean --noconfirm

Write-Host ""
Write-Host "Build complete:"
Write-Host "dist\MedBIS Price Intelligence.exe"
Write-Host ""
Write-Host "No Playwright browser is downloaded. Scrapers use installed Microsoft Edge or Chrome."

