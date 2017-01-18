# -*- coding: utf-8 -*-
import platform

from setuptools import setup

import emokit

long_description = None

packages = [
    "emokit",
]

requirements = open("requirements.txt", "r").read().split("\n")
system_platform = platform.system()

if system_platform == "Windows":
    requirements += ['pywinusb']
else:
    requirements += ['pyhidapi']

setup_requirements = ['pytest-runner', ]
setup_requirements += requirements
test_requirements = ['pytest', ]
test_requirements += requirements
setup(
    name="emokit",
    version=emokit.__version__,
    url="https://github.com/openyou/emokit",
    license="Public Domain, SEE LICENSE",
    author="Cody Brocious",
    author_email="cody.brocious@gmail.com",
    maintainer="Bill Schumacher",
    maintainer_email="bill@servernet.co",
    description="emotiv epoc eeg headset sdk",
    long_description=long_description,
    packages=packages,
    install_requires=requirements,
    scripts=[],
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    platforms="any",
    zip_safe=False,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
