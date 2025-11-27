"""Version resolution for VarFish.

We try in this order:
1. Read ``VERSION`` file from multiple possible locations:
   - Docker: /usr/src/app/backend/VERSION (one level up from backend/varfish/)
   - Repo root: ../../VERSION (two levels up from backend/varfish/)
2. If a ``.git`` directory exists, use ``git describe`` (development fallback).
3. Fallback to ``0.0.0``.
"""

from pathlib import Path
import subprocess


def _strip_v_prefix(value: str) -> str:
    return value[1:] if value and value.startswith("v") else value


def _get_version() -> str:
    here = Path(__file__).resolve().parent

    # Check multiple VERSION file locations
    # - Docker: backend/VERSION (/usr/src/app/backend/VERSION)
    # - Repo: ../../VERSION (repo root)
    backend_dir = here.parent
    repo_root = backend_dir.parent
    version_files = [
        backend_dir / "VERSION",  # Docker location
        repo_root / "VERSION",  # Repo root location
    ]
    git_dir = repo_root / ".git"

    # 1) Try VERSION files in priority order
    for version_file in version_files:
        if version_file.exists():
            try:
                content = version_file.read_text(encoding="utf-8").strip()
                content = _strip_v_prefix(content)
                # Only use if non-empty
                if content:
                    return content
            except Exception:
                pass

    # 2) git describe (development fallback)
    if git_dir.exists():
        try:
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
