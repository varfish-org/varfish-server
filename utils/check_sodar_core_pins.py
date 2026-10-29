"""List packages pinned through django-sodar-core whose versions differ between two Pipfile.locks.

SODAR Core and everything it requires (Django, djangorestframework, ...) are only updated by
hand (#2806, #2835). The requirements are taken from PyPI for the sodar-core version(s) in the
locks, so the list follows sodar-core upgrades. Exits 1 if such a package changed, 0 otherwise;
any error (e.g. PyPI unreachable) propagates and also yields a non-zero exit.
"""

import json
import re
import sys
import urllib.request

SODAR_CORE = "django-sodar-core"


def normalize(name: str) -> str:
    """Normalize a package name (PEP 503)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def versions(lock: dict[str, dict[str, dict[str, str]]], name: str) -> dict[str, str]:
    """Return ``{category: version}`` of ``name`` in all lock categories."""
    return {
        category: entry.get("version", "-")
        for category, packages in lock.items()
        if category != "_meta"
        for package, entry in packages.items()
        if normalize(package) == name
    }


def sodar_core_requirements(version: str) -> set[str]:
    """Return the normalized names of the (non-extra) requirements of a sodar-core release."""
    url = f"https://pypi.org/pypi/{SODAR_CORE}/{version.lstrip('=')}/json"
    with urllib.request.urlopen(url, timeout=30) as response:
        requires = json.load(response)["info"]["requires_dist"] or []
    return {
        normalize(re.split(r"[\s<>=!~;\[(]", requirement, maxsplit=1)[0])
        for requirement in requires
        if "extra ==" not in requirement
    }


def changed_pins(
    base: dict[str, dict[str, dict[str, str]]], head: dict[str, dict[str, dict[str, str]]]
) -> list[str]:
    """Return one line per sodar-core pinned package whose versions differ."""
    protected = {SODAR_CORE, "django"}
    for lock in (base, head):
        for version in set(versions(lock, SODAR_CORE).values()):
            protected |= sodar_core_requirements(version)
    # Compare the set of versions: a package appearing in another category with the same
    # version is not an update.
    return [
        f"{name} ({versions(base, name)} -> {versions(head, name)})"
        for name in sorted(protected)
        if set(versions(base, name).values()) != set(versions(head, name).values())
    ]


def main(base_path: str, head_path: str) -> int:
    with open(base_path) as base_file, open(head_path) as head_file:
        found = changed_pins(json.load(base_file), json.load(head_file))
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
