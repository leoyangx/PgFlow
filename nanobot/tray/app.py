"""PgFlow system tray application.

Launched when the user double-clicks pgflow.exe with no arguments.
- First run (no config): starts dashboard server + opens browser to setup page
- Subsequent runs: starts gateway + dashboard + shows tray icon
"""

from __future__ import annotations

import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path


# ---------------------------------------------------------------------------
# Icon helpers — colour reflects gateway state
# ---------------------------------------------------------------------------

def _load_icon(state: str = "running"):
    """Load tray icon. Returns a PIL Image.

    state: 'running' → full colour, 'stopped' → dimmed, 'starting' → amber
    """
    from PIL import Image, ImageDraw, ImageEnhance

    # Try to load the project logo
    logo_candidates = []
    if getattr(sys, "frozen", False):
        logo_candidates += [
            Path(sys._MEIPASS) / "nanobot_logo.png",
            Path(sys.executable).parent / "nanobot_logo.png",
        ]
    logo_candidates.append(Path(__file__).parent.parent.parent / "nanobot_logo.png")

    img = None
    for candidate in logo_candidates:
        if candidate.exists():
            try:
                img = Image.open(candidate).resize((64, 64)).convert("RGBA")
                break
            except Exception:
                pass

    if img is None:
        # Fallback: draw a coloured circle
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if state == "running":
            color = (62, 207, 142, 255)   # green
        elif state == "starting":
            color = (255, 180, 0, 255)    # amber
        else:
            color = (100, 100, 100, 255)  # grey
        draw.ellipse([4, 4, size - 4, size - 4], fill=color)
        return img

    # Tint logo to reflect state
    if state == "stopped":
        img = ImageEnhance.Brightness(img).enhance(0.35)
    elif state == "starting":
        # Warm amber overlay
        overlay = Image.new("RGBA", img.size, (255, 160, 0, 80))
        img = Image.alpha_composite(img, overlay)
    # "running" → logo at full brightness (no change)

    return img


# ---------------------------------------------------------------------------
# Dashboard server
# ---------------------------------------------------------------------------

_dashboard_started = False
_dashboard_lock = threading.Lock()


def _ensure_dashboard() -> None:
    global _dashboard_started
    with _dashboard_lock:
        if _dashboard_started:
            return
        try:
            from nanobot.dashboard.server import start_dashboard
            start_dashboard(open_browser=False)
            _dashboard_started = True
        except Exception as e:
            _log(f"Dashboard start failed: {e}")


# ---------------------------------------------------------------------------
# Gateway process management
# ---------------------------------------------------------------------------

_gateway_proc: subprocess.Popen | None = None
_gateway_proc_lock = threading.Lock()


def _exe_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    import shutil
    found = shutil.which("pgflow")
    return Path(found) if found else Path(sys.executable)


def _start_gateway() -> None:
    global _gateway_proc
    with _gateway_proc_lock:
        if _gateway_proc and _gateway_proc.poll() is None:
            return
        exe = _exe_path()
        kwargs: dict = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        try:
            _gateway_proc = subprocess.Popen([str(exe), "gateway"], **kwargs)
            _log(f"Gateway started (pid={_gateway_proc.pid})")
        except Exception as e:
            _log(f"Gateway start failed: {e}")


def _stop_gateway() -> None:
    global _gateway_proc
    with _gateway_proc_lock:
        if _gateway_proc and _gateway_proc.poll() is None:
            _gateway_proc.terminate()
            try:
                _gateway_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _gateway_proc.kill()
        _gateway_proc = None


def _gateway_running() -> bool:
    with _gateway_proc_lock:
        return _gateway_proc is not None and _gateway_proc.poll() is None


# ---------------------------------------------------------------------------
# Simple logger (writes to ~/.pgflow/tray.log)
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    try:
        log_path = Path.home() / ".pgflow" / "tray.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            import datetime
            f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Autostart — Windows Registry (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
# ---------------------------------------------------------------------------

def _autostart_reg_key() -> str:
    return "PgFlow"


def _autostart_enabled() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ,
        )
        winreg.QueryValueEx(key, _autostart_reg_key())
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        _log(f"autostart check failed: {e}")
        return False


