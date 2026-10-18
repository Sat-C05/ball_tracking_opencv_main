# Real-Time Tennis Ball Detection with OpenCV 🎾

A modular Python application that detects and visually follows a yellow-green tennis ball using a live webcam.

The project uses classical computer vision techniques, including HSV color segmentation, morphological operations, contour analysis, shape filtering, and Exponential Moving Average (EMA) smoothing.

## Features

- Real-time webcam capture
- Horizontally mirrored camera feed
- HSV-based tennis ball detection
- Gaussian blur for noise reduction
- Morphological opening and closing
- Contour area and circularity filtering
- Ball center and radius estimation
- EMA smoothing to reduce visual jitter
- Temporary detection-loss tolerance
- Live visualization of detection and HSV mask

## Project Structure

```text
ball_tracker_modular/
├── main.py
├── detector.py
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | Webcam capture, mirroring, smoothing, visualization, and resource cleanup |
| `detector.py` | Preprocessing, HSV segmentation, contour extraction, and candidate selection |
| `config.py` | Color thresholds, detection constraints, and smoothing parameters |

## Detection Pipeline

```text
Webcam Frame
     |
     v
Horizontal Flip
     |
     v
Gaussian Blur
     |
     v
BGR to HSV Conversion
     |
     v
HSV Color Thresholding
     |
     v
Morphological Opening and Closing
     |
     v
Contour Extraction
     |
     v
Area, Circularity and Radius Filtering
     |
     v
Largest Valid Candidate
     |
     v
EMA Smoothing
     |
     v
Detection Visualization
```

The detector processes individual frames and returns the largest qualifying candidate along with its binary mask. The main application maintains smoothed coordinates between frames.

## Installation

### Requirements

- Python 3.10 or newer
- Working webcam
- OpenCV
- NumPy

### Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Press **Q** while an OpenCV window is focused to exit.

## Configuration

The detector's parameters are defined in `config.py`.

| Parameter | Value | Purpose |
|---|---|---|
| Lower HSV | `[20, 40, 40]` | Lower color threshold |
| Upper HSV | `[85, 255, 255]` | Upper color threshold |
| Gaussian blur | `5×5` | Reduce pixel-level noise |
| Morphological kernel | `5×5` | Clean binary mask |
| Minimum contour area | `600` | Reject small regions |
| Minimum circularity | `0.55` | Reject highly irregular regions |
| Minimum radius | `10` | Reject small candidates |
| EMA alpha | `0.75` | Balance responsiveness and jitter |
| Maximum missed frames | `5` | Preserve smoothing state briefly |

These values were calibrated experimentally and may need adjustment for different environments.

## Detection Visualization

The application displays:

- **Yellow outline:** Detected contour
- **Green circle:** Smoothed enclosing circle
- **Red dot:** Smoothed center
- **Text overlay:** Coordinates and contour circularity
- **HSV Mask window:** Pixels matching the configured color range

## Validation

The prototype passed four manual functional tests:

| Test | Result |
|---|---|
| Stationary ball detection | Passed |
| Fast hand-guided movement | Passed |
| Distance variation | Passed |
| Disappearance and recovery | Passed |

These are qualitative manual tests, not a benchmark of detection accuracy or frame rate.

## Known Limitations

- Detection depends on the configured HSV color range.
- Similarly colored objects may cause false positives.
- Performance may vary with lighting, background, and motion blur.
- Only the largest qualifying candidate is selected per frame.
- Temporary detection-loss handling retains smoothing state but does not predict motion.
- The system does not maintain persistent identities or track multiple balls.

## Future Improvements

- Adjustable HSV calibration interface
- Additional shape and appearance validation
- Detection confidence estimation
- Recorded-video testing
- Quantitative accuracy and latency evaluation

## Project Status

**Functional modular single-ball detection prototype.**

Designed to demonstrate real-time visual detection and following of a hand-moved tennis ball using a webcam.