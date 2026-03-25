"""
Entry point for running PgFlow as a module: python -m nanobot

- With arguments           → normal CLI (pgflow gateway / onboard / etc.)
- No arguments, Windows    → relaunch self as a hidden-window tray process
- No arguments, other OS   → tray application directly
"""

import sys


def _relaunch_as_tray() -> None:
    """Relaunch this exe as a windowless tray process and exit immediately."""
    import subprocess

    CREATE_NO_WINDOW        = 0x08000000
    DETACHED_PROCESS        = 0x00000008
    CREATE_BREAKAWAY_FROM_JOB = 0x01000000  # escape the parent's Job Object

    subprocess.Popen(
        [sys.executable, "--tray"],
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB,
        close_fds=True,
    )


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        # Double-clicked with no arguments
        if sys.platform == "win32" and getattr(sys, "frozen", False):
            # On Windows frozen exe: relaunch hidden, then exit so the
            # console window disappears immediately.
            _relaunch_as_tray()
            sys.exit(0)
        else:
            # Dev mode or non-Windows: run tray directly
            from nanobot.tray.app import run_tray
            run_tray()

    elif args == ["--tray"]:
        # Hidden relaunch — run the actual tray app (no console window)
        from nanobot.tray.app import run_tray
        run_tray()

    else:
        from nanobot.cli.commands import app
        app()
