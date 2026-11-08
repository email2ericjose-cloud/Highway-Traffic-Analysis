"""Backward-compatible setup.py.

The canonical configuration lives in ``pyproject.toml``.  This file exists so
that ``pip install -e .`` works on older pip versions that don't read
pyproject.toml natively.
"""
from setuptools import setup, find_packages

setup(
    name="uav-vehicle-analysis",
    version="1.0.0",
    description="UAV-Based Vehicle Detection and Trajectory Analysis",
    packages=find_packages(include=["uav_vehicle_analysis*"]),
    python_requires=">=3.10",
    install_requires=[
        "ultralytics>=8.0.0",
        "opencv-python>=4.8.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "torch>=2.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "uav-pipeline=uav_vehicle_analysis.pipeline:main",
        ],
    },
)
