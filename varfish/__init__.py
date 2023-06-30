# Define the package version.  We will first try to determine the version via
# ``git describe --tags``.  If this fails, we assume that we are in a Docker
# image and a file ``VERSION`` exists.

import os
import subprocess

def get_version():
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--always"], encoding="utf-8"
        ).strip()
    except subprocess.CalledProcessError:
        dirname = os.path.dirname(__file__)
        with open(f"{dirname}/../utils/docker/VERSION", "rt") as inputf:
            return inputf.read().strip()

__version__ = _get_version()
