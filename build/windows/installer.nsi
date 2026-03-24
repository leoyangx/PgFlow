; NSIS installer script for PgFlow
; Requires NSIS 3.x: https://nsis.sourceforge.io/
; Build: makensis build\windows\installer.nsi

!define APP_NAME "PgFlow"
!define APP_VERSION "0.1.0"
!define APP_EXE "pgflow.exe"
!define INSTALL_DIR "$PROGRAMFILES64\PgFlow"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\PgFlow"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "..\..\dist\PgFlow-${APP_VERSION}-Setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\PgFlow" "InstallPath"
RequestExecutionLevel admin
Unicode True

; ─── Pages ───────────────────────────────────────────────────────────────────
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

; ─── Installer sections ──────────────────────────────────────────────────────
Section "PgFlow (required)" SecMain
    SectionIn RO
    SetOutPath "$INSTDIR"

    ; Copy all files from PyInstaller dist/pgflow/
    File /r "..\..\dist\pgflow\*.*"

    ; Write install path to registry
    WriteRegStr HKLM "Software\PgFlow" "InstallPath" "$INSTDIR"

    ; Add to system PATH
    EnVar::SetHKLM
    EnVar::AddValue "PATH" "$INSTDIR"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Add uninstall entry to Windows registry
    WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${UNINSTALL_KEY}" "Publisher" "PgFlow"
    WriteRegStr HKLM "${UNINSTALL_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoRepair" 1

    ; Desktop shortcut — opens terminal with pgflow
    CreateShortcut "$DESKTOP\PgFlow.lnk" "cmd.exe" '/k "pgflow --help"' "$INSTDIR\${APP_EXE}"

    ; Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\PgFlow"
    CreateShortcut "$SMPROGRAMS\PgFlow\PgFlow.lnk" "cmd.exe" '/k "pgflow --help"' "$INSTDIR\${APP_EXE}"
    CreateShortcut "$SMPROGRAMS\PgFlow\Uninstall PgFlow.lnk" "$INSTDIR\Uninstall.exe"

SectionEnd

; ─── Uninstaller ─────────────────────────────────────────────────────────────
Section "Uninstall"
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "PATH" "$INSTDIR"

    ; Remove files
    RMDir /r "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\PgFlow.lnk"
    RMDir /r "$SMPROGRAMS\PgFlow"

    ; Remove registry keys
    DeleteRegKey HKLM "${UNINSTALL_KEY}"
    DeleteRegKey HKLM "Software\PgFlow"

    ; Note: user data (~/.pgflow/) is intentionally NOT deleted
    MessageBox MB_OK "PgFlow has been uninstalled.$\nYour data in %USERPROFILE%\.pgflow\ was kept."
SectionEnd
