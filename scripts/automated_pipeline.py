'''Automated pipeline entry point

This script coordinates the full UAV‑based traffic analysis workflow:

1. **Calibration** – optional road‑plane calibration using a clean frame.
2. **Detection & Tracking** – runs the YOLOv8‑VisDrone model with ByteTrack.
3. **Trajectory post‑processing** – aggregates raw tracks into CSV files.
4. **Safety & Flow analysis** – computes TTC, headway, etc.
5. **Dashboard launch** – starts the HTML dashboard.

The implementation is intentionally modular: each stage is delegated to an existing
script in ``scripts/``.  If the internal implementation of a stage changes, only
that script needs to be updated – the pipeline logic remains unchanged.

Configuration is externalised in ``config/pipeline_config.json``; the user can
override any setting via command‑line arguments.
''' 

import argparse
import json
import subprocess
import sys
from pathlib import Path

def load_config(config_path: Path) -> dict:
    """Load JSON configuration.

    Parameters
    ----------
    config_path: Path
        Path to the JSON config file.
    """
    if not config_path.is_file():
        sys.exit(f"[ERROR] Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def run_stage(script_path: Path, args: list[str]):
    """Execute a stage script via ``python``.

    Returns ``True`` on success, ``False`` otherwise.
    """
    if not script_path.is_file():
        print(f"[WARN] Stage script missing: {script_path}")
        return False
    cmd = [sys.executable, str(script_path)] + args
    print(f"[INFO] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {script_path.name} failed (code {result.returncode})")
        print(result.stderr)
        return False
    print(result.stdout)
    return True

def main():
    parser = argparse.ArgumentParser(description="Run the full UAV traffic analysis pipeline")
    parser.add_argument("--config", type=Path, default=Path(__file__).parents[1] / "config" / "pipeline_config.json",
                        help="Path to the JSON configuration file")
    parser.add_argument("--video", type=Path, help="Override video input path")
    parser.add_argument("--output", type=Path, help="Override base output directory")
    parser.add_argument("--model", type=Path, help="Override YOLO model checkpoint")
    parser.add_argument("--lane-width", type=float, help="Lane width (m) for calibration")
    args = parser.parse_args()

    cfg = load_config(args.config)

    # Apply CLI overrides
    if args.video:
        cfg["video_path"] = str(args.video)
    if args.output:
        cfg["output_dir"] = str(args.output)
    if args.model:
        cfg["model_path"] = str(args.model)
    if args.lane_width is not None:
        cfg["calibration"]["assumed_lane_width_m"] = args.lane_width

    # Ensure output directory exists
    out_dir = Path(cfg["output_dir"]).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Calibration (optional)
    calib_cfg = cfg.get("calibration", {})
    if calib_cfg.get("run", True):
        clean_frame = out_dir / "calibration" / "clean_frame.png"
        calib_args = [
            "--video", cfg["video_path"],
            "--output", str(out_dir / "calibration"),
            "--lane-width", str(calib_cfg.get("assumed_lane_width_m", 3.5))
        ]
        run_stage(Path(__file__).parent / "road_plane_calibration.py", calib_args)
    else:
        print("[INFO] Skipping calibration as per config.")

    # 2) Detection & Tracking
    track_args = [
        "--video", cfg["video_path"],
        "--model", cfg["model_path"],
        "--output", str(out_dir / "outputs"),
        "--conf-thresh", str(cfg.get("detection_confidence", 0.5))
    ]
    run_stage(Path(__file__).parent / "track_traffic.py", track_args)

    # 3) Trajectory analysis
    traj_args = [
        "--input", str(out_dir / "outputs" / "National_Highway_48_trajectories.csv"),
        "--output", str(out_dir / "outputs" / "analysis")
    ]
    run_stage(Path(__file__).parent / "analyze_trajectories.py", traj_args)

    # 4) Safety & flow analysis (optional)
    if cfg.get("run_safety_analysis", True):
        safety_args = [
            "--input", str(out_dir / "outputs" / "analysis"),
            "--output", str(out_dir / "outputs" / "safety_analysis")
        ]
        run_stage(Path(__file__).parent / "safety_and_flow_analysis.py", safety_args)

    # 5) Launch dashboard (optional)
    if cfg.get("launch_dashboard", True):
        dash_args = ["--output", str(out_dir / "outputs" / "dashboard")]
        run_stage(Path(__file__).parent / "launch_dashboard.py", dash_args)

    print("[INFO] Pipeline completed.")

if __name__ == "__main__":
    main()
