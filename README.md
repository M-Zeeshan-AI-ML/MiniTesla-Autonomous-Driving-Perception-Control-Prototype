# MiniTesla — CARLA-Free Autonomous Driving Perception & Control

A lightweight local version of the MiniTesla portfolio project that runs in VS Code on a normal Windows PC without the CARLA simulator.

## What it does

Input can be:
- a driving video (`.mp4`, `.avi`, `.mov`, `.mkv`)
- a single image (`.jpg`, `.png`, `.jpeg`)

Pipeline:

Video/Image
→ OpenCV preprocessing
→ YOLO object detection (optional)
→ lane detection
→ safety heuristic
→ PID steering/controller
→ telemetry CSV
→ annotated demo video

## Important

This is a **perception/control prototype**, not a production autonomous-driving system and is not affiliated with Tesla.

The CARLA simulator is intentionally removed from this version.

## Quick start on Windows

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Put a driving video in

```text
data/input/driving.mp4
```

### 4. Run

```powershell
python scripts/run_video.py --input data/input/driving.mp4 --config configs/default.yaml
```

On first YOLO run, the configured model may be downloaded automatically.

### 5. Evaluate

```powershell
python scripts/evaluate.py runs/latest/telemetry.csv
```

## Run without YOLO

If your PC is slow or you want to test only lane detection:

```powershell
python scripts/run_video.py --input data/input/driving.mp4 --config configs/default.yaml --no-yolo
```

## Output

The program creates:

```text
runs/latest/
├── annotated.mp4
└── telemetry.csv
```

The annotated video shows:
- lane lines
- lane center
- detected objects (when YOLO is enabled)
- steering/control status
- safety braking state


