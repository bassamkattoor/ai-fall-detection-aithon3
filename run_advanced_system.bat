@echo off
echo Installing Advanced AI Fall Detection System...
echo.

echo Installing core dependencies...
pip install opencv-python numpy Pillow pyttsx3

echo.
echo Installing MediaPipe...
pip install mediapipe

echo.
echo Installing TensorFlow (this may take a while)...
pip install tensorflow==2.13.0

echo.
echo Installing optional dependencies...
pip install playsound

echo.
echo Installation complete!
echo.
echo Starting the Advanced AI Fall Detection System...
echo.
echo NOTE: Make sure you have your fall_detection_model.h5 file in the same directory!
echo.
python advanced_fall_detection.py

pause
