"""Visualization utilities for the UAV Vehicle Analysis suite.

Generates matplotlib charts consumed by the dashboard and included in reports.
All functions write PNG files and return their paths.
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless environments

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


def plot_traffic_composition(summary_df: pd.DataFrame, output_dir: Path) -> Path:
    """Bar chart of vehicle class counts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    class_counts = summary_df["class_name"].value_counts()
    class_counts.plot(kind="bar", color="steelblue", ax=ax)
    ax.set_title("Traffic Composition", fontsize=14, fontweight="bold")
    ax.set_xlabel("Vehicle Classification")
    ax.set_ylabel("Tracked Vehicle Count")
    for i, v in enumerate(class_counts):
        ax.text(i, v + 0.3, str(v), ha="center", fontweight="bold")
    plt.tight_layout()
    path = output_dir / "traffic_composition.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return path


def plot_speed_distribution(summary_df: pd.DataFrame, output_dir: Path) -> Path:
    """Histogram of vehicle speeds (km/h)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    speeds = summary_df.get("mean_speed_kmh", summary_df.get("mean_speed_kmh_unverified"))
    if speeds is None:
        print("[WARN] No speed column found in summary - skipping speed distribution.")
        return None
    valid = speeds[(speeds > 5) & (speeds < 160)]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(valid, bins=20, color="#f59e0b", edgecolor="white", alpha=0.85)
    if len(valid) > 0:
        mean_v = valid.mean()
        p85 = np.percentile(valid, 85)
        ax.axvline(mean_v, color="red", linestyle="--", label=f"Mean = {mean_v:.1f} km/h")
        ax.axvline(p85, color="purple", linestyle="-.", label=f"V85 = {p85:.1f} km/h")
        ax.legend(fontsize=9)
    ax.set_title("Vehicle Speed Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Speed (km/h)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    path = output_dir / "speed_distribution.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return path


def plot_space_time_diagram(trajectory_df: pd.DataFrame, output_dir: Path, fps: float = 30.0) -> Path:
    """Space-time (x vs t) trajectory diagram."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    for tid, grp in trajectory_df.groupby("track_id"):
        grp = grp.sort_values("frame")
        t = grp["frame"].values / fps
        x = grp.get("metric_x_m", grp.get("x")).values
        ax.plot(t, x, linewidth=0.7, alpha=0.7)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Longitudinal Position")
    ax.set_title("Space-Time Trajectory Diagram", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = output_dir / "space_time_diagram.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return path


def plot_speed_by_class(summary_df: pd.DataFrame, output_dir: Path) -> Path:
    """Box-plot of speeds grouped by vehicle class."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    speed_col = "mean_speed_kmh" if "mean_speed_kmh" in summary_df.columns else "mean_speed_kmh_unverified"
    if speed_col not in summary_df.columns:
        return None
    groups = summary_df.groupby("class_name")[speed_col].apply(list)
    labels = list(groups.index)
    data = list(groups.values)

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    colours = ["#38bdf8", "#818cf8", "#a855f7", "#f97316", "#34d399", "#fb7185", "#facc15"]
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colours[i % len(colours)])
    ax.set_title("Speed by Vehicle Class", fontsize=14, fontweight="bold")
    ax.set_ylabel("Speed (km/h)")
    plt.tight_layout()
    path = output_dir / "speed_by_classification.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return path


def plot_ttc_distribution(ttc_df: pd.DataFrame, output_dir: Path) -> Path:
    """Histogram of TTC values with a critical threshold line."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    capped = ttc_df["ttc_s"].clip(upper=10)
    ax.hist(capped, bins=40, color="#fb7185", edgecolor="white", alpha=0.85)
    ax.axvline(1.5, color="red", linestyle="--", linewidth=2, label="Critical = 1.5 s")
    ax.legend()
    ax.set_title("Time-to-Collision (TTC) Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("TTC (s)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    path = output_dir / "ttc_distribution.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return path


def plot_pet_distribution(pet_df: pd.DataFrame, output_dir: Path) -> Path:
    """Histogram of PET (proximity) values."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(pet_df["distance_m"], bins=30, color="#2dd4bf", edgecolor="white", alpha=0.85)
    ax.axvline(1.0, color="red", linestyle="--", linewidth=2, label="Critical = 1.0 m")
    ax.legend()
    ax.set_title("Post-Encroachment Time (PET) Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Proximity (m)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    path = output_dir / "pet_distribution.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return path
