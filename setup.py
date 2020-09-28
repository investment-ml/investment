# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: BSD 3 clause


import setuptools

import investment

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    required = fh.read().splitlines()

setuptools.setup(
    name="investment",
    version=investment.__version__,
    author="Investment Prediction Enthusiast",
    author_email="investment.ml.prediction@gmail.com",
    description="Python Library for Investment",
    license="BSD 3-Clause",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/investment-ml/investment",
    packages=setuptools.find_packages(),
    classifiers=[  # https://pypi.org/classifiers/
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    python_requires='>=3.6',
    include_package_data=True,
)
