#!/usr/bin/env python3
"""
Setup script for GitHub Repository SEO Optimizer
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version from __init__.py
def get_version():
    version_file = os.path.join("repo_seo", "__init__.py")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="github-repo-seo-optimizer",
    version=get_version(),
    author="Chen Xingqiang",
    author_email="chenxingqiang@turingai.cc",
    description="A tool to optimize GitHub repositories for better discoverability through improved descriptions, topics, and documentation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/chenxingqiang/repo-seo",
    packages=find_packages(exclude=["tests*", "docs*", "examples*", "temp_files*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "nlp": [
            "spacy>=3.4.0",
            "keybert>=0.7.0",
            "transformers>=4.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "repo-seo=repo_seo.cli:cli",
            "github-repo-seo=repo_seo.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "repo_seo": [
            "data/*.json",
            "templates/*.txt",
        ],
    },
    keywords="github seo repository optimization ai llm",
    project_urls={
        "Bug Reports": "https://github.com/chenxingqiang/repo-seo/issues",
        "Source": "https://github.com/chenxingqiang/repo-seo",
        "Documentation": "https://github.com/chenxingqiang/repo-seo#readme",
    },
) 