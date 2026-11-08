#!/usr/bin/env python
"""
UAV-Based Vehicle Detection and Trajectory Analysis
====================================================
Top-level entry point.  This script simply delegates to the package pipeline.

Usage examples
--------------
    # Analyse a video with default settings (lane width = 3.5 m)
    python run_pipeline.py --video "videos/National Highway 48.mp4"

    # Analyse with a custom lane width and output folder
    python run_pipeline.py --video "videos/NH-53 sample.mp4" --lane-width 3.7 --output outputs_nh53

    # Skip calibration if you already have a homography
    python run_pipeline.py --video "videos/myvideo.mp4" --skip-calibration

Run ``python run_pipeline.py --help`` for the full list of options.
"""
import sys
from pathlib import Path

# Ensure the project root is on PYTHONPATH so the package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

from uav_vehicle_analysis.pipeline import main

if __name__ == "__main__":
    main()
