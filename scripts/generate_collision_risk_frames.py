"""
Generate Visual Collision-Risk Annotations on Actual UAV Video Frames
=====================================================================
Extracts the exact video frames corresponding to the highest-risk vehicle conflict
events identified by the surrogate safety analysis (ranked_collision_conflicts.csv
and car_following_conflicts_ttc.csv), projects vehicle bounding boxes, connecting
critical-distance vector lines, impact hotspot crosshairs, and detailed telemetry HUDs.

Output:
  - outputs/safety_analysis/conflict_frames/conflict_rank_01_frame_*.jpg ...
  - outputs/safety_analysis/critical_distance_analysis.json
"""

import json
import os
import cv2
import numpy as np
import pandas as pd


def compute_stopping_safe_distance(v_follower_kmh, v_leader_kmh, t_reaction=1.5, a_follower=3.4, a_leader=3.4):
    """
    Computes AASHTO / IRC kinematic stopping-distance-based safe headway:
    d_safe = v_f * t_r + (v_f^2 / (2 * a_f)) - (v_l^2 / (2 * a_l))
    """
    vf = max(0.0, v_follower_kmh / 3.6)
    vl = max(0.0, v_leader_kmh / 3.6)
    d_reaction = vf * t_reaction
    d_braking_follower = (vf ** 2) / (2.0 * a_follower)
    d_braking_leader = (vl ** 2) / (2.0 * a_leader)
    d_safe = d_reaction + d_braking_follower - d_braking_leader
    return max(2.0, d_safe)  # minimum 2m physical vehicle buffer


