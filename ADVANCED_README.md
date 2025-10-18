# Advanced AI Fall Detection System - AITHON 3.0

## 🚀 Quick Setup

### Prerequisites
1. **Your trained model**: Place `fall_detection_model.h5` in the project directory
2. **Optional files**: 
   - `alarm.wav` - Sound file for alerts
   - `popup_alert.vbs` - Windows popup script

### Installation
```bash
run_advanced_system.bat
```

## 🎯 Features Implemented

### ✅ **Task 1: Computer Vision**
- **Real-time pose estimation** using MediaPipe
- **33 body keypoints** tracking
- **Live camera feed** with pose overlay
- **Bounding box detection** around detected person

### ✅ **Task 2: AI Model Development**
- **TensorFlow model integration** for fall detection
- **Pre-trained model loading** from .h5 file
- **Real-time prediction** on pose crops
- **Probability-based fall detection**

### ✅ **Task 3: Real-Time Integration**
- **Continuous processing** at 10 FPS
- **Smoothing buffer** for stable predictions
- **Sustained detection** requirement (3 consecutive positives)
- **Immediate alert triggering**

### ✅ **Task 4: Voice Interaction System**
- **Text-to-speech** alerts: "Attention. Fall detected. Are you okay?"
- **Voice status display** in UI
- **Audio alarm** (if alarm.wav provided)
- **Windows popup** alerts (if VBS script provided)

### ✅ **Task 7: User Interface**
- **Dark-themed dashboard** as requested
- **Live camera feed** with AI overlays
- **Heart rate monitor** simulation
- **Previous fall data** tracking
- **AI detection info** (probability, FPS)
- **Alert controls** and status display

## 🔧 **Advanced Features**

### **AI Model Integration**
- Loads your trained TensorFlow model
- Processes pose crops for fall detection
- Real-time probability calculation
- Smoothing and threshold-based detection

### **Professional UI**
- Dark theme with modern design
- Real-time metrics display
- AI model status indicator
- Fall probability visualization
- FPS counter

### **Alert System**
- Multi-modal alerts (voice, sound, popup)
- False alarm cancellation
- System reset functionality
- Event logging to file

### **Health Monitoring**
- Simulated heart rate with realistic variations
- Fall count tracking
- Real-time timestamp
- Health data visualization

## 🎮 **How to Use**

1. **Place your model**: Copy `fall_detection_model.h5` to the project folder
2. **Run the system**: Execute `run_advanced_system.bat`
3. **Position yourself**: Stand in front of the camera
4. **Watch the AI**: See real-time pose detection and fall probability
5. **Test alerts**: Use "Simulate Fall" button for demo
6. **Manage alerts**: Cancel false alarms or reset system

## 📊 **System Requirements**

- **Webcam** for live video feed
- **Python 3.7+** with TensorFlow support
- **Windows/Linux/Mac** compatible
- **Your trained model** (.h5 file)

## 🏆 **Hackathon Ready**

This system implements all requirements from your AITHON 3.0 problem statement:

- ✅ Computer vision with pose estimation
- ✅ AI model for fall detection
- ✅ Real-time integration
- ✅ Voice interaction system
- ✅ Dark UI with health monitoring
- ✅ Alert management
- ✅ Professional presentation ready

## 🔧 **Troubleshooting**

### **Model Loading Issues**
- Ensure `fall_detection_model.h5` is in the correct directory
- Check TensorFlow installation: `pip install tensorflow==2.13.0`
- Verify model compatibility with TensorFlow version

### **Camera Issues**
- Ensure webcam is not being used by other applications
- Try different camera index: `python advanced_fall_detection.py --webcam 1`

### **Performance Optimization**
- Adjust `FPS_TARGET` in the code for your system
- Modify `FALL_PROB_THRESHOLD` for sensitivity
- Change `SUSTAIN_REQUIRED` for detection stability

## 📁 **File Structure**
```
project/
├── advanced_fall_detection.py    # Main application
├── fall_detection_model.h5       # Your trained model (required)
├── alarm.wav                     # Alert sound (optional)
├── popup_alert.vbs              # Windows popup (optional)
├── run_advanced_system.bat      # Installation script
├── advanced_requirements.txt    # Dependencies
└── captures/                     # Saved fall images
```

Perfect for your hackathon demo! 🚀
