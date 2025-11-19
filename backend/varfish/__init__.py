# Define the package version.  We will first try to determine the version via
# ``git describe --tags``.  If this fails, we assume that we are in a Docker
# image and a file ``VERSION`` exists.

import os
import subprocess


def _get_version():
    dirname = os.path.dirname(__file__)
    if os.path.exists(f"{dirname}/../../VERSION"):
        with open(f"{dirname}/../../VERSION", "rt") as inputf:
            result = inputf.read().strip()[1:]
    else:
        result = "0.0.0"
    if os.path.exists(".git"):
        try:
            result = subprocess.check_output(
                ["git", "describe", "--tags", "--always"], encoding="utf-8"
            ).strip()[1:]
            return result
        except subprocess.CalledProcessError:
            pass
    else:
        return result


__version__ = _get_version()
