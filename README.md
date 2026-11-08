# UAV-Based Vehicle Detection and Trajectory Analysis

**Intelligent Transportation Systems (ITS) & Surrogate Safety Research Platform**  
*M.Tech Research Project in Civil Engineering and Geoinformatics*  
**Developer**: **Eric Jose**

An end-to-end scientific platform for processing high-resolution UAV / drone highway traffic videos:

1. **Road-Plane Homography Calibration** - Metric projection derived from known lane geometry.
2. **Vehicle Detection** - Deep learning object detection using YOLOv8 (VisDrone & COCO checkpoints).
3. **Multi-Object Tracking (MOT)** - ByteTrack association with metric trajectory smoothing.
4. **Traffic Flow Analytics** - Flow rate (q), density (k), time-mean (ut) and space-mean (us) speeds, and operating 85th-percentile speed (p85).
5. **Surrogate Safety Measures (SSMs)** - Time-to-Collision (TTC), Post-Encroachment Time (PET), and Deceleration Rate to Avoid a Crash (DRAC).
6. **Kinematic Stopping Distance & Collision Risk** - Dynamic AASHTO / IRC:67 stopping sight distance formulation and safety deficit evaluation.
7. **Interactive Research Studio & Dashboards** - Full-stack web application featuring liquid-glass aesthetics, dynamic trajectory canvas, annotated conflict frame inspector, and automated pipeline execution.

---

## Web Applications & Dashboards

The project provides three distinct web dashboard editions:

### 1. UAV Traffic Studio (Standalone Full-Stack Research Suite)
- **Primary Dedicated URL**: `http://localhost:8080/` (or `http://localhost:8080/studio`)
- **Backend Architecture**: Dedicated Python REST API server (`app/server.py`) serving live data and background pipeline worker threads.
- **8 Dedicated Workspaces**:
  1. **Overview & Research Summary**: Priority KPI hierarchy, modal split donut chart, speed distribution histogram with 85th percentile mark, and research disclaimer.
  2. **Video & Vehicle Detection Workspace**: Native UAV video player with frame navigation (forward/backward step), model parameters, and confidence scores.
  3. **Traffic Flow & Speed Analytics**: Hourly flow equivalent curves over time, Lighthill-Whitham-Richards (LWR) relationships, and class-wise speed breakdown.
  4. **Trajectory Analysis Studio**: Interactive Space-Time (x-t) Canvas visualizer, vehicle pair comparator (Follower vs Leader), and class filter chips.
  5. **Critical Distance & Collision-Risk Workspace**:
     - Dynamic AASHTO stopping distance formula:
       $$d_{safe} = v_f \cdot t_r + \frac{v_f^2}{2 a_f} - \frac{v_l^2}{2 a_l}$$
     - Safety Margin deficit: $\Delta d = d_{clear} - d_{safe}$
     - Interactive sliders for perception-reaction time ($t_r$: 0.5s - 2.5s) and deceleration rate ($a_f$: 2.0 - 6.0 m/s²).
     - High-Resolution Annotated UAV Conflict Frame Inspector with vehicle bounding boxes, connecting vectors, and telemetry HUDs.
     - Full 195 evaluated conflict inventory with real-time search.
  6. **Spatial Hotspots & Corridor Segmentation**: 20-meter longitudinal interval analysis identifying primary bottlenecks ([0m, 20m] with 37 conflicts; [80m, 100m] with 32 conflicts).
  7. **Automated Processing Pipeline Studio**: Visual stage runner with real backend execution trigger (`POST /api/pipeline/run`), live stdout/stderr log streaming, and elapsed time tracking.
  8. **Reports & Exports**: Direct downloads for trajectories CSV (3.9 MB), ranked conflicts CSV, critical distance JSON, full research report JSON, annotated video MP4, and conflict frames.
- **Visual Identity & Controls**:
  - **Themes**: Warm Cream (Default), Clean Modern Light, Dark Analytics.
  - **Liquid Glass**: Toggle ON (Default) / OFF (solid surfaces) via quick button or floating Appearance settings modal.
  - **Motion Effects**: Toggle ON / OFF (respects reduced motion).
  - Preferences persisted in browser `localStorage`.
- **Academic Ownership**:
  > **Developed by Eric Jose**  
  > *UAV-Based Vehicle Detection & Trajectory Analysis*  
  > `M.Tech Research Project | Civil Engineering and Geoinformatics`

