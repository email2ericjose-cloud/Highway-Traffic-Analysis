"""
DroneFlow Highway Traffic Tracking Script
=========================================
Performs vehicle detection and multi-object tracking (MOT) using YOLOv8
and ByteTrack on drone/aerial highway video footage.

Outputs:
  - Annotated tracking video with bounding boxes and track IDs.
  - Comprehensive vehicle trajectory CSV (frame, time, ID, class, bbox, center).

Usage:
  python scripts/track_traffic.py --input "videos/National Highway 48.mp4" [options]
"""

import argparse
import os
import sys
import time
import cv2
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="DroneFlow YOLOv8 + ByteTrack Traffic Tracker")
    parser.add_argument(
        "--input",
        type=str,
        default="videos/National Highway 48.mp4",
        help="Path to input video file"
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="models/yolov8s-visdrone.pt",
        help="Path to YOLOv8 weights (e.g. DroneFlow/VisDrone aerial model or standard YOLOv8)"
    )
    parser.add_argument(
        "--tracker",
        type=str,
        default="bytetrack.yaml",
        help="Tracker configuration file (default: bytetrack.yaml)"
    )
    parser.add_argument(
        "--output-video",
        type=str,
        default="outputs/National_Highway_48_annotated.mp4",
        help="Output path for annotated video"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="outputs/National_Highway_48_trajectories.csv",
        help="Output path for trajectory CSV"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detection confidence threshold"
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.5,
        help="NMS IoU threshold"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=960,
        help="Inference image resolution"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help="Computation device ('auto', 'cpu', or '0')"
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        type=int,
        default=None,
        help="Target class IDs to track (auto-selected based on model type if None)"
    )
    parser.add_argument(
        "--roi-y",
        nargs=2,
        type=int,
        default=[360, 560],
        help="Vertical ROI range [ymin, ymax] for the main highway carriageways (None for full frame)"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Limit number of frames to process (useful for preview/testing)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate video file and model loading without running full tracking"
    )
    return parser.parse_args()


def run_tracker(args):
    # Ensure ultralytics is imported
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics is not installed in the active environment.", file=sys.stderr)
        print("Please run: pip install ultralytics", file=sys.stderr)
        sys.exit(1)

    # Validate input video
    if not os.path.exists(args.input):
        print(f"ERROR: Input video not found at: {args.input}", file=sys.stderr)
        sys.exit(1)

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print(f"ERROR: Failed to open video file: {args.input}", file=sys.stderr)
        sys.exit(1)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("=" * 60)
    print(" DroneFlow Traffic Tracking Pipeline ")
    print("=" * 60)
    print(f"Input Video : {args.input}")
    print(f"Resolution  : {width} x {height}")
    print(f"Frame Rate  : {fps:.2f} FPS")
    print(f"Total Frames: {total_frames}")
    print(f"Weights     : {args.weights}")
    print(f"Tracker     : {args.tracker}")
    print(f"Output Video: {args.output_video}")
    print(f"Output CSV  : {args.output_csv}")
    print("=" * 60)

    # Initialize model
    print(f"Loading YOLOv8 model from '{args.weights}'...")
    try:
        model = YOLO(args.weights)
    except Exception as e:
        print(f"ERROR: Could not load model '{args.weights}': {e}", file=sys.stderr)
        cap.release()
        sys.exit(1)

    # Resolve target classes based on model architecture
    if args.classes is None:
        names = model.names if hasattr(model, "names") else {}
        if any("van" in str(v).lower() for v in names.values()):
            # VisDrone aerial model: car(3), van(4), truck(5), tricycle(6), awning-tricycle(7), bus(8), motor(9)
            args.classes = [3, 4, 5, 6, 7, 8, 9]
            print(f"Detected aerial/VisDrone model. Targeting vehicle classes: {[names.get(i, i) for i in args.classes]}")
        else:
            # COCO model: car(2), motorcycle(3), bus(5), truck(7)
            args.classes = [2, 3, 5, 7]
            print(f"Detected COCO model. Targeting vehicle classes: {[names.get(i, i) for i in args.classes]}")

    if args.dry_run:
        print("[DRY-RUN] Model and video successfully verified. Exiting without processing.")
        cap.release()
        return

    # Ensure output directories exist
    os.makedirs(os.path.dirname(os.path.abspath(args.output_video)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.output_csv)), exist_ok=True)

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_writer = cv2.VideoWriter(args.output_video, fourcc, fps, (width, height))

    # Auto-detect device if requested
    import torch
    if args.device == "auto":
        args.device = "0" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {args.device}")

    roi_ymin, roi_ymax = args.roi_y if args.roi_y else (0, height)
    print(f"Highway Corridor ROI (Y-axis): [{roi_ymin}, {roi_ymax}]")

    trajectory_records = []
    frame_idx = 0
    frames_to_process = min(total_frames, args.max_frames) if args.max_frames else total_frames

    start_time = time.time()
    print(f"Starting tracking across {frames_to_process} frames...")

    while cap.isOpened() and frame_idx < frames_to_process:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_sec = frame_idx / fps

        # Track with YOLOv8 + ByteTrack
        results = model.track(
            source=frame,
            persist=True,
            tracker=args.tracker,
            conf=args.conf,
            iou=args.iou,
            imgsz=args.imgsz,
            device=args.device,
            classes=args.classes,
            verbose=False
        )

        res = results[0]
        boxes = res.boxes

        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                # If object is assigned a track ID
                track_id = int(box.id[0].item()) if box.id is not None else -1
                cls_id = int(box.cls[0].item())
                cls_name = model.names[cls_id] if hasattr(model, "names") else str(cls_id)
                conf = float(box.conf[0].item())

                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = xyxy

                # Calculate vehicle footprint contact center (bottom-center of bounding box)
                center_x = (x1 + x2) / 2.0
                center_y = y2  # Bottom edge on road plane
                box_w = x2 - x1
                box_h = y2 - y1

                is_highway = bool(roi_ymin <= center_y <= roi_ymax)

                trajectory_records.append({
                    "frame_id": frame_idx,
                    "timestamp_sec": round(timestamp_sec, 4),
                    "track_id": track_id,
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": round(conf, 4),
                    "is_highway_corridor": is_highway,
                    "bbox_x1": round(x1, 2),
                    "bbox_y1": round(y1, 2),
                    "bbox_x2": round(x2, 2),
                    "bbox_y2": round(y2, 2),
                    "center_x": round(center_x, 2),
                    "center_y": round(center_y, 2),
                    "width_px": round(box_w, 2),
                    "height_px": round(box_h, 2),
                })

        # Annotated frame
        annotated_frame = res.plot()
        out_writer.write(annotated_frame)

        frame_idx += 1
        if frame_idx % 50 == 0 or frame_idx == frames_to_process:
            elapsed = time.time() - start_time
            fps_proc = frame_idx / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\rProcessed {frame_idx}/{frames_to_process} frames ({fps_proc:.1f} FPS)...")
            sys.stdout.flush()

    cap.release()
    out_writer.release()
    print("\nTracking completed.")

    # Save trajectory CSV
    df = pd.DataFrame(trajectory_records)
    df.to_csv(args.output_csv, index=False)
    print(f"Trajectory data saved: {args.output_csv} ({len(df)} rows)")
    print(f"Annotated video saved: {args.output_video}")


if __name__ == "__main__":
    args = parse_args()
    run_tracker(args)
