# MedBIS Price Intelligence

MedBIS Price Intelligence is a Windows desktop application for importing MedBIS product data, storing it in SQLite, and preparing the foundation for competitor price intelligence workflows.

This ZIP contains **Milestone 1 only**:

- Project structure
- SQLite database models
- SQLAlchemy session/repository layer
- CustomTkinter desktop shell
- Excel/CSV import engine with automatic column detection
- Basic dashboard statistics and import history

## Milestone 2 Additions

This package also includes the Milestone 2 foundation:

- RapidFuzz weighted matching engine
- Automatic match/review/ignore thresholds
- Base scraper contract for every competitor website
- Normalised scraper query/result models
- Async Playwright scraper runner with concurrency limit
- SQLite-backed scraper search cache

## Milestone 3 Additions

Milestone 3 adds the first live scraper integrations:

- Medisave scraper
- Medical World scraper
- Shared ecommerce result parser
- JSON-LD product extraction where available
- Persistence of accepted matches and competitor price history
- Desktop "Run Test Search" action for the first imported products

## Milestone 4 Additions

Milestone 4 expands scraper coverage to all requested competitors:

- Medical World
- Medical Dressings
- Medisave
- Amazon UK
- Algeos
- Daylong
- MediSupplies
- Chemist.net
- eSupplies Medical
- Care Supply Store
- EasyMeds Health
- WMS

It also adds a scraper registry, all-competitor desktop run action, search run count, and match count.

## Milestone 5 Additions

Milestone 5 adds Excel reporting and price intelligence calculations:

- Summary worksheet
- Competitor Prices worksheet
- Products Above Market worksheet
- Margin Opportunities worksheet
- Historical Prices worksheet
- Products Without Matches worksheet
- Suggested price increases for products priced well below market average
- Desktop "Export Report" action

## Milestone 6 Additions

Milestone 6 improves the desktop dashboard:

- Overview tab with match quality and run activity charts
- Products tab with live search/filtering
- Matches tab showing recent competitor matches
- History tab showing recent import and scraper runs
- Dashboard counters for products, competitors, imports, matches, and searches

## Milestone 7 Additions

Milestone 7 adds Windows packaging:

- PyInstaller spec file
- Windows file version metadata
- Frozen app launcher
- PowerShell build script
- PowerShell source-run script
- Windows EXE build guide
- Scraper browser launch policy using installed Microsoft Edge or Chrome

The build does **not** download a Playwright browser.

## Milestone 8 Additions

Milestone 8 hardens runtime behaviour:

- Stores app data under `%LOCALAPPDATA%\MedBIS Price Intelligence`
- Adds typed runtime settings
- Adds Settings tab for cache age, concurrency, and products per run
- Adds Logs tab showing recent application log lines
- Makes individual scraper failures non-fatal
- Applies configured cache and concurrency settings to scraper runs

## Milestone 9 Additions

Milestone 9 adds release and installer polish:

- First-run guide
- Release checklist
- Known limitations document
- Inno Setup installer template
- Release ZIP script
- Distribution notes for EXE packaging

Suggested first commit message after upload:

```text
Initialize MedBIS Price Intelligence desktop app
```

## Requirements

- Python 3.12
- Windows 10 or later

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```powershell
python -m medbis_price_intelligence
```

## Importing Products

The importer accepts `.xlsx`, `.xls`, and `.csv` files. It automatically maps likely columns for:

- SKU
- Product name
- Brand
- Pack size
- Quantity
- Strength
- Cost price
- Selling price
- Category
- Barcode

Imported products are stored in SQLite at:

```text
data/medbis_price_intelligence.sqlite3
```

## Test

```powershell
python -m compileall src tests
python -m pytest
```

## Next Milestone

Milestone 10 should focus on full validation, bug fixing, and preparing a first tagged release.

Suggested second commit message:

```text
Add matching engine and scraper framework
```

Suggested third commit message:

```text
Add Medisave and Medical World scrapers
```

Suggested fourth commit message:

```text
Add remaining competitor scrapers and run dashboard stats
```

Suggested fifth commit message:

```text
Add Excel reporting and price intelligence calculations
```

Suggested sixth commit message:

```text
Add dashboard charts filters and history views
```

Suggested seventh commit message:

```text
Add PyInstaller packaging for Windows EXE
```

Suggested eighth commit message:

```text
Add settings logging and scraper resilience
```

Suggested ninth commit message:

```text
Add installer template and release documentation
```
