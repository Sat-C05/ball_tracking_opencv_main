# 🎾 Real-Time Tennis Ball Tracking & Interactive Game

A real-time, gesture-controlled arcade game built with **Python and OpenCV**.

The application detects a physical tennis ball through a webcam and uses its movement to interact with randomly generated targets in a 60-second scoring challenge.

## Features

- **Real-time ball detection:** HSV segmentation, morphological operations, and contour filtering.
- **Smooth tracking:** Exponential Moving Average (EMA) and a visual movement trail.
- **Gesture-controlled gameplay:** Hold the ball inside START to trigger a 3-second countdown.
- **Target collision detection:** Random rectangular targets with position and size validation.
- **Game state management:** Finite-state machine controlling gameplay, scoring, feedback, and restart.
- **Live interface:** Score, countdown timer, FPS monitoring, and final results.
- **Debugging & testing:** HSV mask visualization and automated gameplay tests.

## Tech Stack

- Python
- OpenCV
- NumPy

## Project Structure

```text
ball_tracking_opencv_main/
├── main.py          # Webcam, tracking, UI and controls
├── detector.py      # HSV segmentation and ball detection
├── game.py          # Game states, scoring and collision logic
├── config.py        # Detection configuration
├── test_game.py     # Game logic tests
├── requirements.txt
└── README.md
```

## How It Works

```text
Webcam → HSV Segmentation → Contour Filtering
       → EMA Smoothing → Ball Coordinates
       → Game State Machine → Collision Detection
       → Score & Visual Feedback
```

The detector identifies the tennis ball in each frame, while the game engine interprets its position according to the current game state.

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/Sat-C05/ball_tracking_opencv_main.git
cd ball_tracking_opencv_main
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the game**

```bash
python main.py
```

**5. Run tests (optional)**

```bash
python test_game.py
```

## Controls

| Control | Action |
|---|---|
| Hold ball inside START | Start or replay |
| Move ball into target | Score |
| `R` | Restart |
| `D` | Toggle HSV debug mask |
| `Q` | Quit |

## Current Status

**Fully playable single-ball tracking game**, featuring gesture-based interaction, timed scoring, visual feedback, and automated gameplay tests.

**Known limitations:** Detection depends on lighting and HSV calibration. The system tracks one ball at a time and does not maintain persistent object identities.

### Future Improvements

Multi-ball tracking, adjustable difficulty, interactive HSV calibration, and persistent high scores.
