import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG = {
    "video_path": "",
    "output_dir": "outputs",
    "model_path": "models/yolov8s-visdrone.pt",
    "detection_confidence": 0.5,
    "calibration": {
        "run": True,
        "assumed_lane_width_m": 3.5
    },
    "run_safety_analysis": True,
    "launch_dashboard": True,
    "fps": 30.0
}

def load_config(config_path: Path | str = None) -> Dict[str, Any]:
    """Load the JSON pipeline configuration.

    If *config_path* is omitted, ``config/pipeline_config.json`` under the project
    root is used. The function merges the user-provided config with
    ``DEFAULT_CONFIG`` so that missing keys fall back to sensible defaults.
    """
    if config_path is None:
        config_path = Path(__file__).parents[2] / "config" / "pipeline_config.json"
    else:
        config_path = Path(config_path)

    if not config_path.is_file():
        raise FileNotFoundError(f"[ERROR] Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        user_cfg = json.load(f)

    # Deep-merge with defaults (simple shallow merge works for this structure)
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(user_cfg)
    if "calibration" in user_cfg:
        cfg["calibration"].update(user_cfg["calibration"])
    return cfg

def dump_config(cfg: Dict[str, Any], dest: Path | str) -> None:
    """Write *cfg* back to *dest* in a pretty-printed JSON format."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, sort_keys=True)
