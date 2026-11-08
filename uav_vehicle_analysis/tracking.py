import pandas as pd
from pathlib import Path
import json
import numpy as np
from collections import defaultdict

# Simple SORT-like tracker (Kalman + IOU) - lightweight placeholder
class SimpleTracker:
    def __init__(self, iou_threshold: float = 0.3, max_age: int = 30):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.next_id = 1
        self.tracks = {}  # id -> {'bbox': [x,y,w,h], 'age': int, 'hits': int}
        self.age = defaultdict(int)

    @staticmethod
    def iou(box_a, box_b):
        # boxes are [x, y, w, h] with (x,y) top-left
        ax1, ay1, aw, ah = box_a
        bx1, by1, bw, bh = box_b
        ax2, ay2 = ax1 + aw, ay1 + ah
        bx2, by2 = bx1 + bw, by1 + bh
        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)
        inter_w = max(0, ix2 - ix1)
        inter_h = max(0, iy2 - iy1)
        inter = inter_w * inter_h
        union = aw * ah + bw * bh - inter
        return inter / union if union > 0 else 0

    def update(self, detections):
        """Update tracks with a list of detections ``[[x,y,w,h,cls,conf], ...]``.
        Returns a list of ``[track_id, x, y, w, h, cls, conf]``.
        """
        assigned = set()
        results = []
        # try to match existing tracks
        for tid, trk in list(self.tracks.items()):
            best_iou, best_det = 0, None
            for det in detections:
                i = self.iou(trk['bbox'], det[:4])
                if i > best_iou:
                    best_iou, best_det = i, det
            if best_iou >= self.iou_threshold:
                # update
                trk['bbox'] = best_det[:4]
                trk['age'] = 0
                trk['hits'] += 1
                results.append([tid, *best_det])
                assigned.add(tuple(best_det))
            else:
                trk['age'] += 1
                if trk['age'] > self.max_age:
                    del self.tracks[tid]
        # create new tracks for unassigned detections
        for det in detections:
            if tuple(det) in assigned:
                continue
            self.tracks[self.next_id] = {'bbox': det[:4], 'age': 0, 'hits': 1}
            results.append([self.next_id, *det])
            self.next_id += 1
        return results

def run_tracking(detections_path: Path | str, output_dir: Path | str) -> Path:
    """Read ``detections.jsonl`` produced by :pyfunc:`detection.run_detection`,
    perform simple multi-object tracking, and write a CSV of trajectories.

    The output CSV has columns ``track_id, frame, x, y, w, h, class_id, confidence``.
    """
    detections_path = Path(detections_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = output_dir / "trajectories.csv"
    tracker = SimpleTracker()
    rows = []
    with detections_path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            frame_idx = data["frame"]
            dets = data["detections"]
            tracked = tracker.update(dets)
            for track_id, x, y, w, h, cls, conf in tracked:
                rows.append([track_id, frame_idx, x, y, w, h, int(cls), float(conf)])
    df = pd.DataFrame(rows, columns=["track_id", "frame", "x", "y", "w", "h", "class_id", "confidence"])
    df.to_csv(out_csv, index=False)
    print(f"[INFO] Tracking results saved to {out_csv}")
    return out_csv
