#!/bin/bash
# PgFlow macOS build script
# Requirements: pip install pyinstaller, create-dmg (brew install create-dmg)
# Run from repo root: bash build/macos/build.sh

set -e
cd "$(dirname "$0")/../.."

APP_VERSION=$(python -c "from pgflow import __version__; print(__version__)")
DMG_NAME="PgFlow-${APP_VERSION}-macOS"

echo "[1/3] Installing build dependencies..."
pip install pyinstaller

echo "[2/3] Running PyInstaller..."
pyinstaller build/macos/pgflow.spec --clean --noconfirm

echo "[3/3] Creating .dmg..."
if ! command -v create-dmg &>/dev/null; then
    echo "WARNING: create-dmg not found. Install with: brew install create-dmg"
    echo "  Skipping DMG step. Standalone folder: dist/pgflow/"
else
    mkdir -p dist/dmg
    create-dmg \
        --volname "PgFlow" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --app-drop-link 450 185 \
        --no-internet-enable \
        "dist/${DMG_NAME}.dmg" \
        "dist/pgflow/"
    echo "Done! DMG: dist/${DMG_NAME}.dmg"
fi

echo ""
echo "Build complete."
echo "  Standalone: dist/pgflow/pgflow"
echo "  Run:        ./dist/pgflow/pgflow --help"
