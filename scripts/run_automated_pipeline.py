"""
Automated Highway Traffic Flow & Safety Pipeline
================================================
Executes the end-to-end ITS & Surrogate Safety pipeline for any input video:
  Stage 1: Clean frame extraction & video metadata inspection
  Stage 2: Road-plane homography calibration (assumed 3.5m lane baseline)
  Stage 3: DroneFlow / VisDrone YOLOv8 vehicle detection + ByteTrack MOT
  Stage 4: Metric space projection & trajectory smoothing
  Stage 5: Objective 3: Traffic Flow (q, k, ut, us, V85, headways)
  Stage 6: Objective 4: Microscopic SSMs (TTC, PET, DRAC)
  Stage 7: Objective 5: Crash Prediction Model & Conflict Severity Ranking
  Stage 8: Dashboard data synthesis

Usage:
  python scripts/run_automated_pipeline.py --input "videos/National Highway 48.mp4" [options]
  python scripts/run_automated_pipeline.py --input "videos/NH-53 sample.mp4" [options]
"""

import argparse
import os
import subprocess
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(description="End-to-End Automated Highway Traffic & Safety Pipeline")
    parser.add_argument(
        "--input",
        type=str,
        default="videos/National Highway 48.mp4",
        help="Path to input highway video"
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="models/yolov8s-visdrone.pt",
        help="YOLOv8 model weights path"
    )
    parser.add_argument(
        "--lane-width",
        type=float,
        default=3.5,
        help="Assumed lane width in meters (Unverified preliminary baseline: 3.5m)"
    )
    parser.add_argument(
        "--road-length",
        type=float,
        default=160.0,
        help="Estimated longitudinal length in meters"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=960,
        help="Inference image resolution"
    )
    parser.add_argument(
        "--skip-tracking-if-exists",
        action="store_true",
        help="Skip detection/tracking if trajectory CSV already exists"
    )
    return parser.parse_args()


def run_command_step(cmd, desc):
    print(f"\n>> [STAGE] {desc}...")
    start = time.time()
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"ERROR: Failed during {desc} (Exit code {res.returncode})", file=sys.stderr)
        sys.exit(res.returncode)
    elapsed = time.time() - start
    print(f">> Completed {desc} in {elapsed:.1f}s")


def main():
    args = parse_args()
    python_bin = sys.executable

    base_name = os.path.splitext(os.path.basename(args.input))[0].replace(" ", "_")
    output_annotated = f"outputs/{base_name}_annotated.mp4"
    output_trajectories = f"outputs/{base_name}_trajectories.csv"
    output_clean_frame = f"outputs/calibration/clean_frame_{base_name}.png"
    output_calib_dir = f"outputs/calibration"
    output_analysis_dir = f"outputs/analysis"
    output_safety_dir = f"outputs/safety_analysis"

    print("=" * 70)
    print(" HIGHWAY TRAFFIC ANALYSIS & SAFETY PIPELINE (AUTOMATED) ")
    print("=" * 70)
    print(f"Target Video   : {args.input}")
    print(f"Model Weights  : {args.weights}")
    print(f"Lane Width     : {args.lane_width} m (UNVERIFIED PRELIMINARY)")
    print(f"Corridor Length: {args.road_length} m")
    print("=" * 70)

    # Stage 1: Clean Frame Extraction
    run_command_step(
        f'"{python_bin}" scripts/extract_clean_frame.py --input "{args.input}" --output "{output_clean_frame}" --time-sec 2.0',
        "Stage 1: Extract Clean Reference Frame"
    )

    # Stage 2: Road-Plane Homography Calibration
    run_command_step(
        f'"{python_bin}" scripts/road_plane_calibration.py --image "{output_clean_frame}" --src-points "400,466,1000,469,1000,502,400,499" --lane-width {args.lane_width} --road-length {args.road_length} --output-dir "{output_calib_dir}"',
        "Stage 2: Compute Road-Plane Homography Calibration"
    )

    # Stage 3: Vehicle Detection & ByteTrack Multi-Object Tracking
    if args.skip_tracking_if_exists and os.path.exists(output_trajectories):
        print(f"\n>> [STAGE 3] Skipping tracking: {output_trajectories} already exists.")
    else:
        run_command_step(
            f'"{python_bin}" scripts/track_traffic.py --input "{args.input}" --weights "{args.weights}" --output-video "{output_annotated}" --output-csv "{output_trajectories}" --imgsz {args.imgsz}',
            "Stage 3: YOLOv8 Vehicle Detection & ByteTrack MOT"
        )

    # Stage 4: Trajectory Projection & Metric Smoothing
    run_command_step(
        f'"{python_bin}" scripts/analyze_trajectories.py --trajectories "{output_trajectories}" --calibration "{output_calib_dir}/calibration_config.json" --output-dir "{output_analysis_dir}"',
        "Stage 4: Metric Space Projection & Smoothing"
    )

    # Stage 5, 6, 7: Objectives 3, 4, 5 (Flow, Speeds, TTC, PET, DRAC, Crash Ranking)
    run_command_step(
        f'"{python_bin}" scripts/safety_and_flow_analysis.py --trajectories "{output_analysis_dir}/processed_trajectories_metric.csv" --output-dir "{output_safety_dir}" --road-length-m {args.road_length}',
        "Stages 5-7: Objectives 3, 4 & 5 (Flow, Speeds, SSMs & Crash Severity Ranking)"
    )

    print("\n" + "=" * 70)
    print(" ALL PIPELINE STAGES COMPLETED SUCCESSFULLY ")
    print("=" * 70)
    print(f"Annotated Video        : {output_annotated}")
    print(f"Trajectory CSV         : {output_trajectories}")
    print(f"Metric Trajectories    : {output_analysis_dir}/processed_trajectories_metric.csv")
    print(f"Safety Report JSON     : {output_safety_dir}/comprehensive_safety_report.json")
    print(f"TTC Conflict Events    : {output_safety_dir}/car_following_conflicts_ttc.csv")
    print(f"PET Encroachments      : {output_safety_dir}/encroachment_conflicts_pet.csv")
    print(f"Ranked Crash Conflicts : {output_safety_dir}/ranked_collision_conflicts.csv")
    print("=" * 70)


if __name__ == "__main__":
    main()