### 2. Liquid Glass Dark UI (v2.0)
- **URL**: `http://localhost:8000/` (or `outputs/index.html`)
- **Key Features**: Translucent dark navy glass, specular highlights, native video modal player, 8 KPI cards, 195 ranked collision conflict pairs.

### 3. Classic Dashboard (Original Preserved)
- **URL**: `http://localhost:8000/dashboard/index.html` (or `outputs/dashboard/index.html`)
- **Backup Archive**: `outputs/dashboard/index_original.html`

---

## Launching the Applications

### 1-Click Launchers (Windows)
- **New UAV Traffic Studio (Port 8080)**: Double-click `launch_studio.bat` (or `launch_cream_dashboard.bat`).
- **Dark Dashboard (Port 8000)**: Double-click `launch_dashboard.bat`.

### Command Line
```bash
# Activate Python virtual environment:
.\.venv\Scripts\activate

# Launch the New UAV Traffic Studio (port 8080):
python scripts/launch_studio.py --port 8080

# Launch Dark Dashboard (port 8000):
python scripts/launch_dashboard.py --port 8000

# Launch Classic Original Dashboard:
python scripts/launch_dashboard.py --classic
```

---

## REST API Reference (Port 8080)

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | System status, video metadata, and top-level KPIs |
| `/api/metrics` | GET | Flow rates, traffic density, speed percentiles, modal breakdown |
| `/api/conflicts` | GET | Filterable list of all 195 evaluated collision conflict pairs |
| `/api/critical-distances` | GET | AASHTO safe stopping distance parameters and Top 10 annotated events |
| `/api/hotspots` | GET | Corridor 20m segment conflict distribution and bottleneck ranking |
| `/api/trajectories` | GET | Sampled metric trajectory coordinates for interactive space-time canvas |
| `/api/pipeline/status` | GET | Real-time pipeline state, stage progression, elapsed time, and live logs |
| `/api/pipeline/run` | POST | Trigger backend pipeline execution with custom parameters |

---

## Installation & Setup

### Method 1: 1-Click Windows Setup (Easiest)
Double-click:
```
setup.bat
```
*(or run `install.bat`)*. Automatically verifies Python, configures the `.venv` environment, installs dependencies, and creates the `uav-pipeline` command.

### Method 2: Command Line (Pip)
```bash
.\.venv\Scripts\activate
pip install -e . --no-deps
```

---

## Running the Video Pipeline CLI

```bash
# Run full pipeline with default parameters (lane width = 3.5m):
uav-pipeline --video "videos/National Highway 48.mp4" --lane-width 3.5

# Or run via Python module:
python -m uav_vehicle_analysis --video "videos/National Highway 48.mp4" --lane-width 3.5

# Or run the pipeline script:
python run_pipeline.py --video "videos/National Highway 48.mp4"
```

---

## Project Structure

```
├── launch_studio.bat            1-Click launcher for UAV Traffic Studio (port 8080)
├── launch_cream_dashboard.bat   Dedicated launcher for Cream separate domain
├── launch_dashboard.bat         1-Click launcher for Dark UI (port 8000)
├── run_pipeline.py              Top-level CLI entry point
├── app/                         Standalone Full-Stack Application
│   ├── server.py                Dedicated Python HTTP & REST API server
│   ├── api/
│   │   ├── data_provider.py     Research data loader & JSON endpoints
│   │   └── pipeline_runner.py   Background pipeline executor with log streaming
│   └── static/
│       ├── index.html           Modern responsive HTML5 architecture
│       ├── css/
│       │   └── studio.css       CSS design tokens, themes & liquid glass blur
│       └── js/
│           ├── app.js           Main app lifecycle, routing & modals
│           ├── theme.js         Theme & liquid-glass toggle (localStorage)
│           ├── charts.js        Chart.js visualizations
│           ├── trajectory_studio.js  Interactive Space-Time (x-t) Canvas
│           ├── safety_studio.js Dynamic stopping distance & conflict inspector
│           └── pipeline_studio.js    Live pipeline execution & log stream
├── scripts/
│   ├── launch_studio.py         Launcher for new Studio application
│   ├── launch_cream_dashboard.py Launcher for port 8080
│   ├── launch_dashboard.py      Launcher for port 8000
│   ├── generate_collision_risk_frames.py Annotation engine
│   └── run_automated_pipeline.py End-to-end pipeline script
├── uav_vehicle_analysis/        Core Python research package
├── models/                      YOLOv8 checkpoints (VisDrone, COCO)
├── videos/                      Input video files
└── outputs/                     Generated datasets, frames, and video
```

---

## License

MIT • Academic Research Project • Developed by Eric Jose
