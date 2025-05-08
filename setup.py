#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="cf-pages-deleter",
    version="1.0.0",
    description="A utility to delete Cloudflare Pages deployments",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "cf-pages-deleter=deleter.delete_deployments:main",
        ],
    },
    python_requires=">=3.7",
) 