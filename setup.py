# -*- coding: utf-8 -*-
"""
    Setup file for shimoku_api_python.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.2.3.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import os
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup


def auto_versioning(version):
    import os
    import re

    github_ref = os.environ.get("GITHUB_REF", "")


    if github_ref.startswith("refs/tags/"):
        version_number = github_ref.split("refs/tags/")[1]
        version_number = re.sub(r'\.dev\d+', '', version_number)
        return version_number
    if github_ref.startswith("refs/heads/release/"):
        version_number = github_ref.split("refs/heads/release/")[1]
        version_number = re.sub(r'\.dev\d+', '', version_number)
        return version_number
    return version


try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)


if __name__ == "__main__":
    requirements = open("requirements.txt").readlines()
    setup(
        install_requires=requirements,
        version=auto_versioning("0.0.0"),
    )