def main():
    video_path = "videos/National Highway 48.mp4"
    ranked_csv = "outputs/safety_analysis/ranked_collision_conflicts.csv"
    ttc_csv = "outputs/safety_analysis/car_following_conflicts_ttc.csv"
    traj_csv = "outputs/analysis/processed_trajectories_metric.csv"
    output_dir = "outputs/safety_analysis/conflict_frames"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(video_path):
        print(f"Error: Video not found at {video_path}")
        return

    df_ranked = pd.read_csv(ranked_csv)
    df_ttc = pd.read_csv(ttc_csv)
    df_traj = pd.read_csv(traj_csv)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    critical_events = []

    # Process Top 10 high-risk conflicts
    for _, row in df_ranked.head(10).iterrows():
        rank = int(row['rank'])
        f_id = int(row['follower_id'])
        l_id = int(row['leader_id'])
        f_class = str(row['follower_class'])
        l_class = str(row['leader_class'])
        direction = str(row['direction'])

        # Find matching frame with minimum TTC
        matches = df_ttc[(df_ttc['follower_id'] == f_id) & (df_ttc['leader_id'] == l_id)]
        if matches.empty:
            continue

        crit_row = matches.sort_values('ttc_sec').iloc[0]
        frame_id = int(crit_row['frame_id'])
        time_sec = float(crit_row['time_sec'])
        ttc = float(crit_row['ttc_sec'])
        drac = float(crit_row['drac_mps2'])
        clear_gap = float(crit_row['clear_gap_m'])
        closing_speed = float(crit_row['closing_speed_kmh'])
        conflict_x = float(row['conflict_x_m'])
        severity_score = float(row['conflict_severity_score'])
        risk_tier = str(row['risk_tier'])

        # Get bounding boxes at frame_id
        f_traj = df_traj[(df_traj['frame_id'] == frame_id) & (df_traj['track_id'] == f_id)]
        l_traj = df_traj[(df_traj['frame_id'] == frame_id) & (df_traj['track_id'] == l_id)]

        if f_traj.empty or l_traj.empty:
            continue

        f_row = f_traj.iloc[0]
        l_row = l_traj.iloc[0]

        v_follower = float(f_row.get('speed_kmh_unverified', 25.0))
        v_leader = float(l_row.get('speed_kmh_unverified', 15.0))
        d_safe = compute_stopping_safe_distance(v_follower, v_leader)
        d_margin = clear_gap - d_safe

        # Read video frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if not ret:
            continue

        h, w = frame.shape[:2]
        canvas = frame.copy()

        # Follower Box
        fbx1, fby1, fbx2, fby2 = int(f_row['bbox_x1']), int(f_row['bbox_y1']), int(f_row['bbox_x2']), int(f_row['bbox_y2'])
        fcx, fcy = (fbx1 + fbx2) // 2, (fby1 + fby2) // 2

        # Leader Box
        lbx1, lby1, lbx2, lby2 = int(l_row['bbox_x1']), int(l_row['bbox_y1']), int(l_row['bbox_x2']), int(l_row['bbox_y2'])
        lcx, lcy = (lbx1 + lbx2) // 2, (lby1 + lby2) // 2

        # Colors (BGR)
        COLOR_CRITICAL = (53, 59, 180)    # Deep Red / Crimson (#B43B35)
        COLOR_LEADER = (120, 124, 57)     # Muted Teal (#397C78)
        COLOR_WARN = (37, 121, 183)       # Burnt Amber (#B77925)
        COLOR_LINE = (0, 215, 255)        # Glowing Gold/Cyan line

        # Draw connecting line between vehicle centers
        cv2.line(canvas, (fcx, fcy), (lcx, lcy), COLOR_LINE, 2, cv2.LINE_AA)

        # Draw Follower Bounding Box with glow
        cv2.rectangle(canvas, (fbx1, fby1), (fbx2, fby2), COLOR_CRITICAL, 3, cv2.LINE_AA)
        f_label = f"FOLLOWER #{f_id} ({f_class.upper()}) | {v_follower:.1f} km/h"
        (fw, fh), _ = cv2.getTextSize(f_label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(canvas, (fbx1, fby1 - fh - 8), (fbx1 + fw + 6, fby1), COLOR_CRITICAL, -1)
        cv2.putText(canvas, f_label, (fbx1 + 3, fby1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Draw Leader Bounding Box
        cv2.rectangle(canvas, (lbx1, lby1), (lbx2, lby2), COLOR_LEADER, 3, cv2.LINE_AA)
        l_label = f"LEADER #{l_id} ({l_class.upper()}) | {v_leader:.1f} km/h"
        (lw, lh), _ = cv2.getTextSize(l_label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(canvas, (lbx1, lby1 - lh - 8), (lbx1 + lw + 6, lby1), COLOR_LEADER, -1)
        cv2.putText(canvas, l_label, (lbx1 + 3, lby1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Conflict Hotspot Marker at midpoint
        mid_x, mid_y = (fcx + lcx) // 2, (fcy + lcy) // 2
        cv2.circle(canvas, (mid_x, mid_y), 8, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.circle(canvas, (mid_x, mid_y), 3, (0, 0, 255), -1, cv2.LINE_AA)
        cv2.drawMarker(canvas, (mid_x, mid_y), (0, 255, 255), cv2.MARKER_CROSS, 16, 2)

        # Midpoint Distance Callout Tag
        dist_tag = f"GAP: {clear_gap:.2f}m (SAFE REQ: {d_safe:.1f}m)"
        (dw, dh), _ = cv2.getTextSize(dist_tag, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        tag_x = max(10, min(w - dw - 20, mid_x - dw // 2))
        tag_y = max(fh + 30, mid_y - 14)
        cv2.rectangle(canvas, (tag_x - 4, tag_y - dh - 6), (tag_x + dw + 4, tag_y + 4), (15, 15, 20), -1)
        cv2.rectangle(canvas, (tag_x - 4, tag_y - dh - 6), (tag_x + dw + 4, tag_y + 4), COLOR_CRITICAL, 1)
        cv2.putText(canvas, dist_tag, (tag_x, tag_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Telemetry HUD Card in Top Corner
        hud_w, hud_h = 420, 165
        hud_x, hud_y = 25, 25
        overlay = canvas.copy()
        cv2.rectangle(overlay, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (20, 20, 26), -1)
        cv2.addWeighted(overlay, 0.85, canvas, 0.15, 0, canvas)
        cv2.rectangle(canvas, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (180, 59, 53), 2)

        # HUD Text Entries
        cv2.putText(canvas, f"CRITICAL CONFLICT EVENT #{rank}", (hud_x + 15, hud_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, (53, 59, 240), 2, cv2.LINE_AA)
        
        hud_lines = [
            f"Conflict Pair     : #{f_id} ({f_class}) -> #{l_id} ({l_class}) [{direction}]",
            f"Observed Clearance: {clear_gap:.2f} m  |  Deficit: {d_margin:.2f} m",
            f"Time-To-Collision : {ttc:.2f} s (CRITICAL < 1.5s)",
            f"Decel Demand DRAC : {drac:.2f} m/s^2 (EMERGENCY > 3.4)",
            f"Relative Closing  : {closing_speed:.1f} km/h  |  X = {conflict_x:.1f} m",
            f"Video Time / Frame: t = {time_sec:.2f}s  (Frame #{frame_id})"
        ]

        for i, text in enumerate(hud_lines):
            cv2.putText(canvas, text, (hud_x + 15, hud_y + 48 + i * 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (230, 230, 230), 1, cv2.LINE_AA)

        # Bottom Attribution Badge
        badge_text = "UAV Traffic Flow & Surrogate Safety Analytics | Developed by Eric Jose"
        cv2.rectangle(canvas, (0, h - 28), (w, h), (18, 16, 14), -1)
        cv2.putText(canvas, badge_text, (20, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (180, 180, 180), 1, cv2.LINE_AA)

        # Save Frame
        out_filename = f"conflict_rank_{rank:02d}_frame_{frame_id:04d}.jpg"
        out_filepath = os.path.join(output_dir, out_filename)
        cv2.imwrite(out_filepath, canvas, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"[OK] Generated Rank #{rank} frame annotation -> {out_filename}")

        critical_events.append({
            "rank": rank,
            "follower_id": f_id,
            "leader_id": l_id,
            "follower_class": f_class,
            "leader_class": l_class,
            "direction": direction,
            "frame_id": frame_id,
            "time_sec": round(time_sec, 2),
            "clear_gap_m": round(clear_gap, 2),
            "stopping_safe_distance_m": round(d_safe, 2),
            "safety_margin_m": round(d_margin, 2),
            "ttc_sec": round(ttc, 2),
            "drac_mps2": round(drac, 2),
            "closing_speed_kmh": round(closing_speed, 1),
            "v_follower_kmh": round(v_follower, 1),
            "v_leader_kmh": round(v_leader, 1),
            "conflict_x_m": round(conflict_x, 1),
            "severity_score": round(severity_score, 1),
            "risk_tier": risk_tier,
            "image_filename": out_filename,
            "image_rel_path": f"safety_analysis/conflict_frames/{out_filename}"
        })

    cap.release()

    # Save complete JSON analysis
    json_path = "outputs/safety_analysis/critical_distance_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "status": "COMPLETED",
            "methodology": {
                "safe_distance_formula": "d_safe = v_f * t_r + (v_f^2 / (2 * a_f)) - (v_l^2 / (2 * a_l))",
                "perception_reaction_time_sec": 1.5,
                "emergency_braking_decel_mps2": 3.4,
                "critical_ttc_threshold_sec": 1.5,
                "emergency_drac_threshold_mps2": 3.4
            },
            "total_ranked_events": len(critical_events),
            "events": critical_events
        }, f, indent=2)

    print(f"\n[SUCCESS] Saved critical distance analysis to {json_path}")


if __name__ == "__main__":
    main()
