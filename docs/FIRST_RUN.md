# First Run Guide

Use this checklist after installing or launching MedBIS Price Intelligence for the first time.

## 1. Start the app

Run:

```text
MedBIS Price Intelligence.exe
```

or from source:

```powershell
.\scripts\run_app.ps1
```

## 2. Import MedBIS products

Open **Import Products** and choose the MedBIS Excel or CSV product list.

The importer automatically detects product name, brand, SKU, quantity, strength, pack size, cost price, and selling price columns.

## 3. Check settings

Open the **Settings** tab and review:

- Cache age days
- Scraper concurrency
- Products per run

Lower concurrency if competitor sites are slow or blocking requests.

## 4. Run a small search

Use **Run Test Search** first. This checks Medisave and Medical World for a small product sample.

## 5. Run all competitors

Use **Run All Competitors** after the small search works.

## 6. Export report

Use **Export Report** to create the Excel workbook.

## Runtime location

Runtime files are stored under:

```text
%LOCALAPPDATA%\MedBIS Price Intelligence
```

