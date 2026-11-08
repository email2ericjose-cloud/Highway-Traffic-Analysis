import cv2
import json
from pathlib import Path
import numpy as np

def compute_homography(clean_frame_path: Path, lane_width_m: float) -> np.ndarray:
    """Estimate a homography that maps pixel distances to real-world metres.

    The function expects *clean_frame_path* to point to a frame where lane markings
    are clearly visible. A simple approach is used:
    1. Detect lane markings with Canny + Hough lines.
    2. Choose two parallel lines that represent the lane edges.
    3. Measure the pixel distance between them and derive a scale factor.
    4. Build a similarity transform (scale + translation) that maps the centre of
       the image to the origin.

    Returns a 3x3 homography matrix (pixel -> world). If detection fails, an
    identity matrix is returned and a warning is printed.
    """
    img = cv2.imread(str(clean_frame_path))
    if img is None:
        raise FileNotFoundError(f"[ERROR] Clean frame not found: {clean_frame_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=50, maxLineGap=10)
    if lines is None or len(lines) < 2:
        print("[WARN] Not enough lane lines detected - using identity homography.")
        return np.eye(3)
    # Take first two lines as lane edges (naïve but works for clear frames)
    p1 = lines[0][0]
    p2 = lines[1][0]
    # Compute pixel distance between the two lines (average of end-points)
    def midpoint(line):
        x1, y1, x2, y2 = line
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    mid1 = midpoint(p1)
    mid2 = midpoint(p2)
    pixel_dist = np.hypot(mid1[0] - mid2[0], mid1[1] - mid2[1])
    if pixel_dist == 0:
        print("[WARN] Zero pixel distance - using identity homography.")
        return np.eye(3)
    scale = lane_width_m / pixel_dist
    # Build similarity transform: scale + translate image centre to (0,0)
    h, w = gray.shape
    tx, ty = -w / 2, -h / 2
    H = np.array([
        [scale, 0, scale * tx],
        [0, scale, scale * ty],
        [0, 0, 1]
    ])
    return H

def save_homography(H: np.ndarray, out_path: Path) -> None:
    """Save homography matrix as a JSON file for downstream stages."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({"homography": H.tolist()}, f, indent=2)
