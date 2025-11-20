"""Version resolution for VarFish.

We try in this order:
1. Read ``VERSION`` file from one level up (Docker: /usr/src/app/VERSION).
2. If a ``.git`` directory exists, use ``git describe`` (development fallback).
3. Fallback to ``0.0.0``.
"""

from pathlib import Path
import subprocess


def _strip_v_prefix(value: str) -> str:
    return value[1:] if value and value.startswith("v") else value


def _get_version() -> str:
    here = Path(__file__).resolve().parent

    # Check one level up from backend/varfish/ -> backend/
    backend_dir = here.parent
    version_file = backend_dir / "VERSION"
    git_dir = backend_dir.parent / ".git"

    # 1) VERSION file one level up from backend/varfish/
    if version_file.exists():
        try:
            content = version_file.read_text(encoding="utf-8").strip()
            content = _strip_v_prefix(content)
            if content:
                return content
        except Exception:
            pass

    # 2) git describe (development fallback)
    if git_dir.exists():
        try:
            repo_root = git_dir.parent
            described = subprocess.check_output(
                ["git", "describe", "--tags", "--always"],
                cwd=str(repo_root),
                encoding="utf-8",
            ).strip()
            described = _strip_v_prefix(described)
            if described:
                return described
        except Exception:
            pass

    # 3) Fallback
    return "0.0.0"


__version__ = _get_version()
