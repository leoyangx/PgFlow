@echo off
:: PgFlow Windows build script
:: Make sure your venv is activated before running.
:: Run from repo root: build\windows\build.bat

setlocal
cd /d "%~dp0..\.."

echo [1/3] Installing build dependencies...
python -m pip install pyinstaller pystray Pillow pywin32
if errorlevel 1 (
    echo ERROR: pip failed. Make sure your venv is activated.
    exit /b 1
)

echo [2/3] Running PyInstaller...
python -m PyInstaller build\windows\pgflow.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller failed
    exit /b 1
)

echo [3/3] Building NSIS installer...
where makensis >nul 2>&1
if errorlevel 1 (
    echo WARNING: makensis not found. Skipping installer creation.
    echo   Install NSIS from https://nsis.sourceforge.io/ and run manually:
    echo   makensis build\windows\installer.nsi
) else (
    makensis build\windows\installer.nsi
    if errorlevel 1 (
        echo ERROR: NSIS build failed
        exit /b 1
    )
    echo Done! Installer: dist\PgFlow-Setup.exe
)

echo.
echo Build complete. Standalone folder: dist\pgflow\
echo Test it: dist\pgflow\pgflow.exe --help
endlocal
