"""
Highway Traffic Trajectory & Speed Analysis (Preliminary Unverified)
=====================================================================
Processes raw vehicle trajectories, projects pixel coordinates to real-world
metric space using homography calibration, and generates traffic metrics:
  - Trajectory smoothing & noise filtering
  - Preliminary speed estimation (km/h) - EXPLICITLY UNVERIFIED
  - Traffic flow, composition, and direction classification
  - Space-Time (x-t) trajectory diagrams and speed distribution charts

NOTE:
  The assumed lane width of 3.5 m is used ONLY for preliminary analysis
  and MUST be labelled unverified. Validated speeds must not be calculated
  or reported until ground-truth calibration data is verified.
"""

import argparse
import json
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze vehicle trajectories and compute preliminary metrics")
    parser.add_argument(
        "--trajectories",
        type=str,
        default="outputs/National_Highway_48_trajectories.csv",
        help="Path to raw trajectory CSV"
    )
    parser.add_argument(
        "--calibration",
        type=str,
        default="outputs/calibration/calibration_config.json",
        help="Path to calibration config JSON"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/analysis",
        help="Output directory for analysis results and charts"
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=30.0,
        help="Video frame rate"
    )
    return parser.parse_args()


def load_calibration(calib_path):
    if not os.path.exists(calib_path):
        print(f"ERROR: Calibration file not found: {calib_path}", file=sys.stderr)
        sys.exit(1)
    with open(calib_path, "r") as f:
        config = json.load(f)
    H = np.array(config["homography_matrix_H"], dtype=np.float64)
    status = config.get("calibration_status", "UNVERIFIED_PRELIMINARY")
    return H, status, config


def project_points(H, x_arr, y_arr):
    """Batch projection of pixel (x, y) to metric (X, Y) using homography H."""
    pts = np.vstack([x_arr, y_arr, np.ones_like(x_arr)])
    proj = np.dot(H, pts)
    proj /= proj[2, :]
    return proj[0, :], proj[1, :]


