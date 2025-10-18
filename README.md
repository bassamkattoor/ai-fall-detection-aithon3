# AI Fall Detection System - AITHON 3.0

## Quick Setup (10 minutes)

### 1. Install Dependencies
Run the installation script:
```bash
install.bat
```

### 2. Run the System
```bash
python fall_detection_system.py
```

## Features Implemented

✅ **Task 1: Computer Vision**
- Real-time pose estimation using MediaPipe
- Keypoint tracking for fall detection
- Live camera feed with pose overlay

✅ **Task 2: AI Model Development**
- Fall detection logic using pose features
- Body orientation analysis
- Ground detection algorithms

✅ **Task 3: Real-Time Integration**
- Continuous fall/no-fall classification
- Immediate alert triggering system

✅ **Task 4: Voice Interaction System**
- Automatic voice prompts on fall detection
- Speech recognition for user responses
- Text-to-speech for system communication

✅ **Task 7: User Interface**
- Dark-themed dashboard
- Live camera feed display
- Heart rate monitor simulation
- Previous fall data tracking
- Alert controls and status display

## How It Works

1. **Pose Detection**: Uses MediaPipe to track 33 body keypoints in real-time
2. **Fall Detection**: Analyzes body orientation and ground position
3. **Voice Interaction**: Speaks "Are you okay?" when fall is detected
4. **Response Processing**: Listens for user voice response
5. **Alert Management**: Cancels or escalates based on user response

## Controls

- **Cancel False Alarm**: Button to manually cancel alerts
- **Voice Commands**: Say "I'm fine" or "I'm okay" to cancel
- **Emergency**: Say "help" or "emergency" to escalate

## System Requirements

- Webcam
- Microphone
- Python 3.7+
- Windows/Linux/Mac

## Troubleshooting

If you get audio errors, try:
```bash
pip install pyaudio --upgrade
```

For webcam issues, ensure your camera is not being used by other applications.
