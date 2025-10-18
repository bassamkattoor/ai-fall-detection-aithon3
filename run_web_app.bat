@echo off
echo Installing Streamlit dependencies...
pip install streamlit opencv-python numpy Pillow

echo.
echo Starting Streamlit web app...
echo.
streamlit run streamlit_app.py
