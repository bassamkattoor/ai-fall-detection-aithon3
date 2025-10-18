@echo off
echo Installing AI Fall Detection System...
echo.

echo Installing required packages...
pip install opencv-python mediapipe numpy Pillow

echo.
echo Installation complete!
echo.
echo Starting the AI Fall Detection System...
echo.
python working_fall_detection.py

pause
