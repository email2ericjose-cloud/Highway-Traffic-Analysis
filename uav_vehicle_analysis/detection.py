import os
from pathlib import Path
import torch
from ultralytics import YOLO
import pandas as pd
import json

def load_model(model_path: Path | str = None) -> YOLO:
    """Load a YOLOv8 model for VisDrone detection.

    If *model_path* is None, the default model defined in the package config is used.
    """
    if model_path is None:
        from .config import load_config
        cfg = load_config()
        model_path = cfg["model_path"]
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"[ERROR] YOLO model not found: {model_path}")
    return YOLO(str(model_path))

def run_detection(video_path: Path | str, output_dir: Path | str, model_path: Path | str = None, conf_thresh: float = 0.5) -> Path:
    """Run detection on *video_path* and save per-frame predictions as JSON.

    The function writes a ``detections.jsonl`` file where each line corresponds to a
    frame and contains a list of detections ``[x, y, w, h, class_id, confidence]``.
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    detections_file = output_dir / "detections.jsonl"

    model = load_model(model_path)
    model.conf = conf_thresh
    # Use YOLO's built-in video inference that yields per-frame results
    results = model.predict(str(video_path), save=False, stream=True)
    with detections_file.open("w", encoding="utf-8") as f:
        for frame_idx, r in enumerate(results):
            # r.boxes.xywh, r.boxes.cls, r.boxes.conf are tensors
            detections = []
            for box, cls, conf in zip(r.boxes.xywh.cpu().numpy(), r.boxes.cls.cpu().numpy(), r.boxes.conf.cpu().numpy()):
                x, y, w, h = box.tolist()
                detections.append([x, y, w, h, int(cls), float(conf)])
            line = json.dumps({"frame": frame_idx, "detections": detections})
            f.write(line + "\n")
    print(f"[INFO] Detection results saved to {detections_file}")
    return detections_file
