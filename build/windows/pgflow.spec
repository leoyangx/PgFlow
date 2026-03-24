# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow Windows build
# Usage: pyinstaller build/windows/pgflow.spec

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent.parent  # repo root

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
        # Store & Dashboard & Service
        "nanobot.store.skills",
        "nanobot.dashboard.server",
        "nanobot.service.manager",
        # Deps that PyInstaller misses
        "tiktoken_ext.openai_public",
        "tiktoken_ext",
        "readability",
        "charset_normalizer",
        "pydantic_settings",
        "loguru",
        "questionary",
        "prompt_toolkit",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "PIL"],
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
    icon=str(ROOT / "nanobot_logo.png"),  # replace with .ico if available
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
