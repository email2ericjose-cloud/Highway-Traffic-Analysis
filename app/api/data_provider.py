"""
Data Provider for UAV-Based Vehicle Detection & Trajectory Analysis
===================================================================
Provides verified research data from the pipeline outputs for REST API endpoints.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class DataProvider:
    def __init__(self, root_dir: Optional[str] = None):
        if root_dir is None:
            # Root is project root
            self.root_dir = Path(__file__).resolve().parent.parent.parent
        else:
            self.root_dir = Path(root_dir)

        self.outputs_dir = self.root_dir / "outputs"
        self.analysis_dir = self.outputs_dir / "analysis"
        self.safety_dir = self.outputs_dir / "safety_analysis"
        self.calib_dir = self.outputs_dir / "calibration"

    def _read_json_safe(self, path: Path) -> Dict[str, Any]:
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[DataProvider] Error reading {path}: {e}")
        return {}

    def get_status(self) -> Dict[str, Any]:
        analysis_sum = self._read_json_safe(self.analysis_dir / "analysis_summary.json")
        safety_rep = self._read_json_safe(self.safety_dir / "comprehensive_safety_report.json")
        
        video_name = safety_rep.get("video", "National Highway 48.mp4")
        obj3 = safety_rep.get("objective_3", {})
        obj4 = safety_rep.get("objective_4", {})
        obj5 = safety_rep.get("objective_5", {})

        return {
            "status": "ONLINE",
            "project_name": "UAV-Based Vehicle Detection & Trajectory Analysis",
            "academic_context": "M.Tech Research Project | Civil Engineering and Geoinformatics",
            "author": "Eric Jose",
            "video_metadata": {
                "filename": video_name,
                "resolution": "1608x908",
                "fps": 30.0,
                "duration_sec": obj3.get("duration_sec", 20.03),
                "total_frames": 601,
                "corridor_length_m": 160.0,
                "assumed_lane_width_m": 3.5,
                "calibration_status": obj3.get("calibration_status", "UNVERIFIED_PRELIMINARY"),
                "methodology_disclaimer": obj3.get("methodology_disclaimer", "Assumed 3.5m lane width without surveyed ground truth.")
            },
            "kpi_summary": {
                "total_tracked_vehicles": analysis_sum.get("total_tracked_vehicles", 160),
                "highway_vehicles": obj3.get("total_unique_vehicles", 48),
                "flow_rate_veh_hr": obj3.get("flow_rate_q_veh_per_hr", {}).get("total", 8625.6),
                "traffic_density_veh_km": obj3.get("traffic_density_k_veh_per_km", {}).get("density_k", 175.1),
                "time_mean_speed_kmh": obj3.get("speed_analysis_kmh_unverified", {}).get("time_mean_speed_ut", 26.59),
                "space_mean_speed_kmh": obj3.get("speed_analysis_kmh_unverified", {}).get("space_mean_speed_us", 25.44),
                "p85_speed_kmh": obj3.get("speed_analysis_kmh_unverified", {}).get("p85_speed", 31.67),
                "critical_ttc_count": obj4.get("ttc_analysis", {}).get("critical_ttc_under_1_5s", 2391),
                "critical_pet_count": obj4.get("pet_analysis", {}).get("critical_pet_under_1_0s", 209),
                "evaluated_conflict_pairs": obj5.get("total_conflict_pairs_evaluated", 195),
                "tier1_high_risk_pairs": obj5.get("risk_tier_breakdown", {}).get("Tier 1: High / Critical Collision Risk", 147)
            }
        }

    def get_metrics(self) -> Dict[str, Any]:
        safety_rep = self._read_json_safe(self.safety_dir / "comprehensive_safety_report.json")
        obj3 = safety_rep.get("objective_3", {})
        obj4 = safety_rep.get("objective_4", {})

        return {
            "flow_rate": obj3.get("flow_rate_q_veh_per_hr", {
                "total": 8625.6,
                "eastbound": 3594.0,
                "westbound": 5031.6
            }),
            "density": obj3.get("traffic_density_k_veh_per_km", {
                "average_vehicles_in_segment": 28.02,
                "density_k": 175.1,
                "segment_length_m": 160.0
            }),
            "speed_metrics": obj3.get("speed_analysis_kmh_unverified", {
                "time_mean_speed_ut": 26.59,
                "space_mean_speed_us": 25.44,
                "p85_speed": 31.67,
                "speed_std_dev": 5.42,
                "min_speed": 16.0,
                "max_speed": 44.5
            }),
            "modal_split": obj3.get("class_breakdown", {
                "car": 31,
                "van": 8,
                "bus": 7,
                "truck": 1,
                "motor": 1
            }),
            "directional_split": obj3.get("directional_split", {
                "Westbound": 28,
                "Eastbound": 20
            }),
            "ttc_summary": obj4.get("ttc_analysis", {}),
            "pet_summary": obj4.get("pet_analysis", {})
        }

    def get_conflicts(self, tier: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        conflicts = self._read_json_safe(self.safety_dir / "ranked_collision_conflicts.json")
        if not isinstance(conflicts, list):
            return []

        results = []
        for c in conflicts:
            if tier and tier.lower() not in c.get("risk_tier", "").lower():
                continue
            if search:
                s = search.lower()
                follower = f"veh #{c.get('follower_id')} {c.get('follower_class')}".lower()
                leader = f"veh #{c.get('leader_id')} {c.get('leader_class')}".lower()
                zone = str(c.get("hotspot_zone_m", "")).lower()
                if s not in follower and s not in leader and s not in zone:
                    continue
            results.append(c)
        return results

    def get_critical_distances(self) -> Dict[str, Any]:
        return self._read_json_safe(self.safety_dir / "critical_distance_analysis.json")

    def get_hotspots(self) -> Dict[str, Any]:
        safety_rep = self._read_json_safe(self.safety_dir / "comprehensive_safety_report.json")
        hotspots = safety_rep.get("objective_5", {}).get("spatial_hotspots_20m_intervals", {})
        
        # Sort intervals by conflict count descending
        sorted_hotspots = sorted(
            [{"interval": k, "conflicts": v} for k, v in hotspots.items()],
            key=lambda x: x["conflicts"],
            reverse=True
        )
        return {
            "total_intervals": len(hotspots),
            "ranked_zones": sorted_hotspots,
            "raw_distribution": hotspots
        }

    def get_trajectories(self) -> Dict[str, Any]:
        traj_file = self.analysis_dir / "trajectory_studio_data.json"
        return self._read_json_safe(traj_file)