def analyze(args):
    if not os.path.exists(args.trajectories):
        print(f"ERROR: Trajectory file not found: {args.trajectories}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(args.trajectories)
    if df.empty:
        print("ERROR: Trajectory file is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded raw trajectories: {len(df)} records across {df['track_id'].nunique()} unique track IDs.")

    # Filter out unassigned tracks (-1) if any
    df = df[df["track_id"] > 0].copy()

    # Load calibration
    H, calib_status, calib_cfg = load_calibration(args.calibration)
    print(f"Using calibration status: {calib_status}")

    # Project pixel coordinates to metric road coordinates
    df["metric_x_m"], df["metric_y_m"] = project_points(
        H, df["center_x"].values, df["center_y"].values
    )

    # Process per track
    processed_dfs = []
    summary_records = []

    # Filter tracks with at least 5 observations (~0.17 seconds)
    min_obs = 5

    for track_id, group in df.groupby("track_id"):
        if len(group) < min_obs:
            continue

        g = group.sort_values("frame_id").copy()

        # Smooth positions with simple rolling window
        win = min(5, len(g))
        g["smooth_x_m"] = g["metric_x_m"].rolling(window=win, min_periods=1, center=True).mean()
        g["smooth_y_m"] = g["metric_y_m"].rolling(window=win, min_periods=1, center=True).mean()

        # Time delta
        dt = g["timestamp_sec"].diff().fillna(1.0 / args.fps)
        dt = dt.replace(0, 1.0 / args.fps)

        # Displacement along longitudinal axis (road length)
        dx = g["smooth_x_m"].diff().fillna(0)
        dy = g["smooth_y_m"].diff().fillna(0)
        dist_m = np.sqrt(dx**2 + dy**2)

        # Speed calculation (instantaneous m/s and km/h)
        speed_mps = dist_m / dt
        speed_kmh = speed_mps * 3.6

        # Rolling average speed to filter detection noise
        g["speed_kmh_unverified"] = speed_kmh.rolling(window=win, min_periods=1, center=True).mean()

        # Direction of travel: based on delta_x in image / road plane
        total_dx = g["smooth_x_m"].iloc[-1] - g["smooth_x_m"].iloc[0]
        direction = "Eastbound (L->R)" if total_dx > 0 else "Westbound (R->L)"

        # Mean preliminary speed for vehicle (excluding first/last boundary frame)
        valid_speeds = g["speed_kmh_unverified"].iloc[1:-1] if len(g) > 2 else g["speed_kmh_unverified"]
        mean_speed = valid_speeds.median() if len(valid_speeds) > 0 else 0

        # Class
        cls_name = g["class_name"].mode()[0] if not g["class_name"].empty else "unknown"
        is_hwy = g["is_highway_corridor"].mean() > 0.5 if "is_highway_corridor" in g.columns else True

        summary_records.append({
            "track_id": track_id,
            "class_name": cls_name,
            "observations": len(g),
            "duration_sec": round(float(g["timestamp_sec"].iloc[-1] - g["timestamp_sec"].iloc[0]), 2),
            "direction": direction,
            "distance_traveled_m": round(float(abs(total_dx)), 2),
            "mean_speed_kmh_unverified": round(float(mean_speed), 1),
            "is_highway_corridor": is_hwy
        })

        processed_dfs.append(g)

    if not processed_dfs:
        print("No valid tracks met the observation threshold.")
        return

    full_proc_df = pd.concat(processed_dfs, ignore_index=True)
    summary_df = pd.DataFrame(summary_records)

    # Save outputs
    os.makedirs(args.output_dir, exist_ok=True)
    proc_csv_path = os.path.join(args.output_dir, "processed_trajectories_metric.csv")
    full_proc_df.to_csv(proc_csv_path, index=False)

    summary_csv_path = os.path.join(args.output_dir, "vehicle_tracking_summary.csv")
    summary_df.to_csv(summary_csv_path, index=False)

    print(f"Processed trajectory CSV saved to: {proc_csv_path}")
    print(f"Vehicle tracking summary saved to: {summary_csv_path}")

    # Generate Figures
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Traffic Composition Chart
    fig, ax = plt.subplots(figsize=(8, 5))
    class_counts = summary_df["class_name"].value_counts()
    class_counts.plot(kind="bar", color="steelblue", ax=ax)
    ax.set_title("Traffic Composition (National Highway 48)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Vehicle Classification")
    ax.set_ylabel("Tracked Vehicle Count")
    for i, v in enumerate(class_counts):
        ax.text(i, v + 0.3, str(v), ha="center", fontweight="bold")
    plt.tight_layout()
    chart1_path = os.path.join(args.output_dir, "traffic_composition.png")
    plt.savefig(chart1_path, dpi=200)
    plt.close()

    # 2. Preliminary Speed Distribution (With prominent unverified banner)
    # Filter highway vehicles with non-trivial movement (> 10 m)
    moving_veh = summary_df[
        (summary_df["is_highway_corridor"]) &
        (summary_df["distance_traveled_m"] > 10) &
        (summary_df["mean_speed_kmh_unverified"] > 5) &
        (summary_df["mean_speed_kmh_unverified"] < 160)
    ]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    if not moving_veh.empty:
        ax.hist(moving_veh["mean_speed_kmh_unverified"], bins=15, color="coral", edgecolor="black", alpha=0.8)
        median_spd = moving_veh["mean_speed_kmh_unverified"].median()
        p85_spd = np.percentile(moving_veh["mean_speed_kmh_unverified"], 85)
        ax.axvline(median_spd, color="blue", linestyle="--", linewidth=2, label=f"Median: {median_spd:.1f} km/h")
        ax.axvline(p85_spd, color="red", linestyle=":", linewidth=2, label=f"85th Percentile: {p85_spd:.1f} km/h")
        ax.legend(fontsize=11)

    ax.set_title("Vehicle Speed Distribution (National Highway 48)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Speed (km/h)")
    ax.set_ylabel("Vehicle Frequency")
    plt.tight_layout()
    chart2_path = os.path.join(args.output_dir, "preliminary_speed_distribution.png")
    plt.savefig(chart2_path, dpi=200)
    plt.close()

    # 3. Space-Time Diagram (x-t plot)
    fig, ax = plt.subplots(figsize=(10, 6))
    for track_id, g in full_proc_df.groupby("track_id"):
        if track_id in moving_veh["track_id"].values:
            ax.plot(g["timestamp_sec"], g["smooth_x_m"], alpha=0.7, linewidth=1.5, label=f"ID {track_id}" if len(moving_veh) < 15 else "")

    ax.set_title("Space-Time Trajectory Diagram (x-t) - NH-48", fontsize=14, fontweight="bold")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Longitudinal Road Position (meters) [Assumed 3.5m Scale]")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart3_path = os.path.join(args.output_dir, "space_time_diagram.png")
    plt.savefig(chart3_path, dpi=200)
    plt.close()

    # Compile executive summary stats
    exec_summary = {
        "status": "UNVERIFIED_PRELIMINARY",
        "methodology_disclaimer": "All metric coordinates and speeds derived from assumed 3.5m lane width without surveyed ground truth. Speeds must remain strictly unverified.",
        "total_tracked_vehicles": int(len(summary_df)),
        "highway_vehicles": int(summary_df["is_highway_corridor"].sum()),
        "traffic_breakdown": class_counts.to_dict(),
        "directional_split": summary_df["direction"].value_counts().to_dict(),
        "preliminary_speed_stats_kmh": {
            "sample_size": int(len(moving_veh)),
            "mean": round(float(moving_veh["mean_speed_kmh_unverified"].mean()), 2) if not moving_veh.empty else 0,
            "median": round(float(moving_veh["mean_speed_kmh_unverified"].median()), 2) if not moving_veh.empty else 0,
            "p85": round(float(np.percentile(moving_veh["mean_speed_kmh_unverified"], 85)), 2) if not moving_veh.empty else 0,
            "min": round(float(moving_veh["mean_speed_kmh_unverified"].min()), 2) if not moving_veh.empty else 0,
            "max": round(float(moving_veh["mean_speed_kmh_unverified"].max()), 2) if not moving_veh.empty else 0,
            "label": "UNVERIFIED_PRELIMINARY"
        }
    }

    summary_json_path = os.path.join(args.output_dir, "analysis_summary.json")
    with open(summary_json_path, "w") as f:
        json.dump(exec_summary, f, indent=2)

    print("\n" + "=" * 60)
    print(" Preliminary Traffic Analysis Completed ")
    print("=" * 60)
    print(f"Total Vehicles Tracked : {exec_summary['total_tracked_vehicles']}")
    print(f"Highway Flow Vehicles  : {exec_summary['highway_vehicles']}")
    print(f"Traffic Breakdown      : {exec_summary['traffic_breakdown']}")
    print(f"Directional Split      : {exec_summary['directional_split']}")
    if not moving_veh.empty:
        print(f"Median Preliminary Speed: {exec_summary['preliminary_speed_stats_kmh']['median']} km/h (UNVERIFIED)")
        print(f"85th Percentile Speed   : {exec_summary['preliminary_speed_stats_kmh']['p85']} km/h (UNVERIFIED)")
    print(f"Executive Summary JSON : {summary_json_path}")
    print("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    analyze(args)
