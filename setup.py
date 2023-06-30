import os

from setuptools import find_packages, setup

import versioneer

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="varfish-server",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="BIH VarFish",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    url="https://bihealth.org",
    author="Oliver Stolpe, Manuel Holtgrewe",
    author_email="oliver.stolpe@bihealth.de, manuel.holtgrewe@bihealth.de",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
