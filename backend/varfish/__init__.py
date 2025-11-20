"""Version resolution for VarFish.

We try in this order:
1. Environment override via ``VARFISH_VERSION``.
2. Read a ``VERSION`` file discovered by walking up from this file's directory.
3. If a ``.git`` directory is found in any parent, use ``git describe`` there.
4. Fallback to ``0.0.0``.

The discovery-based approach makes this work both in development (repo layout)
and in Docker images where the backend is located at ``/usr/src/app`` and a
``VERSION`` file is generated there.
"""

import os
from pathlib import Path
import subprocess


def _strip_v_prefix(value: str) -> str:
    return value[1:] if value and value.startswith("v") else value


def _find_nearest(path: Path, name: str, max_up: int = 5) -> Path | None:
    """Walk up from ``path`` to find the first occurrence of ``name``.

    Returns the full path or ``None`` if not found within ``max_up`` levels.
    """
    cur = path
    for _ in range(max_up + 1):
        candidate = cur / name
        if candidate.exists():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _get_version() -> str:
    # 1) Environment override
    env_version = os.getenv("VARFISH_VERSION")
    if env_version:
        return _strip_v_prefix(env_version.strip())

    here = Path(__file__).resolve().parent

    # 2) VERSION file: allow override path via env, else discover by walking up
    version_file_env = os.getenv("VARFISH_VERSION_FILE")
    version_file: Path | None = None
    if version_file_env:
        vf = Path(version_file_env)
        if vf.exists():
            version_file = vf
    if version_file is None:
        version_file = _find_nearest(here, "VERSION", max_up=6)

    if version_file and version_file.exists():
        try:
            content = version_file.read_text(encoding="utf-8").strip()
            content = _strip_v_prefix(content)
            if content:
                return content
        except Exception:
            pass

    # 3) git describe from nearest .git root (development only)
    git_dir = _find_nearest(here, ".git", max_up=6)
    if git_dir is not None and git_dir.exists():
        try:
            # Run in the repository root (``.git``'s parent directory)
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

    # 4) Fallback
    return "0.0.0"


__version__ = _get_version()
