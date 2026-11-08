import pandas as pd
import numpy as np
from pathlib import Path
import json

# Helper functions for surrogate safety metrics

def compute_ttc(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Time-to-Collision (TTC) for each pair of vehicles on the same frame.
    Simplified longitudinal TTC assuming constant speed and same lane.
    Returns a DataFrame with columns: frame, lead_id, follow_id, ttc_s.
    """
    records = []
    # Ensure speed column exists; if not, set to NaN
    if 'speed_mps' not in df.columns:
        df['speed_mps'] = np.nan
    for frame, grp in df.groupby('frame'):
        # Sort by longitudinal position (x) - assuming x increases downstream
        sorted_grp = grp.sort_values('x')
        ids = sorted_grp['track_id'].values
        xs = sorted_grp['x'].values
        speeds = sorted_grp['speed_mps'].values
        for i in range(len(ids) - 1):
            lead_id, follow_id = ids[i+1], ids[i]
            lead_speed, follow_speed = speeds[i+1], speeds[i]
            gap = xs[i+1] - xs[i]
            rel_speed = follow_speed - lead_speed
            if rel_speed <= 0:
                continue  # no closing
            ttc = gap / rel_speed if rel_speed != 0 else np.inf
            records.append({
                'frame': frame,
                'lead_id': int(lead_id),
                'follow_id': int(follow_id),
                'ttc_s': float(ttc)
            })
    return pd.DataFrame(records)

def compute_pet(df: pd.DataFrame, proximity_m: float = 2.0) -> pd.DataFrame:
    """Compute Potential Encounter Time (PET) - a proximity metric.
    If two vehicles are within *proximity_m* meters on the same frame, record the event.
    """
    records = []
    for frame, grp in df.groupby('frame'):
        coords = grp[['x', 'y']].values
        ids = grp['track_id'].values
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                dist = np.linalg.norm(coords[i] - coords[j])
                if dist <= proximity_m:
                    records.append({
                        'frame': frame,
                        'veh_a': int(ids[i]),
                        'veh_b': int(ids[j]),
                        'distance_m': float(dist)
                    })
    return pd.DataFrame(records)

def run_safety_analysis(trajectory_csv: Path | str, output_dir: Path | str, fps: float = 30.0, homography_path: Path | str = None) -> Path:
    """Perform surrogate safety analysis and save results as CSV/JSON.
    * TTC < 1.5 s are considered critical.
    * PET (proximity) < 2 m are considered encroachments.
    """
    traj_path = Path(trajectory_csv)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(traj_path)
    # Ensure speed column exists - if not, compute using homography if provided
    if homography_path and 'speed_mps' not in df.columns:
        from .analysis import load_homography, compute_speed
        H = load_homography(homography_path)
        df = compute_speed(df, H, fps)
    ttc_df = compute_ttc(df)
    critical_ttc = ttc_df[ttc_df['ttc_s'] < 1.5]
    pet_df = compute_pet(df)
    critical_pet = pet_df[pet_df['distance_m'] <= 2.0]
    # Save outputs
    ttc_df.to_csv(out_dir / 'ttc_all.csv', index=False)
    critical_ttc.to_csv(out_dir / 'critical_ttc.csv', index=False)
    pet_df.to_csv(out_dir / 'pet_all.csv', index=False)
    critical_pet.to_csv(out_dir / 'critical_pet.csv', index=False)
    # Summary JSON
    summary = {
        'total_ttc_events': len(ttc_df),
        'critical_ttc_events': len(critical_ttc),
        'total_pet_events': len(pet_df),
        'critical_pet_events': len(critical_pet)
    }
    with (out_dir / 'safety_summary.json').open('w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"[INFO] Safety analysis saved to {out_dir}")
    return out_dir / 'safety_summary.json'
