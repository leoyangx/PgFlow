# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow Windows build
# Usage: pyinstaller build/windows/pgflow.spec

import sys
import litellm
from pathlib import Path

ROOT = Path(SPECPATH).parent.parent  # repo root
LITELLM_DIR = Path(litellm.__file__).parent

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
    hiddenimports=[
        # Channels
        "nanobot.channels.telegram",
        "nanobot.channels.discord",
        "nanobot.channels.slack",
        "nanobot.channels.dingtalk",
        "nanobot.channels.feishu",
        "nanobot.channels.qq",
        "nanobot.channels.wecom",
        "nanobot.channels.weixin",
        "nanobot.channels.whatsapp",
        "nanobot.channels.email",
        "nanobot.channels.matrix",
        "nanobot.channels.mochat",
        # Providers
        "nanobot.providers.litellm_provider",
        "nanobot.providers.custom_provider",
        "nanobot.providers.azure_openai_provider",
        "nanobot.providers.openai_codex_provider",
        # Store & Dashboard & Service & Tray
        "nanobot.store.skills",
        "nanobot.dashboard.server",
        "nanobot.service.manager",
        "nanobot.tray.app",
        "nanobot.cli.onboard",
        "nanobot.cli.models",
        "nanobot.cli.stream",
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
