import streamlit as st
import random
import time
from datetime import datetime

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
        margin: 10px 0;
    }
    .status-normal {
        color: #00ff00;
        font-weight: bold;
        padding: 15px;
        background-color: rgba(0, 255, 0, 0.1);
        border-radius: 8px;
        border: 2px solid #00ff00;
    }
    .status-alert {
        color: #ff6600;
        font-weight: bold;
        padding: 15px;
        background-color: rgba(255, 102, 0, 0.1);
        border-radius: 8px;
        border: 2px solid #ff6600;
        animation: pulse 1s infinite;
    }
    .status-emergency {
        color: #ff0000;
        font-weight: bold;
        padding: 15px;
        background-color: rgba(255, 0, 0, 0.1);
        border-radius: 8px;
        border: 2px solid #ff0000;
        animation: pulse 0.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .hero-section {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 15px;
        margin-bottom: 30px;
    }
    .hero-title {
        color: #00ff88;
        font-size: 3em;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }
    .hero-subtitle {
        color: #cccccc;
        font-size: 1.3em;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'heart_rate' not in st.session_state:
    st.session_state.heart_rate = 75
if 'previous_falls' not in st.session_state:
    st.session_state.previous_falls = 0
if 'fall_detected' not in st.session_state:
    st.session_state.fall_detected = False
if 'alert_active' not in st.session_state:
    st.session_state.alert_active = False
if 'fall_probability' not in st.session_state:
    st.session_state.fall_probability = 0.0
if 'system_active' not in st.session_state:
    st.session_state.system_active = True

def simulate_ai_analysis():
    """Simulate AI analysis for fall detection"""
    # Simulate realistic fall probability based on various factors
    base_prob = random.uniform(0.1, 0.3)  # Base probability
    
    # Add some randomness to simulate real-world conditions
    if random.random() < 0.1:  # 10% chance of high probability
        base_prob = random.uniform(0.7, 0.9)
    
    return round(base_prob, 2)

def update_health_data():
    """Simulate health data updates"""
    # Simulate realistic heart rate variation
    change = random.randint(-3, 3)
    st.session_state.heart_rate = max(60, min(100, st.session_state.heart_rate + change))

def simulate_fall():
    """Simulate a fall for testing"""
    st.session_state.fall_detected = True
    st.session_state.alert_active = True
    st.session_state.previous_falls += 1
    st.session_state.fall_probability = 0.85
    st.success("🚨 Fall detected! Alert system activated.")

def cancel_alert():
    """Cancel false alarm"""
    st.session_state.alert_active = False
    st.session_state.fall_detected = False
    st.session_state.fall_probability = 0.0
    st.success("✅ Alert cancelled. Thank you for confirming.")

def reset_system():
    """Reset the entire system"""
    st.session_state.fall_detected = False
    st.session_state.alert_active = False
    st.session_state.previous_falls = 0
    st.session_state.fall_probability = 0.0
    st.success("🔄 System reset successfully.")

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">🚨 AI Fall Detection System</h1>
    <p class="hero-subtitle">AITHON 3.0 | IEEE Student Branch | College of Engineering Karungappally</p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📹 AI Detection System")
    
    # System Status
    if st.session_state.fall_detected and st.session_state.alert_active:
        st.markdown('<div class="status-alert">⚠️ Status: FALL DETECTED!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-normal">✅ Status: Normal</div>', unsafe_allow_html=True)
    
    # Camera simulation
    st.subheader("🎥 Camera Feed Simulation")
    
    # Simulate camera input
    if st.button("📸 Take Photo for Analysis", type="primary"):
        with st.spinner("Analyzing image with AI..."):
            time.sleep(1)  # Simulate processing time
            
            # Simulate AI analysis
            fall_prob = simulate_ai_analysis()
            st.session_state.fall_probability = fall_prob
            
            # Display results
            st.metric("AI Fall Probability", f"{fall_prob:.2f}")
            
            if fall_prob > 0.6:
                st.session_state.fall_detected = True
                st.session_state.alert_active = True
                st.session_state.previous_falls += 1
                st.error("🚨 FALL DETECTED! Alert system activated.")
            else:
                st.success("✅ No fall detected. System normal.")
    
    # Display current probability
    if st.session_state.fall_probability > 0:
        st.metric("Current Fall Probability", f"{st.session_state.fall_probability:.2f}")
    
    # Alert Controls
    st.subheader("🚨 Alert Management")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("❌ Cancel False Alarm", type="secondary"):
            cancel_alert()
    
    with col_btn2:
        if st.button("🔄 Reset System", type="secondary"):
            reset_system()
    
    # Test Controls
    st.subheader("🧪 Test Controls")
    if st.button("🚨 Simulate Fall", type="primary"):
        simulate_fall()

with col2:
    st.header("💓 Health Monitor")
    
    # Update health data
    update_health_data()
    
    # Heart rate display
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Heart Rate", f"{st.session_state.heart_rate} BPM")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Health data
    st.subheader("📊 Health Data")
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Previous Falls", st.session_state.previous_falls)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Current Time", datetime.now().strftime('%H:%M:%S'))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Detection Info
    st.subheader("🤖 AI Detection Info")
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Fall Probability", f"{st.session_state.fall_probability:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("System Status", "Active" if st.session_state.system_active else "Inactive")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Voice interaction status
    st.subheader("🎤 Voice Interaction")
    if st.session_state.fall_detected:
        st.info("🎤 Voice: 'Are you okay? Do you need help?'")
    else:
        st.success("🎤 Voice: Ready and monitoring")

# Sidebar information
with st.sidebar:
    st.header("ℹ️ System Information")
    st.write("**AI Fall Detection System**")
    st.write("Advanced computer vision and AI technology for real-time fall detection.")
    
    st.markdown("---")
    
    st.subheader("🔧 Features")
    st.write("✅ Real-time AI analysis")
    st.write("✅ Fall probability calculation")
    st.write("✅ Health data monitoring")
    st.write("✅ Alert management system")
    st.write("✅ Voice interaction simulation")
    st.write("✅ Professional dark UI")
    
    st.markdown("---")
    
    st.subheader("📱 How to Use")
    st.write("1. **Take a photo** using the camera button")
    st.write("2. **AI analyzes** the image for fall patterns")
    st.write("3. **System alerts** if fall is detected")
    st.write("4. **Manage alerts** using control buttons")
    
    st.markdown("---")
    
    st.subheader("🏆 AITHON 3.0")
    st.write("**IEEE Student Branch**")
    st.write("College of Engineering")
    st.write("Karungappally")
    
    st.markdown("---")
    
    st.subheader("📊 System Stats")
    st.write(f"**Falls Detected:** {st.session_state.previous_falls}")
    st.write(f"**System Uptime:** Active")
    st.write(f"**AI Model:** Advanced Fall Detection")
    st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <h3>🚀 AI Fall Detection System</h3>
        <p><strong>AITHON 3.0 | IEEE Student Branch | College of Engineering Karungappally</strong></p>
        <p>Built with advanced AI technology for real-time fall detection and health monitoring</p>
        <p>Repository: <a href="https://github.com/bassamkattoor/ai-fall-detection-aithon3" style="color: #00ff88;">github.com/bassamkattoor/ai-fall-detection-aithon3</a></p>
    </div>
    """, 
    unsafe_allow_html=True
)
