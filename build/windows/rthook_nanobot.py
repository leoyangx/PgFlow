"""Runtime hook: add bundled source trees to sys.path.

Ensures nanobot and litellm submodules are importable even if
PyInstaller's static analysis failed to compile them into the PYZ archive.
"""
import os
import sys

_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

for _src in ("nanobot_src", "litellm_src"):
    _path = os.path.join(_base, _src)
    if _path not in sys.path:
        sys.path.insert(1, _path)