def _autostart_enable() -> None:
    if sys.platform != "win32":
        return
    try:
        import winreg
        exe = str(_exe_path())
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, _autostart_reg_key(), 0, winreg.REG_SZ, f'"{exe}"')
        winreg.CloseKey(key)
        _log("Autostart enabled")
    except Exception as e:
        _log(f"autostart enable failed: {e}")


def _autostart_disable() -> None:
    if sys.platform != "win32":
        return
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, _autostart_reg_key())
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        _log("Autostart disabled")
    except Exception as e:
        _log(f"autostart disable failed: {e}")


# ---------------------------------------------------------------------------
# Tray menu actions
# ---------------------------------------------------------------------------

def _open_dashboard(_icon=None, _item=None) -> None:
    webbrowser.open("http://localhost:18791")


def _open_logs(_icon=None, _item=None) -> None:
    """Open the latest log file in the default text editor."""
    from nanobot.config.paths import get_logs_dir
    logs_dir = get_logs_dir()
    try:
        log_files = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        target = log_files[0] if log_files else logs_dir / "tray.log"
    except Exception:
        target = Path.home() / ".pgflow" / "tray.log"
    try:
        if sys.platform == "win32":
            subprocess.Popen(["notepad", str(target)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target)])
        else:
            subprocess.Popen(["xdg-open", str(target)])
    except Exception as e:
        _log(f"open logs failed: {e}")


def _restart_gateway(icon=None, _item=None) -> None:
    _log("Restarting gateway…")
    if icon:
        icon.icon = _load_icon("starting")
        icon.title = "PgFlow — 重启中…"
    _stop_gateway()
    time.sleep(1)
    _start_gateway()


def _toggle_autostart(_icon=None, _item=None) -> None:
    if _autostart_enabled():
        _autostart_disable()
    else:
        _autostart_enable()


def _quit_app(icon, _item=None) -> None:
    _log("Quit requested")
    _stop_gateway()
    icon.stop()


# ---------------------------------------------------------------------------
# Status monitor thread — updates icon colour + tooltip every 5 s
# ---------------------------------------------------------------------------

def _monitor(icon) -> None:
    while True:
        time.sleep(5)
        try:
            if not icon.visible:
                break
            running = _gateway_running()
            icon.title = "PgFlow — 运行中" if running else "PgFlow — 已停止"
            icon.icon = _load_icon("running" if running else "stopped")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# First-run check
# ---------------------------------------------------------------------------

def _is_first_run() -> bool:
    return not (Path.home() / ".pgflow" / "config.json").exists()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_tray() -> None:
    """Start the tray application. Must be called from the main thread."""
    _log("tray starting")

    try:
        import pystray
        from PIL import Image  # noqa: F401 — verify PIL is available
    except ImportError as e:
        _log(f"tray deps missing: {e}, falling back to CLI")
        from nanobot.cli.commands import app
        app()
        return

    first_run = _is_first_run()

    # Always start the dashboard so the browser can reach it
    _ensure_dashboard()

    # Start gateway if already configured
    if not first_run:
        _start_gateway()

    # Open browser after a short delay (let dashboard bind to port first)
    def _open_browser_deferred():
        time.sleep(1.5)
        webbrowser.open("http://localhost:18791")

    threading.Thread(target=_open_browser_deferred, daemon=True).start()

    # Build tray menu
    if first_run:
        menu = pystray.Menu(
            pystray.MenuItem("🌊 PgFlow", None, enabled=False),
            pystray.MenuItem("首次运行 — 请完成配置", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("打开配置向导", _open_dashboard, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", _quit_app),
        )
        title = "PgFlow — 请完成初始配置"
        state = "stopped"
    else:
        menu = pystray.Menu(
            pystray.MenuItem("🌊 PgFlow", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("打开管理面板", _open_dashboard, default=True),
            pystray.MenuItem("重启服务", _restart_gateway),
            pystray.MenuItem("查看日志", _open_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "开机自启",
                _toggle_autostart,
                checked=lambda item: _autostart_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", _quit_app),
        )
        title = "PgFlow — 运行中"
        state = "running"

    icon = pystray.Icon(
        name="pgflow",
        icon=_load_icon(state),
        title=title,
        menu=menu,
    )

    # Start monitor in background
    threading.Thread(target=_monitor, args=(icon,), daemon=True).start()

    _log("tray icon.run()")
    try:
        icon.run()
    except Exception as e:
        _log(f"tray icon.run() failed: {e}")
        raise
    _log("tray exited")
