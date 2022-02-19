"""
Setuptools definition
"""

import os
from setuptools import setup

# utility function to read the readme
def read(fname):
    """reads a file"""
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="UTF-8").read()

setup(
    name="multiform",
    version="1.0.0",
    author="Michael Lohr",
    author_email="michael@lohr.dev",
    description=("A Multi-Cloud Templating System "),
    long_description=read('README.md'),
    license="MIT",
    packages=['src'],
    install_requires=[
        "Cerberus   == 1.3.4",
        "Jinja2     == 3.1.1",
        "loguru     == 0.6.0",
        "MarkupSafe == 2.1.1",
        "pygraphviz ==   1.9",
        "PyYAML     ==   6.0",
    ],
    entry_points={
        "console_scripts": ["multiform=src.main:main"]
    }
)
