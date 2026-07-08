$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ReleaseDir = "release"
$ZipPath = Join-Path $ReleaseDir "MedBIS-Price-Intelligence-release.zip"

if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir | Out-Null
}

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

Compress-Archive `
    -Path "dist\MedBIS Price Intelligence.exe", "docs\FIRST_RUN.md", "docs\RELEASE_CHECKLIST.md" `
    -DestinationPath $ZipPath `
    -Force

Write-Host "Release package created:"
Write-Host $ZipPath

