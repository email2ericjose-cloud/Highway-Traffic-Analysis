"""Vehicle class mapping for VisDrone and COCO model architectures.

This module provides a unified class taxonomy so that every stage of the
pipeline works with human-readable class names regardless of the underlying
detection model (VisDrone, COCO, or custom).
"""

# VisDrone class-id -> human-readable name
VISDRONE_CLASSES = {
    0: "Pedestrian",
    1: "Person",
    2: "Bicycle",
    3: "Car",
    4: "Van",
    5: "Truck",
    6: "Tricycle",
    7: "Awning-Tricycle",
    8: "Bus",
    9: "Motorcycle",
}

# COCO class-id -> human-readable name (vehicle subset)
COCO_VEHICLE_CLASSES = {
    0: "Person",
    1: "Bicycle",
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck",
}

# Broad vehicle categories for aggregation
VEHICLE_CATEGORIES = {
    "Car":           ["Car"],
    "Van / LCV":     ["Van"],
    "Bus":           ["Bus"],
    "Truck / HCV":   ["Truck"],
    "Two-Wheeler":   ["Motorcycle", "Bicycle"],
    "Three-Wheeler": ["Tricycle", "Awning-Tricycle"],
    "Pedestrian":    ["Pedestrian", "Person"],
}


def class_id_to_name(class_id: int, model_type: str = "visdrone") -> str:
    """Convert a numeric class ID to a human-readable name.

    Parameters
    ----------
    class_id : int
        The detection model's integer class label.
    model_type : str
        ``"visdrone"`` or ``"coco"``.
    """
    lookup = VISDRONE_CLASSES if model_type.lower() == "visdrone" else COCO_VEHICLE_CLASSES
    return lookup.get(class_id, f"Unknown-{class_id}")


def name_to_category(class_name: str) -> str:
    """Map a fine-grained class name to a broad vehicle category."""
    for cat, members in VEHICLE_CATEGORIES.items():
        if class_name in members:
            return cat
    return "Other"


def detect_model_type(model) -> str:
    """Infer whether *model* is a VisDrone or COCO model from its class names."""
    names = getattr(model, "names", {})
    if any("van" in str(v).lower() for v in names.values()):
        return "visdrone"
    return "coco"
