"""
Clean Frame Extraction Tool for Road-Plane Calibration
======================================================
Extracts high-resolution reference frame(s) from highway drone video footage.
These clean frames serve as the visual baseline for homography / road-plane calibration.

Usage:
  python scripts/extract_clean_frame.py --input "videos/National Highway 48.mp4" --output "outputs/calibration/clean_frame_NH48.png" --time-sec 2.0
"""

import argparse
import json
import os
import sys
import cv2


def parse_args():
    parser = argparse.ArgumentParser(description="Extract clean reference frames for calibration")
    parser.add_argument(
        "--input",
        type=str,
        default="videos/National Highway 48.mp4",
        help="Input video file path"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/calibration/clean_frame_NH48.png",
        help="Output image path for selected clean frame"
    )
    parser.add_argument(
        "--time-sec",
        type=float,
        default=2.0,
        help="Timestamp in seconds to extract (default: 2.0s)"
    )
    parser.add_argument(
        "--extract-candidates",
        action="store_true",
        help="Extract multiple candidate frames across the video for visual inspection"
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=5,
        help="Number of candidate frames to sample evenly across video"
    )
    return parser.parse_args()


def extract_frame(args):
    if not os.path.exists(args.input):
        print(f"ERROR: Video file not found at: {args.input}", file=sys.stderr)
        sys.exit(1)

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print(f"ERROR: Could not open video file: {args.input}", file=sys.stderr)
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames / fps if fps > 0 else 0

    print("=" * 60)
    print(" Video Metadata Inspection ")
    print("=" * 60)
    print(f"File       : {args.input}")
    print(f"Resolution : {width} x {height}")
    print(f"Frame Rate : {fps:.2f} FPS")
    print(f"Total Frames: {total_frames}")
    print(f"Duration   : {duration_sec:.2f} seconds")
    print("=" * 60)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    metadata = {
        "video_path": args.input,
        "width": width,
        "height": height,
        "fps": fps,
        "total_frames": total_frames,
        "duration_sec": duration_sec
    }

    if args.extract_candidates:
        candidate_dir = os.path.join(os.path.dirname(args.output), "candidates")
        os.makedirs(candidate_dir, exist_ok=True)
        step = max(1, total_frames // (args.num_candidates + 1))
        candidate_files = []
        for i in range(1, args.num_candidates + 1):
            f_idx = min(i * step, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
            ret, frame = cap.read()
            if ret:
                c_path = os.path.join(candidate_dir, f"frame_{f_idx:05d}_t{f_idx/fps:.2f}s.png")
                cv2.imwrite(c_path, frame)
                candidate_files.append(c_path)
                print(f"Saved candidate frame: {c_path}")
        metadata["candidate_frames"] = candidate_files

    # Extract target frame
    target_frame_idx = min(int(args.time_sec * fps), total_frames - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_idx)
    ret, frame = cap.read()
    if not ret:
        print(f"WARNING: Could not seek to frame {target_frame_idx}, reading frame 0...", file=sys.stderr)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()

    if ret:
        cv2.imwrite(args.output, frame)
        print(f"Successfully extracted clean frame to: {args.output} (Frame {target_frame_idx}, time {target_frame_idx/fps:.2f}s)")
        metadata["clean_frame_path"] = args.output
        metadata["clean_frame_index"] = target_frame_idx
        metadata["clean_frame_timestamp_sec"] = target_frame_idx / fps
    else:
        print("ERROR: Failed to read frame from video.", file=sys.stderr)
        cap.release()
        sys.exit(1)

    cap.release()

    meta_json_path = os.path.splitext(args.output)[0] + "_info.json"
    with open(meta_json_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata recorded to: {meta_json_path}")


if __name__ == "__main__":
    args = parse_args()
    extract_frame(args)
