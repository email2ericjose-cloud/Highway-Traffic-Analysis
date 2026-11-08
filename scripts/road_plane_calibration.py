"""
Road-Plane Homography Calibration Tool
=======================================
Performs perspective calibration from aerial drone camera pixel coordinates
to real-world road-plane coordinates (in meters).

Methodology & Protocol:
- Maps 4 user-selected points along lane markings to a metric road rectangle.
- NOTE: The assumed lane width of 3.5 m may be used ONLY for preliminary analysis
  and MUST be labelled unverified.
- Validated speeds must not be calculated or reported until ground-truth
  calibration data is verified.

Usage:
  # Interactive mode (click 4 points on road surface: Top-Left, Top-Right, Bottom-Right, Bottom-Left):
  python scripts/road_plane_calibration.py --image "outputs/calibration/clean_frame_NH48.png"

  # Non-interactive / Headless mode:
  python scripts/road_plane_calibration.py --image "outputs/calibration/clean_frame_NH48.png" \
      --src-points "x1,y1,x2,y2,x3,y3,x4,y4" --lane-width 3.5 --road-length 25.0
"""

import argparse
import json
import os
import sys
import cv2
import numpy as np


class PointSelector:
    """Helper to collect 4 points via OpenCV mouse callbacks."""
    def __init__(self, image, window_name="Select 4 Road Plane Points"):
        self.image = image.copy()
        self.clean_image = image.copy()
        self.window_name = window_name
        self.points = []

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) < 4:
                self.points.append((x, y))
                cv2.circle(self.image, (x, y), 5, (0, 0, 255), -1)
                cv2.putText(
                    self.image,
                    f"P{len(self.points)}: ({x},{y})",
                    (x + 8, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1,
                    cv2.LINE_AA
                )
                if len(self.points) > 1:
                    cv2.line(self.image, self.points[-2], self.points[-1], (0, 255, 0), 2)
                if len(self.points) == 4:
                    cv2.line(self.image, self.points[3], self.points[0], (0, 255, 0), 2)
                cv2.imshow(self.window_name, self.image)

    def select(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 720)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        print("\n[INSTRUCTIONS]")
        print("Click 4 road-plane boundary points in order:")
        print("  1: Top-Left (lane marking start)")
        print("  2: Top-Right (opposite lane marking start)")
        print("  3: Bottom-Right (opposite lane marking end)")
        print("  4: Bottom-Left (lane marking end)")
        print("Press 'r' to reset points, or 'q'/ENTER once all 4 points are chosen.")

        while True:
            cv2.imshow(self.window_name, self.image)
            key = cv2.waitKey(20) & 0xFF
            if key == ord('r'):
                self.points = []
                self.image = self.clean_image.copy()
                print("Points reset. Please click 4 points again.")
            elif key in [ord('q'), 13, 27]:  # 'q', Enter, or Esc
                if len(self.points) == 4:
                    break
                elif key == 27:
                    print("Calibration cancelled.")
                    sys.exit(0)
                else:
                    print(f"Please select all 4 points (currently {len(self.points)}).")

        cv2.destroyAllWindows()
        return self.points


def compute_calibration(src_points, lane_width_m=3.5, road_length_m=60.0):
    """
    Computes homography matrix from pixel coordinates to real-world metric coordinates.
    Highway orientation in image is horizontal (longitudinal along X, lateral lane width along Y):
      P1 (Top-Left):     (0.0, 0.0)
      P2 (Top-Right):    (road_length_m, 0.0)
      P3 (Bottom-Right): (road_length_m, lane_width_m)
      P4 (Bottom-Left):  (0.0, lane_width_m)
    """
    src = np.array(src_points, dtype=np.float32)
    dst = np.array([
        [0.0, 0.0],
        [road_length_m, 0.0],
        [road_length_m, lane_width_m],
        [0.0, lane_width_m]
    ], dtype=np.float32)

    H, _ = cv2.findHomography(src, dst)
    H_inv, _ = cv2.findHomography(dst, src)

    return H, H_inv, src, dst


def pixel_to_meter(H, u, v):
    """Transform pixel coordinate (u, v) to road plane (X, Y) meters."""
    pt = np.array([u, v, 1.0], dtype=np.float64)
    res = np.dot(H, pt)
    res /= res[2]
    return float(res[0]), float(res[1])


def generate_visualizations(image, src_points, H, output_dir, lane_width_m, road_length_m):
    """Generate visual overlay and bird's-eye view verification images."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Verification Overlay
    overlay = image.copy()
    pts = np.array(src_points, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    for idx, (x, y) in enumerate(src_points):
        cv2.circle(overlay, (int(x), int(y)), 6, (0, 0, 255), -1)
        cv2.putText(
            overlay,
            f"P{idx+1}",
            (int(x) + 8, int(y) - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA
        )

    # Clean Title Header
    banner_text = "National Highway 48 - Road-Plane Reference Coordinates"
    cv2.rectangle(overlay, (10, 10), (750, 50), (30, 30, 30), -1)
    cv2.putText(overlay, banner_text, (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    overlay_path = os.path.join(output_dir, "calibration_overlay.png")
    cv2.imwrite(overlay_path, overlay)

    # 2. Bird's Eye View (Warped Top-Down)
    # Warping to a synthetic canvas scaled for visualization (e.g. 25 pixels per meter)
    scale_px_per_m = 25
    bev_w = int(road_length_m * scale_px_per_m)
    bev_h = int(max(lane_width_m * scale_px_per_m, 100))

    dst_bev = np.array([
        [0, 0],
        [bev_w, 0],
        [bev_w, bev_h],
        [0, bev_h]
    ], dtype=np.float32)

    M_warp = cv2.getPerspectiveTransform(np.array(src_points, dtype=np.float32), dst_bev)
    bev_img = cv2.warpPerspective(image, M_warp, (bev_w, bev_h))

    # Add metric grid on BEV along longitudinal highway distance
    for xm in range(0, int(road_length_m) + 1, 10):
        x_px = int(xm * scale_px_per_m)
        cv2.line(bev_img, (x_px, 0), (x_px, bev_h), (0, 255, 255), 1)
        cv2.putText(bev_img, f"{xm}m", (x_px + 4, bev_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    bev_path = os.path.join(output_dir, "bird_eye_view.png")
    cv2.imwrite(bev_path, bev_img)

    return overlay_path, bev_path


def save_calibration_config(
    output_path,
    src_points,
    lane_width_m,
    road_length_m,
    H,
    H_inv,
    image_path,
    is_validated=False
):
    status_label = "VALIDATED" if is_validated else "UNVERIFIED_PRELIMINARY"
    config = {
        "calibration_status": status_label,
        "is_validated": is_validated,
        "assumed_lane_width_m": lane_width_m,
        "assumed_road_length_m": road_length_m,
        "source_frame": image_path,
        "methodology": {
            "plane_model": "Homography (Planar Perspective)",
            "lane_width_policy": "Assumed 3.5 m (Unverified preliminary only)",
            "speed_validation_allowed": is_validated,
            "disclaimer": (
                "The assumed lane width of 3.5 m is used ONLY for preliminary analysis "
                "and is strictly UNVERIFIED. Do not calculate or report validated speeds "
                "until sufficient calibration data is verified."
            )
        },
        "src_points_pixel": [[float(pt[0]), float(pt[1])] for pt in src_points],
        "dst_points_meter": [
            [0.0, 0.0],
            [float(road_length_m), 0.0],
            [float(road_length_m), float(lane_width_m)],
            [0.0, float(lane_width_m)]
        ],
        "homography_matrix_H": H.tolist(),
        "inverse_homography_matrix_H_inv": H_inv.tolist()
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Calibration configuration saved: {output_path}")
    print(f"Status: {status_label}")
    if not is_validated:
        print("[CAUTION] Speeds derived from this calibration must remain unverified!")


def main():
    parser = argparse.ArgumentParser(description="Road-Plane Homography Calibration Tool")
    parser.add_argument(
        "--image",
        type=str,
        default="outputs/calibration/clean_frame_NH48.png",
        help="Path to clean calibration frame"
    )
    parser.add_argument(
        "--src-points",
        type=str,
        default=None,
        help="Comma-separated 8 coordinates: x1,y1,x2,y2,x3,y3,x4,y4"
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
        default=25.0,
        help="Estimated longitudinal length in meters"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/calibration",
        help="Output directory for calibration files"
    )
    parser.add_argument(
        "--validated",
        action="store_true",
        help="Flag if calibration points have been independently surveyed and verified"
    )
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"ERROR: Calibration frame not found: {args.image}", file=sys.stderr)
        print("Run scripts/extract_clean_frame.py first to extract a reference frame.", file=sys.stderr)
        sys.exit(1)

    image = cv2.imread(args.image)
    if image is None:
        print(f"ERROR: Could not load image from: {args.image}", file=sys.stderr)
        sys.exit(1)

    if args.src_points:
        coords = [float(v.strip()) for v in args.src_points.split(",")]
        if len(coords) != 8:
            print("ERROR: --src-points must contain exactly 8 values: x1,y1,x2,y2,x3,y3,x4,y4", file=sys.stderr)
            sys.exit(1)
        src_points = [(coords[i], coords[i + 1]) for i in range(0, 8, 2)]
    else:
        # Interactive UI mode
        selector = PointSelector(image)
        src_points = selector.select()

    H, H_inv, src, dst = compute_calibration(src_points, args.lane_width, args.road_length)

    config_path = os.path.join(args.output_dir, "calibration_config.json")
    save_calibration_config(
        config_path,
        src_points,
        args.lane_width,
        args.road_length,
        H,
        H_inv,
        args.image,
        is_validated=args.validated
    )

    overlay_path, bev_path = generate_visualizations(
        image,
        src_points,
        H,
        args.output_dir,
        args.lane_width,
        args.road_length
    )

    print("=" * 60)
    print(" Road-Plane Calibration Completed ")
    print("=" * 60)
    print(f"Calibration Config : {config_path}")
    print(f"Verification Overlay: {overlay_path}")
    print(f"Bird's-Eye View     : {bev_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
