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
# Icon helpers
# ---------------------------------------------------------------------------

def _load_icon(state: str = "running"):
    """Load tray icon. Returns a PIL Image."""
    from PIL import Image, ImageDraw

    # Try to load the project logo
    logo_candidates = []
    if getattr(sys, "frozen", False):
        # Frozen .exe: _internal folder or next to exe
        logo_candidates += [
            Path(sys._MEIPASS) / "nanobot_logo.png",
            Path(sys.executable).parent / "nanobot_logo.png",
        ]
    # Dev: repo root
    logo_candidates.append(Path(__file__).parent.parent.parent / "nanobot_logo.png")

    for candidate in logo_candidates:
        if candidate.exists():
            try:
                img = Image.open(candidate).resize((64, 64)).convert("RGBA")
                if state == "stopped":
                    from PIL import ImageEnhance
                    img = ImageEnhance.Brightness(img).enhance(0.4)
                return img
            except Exception:
                pass

    # Fallback: draw a coloured circle
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (62, 207, 142, 255) if state == "running" else (100, 100, 100, 255)
    draw.ellipse([4, 4, size - 4, size - 4], fill=color)
    return img


# ---------------------------------------------------------------------------
# Dashboard server
# ---------------------------------------------------------------------------

_dashboard_started = False
_dashboard_lock = threading.Lock()


def _ensure_dashboard() -> None:
    """Start the dashboard HTTP server if not already running."""
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
# Tray menu actions
# ---------------------------------------------------------------------------

def _open_dashboard(_icon=None, _item=None) -> None:
    webbrowser.open("http://localhost:18791")


def _restart_gateway(icon=None, _item=None) -> None:
    _stop_gateway()
    time.sleep(1)
    _start_gateway()


def _quit_app(icon, _item=None) -> None:
    _stop_gateway()
    icon.stop()


# ---------------------------------------------------------------------------
# Status monitor thread
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
    # icon.run() blocks the main thread — required on Windows
    try:
        icon.run()
    except Exception as e:
        _log(f"tray icon.run() failed: {e}")
        raise
    _log("tray exited")
