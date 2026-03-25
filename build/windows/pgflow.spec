# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow Windows build
# Usage: pyinstaller build/windows/pgflow.spec

import sys
import litellm
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).parent.parent  # repo root
LITELLM_DIR = Path(litellm.__file__).parent

# Collect ALL nanobot submodules so nothing is missed
sys.path.insert(0, str(ROOT))
nanobot_all = collect_submodules("nanobot")

a = Analysis(
    [str(ROOT / "nanobot" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
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
    hiddenimports=nanobot_all + [
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
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    icon=str(ROOT / "pgflow.ico"),  # replace with .ico if available
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
