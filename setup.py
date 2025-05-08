#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

# Read requirements from file
with open(os.path.join('deleter', 'src', 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name="cf-pages-deleter",
    version="1.0.0",
    description="A utility to delete Cloudflare Pages deployments",
    author="Your Name",
    packages=['deleter'],
    package_data={
        "deleter": [
            "config/*",
            "scripts/*",
            "docker/*",
            "src/*",
        ],
    },
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cf-pages-deleter=deleter.src.delete_deployments:main",
        ],
    },
    python_requires=">=3.7",
) 