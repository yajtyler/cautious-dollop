#!/usr/bin/env python3
"""
DNS Benchmark Tool - Setup Script

A high-performance DNS benchmarking utility that measures and compares
the performance of various DNS providers across multiple metrics.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read the contents of requirements file
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read version from __init__.py (will be created when the package is implemented)
version = "1.0.0"

setup(
    name="dns-benchmark",
    version=version,
    author="DNS Benchmark Tool Contributors",
    author_email="contributors@example.com",
    description="A high-performance DNS benchmarking utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/dns-benchmark",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/dns-benchmark/issues",
        "Documentation": "https://github.com/your-username/dns-benchmark/wiki",
        "Source Code": "https://github.com/your-username/dns-benchmark",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Networking",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "responses>=0.22.0",
            "faker>=16.6.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-click>=4.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dns-benchmark=dns_benchmark.cli:main",
            "dnsbenchmark=dns_benchmark.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dns_benchmark": [
            "config/*.yaml",
            "data/*.json",
            "templates/*.txt",
        ],
    },
    data_files=[
        ("share/dns-benchmark/examples", [
            "config.yaml.example",
        ]),
        ("share/doc/dns-benchmark", [
            "README.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "LICENSE",
        ]),
    ],
    zip_safe=False,
    keywords=[
        "dns",
        "benchmark",
        "performance",
        "networking",
        "monitoring",
        "tools",
        "utility",
        "speed-test",
        "latency",
        "resolver",
    ],
    license="MIT",
    platforms=["any"],
    test_suite="tests",
    tests_require=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-asyncio>=0.21.0",
    ],
)