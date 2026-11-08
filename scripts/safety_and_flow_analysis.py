"""
Comprehensive Highway Traffic Flow, Speed & Surrogate Safety Analysis
=====================================================================
Fulfills Thesis Objectives 3, 4, and 5:
  Objective 3: Macroscopic & Microscopic Traffic Flow (Count, Density, Speed, Headways)
  Objective 4: Microscopic Surrogate Safety Measures (TTC, PET, DRAC)
  Objective 5: Crash Prediction Model & Conflict Severity Ranking

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
    parser = argparse.ArgumentParser(description="Highway Traffic Flow & Surrogate Safety Analysis")
    parser.add_argument(
        "--trajectories",
        type=str,
        default="outputs/analysis/processed_trajectories_metric.csv",
        help="Path to processed metric trajectory CSV"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/safety_analysis",
        help="Directory to save safety metrics, tables, and figures"
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=30.0,
        help="Video frame rate (FPS)"
    )
    parser.add_argument(
        "--road-length-m",
        type=float,
        default=160.0,
        help="Visible highway segment length in meters"
    )
    return parser.parse_args()


def compute_objective_3_flow_and_speed(df, fps, road_length_m):
    """
    Objective 3:
    Derive vehicle count, speed (time-mean & space-mean), traffic density, and headways.
    """
    hwy = df[df["is_highway_corridor"]].copy()

    # Determine travel direction per vehicle
    dx_map = {}
    for tid, g in hwy.groupby("track_id"):
        dx = g["smooth_x_m"].iloc[-1] - g["smooth_x_m"].iloc[0]
        dx_map[tid] = "Eastbound" if dx > 0 else "Westbound"
    hwy["direction"] = hwy["track_id"].map(dx_map)

    total_duration_sec = (hwy["frame_id"].max() - hwy["frame_id"].min() + 1) / fps
    total_duration_hours = total_duration_sec / 3600.0

    # Moving vehicles on the highway corridor (> 10m traveled)
    track_summary = []
    for tid, g in hwy.groupby("track_id"):
        dx = abs(g["smooth_x_m"].iloc[-1] - g["smooth_x_m"].iloc[0])
        dur = float(g["timestamp_sec"].iloc[-1] - g["timestamp_sec"].iloc[0])
        valid_speeds = g["speed_kmh_unverified"].iloc[1:-1] if len(g) > 2 else g["speed_kmh_unverified"]
        mean_v = float(valid_speeds.median()) if len(valid_speeds) > 0 else 0.0
        cls = g["class_name"].mode()[0] if not g["class_name"].empty else "unknown"
        dir_name = dx_map.get(tid, "Westbound")

        track_summary.append({
            "track_id": tid,
            "class_name": cls,
            "direction": dir_name,
            "distance_m": dx,
            "duration_sec": dur,
            "mean_speed_kmh": mean_v,
            "is_moving": bool(dx >= 10.0 and mean_v >= 5.0)
        })

    sum_df = pd.DataFrame(track_summary)
    moving_df = sum_df[sum_df["is_moving"]].copy()

    # Flow Rate q (veh/h)
    unique_vehicles = moving_df["track_id"].nunique()
    flow_rate_total = unique_vehicles / total_duration_hours if total_duration_hours > 0 else 0
    flow_rate_east = moving_df[moving_df["direction"] == "Eastbound"]["track_id"].nunique() / total_duration_hours
    flow_rate_west = moving_df[moving_df["direction"] == "Westbound"]["track_id"].nunique() / total_duration_hours

    # Traffic Density k (veh/km)
    # Average number of simultaneous vehicles in the 160m segment
    simultaneous_counts = hwy.groupby("frame_id")["track_id"].nunique()
    avg_veh_in_segment = simultaneous_counts.mean()
    density_k_total = avg_veh_in_segment / (road_length_m / 1000.0)

    # Time-Mean Speed ut (Arithmetic Mean) and Space-Mean Speed us (Harmonic Mean)
    speeds_kmh = moving_df["mean_speed_kmh"].values
    speeds_mps = speeds_kmh / 3.6
    time_mean_speed_kmh = float(np.mean(speeds_kmh)) if len(speeds_kmh) > 0 else 0.0
    space_mean_speed_kmh = float(len(speeds_mps) / np.sum(1.0 / speeds_mps) * 3.6) if len(speeds_mps) > 0 else 0.0
    speed_std_kmh = float(np.std(speeds_kmh)) if len(speeds_kmh) > 0 else 0.0
    speed_p85_kmh = float(np.percentile(speeds_kmh, 85)) if len(speeds_kmh) > 0 else 0.0

    # Classified Speed Breakdown
    class_speed_stats = {}
    for c_name, g in moving_df.groupby("class_name"):
        s_arr = g["mean_speed_kmh"].values
        class_speed_stats[c_name] = {
            "count": int(len(g)),
            "mean_kmh": round(float(np.mean(s_arr)), 2),
            "median_kmh": round(float(np.median(s_arr)), 2),
            "p85_kmh": round(float(np.percentile(s_arr, 85)), 2),
            "min_kmh": round(float(np.min(s_arr)), 2),
            "max_kmh": round(float(np.max(s_arr)), 2)
        }

    # Headways (Distance & Time Headways)
    # Measured between consecutive vehicles in each direction
    headway_records = []
    for fid, f_df in hwy.groupby("frame_id"):
        for dir_name, d_df in f_df.groupby("direction"):
            if len(d_df) < 2:
                continue
            asc = False if dir_name == "Eastbound" else True
            sorted_v = d_df.sort_values("smooth_x_m", ascending=asc).to_dict("records")
            for i in range(len(sorted_v) - 1):
                ldr = sorted_v[i]
                flr = sorted_v[i + 1]
                lat_d = abs(ldr["smooth_y_m"] - flr["smooth_y_m"])
                if lat_d < 2.5: # Same lane follower
                    dist_hw = abs(ldr["smooth_x_m"] - flr["smooth_x_m"])
                    v_flr_mps = max(0.5, flr["speed_kmh_unverified"] / 3.6)
                    time_hw = dist_hw / v_flr_mps
                    if 0.2 <= time_hw <= 12.0:
                        headway_records.append({
                            "frame_id": fid,
                            "direction": dir_name,
                            "distance_headway_m": dist_hw,
                            "time_headway_sec": time_hw
                        })

    hw_df = pd.DataFrame(headway_records)
    mean_dist_hw = float(hw_df["distance_headway_m"].mean()) if not hw_df.empty else 0.0
    median_dist_hw = float(hw_df["distance_headway_m"].median()) if not hw_df.empty else 0.0
    mean_time_hw = float(hw_df["time_headway_sec"].mean()) if not hw_df.empty else 0.0
    median_time_hw = float(hw_df["time_headway_sec"].median()) if not hw_df.empty else 0.0

    obj3_results = {
        "objective": "Objective 3: Traffic Count, Speed & Density",
        "calibration_status": "UNVERIFIED_PRELIMINARY",
        "methodology_disclaimer": "Assumed 3.5m lane width without surveyed ground truth. Speeds and distances are strictly unverified.",
        "duration_sec": round(total_duration_sec, 2),
        "total_unique_vehicles": int(unique_vehicles),
        "class_breakdown": moving_df["class_name"].value_counts().to_dict(),
        "directional_split": moving_df["direction"].value_counts().to_dict(),
        "flow_rate_q_veh_per_hr": {
            "total": round(flow_rate_total, 1),
            "eastbound": round(flow_rate_east, 1),
            "westbound": round(flow_rate_west, 1)
        },
        "traffic_density_k_veh_per_km": {
            "average_vehicles_in_segment": round(avg_veh_in_segment, 2),
            "density_k": round(density_k_total, 1),
            "segment_length_m": road_length_m
        },
        "speed_analysis_kmh_unverified": {
            "time_mean_speed_ut": round(time_mean_speed_kmh, 2),
            "space_mean_speed_us": round(space_mean_speed_kmh, 2),
            "speed_std_dev": round(speed_std_kmh, 2),
            "speed_85th_percentile_v85": round(speed_p85_kmh, 2),
            "speed_by_class": class_speed_stats
        },
        "headway_analysis": {
            "mean_distance_headway_m": round(mean_dist_hw, 2),
            "median_distance_headway_m": round(median_dist_hw, 2),
            "mean_time_headway_sec": round(mean_time_hw, 2),
            "median_time_headway_sec": round(median_time_hw, 2),
            "sample_headway_observations": len(hw_df)
        }
    }

    return obj3_results, hwy, moving_df, hw_df


def compute_objective_4_surrogate_safety_measures(hwy):
    """
    Objective 4:
    Evaluate microscopic surrogate safety measures:
      - Time-To-Collision (TTC)
      - Modified TTC (MTTC)
      - Deceleration Rate to Avoid Collision (DRAC)
      - Post-Encroachment Time (PET)
    """
    len_map = {"car": 4.5, "van": 5.0, "bus": 10.5, "truck": 10.0, "motor": 2.0}
    hwy = hwy.copy()
    hwy["veh_len"] = hwy["class_name"].map(len_map).fillna(4.5)

    # 1. Car-Following Conflicts (TTC & DRAC)
    ttc_events = []
    for fid, frame_df in hwy.groupby("frame_id"):
        for dir_name, dir_df in frame_df.groupby("direction"):
            if len(dir_df) < 2:
                continue
            asc = False if dir_name == "Eastbound" else True
            sorted_v = dir_df.sort_values("smooth_x_m", ascending=asc).to_dict("records")

            for i in range(len(sorted_v) - 1):
                leader = sorted_v[i]
                follower = sorted_v[i + 1]

                lat_diff = abs(leader["smooth_y_m"] - follower["smooth_y_m"])
                if lat_diff < 2.5: # Following in same corridor
                    long_diff = abs(leader["smooth_x_m"] - follower["smooth_x_m"])
                    clear_gap = max(0.5, long_diff - leader["veh_len"])

                    v_f_mps = follower["speed_kmh_unverified"] / 3.6
                    v_l_mps = leader["speed_kmh_unverified"] / 3.6
                    delta_v_mps = v_f_mps - v_l_mps

                    if delta_v_mps > 0.3: # Closing in
                        ttc = clear_gap / delta_v_mps
                        drac = (delta_v_mps ** 2) / (2.0 * clear_gap)

                        if ttc <= 6.0:
                            # Severity categorization
                            if ttc < 1.5 or drac > 3.4:
                                cat = "Critical (Near Crash)"
                            elif ttc < 2.5 or drac > 2.0:
                                cat = "Severe Conflict"
                            else:
                                cat = "Potential Conflict"

                            ttc_events.append({
                                "frame_id": int(fid),
                                "time_sec": round(float(follower["timestamp_sec"]), 3),
                                "direction": dir_name,
                                "follower_id": int(follower["track_id"]),
                                "leader_id": int(leader["track_id"]),
                                "follower_class": follower["class_name"],
                                "leader_class": leader["class_name"],
                                "follower_x_m": round(float(follower["smooth_x_m"]), 2),
                                "follower_y_m": round(float(follower["smooth_y_m"]), 2),
                                "clear_gap_m": round(float(clear_gap), 2),
                                "closing_speed_kmh": round(float(delta_v_mps * 3.6), 2),
                                "ttc_sec": round(float(ttc), 2),
                                "drac_mps2": round(float(drac), 2),
                                "conflict_category": cat
                            })

    ttc_df = pd.DataFrame(ttc_events)

    # 2. Encroachment Conflicts (PET)
    # Discretize road corridor into 5m x 2.5m grid cells
    hwy["cell_x"] = (hwy["smooth_x_m"] // 5.0).astype(int)
    hwy["cell_y"] = (hwy["smooth_y_m"] // 2.5).astype(int)

    cell_visits = []
    for (cx, cy, tid), g in hwy.groupby(["cell_x", "cell_y", "track_id"]):
        cell_visits.append({
            "cell_x": cx,
            "cell_y": cy,
            "track_id": tid,
            "class_name": g["class_name"].iloc[0],
            "t_entry": g["timestamp_sec"].min(),
            "t_exit": g["timestamp_sec"].max()
        })
    cv_df = pd.DataFrame(cell_visits)

    pet_events = []
    for (cx, cy), g in cv_df.groupby(["cell_x", "cell_y"]):
        if len(g) < 2:
            continue
        g_sorted = g.sort_values("t_entry").to_dict("records")
        for i in range(len(g_sorted) - 1):
            veh_a = g_sorted[i]
            veh_b = g_sorted[i + 1]
            if veh_a["track_id"] != veh_b["track_id"]:
                pet = veh_b["t_entry"] - veh_a["t_exit"]
                if 0.05 < pet <= 4.0:
                    if pet <= 1.0:
                        p_cat = "Critical Encroachment"
                    elif pet <= 2.0:
                        p_cat = "Severe Encroachment"
                    else:
                        p_cat = "Moderate Encroachment"

                    pet_events.append({
                        "cell_x_m": round(float(cx * 5.0 + 2.5), 1),
                        "cell_y_m": round(float(cy * 2.5 + 1.25), 1),
                        "leading_id": int(veh_a["track_id"]),
                        "trailing_id": int(veh_b["track_id"]),
                        "leading_class": veh_a["class_name"],
                        "trailing_class": veh_b["class_name"],
                        "t_exit_leading": round(float(veh_a["t_exit"]), 3),
                        "t_entry_trailing": round(float(veh_b["t_entry"]), 3),
                        "pet_sec": round(float(pet), 3),
                        "encroachment_category": p_cat
                    })

    pet_df = pd.DataFrame(pet_events)

    obj4_results = {
        "objective": "Objective 4: Microscopic Surrogate Safety Measures (SSMs)",
        "ttc_analysis": {
            "total_following_conflict_instances": len(ttc_df),
            "critical_ttc_under_1_5s": int((ttc_df["ttc_sec"] < 1.5).sum()) if not ttc_df.empty else 0,
            "severe_ttc_1_5s_to_2_5s": int(((ttc_df["ttc_sec"] >= 1.5) & (ttc_df["ttc_sec"] < 2.5)).sum()) if not ttc_df.empty else 0,
            "potential_ttc_2_5s_to_4_0s": int(((ttc_df["ttc_sec"] >= 2.5) & (ttc_df["ttc_sec"] <= 4.0)).sum()) if not ttc_df.empty else 0,
            "drac_exceeding_3_4_mps2": int((ttc_df["drac_mps2"] > 3.4).sum()) if not ttc_df.empty else 0,
            "mean_critical_ttc": round(float(ttc_df[ttc_df["ttc_sec"] < 1.5]["ttc_sec"].mean()), 2) if not ttc_df.empty and (ttc_df["ttc_sec"] < 1.5).sum() > 0 else 0.0
        },
        "pet_analysis": {
            "total_encroachment_instances": len(pet_df),
            "critical_pet_under_1_0s": int((pet_df["pet_sec"] <= 1.0).sum()) if not pet_df.empty else 0,
            "severe_pet_1_0s_to_2_0s": int(((pet_df["pet_sec"] > 1.0) & (pet_df["pet_sec"] <= 2.0)).sum()) if not pet_df.empty else 0,
            "moderate_pet_2_0s_to_4_0s": int(((pet_df["pet_sec"] > 2.0) & (pet_df["pet_sec"] <= 4.0)).sum()) if not pet_df.empty else 0,
            "median_pet_sec": round(float(pet_df["pet_sec"].median()), 2) if not pet_df.empty else 0.0
        }
    }

    return obj4_results, ttc_df, pet_df


def compute_objective_5_crash_prediction_and_ranking(ttc_df, pet_df):
    """
    Objective 5:
    Develop crash prediction model and rank severity of potential collisions
    based on evaluated surrogate safety measures (TTC, DRAC, PET, vehicle vulnerability).
    """
    # Group car-following conflicts by unique interacting pair (follower_id, leader_id)
    pair_records = []
    if not ttc_df.empty:
        for (f_id, l_id), g in ttc_df.groupby(["follower_id", "leader_id"]):
            min_ttc = float(g["ttc_sec"].min())
            max_drac = float(g["drac_mps2"].max())
            max_closing_spd = float(g["closing_speed_kmh"].max())
            dur_conflict = float(g["time_sec"].max() - g["time_sec"].min())
            direction = g["direction"].iloc[0]
            f_cls = g["follower_class"].iloc[0]
            l_cls = g["leader_class"].iloc[0]

            # Representative location of conflict (follower position at min TTC)
            min_row = g.loc[g["ttc_sec"].idxmin()]
            x_loc = float(min_row["follower_x_m"])
            y_loc = float(min_row["follower_y_m"])

            # Vehicle mass / vulnerability weighting:
            # Heavy vehicles (bus, truck) or vulnerable road users (motor) increase severity
            mass_w = 1.0
            if f_cls in ["truck", "bus"] or l_cls in ["truck", "bus"]:
                mass_w = 1.35
            elif f_cls == "motor" or l_cls == "motor":
                mass_w = 1.25

            # Conflict Severity Score (CSS) formulation (0 to 10 scale):
            # S_TTC = max(0, (3.0 - min_ttc) / 3.0) * 4.0
            # S_DRAC = min(1.0, max_drac / 5.0) * 3.0
            # S_V = min(1.0, max_closing_spd / 20.0) * 3.0
            s_ttc = max(0.0, (3.0 - min_ttc) / 3.0) * 4.0
            s_drac = min(1.0, max_drac / 5.0) * 3.0
            s_v = min(1.0, max_closing_spd / 20.0) * 3.0
            raw_css = (s_ttc + s_drac + s_v) * mass_w
            css = round(min(10.0, raw_css), 2)

            # Severity Risk Tier
            if min_ttc < 1.0 or max_drac > 3.4 or css >= 7.5:
                risk_tier = "Tier 1: High / Critical Collision Risk"
                prob_level = "High"
            elif min_ttc < 2.0 or max_drac > 2.0 or css >= 5.0:
                risk_tier = "Tier 2: Moderate Collision Risk"
                prob_level = "Medium"
            else:
                risk_tier = "Tier 3: Low Collision Risk"
                prob_level = "Low"

            pair_records.append({
                "follower_id": f_id,
                "leader_id": l_id,
                "follower_class": f_cls,
                "leader_class": l_cls,
                "direction": direction,
                "min_ttc_sec": min_ttc,
                "max_drac_mps2": max_drac,
                "max_closing_speed_kmh": max_closing_spd,
                "conflict_duration_sec": round(dur_conflict, 2),
                "conflict_x_m": round(x_loc, 1),
                "conflict_y_m": round(y_loc, 1),
                "conflict_severity_score": css,
                "risk_tier": risk_tier,
                "crash_probability": prob_level
            })

    ranked_pairs_df = pd.DataFrame(pair_records)
    if not ranked_pairs_df.empty:
        ranked_pairs_df = ranked_pairs_df.sort_values("conflict_severity_score", ascending=False).reset_index(drop=True)
        ranked_pairs_df["rank"] = ranked_pairs_df.index + 1

    # Conflict Hotspots (spatial clustering in X along the road)
    hotspot_bins = np.arange(-40, 140, 20)
    if not ranked_pairs_df.empty:
        ranked_pairs_df["hotspot_zone_m"] = pd.cut(ranked_pairs_df["conflict_x_m"], bins=hotspot_bins).astype(str)
        hotspot_counts = ranked_pairs_df["hotspot_zone_m"].value_counts().sort_index()
        hotspots_dict = {str(k): int(v) for k, v in hotspot_counts.items()}
    else:
        hotspots_dict = {}

    tier_breakdown = ranked_pairs_df["risk_tier"].value_counts().to_dict() if not ranked_pairs_df.empty else {}

    obj5_results = {
        "objective": "Objective 5: Crash Prediction Model & Severity Ranking",
        "total_conflict_pairs_evaluated": len(ranked_pairs_df),
        "risk_tier_breakdown": tier_breakdown,
        "high_risk_conflict_pairs": int((ranked_pairs_df["conflict_severity_score"] >= 7.5).sum()) if not ranked_pairs_df.empty else 0,
        "spatial_hotspots_20m_intervals": hotspots_dict,
        "top_ranked_conflicts": ranked_pairs_df.head(10).to_dict("records") if not ranked_pairs_df.empty else []
    }

    return obj5_results, ranked_pairs_df


def generate_safety_visualizations(obj3, obj4, obj5, moving_df, hw_df, ttc_df, pet_df, ranked_pairs_df, output_dir):
    """Generate high-resolution figures for Objectives 3, 4, and 5."""
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Figure 1: Objective 3 - Speed by Vehicle Classification
    fig, ax = plt.subplots(figsize=(9, 5.5))
    class_speeds = [g["mean_speed_kmh"].values for _, g in moving_df.groupby("class_name")]
    class_labels = [name for name, _ in moving_df.groupby("class_name")]

    bplot = ax.boxplot(class_speeds, tick_labels=class_labels, patch_artist=True, medianprops=dict(color="red", linewidth=2))
    colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"]
    for patch, color in zip(bplot["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_title("Vehicle Operating Speed by Classification (National Highway 48)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Vehicle Classification", fontsize=11)
    ax.set_ylabel("Speed (km/h)", fontsize=11)
    plt.tight_layout()
    fig1_path = os.path.join(output_dir, "speed_by_classification.png")
    plt.savefig(fig1_path, dpi=200)
    plt.close()

    # Figure 2: Objective 3 - Distance vs Time Headway Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    if not hw_df.empty:
        ax1.hist(hw_df["distance_headway_m"], bins=20, color="#3470a3", edgecolor="black", alpha=0.8)
        ax1.axvline(hw_df["distance_headway_m"].median(), color="red", linestyle="--", label=f"Median: {hw_df['distance_headway_m'].median():.1f}m")
        ax1.set_title("Distance Headway ($h_d$) Distribution", fontsize=12, fontweight="bold")
        ax1.set_xlabel("Distance Headway (meters)")
        ax1.set_ylabel("Frequency")
        ax1.legend()

        ax2.hist(hw_df["time_headway_sec"], bins=20, color="#d95f02", edgecolor="black", alpha=0.8)
        ax2.axvline(hw_df["time_headway_sec"].median(), color="blue", linestyle="--", label=f"Median: {hw_df['time_headway_sec'].median():.2f}s")
        ax2.axvline(1.5, color="red", linestyle=":", label="Critical Threshold (1.5s)")
        ax2.set_title("Time Headway ($h_t$) Distribution", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Time Headway (seconds)")
        ax2.set_ylabel("Frequency")
        ax2.legend()

    plt.tight_layout()
    fig2_path = os.path.join(output_dir, "headway_distribution.png")
    plt.savefig(fig2_path, dpi=200)
    plt.close()

    # Figure 3: Objective 4 - Time-To-Collision (TTC) Cumulative & Distribution
    fig, ax = plt.subplots(figsize=(9, 5.5))
    if not ttc_df.empty:
        ttc_vals = ttc_df["ttc_sec"].values
        ax.hist(ttc_vals, bins=30, range=(0, 6), color="#e15759", edgecolor="black", alpha=0.75, density=False)
        ax.axvline(1.5, color="darkred", linestyle="--", linewidth=2.5, label="Critical TTC Threshold (1.5s)")
        ax.axvline(2.5, color="darkorange", linestyle=":", linewidth=2, label="Severe TTC Threshold (2.5s)")
        ax.set_title("Microscopic Surrogate Safety Measure: Time-To-Collision (TTC)\nNational Highway 48", fontsize=13, fontweight="bold")
        ax.set_xlabel("Time-To-Collision (seconds)", fontsize=11)
        ax.set_ylabel("Conflict Frequency", fontsize=11)
        ax.legend(fontsize=11)
    plt.tight_layout()
    fig3_path = os.path.join(output_dir, "ttc_distribution.png")
    plt.savefig(fig3_path, dpi=200)
    plt.close()

    # Figure 4: Objective 4 - Post-Encroachment Time (PET) Distribution
    fig, ax = plt.subplots(figsize=(9, 5.5))
    if not pet_df.empty:
        pet_vals = pet_df["pet_sec"].values
        ax.hist(pet_vals, bins=25, range=(0, 4), color="#76b7b2", edgecolor="black", alpha=0.85)
        ax.axvline(1.0, color="red", linestyle="--", linewidth=2.5, label="Critical PET Threshold (1.0s)")
        ax.axvline(2.0, color="orange", linestyle=":", linewidth=2, label="Severe PET Threshold (2.0s)")
        ax.set_title("Post-Encroachment Time (PET) Conflict Distribution (NH-48)", fontsize=13, fontweight="bold")
        ax.set_xlabel("Post-Encroachment Time (seconds)", fontsize=11)
        ax.set_ylabel("Encroachment Events", fontsize=11)
        ax.legend(fontsize=11)
    plt.tight_layout()
    fig4_path = os.path.join(output_dir, "pet_distribution.png")
    plt.savefig(fig4_path, dpi=200)
    plt.close()

    # Figure 5: Objective 5 - Collision Severity Ranking & Hotspots Map
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5))
    if not ranked_pairs_df.empty:
        # Scatter of conflict locations along the corridor colored by severity score
        sc = ax1.scatter(
            ranked_pairs_df["conflict_x_m"],
            ranked_pairs_df["conflict_y_m"],
            c=ranked_pairs_df["conflict_severity_score"],
            cmap="YlOrRd",
            s=ranked_pairs_df["conflict_severity_score"] * 25,
            edgecolors="black",
            alpha=0.85
        )
        cbar = plt.colorbar(sc, ax=ax1, orientation="vertical", pad=0.02)
        cbar.set_label("Conflict Severity Score (0-10)", fontsize=10)
        ax1.axhline(0, color="gray", linestyle="--", alpha=0.5, label="Median Separation (approx)")
        ax1.set_title("Spatial Conflict Hotspot Mapping along National Highway 48", fontsize=13, fontweight="bold")
        ax1.set_xlabel("Longitudinal Distance (meters) along Highway", fontsize=10)
        ax1.set_ylabel("Lateral Position (meters)", fontsize=10)
        ax1.legend(loc="upper right")

        # Top 10 Ranked Conflict Pairs Bar Chart
        top10 = ranked_pairs_df.head(10)
        pair_labels = [f"Flr:{r['follower_id']} ({r['follower_class']})\nLdr:{r['leader_id']} ({r['leader_class']})" for _, r in top10.iterrows()]
        y_pos = np.arange(len(top10))
        bars = ax2.barh(y_pos, top10["conflict_severity_score"], color="#b03030", edgecolor="black", alpha=0.85)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(pair_labels, fontsize=9)
        ax2.invert_yaxis()
        ax2.set_title("Top 10 Most Critical Collision Conflict Pairs (Ranked)", fontsize=13, fontweight="bold")
        ax2.set_xlabel("Conflict Severity Score (CSS)", fontsize=10)
        for bar in bars:
            w = bar.get_width()
            ax2.text(w + 0.1, bar.get_y() + bar.get_height() / 2, f"{w:.2f}", va="center", fontweight="bold", fontsize=9)

    plt.tight_layout()
    fig5_path = os.path.join(output_dir, "crash_ranking_and_hotspots.png")
    plt.savefig(fig5_path, dpi=200)
    plt.close()

    return {
        "speed_by_classification": fig1_path,
        "headway_distribution": fig2_path,
        "ttc_distribution": fig3_path,
        "pet_distribution": fig4_path,
        "crash_ranking_and_hotspots": fig5_path
    }


def main():
    args = parse_args()
    if not os.path.exists(args.trajectories):
        print(f"ERROR: File not found: {args.trajectories}", file=sys.stderr)
        sys.exit(1)

    print("=" * 65)
    print(" Running Objectives 3, 4, and 5 Analysis Pipeline ")
    print("=" * 65)
    df = pd.read_csv(args.trajectories)

    # 1. Objective 3
    print("[1/3] Computing Objective 3: Traffic Count, Speeds, Density & Headways...")
    obj3, hwy, moving_df, hw_df = compute_objective_3_flow_and_speed(df, args.fps, args.road_length_m)

    # 2. Objective 4
    print("[2/3] Computing Objective 4: Surrogate Safety Measures (TTC, PET, DRAC)...")
    obj4, ttc_df, pet_df = compute_objective_4_surrogate_safety_measures(hwy)

    # 3. Objective 5
    print("[3/3] Computing Objective 5: Crash Prediction Model & Severity Ranking...")
    obj5, ranked_pairs_df = compute_objective_5_crash_prediction_and_ranking(ttc_df, pet_df)

    # Save Tables
    os.makedirs(args.output_dir, exist_ok=True)
    ttc_csv = os.path.join(args.output_dir, "car_following_conflicts_ttc.csv")
    pet_csv = os.path.join(args.output_dir, "encroachment_conflicts_pet.csv")
    ranking_csv = os.path.join(args.output_dir, "ranked_collision_conflicts.csv")

    ttc_df.to_csv(ttc_csv, index=False)
    pet_df.to_csv(pet_csv, index=False)
    ranked_pairs_df.to_csv(ranking_csv, index=False)

    # Generate Visualizations
    print("Generating comprehensive figures...")
    figures = generate_safety_visualizations(
        obj3, obj4, obj5, moving_df, hw_df, ttc_df, pet_df, ranked_pairs_df, args.output_dir
    )

    # Compile Final JSON Report
    full_report = {
        "status": "COMPLETED_UNVERIFIED_PRELIMINARY",
        "video": "National Highway 48.mp4",
        "objective_3": obj3,
        "objective_4": obj4,
        "objective_5": obj5,
        "artifacts_generated": {
            "tables": {
                "ttc_conflicts_csv": ttc_csv,
                "pet_encroachments_csv": pet_csv,
                "ranked_collision_conflicts_csv": ranking_csv
            },
            "figures": figures
        }
    }

    report_json = os.path.join(args.output_dir, "comprehensive_safety_report.json")
    with open(report_json, "w") as f:
        json.dump(full_report, f, indent=2)

    print("\n" + "=" * 65)
    print(" Comprehensive Safety & Flow Analysis Complete ")
    print("=" * 65)
    print(f"Vehicle Count Tracked  : {obj3['total_unique_vehicles']}")
    print(f"Flow Rate Total (q)    : {obj3['flow_rate_q_veh_per_hr']['total']} veh/h")
    print(f"Traffic Density (k)    : {obj3['traffic_density_k_veh_per_km']['density_k']} veh/km")
    print(f"Time-Mean Speed (ut)   : {obj3['speed_analysis_kmh_unverified']['time_mean_speed_ut']} km/h (UNVERIFIED)")
    print(f"Space-Mean Speed (us)  : {obj3['speed_analysis_kmh_unverified']['space_mean_speed_us']} km/h (UNVERIFIED)")
    print(f"Critical TTC Events    : {obj4['ttc_analysis']['critical_ttc_under_1_5s']} instances (< 1.5s)")
    print(f"Critical PET Events    : {obj4['pet_analysis']['critical_pet_under_1_0s']} instances (<= 1.0s)")
    print(f"DRAC > 3.4 m/s^2       : {obj4['ttc_analysis']['drac_exceeding_3_4_mps2']} instances")
    print(f"Total Conflict Pairs   : {obj5['total_conflict_pairs_evaluated']}")
    print(f"High-Risk Pairs        : {obj5['high_risk_conflict_pairs']}")
    print(f"Full Report JSON       : {report_json}")
    print("=" * 65)


if __name__ == "__main__":
    main()
