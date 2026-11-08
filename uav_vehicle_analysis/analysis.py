import pandas as pd
import numpy as np
from pathlib import Path
import json
import math

def load_homography(homography_path: Path | str) -> np.ndarray:
    """Load homography matrix saved by :pyfunc:`calibration.save_homography`."""
    with Path(homography_path).open('r', encoding='utf-8') as f:
        data = json.load(f)
    return np.array(data['homography'])

def world_coords(px, py, H):
    """Convert pixel coordinates (px, py) to world coordinates using homography H.
    Returns (x, y) in metres.
    """
    pt = np.array([px, py, 1.0])
    world = H @ pt
    world /= world[2]
    return world[0], world[1]

def compute_speed(df: pd.DataFrame, H: np.ndarray, fps: float) -> pd.DataFrame:
    """Add speed (m/s) column to trajectory dataframe.
    Speed is computed per track using successive world positions.
    """
    df = df.copy()
    df['speed_mps'] = np.nan
    for tid, group in df.groupby('track_id'):
        group = group.sort_values('frame')
        xs, ys = world_coords(group['x'].values, group['y'].values, H)
        dists = np.hypot(np.diff(xs), np.diff(ys))
        speeds = dists * fps  # m/s (dist per frame * fps)
        df.loc[group.index[1:], 'speed_mps'] = speeds
    return df

def aggregate_metrics(df: pd.DataFrame) -> dict:
    """Return a dictionary of high-level traffic metrics.
    * active_vehicles - number of distinct tracks
    * flow_rate - vehicles per hour (approx.)
    * density - vehicles per km (using corridor length from homography)
    * avg_speed - mean speed across all tracks (km/h)
    """
    active = df['track_id'].nunique()
    # approximate corridor length: take max x world coordinate
    H = np.eye(3)  # placeholder - callers should pass real H if needed for density
    xs, _ = world_coords(df['x'].values, df['y'].values, H)
    length_km = (np.max(xs) - np.min(xs)) / 1000 if xs.size else 1.0
    flow = active / (df['frame'].max() / 30) * 3600  # assuming 30 FPS video
    density = active / length_km if length_km else np.nan
    avg_speed_kmh = df['speed_mps'].mean() * 3.6 if 'speed_mps' in df else np.nan
    return {
        'active_vehicles': int(active),
        'flow_rate_veh_per_hr': round(flow, 2),
        'density_veh_per_km': round(density, 2),
        'average_speed_kmh': round(avg_speed_kmh, 2)
    }

def analyze_trajectories(input_csv: Path | str, output_dir: Path | str, fps: float = 30.0, homography_path: Path | str = None) -> Path:
    """Main entry point used by the pipeline.
    Loads ``trajectories.csv`` and writes a summary JSON and an enriched CSV with speed.
    """
    input_path = Path(input_csv)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_path)
    if homography_path:
        H = load_homography(homography_path)
        df = compute_speed(df, H, fps)
        enriched_csv = out_dir / "trajectories_with_speed.csv"
        df.to_csv(enriched_csv, index=False)
    else:
        enriched_csv = out_dir / "trajectories.csv"
        df.to_csv(enriched_csv, index=False)
    metrics = aggregate_metrics(df)
    metrics_path = out_dir / "traffic_metrics.json"
    with metrics_path.open('w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    print(f"[INFO] Analysis complete - metrics saved to {metrics_path}")
    return metrics_path
