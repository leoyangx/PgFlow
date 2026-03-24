"""PgFlow skill store — install and manage skills from ClawHub."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


def _workspace_path() -> Path:
    from nanobot.config.loader import get_config_path, load_config
    cfg = load_config(get_config_path())
    return cfg.workspace_path


def _skills_dir() -> Path:
    return _workspace_path() / "skills"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _has_npx() -> bool:
    if shutil.which("npx"):
        return True
    if sys.platform == "win32":
        # On Windows, shutil.which may miss .cmd/.ps1 extensions
        try:
            result = subprocess.run(["npx", "--version"], capture_output=True, shell=True)
            return result.returncode == 0
        except Exception:
            return False
    return False


def _npx_clawhub(*args: str) -> subprocess.CompletedProcess:
    cmd = ["npx", "--yes", "clawhub@latest", *args]
    # shell=True is required on Windows so PATH is resolved correctly
    return subprocess.run(cmd, capture_output=False, text=True, shell=sys.platform == "win32")


def _parse_skill_frontmatter(skill_md: Path) -> dict:
    """Return name, description, icon from a SKILL.md file."""
    name = skill_md.parent.name
    description = ""
    icon = "🔧"
    source = "workspace"
    try:
        text = skill_md.read_text(encoding="utf-8")
        if text.startswith("---"):
            match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            if match:
                for line in match.group(1).splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"\'')
                    elif line.startswith("description:"):
                        description = line.split(":", 1)[1].strip().strip('"\'')
        # Extract emoji from first heading
        for line in text.splitlines():
            if line.startswith("# "):
                for ch in line[2:]:
                    if ord(ch) > 127:
                        icon = ch
                        break
                break
    except Exception:
        pass
    return {"name": name, "description": description, "icon": icon, "source": source}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_installed() -> list[dict]:
    """Return all installed skills (workspace + builtin)."""
    from nanobot.agent.skills import BUILTIN_SKILLS_DIR

    skills = []
    skills_dir = _skills_dir()

    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            skill_md = d / "SKILL.md"
            if d.is_dir() and skill_md.exists():
                info = _parse_skill_frontmatter(skill_md)
                info["source"] = "workspace"
                skills.append(info)

    if BUILTIN_SKILLS_DIR.exists():
        existing_names = {s["name"] for s in skills}
        for d in sorted(BUILTIN_SKILLS_DIR.iterdir()):
            skill_md = d / "SKILL.md"
            if d.is_dir() and skill_md.exists():
                info = _parse_skill_frontmatter(skill_md)
                if info["name"] not in existing_names:
                    info["source"] = "builtin"
                    skills.append(info)

    return skills


def search_skills(query: str, limit: int = 10) -> int:
    """Search ClawHub for skills. Returns exit code."""
    if not _has_npx():
        print("✗ 需要 Node.js (npx)，请先安装：https://nodejs.org", file=sys.stderr)
        return 1
    return _npx_clawhub("search", query, "--limit", str(limit)).returncode


def install_skill(slug: str) -> int:
    """Install a skill from ClawHub. Returns exit code."""
    if not _has_npx():
        print("✗ 需要 Node.js (npx)，请先安装：https://nodejs.org", file=sys.stderr)
        return 1
    workspace = str(_workspace_path())
    result = _npx_clawhub("install", slug, "--workdir", workspace)
    return result.returncode


def remove_skill(name: str) -> bool:
    """Remove a workspace skill by directory name. Returns True if removed."""
    skill_dir = _skills_dir() / name
    if skill_dir.exists() and skill_dir.is_dir():
        shutil.rmtree(skill_dir)
        return True
    return False


def update_all_skills() -> int:
    """Update all workspace skills via ClawHub. Returns exit code."""
    if not _has_npx():
        print("✗ 需要 Node.js (npx)，请先安装：https://nodejs.org", file=sys.stderr)
        return 1
    workspace = str(_workspace_path())
    return _npx_clawhub("update", "--all", "--workdir", workspace).returncode
