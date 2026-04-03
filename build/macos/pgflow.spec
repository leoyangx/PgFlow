# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PgFlow macOS build
# Usage: pyinstaller build/macos/pgflow.spec

from pathlib import Path

ROOT = Path(SPECPATH).parent.parent

a = Analysis(
    [str(ROOT / "pgflow" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "pgflow" / "templates"), "pgflow/templates"),
        (str(ROOT / "pgflow" / "skills"), "pgflow/skills"),
        (str(ROOT / "bridge"), "pgflow/bridge"),
    ],
    hiddenimports=[
        "pgflow.channels.telegram",
        "pgflow.channels.discord",
        "pgflow.channels.slack",
        "pgflow.channels.dingtalk",
        "pgflow.channels.feishu",
        "pgflow.channels.qq",
        "pgflow.channels.wecom",
        "pgflow.channels.weixin",
        "pgflow.channels.whatsapp",
        "pgflow.channels.email",
        "pgflow.channels.matrix",
        "pgflow.channels.mochat",
        "pgflow.providers.azure_openai_provider",
        "pgflow.providers.openai_codex_provider",
        "pgflow.store.skills",
        "pgflow.dashboard.server",
        "pgflow.service.manager",
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
