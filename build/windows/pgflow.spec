# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow Windows build
# Usage: pyinstaller build/windows/pgflow.spec

import sys
import pgflow
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

ROOT = Path(SPECPATH).parent.parent  # repo root

# Insert ROOT so collect_submodules can find pgflow (requires pip install -e .)
sys.path.insert(0, str(ROOT))

# Collect all pgflow submodules (hiddenimports)
pgflow_hidden = collect_submodules("pgflow")

a = Analysis(
    [str(ROOT / "pgflow" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Ship pgflow Python source as data files — guarantees every .py is present
        # regardless of PyInstaller's static analysis result.
        # A runtime hook adds this to sys.path so imports work normally.
        (str(ROOT / "pgflow"), "pgflow_src/pgflow"),
        # Include all template markdown files
        (str(ROOT / "pgflow" / "templates"), "pgflow/templates"),
        # Include built-in skills
        (str(ROOT / "pgflow" / "skills"), "pgflow/skills"),
        # Include bridge (WhatsApp bridge binaries)
        (str(ROOT / "bridge"), "pgflow/bridge"),
        # Project logo for tray icon
        (str(ROOT / "pgflow_logo.png"), "."),
    ],
    hiddenimports=pgflow_hidden + [
        # Deps that PyInstaller misses
        "tiktoken_ext.openai_public",
        "tiktoken_ext",
        "readability",
        "charset_normalizer",
        "pydantic_settings",
        "loguru",
        "questionary",
        "prompt_toolkit",
        # Tray deps
        "pystray",
        "pystray._win32",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "PIL.ImageEnhance",
        # pywin32 — required by pystray._win32
        "win32api",
        "win32con",
        "win32gui",
        "win32gui_struct",
        "pywintypes",
        "win32print",
    ],
    hookspath=[str(ROOT / "build" / "windows" / "hooks")],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "build" / "windows" / "rthook_pgflow.py")],
    excludes=["tkinter", "matplotlib", "numpy", "pandas"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pgflow",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # CLI app — keep console window
    icon=str(ROOT / "pgflow.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="pgflow",
)
