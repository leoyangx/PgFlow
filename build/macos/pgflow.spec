# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow macOS build
# Usage: pyinstaller build/macos/pgflow.spec

from pathlib import Path

ROOT = Path(SPECPATH).parent.parent

a = Analysis(
    [str(ROOT / "nanobot" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "nanobot" / "templates"), "nanobot/templates"),
        (str(ROOT / "nanobot" / "skills"), "nanobot/skills"),
        (str(ROOT / "bridge"), "nanobot/bridge"),
    ],
    hiddenimports=[
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
        "nanobot.providers.litellm_provider",
        "nanobot.providers.custom_provider",
        "nanobot.providers.azure_openai_provider",
        "nanobot.providers.openai_codex_provider",
        "nanobot.store.skills",
        "nanobot.dashboard.server",
        "nanobot.service.manager",
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
    strip=True,
    upx=False,      # UPX not recommended on macOS
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=False,
    name="pgflow",
)
