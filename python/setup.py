# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 22:40:54 2022

@author: philippe@loco-labs.io
"""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="observation",
    version="0.0.4",
    description="environmental data interoperability in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loco-philippe/Environmental-Sensing",
    author="Philippe Thomy",
    author_email="philippe@loco-labs.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"],
    keywords="observation, indexed list, development, environmental data",
    packages=find_packages(include=['observation', 'observation.*']),
    python_requires=">=3.7, <4",
    install_requires=['numpy', 'shapely', 'cbor2', 'xarray', 'pandas']
)
