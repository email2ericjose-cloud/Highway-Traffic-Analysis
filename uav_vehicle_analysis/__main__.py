"""Allow running the package directly with ``python -m uav_vehicle_analysis``.

Example::

    python -m uav_vehicle_analysis --video "videos/National Highway 48.mp4" --lane-width 3.5
"""
from uav_vehicle_analysis.pipeline import main

if __name__ == "__main__":
    main()
