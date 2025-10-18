@echo off
echo Installing Advanced AI Fall Detection System (Demo Version)...
echo.

echo Installing core dependencies...
pip install opencv-python numpy Pillow pyttsx3

echo.
echo Installing MediaPipe...
pip install mediapipe

echo.
echo Installation complete!
echo.
echo Starting the Advanced AI Fall Detection System (Demo)...
echo.
echo NOTE: This version uses pose-based detection (no TensorFlow model required)
echo.
python advanced_fall_detection_demo.py

pause
