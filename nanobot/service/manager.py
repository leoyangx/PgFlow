"""PgFlow service management — install/uninstall/status autostart on boot."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _exe_path() -> Path:
    """Return the path to the pgflow executable (works both from .exe and venv)."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        return Path(sys.executable)
    # Running from venv / development — find pgflow script
    import shutil
    pgflow = shutil.which("pgflow")
    if pgflow:
        return Path(pgflow)
    # Fallback: python -m nanobot
    return Path(sys.executable)


def _gateway_cmd() -> str:
    """Return the full command string to run pgflow gateway."""
    exe = _exe_path()
    if getattr(sys, "frozen", False):
        return f'"{exe}" gateway'
    # venv: use the pgflow script directly
    return f'"{exe}" gateway'


# ---------------------------------------------------------------------------
# Windows — Task Scheduler
# ---------------------------------------------------------------------------

def _win_task_name() -> str:
    return "PgFlow Gateway"


def install_windows() -> tuple[bool, str]:
    """Register PgFlow gateway as a Windows Task Scheduler task at logon."""
    cmd = _gateway_cmd()
    task_name = _win_task_name()

    # schtasks XML-less one-liner: run at logon, for current user, hidden
    args = [
        "schtasks", "/Create", "/F",
        "/TN", task_name,
        "/TR", cmd,
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/IT",          # interact with desktop (needed for console apps)
    ]
    result = subprocess.run(args, capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        return True, f"Task '{task_name}' registered. PgFlow will start on next login."
    return False, result.stderr.strip() or result.stdout.strip()


def uninstall_windows() -> tuple[bool, str]:
    """Remove PgFlow from Windows Task Scheduler."""
    task_name = _win_task_name()
    result = subprocess.run(
        ["schtasks", "/Delete", "/F", "/TN", task_name],
        capture_output=True, text=True, shell=True,
    )
    if result.returncode == 0:
        return True, f"Task '{task_name}' removed."
    return False, result.stderr.strip() or result.stdout.strip()


def status_windows() -> tuple[bool, str]:
    """Check if PgFlow task exists in Task Scheduler."""
    task_name = _win_task_name()
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST"],
        capture_output=True, text=True, shell=True,
    )
    if result.returncode == 0:
        # Extract Status line
        for line in result.stdout.splitlines():
            if "Status" in line or "状态" in line:
                return True, f"Registered — {line.strip()}"
        return True, "Registered (running or ready)"
    return False, "Not registered"


# ---------------------------------------------------------------------------
# macOS — launchd
# ---------------------------------------------------------------------------

def _launchd_label() -> str:
    return "com.pgflow.gateway"


def _launchd_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / "com.pgflow.gateway.plist"


def _launchd_plist_content() -> str:
    cmd = _gateway_cmd()
    # Split into program + args for plist
    parts = cmd.split()
    program_args = "\n".join(f"        <string>{p.strip(chr(34))}</string>" for p in parts)
    label = _launchd_label()
    log_dir = Path.home() / ".pgflow" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
{program_args}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_dir}/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>{log_dir}/gateway.err</string>
</dict>
</plist>
"""


def install_macos() -> tuple[bool, str]:
    """Install PgFlow as a macOS launchd agent (runs at login)."""
    plist_path = _launchd_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_text(_launchd_plist_content(), encoding="utf-8")

    result = subprocess.run(
        ["launchctl", "load", "-w", str(plist_path)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True, f"LaunchAgent installed: {plist_path}\nPgFlow will start on next login."
    return False, result.stderr.strip()


def uninstall_macos() -> tuple[bool, str]:
    """Remove PgFlow launchd agent."""
    plist_path = _launchd_plist_path()
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", "-w", str(plist_path)], capture_output=True)
        plist_path.unlink()
        return True, "LaunchAgent removed."
    return False, f"Plist not found: {plist_path}"


def status_macos() -> tuple[bool, str]:
    """Check macOS launchd agent status."""
    label = _launchd_label()
    result = subprocess.run(
        ["launchctl", "list", label],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True, f"Registered ({label})"
    plist_path = _launchd_plist_path()
    if plist_path.exists():
        return True, "Plist exists but not loaded (run: pgflow service install)"
    return False, "Not registered"


# ---------------------------------------------------------------------------
# Linux — systemd user service
# ---------------------------------------------------------------------------

def _systemd_service_name() -> str:
    return "pgflow-gateway"


def _systemd_service_path() -> Path:
    return Path.home() / ".config" / "systemd" / "user" / "pgflow-gateway.service"


def _systemd_service_content() -> str:
    cmd = _gateway_cmd()
    parts = cmd.split(None, 1)
    exe = parts[0].strip('"')
    args = parts[1] if len(parts) > 1 else ""
    log_dir = Path.home() / ".pgflow" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return f"""[Unit]
Description=PgFlow Gateway
After=network.target

[Service]
Type=simple
ExecStart={exe} {args}
Restart=on-failure
RestartSec=5
StandardOutput=append:{log_dir}/gateway.log
StandardError=append:{log_dir}/gateway.err

[Install]
WantedBy=default.target
"""


def install_linux() -> tuple[bool, str]:
    """Install PgFlow as a systemd user service."""
    service_path = _systemd_service_path()
    service_path.parent.mkdir(parents=True, exist_ok=True)
    service_path.write_text(_systemd_service_content(), encoding="utf-8")

    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    result = subprocess.run(
        ["systemctl", "--user", "enable", "--now", _systemd_service_name()],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True, f"systemd user service installed and started.\nPgFlow will start on login."
    return False, result.stderr.strip()


def uninstall_linux() -> tuple[bool, str]:
    """Remove PgFlow systemd user service."""
    name = _systemd_service_name()
    subprocess.run(["systemctl", "--user", "disable", "--now", name], capture_output=True)
    service_path = _systemd_service_path()
    if service_path.exists():
        service_path.unlink()
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    return True, "systemd user service removed."


def status_linux() -> tuple[bool, str]:
    """Check systemd user service status."""
    name = _systemd_service_name()
    result = subprocess.run(
        ["systemctl", "--user", "is-active", name],
        capture_output=True, text=True,
    )
    state = result.stdout.strip()
    if state == "active":
        return True, "Running (active)"
    service_path = _systemd_service_path()
    if service_path.exists():
        return True, f"Installed but not running ({state})"
    return False, "Not installed"


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def install() -> tuple[bool, str]:
    if sys.platform == "win32":
        return install_windows()
    if sys.platform == "darwin":
        return install_macos()
    return install_linux()


def uninstall() -> tuple[bool, str]:
    if sys.platform == "win32":
        return uninstall_windows()
    if sys.platform == "darwin":
        return uninstall_macos()
    return uninstall_linux()


def status() -> tuple[bool, str]:
    if sys.platform == "win32":
        return status_windows()
    if sys.platform == "darwin":
        return status_macos()
    return status_linux()
