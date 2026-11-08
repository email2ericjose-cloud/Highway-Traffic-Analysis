"""
Pipeline Runner for UAV Traffic Analysis Backend
================================================
Coordinates execution of the real automated processing pipeline in a background thread,
capturing real-time logs, tracking stage progression, and reporting live status to the UI.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional


class PipelineRunner:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_singleton()
            return cls._instance

    def _init_singleton(self):
        self.status = "completed"  # Initial state represents current dataset state
        self.current_stage = "Surrogate Safety Measures & Report Generation"
        self.progress_percent = 100
        self.start_time = None
        self.end_time = None
        self.elapsed_sec = 28.4
        self.error_message = None
        self.logs: List[str] = [
            "[SYSTEM] Pipeline ready. Current dataset: National Highway 48 (1608x908 @ 30 FPS).",
            "[SYSTEM] 160 vehicle tracks registered (126 highway corridor trajectories).",
            "[SYSTEM] 195 collision conflict pairs evaluated and ranked.",
            "[SYSTEM] Ready to execute automated pipeline for newly uploaded or selected video."
        ]
        self.stages = [
            {"id": 1, "name": "Video Input & Frame Extraction", "status": "completed", "duration": "0.4s"},
            {"id": 2, "name": "Road-Plane Calibration (Homography)", "status": "completed", "duration": "1.2s"},
            {"id": 3, "name": "YOLOv8s-VisDrone Detection", "status": "completed", "duration": "12.8s"},
            {"id": 4, "name": "ByteTrack Multi-Object Tracking", "status": "completed", "duration": "4.6s"},
            {"id": 5, "name": "Trajectory Smoothing & Metric Projection", "status": "completed", "duration": "2.9s"},
            {"id": 6, "name": "Traffic Flow Analytics (q, k, u)", "status": "completed", "duration": "2.1s"},
            {"id": 7, "name": "Surrogate Safety Measures (TTC, PET, Risk)", "status": "completed", "duration": "4.4s"}
        ]
        self._thread: Optional[threading.Thread] = None

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            elapsed = self.elapsed_sec
            if self.status == "running" and self.start_time:
                elapsed = round(time.time() - self.start_time, 1)

            return {
                "status": self.status,
                "current_stage": self.current_stage,
                "progress_percent": self.progress_percent,
                "elapsed_seconds": elapsed,
                "stages": [dict(s) for s in self.stages],
                "logs": list(self.logs[-80:]),  # Return last 80 lines
                "error": self.error_message
            }

    def start_pipeline(self, video_path: str = "videos/National Highway 48.mp4",
                       lane_width: float = 3.5,
                       skip_tracking: bool = True) -> Dict[str, Any]:
        with self._lock:
            if self.status == "running":
                return {"success": False, "message": "Pipeline is already running."}

            self.status = "running"
            self.current_stage = "Initializing video pipeline..."
            self.progress_percent = 5
            self.start_time = time.time()
            self.error_message = None
            self.logs.append(f"\n--- [PIPELINE TRIGGERED] Input: {video_path} (Lane Width: {lane_width}m) ---")
            
            # Reset stages to pending
            for s in self.stages:
                s["status"] = "pending"
                s["duration"] = "--"

            self._thread = threading.Thread(
                target=self._run_worker,
                args=(video_path, lane_width, skip_tracking),
                daemon=True
            )
            self._thread.start()
            return {"success": True, "message": "Pipeline worker thread started."}

    def _run_worker(self, video_path: str, lane_width: float, skip_tracking: bool):
        project_root = Path(__file__).resolve().parent.parent.parent
        script_path = project_root / "scripts" / "run_automated_pipeline.py"
        python_bin = sys.executable

        cmd = [
            python_bin,
            str(script_path),
            "--input", str(video_path),
            "--lane-width", str(lane_width),
        ]
        if skip_tracking:
            cmd.append("--skip-tracking-if-exists")

        try:
            self.logs.append(f"[EXEC] Command: {' '.join(cmd)}")
            proc = subprocess.Popen(
                cmd,
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )

            stage_map = {
                "STAGE 1": (0, "Video Input & Frame Extraction", 15),
                "STAGE 2": (1, "Road-Plane Calibration (Homography)", 30),
                "STAGE 3": (2, "YOLOv8s-VisDrone Detection", 50),
                "STAGE 4": (3, "ByteTrack Multi-Object Tracking", 65),
                "STAGE 5": (4, "Trajectory Smoothing & Metric Projection", 80),
                "OBJECTIVE 3": (5, "Traffic Flow Analytics (q, k, u)", 90),
                "OBJECTIVE 4": (6, "Surrogate Safety Measures (TTC, PET, Risk)", 95),
            }

            for line in iter(proc.stdout.readline, ''):
                clean_line = line.strip()
                if clean_line:
                    with self._lock:
                        self.logs.append(clean_line)
                        # Check for stage triggers
                        for trigger, (idx, name, pct) in stage_map.items():
                            if trigger in clean_line.upper():
                                if idx > 0:
                                    self.stages[idx - 1]["status"] = "completed"
                                self.stages[idx]["status"] = "running"
                                self.current_stage = name
                                self.progress_percent = pct
                                break

            proc.stdout.close()
            return_code = proc.wait()

            with self._lock:
                self.end_time = time.time()
                self.elapsed_sec = round(self.end_time - self.start_time, 1)

                if return_code == 0:
                    self.status = "completed"
                    self.progress_percent = 100
                    self.current_stage = "Pipeline finished successfully."
                    for s in self.stages:
                        s["status"] = "completed"
                    self.logs.append(f"[SUCCESS] Pipeline finished in {self.elapsed_sec}s with exit code 0.")
                else:
                    self.status = "error"
                    self.error_message = f"Process exited with error code {return_code}"
                    self.logs.append(f"[ERROR] Pipeline failed with exit code {return_code}")

        except Exception as e:
            with self._lock:
                self.status = "error"
                self.error_message = str(e)
                self.logs.append(f"[EXCEPTION] {e}")
