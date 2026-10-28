"""Check that every package has the same version in all categories of a ``Pipfile.lock``.

When several categories are installed together, the later one wins, so a version that differs
between categories silently replaces the intended one (#2825).
"""

import json
import sys


def mismatches(lock: dict[str, dict[str, dict[str, str]]]) -> list[str]:
    """Return one line per package whose version differs between the lock categories."""
    versions: dict[str, dict[str, str]] = {}
    for category, packages in lock.items():
        if category == "_meta":
            continue
        for name, entry in packages.items():
            versions.setdefault(name, {})[category] = entry.get("version", "-")
    return [
        f"{name}: "
        + ", ".join(f"{category} {version}" for category, version in sorted(cats.items()))
        for name, cats in sorted(versions.items())
        if len(set(cats.values())) > 1
    ]


def main(path: str) -> int:
    with open(path) as f:
        found = mismatches(json.load(f))
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
