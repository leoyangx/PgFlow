# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow Windows build
# Usage: pyinstaller build/windows/pgflow.spec

import sys
import litellm
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

ROOT = Path(SPECPATH).parent.parent  # repo root
LITELLM_DIR = Path(litellm.__file__).parent

# Insert ROOT so collect_submodules can find nanobot (requires pip install -e .)
sys.path.insert(0, str(ROOT))

# Collect all nanobot submodules (hiddenimports)
nanobot_hidden = collect_submodules("nanobot")

a = Analysis(
    [str(ROOT / "nanobot" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Ship nanobot Python source as data files — guarantees every .py is present
        # regardless of PyInstaller's static analysis result.
        # A runtime hook adds this to sys.path so imports work normally.
        (str(ROOT / "nanobot"), "nanobot_src/nanobot"),
        # Include all template markdown files
        (str(ROOT / "nanobot" / "templates"), "nanobot/templates"),
        # Include built-in skills
        (str(ROOT / "nanobot" / "skills"), "nanobot/skills"),
        # Include bridge (WhatsApp bridge binaries)
        (str(ROOT / "bridge"), "nanobot/bridge"),
        # litellm model pricing data (required at runtime, missed by PyInstaller)
        (str(LITELLM_DIR / "model_prices_and_context_window_backup.json"), "litellm"),
        # Project logo for tray icon
        (str(ROOT / "nanobot_logo.png"), "."),
    ],
    hiddenimports=nanobot_hidden + [
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
    runtime_hooks=[str(ROOT / "build" / "windows" / "rthook_nanobot.py")],
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
