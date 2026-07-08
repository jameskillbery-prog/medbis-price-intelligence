# Build the Windows EXE

This guide builds a standalone Windows executable for MedBIS Price Intelligence.

## Requirements

- Windows 10 or later
- Python 3.12
- PowerShell
- Microsoft Edge or Google Chrome already installed

## Build

From the project root:

```powershell
.\scripts\build_exe.ps1
```

The build script will:

- create `.venv` if needed
- install Python dependencies
- run PyInstaller with `packaging/medbis_price_intelligence.spec`

It will **not** download a Playwright browser. Scrapers use installed Microsoft Edge first, then installed Google Chrome.

The EXE is created at:

```text
dist\MedBIS Price Intelligence.exe
```

## Run from source

```powershell
.\scripts\run_app.ps1
```

## Runtime data

The application stores runtime files under the working directory:

- `data/medbis_price_intelligence.sqlite3`
- `logs/app.log`

For a production installer, package the EXE with a signed installer and use a fixed application data directory under `%LOCALAPPDATA%`.

