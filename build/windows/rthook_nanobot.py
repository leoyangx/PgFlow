"""Runtime hook: add bundled nanobot source tree to sys.path.

This ensures that even if PyInstaller's static analysis failed to compile
a nanobot submodule into the PYZ archive, the raw .py source files
(shipped in nanobot_src/) are always importable at runtime.
"""
import os
import sys

# sys._MEIPASS is the _internal/ directory where PyInstaller unpacks data files
_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_base, "nanobot_src")

if _src not in sys.path:
    # Insert at position 1 (after '' for relative imports) so the bundled
    # source is found before any system-installed nanobot package.
    sys.path.insert(1, _src)
