import io
from setuptools import setup, find_packages
from typing import List

requirements: List[str] = ["logzero", "click", "flask", "more_itertools"]

# Use the README.md content for the long description:
with io.open("README.md", encoding="utf-8") as fo:
    long_description = fo.read()

setup(
    name="my_api",
    version="0.1.0",
    url="https://github.com/seanbreckenridge/HPI_API",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""An automatic JSON API for HPI"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["my_api"]),
    install_requires=requirements,
    keywords="data server",
    entry_points={"console_scripts": ["hpi_api = my_api.__main__:main"]},
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
