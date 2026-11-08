import argparse
from pathlib import Path
from uav_vehicle_analysis.detection import run_detection

def main():
    parser = argparse.ArgumentParser(description="Run vehicle detection on a UAV video.")
    parser.add_argument("--video", type=Path, required=True, help="Path to input video")
    parser.add_argument("--output", type=Path, default=Path('outputs/detection'), help="Directory to store detection results")
    parser.add_argument("--model", type=Path, help="Path to YOLO model checkpoint (overrides config)")
    parser.add_argument("--conf-thresh", type=float, default=0.5, help="Detection confidence threshold")
    args = parser.parse_args()
    run_detection(video_path=args.video, output_dir=args.output, model_path=args.model, conf_thresh=args.conf_thresh)

if __name__ == "__main__":
    main()
