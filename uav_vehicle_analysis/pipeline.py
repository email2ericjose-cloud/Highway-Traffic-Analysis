"""Unified pipeline runner for UAV-Based Vehicle Detection and Trajectory Analysis.

Orchestrates all stages (calibration -> detection -> tracking -> analysis -> safety
-> visualization -> dashboard) using the package modules directly (no subprocess
calls). The pipeline is designed so that each stage is independent and
replaceable - if the internal logic of any module changes, the pipeline logic
here stays the same.

Usage
-----
    python -m uav_vehicle_analysis.pipeline --video "videos/myvideo.mp4" --lane-width 3.5

Or programmatically::

    from uav_vehicle_analysis.pipeline import run_pipeline
    run_pipeline(video_path="videos/myvideo.mp4", lane_width_m=3.5)
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from .config import load_config, dump_config


def run_pipeline(
    video_path: str | Path,
    output_dir: str | Path = "outputs",
    model_path: str | Path | None = None,
    lane_width_m: float = 3.5,
    conf_thresh: float = 0.5,
    fps: float = 30.0,
    skip_calibration: bool = False,
    skip_safety: bool = False,
    config_path: str | Path | None = None,
) -> dict:
    """Run the full end-to-end pipeline.

    Returns a dict summarising the outputs produced.
    """
    start = time.time()
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Try to load config; fall back to defaults
    try:
        cfg = load_config(config_path)
    except FileNotFoundError:
        cfg = {}

    # Apply overrides
    cfg["video_path"] = str(video_path)
    cfg["output_dir"] = str(output_dir)
    if model_path:
        cfg["model_path"] = str(model_path)
    else:
        model_path = cfg.get("model_path", "models/yolov8s-visdrone.pt")
    cfg.setdefault("calibration", {})
    cfg["calibration"]["assumed_lane_width_m"] = lane_width_m
    cfg["detection_confidence"] = conf_thresh
    cfg["fps"] = fps

    # Save runtime config
    runtime_cfg_path = output_dir / "runtime_config.json"
    dump_config(cfg, runtime_cfg_path)

    result = {"video": str(video_path), "stages": {}}
    video_stem = video_path.stem.replace(" ", "_")

    # ── Stage 1: Calibration ──────────────────────────────────────────────
    homography_path = None
    if not skip_calibration:
        print("\n" + "=" * 60)
        print("  STAGE 1 / 5 : Road-Plane Calibration")
        print("=" * 60)
        from .calibration import compute_homography, save_homography
        calib_dir = output_dir / "calibration"
        calib_dir.mkdir(parents=True, exist_ok=True)

        # Extract a clean frame for calibration
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        if cap.isOpened():
            # Grab a frame ~1/3 into the video
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, total // 3)
            ret, frame = cap.read()
            cap.release()
            if ret:
                clean_frame_path = calib_dir / f"clean_frame_{video_stem}.png"
                cv2.imwrite(str(clean_frame_path), frame)
                H = compute_homography(clean_frame_path, lane_width_m)
                homography_path = calib_dir / "homography.json"
                save_homography(H, homography_path)
                result["stages"]["calibration"] = str(homography_path)
                print(f"[OK] Calibration saved -> {homography_path}")
            else:
                print("[WARN] Could not read video frame - skipping calibration.")
        else:
            print("[WARN] Could not open video - skipping calibration.")
    else:
        print("[INFO] Calibration skipped (--skip-calibration).")

    # ── Stage 2: Detection ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  STAGE 2 / 5 : Vehicle Detection (YOLOv8)")
    print("=" * 60)
    from .detection import run_detection
    det_dir = output_dir / "detection"
    detections_path = run_detection(
        video_path=video_path,
        output_dir=det_dir,
        model_path=model_path,
        conf_thresh=conf_thresh,
    )
    result["stages"]["detection"] = str(detections_path)

    # ── Stage 3: Multi-Object Tracking ────────────────────────────────────
    print("\n" + "=" * 60)
    print("  STAGE 3 / 5 : Multi-Object Tracking")
    print("=" * 60)
    from .tracking import run_tracking
    track_dir = output_dir / "tracking"
    trajectories_path = run_tracking(
        detections_path=detections_path,
        output_dir=track_dir,
    )
    result["stages"]["tracking"] = str(trajectories_path)

    # ── Stage 4: Trajectory Analysis ──────────────────────────────────────
    print("\n" + "=" * 60)
    print("  STAGE 4 / 5 : Trajectory & Speed Analysis")
    print("=" * 60)
    from .analysis import analyze_trajectories
    analysis_dir = output_dir / "analysis"
    metrics_path = analyze_trajectories(
        input_csv=trajectories_path,
        output_dir=analysis_dir,
        fps=fps,
        homography_path=homography_path,
    )
    result["stages"]["analysis"] = str(metrics_path)

    # ── Stage 5: Safety Analysis ──────────────────────────────────────────
    if not skip_safety:
        print("\n" + "=" * 60)
        print("  STAGE 5 / 5 : Surrogate Safety Analysis (TTC / PET)")
        print("=" * 60)
        from .safety import run_safety_analysis
        safety_dir = output_dir / "safety_analysis"
        # Prefer the enriched CSV (with speed) if it exists
        enriched = analysis_dir / "trajectories_with_speed.csv"
        traj_input = enriched if enriched.is_file() else trajectories_path
        safety_path = run_safety_analysis(
            trajectory_csv=traj_input,
            output_dir=safety_dir,
            fps=fps,
            homography_path=homography_path,
        )
        result["stages"]["safety"] = str(safety_path)
    else:
        print("[INFO] Safety analysis skipped (--skip-safety).")

    elapsed = time.time() - start
    result["elapsed_seconds"] = round(elapsed, 2)
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE COMPLETE  ({elapsed:.1f}s)")
    print(f"  All outputs saved under: {output_dir}")
    print(f"{'=' * 60}\n")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="UAV-Based Vehicle Detection and Trajectory Analysis - Full Pipeline"
    )
    parser.add_argument("--video", type=Path, required=True,
                        help="Path to the input video file")
    parser.add_argument("--output", type=Path, default=Path("outputs"),
                        help="Base output directory (default: outputs/)")
    parser.add_argument("--model", type=Path, default=None,
                        help="Path to YOLO model checkpoint (overrides config)")
    parser.add_argument("--lane-width", type=float, default=3.5,
                        help="Known road/lane width in metres for calibration (default: 3.5)")
    parser.add_argument("--conf-thresh", type=float, default=0.5,
                        help="Detection confidence threshold (default: 0.5)")
    parser.add_argument("--fps", type=float, default=30.0,
                        help="Video frame rate in FPS (default: 30.0)")
    parser.add_argument("--config", type=Path, default=None,
                        help="Path to pipeline_config.json (optional)")
    parser.add_argument("--skip-calibration", action="store_true",
                        help="Skip the calibration stage")
    parser.add_argument("--skip-safety", action="store_true",
                        help="Skip the surrogate safety analysis stage")
    args = parser.parse_args()

    results = run_pipeline(
        video_path=args.video,
        output_dir=args.output,
        model_path=args.model,
        lane_width_m=args.lane_width,
        conf_thresh=args.conf_thresh,
        fps=args.fps,
        skip_calibration=args.skip_calibration,
        skip_safety=args.skip_safety,
        config_path=args.config,
    )
    # Write results summary
    summary_path = args.output / "pipeline_results.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results summary: {summary_path}")


if __name__ == "__main__":
    main()
