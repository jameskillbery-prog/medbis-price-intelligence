# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


block_cipher = None
project_root = Path.cwd()

customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all("customtkinter")
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all("pandas")
playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all("playwright")

a = Analysis(
    ["src/medbis_price_intelligence/launcher.py"],
    pathex=[str(project_root), str(project_root / "src")],
    binaries=customtkinter_binaries + pandas_binaries + playwright_binaries,
    datas=customtkinter_datas + pandas_datas + playwright_datas,
    hiddenimports=[
        "openpyxl",
        "rapidfuzz",
        "sqlalchemy",
        "playwright.async_api",
        *customtkinter_hiddenimports,
        *pandas_hiddenimports,
        *playwright_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "mypy", "ruff"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MedBIS Price Intelligence",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="packaging/version_info.txt",
)

