# -*- coding: utf-8 -*-
from setuptools import setup
import os

import emokit

long_description = None

packages = [
    "emokit",
]

requirements = open("requirements.txt", "r").read().split("\n")

setup(
    name="emokit",
    version=emokit.__version__,
    url="https://github.com/kanzure/emokit",
    license="",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    maintainer="Bryan Bishop",
    maintainer_email="kanzure@gmail.com",
    description="emotiv epoc eeg headset sdk",
    long_description=long_description,
    packages=packages,
    install_requires=requirements,
    scripts=[],
    platforms="any",
    zip_safe=False,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
