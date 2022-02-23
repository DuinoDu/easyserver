# -*- coding: utf-8 -*-
# mypy: ignore-errors

import io
import re

from setuptools import setup

with open("README.md", "r") as f:
    readme = f.read()

with open("LICENSE", "r") as f:
    license = f.read()

with open("requirements/build.txt", "r") as f:
    requires = []
    for line in f:
        line = line.strip()
        if not line.startswith("#"):
            requires.append(line)

with io.open("easyserver/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)

setup(
    name="easyserver",
    version=version,
    description="Simple python server runner with config",
    long_description=readme,
    author="duinodu",
    author_email="duino472365351@gmail.com",
    url="https://github.com/duinodu/easyserver",
    license=license,
    platform="linux",
    zip_safe=False,
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=requires,
    entry_points={"console_scripts": ["easyserver = easyserver.core:main"]},
)
