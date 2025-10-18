import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import threading

# Page configuration
st.set_page_config(
    page_title="AI Fall Detection System - AITHON 3.0",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
    }
    .stApp {
        background-color: #1a1a1a;
    }
    .stSidebar {
        background-color: #2d2d2d;
    }
    .metric-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #444;
    }
    .status-normal {
        color: #00ff00;
        font-weight: bold;
    }
    .status-alert {
        color: #ff6600;
        font-weight: bold;
    }
    .status-emergency {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class WebFallDetectionSystem:
    def __init__(self):
        self.fall_detected = False
        self.alert_active = False
        self.motion_threshold = 1000
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        
        # Initialize session state
        if 'heart_rate' not in st.session_state:
            st.session_state.heart_rate = 75
        if 'previous_falls' not in st.session_state:
            st.session_state.previous_falls = 0
        if 'fall_detected' not in st.session_state:
            st.session_state.fall_detected = False
        if 'alert_active' not in st.session_state:
            st.session_state.alert_active = False

    def detect_motion_and_fall(self, frame):
        """Detect motion and potential falls using background subtraction"""
        fg_mask = self.background_subtractor.apply(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_area = 0
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                motion_area += cv2.contourArea(contour)
        
        if motion_area > self.motion_threshold:
            return True
        return False

    def update_health_data(self):
        """Simulate health data updates"""
        st.session_state.heart_rate += np.random.randint(-2, 3)
        st.session_state.heart_rate = max(60, min(100, st.session_state.heart_rate))

    def simulate_fall(self):
        """Simulate a fall for testing"""
        st.session_state.fall_detected = True
        st.session_state.alert_active = True
        st.session_state.previous_falls += 1
        st.success("Fall detected! Alert system activated.")

    def cancel_alert(self):
        """Cancel false alarm"""
        st.session_state.alert_active = False
        st.session_state.fall_detected = False
        st.success("Alert cancelled. Thank you for confirming.")

    def reset_system(self):
        """Reset the entire system"""
        st.session_state.fall_detected = False
        st.session_state.alert_active = False
        st.session_state.previous_falls = 0
        st.success("System reset successfully.")

# Initialize the system
system = WebFallDetectionSystem()

# Main title
st.title("🚨 AI Fall Detection System - AITHON 3.0")
st.markdown("---")

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📹 Live Camera Feed")
    
    # Camera input
    camera_input = st.camera_input("Take a picture for fall detection")
    
    if camera_input is not None:
        # Convert to OpenCV format
        bytes_data = camera_input.getvalue()
        cv_image = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Process the image
        if cv_image is not None:
            # Detect motion and potential falls
            if system.detect_motion_and_fall(cv_image):
                if not st.session_state.fall_detected:
                    st.session_state.fall_detected = True
                    st.session_state.alert_active = True
                    st.session_state.previous_falls += 1
                    st.error("⚠️ FALL DETECTED!")
            
            # Draw motion detection overlay
            fg_mask = system.background_subtractor.apply(cv_image)
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(cv_image, contours, -1, (0, 255, 0), 2)
            
            # Add status text
            cv2.putText(cv_image, "Motion Detection Active", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the processed image
            st.image(cv_image, channels="BGR", use_column_width=True)
    
    # Status display
    if st.session_state.fall_detected and st.session_state.alert_active:
        st.markdown('<p class="status-alert">⚠️ Status: FALL DETECTED!</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-normal">✅ Status: Normal</p>', unsafe_allow_html=True)

with col2:
    st.header("💓 Health Monitor")
    
    # Heart rate display
    system.update_health_data()
    st.metric("Heart Rate", f"{st.session_state.heart_rate} BPM")
    
    # Health data
    st.subheader("📊 Health Data")
    st.metric("Previous Falls", st.session_state.previous_falls)
    st.metric("Current Time", datetime.now().strftime('%H:%M:%S'))
    
    st.markdown("---")
    
    # Alert controls
    st.subheader("🚨 Alert Controls")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Cancel False Alarm", type="secondary"):
            system.cancel_alert()
    
    with col_btn2:
        if st.button("Reset System", type="secondary"):
            system.reset_system()
    
    st.markdown("---")
    
    # Test controls
    st.subheader("🧪 Test Controls")
    if st.button("Simulate Fall", type="primary"):
        system.simulate_fall()
    
    # Voice interaction status
    st.subheader("🎤 Voice Interaction")
    if st.session_state.fall_detected:
        st.info("Voice: 'Are you okay?'")
    else:
        st.success("Voice: Ready")

# Sidebar information
with st.sidebar:
    st.header("ℹ️ System Info")
    st.write("**AI Fall Detection System**")
    st.write("Using computer vision and motion detection to identify potential falls.")
    
    st.markdown("---")
    
    st.subheader("🔧 Features")
    st.write("✅ Real-time motion detection")
    st.write("✅ Background subtraction")
    st.write("✅ Health data simulation")
    st.write("✅ Alert management")
    st.write("✅ Voice interaction simulation")
    
    st.markdown("---")
    
    st.subheader("📱 How to Use")
    st.write("1. **Take a photo** using the camera")
    st.write("2. **System analyzes** for motion patterns")
    st.write("3. **Alerts trigger** on fall detection")
    st.write("4. **Cancel or escalate** as needed")
    
    st.markdown("---")
    
    st.subheader("🏆 AITHON 3.0")
    st.write("IEEE Student Branch")
    st.write("College of Engineering")
    st.write("Karungappally")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>AI Fall Detection System | AITHON 3.0 | IEEE Student Branch</p>
    </div>
    """, 
    unsafe_allow_html=True
)
